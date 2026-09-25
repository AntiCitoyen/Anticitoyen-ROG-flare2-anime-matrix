#!/usr/bin/env python3
"""Régénère locale/_source.json, fichier de base (monolingue) pour Weblate : clé -> texte source en français.

Clés françaises : le texte lui-même ; clés anglaises (noms et réglages d'effets) : leur traduction de fr.json.
    .venv/bin/python tests/i18n_modele.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALE = ROOT / "locale"


def build() -> dict[str, str]:
    keys = json.loads((LOCALE / "_cles.json").read_text(encoding="utf-8"))
    fr = json.loads((LOCALE / "fr.json").read_text(encoding="utf-8"))
    return {k: fr.get(k, k) for k in keys}


if __name__ == "__main__":
    (LOCALE / "_source.json").write_text(json.dumps(build(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
