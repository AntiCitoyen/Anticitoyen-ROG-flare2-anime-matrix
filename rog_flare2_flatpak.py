"""Particularités du paquet Flatpak : pas de systemd ni d'apt dans le bac à sable.

- le démon est lancé par le lanceur (processus détaché) ;
- démarrage avec la session : portail Background (autostart de « animematrixd ») ;
- mises à jour : par Flatpak (logithèque, flatpak update), pas par le lanceur.
"""
from __future__ import annotations

import os
import subprocess

APP_ID = os.environ.get("FLATPAK_ID", "")


def in_flatpak() -> bool:
    return bool(APP_ID) or os.path.exists("/.flatpak-info")


def request_autostart(on: bool, reason: str = "") -> bool:
    """Demande (ou retire) le démarrage de animematrixd avec la session ; le système peut demander l'accord."""
    options = (f"{{'autostart': <{'true' if on else 'false'}>, 'commandline': <['animematrixd']>, "
               f"'reason': <{reason!r}>}}")
    try:
        r = subprocess.run(["gdbus", "call", "--session", "--dest", "org.freedesktop.portal.Desktop",
                            "--object-path", "/org/freedesktop/portal/desktop",
                            "--method", "org.freedesktop.portal.Background.RequestBackground", "", options],
                           capture_output=True, timeout=10)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False
