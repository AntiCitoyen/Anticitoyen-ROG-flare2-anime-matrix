<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# AniMe Matrix for Linux — ROG Strix Flare II Animate

[![Release](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![MIT License](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

Control the **AniMe Matrix** display (312 mini-LEDs) of the **ASUS ROG Strix Flare II Animate** keyboard on Linux, without Armoury Crate or Windows: GIFs and images, background gallery, clock, 19 animated effects, 7 audio visualizers, LED-by-LED drawing.

The application's graphical interface is available in 19 languages and follows the system language automatically; it can be changed in the **Settings** tab (**Language:**).

<div align="center">

[🇫🇷 Français](../../README.md) · **🇬🇧 English** · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/en/interface-drawer.png" alt="Dial + drawer" width="760"><br><em>Dial + drawer (default interface)</em></p>

| Dial | Rounded | Classic |
|:---:|:---:|:---:|
| <img src="../captures/en/interface-dial.png" alt="Dial" width="260"> | <img src="../captures/en/interface-rounded.png" alt="Rounded" width="190"> | <img src="../captures/en/interface-classic.png" alt="Classic" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## Table of contents

- [What the project does](#projet)
- [Supported hardware](#materiel)
- [Installation](#installation)
- [Usage](#utilisation)
- [Preparing good GIFs](#gif)
- [How it works](#fonctionnement)
- [Troubleshooting](#depannage)
- [Repository layout](#depot)
- [Building the .deb package](#deb)
- [Credits](#credits)
- [License](#licence)
- [Supporting the project](#soutien)

---

<a id="projet"></a>

## What the project does

ASUS only provides the AniMe Matrix display of this keyboard on Windows (Armoury Crate). This project talks to the keyboard directly over USB HID and brings:

- **A graphical launcher** (`animematrix`), with a choice of **4 interfaces**: *Dial + drawer* (round window with a settings panel that slides out to the right, the default), *Dial* (everything in the circle), *Rounded* (very rounded corners, brightness wheel) and *Classic* (tabs). The round interfaces show **the 312 LEDs live**, exactly as sent to the keyboard. Four control blocks:
  - **GIF / images**: play one or more files, or a whole folder as a looping gallery; convert GIFs for the matrix.
  - **Effects**: 19 animations (Matrix-style rain, plasma, fire, stars, fireworks, lightning, metaballs, wave, snake, scrolling text, styled clock, keyboard reaction…), adjustable while they run.
  - **Audio**: 7 visualizers that react to the sound played by the PC (spectrum, KITT/KARR, starburst, oscilloscope, audio fire…).
  - **Settings**: what is shown at session start, language, theme and interface, drawing editor, project links.
- **A clock**, HH:MM, from the launcher or as a background service.
- **A background gallery**: a `systemd --user` service that cycles through a GIF folder as soon as the session opens.
- **A one-click toggle** (`animematrix-bascule`): the tray icon turns the screen on or off; right-click picks GIF Gallery, Clock, or Off.
- **A GIF conversion tailored to the matrix** (`animematrix-convertir`): 19×24, grayscale, 3 levels, no dithering — see [../GUIDE-GIF.md](../GUIDE-GIF.md).
- **A drawing editor**, LED by LED (`animematrix-dessin`).
- **11 themes**: 5 inspired by ROG (Classic, Strix, Glitch, Gold, Carbon), 5 pink ones (Sakura, Bubblegum, Rose Gold, Lavender Rose, Rose Night) and the system look, selectable in *Settings* → *Theme:*.
- **Low resource usage**: GIFs are decoded frame by frame; a 400-GIF gallery runs in ~25 MB of memory.

<a id="materiel"></a>

## Supported hardware

| Keyboard | USB | Interface |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | HID, interface 4 (usage page `0xFF02`) |

The AniMe Matrix displays on ROG **laptops** (Zephyrus G14, etc.) use a different protocol: they are **not** supported here (see `asusctl` instead).

Tested on Ubuntu 26.04 (X11, PipeWire). Any distribution with Python ≥ 3.10, hidapi, Tk and systemd should work.

<a id="installation"></a>

## Installation

### .deb package (Debian, Ubuntu, Mint, Pop!_OS…)

1. Download `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` from the [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) page.
2. Install it (apt fetches the dependencies):
   ```bash
   sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb
   ```
3. **Unplug and replug the keyboard** (the udev rule grants access to the logged-in user).
4. Launch **AniMe Matrix** from the applications menu, or `animematrix` in a terminal.

The package installs:

| Item | Location |
|---|---|
| Programs | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| Commands | `animematrix`, `animematrix-bascule`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-convertir`, `animematrix-dessin`, `animematrix-lecture` |
| User services | `/usr/lib/systemd/user/animematrix-galerie.service`, `animematrix-horloge.service`, `animematrix-lecture.service` (not enabled by default) |
| udev rule | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| Menu and icon | `animematrix.desktop`, `animematrix` icon |

Uninstall: `sudo apt remove anticitoyen-rog-flare2-anime-matrix`.

### From source

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# access to the keyboard without root
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# then unplug/replug the keyboard
.venv/bin/python rog_flare2_launcher.py
```

Useful system tools: `imagemagick` (conversion), `pulseaudio-utils` (`parec`, for audio), `zenity` (file pickers), `libnotify-bin` (toggle notifications).

For the background services when running from source, copy `systemd/*.service` into `~/.config/systemd/user/`, replacing the `ExecStart=` lines with the path to `.venv/bin/python` and the script (`rog_flare2_folder_player.py`, `rog_flare2_clock_v3.py`), then `systemctl --user daemon-reload`.

<a id="utilisation"></a>

## Usage

### The launcher

`animematrix` (or the **AniMe Matrix** entry in the applications menu).

In the round interfaces, the round buttons open the *GIF*, *Effects*, *Audio* and *Settings* blocks (in the drawer or in the circle); *Clock* and *Stop* act immediately; the bottom arc sets the brightness; drag the window by its background to move it; the small buttons at the top minimize or close it. The round shape uses the X11 SHAPE extension (`python3-xlib` package); without it, the same interface is shown in a rectangular window.

- **GIF / images**: *GIF/images…* for a selection, *Folder (gallery)…* for a whole folder. The chosen folder also becomes the background gallery's folder. *Prefer converted versions* reads `dossier/matrix/nom.gif` when it exists (produced by the conversion).
- **Effects** and **Audio**: choose, adjust, *▶ Run effect*. The sliders act live; *Tempo* speeds up or slows down the animation.
- **Brightness**, **🕒 Clock**, **■ Stop** (which clears the screen) are common to all tabs.
- **Settings**: *At session start* = GIF gallery, Clock, Last playback or None; *Interface:* chooses one of the 4 interfaces (the launcher restarts, what is displayed keeps playing).

**When you close the launcher, whatever is displayed keeps playing** (GIF, effect with its current settings, audio visualizer or clock): the launcher hands it off to the background service `animematrix-lecture.service`. On the next launch, it takes back control as soon as something else starts (only one program can write to the keyboard). *■ Stop* before closing leaves the screen off.

### Toggle and background services

```bash
animematrix-bascule            # on → off; off → last mode
animematrix-bascule gif        # background gallery, also at session start
animematrix-bascule horloge    # background clock, also at session start
animematrix-bascule lecture    # last launcher playback, also at session start
animematrix-bascule off        # off, nothing at session start
animematrix-bascule etat       # current mode
```

The same choices are in the tray icon's right-click menu. Under the hood: `systemctl --user enable --now animematrix-galerie.service` (or `animematrix-horloge.service`).

### From the command line

| Command | Role |
|---|---|
| `animematrix-effet --liste` | lists the effects and visualizers |
| `animematrix-effet "Plasma" --brightness 60 --vitesse 1.5` | launches an effect (Ctrl+C to stop) |
| `animematrix-galerie [dossier] --brightness 60 [--originaux]` | cycles through a folder (defaults to the last one chosen in the launcher, otherwise `~/Images/AniMe-Matrix`) |
| `animematrix-lecture` | replays the launcher's last playback (`~/.config/rog-flare2/lecture.json`) |
| `animematrix-horloge -b 25` | clock; `--clear` clears the screen, `--once --text 12:34` displays text |
| `animematrix-convertir dossier/ [--sortie D] [--force]` | converts GIFs for the matrix (into `dossier/matrix/`) |
| `animematrix-dessin` | drawing editor |

### Audio

The visualizers listen to the **default audio output's monitor** using `parec` (PipeWire or PulseAudio): they react to what the PC is playing, not to the microphone. To change the output, change the system's default output.

### "Keyboard React" effect

It lights up the screen in time with your typing using `pynput`, which reads keystrokes across the whole session while the effect is running. It works under X11; under Wayland, it does not receive keystrokes.

<a id="gif"></a>

## Preparing good GIFs

The screen is not a rectangle: 24 staggered rows, from 19 LEDs at the top to 7 at the bottom, 3 truly distinct grayscale levels, a halo between neighboring LEDs. Silhouettes, pictograms, short text and slow motion render well; photos and videos do not.

The full guide (canvas size, levels, frame rate, brightness, ImageMagick command): **[../GUIDE-GIF.md](../GUIDE-GIF.md)**.

<a id="fonctionnement"></a>

## How it works

- **Transport**: hidapi opens the keyboard's HID interface #4 and writes **1024-byte** frames to it.
- **Frame**: `60 81 00 00` + **312 bytes** (one 0–255 brightness value per LED, in hardware order) + zeros up to 1024.
- **Geometry**: 24 rows staggered diagonally (19 → 7 LEDs), or equivalently 12 logical rows of 37 → 15 columns (PolyWollyWin's model); both mappings have been verified identical across the 312 LEDs.
- **GIF**: each frame is recomposed (optimized GIFs only store the differences), converted to grayscale, resampled to 24 rows and sampled row by row.
- **Animation**: no onboard memory is used; the animation is the host sending frames one after another (~30 fps for effects).

The original reverse-engineering notes (USBPcap captures, LED order, calibration points) are in **[../PROTOCOL.md](../PROTOCOL.md)**; the `*.cap` captures and the `parse_usbpcap.py` / `rog_flare2_replay_capture.py` tools remain in the repository for anyone who wants to dig further.

⚠️ Do not send the keyboard the packets used by laptop AniMe Matrix displays (`0x5E …`, `0xEC …`): that is the wrong protocol and it can lock up the keyboard (unplug/replug, or hold **Fn + Esc** for 10–15 s).

<a id="depannage"></a>

## Troubleshooting

| Symptom | Likely cause | Solution |
|---|---|---|
| `interface 4 not found` | keyboard not detected or no permissions | `lsusb \| grep 0b05:19fc`; is the udev rule installed? unplug/replug |
| `Permission denied` / `open failed` | udev rule not applied | `sudo udevadm control --reload-rules && sudo udevadm trigger`, then replug |
| The screen does not change | another program is already writing to it | `animematrix-bascule off`, close other launchers or scripts |
| Visualizers stay in demo mode | no `parec` or no sound | install `pulseaudio-utils`, play some sound |
| "Keyboard React" does not respond | Wayland session or `pynput` missing | X11 session, `sudo apt install python3-pynput` |
| The background gallery does not start | empty or missing folder | choose a folder in the launcher (GIF tab) |
| The round window shows as a rectangle | SHAPE extension or `python3-xlib` missing | `sudo apt install python3-xlib`, or *Settings* → *Interface:* → *Classic* |
| A service's log | — | `journalctl --user -u animematrix-galerie.service -f` |

<a id="depot"></a>

## Repository layout

| File | Role |
|---|---|
| `rog_flare2_launcher.py` | graphical launcher (Tk) |
| `rog_flare2_i18n.py`, `locale/` | interface translation (19 languages, one JSON catalogue per language) |
| `rog_flare2_themes.py` | interface themes (ROG and pink) |
| `rog_flare2_ui_ronde.py` | round interfaces (dial + drawer, dial, rounded): drawing, window shape, LED preview |
| `rog_flare2_effets.py` | effects and audio visualizers (PolyWollyWin engine adapted for Linux) |
| `polywollywin/` | PolyWollyWin's effects engine, copied unmodified (MIT) |
| `rog_flare2_folder_player.py` | background gallery (service) |
| `rog_flare2_lecture.py` | background playback: resumes what the launcher was displaying when closed (service) |
| `rog_flare2_clock_v3.py` | clock (service) |
| `rog_flare2_bascule.sh` | gallery / clock / off toggle |
| `rog_flare2_convertir.py` | GIF conversion (ImageMagick) |
| `rog_flare2_matrix_paint.py` | HID transport, LED order, drawing editor |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | reverse-engineering tools and captures |
| `systemd/` | user services |
| `packaging/` | udev rule, menu entry, icon, .deb package files and script |
| `docs/` | GIF guide, protocol notes, screenshots |

<a id="deb"></a>

## Building the .deb package

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

Only `dpkg-deb` and `bash` are required; the version is read from `rog_flare2_launcher.py` (`VERSION`).

<a id="credits"></a>

## Credits

- **NicRoss512** — protocol reverse-engineering, original clock and editor: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol). This repository is forked from it; its history is preserved.
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin) (MIT), the Windows controller whose effects and audio-visualizer engine is reused here.
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), for LED behavior (halo, perceived levels, frame rate).

Independent project, not affiliated with ASUS. "ROG", "AniMe Matrix" and "Armoury Crate" are trademarks of ASUSTeK.

<a id="licence"></a>

## License

[MIT](../../LICENSE) for the code in this repository. `polywollywin/` remains under its author's MIT license ([polywollywin/LICENSE](../../polywollywin/LICENSE)). NicRoss512's original files (`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `docs/PROTOCOL.md`, captures) were published without an explicit license and remain their author's; they are redistributed with attribution.

<a id="soutien"></a>

## Supporting the project

If this project is useful to you, a coffee helps keep it going:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — the link is also in the launcher's *Settings* tab.

Bug reports and ideas: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues).
