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

# systemctl factice en tête du PATH : les tests ne touchent jamais aux services de la vraie session
# (« disable --now » arrêterait un vrai service). Il répond « non actif / non activé ».
_BIN = _TMP / "bin"
_BIN.mkdir()
(_BIN / "systemctl").write_text(f'#!/bin/sh\necho "$@" >> {_TMP / "systemctl.log"}\nexit 1\n')
(_BIN / "systemctl").chmod(0o755)
os.environ["PATH"] = f"{_BIN}:{os.environ['PATH']}"
