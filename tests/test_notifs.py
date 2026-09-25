"""Notifications du bureau : lecture de dbus-monitor, liste blanche, surimpression."""
import os
import shutil
import subprocess
import time

import pytest

import rog_flare2_notifs as N

SAMPLE = """method call time=1 sender=:1.9 -> destination=:1.52 serial=9 path=/org/freedesktop/Notifications; interface=org.freedesktop.Notifications; member=Notify
   string "thunderbird"
   uint32 0
   string ""
   string "Nouveau message"
   string "corps"
   array [
   ]
""".splitlines(keepends=True)


def test_parse_monitor():
    assert list(N.parse_monitor(SAMPLE)) == [("thunderbird", "Nouveau message", "corps")]


def test_matrix_text():
    assert N.matrix_text("Été : réunion") == "ETE : REUNION"


def test_config_roundtrip():
    N.save_config({"actif": True, "applis": ["a", "b"]})
    assert N.load_config() == {"actif": True, "applis": ["a", "b"]}


def _server_present():
    out = subprocess.run(["gdbus", "call", "--session", "--dest", "org.freedesktop.DBus", "--object-path",
                          "/org/freedesktop/DBus", "--method", "org.freedesktop.DBus.ListNames"],
                         capture_output=True, text=True).stdout if shutil.which("gdbus") else ""
    return "org.freedesktop.Notifications" in out


@pytest.mark.skipif(not (os.environ.get("DBUS_SESSION_BUS_ADDRESS") and shutil.which("notify-send")
                         and shutil.which("dbus-monitor") and _server_present()),
                    reason="bus de session avec serveur de notifications requis")
def test_live_notifications_with_whitelist():
    got = []
    w = N.NotificationWatcher(got.append)
    assert w.start({"actif": True, "applis": ["essaiam"]})
    time.sleep(0.8)
    subprocess.run(["notify-send", "-a", "autreappli", "Ignorée", "x"])
    subprocess.run(["notify-send", "-a", "essaiam", "Café prêt", "x"])
    subprocess.run(["notify-send", "AniMe Matrix", "nos propres notifications sont ignorées"])
    for _ in range(30):
        if got:
            break
        time.sleep(0.1)
    time.sleep(0.5)
    w.stop()
    assert got == ["ESSAIAM : CAFE PRET"]
