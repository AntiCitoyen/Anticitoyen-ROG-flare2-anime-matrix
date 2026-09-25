#!/usr/bin/env python3
"""Génère les animations de départ de la bibliothèque (CC0) et catalogue.json.

Toutes en géométrie fidèle (19 × 24, la rangée r couvre les colonnes (r+1)//2 à 18),
3 niveaux (0, 64, 255), dessinées pour le coin de l'écran.

    python3 bibliotheque/generer.py
"""
import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
W, H = 19, 24
LOW, FULL = 64, 255


def visible(x, y):
    return 0 <= y < H and (y + 1) // 2 <= x < W


def canvas():
    return Image.new("L", (W, H), 0)


def put(img, x, y, v):
    if visible(int(x), int(y)):
        img.putpixel((int(x), int(y)), max(v, img.getpixel((int(x), int(y)))))


def heart(n=12):
    shape = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
    frames = []
    for k in range(n):
        img = canvas()
        beat = (math.exp(-((k / n - 0.1) / 0.06) ** 2) + 0.7 * math.exp(-((k / n - 0.3) / 0.06) ** 2))
        v = FULL if beat > 0.4 else LOW
        for r, row in enumerate(shape):
            for c, ch in enumerate(row):
                if ch == "X":
                    put(img, 10 + c, 5 + r * 2, v)
                    put(img, 10 + c, 6 + r * 2, v)
        frames.append(img)
    return frames, 90


def rain(n=24):
    rng = random.Random(7)
    drops = [[rng.randrange(W), rng.randrange(H), rng.choice((1, 2))] for _ in range(14)]
    frames = []
    for _ in range(n):
        img = canvas()
        for d in drops:
            put(img, d[0], d[1], FULL)
            put(img, d[0], d[1] - 1, LOW)
            d[1] = (d[1] + d[2]) % (H + 2)
        frames.append(img)
    return frames, 80


def wave(n=20):
    frames = []
    for k in range(n):
        img = canvas()
        for x in range(W):
            y = 12 + 5 * math.sin((x + k) * 2 * math.pi / 12)
            put(img, x, y, FULL)
            put(img, x, y + 1, LOW)
        frames.append(img)
    return frames, 80


def spinner(n=8):
    frames = []
    cx, cy, r = 13, 12, 4
    for k in range(n):
        img = canvas()
        for i in range(n):
            a = 2 * math.pi * i / n
            put(img, cx + r * math.cos(a), cy + r * 1.3 * math.sin(a), FULL if i == k else LOW if (k - i) % n < 3 else 0)
        frames.append(img)
    return frames, 100


def equalizer(n=16):
    rng = random.Random(3)
    frames = []
    heights = [rng.randint(2, 12) for _ in range(5)]
    for _ in range(n):
        img = canvas()
        heights = [max(2, min(20, h + rng.randint(-4, 4))) for h in heights]
        for i, h in enumerate(heights):
            x = 9 + i * 2
            for y in range(H - h, H):
                put(img, x, y, FULL if y > H - h + 1 else LOW)
        frames.append(img)
    return frames, 90


def snow(n=30):
    rng = random.Random(11)
    flakes = [[rng.uniform(0, W), rng.uniform(0, H)] for _ in range(18)]
    frames = []
    for k in range(n):
        img = canvas()
        for f in flakes:
            put(img, f[0], f[1], FULL if int(f[0] * 7 + k) % 5 else LOW)
            f[1] = (f[1] + 0.5) % H
            f[0] = (f[0] + 0.3 * math.sin((f[1] + k) / 3)) % W
        frames.append(img)
    return frames, 110


def twinkle(n=20):
    rng = random.Random(5)
    stars = [(rng.randrange(W), rng.randrange(H), rng.random() * 6.28) for _ in range(24)]
    frames = []
    for k in range(n):
        img = canvas()
        for x, y, ph in stars:
            s = math.sin(k * 6.28 / n + ph)
            put(img, x, y, FULL if s > 0.6 else LOW if s > -0.2 else 0)
        frames.append(img)
    return frames, 100


def chevrons(n=6):
    frames = []
    for k in range(n):
        img = canvas()
        for base in range(-6, W + 6, 6):
            x0 = base + k
            for dy in range(0, 5):
                put(img, x0 + dy, 7 + dy, FULL)
                put(img, x0 + dy, 17 - dy, FULL)
        frames.append(img)
    return frames, 90


def eye(n=24):
    frames = []
    for k in range(n):
        img = canvas()
        open_ = not (k in (10, 11, 20))
        cx, cy = 13, 11
        for a in range(0, 360, 12):
            t = math.radians(a)
            put(img, cx + 5 * math.cos(t), cy + (4 if open_ else 0.5) * math.sin(t), LOW)
        if open_:
            px = cx + (2 if 4 <= k < 9 else -2 if 13 <= k < 18 else 0)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    put(img, px + dx, cy + dy, FULL)
        frames.append(img)
    return frames, 120


def pulse_ring(n=12):
    frames = []
    cx, cy = 13, 12
    for k in range(n):
        img = canvas()
        for r, v in ((k % n * 0.8, FULL), ((k - 3) % n * 0.8, LOW)):
            for a in range(0, 360, 8):
                t = math.radians(a)
                put(img, cx + r * math.cos(t), cy + r * 1.3 * math.sin(t), v)
        frames.append(img)
    return frames, 90


ENTRIES = [
    ("coeur", heart, "Cœur qui bat", "Heartbeat", ["amour", "love"]),
    ("pluie", rain, "Pluie", "Rain", ["météo", "weather"]),
    ("vague", wave, "Vague", "Wave", ["mer", "sea"]),
    ("chargement", spinner, "Chargement", "Loading", ["attente", "loading"]),
    ("egaliseur", equalizer, "Égaliseur", "Equalizer", ["musique", "music"]),
    ("neige", snow, "Neige", "Snow", ["hiver", "winter"]),
    ("etoiles", twinkle, "Étoiles", "Stars", ["nuit", "night"]),
    ("chevrons", chevrons, "Chevrons", "Chevrons", ["défilement", "scroll"]),
    ("oeil", eye, "Œil", "Eye", ["visage", "face"]),
    ("onde", pulse_ring, "Onde", "Ripple", ["cercle", "ring"]),
]


def main():
    catalogue = {"version": 1, "animations": []}
    for key, fn, fr, en, tags in ENTRIES:
        frames, duration = fn()
        path = HERE / "gif" / f"{key}.gif"
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=1,
                       comment=b"animematrix:fidele")  # lu par la lecture : géométrie fidèle
        catalogue["animations"].append({
            "id": key, "noms": {"fr": fr, "en": en}, "auteur": "AntiCitoyen", "licence": "CC0-1.0",
            "fichier": f"gif/{key}.gif", "fidele": True, "etiquettes": tags,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    (HERE / "catalogue.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(catalogue["animations"]), "animations")


if __name__ == "__main__":
    main()
