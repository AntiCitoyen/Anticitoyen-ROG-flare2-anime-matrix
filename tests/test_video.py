"""Vidéo (ffmpeg), miroir d'écran X11 (Xvfb) et contraste."""
import os
import shutil
import subprocess
import threading

import numpy as np
import pytest

import rog_flare2_core as core
import rog_flare2_video as V

pytestmark = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg requis")


class Sink:
    def __init__(self, stop=None, limit=None):
        self.frames, self.stop, self.limit = [], stop, limit

    def write(self, frame):
        self.frames.append(frame)
        if self.limit and len(self.frames) >= self.limit:
            self.stop.set()
        return len(frame)


@pytest.fixture
def clip(tmp_path):
    path = tmp_path / "mire.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                    "testsrc=size=320x240:rate=25:duration=1", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


def test_video_in_gallery_plays_through_ffmpeg(clip):
    assert clip.suffix in core.MEDIA_EXTENSIONS and core.media_files(clip.parent) == [clip]
    sink = Sink()
    core.play_file(clip, sink, threading.Event(), lambda: 100)
    assert 15 <= len(sink.frames) <= 25  # 1 s à 20 images/s
    assert all(len(f) == 1024 and f[:2] == bytes([0x60, 0x81]) for f in sink.frames)
    assert max(sink.frames[5][4:316]) > 200  # contraste étiré


def test_preview_frames(clip):
    frames = V.preview_frames(clip, seconds=0.5)
    assert 8 <= len(frames) <= 12 and all(len(f) == 1024 for f, _d in frames)


def test_contrast_and_silhouette():
    gray = np.tile(np.arange(100, 119, dtype=np.uint8), (24, 1))  # image terne
    out = V.Contrast()(gray)
    assert out.max() - out.min() > gray.max() - gray.min()
    sil = V.Contrast(silhouette=True)(gray)
    assert set(np.unique(sil)) <= {0, 255}


def test_screen_mirror_x11():
    if not os.environ.get("DISPLAY"):
        pytest.skip("affichage X requis")
    stop = threading.Event()
    sink = Sink(stop, limit=5)
    t = threading.Thread(target=V.play_screen, args=(sink, stop, lambda: 100), daemon=True)
    t.start()
    t.join(timeout=20)
    stop.set()
    assert len(sink.frames) >= 5


def test_missing_webcam_raises():
    with pytest.raises(OSError):
        V.play_webcam(Sink(), threading.Event(), lambda: 100, device="/dev/video-absente")


def test_shrink_keeps_center():
    img = np.zeros((90, 160), dtype=np.uint8)
    img[:, 70:90] = 255  # bande verticale au centre
    out = np.frombuffer(V.shrink(img.tobytes(), 160, 90), dtype=np.uint8).reshape(V.H, V.W)
    assert out[:, 9].mean() > 100 and out[:, 0].mean() < 20
