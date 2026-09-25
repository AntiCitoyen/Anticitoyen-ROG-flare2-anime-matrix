"""Couleurs du clavier via OpenRGB (serveur SDK, port 6742), synchronisées avec l'écran.

Client minimal du protocole SDK d'OpenRGB (version 0, sans dépendance) :
liste des appareils, passage en mode direct, couleurs des touches. Deux usages (réglage dans le lanceur) :
  - « theme »    : toutes les touches à la couleur d'accent du thème ;
  - « pulsation » : les touches suivent la luminosité moyenne de l'écran.
Réglages : ~/.config/rog-flare2/openrgb.json {"mode": "off"|"theme"|"pulsation", "serveur": true}
"""
from __future__ import annotations

import json
import shutil
import socket
import struct
import subprocess
import threading
import time

from rog_flare2_core import CONFIG_DIR

CONFIG_FILE = CONFIG_DIR / "openrgb.json"
DEVICE_NAME = "Strix Flare II Animate"
PORT = 6742

REQUEST_CONTROLLER_COUNT = 0
REQUEST_CONTROLLER_DATA = 1
SET_CLIENT_NAME = 50
UPDATELEDS = 1050
SETCUSTOMMODE = 1100
UPDATEMODE = 1101


def load_config() -> dict:
    try:
        return {"mode": "off", "serveur": True, **json.loads(CONFIG_FILE.read_text())}
    except (OSError, ValueError):
        return {"mode": "off", "serveur": True}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg))


class Reader:
    def __init__(self, data: bytes):
        self.d, self.i = data, 0

    def take(self, fmt: str):
        v = struct.unpack_from("<" + fmt, self.d, self.i)
        self.i += struct.calcsize("<" + fmt)
        return v[0] if len(v) == 1 else v

    def string(self) -> str:
        n = self.take("H")
        s = self.d[self.i:self.i + n].rstrip(b"\0").decode("utf-8", "replace")
        self.i += n
        return s


def parse_controller(data: bytes) -> dict:
    """Données d'un contrôleur (protocole 0) : nom, modes (bruts, pour la remise), nombre de LED."""
    r = Reader(data)
    r.take("I")  # taille
    ctrl = {"type": r.take("i"), "name": r.string()}
    for _ in range(4):  # description, version, série, emplacement
        r.string()
    n_modes = r.take("H")
    ctrl["active_mode"] = r.take("i")
    modes = []
    for _ in range(n_modes):
        start = r.i
        r.string()
        r.take("iIIIIIIII")  # valeur, drapeaux, vitesses, couleurs min/max, vitesse, direction, mode couleur
        n_colors = r.take("H")  # (r.i += 4 * r.take(…) perdrait l'avance de take)
        r.i += 4 * n_colors
        modes.append(data[start:r.i])
    ctrl["modes"] = modes
    for _ in range(r.take("H")):  # zones : nom, type, LED min/max/nombre, matrice
        r.string()
        r.take("iIII")
        matrix_len = r.take("H")
        r.i += matrix_len
    ctrl["num_leds"] = r.take("H")
    for _ in range(ctrl["num_leds"]):  # nom et valeur de chaque LED
        r.string()
        r.take("I")
    n_colors = r.take("H")
    ctrl["colors"] = [r.take("BBBx") for _ in range(n_colors)]  # couleurs actuelles (remise à l'identique)
    return ctrl


class OpenRGBClient:
    def __init__(self, host: str = "127.0.0.1", port: int = PORT, timeout: float = 3):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self._send(0, SET_CLIENT_NAME, b"AniMe Matrix\0")

    def _send(self, dev: int, pkt: int, payload: bytes = b""):
        self.sock.sendall(b"ORGB" + struct.pack("<III", dev, pkt, len(payload)) + payload)

    def _recv(self) -> tuple[int, bytes]:
        head = self._exact(16)
        _magic, _dev, pkt, size = struct.unpack("<4sIII", head)
        return pkt, self._exact(size)

    def _exact(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise OSError("connexion OpenRGB fermée")
            buf += chunk
        return buf

    def _request(self, dev: int, pkt: int) -> bytes:
        self._send(dev, pkt)
        while True:
            got, data = self._recv()
            if got == pkt:
                return data

    def controllers(self) -> list[dict]:
        count = struct.unpack("<I", self._request(0, REQUEST_CONTROLLER_COUNT))[0]
        return [dict(parse_controller(self._request(i, REQUEST_CONTROLLER_DATA)), index=i) for i in range(count)]

    def find(self, name: str = DEVICE_NAME) -> dict | None:
        return next((c for c in self.controllers() if name.lower() in c["name"].lower()), None)

    def direct(self, dev: int):
        self._send(dev, SETCUSTOMMODE)

    def set_all(self, dev: int, n: int, rgb: tuple[int, int, int]):
        self.set_colors(dev, [rgb] * n)

    def set_colors(self, dev: int, colors: list[tuple[int, int, int]]):
        payload = struct.pack("<H", len(colors)) + b"".join(struct.pack("<BBBx", *c) for c in colors)
        self._send(dev, UPDATELEDS, struct.pack("<I", 4 + len(payload)) + payload)

    def restore_mode(self, dev: int, index: int, mode_block: bytes):
        payload = struct.pack("<i", index) + mode_block
        self._send(dev, UPDATEMODE, struct.pack("<I", 4 + len(payload)) + payload)

    def close(self):
        self.sock.close()


def hex_rgb(color: str) -> tuple[int, int, int]:
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))


class KeyboardSync:
    """Fil du démon : applique le mode choisi.

    OpenRGB ne sait pas lire l'éclairage que le clavier avait avant (il le suppose « direct », tout
    noir) : à l'arrêt, les touches gardent donc la dernière couleur appliquée. L'effet enregistré
    dans le clavier revient en le débranchant puis en le rebranchant.
    """

    def __init__(self, screen_level, accent):
        self.screen_level = screen_level  # () -> 0..1, luminosité moyenne de l'écran
        self.accent = accent  # () -> "#rrggbb"
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.server: subprocess.Popen | None = None
        self.status = "off"

    def _connect(self, cfg) -> OpenRGBClient | None:
        for attempt in range(2):
            try:
                return OpenRGBClient()
            except OSError:
                if attempt == 0 and cfg.get("serveur") and shutil.which("openrgb") and self.server is None:
                    self.server = subprocess.Popen(["openrgb", "--server", "--noautoconnect"],
                                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    for _ in range(40):  # détection des appareils : quelques secondes
                        time.sleep(0.25)
                        try:
                            return OpenRGBClient()
                        except OSError:
                            continue
        return None

    def start(self, cfg: dict):
        self.stop()
        if cfg.get("mode", "off") == "off":
            self.status = "off"
            return
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, args=(cfg, self.stop_event), daemon=True)
        self.thread.start()

    def _run(self, cfg, stop):
        client = self._connect(cfg)
        if client is None:
            self.status = "serveur OpenRGB injoignable"
            return
        try:
            dev = client.find()
            if dev is None:
                self.status = "clavier absent d'OpenRGB"
                return
            i, n = dev["index"], dev["num_leds"]
            client.direct(i)
            self.status = cfg["mode"]
            last = None
            accent, accent_at = self.accent(), time.monotonic()
            while not stop.is_set():
                if time.monotonic() - accent_at > 1.0:  # thème relu une fois par seconde
                    accent, accent_at = self.accent(), time.monotonic()
                rgb = hex_rgb(accent)
                if cfg["mode"] == "pulsation":
                    level = 0.15 + 0.85 * self.screen_level()
                    rgb = tuple(int(c * level) for c in rgb)
                if rgb != last:
                    client.set_all(i, n, rgb)
                    last = rgb
                stop.wait(1 / 15 if cfg["mode"] == "pulsation" else 1.0)
        except (OSError, struct.error, IndexError) as exc:
            self.status = f"erreur OpenRGB : {exc}"
        finally:
            client.close()

    def stop(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=3)
        self.thread = None
