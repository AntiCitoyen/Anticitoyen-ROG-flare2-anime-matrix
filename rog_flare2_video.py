"""Vidéo, webcam et miroir d'écran sur l'AniMe Matrix (ffmpeg ; GStreamer + portail sous Wayland).

Toutes les sources passent par le même tuyau : images en niveaux de gris déjà réduites
à la géométrie fidèle (19 × 24, proportions réelles, centre de l'image gardé), contraste
étiré image par image, puis 312 LED dans l'ordre matériel.

- vidéos (.mp4, .webm, .mkv, .mov, .avi, .m4v) : dans la galerie comme les GIF ;
- webcam : /dev/video0 (v4l2), en image ou en silhouette ;
- miroir d'écran : X11 (ffmpeg x11grab) écran entier, zone qui suit la souris ou fenêtre
  active ; Wayland (expérimental) : portail ScreenCast + PipeWire, l'écran est choisi
  dans la fenêtre du système.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import threading

import numpy as np

from rog_flare2_matrix_paint import FB_OFFSET, FRAME_SIZE, PHYSICAL_CALIBRATED_ORDER, PREFIX

from rog_flare2_core import VIDEO_EXTENSIONS  # noqa: F401  (réexporté)
W, H = 19, 24
FPS = 20
RATIO = 19 / (24 * 0.77)  # largeur / hauteur réelles de l'écran
VF = (f"crop='min(iw,ih*{RATIO:.4f})':'min(ih,iw/{RATIO:.4f})',scale={W}:{H}:flags=area,format=gray")
INDEX = np.array([row * W + min(W - 1, (row + 1) // 2 + col) for row, col in PHYSICAL_CALIBRATED_ORDER])
HEADER = bytes(PREFIX) + bytes(FB_OFFSET - len(PREFIX))
TRAILER = bytes(FRAME_SIZE - FB_OFFSET - len(INDEX))


def shrink(data: bytes, width: int, height: int) -> bytes:
    """Image grise width × height -> W × H fidèle (centre gardé aux proportions de l'écran)."""
    from PIL import Image
    img = Image.frombytes("L", (width, height), data[:width * height])
    cw = min(width, round(height * RATIO))
    chh = min(height, round(width / RATIO))
    left, top = (width - cw) // 2, (height - chh) // 2
    return img.crop((left, top, left + cw, top + chh)).resize((W, H), Image.BOX).tobytes()


def available() -> bool:
    return shutil.which("ffmpeg") is not None


class Contrast:
    """Étire le contraste (centiles 2-98), lissé dans le temps pour éviter le scintillement."""

    def __init__(self, silhouette: bool = False):
        self.silhouette = silhouette
        self.lo, self.hi = 0.0, 255.0

    def __call__(self, gray: np.ndarray) -> np.ndarray:
        g = gray.astype(np.float32)
        lo, hi = np.percentile(g, 2), np.percentile(g, 98)
        self.lo += (lo - self.lo) * 0.3
        self.hi += (max(hi, lo + 24) - self.hi) * 0.3
        g = np.clip((g - self.lo) * 255.0 / max(1.0, self.hi - self.lo), 0, 255)
        if self.silhouette:  # contour du sujet : plein ou éteint, seuil sur la moyenne
            g = np.where(g > g.mean(), 255.0, 0.0)
        return g.astype(np.uint8)


def frame_bytes(gray19x24: np.ndarray, brightness: int) -> bytes:
    leds = gray19x24.reshape(-1)[INDEX].astype(np.float32) * (brightness / 100.0)
    return HEADER + np.clip(leds, 0, 255).astype(np.uint8).tobytes() + TRAILER


def pump(read, transport, stop: threading.Event, brightness, silhouette=False, paced=False) -> int:
    """Lit des images W × H (octets) par read(n) jusqu'à stop ou fin ; renvoie le nombre d'images."""
    contrast = Contrast(silhouette)
    n = 0
    while not stop.is_set():
        data = read(W * H)
        if not data or len(data) < W * H:
            break
        gray = contrast(np.frombuffer(data, dtype=np.uint8).reshape(H, W))
        transport.write(frame_bytes(gray, brightness()))
        n += 1
        if paced:
            stop.wait(1.0 / FPS)
    return n


def _ffmpeg(input_args: list[str], transport, stop, brightness, silhouette=False) -> int:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", *input_args, "-an", "-vf", VF, "-r", str(FPS),
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    watcher = threading.Thread(target=lambda: (stop.wait(), proc.poll() is None and proc.terminate()), daemon=True)
    watcher.start()
    try:
        n = pump(proc.stdout.read, transport, stop, brightness, silhouette)
    finally:
        if proc.poll() is None:
            proc.terminate()
        proc.wait(timeout=5)
    if n == 0 and not stop.is_set():
        err = proc.stderr.read().decode(errors="replace").strip().splitlines()
        raise OSError(err[-1] if err else "ffmpeg n'a produit aucune image")
    return n


def play_video(path, transport, stop: threading.Event, brightness, loop: bool = False) -> None:
    _ffmpeg(["-re", *(["-stream_loop", "-1"] if loop else []), "-i", str(path)], transport, stop, brightness)


def play_webcam(transport, stop, brightness, device: str = "/dev/video0", silhouette: bool = False) -> None:
    _ffmpeg(["-f", "v4l2", "-i", device], transport, stop, brightness, silhouette)


# ---------------------------------------------------------------- miroir d'écran
def _xwininfo_active() -> list[int] | None:
    """Géométrie (x, y, largeur, hauteur) de la fenêtre active sous X11."""
    try:
        win = subprocess.run(["xprop", "-root", "_NET_ACTIVE_WINDOW"], capture_output=True, text=True,
                             timeout=2).stdout.split()[-1]
        info = subprocess.run(["xwininfo", "-id", win], capture_output=True, text=True, timeout=2).stdout
    except (OSError, IndexError, subprocess.SubprocessError):
        return None
    vals = {}
    for line in info.splitlines():
        key, _sep, value = line.strip().partition(":")
        vals[key] = value.strip()
    try:
        return [int(vals["Absolute upper-left X"]), int(vals["Absolute upper-left Y"]), int(vals["Width"]),
                int(vals["Height"])]
    except (KeyError, ValueError):
        return None


def x11_input(mode: str, display: str) -> list[str]:
    if mode == "souris":  # carré de 480 px centré sur le pointeur
        return ["-f", "x11grab", "-framerate", str(FPS), "-follow_mouse", "centered", "-video_size", "480x480",
                "-i", f"{display}+0,0"]
    if mode == "fenetre":
        geo = _xwininfo_active()
        if geo:
            x, y, w, h = geo
            return ["-f", "x11grab", "-framerate", str(FPS), "-video_size", f"{w - w % 2}x{h - h % 2}",
                    "-i", f"{display}+{x},{y}"]
    return ["-f", "x11grab", "-framerate", str(FPS), "-i", display]


def play_screen(transport, stop, brightness, mode: str = "ecran") -> None:
    wayland = bool(os.environ.get("WAYLAND_DISPLAY")) or os.environ.get("XDG_SESSION_TYPE") == "wayland"
    if wayland:
        play_screen_portal(transport, stop, brightness)
    else:
        display = os.environ.get("DISPLAY")
        if not display:
            raise OSError("miroir d'écran : pas d'affichage X11 (DISPLAY) dans l'environnement du démon")
        _ffmpeg(x11_input(mode, display), transport, stop, brightness)


def play_screen_portal(transport, stop, brightness) -> None:
    """Wayland : portail org.freedesktop.portal.ScreenCast, puis PipeWire lu par GStreamer (python3-gi)."""
    import secrets

    import gi
    gi.require_version("Gst", "1.0")
    from gi.repository import Gio, GLib, Gst
    Gst.init(None)
    bus = Gio.bus_get_sync(Gio.BusType.SESSION)
    sender = bus.get_unique_name()[1:].replace(".", "_")
    ctx = GLib.MainContext.new()
    ctx.push_thread_default()
    try:
        def call(method, params, sig):
            """Appel au portail et attente du signal Response de sa requête."""
            token = "amx" + secrets.token_hex(6)
            path = f"/org/freedesktop/portal/desktop/request/{sender}/{token}"
            result = {}

            def on_response(_c, _s, _p, _i, _sig, args):
                result["code"], result["res"] = args.unpack()
            sub = bus.signal_subscribe("org.freedesktop.portal.Desktop", "org.freedesktop.portal.Request",
                                       "Response", path, None, Gio.DBusSignalFlags.NO_MATCH_RULE, on_response)
            params[-1]["handle_token"] = GLib.Variant("s", token)
            bus.call_sync("org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop",
                          "org.freedesktop.portal.ScreenCast", method, GLib.Variant(sig, tuple(params)), None,
                          Gio.DBusCallFlags.NONE, -1, None)
            waited = 0.0
            while not result and not stop.is_set() and waited < 120:  # le temps de choisir l'écran
                if not ctx.iteration(False):
                    stop.wait(0.05)
                    waited += 0.05
            bus.signal_unsubscribe(sub)
            if result.get("code") != 0:
                raise OSError("miroir d'écran refusé ou annulé")
            return result["res"]
        res = call("CreateSession", [{"session_handle_token": GLib.Variant("s", "amx" + secrets.token_hex(6))}],
                   "(a{sv})")
        session = res["session_handle"]
        call("SelectSources", [session, {"types": GLib.Variant("u", 1), "cursor_mode": GLib.Variant("u", 2)}],
             "(oa{sv})")
        res = call("Start", [session, "", {}], "(osa{sv})")
        node = res["streams"][0][0]
        reply, fds = bus.call_with_unix_fd_list_sync(
            "org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.ScreenCast", "OpenPipeWireRemote",
            GLib.Variant("(oa{sv})", (session, {})), None, Gio.DBusCallFlags.NONE, -1, None, None)
        fd = fds.get(reply.unpack()[0])
    finally:
        ctx.pop_thread_default()
    cw, ch = 160, 90  # capture réduite (largeur multiple de 4 : pas de bourrage de lignes), puis recadrage
    pipeline = Gst.parse_launch(
        f"pipewiresrc fd={fd} path={node} ! videoconvert ! videoscale ! videorate ! "
        f"video/x-raw,format=GRAY8,width={cw},height={ch},framerate={FPS}/1 ! appsink name=sink max-buffers=2 drop=true")
    sink = pipeline.get_by_name("sink")
    pipeline.set_state(Gst.State.PLAYING)

    def read(_n):
        while not stop.is_set():
            sample = sink.emit("try-pull-sample", Gst.SECOND // 5)
            if sample is not None:
                buf = sample.get_buffer()
                return shrink(buf.extract_dup(0, buf.get_size()), cw, ch)
        return b""
    try:
        pump(read, transport, stop, brightness)
    finally:
        pipeline.set_state(Gst.State.NULL)
        os.close(fd)


def preview_frames(path, seconds: float = 6.0, brightness: int = 100) -> list[tuple[bytes, float]]:
    """Premières secondes d'une vidéo en trames (aperçu fidèle du lanceur)."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-t", str(seconds), "-i", str(path), "-an", "-vf", VF,
           "-r", str(FPS), "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    out = subprocess.run(cmd, capture_output=True, timeout=60).stdout
    contrast = Contrast()
    return [(frame_bytes(contrast(np.frombuffer(out[i:i + W * H], dtype=np.uint8).reshape(H, W)), brightness),
             1.0 / FPS) for i in range(0, len(out) - W * H + 1, W * H)]
