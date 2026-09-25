"""Fenêtre active (application, titre, plein écran), sous X11 et sous Wayland.

Sert à éteindre l'écran quand une application est en plein écran et aux profils par
application. Wayland n'a pas d'interface commune : on interroge le compositeur.

- X11 (et fenêtres XWayland) : xprop (_NET_ACTIVE_WINDOW, WM_CLASS, _NET_WM_STATE)
- Sway : swaymsg -t get_tree        - Hyprland : hyprctl activewindow -j
- KDE Plasma : kdotool (s'il est installé)
- GNOME : extension « Window Calls » (org.gnome.Shell.Extensions.Windows), si elle est active
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess


def _run(cmd: list[str], env: dict | None = None) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=2, env=env).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def _window(app: str, title: str = "", fullscreen: bool = False) -> dict | None:
    return {"app": app.strip().lower(), "title": title.strip(), "fullscreen": bool(fullscreen)} if app else None


def x11() -> dict | None:
    if not os.environ.get("DISPLAY") or not shutil.which("xprop"):
        return None
    out = _run(["xprop", "-root", "_NET_ACTIVE_WINDOW"]).split()
    win = out[-1] if out else ""
    if win in ("", "0x0") or not win.startswith("0x"):
        return None
    props = _run(["xprop", "-id", win, "WM_CLASS", "_NET_WM_NAME", "_NET_WM_STATE"])
    app = title = ""
    for line in props.splitlines():
        if line.startswith("WM_CLASS") and '"' in line:
            app = line.split('"')[-2]  # classe (2e chaîne), ex. "Firefox"
        elif line.startswith("_NET_WM_NAME") and '"' in line:
            title = line.split("=", 1)[1].strip().strip('"')
    return _window(app, title, "_NET_WM_STATE_FULLSCREEN" in props)


def _sway_env() -> dict | None:
    env = dict(os.environ)
    if not env.get("SWAYSOCK"):
        socks = glob.glob(os.path.join(env.get("XDG_RUNTIME_DIR", ""), "sway-ipc.*.sock"))
        if not socks:
            return None
        env["SWAYSOCK"] = socks[0]
    return env


def sway() -> dict | None:
    env = _sway_env() if shutil.which("swaymsg") else None
    if env is None:
        return None
    try:
        tree = json.loads(_run(["swaymsg", "-t", "get_tree"], env) or "null")
    except ValueError:
        return None
    stack = [tree] if tree else []
    while stack:
        node = stack.pop()
        if node.get("focused") and node.get("type") in ("con", "floating_con"):
            app = node.get("app_id") or (node.get("window_properties") or {}).get("class", "")
            return _window(app or "", node.get("name") or "", node.get("fullscreen_mode", 0) != 0)
        stack.extend(node.get("nodes", []) + node.get("floating_nodes", []))
    return None


def hyprland() -> dict | None:
    if not shutil.which("hyprctl"):
        return None
    env = dict(os.environ)
    if not env.get("HYPRLAND_INSTANCE_SIGNATURE"):
        sigs = glob.glob(os.path.join(env.get("XDG_RUNTIME_DIR", ""), "hypr", "*", ".socket.sock"))
        if not sigs:
            return None
        env["HYPRLAND_INSTANCE_SIGNATURE"] = os.path.basename(os.path.dirname(sigs[0]))
    try:
        w = json.loads(_run(["hyprctl", "activewindow", "-j"], env) or "{}")
    except ValueError:
        return None
    return _window(w.get("class", ""), w.get("title", ""), w.get("fullscreen") not in (None, False, 0))


def kde() -> dict | None:
    if not shutil.which("kdotool"):
        return None
    wid = _run(["kdotool", "getactivewindow"]).strip()
    if not wid:
        return None
    return _window(_run(["kdotool", "getwindowclassname", wid]), _run(["kdotool", "getwindowname", wid]))


def gnome() -> dict | None:
    if not shutil.which("gdbus"):
        return None
    out = _run(["gdbus", "call", "--session", "--dest", "org.gnome.Shell", "--object-path",
                "/org/gnome/Shell/Extensions/Windows", "--method", "org.gnome.Shell.Extensions.Windows.List"])
    start, end = out.find("["), out.rfind("]")  # réponse : ('[{...}, ...]',)
    if start < 0:
        return None
    try:
        windows = json.loads(out[start:end + 1])
    except ValueError:
        return None
    for w in windows:
        if w.get("focus"):
            return _window(w.get("wm_class") or w.get("wm_class_instance") or "", w.get("title", ""),
                           w.get("fullscreen", False))
    return None


def active_window() -> dict | None:
    """{"app": classe en minuscules, "title": ..., "fullscreen": bool} ; None si inconnue."""
    wayland = bool(os.environ.get("WAYLAND_DISPLAY")) or os.environ.get("XDG_SESSION_TYPE") == "wayland"
    backends = (sway, hyprland, kde, gnome, x11) if wayland else (x11, sway, hyprland)
    for backend in backends:
        w = backend()
        if w:
            return w
    return None
