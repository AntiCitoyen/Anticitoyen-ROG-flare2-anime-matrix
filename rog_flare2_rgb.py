#!/usr/bin/env python3
"""Couleurs et effets des touches du ROG Strix Flare II Animate, sans OpenRGB.

Interface HID 1 (page 0xFF00), rapports de 64 octets, sans numéro de rapport :
  - effets du clavier (gardés en mémoire)   51 2C mode 00 vitesse luminosité mode_couleur direction …
  - enregistrer l'effet                      50 55
  - couleur par touche (mode direct)         C0 81 reste 00 + 15 × (index, R, G, B)
Index d'une touche = colonne × 8 + rangée (30 colonnes, 7 rangées : 210 LED), relevé sur Armoury Crate.
"""
from __future__ import annotations

import json
import os
import threading
import time

from rog_flare2_core import CONFIG_DIR

CONFIG_FILE = CONFIG_DIR / "rgb.json"
LEGACY_FILE = CONFIG_DIR / "openrgb.json"  # réglage des versions ≤ 1.6.0 (OpenRGB)

VID, PID = 0x0B05, 0x19FC
IFACE = 1
REPORT = 64
COLUMNS, ROWS = 30, 7
LEDS = [c * 8 + r for c in range(COLUMNS) for r in range(ROWS)]

# Touches : nom de position physique (QWERTY) -> index ; disposition ISO du Flare II Animate
# (contrôleur Aura TUF d'OpenRGB), plus la barre oblique ANSI. AZERTY : caractère gravé -> position.
KEYS = {
    "ESC": 0x00, "`": 0x01, "TAB": 0x02, "CAPS": 0x03, "LSHIFT": 0x04, "LCTRL": 0x05, "1": 0x11, "ISO\\": 0x0C,
    "WIN": 0x15, "F1": 0x18, "2": 0x19, "Q": 0x12, "A": 0x13, "Z": 0x14, "LALT": 0x1D, "F2": 0x20, "3": 0x21,
    "W": 0x1A, "S": 0x1B, "X": 0x1C, "F3": 0x28, "4": 0x29, "E": 0x22, "D": 0x23, "C": 0x24, "F4": 0x30,
    "5": 0x31, "R": 0x2A, "F": 0x2B, "V": 0x2C, "6": 0x39, "T": 0x32, "G": 0x33, "B": 0x34, "SPACE": 0x35,
    "F5": 0x40, "7": 0x41, "Y": 0x3A, "H": 0x3B, "N": 0x3C, "F6": 0x48, "8": 0x49, "U": 0x42, "J": 0x43,
    "M": 0x44, "F7": 0x50, "9": 0x51, "I": 0x4A, "K": 0x4B, ",": 0x4C, "F8": 0x58, "0": 0x59, "O": 0x52,
    "L": 0x53, ".": 0x54, "RALT": 0x4D, "F9": 0x60, "-": 0x61, "P": 0x5A, ";": 0x5B, "/": 0x5C, "FN": 0x5D,
    "F10": 0x68, "=": 0x69, "[": 0x62, "'": 0x63, "MENU": 0x65, "F11": 0x70, "BKSP": 0x79, "]": 0x6A,
    "#": 0x6B, "RSHIFT": 0x7C, "F12": 0x78, "ENTER": 0x7B, "ANSI\\": 0x7A, "RCTRL": 0x7D, "PRTSC": 0x80,
    "INS": 0x81, "DEL": 0x82, "LEFT": 0x85, "SCRLK": 0x88, "HOME": 0x89, "END": 0x8A, "UP": 0x8C,
    "DOWN": 0x8D, "PAUSE": 0x90, "PGUP": 0x91, "PGDN": 0x92, "RIGHT": 0x95, "NUM": 0x99, "P7": 0x9A,
    "P4": 0x9B, "P1": 0x9C, "P0": 0x9D, "P/": 0xA1, "P8": 0xA2, "P5": 0xA3, "P2": 0xA4, "P*": 0xA9,
    "P9": 0xAA, "P6": 0xAB, "P3": 0xAC, "P.": 0xAD, "P-": 0xB1, "P+": 0xB2, "PENTER": 0xB4,
}
AZERTY = {"`": "²", "1": "&", "2": "é", "3": '"', "4": "'", "5": "(", "6": "-", "7": "è", "8": "_", "9": "ç",
          "0": "à", "-": ")", "=": "=", "Q": "A", "W": "Z", "[": "^", "]": "$", "A": "Q", ";": "M", "'": "ù",
          "#": "*", "Z": "W", "M": ",", ",": ";", ".": ":", "/": "!"}


class RGBTransport:
    """Accès à l'interface d'éclairage (hidapi, comme l'écran)."""

    def __init__(self, iface: int = IFACE):
        self.iface, self.h = iface, None

    def connect(self) -> str:
        import hid  # type: ignore
        matches = [d for d in hid.enumerate(VID, PID) if d.get("interface_number") == self.iface]
        if not matches:
            raise OSError("ROG Strix Flare II Animate : interface d'éclairage introuvable")
        self.close()
        self.h = hid.device()
        self.h.open_path(matches[0]["path"])
        return repr(matches[0]["path"])

    def write(self, report: bytes) -> int:
        if self.h is None:
            self.connect()
        body = bytes(report)[:REPORT]
        n = self.h.write(b"\x00" + body + bytes(REPORT - len(body)))  # 0x00 : pas de numéro de rapport
        if n < 0:
            raise OSError("écriture HID refusée (éclairage)")
        return n

    def read(self, timeout_ms: int = 20) -> bytes:
        if self.h is None:
            self.connect()
        return bytes(self.h.read(REPORT, max(1, int(timeout_ms))))

    def close(self) -> None:
        if self.h is not None:
            try:
                self.h.close()
            except Exception:
                pass
        self.h = None


class FakeRGBTransport:
    """Clavier factice (ANIMEMATRIX_FAUX_CLAVIER=1)."""

    def __init__(self, *a, **kw):
        self.reports: list[bytes] = []

    def connect(self):
        return "factice"

    def write(self, report):
        self.reports.append(bytes(report)[:REPORT].ljust(REPORT, b"\0"))
        return REPORT + 1

    def read(self, timeout_ms=0):
        return b""

    def close(self):
        pass


def _exchange(t, report: bytes, wait_ms: int = 20) -> bytes:
    """Écrit un rapport et lit la réponse du clavier (les réponses en retard sont vidées avant)."""
    for _ in range(32):
        if not t.read(1):
            break
    t.write(report)
    return t.read(wait_ms)


# ---------- effets du clavier (51 2C) ----------
# nom : (valeur, couleurs par défaut, direction possible) ; valeurs du contrôleur Aura TUF (OpenRGB)
RAINBOW = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (139, 0, 255)]
EFFECTS = {
    "statique": (0, [(255, 0, 0)], False),
    "respiration": (1, [(255, 0, 0)], False),
    "cycle": (2, [], False),
    "reactif": (3, [(255, 0, 0)], False),
    "arc-en-ciel": (4, RAINBOW, True),
    "ondulation": (5, RAINBOW, False),
    "nuit-etoilee": (6, [(255, 255, 255)], False),
    "sable": (7, [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (139, 0, 255)], True),
    "courant": (8, [(0, 127, 255)], False),
    "pluie": (9, [(0, 127, 255)], False),
}
DIRECTIONS = {"gauche": 4, "droite": 0, "haut": 6, "bas": 2, "horizontal": 8, "vertical": 1}


def effect_report(name: str, colors: list[tuple[int, int, int]] | None = None, speed: int = 50,
                  brightness: int = 100, direction: str = "gauche", random: bool = False) -> bytes:
    """Rapport 51 2C : vitesse 0-100 (%), luminosité 0-100 (5 crans), couleurs de l'effet."""
    mode, default, has_direction = EFFECTS[name]
    colors = list(colors or default)
    speed_byte = round(255 - 255 * max(0, min(100, speed)) / 100)  # 255 = lent, 0 = rapide
    level = round(max(0, min(100, brightness)) / 25) * 25
    color_mode = 1 if random else (16 if mode in (1, 3, 6, 8, 9) and len(colors) > 1 and any(colors[1]) else 0)
    body = bytearray([0x51, 0x2C, mode, 0x00, speed_byte, level, color_mode,
                      DIRECTIONS.get(direction, 4) if has_direction else 0, 0x02])
    if mode in (4, 5):  # dégradé : nombre de couleurs, puis (position %, R, G, B)
        body += bytes([len(colors)])
        for i, rgb in enumerate(colors):
            body += bytes([int(100 / len(colors) * (i + 1)), *rgb]) if any(rgb) else bytes(4)
    else:
        for rgb in colors:
            body += bytes(rgb)
    return bytes(body[:REPORT]).ljust(REPORT, b"\0")


def apply_effect(t, name: str, save: bool = True, **kw) -> None:
    """Effet exécuté par le clavier lui-même ; save : gardé après débranchement (50 55)."""
    _exchange(t, effect_report(name, **kw))
    if save:
        _exchange(t, bytes([0x50, 0x55]), 60)


def direct_reports(colors: dict[int, tuple[int, int, int]]) -> list[bytes]:
    """Rapports C0 81 comme Armoury Crate : l'octet 2 compte les entrées qui restent à envoyer."""
    items = sorted(colors.items(), key=lambda kv: (kv[0] % 8, kv[0] // 8))  # rangée par rangée, comme Armoury Crate
    out = []
    for k in range(0, len(items), 15):
        chunk = items[k:k + 15]
        body = bytearray([0xC0, 0x81, len(items) - k, 0x00])
        for index, (r, g, b) in chunk:
            body += bytes([index, r & 255, g & 255, b & 255])
        out.append(bytes(body).ljust(REPORT, b"\0"))
    return out


def send_direct(t, colors: dict[int, tuple[int, int, int]]) -> None:
    for report in direct_reports(colors):
        t.write(report)
    t.read(20)  # accusé C0 82 après une image complète


def firmware(t) -> str:
    """Version du micrologiciel (requête 12 00)."""
    r = _exchange(t, bytes([0x12, 0x00]), 100)
    return f"{r[6]:02X}.{r[5]:02X}.{r[4]:02X}" if len(r) > 6 and r[:2] == b"\x12\x00" else "?"


# ---------- couleurs envoyées par le logiciel (mode direct) ----------

def solid_frame(rgb: tuple[int, int, int], level: float = 1.0) -> dict[int, tuple[int, int, int]]:
    col = tuple(int(v * level) for v in rgb)
    return {i: col for i in LEDS}


def hex_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_hex(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


DEFAULT_CONFIG = {"mode": "clavier", "effet": "arc-en-ciel", "couleurs": [], "vitesse": 50, "luminosite": 100,
                  "direction": "gauche", "aleatoire": False}


def load_config() -> dict:
    """mode : « clavier » (effet exécuté par le clavier), « theme » (couleur du thème),
    « pulsation » (suit la luminosité de l'écran), « off » (rien n'est envoyé)."""
    try:
        return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text(encoding="utf-8"))}
    except (OSError, ValueError):
        pass
    try:  # reprise du réglage OpenRGB
        legacy = json.loads(LEGACY_FILE.read_text(encoding="utf-8")).get("mode")
        if legacy in ("theme", "pulsation"):
            return {**DEFAULT_CONFIG, "mode": legacy}
    except (OSError, ValueError):
        pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")


def effect_kwargs(cfg: dict) -> dict:
    return {"colors": [hex_rgb(c) for c in cfg.get("couleurs") or []] or None, "speed": int(cfg.get("vitesse", 50)),
            "brightness": int(cfg.get("luminosite", 100)), "direction": cfg.get("direction", "gauche"),
            "random": bool(cfg.get("aleatoire"))}


SOFTWARE_MODES = ("theme", "pulsation", "ecran", "audio", "perso", "frappe")  # couleurs envoyées touche par touche
BADGE_KEYS = {"micro": ("F1", (255, 0, 0)), "webcam": ("F2", (255, 120, 0)), "obs": ("F3", (170, 0, 255))}
FLASH_SECONDS = 0.8
FPS = {"theme": 1.0, "perso": 1.0, "pulsation": 15, "ecran": 20, "audio": 25, "frappe": 25, "imitation": 20}
KEY_ROWS = 6  # rangées de touches (la 7e, index 6, est le rétroéclairage)


def preset_config(preset: str) -> dict:
    """Préréglage d'une règle de programmation ou d'un profil (« touches ») -> réglage complet."""
    if preset == "perso":  # dessin touche par touche enregistré dans rgb.json
        return {**DEFAULT_CONFIG, "mode": "perso", "perso": load_config().get("perso", {})}
    if preset in SOFTWARE_MODES:
        return {**DEFAULT_CONFIG, "mode": preset}
    if preset == "eteint":
        return {**DEFAULT_CONFIG, "effet": "statique", "couleurs": ["#000000"], "luminosite": 0}
    if preset.startswith("statique:#"):
        return {**DEFAULT_CONFIG, "effet": "statique", "couleurs": [preset.split(":", 1)[1]]}
    if preset in EFFECTS:
        return {**DEFAULT_CONFIG, "effet": preset}
    raise KeyError(preset)


def screen_frame(leds: bytes, positions, rgb, fraction: float = 1.0) -> dict[int, tuple[int, int, int]]:
    """Les touches reprennent l'image de l'écran, agrandie au clavier (30 × 6 cases, maximum par case)."""
    grid = [[0] * KEY_ROWS for _ in range(COLUMNS)]
    for level, (x, y) in zip(leds, positions):
        c, r = min(COLUMNS - 1, int(x * COLUMNS)), min(KEY_ROWS - 1, int(y * KEY_ROWS))
        grid[c][r] = max(grid[c][r], level)
    out = {}
    for c in range(COLUMNS):
        for r in range(KEY_ROWS):
            k = grid[c][r] / 255 * fraction
            out[c * 8 + r] = tuple(int(v * k) for v in rgb)
        k = max(grid[c]) / 255 * fraction
        out[c * 8 + 6] = tuple(int(v * k) for v in rgb)
    return out


def bars_frame(levels, brightness: float = 1.0) -> dict[int, tuple[int, int, int]]:
    """Spectre : une barre par colonne, du bas vers le haut, teinte arc-en-ciel de gauche à droite."""
    import colorsys
    out = {}
    for c in range(COLUMNS):
        r_, g_, b_ = colorsys.hsv_to_rgb(c / COLUMNS * 0.83, 1.0, brightness)
        rgb = (int(r_ * 255), int(g_ * 255), int(b_ * 255))
        height = float(levels[c]) * KEY_ROWS
        for r in range(KEY_ROWS):
            k = max(0.0, min(1.0, height - (KEY_ROWS - 1 - r)))  # rangée 5 (Ctrl) en bas
            out[c * 8 + r] = tuple(int(v * k) for v in rgb)
        out[c * 8 + 6] = tuple(int(v * min(1.0, float(levels[c]))) for v in rgb)
    return out


class Spectrum:
    """Niveaux par colonne (30 bandes logarithmiques) du son joué, montée immédiate, retombée douce."""

    def __init__(self):
        import numpy as np
        self.np = np
        self.levels = np.zeros(COLUMNS)
        self.peak = 1e-4

    def columns(self):
        np = self.np
        from rog_flare2_effets import AUDIO
        buf, last_t, rate, _mode = AUDIO.get()
        target = np.zeros(COLUMNS)
        if buf is not None and buf.size >= 256 and time.monotonic() - last_t < 1.0:
            spec = np.abs(np.fft.rfft(buf * np.hanning(buf.size)))
            freqs = np.fft.rfftfreq(buf.size, 1 / rate)
            edges = np.geomspace(40, min(16000, rate / 2), COLUMNS + 1)
            idx = np.searchsorted(freqs, edges)
            vals = np.array([spec[a:max(a + 1, b)].max() for a, b in zip(idx[:-1], idx[1:])])
            vals = np.log1p(vals * 20)
            self.peak = max(self.peak * 0.997, float(vals.max()), 1e-4)  # gain automatique
            target = np.clip(vals / self.peak, 0, 1)
        self.levels = np.maximum(target, self.levels * 0.8)
        return self.levels


def keyboard_is_azerty() -> bool:
    """Disposition AZERTY (fr, be) : setxkbmap sous X11, sinon la langue."""
    import subprocess
    try:
        out = subprocess.run(["setxkbmap", "-query"], capture_output=True, text=True, timeout=2).stdout
        for line in out.splitlines():
            if line.startswith("layout:"):
                return line.split(":", 1)[1].strip().split(",")[0] in ("fr", "be")
    except (OSError, subprocess.SubprocessError):
        pass
    return (os.environ.get("LANG") or "").startswith(("fr", "be"))


def key_index(name: str, chars: bool = False, azerty: bool = False) -> int | None:
    """Nom transmis par rog_flare2_touches -> index. chars : caractères de la disposition (pynput, X11),
    sinon positions physiques (evdev) ; AZERTY : le caractère gravé est ramené à sa position."""
    special = {"space": "SPACE", "enter": "ENTER", "backspace": "BKSP", "shift": "LSHIFT", "caps_lock": "CAPS",
               "iso\\": "ISO\\"}
    if name in special:
        return KEYS[special[name]]
    if chars and azerty:
        position = {label.lower(): pos for pos, label in AZERTY.items()}.get(name)
        if position:
            return KEYS.get(position)
    return KEYS.get(name.upper())


def rainbow_frame(t: float, speed: float = 1.0, brightness: float = 1.0) -> dict[int, tuple[int, int, int]]:
    """Vague arc-en-ciel de droite à gauche (imitation de l'effet du clavier)."""
    import colorsys
    out = {}
    for c in range(COLUMNS):
        r, g, b = colorsys.hsv_to_rgb((c / COLUMNS + t * 0.25 * speed) % 1.0, 1.0, brightness)
        rgb = (int(r * 255), int(g * 255), int(b * 255))
        for row in range(ROWS):
            out[c * 8 + row] = rgb
    return out


def imitation_frame(cfg: dict, t: float, accent: str) -> dict[int, tuple[int, int, int]]:
    """Approximation logicielle de l'effet du clavier, le temps d'un voyant ou d'un éclair."""
    import colorsys
    effect = cfg.get("effet", "arc-en-ciel")
    level = int(cfg.get("luminosite", 100)) / 100
    speed = 0.3 + int(cfg.get("vitesse", 50)) / 50
    if effect in ("arc-en-ciel", "ondulation"):
        return rainbow_frame(t, speed, level)
    if effect == "cycle":
        r, g, b = colorsys.hsv_to_rgb((t * 0.08 * speed) % 1.0, 1.0, level)
        return solid_frame((int(r * 255), int(g * 255), int(b * 255)))
    colors = [hex_rgb(c) for c in cfg.get("couleurs") or []] or EFFECTS.get(effect, (0, [], False))[1]
    return solid_frame(colors[0] if colors else hex_rgb(accent), level)


class KeyboardLights:
    """Fil du démon : couleurs des touches selon le réglage (rgb.json), ou le préréglage d'une règle
    de programmation ou d'un profil d'application tant qu'il est actif (override)."""

    def __init__(self, screen_level, accent, screen_leds=None, transport=None):
        self.screen_level = screen_level  # () -> 0..1, luminosité moyenne de l'écran
        self.accent = accent  # () -> "#rrggbb"
        self.screen_leds = screen_leds  # () -> 312 niveaux affichés par l'écran
        fake = os.environ.get("ANIMEMATRIX_FAUX_CLAVIER")
        self.transport = transport or (FakeRGBTransport() if fake else RGBTransport())
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.status = "off"
        self.base: dict = dict(DEFAULT_CONFIG)
        self.overridden: str | None = None
        self.badges: dict[int, tuple[int, int, int]] = {}  # voyants sur les touches (F1-F3)
        self.flash_until, self.flash_color = 0.0, (255, 255, 255)
        self.hits: dict[int, float] = {}  # frappe : touche -> intensité qui s'estompe
        self.wake = threading.Event()  # réveille le fil quand un voyant ou une touche change

    # ---------- voyants, éclair ----------
    def overlay_active(self) -> bool:
        return bool(self.badges) or time.monotonic() < self.flash_until

    def set_badges(self, states: dict):
        """États des voyants (rog_flare2_voyants) -> touches F1 (micro), F2 (webcam), F3 (OBS)."""
        badges = {KEYS[key]: color for name, (key, color) in BADGE_KEYS.items() if states.get(name)}
        if badges != self.badges:
            self.badges = badges
            self._overlay_changed()

    def flash(self, color: str | None = None):
        """Éclair bref de toutes les touches (notification)."""
        self.flash_color = hex_rgb(color or self.accent())
        self.flash_until = time.monotonic() + FLASH_SECONDS
        self._overlay_changed()

    def _overlay_changed(self):
        if self.thread is None and self.overlay_active() and self.current().get("mode", "clavier") == "clavier":
            self._start_thread({**self.current(), "mode": "imitation"})
        self.wake.set()

    def _with_overlay(self, frame: dict) -> dict:
        now = time.monotonic()
        if now < self.flash_until:
            k = (self.flash_until - now) / FLASH_SECONDS  # éclair qui s'éteint
            frame = {i: tuple(int(c * (1 - k) + f * k) for c, f in zip(rgb, self.flash_color))
                     for i, rgb in frame.items()}
        if self.badges:
            frame = {**frame, **self.badges}
        return frame

    def current(self) -> dict:
        return preset_config(self.overridden) if self.overridden else self.base

    def _start_thread(self, cfg: dict):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, args=(cfg, self.stop_event), daemon=True)
        self.thread.start()

    def apply(self, cfg: dict, save: bool = True) -> None:
        """Effet du clavier (enregistré dans le clavier si save)."""
        with self.lock:
            try:
                apply_effect(self.transport, cfg.get("effet", "arc-en-ciel"), save, **effect_kwargs(cfg))
            except OSError:
                self.transport.close()
                raise

    def start(self, cfg: dict):
        """Réglage de base (rgb.json) ; un préréglage actif reste prioritaire."""
        self.base = cfg
        self._activate(reapply=False)

    def override(self, preset: str | None):
        """Préréglage d'une règle ou d'un profil ; None : retour au réglage de base."""
        if preset == self.overridden:
            return
        if preset is not None:
            preset_config(preset)  # préréglage inconnu : KeyError, rien ne change
        self.overridden = preset
        self._activate(reapply=True)

    def _activate(self, reapply: bool):
        cfg = self.current()
        was_direct = self._stop_thread()
        mode = cfg.get("mode", "clavier")
        self.status = mode if not self.overridden else f"{mode} ({self.overridden})"
        if mode in SOFTWARE_MODES:
            self._start_thread(cfg)
        elif mode == "clavier" and self.overlay_active():  # voyant ou éclair en cours : imitation
            self._start_thread({**cfg, "mode": "imitation"})
        elif mode == "clavier" and (reapply or was_direct):  # le clavier reprend (ou prend) son effet
            try:
                self.apply(cfg, save=False)
            except (OSError, KeyError):
                pass

    def _frame(self, mode, accent, spectrum, cfg=None, t=0.0):
        if mode == "imitation":
            return imitation_frame(cfg or {}, t, accent)
        if mode == "frappe":
            rgb = hex_rgb(accent)
            frame = {i: (0, 0, 0) for i in LEDS}
            for idx, level in list(self.hits.items()):
                frame[idx] = tuple(int(v * level) for v in rgb)
                self.hits[idx] = level * 0.88
                if self.hits[idx] < 0.03:
                    self.hits.pop(idx, None)
            return frame
        if mode == "perso":
            colors = {i: (0, 0, 0) for i in LEDS}
            for key, color in (cfg or {}).get("perso", {}).items():
                try:
                    if int(key) in colors:
                        colors[int(key)] = hex_rgb(color)
                except (ValueError, TypeError):
                    pass
            return colors
        rgb = hex_rgb(accent)
        if mode == "pulsation":
            return solid_frame(rgb, 0.15 + 0.85 * self.screen_level())
        if mode == "ecran" and self.screen_leds is not None:
            if not hasattr(self, "_positions"):
                from rog_flare2_simulateur import _positions
                pos = _positions(1.0, 0.0)
                x0, y0 = min(x for x, _y in pos), min(y for _x, y in pos)
                w = (max(x for x, _y in pos) - x0) or 1
                h = (max(y for _x, y in pos) - y0) or 1
                self._positions = [((x - x0) / w, (y - y0) / h) for x, y in pos]
            return screen_frame(self.screen_leds(), self._positions, rgb)
        if mode == "audio":
            return bars_frame(spectrum.columns())
        return solid_frame(rgb)

    def _run(self, cfg, stop):
        mode = cfg["mode"]
        spectrum = Spectrum() if mode == "audio" else None
        listener = self._listen() if mode == "frappe" else None
        try:
            self._loop(mode, stop, spectrum, cfg)
        finally:
            if spectrum is not None:  # parec arrêté (un visualiseur de l'écran le relance s'il en a besoin)
                from rog_flare2_effets import AUDIO
                AUDIO.stop()
            if listener is not None:
                listener.stop()
        if mode == "imitation" and not stop.is_set():  # voyants éteints : le clavier reprend son effet
            with self.lock:
                if self.thread is threading.current_thread():
                    self.thread = None
            try:
                self.apply(cfg, save=False)
                self.status = "clavier" if not self.overridden else f"clavier ({self.overridden})"
            except (OSError, KeyError):
                pass

    def _listen(self):
        """Touches pressées (rog_flare2_touches) -> self.hits ; None sans source de touches."""
        from rog_flare2_touches import EvdevListener, listen
        azerty = keyboard_is_azerty()
        holder = {}

        def press(name):
            idx = key_index(name, chars=not isinstance(holder.get("l"), EvdevListener), azerty=azerty)
            if idx is not None:
                self.hits[idx] = 1.0
                self.wake.set()
        holder["l"] = listen(press)
        if holder["l"] is None:
            self.status = "frappe : touches illisibles (droits sur /dev/input ?)"
        return holder["l"]

    def _loop(self, mode, stop, spectrum, cfg):
        last, accent, accent_at = None, self.accent(), time.monotonic()
        t0 = time.monotonic()
        while not stop.is_set():
            if mode == "imitation" and not self.overlay_active():
                return
            if time.monotonic() - accent_at > 1.0:  # thème relu une fois par seconde
                accent, accent_at = self.accent(), time.monotonic()
            try:
                frame = self._with_overlay(self._frame(mode, accent, spectrum, cfg, time.monotonic() - t0))
                if frame != last or mode in ("theme", "perso"):  # renvoyé chaque seconde (rebranchement)
                    with self.lock:
                        send_direct(self.transport, frame)
                    last = frame
                    self.status = mode if not self.overridden else f"{mode} ({self.overridden})"
            except OSError as exc:
                self.status = f"clavier indisponible : {exc}"
                self.transport.close()
                last = None
                stop.wait(3)
            busy = time.monotonic() < self.flash_until or bool(self.hits)
            self.wake.wait(1 / max(FPS[mode], 20 if busy else 0))  # réveillé par un voyant ou une touche
            self.wake.clear()

    def _stop_thread(self) -> bool:
        was_direct = self.thread is not None
        self.stop_event.set()
        self.wake.set()
        if self.thread is not None:
            self.thread.join(timeout=3)
        self.thread = None
        return was_direct

    def stop(self):
        """Arrêt du démon : le clavier reprend l'effet enregistré s'il recevait des couleurs directes."""
        if self._stop_thread():
            try:
                self.apply(load_config(), save=False)
            except (OSError, KeyError):
                pass
