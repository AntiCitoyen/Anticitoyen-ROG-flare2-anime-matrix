"""Couleurs des touches (rog_flare2_rgb) : rapports, réglage, fil du démon, sans clavier."""
import json
import time

import rog_flare2_demon as D
import rog_flare2_rgb as R


def test_arc_en_ciel_comme_valide_sur_le_clavier():
    report = R.effect_report("arc-en-ciel")
    assert len(report) == 64
    assert report[:40].hex() == ("512c04008064000402070eff00001cff7f002affff0039"
                                 "00ff004700ffff550000ff648b00ff0000")
    assert R.effect_report("statique", [(1, 2, 3)], brightness=60)[:12].hex() == "512c00008032000002010203"
    assert R.effect_report("sable", direction="bas")[7] == 2
    assert R.effect_report("respiration", [(9, 9, 9), (1, 1, 1)])[6] == 16  # deux couleurs choisies
    assert R.effect_report("pluie", random=True)[6] == 1


def test_mode_direct_comme_armoury_crate():
    reports = R.direct_reports({i: (i, 0, 0) for i in R.LEDS})
    assert len(R.LEDS) == 210 and len(reports) == 14
    assert [r[2] for r in reports] == list(range(210, 0, -15))
    assert reports[0][4:12] == bytes([0x00, 0, 0, 0, 0x08, 8, 0, 0])  # rangée 0 d'abord, colonne par colonne


def test_reglage_repris_d_openrgb(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "CONFIG_FILE", tmp_path / "rgb.json")
    monkeypatch.setattr(R, "LEGACY_FILE", tmp_path / "openrgb.json")
    assert R.load_config()["mode"] == "clavier"
    (tmp_path / "openrgb.json").write_text(json.dumps({"mode": "pulsation"}))
    assert R.load_config()["mode"] == "pulsation"
    R.save_config({**R.DEFAULT_CONFIG, "effet": "pluie"})
    assert R.load_config()["effet"] == "pluie"


def test_fil_theme_puis_retour_a_l_effet_du_clavier():
    t = R.FakeRGBTransport()
    lights = R.KeyboardLights(lambda: 0.5, lambda: "#ff8000", transport=t)
    lights.start({"mode": "theme"})
    time.sleep(0.3)
    assert t.reports and t.reports[0][:2] == b"\xc0\x81" and t.reports[0][5:8] == bytes([255, 128, 0])
    lights.stop()
    assert t.reports[-1][:2] == b"\x51\x2c"  # effet enregistré réaffiché


def test_commande_du_demon():
    d = D.Daemon()
    try:
        r = d.handle({"cmd": "rgb", "config": {"mode": "clavier", "effet": "statique", "couleurs": ["#00ff00"]}})
        assert r["ok"] and R.load_config()["effet"] == "statique"
        sent = d.rgb.transport.reports
        assert sent[-2][:3] == bytes([0x51, 0x2C, 0x00]) and sent[-2][9:12] == bytes([0, 255, 0])
        assert sent[-1][:2] == b"\x50\x55"
        assert d.handle({"cmd": "rgb", "config": {"effet": "inconnu"}})["ok"] is False
        assert d.handle({"cmd": "status"})["rgb"] == "clavier"
    finally:
        d.stop()
