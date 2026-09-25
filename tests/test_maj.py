"""Mises à jour : versions, extraits de notes, téléchargement vérifié (serveur local)."""
import hashlib
import http.server
import threading

import pytest

import rog_flare2_maj as maj

NOTES = """## 🇬🇧 English

### What's new
- **Thing**: it works.
```bash
sudo dpkg -i x.deb
```

---

## 🇫🇷 Français

### Nouveautés
- **Truc** : ça marche.
"""


def test_versions():
    assert maj.parse_version("v1.10.2") == (1, 10, 2)
    assert maj.is_newer({"version": "1.4.0"}, "1.3.9")
    assert not maj.is_newer({"version": "1.3.0"}, "1.3.0")


def test_notes_excerpt_picks_language():
    fr = maj.notes_excerpt(NOTES, "fr")
    en = maj.notes_excerpt(NOTES, "ja")  # langue sans section : anglais
    assert "Truc : ça marche." in fr and "Thing" not in fr
    assert "Thing: it works." in en and "dpkg" not in en


@pytest.fixture
def deb_server(tmp_path):
    payload = b"paquet factice" * 1000
    (tmp_path / "x_all.deb").write_bytes(payload)

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(tmp_path), **kw)

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}/x_all.deb", hashlib.sha256(payload).hexdigest()
    srv.shutdown()


def test_download_verifies_checksum(deb_server):
    url, digest = deb_server
    info = {"deb_url": url, "deb_name": "x_all.deb", "sha256": digest}
    seen = []
    path = maj.download(info, seen.append)
    assert path.exists() and seen[-1] == 100


def test_download_rejects_bad_checksum(deb_server):
    url, _digest = deb_server
    with pytest.raises(OSError):
        maj.download({"deb_url": url, "deb_name": "y_all.deb", "sha256": "0" * 64})
    assert not (maj.CACHE_DIR / "y_all.deb").exists()


def test_state_and_due():
    maj.save_state({"auto": True, "last": 0})
    assert maj.due()
    maj.save_state({"auto": False, "last": 0})
    assert not maj.due()


def test_download_needs_checksum_and_clean_name(deb_server):
    url, digest = deb_server
    with pytest.raises(OSError):
        maj.download({"deb_url": url, "deb_name": "x_all.deb", "sha256": None})
    with pytest.raises(OSError):
        maj.download({"deb_url": url, "deb_name": "../../.bashrc_all.deb", "sha256": digest})


def test_root_install_script_checks_its_own_copy(tmp_path):
    """Le script root (ici lancé sans pkexec, apt-get factice) refuse un paquet d'une autre empreinte."""
    import subprocess
    deb = tmp_path / "p_all.deb"
    deb.write_bytes(b"paquet")
    good = hashlib.sha256(b"paquet").hexdigest()
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "apt-get").write_text(f'#!/bin/sh\necho "$@" > {tmp_path / "apt"}\n')
    (fake / "apt-get").chmod(0o755)
    env = {"PATH": f"{fake}:/usr/bin:/bin"}
    run = lambda sha: subprocess.run(["/bin/sh", "-c", maj.ROOT_INSTALL, "x", str(deb), sha], env=env,
                                     capture_output=True, text=True)
    assert run("0" * 64).returncode != 0 and not (tmp_path / "apt").exists()
    assert run(good).returncode == 0 and "paquet.deb" in (tmp_path / "apt").read_text()
    assert maj.install(deb, "pas-une-empreinte") == (False, "empreinte SHA-256 absente")
