"""Portables via asusctl (expérimental) : faux asusctl qui enregistre ses appels."""
import os
import stat
import time

import pytest
from PIL import Image

import rog_flare2_portable as P
from rog_flare2_matrix_paint import FB_OFFSET, FRAME_SIZE, LED_COUNT


@pytest.fixture
def fake_asusctl(tmp_path, monkeypatch):
    log = tmp_path / "appels.txt"
    exe = tmp_path / "bin" / "asusctl"
    exe.parent.mkdir()
    exe.write_text(f'#!/bin/sh\necho "$@" >> {log}\n')
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{exe.parent}:{os.environ['PATH']}")
    return log


def frame(value):
    f = bytearray(FRAME_SIZE)
    f[FB_OFFSET:FB_OFFSET + LED_COUNT] = bytes([value]) * LED_COUNT
    return bytes(f)


def test_default_hardware_is_keyboard():
    assert P.hardware() == "clavier"


def test_png_uses_faithful_geometry(tmp_path):
    P.frame_to_png(frame(255), tmp_path / "a.png", zoom=1)
    img = Image.open(tmp_path / "a.png")
    assert img.size == (19, 24) and img.getpixel((18, 23)) == 255 and img.getpixel((0, 23)) == 0  # coin


def test_transport_calls_asusctl_and_throttles(fake_asusctl, tmp_path):
    t = P.AsusctlTransport(tmp_path)
    t.connect()
    for _ in range(10):
        t.write(frame(200))  # 10 trames d'affilée : une seule image envoyée
    time.sleep(P.MIN_INTERVAL + 0.05)
    t.write(frame(100))
    t.write(frame(0))  # écran noir : effacement
    calls = fake_asusctl.read_text().splitlines()
    assert calls[0] == "anime --enable-display true"
    assert sum(1 for c in calls if c.startswith("anime image --path")) == 2
    assert calls[-1] == "anime --clear"


def test_daemon_selects_laptop_backend(monkeypatch):
    import rog_flare2_demon as D
    P.HARDWARE_FILE.parent.mkdir(parents=True, exist_ok=True)
    P.HARDWARE_FILE.write_text("portable-asusctl")
    try:
        assert isinstance(D.Screen().transport, P.AsusctlTransport)
    finally:
        P.HARDWARE_FILE.unlink()
