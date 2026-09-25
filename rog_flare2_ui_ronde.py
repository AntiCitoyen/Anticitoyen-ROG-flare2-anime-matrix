"""Interfaces rondes du lanceur AniMe Matrix.

- "drawer"  : cadran rond + tiroir arrondi à droite pour les réglages (défaut) ;
- "dial"    : cadran rond seul, les réglages s'ouvrent en surimpression dans le cercle ;
- "rounded" : fenêtre aux coins très arrondis, aperçu rond, molette de luminosité.

Les commandes (GIF, Effets, Audio, Réglages) sont les blocs ttk du lanceur
(LauncherApp.build_sections) ; ce module ne fait que la mise en page, le dessin
(Pillow, suréchantillonné pour des bords lisses) et la forme de la fenêtre
(extension X11 SHAPE + _MOTIF_WM_HINTS via python-xlib ; sans elle, la fenêtre
reste rectangulaire avec le dessin rond à l'intérieur).
"""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from PIL import Image, ImageDraw, ImageTk

import rog_flare2_themes as themes
from rog_flare2_core import VERSION
from rog_flare2_effets import pww  # noqa: F401  (met polywollywin/ dans sys.path)
from rog_flare2_i18n import _
from rog_flare2_matrix_paint import FB_OFFSET
from renderer import PHYSICAL_INDICES  # (rangée, colonne) logiques 12 x 37 de chaque LED matérielle

SS = 3  # suréchantillonnage du dessin
PREVIEW_MS = 80


def rgb(color: str) -> tuple[int, int, int]:
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))


def mix(a: str, b: str, t: float) -> tuple[int, int, int]:
    ra, rb = rgb(a), rgb(b)
    return tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))


def render(w: int, h: int, draw) -> ImageTk.PhotoImage:
    """draw(ImageDraw, s) dessine à l'échelle s ; rendu réduit avec lissage."""
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    draw(ImageDraw.Draw(img), SS)
    return ImageTk.PhotoImage(img.resize((w, h), Image.LANCZOS))


class Shaper:
    """Forme de la fenêtre (XShape) et retrait des décorations (_MOTIF_WM_HINTS)."""

    def __init__(self, root: tk.Tk):
        self.ok = False
        try:
            from Xlib import display
            from Xlib.ext import shape
            self.shape = shape
            self.d = display.Display()
            if not self.d.has_extension("SHAPE"):
                return
            root.update_idletasks()
            inner = self.d.create_resource_object("window", root.winfo_id())
            self.win = inner.query_tree().parent  # enveloppe Tk = fenêtre gérée par le gestionnaire
            self.ok = True
        except Exception:
            self.ok = False

    def undecorate(self):
        if not self.ok:
            return
        atom = self.d.intern_atom("_MOTIF_WM_HINTS")
        self.win.change_property(atom, atom, 32, [2, 0, 0, 0, 0])
        self.d.flush()

    def set(self, w: int, h: int, parts: list[tuple]):
        """parts : ("ellipse" | "rect", x, y, largeur, hauteur) ; l'union forme la fenêtre."""
        if not self.ok:
            return
        pm = self.win.create_pixmap(w, h, 1)
        gc = pm.create_gc(foreground=0, background=0)
        pm.fill_rectangle(gc, 0, 0, w, h)
        gc.change(foreground=1)
        for kind, x, y, pw, ph in parts:
            if kind == "ellipse":
                pm.fill_arc(gc, int(x), int(y), int(pw), int(ph), 0, 360 * 64)
            else:
                pm.fill_rectangle(gc, int(x), int(y), int(pw), int(ph))
        self.win.shape_mask(self.shape.SO.Set, self.shape.SK.Bounding, 0, 0, pm)
        gc.free()
        pm.free()
        self.d.flush()


def fit_size(text: str, width: float, size: int, smallest: int = 5) -> int:
    """Plus grande taille de police (≤ size) pour que text tienne dans width pixels (libellés traduits)."""
    while size > smallest and tkfont.Font(family="Sans", size=size).measure(text) > width:
        size -= 1
    return size


def rounded_parts(x, y, w, h, r) -> list[tuple]:
    return [("rect", x + r, y, w - 2 * r, h), ("rect", x, y + r, w, h - 2 * r),
            ("ellipse", x, y, 2 * r, 2 * r), ("ellipse", x + w - 2 * r, y, 2 * r, 2 * r),
            ("ellipse", x, y + h - 2 * r, 2 * r, 2 * r), ("ellipse", x + w - 2 * r, y + h - 2 * r, 2 * r, 2 * r)]


class RoundButton:
    """Bouton rond dessiné sur le canevas : icône + libellé, survol, état actif."""

    def __init__(self, ui: "RoundUI", cx, cy, r, icon, label, command, label_inside=True):
        self.ui, self.cx, self.cy, self.r, self.command = ui, cx, cy, r, command
        self.active = False
        self.hover = False
        ui.all_buttons.append(self)
        c = ui.canvas
        self.tag = f"btn{id(self)}"
        self.img_id = c.create_image(cx, cy, tags=(self.tag,))
        dy = -r * 0.2 if label and label_inside else 0
        self.icon_id = c.create_text(cx, cy + dy, text=icon, font=("Sans", max(9, int(r * 0.5))), tags=(self.tag,))
        ly = cy + r * 0.45 if label_inside else cy + r + 12
        self.label_id = c.create_text(cx, ly, text=label, font=("Sans", fit_size(label, 1.4 * r, max(7, int(r * 0.22)))),
                                      tags=(self.tag,))
        c.tag_bind(self.tag, "<Enter>", lambda _e: self._set(hover=True))
        c.tag_bind(self.tag, "<Leave>", lambda _e: self._set(hover=False))
        c.tag_bind(self.tag, "<Button-1>", lambda _e: self.command())
        self.redraw()

    def _set(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        self.redraw()

    def set_active(self, active: bool):
        self._set(active=active)

    def redraw(self):
        p = self.ui.p
        fill = p["accent"] if self.active else (p["trough"] if self.hover else p["surface"])
        d = 2 * self.r + 4

        def draw(g, s):
            g.ellipse([2 * s, 2 * s, (d - 2) * s, (d - 2) * s], fill=fill, outline=p["accent"], width=2 * s)
        self.img = render(d, d, draw)
        c = self.ui.canvas
        c.itemconfigure(self.img_id, image=self.img)
        text = p["accent_fg"] if self.active else p["fg"]
        c.itemconfigure(self.icon_id, fill=text)
        c.itemconfigure(self.label_id, fill=p["accent_fg"] if self.active else p["muted"])


class ArcSlider:
    """Curseur en arc lié à un IntVar : angle(v) = start + sweep * v (degrés, sens horaire depuis 3 h)."""

    def __init__(self, ui: "RoundUI", cx, cy, r, width, start, sweep, var: tk.IntVar, lo=5, hi=100, label=None):
        self.ui, self.cx, self.cy, self.r, self.width = ui, cx, cy, r, width
        self.start, self.sweep, self.var, self.lo, self.hi = start, sweep, var, lo, hi
        c = ui.canvas
        # Image carrée qui couvre les boutons : insensible aux clics (state="disabled") ;
        # seul un clic sur l'anneau lui-même règle la valeur (on_arc).
        self.img_id = c.create_image(cx, cy, state="disabled")
        self.label_id = c.create_text(*label, font=("Sans", 9), state="disabled") if label else None
        self.dragging = False
        c.bind("<ButtonPress-1>", self._press, add="+")
        c.bind("<B1-Motion>", lambda e: self.dragging and self._drag(e), add="+")
        c.bind("<ButtonRelease-1>", lambda _e: setattr(self, "dragging", False), add="+")
        var.trace_add("write", lambda *_a: self.redraw())
        self.redraw()

    def on_arc(self, x, y) -> bool:
        """(x, y) sur l'anneau, à la largeur du bouton près, dans l'étendue de l'arc."""
        dist = math.hypot(x - self.cx, y - self.cy)
        if abs(dist - self.r) > self.width * 1.8:
            return False
        ang = math.degrees(math.atan2(y - self.cy, x - self.cx)) % 360
        rel = ((ang - self.start) if self.sweep > 0 else (self.start - ang)) % 360
        return rel <= abs(self.sweep) + 6 or rel >= 354

    def _press(self, e):
        self.dragging = self.on_arc(e.x, e.y)
        if self.dragging:
            self._drag(e)

    def _value(self) -> float:
        return (self.var.get() - self.lo) / (self.hi - self.lo)

    def _drag(self, e):
        ang = math.degrees(math.atan2(e.y - self.cy, e.x - self.cx)) % 360
        span = abs(self.sweep)
        rel = ((ang - self.start) if self.sweep > 0 else (self.start - ang)) % 360
        if rel > span:  # hors de l'arc : borne la plus proche
            rel = span if rel - span < (360 - span) / 2 else 0
        self.var.set(round(self.lo + (self.hi - self.lo) * rel / span))

    def redraw(self):
        p = self.ui.p
        size = 2 * (self.r + self.width) + 4
        o = size / 2
        v = self._value()
        a_knob = self.start + self.sweep * v
        lo_ang, hi_ang = sorted((self.start, self.start + self.sweep))
        fill_a, fill_b = sorted((self.start, a_knob))

        def draw(g, s):
            box = [(o - self.r) * s, (o - self.r) * s, (o + self.r) * s, (o + self.r) * s]
            g.arc(box, lo_ang, hi_ang, fill=p["trough"], width=self.width * s)
            if fill_b > fill_a:
                g.arc(box, fill_a, fill_b, fill=p["accent"], width=self.width * s)
            a = math.radians(a_knob)
            kx, ky = (o + self.r * math.cos(a)) * s, (o + self.r * math.sin(a)) * s
            k = self.width * 0.95 * s
            g.ellipse([kx - k, ky - k, kx + k, ky + k], fill="#ffffff", outline=p["accent"], width=2 * s)
        self.img = render(int(size), int(size), draw)
        c = self.ui.canvas
        c.itemconfigure(self.img_id, image=self.img)
        if self.label_id:
            c.itemconfigure(self.label_id, fill=p["muted"],
                            text=_("Luminosité :").rstrip(" :：") + f" {self.var.get()} %")


class Preview:
    """Aperçu en direct des 312 LED (dernière trame envoyée au clavier)."""

    def __init__(self, ui: "RoundUI", cx, cy, w, h):
        self.ui, self.w, self.h = ui, int(w), int(h)
        self.img_id = ui.canvas.create_image(cx, cy)
        self.last = None
        self.redraw(force=True)
        ui.app.after(PREVIEW_MS, self._tick)

    def _tick(self):
        self.redraw()
        self.ui.app.after(PREVIEW_MS, self._tick)

    def redraw(self, force=False):
        frame = self.ui.app.last_frame
        if frame == self.last and not force:
            return
        self.last = frame
        p = self.ui.p
        vals = frame[FB_OFFSET:FB_OFFSET + len(PHYSICAL_INDICES)] if frame else bytes(len(PHYSICAL_INDICES))
        cw, ch = self.w / 37, self.h / 12
        s = 2
        img = Image.new("RGBA", (self.w * s, self.h * s), (0, 0, 0, 0))
        g = ImageDraw.Draw(img)
        rad = min(cw, ch) * 0.38 * s
        for (r, c), v in zip(PHYSICAL_INDICES, vals):
            x, y = (c + 0.5) * cw * s, (r + 0.5) * ch * s
            g.ellipse([x - rad, y - rad, x + rad, y + rad], fill=mix(p["trough"], p["accent"], v / 255))
        self.img = ImageTk.PhotoImage(img.resize((self.w, self.h), Image.LANCZOS))
        self.ui.canvas.itemconfigure(self.img_id, image=self.img)


class RoundUI:
    SECTIONS = [("GIF", "▶", 0), ("Effets", "✦", 1), ("Audio", "♫", 2), ("Réglages", "⚙", 3)]

    def __init__(self, app, mode: str):
        self.app, self.mode = app, mode
        self.p = themes.palette()
        self.open_section: int | None = None
        self._drag_origin: tuple[int, int] | None = None
        self.buttons: dict[int, RoundButton] = {}
        self.all_buttons: list[RoundButton] = []
        app.resizable(False, False)
        self.canvas = tk.Canvas(app, highlightthickness=0, bd=0, bg=self.p["bg"])
        self.canvas.pack()
        style = ttk.Style(app)
        style.configure("Round.TLabel", background=self.p["bg"], foreground=self.p["muted"])
        if mode == "rounded":
            self._build_rounded()
        else:
            self._build_dial(drawer=(mode == "drawer"))
        self.shaper = Shaper(app)
        self.shaper.undecorate()
        self._apply_shape()
        app.after(50, self._center)
        # déplacement de la fenêtre en tirant le fond
        self.canvas.tag_bind("drag", "<ButtonPress-1>", self._drag_start)
        self.canvas.tag_bind("drag", "<B1-Motion>", self._drag_move)

    # ---------- construction ----------
    def _sections(self, wrap: int):
        """Crée les quatre blocs de commandes, cachés, dans le canevas."""
        frames = self.app.build_sections(self.canvas, padding=6, wrap=wrap)
        self.frames = [f for f, _t in frames]
        self.section_titles = [t for _f, t in frames]

    def _controls(self, x, y):
        """Boutons ronds Réduire / Fermer."""
        RoundButton(self, x - 14, y, 10, "–", "", self.app.iconify)
        RoundButton(self, x + 14, y, 10, "✕", "", self.app.on_close)

    def _build_dial(self, drawer: bool):
        self.DW = 400 if drawer else 0  # largeur du tiroir au-delà du cercle
        # Blocs de commandes créés d'abord : leur hauteur fixe la taille du tiroir ou du cadran.
        self._sections(wrap=self.DW - 48 if drawer else int(660 * 0.66) - 30)
        self.app.update_idletasks()
        need = max(f.winfo_reqheight() for f in self.frames)
        if drawer:
            box_h = max(540 * 0.74, need + 36)
            D = int(max(540, box_h + 24))
        else:
            D = int(max(660, (need + 20) / 0.6))
        self.D = D
        W = D + self.DW
        c = self.canvas
        c.configure(width=W, height=D)
        self.cx = self.cy = D / 2
        self.drawer_box = (D - 150, (D - box_h) / 2, W - 4, (D + box_h) / 2) if drawer else None
        self.drawer_id = c.create_image(0, 0, anchor="nw", tags=("drag",)) if drawer else None
        self.dial_id = c.create_image(0, 0, anchor="nw", tags=("drag",))
        self.title_id = c.create_text(self.cx, D * 0.16, text="AniMe Matrix", font=("Sans", 16, "bold"), tags=("drag",))
        self.sub_id = c.create_text(self.cx, D * 0.21, text=f"ROG Strix Flare II Animate · v{VERSION}", font=("Sans", 8),
                                    tags=("drag",))
        self.panel_id = c.create_image(self.cx, D * 0.36, tags=("drag",))
        self.preview = Preview(self, self.cx, D * 0.36, D * 0.4, D * 0.13)
        self.app.status = ttk.Label(c, text="", style="Round.TLabel")
        c.create_window(self.cx, D * 0.49, window=self.app.status)
        # rangée de boutons en sourire
        r = 27 if drawer else 30
        items = [(t, ic, i) for t, ic, i in self.SECTIONS[:3]] + [("Horloge", "◷", "clock"),
                                                                  ("Réglages", "⚙", 3), ("Arrêter", "■", "stop")]
        for k, (title, icon, action) in enumerate(items):
            t = k - 2.5
            x = self.cx + t * (r * 2.35)
            y = D * 0.63 + (t * t) * 3.2
            label = {"GIF": _("GIF / images").split("/")[0].strip(), "Effets": _("Effets"), "Audio": _("Audio"),
                     "Réglages": _("Réglages"), "Horloge": _("Horloge"),
                     "Arrêter": _("■ Arrêter").lstrip("■ ")}[title]
            cmd = (self.app.start_clock if action == "clock" else self.app.stop_and_clear if action == "stop"
                   else (lambda i=action: self.toggle_section(i)))
            b = RoundButton(self, x, y, r, icon, label, cmd)
            if isinstance(action, int):
                self.buttons[action] = b
        self.arc = ArcSlider(self, self.cx, self.cy, D / 2 - 34, 9, 145, -110, self.app.brightness,
                             label=(self.cx, D - 62))
        self._controls(self.cx, 30)
        # blocs de commandes : dans le tiroir (B) ou en surimpression (A)
        if drawer:
            x0 = D + 6
            self.content_box = (x0, self.drawer_box[1] + 18, W - 22 - x0)
        else:
            w = D * 0.66  # bloc inscrit dans le disque intérieur
            self.overlay_id = c.create_image(self.cx, self.cy, state="hidden", tags=("drag",))
            self.content_box = (self.cx - w / 2, D * 0.18, w)
            self.close_overlay = RoundButton(self, self.cx, D * 0.135, 13, "✕", "",
                                             lambda: self.toggle_section(None))
            for item in (self.close_overlay.img_id, self.close_overlay.icon_id, self.close_overlay.label_id):
                c.itemconfigure(item, state="hidden")
        x, y, w = self.content_box
        self.window_ids = [c.create_window(x, y, window=f, anchor="nw", width=w, state="hidden") for f in self.frames]
        self.render_static()
        self.toggle_section(0 if drawer else None)

    def _build_rounded(self):
        c = self.canvas
        W = 440
        self._sections(wrap=W - 80)
        self.app.update_idletasks()
        content_h = max(f.winfo_reqheight() for f in self.frames)
        top_content = 336
        H = top_content + content_h + 16 + 150
        self.W, self.H = W, H
        c.configure(width=W, height=H)
        self.bg_id = c.create_image(0, 0, anchor="nw", tags=("drag",))
        self.title_id = c.create_text(28, 32, text="AniMe Matrix", anchor="w", font=("Sans", 14, "bold"), tags=("drag",))
        self.sub_id = None
        self._controls(W - 48, 32)
        self.cx, self.circle_cy, self.circle_r = W / 2, 150, 92
        self.circle_id = c.create_image(self.cx, self.circle_cy, tags=("drag",))
        self.preview = Preview(self, self.cx, self.circle_cy, 150, 58)
        self.app.status = ttk.Label(c, text="", style="Round.TLabel")
        c.create_window(self.cx, 262, window=self.app.status)
        # onglets en pilules
        self.pills = []
        pw = (W - 56 - 3 * 8) / 4
        for i, title in enumerate(self.section_titles):
            x = 28 + i * (pw + 8)
            img_id = c.create_image(x, 284, anchor="nw")
            txt = c.create_text(x + pw / 2, 300, text=title, font=("Sans", fit_size(title, pw - 14, 9)))
            for item in (img_id, txt):
                c.tag_bind(item, "<Button-1>", lambda _e, i=i: self.toggle_section(i, keep_open=True))
            self.pills.append((img_id, txt, pw))
        self.content_box = (28, top_content, W - 56)
        x, y, w = self.content_box
        self.window_ids = [c.create_window(x, y, window=f, anchor="nw", width=w, state="hidden") for f in self.frames]
        by = H - 82
        self.arc = ArcSlider(self, 104, by, 52, 9, 135, 270, self.app.brightness)
        self.knob_text = c.create_text(104, by - 4, font=("Sans", 13, "bold"))
        self.knob_sub = c.create_text(104, by + 18, text=_("Luminosité :").rstrip(" :："), font=("Sans", 7))
        self.app.brightness.trace_add("write", lambda *_a: self._knob_text())
        RoundButton(self, 262, by, 40, "◷", _("Horloge"), self.app.start_clock)
        RoundButton(self, 360, by, 40, "■", _("■ Arrêter").lstrip("■ "), self.app.stop_and_clear)
        self.render_static()
        self.toggle_section(1, keep_open=True)

    # ---------- dessin ----------
    def render_static(self):
        p, c = self.p, self.canvas
        c.configure(bg=p["bg"])
        for item in (self.title_id, self.sub_id):
            if item:
                c.itemconfigure(item, fill=p["fg"] if item == self.title_id else p["muted"])
        if self.mode == "rounded":
            W, H = self.W, self.H
            self.bg_img = render(W, H, lambda g, s: g.rounded_rectangle(
                [2 * s, 2 * s, (W - 2) * s, (H - 2) * s], 36 * s, fill=p["bg"], outline=p["accent"], width=3 * s))
            c.itemconfigure(self.bg_id, image=self.bg_img)
            d = 2 * self.circle_r + 6
            self.circle_img = render(d, d, lambda g, s: g.ellipse(
                [3 * s, 3 * s, (d - 3) * s, (d - 3) * s], fill="#0a0b0d" if _dark(p) else p["surface"], outline=p["accent"], width=3 * s))
            c.itemconfigure(self.circle_id, image=self.circle_img)
            self._knob_text()
            c.itemconfigure(self.knob_sub, fill=p["muted"])
            self._draw_pills()
            return
        D = self.D
        self.dial_img = render(D, D, lambda g, s: (
            g.ellipse([3 * s, 3 * s, (D - 3) * s, (D - 3) * s], fill=p["bg"], outline=p["accent"], width=4 * s),
            g.ellipse([16 * s, 16 * s, (D - 16) * s, (D - 16) * s], outline=p["trough"], width=1 * s)))
        c.itemconfigure(self.dial_id, image=self.dial_img)
        pw, ph = int(D * 0.44), int(D * 0.17)
        self.panel_img = render(pw, ph, lambda g, s: g.rounded_rectangle(
            [1 * s, 1 * s, (pw - 1) * s, (ph - 1) * s], 14 * s, fill="#0a0b0d" if _dark(p) else p["surface"],
            outline=p["trough"], width=1 * s))
        c.itemconfigure(self.panel_id, image=self.panel_img)
        if self.drawer_id is not None:
            x0, y0, x1, y1 = self.drawer_box
            w, h = int(x1 - x0), int(y1 - y0)
            self.drawer_img = render(w, h, lambda g, s: g.rounded_rectangle(
                [2 * s, 2 * s, (w - 2) * s, (h - 2) * s], 28 * s, fill=p["bg"], outline=p["accent"], width=2 * s))
            c.itemconfigure(self.drawer_id, image=self.drawer_img)
            c.coords(self.drawer_id, x0, y0)
        else:
            d = int(D - 2 * 52)  # disque qui laisse visibles l'arc de luminosité et les boutons du haut
            self.overlay_img = render(d, d, lambda g, s: g.ellipse(
                [2 * s, 2 * s, (d - 2) * s, (d - 2) * s], fill=p["bg"], outline=p["accent"], width=2 * s))
            c.itemconfigure(self.overlay_id, image=self.overlay_img)

    def _knob_text(self):
        self.canvas.itemconfigure(self.knob_text, text=f"{self.app.brightness.get()} %", fill=self.p["fg"])

    def _draw_pills(self):
        p, c = self.p, self.canvas
        self.pill_imgs = []
        for i, (img_id, txt, pw) in enumerate(self.pills):
            on = i == self.open_section
            img = render(int(pw), 32, lambda g, s, on=on: g.rounded_rectangle(
                [1 * s, 1 * s, (pw - 1) * s, 31 * s], 16 * s, fill=p["accent"] if on else p["surface"]))
            self.pill_imgs.append(img)
            c.itemconfigure(img_id, image=img)
            c.itemconfigure(txt, fill=p["accent_fg"] if on else p["muted"])

    def retheme(self):
        self.p = themes.palette()
        ttk.Style(self.app).configure("Round.TLabel", background=self.p["bg"], foreground=self.p["muted"])
        self.render_static()
        for b in self.all_buttons:
            b.redraw()
        self.arc.redraw()
        self.preview.redraw(force=True)

    # ---------- sections ----------
    def toggle_section(self, index: int | None, keep_open: bool = False):
        if index == self.open_section and not keep_open:
            index = None
        self.open_section = index
        c = self.canvas
        for i, wid in enumerate(self.window_ids):
            c.itemconfigure(wid, state="normal" if i == index else "hidden")
        for i, b in self.buttons.items():
            b.set_active(i == index)
        if self.mode == "rounded":
            self._draw_pills()
        elif self.mode == "dial":
            state = "normal" if index is not None else "hidden"
            c.itemconfigure(self.overlay_id, state=state)
            for item in (self.close_overlay.img_id, self.close_overlay.icon_id, self.close_overlay.label_id):
                c.itemconfigure(item, state=state)
            c.tag_raise(self.overlay_id)
            c.tag_raise(self.close_overlay.tag)
        else:
            c.itemconfigure(self.drawer_id, state="normal" if index is not None else "hidden")
        self._apply_shape()

    def shape_parts(self) -> tuple[int, int, list[tuple]]:
        """Largeur, hauteur et formes (union) de la fenêtre dans son état actuel."""
        if self.mode == "rounded":
            return self.W, self.H, rounded_parts(0, 0, self.W, self.H, 36)
        D = self.D
        parts = [("ellipse", 0, 0, D, D)]
        if self.mode == "drawer" and self.open_section is not None:
            x0, y0, x1, y1 = self.drawer_box
            parts += rounded_parts(x0, y0, x1 - x0, y1 - y0, 28)
        return D + self.DW, D, parts

    def _apply_shape(self):
        if hasattr(self, "shaper"):
            self.shaper.set(*self.shape_parts())

    # ---------- fenêtre ----------
    def _center(self):
        a = self.app
        a.update_idletasks()
        x = (a.winfo_screenwidth() - a.winfo_width()) // 2
        y = (a.winfo_screenheight() - a.winfo_height()) // 2
        a.geometry(f"+{x}+{y}")

    def _drag_start(self, e):
        # un clic sur l'arc de luminosité règle la valeur, il ne déplace pas la fenêtre
        self._drag_origin = None if self.arc.on_arc(e.x, e.y) else (
            e.x_root - self.app.winfo_x(), e.y_root - self.app.winfo_y())

    def _drag_move(self, e):
        if self._drag_origin is None:
            return
        dx, dy = self._drag_origin
        self.app.geometry(f"+{e.x_root - dx}+{e.y_root - dy}")


def _dark(p: dict) -> bool:
    return sum(rgb(p["bg"])) < 3 * 128
