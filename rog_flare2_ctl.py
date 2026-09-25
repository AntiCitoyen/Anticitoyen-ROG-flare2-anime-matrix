#!/usr/bin/env python3
"""animematrix-ctl — commande le démon animematrixd (et bibliothèque client).

    animematrix-ctl etat
    animematrix-ctl gif [DOSSIER|FICHIER...] [--originaux] [--une-fois]
    animematrix-ctl effet NOM [--param clé=valeur ...] [--cadence 1.5]
    animematrix-ctl horloge
    animematrix-ctl texte "Bonjour"              (texte défilant en lecture de base)
    animematrix-ctl notifier "Nouveau mail" [--duree 6]
    animematrix-ctl luminosite 60
    animematrix-ctl stop
    animematrix-ctl derniere                     (rejoue la dernière lecture)
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_demon import SHOW_FILE, SOCKET_PATH  # noqa: E402


class DaemonError(RuntimeError):
    pass


def request(cmd: str, timeout: float = 5, **kw) -> dict:
    """Une requête au démon ; lève OSError s'il ne répond pas, DaemonError s'il refuse."""
    with socket.socket(socket.AF_UNIX) as s:
        s.settimeout(timeout)
        s.connect(str(SOCKET_PATH))
        s.sendall((json.dumps({"cmd": cmd, **kw}) + "\n").encode())
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
    resp = json.loads(buf or b"{}")
    if not resp.get("ok"):
        raise DaemonError(resp.get("error", "réponse vide"))
    return resp


def ensure_daemon(wait: float = 4.0) -> bool:
    """Démon joignable ; sinon le démarre (service systemd --user, sinon processus détaché)."""
    try:
        request("ping", timeout=1)
        return True
    except (OSError, DaemonError, ValueError):
        pass
    # Service systemd seulement pour le socket standard (pas pour un environnement de test isolé)
    standard = SOCKET_PATH.parent == Path(f"/run/user/{os.getuid()}")
    if not standard or subprocess.run(["systemctl", "--user", "start", "animematrixd.service"],
                                      capture_output=True).returncode != 0:
        subprocess.Popen([sys.executable, str(Path(__file__).with_name("rog_flare2_demon.py"))],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        try:
            request("ping", timeout=1)
            return True
        except (OSError, DaemonError, ValueError):
            time.sleep(0.1)
    return False


def _value(text: str):
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def main(argv=None):
    ap = argparse.ArgumentParser(prog="animematrix-ctl", description="Commande le démon AniMe Matrix.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("etat")
    g = sub.add_parser("gif")
    g.add_argument("chemins", nargs="*")
    g.add_argument("--originaux", action="store_true")
    g.add_argument("--une-fois", action="store_true")
    g.add_argument("--fidele", action="store_true", help="géométrie fidèle (proportions gardées)")
    e = sub.add_parser("effet")
    e.add_argument("nom")
    e.add_argument("--param", action="append", default=[], metavar="clé=valeur")
    e.add_argument("--cadence", type=float, default=1.0)
    sub.add_parser("horloge")
    li = sub.add_parser("liste", help="joue une liste de lecture (sans nom : les affiche)")
    li.add_argument("nom", nargs="?")
    fa = sub.add_parser("favori", help="joue le favori numéro N (sans numéro : les affiche)")
    fa.add_argument("numero", nargs="?", type=int)
    t = sub.add_parser("texte")
    t.add_argument("message")
    n = sub.add_parser("notifier")
    n.add_argument("message")
    n.add_argument("--duree", type=float, default=6)
    b = sub.add_parser("luminosite")
    b.add_argument("valeur", type=int)
    sub.add_parser("stop")
    sub.add_parser("derniere")
    sub.add_parser("quitter")
    args = ap.parse_args(argv)

    if not ensure_daemon():
        sys.exit("animematrixd injoignable")
    if args.cmd == "etat":
        print(json.dumps(request("status"), ensure_ascii=False, indent=1))
        return
    if args.cmd == "gif":
        from rog_flare2_core import gallery_dir, media_files, MEDIA_EXTENSIONS
        paths = [Path(p).expanduser() for p in args.chemins] or [gallery_dir()]
        files = []
        for p in paths:
            files += media_files(p) if p.is_dir() else [p] if p.suffix.lower() in MEDIA_EXTENSIONS else []
        show = {"type": "gif", "files": [str(f) for f in files], "loop": not args.une_fois,
                "converted": not args.originaux, "fidele": args.fidele}
    elif args.cmd == "effet":
        params = dict(kv.split("=", 1) for kv in args.param)
        show = {"type": "effet", "name": args.nom, "params": {k: _value(v) for k, v in params.items()},
                "speed": args.cadence}
    elif args.cmd == "horloge":
        show = {"type": "horloge"}
    elif args.cmd in ("liste", "favori"):
        from rog_flare2_listes import load_favorites, load_lists
        if args.cmd == "liste":
            names = sorted(load_lists())
            if not args.nom:
                print("\n".join(names))
                return
            show = {"type": "liste", "name": args.nom}
        else:
            favorites = load_favorites()
            if args.numero is None:
                print("\n".join(f"{i}. {f.get('label', '?')}" for i, f in enumerate(favorites, 1)))
                return
            if not 1 <= args.numero <= len(favorites):
                sys.exit(f"favori {args.numero} introuvable")
            show = favorites[args.numero - 1]["show"]
    elif args.cmd == "texte":
        show = {"type": "effet", "name": "Scroll Text", "params": {"message": args.message}, "speed": 1.0}
    elif args.cmd == "derniere":
        show = json.loads(SHOW_FILE.read_text(encoding="utf-8"))
    elif args.cmd == "notifier":
        request("notify", text=args.message, duration=args.duree)
        return
    elif args.cmd == "quitter":
        request("quit")
        return
    elif args.cmd == "luminosite":
        request("brightness", value=args.valeur)
        return
    else:
        request("stop")
        return
    request("play", show=show)


if __name__ == "__main__":
    main()
