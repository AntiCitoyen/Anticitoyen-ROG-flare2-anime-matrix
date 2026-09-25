"""Cadrans d'horloge et texte toutes écritures."""
import datetime
import time

import pytest

import rog_flare2_effets as E
import rog_flare2_horloges as H
import rog_flare2_texte as T


def test_faces_render_312_leds():
    for name in ("Analog Clock", "Binary Clock", "Word Clock"):
        fx = E.make_effect(name)
        for _ in range(40):
            leds = fx.tick(0.1)
        assert len(leds) == 312 and max(leds) > 0, name


def test_binary_clock_bits(monkeypatch):
    class FakeDT(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 9, 25, 13, 45, 7)
    monkeypatch.setattr(H.datetime, "datetime", FakeDT)
    from renderer import physical_to_logical
    grid = physical_to_logical(E.make_effect("Binary Clock", {"dim": 0}).tick(0))
    on = lambda digit, bit: grid[9 - bit * 2, 20 + digit * 3] == 255  # noqa: E731
    assert [on(1, b) for b in range(4)] == [True, True, False, False]  # 3 = 0011
    assert [on(3, b) for b in range(4)] == [True, False, True, False]  # 5 = 0101
    assert [on(5, b) for b in range(4)] == [True, True, True, False]  # 7 = 0111


@pytest.mark.parametrize("lang,h,m,expected", [
    ("fr", 10, 20, "IL EST DIX HEURES VINGT"), ("fr", 0, 2, "IL EST MINUIT"),
    ("fr", 12, 47, "IL EST UNE HEURE MOINS LE QUART"), ("en", 9, 30, "IT IS HALF PAST NINE"),
    ("de", 1, 0, "ES IST EIN UHR"), ("de", 7, 25, "ES IST FÜNF VOR HALB ACHT"),
    ("es", 1, 15, "ES LA UNA Y CUARTO"), ("it", 13, 55, "SONO LE DUE MENO CINQUE"),
    ("pt", 2, 50, "FALTAM DEZ PARA AS TRÊS"), ("nl", 3, 40, "HET IS TIEN OVER HALF VIER"),
    ("ja", 8, 5, "IT IS FIVE PAST EIGHT"),
])
def test_word_clock(lang, h, m, expected):
    assert H.words_for(lang, h, m) == expected


def test_text_folds_accents_and_renders_other_scripts():
    assert T.fold("é") == "E" and T.fold("Œ") == "OE" and T.fold("ж") == ""
    latin = T.render("ÉTÉ")
    assert latin.shape == (12, 15) and latin.max() == 255  # 3 caractères de 4 + 1
    cyr = T.render("Жук")
    assert cyr.shape[0] == 12 and cyr.max() > 0
    if T.font_file(ord("日")):
        cjk = T.render("日本")
        assert cjk[0].any() or cjk[-1].any() or cjk.shape[1] >= 16  # pleine hauteur


def test_daemon_clock_face(monkeypatch):
    import rog_flare2_demon as D

    class Fake:
        def __init__(self, *a):
            pass

        def connect(self):
            return "x"

        def write(self, f):
            return len(f)

        def close(self):
            pass
    monkeypatch.setattr(D, "FlareTransport", Fake)
    H.save_face("binaire")
    d = D.Daemon()
    d.handle({"cmd": "play", "show": {"type": "horloge"}})
    time.sleep(0.3)
    assert d.effect is not None and d.effect.name == "Binary Clock"
    d.stop()
    H.save_face("numerique")
