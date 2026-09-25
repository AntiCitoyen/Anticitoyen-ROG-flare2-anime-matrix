#!/usr/bin/python3
"""Icône de barre système AniMe Matrix (AyatanaAppIndicator, sinon Gtk.StatusIcon).

Menu rapide : ouvrir le lanceur, galerie, horloge, moniteur, morceau en cours,
dernière lecture, éteindre l'écran, luminosité. Commande le démon animematrixd.
Lancé par le python3 du système (PyGObject), au démarrage de session si l'option
« Icône dans la barre système » est cochée dans le lanceur.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rog_flare2_ctl as ctl  # noqa: E402
from rog_flare2_core import CONFIG_DIR  # noqa: E402
from rog_flare2_i18n import _  # noqa: E402

AUTOSTART = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "autostart" / "animematrix-tray.desktop"
PID_FILE = ctl.SOCKET_PATH.parent / "animematrix-tray.pid"


def icon() -> str:
    for p in (HERE / "packaging" / "animematrix.svg", Path("/usr/share/icons/hicolor/scalable/apps/animematrix.svg")):
        if p.exists():
            return str(p)
    return "input-keyboard"


def set_autostart(on: bool, command: str) -> None:
    """Lance l'icône à l'ouverture de session (fichier .desktop d'autostart) ou retire ce lancement."""
    if on:
        AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
        AUTOSTART.write_text("[Desktop Entry]\nType=Application\nName=AniMe Matrix\n"
                             f"Exec={command}\nIcon=animematrix\nX-GNOME-Autostart-enabled=true\n")
    elif AUTOSTART.exists() and "AniMe Matrix" in AUTOSTART.read_text():
        AUTOSTART.unlink()


def running() -> bool:
    try:
        pid = int(PID_FILE.read_text())
        return "rog_flare2_tray" in Path(f"/proc/{pid}/cmdline").read_text()
    except (OSError, ValueError):
        return False


def stop_running() -> None:
    if running():
        os.kill(int(PID_FILE.read_text()), 15)


def act(show: dict | None = None, **req):
    try:
        ctl.ensure_daemon()
        if show is not None:
            ctl.request("play", show=show)
        elif req:
            ctl.request(req.pop("cmd"), **req)
    except Exception as exc:  # démon absent, etc. : rien ne doit faire tomber l'icône
        print(f"animematrix-tray : {exc}", file=sys.stderr)


def build_menu():
    from gi.repository import Gtk
    from rog_flare2_programme import show_for
    menu = Gtk.Menu()

    def item(label, callback):
        mi = Gtk.MenuItem(label=label)
        mi.connect("activate", lambda _w: callback())
        menu.append(mi)

    launcher = HERE / "rog_flare2_launcher.py"
    python = HERE / ".venv" / "bin" / "python"
    item(_("Ouvrir AniMe Matrix"), lambda: subprocess.Popen(
        [str(python) if python.exists() else "/usr/bin/python3", str(launcher)], start_new_session=True))
    menu.append(Gtk.SeparatorMenuItem())
    item(_("Galerie GIF"), lambda: act(show_for("galerie")))
    item(_("Horloge"), lambda: act(show_for("horloge")))
    item(_("System Monitor"), lambda: act(show_for("moniteur")))
    item(_("Now Playing"), lambda: act(show_for("morceau")))
    item(_("Dernière lecture"), lambda: act(ctl_last()))
    from rog_flare2_listes import load_favorites, load_lists
    for title, entries in ((_("Favoris"), [(f.get("label", "?"), f.get("show")) for f in load_favorites()]),
                           (_("Listes de lecture"), [(name, {"type": "liste", "name": name})
                                                     for name in sorted(load_lists())])):
        if not entries:
            continue
        parent = Gtk.MenuItem(label=title)
        sub = Gtk.Menu()
        for label, show in entries:
            mi = Gtk.MenuItem(label=label)
            mi.connect("activate", lambda _w, show=show: act(show))
            sub.append(mi)
        parent.set_submenu(sub)
        menu.append(parent)
    item(_("Éteindre l'écran"), lambda: act(cmd="stop"))
    menu.append(Gtk.SeparatorMenuItem())
    bright = Gtk.MenuItem(label=_("Luminosité :").rstrip(" :："))
    sub = Gtk.Menu()
    for v in (25, 50, 75, 100):
        mi = Gtk.MenuItem(label=f"{v} %")
        mi.connect("activate", lambda _w, v=v: act(cmd="brightness", value=v))
        sub.append(mi)
    bright.set_submenu(sub)
    menu.append(bright)
    menu.append(Gtk.SeparatorMenuItem())
    item(_("Masquer l'icône"), Gtk.main_quit)
    menu.show_all()
    return menu


def ctl_last() -> dict | None:
    import json
    try:
        return json.loads((CONFIG_DIR / "lecture.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def main():
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GLib, Gtk
    if running():
        return
    menu = build_menu()
    ind = None
    try:
        gi.require_version("AyatanaAppIndicator3", "0.1")
        from gi.repository import AyatanaAppIndicator3 as AI
        ind = AI.Indicator.new("animematrix", icon(), AI.IndicatorCategory.HARDWARE)
        ind.set_status(AI.IndicatorStatus.ACTIVE)
        ind.set_title("AniMe Matrix")
        ind.set_menu(menu)
    except (ValueError, ImportError):
        status = Gtk.StatusIcon.new_from_file(icon()) if icon().endswith(".svg") else Gtk.StatusIcon()
        status.set_tooltip_text("AniMe Matrix")
        status.connect("popup-menu", lambda _i, b, t: menu.popup(None, None, None, None, b, t))
        status.connect("activate", lambda _i: menu.popup(None, None, None, None, 0, Gtk.get_current_event_time()))
    from rog_flare2_listes import FAVORITES_FILE, LISTS_FILE

    def stamp():
        return tuple(f.stat().st_mtime if f.exists() else 0 for f in (FAVORITES_FILE, LISTS_FILE))
    seen = [stamp()]

    def refresh():  # favoris ou listes modifiés dans le lanceur : menu refait
        nonlocal menu
        if stamp() != seen[0]:
            seen[0] = stamp()
            menu = build_menu()
            if ind is not None:
                ind.set_menu(menu)
        return True
    GLib.timeout_add_seconds(5, refresh)
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, 15, Gtk.main_quit)
    # PID écrit une fois l'arrêt propre en place : un SIGTERM plus tôt ne laisserait pas de PID périmé
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))
    try:
        Gtk.main()
    finally:
        PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
