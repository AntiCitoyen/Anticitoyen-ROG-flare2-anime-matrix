"""Notifications du bureau vers l'AniMe Matrix (démon animematrixd).

Écoute, en lecture seule, les appels Notify du bus de session
(org.freedesktop.Notifications) avec dbus-monitor, et passe « APPLI : TITRE »
au démon, qui l'affiche en surimpression puis rend la lecture en cours.
Désactivé par défaut ; réglages dans ~/.config/rog-flare2/notifications.json :

    {"actif": true, "applis": ["thunderbird", "discord"]}   (liste vide = toutes)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import threading
import unicodedata

from rog_flare2_core import CONFIG_DIR

CONFIG_FILE = CONFIG_DIR / "notifications.json"
IGNORED_SUMMARIES = {"AniMe Matrix"}  # nos propres notifications (bascule)


def load_config() -> dict:
    try:
        return {"actif": False, "applis": [], **json.loads(CONFIG_FILE.read_text())}
    except (OSError, ValueError):
        return {"actif": False, "applis": []}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False))


def matrix_text(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().upper().strip()


def parse_monitor(lines):
    """Itère (appli, titre, corps) depuis la sortie de dbus-monitor."""
    pending = None
    for line in lines:
        line = line.rstrip("\n")
        if "member=Notify" in line and line.startswith("method call"):
            pending = []
            continue
        if pending is None:
            continue
        stripped = line.strip()
        if stripped.startswith("string "):
            pending.append(stripped[len("string "):].strip('"'))
        elif stripped.startswith("uint32 "):
            pending.append(None)
        if len(pending) >= 5:  # appli, id, icône, titre, corps
            app, _id, _icon, summary, body = pending[:5]
            pending = None
            yield app, summary, body


class NotificationWatcher:
    """Lance dbus-monitor et appelle on_notify(texte) pour chaque notification autorisée."""

    def __init__(self, on_notify):
        self.on_notify = on_notify
        self.proc: subprocess.Popen | None = None

    def start(self, cfg: dict) -> bool:
        self.stop()
        if not cfg.get("actif") or not shutil.which("dbus-monitor"):
            return False
        allowed = {a.strip().lower() for a in cfg.get("applis", []) if a.strip()}
        self.proc = subprocess.Popen(
            ["dbus-monitor", "--session", "interface='org.freedesktop.Notifications',member='Notify'"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

        def loop(proc):
            for app, summary, _body in parse_monitor(proc.stdout):
                if summary in IGNORED_SUMMARIES:
                    continue
                if allowed and app.lower() not in allowed:
                    continue
                label = f"{app} : {summary}" if app else summary
                self.on_notify(matrix_text(label))
        threading.Thread(target=loop, args=(self.proc,), daemon=True).start()
        return True

    def stop(self):
        if self.proc is not None:
            self.proc.terminate()
            self.proc = None
