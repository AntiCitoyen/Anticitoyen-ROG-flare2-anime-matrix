"""Bibliothèque : catalogue et GIF servis localement, empreintes, galerie, marquage fidèle."""
import http.server
import json
import os
import shutil
import threading
from pathlib import Path

import pytest

import rog_flare2_bibliotheque as B
from rog_flare2_core import is_faithful

LIB = Path(__file__).resolve().parent.parent / "bibliotheque"


@pytest.fixture
def served(tmp_path, monkeypatch):
    root = tmp_path / "lib"
    shutil.copytree(LIB, root)

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root), **kw)

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    monkeypatch.setattr(B, "BASE_URL", f"http://127.0.0.1:{srv.server_port}/")
    monkeypatch.setattr(B, "LIB_CACHE", tmp_path / "cache")
    yield root
    srv.shutdown()


def test_catalogue_is_consistent():
    cat = json.loads((LIB / "catalogue.json").read_text(encoding="utf-8"))["animations"]
    assert len(cat) >= 10
    for e in cat:
        assert (LIB / e["fichier"]).exists() and e["noms"]["fr"] and e["noms"]["en"] and e["licence"]
        assert is_faithful(LIB / e["fichier"])


def test_fetch_and_verify(served):
    entries = B.fetch_catalogue()
    path = B.fetch_animation(entries[0])
    assert path.exists()
    bad = dict(entries[1], sha256="0" * 64)
    with pytest.raises(OSError):
        B.fetch_animation(bad)


def test_add_to_gallery(served, monkeypatch, tmp_path):
    monkeypatch.setattr(B, "gallery_dir", lambda: tmp_path / "galerie")
    e = B.fetch_catalogue()[0]
    dest = B.add_to_gallery(B.fetch_animation(e), e)
    assert dest.parent == tmp_path / "galerie" and is_faithful(dest)


@pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="affichage X requis")
def test_library_window(served):
    import tkinter as tk
    played = []
    root = tk.Tk()
    w = B.LibraryWindow(root, played.append)
    for _ in range(100):
        root.update()
        if w.entries and w.frames:
            break
        root.after(30)
    assert w.entries and w.frames
    w.on_play()
    assert played and played[0]["fidele"] is True
    root.destroy()


def test_catalogue_entries_are_checked():
    import pytest
    good = {"id": "coeur", "fichier": "gif/coeur.gif", "sha256": "a" * 64}
    assert B.check_entry(good) == "coeur"
    for bad in ({**good, "id": "../../.bashrc"}, {**good, "fichier": "../secret.gif"},
                {**good, "sha256": ""}, {**good, "id": "A B"}):
        with pytest.raises(OSError):
            B.check_entry(bad)
