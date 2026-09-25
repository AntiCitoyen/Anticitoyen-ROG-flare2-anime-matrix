"""Listes de lecture et favoris.

~/.config/rog-flare2/listes.json :
    {"Soirée": [{"contenu": "gif:/chemin/a.gif", "duree": 60}, {"contenu": "effet:Plasma", "duree": 120},
                {"show": {...lecture complète...}, "label": "Plasma rapide", "duree": 30}]}
~/.config/rog-flare2/favoris.json :
    [{"label": "Plasma rapide", "show": {...}}, ...]

Le démon joue une liste en boucle ({"type": "liste", "name": "Soirée"}) : chaque élément
pendant sa durée. Contenus : ceux de la programmation (rog_flare2_programme.show_for).
"""
from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from rog_flare2_core import CONFIG_DIR
from rog_flare2_i18n import _

LISTS_FILE = CONFIG_DIR / "listes.json"
FAVORITES_FILE = CONFIG_DIR / "favoris.json"
DEFAULT_SECONDS = 60


def _load(path: Path, default):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, type(default)) else default
    except (OSError, ValueError):
        return default


def _save(path: Path, data) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def load_lists() -> dict[str, list[dict]]:
    return _load(LISTS_FILE, {})


def save_lists(lists: dict[str, list[dict]]) -> None:
    _save(LISTS_FILE, lists)


def load_favorites() -> list[dict]:
    return _load(FAVORITES_FILE, [])


def save_favorites(favorites: list[dict]) -> None:
    _save(FAVORITES_FILE, favorites)


def item_show(item: dict) -> dict | None:
    """Lecture d'un élément de liste (None : écran éteint pendant sa durée)."""
    if isinstance(item.get("show"), dict):
        return item["show"]
    from rog_flare2_programme import show_for
    return show_for(str(item.get("contenu", "horloge")))


def show_label(show: dict | None) -> str:
    """Nom lisible d'une lecture : effet, fichier, horloge…"""
    if not show:
        return _("Écran éteint")
    kind = show.get("type")
    if kind == "effet":
        from rog_flare2_effets import effect_label
        return effect_label(show.get("name", ""))
    if kind == "gif":
        files = show.get("files") or []
        if len(files) == 1:
            return Path(files[0]).name
        return Path(show.get("folder", "")).name or _("Galerie GIF")
    if kind == "horloge":
        return _("Horloge")
    if kind == "liste":
        return _("Liste : {nom}").format(nom=show.get("name", ""))
    if kind == "webcam":
        return _("Webcam")
    if kind == "ecran":
        return _("Miroir d'écran")
    return str(kind)


def item_label(item: dict) -> str:
    if item.get("label"):
        return item["label"]
    from rog_flare2_ui_programme import content_choices
    names = {v: k for k, v in content_choices().items()}
    content = str(item.get("contenu", ""))
    if content in names:
        return names[content]
    if content.startswith("gif:"):
        return Path(content[4:]).name
    return show_label(item_show(item))


class ListsWindow:
    """Fenêtre « Listes de lecture et favoris » du lanceur."""

    def __init__(self, parent, play, current):
        """play(show, status) : lecture par le lanceur ; current() : lecture en cours (ou None)."""
        from rog_flare2_ui_programme import content_choices
        self.play, self.current = play, current
        self.lists = load_lists()
        self.favorites = load_favorites()
        self.choices = content_choices()
        self.win = tk.Toplevel(parent)
        self.win.title(_("Listes de lecture et favoris"))
        body = ttk.Frame(self.win, padding=14)
        body.pack(fill="both", expand=True)

        # Favoris
        ttk.Label(body, text=_("Favoris :")).pack(anchor="w")
        self.fav_frame = ttk.Frame(body)
        self.fav_frame.pack(fill="x", pady=4)
        ttk.Button(body, text=_("★ Ajouter la lecture en cours"), command=self.add_favorite).pack(anchor="w")
        ttk.Separator(body).pack(fill="x", pady=10)

        # Listes
        top = ttk.Frame(body)
        top.pack(fill="x")
        ttk.Label(top, text=_("Liste :")).pack(side="left")
        self.name = tk.StringVar()
        self.picker = ttk.Combobox(top, textvariable=self.name, values=sorted(self.lists), width=22)
        self.picker.pack(side="left", padx=6)
        self.picker.bind("<<ComboboxSelected>>", lambda _e: self.show_items())
        ttk.Button(top, text=_("Nouvelle"), command=self.new_list).pack(side="left")
        ttk.Button(top, text=_("Supprimer"), command=self.delete_list).pack(side="left", padx=4)
        self.items_frame = ttk.Frame(body)
        self.items_frame.pack(fill="x", pady=6)
        add = ttk.Frame(body)
        add.pack(fill="x")
        self.to_add = tk.StringVar(value=next(iter(self.choices)))
        ttk.Combobox(add, textvariable=self.to_add, values=list(self.choices), state="readonly",
                     width=28).pack(side="left")
        ttk.Button(add, text=_("+ Ajouter"), command=self.add_choice).pack(side="left", padx=4)
        ttk.Button(add, text=_("+ Fichier…"), command=self.add_file).pack(side="left")
        ttk.Button(add, text=_("+ Lecture en cours"), command=self.add_current).pack(side="left", padx=4)
        ttk.Label(body, text=_("Durées en secondes ; la liste tourne en boucle."), style="Muted.TLabel").pack(
            anchor="w", pady=(6, 0))
        self.status = ttk.Label(body, text="", style="Muted.TLabel")
        self.status.pack(anchor="w")
        ttk.Button(body, text=_("▶ Lire la liste"), command=self.play_list).pack(fill="x", pady=(8, 0))
        self.rows: list[dict] = []
        if self.lists:
            self.name.set(sorted(self.lists)[0])
        self.show_favorites()
        self.show_items()

    # --- favoris ---
    def show_favorites(self):
        for w in self.fav_frame.winfo_children():
            w.destroy()
        if not self.favorites:
            ttk.Label(self.fav_frame, text=_("Aucun favori"), style="Muted.TLabel").pack(anchor="w")
        for i, fav in enumerate(self.favorites):
            f = ttk.Frame(self.fav_frame)
            f.pack(fill="x", pady=1)
            ttk.Button(f, text="▶", width=3, command=lambda fav=fav: self.play(fav["show"], fav["label"])).pack(
                side="left")
            ttk.Label(f, text=fav.get("label", "?")).pack(side="left", padx=6)
            ttk.Button(f, text="✕", width=3, command=lambda i=i: self.remove_favorite(i)).pack(side="right")

    def add_favorite(self):
        show = self.current()
        if not show:
            self.status.config(text=_("Rien n'est en cours de lecture"))
            return
        self.favorites.append({"label": show_label(show), "show": show})
        save_favorites(self.favorites)
        self.show_favorites()

    def remove_favorite(self, i: int):
        del self.favorites[i]
        save_favorites(self.favorites)
        self.show_favorites()

    # --- listes ---
    def items(self) -> list[dict]:
        return self.lists.setdefault(self.name.get().strip(), []) if self.name.get().strip() else []

    def show_items(self):
        for w in self.items_frame.winfo_children():
            w.destroy()
        self.rows = []
        for item in self.items():
            f = ttk.Frame(self.items_frame)
            f.pack(fill="x", pady=1)
            secs = tk.StringVar(value=str(item.get("duree", DEFAULT_SECONDS)))
            ttk.Label(f, text=item_label(item), width=30).pack(side="left")
            ttk.Entry(f, textvariable=secs, width=6).pack(side="left", padx=4)
            ttk.Button(f, text="✕", width=3, command=lambda item=item: self.remove_item(item)).pack(side="left")
            self.rows.append({"item": item, "secs": secs})

    def _sync_durations(self):
        for row in self.rows:
            try:
                row["item"]["duree"] = max(1, int(float(row["secs"].get())))
            except ValueError:
                pass

    def _append(self, item: dict):
        if not self.name.get().strip():
            self.new_list()
        self._sync_durations()
        self.items().append({**item, "duree": item.get("duree", DEFAULT_SECONDS)})
        self.save()
        self.show_items()

    def add_choice(self):
        self._append({"contenu": self.choices[self.to_add.get()]})

    def add_file(self):
        path = filedialog.askopenfilename(parent=self.win, title=_("Fichier GIF"),
                                          filetypes=[(_("Images"), "*.gif *.png *.jpg *.jpeg *.webp *.bmp")])
        if path:
            self._append({"contenu": f"gif:{path}"})

    def add_current(self):
        show = self.current()
        if not show:
            self.status.config(text=_("Rien n'est en cours de lecture"))
            return
        self._append({"show": show, "label": show_label(show)})

    def remove_item(self, item: dict):
        self._sync_durations()
        self.items().remove(item)
        self.save()
        self.show_items()

    def new_list(self):
        base = _("Liste")
        n = 1
        while f"{base} {n}" in self.lists:
            n += 1
        name = self.name.get().strip()
        if not name or name in self.lists:
            name = f"{base} {n}"
        self.lists[name] = []
        self.name.set(name)
        self.save()
        self.show_items()

    def delete_list(self):
        self.lists.pop(self.name.get().strip(), None)
        self.name.set(sorted(self.lists)[0] if self.lists else "")
        self.save()
        self.show_items()

    def save(self):
        self._sync_durations()
        self.lists = {k: v for k, v in self.lists.items() if k}
        save_lists(self.lists)
        self.picker.configure(values=sorted(self.lists))

    def play_list(self):
        self.save()
        name = self.name.get().strip()
        if not self.lists.get(name):
            self.status.config(text=_("La liste est vide"))
            return
        self.play({"type": "liste", "name": name}, _("Liste : {nom}").format(nom=name))
