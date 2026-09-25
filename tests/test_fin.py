"""Fin des commandes longues : message, ligne ajoutée au shell, déclenchement réel dans bash."""
import os
import subprocess
from pathlib import Path

import rog_flare2_ctl as ctl
import rog_flare2_fin as fin


def test_end_message():
    assert ctl.end_message(0, 125, "make -j8") == "Terminé : make 2 min 05"
    assert ctl.end_message(2, 3700, "/usr/bin/cargo build") == "Échec (2) : cargo 1 h 01"


def test_rc_line_added_and_removed(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    (tmp_path / ".bashrc").write_text("alias ll='ls -l'\n")
    fin.set_enabled(True)
    fin.set_enabled(True)  # pas de doublon
    text = (tmp_path / ".bashrc").read_text()
    assert text.count(fin.MARK) == 1 and text.startswith("alias ll") and fin.enabled()
    fin.set_enabled(False)
    assert (tmp_path / ".bashrc").read_text() == "alias ll='ls -l'\n" and not fin.enabled()


def test_bash_hook_reports_long_commands(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = tmp_path / "appels"
    (bin_dir / "animematrix-ctl").write_text(f'#!/bin/sh\necho "$@" >> {calls}\n')
    (bin_dir / "animematrix-ctl").chmod(0o755)
    rc = tmp_path / "rc"
    rc.write_text(f". {fin.script_path()}\nANIMEMATRIX_FIN_SECONDES=1\n")
    script = "sleep 1.2\ntrue\nsleep 1.2; false\nless /dev/null </dev/null >/dev/null; sleep 1.2\nexit\n"
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "HOME": str(tmp_path)}
    subprocess.run(["bash", "--rcfile", str(rc), "-i"], input=script, text=True, env=env,
                   capture_output=True, timeout=30)
    import time
    time.sleep(0.5)
    lines = [line.split() for line in calls.read_text().splitlines()]  # fin CODE SECONDES COMMANDE…
    assert [(c[1], c[3:]) for c in lines] == [("0", ["sleep", "1.2"]), ("1", ["sleep", "1.2"])]
