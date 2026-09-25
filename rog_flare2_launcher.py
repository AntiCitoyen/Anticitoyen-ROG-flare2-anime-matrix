#!/usr/bin/env python3
"""
Lanceur AniMe Matrix : GIF/images ou galerie d'un dossier, horloge, effets et
visualiseurs audio de PolyWollyWin (rog_flare2_effets.py), conversion, mode du
démarrage de session et éditeur de dessin pour l'écran du clavier
ROG Strix Flare II Animate. Les services de fond (galerie, horloge) sont
suspendus pendant que le lanceur écrit sur le clavier et repris à la fermeture.

Réutilise le transport et le mapping physique 312 LEDs de
rog_flare2_matrix_paint.py. Ajoute la lecture GIF/image absente en amont
(cf. docs/PROTOCOL.md : "Import GIF/image files directly in the Linux tool" non
implémenté).
"""
from __future__ import annotations

import base64
import os
import subprocess
import webbrowser
import sys
import threading
import time
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_convertir import convertir_tout
from rog_flare2_i18n import LANG, LANGUAGES, _, save_language
import rog_flare2_ctl as ctl
import rog_flare2_maj as maj
import rog_flare2_notifs as notifs
import rog_flare2_openrgb as openrgb
import rog_flare2_tray as tray
from rog_flare2_demon import START_FILE
from rog_flare2_matrix_paint import FB_OFFSET
import rog_flare2_themes as themes
from rog_flare2_core import (  # noqa: F401  (réexportés pour les autres modules)
    VERSION, CONFIG_DIR, GALLERY_FILE, MEDIA_EXTENSIONS, STILL_SECONDS, Image, gallery_dir, image_to_frame,
    iter_gif_frames, media_files, pick_version, play_clock, play_file, save_gallery_dir,
)
from rog_flare2_effets import AUDIO_EFFECTS, EFFECTS, PLUGIN_DIR, effect_class, effect_label
from rog_flare2_jeux import GAMES

GAME_NAMES = {g.name for g in GAMES}


PROJECT_URL = "https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix"
SUPPORT_URL = "https://buymeacoffee.com/anticitoyen"
# Mode rejoué par le démon à l'ouverture de session (rog_flare2_demon.START_FILE)
BOOT_MODES = {"Galerie GIF": "gif", "Horloge": "horloge", "Dernière lecture": "derniere", "Rien": "rien"}
INTERFACE_FILE = CONFIG_DIR / "interface"
# Interfaces : cadran + tiroir (défaut), cadran seul, fenêtre arrondie, onglets classiques
INTERFACES = {"drawer": "Cadran + tiroir", "dial": "Cadran", "rounded": "Arrondie", "classic": "Classique"}
# Anciens services (≤ 1.3) qui tenaient le HID eux-mêmes : arrêtés pour laisser la place au démon
LEGACY_SERVICES = ("animematrix-galerie.service", "animematrix-horloge.service", "animematrix-lecture.service")


def interface_saved() -> str:
    try:
        code = INTERFACE_FILE.read_text().strip()
        if code in INTERFACES:
            return code
    except OSError:
        pass
    return "drawer"


def systemctl(*args: str) -> int:
    return subprocess.run(["systemctl", "--user", *args], capture_output=True).returncode


def stop_legacy_services() -> None:
    active = [s for s in LEGACY_SERVICES if systemctl("is-active", "--quiet", s) == 0]
    if active:
        systemctl("stop", *active)


class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"AniMe Matrix {VERSION} - ROG Strix Flare II Animate")
        themes.apply(self, themes.saved())
        self.resizable(False, False)

        self.gif_files: list[Path] = []
        self.show: dict | None = None  # ce que le démon affiche à la demande du lanceur
        self.show_panel: dict | None = None
        self._pending_status: str | None = None
        self._pending_update: tuple[dict, bool] | None = None  # résultat d'une vérification (fil)
        self._pending_install: tuple[bool, str] | None = None
        self.update_info: dict | None = None
        self.update_btn: ttk.Button | None = None
        self.brightness = tk.IntVar(value=60)
        self.last_frame: bytes | None = None  # dernière trame du démon (aperçu des interfaces rondes)
        # Le démon animematrixd est le seul à écrire sur le clavier ; le lanceur le commande.
        stop_legacy_services()
        self.daemon_ok = ctl.ensure_daemon()
        if self.daemon_ok:
            st = self._send("status") or {}
            self.brightness.set(st.get("brightness", 60))
            self.show = st.get("show")
        self._brightness_job = None
        self.brightness.trace_add("write", lambda *_a: self._brightness_changed())

        self.interface = interface_saved()
        if self.interface == "classic":
            self._build_classic()
        else:
            try:
                from rog_flare2_ui_ronde import RoundUI
            except ImportError as exc:  # PIL.ImageTk absent (paquet python3-pil.imagetk) : onglets
                print(f"interface ronde indisponible : {exc}", file=sys.stderr)
                self.interface = "classic"
                self._build_classic()
            else:
                self.round_ui = RoundUI(self, self.interface)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind_all("<KeyPress>", self._game_key, add="+")
        self._poll_status()
        if getattr(self, "round_ui", None) is not None:
            self._poll_frame()
        if not self.daemon_ok:
            self.status.config(text=_("Service animematrixd injoignable"))

        if Image is None:
            messagebox.showwarning(
                _("Pillow manquant"),
                _("Le module Pillow n'est pas installé dans cet environnement.\n"
                  "La lecture de GIF/images sera indisponible.")
            )
        elif gallery_dir().is_dir():
            self.set_files(media_files(gallery_dir()), gallery_dir().name)
        if maj.due():
            self.check_updates(silent=True)

    def _build_classic(self):
        """Interface classique : onglets."""
        ttk.Label(self, text="AniMe Matrix", font=("Sans", 16, "bold")).pack(pady=(16, 4))
        ttk.Label(self, text=f"ROG Strix Flare II Animate · v{VERSION}").pack(pady=(0, 8))

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=12, pady=4)
        for frame, title in self.build_sections(tabs, padding=12):
            tabs.add(frame, text=title)

        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=24, pady=(10, 4))
        ttk.Label(frm, text=_("Luminosité :")).pack(side="left")
        ttk.Scale(frm, from_=5, to=100, variable=self.brightness, orient="horizontal").pack(
            side="left", fill="x", expand=True, padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=24, pady=4)
        ttk.Button(btns, text=_("🕒 Horloge"), command=self.start_clock).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(btns, text=_("■ Arrêter"), command=self.stop_and_clear).pack(
            side="left", expand=True, fill="x", padx=(4, 0))

        self.status = ttk.Label(self, text="", style="Muted.TLabel")
        self.status.pack(pady=(8, 12))

    def build_sections(self, parent, padding=12, wrap=380) -> list[tuple[ttk.Frame, str]]:
        """Les quatre blocs de commandes (GIF, Effets, Audio, Réglages), communs à toutes les interfaces."""
        self.wrap = wrap
        gif = self._build_gif_tab(parent, padding)
        eff, self.effect_panel = self._build_effect_tab(parent, "Effets", list(EFFECTS), "Plasma", padding)
        aud, self.audio_panel = self._build_effect_tab(parent, "Audio", list(AUDIO_EFFECTS), "Spectrum Bars", padding)
        sett = self._build_settings_tab(parent, padding)
        return [(gif, _("GIF / images")), (eff, _("Effets")), (aud, _("Audio")), (sett, _("Réglages"))]

    def _build_gif_tab(self, parent, padding=12) -> ttk.Frame:
        tab = ttk.Frame(parent, padding=padding)
        src = ttk.Frame(tab)
        src.pack(fill="x", pady=4)
        ttk.Button(src, text=_("GIF/images…"), command=self.choose_files).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(src, text=_("Dossier (galerie)…"), command=self.choose_folder).pack(
            side="left", expand=True, fill="x", padx=(4, 0))

        self.loop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text=_("Boucler / enchaîner les fichiers"), variable=self.loop_var).pack(anchor="w")
        self.converted_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text=_("Préférer les versions converties (matrix/)"),
                        variable=self.converted_var).pack(anchor="w")
        self.faithful_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab, text=_("Géométrie fidèle (les formes gardent leurs proportions)"),
                        variable=self.faithful_var).pack(anchor="w")
        self.play_btn = ttk.Button(tab, text=_("▶ Lancer les GIF"), command=self.start_playback, state="disabled")
        self.play_btn.pack(fill="x", pady=(8, 4))
        ttk.Button(tab, text=_("👁 Aperçu fidèle (avant envoi)"), command=self.open_preview).pack(fill="x", pady=(0, 4))
        ttk.Button(tab, text=_("🎞 Créer une animation (éditeur)"), command=self.open_animation).pack(fill="x", pady=(0, 4))
        ttk.Button(tab, text=_("📚 Bibliothèque d'animations"), command=self.open_library).pack(fill="x", pady=(0, 4))
        ttk.Button(tab, text=_("★ Listes de lecture et favoris"), command=self.open_lists).pack(fill="x", pady=(0, 4))

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(tab, text=_("Convertir pour la matrice (19×24, gris, 3 niveaux, sans tramage)"),
                  wraplength=self.wrap, justify="center").pack()
        self.smart_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text=_("Conversion intelligente (recadrage sur le sujet, contours)"),
                        variable=self.smart_var).pack(anchor="w", pady=(4, 0))
        conv = ttk.Frame(tab)
        conv.pack(fill="x", pady=(4, 0))
        ttk.Button(conv, text=_("Convertir des GIF…"), command=self.convert_files).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(conv, text=_("Convertir un dossier…"), command=self.convert_folder).pack(
            side="left", expand=True, fill="x", padx=(4, 0))
        return tab

    def _build_effect_tab(self, parent, title: str, names: list[str], default: str,
                          padding=12) -> tuple[ttk.Frame, dict]:
        """Bloc d'effets PolyWollyWin : choix, réglages de l'effet (PARAMS), cadence, lancement."""
        tab = ttk.Frame(parent, padding=padding)
        # Noms internes (anglais, PolyWollyWin) <-> noms affichés (traduits)
        panel = {"labels": {effect_label(n): n for n in names}, "values": {}, "speed": tk.DoubleVar(value=1.0)}
        panel["name"] = tk.StringVar(value=effect_label(default))
        panel["speed"].trace_add("write", lambda *_a: self._speed_changed(panel))
        # liste entière déroulée : Moniteur système et jeux, en fin de liste, restaient cachés sous le défilement
        cb = ttk.Combobox(tab, textvariable=panel["name"], values=list(panel["labels"]), state="readonly",
                          height=len(panel["labels"]))
        cb.pack(fill="x", pady=(0, 8))
        panel["params"] = ttk.Frame(tab)
        panel["params"].pack(fill="x")
        spd = ttk.Frame(tab)
        spd.pack(fill="x", pady=(8, 0))
        ttk.Label(spd, text=_("Cadence"), width=14).pack(side="left")
        ttk.Scale(spd, from_=0.2, to=3.0, variable=panel["speed"], orient="horizontal").pack(
            side="left", fill="x", expand=True)
        if title == "Effets":
            self.game_hint = ttk.Label(tab, text=_("Jeux : flèches et Espace, Entrée pour rejouer (fenêtre au premier plan)"),
                                       style="Muted.TLabel", wraplength=self.wrap)
            self.game_hint.pack(anchor="w", pady=(6, 0))
        if title == "Audio":
            ttk.Label(tab, text=_("Source : moniteur de la sortie son par défaut (parec)"),
                      style="Muted.TLabel", wraplength=self.wrap).pack(anchor="w", pady=(6, 0))
        ttk.Button(tab, text=_("▶ Lancer l'effet"), command=lambda: self.start_effect(panel)).pack(
            fill="x", pady=(10, 0))
        ttk.Label(tab, text=_("Effets : PolyWollyWin (MIT, Mike Opitz)"), style="Muted.TLabel").pack(pady=(6, 0))
        cb.bind("<<ComboboxSelected>>", lambda _e: self._fill_params(panel))
        self._fill_params(panel)
        return tab, panel

    def _fill_params(self, panel: dict):
        for w in panel["params"].winfo_children():
            w.destroy()
        panel["values"] = {}
        for attr, spec in effect_class(self._effect_name(panel)).PARAMS.items():
            row = ttk.Frame(panel["params"])
            row.pack(fill="x", pady=1)
            ttk.Label(row, text=_(spec.get("label", attr)), width=14).pack(side="left")
            if spec.get("type") == "text":
                var = tk.StringVar(value=spec.get("default", ""))
                ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
            else:
                var = tk.IntVar(value=int(spec["default"]))
                ttk.Scale(row, from_=spec["min"], to=spec["max"], variable=var, orient="horizontal",
                          command=lambda v, var=var: var.set(round(float(v)))).pack(
                    side="left", fill="x", expand=True)
                ttk.Label(row, textvariable=var, width=5).pack(side="left")
            var.trace_add("write", lambda *_a, a=attr, s=spec, v=var: self._apply_param(a, s, v))
            panel["values"][attr] = var

    @staticmethod
    def _effect_name(panel: dict) -> str:
        return panel["labels"].get(panel["name"].get(), panel["name"].get())

    def _apply_param(self, attr: str, spec: dict, var: tk.Variable):
        """Réglage appliqué en direct à l'effet en cours s'il possède cet attribut."""
        show = self.show
        if not show or show.get("type") != "effet" or attr not in effect_class(show["name"]).PARAMS:
            return
        try:
            self._send("params", params={attr: var.get()})
        except tk.TclError:
            pass

    def _build_settings_tab(self, parent, padding=12) -> ttk.Frame:
        tab = ttk.Frame(parent, padding=padding)
        boot = ttk.Frame(tab)
        boot.pack(fill="x", pady=4)
        ttk.Label(boot, text=_("Au démarrage de session :")).pack(side="left")
        boot_labels = {_(m): m for m in BOOT_MODES}
        self.boot_var = tk.StringVar(value=_(self.boot_mode()))
        cb = ttk.Combobox(boot, textvariable=self.boot_var, values=list(boot_labels), state="readonly", width=14)
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", lambda _e: self.set_boot_mode(boot_labels[self.boot_var.get()]))

        import rog_flare2_horloges as horloges
        face = ttk.Frame(tab)
        face.pack(fill="x", pady=4)
        ttk.Label(face, text=_("Cadran de l'horloge :")).pack(side="left")
        face_labels = {_(label): key for key, label in horloges.FACE_LABELS.items()}
        self.face_var = tk.StringVar(value=_(horloges.FACE_LABELS[horloges.saved_face()]))
        fcb = ttk.Combobox(face, textvariable=self.face_var, values=list(face_labels), state="readonly", width=14)
        fcb.pack(side="left", padx=8)
        fcb.bind("<<ComboboxSelected>>", lambda _e: self.set_face(face_labels[self.face_var.get()]))

        lang = ttk.Frame(tab)
        lang.pack(fill="x", pady=4)
        ttk.Label(lang, text=_("Langue :")).pack(side="left")
        codes = {name: code for code, name in LANGUAGES.items()}
        self.lang_var = tk.StringVar(value=LANGUAGES[LANG])
        lcb = ttk.Combobox(lang, textvariable=self.lang_var, values=list(codes), state="readonly", width=18)
        lcb.pack(side="left", padx=8)
        lcb.bind("<<ComboboxSelected>>", lambda _e: self.change_language(codes[self.lang_var.get()]))

        thm = ttk.Frame(tab)
        thm.pack(fill="x", pady=4)
        ttk.Label(thm, text=_("Thème :")).pack(side="left")
        theme_labels = {_(t): t for t in themes.THEMES}
        self.theme_var = tk.StringVar(value=_(themes.saved()))
        tcb = ttk.Combobox(thm, textvariable=self.theme_var, values=list(theme_labels), state="readonly", width=18)
        tcb.pack(side="left", padx=8)
        tcb.bind("<<ComboboxSelected>>", lambda _e: self.change_theme(theme_labels[self.theme_var.get()]))

        itf = ttk.Frame(tab)
        itf.pack(fill="x", pady=4)
        ttk.Label(itf, text=_("Interface :")).pack(side="left")
        itf_labels = {_(label): code for code, label in INTERFACES.items()}
        self.itf_var = tk.StringVar(value=_(INTERFACES[self.interface]))
        icb = ttk.Combobox(itf, textvariable=self.itf_var, values=list(itf_labels), state="readonly", width=18)
        icb.pack(side="left", padx=8)
        icb.bind("<<ComboboxSelected>>", lambda _e: self.change_interface(itf_labels[self.itf_var.get()]))
        cfg = notifs.load_config()
        self.notif_var = tk.BooleanVar(value=cfg.get("actif", False))
        ttk.Checkbutton(tab, text=_("Notifications du bureau sur l'écran"), variable=self.notif_var,
                        command=self._save_notifications).pack(anchor="w", pady=(4, 0))
        apps = ttk.Frame(tab)
        apps.pack(fill="x")
        ttk.Label(apps, text=_("Applications (vide = toutes) :")).pack(side="left")
        self.notif_apps = tk.StringVar(value=", ".join(cfg.get("applis", [])))
        entry = ttk.Entry(apps, textvariable=self.notif_apps)
        entry.pack(side="left", fill="x", expand=True, padx=(6, 0))
        entry.bind("<Return>", lambda _e: self._save_notifications())
        entry.bind("<FocusOut>", lambda _e: self._save_notifications())
        rgb = ttk.Frame(tab)
        rgb.pack(fill="x", pady=4)
        ttk.Label(rgb, text=_("Couleurs du clavier (OpenRGB) :")).pack(side="left")
        rgb_modes = {_("Désactivées"): "off", _("Couleur du thème"): "theme", _("Pulsation avec l'écran"): "pulsation"}
        current = openrgb.load_config().get("mode", "off")
        self.rgb_var = tk.StringVar(value=next(k for k, v in rgb_modes.items() if v == current))
        rcb = ttk.Combobox(rgb, textvariable=self.rgb_var, values=list(rgb_modes), state="readonly", width=20)
        rcb.pack(side="left", padx=8)
        rcb.bind("<<ComboboxSelected>>", lambda _e: (
            openrgb.save_config({**openrgb.load_config(), "mode": rgb_modes[self.rgb_var.get()]}), self._send("config")))
        ttk.Label(tab, text=_("La galerie de fond lit le dernier dossier choisi dans l'onglet GIF."),
                  style="Muted.TLabel", wraplength=self.wrap).pack(anchor="w")
        ttk.Button(tab, text=_("✎ Dessiner mon propre motif (éditeur)"),
                   command=self.open_paint_editor).pack(fill="x", pady=(12, 0))
        ttk.Button(tab, text=_("Dossier des extensions (effets)"),
                   command=self.open_plugin_dir).pack(fill="x", pady=(4, 0))
        ttk.Button(tab, text=_("Programmation…"), command=self.open_schedule).pack(fill="x", pady=(4, 0))
        ttk.Button(tab, text=_("Voyants (micro, webcam, OBS)…"), command=self.open_badges).pack(fill="x", pady=(4, 0))
        self.tray_var = tk.BooleanVar(value=tray.AUTOSTART.exists())
        ttk.Checkbutton(tab, text=_("Icône dans la barre système"), variable=self.tray_var,
                        command=self._toggle_tray).pack(anchor="w", pady=(4, 0))
        import rog_flare2_fin as fin
        self.fin_var = tk.BooleanVar(value=fin.enabled())
        ttk.Checkbutton(tab, text=_("Afficher la fin des commandes longues (terminal)"), variable=self.fin_var,
                        command=lambda: fin.set_enabled(self.fin_var.get())).pack(anchor="w", pady=(2, 0))

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=12)
        ttk.Label(tab, text=_("AniMe Matrix pour Linux {version}").format(version=VERSION)).pack()
        self.update_btn = ttk.Button(tab, text=_("Rechercher les mises à jour"), command=self.on_update_button)
        self.update_btn.pack(fill="x", pady=(8, 0))
        self.update_auto = tk.BooleanVar(value=maj.load_state().get("auto", True))
        ttk.Checkbutton(tab, text=_("Vérifier au démarrage"), variable=self.update_auto,
                        command=lambda: maj.save_state({**maj.load_state(), "auto": self.update_auto.get()})
                        ).pack(anchor="w")
        ttk.Button(tab, text=_("☕ Soutenir le projet (Buy Me a Coffee)"),
                   command=lambda: webbrowser.open(SUPPORT_URL)).pack(fill="x", pady=(8, 4))
        ttk.Button(tab, text=_("Page du projet (GitHub)"),
                   command=lambda: webbrowser.open(PROJECT_URL)).pack(fill="x")
        return tab

    def set_status(self, text: str):
        """Appelable depuis un fil : le texte est posé ici et affiché par _poll_status."""
        self._pending_status = text

    def _poll_status(self):
        text, self._pending_status = self._pending_status, None
        if text is not None:
            self.status.config(text=text)
        if self._pending_update is not None:
            (info, silent), self._pending_update = self._pending_update, None
            self._update_result(info, silent)
        if self._pending_install is not None:
            (ok, err), self._pending_install = self._pending_install, None
            self._install_result(ok, err)
        self.after(100, self._poll_status)

    # --- Mises à jour (releases GitHub, rog_flare2_maj.py) ------------------
    def check_updates(self, silent: bool = False):
        """Interroge GitHub dans un fil ; silent : vérification automatique, rien si à jour ou hors ligne."""
        if not silent:
            self.set_status(_("Recherche de mises à jour…"))

        def worker():
            try:
                info = maj.latest(VERSION)
            except (OSError, ValueError, KeyError) as exc:
                if not silent:
                    self.set_status(_("Impossible de joindre GitHub : {err}").format(err=exc))
                return
            maj.save_state({**maj.load_state(), "last": time.time()})
            self._pending_update = (info, silent)

        threading.Thread(target=worker, daemon=True).start()

    def _update_result(self, info: dict, silent: bool):
        if not maj.is_newer(info, VERSION):
            if not silent:
                self.status.config(text=_("AniMe Matrix est à jour ({version}).").format(version=VERSION))
            return
        self.update_info = info
        self.status.config(text=_("Mise à jour {version} disponible").format(version=info["version"]))
        if self.update_btn is not None:
            self.update_btn.config(text=_("Installer la version {version}").format(version=info["version"]))
        if not silent:
            self.offer_update()

    def on_update_button(self):
        if self.update_info is not None:
            self.offer_update()
        else:
            self.check_updates()

    def offer_update(self):
        info = self.update_info
        if not maj.packaged():
            messagebox.showinfo(_("Mise à jour disponible"), _(
                "AniMe Matrix tourne depuis les sources : mettez à jour avec git pull, "
                "ou installez le paquet .deb de la page des versions."))
            webbrowser.open(info["page"])
            return
        text = _("La version {new} est disponible (installée : {current}).\n\n{notes}\n\nL'installer maintenant ?").format(
            new=info["version"], current=VERSION, notes=maj.notes_excerpt(info["notes"], LANG))
        if not messagebox.askyesno(_("Mise à jour disponible"), text):
            return

        def worker():
            try:
                deb = maj.download(info, lambda pct: self.set_status(
                    _("Téléchargement de la version {version}… {pct} %").format(version=info["version"], pct=pct)))
            except OSError as exc:
                self._pending_install = (False, str(exc))
                return
            self.set_status(_("Installation (mot de passe administrateur)…"))
            self._pending_install = maj.install(deb)

        threading.Thread(target=worker, daemon=True).start()

    def _install_result(self, ok: bool, err: str):
        if ok:
            self.update_info = None
            if messagebox.askyesno(_("Mise à jour disponible"), _("Mise à jour installée. Relancer AniMe Matrix maintenant ?")):
                self.restart()
        elif err == "annulé":
            self.status.config(text=_("Mise à jour annulée."))
        else:
            self.status.config(text=_("Échec de la mise à jour : {err}").format(err=err))

    def set_files(self, files: list[Path], label: str):
        self.gif_files = files
        self.status.config(text=_("{n} fichier(s) : {label}").format(n=len(files), label=label))
        self.play_btn.config(state="normal" if files and Image is not None else "disabled")

    def choose_files(self):
        try:
            result = subprocess.run(
                [
                    "zenity", "--file-selection", "--multiple", "--separator=\n",
                    "--title=" + _("Choisir un ou plusieurs GIF/images"),
                    f"--file-filter={_('Images et GIF')} | *.gif *.png *.jpg *.jpeg *.bmp *.webp",
                    f"--file-filter={_('Tous les fichiers')} | *",
                ],
                capture_output=True, text=True, timeout=300,
            )
            paths = [p for p in result.stdout.strip().split("\n") if p]
        except (FileNotFoundError, subprocess.SubprocessError):
            paths = filedialog.askopenfilenames(
                title=_("Choisir un ou plusieurs GIF/images"),
                filetypes=[(_("Images et GIF"), "*.gif *.png *.jpg *.jpeg *.bmp *.webp"), (_("Tous les fichiers"), "*.*")],
            )
        if paths:
            self.set_files([Path(p) for p in paths], _("sélection"))

    def choose_folder(self):
        try:
            result = subprocess.run(
                ["zenity", "--file-selection", "--directory", "--title=" + _("Dossier de GIF à lire en galerie"),
                 f"--filename={gallery_dir()}/"],
                capture_output=True, text=True, timeout=300)
            path = result.stdout.strip()
        except (FileNotFoundError, subprocess.SubprocessError):
            path = filedialog.askdirectory(title=_("Dossier de GIF à lire en galerie"), initialdir=gallery_dir())
        if path:
            save_gallery_dir(Path(path))
            self.set_files(media_files(Path(path)), Path(path).name)

    # --- Lecture sur le clavier ---------------------------------------------
    # --- Commandes au démon ------------------------------------------------
    def _send(self, cmd: str, **kw) -> dict | None:
        try:
            return ctl.request(cmd, **kw)
        except (OSError, ValueError, ctl.DaemonError) as exc:
            self.set_status(_("Erreur : {err}").format(err=exc))
            return None

    def _play(self, show: dict, status: str):
        if self._send("play", show=show) is not None:
            self.show = show
            self.set_status(status)

    def _brightness_changed(self):
        """Luminosité envoyée au démon, au plus toutes les 60 ms pendant un glissement."""
        if self._brightness_job is None:
            self._brightness_job = self.after(60, self._send_brightness)

    def _send_brightness(self):
        self._brightness_job = None
        self._send("brightness", value=int(self.brightness.get()))

    def _poll_frame(self):
        """Aperçu : dernière trame envoyée par le démon."""
        try:
            leds = base64.b64decode(ctl.request("frame", timeout=0.3)["frame"])
            self.last_frame = bytes(FB_OFFSET) + leds
        except (OSError, ValueError, KeyError, ctl.DaemonError):
            pass
        self.after(80, self._poll_frame)

    def start_playback(self):
        if not self.gif_files or Image is None:
            return
        show = {"type": "gif", "files": [str(f) for f in self.gif_files], "loop": bool(self.loop_var.get()),
                "converted": bool(self.converted_var.get()), "fidele": bool(self.faithful_var.get())}
        self._play(show, _("Lecture : {name}").format(name=self.status_label_for_files()))

    def status_label_for_files(self) -> str:
        return self.gif_files[0].parent.name if len(self.gif_files) > 1 else self.gif_files[0].name

    def start_clock(self):
        self._play({"type": "horloge"}, _("Horloge"))

    def set_face(self, face: str):
        """Cadran mémorisé ; l'horloge en cours change tout de suite."""
        import rog_flare2_horloges as horloges
        horloges.save_face(face)
        if (self.show or {}).get("type") == "horloge":
            self.start_clock()

    def start_effect(self, panel: dict):
        name = self._effect_name(panel)
        show = {"type": "effet", "name": name, "params": {a: v.get() for a, v in panel["values"].items()},
                "speed": float(panel["speed"].get())}
        self.show_panel = panel
        self._play(show, _("Effet : {name}").format(name=effect_label(name)))

    def _game_key(self, event):
        """Touches transmises au jeu affiché (sauf pendant la saisie dans un champ)."""
        show = self.show or {}
        if show.get("type") != "effet" or show.get("name") not in GAME_NAMES:
            return
        if isinstance(event.widget, (tk.Entry, ttk.Entry, ttk.Combobox)):
            return
        if event.keysym in ("Up", "Down", "Left", "Right", "space", "Return", "KP_Enter"):
            self._send("key", key=event.keysym)
            return "break"

    def _speed_changed(self, panel: dict):
        if self.show and self.show.get("type") == "effet" and self.show_panel is panel:
            self._send("speed", value=float(panel["speed"].get()))

    def stop_playback(self):
        """Rien à arrêter localement : la lecture est dans le démon."""

    def stop_and_clear(self):
        if self._send("stop") is not None:
            self.show = None
            self.set_status(_("Arrêté"))

    # --- Démarrage de session (services systemd --user) ---------------------
    def boot_mode(self) -> str:
        try:
            mode = START_FILE.read_text().strip()
        except OSError:
            mode = "rien"
        return next((label for label, m in BOOT_MODES.items() if m == mode), "Rien")

    def set_boot_mode(self, label: str):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        START_FILE.write_text(BOOT_MODES[label] + "\n")
        systemctl("enable", "animematrixd.service")  # le démon démarre avec la session
        for service in LEGACY_SERVICES:
            systemctl("disable", service)
        self.status.config(text=_("Au démarrage : {mode}").format(mode=_(label)))

    # --- Conversion ImageMagick (rog_flare2_convertir.py) -------------------
    def convert_files(self):
        try:
            result = subprocess.run(
                ["zenity", "--file-selection", "--multiple", "--separator=\n",
                 "--title=" + _("GIF/images à convertir pour la matrice"),
                 f"--file-filter={_('Images et GIF')} | *.gif *.png *.jpg *.jpeg *.bmp *.webp",
                 f"--file-filter={_('Tous les fichiers')} | *"],
                capture_output=True, text=True, timeout=300)
            paths = [p for p in result.stdout.strip().split("\n") if p]
        except (FileNotFoundError, subprocess.SubprocessError):
            paths = filedialog.askopenfilenames(
                title=_("GIF/images à convertir pour la matrice"),
                filetypes=[(_("Images et GIF"), "*.gif *.png *.jpg *.jpeg *.bmp *.webp"), (_("Tous les fichiers"), "*.*")])
        if paths:
            self._convert([Path(p) for p in paths])

    def convert_folder(self):
        try:
            result = subprocess.run(
                ["zenity", "--file-selection", "--directory", "--title=" + _("Dossier de GIF à convertir")],
                capture_output=True, text=True, timeout=300)
            path = result.stdout.strip()
        except (FileNotFoundError, subprocess.SubprocessError):
            path = filedialog.askdirectory(title=_("Dossier de GIF à convertir"))
        if path:
            self._convert([Path(path)])

    def _convert(self, chemins: list[Path]):
        """Conversion dans un fil ; sortie dans <dossier>/matrix/ ; propose ensuite de charger le résultat."""
        smart, faithful = bool(self.smart_var.get()), bool(self.faithful_var.get())

        def rappel(i, n, src, etat):
            etat = {"ok": _("converti"), "saute": _("déjà à jour")}.get(etat, etat.replace("erreur", _("erreur"), 1))
            self.after(0, lambda: self.status.config(text=_("Conversion {i}/{n} : {name} — {state}").format(
                i=i, n=n, name=src.name, state=etat)))

        def worker():
            produits = convertir_tout(chemins, None, False, rappel, intelligente=smart, fidele=faithful)

            def fin():
                if not produits:
                    self.status.config(text=_("Conversion : aucun fichier produit"))
                    return
                dossier = produits[0].parent
                self.status.config(text=_("{n} GIF prêt(s) dans {folder}").format(n=len(produits), folder=dossier))
                if messagebox.askyesno(_("Conversion terminée"),
                                       _("{n} GIF convertis dans\n{folder}\n\nLes charger pour lecture ?").format(
                                           n=len(produits), folder=dossier)):
                    self.gif_files = list(produits)
                    self.play_btn.config(state="normal" if Image is not None else "disabled")
            self.after(0, fin)

        self.status.config(text=_("Conversion en cours…"))
        threading.Thread(target=worker, daemon=True).start()


    def change_theme(self, name: str):
        themes.save(name)
        themes.apply(self, name)
        if getattr(self, "round_ui", None) is not None:
            self.round_ui.retheme()

    def change_interface(self, code: str):
        if code == self.interface:
            return
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        INTERFACE_FILE.write_text(code + "\n")
        self.restart()

    def restart(self):
        """Relance le lanceur (langue ou interface changée) ; le démon continue d'afficher."""
        os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])

    def change_language(self, code: str):
        """Enregistre la langue et relance le lanceur pour l'appliquer."""
        if code == LANG:
            return
        save_language(code)
        self.restart()

    def _save_notifications(self):
        apps = [a.strip() for a in self.notif_apps.get().split(",") if a.strip()]
        notifs.save_config({"actif": bool(self.notif_var.get()), "applis": apps})
        self._send("config")

    def open_preview(self):
        """Aperçu fidèle des GIF sélectionnés, sans rien envoyer au clavier."""
        if not self.gif_files:
            return
        try:
            from rog_flare2_simulateur import PreviewWindow
            PreviewWindow(self, self.gif_files, self.brightness.get, _("Aperçu fidèle (avant envoi)"),
                          pick=pick_version if self.converted_var.get() else (lambda f: f),
                          fidele=bool(self.faithful_var.get()))
        except ImportError as exc:  # PIL.ImageTk absent
            self.set_status(_("Erreur : {err}").format(err=exc))

    def _toggle_tray(self):
        """Icône de barre système (python3 du système, PyGObject), lancée aussi au démarrage de session."""
        here = Path(__file__).resolve().parent
        command = "animematrix-tray" if maj.packaged() else f"/usr/bin/python3 {here / 'rog_flare2_tray.py'}"
        tray.set_autostart(self.tray_var.get(), command)
        if self.tray_var.get():
            if not tray.running():
                subprocess.Popen(command.split(), start_new_session=True, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        else:
            tray.stop_running()

    def open_schedule(self):
        from rog_flare2_ui_programme import ScheduleWindow
        ScheduleWindow(self, lambda: self._send("config"))

    def open_badges(self):
        from rog_flare2_ui_programme import BadgesWindow
        BadgesWindow(self, lambda: self._send("config"))

    def open_lists(self):
        from rog_flare2_listes import ListsWindow
        ListsWindow(self, self._play, lambda: (self._send("status") or {}).get("show"))

    def open_library(self):
        from rog_flare2_bibliotheque import LibraryWindow
        LibraryWindow(self, lambda show: self._play(show, _("Bibliothèque d'animations")))

    def open_animation(self):
        from rog_flare2_animation import AnimationEditor
        AnimationEditor(self)

    def open_plugin_dir(self):
        """Ouvre le dossier des extensions ; à la première ouverture, y dépose l'exemple et le guide."""
        PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
        here = Path(__file__).parent
        example = here / "examples" / "effets" / "battement_coeur.py"
        if not any(PLUGIN_DIR.glob("*.py")) and example.exists():
            (PLUGIN_DIR / "battement_coeur.py.exemple").write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
        subprocess.Popen(["xdg-open", str(PLUGIN_DIR)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def open_paint_editor(self):
        self._send("release")  # l'éditeur écrit lui-même ; il rend la main au démon en fermant
        script = Path(__file__).parent / "rog_flare2_matrix_paint.py"
        subprocess.Popen([sys.executable, str(script)])
        self.destroy()

    def on_close(self):
        """Ce qui est affiché continue après la fermeture : le démon garde la main."""
        self.destroy()


if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
