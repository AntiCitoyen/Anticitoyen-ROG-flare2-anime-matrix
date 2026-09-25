"""Environnement de test : dossiers de configuration, cache et socket isolés, sans clavier requis."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Avant tout import du projet : config, cache et socket du démon dans un dossier jetable
# (chemin court : un socket Unix est limité à 108 caractères).
_TMP = Path(tempfile.mkdtemp(prefix="amt-"))
os.environ["XDG_CONFIG_HOME"] = str(_TMP / "cfg")
os.environ["XDG_CACHE_HOME"] = str(_TMP / "cache")
os.environ["XDG_RUNTIME_DIR"] = str(_TMP / "run")
os.environ["ANIMEMATRIX_LANG"] = "fr"
os.environ["ANIMEMATRIX_FAUX_CLAVIER"] = "1"  # jamais le vrai clavier pendant les tests
(_TMP / "run").mkdir(parents=True, exist_ok=True)
