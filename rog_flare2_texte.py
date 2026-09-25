"""Texte défilant dans toutes les écritures (latin accentué, cyrillique, grec, arabe, hindi, CJK…).

La police 4 × 7 de PolyWollyWin ne connaît que les majuscules ASCII : les autres
caractères devenaient des blancs (« ÉCHEC » s'affichait « CHEC »). Ici :
- lettres latines accentuées : accent retiré (É -> E), police 4 × 7 d'origine ;
- autres écritures : rendu par une police du système (fontconfig : fc-match), en
  niveaux de gris ; CJK, coréen, arabe, devanagari… sur toute la hauteur (12 rangées),
  les autres (cyrillique, grec…) à la hauteur de la police 4 × 7.

Le texte est rendu une fois en bande (12 × largeur), puis défile.
"""
from __future__ import annotations

import functools
import shutil
import subprocess
import unicodedata

import numpy as np

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "polywollywin"))
import effects as pww  # noqa: E402  (moteur PolyWollyWin, sans passer par rog_flare2_effets : import circulaire)

ROWS, COLS = pww.ROWS, pww.COLS
FONT = pww._CLOCK_FONT
CHAR_W, GAP, H = 4, 1, 7
TOP = max(0, (ROWS - H) // 2 - 1)  # rangée du haut de la police 4 × 7 (comme Scroll Text)
TALL_SCRIPTS = ("CJK", "HIRAGANA", "KATAKANA", "HANGUL", "ARABIC", "DEVANAGARI", "BENGALI", "THAI", "HEBREW",
                "TAMIL", "TELUGU", "GUJARATI", "GURMUKHI", "KANNADA", "MALAYALAM", "IDEOGRAPHIC", "FULLWIDTH")


def fold(ch: str) -> str:
    """Caractère de la police 4 × 7 : majuscule, accents retirés ; '' s'il n'y en a pas."""
    up = ch.upper()
    if up in FONT:
        return up
    base = "".join(c for c in unicodedata.normalize("NFD", up) if not unicodedata.combining(c))
    if base and all(c in FONT for c in base):
        return base
    return {"Œ": "OE", "Æ": "AE", "ß": "SS", "Ø": "O", "Ł": "L", "Đ": "D", "Ð": "D", "İ": "I", "ı": "I",
            "'": "", "’": "", "«": "<", "»": ">", ":": "-", ";": ",", "(": "", ")": "", "&": "+"}.get(up, "")


def tall(ch: str) -> bool:
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return False
    return unicodedata.east_asian_width(ch) in ("W", "F") or name.startswith(TALL_SCRIPTS)


@functools.lru_cache(maxsize=64)
def font_file(codepoint: int) -> str | None:
    """Fichier de police qui contient ce caractère (fontconfig)."""
    if not shutil.which("fc-match"):
        return None
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", f":charset={codepoint:x}"], capture_output=True,
                             text=True, timeout=3).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return out or None


def _render_run(run: str, height: int) -> np.ndarray:
    """Bande (height × largeur) d'une suite de caractères hors police 4 × 7, rendue par PIL."""
    from PIL import Image, ImageDraw, ImageFont
    path = font_file(ord(run[0]))
    if path is None:
        return np.zeros((height, 0), dtype=np.uint8)
    size = height + 2 if height > H else height + 3  # petite taille : on vise la hauteur des capitales
    try:
        font = ImageFont.truetype(path, size)
    except OSError:
        return np.zeros((height, 0), dtype=np.uint8)
    box = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), run, font=font)
    w, h = max(1, box[2] - box[0]), max(1, box[3] - box[1])
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).text((-box[0], -box[1]), run, font=font, fill=255)
    if h > height:  # trop haut : réduit en gardant les proportions
        img = img.resize((max(1, round(w * height / h)), height), Image.LANCZOS)
    band = np.zeros((height, img.width), dtype=np.float32)
    arr = np.asarray(img, dtype=np.float32)
    top = (height - arr.shape[0]) // 2
    band[top:top + arr.shape[0], :] = arr
    return np.clip(band * 1.6, 0, 255).astype(np.uint8)  # traits fins : renforcés pour les LED


def render(text: str) -> np.ndarray:
    """Bande ROWS × largeur du texte (niveaux 0-255)."""
    parts: list[np.ndarray] = []

    def column_block(width: int) -> np.ndarray:
        return np.zeros((ROWS, width), dtype=np.uint8)

    i = 0
    while i < len(text):
        folded = fold(text[i])
        if folded or text[i] == " ":
            for ch in folded or " ":
                block = column_block(CHAR_W + GAP)
                for ri, bits in enumerate(FONT.get(ch, FONT[" "])):
                    for bi in range(CHAR_W):
                        if (bits >> (CHAR_W - 1 - bi)) & 1:
                            block[TOP + ri, bi] = 255
                parts.append(block)
            i += 1
            continue
        j = i
        while j < len(text) and not fold(text[j]) and text[j] != " " and tall(text[j]) == tall(text[i]):
            j += 1
        if j == i:  # caractère sans équivalent ni police : ignoré
            i += 1
            continue
        run = text[i:j]
        height = ROWS if tall(run[0]) else H + 1
        band = _render_run(run, height)
        block = column_block(band.shape[1] + GAP)
        top = 0 if height == ROWS else TOP
        block[top:top + band.shape[0], :band.shape[1]] = band
        parts.append(block)
        i = j
    return np.concatenate(parts, axis=1) if parts else column_block(1)


class ScrollTextEffect(pww.ScrollTextEffect):
    """« Scroll Text » de PolyWollyWin, tout Unicode ; mêmes réglages (message, speed, loop_gap)."""

    def __init__(self, message: str = "POLYWOLLYWIN", speed: float = 1.0, loop_gap: int = 20):
        super().__init__(message, speed, loop_gap)
        self._cache = ("", render(" "))

    def band(self) -> np.ndarray:
        text = str(self.message) or " "
        if self._cache[0] != text:
            self._cache = (text, render(text))
        return self._cache[1]

    def tick(self, dt: float) -> list[int]:
        band = self.band()
        tw = band.shape[1]
        self._x -= dt * self.speed * 20.0  # 20 colonnes/s à la vitesse 1
        if self._x < -tw:
            self._x += tw + int(self.loop_gap) + COLS
        frame = np.zeros((ROWS, COLS), dtype=np.uint8)
        x = int(self._x)
        src0, dst0 = max(0, -x), max(0, x)
        width = min(tw - src0, COLS - dst0)
        if width > 0:
            frame[:, dst0:dst0 + width] = band[:, src0:src0 + width]
        return self._emit(frame)
