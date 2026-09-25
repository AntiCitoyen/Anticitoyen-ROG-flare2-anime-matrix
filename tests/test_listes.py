"""Listes de lecture et favoris : fichiers, lecture par le démon, fenêtre."""
import time

import pytest

import rog_flare2_demon as D
import rog_flare2_listes as L


class FakeTransport:
    def __init__(self, *a, **kw):
        pass

    def connect(self):
        return "factice"

    def write(self, frame):
        return len(frame)

    def close(self):
        pass


@pytest.fixture
def daemon(monkeypatch):
    monkeypatch.setattr(D, "FlareTransport", FakeTransport)
    d = D.Daemon()
    yield d
    d.stop()


def test_item_show_and_labels():
    assert L.item_show({"contenu": "horloge"}) == {"type": "horloge"}
    assert L.item_show({"contenu": "eteint"}) is None
    show = {"type": "effet", "name": "Plasma"}
    assert L.item_show({"show": show}) is show
    assert L.show_label(show) == "Plasma" and L.show_label(None) == "Écran éteint"
    assert L.item_label({"contenu": "gif:/x/chat.gif"}) == "chat.gif"


def test_daemon_plays_list_items_in_turn(daemon):
    L.save_lists({"Test": [{"contenu": "effet:Plasma", "duree": 1}, {"contenu": "horloge", "duree": 1}]})
    daemon.handle({"cmd": "play", "show": {"type": "liste", "name": "Test"}})
    seen = set()
    for _ in range(30):
        time.sleep(0.1)
        seen.add(daemon.effect.name if daemon.effect else "horloge")
    assert {"Plasma", "horloge"} <= seen
    daemon.handle({"cmd": "stop"})
    assert daemon.handle({"cmd": "status"})["show"] is None


def test_unknown_list_is_refused(daemon):
    with pytest.raises(ValueError):  # le serveur du socket en fait {"ok": false, "error": ...}
        daemon.handle({"cmd": "play", "show": {"type": "liste", "name": "absente"}})


def test_lists_window(monkeypatch):
    import tkinter as tk
    L.save_lists({})
    L.save_favorites([])
    played = []
    root = tk.Tk()
    w = L.ListsWindow(root, lambda show, status: played.append(show), lambda: {"type": "effet", "name": "Plasma"})
    w.add_favorite()
    w.to_add.set("Horloge")
    w.add_choice()
    w.add_current()
    w.rows[0]["secs"].set("15")
    w.play_list()
    name = w.name.get()
    root.destroy()
    assert L.load_favorites() == [{"label": "Plasma", "show": {"type": "effet", "name": "Plasma"}}]
    assert L.load_lists()[name] == [{"contenu": "horloge", "duree": 15},
                                    {"show": {"type": "effet", "name": "Plasma"}, "label": "Plasma", "duree": 60}]
    assert played == [{"type": "liste", "name": name}]
