#!/usr/bin/env python3
"""Génère packaging/animematrix.desktop, traduit depuis locale/*.json."""
import json
from pathlib import Path

DEPOT = Path(__file__).resolve().parent.parent
CATALOGS = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((DEPOT / "locale").glob("*.json"))}


def entry(key: str, source: str) -> list[str]:
    """Valeur par défaut en anglais, puis une ligne par langue (sources françaises)."""
    base = CATALOGS.get("en", {}).get(source, source)
    lines = [f"{key}={base}"]
    for code, cat in CATALOGS.items():
        text = source if code == "fr" else cat.get(source)
        if text and text != base:
            lines.append(f"{key}[{code.replace('-', '_')}]={text}")
    return lines


out = ["[Desktop Entry]", "Type=Application", "Name=AniMe Matrix"]
out += entry("GenericName", "Écran AniMe Matrix du clavier ROG")
out += entry("Comment", "GIF, horloge, effets et visualiseurs audio sur l'écran du ROG Strix Flare II Animate")
out += ["Exec=animematrix", "Icon=animematrix", "Terminal=false", "Categories=Utility;",
        "Keywords=rog;asus;clavier;keyboard;matrix;anime;gif;led;", "StartupNotify=true",
        "Actions=gif;horloge;off;"]
for action, label in (("gif", "Galerie GIF"), ("horloge", "Horloge"), ("off", "Éteindre l'écran")):
    out += ["", f"[Desktop Action {action}]"] + entry("Name", label) + [f"Exec=animematrix-bascule {action}"]
(DEPOT / "packaging" / "animematrix.desktop").write_text("\n".join(out) + "\n", encoding="utf-8")
