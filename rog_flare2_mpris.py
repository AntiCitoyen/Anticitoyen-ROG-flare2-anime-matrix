"""Morceau en cours (MPRIS) : titre défilant au changement de piste, puis visualiseur audio.

Effet « Now Playing » : interroge les lecteurs MPRIS (Spotify, Rhythmbox, VLC,
navigateurs…) par D-Bus avec `gdbus` (sans dépendance Python), toutes les deux
secondes, dans un fil séparé.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import threading
import time
import unicodedata

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).parent / "polywollywin"))  # moteur d'effets
from effects import COLS, BaseEffect  # noqa: E402

POLL_S = 2.0


def _gdbus(*args: str) -> str:
    try:
        return subprocess.run(["gdbus", "call", "--session", *args], capture_output=True, text=True,
                              timeout=2).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def players() -> list[str]:
    out = _gdbus("--dest", "org.freedesktop.DBus", "--object-path", "/org/freedesktop/DBus",
                 "--method", "org.freedesktop.DBus.ListNames")
    return re.findall(r"'(org\.mpris\.MediaPlayer2\.[^']+)'", out)


def _prop(player: str, name: str) -> str:
    return _gdbus("--dest", player, "--object-path", "/org/mpris/MediaPlayer2",
                  "--method", "org.freedesktop.DBus.Properties.Get", "org.mpris.MediaPlayer2.Player", name)


def now_playing() -> tuple[str, str] | None:
    """(artiste, titre) du premier lecteur en lecture, sinon None."""
    for p in players():
        if "Playing" not in _prop(p, "PlaybackStatus"):
            continue
        meta = _prop(p, "Metadata")
        title = re.search(r"'xesam:title': <'((?:[^'\\]|\\.)*)'>", meta)
        artist = re.search(r"'xesam:artist': <\['((?:[^'\\]|\\.)*)'", meta)
        if title:
            return (artist.group(1) if artist else ""), title.group(1)
    return None


def ascii_upper(text: str) -> str:
    """Accents retirés, majuscules : la police 4×7 ne connaît que A-Z, chiffres et ponctuation simple."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().upper()


class Watcher:
    def __init__(self):
        self.track: tuple[str, str] | None = None
        self.changed_at = 0.0
        self._started = False
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._started or not shutil.which("gdbus"):
                return
            self._started = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            track = now_playing()
            if track != self.track:
                self.track, self.changed_at = track, time.monotonic()
            time.sleep(POLL_S)


WATCHER = Watcher()


class NowPlayingEffect(BaseEffect):
    name = "Now Playing"
    PARAMS = {
        "visualizer": {"label": "Visualizer", "min": 0, "max": 6, "default": 0, "scale": 1.0},
        "scroll": {"label": "Scroll", "min": 1, "max": 3, "default": 2, "scale": 1.0},
    }

    def __init__(self, visualizer: float = 0, scroll: float = 2):
        from rog_flare2_effets import AUDIO_EFFECTS, make_effect
        self.visualizer, self.scroll = visualizer, scroll
        self._names = [n for n in AUDIO_EFFECTS if n != self.name]  # pas lui-même
        self._make = make_effect
        self._viz = None
        self._viz_index = None
        self._text = None
        self._shown_at = -1.0
        WATCHER.start()

    def _visual(self):
        i = int(self.visualizer) % len(self._names)
        if i != self._viz_index:
            if self._viz is not None:
                self._viz.stop()
            self._viz, self._viz_index = self._make(self._names[i]), i
        return self._viz

    def tick(self, dt: float) -> list[int]:
        track = WATCHER.track
        if track and WATCHER.changed_at != self._shown_at:  # nouvelle piste : titre défilant
            self._shown_at = WATCHER.changed_at
            artist, title = track
            self._text = self._make("Scroll Text", {"message": ascii_upper(f"{artist} - {title}" if artist else title),
                                                    "speed": 100})
            self._scrolled = 0.0
        if self._text is not None:
            self._text.speed = float(self.scroll)
            frame = self._text.tick(dt)
            # un seul passage : l'écran (37 colonnes) plus la largeur du texte, à 20 px/s × vitesse
            self._scrolled += dt * self._text.speed * 20.0
            if self._scrolled < COLS + self._text._text_width(self._text.message):
                return frame
            self._text = None
        return self._visual().tick(dt)

    def stop(self):
        from rog_flare2_effets import AUDIO
        if self._viz is not None:
            self._viz.stop()
        AUDIO.stop()  # capture du son des visualiseurs
