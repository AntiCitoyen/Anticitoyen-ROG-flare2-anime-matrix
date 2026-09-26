"""Sauvegarde et restauration des réglages (~/.config/rog-flare2) dans une archive .zip.

Tout le dossier : couleurs et dessin des touches, programmation, listes, favoris, voyants, thème,
langue, interface, animation enregistrée (copie), extensions d'effets. Sans les secrets (jeton de la
télécommande, mot de passe OBS) sauf demande explicite. Avant une restauration, les réglages en place
sont d'abord sauvegardés dans ~/.config/rog-flare2/sauvegardes/.

    animematrix-ctl sauvegarde reglages.zip [--secrets]
    animematrix-ctl restaurer reglages.zip
"""
from __future__ import annotations

import io
import json
import re
import time
import zipfile
from pathlib import Path

from rog_flare2_core import CONFIG_DIR

BACKUP_DIR = CONFIG_DIR / "sauvegardes"
SECRETS = {"telecommande.json": ("jeton",), "voyants.json": ("obs_mot_de_passe",)}
SKIP = {"sauvegardes", "lecture.pid"}
SAFE_NAME = re.compile(r"[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)?")  # « effets/x.py » au plus
MAX_FILE, MAX_TOTAL, MAX_FILES = 8 << 20, 64 << 20, 500
MARK = "animematrix-reglages.json"


def _files(root: Path):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_file() and not path.is_symlink() and rel.split("/")[0] not in SKIP and SAFE_NAME.fullmatch(rel):
            yield rel, path


def export(dest: Path, secrets: bool = False, root: Path = CONFIG_DIR) -> int:
    """Écrit l'archive ; renvoie le nombre de fichiers."""
    from rog_flare2_core import VERSION
    count = 0
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(MARK, json.dumps({"version": VERSION, "date": time.strftime("%Y-%m-%d %H:%M"),
                                     "secrets": secrets}, indent=1))
        for rel, path in _files(root):
            data = path.read_bytes()
            if rel in SECRETS and not secrets:
                try:
                    cfg = json.loads(data)
                    for key in SECRETS[rel]:
                        cfg.pop(key, None)
                    data = json.dumps(cfg, ensure_ascii=False, indent=1).encode()
                except ValueError:
                    continue
            z.writestr(rel, data)
            count += 1
    return count


def check(archive: Path) -> list[str]:
    """Noms des fichiers d'une archive de réglages ; lève ValueError si elle est douteuse."""
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        if MARK not in names:
            raise ValueError("ce n'est pas une sauvegarde de réglages AniMe Matrix")
        if len(infos) > MAX_FILES or sum(i.file_size for i in infos) > MAX_TOTAL:
            raise ValueError("archive trop grande")
        for i in infos:
            name = i.filename
            if name == MARK:
                continue
            if i.is_dir() or not SAFE_NAME.fullmatch(name) or ".." in name.split("/") or i.file_size > MAX_FILE \
                    or name.split("/")[0] in SKIP:
                raise ValueError(f"entrée refusée dans l'archive : {name[:60]}")
    return [n for n in names if n != MARK]


def restore(archive: Path, root: Path = CONFIG_DIR) -> tuple[int, Path | None]:
    """Remplace les réglages par ceux de l'archive, après en avoir sauvegardé une copie.
    Les secrets absents de l'archive (jeton, mot de passe OBS) sont conservés."""
    names = check(archive)
    before = None
    if root.exists() and any(True for _ in _files(root)):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        before = BACKUP_DIR / time.strftime("avant-restauration-%Y%m%d-%H%M%S.zip")
        export(before, secrets=True, root=root)
    with zipfile.ZipFile(archive) as z:
        for name in names:
            data = z.read(name)
            target = root / name
            if name in SECRETS and target.exists():
                try:  # secrets gardés quand l'archive n'en contient pas
                    new, old = json.loads(data), json.loads(target.read_bytes())
                    for key in SECRETS[name]:
                        if key not in new and key in old:
                            new[key] = old[key]
                    data = json.dumps(new, ensure_ascii=False, indent=1).encode()
                except ValueError:
                    pass
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(target.name + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(target)
            if name in SECRETS:
                target.chmod(0o600)
    return len(names), before


def summary(archive: Path) -> dict:
    with zipfile.ZipFile(archive) as z:
        return json.load(io.BytesIO(z.read(MARK)))
