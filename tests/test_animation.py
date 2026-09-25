"""Éditeur d'animation : modèle (aller-retour GIF exact, décalage) et interface."""
import os

import pytest

import rog_flare2_animation as A
from rog_flare2_matrix_paint import LED_COUNT


def pattern(k):
    f = A.blank()
    for i in range(0, LED_COUNT, 7 + k):
        f[i] = 255 if i % 2 else 64
    return f


def test_gif_roundtrip_is_exact(tmp_path):
    frames, durations = [pattern(0), pattern(1), pattern(2)], [100, 150, 200]
    A.export_gif(frames, durations, tmp_path / "a.gif")
    got, got_d = A.import_gif(tmp_path / "a.gif")
    assert got == frames and got_d == durations


def test_shift_right_moves_and_drops():
    f = A.blank()
    f[0] = 255  # rangée 0, colonne 0 (coin haut gauche)
    moved = A.shift(f, 1, 0)
    assert moved[0] == 0 and sum(1 for v in moved if v) == 1
    gone = A.shift(A.shift(f, -1, 0), 0, 0)
    assert not any(gone)  # sorti du coin : perdu


@pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="affichage X requis")
def test_editor_ui(tmp_path):
    import tkinter as tk
    root = tk.Tk()
    ed = A.AnimationEditor(root)
    root.update()
    x0, y0, x1, y1 = ed.canvas.coords(ed.items[100])
    ed.canvas.event_generate("<Button-1>", x=int((x0 + x1) / 2), y=int((y0 + y1) / 2))
    assert ed.frames[0][100] == 255
    ed.level.set("faible")
    ed.duplicate()
    assert len(ed.frames) == 2 and ed.index == 1 and ed.frames[1][100] == 255
    ed.copy()
    ed.add()
    ed.paste()
    assert ed.frames[2] == ed.frames[1]
    ed.delete()
    assert len(ed.frames) == 2
    ed.frames[1][5] = 64  # images différentes (Pillow fusionne deux images identiques consécutives)
    ed.export(tmp_path / "e.gif")
    assert A.import_gif(tmp_path / "e.gif")[0] == ed.frames
    root.destroy()
