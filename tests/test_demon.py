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


def test_migration_from_legacy_dangling_link(tmp_path, monkeypatch):
    """Paquet ≤ 1.3 → 1.4 : l'unité a disparu mais le lien d'activation reste ; le mode est repris."""
    wants = D.CONFIG_DIR.parent / "systemd" / "user" / "default.target.wants"
    wants.mkdir(parents=True, exist_ok=True)
    (wants / "animematrix-horloge.service").symlink_to("/usr/lib/systemd/user/animematrix-horloge.service")
    D.START_FILE.unlink(missing_ok=True)
    assert D.migrate_legacy() == "horloge"
    assert D.START_FILE.read_text().strip() == "horloge"
    assert not (wants / "animematrix-horloge.service").is_symlink()


def test_identical_frames_are_not_resent(daemon, monkeypatch):
    screen = daemon.screen
    frame = bytes(D.BLANK[:4]) + bytes([9]) * 312 + bytes(1024 - 316)
    for _ in range(5):
        screen.write(frame)
    assert screen.transport.frames.count(frame) == 1 and screen.skipped >= 4
    monkeypatch.setattr(D, "KEEPALIVE", 0.0)  # au-delà du délai, la même trame repart
    screen.write(frame)
    assert screen.transport.frames.count(frame) == 2


def test_old_daemon_is_replaced_after_an_update(monkeypatch):
    """Après une mise à jour du paquet, l'ancien démon (autre version) est arrêté puis relancé."""
    monkeypatch.setattr(D, "FlareTransport", FakeTransport)
    import rog_flare2_ctl as ctl
    D.RUNTIME.mkdir(parents=True, exist_ok=True)
    d = D.Daemon()
    monkeypatch.setattr(D, "VERSION", "0.0.1")  # le démon en cours se présente comme ancien
    server = D.UnixServer(str(D.SOCKET_PATH), D.Handler)
    server.daemon_ref, d.server = d, server
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    started = []
    import subprocess
    import types
    # module subprocess propre à ctl : patcher subprocess.Popen lui-même casserait les autres fils
    monkeypatch.setattr(ctl, "subprocess", types.SimpleNamespace(
        Popen=lambda *a, **kw: started.append(a), run=subprocess.run, DEVNULL=subprocess.DEVNULL,
        SubprocessError=subprocess.SubprocessError))
    try:
        assert ctl.ensure_daemon(wait=0.5) is False  # nouveau démon « lancé » (factice) mais muet
        t.join(3)
        assert not t.is_alive() and started  # l'ancien a reçu quit, un nouveau a été lancé
    finally:
        d.stop()
        server.server_close()
        D.SOCKET_PATH.unlink(missing_ok=True)


def test_http_api_refuses_browser_requests():
    ok = D.local_request_allowed
    json_ct = {"Host": "127.0.0.1:8765", "Content-Type": "application/json"}
    assert ok(json_ct) and ok({**json_ct, "Host": "localhost:8765"}) and ok({**json_ct, "Host": "[::1]:8765"})
    assert not ok({**json_ct, "Origin": "https://exemple.org"})  # page web (CSRF)
    assert not ok({**json_ct, "Content-Type": "text/plain"})  # formulaire sans pré-vol CORS
    assert not ok({**json_ct, "Host": "attaquant.exemple:8765"})  # DNS rebinding
    assert not ok({"Host": "127.0.0.1"})


def test_runtime_dir_must_be_private(tmp_path, monkeypatch):
    d = tmp_path / "run"
    d.mkdir(mode=0o755)
    d.chmod(0o755)
    monkeypatch.setattr(D, "RUNTIME", d)
    with pytest.raises(SystemExit):
        D.check_runtime_dir()
    d.chmod(0o700)
    D.check_runtime_dir()


def test_release_resumes_when_the_editor_dies(daemon):
    import subprocess
    proc = subprocess.Popen(["sleep", "0.5"])
    daemon.handle({"cmd": "release", "pid": proc.pid})
    assert daemon.screen.released
    proc.wait()
    time.sleep(1.5)
    assert not daemon.screen.released  # l'éditeur a disparu sans « resume » : l'écran est rendu


def test_hold_really_switches_the_panel_off(monkeypatch):
    class EchoTransport(FakeTransport):
        def read(self, size=1024, timeout_ms=0):
            return b""
    monkeypatch.setattr(D, "FlareTransport", EchoTransport)
    d = D.Daemon()
    try:
        d.screen.write(bytes(D.PREFIX) + bytes([0, 0, 9]) + bytes(1019), "base")
        d.screen.hold("verrouillage", True)
        sent = d.screen.transport.frames
        assert sent[-1][:6] == bytes.fromhex("60a88700ff00")  # panneau éteint
        d.screen.hold("verrouillage", False)
        assert sent[-2][:6] == bytes.fromhex("60a88764ff00") and sent[-1][D.FB_OFFSET] == 9  # rallumé, image rendue
    finally:
        d.stop()
