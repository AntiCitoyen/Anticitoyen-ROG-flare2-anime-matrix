<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# AniMe Matrix voor Linux — ROG Strix Flare II Animate

[![Release](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![MIT-licentie](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

Bestuur onder Linux het **AniMe Matrix**-scherm (312 mini-leds) van het **ASUS ROG Strix Flare II Animate**-toetsenbord, zonder Armoury Crate of Windows: GIF's en afbeeldingen, achtergrondgalerij, klok, 19 geanimeerde effecten, 7 audiovisualisaties, LED-voor-LED tekenen.

De interface van de toepassing is beschikbaar in 19 talen: ze volgt automatisch de systeemtaal en kan worden gewijzigd in het tabblad *Instellingen* → *Taal:*.

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · **🇳🇱 Nederlands** · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/nl/interface-drawer.png" alt="Draaiknop + lade" width="760"><br><em>Draaiknop + lade (standaardinterface)</em></p>

| Draaiknop | Afgerond | Klassiek |
|:---:|:---:|:---:|
| <img src="../captures/nl/interface-dial.png" alt="Draaiknop" width="260"> | <img src="../captures/nl/interface-rounded.png" alt="Afgerond" width="190"> | <img src="../captures/nl/interface-classic.png" alt="Klassiek" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## Inhoud

- [Wat het project doet](#projet)
- [Ondersteunde hardware](#materiel)
- [Installatie](#installation)
- [Gebruik](#utilisation)
- [Goede GIF's voorbereiden](#gif)
- [Hoe het werkt](#fonctionnement)
- [Problemen oplossen](#depannage)
- [Structuur van de repository](#depot)
- [Het .deb-pakket bouwen](#deb)
- [Credits](#credits)
- [Licentie](#licence)
- [Het project steunen](#soutien)

---

<a id="projet"></a>

## Wat het project doet

ASUS levert het AniMe Matrix-scherm van dit toetsenbord alleen onder Windows (Armoury Crate). Dit project communiceert rechtstreeks met het toetsenbord via USB HID en biedt:

- **Een grafische launcher** (`animematrix`), naar keuze uit **4 interfaces**: *Draaiknop + lade* (rond venster met een instellingenpaneel dat naar rechts uitschuift, de standaard), *Draaiknop* (alles in de cirkel), *Afgerond* (zeer afgeronde hoeken, helderheidswieltje) en *Klassiek* (tabbladen). De ronde interfaces tonen **live de 312 leds**, precies zoals ze naar het toetsenbord worden verzonden. Vier bedieningsblokken:
  - **GIF / afbeeldingen**: een of meerdere bestanden afspelen, of een hele map als galerij, in lus; GIF's converteren voor de matrix.
  - **Effecten**: 19 animaties (regen in Matrix-stijl, plasma, vuur, sterren, vuurwerk, bliksem, metaballs, golf, slang, lopende tekst, gestileerde klok, reactie op het toetsenbord…), aanpasbaar terwijl ze lopen.
  - **Audio**: 7 visualisaties die reageren op het geluid dat de pc afspeelt (spectrum, KITT/KARR, starburst, oscilloscoop, audiovuur…).
  - **Instellingen**: wat wordt weergegeven bij het openen van de sessie, taal, thema en interface, tekeneditor, links van het project.
- **Een klok** UU:MM, vanuit de launcher of als achtergrondservice.
- **Een achtergrondgalerij**: een `systemd --user`-service die vanaf het openen van de sessie een map met GIF's laat doorlopen.
- **Een schakelaar met één klik** (`animematrix-bascule`): het menupictogram zet het scherm aan of uit; met de rechtermuisknop kies je GIF-galerij, Klok of Scherm uit.
- **Een op de matrix afgestemde GIF-conversie** (`animematrix-convertir`): 19×24, grijstinten, 3 niveaus, zonder dithering — zie [../GUIDE-GIF.md](../GUIDE-GIF.md).
- **Een tekeneditor** LED voor LED (`animematrix-dessin`).
- **11 thema's**: 5 geïnspireerd op ROG (Classic, Strix, Glitch, Gold, Carbon), 5 roze (Sakura, Kauwgom, Roségoud, Lavendelroze, Roze nacht) en dat van het systeem, te kiezen via *Instellingen* → *Thema:*.
- **Ingebouwde updates**: *Instellingen* → *Naar updates zoeken*; automatische controle eens per dag (uit te schakelen). De starter downloadt de `.deb` van de nieuwste GitHub-release, controleert de SHA-256-controlesom en installeert hem na het vragen van het beheerderswachtwoord (`pkexec`).
- **Laag verbruik**: de GIF's worden beeld voor beeld gedecodeerd; een galerij van 400 GIF's draait op ongeveer 25 MB geheugen.

<a id="materiel"></a>

## Ondersteunde hardware

| Toetsenbord | USB | Interface |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | HID, interface 4 (usage page `0xFF02`) |

De AniMe Matrix-schermen van ROG-**laptops** (Zephyrus G14, enz.) gebruiken een ander protocol: ze worden hier **niet** ondersteund (zie in plaats daarvan `asusctl`).

Getest op Ubuntu 26.04 (X11, PipeWire). Elke distributie met Python ≥ 3.10, hidapi, Tk en systemd zou moeten werken.

<a id="installation"></a>

## Installatie

### .deb-pakket (Debian, Ubuntu, Mint, Pop!_OS…)

1. Download `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` van de [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)-pagina.
2. Installeer het (apt haalt de afhankelijkheden op):
   ```bash
   sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb
   ```
3. **Koppel het toetsenbord los en sluit het opnieuw aan** (de udev-regel geeft de ingelogde gebruiker toegang).
4. Start **AniMe Matrix** vanuit het toepassingenmenu, of `animematrix` in een terminal.

Het pakket installeert:

| Onderdeel | Locatie |
|---|---|
| Programma's | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| Commando's | `animematrix`, `animematrix-bascule`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-convertir`, `animematrix-dessin`, `animematrix-lecture` |
| Gebruikersservices | `/usr/lib/systemd/user/animematrix-galerie.service`, `animematrix-horloge.service`, `animematrix-lecture.service` (standaard niet ingeschakeld) |
| udev-regel | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| Menu en pictogram | `animematrix.desktop`, pictogram `animematrix` |

Verwijderen: `sudo apt remove anticitoyen-rog-flare2-anime-matrix`.

### Vanuit de broncode

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# toegang tot het toetsenbord zonder root
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# daarna toetsenbord loskoppelen/opnieuw aansluiten
.venv/bin/python rog_flare2_launcher.py
```

Nuttige systeemtools: `imagemagick` (conversie), `pulseaudio-utils` (`parec`, voor audio), `zenity` (bestandskiezers), `libnotify-bin` (meldingen van de schakelaar).

Voor de achtergrondservices vanuit de broncode kopieer je `systemd/*.service` naar `~/.config/systemd/user/`, waarbij je de regels `ExecStart=` vervangt door het pad naar `.venv/bin/python` en het script (`rog_flare2_folder_player.py`, `rog_flare2_clock_v3.py`), en voer je daarna `systemctl --user daemon-reload` uit.

<a id="utilisation"></a>

## Gebruik

### De launcher

`animematrix` (of het item **AniMe Matrix** in het menu).

In de ronde interfaces openen de ronde knoppen de blokken *GIF*, *Effecten*, *Audio* en *Instellingen* (in de lade of in de cirkel); *Klok* en *Stoppen* werken meteen; de boog onderaan regelt de helderheid; het venster wordt verplaatst door het aan de achtergrond te slepen; de kleine knoppen bovenaan minimaliseren of sluiten het. De ronde vorm gebruikt de X11 SHAPE-extensie (pakket `python3-xlib`); zonder deze wordt dezelfde interface in een rechthoekig venster weergegeven.

- **GIF / afbeeldingen**: *GIF's/afbeeldingen…* voor een selectie, *Map (galerij)…* voor een hele map. De gekozen map wordt ook die van de achtergrondgalerij. *Geconverteerde versies verkiezen* leest `dossier/matrix/nom.gif` indien aanwezig (geproduceerd door de conversie).
- **Effecten** en **Audio**: kiezen, instellen, *▶ Effect starten*. De schuifregelaars werken live; *Tempo* versnelt of vertraagt de animatie.
- **Helderheid**, **🕒 Klok**, **■ Stoppen** (wat het scherm wist) zijn gemeenschappelijk voor alle tabbladen.
- **Instellingen**: *Bij het opstarten van de sessie:* = GIF-galerij, Klok, Laatste weergave of Niets; *Interface:* kiest een van de 4 interfaces (de launcher herstart, wat wordt weergegeven blijft doorspelen).

**Wanneer je de launcher sluit, blijft wat wordt weergegeven doorspelen** (GIF, effect met de huidige instellingen, audiovisualisatie of klok): de launcher draagt het over aan de achtergrondservice `animematrix-lecture.service`. Bij de volgende start neemt hij het weer over zodra er iets anders wordt gestart (slechts één programma kan naar het toetsenbord schrijven). *■ Stoppen* voor het sluiten laat het scherm uit.

### Schakelaar en achtergrondservices

```bash
animematrix-bascule            # aan → uit ; uit → laatste modus
animematrix-bascule gif        # achtergrondgalerij, ook bij het openen van de sessie
animematrix-bascule horloge    # achtergrondklok, ook bij het openen van de sessie
animematrix-bascule lecture    # laatste weergave van de launcher, ook bij het openen van de sessie
animematrix-bascule off        # uit, niets bij het opstarten
animematrix-bascule etat       # huidige modus
```

Dezelfde keuzes staan in het rechtermuisknopmenu van het menupictogram. Onder de motorkap: `systemctl --user enable --now animematrix-galerie.service` (of `animematrix-horloge.service`).

### Vanaf de opdrachtregel

| Commando | Functie |
|---|---|
| `animematrix-effet --liste` | toont de lijst met effecten en visualisaties |
| `animematrix-effet "Plasma" --brightness 60 --vitesse 1.5` | start een effect (Ctrl+C om te stoppen) |
| `animematrix-galerie [dossier] --brightness 60 [--originaux]` | doorloopt een map (standaard de laatst gekozen map in de launcher, anders `~/Images/AniMe-Matrix`) |
| `animematrix-lecture` | speelt de laatste weergave van de launcher opnieuw af (`~/.config/rog-flare2/lecture.json`) |
| `animematrix-horloge -b 25` | klok; `--clear` wist het scherm, `--once --text 12:34` toont een tekst |
| `animematrix-convertir dossier/ [--sortie D] [--force]` | converteert GIF's voor de matrix (in `dossier/matrix/`) |
| `animematrix-dessin` | tekeneditor |

### Audio

De visualisaties luisteren naar de **monitor van de standaard audio-uitgang** via `parec` (PipeWire of PulseAudio): ze reageren op wat de pc afspeelt, niet op de microfoon. Om van uitgang te wisselen, wijzig je de standaarduitgang van het systeem.

### Effect « Keyboard React »

Dit laat het scherm oplichten op het ritme van het typen dankzij `pynput`, dat toetsaanslagen van de hele sessie leest zolang het effect actief is. Het werkt onder X11; onder Wayland ontvangt het geen toetsaanslagen.

<a id="gif"></a>

## Goede GIF's voorbereiden

Het scherm is geen rechthoek: 24 verspringende rijen, van 19 leds bovenaan tot 7 onderaan, 3 echt onderscheiden grijstinten, een halo tussen naburige leds. Silhouetten, pictogrammen, korte teksten en trage bewegingen komen goed over; foto's en video's niet.

De volledige gids (canvasgrootte, niveaus, framerate, helderheid, ImageMagick-commando): **[../GUIDE-GIF.md](../GUIDE-GIF.md)**.

<a id="fonctionnement"></a>

## Hoe het werkt

- **Transport**: hidapi opent HID-interface nr. 4 van het toetsenbord en schrijft er frames van **1024 bytes** naartoe.
- **Frame**: `60 81 00 00` + **312 bytes** (een helderheid van 0–255 per led, in hardwarevolgorde) + nullen tot 1024.
- **Geometrie**: 24 diagonaal verspringende rijen (19 → 7 leds), of gelijkwaardig 12 logische rijen van 37 → 15 kolommen (model van PolyWollyWin); beide indelingen zijn geverifieerd als identiek over de 312 leds.
- **GIF**: elk beeld wordt herbouwd (geoptimaliseerde GIF's bewaren alleen de verschillen), omgezet naar grijstinten, teruggebracht tot 24 rijen en rij per rij bemonsterd.
- **Animatie**: er wordt geen ingebouwd geheugen gebruikt; de animatie bestaat eruit dat de host de frames na elkaar verstuurt (~30 fps voor de effecten).

De oorspronkelijke reverse-engineeringnotities (USBPcap-captures, ledvolgorde, kalibratiepunten) staan in **[../PROTOCOL.md](../PROTOCOL.md)**; de `*.cap`-captures en de tools `parse_usbpcap.py` / `rog_flare2_replay_capture.py` blijven in de repository voor wie verder wil gaan.

⚠️ Stuur geen pakketten van de AniMe Matrix van laptops (`0x5E …`, `0xEC …`) naar het toetsenbord: dat is niet het juiste protocol en kan het toetsenbord blokkeren (loskoppelen/opnieuw aansluiten, of **Fn + Esc** 10–15 s ingedrukt houden).

<a id="depannage"></a>

## Problemen oplossen

| Symptoom | Waarschijnlijke oorzaak | Oplossing |
|---|---|---|
| `interface 4 not found` | toetsenbord niet herkend of geen rechten | `lsusb \| grep 0b05:19fc`; udev-regel geïnstalleerd? loskoppelen/opnieuw aansluiten |
| `Permission denied` / `open failed` | udev-regel niet toegepast | `sudo udevadm control --reload-rules && sudo udevadm trigger`, daarna opnieuw aansluiten |
| Het scherm verandert niet | een ander programma schrijft al | `animematrix-bascule off`, andere launchers of scripts sluiten |
| De visualisaties blijven in demomodus | geen `parec` of geen geluid | `pulseaudio-utils` installeren, geluid afspelen |
| « Keyboard React » reageert niet | Wayland-sessie of `pynput` ontbreekt | X11-sessie, `sudo apt install python3-pynput` |
| De achtergrondgalerij start niet | map leeg of ontbreekt | een map kiezen in de launcher (tabblad GIF) |
| Het ronde venster wordt als een rechthoek weergegeven | SHAPE-extensie of `python3-xlib` ontbreekt | `sudo apt install python3-xlib`, of *Instellingen* → *Interface:* → *Klassiek* |
| Logboek van een service | — | `journalctl --user -u animematrix-galerie.service -f` |

<a id="depot"></a>

## Structuur van de repository

| Bestand | Functie |
|---|---|
| `rog_flare2_launcher.py` | grafische launcher (Tk) |
| `rog_flare2_i18n.py`, `locale/` | vertaling van de interface (19 talen, één JSON-catalogus per taal) |
| `rog_flare2_themes.py` | thema's van de interface (ROG en roze) |
| `rog_flare2_ui_ronde.py` | ronde interfaces (draaiknop + lade, draaiknop, afgerond): tekenen, vorm van het venster, ledvoorbeeld |
| `rog_flare2_effets.py` | effecten en audiovisualisaties (PolyWollyWin-engine aangepast voor Linux) |
| `polywollywin/` | effectenengine van PolyWollyWin, ongewijzigd overgenomen (MIT) |
| `rog_flare2_folder_player.py` | achtergrondgalerij (service) |
| `rog_flare2_lecture.py` | achtergrondweergave: hervat wat de launcher weergaf bij het sluiten (service) |
| `rog_flare2_clock_v3.py` | klok (service) |
| `rog_flare2_bascule.sh` | schakelaar galerij / klok / uit |
| `rog_flare2_convertir.py` | GIF-conversie (ImageMagick) |
| `rog_flare2_matrix_paint.py` | HID-transport, ledvolgorde, tekeneditor |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | reverse-engineeringtools en -captures |
| `systemd/` | gebruikersservices |
| `packaging/` | udev-regel, menu-item, pictogram, bestanden en script van het .deb-pakket |
| `docs/` | GIF-gids, protocolnotities, schermafbeeldingen |

<a id="deb"></a>

## Het .deb-pakket bouwen

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

Alleen `dpkg-deb` en `bash` zijn nodig; de versie wordt gelezen uit `rog_flare2_launcher.py` (`VERSION`).

<a id="credits"></a>

## Credits

- **NicRoss512** — reverse engineering van het protocol, oorspronkelijke klok en editor: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol). Deze repository is daarvan afgeleid; de geschiedenis ervan is bewaard.
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin) (MIT), Windows-controller waarvan de effecten- en audiovisualisatie-engine hier wordt hergebruikt.
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), voor het gedrag van de leds (halo, waargenomen niveaus, framerate).

Onafhankelijk project, niet gelieerd aan ASUS. « ROG », « AniMe Matrix » en « Armoury Crate » zijn handelsmerken van ASUSTeK.

<a id="licence"></a>

## Licentie

[MIT](../../LICENSE) voor de code van deze repository. `polywollywin/` blijft onder de MIT-licentie van de oorspronkelijke auteur ([../../polywollywin/LICENSE](../../polywollywin/LICENSE)). De oorspronkelijke bestanden van NicRoss512 (`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `../PROTOCOL.md`, captures) zijn zonder expliciete licentie gepubliceerd en blijven eigendom van hun auteur; ze worden herverspreid met bronvermelding.

<a id="soutien"></a>

## Het project steunen

Als je iets hebt aan dit project, helpt een kopje koffie om het te onderhouden:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Trakteer%20me%20op%20een%20koffie&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — de link staat ook op het tabblad *Instellingen* van de launcher.

Bugmeldingen en ideeën: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues).
