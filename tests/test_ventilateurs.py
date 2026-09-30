"""Ventilateurs : courbe, carte mère (hwmon simulé), alimentation Corsair (hidraw simulé), régulation, démon."""
import os
import socket
import threading

import pytest

import rog_flare2_ventilateurs as V


def test_curve_value():
    pts = [[40, 30], [70, 60], [85, 100]]
    assert V.curve_value(pts, 20) == 30 and V.curve_value(pts, 55) == 45 and V.curve_value(pts, 99) == 100
    assert V.curve_value([[70, 60], [40, 30]], 55) == 45  # points dans le désordre


def test_check_config():
    assert V.check_config({"canaux": {"cm:1": {"mode": "fixe", "valeur": 50}}}) is None
    assert "mode" in V.check_config({"canaux": {"cm:1": {"mode": "turbo"}}})
    assert "courbe" in V.check_config({"canaux": {"cm:1": {"mode": "courbe", "courbe": [[40]]}}})


@pytest.fixture
def board(tmp_path, monkeypatch):
    """Contrôleur nct6798 à deux pwm (SmartFan IV = 5) et sonde coretemp."""
    nct = tmp_path / "hwmon3"
    nct.mkdir()
    (nct / "name").write_text("nct6798\n")
    for n, rpm in ((1, 900), (2, 1200)):
        (nct / f"pwm{n}").write_text("128\n")
        (nct / f"pwm{n}_enable").write_text("5\n")
        (nct / f"fan{n}_input").write_text(f"{rpm}\n")
    cpu = tmp_path / "hwmon7"
    cpu.mkdir()
    (cpu / "name").write_text("coretemp\n")
    (cpu / "temp1_input").write_text("55000\n")
    monkeypatch.setattr(V, "HWMON", tmp_path)
    monkeypatch.setattr(V, "HIDRAW", tmp_path / "aucun")
    monkeypatch.setattr(V._NVML, "count", classmethod(lambda cls: 0))
    return nct, cpu


def test_motherboard_fixed_curve_and_restore(board):
    nct, cpu = board
    ctl = V.FanControl()
    ctl.start({"canaux": {"cm:1": {"mode": "fixe", "valeur": 10},  # sous le plancher de 20 %
                          "cm:2": {"mode": "courbe", "source": "cpu", "courbe": [[40, 30], [70, 60]]}}})
    ctl.tick()
    assert (nct / "pwm1_enable").read_text() == "1" and (nct / "pwm1").read_text() == str(round(20 * 255 / 100))
    assert ctl.applied == {"cm:1": 20, "cm:2": 45}
    (cpu / "temp1_input").write_text("53000\n")  # baisse de 2 % seulement : consigne gardée
    ctl.tick()
    assert ctl.applied["cm:2"] == 45
    (cpu / "temp1_input").write_text("95000\n")  # critique : 100 %
    ctl.tick()
    assert ctl.applied["cm:2"] == 100
    (nct / "pwm2_enable").write_text("5")  # repris par le micrologiciel (veille) : consigne renvoyée
    ctl.tick()
    assert (nct / "pwm2_enable").read_text() == "1"
    status = {c["id"]: c for c in ctl.status()}
    assert status["cm:2"]["rpm"] == 1200 and status["cm:2"]["mode"] == "courbe"
    ctl.stop()
    assert (nct / "pwm1_enable").read_text() == "5" and (nct / "pwm2_enable").read_text() == "5"
    assert not V._origins()


def test_unreadable_probe_returns_fan_to_firmware(board):
    nct, cpu = board
    ctl = V.FanControl()
    ctl.start({"canaux": {"cm:1": {"mode": "courbe", "source": "cpu", "courbe": [[40, 50]]}}})
    ctl.tick()
    assert (nct / "pwm1_enable").read_text() == "1"
    (cpu / "temp1_input").unlink()
    ctl.tick()
    assert (nct / "pwm1_enable").read_text() == "5" and "cm:1" in ctl.errors
    ctl.stop()


def test_restore_all_after_crash(board):
    nct, _cpu = board
    ctl = V.FanControl()
    ctl.start({"canaux": {"cm:2": {"mode": "fixe", "valeur": 70}}})
    ctl.tick()
    assert (nct / "pwm2_enable").read_text() == "1"  # le démon meurt ici sans rendre la main
    assert V.restore_all() == [] and (nct / "pwm2_enable").read_text() == "5"


def test_corsair_psu_protocol(tmp_path, monkeypatch):
    """Écritures PMBus sur un faux hidraw (paire de sockets) : mode logiciel, consigne, puis mode matériel."""
    ours, device = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    sent = []

    def firmware():
        while True:
            pkt = device.recv(65)
            if not pkt:
                return
            sent.append(pkt[1:4])
            device.send(pkt[1:3] + bytes(62))  # écho adresse + commande

    threading.Thread(target=firmware, daemon=True).start()
    monkeypatch.setattr(V.os, "open", lambda *_a: ours.fileno())
    monkeypatch.setattr(V.os, "close", lambda _fd: None)
    psu = V.CorsairPSU("/dev/hidrawX", None)
    psu.set(55)
    psu.auto()
    assert sent == [b"\x02\xf0\x01", b"\x02\x3b\x37", b"\x02\xf0\x00"]
    # déjà en mode logiciel à 25 % avant la prise en main (pilote corsair-psu) : rendue telle quelle
    hw = tmp_path / "hwmon5"
    hw.mkdir()
    (hw / "pwm1_enable").write_text("1\n")
    (hw / "pwm1").write_text("63\n")
    sent.clear()
    psu = V.CorsairPSU("/dev/hidrawX", hw)
    psu.set(55)
    psu.auto()
    assert sent == [b"\x02\xf0\x01", b"\x02\x3b\x37", b"\x02\xf0\x01", b"\x02\x3b\x19"]
    assert "alim" not in V._origins()
    ours.close()
    device.close()


def test_psu_found_by_hid_id(tmp_path, monkeypatch):
    d = tmp_path / "hidraw12" / "device"
    d.mkdir(parents=True)
    (d / "uevent").write_text("DRIVER=corsair-psu\nHID_ID=0003:00001B1C:00001C1F\n")
    monkeypatch.setattr(V, "HIDRAW", tmp_path)
    assert V._psu_node() == "/dev/hidraw12"


def test_gpu_helper_rejects_bad_arguments():
    import runpy
    helper = runpy.run_path(os.path.join(os.path.dirname(__file__), "..", "packaging", "animematrix-ventilateurs-gpu"))
    assert helper["main"](["0"]) == 2 and helper["main"](["x", "50"]) == 2 and helper["main"](["0", "50%"]) == 2


def test_daemon_command(board):
    from rog_flare2_demon import Daemon
    nct, _cpu = board
    d = Daemon()
    d.fans = V.FanControl()
    r = d.handle({"cmd": "ventilateurs"})
    assert r["ok"] and [c["id"] for c in r["canaux"]] == ["cm:1", "cm:2"]
    assert not d.handle({"cmd": "ventilateurs", "config": {"canaux": {"cm:1": {"mode": "x"}}}})["ok"]
    r = d.handle({"cmd": "ventilateurs", "config": {"canaux": {"cm:1": {"mode": "fixe", "valeur": 80}}}})
    assert r["ok"] and (nct / "pwm1").read_text() == str(round(80 * 255 / 100))
    assert V.load_config()["canaux"]["cm:1"]["valeur"] == 80
    d.fans.stop()
    assert (nct / "pwm1_enable").read_text() == "5"
