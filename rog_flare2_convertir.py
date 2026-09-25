#!/usr/bin/env python3
"""Conversion de GIF/images pour l'AniMe Matrix du ROG Strix Flare II Animate.

Chaîne ImageMagick (voir docs/GUIDE-GIF.md) : toile 19x24 (une LED par pixel sur la
rangée du haut), gris, contraste étiré, 3 niveaux, sans tramage, boucle.

    rog_flare2_convertir.py fichier.gif [autre.gif ...] [--sortie DOSSIER]
    rog_flare2_convertir.py dossier/                    [--sortie DOSSIER]

Sans --sortie : les fichiers convertis vont dans <dossier>/matrix/ (ou à côté
du fichier, sous-dossier matrix/). Un fichier déjà converti et plus récent que
sa source est sauté (--force pour refaire).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from typing import Callable

EXTENSIONS = {".gif", ".png", ".jpg", ".jpeg", ".bmp", ".webp"}
ARGUMENTS = [
    "-coalesce", "-colorspace", "Gray", "-resize", "19x24!", "-filter", "Lanczos",
    "-contrast-stretch", "2%x2%", "-posterize", "3", "-dither", "None",
    "-loop", "0",
]


def binaire_imagemagick() -> str:
    for b in ("magick", "convert"):
        if shutil.which(b):
            return b
    raise FileNotFoundError("ImageMagick introuvable (magick/convert) : sudo apt install imagemagick")


def destination(src: Path, sortie: Path | None) -> Path:
    dossier = sortie if sortie is not None else src.parent / "matrix"
    return dossier / (src.stem + ".gif")


def convertir(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [binaire_imagemagick(), str(src), *ARGUMENTS, str(dst)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not dst.exists():
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else f"rc={r.returncode}")


# --- Conversion intelligente (Pillow + NumPy, sans ImageMagick) ---------------
SCREEN_ASPECT = 19 / 18.5  # largeur / hauteur du coin réel : 19 pas de LED × 24 rangées de 0,77 pas
LEVELS = np.array([0, 64, 255], dtype=np.float32)  # 3 niveaux perçus (docs/GUIDE-GIF.md)


def _frames_gray(src: Path) -> list[tuple[np.ndarray, int]]:
    """Images recomposées en gris (float 0-255) et durées en ms."""
    from rog_flare2_core import iter_gif_frames
    out = []
    for img, delay in iter_gif_frames(src):
        rgba = np.asarray(img.convert("RGBA"), dtype=np.float32)
        gray = rgba[..., :3] @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
        alpha = rgba[..., 3] / 255.0
        out.append((gray * alpha, int(delay * 1000)))  # transparent -> noir
    return out


def _subject_box(frames: list[np.ndarray], bg: float, seuil: float = 28.0) -> tuple[int, int, int, int] | None:
    """Boîte (x0, y0, x1, y1) de ce qui diffère du fond sur l'ensemble des images."""
    diff = np.zeros(frames[0].shape, dtype=bool)
    for f in frames:
        diff |= np.abs(f - bg) > seuil
    ys, xs = np.nonzero(diff)
    if xs.size == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _fit_box(box, w, h, marge=0.08):
    """Élargit la boîte (marge) et l'amène aux proportions de l'écran, dans les limites de l'image."""
    x0, y0, x1, y1 = box
    bw, bh = (x1 - x0) * (1 + 2 * marge), (y1 - y0) * (1 + 2 * marge)
    if bw / max(bh, 1) < SCREEN_ASPECT:
        bw = bh * SCREEN_ASPECT
    else:
        bh = bw / SCREEN_ASPECT
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    bw, bh = min(bw, w), min(bh, h)
    x0 = int(max(0, min(w - bw, cx - bw / 2)))
    y0 = int(max(0, min(h - bh, cy - bh / 2)))
    return x0, y0, int(x0 + bw), int(y0 + bh)


def convertir_intelligent(src: Path, dst: Path, recadrer: bool = True, contours: bool = True,
                          fidele: bool = False) -> None:
    """Recadrage sur le sujet, sujet clair sur fond noir, contours renforcés, 3 niveaux, sans tramage."""
    from PIL import Image, ImageFilter
    frames = _frames_gray(src)
    if not frames:
        raise RuntimeError("aucune image")
    first = frames[0][0]
    border = np.concatenate([first[0], first[-1], first[:, 0], first[:, -1]])
    bg = float(np.median(border))
    near_bg = float((np.abs(first - bg) < 20).mean())  # part de l'image au niveau du fond
    graphic = near_bg > 0.45  # dessin/pictogramme sur fond uni ; sinon image dense (photo)
    invert = graphic and bg > 128  # fond clair uni : sujet clair sur fond noir
    h, w = first.shape
    box = _subject_box([f for f, _d in frames], bg) if recadrer else None
    box = _fit_box(box, w, h) if box else (0, 0, w, h)
    size = (19, 24)  # une colonne par LED de la rangée du haut, une ligne par rangée
    factor = max(1, min((box[2] - box[0]) // size[0], (box[3] - box[1]) // size[1]))
    result, durations = [], []
    for gray, delay in frames:
        img = Image.fromarray(np.clip(255 - gray if invert else gray, 0, 255).astype(np.uint8), "L").crop(box)
        if contours and graphic and factor >= 3:  # traits fins clairs épaissis pour survivre à la réduction
            img = img.filter(ImageFilter.MaxFilter(min(9, factor // 2 * 2 + 1)))
        small = np.asarray(img.resize(size, Image.LANCZOS), dtype=np.float32)
        lo, hi = np.percentile(small, 2), np.percentile(small, 98)  # contraste étiré
        small = np.clip((small - lo) / max(hi - lo, 1) * 255, 0, 255)
        if contours and not graphic:
            # Image dense : les grandes surfaces claires feraient une flaque (halo) ; on garde les
            # contours en plein et on ramène les surfaces au niveau faible.
            edges = np.asarray(img.resize(size, Image.LANCZOS).filter(ImageFilter.FIND_EDGES), dtype=np.float32)
            edges = np.clip(edges / max(np.percentile(edges, 95), 1) * 255, 0, 255)
            small = np.maximum(edges, np.minimum(small, 64.0))
        small = LEVELS[np.abs(small[..., None] - LEVELS).argmin(axis=-1)]
        if result and np.abs(small - result[-1]).mean() < 2:  # image quasi identique : durée cumulée
            durations[-1] += delay
            continue
        result.append(small)
        durations.append(delay)
    durations = [max(80, d) for d in durations]  # cadence que l'écran suit (≈ 12 i/s)
    images = [Image.fromarray(a.astype(np.uint8), "L") for a in result]
    dst.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(dst, save_all=True, append_images=images[1:], duration=durations, loop=0, disposal=1,
                   optimize=False)


def lister(chemins: list[Path]) -> list[Path]:
    fichiers: list[Path] = []
    for c in chemins:
        if c.is_dir():
            fichiers += sorted(p for p in c.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS and p.parent.name != "matrix")
        elif c.is_file():
            fichiers.append(c)
    return fichiers


def convertir_tout(chemins: list[Path], sortie: Path | None = None, force: bool = False,
                   rappel: Callable[[int, int, Path, str], None] | None = None,
                   intelligente: bool = True, fidele: bool = False) -> list[Path]:
    """Convertit fichiers et dossiers ; rappel(i, n, source, 'ok'|'saute'|'erreur: ...'). Rend la liste des GIF produits."""
    fichiers = lister(chemins)
    produits: list[Path] = []
    n = len(fichiers)
    for i, src in enumerate(fichiers, 1):
        dst = destination(src, sortie)
        if not force and dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            produits.append(dst)
            if rappel: rappel(i, n, src, "saute")
            continue
        try:
            if intelligente:
                convertir_intelligent(src, dst, fidele=fidele)
            else:
                convertir(src, dst)
            produits.append(dst)
            if rappel: rappel(i, n, src, "ok")
        except Exception as exc:  # noqa: BLE001 — un fichier raté n'arrête pas le dossier
            if rappel: rappel(i, n, src, f"erreur: {exc}")
    return produits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chemins", nargs="+", type=Path, help="GIF/images ou dossiers")
    ap.add_argument("--sortie", type=Path, default=None, help="dossier de sortie (défaut : matrix/ à côté)")
    ap.add_argument("--force", action="store_true", help="reconvertir même si déjà à jour")
    ap.add_argument("--classique", action="store_true", help="chaîne ImageMagick d'origine (sans recadrage)")
    ap.add_argument("--fidele", action="store_true", help="géométrie fidèle (le coin coupe l'image au lieu de l'étirer)")
    a = ap.parse_args()
    bilan = {"ok": 0, "saute": 0, "erreur": 0}

    def rappel(i: int, n: int, src: Path, etat: str) -> None:
        bilan[etat.split(":")[0]] += 1
        print(f"[{i}/{n}] {src.name} : {etat}")

    produits = convertir_tout(a.chemins, a.sortie, a.force, rappel, not a.classique, a.fidele)
    print(f"{bilan['ok']} converti(s), {bilan['saute']} déjà à jour, {bilan['erreur']} en erreur -> {produits[0].parent if produits else '-'}")
    return 1 if bilan["erreur"] else 0


if __name__ == "__main__":
    sys.exit(main())
