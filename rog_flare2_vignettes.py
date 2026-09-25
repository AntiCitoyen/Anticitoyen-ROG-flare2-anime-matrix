"""Galerie en vignettes (rendu fidèle de l'écran) et glisser-déposer de fichiers sur le lanceur.

Vignettes : image du milieu de chaque GIF/vidéo, rendue comme sur le clavier, gardée dans
~/.cache/animematrix/vignettes ; clic : lecture, clic droit : ajout aux favoris.
Glisser-déposer : extension Tcl tkdnd (paquet tkdnd, ou module pip tkinterdnd2).
"""
from __future__ import annotations

import hashlib
import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from rog_flare2_core import CACHE_DIR, VIDEO_EXTENSIONS, image_to_frame, is_faithful, iter_gif_frames
from rog_flare2_i18n import _

THUMBS = CACHE_DIR.parent / "vignettes"
SCALE = 5  # pixels par écart de LED


def thumb_path(path: Path) -> Path:
    st = path.stat()
    key = f"{path.resolve()}|{st.st_size}|{st.st_mtime_ns}|{SCALE}"
    return THUMBS / (hashlib.sha1(key.encode()).hexdigest() + ".png")


def make_thumb(path: Path) -> Path:
    """Vignette PNG (créée au besoin) du milieu de l'animation."""
    out = thumb_path(path)
    if out.exists():
        return out
    from rog_flare2_simulateur import render
    if path.suffix.lower() in VIDEO_EXTENSIONS:
        from rog_flare2_video import preview_frames
        frames = [f for f, _d in preview_frames(path, seconds=2.0)]
    else:
        fidele = is_faithful(path)
        frames = []
        for img, _d in iter_gif_frames(path):
            frames.append(image_to_frame(img, 100, fidele))
            if len(frames) >= 60:  # assez pour trouver une image représentative
                break
    if not frames:
        raise OSError("aucune image")
    lit = max(frames[len(frames) // 3:] or frames, key=lambda f: sum(f[4:316]))  # la plus lumineuse du reste
    THUMBS.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp.png")
    render(lit, scale=SCALE, halo=False).save(tmp)
    tmp.replace(out)
    return out


class ThumbnailWindow:
    """Grille de vignettes d'un dossier ; play(path) au clic, favorite(path) au clic droit."""

    COLS = 5

    def __init__(self, parent, files: list[Path], play, favorite, pick=lambda f: f):
        self.files, self.play, self.favorite, self.pick = files, play, favorite, pick
        self.win = tk.Toplevel(parent)
        self.win.title(_("Galerie en vignettes"))
        self.win.geometry("760x620")
        top = ttk.Frame(self.win, padding=(10, 8))
        top.pack(fill="x")
        self.status = ttk.Label(top, text=_("{n} fichier(s)").format(n=len(files)), style="Muted.TLabel")
        self.status.pack(side="left")
        ttk.Label(top, text=_("Clic : lire · clic droit : favori"), style="Muted.TLabel").pack(side="right")
        import rog_flare2_themes as themes
        self.canvas = tk.Canvas(self.win, highlightthickness=0, background=themes.palette().get("bg", "#16181d"))
        bar = ttk.Scrollbar(self.win, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)
        self.grid = ttk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.grid, anchor="nw")
        self.grid.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.win.bind_all(seq, self._wheel, add="+")
        self.images: dict[int, tk.PhotoImage] = {}
        self.cells: list[ttk.Label] = []
        for i, f in enumerate(files):
            cell = ttk.Frame(self.grid, padding=4)
            cell.grid(row=i // self.COLS, column=i % self.COLS, sticky="n")
            pic = ttk.Label(cell, text="…", width=18, anchor="center")
            pic.pack()
            name = f.stem if len(f.stem) <= 20 else f.stem[:18] + "…"
            ttk.Label(cell, text=name, style="Muted.TLabel").pack()
            for w in (pic, cell):
                w.bind("<Button-1>", lambda _e, f=f: self.play(f))
                w.bind("<Button-3>", lambda _e, f=f: self._fav(f))
            self.cells.append(pic)
        self.results: queue.Queue = queue.Queue()
        self.stop = threading.Event()
        self.win.bind("<Destroy>", lambda e: self.stop.set() if e.widget is self.win else None)
        threading.Thread(target=self._work, daemon=True).start()
        self.win.after(100, self._collect)

    def _wheel(self, event):
        if not self.win.winfo_exists():
            return
        step = -1 if getattr(event, "num", 0) == 4 or getattr(event, "delta", 0) > 0 else 1
        self.canvas.yview_scroll(step * 3, "units")

    def _fav(self, f: Path):
        self.favorite(f)
        self.status.config(text=_("Ajouté aux favoris : {nom}").format(nom=f.name))

    def _work(self):
        for i, f in enumerate(self.files):
            if self.stop.is_set():
                return
            try:
                self.results.put((i, str(make_thumb(self.pick(f)))))
            except (OSError, ValueError):
                self.results.put((i, None))

    def _collect(self):
        if not self.win.winfo_exists():
            return
        try:
            while True:
                i, png = self.results.get_nowait()
                if png:
                    self.images[i] = tk.PhotoImage(file=png)
                    self.cells[i].configure(image=self.images[i], text="", width=0)
                else:
                    self.cells[i].configure(text="✕")
        except queue.Empty:
            pass
        self.win.after(150, self._collect)


def enable_drop(widget, on_paths) -> bool:
    """Accepte les fichiers déposés sur widget (tkdnd) ; False si l'extension manque."""
    try:
        widget.tk.call("package", "require", "tkdnd")
    except tk.TclError:
        try:  # module pip tkinterdnd2 : il embarque tkdnd
            import tkinterdnd2
            base = os.path.join(os.path.dirname(tkinterdnd2.__file__), "tkdnd")
            arch = "linux-x64" if os.uname().machine == "x86_64" else "linux-arm64"
            widget.tk.call("lappend", "auto_path", os.path.join(base, arch))
            widget.tk.call("package", "require", "tkdnd")
        except (ImportError, tk.TclError):
            return False

    def dropped(data):
        paths = [Path(p) for p in widget.tk.splitlist(data)]
        on_paths([p for p in paths if p.exists()])
        return "copy"
    widget.tk.call("tkdnd::drop_target", "register", widget._w, "DND_Files")
    widget.tk.call("bind", widget._w, "<<Drop>>", widget.register(dropped) + " %D")
    return True
