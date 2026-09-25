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
(_TMP / "run").mkdir(mode=0o700, parents=True, exist_ok=True)  # le démon exige un dossier privé

# systemctl factice en tête du PATH : les tests ne touchent jamais aux services de la vraie session
# (« disable --now » arrêterait un vrai service). Il répond « non actif / non activé ».
_BIN = _TMP / "bin"
_BIN.mkdir()
(_BIN / "systemctl").write_text(f'#!/bin/sh\necho "$@" >> {_TMP / "systemctl.log"}\nexit 1\n')
(_BIN / "systemctl").chmod(0o755)
os.environ["PATH"] = f"{_BIN}:{os.environ['PATH']}"


def pytest_sessionfinish(session, exitstatus):
    """Démon lancé en arrière-plan par un test (lanceur, CLI) : arrêté en fin de session, sinon il reste."""
    import json
    import socket
    import time
    sock = _TMP / "run" / "animematrix.sock"
    try:
        with socket.socket(socket.AF_UNIX) as s:
            s.settimeout(2)
            s.connect(str(sock))
            s.sendall(json.dumps({"cmd": "quit"}).encode() + b"\n")
            s.recv(1024)
        time.sleep(0.5)
    except OSError:
        pass
