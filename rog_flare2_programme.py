"""Programmation horaire et déclencheurs de l'AniMe Matrix (démon animematrixd).

~/.config/rog-flare2/programmation.json :
    {"regles": [{"debut": "08:00", "fin": "12:00", "jours": [0, 1, 2, 3, 4], "contenu": "horloge"}],
     "profils": [{"app": "steam_app", "contenu": "moniteur"}],
     "verrouillage": true, "veille": true, "plein_ecran": false}

- Règles : pendant la plage (jours 0 = lundi ; une plage peut passer minuit), le
  démon affiche le contenu ; à la fin, la lecture manuelle reprend.
- Profils par application : tant que la fenêtre active correspond (classe ou titre
  contenant le texte du profil), son contenu passe avant les plages horaires.
- Contenus : horloge, galerie, moniteur, morceau, eteint, « effet:<nom> », « gif:<fichier> »,
  « liste:<nom> » (liste de lecture).
- Déclencheurs : écran noir tant que la session est verrouillée
  (ScreenSaver.ActiveChanged), pendant la mise en veille (logind PrepareForSleep),
  ou quand la fenêtre active est en plein écran (rog_flare2_fenetre : X11, Sway, Hyprland, GNOME).
"""
from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import threading

from rog_flare2_core import CONFIG_DIR, gallery_dir, media_files

CONFIG_FILE = CONFIG_DIR / "programmation.json"
CONTENTS = ["horloge", "galerie", "moniteur", "morceau", "eteint"]


def load_config() -> dict:
    base = {"regles": [], "profils": [], "verrouillage": False, "veille": False, "plein_ecran": False}
    try:
        return {**base, **json.loads(CONFIG_FILE.read_text())}
    except (OSError, ValueError):
        return base


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=1))


def _minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def active_rule(rules: list[dict], now: datetime.datetime) -> dict | None:
    """Première règle en cours ; une plage 22:00-07:00 couvre la nuit (jour = jour du début)."""
    t = now.hour * 60 + now.minute
    for rule in rules:
        try:
            start, end = _minutes(rule["debut"]), _minutes(rule["fin"])
        except (KeyError, ValueError):
            continue
        days = rule.get("jours") or list(range(7))
        today, yesterday = now.weekday(), (now.weekday() - 1) % 7
        if start <= end:
            if today in days and start <= t < end:
                return rule
        elif (today in days and t >= start) or (yesterday in days and t < end):
            return rule
    return None


def show_for(content: str) -> dict | None:
    """Lecture correspondant au contenu d'une règle ; None pour « éteint »."""
    if content == "horloge":
        return {"type": "horloge"}
    if content == "galerie":
        folder = gallery_dir()
        return {"type": "gif", "files": [str(f) for f in media_files(folder)] if folder.is_dir() else [],
                "folder": str(folder), "loop": True, "converted": True}
    if content == "clavier":  # animation enregistrée dans la mémoire du clavier
        return {"type": "clavier"}
    if content == "moniteur":
        return {"type": "effet", "name": "System Monitor", "params": {}}
    if content == "morceau":
        return {"type": "effet", "name": "Now Playing", "params": {}}
    if content.startswith("effet:"):
        return {"type": "effet", "name": content[6:], "params": {}}
    if content.startswith("gif:"):
        return {"type": "gif", "files": [content[4:]], "loop": True, "converted": True}
    if content.startswith("liste:"):
        return {"type": "liste", "name": content[6:]}
    return None


def match_profile(profiles: list[dict], window: dict | None) -> dict | None:
    """Premier profil dont le texte apparaît dans la classe ou le titre de la fenêtre active."""
    if not window:
        return None
    for p in profiles:
        key = str(p.get("app", "")).strip().lower()
        if key and (key in window.get("app", "") or key in window.get("title", "").lower()):
            return p
    return None


class Monitor:
    """Lit une sortie dbus-monitor et appelle on_bool(valeur) à chaque booléen après le membre attendu."""

    def __init__(self, args: list[str], member: str, on_bool):
        self.args, self.member, self.on_bool = args, member, on_bool
        self.proc: subprocess.Popen | None = None

    def start(self):
        if not shutil.which("dbus-monitor"):
            return
        self.proc = subprocess.Popen(["dbus-monitor", *self.args], stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, text=True)
        threading.Thread(target=self._loop, args=(self.proc,), daemon=True).start()

    def _loop(self, proc):
        waiting = False
        for line in proc.stdout:
            if f"member={self.member}" in line:
                waiting = True
            elif waiting and line.strip().startswith("boolean "):
                waiting = False
                self.on_bool(line.strip().endswith("true"))

    def stop(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc = None


class Programme:
    """Fils du démon : règles horaires (toutes les 20 s) et déclencheurs."""

    def __init__(self, play_rule, end_rule, hold):
        self.play_rule, self.end_rule, self.hold = play_rule, end_rule, hold
        self.cfg = load_config()
        self.current: dict | None = None  # règle appliquée
        self.monitors: list[Monitor] = []
        self.stop_event = threading.Event()

    def start(self, cfg: dict):
        self.stop()
        self.cfg, self.stop_event = cfg, threading.Event()
        if cfg.get("verrouillage"):
            rules = [f"type='signal',interface='{iface}',member='ActiveChanged'" for iface in
                     ("org.cinnamon.ScreenSaver", "org.gnome.ScreenSaver", "org.freedesktop.ScreenSaver",
                      "org.mate.ScreenSaver")]
            self.monitors.append(Monitor(["--session", *rules], "ActiveChanged",
                                         lambda on: self.hold("verrouillage", on)))
        if cfg.get("veille"):
            self.monitors.append(Monitor(["--system", "type='signal',interface='org.freedesktop.login1.Manager',"
                                                      "member='PrepareForSleep'"],
                                         "PrepareForSleep", lambda on: self.hold("veille", on)))
        for m in self.monitors:
            m.start()
        threading.Thread(target=self._loop, args=(self.stop_event,), daemon=True).start()

    def tick(self, now: datetime.datetime | None = None, window: dict | None = None):
        """Applique le profil de la fenêtre active, sinon la plage horaire, sinon la lecture manuelle."""
        rule = active_rule(self.cfg.get("regles", []), now or datetime.datetime.now())
        target = match_profile(self.cfg.get("profils", []), window) or rule
        if target != self.current:
            if target is None:
                self.end_rule()
            else:
                self.play_rule(show_for(target.get("contenu", "horloge")))
            self.current = target

    def _loop(self, stop):
        from rog_flare2_fenetre import active_window
        while not stop.is_set():
            watch = self.cfg.get("plein_ecran") or self.cfg.get("profils")
            window = active_window() if watch else None
            if self.cfg.get("plein_ecran"):
                self.hold("plein_ecran", bool((window or {}).get("fullscreen")))
            self.tick(window=window)
            stop.wait(2)

    def stop(self):
        self.stop_event.set()
        for m in self.monitors:
            m.stop()
        self.monitors = []
