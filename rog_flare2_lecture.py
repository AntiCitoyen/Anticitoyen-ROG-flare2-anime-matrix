#!/usr/bin/env python3
"""Lecture de fond : rejoue ce que le lanceur affichait quand on l'a fermé.

Le lanceur écrit ~/.config/rog-flare2/lecture.json puis démarre
animematrix-lecture.service (ou ce script détaché si le service manque) :

    {"type": "gif", "files": [...], "loop": true, "converted": true, "brightness": 60}
    {"type": "effet", "name": "Plasma", "params": {...}, "speed": 1.0, "brightness": 60}
    {"type": "horloge", "brightness": 60}

Usage : rog_flare2_lecture.py [fichier.json]
"""
from __future__ import annotations

import json
import signal
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_launcher import CONFIG_DIR, pick_version, play_clock, play_file  # noqa: E402
from rog_flare2_matrix_paint import FlareTransport  # noqa: E402

SHOW_FILE = CONFIG_DIR / "lecture.json"


def play(show: dict, transport: FlareTransport, stop: threading.Event) -> None:
    brightness = lambda: int(show.get("brightness", 60))  # noqa: E731
    kind = show.get("type")
    if kind == "gif":
        files = [Path(f) for f in show.get("files", [])]
        while not stop.is_set():
            for f in files:
                if stop.is_set():
                    return
                src = pick_version(f) if show.get("converted", True) else f
                try:
                    play_file(src, transport, stop, brightness)
                except OSError as exc:  # fichier disparu ou illisible : on passe au suivant
                    print(f"skip {src}: {exc}", file=sys.stderr)
            if not show.get("loop", True):
                return
    elif kind == "effet":
        from rog_flare2_effets import make_effect, run_effect
        speed = float(show.get("speed", 1.0))
        run_effect(make_effect(show["name"], show.get("params")), transport, stop, brightness, lambda: speed)
    elif kind == "horloge":
        play_clock(transport, stop, brightness)
    else:
        raise SystemExit(f"lecture inconnue : {kind!r}")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else SHOW_FILE
    show = json.loads(path.read_text(encoding="utf-8"))
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    transport = FlareTransport()
    transport.connect()
    try:
        play(show, transport, stop)
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()


if __name__ == "__main__":
    main()
