"""Morceau en cours : lecture MPRIS par D-Bus (faux lecteur) et affichage."""
import os
import shutil
import subprocess
import time

import pytest

import rog_flare2_mpris as M

HAS_GI = subprocess.run(["/usr/bin/python3", "-c", "import gi"], capture_output=True).returncode == 0
pytestmark = pytest.mark.skipif(not (os.environ.get("DBUS_SESSION_BUS_ADDRESS") and shutil.which("gdbus") and HAS_GI),
                                reason="bus de session D-Bus, gdbus et PyGObject requis")


@pytest.fixture
def player():
    proc = subprocess.Popen(["/usr/bin/python3", os.path.join(os.path.dirname(__file__), "fake_mpris.py"),
                             "Café crème", "Aurélie"])
    for _ in range(50):
        if "org.mpris.MediaPlayer2.fauxlecteur" in M.players():
            break
        time.sleep(0.1)
    yield
    proc.terminate()
    proc.wait(3)


def test_now_playing_reads_title_and_artist(player):
    assert M.now_playing() == ("Aurélie", "Café crème")


def test_ascii_upper():
    assert M.ascii_upper("Café crème — ÉTÉ") == "CAFE CREME  ETE"


def test_effect_scrolls_then_visualizes(player, monkeypatch):
    import rog_flare2_effets as E
    monkeypatch.setattr(E.AUDIO, "start", lambda: None)
    M.WATCHER.track, M.WATCHER.changed_at = M.now_playing(), time.monotonic()
    eff = E.make_effect("Now Playing", {"scroll": 3})
    eff.tick(0.05)
    assert eff._text is not None and eff._text.message == "AURELIE - CAFE CREME"
    for _ in range(400):
        eff.tick(0.1)
    assert eff._text is None  # un passage puis le visualiseur
    eff.stop()
