"""Voyants d'état sur l'écran : micro coupé ou en cours d'utilisation, webcam utilisée, OBS en direct.

Chaque voyant allumé est un bloc de 2 × 2 LED en haut à gauche de l'écran, par-dessus la
lecture (1 : micro, 2 : webcam, 3 : OBS) ; à chaque changement, un court texte l'annonce.

~/.config/rog-flare2/voyants.json :
    {"micro": "coupe" | "actif" | "", "webcam": true, "obs": true,
     "obs_port": 4455, "obs_mot_de_passe": "", "annoncer": true}

- micro : PipeWire/PulseAudio (pactl) ; « coupe » : source par défaut coupée,
  « actif » : une application enregistre le micro (hors moniteurs de sortie) ;
- webcam : un de vos programmes a ouvert /dev/video* (lecture de /proc) ;
- OBS : obs-websocket 5 (OBS 28 et plus : Outils → Paramètres du serveur WebSocket).
"""
from __future__ import annotations

import base64
import glob
import hashlib
import json
import os
import socket
import subprocess
import threading

from rog_flare2_core import CONFIG_DIR
from rog_flare2_matrix_paint import PHYSICAL_CALIBRATED_ORDER

CONFIG_FILE = CONFIG_DIR / "voyants.json"
ORDER = ("micro", "webcam", "obs")
C_ENV = {**os.environ, "LC_ALL": "C"}


def load_config() -> dict:
    base = {"micro": "", "webcam": False, "obs": False, "obs_port": 4455, "obs_mot_de_passe": "", "annoncer": True}
    try:
        return {**base, **json.loads(CONFIG_FILE.read_text())}
    except (OSError, ValueError):
        return base


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=1))
    CONFIG_FILE.chmod(0o600)  # mot de passe OBS éventuel


def _badge_leds(slot: int) -> list[int]:
    """Indices matériels du bloc 2 × 2 du voyant n° slot (géométrie fidèle, rangées 0-1)."""
    xs = {1 + slot * 3, 2 + slot * 3}
    return [i for i, (row, col) in enumerate(PHYSICAL_CALIBRATED_ORDER)
            if row in (0, 1) and (row + 1) // 2 + col in xs]


BADGES = {name: _badge_leds(i) for i, name in enumerate(ORDER)}


# ---------------------------------------------------------------- micro
def _pactl(*args: str) -> str:
    try:
        return subprocess.run(["pactl", *args], capture_output=True, text=True, timeout=3, env=C_ENV).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def mic_muted() -> bool:
    return _pactl("get-source-mute", "@DEFAULT_SOURCE@").strip().lower().endswith("yes")


def mic_in_use() -> bool:
    """Une application enregistre une vraie entrée (les moniteurs de sortie, comme nos effets audio, ne comptent pas)."""
    sources = {}
    for line in _pactl("list", "short", "sources").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            sources[parts[0]] = parts[1]
    for line in _pactl("list", "short", "source-outputs").splitlines():
        parts = line.split("\t")
        if len(parts) >= 4 and not sources.get(parts[3], ".monitor").endswith(".monitor"):
            return True
    return False


# ---------------------------------------------------------------- webcam
VIDEO_GLOB = "/dev/video*"


def webcam_in_use() -> bool:
    devices = {os.path.realpath(p) for p in glob.glob(VIDEO_GLOB)}
    if not devices:
        return False
    for fd_dir in glob.glob("/proc/[0-9]*/fd"):
        try:
            for fd in os.listdir(fd_dir):
                try:
                    if os.readlink(f"{fd_dir}/{fd}") in devices:
                        return True
                except OSError:
                    continue
        except OSError:  # processus d'un autre utilisateur ou terminé
            continue
    return False


# ---------------------------------------------------------------- OBS (obs-websocket 5)
class ObsClient:
    """Client WebSocket minimal (RFC 6455, trames texte) pour GetStreamStatus / GetRecordStatus."""

    def __init__(self, port: int = 4455, password: str = "", host: str = "127.0.0.1"):
        self.sock = socket.create_connection((host, port), timeout=3)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET / HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                           "Sec-WebSocket-Protocol: obswebsocket.json\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = self.sock.recv(1024)
            if not chunk:
                raise OSError("connexion fermée")
            head += chunk
        if b" 101 " not in head.split(b"\r\n", 1)[0]:
            raise OSError("obs-websocket a refusé la connexion")
        self._buf = head.split(b"\r\n\r\n", 1)[1]
        hello = self.recv()
        identify = {"rpcVersion": 1, "eventSubscriptions": 0}
        auth = (hello.get("d") or {}).get("authentication")
        if auth:
            secret = base64.b64encode(hashlib.sha256((password + auth["salt"]).encode()).digest()).decode()
            identify["authentication"] = base64.b64encode(
                hashlib.sha256((secret + auth["challenge"]).encode()).digest()).decode()
        self.send({"op": 1, "d": identify})
        if self.recv().get("op") != 2:
            raise OSError("obs-websocket : identification refusée (mot de passe ?)")
        self._n = 0

    def _read(self, n: int) -> bytes:
        while len(self._buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise OSError("connexion fermée")
            self._buf += chunk
        data, self._buf = self._buf[:n], self._buf[n:]
        return data

    def recv(self) -> dict:
        while True:
            b0, b1 = self._read(2)
            size = b1 & 0x7F
            if size == 126:
                size = int.from_bytes(self._read(2), "big")
            elif size == 127:
                size = int.from_bytes(self._read(8), "big")
            payload = self._read(size)
            if b0 & 0x0F == 1:
                return json.loads(payload)
            if b0 & 0x0F == 8:
                raise OSError("connexion fermée par OBS")

    def send(self, msg: dict):
        data = json.dumps(msg).encode()
        mask = os.urandom(4)
        n = len(data)
        head = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + n.to_bytes(2, "big"))
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def request(self, kind: str) -> dict:
        self._n += 1
        rid = str(self._n)
        self.send({"op": 6, "d": {"requestType": kind, "requestId": rid}})
        while True:
            msg = self.recv()
            if msg.get("op") == 7 and msg["d"].get("requestId") == rid:
                return msg["d"].get("responseData") or {}

    def live(self) -> bool:
        return bool(self.request("GetStreamStatus").get("outputActive")
                    or self.request("GetRecordStatus").get("outputActive"))

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


# ---------------------------------------------------------------- surveillance
class Watcher:
    """Fil du démon : relit les états toutes les 2 s ; on_change(états) quand l'un change."""

    def __init__(self, on_change, announce):
        self.on_change, self.announce = on_change, announce
        self.cfg = load_config()
        self.states = {name: False for name in ORDER}
        self.stop_event = threading.Event()
        self.obs: ObsClient | None = None

    def start(self, cfg: dict) -> dict:
        self.stop()
        self.cfg, self.stop_event = cfg, threading.Event()
        if cfg.get("micro") or cfg.get("webcam") or cfg.get("obs"):
            threading.Thread(target=self._loop, args=(self.stop_event,), daemon=True).start()
        else:
            self._set({name: False for name in ORDER})
        return self.states

    def _obs_live(self) -> bool:
        try:
            if self.obs is None:
                self.obs = ObsClient(int(self.cfg.get("obs_port", 4455)), self.cfg.get("obs_mot_de_passe", ""))
            return self.obs.live()
        except (OSError, ValueError, KeyError):
            if self.obs is not None:
                self.obs.close()
            self.obs = None  # OBS fermé : on réessaie au tour suivant
            return False

    def read(self) -> dict:
        mic = self.cfg.get("micro")
        return {"micro": (mic_muted() if mic == "coupe" else mic_in_use() if mic == "actif" else False),
                "webcam": bool(self.cfg.get("webcam")) and webcam_in_use(),
                "obs": bool(self.cfg.get("obs")) and self._obs_live()}

    def _set(self, states: dict):
        changed = {k: v for k, v in states.items() if self.states.get(k) != v}
        self.states = states
        if changed:
            self.on_change(states)
            if self.cfg.get("annoncer", True):
                for name, on in changed.items():
                    if on:
                        self.announce(name)

    def _loop(self, stop):
        while not stop.is_set():
            self._set(self.read())
            stop.wait(2)

    def stop(self):
        self.stop_event.set()
        if self.obs is not None:
            self.obs.close()
            self.obs = None
