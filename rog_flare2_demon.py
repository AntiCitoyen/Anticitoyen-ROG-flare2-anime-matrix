#!/usr/bin/env python3
"""animematrixd — seul propriétaire de l'écran AniMe Matrix.

Un processus tient le HID ; les clients (lanceur, bascule, CLI animematrix-ctl,
notifications, programmation horaire, icône de barre système, API HTTP locale)
lui parlent par un socket Unix ($XDG_RUNTIME_DIR/animematrix.sock), une requête
JSON par ligne, une réponse JSON par ligne :

    {"cmd": "play", "show": {"type": "gif", "files": [...], "loop": true}}
    {"cmd": "play", "show": {"type": "effet", "name": "Plasma", "params": {...}, "speed": 1.0}}
    {"cmd": "play", "show": {"type": "horloge"}}
    {"cmd": "play", "show": {"type": "liste", "name": "Soirée"}}   (listes : rog_flare2_listes)
    {"cmd": "play", "show": {"type": "webcam", "silhouette": false}}
    {"cmd": "play", "show": {"type": "ecran", "mode": "ecran" | "souris" | "fenetre"}}   (miroir d'écran)
    {"cmd": "notify", "text": "Nouveau mail", "duration": 6}
    {"cmd": "brightness", "value": 60}      {"cmd": "params", "params": {"speed": 250}}
    {"cmd": "speed", "value": 1.5}          {"cmd": "stop"}      {"cmd": "status"}
    {"cmd": "frame"}  (dernière trame, base64)   {"cmd": "release"} / {"cmd": "resume"}
    {"cmd": "rgb", "config": {"mode": "clavier", "effet": "arc-en-ciel", "vitesse": 50}, "save": true}
        (touches : effet du clavier, ou « theme » / « pulsation » envoyés par le démon)
    {"cmd": "memoire", "file": "a.gif", "reduire": "couper" | "alterner", "fidele": false}
        (enregistrée dans le clavier, puis affichée : lecture {"type": "clavier"})

Deux couches : la lecture de base, et une surimpression temporaire
(notification) qui masque la base puis la rend. Le clavier débranché est
retrouvé automatiquement. Au démarrage, le mode choisi dans le lanceur
(~/.config/rog-flare2/demarrage : gif | horloge | derniere | rien) est rejoué.

    rog_flare2_demon.py [--http PORT]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import signal
import socket
import socketserver
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rog_flare2_core import VERSION, CONFIG_DIR, gallery_dir, media_files, pick_version, play_clock, play_file  # noqa: E402
from rog_flare2_matrix_paint import FB_OFFSET, FRAME_SIZE, LED_COUNT, PREFIX, FlareTransport  # noqa: E402

RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR") or f"/tmp/animematrix-{os.getuid()}")
SOCKET_PATH = RUNTIME / "animematrix.sock"
SHOW_FILE = CONFIG_DIR / "lecture.json"  # dernière lecture (rejouée au démarrage si « derniere »)
START_FILE = CONFIG_DIR / "demarrage"
STATE_FILE = CONFIG_DIR / "demon.json"  # luminosité mémorisée
MEMORY_FILE = CONFIG_DIR / "memoire.bin"  # copie de l'animation écrite dans le clavier (aperçu)
BLANK = bytes(PREFIX) + bytes(FRAME_SIZE - len(PREFIX))
KEEPALIVE = 1.0  # une trame identique est quand même renvoyée au bout d'une seconde


class FakeTransport:
    """Clavier factice (ANIMEMATRIX_FAUX_CLAVIER=1) : tests, démonstrations, captures d'écran."""

    def __init__(self, *a, **kw):
        self.echo = b""

    def connect(self):
        return "factice"

    def write(self, frame):
        self.echo = bytes(frame)
        return len(frame)

    def read(self, size=FRAME_SIZE, timeout_ms=0):
        echo, self.echo = self.echo, b""
        return echo

    def close(self):
        pass


if os.environ.get("ANIMEMATRIX_FAUX_CLAVIER"):
    FlareTransport = FakeTransport  # noqa: F811


class Screen:
    """Accès au clavier partagé par les couches ; reconnexion quand il revient."""

    def __init__(self):
        from rog_flare2_portable import AsusctlTransport, hardware
        # Clavier ROG Strix Flare II Animate, ou (expérimental) écran d'un portable ROG via asusctl
        self.transport = AsusctlTransport(RUNTIME) if hardware() == "portable-asusctl" else FlareTransport()
        self.lock = threading.Lock()
        self.connected = False
        self.released = False  # rendu à un autre programme (éditeur de dessin)
        self.last = BLANK
        self.base = BLANK  # dernière trame de la lecture, sans voyants
        self.overlay_active = False
        self.holds: set[str] = set()  # raisons d'écran noir (verrouillage, veille, plein écran…)
        self.sent: bytes | None = None  # dernière trame réellement envoyée (None : à renvoyer)
        self.sent_at = 0.0
        self.skipped = 0  # trames identiques non renvoyées (statistique)
        self.badges: list[int] = []  # LED des voyants allumés (rog_flare2_voyants), par-dessus la lecture
        self.error: str | None = None  # clavier introuvable ou refusé (affiché par le lanceur et la télécommande)
        self.hardware = False  # animation enregistrée dans le clavier affichée : la base n'envoie rien
        self.software_sent = False  # une trame 60 81 est passée depuis : le clavier a quitté l'animation enregistrée

    def _ensure(self) -> bool:
        if self.released:
            return False
        if not self.connected:
            try:
                self.transport.connect()
                self.connected = True
                self.sent = None
                self.error = None
            except Exception as exc:
                self.error = f"clavier : {exc}"
                return False
        return True

    def write(self, frame: bytes, layer: str = "base") -> None:
        """Écrit une trame ; celles de la base sont gardées mais pas envoyées sous une surimpression."""
        if layer == "base" and (self.overlay_active or self.hardware):
            return
        if self.holds:
            return
        with self.lock:
            if layer == "base":
                self.base = frame
            if self.badges:
                composed = bytearray(frame)
                for i in self.badges:
                    composed[FB_OFFSET + i] = 255
                frame = bytes(composed)
            self.last = frame
            if not self._ensure():
                return
            now = time.monotonic()
            if frame == self.sent and now - self.sent_at < KEEPALIVE:
                self.skipped += 1  # image fixe, horloge entre deux minutes… : rien de neuf sur l'USB
                return
            try:
                self.transport.write(frame)
                self.sent, self.sent_at = frame, now
                self.software_sent = True
            except Exception:
                self.connected = False
                self.sent = None
                self.transport.close()

    def set_badges(self, leds: list[int], base: bytes):
        """Voyants changés : la dernière trame de base est réécrite avec eux."""
        self.badges = leds
        if not self.overlay_active:
            self.write(base)

    def _panel(self, level: int):
        """Luminosité du panneau (60 A8 87) : 0 l'éteint vraiment, même si le clavier repasse de lui-même
        sur l'animation enregistrée faute de trames. Clavier Flare II seulement (écho attendu)."""
        if hasattr(self.transport, "read"):
            from rog_flare2_memoire import show_frame
            self.transport.write(show_frame(level))

    def hold(self, reason: str, on: bool):
        """Écran éteint tant qu'une raison est active ; la lecture reprend quand il n'en reste aucune."""
        was_held = bool(self.holds)
        if on and not self.holds:
            with self.lock:
                self.last = BLANK
                if self._ensure():
                    try:
                        self.transport.write(BLANK)
                        self._panel(0)
                        self.sent, self.sent_at = BLANK, time.monotonic()
                        self.software_sent = True
                    except Exception:
                        self.connected = False
                        self.sent = None
        (self.holds.add if on else self.holds.discard)(reason)
        if was_held and not self.holds and not self.hardware:
            # (animation du clavier affichée : son fil la rallume lui-même, software_sent)
            with self.lock:
                if self._ensure():
                    try:
                        self._panel(100)
                    except Exception:
                        self.connected = False
                self.sent = None
            self.write(self.base, "base")  # la dernière image revient tout de suite, sans attendre la suivante

    def raw(self, fn):
        """fn(transport) sous le verrou, hors du flux de trames 60 81 (mémoire du clavier)."""
        with self.lock:
            if not self._ensure():
                raise OSError("clavier indisponible")
            if not hasattr(self.transport, "read"):
                raise OSError("mémoire du clavier non prise en charge par ce matériel")
            try:
                result = fn(self.transport)
            except OSError:
                self.connected = False
                self.transport.close()
                raise
            finally:
                self.sent = None
            self.software_sent = False
            return result

    def release(self):
        with self.lock:
            self.released = True
            self.connected = False
            self.sent = None
            self.transport.close()

    def resume(self):
        with self.lock:
            self.released = False


class Layer:
    """Écrivain de trames pour une couche (interface transport.write attendue par les lecteurs)."""

    def __init__(self, screen: Screen, name: str):
        self.screen, self.name = screen, name

    def write(self, frame: bytes) -> int:
        self.screen.write(frame, self.name)
        return len(frame)


class Daemon:
    def __init__(self):
        self.screen = Screen()
        self.state = self._load_state()
        self.show: dict | None = None
        self.error: str | None = None  # dernière erreur de la lecture en cours
        self.effect = None  # effet en cours (réglages en direct)
        self.speed = 1.0
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.overlay_thread: threading.Thread | None = None
        self.overlay_stop = threading.Event()
        self.lock = threading.RLock()
        self.server = None  # serveur du socket (commande quit)
        from rog_flare2_notifs import NotificationWatcher
        from rog_flare2_rgb import KeyboardLights
        self.notifs = NotificationWatcher(lambda text: self.notify(text, 0))
        self.rgb = KeyboardLights(self._screen_level, self._accent,
                                  lambda: self.screen.last[FB_OFFSET:FB_OFFSET + LED_COUNT])
        from rog_flare2_programme import Programme
        self.manual: dict | None = None  # dernière lecture demandée par un client (reprise après une règle)
        self.programme = Programme(self._play_rule, self._end_rule, self.screen.hold, self._rule_keys)
        from rog_flare2_voyants import Watcher
        self.voyants = Watcher(self._badges_changed, self._announce)
        from rog_flare2_telecommande import RemoteServer
        self.remote = RemoteServer(self.handle)

    # ---------- état ----------
    @staticmethod
    def _load_state() -> dict:
        try:
            return {"brightness": 60, **json.loads(STATE_FILE.read_text())}
        except (OSError, ValueError):
            return {"brightness": 60}

    def _save_state(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.state))

    def _screen_level(self) -> float:
        """Luminosité moyenne de l'écran (0-1), pour la pulsation des touches."""
        leds = self.screen.last[FB_OFFSET:FB_OFFSET + LED_COUNT]
        return min(1.0, 3 * sum(leds) / (255 * LED_COUNT))  # ×3 : un écran « plein » n'allume qu'une partie des LED

    @staticmethod
    def _accent() -> str:
        import rog_flare2_themes as themes
        return themes.palette()["accent"]

    def brightness(self) -> int:
        return int(self.state.get("brightness", 60))

    def _badges_changed(self, states: dict):
        from rog_flare2_voyants import BADGES
        self.screen.set_badges([i for name, on in states.items() if on for i in BADGES[name]], self.screen.base)
        self.rgb.set_badges(states if self.voyants.cfg.get("touches") else {})  # aussi F1-F3

    def _announce(self, name: str):
        from rog_flare2_i18n import _
        texts = {"micro": _("Micro coupé") if self.voyants.cfg.get("micro") == "coupe" else _("Micro actif"),
                 "webcam": _("Webcam active"), "obs": _("OBS en direct")}
        self.notify(texts[name], 0)

    # ---------- lecture de base ----------
    def _job(self, show: dict):
        kind = show.get("type")
        layer = Layer(self.screen, "base")
        if kind == "gif":
            files = [Path(f) for f in show.get("files", [])]
            if not files and show.get("folder"):
                files = media_files(Path(show["folder"]))
            converted = show.get("converted", True)

            def job(stop):
                while not stop.is_set():
                    for f in files:
                        if stop.is_set():
                            return
                        try:
                            play_file(pick_version(f) if converted else f, layer, stop, self.brightness,
                                      bool(show.get("fidele")))
                        except OSError:
                            pass
                    if not show.get("loop", True):
                        return
            return job
        if kind == "effet":
            from rog_flare2_effets import make_effect, run_effect
            self.speed = float(show.get("speed", 1.0))

            def job(stop):
                self.effect = make_effect(show["name"], show.get("params"))
                try:
                    run_effect(self.effect, layer, stop, self.brightness, lambda: self.speed)
                finally:
                    self.effect = None
            return job
        if kind == "horloge":
            from rog_flare2_horloges import FACES, saved_face
            effect_name = FACES.get(show.get("cadran") or saved_face())
            if effect_name:  # cadran analogique, binaire, en mots, stylisé
                return self._job({"type": "effet", "name": effect_name, "params": {}, "speed": 1.0})
            return lambda stop: play_clock(layer, stop, self.brightness)
        if kind == "webcam":
            from rog_flare2_video import play_webcam
            return lambda stop: play_webcam(layer, stop, self.brightness, show.get("device", "/dev/video0"),
                                            bool(show.get("silhouette")))
        if kind == "ecran":
            from rog_flare2_video import play_screen
            return lambda stop: play_screen(layer, stop, self.brightness, show.get("mode", "ecran"))
        if kind == "clavier":  # animation du clavier : intégrée (effet 1-6) ou enregistrée (7, défaut)
            effect = int(show.get("effet", 7))
            if not 1 <= effect <= 7:
                raise ValueError(f"animation du clavier inconnue : {effect}")
            return lambda stop: self._hardware_job(stop, effect)
        if kind == "liste":
            from rog_flare2_listes import DEFAULT_SECONDS, item_show, load_lists
            items = show.get("items") or load_lists().get(show.get("name", ""), [])
            if not items:
                raise ValueError(f"liste vide ou inconnue : {show.get('name')!r}")

            def job(stop):
                while not stop.is_set():
                    for item in items:
                        if stop.is_set():
                            return
                        sub_show = item_show(item)
                        if sub_show is not None and sub_show.get("type") == "liste":
                            continue  # pas de liste dans une liste
                        inner = threading.Event()
                        if sub_show is None:
                            self.screen.write(BLANK, "base")
                            worker = None
                        else:
                            sub_job = self._job(sub_show)
                            worker = threading.Thread(target=self._run, args=(sub_job, inner), daemon=True)
                            worker.start()
                        stop.wait(max(1.0, float(item.get("duree", DEFAULT_SECONDS))))
                        inner.set()
                        if worker is not None:
                            worker.join(timeout=5)
            return job
        raise ValueError(f"lecture inconnue : {kind!r}")

    def _hardware_job(self, stop, effect: int = 7):
        """Affiche l'animation enregistrée ; la réaffiche après une notification ou un écran noir,
        et suit la luminosité (octet de luminosité du clavier, sans renvoyer l'animation)."""
        from rog_flare2_memoire import decode_bin, set_hardware_brightness
        screen, level = self.screen, None
        try:  # aperçu : l'animation que ce démon a écrite (inconnue si elle vient d'Armoury Crate)
            frames = decode_bin(MEMORY_FILE.read_bytes()) if effect == 7 else []
        except (OSError, ValueError):
            frames = []
        total = sum(ms for _l, ms in frames) / 1000
        t0 = time.monotonic()
        if not frames:
            screen.last = screen.base = BLANK  # contenu inconnu : pas d'aperçu plutôt qu'une image figée
        screen.hardware = True
        try:
            while not stop.is_set():
                wanted = self.brightness()
                if not screen.overlay_active and not screen.holds and (screen.software_sent or wanted != level):
                    screen.raw(lambda t: set_hardware_brightness(t, wanted, effect=effect))
                    level = wanted
                if frames and not screen.overlay_active and not screen.holds:
                    t = (time.monotonic() - t0) % total
                    for leds, ms in frames:
                        t -= ms / 1000
                        if t < 0:
                            break
                    dim = bytes(v * wanted // 100 for v in leds)
                    screen.last = screen.base = BLANK[:FB_OFFSET] + dim + BLANK[FB_OFFSET + LED_COUNT:]
                stop.wait(0.05)
        finally:
            screen.hardware = False

    def _resume_when_gone(self, pid: int):
        while self.screen.released:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                self.screen.resume()
                return
            except PermissionError:
                pass  # vivant, mais pas à nous
            time.sleep(1)

    def write_memory(self, req: dict) -> dict:
        """Enregistre un GIF, une image ou un .bin dans la mémoire du clavier, puis l'affiche."""
        from rog_flare2_memoire import block_frames, encode_bin, frames_from_file, write_memory
        frames = frames_from_file(Path(req["file"]).expanduser(), bool(req.get("fidele")),
                                  req.get("reduire", "couper"))
        data = encode_bin(frames)
        with self.lock:
            self._stop_base()
            self.show = None
        attempts = self.screen.raw(lambda t: write_memory(t, data, self.brightness()))
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        MEMORY_FILE.write_bytes(data)
        self.play({"type": "clavier"})
        return {"ok": True, "images": len(frames), "octets": len(data), "blocs": len(block_frames(data)),
                "tentatives": attempts}

    def play(self, show: dict, manual: bool = True):
        job = self._job(show)
        if manual:
            self.manual = show
        with self.lock:
            self._stop_base()
            self.show = show
            self.error = None
            self.stop_event = threading.Event()
            stop = self.stop_event
            self.thread = threading.Thread(target=self._run, args=(job, stop), daemon=True)
            self.thread.start()
        if manual:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            SHOW_FILE.write_text(json.dumps(show, ensure_ascii=False, indent=1), encoding="utf-8")

    def _play_rule(self, show: dict | None):
        if show is None:
            self.stop(manual=False)
        else:
            self.play(show, manual=False)

    def current_error(self) -> str | None:
        """Ce qui empêche l'affichage : clavier absent, lecture en échec, touches injoignables."""
        if self.screen.error and not self.screen.released:
            return self.screen.error
        if self.error:
            return self.error
        status = str(self.rgb.status)
        return status if status.startswith("clavier indisponible") else None

    def _rule_keys(self, preset: str | None):
        try:
            self.rgb.override(preset or None)
        except KeyError:
            print(f"touches : préréglage inconnu {preset!r}", file=sys.stderr, flush=True)

    def _end_rule(self):
        if self.manual is None:
            self.stop(manual=False)
        else:
            self.play(self.manual, manual=False)

    def _run(self, job, stop):
        while not stop.is_set():
            try:
                job(stop)
                return
            except Exception as exc:  # clavier débranché, fichier illisible… : on réessaie
                print(f"lecture interrompue : {exc}", file=sys.stderr, flush=True)
                self.error = str(exc).strip().splitlines()[-1][:200] if str(exc).strip() else type(exc).__name__
                stop.wait(3)

    def _stop_base(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=5)
        self.thread = None

    def stop(self, manual: bool = True):
        with self.lock:
            self._stop_base()
            self.show = None
            if manual:
                self.manual = None
        self.screen.write(BLANK, "base")

    # ---------- surimpression ----------
    def notify(self, text: str, duration: float = 6.0):
        """Surimpression d'un texte défilant ; duration <= 0 : le temps d'un passage complet."""
        from rog_flare2_effets import make_effect, run_effect
        from rog_flare2_rgb import load_config as rgb_config
        if rgb_config().get("eclair"):
            self.rgb.flash()  # éclair des touches
        if duration <= 0:
            from rog_flare2_texte import render
            duration = (37 + render(text).shape[1]) / 20.0 + 0.5  # 20 colonnes/s : un passage complet
        with self.lock:
            self.overlay_stop.set()
            if self.overlay_thread is not None:
                self.overlay_thread.join(timeout=3)
            self.overlay_stop = threading.Event()
            stop = self.overlay_stop
            effect = make_effect("Scroll Text", {"message": text})
            self.screen.overlay_active = True

            def job():
                timer = threading.Timer(duration, stop.set)
                timer.start()
                try:
                    run_effect(effect, Layer(self.screen, "overlay"), stop, self.brightness)
                finally:
                    timer.cancel()
                    self.screen.overlay_active = False
                    if self.show is None:
                        self.screen.write(BLANK, "base")
            self.overlay_thread = threading.Thread(target=job, daemon=True)
            self.overlay_thread.start()

    # ---------- commandes ----------
    def handle(self, req: dict) -> dict:
        cmd = req.get("cmd")
        if cmd == "ping":
            return {"ok": True, "version": VERSION}
        if cmd == "status":
            return {"ok": True, "version": VERSION, "show": self.show, "brightness": self.brightness(),
                    "rgb": self.rgb.status, "hold": sorted(self.screen.holds),
                    "regle": (self.programme.current or {}).get("contenu"),
                    "speed": self.speed, "connected": self.screen.connected, "released": self.screen.released,
                    "overlay": self.screen.overlay_active, "skipped": self.screen.skipped,
                    "voyants": [k for k, v in self.voyants.states.items() if v],
                    "telecommande": self.remote.httpd is not None, "erreur": self.current_error()}
        if cmd == "play":
            self.play(req["show"])
            return {"ok": True}
        if cmd == "stop":
            self.stop()
            return {"ok": True}
        if cmd == "rgb":  # couleurs des touches (rog_flare2_rgb)
            from rog_flare2_rgb import EFFECTS, SOFTWARE_MODES, load_config as rgb_config, save_config as rgb_save
            cfg = {**rgb_config(), **req.get("config", {})}
            if cfg.get("effet") not in EFFECTS or cfg.get("mode") not in ("clavier", "off", *SOFTWARE_MODES):
                return {"ok": False, "error": f"réglage inconnu : {cfg.get('mode')!r} / {cfg.get('effet')!r}"}
            rgb_save(cfg)
            self.rgb.overridden = None  # un choix explicite passe avant la règle en cours
            self.rgb.start(cfg)
            if cfg["mode"] == "clavier":
                try:
                    self.rgb.apply(cfg, save=bool(req.get("save", True)))
                except OSError as exc:
                    return {"ok": False, "error": str(exc)}
            return {"ok": True, "rgb": cfg}
        if cmd == "memoire":
            try:
                return self.write_memory(req)
            except (OSError, ValueError, RuntimeError) as exc:
                return {"ok": False, "error": str(exc)}
        if cmd == "galerie":
            from rog_flare2_programme import show_for
            self.play(show_for("galerie"))
            return {"ok": True}
        if cmd == "catalogue":
            from rog_flare2_telecommande import catalogue
            return {"ok": True, **catalogue()}
        if cmd == "brightness":
            self.state["brightness"] = max(0, min(100, int(req["value"])))
            self._save_state()
            return {"ok": True}
        if cmd == "speed":
            self.speed = float(req["value"])
            if self.show and self.show.get("type") == "effet":
                self.show["speed"] = self.speed
            return {"ok": True}
        if cmd == "params":
            from rog_flare2_effets import effect_class, param_value
            effect, show = self.effect, self.show
            if effect is None or not show or show.get("type") != "effet":
                return {"ok": False, "error": "aucun effet en cours"}
            specs = effect_class(show["name"]).PARAMS
            for attr, raw in req.get("params", {}).items():
                if attr in specs:
                    setattr(effect, attr, param_value(specs[attr], raw))
                    show.setdefault("params", {})[attr] = raw
            return {"ok": True}
        if cmd == "key":  # touche pour un jeu en cours
            on_key = getattr(self.effect, "on_key", None)
            if on_key is None:
                return {"ok": False, "error": "aucun jeu en cours"}
            on_key(str(req.get("key", "")))
            return {"ok": True}
        if cmd == "hold":  # écran noir pour une raison donnée (déclencheurs, tests)
            self.screen.hold(str(req.get("reason", "manuel")), bool(req.get("on", True)))
            return {"ok": True, "hold": sorted(self.screen.holds)}
        if cmd == "config":  # réglages relus (notifications du bureau)
            from rog_flare2_notifs import load_config
            from rog_flare2_rgb import load_config as rgb_config
            from rog_flare2_programme import load_config as prog_config
            self.rgb.start(rgb_config())
            self.programme.start(prog_config())
            from rog_flare2_voyants import load_config as badge_config
            self.voyants.start(badge_config())
            self._badges_changed(self.voyants.states)  # « aussi sur les touches » pris en compte tout de suite
            from rog_flare2_telecommande import load_config as remote_config
            self.remote.start(remote_config())
            return {"ok": True, "notifications": self.notifs.start(load_config())}
        if cmd == "notify":
            self.notify(str(req.get("text", "")), float(req.get("duration", 6)))
            return {"ok": True}
        if cmd == "frame":
            leds = self.screen.last[FB_OFFSET:FB_OFFSET + LED_COUNT]
            return {"ok": True, "frame": base64.b64encode(leds).decode()}
        if cmd == "release":  # pid : reprise automatique quand ce processus disparaît
            self.screen.release()
            pid = req.get("pid")
            if isinstance(pid, int) and pid > 0:
                threading.Thread(target=self._resume_when_gone, args=(pid,), daemon=True).start()
            return {"ok": True}
        if cmd == "resume":
            self.screen.resume()
            return {"ok": True}
        if cmd == "quit":
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return {"ok": True}
        return {"ok": False, "error": f"commande inconnue : {cmd!r}"}

    def start_mode(self):
        """Rejoue le mode de démarrage choisi dans le lanceur."""
        try:
            mode = START_FILE.read_text().strip()
        except OSError:
            mode = migrate_legacy()
        try:
            if mode == "gif":
                folder = gallery_dir()
                self.play({"type": "gif", "files": [str(f) for f in media_files(folder)] if folder.is_dir() else [],
                           "folder": str(folder), "loop": True, "converted": True})
            elif mode == "horloge":
                self.play({"type": "horloge"})
            elif mode == "derniere":
                self.play(json.loads(SHOW_FILE.read_text(encoding="utf-8")))
        except (OSError, ValueError, KeyError) as exc:
            print(f"mode de démarrage {mode!r} impossible : {exc}", file=sys.stderr, flush=True)


LEGACY = {"animematrix-galerie.service": "gif", "animematrix-horloge.service": "horloge",
          "animematrix-lecture.service": "derniere"}


def migrate_legacy() -> str:
    """Première exécution après les versions ≤ 1.3 : reprend le service activé au démarrage, puis le désactive."""
    import subprocess
    mode = "rien"
    wants = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "systemd" / "user" / "default.target.wants"
    for unit, m in LEGACY.items():
        link = wants / unit  # après la mise à jour du paquet, le lien reste mais l'unité n'existe plus
        enabled = link.is_symlink() or subprocess.run(["systemctl", "--user", "is-enabled", "--quiet", unit],
                                                      capture_output=True).returncode == 0
        if enabled:
            mode = m
            subprocess.run(["systemctl", "--user", "disable", "--now", unit], capture_output=True)
            if link.is_symlink():
                link.unlink()  # lien orphelin de l'ancienne unité
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    START_FILE.write_text(mode + "\n")
    return mode


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            try:
                resp = self.server.daemon_ref.handle(json.loads(line))
            except Exception as exc:
                resp = {"ok": False, "error": str(exc)}
            self.wfile.write((json.dumps(resp, ensure_ascii=False) + "\n").encode())
            self.wfile.flush()


class UnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


def local_request_allowed(headers) -> bool:
    """API HTTP locale : refuse ce qu'un navigateur envoie pour une page web (CSRF, DNS rebinding).

    Une page ne peut pas poster du JSON sans pré-vol CORS (jamais accordé ici) ; elle peut poster en
    text/plain, mais son navigateur ajoute alors Origin. Le nom d'hôte doit être local.
    """
    host = (headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
    return (host in ("127.0.0.1", "localhost", "::1") and headers.get("Origin") is None
            and (headers.get("Content-Type") or "").split(";")[0].strip().lower() == "application/json")


def serve_http(daemon: Daemon, port: int):
    """API HTTP locale (127.0.0.1 seulement) : POST /api avec le même JSON que le socket."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/api":
                self.send_error(404)
                return
            if not local_request_allowed(self.headers):
                self.send_error(403)
                return
            size = int(self.headers.get("Content-Length") or 0)
            if not 0 <= size <= 1 << 20:
                self.send_error(413)
                return
            try:
                body = json.loads(self.rfile.read(size))
                resp = daemon.handle(body)
            except Exception as exc:
                resp = {"ok": False, "error": str(exc)}
            data = json.dumps(resp, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()


def check_runtime_dir() -> None:
    """Dossier du socket à nous seul : sans XDG_RUNTIME_DIR, /tmp/animematrix-<uid> pourrait avoir été
    créé à l'avance par un autre compte pour y substituer un faux socket."""
    RUNTIME.mkdir(mode=0o700, parents=True, exist_ok=True)
    st = RUNTIME.stat()
    if st.st_uid != os.getuid() or st.st_mode & 0o077:
        sys.exit(f"animematrixd : {RUNTIME} n'appartient pas à cet utilisateur ou est accessible à d'autres")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", type=int, default=0, help="port de l'API HTTP locale (0 = désactivée)")
    args = ap.parse_args()
    check_runtime_dir()
    # Un seul démon : si le socket répond, on s'arrête.
    if SOCKET_PATH.exists():
        try:
            with socket.socket(socket.AF_UNIX) as s:
                s.connect(str(SOCKET_PATH))
            print("animematrixd tourne déjà", file=sys.stderr)
            return
        except OSError:
            SOCKET_PATH.unlink()
    daemon = Daemon()
    server = UnixServer(str(SOCKET_PATH), Handler)
    os.chmod(SOCKET_PATH, 0o600)
    server.daemon_ref = daemon
    daemon.server = server
    if args.http:
        serve_http(daemon, args.http)

    def shutdown(*_a):
        threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    daemon.start_mode()
    from rog_flare2_notifs import load_config
    from rog_flare2_rgb import load_config as rgb_config
    daemon.notifs.start(load_config())
    daemon.rgb.start(rgb_config())
    from rog_flare2_programme import load_config as prog_config
    daemon.programme.start(prog_config())
    from rog_flare2_voyants import load_config as badge_config
    daemon.voyants.start(badge_config())
    from rog_flare2_telecommande import load_config as remote_config
    daemon.remote.start(remote_config())
    try:
        server.serve_forever()
    finally:
        daemon.stop_event.set()
        daemon.notifs.stop()
        daemon.rgb.stop()
        daemon.programme.stop()
        daemon.voyants.stop()
        daemon.remote.stop()
        SOCKET_PATH.unlink(missing_ok=True)
        time.sleep(0.2)
        daemon.screen.transport.close()


if __name__ == "__main__":
    main()
