"""Fenêtre « Programmation » du lanceur : plages horaires et déclencheurs (rog_flare2_programme)."""
from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

import rog_flare2_programme as prog
from rog_flare2_i18n import _

CONTENT_LABELS = {  # contenu -> texte source déjà traduit ailleurs dans l'interface
    "horloge": "Horloge", "galerie": "Galerie GIF", "moniteur": "System Monitor", "morceau": "Now Playing",
    "eteint": "Écran éteint",
}
HHMM = re.compile(r"^([01]?\d|2[0-3]):[0-5]\d$")


class ScheduleWindow:
    def __init__(self, parent, on_saved):
        self.on_saved = on_saved
        cfg = prog.load_config()
        self.win = tk.Toplevel(parent)
        self.win.title(_("Programmation"))
        self.win.resizable(False, False)
        body = ttk.Frame(self.win, padding=14)
        body.pack(fill="both", expand=True)
        self.triggers = {}
        for key, text in (("verrouillage", "Éteindre l'écran quand la session est verrouillée"),
                          ("veille", "Éteindre l'écran pendant la mise en veille"),
                          ("plein_ecran", "Éteindre l'écran quand une application est en plein écran")):
            var = tk.BooleanVar(value=bool(cfg.get(key)))
            ttk.Checkbutton(body, text=_(text), variable=var).pack(anchor="w")
            self.triggers[key] = var
        ttk.Separator(body).pack(fill="x", pady=10)
        ttk.Label(body, text=_("Plages horaires :")).pack(anchor="w")
        self.rows_frame = ttk.Frame(body)
        self.rows_frame.pack(fill="x", pady=4)
        self.days = [d.strip() for d in _("Lu,Ma,Me,Je,Ve,Sa,Di").split(",")][:7]
        self.labels = {_(src): key for key, src in CONTENT_LABELS.items()}
        self.rows: list[dict] = []
        for rule in cfg.get("regles", []):
            self.add_row(rule)
        ttk.Button(body, text=_("+ Ajouter une plage"), command=self.add_row).pack(anchor="w", pady=(2, 8))
        self.status = ttk.Label(body, text=_("Heures au format HH:MM"), style="Muted.TLabel")
        self.status.pack(anchor="w")
        ttk.Button(body, text=_("Enregistrer"), command=self.save).pack(fill="x", pady=(8, 0))

    def add_row(self, rule: dict | None = None):
        rule = rule or {"debut": "08:00", "fin": "12:00", "jours": list(range(7)), "contenu": "horloge"}
        f = ttk.Frame(self.rows_frame)
        f.pack(fill="x", pady=2)
        row = {"frame": f, "debut": tk.StringVar(value=rule["debut"]), "fin": tk.StringVar(value=rule["fin"]),
               "jours": [tk.BooleanVar(value=d in rule.get("jours", range(7))) for d in range(7)],
               "contenu": tk.StringVar(value=_(CONTENT_LABELS.get(rule.get("contenu"), "Horloge")))}
        ttk.Entry(f, textvariable=row["debut"], width=6).pack(side="left")
        ttk.Label(f, text="→").pack(side="left", padx=2)
        ttk.Entry(f, textvariable=row["fin"], width=6).pack(side="left")
        for i, var in enumerate(row["jours"]):
            ttk.Checkbutton(f, text=self.days[i] if i < len(self.days) else str(i), variable=var).pack(side="left")
        ttk.Combobox(f, textvariable=row["contenu"], values=list(self.labels), state="readonly",
                     width=16).pack(side="left", padx=4)
        ttk.Button(f, text="✕", width=3, command=lambda: self.remove_row(row)).pack(side="left")
        self.rows.append(row)

    def remove_row(self, row: dict):
        row["frame"].destroy()
        self.rows.remove(row)

    def save(self):
        rules = []
        for row in self.rows:
            debut, fin = row["debut"].get().strip(), row["fin"].get().strip()
            if not (HHMM.match(debut) and HHMM.match(fin)):
                self.status.config(text=_("Heures au format HH:MM"))
                return
            rules.append({"debut": debut, "fin": fin, "jours": [d for d, v in enumerate(row["jours"]) if v.get()],
                          "contenu": self.labels.get(row["contenu"].get(), "horloge")})
        cfg = {"regles": rules, **{k: bool(v.get()) for k, v in self.triggers.items()}}
        prog.save_config(cfg)
        self.on_saved()
        self.status.config(text=_("Programmation enregistrée"))
