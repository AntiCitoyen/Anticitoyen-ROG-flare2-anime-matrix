"""Fin des commandes longues : ajout ou retrait de shell/animematrix-fin.sh dans ~/.bashrc et ~/.zshrc."""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
MARK = "# animematrix-fin"


def script_path() -> Path:
    """Script installé (paquet) ou celui du dépôt."""
    for p in (HERE / "shell" / "animematrix-fin.sh", HERE / "packaging" / "shell" / "animematrix-fin.sh"):
        if p.exists():
            return p
    return HERE / "shell" / "animematrix-fin.sh"


def rc_files() -> list[Path]:
    home = Path.home()
    return [home / ".bashrc"] + ([home / ".zshrc"] if (home / ".zshrc").exists() else [])


def enabled() -> bool:
    return any(MARK in _read(f) for f in rc_files())


def _read(f: Path) -> str:
    try:
        return f.read_text(encoding="utf-8")
    except OSError:
        return ""


def set_enabled(on: bool) -> None:
    """Ajoute (ou retire) une ligne marquée ; le reste du fichier n'est pas touché."""
    line = f'[ -r "{script_path()}" ] && . "{script_path()}"  {MARK}'
    for f in rc_files():
        text = _read(f)
        kept = [x for x in text.splitlines() if MARK not in x]
        if on:
            kept.append(line)
        new = "\n".join(kept) + ("\n" if kept else "")
        if new != text:
            f.write_text(new, encoding="utf-8")
