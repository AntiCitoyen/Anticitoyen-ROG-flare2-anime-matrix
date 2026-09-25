#!/usr/bin/env python3
"""Éditeur d'animation image par image pour l'AniMe Matrix.

Dessin LED par LED sur la vraie géométrie du coin (3 niveaux : faible, plein,
gomme), frise d'images (ajouter, dupliquer, supprimer, copier/coller, durée),
calque fantôme de l'image précédente, décalage du dessin, aperçu animé, envoi au
clavier par le démon, export et ouverture de GIF en géométrie fidèle (une LED =
un pixel de 19 × 24 : l'aller-retour est exact).

    rog_flare2_animation.py [fichier.gif]
"""
from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_i18n import _  # noqa: E402
from rog_flare2_core import FAITHFUL_TAG  # noqa: E402
from rog_flare2_matrix_paint import LED_COUNT, PHYSICAL_CALIBRATED_ORDER  # noqa: E402

W, H = 19, 24
LEVELS = {"faible": 64, "plein": 255, "gomme": 0}
ROW_SHIFT, Y_STEP = 0.52, 0.77  # géométrie réelle (voir rog_flare2_simulateur)


# ---------- modèle (sans Tk, testé) ----------
def blank() -> bytearray:
    return bytearray(LED_COUNT)


def to_image(leds: bytes):
    """Trame (312 valeurs, ordre matériel) -> image L 19 × 24, géométrie fidèle (une LED = un pixel)."""
    from PIL import Image
    img = Image.new("L", (W, H), 0)
    px = img.load()
    for (row, col), v in zip(PHYSICAL_CALIBRATED_ORDER, leds):
        px[(row + 1) // 2 + col, row] = v
    return img


def from_image(img) -> bytearray:
    from rog_flare2_core import image_to_frame
    from rog_flare2_matrix_paint import FB_OFFSET
    return bytearray(image_to_frame(img, 100, fidele=True)[FB_OFFSET:FB_OFFSET + LED_COUNT])


def export_gif(frames: list[bytes], durations: list[int], path: Path) -> None:
    """GIF 19 × 24 ; deux images identiques consécutives sont fusionnées par Pillow (durées additionnées)."""
    images = [to_image(f) for f in frames]
    images[0].save(path, save_all=True, append_images=images[1:], duration=durations, loop=0, disposal=1,
                   comment=FAITHFUL_TAG)


def import_gif(path: Path) -> tuple[list[bytearray], list[int]]:
    from rog_flare2_core import iter_gif_frames
    frames, durations = [], []
    for img, delay in iter_gif_frames(path):
        frames.append(from_image(img))
        durations.append(max(20, int(delay * 1000)))
    return frames, durations


def shift(leds: bytes, dx: int, dy: int) -> bytearray:
    """Décale le dessin sur la grille fidèle (ce qui sort du coin est perdu)."""
    img = to_image(leds)
    from PIL import ImageChops
    moved = ImageChops.offset(img, dx, dy)
    px = moved.load()
    if dx > 0:
        for x in range(dx):
            for y in range(H):
                px[x, y] = 0
    elif dx < 0:
        for x in range(W + dx, W):
            for y in range(H):
                px[x, y] = 0
    if dy > 0:
        for y in range(dy):
            for x in range(W):
                px[x, y] = 0
    elif dy < 0:
        for y in range(H + dy, H):
            for x in range(W):
                px[x, y] = 0
    return from_image(moved)


# ---------- interface ----------
class AnimationEditor:
    SCALE = 24

    def __init__(self, parent=None, path: Path | None = None):
        import rog_flare2_themes as themes
        self.root = tk.Toplevel(parent) if parent is not None else tk.Tk()
        if parent is None:
            themes.apply(self.root, themes.saved())
        self.p = themes.palette()
        self.root.title(_("Éditeur d'animation"))
        self.frames: list[bytearray] = [blank()]
        self.durations: list[int] = [150]
        self.index = 0
        self.clipboard: bytearray | None = None
        self.level = tk.StringVar(value="plein")
        self.onion = tk.BooleanVar(value=True)
        self.playing = False
        self.path = path
        self._build()
        if path is not None:
            self.open(path)
        self.redraw()

    def _build(self):
        r = self.root
        tools = ttk.Frame(r, padding=(10, 8, 10, 0))
        tools.pack(fill="x")
        for key, label in (("faible", _("Faible")), ("plein", _("Plein")), ("gomme", _("Gomme"))):
            ttk.Radiobutton(tools, text=label, value=key, variable=self.level).pack(side="left", padx=(0, 6))
        ttk.Checkbutton(tools, text=_("Calque fantôme"), variable=self.onion, command=self.redraw).pack(side="left", padx=8)
        for text, dx, dy in (("←", -1, 0), ("→", 1, 0), ("↑", 0, -1), ("↓", 0, 1)):
            ttk.Button(tools, text=text, width=3, command=lambda dx=dx, dy=dy: self.move(dx, dy)).pack(side="left")
        ttk.Button(tools, text=_("Effacer"), command=self.clear).pack(side="left", padx=(8, 0))
        width = int((23 * ROW_SHIFT + W) * self.SCALE + 2 * self.SCALE)
        height = int(23 * Y_STEP * self.SCALE + 2 * self.SCALE)
        self.canvas = tk.Canvas(r, width=width, height=height, bg=self.p["bg"], highlightthickness=0)
        self.canvas.pack(padx=10, pady=8)
        self.items = []
        rad = self.SCALE * 0.36
        for idx, (row, col) in enumerate(PHYSICAL_CALIBRATED_ORDER):
            x = self.SCALE + (row * ROW_SHIFT + col) * self.SCALE
            y = self.SCALE + row * Y_STEP * self.SCALE
            item = self.canvas.create_oval(x - rad, y - rad, x + rad, y + rad, width=2)
            self.items.append(item)
        self.item_index = {item: i for i, item in enumerate(self.items)}
        for ev in ("<Button-1>", "<B1-Motion>"):
            self.canvas.bind(ev, self.paint)
        timeline = ttk.Frame(r, padding=(10, 0, 10, 8))
        timeline.pack(fill="x")
        for text, cmd in (("◀", lambda: self.go(-1)), ("▶", lambda: self.go(1)), (_("+ Image"), self.add),
                          (_("Dupliquer"), self.duplicate), (_("Supprimer"), self.delete)):
            ttk.Button(timeline, text=text, command=cmd).pack(side="left", padx=(0, 4))
        ttk.Label(timeline, text=_("Durée (ms) :")).pack(side="left", padx=(8, 2))
        self.duration_var = tk.IntVar(value=150)
        spin = ttk.Spinbox(timeline, from_=20, to=5000, increment=10, width=6, textvariable=self.duration_var,
                           command=self._duration_changed)
        spin.pack(side="left")
        spin.bind("<FocusOut>", lambda _e: self._duration_changed())
        self.pos_label = ttk.Label(timeline, style="Muted.TLabel")
        self.pos_label.pack(side="left", padx=8)
        actions = ttk.Frame(r, padding=(10, 0, 10, 10))
        actions.pack(fill="x")
        self.play_btn = ttk.Button(actions, text=_("▶ Aperçu"), command=self.toggle_play)
        self.play_btn.pack(side="left", padx=(0, 4))
        ttk.Button(actions, text=_("⌨ Sur le clavier"), command=self.send).pack(side="left", padx=4)
        ttk.Button(actions, text=_("Ouvrir…"), command=self.ask_open).pack(side="right")
        ttk.Button(actions, text=_("Exporter en GIF…"), command=self.ask_export).pack(side="right", padx=4)
        self.status = ttk.Label(r, style="Muted.TLabel")
        self.status.pack(pady=(0, 8))
        r.bind("<Left>", lambda _e: self.go(-1))
        r.bind("<Right>", lambda _e: self.go(1))
        r.bind("<Control-c>", lambda _e: self.copy())
        r.bind("<Control-v>", lambda _e: self.paste())
        r.bind("<space>", lambda _e: self.toggle_play())

    # ---------- dessin ----------
    def _color(self, v: int, ghost: bool) -> tuple[str, str]:
        from rog_flare2_ui_ronde import mix
        fill = "#%02x%02x%02x" % mix(self.p["trough"], self.p["accent"], v / 255) if v else self.p["surface"]
        outline = self.p["muted"] if ghost else self.p["trough"]
        return fill, outline

    def redraw(self):
        cur = self.frames[self.index]
        prev = self.frames[self.index - 1] if self.onion.get() and self.index > 0 else None
        for i, item in enumerate(self.items):
            fill, outline = self._color(cur[i], ghost=bool(prev and prev[i] and not cur[i]))
            self.canvas.itemconfigure(item, fill=fill, outline=outline)
        self.duration_var.set(self.durations[self.index])
        self.pos_label.config(text=f"{self.index + 1} / {len(self.frames)}")

    def paint(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        i = self.item_index.get(item[0]) if item else None
        if i is None:
            return
        self.frames[self.index][i] = LEVELS[self.level.get()]
        fill, outline = self._color(self.frames[self.index][i], False)
        self.canvas.itemconfigure(self.items[i], fill=fill, outline=outline)

    def clear(self):
        self.frames[self.index] = blank()
        self.redraw()

    def move(self, dx, dy):
        self.frames[self.index] = shift(self.frames[self.index], dx, dy)
        self.redraw()

    # ---------- frise ----------
    def go(self, step: int):
        self.index = (self.index + step) % len(self.frames)
        self.redraw()

    def add(self):
        self.frames.insert(self.index + 1, blank())
        self.durations.insert(self.index + 1, self.durations[self.index])
        self.go(1)

    def duplicate(self):
        self.frames.insert(self.index + 1, bytearray(self.frames[self.index]))
        self.durations.insert(self.index + 1, self.durations[self.index])
        self.go(1)

    def delete(self):
        if len(self.frames) > 1:
            del self.frames[self.index]
            del self.durations[self.index]
            self.index = min(self.index, len(self.frames) - 1)
        else:
            self.frames[0] = blank()
        self.redraw()

    def copy(self):
        self.clipboard = bytearray(self.frames[self.index])

    def paste(self):
        if self.clipboard is not None:
            self.frames[self.index] = bytearray(self.clipboard)
            self.redraw()

    def _duration_changed(self):
        try:
            self.durations[self.index] = max(20, int(self.duration_var.get()))
        except (tk.TclError, ValueError):
            pass

    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.config(text=_("■ Arrêter l'aperçu") if self.playing else _("▶ Aperçu"))
        if self.playing:
            self._tick()

    def _tick(self):
        if not self.playing or not self.root.winfo_exists():
            return
        self.go(1)
        self.root.after(self.durations[self.index], self._tick)

    # ---------- fichiers ----------
    def open(self, path: Path):
        self.frames, self.durations = import_gif(path)
        self.index, self.path = 0, path
        self.status.config(text=str(path))
        self.redraw()

    def export(self, path: Path):
        export_gif(self.frames, self.durations, path)
        self.path = path
        self.status.config(text=_("Exporté : {path}").format(path=path))

    def ask_open(self):
        path = filedialog.askopenfilename(parent=self.root, filetypes=[("GIF", "*.gif")])
        if path:
            self.open(Path(path))

    def ask_export(self):
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension=".gif", filetypes=[("GIF", "*.gif")])
        if path:
            self.export(Path(path))

    def send(self):
        """Joue l'animation sur le clavier (démon), en géométrie fidèle."""
        from rog_flare2_maj import CACHE_DIR
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = CACHE_DIR / "editeur.gif"
        export_gif(self.frames, self.durations, path)
        try:
            import rog_flare2_ctl as ctl
            ctl.ensure_daemon()
            ctl.request("play", show={"type": "gif", "files": [str(path)], "loop": True, "converted": False,
                                      "fidele": True})
            self.status.config(text=_("Animation envoyée au clavier"))
        except Exception as exc:
            self.status.config(text=_("Erreur : {err}").format(err=exc))


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    AnimationEditor(None, path).root.mainloop()


if __name__ == "__main__":
    main()
