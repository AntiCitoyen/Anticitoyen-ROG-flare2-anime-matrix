"""Mémoire du clavier : format .bin, trames d'écriture, échos, reprise, démon (transport factice)."""
import time

import pytest
from PIL import Image

import rog_flare2_demon as D
import rog_flare2_memoire as M


class EchoTransport:
    """Renvoie l'écho de chaque trame ; drop = numéros d'écriture (à partir de 0) restés sans écho."""

    def __init__(self, *a, drop=(), **kw):
        self.frames, self.pending, self.drop = [], [], set(drop)

    def connect(self):
        return "factice"

    def write(self, frame):
        if len(self.frames) not in self.drop:
            self.pending.append(bytes(frame))
        self.frames.append(bytes(frame))
        return len(frame)

    def read(self, size=1024, timeout_ms=0):
        return self.pending.pop(0) if self.pending else b""

    def close(self):
        pass


def anim(n, ms=64):
    return [(bytes([i % 256]) * M.LED_COUNT, ms) for i in range(n)]


def test_bin_aller_retour():
    frames = anim(97)
    data = M.encode_bin(frames)
    assert len(data) == 30460  # taille du .bin d'Armoury Crate pour 97 images
    assert data[:4] == bytes([97, 0, 64, 0])
    assert M.decode_bin(data) == frames
    with pytest.raises(ValueError):
        M.decode_bin(data[:-1])


def test_trames_comme_armoury_crate():
    blocks = M.block_frames(M.encode_bin(anim(97)))
    assert len(blocks) == 30 and all(len(b) == 1024 for b in blocks)
    assert [b[2] for b in blocks] == list(range(0x1D, -1, -1))
    assert blocks[0][:4] == bytes([0x60, 0xA0, 0x1D, 0x00])
    assert not any(blocks[-1][4 + 30460 - 29 * 1020:])  # fin complétée par des zéros
    assert M.begin_frame(30)[:6] == bytes.fromhex("60a807641e00")
    assert M.show_frame(75)[:6] == bytes.fromhex("60a8874bff00")
    assert M.show_frame(0)[:6] == bytes.fromhex("60a88700ff00")


def test_reduire():
    assert len(M.fit(anim(300), "couper")) == M.MAX_FRAMES
    short = M.fit(anim(400, 50), "alterner")
    assert len(short) == 100 and short[0][1] == 200  # 2 passes : durée totale conservée
    with pytest.raises(ValueError):
        M.encode_bin(anim(M.MAX_FRAMES + 1))


def test_ecriture_et_reprise():
    data = M.encode_bin(anim(10))
    t = EchoTransport()
    seen = []
    assert M.write_memory(t, data, 50, progress=lambda k, n: seen.append((k, n))) == 1
    assert t.frames[0][:3] == bytes([0x60, 0xA8, 0x07])
    assert [f[1] for f in t.frames[1:-1]] == [0xA0] * len(M.block_frames(data))
    assert t.frames[-1][:6] == bytes.fromhex("60a88732ff00")
    assert seen[-1] == (len(M.block_frames(data)),) * 2

    t = EchoTransport(drop={2})  # écho du 2e bloc perdu : tout recommence au début
    assert M.write_memory(t, data, timeout_ms=20) == 2
    assert sum(1 for f in t.frames if f[:3] == bytes([0x60, 0xA8, 0x07])) == 2

    t = EchoTransport(drop=set(range(1000)))
    with pytest.raises(M.WriteError):
        M.write_memory(t, data, timeout_ms=5, attempts=2)


def test_depuis_un_gif(tmp_path):
    imgs = [Image.new("L", (19, 24), v) for v in (0, 255)]
    gif = tmp_path / "a.gif"
    imgs[0].save(gif, save_all=True, append_images=imgs[1:], duration=[120, 80], loop=0)
    frames = M.frames_from_file(gif)
    assert [ms for _l, ms in frames] == [120, 80]
    assert not any(frames[0][0]) and min(frames[1][0]) > 200
    out = tmp_path / "a.bin"
    M.main([str(gif), str(out)])
    assert M.frames_from_file(out) == frames


def test_demon(monkeypatch, tmp_path):
    monkeypatch.setattr(D, "FlareTransport", EchoTransport)
    d = D.Daemon()
    try:
        gif = tmp_path / "b.gif"
        Image.new("L", (19, 24), 255).save(gif)
        r = d.handle({"cmd": "memoire", "file": str(gif)})
        assert r["ok"] and r["images"] == 1 and d.show == {"type": "clavier"}
        sent = d.screen.transport.frames
        assert any(f[:3] == bytes([0x60, 0xA8, 0x07]) for f in sent)
        d.handle({"cmd": "brightness", "value": 30})
        time.sleep(0.6)
        assert sent[-1][:6] == bytes.fromhex("60a8871eff00")  # luminosité du clavier, sans renvoi
        d.notify("x", 0.2)  # la notification passe en trames 60 81, puis l'animation revient
        time.sleep(1.2)
        assert sent[-1][:6] == bytes.fromhex("60a8871eff00")
        assert d.handle({"cmd": "memoire", "file": str(tmp_path / "absent.gif")})["ok"] is False
    finally:
        d.stop()
