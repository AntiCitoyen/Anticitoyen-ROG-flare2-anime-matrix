"""Touches du clavier pour les effets « Réaction au clavier » et « Frappe », sous X11 et Wayland.

Sous Wayland, un programme ne voit pas les touches des autres fenêtres : pynput (X11)
ne reçoit rien. On lit alors directement les périphériques /dev/input (python3-evdev) ;
les codes evdev sont des positions physiques (QWERTY), ce qui convient à un effet qui
allume la LED à l'emplacement de la touche, quelle que soit la disposition.

Accès : l'utilisateur de la session doit pouvoir lire /dev/input/event* du clavier.
Règle udev optionnelle (clavier ROG seulement) : packaging/udev/73-rog-flare2-animate-touches.rules.

Noms transmis aux rappels : un caractère minuscule ('a', '1'), ou 'space', 'enter',
'backspace', 'shift', 'caps_lock' ; et pour les autres touches (couleurs des touches, « frappe ») :
'f1'…'f12', 'esc', 'tab', 'lctrl', 'rctrl', 'lalt', 'ralt', 'win', 'menu', 'rshift', flèches ('up'…),
'ins', 'del', 'home', 'end', 'pgup', 'pgdn', 'prtsc', 'scrlk', 'pause', 'num', pavé ('p0'…'p9', 'p/',
'p*', 'p-', 'p+', 'p.', 'penter'), ponctuation par position physique ('`', '-', '=', '[', ']', ';', "'",
'#', 'iso\\', ',', '.', '/').
"""
from __future__ import annotations

import os
import select
import threading

SPECIAL = {"KEY_SPACE": "space", "KEY_ENTER": "enter", "KEY_KPENTER": "penter", "KEY_BACKSPACE": "backspace",
           "KEY_LEFTSHIFT": "shift", "KEY_RIGHTSHIFT": "rshift", "KEY_CAPSLOCK": "caps_lock",
           "KEY_ESC": "esc", "KEY_TAB": "tab", "KEY_LEFTCTRL": "lctrl", "KEY_RIGHTCTRL": "rctrl",
           "KEY_LEFTALT": "lalt", "KEY_RIGHTALT": "ralt", "KEY_LEFTMETA": "win", "KEY_COMPOSE": "menu",
           "KEY_UP": "up", "KEY_DOWN": "down", "KEY_LEFT": "left", "KEY_RIGHT": "right", "KEY_INSERT": "ins",
           "KEY_DELETE": "del", "KEY_HOME": "home", "KEY_END": "end", "KEY_PAGEUP": "pgup",
           "KEY_PAGEDOWN": "pgdn", "KEY_SYSRQ": "prtsc", "KEY_SCROLLLOCK": "scrlk", "KEY_PAUSE": "pause",
           "KEY_NUMLOCK": "num", "KEY_KPSLASH": "p/", "KEY_KPASTERISK": "p*", "KEY_KPMINUS": "p-",
           "KEY_KPPLUS": "p+", "KEY_KPDOT": "p.", "KEY_GRAVE": "`", "KEY_MINUS": "-", "KEY_EQUAL": "=",
           "KEY_LEFTBRACE": "[", "KEY_RIGHTBRACE": "]", "KEY_SEMICOLON": ";", "KEY_APOSTROPHE": "'",
           "KEY_BACKSLASH": "#", "KEY_102ND": "iso\\", "KEY_COMMA": ",", "KEY_DOT": ".", "KEY_SLASH": "/",
           **{f"KEY_F{n}": f"f{n}" for n in range(1, 13)}, **{f"KEY_KP{n}": f"p{n}" for n in range(10)}}
# pavé numérique sous X11 (keysyms XK_KP_*) : pynput les rend comme des caractères, on garde la position
KEYPAD_VK = {0xFFB0 + n: f"p{n}" for n in range(10)} | {0xFFAF: "p/", 0xFFAA: "p*", 0xFFAD: "p-", 0xFFAB: "p+",
                                                     0xFFAE: "p.", 0xFFAC: "p.", 0xFF8D: "penter"}


def wayland() -> bool:
    return bool(os.environ.get("WAYLAND_DISPLAY")) or os.environ.get("XDG_SESSION_TYPE") == "wayland"


def evdev_name(code_name: str) -> str | None:
    """KEY_A -> 'a', KEY_1 -> '1', KEY_SPACE -> 'space', KEY_F1 -> 'f1', KEY_KP7 -> 'p7' ; None sinon."""
    if code_name in SPECIAL:
        return SPECIAL[code_name]
    tail = code_name[4:] if code_name.startswith("KEY_") else ""
    if len(tail) == 1 and tail.isalnum():
        return tail.lower()
    return None


def keyboards():
    """Claviers lisibles (ceux qui ont une touche A) ; liste vide sans evdev ou sans droits."""
    try:
        import evdev
    except ImportError:
        return []
    found = []
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
        except OSError:
            continue
        if evdev.ecodes.KEY_A in dev.capabilities().get(evdev.ecodes.EV_KEY, []):
            found.append(dev)
        else:
            dev.close()
    return found


class EvdevListener:
    """Lit les claviers /dev/input dans un fil ; stop() le termine."""

    def __init__(self, on_press, on_release, devices=None):
        import evdev
        self.ecodes = evdev.ecodes
        self.devices = keyboards() if devices is None else devices
        if not self.devices:
            raise OSError("aucun clavier lisible dans /dev/input")
        self.on_press, self.on_release = on_press, on_release
        self._r, self._w = os.pipe()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        fds = {d.fd: d for d in self.devices}
        try:
            while True:
                ready, _w, _x = select.select([*fds, self._r], [], [])
                if self._r in ready:
                    return
                for fd in ready:
                    try:
                        events = list(fds[fd].read())
                    except OSError:  # clavier débranché
                        fds.pop(fd).close()
                        continue
                    for ev in events:
                        if ev.type != self.ecodes.EV_KEY or ev.value == 2:  # 2 = répétition
                            continue
                        names = self.ecodes.KEY.get(ev.code)
                        for code_name in names if isinstance(names, list) else [names]:
                            name = evdev_name(code_name or "")
                            if name:
                                (self.on_press if ev.value == 1 else self.on_release)(name)
                                break
        finally:
            for d in fds.values():
                d.close()

    def stop(self):
        os.write(self._w, b"x")


class PynputListener:
    """Touches X11 (pynput), traduites dans les mêmes noms."""

    def __init__(self, on_press, on_release):
        from pynput import keyboard
        K = keyboard.Key
        special = {K.space: "space", K.enter: "enter", K.backspace: "backspace", K.shift: "shift",
                   K.shift_r: "rshift", K.caps_lock: "caps_lock", K.esc: "esc", K.tab: "tab", K.ctrl_l: "lctrl",
                   K.ctrl_r: "rctrl", K.alt_l: "lalt", K.alt_r: "ralt", K.alt_gr: "ralt", K.cmd: "win",
                   K.menu: "menu", K.up: "up", K.down: "down", K.left: "left", K.right: "right",
                   K.insert: "ins", K.delete: "del", K.home: "home", K.end: "end", K.page_up: "pgup",
                   K.page_down: "pgdn", K.print_screen: "prtsc", K.scroll_lock: "scrlk", K.pause: "pause",
                   K.num_lock: "num", **{getattr(K, f"f{n}"): f"f{n}" for n in range(1, 13)}}

        def name(key):
            if key in special:
                return special[key]
            vk = getattr(key, "vk", None)
            if vk in KEYPAD_VK:
                return KEYPAD_VK[vk]
            ch = getattr(key, "char", None)
            return ch.lower() if ch and len(ch) == 1 else None

        def wrap(cb):
            return lambda key: (n := name(key)) and cb(n)
        self.listener = keyboard.Listener(on_press=wrap(on_press), on_release=wrap(on_release))
        self.listener.start()
        self.listener.wait()  # prêt : un stop() immédiat ne trouve plus un écouteur à moitié créé

    def stop(self):
        try:
            self.listener.stop()
        except AttributeError:  # pynput (xorg) arrêté avant d'avoir ouvert son contexte d'enregistrement
            pass


def listen(on_press, on_release=lambda _n: None):
    """Source de touches adaptée à la session ; None si aucune n'est disponible (mode démonstration)."""
    order = (EvdevListener, PynputListener) if wayland() or not os.environ.get("DISPLAY") else (
        PynputListener, EvdevListener)
    for cls in order:
        try:
            return cls(on_press, on_release)
        except Exception:
            continue
    return None
