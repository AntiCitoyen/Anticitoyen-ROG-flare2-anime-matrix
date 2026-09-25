#!/usr/bin/env python3
"""
Lecture en boucle de tous les GIF/images d'un dossier sur l'écran AniMe
Matrix du clavier ROG Strix Flare II Animate. Pensé pour tourner en
service systemd --user au démarrage de session (headless, pas de GUI).

Usage: rog_flare2_folder_player.py [dossier] [--brightness N] [--originaux]

Sans dossier : celui choisi en dernier dans le lanceur (~/.config/rog-flare2/galerie).

Si <dossier>/matrix/ contient la version convertie d'un fichier
(rog_flare2_convertir.py, toile 19x24), c'est elle qui est lue, sauf avec
--originaux. Les frames sont décodées en flux : la mémoire reste celle d'un
seul canevas, quelle que soit la taille des GIF.
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_matrix_paint import FlareTransport
from rog_flare2_launcher import gallery_dir, media_files, pick_version, play_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path, nargs="?")
    ap.add_argument("--brightness", type=int, default=60)
    ap.add_argument("--originaux", action="store_true",
                    help="ignorer les versions converties de <dossier>/matrix/")
    args = ap.parse_args()

    folder = args.folder or gallery_dir()
    transport = FlareTransport()
    transport.connect()
    stop = threading.Event()  # jamais posé : le service tourne jusqu'à son arrêt

    while True:
        files = media_files(folder) if folder.is_dir() else []
        if not files:
            time.sleep(5)
            continue
        for f in files:
            src = f if args.originaux else pick_version(f)
            try:
                play_file(src, transport, stop, lambda: args.brightness)
            except Exception as exc:
                print(f"skip {src}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
