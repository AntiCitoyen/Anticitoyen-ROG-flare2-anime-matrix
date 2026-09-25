#!/usr/bin/env python3
"""Textes d'interface absents de locale/_cles.json : _("…") littéraux de tous les modules + libellés dynamiques."""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def literal_strings() -> dict[str, str]:
    found = {}
    for f in sorted(ROOT.glob("rog_flare2_*.py")):
        for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_" and node.args
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                found.setdefault(node.args[0].value, f.stem)
    return found


def dynamic_strings() -> dict[str, str]:
    """Libellés passés à _() par variable : noms et réglages d'effets (sources anglaises), listes de choix."""
    import rog_flare2_effets as E
    import rog_flare2_horloges as H
    import rog_flare2_ui_programme as U
    out = {}
    for name, cls in [*E.EFFECTS.items(), *E.AUDIO_EFFECTS.items()]:
        if not (cls.__module__ == "effects" or cls.__module__.startswith("rog_flare2_")):
            continue  # extensions : elles fournissent leurs propres noms traduits
        out.setdefault(name, "effets (source anglaise)")
        for spec in cls.PARAMS.values():
            out.setdefault(spec.get("label", ""), "effets (source anglaise)")
            for _key, label in spec.get("choices", []):
                out.setdefault(label, "effets (source française)")
    for label in [*H.FACE_LABELS.values(), *U.BadgesWindow.MIC.values(), *U.CONTENT_LABELS.values()]:
        out.setdefault(label, "lanceur (source française)")
    out.pop("", None)
    return out


if __name__ == "__main__":
    keys = json.loads((ROOT / "locale" / "_cles.json").read_text(encoding="utf-8"))
    wanted = {**{k: f"{v} (source française)" for k, v in literal_strings().items()}, **dynamic_strings()}
    missing = {k: v for k, v in wanted.items() if k not in keys}
    json.dump(missing, sys.stdout, ensure_ascii=False, indent=1)
