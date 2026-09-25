#!/usr/bin/env python3
"""Couleurs et effets des touches du ROG Strix Flare II Animate, sans OpenRGB.

Interface HID 1 (page 0xFF00), rapports de 64 octets, sans numéro de rapport :
  - effets du clavier (gardés en mémoire)   51 2C mode 00 vitesse luminosité mode_couleur direction …
  - enregistrer l'effet                      50 55
  - couleur par touche (mode direct)         C0 81 reste 00 + 15 × (index, R, G, B)
Index d'une touche = colonne × 8 + rangée (30 colonnes, 7 rangées : 210 LED), relevé sur Armoury Crate.
"""
from __future__ import annotations

import json
import os
import threading
import time

from rog_flare2_core import CONFIG_DIR

CONFIG_FILE = CONFIG_DIR / "rgb.json"
LEGACY_FILE = CONFIG_DIR / "openrgb.json"  # réglage des versions ≤ 1.6.0 (OpenRGB)

VID, PID = 0x0B05, 0x19FC
IFACE = 1
REPORT = 64
COLUMNS, ROWS = 30, 7
LEDS = [c * 8 + r for c in range(COLUMNS) for r in range(ROWS)]


class RGBTransport:
    """Accès à l'interface d'éclairage (hidapi, comme l'écran)."""

    def __init__(self, iface: int = IFACE):
        self.iface, self.h = iface, None

    def connect(self) -> str:
        import hid  # type: ignore
        matches = [d for d in hid.enumerate(VID, PID) if d.get("interface_number") == self.iface]
        if not matches:
            raise OSError("ROG Strix Flare II Animate : interface d'éclairage introuvable")
        self.close()
        self.h = hid.device()
        self.h.open_path(matches[0]["path"])
        return repr(matches[0]["path"])

    def write(self, report: bytes) -> int:
        if self.h is None:
            self.connect()
        body = bytes(report)[:REPORT]
        n = self.h.write(b"\x00" + body + bytes(REPORT - len(body)))  # 0x00 : pas de numéro de rapport
        if n < 0:
            raise OSError("écriture HID refusée (éclairage)")
        return n

    def read(self, timeout_ms: int = 20) -> bytes:
        if self.h is None:
            self.connect()
        return bytes(self.h.read(REPORT, max(1, int(timeout_ms))))

    def close(self) -> None:
        if self.h is not None:
            try:
                self.h.close()
            except Exception:
                pass
        self.h = None


class FakeRGBTransport:
    """Clavier factice (ANIMEMATRIX_FAUX_CLAVIER=1)."""

    def __init__(self, *a, **kw):
        self.reports: list[bytes] = []

    def connect(self):
        return "factice"

    def write(self, report):
        self.reports.append(bytes(report)[:REPORT].ljust(REPORT, b"\0"))
        return REPORT + 1

    def read(self, timeout_ms=0):
        return b""

    def close(self):
        pass


def _exchange(t, report: bytes, wait_ms: int = 20) -> bytes:
    """Écrit un rapport et lit la réponse du clavier (les réponses en retard sont vidées avant)."""
    for _ in range(32):
        if not t.read(1):
            break
    t.write(report)
    return t.read(wait_ms)


# ---------- effets du clavier (51 2C) ----------
# nom : (valeur, couleurs par défaut, direction possible) ; valeurs du contrôleur Aura TUF (OpenRGB)
RAINBOW = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (139, 0, 255)]
EFFECTS = {
    "statique": (0, [(255, 0, 0)], False),
    "respiration": (1, [(255, 0, 0)], False),
    "cycle": (2, [], False),
    "reactif": (3, [(255, 0, 0)], False),
    "arc-en-ciel": (4, RAINBOW, True),
    "ondulation": (5, RAINBOW, False),
    "nuit-etoilee": (6, [(255, 255, 255)], False),
    "sable": (7, [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (139, 0, 255)], True),
    "courant": (8, [(0, 127, 255)], False),
    "pluie": (9, [(0, 127, 255)], False),
}
DIRECTIONS = {"gauche": 4, "droite": 0, "haut": 6, "bas": 2, "horizontal": 8, "vertical": 1}


def effect_report(name: str, colors: list[tuple[int, int, int]] | None = None, speed: int = 50,
                  brightness: int = 100, direction: str = "gauche", random: bool = False) -> bytes:
    """Rapport 51 2C : vitesse 0-100 (%), luminosité 0-100 (5 crans), couleurs de l'effet."""
    mode, default, has_direction = EFFECTS[name]
    colors = list(colors or default)
    speed_byte = round(255 - 255 * max(0, min(100, speed)) / 100)  # 255 = lent, 0 = rapide
    level = round(max(0, min(100, brightness)) / 25) * 25
    color_mode = 1 if random else (16 if mode in (1, 3, 6, 8, 9) and len(colors) > 1 and any(colors[1]) else 0)
    body = bytearray([0x51, 0x2C, mode, 0x00, speed_byte, level, color_mode,
                      DIRECTIONS.get(direction, 4) if has_direction else 0, 0x02])
    if mode in (4, 5):  # dégradé : nombre de couleurs, puis (position %, R, G, B)
        body += bytes([len(colors)])
        for i, rgb in enumerate(colors):
            body += bytes([int(100 / len(colors) * (i + 1)), *rgb]) if any(rgb) else bytes(4)
    else:
        for rgb in colors:
            body += bytes(rgb)
    return bytes(body[:REPORT]).ljust(REPORT, b"\0")


def apply_effect(t, name: str, save: bool = True, **kw) -> None:
    """Effet exécuté par le clavier lui-même ; save : gardé après débranchement (50 55)."""
    _exchange(t, effect_report(name, **kw))
    if save:
        _exchange(t, bytes([0x50, 0x55]), 60)


def direct_reports(colors: dict[int, tuple[int, int, int]]) -> list[bytes]:
    """Rapports C0 81 comme Armoury Crate : l'octet 2 compte les entrées qui restent à envoyer."""
    items = sorted(colors.items(), key=lambda kv: (kv[0] % 8, kv[0] // 8))  # rangée par rangée, comme Armoury Crate
    out = []
    for k in range(0, len(items), 15):
        chunk = items[k:k + 15]
        body = bytearray([0xC0, 0x81, len(items) - k, 0x00])
        for index, (r, g, b) in chunk:
            body += bytes([index, r & 255, g & 255, b & 255])
        out.append(bytes(body).ljust(REPORT, b"\0"))
    return out


def send_direct(t, colors: dict[int, tuple[int, int, int]]) -> None:
    for report in direct_reports(colors):
        t.write(report)
    t.read(20)  # accusé C0 82 après une image complète


def firmware(t) -> str:
    """Version du micrologiciel (requête 12 00)."""
    r = _exchange(t, bytes([0x12, 0x00]), 100)
    return f"{r[6]:02X}.{r[5]:02X}.{r[4]:02X}" if len(r) > 6 and r[:2] == b"\x12\x00" else "?"


# ---------- couleurs envoyées par le logiciel (mode direct) ----------

def solid_frame(rgb: tuple[int, int, int], level: float = 1.0) -> dict[int, tuple[int, int, int]]:
    col = tuple(int(v * level) for v in rgb)
    return {i: col for i in LEDS}


def hex_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_hex(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


DEFAULT_CONFIG = {"mode": "clavier", "effet": "arc-en-ciel", "couleurs": [], "vitesse": 50, "luminosite": 100,
                  "direction": "gauche", "aleatoire": False}


def load_config() -> dict:
    """mode : « clavier » (effet exécuté par le clavier), « theme » (couleur du thème),
    « pulsation » (suit la luminosité de l'écran), « off » (rien n'est envoyé)."""
    try:
        return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text(encoding="utf-8"))}
    except (OSError, ValueError):
        pass
    try:  # reprise du réglage OpenRGB
        legacy = json.loads(LEGACY_FILE.read_text(encoding="utf-8")).get("mode")
        if legacy in ("theme", "pulsation"):
            return {**DEFAULT_CONFIG, "mode": legacy}
    except (OSError, ValueError):
        pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")


def effect_kwargs(cfg: dict) -> dict:
    return {"colors": [hex_rgb(c) for c in cfg.get("couleurs") or []] or None, "speed": int(cfg.get("vitesse", 50)),
            "brightness": int(cfg.get("luminosite", 100)), "direction": cfg.get("direction", "gauche"),
            "random": bool(cfg.get("aleatoire"))}


class KeyboardLights:
    """Fil du démon : couleurs des touches selon le réglage (rgb.json)."""

    def __init__(self, screen_level, accent, transport=None):
        self.screen_level = screen_level  # () -> 0..1, luminosité moyenne de l'écran
        self.accent = accent  # () -> "#rrggbb"
        fake = os.environ.get("ANIMEMATRIX_FAUX_CLAVIER")
        self.transport = transport or (FakeRGBTransport() if fake else RGBTransport())
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.status = "off"

    def apply(self, cfg: dict, save: bool = True) -> None:
        """Effet du clavier (enregistré dans le clavier si save)."""
        with self.lock:
            try:
                apply_effect(self.transport, cfg.get("effet", "arc-en-ciel"), save, **effect_kwargs(cfg))
            except OSError:
                self.transport.close()
                raise

    def start(self, cfg: dict):
        self.stop()
        mode = cfg.get("mode", "clavier")
        self.status = mode
        if mode not in ("theme", "pulsation"):
            return
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, args=(cfg, self.stop_event), daemon=True)
        self.thread.start()

    def _run(self, cfg, stop):
        last, accent, accent_at = None, self.accent(), time.monotonic()
        while not stop.is_set():
            if time.monotonic() - accent_at > 1.0:  # thème relu une fois par seconde
                accent, accent_at = self.accent(), time.monotonic()
            level = 0.15 + 0.85 * self.screen_level() if cfg["mode"] == "pulsation" else 1.0
            frame = solid_frame(hex_rgb(accent), level)
            try:
                if frame != last or cfg["mode"] == "theme":  # thème : renvoyé chaque seconde (rebranchement)
                    with self.lock:
                        send_direct(self.transport, frame)
                    last = frame
                    self.status = cfg["mode"]
            except OSError as exc:
                self.status = f"clavier indisponible : {exc}"
                self.transport.close()
                last = None
                stop.wait(3)
            stop.wait(1 / 15 if cfg["mode"] == "pulsation" else 1.0)

    def stop(self):
        was_direct = self.thread is not None
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=3)
        self.thread = None
        if was_direct:  # le clavier reprend l'effet enregistré
            try:
                self.apply(load_config(), save=False)
            except (OSError, KeyError):
                pass
