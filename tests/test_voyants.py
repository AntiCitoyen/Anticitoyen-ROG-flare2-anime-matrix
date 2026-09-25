"""Voyants : micro (pactl simulé), webcam (/proc), OBS (faux serveur obs-websocket 5), affichage par le démon."""
import base64
import hashlib
import json
import os
import socket
import threading
import time

import pytest

import rog_flare2_voyants as V


def test_badges_are_distinct_top_left_blocks():
    leds = [set(V.BADGES[n]) for n in V.ORDER]
    assert all(len(b) >= 3 for b in leds) and not (leds[0] & leds[1]) and not (leds[1] & leds[2])


def test_microphone(monkeypatch):
    answers = {
        ("get-source-mute", "@DEFAULT_SOURCE@"): "Mute: yes\n",
        ("list", "short", "sources"): "59\tsortie.monitor\tx\n60\tmicro-usb\tx\n",
        ("list", "short", "source-outputs"): "7\t4\t12\t59\tfloat32le\n",
    }
    monkeypatch.setattr(V, "_pactl", lambda *a: answers.get(a, ""))
    assert V.mic_muted() and not V.mic_in_use()  # seul un moniteur est enregistré (effets audio)
    answers[("list", "short", "source-outputs")] += "8\t4\t13\t60\ts16le\n"
    assert V.mic_in_use()


def test_webcam_detected_when_a_process_opens_it(tmp_path, monkeypatch):
    cam = tmp_path / "video0"
    cam.write_bytes(b"")
    monkeypatch.setattr(V, "VIDEO_GLOB", str(tmp_path / "video*"))
    assert not V.webcam_in_use()
    with open(cam, "rb"):
        assert V.webcam_in_use()


class FakeObs:
    """Serveur obs-websocket 5 minimal : authentification, GetStreamStatus, GetRecordStatus."""

    def __init__(self, password="secret", streaming=True):
        self.password, self.streaming = password, streaming
        self.srv = socket.socket()
        self.srv.bind(("127.0.0.1", 0))
        self.srv.listen()
        self.port = self.srv.getsockname()[1]
        threading.Thread(target=self.serve, daemon=True).start()

    def serve(self):
        conn, _ = self.srv.accept()
        req = b""
        while b"\r\n\r\n" not in req:
            req += conn.recv(1024)
        key = [line.split(b": ")[1] for line in req.split(b"\r\n") if line.lower().startswith(b"sec-websocket-key")][0]
        accept = base64.b64encode(hashlib.sha1(key + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
        conn.sendall(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                     b"Sec-WebSocket-Accept: " + accept + b"\r\n\r\n")
        salt, challenge = "sel", "defi"
        self.send(conn, {"op": 0, "d": {"rpcVersion": 1, "authentication": {"salt": salt, "challenge": challenge}}})
        secret = base64.b64encode(hashlib.sha256((self.password + salt).encode()).digest()).decode()
        expected = base64.b64encode(hashlib.sha256((secret + challenge).encode()).digest()).decode()
        ident = self.recv(conn)
        if ident["d"].get("authentication") != expected:
            conn.close()
            return
        self.send(conn, {"op": 2, "d": {"negotiatedRpcVersion": 1}})
        while True:
            try:
                msg = self.recv(conn)
            except OSError:
                return
            active = self.streaming if msg["d"]["requestType"] == "GetStreamStatus" else False
            self.send(conn, {"op": 7, "d": {"requestId": msg["d"]["requestId"], "responseData": {"outputActive": active}}})

    @staticmethod
    def send(conn, msg):
        data = json.dumps(msg).encode()
        conn.sendall(bytes([0x81, len(data)]) + data if len(data) < 126 else
                     bytes([0x81, 126]) + len(data).to_bytes(2, "big") + data)

    @staticmethod
    def recv(conn):
        def read(n):
            out = b""
            while len(out) < n:
                chunk = conn.recv(n - len(out))
                if not chunk:
                    raise OSError
                out += chunk
            return out
        b0, b1 = read(2)
        size = b1 & 0x7F
        if size == 126:
            size = int.from_bytes(read(2), "big")
        mask = read(4)
        return json.loads(bytes(b ^ mask[i % 4] for i, b in enumerate(read(size))))


def test_obs_live_with_password():
    obs = FakeObs()
    client = V.ObsClient(obs.port, "secret")
    assert client.live() is True
    client.close()


def test_obs_wrong_password_refused():
    obs = FakeObs()
    with pytest.raises(OSError):
        V.ObsClient(obs.port, "faux")


def test_daemon_draws_badges_and_announces(monkeypatch):
    import rog_flare2_demon as D

    class Fake:
        def __init__(self, *a):
            self.frames = []

        def connect(self):
            return "x"

        def write(self, f):
            self.frames.append(f)
            return len(f)

        def close(self):
            pass
    monkeypatch.setattr(D, "FlareTransport", Fake)
    monkeypatch.setattr(V, "webcam_in_use", lambda: True)
    d = D.Daemon()
    V.save_config({"webcam": True, "annoncer": True})
    d.handle({"cmd": "config"})
    for _ in range(30):
        if d.handle({"cmd": "status"})["voyants"] == ["webcam"] and d.screen.overlay_active:
            break
        time.sleep(0.1)
    assert d.handle({"cmd": "status"})["voyants"] == ["webcam"]
    assert d.screen.overlay_active  # « Webcam active » annoncé
    last = d.screen.last
    assert all(last[D.FB_OFFSET + i] == 255 for i in V.BADGES["webcam"])
    V.save_config({})
    d.handle({"cmd": "config"})
    d.voyants.stop()
    d.stop()
    assert os.path.exists(V.CONFIG_FILE)


def test_badges_window_saves():
    import tkinter as tk
    from rog_flare2_ui_programme import BadgesWindow
    root = tk.Tk()
    saved = []
    w = BadgesWindow(root, lambda: saved.append(1))
    w.mic.set("Quand il est coupé")
    w.obs.set(True)
    w.password.set("pw")
    w.save()
    root.destroy()
    cfg = V.load_config()
    assert saved and cfg["micro"] == "coupe" and cfg["obs"] and cfg["obs_mot_de_passe"] == "pw"
    assert oct(V.CONFIG_FILE.stat().st_mode)[-3:] == "600"
    V.save_config({})
