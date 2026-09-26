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

VERSION = "2.1.0"  # version unique du projet (paquet, lanceur, démon, mises à jour)
MAX_ROW_WIDTH = max(PHYSICAL_ROW_COUNTS)
NUM_ROWS = len(PHYSICAL_ROW_COUNTS)
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v"}  # lues par ffmpeg (rog_flare2_video)
MEDIA_EXTENSIONS = {".gif", ".png", ".jpg", ".jpeg", ".bmp", ".webp"} | VIDEO_EXTENSIONS
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


CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "animematrix" / "trames"
CACHE_MAGIC = b"AMX1"
CACHE_MAX_BYTES = 256 * 1024 * 1024
LED_BYTES = len(PHYSICAL_CALIBRATED_ORDER)


def _cache_path(path: Path, fidele: bool) -> Path:
    """Clé : chemin, taille, date et géométrie ; un fichier modifié donne une nouvelle entrée."""
    import hashlib
    st = path.stat()
    key = f"{path.resolve()}|{st.st_size}|{st.st_mtime_ns}|{int(fidele)}|{LED_BYTES}"
    return CACHE_DIR / (hashlib.sha1(key.encode()).hexdigest() + ".amx")


def _read_cache(cache: Path) -> list[tuple[bytes, float]] | None:
    try:
        data = cache.read_bytes()
    except OSError:
        return None
    if data[:4] != CACHE_MAGIC:
        return None
    step, frames = 2 + LED_BYTES, []
    for i in range(4, len(data) - step + 1, step):
        frames.append((data[i + 2:i + step], int.from_bytes(data[i:i + 2], "little") / 1000.0))
    return frames or None


def _write_cache(cache: Path, frames: list[tuple[bytes, float]]) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        body = b"".join(min(65535, round(d * 1000)).to_bytes(2, "little") + leds for leds, d in frames)
        tmp = cache.with_suffix(".tmp")
        tmp.write_bytes(CACHE_MAGIC + body)
        tmp.replace(cache)
        _prune_cache()
    except OSError:
        pass


def _prune_cache() -> None:
    """Garde le cache sous CACHE_MAX_BYTES en retirant les entrées les moins récemment lues."""
    entries = [(f.stat().st_atime, f.stat().st_size, f) for f in CACHE_DIR.glob("*.amx")]
    total = sum(size for _t, size, _f in entries)
    for _t, size, f in sorted(entries):
        if total <= CACHE_MAX_BYTES:
            break
        f.unlink(missing_ok=True)
        total -= size


def _dimmer(brightness: int) -> bytes:
    """Table de 256 octets : applique la luminosité par bytes.translate (même arrondi que image_to_frame)."""
    scale = brightness / 100.0
    return bytes(max(0, min(255, int(v * scale))) for v in range(256))


HEADER = bytes(PREFIX) + bytes(FB_OFFSET - len(PREFIX))
TRAILER = bytes(FRAME_SIZE - FB_OFFSET - LED_BYTES)


def play_file(path: Path, transport: FlareTransport, stop_event: threading.Event, brightness,
              fidele: bool = False) -> None:
    """Joue une fois un GIF/image ; brightness() est relue à chaque frame.

    Les trames converties (pleine luminosité) sont gardées dans ~/.cache/animematrix/trames :
    à la lecture suivante, ni décodage ni conversion.
    """
    if Path(path).suffix.lower() in VIDEO_EXTENSIONS:
        from rog_flare2_video import play_video
        play_video(path, transport, stop_event, brightness)
        return
    fidele = fidele or is_faithful(path)
    cache = _cache_path(path, fidele)
    frames = _read_cache(cache)
    table, level = _dimmer(100), 100
    if frames is None:
        frames = []
        for img, delay in iter_gif_frames(path):
            if stop_event.is_set():
                return  # interrompu : rien n'est mis en cache
            leds = image_to_frame(img, 100, fidele)[FB_OFFSET:FB_OFFSET + LED_BYTES]
            frames.append((leds, delay))
            b = brightness()
            if b != level:
                table, level = _dimmer(b), b
            transport.write(HEADER + leds.translate(table) + TRAILER)
            stop_event.wait(delay)
        _write_cache(cache, frames)
    else:
        for leds, delay in frames:
            if stop_event.is_set():
                return
            b = brightness()
            if b != level:
                table, level = _dimmer(b), b
            transport.write(HEADER + leds.translate(table) + TRAILER)
            stop_event.wait(delay)
    if len(frames) == 1:
        stop_event.wait(STILL_SECONDS)


def play_clock(transport: FlareTransport, stop_event: threading.Event, brightness) -> None:
    while not stop_event.is_set():
        now = datetime.datetime.now()
        transport.write(make_frame(now.strftime("%H:%M"), preset="flare", val=brightness_to_raw(brightness()),
                                   y=0, blink_colon=now.second % 2 == 0, overrides={}))
        stop_event.wait(0.5)
