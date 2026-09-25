"""Mises à jour d'AniMe Matrix depuis les releases GitHub du projet.

latest() interroge l'API publique (sans compte) ; download() récupère le .deb
de la release et vérifie son empreinte SHA-256 publiée par GitHub ; install()
l'installe avec les droits administrateur via pkexec (apt-get, sinon dpkg).

    rog_flare2_maj.py            affiche la dernière version et si elle est plus récente
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

from rog_flare2_i18n import _

REPO = "AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix"
API = f"https://api.github.com/repos/{REPO}/releases/latest"
RELEASES_URL = f"https://github.com/{REPO}/releases"
CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "animematrix"
STATE_FILE = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "rog-flare2" / "maj.json"
CHECK_EVERY = 24 * 3600  # vérification automatique : au plus une fois par jour


def parse_version(text: str) -> tuple[int, ...]:
    return tuple(int(n) for n in re.findall(r"\d+", text)[:3])


def packaged() -> bool:
    """Installé par le paquet .deb (sinon : lancé depuis les sources)."""
    return str(Path(__file__).resolve()).startswith("/usr/share/")


def latest(current: str, timeout: float = 8) -> dict:
    """Dernière release : version, page, notes, .deb (url, nom, sha256) ; lève OSError hors ligne."""
    req = urllib.request.Request(API, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": f"animematrix/{current}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    deb = next((a for a in data.get("assets", []) if a["name"].endswith("_all.deb")), None)
    digest = (deb or {}).get("digest") or ""
    return {
        "version": data["tag_name"].lstrip("v"),
        "page": data.get("html_url", RELEASES_URL),
        "notes": data.get("body") or "",
        "deb_url": deb["browser_download_url"] if deb else None,
        "deb_name": deb["name"] if deb else None,
        "sha256": digest.split(":", 1)[1] if digest.startswith("sha256:") else None,
    }


def is_newer(info: dict, current: str) -> bool:
    return parse_version(info["version"]) > parse_version(current)


def notes_excerpt(body: str, lang: str, max_lines: int = 12) -> str:
    """Section de la langue (français ou anglais) des notes bilingues, allégée du markdown."""
    marker = "## 🇫🇷" if lang == "fr" else "## 🇬🇧"
    part = body.split(marker, 1)[1] if marker in body else body
    part = part.split("\n---", 1)[0]
    lines = []
    in_code = False
    for line in part.splitlines()[1:]:
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.startswith("!["):
            continue
        line = re.sub(r"[*`]|^#+\s*", "", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines[:max_lines])


def download(info: dict, progress=None) -> Path:
    """Télécharge le .deb dans ~/.cache/animematrix ; progress(pourcent) ; vérifie le SHA-256."""
    if not info.get("deb_url"):
        raise OSError(_("pas de paquet .deb dans cette release"))
    if not re.fullmatch(r"[0-9a-f]{64}", info.get("sha256") or ""):
        raise OSError(_("empreinte SHA-256 absente : paquet rejeté"))
    name = info.get("deb_name") or ""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+~-]*_all\.deb", name):
        raise OSError(_("nom de paquet inattendu : paquet rejeté"))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest = CACHE_DIR / name
    part = dest.with_suffix(".part")
    h = hashlib.sha256()
    req = urllib.request.Request(info["deb_url"], headers={"User-Agent": "animematrix"})
    with urllib.request.urlopen(req, timeout=30) as r, open(part, "wb") as out:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while chunk := r.read(64 * 1024):
            out.write(chunk)
            h.update(chunk)
            done += len(chunk)
            if progress and total:
                progress(round(100 * done / total))
    if h.hexdigest() != info["sha256"]:
        part.unlink(missing_ok=True)
        raise OSError(_("empreinte SHA-256 différente de celle publiée : paquet rejeté"))
    part.replace(dest)
    return dest


# Exécuté en root : le paquet est d'abord copié dans un dossier à root puis revérifié, pour qu'un
# autre programme de la session ne puisse pas le remplacer entre la vérification et l'installation.
ROOT_INSTALL = r"""set -e
d=$(mktemp -d)
trap 'rm -rf "$d"' EXIT
cp -- "$1" "$d/paquet.deb"
echo "$2  $d/paquet.deb" | sha256sum -c --quiet -
chmod 755 "$d"; chmod 644 "$d/paquet.deb"
apt-get install -y "$d/paquet.deb" || dpkg -i "$d/paquet.deb"
"""


def install(deb: Path, sha256: str) -> tuple[bool, str]:
    """Installe avec pkexec (une fenêtre de mot de passe) : apt-get (dépendances), sinon dpkg -i."""
    if not re.fullmatch(r"[0-9a-f]{64}", sha256 or ""):
        return False, "empreinte SHA-256 absente"
    r = subprocess.run(["pkexec", "/bin/sh", "-c", ROOT_INSTALL, "animematrix-maj", str(deb), sha256],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return True, ""
    if r.returncode in (126, 127):  # authentification refusée ou annulée
        return False, "annulé"
    err = (r.stderr or r.stdout).strip().splitlines()
    return False, err[-1] if err else "erreur inconnue"


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {"auto": True, "last": 0}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state))


def due() -> bool:
    """Vérification automatique à faire maintenant (activée et dernière il y a plus d'un jour)."""
    s = load_state()
    return s.get("auto", True) and time.time() - s.get("last", 0) > CHECK_EVERY


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from rog_flare2_core import VERSION
    info = latest(VERSION)
    print(f"installée {VERSION} · dernière {info['version']} · {'plus récente' if is_newer(info, VERSION) else 'à jour'}")
    print(info["page"])
