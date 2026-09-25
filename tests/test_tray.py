"""Icône de barre système : lancement au démarrage de session et exécution réelle (python3 du système)."""
import os
import subprocess
import time
from pathlib import Path

import pytest

import rog_flare2_tray as T

HAS_GI = subprocess.run(["/usr/bin/python3", "-c", "import gi; gi.require_version('Gtk', '3.0')"],
                        capture_output=True).returncode == 0


def test_autostart_on_off():
    T.set_autostart(True, "animematrix-tray")
    assert "Exec=animematrix-tray" in T.AUTOSTART.read_text()
    T.set_autostart(False, "animematrix-tray")
    assert not T.AUTOSTART.exists()


def test_autostart_never_removes_foreign_file():
    T.AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
    T.AUTOSTART.write_text("[Desktop Entry]\nName=Autre\n")
    T.set_autostart(False, "x")
    assert T.AUTOSTART.exists()
    T.AUTOSTART.unlink()


@pytest.mark.skipif(not (os.environ.get("DISPLAY") and HAS_GI), reason="affichage X et PyGObject requis")
def test_tray_runs_and_stops():
    root = Path(__file__).resolve().parent.parent
    proc = subprocess.Popen(["/usr/bin/python3", str(root / "rog_flare2_tray.py")], env=os.environ.copy())
    try:
        for _ in range(150):  # premier lancement : compilation des modules
            if T.running():
                break
            time.sleep(0.1)
        assert T.running() and proc.poll() is None
        T.stop_running()
        proc.wait(5)
        assert not T.PID_FILE.exists()
    finally:
        if proc.poll() is None:
            proc.kill()
