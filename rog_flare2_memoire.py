#!/usr/bin/env python3
"""Animation enregistrée dans la mémoire du clavier : elle s'affiche sans logiciel, dès le branchement.

Protocole relevé sur le ROG Strix Flare II Animate (micrologiciel 3.00.14), trames de 1024 octets
sur l'interface 4, chacune renvoyée à l'identique par le clavier (écho) :

    60 A8 07 64 N 00          début : effet 7 (animation personnalisée), N blocs à suivre
    60 A0 i 00 + 1020 octets  N blocs, i = N-1 … 0 ; données = fichier .bin, complété par des zéros
    60 A8 87 L FF 00          affichage de l'effet 7, luminosité L = 0 … 100 (0 : écran éteint)

Fichier .bin (celui d'Armoury Crate) : F (u16 LE), F durées en ms (u16 LE), F × 312 niveaux de gris
dans l'ordre des LED des trames 60 81. Armoury Crate s'arrête à 196 images.
"""
from __future__ import annotations

import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_matrix_paint import FRAME_SIZE, LED_COUNT  # noqa: E402

MAX_FRAMES = 196
BLOCK_DATA = FRAME_SIZE - 4
CUSTOM_EFFECT = 7
MIN_MS, MAX_MS = 20, 0xFFFF
ECHO_TIMEOUT_MS = 1000  # l'écho tarde parfois ~170 ms (écriture en flash)
ATTEMPTS = 3


class WriteError(RuntimeError):
    """Écriture refusée ou interrompue (écho absent après toutes les tentatives)."""


def _frame(head: bytes, data: bytes = b"") -> bytes:
    body = head + data
    return body + bytes(FRAME_SIZE - len(body))


def encode_bin(frames: list[tuple[bytes, int]]) -> bytes:
    """[(312 octets, durée ms)] → .bin."""
    if not frames:
        raise ValueError("aucune image")
    if len(frames) > MAX_FRAMES:
        raise ValueError(f"{len(frames)} images, {MAX_FRAMES} au plus")
    out = bytearray(struct.pack("<H", len(frames)))
    for _leds, ms in frames:
        out += struct.pack("<H", max(MIN_MS, min(MAX_MS, int(ms))))
    for leds, _ms in frames:
        if len(leds) != LED_COUNT:
            raise ValueError(f"image de {len(leds)} octets, {LED_COUNT} attendus")
        out += leds
    return bytes(out)


def decode_bin(data: bytes) -> list[tuple[bytes, int]]:
    """.bin → [(312 octets, durée ms)] ; lève ValueError si le fichier est incohérent."""
    if len(data) < 2:
        raise ValueError("fichier trop court")
    (count,) = struct.unpack_from("<H", data)
    size = 2 + count * (2 + LED_COUNT)
    if not 1 <= count <= MAX_FRAMES or len(data) < size:
        raise ValueError(f"en-tête incohérent : {count} images, {len(data)} octets")
    durations = struct.unpack_from(f"<{count}H", data, 2)
    base = 2 + 2 * count
    return [(data[base + i * LED_COUNT: base + (i + 1) * LED_COUNT], durations[i]) for i in range(count)]


def fit(frames: list, mode: str = "couper") -> list:
    """Ramène une animation à MAX_FRAMES images : « couper » garde le début, « alterner » retire une
    image sur deux (en doublant la durée des gardées) jusqu'à ce qu'elle tienne."""
    if mode == "alterner":
        while len(frames) > MAX_FRAMES:
            frames = [(leds, min(MAX_MS, ms + frames[i + 1][1] if i + 1 < len(frames) else ms))
                      for i, (leds, ms) in enumerate(frames) if i % 2 == 0]
        return frames
    return frames[:MAX_FRAMES]


def frames_from_file(path: Path, fidele: bool = False, mode: str = "couper") -> list[tuple[bytes, int]]:
    """GIF, image fixe ou .bin → images prêtes pour encode_bin (pleine luminosité)."""
    path = Path(path)
    if path.suffix.lower() == ".bin":
        return fit(decode_bin(path.read_bytes()), mode)
    from rog_flare2_core import FB_OFFSET, LED_BYTES, image_to_frame, is_faithful, iter_gif_frames
    fidele = fidele or is_faithful(path)
    frames = []
    for img, delay in iter_gif_frames(path):
        frames.append((image_to_frame(img, 100, fidele)[FB_OFFSET:FB_OFFSET + LED_BYTES], round(delay * 1000)))
        if mode == "couper" and len(frames) >= MAX_FRAMES:
            break
    if len(frames) == 1:
        frames[0] = (frames[0][0], 1000)  # image fixe : la durée n'a pas d'effet visible
    return fit(frames, mode)


def begin_frame(blocks: int) -> bytes:
    return _frame(bytes([0x60, 0xA8, CUSTOM_EFFECT, 0x64, blocks, 0x00]))


def block_frames(data: bytes) -> list[bytes]:
    count = -(-len(data) // BLOCK_DATA)
    if count > 0xFF:
        raise ValueError("animation trop grande")
    return [_frame(bytes([0x60, 0xA0, count - 1 - k, 0x00]), data[k * BLOCK_DATA:(k + 1) * BLOCK_DATA])
            for k in range(count)]


def show_frame(brightness: int, effect: int = CUSTOM_EFFECT) -> bytes:
    """Affiche l'effet enregistré ; luminosité 0 = écran éteint."""
    return _frame(bytes([0x60, 0xA8, 0x80 | effect, max(0, min(100, int(brightness))), 0xFF, 0x00]))


def _drain(transport) -> None:
    """Vide les échos en attente (ceux des trames 60 81 d'une lecture précédente)."""
    for _ in range(256):
        if not transport.read(FRAME_SIZE, 0):
            return


def _send(transport, frame: bytes, timeout_ms: int) -> bool:
    """Écrit une trame et attend son écho (les échos d'autres trames sont ignorés)."""
    transport.write(frame)
    deadline = time.monotonic() + timeout_ms / 1000
    while True:
        left = int((deadline - time.monotonic()) * 1000)
        if left <= 0:
            return False
        echo = bytes(transport.read(FRAME_SIZE, left) or b"")
        if echo[:4] == frame[:4]:
            return True


def write_memory(transport, data: bytes, brightness: int = 100, progress=None,
                 timeout_ms: int = ECHO_TIMEOUT_MS, attempts: int = ATTEMPTS) -> int:
    """Enregistre le .bin dans le clavier puis l'affiche ; renvoie le nombre de tentatives.

    Un écho manquant fait tout recommencer depuis la trame de début, comme Armoury Crate.
    progress(fait, total) est appelé après chaque bloc.
    """
    blocks = block_frames(data)
    for attempt in range(1, attempts + 1):
        _drain(transport)
        ok = _send(transport, begin_frame(len(blocks)), timeout_ms)
        for k, frame in enumerate(blocks):
            if not ok:
                break
            ok = _send(transport, frame, timeout_ms)
            if ok and progress:
                progress(k + 1, len(blocks))
        if ok and _send(transport, show_frame(brightness), timeout_ms):
            return attempt
        time.sleep(0.5)
    raise WriteError(f"le clavier n'a pas confirmé l'écriture ({attempts} tentatives)")


def set_hardware_brightness(transport, brightness: int, timeout_ms: int = ECHO_TIMEOUT_MS) -> bool:
    """Luminosité (0 = éteint) de l'animation enregistrée, sans la renvoyer."""
    _drain(transport)
    return _send(transport, show_frame(brightness), timeout_ms)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(prog="animematrix-memoire",
                                 description="Prépare le fichier .bin d'une animation pour la mémoire du clavier.")
    ap.add_argument("source", help="GIF, image ou .bin")
    ap.add_argument("sortie", help="fichier .bin écrit")
    ap.add_argument("--fidele", action="store_true", help="géométrie fidèle")
    ap.add_argument("--reduire", choices=("couper", "alterner"), default="couper",
                    help=f"au-delà de {MAX_FRAMES} images : garder le début, ou retirer une image sur deux")
    args = ap.parse_args(argv)
    frames = frames_from_file(Path(args.source), args.fidele, args.reduire)
    data = encode_bin(frames)
    Path(args.sortie).write_bytes(data)
    print(f"{len(frames)} images, {len(data)} octets, {len(block_frames(data))} blocs")


if __name__ == "__main__":
    main()
