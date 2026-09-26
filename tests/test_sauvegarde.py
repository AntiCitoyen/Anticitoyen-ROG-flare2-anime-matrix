"""Sauvegarde et restauration des réglages : contenu, secrets, archive douteuse, copie préalable."""
import json
import zipfile

import pytest

import rog_flare2_sauvegarde as S


def make_config(root):
    (root / "effets").mkdir(parents=True)
    (root / "rgb.json").write_text(json.dumps({"mode": "perso", "perso": {"18": "#ff0000"}}))
    (root / "telecommande.json").write_text(json.dumps({"actif": True, "jeton": "SECRET-JETON"}))
    (root / "voyants.json").write_text(json.dumps({"obs": True, "obs_mot_de_passe": "SECRET-OBS"}))
    (root / "theme").write_text("ROG Classic\n")
    (root / "effets" / "mon_effet.py").write_text("# extension\n")


def test_export_without_secrets_then_restore(tmp_path, monkeypatch):
    src, dst = tmp_path / "a", tmp_path / "b"
    make_config(src)
    archive = tmp_path / "r.zip"
    assert S.export(archive, root=src) == 5
    raw = b"".join(zipfile.ZipFile(archive).read(n) for n in zipfile.ZipFile(archive).namelist())
    assert b"SECRET" not in raw
    dst.mkdir()
    (dst / "telecommande.json").write_text(json.dumps({"jeton": "JETON-DU-NOUVEAU-PC"}))
    monkeypatch.setattr(S, "BACKUP_DIR", tmp_path / "copies")
    n, before = S.restore(archive, root=dst)
    assert n == 5 and before is not None and before.exists()
    assert json.loads((dst / "rgb.json").read_text())["perso"] == {"18": "#ff0000"}
    assert json.loads((dst / "telecommande.json").read_text()) == {"actif": True, "jeton": "JETON-DU-NOUVEAU-PC"}
    assert (dst / "effets" / "mon_effet.py").exists() and (dst / "telecommande.json").stat().st_mode & 0o077 == 0


def test_secrets_only_on_request(tmp_path):
    make_config(tmp_path / "c")
    S.export(tmp_path / "s.zip", secrets=True, root=tmp_path / "c")
    assert b"SECRET-OBS" in zipfile.ZipFile(tmp_path / "s.zip").read("voyants.json")


@pytest.mark.parametrize("name", ["../evil.json", "/etc/passwd", "a/b/c.json", "sauvegardes/x.zip"])
def test_suspicious_archives_are_refused(tmp_path, name):
    archive = tmp_path / "x.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(S.MARK, "{}")
        z.writestr(name, "x")
    with pytest.raises(ValueError):
        S.check(archive)
    with zipfile.ZipFile(tmp_path / "y.zip", "w") as z:
        z.writestr("rgb.json", "{}")  # pas une sauvegarde AniMe Matrix
    with pytest.raises(ValueError):
        S.check(tmp_path / "y.zip")
