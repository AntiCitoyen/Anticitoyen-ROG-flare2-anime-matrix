"""Bibliothèque communautaire d'animations pour l'AniMe Matrix.

Le catalogue (bibliotheque/catalogue.json du dépôt GitHub) liste des GIF 19 × 24
avec leur empreinte SHA-256 ; le lanceur les montre, les télécharge (empreinte
vérifiée), les joue sur le clavier ou les ajoute à la galerie. Partager une
animation : formulaire de ticket GitHub (aucun compte à configurer ici).
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import threading
import urllib.request
import webbrowser
from pathlib import Path

from rog_flare2_core import VERSION, gallery_dir
from rog_flare2_i18n import LANG, _
from rog_flare2_maj import CACHE_DIR, REPO

BASE_URL = f"https://raw.githubusercontent.com/{REPO}/main/bibliotheque/"
SHARE_URL = f"https://github.com/{REPO}/issues/new?template=partage-animation.yml"
LIB_CACHE = CACHE_DIR / "bibliotheque"


def fetch_catalogue(base_url: str | None = None, timeout: float = 8) -> list[dict]:
    req = urllib.request.Request((base_url or BASE_URL) + "catalogue.json", headers={"User-Agent": f"animematrix/{VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r).get("animations", [])


def display_name(entry: dict) -> str:
    noms = entry.get("noms", {})
    return noms.get(LANG) or noms.get("en") or entry.get("id", "?")


MAX_ANIMATION = 16 * 1024 * 1024
SAFE_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")
SAFE_FILE = re.compile(r"[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*\.gif")


def check_entry(entry: dict) -> str:
    """Identifiant sûr comme nom de fichier ; lève OSError pour une entrée de catalogue douteuse."""
    ident, fichier = str(entry.get("id", "")), str(entry.get("fichier", ""))
    if not SAFE_ID.fullmatch(ident) or not SAFE_FILE.fullmatch(fichier) \
            or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
        raise OSError(_("entrée de catalogue invalide : {name}").format(name=ident[:40] or "?"))
    return ident


def fetch_animation(entry: dict, base_url: str | None = None, timeout: float = 15) -> Path:
    """GIF de l'animation dans le cache (téléchargé une fois, empreinte SHA-256 vérifiée)."""
    ident = check_entry(entry)
    LIB_CACHE.mkdir(parents=True, exist_ok=True)
    dest = LIB_CACHE / f"{ident}.gif"
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == entry.get("sha256"):
        return dest
    req = urllib.request.Request((base_url or BASE_URL) + entry["fichier"], headers={"User-Agent": f"animematrix/{VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(MAX_ANIMATION + 1)
    if len(data) > MAX_ANIMATION:
        raise OSError(_("animation trop volumineuse : paquet rejeté"))
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise OSError(_("empreinte SHA-256 différente de celle publiée : paquet rejeté"))
    dest.write_bytes(data)
    return dest


def add_to_gallery(path: Path, entry: dict) -> Path:
    folder = gallery_dir()
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / f"{check_entry(entry)}.gif"
    shutil.copyfile(path, dest)
    return dest


class LibraryWindow:
    """Fenêtre « Bibliothèque » : liste, aperçu fidèle animé, jouer, ajouter à la galerie, partager."""

    def __init__(self, parent, play):
        import tkinter as tk
        from tkinter import ttk
        self.play = play  # play(show) : lecture par le démon
        self.entries: list[dict] = []
        self.frames: list = []
        self._job = None
        self.win = tk.Toplevel(parent)
        self.win.title(_("Bibliothèque d'animations"))
        body = ttk.Frame(self.win, padding=12)
        body.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(body, height=14, width=26, exportselection=False)
        self.listbox.grid(row=0, column=0, rowspan=4, sticky="ns")
        self.listbox.bind("<<ListboxSelect>>", lambda _e: self.select())
        self.preview = ttk.Label(body)
        self.preview.grid(row=0, column=1, padx=12)
        self.info = ttk.Label(body, style="Muted.TLabel")
        self.info.grid(row=1, column=1)
        buttons = ttk.Frame(body)
        buttons.grid(row=2, column=1, pady=6)
        ttk.Button(buttons, text=_("⌨ Sur le clavier"), command=self.on_play).pack(side="left", padx=3)
        ttk.Button(buttons, text=_("⬇ Ajouter à ma galerie"), command=self.on_add).pack(side="left", padx=3)
        ttk.Button(body, text=_("Partager une animation…"), command=lambda: webbrowser.open(SHARE_URL)).grid(
            row=3, column=1, sticky="ew")
        self.status = ttk.Label(self.win, text=_("Chargement du catalogue…"), style="Muted.TLabel")
        self.status.pack(pady=(0, 8))
        self._pending = None
        threading.Thread(target=self._load, daemon=True).start()
        self._poll()

    def _load(self):
        try:
            self._pending = ("ok", fetch_catalogue())
        except (OSError, ValueError) as exc:
            self._pending = ("err", exc)

    def _poll(self):
        if not self.win.winfo_exists():
            return
        if self._pending is not None:
            kind, value = self._pending
            self._pending = None
            if kind == "ok":
                self.entries = value
                for e in value:
                    self.listbox.insert("end", display_name(e))
                self.status.config(text=_("{n} animations").format(n=len(value)))
                if value:
                    self.listbox.selection_set(0)
                    self.select()
            else:
                self.status.config(text=_("Catalogue injoignable : {err}").format(err=value))
        self.win.after(100, self._poll)

    def current(self) -> dict | None:
        sel = self.listbox.curselection()
        return self.entries[sel[0]] if sel else None

    def select(self):
        entry = self.current()
        if entry is None:
            return
        self.info.config(text=f"{entry.get('auteur', '?')} · {entry.get('licence', '?')}")

        def worker():
            try:
                path = fetch_animation(entry)
                from rog_flare2_core import image_to_frame, iter_gif_frames
                frames = [(image_to_frame(img, 80, entry.get("fidele", True)), d) for img, d in iter_gif_frames(path)]
                self._pending_frames = (entry["id"], frames)
            except OSError as exc:
                self._pending_frames = (entry["id"], exc)
        self._pending_frames = None
        threading.Thread(target=worker, daemon=True).start()
        self._wait_frames(entry["id"])

    def _wait_frames(self, key):
        if not self.win.winfo_exists():
            return
        pending = getattr(self, "_pending_frames", None)
        if pending is None or pending[0] != key:
            self.win.after(50, lambda: self._wait_frames(key))
            return
        if isinstance(pending[1], Exception):
            self.status.config(text=_("Erreur : {err}").format(err=pending[1]))
            return
        self.frames, self.k = pending[1], 0
        if self._job is not None:
            self.win.after_cancel(self._job)
        self._animate()

    def _animate(self):
        from PIL import ImageTk
        from rog_flare2_simulateur import render
        if not self.frames or not self.win.winfo_exists():
            return
        frame, delay = self.frames[self.k % len(self.frames)]
        self._img = ImageTk.PhotoImage(render(frame, scale=11))
        self.preview.config(image=self._img)
        self.k += 1
        self._job = self.win.after(max(20, int(delay * 1000)), self._animate)

    def on_play(self):
        entry = self.current()
        if entry is None:
            return
        try:
            path = fetch_animation(entry)
            self.play({"type": "gif", "files": [str(path)], "loop": True, "converted": False,
                       "fidele": entry.get("fidele", True)})
            self.status.config(text=_("Lecture : {name}").format(name=display_name(entry)))
        except OSError as exc:
            self.status.config(text=_("Erreur : {err}").format(err=exc))

    def on_add(self):
        entry = self.current()
        if entry is None:
            return
        try:
            dest = add_to_gallery(fetch_animation(entry), entry)
            self.status.config(text=_("Ajouté à la galerie : {path}").format(path=dest))
        except OSError as exc:
            self.status.config(text=_("Erreur : {err}").format(err=exc))
