"""Fenêtre active : lecture des réponses de chaque compositeur (réponses simulées)."""
import json

import rog_flare2_fenetre as F


def fake(monkeypatch, answers):
    monkeypatch.setattr(F.shutil, "which", lambda _c: "/usr/bin/x")
    monkeypatch.setattr(F, "_run", lambda cmd, env=None: answers(cmd))


def test_x11(monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    fake(monkeypatch, lambda cmd: "_NET_ACTIVE_WINDOW(WINDOW): window id # 0x3a00007" if "-root" in cmd else
         'WM_CLASS(STRING) = "steam_app_570", "steam_app_570"\n_NET_WM_NAME(UTF8_STRING) = "Dota 2"\n'
         "_NET_WM_STATE(ATOM) = _NET_WM_STATE_FULLSCREEN\n")
    assert F.x11() == {"app": "steam_app_570", "title": "Dota 2", "fullscreen": True}


def test_sway(monkeypatch):
    monkeypatch.setenv("SWAYSOCK", "/run/sway.sock")
    tree = {"type": "root", "nodes": [{"type": "output", "nodes": [{"type": "workspace", "nodes": [
        {"type": "con", "focused": False, "app_id": "foot", "name": "t"},
        {"type": "con", "focused": True, "app_id": "firefox", "name": "Vidéo", "fullscreen_mode": 1}]}]}]}
    fake(monkeypatch, lambda cmd: json.dumps(tree))
    assert F.sway() == {"app": "firefox", "title": "Vidéo", "fullscreen": True}


def test_hyprland(monkeypatch):
    monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "abc")
    fake(monkeypatch, lambda cmd: json.dumps({"class": "mpv", "title": "film", "fullscreen": 2}))
    assert F.hyprland() == {"app": "mpv", "title": "film", "fullscreen": True}


def test_gnome_window_calls(monkeypatch):
    windows = [{"wm_class": "org.gnome.Nautilus", "focus": False}, {"wm_class": "Blender", "title": "b", "focus": True}]
    fake(monkeypatch, lambda cmd: f"('{json.dumps(windows)}',)\n")
    assert F.gnome() == {"app": "blender", "title": "b", "fullscreen": False}


def test_wayland_order_falls_back_to_x11(monkeypatch):
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    for name in ("sway", "hyprland", "kde", "gnome"):
        monkeypatch.setattr(F, name, lambda: None)
    monkeypatch.setattr(F, "x11", lambda: {"app": "xterm", "title": "", "fullscreen": False})
    assert F.active_window()["app"] == "xterm"
