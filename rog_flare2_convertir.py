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


def lister(chemins: list[Path]) -> list[Path]:
    fichiers: list[Path] = []
    for c in chemins:
        if c.is_dir():
            fichiers += sorted(p for p in c.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS and p.parent.name != "matrix")
        elif c.is_file():
            fichiers.append(c)
    return fichiers


def convertir_tout(chemins: list[Path], sortie: Path | None = None, force: bool = False,
                   rappel: Callable[[int, int, Path, str], None] | None = None) -> list[Path]:
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
    a = ap.parse_args()
    bilan = {"ok": 0, "saute": 0, "erreur": 0}

    def rappel(i: int, n: int, src: Path, etat: str) -> None:
        bilan[etat.split(":")[0]] += 1
        print(f"[{i}/{n}] {src.name} : {etat}")

    produits = convertir_tout(a.chemins, a.sortie, a.force, rappel)
    print(f"{bilan['ok']} converti(s), {bilan['saute']} déjà à jour, {bilan['erreur']} en erreur -> {produits[0].parent if produits else '-'}")
    return 1 if bilan["erreur"] else 0


if __name__ == "__main__":
    sys.exit(main())
