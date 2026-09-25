"""Conversion intelligente et géométrie fidèle (images de synthèse)."""
import shutil

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFilter

import rog_flare2_convertir as C
from rog_flare2_core import image_to_frame, iter_gif_frames
from rog_flare2_matrix_paint import FB_OFFSET, LED_COUNT, PHYSICAL_CALIBRATED_ORDER


def full_ratio(path, fidele=False):
    img, _ = next(iter(iter_gif_frames(path)))
    leds = image_to_frame(img, 100, fidele)[FB_OFFSET:FB_OFFSET + LED_COUNT]
    return sum(1 for v in leds if v > 200) / LED_COUNT


@pytest.fixture
def picto(tmp_path):
    im = Image.new("L", (600, 400), 255)
    d = ImageDraw.Draw(im)
    d.ellipse([250, 150, 350, 250], outline=0, width=4)
    d.line([300, 150, 300, 250], fill=0, width=4)
    im.save(tmp_path / "picto.png")
    return tmp_path / "picto.png"


def test_pictogram_on_white_is_not_a_flood(picto, tmp_path):
    C.convertir_intelligent(picto, tmp_path / "i.gif")
    assert 0.03 < full_ratio(tmp_path / "i.gif") < 0.4  # sujet clair sur fond noir, recadré
    if shutil.which("convert") or shutil.which("magick"):
        C.convertir(picto, tmp_path / "c.gif")
        assert full_ratio(tmp_path / "c.gif") > 0.8  # la chaîne classique inonde l'écran


def test_photo_gets_edges_not_flood(tmp_path):
    rng = np.random.default_rng(1)
    a = np.linspace(60, 200, 640)[None, :].repeat(480, 0) + rng.normal(0, 25, (480, 640))
    ph = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    ImageDraw.Draw(ph).ellipse([220, 120, 420, 420], fill=240)
    ph.filter(ImageFilter.GaussianBlur(2)).save(tmp_path / "photo.png")
    C.convertir_intelligent(tmp_path / "photo.png", tmp_path / "p.gif")
    assert full_ratio(tmp_path / "p.gif") < 0.5


def test_output_levels_and_duplicates(tmp_path):
    frames = [Image.new("L", (200, 120), 0) for _ in range(6)]
    for i, f in enumerate(frames[:3]):
        ImageDraw.Draw(f).rectangle([20 + i * 50, 40, 60 + i * 50, 80], fill=255)
    # les 3 dernières images sont identiques à la 3e : fusionnées
    for f in frames[3:]:
        ImageDraw.Draw(f).rectangle([120, 40, 160, 80], fill=255)
    frames[0].save(tmp_path / "a.gif", save_all=True, append_images=frames[1:], duration=40, loop=0)
    C.convertir_intelligent(tmp_path / "a.gif", tmp_path / "o.gif")
    with Image.open(tmp_path / "o.gif") as out:
        assert out.size == (19, 24) and out.n_frames == 3
        values = set(np.unique(np.asarray(out.convert("L"))))
        assert values <= {0, 64, 255}
        durations = []
        for k in range(out.n_frames):
            out.seek(k)
            durations.append(out.info["duration"])
        assert min(durations) >= 80 and durations[-1] >= 160  # durée des images fusionnées cumulée


def test_faithful_output_size(picto, tmp_path):
    C.convertir_intelligent(picto, tmp_path / "f.gif", fidele=True)
    with Image.open(tmp_path / "f.gif") as out:
        assert out.size == (19, 24)


def test_faithful_mapping_keeps_vertical_lines():
    im = Image.new("L", (19, 24), 0)
    ImageDraw.Draw(im).line([15, 0, 15, 23], fill=255)
    leds = image_to_frame(im, 100, fidele=True)[FB_OFFSET:FB_OFFSET + LED_COUNT]
    lit = {(row + 1) // 2 + col for (row, col), v in zip(PHYSICAL_CALIBRATED_ORDER, leds) if v > 128}
    assert lit == {15}  # même colonne réelle sur toutes les rangées
    assert sum(1 for v in leds if v > 128) == 24  # une LED par rangée
