"""Lecture GIF en flux, trames, choix des versions converties."""
import os
import threading
import time

from PIL import Image

import rog_flare2_core as core
from rog_flare2_matrix_paint import FB_OFFSET, FRAME_SIZE, LED_COUNT, PREFIX


class Sink:
    def __init__(self):
        self.frames = []

    def write(self, frame):
        self.frames.append(frame)
        return len(frame)


def make_gif(path, n=5, size=(40, 30)):
    frames = [Image.new("L", size, 40 * i) for i in range(n)]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=20, loop=0)
    return path


def test_image_to_frame_format():
    frame = core.image_to_frame(Image.new("L", (19, 24), 255), brightness=50)
    assert len(frame) == FRAME_SIZE and frame[:2] == bytes(PREFIX)
    leds = frame[FB_OFFSET:FB_OFFSET + LED_COUNT]
    assert set(leds) == {127}  # 255 × 50 %
    assert not any(frame[FB_OFFSET + LED_COUNT:])


def test_iter_gif_frames_streams_every_frame(tmp_path):
    gif = make_gif(tmp_path / "a.gif", n=7)
    frames = list(core.iter_gif_frames(gif))
    assert len(frames) == 7
    assert all(delay >= 0.02 for _img, delay in frames)


def test_play_file_writes_one_frame_per_gif_frame(tmp_path):
    gif = make_gif(tmp_path / "a.gif", n=4)
    sink = Sink()
    core.play_file(gif, sink, threading.Event(), lambda: 60)
    assert len(sink.frames) == 4 and all(len(f) == FRAME_SIZE for f in sink.frames)


def test_pick_version_prefers_newer_converted(tmp_path):
    src = make_gif(tmp_path / "chat.gif")
    assert core.pick_version(src) == src
    (tmp_path / "matrix").mkdir()
    conv = make_gif(tmp_path / "matrix" / "chat.gif")
    assert core.pick_version(src) == conv
    old = time.time() - 3600
    os.utime(conv, (old, old))  # version convertie plus vieille que la source : ignorée
    assert core.pick_version(src) == src


def test_media_files_filters_and_sorts(tmp_path):
    for name in ("b.gif", "a.png", "notes.txt", "c.JPG"):
        (tmp_path / name).write_bytes(b"x")
    assert [p.name for p in core.media_files(tmp_path)] == ["a.png", "b.gif", "c.JPG"]


def test_play_clock_stops(tmp_path):
    sink, stop = Sink(), threading.Event()
    t = threading.Thread(target=core.play_clock, args=(sink, stop, lambda: 30))
    t.start()
    time.sleep(0.3)
    stop.set()
    t.join(2)
    assert not t.is_alive() and sink.frames


def test_play_file_cache_gives_same_frames_without_decoding(tmp_path, monkeypatch):
    gif = make_gif(tmp_path / "c.gif", n=5)
    first = Sink()
    core.play_file(gif, first, threading.Event(), lambda: 60)
    assert list(core.CACHE_DIR.glob("*.amx"))
    direct = [core.image_to_frame(img, 60) for img, _d in _frames(gif)]
    assert first.frames == direct  # cache pleine luminosité + table : même résultat que la conversion directe
    monkeypatch.setattr(core, "iter_gif_frames", lambda _p: (_ for _ in ()).throw(AssertionError("décodé")))
    second = Sink()
    core.play_file(gif, second, threading.Event(), lambda: 60)
    assert second.frames == first.frames


def _frames(gif):
    for img, delay in core.iter_gif_frames(gif):
        yield img.copy(), delay


def test_cache_invalidated_when_file_changes(tmp_path):
    gif = make_gif(tmp_path / "d.gif", n=3)
    key = core._cache_path(gif, False)
    time.sleep(0.01)
    make_gif(gif, n=4)
    os.utime(gif, ns=(time.time_ns(), time.time_ns() + 10**9))
    assert core._cache_path(gif, False) != key


def test_interrupted_play_is_not_cached(tmp_path):
    gif = make_gif(tmp_path / "e.gif", n=6)
    stop = threading.Event()
    sink = Sink()
    sink.write = lambda f: (Sink.write(sink, f), stop.set())[0]
    core.play_file(gif, sink, stop, lambda: 60)
    assert not core._cache_path(gif, False).exists()
