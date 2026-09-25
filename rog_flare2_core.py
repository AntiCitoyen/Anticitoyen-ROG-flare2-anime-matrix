"""Cœur commun AniMe Matrix : lecture GIF/images en flux, horloge, dossiers.

Utilisé par le démon (rog_flare2_demon.py), le lanceur et les outils en ligne de
commande ; ne dépend pas de Tk.
"""
from __future__ import annotations

import datetime
import os
import subprocess
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_clock_v3 import brightness_to_raw, make_frame  # noqa: E402
from rog_flare2_matrix_paint import (  # noqa: E402
    FB_OFFSET,
    FRAME_SIZE,
    PHYSICAL_CALIBRATED_ORDER,
    PHYSICAL_ROW_COUNTS,
    PREFIX,
    FlareTransport,
)

try:
    from PIL import Image, ImageSequence
except ImportError:
    Image = None

VERSION = "1.4.0"  # version unique du projet (paquet, lanceur, démon, mises à jour)
MAX_ROW_WIDTH = max(PHYSICAL_ROW_COUNTS)
NUM_ROWS = len(PHYSICAL_ROW_COUNTS)
MEDIA_EXTENSIONS = {".gif", ".png", ".jpg", ".jpeg", ".bmp", ".webp"}
STILL_SECONDS = 5.0  # durée d'affichage d'une image fixe dans une galerie
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "rog-flare2"
GALLERY_FILE = CONFIG_DIR / "galerie"  # dossier lu par la galerie (lanceur et service)


def gallery_dir() -> Path:
    """Dossier de la galerie : celui choisi en dernier, sinon <Images>/AniMe-Matrix."""
    try:
        saved = GALLERY_FILE.read_text().strip()
        if saved:
            return Path(saved)
    except OSError:
        pass
    try:
        pictures = subprocess.run(["xdg-user-dir", "PICTURES"], capture_output=True, text=True,
                                  timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pictures = ""
    return Path(pictures or Path.home() / "Pictures") / "AniMe-Matrix"


def save_gallery_dir(folder: Path) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    GALLERY_FILE.write_text(f"{folder}\n")


FAITHFUL_COLS = 19  # gabarit en coin : la rangée r couvre les colonnes (r+1)//2 à 18 (bord droit vertical)


def image_to_frame(img: "Image.Image", brightness: int = 100, fidele: bool = False) -> bytes:
    """Convertit une image PIL en trame 1024 octets pour la matrice.

    Le panneau physique est un triangle/coin (19 LED de large en haut,
    7 en bas), pas un rectangle. Pour montrer l'image ENTIERE (pas juste
    une fenêtre fixe qui coupe la partie gauche des lignes étroites), on
    échantillonne chaque ligne sur toute la largeur de l'image source,
    proportionnellement au nombre réel de LED de cette ligne.

    fidele : l'image est posée sur le gabarit en coin (19 × 24) sans étirer les
    rangées : les formes gardent leurs proportions, ce qui dépasse du coin est perdu.
    """
    scale = brightness / 100.0
    if fidele:
        pixels = img.convert("L").resize((FAITHFUL_COLS, NUM_ROWS), Image.LANCZOS).load()
        frame = bytearray(FRAME_SIZE)
        frame[0:2] = PREFIX
        for raw_idx, (row, col) in enumerate(PHYSICAL_CALIBRATED_ORDER):
            x = min(FAITHFUL_COLS - 1, (row + 1) // 2 + col)
            frame[FB_OFFSET + raw_idx] = max(0, min(255, int(pixels[x, row] * scale)))
        return bytes(frame)
    # Hauteur fixée au nombre de lignes physiques ; largeur gardée haute
    # résolution pour un échantillonnage précis par ligne.
    src_w, src_h = img.size
    sample_w = max(MAX_ROW_WIDTH, src_w)
    gray = img.convert("L").resize((sample_w, NUM_ROWS), Image.LANCZOS)
    pixels = gray.load()

    frame = bytearray(FRAME_SIZE)
    frame[0:2] = PREFIX

    for raw_idx, (row, col) in enumerate(PHYSICAL_CALIBRATED_ORDER):
        row_count = PHYSICAL_ROW_COUNTS[row]
        if row_count > 1:
            gcol = round(col * (sample_w - 1) / (row_count - 1))
        else:
            gcol = 0
        gcol = max(0, min(sample_w - 1, gcol))
        val = int(pixels[gcol, row] * scale)
        frame[FB_OFFSET + raw_idx] = max(0, min(255, val))

    return bytes(frame)


def iter_gif_frames(path: Path):
    """Itère les frames d'un GIF recomposées sur un canevas complet.

    De nombreux GIF (surtout optimisés pour le web) ne stockent, à partir de
    la 2e frame, que la zone modifiée depuis la frame précédente. Itérer
    directement sur ImageSequence sans recomposer ne donne que ce fragment,
    pas l'image entière.

    Le canevas est réutilisé : le consommateur doit le convertir avant de
    demander la frame suivante (garder les canevas pleine taille coûtait
    ~470 Mo pour un GIF 512x720 de 318 frames).
    """
    with Image.open(path) as im:
        canvas = Image.new("RGBA", im.size, (0, 0, 0, 255))
        for frame in ImageSequence.Iterator(im):
            rgba = frame.convert("RGBA")
            canvas.paste(rgba, (0, 0), rgba)
            duration_ms = frame.info.get("duration", 100)
            yield canvas, max(20, duration_ms) / 1000.0


def pick_version(f: Path) -> Path:
    """Version convertie <dossier>/matrix/<nom>.gif si elle existe et n'est pas plus vieille que la source."""
    converted = f.parent / "matrix" / f.with_suffix(".gif").name
    if converted.exists() and converted.stat().st_mtime >= f.stat().st_mtime:
        return converted
    return f


def media_files(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS)


FAITHFUL_TAG = b"animematrix:fidele"  # commentaire GIF : dessiné pour la géométrie fidèle


def is_faithful(path: Path) -> bool:
    """GIF marqué « géométrie fidèle » (éditeur d'animation, bibliothèque)."""
    try:
        with Image.open(path) as im:
            return FAITHFUL_TAG in (im.info.get("comment") or b"")
    except (OSError, AttributeError):
        return False


def play_file(path: Path, transport: FlareTransport, stop_event: threading.Event, brightness,
              fidele: bool = False) -> None:
    """Joue une fois un GIF/image en flux ; brightness() est relue à chaque frame."""
    fidele = fidele or is_faithful(path)
    n = 0
    for img, delay in iter_gif_frames(path):
        if stop_event.is_set():
            return
        transport.write(image_to_frame(img, brightness(), fidele))
        n += 1
        stop_event.wait(delay)
    if n == 1:
        stop_event.wait(STILL_SECONDS)


def play_clock(transport: FlareTransport, stop_event: threading.Event, brightness) -> None:
    while not stop_event.is_set():
        now = datetime.datetime.now()
        transport.write(make_frame(now.strftime("%H:%M"), preset="flare", val=brightness_to_raw(brightness()),
                                   y=0, blink_colon=now.second % 2 == 0, overrides={}))
        stop_event.wait(0.5)
