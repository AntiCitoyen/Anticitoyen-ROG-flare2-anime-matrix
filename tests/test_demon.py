"""Démon animematrixd : commandes, surimpression, socket et CLI, sans clavier (transport factice)."""
import base64
import json
import threading
import time

import pytest

import rog_flare2_demon as D


class FakeTransport:
    """Remplace FlareTransport : garde les trames au lieu de les envoyer au clavier."""

    def __init__(self, *a, **kw):
        self.frames = []

    def connect(self):
        return "factice"

    def write(self, frame):
        self.frames.append(frame)
        return len(frame)

    def close(self):
        pass


@pytest.fixture
def daemon(monkeypatch):
    monkeypatch.setattr(D, "FlareTransport", FakeTransport)
    d = D.Daemon()
    yield d
    d.stop()


def leds(d):
    return base64.b64decode(d.handle({"cmd": "frame"})["frame"])


def test_play_effect_and_live_params(daemon):
    assert daemon.handle({"cmd": "play", "show": {"type": "effet", "name": "Plasma", "params": {"speed": 100}}})["ok"]
    time.sleep(0.4)
    assert any(leds(daemon))
    assert daemon.handle({"cmd": "params", "params": {"speed": 300}})["ok"]
    assert daemon.effect.speed == pytest.approx(3.0)
    assert daemon.handle({"cmd": "status"})["show"]["params"]["speed"] == 300


def test_brightness_is_applied_and_saved(daemon):
    daemon.handle({"cmd": "brightness", "value": 20})
    daemon.handle({"cmd": "play", "show": {"type": "effet", "name": "Plasma"}})
    time.sleep(0.4)
    assert max(leds(daemon)) <= 51  # 255 × 20 %
    assert json.loads(D.STATE_FILE.read_text())["brightness"] == 20


def test_notification_overlays_then_returns(daemon):
    daemon.handle({"cmd": "play", "show": {"type": "horloge"}})
    time.sleep(0.3)
    daemon.handle({"cmd": "notify", "text": "SALUT", "duration": 0.6})
    time.sleep(0.2)
    assert daemon.handle({"cmd": "status"})["overlay"] is True
    time.sleep(1.0)
    assert daemon.handle({"cmd": "status"})["overlay"] is False
    assert daemon.handle({"cmd": "status"})["show"]["type"] == "horloge"


def test_stop_blanks_the_screen(daemon):
    daemon.handle({"cmd": "play", "show": {"type": "effet", "name": "Plasma"}})
    time.sleep(0.3)
    daemon.handle({"cmd": "stop"})
    assert daemon.handle({"cmd": "status"})["show"] is None and not any(leds(daemon))


def test_last_show_is_saved_and_start_mode(daemon):
    show = {"type": "effet", "name": "Rain", "params": {}}
    daemon.handle({"cmd": "play", "show": show})
    assert json.loads(D.SHOW_FILE.read_text())["name"] == "Rain"
    daemon.stop()
    D.START_FILE.write_text("derniere\n")
    daemon.start_mode()
    assert daemon.show["name"] == "Rain"


def test_unknown_command(daemon):
    assert daemon.handle({"cmd": "danse"})["ok"] is False


def test_socket_and_ctl(monkeypatch):
    monkeypatch.setattr(D, "FlareTransport", FakeTransport)
    import rog_flare2_ctl as ctl
    D.RUNTIME.mkdir(parents=True, exist_ok=True)
    d = D.Daemon()
    server = D.UnixServer(str(D.SOCKET_PATH), D.Handler)
    server.daemon_ref, d.server = d, server
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        assert ctl.request("ping")["version"]
        ctl.main(["texte", "BONJOUR"])
        assert ctl.request("status")["show"]["params"]["message"] == "BONJOUR"
        ctl.main(["luminosite", "33"])
        assert ctl.request("status")["brightness"] == 33
        ctl.main(["stop"])
        assert ctl.request("status")["show"] is None
        ctl.request("quit")
        t.join(3)
        assert not t.is_alive()
    finally:
        d.stop()
        server.server_close()
        D.SOCKET_PATH.unlink(missing_ok=True)


def test_notification_auto_duration(daemon):
    daemon.handle({"cmd": "notify", "text": "AB", "duration": 0})  # 0 : le temps d'un passage (~2,8 s)
    time.sleep(0.3)
    assert daemon.handle({"cmd": "status"})["overlay"] is True
    time.sleep(3.2)
    assert daemon.handle({"cmd": "status"})["overlay"] is False


def test_config_command_without_notifications(daemon):
    import rog_flare2_notifs as N
    N.save_config({"actif": False, "applis": []})
    assert daemon.handle({"cmd": "config"}) == {"ok": True, "notifications": False}
