"""Fenêtre « Ventilateurs » du lanceur : mode automatique, vitesse fixe ou courbe de température par canal."""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from rog_flare2_i18n import _

DEFAULT_CURVE = [[40, 30], [70, 60], [85, 100]]


def mode_labels() -> dict[str, str]:
    return {_("Automatique"): "auto", _("Vitesse fixe"): "fixe", _("Courbe de température"): "courbe"}


def curve_text(points: list) -> str:
    return ", ".join(f"{t}:{v}" for t, v in points)


def parse_curve(text: str) -> list[list[int]]:
    """« 40:30, 70:60 » → [[40, 30], [70, 60]] ; ValueError si mal formé."""
    return [[int(x) for x in pt.strip().split(":")] for pt in text.split(",") if pt.strip()]


class FansWindow:
    def __init__(self, parent, send):
        self.send = send  # (cmd, **kw) -> réponse du démon ; lève une exception s'il refuse
        self.modes = mode_labels()
        self.rows: dict[str, dict] = {}
        self.results: list = []
        self.win = tk.Toplevel(parent)
        self.win.title(_("Ventilateurs"))
        self.win.resizable(False, False)
        self.body = ttk.Frame(self.win, padding=14)
        self.body.pack(fill="both", expand=True)
        ttk.Label(self.body, text=_("Sonde de la courbe : cpu, gpu0, gpu1…, alim. Points : température:pourcentage."),
                  style="Muted.TLabel", wraplength=560).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))
        self.table = ttk.Frame(self.body)
        self.table.grid(row=1, column=0, columnspan=6, sticky="we")
        self.note = ttk.Label(self.body, text="", style="Muted.TLabel", wraplength=560)
        self.note.grid(row=2, column=0, columnspan=6, sticky="w", pady=(8, 0))
        ttk.Button(self.body, text=_("Appliquer"), command=self.apply).grid(row=3, column=5, sticky="e", pady=(8, 0))
        self._request({}, build=True)
        self._poll()

    # ---------- démon (fil séparé ; Tk n'est touché que depuis le fil principal)
    def _request(self, kw: dict, build: bool = False) -> None:
        def job():
            try:
                self.results.append((build, self.send("ventilateurs", timeout=15, **kw), None))
            except Exception as exc:  # démon absent ou réglage refusé
                self.results.append((build, None, str(exc)))
        threading.Thread(target=job, daemon=True).start()

    def _poll(self) -> None:
        if not self.win.winfo_exists():
            return
        while self.results:
            build, resp, error = self.results.pop(0)
            if error:
                self.note.config(text=error)
            elif build:
                self._build(resp)
            else:
                self._refresh(resp["canaux"])
        self.win.after(200, self._poll)
        if not getattr(self, "_ticking", False):
            self._ticking = True
            self.win.after(2000, self._tick)

    def _tick(self) -> None:
        self._ticking = False
        if self.win.winfo_exists():
            self._request({})

    # ---------- tableau
    def _build(self, resp: dict) -> None:
        cfg = resp.get("config", {}).get("canaux", {})
        for col, title in enumerate((_("Nom"), _("Vitesse"), _("Mode"), _("Fixe (%)"), _("Sonde"), _("Courbe"))):
            ttk.Label(self.table, text=title, style="Muted.TLabel").grid(row=0, column=col, sticky="w", padx=4)
        if not resp["canaux"]:
            self.note.config(text=_("Aucun ventilateur pilotable trouvé."))
        for i, ch in enumerate(resp["canaux"], start=1):
            c = cfg.get(ch["id"], {})
            row = {"nom": tk.StringVar(value=ch["nom"]), "vitesse": tk.StringVar(),
                   "mode": tk.StringVar(value=next(k for k, v in self.modes.items() if v == ch["mode"])),
                   "fixe": tk.IntVar(value=int(c.get("valeur", 60))),
                   "source": tk.StringVar(value=c.get("source") or (f"gpu{ch['id'][4:]}" if ch["type"] == "gpu"
                                                                    else "alim" if ch["type"] == "alim" else "cpu")),
                   "courbe": tk.StringVar(value=curve_text(c.get("courbe") or DEFAULT_CURVE)), "label": ch["materiel"]}
            state = "normal" if ch["ecriture"] else "disabled"
            ttk.Entry(self.table, textvariable=row["nom"], width=16).grid(row=i, column=0, padx=4, pady=2)
            ttk.Label(self.table, textvariable=row["vitesse"], width=12).grid(row=i, column=1, padx=4)
            ttk.Combobox(self.table, textvariable=row["mode"], values=list(self.modes), state="readonly" if
                         ch["ecriture"] else "disabled", width=20).grid(row=i, column=2, padx=4)
            ttk.Spinbox(self.table, from_=0, to=100, textvariable=row["fixe"], width=5, state=state).grid(
                row=i, column=3, padx=4)
            ttk.Combobox(self.table, textvariable=row["source"], values=["cpu", "gpu0", "gpu1", "alim"], width=6,
                         state=state).grid(row=i, column=4, padx=4)
            ttk.Entry(self.table, textvariable=row["courbe"], width=22, state=state).grid(row=i, column=5, padx=4)
            self.rows[ch["id"]] = row
        self._refresh(resp["canaux"])

    def _refresh(self, channels: list) -> None:
        locked = []
        for ch in channels:
            row = self.rows.get(ch["id"])
            if not row:
                continue
            speed = _("{n} tr/min").format(n=ch["rpm"]) if ch["rpm"] is not None else (
                f"{ch['pourcent']} %" if ch["pourcent"] is not None else "?")
            row["vitesse"].set(speed + (" ⚠" if ch["erreur"] else ""))
            if not ch["ecriture"]:
                locked.append(ch["nom"])
        errors = [f"{ch['id']} : {ch['erreur']}" for ch in channels if ch["erreur"]]
        text = "\n".join(errors)
        if locked:
            text += ("\n" if text else "") + _("Lecture seule : {names} (règle udev ou sudo manquante, voir le README)."
                                               ).format(names=", ".join(locked))
        self.note.config(text=text)

    def config(self) -> dict:
        canaux = {}
        for cid, row in self.rows.items():
            c = {"mode": self.modes[row["mode"].get()], "valeur": int(row["fixe"].get()),
                 "source": row["source"].get(), "courbe": parse_curve(row["courbe"].get())}
            if row["nom"].get().strip() and row["nom"].get().strip() != row["label"]:
                c["nom"] = row["nom"].get().strip()
            canaux[cid] = c
        return {"canaux": canaux}

    def apply(self) -> None:
        try:
            cfg = self.config()
        except (ValueError, tk.TclError):
            self.note.config(text=_("Courbe mal formée : température:pourcentage, séparés par des virgules."))
            return
        self._request({"config": cfg})
