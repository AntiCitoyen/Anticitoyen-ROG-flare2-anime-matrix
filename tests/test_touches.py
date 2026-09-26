"""Touches pour « Réaction au clavier » : noms evdev et lecture par un clavier virtuel (uinput).

Le test ne lit jamais les vrais claviers : l'écouteur ne reçoit que le périphérique virtuel.
"""
import time

import pytest

import rog_flare2_touches as T


def test_evdev_names():
    assert T.evdev_name("KEY_A") == "a" and T.evdev_name("KEY_7") == "7"
    assert T.evdev_name("KEY_SPACE") == "space" and T.evdev_name("KEY_KPENTER") == "penter"
    assert T.evdev_name("KEY_LEFTSHIFT") == "shift" and T.evdev_name("KEY_F1") == "f1" and T.evdev_name("KEY_POWER") is None


class FakeDevice:
    """Périphérique evdev simulé : un tube pour select(), des événements EV_KEY à lire."""

    def __init__(self, events):
        import os
        self.events = events
        self.fd, self._w = os.pipe()
        os.write(self._w, b"x")

    def read(self):
        import os
        os.read(self.fd, 1)
        events, self.events = self.events, []
        return events

    def close(self):
        pass


def test_listener_translates_evdev_events():
    evdev = pytest.importorskip("evdev")
    e = evdev.ecodes

    class Ev:
        def __init__(self, code, value, type=e.EV_KEY):
            self.code, self.value, self.type = code, value, type
    events = [Ev(e.KEY_LEFTSHIFT, 1), Ev(e.KEY_A, 1), Ev(e.KEY_A, 2), Ev(e.KEY_A, 0), Ev(e.KEY_LEFTSHIFT, 0),
              Ev(e.KEY_SPACE, 1), Ev(0, 0, type=e.EV_SYN), Ev(e.KEY_F1, 1)]
    got = []
    listener = T.EvdevListener(lambda n: got.append(("+", n)), lambda n: got.append(("-", n)),
                               devices=[FakeDevice(events)])
    time.sleep(0.3)
    listener.stop()
    assert got == [("+", "shift"), ("+", "a"), ("-", "a"), ("-", "shift"), ("+", "space"), ("+", "f1")]


def test_keyboard_react_lights_the_key(monkeypatch):
    import rog_flare2_effets as E
    monkeypatch.setattr(T, "listen", lambda *_a: None)
    fx = E.EFFECTS["Keyboard React"]()
    assert fx._demo  # sans source de touches : démonstration
    fx._demo = False
    fx._press("a")
    assert max(fx.tick(0.03)) > 0
    fx.stop()
