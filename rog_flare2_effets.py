#!/usr/bin/env python3
"""Effets de PolyWollyWin portés sous Linux pour l'AniMe Matrix.

Le moteur d'effets (polywollywin/effects.py, renderer.py) est repris tel quel
de https://github.com/MikeOpitz99/PolyWollyWin (licence MIT, voir
polywollywin/LICENSE et polywollywin/ORIGINE.md). Seules les parties Windows
sont remplacées ici :

- capture audio : le moteur passe par sounddevice/PortAudio et « Stereo Mix » ;
  sous Linux on lit le moniteur de la sortie par défaut avec `parec`
  (PipeWire/PulseAudio), sans PortAudio ;
- transport : les effets rendent 312 octets dans l'ordre matériel, on les
  envoie dans la trame 60 81 00 00 du dépôt (rog_flare2_matrix_paint).

    rog_flare2_effets.py --liste
    rog_flare2_effets.py "Plasma" [--brightness 60] [--vitesse 1.0]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "polywollywin"))
import effects as pww  # noqa: E402  (moteur PolyWollyWin)
from rog_flare2_matrix_paint import FB_OFFSET, FRAME_SIZE, PREFIX, FlareTransport  # noqa: E402

FPS = 30  # cadence de PolyWollyWin (TICK_HZ)
AUDIO_RATE = 44100
AUDIO_BLOCK = 2048


class LinuxAudioCapture:
    """Remplace _SharedAudioCapture : même interface get() -> (buf, last_audio_t, samplerate, mode)."""

    def __init__(self):
        self._lock = threading.Lock()
        self._buf: np.ndarray | None = None
        self._last_audio_t = 0.0
        self._mode = "demo"
        self._proc: subprocess.Popen | None = None
        self.source = ""

    @staticmethod
    def default_monitor() -> str:
        sink = subprocess.run(["pactl", "get-default-sink"], capture_output=True, text=True, timeout=5).stdout.strip()
        return f"{sink}.monitor" if sink else "@DEFAULT_MONITOR@"

    def start(self):
        if self._proc is not None:
            return
        try:
            self.source = self.default_monitor()
            self._proc = subprocess.Popen(
                ["parec", f"--device={self.source}", "--format=float32le", "--channels=1",
                 f"--rate={AUDIO_RATE}", "--latency-msec=40", "--raw"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"audio indisponible : {exc}", file=sys.stderr)
            self._proc = None
            return
        self._mode = "input"
        threading.Thread(target=self._read, args=(self._proc,), daemon=True).start()

    def _read(self, proc: subprocess.Popen):
        nbytes = AUDIO_BLOCK * 4
        while proc.poll() is None:
            chunk = proc.stdout.read(nbytes)
            if not chunk:
                break
            data = np.frombuffer(chunk[: len(chunk) // 4 * 4], dtype=np.float32)
            rms = float(np.sqrt(np.mean(data * data))) if data.size else 0.0
            with self._lock:
                self._buf = data.copy()
                if rms > 0.00002:
                    self._last_audio_t = time.monotonic()
        with self._lock:
            self._mode = "demo"

    def get(self):
        self.start()
        with self._lock:
            buf = None if self._buf is None else self._buf.copy()
            return buf, self._last_audio_t, AUDIO_RATE, self._mode

    def stop(self):
        proc, self._proc = self._proc, None
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        with self._lock:
            self._buf = None
            self._mode = "demo"


AUDIO = LinuxAudioCapture()
pww._SHARED_AUDIO_CAPTURE = AUDIO  # lu en global par les effets audio à chaque tick

EFFECTS: dict[str, type[pww.BaseEffect]] = {cls.name: cls for cls in pww.ALL_EFFECTS}
AUDIO_EFFECTS: dict[str, type[pww.BaseEffect]] = dict(pww.AUDIO_VISUALIZERS)


class KeyboardReactEffect(pww.KeyboardReactEffect):
    """Réaction au clavier : touches par rog_flare2_touches (evdev sous Wayland, pynput sous X11)."""

    def __init__(self, decay: float = 0.82, glow: int = 2):
        import rog_flare2_touches as touches
        # mêmes champs que PolyWollyWin, sans son écouteur pynput (aveugle sous Wayland)
        self.decay, self.glow = decay, glow
        self._buf = np.zeros((pww.ROWS, pww.COLS), dtype=np.float32)
        self._lock = threading.Lock()
        self._demo_t, self._caps = 0.0, False
        self._listener = touches.listen(self._press, self._release)
        self._demo = self._listener is None

    def _press(self, name: str):
        if name in ("shift", "caps_lock"):
            self._caps = True
            return
        bri, glow = (255, int(self.glow) + 2) if self._caps else (180, int(self.glow))
        if name == "space":
            self._flash_row(10, 28, bri, glow)
        elif name == "enter":
            self._flash_col(6, 35, bri, glow)
        elif name == "backspace":
            self._flash_col(2, 34, bri, glow)
        elif name in pww._KEY_POS:
            self._flash_point(*pww._KEY_POS[name], bri, glow)

    def _release(self, name: str):
        if name in ("shift", "caps_lock"):
            self._caps = False


EFFECTS[KeyboardReactEffect.name] = KeyboardReactEffect

from rog_flare2_texte import ScrollTextEffect, TextEffect  # noqa: E402  (texte, toutes écritures)
EFFECTS[ScrollTextEffect.name] = ScrollTextEffect
EFFECTS[TextEffect.name] = TextEffect
from rog_flare2_horloges import CLOCK_EFFECTS  # noqa: E402  (cadrans d'horloge)
for _clock in CLOCK_EFFECTS:
    EFFECTS[_clock.name] = _clock
from rog_flare2_infos import SystemMonitorEffect  # noqa: E402  (écran d'infos système)
EFFECTS[SystemMonitorEffect.name] = SystemMonitorEffect
from rog_flare2_mpris import NowPlayingEffect  # noqa: E402  (morceau en cours, MPRIS)
AUDIO_EFFECTS[NowPlayingEffect.name] = NowPlayingEffect
from rog_flare2_jeux import GAMES  # noqa: E402  (jeux jouables : touches transmises par le lanceur)
for _game in GAMES:
    EFFECTS[_game.name] = _game

# Extensions : tout fichier .py de ce dossier peut définir des effets (sous-classes de BaseEffect
# avec un attribut name). Voir docs/EXTENSIONS.md et examples/effets/.
PLUGIN_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "rog-flare2" / "effets"
PLUGIN_ERRORS: dict[str, str] = {}  # fichier -> erreur de chargement
PLUGIN_NAMES: dict[str, dict[str, str]] = {}  # nom interne -> noms traduits fournis par l'extension


def load_plugins(folder: Path = PLUGIN_DIR) -> list[str]:
    """Charge les extensions ; renvoie les noms des effets ajoutés. Une extension en erreur est ignorée."""
    import importlib.util
    added = []
    for path in sorted(folder.glob("*.py")) if folder.is_dir() else []:
        try:
            spec = importlib.util.spec_from_file_location(f"animematrix_ext_{path.stem}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as exc:  # code tiers : rien ne doit faire tomber le lanceur ni le démon
            PLUGIN_ERRORS[path.name] = f"{type(exc).__name__}: {exc}"
            continue
        for obj in vars(module).values():
            if (isinstance(obj, type) and issubclass(obj, pww.BaseEffect) and obj.__module__ == module.__name__
                    and getattr(obj, "name", "")):
                target = AUDIO_EFFECTS if issubclass(obj, pww.AudioVisualizer) else EFFECTS
                target[obj.name] = obj
                PLUGIN_NAMES[obj.name] = dict(getattr(obj, "noms", {}) or {})
                added.append(obj.name)
    return added


load_plugins()


def effect_class(name: str) -> type[pww.BaseEffect]:
    return EFFECTS.get(name) or AUDIO_EFFECTS[name]


def param_value(spec: dict, raw):
    """Valeur de curseur (entier) -> valeur d'attribut, comme app.py."""
    if spec.get("type") in ("text", "choice"):
        return str(raw)
    return float(raw) / float(spec.get("scale", 1.0))


def effect_label(name: str) -> str:
    """Nom affiché d'un effet : traduction du catalogue, ou noms fournis par l'extension."""
    from rog_flare2_i18n import LANG, _
    names = PLUGIN_NAMES.get(name)
    if names:
        return names.get(LANG) or names.get("en") or name
    return _(name)


def make_effect(name: str, raw_values: dict | None = None) -> pww.BaseEffect:
    cls = effect_class(name)
    effect = cls()
    for attr, raw in (raw_values or {}).items():
        spec = cls.PARAMS.get(attr)
        if spec is not None and hasattr(effect, attr):
            setattr(effect, attr, param_value(spec, raw))
    return effect


def led_frame(raw: list[int], brightness: int) -> bytes:
    scale = max(0, min(100, brightness)) / 100.0
    frame = bytearray(FRAME_SIZE)
    frame[0:2] = PREFIX
    frame[FB_OFFSET:FB_OFFSET + len(raw)] = bytes(max(0, min(255, int(v * scale))) for v in raw)
    return bytes(frame)


def run_effect(effect: pww.BaseEffect, transport, stop_event: threading.Event, brightness, speed=lambda: 1.0):
    """Anime effect jusqu'à stop_event ; brightness() et speed() relus à chaque image."""
    period = 1.0 / FPS
    last = time.monotonic()
    try:
        while not stop_event.is_set():
            now = time.monotonic()
            dt, last = now - last, now
            transport.write(led_frame(effect.tick(dt * speed()), brightness()))
            stop_event.wait(max(0.0, period - (time.monotonic() - now)))
    finally:
        effect.stop()
        if isinstance(effect, pww.AudioVisualizer):
            AUDIO.stop()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("effet", nargs="?")
    ap.add_argument("--liste", action="store_true")
    ap.add_argument("--brightness", type=int, default=60)
    ap.add_argument("--vitesse", type=float, default=1.0)
    args = ap.parse_args()
    if args.liste or not args.effet:
        print("Effets :", ", ".join(EFFECTS))
        print("Audio  :", ", ".join(AUDIO_EFFECTS))
        return
    transport = FlareTransport()
    transport.connect()
    try:
        run_effect(make_effect(args.effet), transport, threading.Event(),
                   lambda: args.brightness, lambda: args.vitesse)
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()


if __name__ == "__main__":
    main()
