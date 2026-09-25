"""Simulateur fidèle : géométrie, halo, rendu d'un GIF et fenêtre d'aperçu."""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import rog_flare2_simulateur as S
from rog_flare2_matrix_paint import LED_COUNT


def test_render_size_and_levels():
    dark = np.asarray(S.render(bytes(LED_COUNT)))
    lit = np.asarray(S.render(bytes([255]) * LED_COUNT))
    assert dark.shape == lit.shape and dark.shape[:2][::-1] == S.size()
    assert lit.mean() > 4 * dark.mean()


def test_halo_spreads_light():
    one = bytearray(LED_COUNT)
    one[100] = 255
    dark = np.asarray(S.render(bytes(LED_COUNT)), dtype=float)
    with_halo = np.asarray(S.render(one, halo=True), dtype=float) - dark
    without = np.asarray(S.render(one, halo=False), dtype=float) - dark
    assert with_halo.sum() > without.sum() * 1.3  # lumière qui déborde autour de la LED


def test_full_frame_accepted():
    frame = bytes(4) + bytes([200]) * LED_COUNT + bytes(1024 - 4 - LED_COUNT)
    assert S.render(frame).size == S.size()


def test_cli_writes_preview_gif(tmp_path):
    src = tmp_path / "a.gif"
    frames = [Image.new("L", (19, 24), v) for v in (0, 128, 255)]
    frames[0].save(src, save_all=True, append_images=frames[1:], duration=100, loop=0)
    out = tmp_path / "apercu.gif"
    root = Path(__file__).resolve().parent.parent
    subprocess.run([sys.executable, str(root / "rog_flare2_simulateur.py"), str(src), "-o", str(out)], check=True,
                   capture_output=True)
    with Image.open(out) as im:
        assert im.n_frames == 3 and im.size == S.size()


@pytest.mark.skipif(not os.environ.get("DISPLAY"), reason="affichage X requis")
def test_preview_window(tmp_path):
    import tkinter as tk
    src = tmp_path / "b.gif"
    Image.new("L", (19, 24), 255).save(src)
    root = tk.Tk()
    w = S.PreviewWindow(root, [src, src], lambda: 60, "aperçu")
    root.update()
    w.go(1)
    root.update()
    assert w.index == 1 and w._imagetk is not None
    root.destroy()
