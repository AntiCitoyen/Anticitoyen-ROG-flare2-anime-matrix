"""Télécommande web : jeton exigé, page servie, commandes transmises au démon."""
import json
import time
import urllib.error
import urllib.request

import pytest

import rog_flare2_demon as D
import rog_flare2_telecommande as R


class Fake:
    def __init__(self, *a):
        pass

    def connect(self):
        return "x"

    def write(self, f):
        return len(f)

    def close(self):
        pass


@pytest.fixture
def remote(monkeypatch):
    monkeypatch.setattr(D, "FlareTransport", Fake)
    d = D.Daemon()
    cfg = R.load_config()
    cfg.update(actif=True, port=0)  # port 0 : choisi par le système
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        cfg["port"] = s.getsockname()[1]
    assert d.remote.start(cfg)
    yield d, cfg
    d.remote.stop()
    d.stop()


def call(cfg, body, token):
    req = urllib.request.Request(f"http://127.0.0.1:{cfg['port']}/api", data=json.dumps(body).encode(),
                                 headers={"X-Jeton": token, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


def test_token_required(remote):
    _d, cfg = remote
    with pytest.raises(urllib.error.HTTPError) as err:
        call(cfg, {"cmd": "status"}, "mauvais")
    assert err.value.code == 403


def test_page_and_commands(remote):
    d, cfg = remote
    html = urllib.request.urlopen(f"http://127.0.0.1:{cfg['port']}/", timeout=5).read().decode()
    assert "AniMe Matrix" in html and "Horloge" in html and cfg["jeton"] not in html
    cat = call(cfg, {"cmd": "catalogue"}, cfg["jeton"])
    assert len(cat["leds"]) == 312 and ["Plasma", "Plasma"] in cat["effets"]
    assert call(cfg, {"cmd": "play", "show": {"type": "horloge"}}, cfg["jeton"])["ok"]
    time.sleep(0.2)
    assert call(cfg, {"cmd": "status"}, cfg["jeton"])["show"] == {"type": "horloge"}
    call(cfg, {"cmd": "brightness", "value": 30}, cfg["jeton"])
    assert d.brightness() == 30


def test_token_file_is_private_and_url_has_token():
    cfg = R.load_config()
    assert oct(R.CONFIG_FILE.stat().st_mode)[-3:] == "600" and len(cfg["jeton"]) >= 20
    assert R.url(cfg).endswith("#" + cfg["jeton"])
    old = cfg["jeton"]
    assert R.new_token() != old


def test_remote_only_allows_safe_commands(monkeypatch):
    import rog_flare2_listes as L
    fav = {"type": "gif", "files": ["/home/x/a.gif"], "loop": True}
    monkeypatch.setattr(L, "load_favorites", lambda: [{"label": "a", "show": fav}])
    ok = R.remote_allowed
    assert ok({"cmd": "play", "show": {"type": "horloge"}}) and ok({"cmd": "brightness", "value": 3})
    assert ok({"cmd": "play", "show": dict(fav)})  # un favori : oui
    for bad in ({"cmd": "memoire", "file": "/etc/shadow"}, {"cmd": "quit"}, {"cmd": "config"},
                {"cmd": "rgb", "config": {}}, {"cmd": "release"}, {"cmd": "hold", "on": True},
                {"cmd": "play", "show": {"type": "gif", "files": ["/home/x/.ssh/id_ed25519"]}},
                {"cmd": "play", "show": {"type": "webcam"}}, {"cmd": "play", "show": {"type": "ecran"}},
                {"cmd": "play", "show": "horloge"}, ["play"]):
        assert not ok(bad), bad
