<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# AniMe Matrix dla Linuksa — ROG Strix Flare II Animate

[![Release](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![CI](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml)
[![Licencja MIT](https://img.shields.io/badge/licencja-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-wesprzyj-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

Sterowanie pod Linuksem ekranem **AniMe Matrix** (312 mini-diod LED) klawiatury **ASUS ROG Strix Flare II Animate**, bez Armoury Crate ani Windows: GIF-y i galeria, zegar, efekty i wizualizatory audio, gry, monitor systemu, powiadomienia pulpitu, harmonogram, edytor animacji, wspólna biblioteka, zsynchronizowane kolory klawiatury.

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · **🇵🇱 Polski** · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/pl/interface-drawer.png" alt="Tarcza + szuflada" width="760"><br><em>Tarcza + szuflada (interfejs domyślny)</em></p>

| Tarcza | Zaokrąglony | Klasyczny |
|:---:|:---:|:---:|
| <img src="../captures/pl/interface-dial.png" alt="Tarcza" width="260"> | <img src="../captures/pl/interface-rounded.png" alt="Zaokrąglony" width="190"> | <img src="../captures/pl/interface-classic.png" alt="Klasyczny" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## Spis treści

- [Co robi projekt](#projet)
- [Obsługiwany sprzęt](#materiel)
- [Instalacja](#installation)
- [Użytkowanie](#utilisation)
- [Przygotowanie dobrych GIF-ów](#gif)
- [Jak to działa](#fonctionnement)
- [Rozwiązywanie problemów](#depannage)
- [Organizacja repozytorium](#depot)
- [Budowanie pakietów](#deb)
- [Podziękowania](#credits)
- [Licencja](#licence)
- [Wsparcie projektu](#soutien)

---

<a id="projet"></a>

## Co robi projekt

ASUS udostępnia ekran AniMe Matrix tej klawiatury wyłącznie pod Windows (Armoury Crate). Ten projekt komunikuje się bezpośrednio z klawiaturą przez USB HID i dostarcza:

**Wyświetlanie**
- **GIF-y i obrazy**: pojedynczy plik, wybór plików lub cały folder jako galeria; odtwarzanie strumieniowe (galeria 400 GIF-ów mieści się w ~25 MB pamięci).
- **Zegar** GG:MM.
- **19 animowanych efektów** (deszcz w stylu Matrix, plazma, ogień, gwiazdy, fajerwerki, błyskawice, metaballe, fala, przewijany tekst…) oraz **7 wizualizatorów audio** reagujących na dźwięk odtwarzany przez komputer.
- **Monitor systemu**: CPU, RAM, GPU, temperatura, przepustowość sieci i godzina, w formie wskaźników.
- **Aktualnie odtwarzany utwór**: przy zmianie utworu „WYKONAWCA - TYTUŁ” przewija się raz, a następnie pojawia się wizualizator (Spotify, VLC, Rhythmbox, przeglądarki… przez MPRIS).
- **Powiadomienia pulpitu**: „APLIKACJA: TYTUŁ” wyświetla się jako nakładka, po czym odtwarzanie wraca do poprzedniego stanu (domyślnie wyłączone, lista dozwolonych aplikacji).
- **Grywalne gry** na klawiaturze: Snake, Pong, Tetris, Breakout, z rekordami.

**Tworzenie**
- **Edytor animacji** klatka po klatce, na rzeczywistej geometrii ekranu: 3 poziomy, oś czasu, warstwa-widmo, przesunięcie, kopiuj-wklej, podgląd, wysyłanie do klawiatury, eksport GIF.
- **Wspólna biblioteka animacji**: przeglądaj, odtwarzaj, dodawaj do swojej galerii, zgłaszaj własne.
- **Inteligentna konwersja** GIF-ów: kadrowanie na obiekcie, jasny obiekt na czarnym tle, wzmocnione kontury, 3 poziomy.
- **Wierny podgląd** przed wysłaniem: symulowane wyświetlanie ekranu (rzeczywisty układ, poświata między diodami).
- **Efekty jako rozszerzenia**: plik Python umieszczony w folderze dodaje efekt (zob. [../EXTENSIONS.md](../EXTENSIONS.md)).

**Automatyzacja**
- **Demon `animematrixd`**: jedyny właściciel ekranu, kontynuuje wyświetlanie po zamknięciu launchera; polecenie `animematrix-ctl` i opcjonalne lokalne API HTTP.
- **Harmonogram**: przedziały czasowe (dni, także noc) z zegarem, galerią, monitorem, aktualnie odtwarzanym utworem lub wyłączonym ekranem; czarny ekran, gdy sesja jest zablokowana, w uśpieniu lub gdy aplikacja działa w pełnym ekranie.
- **Kolory klawiatury przez OpenRGB**: kolor motywu na klawiszach lub pulsowanie zsynchronizowane z ekranem.
- **Ikona na pasku systemowym**: szybkie menu (tryby, jasność).

**Wygoda**
- **4 interfejsy** (*Tarcza + szuflada* domyślnie, *Tarcza*, *Zaokrąglony*, *Klasyczny*) z **podglądem 312 diod LED na żywo**, **11 motywami** (5 ROG, 5 różowych, systemowy) i **19 językami**.
- **Wbudowane aktualizacje**: launcher pobiera najnowsze wydanie, sprawdza jego odcisk SHA-256 i instaluje je (hasło administratora); albo `apt upgrade` z repozytorium APT.

<a id="materiel"></a>

## Obsługiwany sprzęt

| Urządzenie | USB | Stan |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | obsługiwane (HID, interfejs 4, usage page `0xFF02`) |
| Ekrany AniMe Matrix laptopów ROG (G14, G16…) | różne | **eksperymentalne** przez `asusctl`, nietestowane na sprzęcie (zob. [Użytkowanie](#utilisation)) |

Testowano na Ubuntu 26.04 (X11, PipeWire, Cinnamon). Każda dystrybucja z Pythonem ≥ 3.10, hidapi, Tk i systemd powinna działać.

<a id="installation"></a>

## Instalacja

### Repozytorium APT (Debian, Ubuntu, Mint, Pop!_OS…) — aktualizacje przez `apt upgrade`

```bash
curl -fsSL https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix/animematrix.gpg \
  | sudo tee /usr/share/keyrings/animematrix.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/animematrix.gpg] https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix stable main" \
  | sudo tee /etc/apt/sources.list.d/animematrix.list
sudo apt update && sudo apt install anticitoyen-rog-flare2-anime-matrix
```

Następnie **odłącz i podłącz ponownie klawiaturę** (reguła udev nadaje dostęp zalogowanemu użytkownikowi) i uruchom **AniMe Matrix** z menu.

### Inne formaty (strona [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest))

| System | Plik | Instalacja |
|---|---|---|
| Debian, Ubuntu… | `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` | `sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb` |
| Fedora, openSUSE… | `anticitoyen-rog-flare2-anime-matrix-<version>-1.noarch.rpm` | `sudo dnf install ./anticitoyen-rog-flare2-anime-matrix-*.noarch.rpm` |
| Arch, Manjaro… | `anticitoyen-rog-flare2-anime-matrix-<version>-1-any.pkg.tar.zst` | `sudo pacman -U anticitoyen-rog-flare2-anime-matrix-*.pkg.tar.zst` |
| Wszystkie (Flatpak) | `AniMeMatrix-<version>.flatpak` | `flatpak install --user AniMeMatrix-*.flatpak` (zainstaluj też regułę udev poniżej; bez wizualizatorów audio) |

Pakiet instaluje:

| Element | Lokalizacja |
|---|---|
| Programy | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| Polecenia | `animematrix`, `animematrixd`, `animematrix-ctl`, `animematrix-bascule`, `animematrix-animation`, `animematrix-apercu`, `animematrix-convertir`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-dessin`, `animematrix-tray` |
| Usługa użytkownika | `/usr/lib/systemd/user/animematrixd.service` (włączona dla wszystkich sesji) |
| Reguła udev | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| Menu i ikona | `animematrix.desktop`, ikona `animematrix` |

### Ze źródeł

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# dostęp do klawiatury bez roota
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# następnie odłącz/podłącz ponownie klawiaturę
.venv/bin/python rog_flare2_launcher.py
```

Przydatne narzędzia systemowe: `imagemagick` (klasyczna konwersja), `pulseaudio-utils` (`parec`, do audio), `zenity` (wybór plików), `libnotify-bin` (powiadomienia), `python3-gi` i `gir1.2-ayatanaappindicator3-0.1` (ikona na pasku systemowym), `openrgb` (kolory klawiszy).

<a id="utilisation"></a>

## Użytkowanie

### Launcher

`animematrix` (lub wpis **AniMe Matrix** w menu).

W okrągłych interfejsach okrągłe przyciski otwierają bloki *GIF*, *Efekty*, *Audio* i *Ustawienia* (w szufladzie lub w kole); *Zegar* i *Zatrzymaj* działają natychmiast; dolny łuk reguluje jasność; okno przesuwa się, przeciągając je za tło; małe przyciski u góry minimalizują lub zamykają. Okrągły kształt wykorzystuje rozszerzenie X11 SHAPE (pakiet `python3-xlib`); bez niego ten sam interfejs wyświetla się w prostokątnym oknie.

- **GIF / obrazy**: *GIF/obrazy…* lub *Folder (galeria)…*; *Wierna geometria* zachowuje proporcje (róg przycina obraz zamiast go rozciągać); *👁 Wierny podgląd (przed wysłaniem)* pokazuje wynik bez niczego wysyłania; *🎞 Utwórz animację (edytor)*; *📚 Biblioteka animacji*; *Inteligentna konwersja* do przekształcania GIF-ów.
- **Efekty** i **Audio**: wybierz, ustaw, *▶ Uruchom efekt*. Suwaki działają na żywo; *Tempo* przyspiesza lub spowalnia całą animację. Gry gra się strzałkami, spacją i Enterem, gdy okno launchera jest na pierwszym planie.
- **Jasność**, **🕒 Zegar**, **■ Zatrzymaj** (co czyści ekran) są wspólne dla wszystkich zakładek.
- **Ustawienia**: start sesji (Galeria GIF, Zegar, Ostatnie odtwarzanie lub Nic), język, motyw, interfejs, powiadomienia pulpitu, kolory klawiatury (OpenRGB), *Harmonogram…*, ikona na pasku systemowym, folder rozszerzeń, aktualizacje.

**Zamknięcie launchera niczego nie przerywa**: demon `animematrixd` kontynuuje wyświetlanie. *■ Zatrzymaj* wyłącza ekran.

### Demon i wiersz poleceń

```bash
animematrix-ctl etat                               # co jest wyświetlane
animematrix-ctl gif ~/Images/AniMe-Matrix --fidele # galeria (folder lub pliki)
animematrix-ctl effet "Plasma" --param speed=250   # efekt i ustawienia
animematrix-ctl horloge
animematrix-ctl texte "Bonjour"
animematrix-ctl notifier "Café prêt" --duree 5     # nakładka, potem powrót
animematrix-ctl luminosite 60
animematrix-ctl stop
```

| Komenda | Rola |
|---|---|
| `animematrix-bascule [gif\|horloge\|lecture\|off\|etat]` | przełącznik (także pod prawym przyciskiem ikony w menu); wybrany tryb jest też trybem startu sesji |
| `animematrixd --http 8765` | demon z lokalnym API HTTP (`POST http://127.0.0.1:8765/api`, ten sam JSON co gniazdo) |
| `animematrix-animation [plik.gif]` | edytor animacji |
| `animematrix-apercu plik.gif -o apercu.gif` | wierny podgląd GIF-a (plik) |
| `animematrix-convertir folder/ [--fidele] [--classique]` | konwertuje GIF-y pod matrycę (do `folder/matrix/`) |
| `animematrix-effet --liste` | wyświetla listę efektów i wizualizatorów |
| `animematrix-dessin` | edytor dioda po diodzie (oddaje kontrolę demonowi po zamknięciu) |

### Audio

Wizualizatory nasłuchują **monitora domyślnego wyjścia dźwięku** za pomocą `parec` (PipeWire lub PulseAudio): reagują na to, co odtwarza komputer, a nie na mikrofon.

### Efekt „Keyboard React”

Zapala ekran w rytm pisania dzięki `pynput`, który odczytuje klawisze z całej sesji, dopóki efekt działa. Działa pod X11; pod Waylandem nie odbiera klawiszy.

### Kolory klawiatury (OpenRGB)

*Ustawienia* → *Kolory klawiatury (OpenRGB)*: kolor motywu lub pulsowanie zsynchronizowane z ekranem. Demon uruchamia w razie potrzeby `openrgb --server`. OpenRGB nie zna poprzedniego podświetlenia klawiatury: aby przywrócić efekt zapisany w klawiaturze, odłącz ją i podłącz ponownie.

### Laptopy ROG (eksperymentalne)

Wpisz `portable-asusctl` w `~/.config/rog-flare2/materiel`, a następnie zrestartuj demona: ramki przechodzą przez `asusctl anime image` (maksymalnie 5 klatek na sekundę). Nietestowane na prawdziwym laptopie: opinie mile widziane w zgłoszeniach.

<a id="gif"></a>

## Przygotowanie dobrych GIF-ów

Ekran nie jest prostokątem: 24 przesunięte rzędy, od 19 diod na górze do 7 na dole (prawa krawędź pionowa, lewa po przekątnej), 3 naprawdę rozróżnialne poziomy szarości, poświata między sąsiednimi diodami. Sylwetki, piktogramy, krótkie teksty i powolny ruch wyglądają dobrze; zdjęcia i wideo — słabo.

Pełny przewodnik (płótno, poziomy, tempo, konwersja, wierna geometria): **[../GUIDE-GIF.md](../GUIDE-GIF.md)**.

<a id="fonctionnement"></a>

## Jak to działa

- **Transport**: hidapi otwiera interfejs HID nr 4 klawiatury i zapisuje do niego ramki o długości **1024 bajtów**; klawiatura odsyła każdą ramkę.
- **Ramka**: `60 81 00 00` + **312 bajtów** (jasność 0–255 na diodę, w kolejności sprzętowej) + zera do 1024.
- **Geometria**: 24 przesunięte rzędy (rząd r obejmuje kolumny (r+1)//2 do 18), lub równoważnie 12 rzędów logicznych po 37 → 15 kolumn (model PolyWollyWin); oba odwzorowania zweryfikowano jako identyczne dla wszystkich 312 diod.
- **Demon**: `animematrixd` samodzielnie zarządza klawiaturą; podstawowe odtwarzanie i nakładka (powiadomienia); gniazdo JSON `$XDG_RUNTIME_DIR/animematrix.sock`; automatyczne ponowne łączenie z klawiaturą.
- **Animacja**: host wysyła ramki jedna po drugiej (~30 kl./s dla efektów); wewnętrzna pamięć klawiatury nie jest wykorzystywana (badania: [../RECHERCHE-MEMOIRE.md](../RECHERCHE-MEMOIRE.md)).

Oryginalne notatki z inżynierii wstecznej znajdują się w **[../PROTOCOL.md](../PROTOCOL.md)**; przechwyty `*.cap` oraz narzędzia `parse_usbpcap.py` / `rog_flare2_replay_capture.py` pozostają w repozytorium.

⚠️ Nie wysyłaj do klawiatury pakietów przeznaczonych dla AniMe Matrix laptopów (`0x5E …`, `0xEC …`): to niewłaściwy protokół, który może zablokować klawiaturę (odłącz/podłącz ponownie, albo przytrzymaj **Fn + Esc** przez 10–15 s).

<a id="depannage"></a>

## Rozwiązywanie problemów

| Objaw | Prawdopodobna przyczyna | Rozwiązanie |
|---|---|---|
| `interface 4 not found` | klawiatura niewidoczna lub brak uprawnień | `lsusb \| grep 0b05:19fc` ; czy reguła udev jest zainstalowana? odłącz/podłącz |
| `Permission denied` / `open failed` | reguła udev nie została zastosowana | `sudo udevadm control --reload-rules && sudo udevadm trigger`, następnie podłącz ponownie |
| „Usługa animematrixd niedostępna” | demon zatrzymany | `systemctl --user restart animematrixd.service` lub `animematrixd &` |
| Ekran się nie zmienia | inny program zapisuje na klawiaturze | zamknij stare skrypty; `animematrix-ctl etat` |
| Wizualizatory pozostają w trybie demo | brak `parec` lub brak dźwięku | zainstaluj `pulseaudio-utils`, odtwórz dźwięk |
| „Keyboard React” nie reaguje | sesja Wayland lub brak `pynput` | sesja X11, `sudo apt install python3-pynput` |
| Okrągłe okno wyświetla się jako prostokąt | brak rozszerzenia SHAPE lub `python3-xlib` | `sudo apt install python3-xlib`, albo *Ustawienia* → *Interfejs:* → *Klasyczny* |
| Klawisze pozostają w jednym kolorze po OpenRGB | OpenRGB nie odtwarza oryginalnego efektu | odłącz i podłącz ponownie klawiaturę |
| Dziennik demona | — | `journalctl --user -u animematrixd.service -f` |

<a id="depot"></a>

## Organizacja repozytorium

| Plik | Rola |
|---|---|
| `rog_flare2_launcher.py` | launcher graficzny (Tk) |
| `rog_flare2_ui_ronde.py`, `rog_flare2_themes.py` | okrągłe interfejsy, motywy |
| `rog_flare2_i18n.py`, `locale/` | tłumaczenie (19 języków; `locale/_cles.json` = teksty do przetłumaczenia) |
| `rog_flare2_demon.py`, `rog_flare2_ctl.py` | demon `animematrixd`, klient i polecenie `animematrix-ctl` |
| `rog_flare2_core.py` | odtwarzanie GIF-ów strumieniowo, zegar, geometria |
| `rog_flare2_effets.py`, `polywollywin/` | efekty i wizualizatory (silnik PolyWollyWin, MIT), rozszerzenia |
| `rog_flare2_infos.py`, `rog_flare2_mpris.py`, `rog_flare2_jeux.py` | monitor systemu, aktualnie odtwarzany utwór, gry |
| `rog_flare2_notifs.py`, `rog_flare2_programme.py`, `rog_flare2_ui_programme.py` | powiadomienia, harmonogram i wyzwalacze |
| `rog_flare2_openrgb.py`, `rog_flare2_tray.py`, `rog_flare2_portable.py` | kolory przez OpenRGB, ikona na pasku systemowym, laptopy (eksperymentalne) |
| `rog_flare2_animation.py`, `rog_flare2_simulateur.py`, `rog_flare2_convertir.py` | edytor animacji, symulator, konwersja |
| `rog_flare2_bibliotheque.py`, `bibliotheque/` | biblioteka animacji (katalog, GIF CC0) |
| `rog_flare2_maj.py` | aktualizacje z wydań |
| `rog_flare2_matrix_paint.py`, `rog_flare2_clock_v3.py`, `rog_flare2_folder_player.py` | transport HID i edytor LED, zegar, galeria (narzędzia oryginalne) |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | inżynieria wsteczna |
| `examples/effets/` | przykład rozszerzenia |
| `tests/` | testy (w tym interfejsy poprzez prawdziwe kliknięcia) |
| `systemd/`, `packaging/` | usługa użytkownika; .deb, RPM, Arch, Flatpak, repozytorium APT |
| `docs/` | przewodnik GIF, rozszerzenia, protokół, badania, zrzuty ekranu, przetłumaczone README |

<a id="deb"></a>

## Budowanie pakietów

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

`packaging/install.sh` instaluje projekt w dowolnej strukturze katalogów; służy do budowy .deb, RPM (`packaging/rpm/`), pakietu Arch (`packaging/aur/`) i Flatpaka (`packaging/flatpak/`). Przy każdym opublikowanym wydaniu GitHub buduje RPM, pakiet Arch i Flatpak oraz aktualizuje podpisane repozytorium APT. Wersja jest odczytywana z `rog_flare2_core.py` (`VERSION`). Testy: `python -m pytest tests`.

<a id="credits"></a>

## Podziękowania

- **NicRoss512** — inżynieria wsteczna protokołu, oryginalny zegar i edytor: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol). To repozytorium wychodzi z tego projektu; jego historia commitów została zachowana.
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin) (MIT), kontroler dla Windows, którego silnik efektów i wizualizatorów audio został tu wykorzystany.
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), za opis zachowania diod (poświata, odbierane poziomy, tempo).
- **asus-linux** — [asusctl](https://gitlab.com/asus-linux/asusctl), używane dla ekranów laptopów.

Projekt niezależny, niezwiązany z ASUS. „ROG”, „AniMe Matrix” i „Armoury Crate” są znakami towarowymi ASUSTeK.

<a id="licence"></a>

## Licencja

[MIT](../../LICENSE) dla kodu tego repozytorium; animacje z `bibliotheque/` na licencji CC0. `polywollywin/` pozostaje na licencji MIT swojego autora ([../../polywollywin/LICENSE](../../polywollywin/LICENSE)). Oryginalne pliki NicRoss512 (`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `../PROTOCOL.md`, przechwyty) zostały opublikowane bez jawnej licencji i pozostają własnością ich autora; są redystrybuowane z podaniem źródła.

<a id="soutien"></a>

## Wsparcie projektu

Jeśli ten projekt jest dla Ciebie przydatny, kawa pomaga w jego utrzymaniu:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Postaw%20mi%20kaw%C4%99&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — link znajduje się także w zakładce *Ustawienia* launchera.

Zgłoszenia błędów, pomysły i animacje do udostępnienia: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues).
