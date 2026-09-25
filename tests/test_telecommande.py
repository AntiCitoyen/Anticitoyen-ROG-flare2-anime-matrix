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
