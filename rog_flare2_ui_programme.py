"""Fenêtre « Programmation » du lanceur : déclencheurs, profils par application et plages horaires."""
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


def content_choices() -> dict[str, str]:
    """Libellé affiché -> contenu : contenus de base, listes de lecture, puis chaque effet."""
    from rog_flare2_effets import AUDIO_EFFECTS, EFFECTS, effect_label
    choices = {_(src): key for key, src in CONTENT_LABELS.items()}
    try:
        from rog_flare2_listes import load_lists
        for name in load_lists():
            choices[_("Liste : {nom}").format(nom=name)] = f"liste:{name}"
    except ImportError:
        pass
    for name in [*EFFECTS, *AUDIO_EFFECTS]:
        choices.setdefault(_("Effet : {nom}").format(nom=effect_label(name)), f"effet:{name}")
    return choices


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
        self.labels = content_choices()
        self.keys = {v: k for k, v in self.labels.items()}
        ttk.Separator(body).pack(fill="x", pady=10)
        ttk.Label(body, text=_("Profils par application (prioritaires) :")).pack(anchor="w")
        self.profiles_frame = ttk.Frame(body)
        self.profiles_frame.pack(fill="x", pady=4)
        self.profiles: list[dict] = []
        for profile in cfg.get("profils", []):
            self.add_profile(profile)
        ttk.Button(body, text=_("+ Ajouter un profil"), command=self.add_profile).pack(anchor="w", pady=(2, 0))
        ttk.Label(body, text=_("Texte contenu dans le nom ou le titre de la fenêtre ; « Détecter » lit la fenêtre "
                               "active au bout de 3 secondes."), style="Muted.TLabel", wraplength=520).pack(anchor="w")
        ttk.Separator(body).pack(fill="x", pady=10)
        ttk.Label(body, text=_("Plages horaires :")).pack(anchor="w")
        self.rows_frame = ttk.Frame(body)
        self.rows_frame.pack(fill="x", pady=4)
        self.days = [d.strip() for d in _("Lu,Ma,Me,Je,Ve,Sa,Di").split(",")][:7]
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
               "contenu": tk.StringVar(value=self.keys.get(rule.get("contenu"), _("Horloge")))}
        ttk.Entry(f, textvariable=row["debut"], width=6).pack(side="left")
        ttk.Label(f, text="→").pack(side="left", padx=2)
        ttk.Entry(f, textvariable=row["fin"], width=6).pack(side="left")
        for i, var in enumerate(row["jours"]):
            ttk.Checkbutton(f, text=self.days[i] if i < len(self.days) else str(i), variable=var).pack(side="left")
        ttk.Combobox(f, textvariable=row["contenu"], values=list(self.labels), state="readonly",
                     width=16).pack(side="left", padx=4)
        ttk.Button(f, text="✕", width=3, command=lambda: self.remove_row(row)).pack(side="left")
        self.rows.append(row)

    def add_profile(self, profile: dict | None = None):
        profile = profile or {"app": "", "contenu": "moniteur"}
        f = ttk.Frame(self.profiles_frame)
        f.pack(fill="x", pady=2)
        row = {"frame": f, "app": tk.StringVar(value=profile.get("app", "")),
               "contenu": tk.StringVar(value=self.keys.get(profile.get("contenu"), _("Horloge")))}
        ttk.Entry(f, textvariable=row["app"], width=20).pack(side="left")
        detect = ttk.Button(f, text=_("Détecter"))
        detect.configure(command=lambda: self.detect(row, detect, 3))
        detect.pack(side="left", padx=4)
        ttk.Combobox(f, textvariable=row["contenu"], values=list(self.labels), state="readonly",
                     width=24).pack(side="left", padx=4)
        ttk.Button(f, text="✕", width=3, command=lambda: (f.destroy(), self.profiles.remove(row))).pack(side="left")
        self.profiles.append(row)

    def detect(self, row: dict, button, left: int):
        """Compte à rebours, puis classe de la fenêtre active (le temps d'y cliquer)."""
        if left > 0:
            button.configure(text=str(left))
            self.win.after(1000, lambda: self.detect(row, button, left - 1))
            return
        from rog_flare2_fenetre import active_window
        w = active_window()
        button.configure(text=_("Détecter"))
        if w:
            row["app"].set(w["app"])
        else:
            self.status.config(text=_("Fenêtre active introuvable dans cette session"))

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
        profiles = [{"app": r["app"].get().strip(), "contenu": self.labels.get(r["contenu"].get(), "horloge")}
                    for r in self.profiles if r["app"].get().strip()]
        cfg = {"regles": rules, "profils": profiles, **{k: bool(v.get()) for k, v in self.triggers.items()}}
        prog.save_config(cfg)
        self.on_saved()
        self.status.config(text=_("Programmation enregistrée"))


class BadgesWindow:
    """Fenêtre « Voyants » : micro, webcam, OBS (rog_flare2_voyants)."""

    MIC = {"": "Désactivé", "coupe": "Quand il est coupé", "actif": "Quand une application l'utilise"}

    def __init__(self, parent, on_saved):
        import rog_flare2_voyants as voyants
        self.voyants, self.on_saved = voyants, on_saved
        cfg = voyants.load_config()
        self.win = tk.Toplevel(parent)
        self.win.title(_("Voyants"))
        self.win.resizable(False, False)
        body = ttk.Frame(self.win, padding=14)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=_("Petits blocs lumineux en haut à gauche de l'écran : 1 micro, 2 webcam, 3 OBS."),
                  style="Muted.TLabel", wraplength=420).pack(anchor="w", pady=(0, 8))
        mic = ttk.Frame(body)
        mic.pack(fill="x", pady=2)
        ttk.Label(mic, text=_("Micro :")).pack(side="left")
        self.mic_labels = {_(v): k for k, v in self.MIC.items()}
        self.mic = tk.StringVar(value=_(self.MIC.get(cfg.get("micro", ""), "Désactivé")))
        ttk.Combobox(mic, textvariable=self.mic, values=list(self.mic_labels), state="readonly",
                     width=30).pack(side="left", padx=6)
        self.webcam = tk.BooleanVar(value=bool(cfg.get("webcam")))
        ttk.Checkbutton(body, text=_("Webcam utilisée"), variable=self.webcam).pack(anchor="w", pady=2)
        self.obs = tk.BooleanVar(value=bool(cfg.get("obs")))
        ttk.Checkbutton(body, text=_("OBS en direct ou en enregistrement (obs-websocket)"),
                        variable=self.obs).pack(anchor="w", pady=2)
        obs = ttk.Frame(body)
        obs.pack(fill="x", padx=(22, 0))
        ttk.Label(obs, text=_("Port :")).pack(side="left")
        self.port = tk.StringVar(value=str(cfg.get("obs_port", 4455)))
        ttk.Entry(obs, textvariable=self.port, width=6).pack(side="left", padx=4)
        ttk.Label(obs, text=_("Mot de passe :")).pack(side="left", padx=(8, 0))
        self.password = tk.StringVar(value=cfg.get("obs_mot_de_passe", ""))
        ttk.Entry(obs, textvariable=self.password, width=16, show="•").pack(side="left", padx=4)
        self.announce = tk.BooleanVar(value=bool(cfg.get("annoncer", True)))
        ttk.Checkbutton(body, text=_("Annoncer chaque changement par un texte défilant"),
                        variable=self.announce).pack(anchor="w", pady=(6, 2))
        self.status = ttk.Label(body, text="", style="Muted.TLabel")
        self.status.pack(anchor="w")
        ttk.Button(body, text=_("Enregistrer"), command=self.save).pack(fill="x", pady=(8, 0))

    def save(self):
        try:
            port = int(self.port.get())
        except ValueError:
            port = 4455
        self.voyants.save_config({"micro": self.mic_labels.get(self.mic.get(), ""), "webcam": self.webcam.get(),
                                  "obs": self.obs.get(), "obs_port": port,
                                  "obs_mot_de_passe": self.password.get(), "annoncer": self.announce.get()})
        self.on_saved()
        self.status.config(text=_("Voyants enregistrés"))
