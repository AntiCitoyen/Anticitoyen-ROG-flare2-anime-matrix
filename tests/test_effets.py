"""Effets PolyWollyWin, visualiseurs audio et extensions."""
import threading

import pytest

import rog_flare2_effets as E
from rog_flare2_matrix_paint import FRAME_SIZE, LED_COUNT


@pytest.mark.parametrize("name", sorted(E.EFFECTS) + sorted(E.AUDIO_EFFECTS))
def test_every_effect_renders_312_leds(name, monkeypatch):
    monkeypatch.setattr(E.AUDIO, "start", lambda: None)  # pas de capture audio en test
    effect = E.make_effect(name)
    for _ in range(10):
        raw = effect.tick(1 / 30)
        assert len(raw) == LED_COUNT and all(0 <= v <= 255 for v in raw)
    effect.stop()


def test_led_frame_applies_brightness():
    frame = E.led_frame([200] * LED_COUNT, 50)
    assert len(frame) == FRAME_SIZE and frame[4] == 100


def test_params_are_scaled():
    effect = E.make_effect("Plasma", {"speed": 250})
    assert effect.speed == pytest.approx(2.5)


def test_run_effect_stops(monkeypatch):
    frames = []

    class Sink:
        def write(self, f):
            frames.append(f)

    stop = threading.Event()
    t = threading.Thread(target=E.run_effect, args=(E.make_effect("Rain"), Sink(), stop, lambda: 60))
    t.start()
    stop.wait(0.3)
    stop.set()
    t.join(2)
    assert not t.is_alive() and len(frames) >= 3


def test_plugins_load_and_isolate_errors(tmp_path):
    (tmp_path / "bon.py").write_text(
        "from effects import BaseEffect\n"
        "class Essai(BaseEffect):\n"
        "    name = 'Essai extension'\n"
        "    noms = {'fr': 'Essai'}\n"
        "    def tick(self, dt):\n"
        "        return self._blank()\n")
    (tmp_path / "casse.py").write_text("raise RuntimeError('exprès')\n")
    added = E.load_plugins(tmp_path)
    assert added == ["Essai extension"]
    assert "Essai extension" in E.EFFECTS and E.PLUGIN_NAMES["Essai extension"] == {"fr": "Essai"}
    assert "casse.py" in E.PLUGIN_ERRORS


def test_example_plugin_runs():
    from pathlib import Path
    added = E.load_plugins(Path(__file__).resolve().parent.parent / "examples" / "effets")
    assert "Heartbeat" in added
    assert len(E.make_effect("Heartbeat", {"bpm": 120}).tick(0.1)) == LED_COUNT
