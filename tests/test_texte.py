"""Effet « Texte » : message libre, sens de défilement au choix."""
import numpy as np
import pytest

import rog_flare2_effets as E
from renderer import physical_to_logical


def centroid_col(leds):
    grid = physical_to_logical(leds).astype(float)
    return (grid.sum(axis=0) * np.arange(grid.shape[1])).sum() / max(1.0, grid.sum())


def centroid_row(leds):
    from rog_flare2_matrix_paint import PHYSICAL_CALIBRATED_ORDER
    rows = np.array([r for r, _c in PHYSICAL_CALIBRATED_ORDER], dtype=float)
    v = np.array(leds, dtype=float)
    return (rows * v).sum() / max(1.0, v.sum())


def frames(direction, message="I", n=40, dt=0.05):
    fx = E.make_effect("Text", {"message": message, "direction": direction})
    return [fx.tick(dt) for _ in range(n)]


@pytest.mark.parametrize("direction,sign", [("gauche", -1), ("droite", 1)])
def test_horizontal_motion(direction, sign):
    lit = [f for f in frames(direction, n=38) if max(f) > 0]  # moins d un tour complet
    assert len(lit) > 5
    assert (centroid_col(lit[-1]) - centroid_col(lit[1])) * sign > 0


@pytest.mark.parametrize("direction,sign", [("haut", -1), ("bas", 1)])
def test_vertical_motion(direction, sign):
    lit = [f for f in frames(direction, n=30) if max(f) > 0]
    assert len(lit) > 5
    assert (centroid_row(lit[-1]) - centroid_row(lit[1])) * sign > 0


def test_fixed_text_does_not_move_and_long_text_scrolls():
    still = frames("fixe", "OK", n=10)
    assert still[0] == still[-1] and max(still[0]) == 255
    long = frames("fixe", "UN TEXTE BIEN TROP LONG", n=10)
    assert long[1] != long[-1]


def test_choice_param_in_launcher_panel():
    import tkinter as tk

    import rog_flare2_launcher as L
    app = L.LauncherApp()
    panel = app.effect_panel
    panel["name"].set(E.effect_label("Text"))
    app._fill_params(panel)
    boxes = [w for row in panel["params"].winfo_children() for w in row.winfo_children()
             if w.winfo_class() == "TCombobox"]
    assert boxes and "Vers le haut" in boxes[0]["values"]
    boxes[0].set("Vers le haut")
    boxes[0].event_generate("<<ComboboxSelected>>")
    assert panel["values"]["direction"].get() == "haut"
    app.destroy()
    assert tk
