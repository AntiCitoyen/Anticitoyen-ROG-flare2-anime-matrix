"""Programmation horaire et déclencheurs de l'AniMe Matrix (démon animematrixd).

~/.config/rog-flare2/programmation.json :
    {"regles": [{"debut": "08:00", "fin": "12:00", "jours": [0, 1, 2, 3, 4], "contenu": "horloge"}],
     "verrouillage": true, "veille": true, "plein_ecran": false}

- Règles : pendant la plage (jours 0 = lundi ; une plage peut passer minuit), le
  démon affiche le contenu ; à la fin, la lecture manuelle reprend.
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
    base = {"regles": [], "verrouillage": False, "veille": False, "plein_ecran": False}
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
    if content == "moniteur":
        return {"type": "effet", "name": "System Monitor", "params": {}}
    if content == "morceau":
        return {"type": "effet", "name": "Now Playing", "params": {}}
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


def fullscreen_active() -> bool:
    """Fenêtre active en plein écran (X11, Sway, Hyprland, GNOME avec Window Calls)."""
    from rog_flare2_fenetre import active_window
    return bool((active_window() or {}).get("fullscreen"))


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

    def tick(self, now: datetime.datetime | None = None):
        rule = active_rule(self.cfg.get("regles", []), now or datetime.datetime.now())
        if rule != self.current:
            if rule is None:
                self.end_rule()
            else:
                self.play_rule(show_for(rule.get("contenu", "horloge")))
            self.current = rule

    def _loop(self, stop):
        n = 0
        while not stop.is_set():
            if n % 10 == 0:  # règles : toutes les 20 s
                self.tick()
            if self.cfg.get("plein_ecran"):
                self.hold("plein_ecran", fullscreen_active())
            n += 1
            stop.wait(2)

    def stop(self):
        self.stop_event.set()
        for m in self.monitors:
            m.stop()
        self.monitors = []
