"""Écran d'infos pour l'AniMe Matrix : CPU, RAM, GPU, température, réseau, heure.

Effet « System Monitor » (moteur PolyWollyWin) : une page par mesure, étiquette
et valeur en police 4×7 en haut du coin, jauge de 15 LED en bas. Les mesures sont
lues sans dépendance (/proc, /sys, nvidia-smi en lecture seule) par un fil
d'échantillonnage, une fois par seconde, pour ne jamais ralentir l'animation.
"""
from __future__ import annotations

import datetime
import shutil
import subprocess
import threading
import time
from pathlib import Path

import numpy as np

from effects import _CLOCK_FONT, COLS, ROWS, BaseEffect

TEXT_COL = 12  # première colonne où les 7 rangées du texte existent (rangée 6 : colonnes 12 à 36)
GAUGE = (9, 22, 15)  # rangée de départ, colonne, longueur : rangées 9-11 ont toutes les colonnes 22-36
PAGES = ["cpu", "ram", "gpu", "temp", "net", "heure"]


class Sampler:
    """Mesures système, rafraîchies en arrière-plan (une seule instance partagée)."""

    def __init__(self):
        self.values: dict[str, float | None] = {p: None for p in PAGES}
        self._cpu = None
        self._net = None
        self._started = False
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._started:
                return
            self._started = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        n = 0
        while True:
            self.values["cpu"] = self._cpu_percent()
            self.values["ram"] = self._ram_percent()
            self.values["temp"] = self._cpu_temp()
            self.values["net"] = self._net_mbps()
            if n % 2 == 0:
                self.values["gpu"] = self._gpu_percent()
            n += 1
            time.sleep(1)

    def _cpu_percent(self):
        f = Path("/proc/stat").read_text().split("\n", 1)[0].split()[1:]
        vals = list(map(int, f))
        idle, total = vals[3] + vals[4], sum(vals)
        prev, self._cpu = self._cpu, (idle, total)
        if not prev or total == prev[1]:
            return None
        return 100 * (1 - (idle - prev[0]) / (total - prev[1]))

    @staticmethod
    def _ram_percent():
        info = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1)
            info[k] = int(v.split()[0])
        return 100 * (1 - info["MemAvailable"] / info["MemTotal"])

    @staticmethod
    def _cpu_temp():
        for hw in Path("/sys/class/hwmon").glob("hwmon*"):
            try:
                if (hw / "name").read_text().strip() in ("k10temp", "coretemp", "zenpower", "cpu_thermal"):
                    return int((hw / "temp1_input").read_text()) / 1000
            except OSError:
                continue
        return None

    def _net_mbps(self):
        rx = tx = 0
        for line in Path("/proc/net/dev").read_text().splitlines()[2:]:
            name, data = line.split(":", 1)
            if name.strip() == "lo":
                continue
            f = data.split()
            rx, tx = rx + int(f[0]), tx + int(f[8])
        now = time.monotonic()
        prev, self._net = self._net, (now, rx + tx)
        if not prev:
            return None
        return (rx + tx - prev[1]) / (now - prev[0]) / 1e6

    @staticmethod
    def _gpu_percent():
        """Charge du GPU : NVIDIA (nvidia-smi, lecture seule) ou AMD (gpu_busy_percent)."""
        if shutil.which("nvidia-smi"):
            try:
                out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                                     capture_output=True, text=True, timeout=3).stdout
                return float(out.split()[0])
            except (OSError, ValueError, IndexError, subprocess.SubprocessError):
                return None
        for busy in Path("/sys/class/drm").glob("card*/device/gpu_busy_percent"):
            try:
                return float(busy.read_text())
            except (OSError, ValueError):
                continue
        return None


SAMPLER = Sampler()


def draw_text(frame: np.ndarray, text: str, col: int, level: float, row: int = 0) -> int:
    """Écrit text (police 4×7) à partir de col ; renvoie la colonne suivante."""
    for ch in text.upper():
        glyph = _CLOCK_FONT.get(ch, _CLOCK_FONT[" "])
        for r, bits in enumerate(glyph):
            for c in range(4):
                if bits & (1 << (3 - c)) and 0 <= col + c < COLS and row + r < ROWS:
                    frame[row + r, col + c] = level
        col += 5
    return col


class SystemMonitorEffect(BaseEffect):
    name = "System Monitor"
    PARAMS = {
        "page": {"label": "Page (0 = auto)", "min": 0, "max": len(PAGES), "default": 0, "scale": 1.0},
        "period": {"label": "Period", "min": 2, "max": 20, "default": 5, "scale": 1.0},
    }
    LABELS = {"cpu": "CPU", "ram": "RAM", "gpu": "GPU", "temp": "TMP", "net": "NET"}

    def __init__(self, page: float = 0, period: float = 5):
        self.page, self.period = page, period
        self._t = 0.0
        SAMPLER.start()

    def _pages(self) -> list[str]:
        """Pages disponibles sur cette machine (sans GPU ni capteur : pages masquées)."""
        return [p for p in PAGES if p == "heure" or SAMPLER.values.get(p) is not None]

    def tick(self, dt: float) -> list[int]:
        self._t += dt
        pages = self._pages() or ["heure"]
        fixed = int(self.page)
        page = PAGES[fixed - 1] if fixed else pages[int(self._t // max(1, self.period)) % len(pages)]
        frame = np.zeros((ROWS, COLS), dtype=np.float32)
        if page == "heure":
            draw_text(frame, datetime.datetime.now().strftime("%H%M"), TEXT_COL + 3, 255)
            if int(self._t * 2) % 2 == 0:  # deux-points clignotants entre les heures et les minutes
                frame[2, TEXT_COL + 12] = frame[4, TEXT_COL + 12] = 255
            return self._emit(frame)
        value = SAMPLER.values.get(page)
        if value is None:
            draw_text(frame, self.LABELS[page], TEXT_COL, 110)
            draw_text(frame, "--", TEXT_COL + 15, 255)
            return self._emit(frame)
        shown = f"{min(99, round(value)):2d}"
        draw_text(frame, self.LABELS[page], TEXT_COL, 110)  # étiquette atténuée, valeur pleine
        draw_text(frame, shown, TEXT_COL + 15, 255)
        full = 100 if page in ("cpu", "ram", "gpu") else 90 if page == "temp" else 100
        ratio = value / full if page != "net" else min(1.0, np.log10(1 + value) / 2)  # réseau : 1 → 100 Mo/s
        row, col, length = GAUGE
        lit = round(max(0.0, min(1.0, ratio)) * length)
        frame[row:row + 3, col:col + length] = 35
        frame[row:row + 3, col:col + lit] = 255
        return self._emit(frame)
