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
    """Tout _("…") littéral du code doit figurer dans locale/_cles.json."""
    import ast
    missing = set()
    for f in ["rog_flare2_launcher.py", "rog_flare2_matrix_paint.py", "rog_flare2_ui_ronde.py", "rog_flare2_maj.py"]:
        for node in ast.walk(ast.parse((ROOT / f).read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_" and node.args
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                if node.args[0].value not in SOURCES:
                    missing.add(node.args[0].value)
    assert not missing


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
