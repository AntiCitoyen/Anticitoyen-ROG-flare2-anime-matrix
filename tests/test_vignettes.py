"""Galerie en vignettes et glisser-déposer."""
import time
import tkinter as tk

import pytest
from PIL import Image

import rog_flare2_vignettes as V


def make_gif(path, n=4):
    frames = [Image.new("L", (40, 30), 60 * i) for i in range(n)]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=40, loop=0)
    return path


def test_thumbnail_is_cached(tmp_path):
    gif = make_gif(tmp_path / "a.gif")
    png = V.make_thumb(gif)
    assert png.exists() and Image.open(png).size[0] > 50
    mtime = png.stat().st_mtime_ns
    assert V.make_thumb(gif) == png and png.stat().st_mtime_ns == mtime


def test_thumbnail_window_fills_and_clicks(tmp_path):
    files = [make_gif(tmp_path / f"{i}.gif") for i in range(3)]
    (tmp_path / "casse.gif").write_bytes(b"pas un gif")
    files.append(tmp_path / "casse.gif")
    root = tk.Tk()
    played, favs = [], []
    w = V.ThumbnailWindow(root, files, played.append, favs.append)
    for _ in range(60):
        root.update()
        if len(w.images) == 3 and w.cells[3].cget("text") == "✕":
            break
        time.sleep(0.05)
    assert len(w.images) == 3 and w.cells[3].cget("text") == "✕"
    w.cells[1].event_generate("<Button-1>")
    w.cells[2].event_generate("<Button-3>")
    root.update()
    root.destroy()
    assert played == [files[1]] and favs == [files[2]]


def test_drop_target(tmp_path):
    root = tk.Tk()
    got = []
    if not V.enable_drop(root, got.extend):
        root.destroy()
        pytest.skip("tkdnd absent")
    gif = make_gif(tmp_path / "d.gif")
    # simulation d'un dépôt : le script lié à <<Drop>> reçoit la liste Tcl des chemins (%D)
    script = root.tk.call("bind", root._w, "<<Drop>>").replace("%D", "{%s}" % gif)
    assert root.tk.eval(script) == "copy"
    root.destroy()
    assert got == [gif]
