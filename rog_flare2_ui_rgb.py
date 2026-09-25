"""Fenêtre « Couleurs du clavier » du lanceur : effets exécutés par le clavier, couleur du thème, pulsation."""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import colorchooser, ttk

import rog_flare2_rgb as rgb
from rog_flare2_i18n import _

MAX_COLORS = 7


class RGBWindow:
    def __init__(self, parent, send):
        self.send = send  # (cmd, **kw) -> réponse du démon ou None
        cfg = rgb.load_config()
        self.labels = {
            _("Arc-en-ciel (vague)"): "arc-en-ciel", _("Statique"): "statique", _("Respiration"): "respiration",
            _("Cycle des couleurs"): "cycle", _("Réactif (touche pressée)"): "reactif",
            _("Ondulation"): "ondulation", _("Nuit étoilée"): "nuit-etoilee", _("Sable mouvant"): "sable",
            _("Courant"): "courant", _("Pluie"): "pluie",
            _("Couleur du thème (logiciel)"): "theme", _("Pulsation avec l'écran (logiciel)"): "pulsation"}
        self.directions = {_("Vers la gauche"): "gauche", _("Vers la droite"): "droite", _("Vers le haut"): "haut",
                           _("Vers le bas"): "bas", _("Horizontal"): "horizontal", _("Vertical"): "vertical"}
        self.win = tk.Toplevel(parent)
        self.win.title(_("Couleurs du clavier"))
        self.win.resizable(False, False)
        body = ttk.Frame(self.win, padding=14)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=_("Les effets du clavier tournent sans logiciel et restent après débranchement."),
                  style="Muted.TLabel", wraplength=420).pack(anchor="w", pady=(0, 8))

        key = cfg["mode"] if cfg["mode"] in ("theme", "pulsation") else cfg.get("effet", "arc-en-ciel")
        self.effect = tk.StringVar(value=next((k for k, v in self.labels.items() if v == key), _("Arc-en-ciel (vague)")))
        cb = ttk.Combobox(body, textvariable=self.effect, values=list(self.labels), state="readonly",
                          height=len(self.labels), width=36)
        cb.pack(fill="x")
        cb.bind("<<ComboboxSelected>>", lambda _e: self._effect_changed())

        self.colors_frame = ttk.Frame(body)
        self.colors_frame.pack(fill="x", pady=(10, 0))
        self.colors = [rgb.hex_rgb(c) for c in cfg.get("couleurs") or []]

        self.options = ttk.Frame(body)
        self.options.pack(fill="x", pady=(8, 0))
        self.speed = tk.IntVar(value=int(cfg.get("vitesse", 50)))
        self.level = tk.IntVar(value=int(cfg.get("luminosite", 100)))
        self.direction = tk.StringVar(value=next(k for k, v in self.directions.items()
                                                 if v == cfg.get("direction", "gauche")))
        self.random = tk.BooleanVar(value=bool(cfg.get("aleatoire")))
        ttk.Label(self.options, text=_("Vitesse")).grid(row=0, column=0, sticky="w")
        ttk.Scale(self.options, from_=0, to=100, variable=self.speed, length=260).grid(row=0, column=1, sticky="we")
        ttk.Label(self.options, text=_("Luminosité")).grid(row=1, column=0, sticky="w")
        ttk.Scale(self.options, from_=0, to=100, variable=self.level, length=260,
                  command=lambda v: self.level.set(round(float(v) / 25) * 25)).grid(row=1, column=1, sticky="we")
        self.dir_label = ttk.Label(self.options, text=_("Direction"))
        self.dir_box = ttk.Combobox(self.options, textvariable=self.direction, values=list(self.directions),
                                    state="readonly", width=18)
        self.random_box = ttk.Checkbutton(self.options, text=_("Couleurs aléatoires"), variable=self.random)

        buttons = ttk.Frame(body)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(buttons, text=_("Essayer"), command=lambda: self.apply(False)).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(buttons, text=_("💾 Enregistrer dans le clavier"), command=lambda: self.apply(True)).pack(
            side="left", expand=True, fill="x", padx=(4, 0))
        self.status = ttk.Label(body, text="", style="Muted.TLabel")
        self.status.pack(anchor="w", pady=(6, 0))
        self._effect_changed(keep_colors=True)

    # ---------- couleurs ----------
    def _key(self) -> str:
        return self.labels[self.effect.get()]

    def _effect_changed(self, keep_colors: bool = False):
        key = self._key()
        software = key in ("theme", "pulsation")
        default = [] if software else rgb.EFFECTS[key][1]
        if not keep_colors or not self.colors:
            self.colors = list(default)
        self.max_colors = 0 if software or key == "cycle" else (
            len(default) if key == "sable" else MAX_COLORS if key in ("arc-en-ciel", "ondulation") else
            1 if key == "statique" else 2)
        self.colors = self.colors[:self.max_colors]
        self._draw_colors()
        has_dir = not software and rgb.EFFECTS[key][2]
        for w in (self.dir_label, self.dir_box, self.random_box):
            w.grid_remove()
        if has_dir:
            self.dir_label.grid(row=2, column=0, sticky="w")
            self.dir_box.grid(row=2, column=1, sticky="w", pady=2)
        if not software and key not in ("statique", "cycle", "arc-en-ciel"):
            self.random_box.grid(row=3, column=0, columnspan=2, sticky="w")
        for w in self.options.winfo_children():
            if isinstance(w, ttk.Scale):
                w.state(["disabled" if software else "!disabled"])

    def _draw_colors(self):
        for w in self.colors_frame.winfo_children():
            w.destroy()
        if not self.max_colors:
            return
        ttk.Label(self.colors_frame, text=_("Couleurs :")).pack(side="left")
        for i, c in enumerate(self.colors):
            tk.Button(self.colors_frame, bg=rgb.rgb_hex(c), activebackground=rgb.rgb_hex(c), width=2,
                      relief="flat", command=lambda i=i: self._pick(i)).pack(side="left", padx=2)
        if len(self.colors) < self.max_colors:
            ttk.Button(self.colors_frame, text="+", width=2, command=lambda: self._pick(len(self.colors))).pack(
                side="left", padx=2)
        if len(self.colors) > 1:
            ttk.Button(self.colors_frame, text="−", width=2, command=self._remove).pack(side="left", padx=2)

    def _pick(self, i: int):
        start = rgb.rgb_hex(self.colors[i]) if i < len(self.colors) else "#ffffff"
        chosen = colorchooser.askcolor(color=start, parent=self.win, title=_("Couleurs du clavier"))[1]
        if chosen:
            if i < len(self.colors):
                self.colors[i] = rgb.hex_rgb(chosen)
            else:
                self.colors.append(rgb.hex_rgb(chosen))
            self._draw_colors()

    def _remove(self):
        self.colors.pop()
        self._draw_colors()

    # ---------- envoi ----------
    def config(self) -> dict:
        key = self._key()
        if key in ("theme", "pulsation"):
            return {"mode": key}
        return {"mode": "clavier", "effet": key, "couleurs": [rgb.rgb_hex(c) for c in self.colors],
                "vitesse": int(self.speed.get()), "luminosite": int(self.level.get()),
                "direction": self.directions[self.direction.get()], "aleatoire": bool(self.random.get())}

    def apply(self, save: bool):
        cfg = self.config()
        self.status.configure(text=_("Envoi au clavier…"))

        result = []

        def job():  # Tk n'est touché que depuis le fil principal (sondage ci-dessous)
            try:
                self.send("rgb", timeout=10, config=cfg, save=save)
                result.append(None)
            except Exception as exc:  # démon absent, ancien démon, clavier débranché : le dire tel quel
                result.append(str(exc) or type(exc).__name__)

        def poll():
            if not result:
                self.win.after(100, poll)
                return
            done = _("Enregistré dans le clavier") if save and cfg["mode"] == "clavier" else _("Appliqué")
            self.status.configure(text=done if result[0] is None else
                                  _("Clavier injoignable") + " : " + result[0])
        threading.Thread(target=job, daemon=True).start()
        poll()
