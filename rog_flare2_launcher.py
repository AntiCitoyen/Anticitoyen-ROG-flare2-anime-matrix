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
VERSION = "1.0.0"
PROJECT_URL = "https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix"
SUPPORT_URL = "https://buymeacoffee.com/anticitoyen"
# Services de fond (rog_flare2_bascule.sh) ; un seul peut tenir le HID.
SERVICES = {"gif": "animematrix-galerie.service", "horloge": "animematrix-horloge.service"}
BOOT_MODES = {"Galerie GIF": SERVICES["gif"], "Horloge": SERVICES["horloge"], "Rien": None}
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "rog-flare2"
MODE_FILE = CONFIG_DIR / "mode"
GALLERY_FILE = CONFIG_DIR / "galerie"  # dossier lu par la galerie (lanceur et service)


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
    return active


class LauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AniMe Matrix - ROG Strix Flare II Animate")
        self.resizable(False, False)

        self.transport = FlareTransport()
        self.play_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.gif_files: list[Path] = []
        self.suspended: list[str] = []
        self._pending_status: str | None = None
        self.running_effect = None

        ttk.Label(self, text="AniMe Matrix", font=("Sans", 16, "bold")).pack(pady=(16, 4))
        ttk.Label(self, text="ROG Strix Flare II Animate").pack(pady=(0, 8))

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=12, pady=4)
        self._build_gif_tab(tabs)
        self.effect_panel = self._build_effect_tab(tabs, "Effets", list(EFFECTS), "Plasma")
        self.audio_panel = self._build_effect_tab(tabs, "Audio", list(AUDIO_EFFECTS), "Spectrum Bars")
        self._build_settings_tab(tabs)

        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=24, pady=(10, 4))
        ttk.Label(frm, text="Luminosité :").pack(side="left")
        self.brightness = tk.IntVar(value=60)
        ttk.Scale(frm, from_=5, to=100, variable=self.brightness, orient="horizontal").pack(
            side="left", fill="x", expand=True, padx=8)

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=24, pady=4)
        ttk.Button(btns, text="🕒 Horloge", command=self.start_clock).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(btns, text="■ Arrêter", command=self.stop_and_clear).pack(
            side="left", expand=True, fill="x", padx=(4, 0))

        self.status = ttk.Label(self, text="", foreground="gray")
        self.status.pack(pady=(8, 12))

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._poll_status()

        if Image is None:
            messagebox.showwarning(
                "Pillow manquant",
                "Le module Pillow n'est pas installé dans cet environnement.\n"
                "La lecture de GIF/images sera indisponible."
            )
        elif gallery_dir().is_dir():
            self.set_files(media_files(gallery_dir()), gallery_dir().name)

    def _build_gif_tab(self, tabs: ttk.Notebook):
        tab = ttk.Frame(tabs, padding=12)
        tabs.add(tab, text="GIF / images")
        src = ttk.Frame(tab)
        src.pack(fill="x", pady=4)
        ttk.Button(src, text="GIF/images…", command=self.choose_files).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(src, text="Dossier (galerie)…", command=self.choose_folder).pack(
            side="left", expand=True, fill="x", padx=(4, 0))

        self.loop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="Boucler / enchaîner les fichiers", variable=self.loop_var).pack(anchor="w")
        self.converted_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="Préférer les versions converties (matrix/)",
                        variable=self.converted_var).pack(anchor="w")
        self.play_btn = ttk.Button(tab, text="▶ Lancer les GIF", command=self.start_playback, state="disabled")
        self.play_btn.pack(fill="x", pady=(8, 4))

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(tab, text="Convertir pour la matrice (19×24, gris, 3 niveaux, sans tramage)").pack()
        conv = ttk.Frame(tab)
        conv.pack(fill="x", pady=(4, 0))
        ttk.Button(conv, text="Convertir des GIF…", command=self.convert_files).pack(
            side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(conv, text="Convertir un dossier…", command=self.convert_folder).pack(
            side="left", expand=True, fill="x", padx=(4, 0))

    def _build_effect_tab(self, tabs: ttk.Notebook, title: str, names: list[str], default: str) -> dict:
        """Onglet d'effets PolyWollyWin : choix, réglages de l'effet (PARAMS), vitesse, lancement."""
        tab = ttk.Frame(tabs, padding=12)
        tabs.add(tab, text=title)
        panel = {"name": tk.StringVar(value=default), "values": {}, "speed": tk.DoubleVar(value=1.0)}
        cb = ttk.Combobox(tab, textvariable=panel["name"], values=names, state="readonly")
        cb.pack(fill="x", pady=(0, 8))
        panel["params"] = ttk.Frame(tab)
        panel["params"].pack(fill="x")
        spd = ttk.Frame(tab)
        spd.pack(fill="x", pady=(8, 0))
        ttk.Label(spd, text="Vitesse", width=14).pack(side="left")
        ttk.Scale(spd, from_=0.2, to=3.0, variable=panel["speed"], orient="horizontal").pack(
            side="left", fill="x", expand=True)
        if title == "Audio":
            ttk.Label(tab, text="Source : moniteur de la sortie son par défaut (parec)",
                      foreground="gray").pack(anchor="w", pady=(6, 0))
        ttk.Button(tab, text="▶ Lancer l'effet", command=lambda: self.start_effect(panel)).pack(
            fill="x", pady=(10, 0))
        ttk.Label(tab, text="Effets : PolyWollyWin (MIT, Mike Opitz)", foreground="gray").pack(pady=(6, 0))
        cb.bind("<<ComboboxSelected>>", lambda _e: self._fill_params(panel))
        self._fill_params(panel)
        return panel

    def _fill_params(self, panel: dict):
        for w in panel["params"].winfo_children():
            w.destroy()
        panel["values"] = {}
        for attr, spec in effect_class(panel["name"].get()).PARAMS.items():
            row = ttk.Frame(panel["params"])
            row.pack(fill="x", pady=1)
            ttk.Label(row, text=spec.get("label", attr), width=14).pack(side="left")
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

    def _apply_param(self, attr: str, spec: dict, var: tk.Variable):
        """Réglage appliqué en direct à l'effet en cours s'il possède cet attribut."""
        effect = self.running_effect
        if effect is not None and attr in type(effect).PARAMS:
            try:
                setattr(effect, attr, param_value(spec, var.get()))
            except (tk.TclError, ValueError):
                pass

    def _build_settings_tab(self, tabs: ttk.Notebook):
        tab = ttk.Frame(tabs, padding=12)
        tabs.add(tab, text="Réglages")
        boot = ttk.Frame(tab)
        boot.pack(fill="x", pady=4)
        ttk.Label(boot, text="Au démarrage de session :").pack(side="left")
        self.boot_var = tk.StringVar(value=self.boot_mode())
        cb = ttk.Combobox(boot, textvariable=self.boot_var, values=list(BOOT_MODES), state="readonly", width=12)
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", lambda _e: self.set_boot_mode(self.boot_var.get()))
        ttk.Label(tab, text="La galerie de fond lit le dernier dossier choisi dans l'onglet GIF.",
                  foreground="gray").pack(anchor="w")
        ttk.Button(tab, text="✎ Dessiner mon propre motif (éditeur)",
                   command=self.open_paint_editor).pack(fill="x", pady=(12, 0))

        ttk.Separator(tab, orient="horizontal").pack(fill="x", pady=12)
        ttk.Label(tab, text=f"AniMe Matrix pour Linux {VERSION}").pack()
        ttk.Button(tab, text="☕ Soutenir le projet (Buy Me a Coffee)",
                   command=lambda: webbrowser.open(SUPPORT_URL)).pack(fill="x", pady=(8, 4))
        ttk.Button(tab, text="Page du projet (GitHub)",
                   command=lambda: webbrowser.open(PROJECT_URL)).pack(fill="x")

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
        self.status.config(text=f"{len(files)} fichier(s) : {label}")
        self.play_btn.config(state="normal" if files and Image is not None else "disabled")

    def choose_files(self):
        try:
            result = subprocess.run(
                [
                    "zenity", "--file-selection", "--multiple", "--separator=\n",
                    "--title=Choisir un ou plusieurs GIF/images",
                    "--file-filter=Images et GIF | *.gif *.png *.jpg *.jpeg *.bmp *.webp",
                    "--file-filter=Tous les fichiers | *",
                ],
                capture_output=True, text=True, timeout=300,
            )
            paths = [p for p in result.stdout.strip().split("\n") if p]
        except (FileNotFoundError, subprocess.SubprocessError):
            paths = filedialog.askopenfilenames(
                title="Choisir un ou plusieurs GIF/images",
                filetypes=[("Images et GIF", "*.gif *.png *.jpg *.jpeg *.bmp *.webp"), ("Tous les fichiers", "*.*")],
            )
        if paths:
            self.set_files([Path(p) for p in paths], "sélection")

    def choose_folder(self):
        try:
            result = subprocess.run(
                ["zenity", "--file-selection", "--directory", "--title=Dossier de GIF à lire en galerie",
                 f"--filename={gallery_dir()}/"],
                capture_output=True, text=True, timeout=300)
            path = result.stdout.strip()
        except (FileNotFoundError, subprocess.SubprocessError):
            path = filedialog.askdirectory(title="Dossier de GIF à lire en galerie", initialdir=gallery_dir())
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
        for s in stop_services():
            if s not in self.suspended:
                self.suspended.append(s)
        self.stop_event = threading.Event()
        stop = self.stop_event

        def worker():
            try:
                self.transport.connect()
                job(stop)
            except Exception as exc:
                self.set_status(f"Erreur : {exc}")
                return
            self.set_status("Arrêté")

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
                    self.set_status(f"Lecture : {src.name}")
                    try:
                        play_file(src, self.transport, stop, self.brightness.get)
                    except OSError as exc:
                        self.set_status(f"Sauté {src.name} : {exc}")
                if not loop():
                    break

        self._start(job)

    def start_clock(self):
        def job(stop):
            self.set_status("Horloge")
            play_clock(self.transport, stop, self.brightness.get)

        self._start(job)

    def start_effect(self, panel: dict):
        name = panel["name"].get()
        raw = {a: v.get() for a, v in panel["values"].items()}
        speed = panel["speed"].get

        def job(stop):
            effect = make_effect(name, raw)
            self.running_effect = effect
            self.set_status(f"Effet : {name}")
            try:
                run_effect(effect, self.transport, stop, self.brightness.get, speed)
            finally:
                self.running_effect = None

        self._start(job)

    def stop_playback(self):
        self.stop_event.set()
        if self.play_thread is not None:
            # Attendre reellement la fin du thread precedent : deux threads
            # ne doivent jamais ecrire en meme temps sur le meme peripherique
            # (sinon ecritures HID concurrentes -> erreurs et ecran noir).
            self.play_thread.join(timeout=10.0)
            if self.play_thread.is_alive():
                self.status.config(text="Ancien thread bloqué, réessaie dans un instant")
                return
        self.play_thread = None

    def stop_and_clear(self):
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
        self.status.config(text=f"Au démarrage : {label}")

    # --- Conversion ImageMagick (rog_flare2_convertir.py) -------------------
    def convert_files(self):
        try:
            result = subprocess.run(
                ["zenity", "--file-selection", "--multiple", "--separator=\n",
                 "--title=GIF/images à convertir pour la matrice",
                 "--file-filter=Images et GIF | *.gif *.png *.jpg *.jpeg *.bmp *.webp",
                 "--file-filter=Tous les fichiers | *"],
                capture_output=True, text=True, timeout=300)
            paths = [p for p in result.stdout.strip().split("\n") if p]
        except (FileNotFoundError, subprocess.SubprocessError):
            paths = filedialog.askopenfilenames(
                title="GIF/images à convertir pour la matrice",
                filetypes=[("Images et GIF", "*.gif *.png *.jpg *.jpeg *.bmp *.webp"), ("Tous les fichiers", "*.*")])
        if paths:
            self._convert([Path(p) for p in paths])

    def convert_folder(self):
        try:
            result = subprocess.run(
                ["zenity", "--file-selection", "--directory", "--title=Dossier de GIF à convertir"],
                capture_output=True, text=True, timeout=300)
            path = result.stdout.strip()
        except (FileNotFoundError, subprocess.SubprocessError):
            path = filedialog.askdirectory(title="Dossier de GIF à convertir")
        if path:
            self._convert([Path(path)])

    def _convert(self, chemins: list[Path]):
        """Conversion dans un fil ; sortie dans <dossier>/matrix/ ; propose ensuite de charger le résultat."""
        def rappel(i, n, src, etat):
            self.after(0, lambda: self.status.config(text=f"Conversion {i}/{n} : {src.name} — {etat}"))

        def worker():
            produits = convertir_tout(chemins, None, False, rappel)

            def fin():
                if not produits:
                    self.status.config(text="Conversion : aucun fichier produit")
                    return
                dossier = produits[0].parent
                self.status.config(text=f"{len(produits)} GIF prêt(s) dans {dossier}")
                if messagebox.askyesno("Conversion terminée",
                                       f"{len(produits)} GIF convertis dans\n{dossier}\n\nLes charger pour lecture ?"):
                    self.gif_files = list(produits)
                    self.play_btn.config(state="normal" if Image is not None else "disabled")
            self.after(0, fin)

        self.status.config(text="Conversion en cours…")
        threading.Thread(target=worker, daemon=True).start()


    def resume_services(self):
        """Rend l'écran au service du démarrage de session s'il a été arrêté par le lanceur."""
        wanted = BOOT_MODES[self.boot_mode()]
        if self.suspended and wanted:
            systemctl("start", wanted)
        self.suspended = []

    def open_paint_editor(self):
        self.stop_playback()
        self.transport.close()
        stop_services()
        script = Path(__file__).parent / "rog_flare2_matrix_paint.py"
        subprocess.Popen([sys.executable, str(script)])
        self.destroy()

    def on_close(self):
        self.stop_playback()
        self.transport.close()
        self.resume_services()
        self.destroy()


if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
