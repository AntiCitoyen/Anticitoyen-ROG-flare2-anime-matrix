"""Exemple d'extension AniMe Matrix : un cœur qui bat.

Copier ce fichier dans ~/.config/rog-flare2/effets/ puis relancer le lanceur :
l'effet apparaît dans l'onglet Effets. Voir docs/EXTENSIONS.md.
"""
import math

import numpy as np

from effects import COLS, ROWS, BaseEffect  # moteur d'effets (polywollywin/effects.py)

# Cœur de 9 x 8 cases sur la grille logique 12 x 37 (rangée r : colonnes 2r à 36)
HEART = [
    ".XX...XX.",
    "XXXX.XXXX",
    "XXXXXXXXX",
    "XXXXXXXXX",
    ".XXXXXXX.",
    "..XXXXX..",
    "...XXX...",
    "....X....",
]


class HeartbeatEffect(BaseEffect):
    name = "Heartbeat"
    # Noms affichés selon la langue de l'interface (facultatif)
    noms = {"fr": "Battement de cœur", "en": "Heartbeat", "es": "Latido", "de": "Herzschlag"}
    PARAMS = {
        "bpm": {"label": "BPM", "min": 40, "max": 180, "default": 72, "scale": 1.0},
        "x": {"label": "Position X", "min": 0, "max": 100, "default": 70, "scale": 1.0},
    }

    def __init__(self, bpm: float = 72, x: float = 70):
        self.bpm = bpm
        self.x = x
        self._t = 0.0

    def tick(self, dt: float) -> list[int]:
        self._t += dt
        beat = (self._t * self.bpm / 60.0) % 1.0
        # double battement « toum-toum » puis repos
        level = max(math.exp(-((beat - 0.08) / 0.05) ** 2), 0.7 * math.exp(-((beat - 0.28) / 0.05) ** 2))
        frame = np.zeros((ROWS, COLS), dtype=np.float32)
        top = (ROWS - len(HEART)) // 2
        left = int(8 + (COLS - 9 - 8) * self.x / 100)
        for r, row in enumerate(HEART):
            for c, ch in enumerate(row):
                if ch == "X" and 0 <= left + c < COLS:
                    frame[top + r, left + c] = 60 + 195 * level
        return self._emit(frame)
