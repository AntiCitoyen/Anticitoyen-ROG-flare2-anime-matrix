"""Programmation horaire et déclencheurs."""
import datetime
import time

import pytest

import rog_flare2_programme as P

MONDAY_9H = datetime.datetime(2026, 9, 21, 9, 0)  # lundi


def test_active_rule_day_and_hours():
    rules = [{"debut": "08:00", "fin": "12:00", "jours": [0, 1, 2, 3, 4], "contenu": "horloge"}]
    assert P.active_rule(rules, MONDAY_9H)["contenu"] == "horloge"
    assert P.active_rule(rules, MONDAY_9H.replace(hour=12)) is None
    assert P.active_rule(rules, MONDAY_9H + datetime.timedelta(days=5)) is None  # samedi


def test_overnight_rule():
    rules = [{"debut": "22:00", "fin": "07:00", "jours": [4], "contenu": "eteint"}]  # vendredi soir
    friday_23h = datetime.datetime(2026, 9, 25, 23, 0)
    assert P.active_rule(rules, friday_23h)
    assert P.active_rule(rules, friday_23h + datetime.timedelta(hours=7))  # samedi 6 h : suite de vendredi
    assert P.active_rule(rules, friday_23h + datetime.timedelta(hours=8)) is None


def test_invalid_rules_are_ignored():
    assert P.active_rule([{"debut": "xx", "fin": "12:00"}], MONDAY_9H) is None


def test_show_for():
    assert P.show_for("horloge") == {"type": "horloge"}
    assert P.show_for("moniteur")["name"] == "System Monitor"
    assert P.show_for("eteint") is None


def test_monitor_parses_booleans():
    got = []
    m = P.Monitor([], "ActiveChanged", got.append)
    lines = ["signal time=1 sender=:1.2 -> destination=(null) interface=org.cinnamon.ScreenSaver; member=ActiveChanged\n",
             "   boolean true\n", "signal ... member=ActiveChanged\n", "   boolean false\n"]

    class Proc:
        stdout = iter(lines)
    m._loop(Proc)
    assert got == [True, False]


@pytest.fixture
def daemon(monkeypatch):
    import rog_flare2_demon as D
    from tests.test_demon import FakeTransport
    monkeypatch.setattr(D, "FlareTransport", FakeTransport)
    d = D.Daemon()
    yield d
    d.stop()


def test_hold_blanks_then_resumes(daemon):
    daemon.handle({"cmd": "play", "show": {"type": "effet", "name": "Plasma"}})
    time.sleep(0.3)
    daemon.handle({"cmd": "hold", "reason": "verrouillage", "on": True})
    time.sleep(0.2)
    assert not any(daemon.screen.last[4:316]) and daemon.handle({"cmd": "status"})["hold"] == ["verrouillage"]
    daemon.handle({"cmd": "hold", "reason": "verrouillage", "on": False})
    time.sleep(0.3)
    assert any(daemon.screen.last[4:316])


def test_rule_applies_then_restores_manual_show(daemon):
    daemon.handle({"cmd": "play", "show": {"type": "effet", "name": "Rain"}})
    daemon.programme.cfg = {"regles": [{"debut": "08:00", "fin": "12:00", "contenu": "horloge"}]}
    daemon.programme.tick(MONDAY_9H)
    assert daemon.show == {"type": "horloge"} and daemon.handle({"cmd": "status"})["regle"] == "horloge"
    daemon.programme.tick(MONDAY_9H.replace(hour=13))
    assert daemon.show["name"] == "Rain"  # fin de plage : la lecture manuelle reprend


@pytest.mark.skipif(not __import__("os").environ.get("DISPLAY"), reason="affichage X requis")
def test_schedule_window_saves():
    import tkinter as tk
    from rog_flare2_ui_programme import ScheduleWindow
    P.save_config({"regles": [], "verrouillage": False})
    root = tk.Tk()
    saved = []
    w = ScheduleWindow(root, lambda: saved.append(True))
    w.triggers["verrouillage"].set(True)
    w.add_row()
    w.rows[0]["debut"].set("25:00")  # heure invalide : refusée
    w.save()
    assert not saved
    w.rows[0]["debut"].set("21:30")
    w.rows[0]["jours"][6].set(False)
    w.save()
    root.destroy()
    cfg = P.load_config()
    assert saved and cfg["verrouillage"] is True
    assert cfg["regles"] == [{"debut": "21:30", "fin": "12:00", "jours": [0, 1, 2, 3, 4, 5], "contenu": "horloge"}]


def test_profile_has_priority_over_rule_then_restores():
    played, ended = [], []
    p = P.Programme(played.append, lambda: ended.append(1), lambda *_a: None)
    p.cfg = {"regles": [{"debut": "00:00", "fin": "23:59", "contenu": "horloge"}],
             "profils": [{"app": "steam_app", "contenu": "effet:Plasma"}]}
    now = datetime.datetime(2026, 9, 25, 12, 0)
    game = {"app": "steam_app_570", "title": "Dota 2", "fullscreen": True}
    p.tick(now, game)
    assert played[-1] == {"type": "effet", "name": "Plasma", "params": {}}
    p.tick(now, game)
    assert len(played) == 1  # rien de nouveau tant que la fenêtre ne change pas
    p.tick(now, {"app": "firefox", "title": "x", "fullscreen": False})
    assert played[-1] == {"type": "horloge"}  # retour à la plage horaire
    p.cfg["regles"] = []
    p.tick(now, None)
    assert ended  # plus rien : lecture manuelle


def test_match_profile_by_title():
    assert P.match_profile([{"app": "Blender"}], {"app": "blender", "title": ""})
    assert P.match_profile([{"app": "dota"}], {"app": "steam_app_570", "title": "Dota 2"})
    assert P.match_profile([{"app": ""}], {"app": "x", "title": "y"}) is None


def test_schedule_window_saves_profiles():
    import tkinter as tk
    from rog_flare2_ui_programme import ScheduleWindow
    P.save_config({"profils": [{"app": "blender", "contenu": "effet:Plasma"}]})
    root = tk.Tk()
    w = ScheduleWindow(root, lambda: None)
    assert w.profiles[0]["contenu"].get() == "Effet : Plasma"
    w.add_profile()
    w.profiles[1]["app"].set("steam_app")
    w.profiles[1]["contenu"].set("Moniteur système")
    w.save()
    root.destroy()
    assert P.load_config()["profils"] == [{"app": "blender", "contenu": "effet:Plasma"},
                                          {"app": "steam_app", "contenu": "moniteur"}]


def test_rule_keys_preset_follows_the_rule():
    import datetime
    import rog_flare2_programme as P
    seen = []
    prog = P.Programme(lambda show: None, lambda: None, lambda *a: None, seen.append)
    prog.cfg = {"regles": [{"debut": "08:00", "fin": "09:00", "contenu": "horloge", "touches": "eteint"}]}
    prog.tick(datetime.datetime(2026, 9, 28, 8, 30))
    prog.tick(datetime.datetime(2026, 9, 28, 8, 31))  # même règle : rien de renvoyé
    prog.tick(datetime.datetime(2026, 9, 28, 10, 0))
    assert seen == ["eteint", None]
