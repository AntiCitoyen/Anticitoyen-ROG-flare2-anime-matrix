"""Catalogues de traduction complets, README (19 langues) cohérents, aucune mention d'outil d'IA."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SOURCES = json.loads((ROOT / "locale" / "_cles.json").read_text(encoding="utf-8"))
CODES = ["en", "es", "de", "it", "pt-BR", "nl", "pl", "ru", "uk", "tr", "ar", "hi", "zh-CN", "zh-TW", "ja", "ko", "vi", "id"]
PLACEHOLDER = re.compile(r"\{\w+\}")


@pytest.mark.parametrize("code", CODES)
def test_catalogue_complete(code):
    cat = json.loads((ROOT / "locale" / f"{code}.json").read_text(encoding="utf-8"))
    assert not set(SOURCES) - set(cat), "textes non traduits"
    for key, value in cat.items():
        assert set(PLACEHOLDER.findall(key)) == set(PLACEHOLDER.findall(value)), key


def test_every_ui_string_is_in_the_catalogue():
    """Tout _("…") littéral des modules, et chaque libellé passé à _() par variable, figure dans locale/_cles.json."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("i18n_textes", ROOT / "tests" / "i18n_textes.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    wanted = {**tool.literal_strings(), **tool.dynamic_strings()}
    assert not set(wanted) - set(SOURCES)


README = (ROOT / "README.md").read_text(encoding="utf-8")
ANCHORS = re.findall(r'<a id="([^"]+)"></a>', README)
CODE_BLOCKS = [re.sub(r"(?m)#.*$", "#", b) for b in re.findall(r"```.*?```", README, re.S)]


def links_of(text):
    return re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text) + re.findall(r'src="([^"]+)"', text)


@pytest.mark.parametrize("path", [ROOT / "README.md"] + [ROOT / "docs" / "readme" / f"README.{c}.md" for c in CODES])
def test_readme(path):
    text = path.read_text(encoding="utf-8")
    assert re.findall(r'<a id="([^"]+)"></a>', text) == ANCHORS
    for link in links_of(text):
        if not link.startswith("http"):
            assert (path.parent / link).resolve().exists(), link
    for anchor in re.findall(r"\]\(#([^)]+)\)", text):
        assert anchor in ANCHORS
    if path.name != "README.md":
        blocks = [re.sub(r"(?m)#.*$", "#", b) for b in re.findall(r"```.*?```", text, re.S)]
        assert blocks == CODE_BLOCKS, "commandes modifiées"


def test_no_ai_mention_in_published_files():
    import subprocess
    words = ["cl" + "aude", "anth" + "ropic", "chat" + "gpt", "open" + "ai"]  # écrit en morceaux : ce fichier est lu aussi
    pattern = re.compile(r"\b(" + "|".join(words) + r")\b", re.I)
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for name in tracked:
        f = ROOT / name
        if f.suffix in {".py", ".md", ".json", ".sh", ".service", ".desktop", ".yml"} and f.exists():
            assert not pattern.search(f.read_text(encoding="utf-8", errors="ignore")), name


def test_weblate_base_file_in_sync():
    """locale/_source.json (fichier de base Weblate) suit _cles.json et fr.json : tests/i18n_modele.py le régénère."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("i18n_modele", ROOT / "tests" / "i18n_modele.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    assert json.loads((ROOT / "locale" / "_source.json").read_text(encoding="utf-8")) == tool.build()
