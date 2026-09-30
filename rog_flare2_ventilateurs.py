"""Ventilateurs du PC : carte mère (nct67xx), cartes NVIDIA, alimentation Corsair HXi / RMi.

~/.config/rog-flare2/ventilateurs.json :
    {"canaux": {"cm:2": {"mode": "courbe", "source": "cpu", "courbe": [[40, 30], [70, 60], [85, 100]],
                         "nom": "CPU_FAN"},
                "gpu:0": {"mode": "fixe", "valeur": 60}, "alim": {"mode": "auto"}}}

Canaux : « cm:<n> » (pwm n du contrôleur nct67xx, pilote nct6775), « gpu:<i> » (tous les
ventilateurs de la carte NVIDIA i, ordre NVML = bus PCI), « alim » (Corsair HXi / RMi, HID).
Modes : auto (micrologiciel), fixe (valeur en %), courbe (température de la source → %,
interpolation linéaire). Sources : cpu, gpu0, gpu1…, alim.

Sûreté : plancher par type (PLANCHER), 100 % au-delà de CRITIQUE, retour au mode automatique
si la sonde d'une courbe est illisible, à l'arrêt du démon et après un plantage (ExecStopPost :
`animematrix-ctl ventilateurs --auto`, qui relit les modes d'origine enregistrés).

Accès (facultatifs, voir README) : règle udev 74 pour les pwm de la carte mère et l'alimentation ;
écriture NVML des cartes par l'assistant root `animematrix-ventilateurs-gpu` (sudo sans mot de passe).
Protocole de l'alimentation (PMBus sur HID, rapports de 64 o) relevé dans liquidctl (corsair_hid_psu).
"""
from __future__ import annotations

import ctypes
import json
import os
import select
import subprocess
import threading
from pathlib import Path

from rog_flare2_core import CONFIG_DIR

CONFIG_FILE = CONFIG_DIR / "ventilateurs.json"
ORIGIN_FILE = CONFIG_DIR / "ventilateurs-origine.json"  # modes d'origine des pwm pris en main
HWMON = Path("/sys/class/hwmon")
HIDRAW = Path("/sys/class/hidraw")
GPU_HELPER = os.environ.get("ANIMEMATRIX_VENTILATEURS_GPU", "/usr/libexec/animematrix-ventilateurs-gpu")
PLANCHER = {"cm": 20, "gpu": 30, "alim": 30}  # % minimal accepté en mode fixe / courbe
CRITIQUE = {"cpu": 90, "gpu": 85, "alim": 70}  # °C : 100 % au-delà, quel que soit le réglage
PERIOD = 2.0
PSU_PIDS = {0x1c05, 0x1c06, 0x1c07, 0x1c08, 0x1c0a, 0x1c0b, 0x1c0c, 0x1c0d, 0x1c1e, 0x1c1f, 0x1c23, 0x1c27}


def load_config() -> dict:
    try:
        cfg = json.loads(CONFIG_FILE.read_text())
    except (OSError, ValueError):
        cfg = {}
    return {"canaux": {}, **cfg}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=1))


def check_config(cfg: dict) -> str | None:
    """Message d'erreur, ou None si le réglage est valable."""
    if not isinstance(cfg.get("canaux"), dict):
        return "« canaux » doit être un objet"
    for cid, c in cfg["canaux"].items():
        mode = c.get("mode", "auto")
        if mode not in ("auto", "fixe", "courbe"):
            return f"{cid} : mode inconnu {mode!r}"
        if mode == "fixe" and not (isinstance(c.get("valeur"), (int, float)) and 0 <= c["valeur"] <= 100):
            return f"{cid} : valeur entre 0 et 100 attendue"
        if mode == "courbe":
            pts = c.get("courbe")
            if not (isinstance(pts, list) and pts and all(
                    isinstance(p, (list, tuple)) and len(p) == 2 and 0 <= p[0] <= 120 and 0 <= p[1] <= 100 for p in pts)):
                return f"{cid} : courbe [[°C, %], …] attendue (0-120 °C, 0-100 %)"
    return None


def _read(path: Path) -> str:
    return path.read_text().strip()


def _stable_read(path: Path) -> str:
    """Deux lectures concordantes : le pilote corsair-psu renvoie parfois une valeur parasite juste après un
    échange direct sur le port HID."""
    last = _read(path)
    for _ in range(4):
        value = _read(path)
        if value == last:
            return value
        last = value
    raise OSError(f"{path} : lectures instables")


def _hwmon(prefix: str) -> Path | None:
    for d in sorted(HWMON.glob("hwmon*")):
        try:
            if _read(d / "name").startswith(prefix):
                return d
        except OSError:
            continue
    return None


def curve_value(points: list, temp: float) -> float:
    """Interpolation linéaire, constante avant le premier et après le dernier point."""
    pts = sorted((float(t), float(v)) for t, v in points)
    if not pts:
        return 100.0
    if temp <= pts[0][0]:
        return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if temp <= t1:
            return v0 + (v1 - v0) * (temp - t0) / (t1 - t0) if t1 > t0 else v1
    return pts[-1][1]


# ---------------------------------------------------------------- NVML (lecture, sans root)
class _NVML:
    lib = None

    @classmethod
    def load(cls):
        if cls.lib is None:
            lib = ctypes.CDLL("libnvidia-ml.so.1")
            if lib.nvmlInit_v2() != 0:
                raise OSError("NVML : initialisation refusée")
            cls.lib = lib
        return cls.lib

    @classmethod
    def handle(cls, index: int):
        h = ctypes.c_void_p()
        if cls.load().nvmlDeviceGetHandleByIndex_v2(index, ctypes.byref(h)) != 0:
            raise OSError(f"carte NVIDIA {index} introuvable")
        return h

    @classmethod
    def count(cls) -> int:
        n = ctypes.c_uint()
        return n.value if cls.load().nvmlDeviceGetCount_v2(ctypes.byref(n)) == 0 else 0

    @classmethod
    def uint(cls, fn: str, index: int, *args) -> int:
        v = ctypes.c_uint()
        if getattr(cls.load(), fn)(cls.handle(index), *args, ctypes.byref(v)) != 0:
            raise OSError(f"NVML : {fn} refusé (carte {index})")
        return v.value

    @classmethod
    def name(cls, index: int) -> str:
        buf = ctypes.create_string_buffer(96)
        cls.load().nvmlDeviceGetName(cls.handle(index), buf, 96)
        return buf.value.decode(errors="replace").replace("NVIDIA GeForce ", "")


# ---------------------------------------------------------------- températures
def temperature(source: str) -> float:
    """°C de la source : cpu (Package id 0 de coretemp, sinon k10temp Tctl), gpu<i>, alim (maximum des deux sondes)."""
    if source == "cpu":
        for prefix in ("coretemp", "k10temp", "zenpower"):
            d = _hwmon(prefix)
            if d:
                return int(_read(d / "temp1_input")) / 1000
        raise OSError("sonde du processeur introuvable")
    if source.startswith("gpu") and source[3:].isdigit():
        return float(_NVML.uint("nvmlDeviceGetTemperature", int(source[3:]), 0))
    if source == "alim":
        d = _hwmon("corsairpsu")
        if d:
            return max(int(_read(d / f)) / 1000 for f in ("temp1_input", "temp2_input") if (d / f).exists())
        raise OSError("sonde de l'alimentation introuvable")
    raise OSError(f"source inconnue : {source!r}")


# ---------------------------------------------------------------- canaux
class MotherboardFan:
    """pwm<n> d'un contrôleur nct67xx : 1 = manuel ; le mode d'origine (5 = SmartFan IV…) est rendu en auto."""
    kind = "cm"

    def __init__(self, hwmon: Path, n: int):
        self.dir, self.n, self.id = hwmon, n, f"cm:{n}"
        self.label = f"pwm{n}"

    def rpm(self) -> int | None:
        try:
            return int(_read(self.dir / f"fan{self.n}_input"))
        except (OSError, ValueError):
            return None

    def percent(self) -> int:
        return round(int(_read(self.dir / f"pwm{self.n}")) * 100 / 255)

    def set(self, pct: int) -> None:
        enable = self.dir / f"pwm{self.n}_enable"
        current = _read(enable)
        if current != "1":
            origins = _origins()
            origins.setdefault(self.id, current)
            _save_origins(origins)
            enable.write_text("1")
        (self.dir / f"pwm{self.n}").write_text(str(round(pct * 255 / 100)))

    def held(self) -> bool:
        try:
            return _read(self.dir / f"pwm{self.n}_enable") == "1"
        except OSError:
            return False

    def auto(self) -> None:
        origins = _origins()
        (self.dir / f"pwm{self.n}_enable").write_text(origins.pop(self.id, "5"))
        _save_origins(origins)


class NvidiaFan:
    """Tous les ventilateurs d'une carte ; écriture par l'assistant root (NVML exige root)."""
    kind = "gpu"

    def __init__(self, index: int):
        self.index, self.id = index, f"gpu:{index}"
        try:
            self.label = _NVML.name(index)
        except OSError:
            self.label = f"GPU {index}"

    def rpm(self) -> int | None:
        return None  # NVML ne donne que le pourcentage

    def percent(self) -> int:
        return _NVML.uint("nvmlDeviceGetFanSpeed_v2", self.index, 0)

    def _helper(self, value: str) -> None:
        r = subprocess.run(["sudo", "-n", GPU_HELPER, str(self.index), value], capture_output=True, text=True,
                           timeout=10)
        if r.returncode:
            raise OSError((r.stderr or r.stdout).strip() or "assistant root des cartes graphiques refusé")

    def set(self, pct: int) -> None:
        self._helper(str(pct))

    def auto(self) -> None:
        self._helper("auto")


class CorsairPSU:
    """Alimentation Corsair HXi / RMi par son nœud hidraw (le pilote corsair-psu garde les sondes)."""
    kind = "alim"
    id = "alim"

    def __init__(self, node: str, hwmon: Path | None):
        self.node, self.hwmon, self.label = node, hwmon, "Corsair"

    def rpm(self) -> int | None:
        try:
            return int(_read(self.hwmon / "fan1_input")) if self.hwmon else None
        except (OSError, ValueError):
            return None

    def percent(self) -> int | None:
        try:
            return int(_read(self.hwmon / "pwm1")) * 100 // 255 if self.hwmon else None
        except (OSError, ValueError):
            return None

    def _exec(self, fd: int, cmd: int, data: bytes = b"") -> bytes:
        out = bytes([0x02, cmd]) + data  # adresse 0x02 | bit d'écriture 0, commande PMBus
        for _ in range(3):  # une réponse du pilote noyau peut s'intercaler : on recommence
            while select.select([fd], [], [], 0)[0]:
                os.read(fd, 64)
            os.write(fd, b"\x00" + out + bytes(64 - len(out)))  # 0x00 : pas de numéro de rapport
            if select.select([fd], [], [], 0.5)[0]:
                r = os.read(fd, 64)
                if r[:2] == out[:2]:
                    return r
        raise OSError("alimentation : réponse invalide (autre programme sur le port ?)")

    def _run(self, *steps: tuple[int, bytes]) -> None:
        fd = os.open(self.node, os.O_RDWR)
        try:
            for cmd, data in steps:
                self._exec(fd, cmd, data)
        finally:
            os.close(fd)

    def set(self, pct: int) -> None:
        origins = _origins()
        if self.id not in origins and self.hwmon:  # état d'origine, rendu par auto()
            try:  # pwm1_enable du pilote corsair-psu : 1 = logiciel (consigne pwm1), 2 = matériel
                if _stable_read(self.hwmon / "pwm1_enable") == "1":
                    origins[self.id] = str(round(int(_stable_read(self.hwmon / "pwm1")) * 100 / 255))
                else:
                    origins[self.id] = "materiel"
                _save_origins(origins)
            except (OSError, ValueError):
                pass
        self._run((0xF0, b"\x01"), (0x3B, bytes([pct])))  # mode logiciel, puis FAN_COMMAND_1

    def auto(self) -> None:
        origins = _origins()
        origin = origins.pop(self.id, "materiel")
        if origin.isdigit():  # l'alimentation était déjà en mode logiciel à cette consigne
            self._run((0xF0, b"\x01"), (0x3B, bytes([int(origin)])))
        else:
            self._run((0xF0, b"\x00"))  # mode matériel
        _save_origins(origins)


def _origins() -> dict:
    try:
        return json.loads(ORIGIN_FILE.read_text())
    except (OSError, ValueError):
        return {}


def _save_origins(origins: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ORIGIN_FILE.write_text(json.dumps(origins))


def _psu_node() -> str | None:
    for d in sorted(HIDRAW.glob("hidraw*")):
        try:
            hid = next(line for line in (d / "device" / "uevent").read_text().splitlines() if line.startswith("HID_ID="))
        except (OSError, StopIteration):
            continue
        _bus, vid, pid = hid[7:].split(":")
        if int(vid, 16) == 0x1B1C and int(pid, 16) in PSU_PIDS:
            return f"/dev/{d.name}"
    return None


def discover() -> list:
    """Canaux présents ; `writable` dit si le compte peut les commander."""
    chans: list = []
    d = _hwmon("nct6")
    if d:
        for enable in sorted(d.glob("pwm[0-9]_enable")):
            chans.append(MotherboardFan(d, int(enable.name[3])))
    try:
        chans += [NvidiaFan(i) for i in range(_NVML.count())]
    except OSError:
        pass
    node = _psu_node()
    if node:
        chans.append(CorsairPSU(node, _hwmon("corsairpsu")))
    return chans


def writable(ch) -> bool:
    if ch.kind == "cm":
        return os.access(ch.dir / f"pwm{ch.n}", os.W_OK) and os.access(ch.dir / f"pwm{ch.n}_enable", os.W_OK)
    if ch.kind == "alim":
        return os.access(ch.node, os.R_OK | os.W_OK)
    return os.access(GPU_HELPER, os.X_OK) and subprocess.run(
        ["sudo", "-n", "-l", GPU_HELPER], capture_output=True).returncode == 0


# ---------------------------------------------------------------- régulation (démon)
class FanControl:
    def __init__(self, discover_fn=discover):
        self.discover = discover_fn
        self.cfg: dict = {"canaux": {}}
        self.channels: dict = {}
        self.can_write: dict[str, bool] = {}
        self.applied: dict[str, int] = {}  # dernière consigne envoyée par canal
        self.errors: dict[str, str] = {}
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.lock = threading.Lock()

    def start(self, cfg: dict) -> None:
        self.stop()
        self.cfg = cfg
        self._discover()
        if any(c.get("mode", "auto") != "auto" for c in cfg.get("canaux", {}).values()):
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def _discover(self) -> None:
        self.channels = {ch.id: ch for ch in self.discover()}
        self.can_write = {cid: writable(ch) for cid, ch in self.channels.items()}

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None
        with self.lock:
            for cid in list(self.applied):
                self._release(cid)

    def _release(self, cid: str) -> None:
        ch = self.channels.get(cid)
        self.applied.pop(cid, None)
        if ch:
            try:
                ch.auto()
            except OSError as exc:
                self.errors[cid] = str(exc)

    def target(self, cid: str, c: dict) -> int | None:
        """Consigne en % (None = rendre au micrologiciel)."""
        ch = self.channels[cid]
        if c.get("mode") == "fixe":
            value = float(c.get("valeur", 100))
        else:
            source = c.get("source") or ("gpu" + cid[4:] if ch.kind == "gpu" else "cpu")
            try:
                temp = temperature(source)
            except OSError as exc:
                self.errors[cid] = str(exc)
                return None
            if temp >= CRITIQUE.get(source.rstrip("0123456789"), 90):
                return 100
            value = curve_value(c.get("courbe") or [], temp)
        return int(max(PLANCHER[ch.kind], min(100, round(value))))

    def tick(self) -> None:
        with self.lock:
            for cid, c in self.cfg.get("canaux", {}).items():
                if cid not in self.channels or c.get("mode", "auto") == "auto":
                    if cid in self.applied:
                        self._release(cid)
                    continue
                pct = self.target(cid, c)
                if pct is None:
                    if cid in self.applied:
                        self._release(cid)
                    continue
                last = self.applied.get(cid)
                if last is not None and not getattr(self.channels[cid], "held", lambda: True)():
                    last = None  # repris par le micrologiciel (sortie de veille…) : consigne renvoyée
                # hausse immédiate, baisse par pas de 4 % au moins (pas de pompage autour d'un point)
                if last is None or pct > last or pct <= last - 4 or (c.get("mode") == "fixe" and pct != last):
                    try:
                        self.channels[cid].set(pct)
                        self.applied[cid] = pct
                        self.errors.pop(cid, None)
                    except OSError as exc:
                        self.errors[cid] = str(exc)

    def _loop(self) -> None:
        while not self.stop_event.is_set():
            self.tick()
            self.stop_event.wait(PERIOD)

    def status(self) -> list[dict]:
        if not self.channels:
            self._discover()  # rien trouvé au démarrage (pilote chargé depuis, règle udev posée…)
        out = []
        for cid, ch in self.channels.items():
            c = self.cfg.get("canaux", {}).get(cid, {})
            try:
                pct = ch.percent()
            except (OSError, ValueError):
                pct = None
            out.append({"id": cid, "type": ch.kind, "nom": c.get("nom") or ch.label, "materiel": ch.label, "rpm": ch.rpm(),
                        "pourcent": pct, "mode": c.get("mode", "auto"), "consigne": self.applied.get(cid),
                        "ecriture": self.can_write.get(cid, False), "erreur": self.errors.get(cid)})
        return out


def restore_all() -> list[str]:
    """Tout rendre au micrologiciel sans le démon (après plantage) ; renvoie les erreurs."""
    errors = []
    taken = set(_origins()) | {cid for cid, c in load_config()["canaux"].items() if c.get("mode", "auto") != "auto"}
    for ch in discover():
        if ch.id not in taken:
            continue  # jamais pris en main
        try:
            ch.auto()
        except OSError as exc:
            errors.append(f"{ch.id} : {exc}")
    return errors
