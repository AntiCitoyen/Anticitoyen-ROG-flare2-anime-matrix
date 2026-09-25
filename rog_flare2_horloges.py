"""Cadrans d'horloge : analogique, binaire, en mots (effets, choisis dans Réglages → Cadran).

- Analogique : dessiné sur la géométrie fidèle (19 × 24, proportions réelles) ;
- Binaire : heures, minutes, secondes en colonnes de 4 bits (DCB) ;
- En mots : « IL EST DIX HEURES VINGT », à 5 minutes près, en défilement ; français,
  anglais, allemand, espagnol, italien, portugais, néerlandais (anglais pour les autres langues).
"""
from __future__ import annotations

import datetime
import math

import numpy as np

from rog_flare2_core import CONFIG_DIR
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "polywollywin"))
import effects as pww  # noqa: E402  (moteur PolyWollyWin, sans passer par rog_flare2_effets : import circulaire)
from rog_flare2_matrix_paint import PHYSICAL_CALIBRATED_ORDER

ROWS, COLS = pww.ROWS, pww.COLS
FW, FH = 19, 24  # géométrie fidèle
ASPECT = 0.77  # écart vertical entre rangées / écart horizontal entre LED


def leds_from_faithful(pixels: np.ndarray) -> list[int]:
    """Image fidèle 24 × 19 (rangée, colonne) -> 312 valeurs dans l'ordre matériel."""
    return [int(pixels[row, min(FW - 1, (row + 1) // 2 + col)]) for row, col in PHYSICAL_CALIBRATED_ORDER]


class AnalogClockEffect(pww.BaseEffect):
    name = "Analog Clock"
    PARAMS = {"seconds": {"label": "Seconds", "min": 0, "max": 1, "default": 1, "scale": 1.0}}
    CENTER, RADIUS = (12.9, 9.0), 5.8  # plus grand cercle du coin (unités : écart entre LED)

    def __init__(self, seconds: float = 1):
        self.seconds = seconds

    def tick(self, dt: float) -> list[int]:
        from PIL import Image, ImageDraw
        k = 12  # suréchantillonnage
        w, h = FW * k, round(FH * ASPECT * k)
        img = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(img)
        cx, cy, r = self.CENTER[0] * k, self.CENTER[1] * k, self.RADIUS * k
        for i in range(12):  # graduations : 12, 3, 6, 9 appuyées
            a = math.radians(i * 30)
            x, y = cx + math.sin(a) * r, cy - math.cos(a) * r
            s = k * (0.55 if i % 3 == 0 else 0.35)
            d.ellipse((x - s, y - s, x + s, y + s), fill=255 if i % 3 == 0 else 110)
        now = datetime.datetime.now()
        hands = [((now.hour % 12 + now.minute / 60) * 30, 0.55, 0.95, 255),
                 ((now.minute + now.second / 60) * 6, 0.85, 0.7, 255)]
        for deg, length, width, level in hands:
            a = math.radians(deg)
            d.line((cx, cy, cx + math.sin(a) * r * length, cy - math.cos(a) * r * length), fill=level,
                   width=round(k * width))
        if int(self.seconds):
            a = math.radians(now.second * 6)
            x, y = cx + math.sin(a) * r, cy - math.cos(a) * r
            d.ellipse((x - k * 0.6, y - k * 0.6, x + k * 0.6, y + k * 0.6), fill=170)
        d.ellipse((cx - k * 0.6, cy - k * 0.6, cx + k * 0.6, cy + k * 0.6), fill=255)
        small = np.asarray(img.resize((FW, FH), Image.BOX), dtype=np.float32)
        return leds_from_faithful(np.clip(small * 1.8, 0, 255).astype(np.uint8))


class BinaryClockEffect(pww.BaseEffect):
    name = "Binary Clock"
    PARAMS = {"dim": {"label": "Off level", "min": 0, "max": 80, "default": 25, "scale": 1.0}}
    COL0 = 20  # colonne logique de départ : la rangée 10 commence à la colonne 20

    def __init__(self, dim: float = 25):
        self.dim = dim

    def tick(self, dt: float) -> list[int]:
        now = datetime.datetime.now()
        digits = [int(c) for c in now.strftime("%H%M%S")]
        frame = np.zeros((ROWS, COLS), dtype=np.uint8)
        for i, digit in enumerate(digits):
            col = self.COL0 + i * 3  # 6 colonnes de 2 LED, 20 à 36
            for bit in range(4):  # bit de poids faible en bas
                row = 9 - bit * 2
                frame[row:row + 2, col:col + 2] = 255 if digit >> bit & 1 else int(self.dim)
        return self._emit(frame)


# ---------------------------------------------------------------- en mots
HOURS = {
    "fr": ["MINUIT", "UNE", "DEUX", "TROIS", "QUATRE", "CINQ", "SIX", "SEPT", "HUIT", "NEUF", "DIX", "ONZE", "MIDI"],
    "en": ["TWELVE", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN",
           "TWELVE"],
    "de": ["ZWÖLF", "EINS", "ZWEI", "DREI", "VIER", "FÜNF", "SECHS", "SIEBEN", "ACHT", "NEUN", "ZEHN", "ELF",
           "ZWÖLF"],
    "es": ["DOCE", "UNA", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE", "DIEZ", "ONCE",
           "DOCE"],
    "it": ["DODICI", "UNA", "DUE", "TRE", "QUATTRO", "CINQUE", "SEI", "SETTE", "OTTO", "NOVE", "DIECI",
           "UNDICI", "DODICI"],
    "pt": ["DOZE", "UMA", "DUAS", "TRÊS", "QUATRO", "CINCO", "SEIS", "SETE", "OITO", "NOVE", "DEZ", "ONZE",
           "DOZE"],
    "nl": ["TWAALF", "ÉÉN", "TWEE", "DRIE", "VIER", "VIJF", "ZES", "ZEVEN", "ACHT", "NEGEN", "TIEN", "ELF",
           "TWAALF"],
}


def _h(lang: str, hour24: int) -> str:
    words = HOURS[lang]
    if lang == "fr":
        return words[hour24] if hour24 in (0, 12) else words[hour24 % 12]
    return words[hour24 % 12 or 12]


def words_for(lang: str, hour: int, minute: int) -> str:
    """Heure en mots, arrondie aux 5 minutes inférieures."""
    lang = lang if lang in HOURS else "en"
    m = minute // 5 * 5
    nxt = (hour + 1) % 24
    if lang == "fr":
        def hh(x):
            w = _h("fr", x)
            return w if x in (0, 12) else f"{w} HEURE" + ("" if x % 12 == 1 else "S")
        tail = {0: "", 5: " CINQ", 10: " DIX", 15: " ET QUART", 20: " VINGT", 25: " VINGT-CINQ", 30: " ET DEMIE",
                35: " MOINS VINGT-CINQ", 40: " MOINS VINGT", 45: " MOINS LE QUART", 50: " MOINS DIX",
                55: " MOINS CINQ"}[m]
        return f"IL EST {hh(hour if m <= 30 else nxt)}{tail}"
    if lang == "en":
        if m == 0:
            return f"IT IS {_h('en', hour)} O'CLOCK"
        word = {5: "FIVE", 10: "TEN", 15: "QUARTER", 20: "TWENTY", 25: "TWENTY-FIVE", 30: "HALF"}[min(m, 60 - m)]
        return f"IT IS {word} PAST {_h('en', hour)}" if m <= 30 else f"IT IS {word} TO {_h('en', nxt)}"
    if lang == "de":
        h, n = _h("de", hour), _h("de", nxt)
        if m == 0:
            return f"ES IST {'EIN' if h == 'EINS' else h} UHR"
        return "ES IST " + {5: f"FÜNF NACH {h}", 10: f"ZEHN NACH {h}", 15: f"VIERTEL NACH {h}",
                            20: f"ZWANZIG NACH {h}", 25: f"FÜNF VOR HALB {n}", 30: f"HALB {n}",
                            35: f"FÜNF NACH HALB {n}", 40: f"ZWANZIG VOR {n}", 45: f"VIERTEL VOR {n}",
                            50: f"ZEHN VOR {n}", 55: f"FÜNF VOR {n}"}[m]
    if lang == "es":
        def es(x):
            return f"ES LA {_h('es', x)}" if x % 12 == 1 else f"SON LAS {_h('es', x)}"
        tail = {0: " EN PUNTO", 5: " Y CINCO", 10: " Y DIEZ", 15: " Y CUARTO", 20: " Y VEINTE",
                25: " Y VEINTICINCO", 30: " Y MEDIA", 35: " MENOS VEINTICINCO", 40: " MENOS VEINTE",
                45: " MENOS CUARTO", 50: " MENOS DIEZ", 55: " MENOS CINCO"}[m]
        return es(hour if m <= 30 else nxt) + tail
    if lang == "it":
        def it(x):
            return "È L'UNA" if x % 12 == 1 else f"SONO LE {_h('it', x)}"
        tail = {0: "", 5: " E CINQUE", 10: " E DIECI", 15: " E UN QUARTO", 20: " E VENTI", 25: " E VENTICINQUE",
                30: " E MEZZA", 35: " MENO VENTICINQUE", 40: " MENO VENTI", 45: " MENO UN QUARTO",
                50: " MENO DIECI", 55: " MENO CINQUE"}[m]
        return it(hour if m <= 30 else nxt) + tail
    if lang == "pt":
        if m <= 30:
            h = _h("pt", hour)
            head = f"É {h}" if hour % 12 == 1 else f"SÃO {h}"
            if m == 0:
                return head + (" HORA" if hour % 12 == 1 else " HORAS")
            return head + {5: " E CINCO", 10: " E DEZ", 15: " E QUINZE", 20: " E VINTE", 25: " E VINTE E CINCO",
                           30: " E MEIA"}[m]
        n = _h("pt", nxt)
        return f"FALTAM {({35: 'VINTE E CINCO', 40: 'VINTE', 45: 'QUINZE', 50: 'DEZ', 55: 'CINCO'})[m]} " \
               f"PARA {'A' if nxt % 12 == 1 else 'AS'} {n}"
    h, n = _h("nl", hour), _h("nl", nxt)  # nl
    if m == 0:
        return f"HET IS {h} UUR"
    return "HET IS " + {5: f"VIJF OVER {h}", 10: f"TIEN OVER {h}", 15: f"KWART OVER {h}",
                        20: f"TIEN VOOR HALF {n}", 25: f"VIJF VOOR HALF {n}", 30: f"HALF {n}",
                        35: f"VIJF OVER HALF {n}", 40: f"TIEN OVER HALF {n}", 45: f"KWART VOOR {n}",
                        50: f"TIEN VOOR {n}", 55: f"VIJF VOOR {n}"}[m]


class WordClockEffect(pww.BaseEffect):
    name = "Word Clock"
    PARAMS = {"speed": {"label": "Speed", "min": 10, "max": 300, "default": 100, "scale": 100.0}}

    def __init__(self, speed: float = 1.0):
        from rog_flare2_i18n import LANG
        from rog_flare2_texte import ScrollTextEffect
        self.lang = LANG.split("-")[0]
        self.scroll = ScrollTextEffect(self._text(), speed, 12)

    def _text(self) -> str:
        now = datetime.datetime.now()
        return words_for(self.lang, now.hour, now.minute)

    @property
    def speed(self):
        return self.scroll.speed

    @speed.setter
    def speed(self, value):
        if hasattr(self, "scroll"):
            self.scroll.speed = value

    def tick(self, dt: float) -> list[int]:
        self.scroll.message = self._text()
        return self.scroll.tick(dt)


CLOCK_EFFECTS = [AnalogClockEffect, BinaryClockEffect, WordClockEffect]
FACES = {"numerique": None, "analogique": "Analog Clock", "binaire": "Binary Clock", "mots": "Word Clock",
         "stylisee": "Clock"}
FACE_LABELS = {"numerique": "Numérique", "analogique": "Analogique", "binaire": "Binaire", "mots": "En mots",
               "stylisee": "Stylisée"}
FACE_FILE = CONFIG_DIR / "cadran"


def saved_face() -> str:
    try:
        face = FACE_FILE.read_text().strip()
    except OSError:
        return "numerique"
    return face if face in FACES else "numerique"


def save_face(face: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    FACE_FILE.write_text(face + "\n")
