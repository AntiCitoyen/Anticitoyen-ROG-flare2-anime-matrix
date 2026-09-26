"""Fenêtre « Touche par touche » : une couleur par touche, peinte à la souris sur le plan du clavier.

Index d'une touche = colonne × 8 + rangée (rog_flare2_rgb) ; noms et index : disposition ISO du
ROG Strix Flare II Animate (contrôleur Aura TUF d'OpenRGB), ANSI_BACK_SLASH en plus. La rangée 6 est le
rétroéclairage (30 zones sous le clavier).
"""
from __future__ import annotations

import time
import tkinter as tk
from tkinter import colorchooser, ttk

import rog_flare2_rgb as rgb
from rog_flare2_i18n import LANG, _

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
LABELS = {"ESC": "Esc", "LSHIFT": "⇧", "RSHIFT": "⇧", "LCTRL": "Ctrl", "RCTRL": "Ctrl", "LALT": "Alt",
          "RALT": "AltGr", "WIN": "❖", "FN": "Fn", "MENU": "☰", "TAB": "↹", "CAPS": "⇪", "BKSP": "⌫",
          "ENTER": "↵", "PENTER": "↵", "SPACE": "", "LEFT": "←", "RIGHT": "→", "UP": "↑", "DOWN": "↓",
          "PRTSC": "Impr", "SCRLK": "Arrêt", "PAUSE": "Pause", "INS": "Ins", "DEL": "Suppr", "HOME": "⇱",
          "END": "⇲", "PGUP": "⇞", "PGDN": "⇟", "NUM": "Num", "ISO\\": "<", "ANSI\\": "\\"}
AZERTY = {"`": "²", "1": "&", "2": "é", "3": '"', "4": "'", "5": "(", "6": "-", "7": "è", "8": "_", "9": "ç",
          "0": "à", "-": ")", "=": "=", "Q": "A", "W": "Z", "[": "^", "]": "$", "A": "Q", ";": "M", "'": "ù",
          "#": "*", "Z": "W", "M": ",", ",": ";", ".": ":", "/": "!"}
CELL, PAD = 28, 2
PALETTE = ["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#00ffff", "#0000ff", "#8b00ff", "#ff00ff", "#ffffff"]


def label(name: str, azerty: bool) -> str:
    if azerty and name in AZERTY:
        return AZERTY[name]
    if name.startswith("P") and len(name) == 2:
        return name[1]
    return LABELS.get(name, name)


def spans() -> dict[str, tuple[int, int, int]]:
    """Touche -> (colonne, rangée, largeur en colonnes) : une touche s'étend jusqu'à la suivante de sa rangée."""
    by_row: dict[int, list[tuple[int, str]]] = {}
    for name, idx in KEYS.items():
        by_row.setdefault(idx % 8, []).append((idx // 8, name))
    out = {}
    for row, items in by_row.items():
        items.sort()
        for k, (col, name) in enumerate(items):
            nxt = items[k + 1][0] if k + 1 < len(items) else col + 1
            out[name] = (col, row, max(1, min(nxt - col, 4)))
    return out


class KeysWindow:
    def __init__(self, parent, send):
        self.send = send  # (cmd, **kw) -> réponse du démon
        cfg = rgb.load_config()
        self.colors: dict[int, str] = {int(k): v for k, v in cfg.get("perso", {}).items() if str(k).isdigit()}
        self.current = "#ff0000"
        self.azerty = tk.BooleanVar(value=LANG in ("fr", "be"))
        self.win = tk.Toplevel(parent)
        self.win.title(_("Touche par touche"))
        self.win.resizable(False, False)
        body = ttk.Frame(self.win, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=_("Clic : peindre ; glisser : plusieurs touches ; clic droit : éteindre. "
                               "La bande du bas est le rétroéclairage."), style="Muted.TLabel").pack(anchor="w")
        tools = ttk.Frame(body)
        tools.pack(fill="x", pady=6)
        self.swatch = tk.Label(tools, width=3, bg=self.current, relief="sunken")
        self.swatch.pack(side="left")
        for color in PALETTE:
            tk.Button(tools, bg=color, activebackground=color, width=2, relief="flat",
                      command=lambda c=color: self._set_color(c)).pack(side="left", padx=1)
        ttk.Button(tools, text=_("Couleur…"), command=self._choose).pack(side="left", padx=6)
        ttk.Checkbutton(tools, text="AZERTY", variable=self.azerty, command=self._draw).pack(side="left", padx=6)
        ttk.Button(tools, text=_("Tout remplir"), command=lambda: self._fill(self.current)).pack(side="right")
        ttk.Button(tools, text=_("Tout éteindre"), command=lambda: self._fill(None)).pack(side="right", padx=4)
        self.spans = spans()
        width = (rgb.COLUMNS * CELL) + 2 * PAD
        self.canvas = tk.Canvas(body, width=width, height=7 * CELL + 10 + 2 * PAD, bg="#101014",
                                highlightthickness=0)
        self.canvas.pack()
        for seq, color in (("<Button-1>", "cur"), ("<B1-Motion>", "cur"), ("<Button-3>", None),
                           ("<B3-Motion>", None)):
            self.canvas.bind(seq, lambda e, c=color: self._paint(e, self.current if c else None))
        self.status = ttk.Label(body, text="", style="Muted.TLabel")
        self.status.pack(anchor="w", pady=(6, 0))
        self._pending = None
        self._draw()  # rien n'est envoyé avant le premier coup de pinceau

    # ---------- dessin ----------
    def _cell(self, col, row, w=1):
        x0 = PAD + col * CELL
        y0 = PAD + row * CELL + (10 if row == 6 else 0)
        return x0 + 1, y0 + 1, x0 + w * CELL - 1, y0 + (CELL // 2 if row == 6 else CELL) - 1

    def _draw(self):
        c = self.canvas
        c.delete("all")
        self.hit: list[tuple[tuple[int, int, int, int], int]] = []
        for name, (col, row, w) in self.spans.items():
            if name == "ANSI\\" and self.azerty.get():
                continue  # touche des claviers américains, absente d'un AZERTY (ISO)
            idx = KEYS[name]
            box = self._cell(col, row, w)
            fill = self.colors.get(idx, "#000000")
            c.create_rectangle(*box, fill=fill, outline="#3a3d46")
            lum = sum(rgb.hex_rgb(fill)) / 3
            c.create_text((box[0] + box[2]) / 2, (box[1] + box[3]) / 2, text=label(name, self.azerty.get()),
                          fill="#111111" if lum > 140 else "#d8dbe2", font=("TkDefaultFont", 8))
            self.hit.append((box, idx))
        for col in range(rgb.COLUMNS):  # rétroéclairage
            idx = col * 8 + 6
            box = self._cell(col, 6)
            c.create_rectangle(*box, fill=self.colors.get(idx, "#000000"), outline="#3a3d46")
            self.hit.append((box, idx))

    # ---------- édition ----------
    def _set_color(self, color: str):
        self.current = color
        self.swatch.configure(bg=color)

    def _choose(self):
        chosen = colorchooser.askcolor(color=self.current, parent=self.win, title=_("Touche par touche"))[1]
        if chosen:
            self._set_color(chosen)

    def _paint(self, event, color):
        for (x0, y0, x1, y1), idx in self.hit:
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                if color is None:
                    self.colors.pop(idx, None)
                elif self.colors.get(idx) == color:
                    return
                else:
                    self.colors[idx] = color
                self._draw()
                self._schedule()
                return

    def _fill(self, color):
        self.colors = {i: color for i in rgb.LEDS} if color else {}
        self._draw()
        self._schedule()

    # ---------- envoi (au plus toutes les 150 ms pendant qu'on peint) ----------
    def _schedule(self):
        if self._pending is None:
            self._pending = self.win.after(150, self._send_now)

    def _send_now(self):
        self._pending = None
        perso = {str(k): v for k, v in sorted(self.colors.items())}
        try:
            self.send("rgb", timeout=5, config={"mode": "perso", "perso": perso}, save=False)
            self.status.configure(text=_("Appliqué") + time.strftime(" (%H:%M:%S)"))
        except Exception as exc:
            self.status.configure(text=_("Clavier injoignable") + " : " + str(exc))
