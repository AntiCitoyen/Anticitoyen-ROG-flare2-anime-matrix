"""Traduction de l'interface : _("texte source") -> texte dans la langue choisie.

Les textes sources sont ceux du code (français pour le lanceur, anglais pour
l'éditeur de dessin et les effets PolyWollyWin). Chaque langue a son catalogue
locale/<code>.json {source: traduction} ; un texte absent reste en source.

Langue : ~/.config/rog-flare2/langue (réglée dans le lanceur), sinon
ANIMEMATRIX_LANG, sinon la langue du système (LANGUAGE, LC_ALL, LC_MESSAGES,
LANG), sinon l'anglais.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

LANGUAGES = {
    "fr": "Français", "en": "English", "es": "Español", "de": "Deutsch", "it": "Italiano",
    "pt-BR": "Português (Brasil)", "nl": "Nederlands", "pl": "Polski", "ru": "Русский",
    "uk": "Українська", "tr": "Türkçe", "ar": "العربية", "hi": "हिन्दी", "zh-CN": "简体中文",
    "zh-TW": "繁體中文", "ja": "日本語", "ko": "한국어", "vi": "Tiếng Việt", "id": "Bahasa Indonesia",
}
LOCALE_DIR = Path(__file__).parent / "locale"
LANG_FILE = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "rog-flare2" / "langue"


def _normalize(tag: str) -> str | None:
    """fr_FR.UTF-8 -> fr ; pt_PT -> pt-BR ; zh_HK -> zh-TW ; inconnu -> None."""
    tag = tag.split(".")[0].split("@")[0].replace("_", "-")
    if not tag or tag in ("C", "POSIX"):
        return None
    lang, _, region = tag.partition("-")
    if lang == "zh":
        return "zh-TW" if region.upper() in ("TW", "HK", "MO") or "Hant" in tag else "zh-CN"
    if lang == "pt":
        return "pt-BR"
    return lang if lang in LANGUAGES else None


def detect() -> str:
    try:
        saved = LANG_FILE.read_text().strip()
        if saved in LANGUAGES:
            return saved
    except OSError:
        pass
    candidates = [os.environ.get("ANIMEMATRIX_LANG", "")]
    candidates += os.environ.get("LANGUAGE", "").split(":")
    candidates += [os.environ.get(v, "") for v in ("LC_ALL", "LC_MESSAGES", "LANG")]
    for tag in candidates:
        code = _normalize(tag)
        if code:
            return code
    return "en"


def save_language(code: str) -> None:
    LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LANG_FILE.write_text(code + "\n")


LANG = detect()
try:
    _CATALOG: dict[str, str] = json.loads((LOCALE_DIR / f"{LANG}.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    _CATALOG = {}


def _(text: str) -> str:
    return _CATALOG.get(text) or text


if __name__ == "__main__":  # rog_flare2_i18n.py "texte" -> traduction (scripts shell)
    import sys
    print(_(" ".join(sys.argv[1:])))
