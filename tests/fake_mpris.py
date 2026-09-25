"""Faux lecteur MPRIS pour les tests (python3 système avec PyGObject) : titre et artiste en argument."""
import sys

from gi.repository import Gio, GLib

XML = """<node><interface name="org.mpris.MediaPlayer2.Player">
<property name="PlaybackStatus" type="s" access="read"/><property name="Metadata" type="a{sv}" access="read"/>
</interface></node>"""
title, artist = sys.argv[1], sys.argv[2]


def get_property(conn, sender, path, iface, name):
    if name == "PlaybackStatus":
        return GLib.Variant("s", "Playing")
    return GLib.Variant("a{sv}", {"xesam:title": GLib.Variant("s", title),
                                  "xesam:artist": GLib.Variant("as", [artist])})


def on_bus(conn, name):
    info = Gio.DBusNodeInfo.new_for_xml(XML).interfaces[0]
    conn.register_object("/org/mpris/MediaPlayer2", info, None, get_property, None)


Gio.bus_own_name(Gio.BusType.SESSION, "org.mpris.MediaPlayer2.fauxlecteur", 0, on_bus, None, None)
GLib.MainLoop().run()
