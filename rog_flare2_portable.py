"""EXPÉRIMENTAL — AniMe Matrix des portables ROG (G14, G16…) via asusctl.

Les portables utilisent un autre protocole que le clavier (paquets 0x5E, à ne
JAMAIS envoyer au clavier). Plutôt que de le réimplémenter sans matériel pour le
tester, ce module passe par asusctl (https://asus-linux.org), l'outil de
référence pour ces portables : chaque trame du démon devient une image PNG
affichée par « asusctl anime image », au plus 5 fois par seconde.

Activation : ~/.config/rog-flare2/materiel contenant « portable-asusctl »
(sinon, le clavier ROG Strix Flare II Animate est utilisé). Non testé sur un
vrai portable : retours bienvenus dans les tickets du projet.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from rog_flare2_core import CONFIG_DIR
from rog_flare2_matrix_paint import FB_OFFSET, LED_COUNT, PHYSICAL_CALIBRATED_ORDER

HARDWARE_FILE = CONFIG_DIR / "materiel"
MIN_INTERVAL = 0.2  # asusctl est une commande : au plus 5 images par seconde


def hardware() -> str:
    try:
        return HARDWARE_FILE.read_text().strip() or "clavier"
    except OSError:
        return "clavier"


def frame_to_png(frame: bytes, path: Path, zoom: int = 6) -> None:
    """Trame du clavier -> PNG (géométrie fidèle 19 × 24, agrandie) pour asusctl."""
    from PIL import Image
    leds = frame[FB_OFFSET:FB_OFFSET + LED_COUNT] if len(frame) > LED_COUNT else frame
    img = Image.new("L", (19, 24), 0)
    px = img.load()
    for (row, col), v in zip(PHYSICAL_CALIBRATED_ORDER, leds):
        px[(row + 1) // 2 + col, row] = v
    img.resize((19 * zoom, 24 * zoom), Image.NEAREST).save(path)


class AsusctlTransport:
    """Même interface que FlareTransport (connect/write/close), vers « asusctl anime »."""

    def __init__(self, runtime: Path):
        self.png = runtime / "animematrix-portable.png"
        self._last = 0.0

    def connect(self) -> str:
        if not shutil.which("asusctl"):
            raise RuntimeError("asusctl introuvable (https://asus-linux.org)")
        subprocess.run(["asusctl", "anime", "--enable-display", "true"], capture_output=True, timeout=5)
        return "asusctl"

    def write(self, frame: bytes) -> int:
        now = time.monotonic()
        if now - self._last < MIN_INTERVAL and any(frame[FB_OFFSET:FB_OFFSET + LED_COUNT]):
            return len(frame)  # trame sautée : asusctl ne suit pas la cadence des effets
        self._last = now
        if not any(frame[FB_OFFSET:FB_OFFSET + LED_COUNT]):
            subprocess.run(["asusctl", "anime", "--clear"], capture_output=True, timeout=5)
            return len(frame)
        frame_to_png(frame, self.png)
        r = subprocess.run(["asusctl", "anime", "image", "--path", str(self.png)], capture_output=True, timeout=5)
        if r.returncode != 0:
            raise OSError((r.stderr or r.stdout).decode(errors="replace").strip() or "asusctl a échoué")
        return len(frame)

    def close(self):
        pass
