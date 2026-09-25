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

import datetime
import json
import os
import subprocess
import webbrowser
import sys
import threading
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_clock_v3 import brightness_to_raw, make_frame
from rog_flare2_convertir import convertir_tout
from rog_flare2_i18n import LANG, LANGUAGES, _, save_language
import rog_flare2_themes as themes
from rog_flare2_effets import AUDIO_EFFECTS, EFFECTS, effect_class, make_effect, param_value, run_effect
from rog_flare2_matrix_paint import (
    FlareTransport,
    PHYSICAL_CALIBRATED_ORDER,
    PREFIX,
    FB_OFFSET,
    FRAME_SIZE,
    LED_COUNT,
    PHYSICAL_ROW_COUNTS,
    physical_row_offset,
)

try:
    from PIL import Image, ImageSequence
except ImportError:
    Image = None

MAX_ROW_WIDTH = max(PHYSICAL_ROW_COUNTS)
NUM_ROWS = len(PHYSICAL_ROW_COUNTS)
MEDIA_EXTENSIONS = {".gif", ".png", ".jpg", ".jpeg", ".bmp", ".webp"}
STILL_SECONDS = 5.0  # durée d'affichage d'une image fixe dans une galerie
VERSION = "1.2.0"
PROJECT_URL = "https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix"
SUPPORT_URL = "https://buymeacoffee.com/anticitoyen"
# Services de fond (rog_flare2_bascule.sh) ; un seul peut tenir le HID.
SERVICES = {"gif": "animematrix-galerie.service", "horloge": "animematrix-horloge.service",
            "lecture": "animematrix-lecture.service"}
BOOT_MODES = {"Galerie GIF": SERVICES["gif"], "Horloge": SERVICES["horloge"],
              "Dernière lecture": SERVICES["lecture"], "Rien": None}
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "rog-flare2"
MODE_FILE = CONFIG_DIR / "mode"
GALLERY_FILE = CONFIG_DIR / "galerie"  # dossier lu par la galerie (lanceur et service)
INTERFACE_FILE = CONFIG_DIR / "interface"
# Interfaces : cadran + tiroir (défaut), cadran seul, fenêtre arrondie, onglets classiques
INTERFACES = {"drawer": "Cadran + tiroir", "dial": "Cadran", "rounded": "Arrondie", "classic": "Classique"}
SHOW_FILE = CONFIG_DIR / "lecture.json"  # ce que la lecture de fond rejoue (rog_flare2_lecture.py)
SHOW_PID = CONFIG_DIR / "lecture.pid"  # lecture de fond lancée sans systemd


def gallery_dir() -> Path:
    """Dossier de la galerie : celui choisi en dernier, sinon <Images>/AniMe-Matrix."""
    try:
        saved = GALLERY_FILE.read_text().strip()
        if saved:
            return Path(saved)
    except OSError:
        pass
    try:
        pictures = subprocess.run(["xdg-user-dir", "PICTURES"], capture_output=True, text=True,
                                  timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pictures = ""
    return Path(pictures or Path.home() / "Pictures") / "AniMe-Matrix"


def interface_saved() -> str:
    try:
        code = INTERFACE_FILE.read_text().strip()
        if code in INTERFACES:
            return code
    except OSError:
        pass
    return "drawer"


def save_gallery_dir(folder: Path) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    GALLERY_FILE.write_text(f"{folder}\n")


def image_to_frame(img: "Image.Image", brightness: int = 100) -> bytes:
    """Convertit une image PIL en trame 1024 octets pour la matrice.

    Le panneau physique est un triangle/coin (19 LED de large en haut,
    7 en bas), pas un rectangle. Pour montrer l'image ENTIERE (pas juste
    une fenêtre fixe qui coupe la partie gauche des lignes étroites), on
    échantillonne chaque ligne sur toute la largeur de l'image source,
    proportionnellement au nombre réel de LED de cette ligne.
    """
    scale = brightness / 100.0
    # Hauteur fixée au nombre de lignes physiques ; largeur gardée haute
    # résolution pour un échantillonnage précis par ligne.
    src_w, src_h = img.size
    sample_w = max(MAX_ROW_WIDTH, src_w)
    gray = img.convert("L").resize((sample_w, NUM_ROWS), Image.LANCZOS)
    pixels = gray.load()

    frame = bytearray(FRAME_SIZE)
    frame[0:2] = PREFIX

    for raw_idx, (row, col) in enumerate(PHYSICAL_CALIBRATED_ORDER):
        row_count = PHYSICAL_ROW_COUNTS[row]
        if row_count > 1:
            gcol = round(col * (sample_w - 1) / (row_count - 1))
        else:
            gcol = 0
        gcol = max(0, min(sample_w - 1, gcol))
        val = int(pixels[gcol, row] * scale)
        frame[FB_OFFSET + raw_idx] = max(0, min(255, val))

    return bytes(frame)


def iter_gif_frames(path: Path):
    """Itère les frames d'un GIF recomposées sur un canevas complet.

    De nombreux GIF (surtout optimisés pour le web) ne stockent, à partir de
    la 2e frame, que la zone modifiée depuis la frame précédente. Itérer
    directement sur ImageSequence sans recomposer ne donne que ce fragment,
    pas l'image entière.

    Le canevas est réutilisé : le consommateur doit le convertir avant de
    demander la frame suivante (garder les canevas pleine taille coûtait
    ~470 Mo pour un GIF 512x720 de 318 frames).
    """
    with Image.open(path) as im:
        canvas = Image.new("RGBA", im.size, (0, 0, 0, 255))
        for frame in ImageSequence.Iterator(im):
            rgba = frame.convert("RGBA")
            canvas.paste(rgba, (0, 0), rgba)
            duration_ms = frame.info.get("duration", 100)
            yield canvas, max(20, duration_ms) / 1000.0


def pick_version(f: Path) -> Path:
    """Version convertie <dossier>/matrix/<nom>.gif si elle existe et n'est pas plus vieille que la source."""
    converted = f.parent / "matrix" / f.with_suffix(".gif").name
    if converted.exists() and converted.stat().st_mtime >= f.stat().st_mtime:
        return converted
    return f


def media_files(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS)


def play_file(path: Path, transport: FlareTransport, stop_event: threading.Event, brightness) -> None:
    """Joue une fois un GIF/image en flux ; brightness() est relue à chaque frame."""
    n = 0
    for img, delay in iter_gif_frames(path):
        if stop_event.is_set():
            return
        transport.write(image_to_frame(img, brightness()))
        n += 1
        stop_event.wait(delay)
    if n == 1:
        stop_event.wait(STILL_SECONDS)


def play_clock(transport: FlareTransport, stop_event: threading.Event, brightness) -> None:
    while not stop_event.is_set():
        now = datetime.datetime.now()
        transport.write(make_frame(now.strftime("%H:%M"), preset="flare", val=brightness_to_raw(brightness()),
                                   y=0, blink_colon=now.second % 2 == 0, overrides={}))
        stop_event.wait(0.5)


def systemctl(*args: str) -> int:
    return subprocess.run(["systemctl", "--user", *args], capture_output=True).returncode


def stop_services() -> list[str]:
    """Arrête les services de fond qui tiennent le HID ; renvoie ceux qui tournaient."""
    active = [s for s in SERVICES.values() if systemctl("is-active", "--quiet", s) == 0]
    if active:
        systemctl("stop", *active)
    try:  # lecture de fond détachée (sans systemd)
        pid = int(SHOW_PID.read_text())
        if "rog_flare2_lecture.py" in Path(f"/proc/{pid}/cmdline").read_text():
            os.kill(pid, 15)
            active.append(f"pid {pid}")
        SHOW_PID.unlink()
    except (OSError, ValueError):
        pass
    return active


def hand_off(show: dict) -> None:
    """Confie l'affichage en cours à la lecture de fond, qui survit au lanceur."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    SHOW_FILE.write_text(json.dumps(show, ensure_ascii=False, indent=1), encoding="utf-8")
    MODE_FILE.write_text("lecture\n")
    if systemctl("restart", SERVICES["lecture"]) == 0:
        return
    proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name("rog_flare2_lecture.py"))],
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    SHOW_PID.write_text(f"{proc.pid}\n")


class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AniMe Matrix - ROG Strix Flare II Animate")
        themes.apply(self, themes.saved())
        self.resizable(False, False)

        self.transport = FlareTransport()
        self.play_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.gif_files: list[Path] = []
        self.show: dict | None = None  # ce qui est affiché, pour la lecture de fond à la fermeture
        self.show_panel: dict | None = None
        self.live_params: dict = {}
        self._pending_status: str | None = None
        self.running_effect = None
        self.brightness = tk.IntVar(value=60)
        self.last_frame: bytes | None = None  # dernière trame envoyée (aperçu des interfaces rondes)
        send = self.transport.write

        def write_and_keep(frame: bytes) -> int:
            self.last_frame = frame
            return send(frame)

        self.transport.write = write_and_keep

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
        self._poll_status()

        if Image is None:
            messagebox.showwarning(
                _("Pillow manquant"),
                _("Le module Pillow n'est pas installé dans cet environnement.\n"
                  "La lecture de GIF/images sera indisponible.")
            )
        elif gallery_dir().is_dir():
            self.set_files(media_files(gallery_dir()), gallery_dir().name)

    def _build_classic(self):
        """Interface classique : onglets."""
        ttk.Label(self, text="AniMe Matrix", font=("Sans", 16, "bold")).pack(pady=(16, 4))
        ttk.Label(self, text="ROG Strix Flare II Animate").pack(pady=(0, 8))

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
        self.play_btn = ttk.Button(tab, text=_("▶ Lancer les GIF"), command=self.start_playback, state="disabled")
        self.play_btn.pack(fill="x", pady=(8, 4))

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(tab, text=_("Convertir pour la matrice (19×24, gris, 3 niveaux, sans tramage)"),
                  wraplength=self.wrap, justify="center").pack()
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
        panel = {"labels": {_(n): n for n in names}, "values": {}, "speed": tk.DoubleVar(value=1.0)}
        panel["name"] = tk.StringVar(value=_(default))
        cb = ttk.Combobox(tab, textvariable=panel["name"], values=list(panel["labels"]), state="readonly")
        cb.pack(fill="x", pady=(0, 8))
        panel["params"] = ttk.Frame(tab)
        panel["params"].pack(fill="x")
        spd = ttk.Frame(tab)
        spd.pack(fill="x", pady=(8, 0))
        ttk.Label(spd, text=_("Cadence"), width=14).pack(side="left")
        ttk.Scale(spd, from_=0.2, to=3.0, variable=panel["speed"], orient="horizontal").pack(
            side="left", fill="x", expand=True)
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
        effect = self.running_effect
        if effect is not None and attr in type(effect).PARAMS:
            try:
                setattr(effect, attr, param_value(spec, var.get()))
                self.live_params[attr] = var.get()
            except (tk.TclError, ValueError):
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
        ttk.Label(tab, text=_("La galerie de fond lit le dernier dossier choisi dans l'onglet GIF."),
                  style="Muted.TLabel", wraplength=self.wrap).pack(anchor="w")
        ttk.Button(tab, text=_("✎ Dessiner mon propre motif (éditeur)"),
                   command=self.open_paint_editor).pack(fill="x", pady=(12, 0))

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=12)
        ttk.Label(tab, text=_("AniMe Matrix pour Linux {version}").format(version=VERSION)).pack()
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
        self.after(100, self._poll_status)

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
    def _start(self, job):
        """Lance job(stop_event) dans un fil, seul à écrire sur le HID."""
        self.stop_playback()
        if self.play_thread is not None:
            # stop_playback a echoue a arreter l'ancien thread : ne pas en
            # lancer un second par-dessus.
            return
        stop_services()
        self.stop_event = threading.Event()
        stop = self.stop_event

        def worker():
            try:
                self.transport.connect()
                job(stop)
            except Exception as exc:
                self.set_status(_("Erreur : {err}").format(err=exc))
                return
            self.set_status(_("Arrêté"))

        self.play_thread = threading.Thread(target=worker, daemon=True)
        self.play_thread.start()

    def start_playback(self):
        if not self.gif_files or Image is None:
            return
        files = list(self.gif_files)
        loop = self.loop_var.get
        converted = self.converted_var.get()

        def job(stop):
            while not stop.is_set():
                for f in files:
                    if stop.is_set():
                        break
                    src = pick_version(f) if converted else f
                    self.set_status(_("Lecture : {name}").format(name=src.name))
                    try:
                        play_file(src, self.transport, stop, self.brightness.get)
                    except OSError as exc:
                        self.set_status(_("Sauté {name} : {err}").format(name=src.name, err=exc))
                if not loop():
                    break

        self.show = {"type": "gif", "files": [str(f) for f in files], "converted": converted}
        self._start(job)

    def start_clock(self):
        def job(stop):
            self.set_status(_("Horloge"))
            play_clock(self.transport, stop, self.brightness.get)

        self.show = {"type": "horloge"}
        self._start(job)

    def start_effect(self, panel: dict):
        name = self._effect_name(panel)
        raw = {a: v.get() for a, v in panel["values"].items()}
        speed = panel["speed"].get

        def job(stop):
            effect = make_effect(name, raw)
            self.running_effect = effect
            self.set_status(_("Effet : {name}").format(name=_(name)))
            try:
                run_effect(effect, self.transport, stop, self.brightness.get, speed)
            finally:
                self.running_effect = None

        self.show = {"type": "effet", "name": name}
        self.show_panel, self.live_params = panel, dict(raw)
        self._start(job)

    def stop_playback(self):
        self.stop_event.set()
        if self.play_thread is not None:
            # Attendre reellement la fin du thread precedent : deux threads
            # ne doivent jamais ecrire en meme temps sur le meme peripherique
            # (sinon ecritures HID concurrentes -> erreurs et ecran noir).
            self.play_thread.join(timeout=10.0)
            if self.play_thread.is_alive():
                self.status.config(text=_("Ancien thread bloqué, réessaie dans un instant"))
                return
        self.play_thread = None

    def current_show(self) -> dict | None:
        """Description JSON de ce qui s'affiche, avec les réglages du moment ; None si rien."""
        if self.show is None or self.play_thread is None or not self.play_thread.is_alive():
            return None
        show = dict(self.show, brightness=int(self.brightness.get()))
        if show["type"] == "gif":
            show["loop"] = bool(self.loop_var.get())
        elif show["type"] == "effet":
            show["params"] = dict(self.live_params)
            show["speed"] = float(self.show_panel["speed"].get())
        return show

    def stop_and_clear(self):
        self.show = None
        self.stop_playback()
        if self.play_thread is None:
            try:
                self.transport.write(bytes(PREFIX) + bytes(FRAME_SIZE - len(PREFIX)))
            except Exception:
                pass

    # --- Démarrage de session (services systemd --user) ---------------------
    def boot_mode(self) -> str:
        for label, service in BOOT_MODES.items():
            if service and systemctl("is-enabled", "--quiet", service) == 0:
                return label
        return "Rien"

    def set_boot_mode(self, label: str):
        wanted = BOOT_MODES[label]
        for service in SERVICES.values():
            systemctl("enable" if service == wanted else "disable", service)
        if wanted:
            mode = next(k for k, v in SERVICES.items() if v == wanted)
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            MODE_FILE.write_text(mode + "\n")
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
        def rappel(i, n, src, etat):
            etat = {"ok": _("converti"), "saute": _("déjà à jour")}.get(etat, etat.replace("erreur", _("erreur"), 1))
            self.after(0, lambda: self.status.config(text=_("Conversion {i}/{n} : {name} — {state}").format(
                i=i, n=n, name=src.name, state=etat)))

        def worker():
            produits = convertir_tout(chemins, None, False, rappel)

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
        """Relance le lanceur (langue ou interface changée) ; l'affichage en cours passe au fond puis revient."""
        show = self.current_show()
        self.stop_playback()
        self.transport.close()
        if show is not None:
            hand_off(show)
        os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])

    def change_language(self, code: str):
        """Enregistre la langue et relance le lanceur pour l'appliquer."""
        if code == LANG:
            return
        save_language(code)
        self.restart()

    def open_paint_editor(self):
        self.stop_playback()
        self.transport.close()
        stop_services()
        script = Path(__file__).parent / "rog_flare2_matrix_paint.py"
        subprocess.Popen([sys.executable, str(script)])
        self.destroy()

    def on_close(self):
        """Ce qui est affiché continue après la fermeture, par la lecture de fond."""
        show = self.current_show()
        self.stop_playback()
        self.transport.close()
        if show is not None:
            hand_off(show)
        self.destroy()


if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
