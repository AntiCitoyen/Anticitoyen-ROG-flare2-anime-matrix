#!/usr/bin/env python3
"""Simulateur fidèle de l'écran AniMe Matrix : rendu d'une trame comme sur le clavier.

Géométrie réelle (24 rangées décalées, de 19 à 7 LED ; chaque rangée glisse d'une
demi-case vers la droite), LED blanc chaud, courbe de perception (les faibles
niveaux paraissent plus clairs que leur valeur), halo qui déborde sur les voisines,
trous éteints visibles. Sert à prévisualiser un GIF avant de l'envoyer.

    rog_flare2_simulateur.py entree.gif [-o apercu.gif] [--luminosite 60] [--echelle 14]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_matrix_paint import FB_OFFSET, LED_COUNT, PHYSICAL_CALIBRATED_ORDER  # noqa: E402

X_STEP, Y_STEP, ROW_SHIFT = 1.0, 0.77, 0.52  # en pas de LED (relevé de l'éditeur de dessin)
LED_RGB = np.array([255, 243, 226], dtype=np.float32)  # blanc chaud
HOLE_RGB = np.array([30, 30, 33], dtype=np.float32)
BG_RGB = (12, 12, 14)
GAMMA = 0.55  # perception : 25 % de valeur paraît ~47 %


def _positions(scale: float, margin: float):
    return [(margin + (row * ROW_SHIFT + col * X_STEP) * scale, margin + row * Y_STEP * scale)
            for row, col in PHYSICAL_CALIBRATED_ORDER]


def size(scale: float = 14) -> tuple[int, int]:
    margin = scale
    xs, ys = zip(*_positions(scale, margin))
    return int(max(xs) + margin), int(max(ys) + margin)


def render(leds, scale: float = 14, halo: bool = True) -> Image.Image:
    """Image RGB d'une trame (312 luminosités 0-255, ordre matériel ; ou trame complète de 1024 octets)."""
    leds = bytes(leds)
    if len(leds) > LED_COUNT:
        leds = leds[FB_OFFSET:FB_OFFSET + LED_COUNT]
    w, h = size(scale)
    pos = _positions(scale, scale)
    levels = (np.frombuffer(leds, dtype=np.uint8).astype(np.float32) / 255.0) ** GAMMA

    core = Image.new("L", (w, h), 0)
    glow = Image.new("L", (w, h), 0)
    holes = Image.new("L", (w, h), 0)
    dc, dg, dh = ImageDraw.Draw(core), ImageDraw.Draw(glow), ImageDraw.Draw(holes)
    rc, rg = scale * 0.27, scale * 0.55
    for (x, y), v in zip(pos, levels):
        dh.ellipse([x - rc, y - rc, x + rc, y + rc], fill=255)
        if v > 0:
            dc.ellipse([x - rc, y - rc, x + rc, y + rc], fill=int(255 * v))
            dg.ellipse([x - rg, y - rg, x + rg, y + rg], fill=int(170 * v))
    img = np.full((h, w, 3), BG_RGB, dtype=np.float32)
    img += (np.asarray(holes, dtype=np.float32)[..., None] / 255.0) * (HOLE_RGB - np.array(BG_RGB))
    light = np.asarray(core, dtype=np.float32) / 255.0
    if halo:  # le halo déborde sur les LED voisines, comme sur le vrai clavier
        light = light + np.asarray(glow.filter(ImageFilter.GaussianBlur(scale * 0.45)), dtype=np.float32) / 255.0 * 0.8
    img += np.clip(light, 0, 1.4)[..., None] * LED_RGB
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def main():
    ap = argparse.ArgumentParser(description="Aperçu fidèle d'un GIF/image sur l'AniMe Matrix.")
    ap.add_argument("entree", type=Path)
    ap.add_argument("-o", "--sortie", type=Path, help="GIF animé de l'aperçu (par défaut : entree.apercu.gif)")
    ap.add_argument("--luminosite", type=int, default=60)
    ap.add_argument("--echelle", type=float, default=14)
    args = ap.parse_args()
    from rog_flare2_core import image_to_frame, iter_gif_frames
    frames, durations = [], []
    for img, delay in iter_gif_frames(args.entree):
        frames.append(render(image_to_frame(img, args.luminosite), args.echelle))
        durations.append(int(delay * 1000))
    out = args.sortie or args.entree.with_suffix(".apercu.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print(out)



class PreviewWindow:
    """Fenêtre d'aperçu fidèle d'une liste de GIF/images (lanceur, onglet GIF)."""

    def __init__(self, parent, files: list[Path], brightness, title: str, pick=lambda f: f, fidele: bool = False):
        import tkinter as tk
        from tkinter import ttk

        from PIL import ImageTk
        from rog_flare2_core import image_to_frame, iter_gif_frames
        self._tk, self._imagetk = ImageTk, None
        self.files, self.brightness, self.pick, self.fidele = files, brightness, pick, fidele
        self.image_to_frame, self.iter_gif_frames = image_to_frame, iter_gif_frames
        self.index = 0
        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.resizable(False, False)
        self.label = ttk.Label(self.win)
        self.label.pack(padx=10, pady=(10, 4))
        self.name = ttk.Label(self.win, style="Muted.TLabel")
        self.name.pack()
        nav = ttk.Frame(self.win)
        nav.pack(pady=(4, 10))
        ttk.Button(nav, text="◀", width=4, command=lambda: self.go(-1)).pack(side="left", padx=4)
        ttk.Button(nav, text="▶", width=4, command=lambda: self.go(1)).pack(side="left", padx=4)
        self.win.bind("<Left>", lambda _e: self.go(-1))
        self.win.bind("<Right>", lambda _e: self.go(1))
        self._job = None
        self.go(0)

    def go(self, step: int):
        if not self.files:
            return
        self.index = (self.index + step) % len(self.files)
        src = self.pick(self.files[self.index])
        self.name.config(text=f"{src.name}  ({self.index + 1}/{len(self.files)})")
        try:
            self.frames = [(self.image_to_frame(img, self.brightness(), self.fidele), d)
                           for img, d in self.iter_gif_frames(src)]
        except OSError as exc:
            self.name.config(text=f"{src.name} : {exc}")
            self.frames = []
        self.k = 0
        if self._job is not None:
            self.win.after_cancel(self._job)
        self._next()

    def _next(self):
        if not self.frames or not self.win.winfo_exists():
            return
        frame, delay = self.frames[self.k % len(self.frames)]
        self._imagetk = self._tk.PhotoImage(render(frame))
        self.label.config(image=self._imagetk)
        self.k += 1
        self._job = self.win.after(max(20, int(delay * 1000)), self._next)


if __name__ == "__main__":
    main()
