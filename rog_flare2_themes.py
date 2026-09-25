"""Thèmes de l'interface (ttk) : palettes ROG et palettes roses.

apply(root, nom) restyle tous les widgets ttk à chaud ; le choix est gardé
dans ~/.config/rog-flare2/theme. « System » garde le thème ttk d'origine.
"""
from __future__ import annotations

import os
from pathlib import Path
from tkinter import ttk

THEME_FILE = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "rog-flare2" / "theme"
DEFAULT = "ROG Classic"

# bg : fond ; surface : boutons, onglets ; field : champs ; fg : texte ; muted : texte secondaire ;
# accent : sélection, onglet actif, survol ; accent_fg : texte sur accent ; trough : rail des curseurs
THEMES: dict[str, dict[str, str] | None] = {
    "System": None,
    # ROG
    "ROG Classic": dict(bg="#0e0f12", surface="#1c1e24", field="#16181d", fg="#eceef2", muted="#8a8f99",
                        accent="#e0263a", accent_fg="#ffffff", trough="#2a2d35"),
    "ROG Strix": dict(bg="#101218", surface="#1d2130", field="#161a25", fg="#e8f4ff", muted="#7f8da3",
                      accent="#00c8ff", accent_fg="#001018", trough="#262c3d"),
    "ROG Glitch": dict(bg="#120d1a", surface="#221733", field="#1a1226", fg="#f3eaff", muted="#9a86b5",
                       accent="#ff2bd6", accent_fg="#ffffff", trough="#2f2244"),
    "ROG Gold": dict(bg="#0c0b09", surface="#1d1a14", field="#15130f", fg="#f5ecd8", muted="#9c8f74",
                     accent="#d4a24c", accent_fg="#1a1204", trough="#2b261c"),
    "ROG Carbon": dict(bg="#18191b", surface="#26282b", field="#1f2023", fg="#e6e6e6", muted="#8c8f94",
                       accent="#ff5a1f", accent_fg="#ffffff", trough="#34363a"),
    # Roses
    "Sakura": dict(bg="#fff4f7", surface="#ffe3ec", field="#ffffff", fg="#5b2a3c", muted="#a77a8b",
                   accent="#f06292", accent_fg="#ffffff", trough="#f8cfdc"),
    "Bubblegum": dict(bg="#ffe8f5", surface="#ffcfe9", field="#fff7fc", fg="#4d0f33", muted="#a25b85",
                      accent="#ff1493", accent_fg="#ffffff", trough="#ffb3dc"),
    "Rose Gold": dict(bg="#fbf1ee", surface="#f2dcd6", field="#fffaf8", fg="#4a302c", muted="#9b7a73",
                      accent="#c98a7d", accent_fg="#ffffff", trough="#e8c9c1"),
    "Lavender Rose": dict(bg="#f8f1fb", surface="#ecdcf3", field="#fefbff", fg="#4a2f55", muted="#94799f",
                          accent="#c86fb3", accent_fg="#ffffff", trough="#dfc7ea"),
    "Rose Night": dict(bg="#1d0f18", surface="#2e1826", field="#25131f", fg="#ffe6f2", muted="#b0819b",
                       accent="#ff6fb5", accent_fg="#2a0a1a", trough="#40223a"),
}


def saved() -> str:
    try:
        name = THEME_FILE.read_text().strip()
        if name in THEMES:
            return name
    except OSError:
        pass
    return DEFAULT


def save(name: str) -> None:
    THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
    THEME_FILE.write_text(name + "\n")


def muted_color(root) -> str:
    p = THEMES.get(getattr(root, "_theme_name", DEFAULT))
    return p["muted"] if p else "gray"


def apply(root, name: str) -> None:
    style = ttk.Style(root)
    if not hasattr(root, "_theme_base"):
        root._theme_base = style.theme_use()
        root._theme_bg = root.cget("bg")
    root._theme_name = name
    p = THEMES.get(name)
    if p is None:
        style.theme_use(root._theme_base)
        root.configure(bg=root._theme_bg)
        style.configure("Muted.TLabel", foreground="gray")
        return
    style.theme_use("clam")
    root.configure(bg=p["bg"])
    style.configure(".", background=p["bg"], foreground=p["fg"], fieldbackground=p["field"],
                    troughcolor=p["trough"], bordercolor=p["surface"], lightcolor=p["surface"],
                    darkcolor=p["surface"], focuscolor=p["accent"], selectbackground=p["accent"],
                    selectforeground=p["accent_fg"], insertcolor=p["fg"])
    style.configure("TFrame", background=p["bg"])
    style.configure("TLabel", background=p["bg"], foreground=p["fg"])
    style.configure("Muted.TLabel", background=p["bg"], foreground=p["muted"])
    style.configure("TButton", background=p["surface"], foreground=p["fg"], bordercolor=p["accent"],
                    padding=(10, 5), relief="flat")
    style.map("TButton",
              background=[("disabled", p["bg"]), ("pressed", p["accent"]), ("active", p["accent"])],
              foreground=[("disabled", p["muted"]), ("pressed", p["accent_fg"]), ("active", p["accent_fg"])],
              bordercolor=[("disabled", p["trough"])])
    style.configure("TCheckbutton", background=p["bg"], foreground=p["fg"], indicatorbackground=p["field"],
                    indicatorforeground=p["accent"])
    style.map("TCheckbutton", background=[("active", p["bg"])],
              indicatorbackground=[("selected", p["accent"])], indicatorforeground=[("selected", p["accent_fg"])])
    style.configure("TNotebook", background=p["bg"], bordercolor=p["trough"], tabmargins=(2, 4, 2, 0))
    style.configure("TNotebook.Tab", background=p["surface"], foreground=p["muted"], padding=(10, 4),
                    bordercolor=p["trough"])
    style.map("TNotebook.Tab", background=[("selected", p["accent"]), ("active", p["trough"])],
              foreground=[("selected", p["accent_fg"]), ("active", p["fg"])])
    style.configure("TCombobox", fieldbackground=p["field"], background=p["surface"], foreground=p["fg"],
                    arrowcolor=p["accent"], bordercolor=p["trough"])
    style.map("TCombobox", fieldbackground=[("readonly", p["field"])], foreground=[("readonly", p["fg"])],
              selectbackground=[("readonly", p["field"])], selectforeground=[("readonly", p["fg"])])
    style.configure("TEntry", fieldbackground=p["field"], foreground=p["fg"], bordercolor=p["trough"])
    style.configure("Horizontal.TScale", background=p["accent"], troughcolor=p["trough"],
                    bordercolor=p["bg"], lightcolor=p["accent"], darkcolor=p["accent"])
    style.configure("TSeparator", background=p["trough"])
    # Liste déroulante des combobox (widget Tk classique)
    for opt, val in (("background", p["field"]), ("foreground", p["fg"]),
                     ("selectBackground", p["accent"]), ("selectForeground", p["accent_fg"])):
        root.option_add(f"*TCombobox*Listbox.{opt}", val)

# Couleurs de dessin (interfaces rondes) quand le thème « System » garde le ttk d'origine
SYSTEM_PALETTE = dict(bg="#dcdad5", surface="#eeede9", field="#ffffff", fg="#1f1f1f", muted="#6b6b6b",
                      accent="#4a6984", accent_fg="#ffffff", trough="#bab5ab")


def palette(name: str | None = None) -> dict[str, str]:
    return THEMES.get(name or saved()) or SYSTEM_PALETTE
