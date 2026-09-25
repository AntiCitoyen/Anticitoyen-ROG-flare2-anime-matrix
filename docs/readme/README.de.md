<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# AniMe Matrix für Linux — ROG Strix Flare II Animate

[![Release](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![MIT-Lizenz](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

Steuert unter Linux das **AniMe Matrix**-Display (312 Mini-LEDs) der Tastatur **ASUS ROG Strix Flare II Animate** ganz ohne Armoury Crate oder Windows: GIFs und Bilder, Hintergrundgalerie, Uhr, 19 animierte Effekte, 7 Audio-Visualizer, LED-für-LED-Zeichnen.

Die grafische Benutzeroberfläche der Anwendung ist in 19 Sprachen verfügbar und folgt automatisch der Systemsprache; sie kann im Reiter **Einstellungen** (**Sprache:**) geändert werden.

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · **🇩🇪 Deutsch** · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/de/interface-drawer.png" alt="Drehrad + Schublade" width="760"><br><em>Drehrad + Schublade (Standardoberfläche)</em></p>

| Drehrad | Abgerundet | Klassisch |
|:---:|:---:|:---:|
| <img src="../captures/de/interface-dial.png" alt="Drehrad" width="260"> | <img src="../captures/de/interface-rounded.png" alt="Abgerundet" width="190"> | <img src="../captures/de/interface-classic.png" alt="Klassisch" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## Inhaltsverzeichnis

- [Was das Projekt macht](#projet)
- [Unterstützte Hardware](#materiel)
- [Installation](#installation)
- [Verwendung](#utilisation)
- [Gute GIFs vorbereiten](#gif)
- [Funktionsweise](#fonctionnement)
- [Fehlerbehebung](#depannage)
- [Aufbau des Repositorys](#depot)
- [Das .deb-Paket bauen](#deb)
- [Danksagungen](#credits)
- [Lizenz](#licence)
- [Projekt unterstützen](#soutien)

---

<a id="projet"></a>

## Was das Projekt macht

ASUS bietet das AniMe-Matrix-Display dieser Tastatur nur unter Windows (Armoury Crate) an. Dieses Projekt spricht die Tastatur direkt über USB-HID an und bringt:

- **Einen grafischen Starter** (`animematrix`), wahlweise mit **4 Oberflächen**: *Drehrad + Schublade* (rundes Fenster mit einem Einstellungspanel, das rechts herausfährt, die Standardeinstellung), *Drehrad* (alles im Kreis), *Abgerundet* (sehr runde Ecken, Helligkeitsrad) und *Klassisch* (Reiter). Die runden Oberflächen zeigen **die 312 LEDs live**, genau wie sie an die Tastatur gesendet werden. Vier Bedienblöcke:
  - **GIF / Bilder**: eine oder mehrere Dateien abspielen, oder einen ganzen Ordner als Endlos-Galerie; GIFs für die Matrix konvertieren.
  - **Effekte**: 19 Animationen (Matrix-artiger Regen, Plasma, Feuer, Sterne, Feuerwerk, Blitze, Metaballs, Welle, Schlange, Lauftext, stilisierte Uhr, Reaktion auf die Tastatur…), während des Laufens einstellbar.
  - **Audio**: 7 Visualizer, die auf den vom PC wiedergegebenen Ton reagieren (Spektrum, KITT/KARR, Starburst, Oszilloskop, Audio-Feuer…).
  - **Einstellungen**: was beim Sitzungsstart angezeigt wird, Sprache, Design und Oberfläche, Zeicheneditor, Projekt-Links.
- **Eine Uhr**, HH:MM, aus dem Starter oder als Hintergrunddienst.
- **Eine Hintergrundgalerie**: ein `systemd --user`-Dienst, der einen GIF-Ordner ab dem Sitzungsstart durchläuft.
- **Ein Ein-Klick-Umschalter** (`animematrix-bascule`): das Symbol im Menü schaltet das Display ein oder aus; Rechtsklick wählt GIF-Galerie, Uhr oder Aus.
- **Eine für die Matrix angepasste GIF-Konvertierung** (`animematrix-convertir`): 19×24, Graustufen, 3 Stufen, ohne Dithering — siehe [../GUIDE-GIF.md](../GUIDE-GIF.md).
- **Einen Zeicheneditor** LED für LED (`animematrix-dessin`).
- **11 Designs**: 5 im ROG-Stil (Classic, Strix, Glitch, Gold, Carbon), 5 in Rosa (Sakura, Kaugummi, Roségold, Lavendelrosa, Rosa Nacht) und das des Systems, wählbar unter *Einstellungen* → *Design:*.
- **Integrierte Updates**: *Einstellungen* → *Nach Updates suchen*; automatische Prüfung einmal täglich (abschaltbar). Der Starter lädt das `.deb` des neuesten GitHub-Release herunter, prüft seine SHA-256-Prüfsumme und installiert es nach Abfrage des Administratorpassworts (`pkexec`).
- **Geringer Ressourcenverbrauch**: GIFs werden Bild für Bild dekodiert; eine Galerie mit 400 GIFs läuft mit ~25 MB Speicher.

<a id="materiel"></a>

## Unterstützte Hardware

| Tastatur | USB | Schnittstelle |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | HID, Schnittstelle 4 (Usage Page `0xFF02`) |

Die AniMe-Matrix-Displays der ROG-**Laptops** (Zephyrus G14 usw.) verwenden ein anderes Protokoll: Sie werden hier **nicht** unterstützt (siehe stattdessen `asusctl`).

Getestet unter Ubuntu 26.04 (X11, PipeWire). Jede Distribution mit Python ≥ 3.10, hidapi, Tk und systemd sollte funktionieren.

<a id="installation"></a>

## Installation

### .deb-Paket (Debian, Ubuntu, Mint, Pop!_OS…)

1. `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` von der Seite [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) herunterladen.
2. Installieren (apt löst die Abhängigkeiten auf):
   ```bash
   sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb
   ```
3. **Tastatur ab- und wieder anstecken** (die udev-Regel gewährt dem angemeldeten Benutzer Zugriff).
4. **AniMe Matrix** über das Anwendungsmenü starten, oder `animematrix` im Terminal.

Das Paket installiert:

| Element | Ort |
|---|---|
| Programme | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| Befehle | `animematrix`, `animematrix-bascule`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-convertir`, `animematrix-dessin`, `animematrix-lecture` |
| Benutzerdienste | `/usr/lib/systemd/user/animematrix-galerie.service`, `animematrix-horloge.service`, `animematrix-lecture.service` (standardmäßig nicht aktiviert) |
| udev-Regel | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| Menü und Symbol | `animematrix.desktop`, Symbol `animematrix` |

Deinstallation: `sudo apt remove anticitoyen-rog-flare2-anime-matrix`.

### Aus den Quellen

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# Zugriff auf die Tastatur ohne root
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# dann Tastatur ab- und wieder anstecken
.venv/bin/python rog_flare2_launcher.py
```

Nützliche Systemwerkzeuge: `imagemagick` (Konvertierung), `pulseaudio-utils` (`parec`, für Audio), `zenity` (Dateiauswahl), `libnotify-bin` (Benachrichtigungen des Umschalters).

Für die Hintergrunddienste bei Ausführung aus den Quellen `systemd/*.service` nach `~/.config/systemd/user/` kopieren und dabei die Zeilen `ExecStart=` durch den Pfad zu `.venv/bin/python` und zum Skript ersetzen (`rog_flare2_folder_player.py`, `rog_flare2_clock_v3.py`), anschließend `systemctl --user daemon-reload`.

<a id="utilisation"></a>

## Verwendung

### Der Starter

`animematrix` (oder der Eintrag **AniMe Matrix** im Menü).

In den runden Oberflächen öffnen die runden Schaltflächen die Blöcke *GIF*, *Effekte*, *Audio* und *Einstellungen* (in der Schublade oder im Kreis); *Uhr* und *Stopp* wirken sofort; der untere Bogen regelt die Helligkeit; das Fenster wird durch Ziehen am Hintergrund verschoben; die kleinen Schaltflächen oben verkleinern oder schließen es. Die runde Form nutzt die X11-Erweiterung SHAPE (Paket `python3-xlib`); ohne sie wird dieselbe Oberfläche in einem rechteckigen Fenster angezeigt.

- **GIF / Bilder**: *GIF/Bilder…* für eine Auswahl, *Ordner (Galerie)…* für einen ganzen Ordner. Der gewählte Ordner wird auch zum Ordner der Hintergrundgalerie. *Konvertierte Versionen bevorzugen* liest `dossier/matrix/nom.gif`, wenn vorhanden (durch die Konvertierung erzeugt).
- **Effekte** und **Audio**: auswählen, einstellen, *▶ Effekt starten*. Die Regler wirken live; *Takt* beschleunigt oder verlangsamt die Animation.
- **Helligkeit**, **🕒 Uhr**, **■ Stopp** (löscht das Display) sind allen Reitern gemeinsam.
- **Einstellungen**: *Beim Sitzungsstart* = GIF-Galerie, Uhr, Letzte Wiedergabe oder Nichts; *Oberfläche:* wählt eine der 4 Oberflächen (der Starter startet neu, die aktuelle Anzeige läuft weiter).

**Beim Schließen des Starters läuft die Anzeige weiter** (GIF, Effekt mit seinen aktuellen Einstellungen, Audio-Visualizer oder Uhr): Der Starter übergibt sie an den Hintergrunddienst `animematrix-lecture.service`. Beim nächsten Start übernimmt er wieder, sobald etwas anderes gestartet wird (nur ein Programm kann auf die Tastatur schreiben). *■ Stopp* vor dem Schließen lässt das Display aus.

### Umschalter und Hintergrunddienste

```bash
animematrix-bascule            # an → aus; aus → letzter Modus
animematrix-bascule gif        # Hintergrund-Galerie, auch beim Sitzungsstart
animematrix-bascule horloge    # Hintergrund-Uhr, auch beim Sitzungsstart
animematrix-bascule lecture    # letzte Wiedergabe des Starters, auch beim Sitzungsstart
animematrix-bascule off        # aus, nichts beim Sitzungsstart
animematrix-bascule etat       # aktueller Modus
```

Dieselben Optionen finden sich im Rechtsklickmenü des Menüsymbols. Dahinter: `systemctl --user enable --now animematrix-galerie.service` (oder `animematrix-horloge.service`).

### Über die Kommandozeile

| Befehl | Funktion |
|---|---|
| `animematrix-effet --liste` | listet die Effekte und Visualizer auf |
| `animematrix-effet "Plasma" --brightness 60 --vitesse 1.5` | startet einen Effekt (Strg+C zum Beenden) |
| `animematrix-galerie [dossier] --brightness 60 [--originaux]` | durchläuft einen Ordner (standardmäßig der zuletzt im Starter gewählte, sonst `~/Images/AniMe-Matrix`) |
| `animematrix-lecture` | spielt die letzte Wiedergabe des Starters erneut ab (`~/.config/rog-flare2/lecture.json`) |
| `animematrix-horloge -b 25` | Uhr; `--clear` löscht das Display, `--once --text 12:34` zeigt einen Text an |
| `animematrix-convertir dossier/ [--sortie D] [--force]` | konvertiert GIFs für die Matrix (nach `dossier/matrix/`) |
| `animematrix-dessin` | Zeicheneditor |

### Audio

Die Visualizer hören auf den **Monitor der Standard-Audioausgabe** mit `parec` (PipeWire oder PulseAudio): Sie reagieren auf das, was der PC wiedergibt, nicht auf das Mikrofon. Um die Ausgabe zu ändern, die Standardausgabe des Systems ändern.

### Effekt „Keyboard React“

Er lässt das Display im Takt der Eingabe aufleuchten, dank `pynput`, das die Tasten der gesamten Sitzung liest, solange der Effekt läuft. Er funktioniert unter X11; unter Wayland empfängt er keine Tasteneingaben.

<a id="gif"></a>

## Gute GIFs vorbereiten

Das Display ist kein Rechteck: 24 versetzte Reihen, von 19 LEDs oben bis 7 unten, 3 wirklich unterscheidbare Graustufen, ein Halo zwischen benachbarten LEDs. Silhouetten, Piktogramme, kurze Texte und langsame Bewegungen wirken gut; Fotos und Videos nicht.

Der vollständige Leitfaden (Canvas-Größe, Stufen, Bildrate, Helligkeit, ImageMagick-Befehl): **[../GUIDE-GIF.md](../GUIDE-GIF.md)**.

<a id="fonctionnement"></a>

## Funktionsweise

- **Transport**: hidapi öffnet die HID-Schnittstelle Nr. 4 der Tastatur und schreibt **1024-Byte**-Frames dorthin.
- **Frame**: `60 81 00 00` + **312 Byte** (ein Helligkeitswert 0–255 pro LED, in Hardware-Reihenfolge) + Nullen bis 1024.
- **Geometrie**: 24 diagonal versetzte Reihen (19 → 7 LEDs), oder gleichwertig 12 logische Reihen mit 37 → 15 Spalten (Modell von PolyWollyWin); beide Zuordnungen wurden über alle 312 LEDs als identisch verifiziert.
- **GIF**: jedes Bild wird neu zusammengesetzt (optimierte GIFs speichern nur die Unterschiede), in Graustufen umgewandelt, auf 24 Reihen reduziert und reihenweise abgetastet.
- **Animation**: es wird kein eingebetteter Speicher verwendet; die Animation entsteht dadurch, dass der Host die Frames nacheinander sendet (~30 Bilder/s für Effekte).

Die ursprünglichen Reverse-Engineering-Notizen (USBPcap-Mitschnitte, LED-Reihenfolge, Kalibrierungspunkte) befinden sich in **[../PROTOCOL.md](../PROTOCOL.md)**; die `*.cap`-Mitschnitte und die Werkzeuge `parse_usbpcap.py` / `rog_flare2_replay_capture.py` verbleiben im Repository für alle, die tiefer einsteigen möchten.

⚠️ Sendet nicht die Pakete der AniMe-Matrix-Displays von Laptops an die Tastatur (`0x5E …`, `0xEC …`): Das ist nicht das richtige Protokoll und kann die Tastatur blockieren (ab-/wieder anstecken, oder **Fn + Esc** 10–15 s gedrückt halten).

<a id="depannage"></a>

## Fehlerbehebung

| Symptom | Wahrscheinliche Ursache | Lösung |
|---|---|---|
| `interface 4 not found` | Tastatur nicht erkannt oder keine Rechte | `lsusb \| grep 0b05:19fc`; udev-Regel installiert? ab-/wieder anstecken |
| `Permission denied` / `open failed` | udev-Regel nicht angewendet | `sudo udevadm control --reload-rules && sudo udevadm trigger`, dann wieder anstecken |
| Das Display ändert sich nicht | ein anderes Programm schreibt bereits | `animematrix-bascule off`, andere Starter oder Skripte schließen |
| Die Visualizer bleiben im Demo-Modus | kein `parec` oder kein Ton | `pulseaudio-utils` installieren, Ton abspielen |
| „Keyboard React" reagiert nicht | Wayland-Sitzung oder `pynput` fehlt | X11-Sitzung, `sudo apt install python3-pynput` |
| Die Hintergrundgalerie startet nicht | Ordner leer oder fehlt | Ordner im Starter wählen (Reiter GIF) |
| Das runde Fenster wird als Rechteck angezeigt | SHAPE-Erweiterung oder `python3-xlib` fehlt | `sudo apt install python3-xlib`, oder *Einstellungen* → *Oberfläche:* → *Klassisch* |
| Log eines Dienstes | — | `journalctl --user -u animematrix-galerie.service -f` |

<a id="depot"></a>

## Aufbau des Repositorys

| Datei | Funktion |
|---|---|
| `rog_flare2_launcher.py` | grafischer Starter (Tk) |
| `rog_flare2_i18n.py`, `locale/` | Übersetzung der Oberfläche (19 Sprachen, ein JSON-Katalog pro Sprache) |
| `rog_flare2_themes.py` | Designs der Oberfläche (ROG und Rosa) |
| `rog_flare2_ui_ronde.py` | runde Oberflächen (Drehrad + Schublade, Drehrad, abgerundet): Zeichnen, Fensterform, LED-Vorschau |
| `rog_flare2_effets.py` | Effekte und Audio-Visualizer (PolyWollyWin-Engine für Linux angepasst) |
| `polywollywin/` | Effekt-Engine von PolyWollyWin, unverändert kopiert (MIT) |
| `rog_flare2_folder_player.py` | Hintergrundgalerie (Dienst) |
| `rog_flare2_lecture.py` | Hintergrundwiedergabe: setzt fort, was der Starter beim Schließen angezeigt hat (Dienst) |
| `rog_flare2_clock_v3.py` | Uhr (Dienst) |
| `rog_flare2_bascule.sh` | Umschalter Galerie / Uhr / Aus |
| `rog_flare2_convertir.py` | GIF-Konvertierung (ImageMagick) |
| `rog_flare2_matrix_paint.py` | HID-Transport, LED-Reihenfolge, Zeicheneditor |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | Reverse-Engineering-Werkzeuge und -Mitschnitte |
| `systemd/` | Benutzerdienste |
| `packaging/` | udev-Regel, Menüeintrag, Symbol, Dateien und Skript des .deb-Pakets |
| `docs/` | GIF-Leitfaden, Protokollnotizen, Screenshots |

<a id="deb"></a>

## Das .deb-Paket bauen

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

Nur `dpkg-deb` und `bash` werden benötigt; die Version wird aus `rog_flare2_launcher.py` (`VERSION`) gelesen.

<a id="credits"></a>

## Danksagungen

- **NicRoss512** — Reverse-Engineering des Protokolls, ursprüngliche Uhr und Editor: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol). Dieses Repository geht daraus hervor; seine Historie bleibt erhalten.
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin) (MIT), Windows-Controller, dessen Effekt- und Audio-Visualizer-Engine hier wiederverwendet wird.
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), für das LED-Verhalten (Halo, wahrgenommene Stufen, Bildrate).

Unabhängiges Projekt, nicht mit ASUS verbunden. „ROG", „AniMe Matrix" und „Armoury Crate" sind Marken von ASUSTeK.

<a id="licence"></a>

## Lizenz

[MIT](../../LICENSE) für den Code dieses Repositorys. `polywollywin/` bleibt unter der MIT-Lizenz seines Autors ([polywollywin/LICENSE](../../polywollywin/LICENSE)). Die Originaldateien von NicRoss512 (`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `docs/PROTOCOL.md`, Mitschnitte) wurden ohne ausdrückliche Lizenz veröffentlicht und verbleiben bei ihrem Autor; sie werden mit Namensnennung weiterverbreitet.

<a id="soutien"></a>

## Projekt unterstützen

Wenn euch dieses Projekt nützt, hilft ein Kaffee bei der Pflege:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Kauf%20mir%20einen%20Kaffee&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — der Link findet sich auch im Reiter *Einstellungen* des Starters.

Fehlermeldungen und Ideen: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues).
