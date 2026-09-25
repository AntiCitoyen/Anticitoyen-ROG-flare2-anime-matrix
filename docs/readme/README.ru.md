<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# AniMe Matrix для Linux — ROG Strix Flare II Animate

[![Release](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![Лицензия MIT](https://img.shields.io/badge/лицензия-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-поддержать-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

Управление под Linux экраном **AniMe Matrix** (312 мини-светодиодов) клавиатуры **ASUS ROG Strix Flare II Animate** без Armoury Crate и Windows: GIF и изображения, фоновая галерея, часы, 19 анимированных эффектов, 7 аудиовизуализаторов, рисование по одному светодиоду.

Интерфейс доступен на 19 языках — он автоматически подстраивается под язык системы, а изменить его можно во вкладке *Настройки* → *Язык:*.

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · **🇷🇺 Русский** · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/ru/interface-drawer.png" alt="Циферблат + панель" width="760"><br><em>Циферблат + панель (интерфейс по умолчанию)</em></p>

| Циферблат | Скруглённый | Классический |
|:---:|:---:|:---:|
| <img src="../captures/ru/interface-dial.png" alt="Циферблат" width="260"> | <img src="../captures/ru/interface-rounded.png" alt="Скруглённый" width="190"> | <img src="../captures/ru/interface-classic.png" alt="Классический" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## Содержание

- [Что делает проект](#projet)
- [Поддерживаемое оборудование](#materiel)
- [Установка](#installation)
- [Использование](#utilisation)
- [Подготовка хороших GIF](#gif)
- [Как это работает](#fonctionnement)
- [Устранение неполадок](#depannage)
- [Структура репозитория](#depot)
- [Сборка пакета .deb](#deb)
- [Благодарности](#credits)
- [Лицензия](#licence)
- [Поддержать проект](#soutien)

---

<a id="projet"></a>

## Что делает проект

ASUS предоставляет доступ к экрану AniMe Matrix этой клавиатуры только под Windows (через Armoury Crate). Этот проект напрямую общается с клавиатурой по USB HID и добавляет:

- **Графический лаунчер** (`animematrix`), на выбор из **4 интерфейсов**: *Циферблат + панель* (круглое окно с панелью настроек, выезжающей справа, по умолчанию), *Циферблат* (всё внутри круга), *Скруглённый* (сильно скруглённые углы, колесо яркости) и *Классический* (вкладки). Круглые интерфейсы показывают **312 светодиодов в реальном времени**, именно так, как они отправляются на клавиатуру. Четыре блока управления:
  - **GIF / изображения** (*GIF/изображения…*): воспроизведение одного или нескольких файлов, либо целой папки в режиме галереи, по кругу; конвертация GIF под матрицу.
  - **Эффекты**: 19 анимаций (дождь в стиле Matrix, плазма, огонь, звёзды, фейерверки, молнии, метаболы, волна, змейка, бегущая строка, стилизованные часы, реакция на нажатия клавиш…), настраиваемых прямо во время работы.
  - **Аудио**: 7 визуализаторов, реагирующих на звук, воспроизводимый компьютером (спектр, KITT/KARR, starburst, осциллограф, аудио-огонь…).
  - **Настройки**: что отображать при входе в сессию, язык, тема и интерфейс, редактор рисунка, ссылки проекта.
- **Часы** ЧЧ:ММ — из лаунчера или в виде фоновой службы.
- **Фоновая галерея**: пользовательская служба `systemd --user`, прокручивающая папку с GIF сразу после входа в сессию.
- **Переключение в один клик** (`animematrix-bascule`): значок в меню включает или выключает экран; правый клик позволяет выбрать Галерея GIF, Часы или Выключить.
- **Конвертацию GIF под матрицу** (`animematrix-convertir`): 19×24, оттенки серого, 3 уровня, без дизеринга — см. [../GUIDE-GIF.md](../GUIDE-GIF.md).
- **Редактор рисунка** по одному светодиоду (`animematrix-dessin`).
- **11 тем**: 5 в стиле ROG (Classic, Strix, Glitch, Gold, Carbon), 5 розовых (Сакура, Жвачка, Розовое золото, Лавандовый розовый, Розовая ночь) и системная; выбор в *Настройки* → *Тема:*.
- **Низкое потребление ресурсов**: GIF декодируются покадрово; галерея из 400 GIF работает в ~25 МБ памяти.

<a id="materiel"></a>

## Поддерживаемое оборудование

| Клавиатура | USB | Интерфейс |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | HID, интерфейс 4 (usage page `0xFF02`) |

Экраны AniMe Matrix в **ноутбуках** ROG (Zephyrus G14 и др.) используют другой протокол: они здесь **не** поддерживаются (см. вместо этого `asusctl`).

Протестировано на Ubuntu 26.04 (X11, PipeWire). Должен подойти любой дистрибутив с Python ≥ 3.10, hidapi, Tk и systemd.

<a id="installation"></a>

## Установка

### Пакет .deb (Debian, Ubuntu, Mint, Pop!_OS…)

1. Скачайте `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` со страницы [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest).
2. Установите его (apt подтянет зависимости):
   ```bash
   sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb
   ```
3. **Отключите и снова подключите клавиатуру** (правило udev даёт доступ вошедшему в систему пользователю).
4. Запустите **AniMe Matrix** из меню приложений или командой `animematrix` в терминале.

Пакет устанавливает:

| Элемент | Расположение |
|---|---|
| Программы | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| Команды | `animematrix`, `animematrix-bascule`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-convertir`, `animematrix-dessin`, `animematrix-lecture` |
| Пользовательские службы | `/usr/lib/systemd/user/animematrix-galerie.service`, `animematrix-horloge.service`, `animematrix-lecture.service` (по умолчанию не активированы) |
| Правило udev | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| Меню и значок | `animematrix.desktop`, значок `animematrix` |

Удаление: `sudo apt remove anticitoyen-rog-flare2-anime-matrix`.

### Из исходников

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# доступ к клавиатуре без root
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# затем отключите и снова подключите клавиатуру
.venv/bin/python rog_flare2_launcher.py
```

Полезные системные утилиты: `imagemagick` (конвертация), `pulseaudio-utils` (`parec`, для аудио), `zenity` (диалоги выбора файлов), `libnotify-bin` (уведомления переключателя).

Для фоновых служб при установке из исходников скопируйте `systemd/*.service` в `~/.config/systemd/user/`, заменив строки `ExecStart=` на путь к `.venv/bin/python` и соответствующему скрипту (`rog_flare2_folder_player.py`, `rog_flare2_clock_v3.py`), затем выполните `systemctl --user daemon-reload`.

<a id="utilisation"></a>

## Использование

### Лаунчер

`animematrix` (либо пункт **AniMe Matrix** в меню).

В круглых интерфейсах круглые кнопки открывают блоки *GIF*, *Эффекты*, *Аудио* и *Настройки* (в панели или в круге); *Часы* и *Остановить* действуют сразу; нижняя дуга регулирует яркость; окно перемещается перетаскиванием за фон; маленькие кнопки сверху сворачивают или закрывают его. Круглая форма использует расширение X11 SHAPE (пакет `python3-xlib`); без него тот же интерфейс отображается в прямоугольном окне.

- **GIF / изображения**: *GIF/изображения…* для выбора файлов, *Папка (галерея)…* для целой папки. Выбранная папка также становится папкой фоновой галереи. *Предпочитать конвертированные версии* читает `папка/matrix/имя.gif`, если он существует (создаётся конвертацией).
- **Эффекты** и **Аудио**: выбрать, настроить, *▶ Запустить эффект*. Ползунки действуют в реальном времени; *Темп* ускоряет или замедляет анимацию.
- **Яркость**, **🕒 Часы**, **■ Остановить** (очищает экран) — общие для всех вкладок.
- **Настройки**: *При входе в сессию* = Галерея GIF, Часы, Последнее воспроизведение или Ничего; *Язык:* меняет язык интерфейса (лаунчер перезапускается); *Интерфейс:* выбирает один из 4 интерфейсов (лаунчер перезапускается, текущее отображение продолжает воспроизводиться).

**При закрытии лаунчера то, что отображается, продолжает воспроизводиться** (GIF, эффект с текущими настройками, аудиовизуализатор или часы): лаунчер передаёт это фоновой службе `animematrix-lecture.service`. При следующем запуске он снова берёт управление, как только запускается что-то ещё (записывать в клавиатуру может только одна программа). *■ Остановить* перед закрытием оставляет экран выключенным.

### Переключатель и фоновые службы

```bash
animematrix-bascule            # включено → выключено ; выключено → последний режим
animematrix-bascule gif        # фоновая галерея, также при входе в сессию
animematrix-bascule horloge    # фоновые часы, также при входе в сессию
animematrix-bascule lecture    # последнее воспроизведение лаунчера, также при входе в сессию
animematrix-bascule off        # выключено, ничего при входе
animematrix-bascule etat       # текущий режим
```

Те же варианты доступны по правому клику на значке в меню. Под капотом: `systemctl --user enable --now animematrix-galerie.service` (или `animematrix-horloge.service`).

### Из командной строки

| Команда | Назначение |
|---|---|
| `animematrix-effet --liste` | список эффектов и визуализаторов |
| `animematrix-effet "Plasma" --brightness 60 --vitesse 1.5` | запускает эффект (Ctrl+C для остановки) |
| `animematrix-galerie [папка] --brightness 60 [--originaux]` | прокручивает папку (по умолчанию последняя выбранная в лаунчере, иначе `~/Images/AniMe-Matrix`) |
| `animematrix-lecture` | заново воспроизводит последнее воспроизведение лаунчера (`~/.config/rog-flare2/lecture.json`) |
| `animematrix-horloge -b 25` | часы; `--clear` очищает экран, `--once --text 12:34` отображает текст |
| `animematrix-convertir папка/ [--sortie D] [--force]` | конвертирует GIF под матрицу (в `папка/matrix/`) |
| `animematrix-dessin` | редактор рисунка |

### Аудио

Визуализаторы прослушивают **монитор звукового устройства вывода по умолчанию** через `parec` (PipeWire или PulseAudio): они реагируют на то, что воспроизводит компьютер, а не на микрофон. Чтобы изменить источник, смените устройство вывода по умолчанию в системе.

### Эффект «Реакция на клавиатуру»

Он зажигает экран в такт набору текста благодаря `pynput`, который считывает нажатия клавиш во всей сессии, пока эффект работает. Работает под X11; под Wayland не получает нажатия клавиш.

<a id="gif"></a>

## Подготовка хороших GIF

Экран — не прямоугольник: 24 смещённых ряда, от 19 светодиодов вверху до 7 внизу, 3 действительно различимых уровня серого, ореол между соседними светодиодами. Силуэты, пиктограммы, короткие тексты и медленное движение смотрятся хорошо; фотографии и видео — нет.

Полное руководство (размер холста, уровни, частота кадров, яркость, команда ImageMagick): **[../GUIDE-GIF.md](../GUIDE-GIF.md)**.

<a id="fonctionnement"></a>

## Как это работает

- **Транспорт**: hidapi открывает HID-интерфейс № 4 клавиатуры и записывает в него кадры по **1024 байта**.
- **Кадр**: `60 81 00 00` + **312 байт** (яркость 0–255 на светодиод, в аппаратном порядке) + нули до 1024.
- **Геометрия**: 24 ряда, смещённых по диагонали (19 → 7 светодиодов), либо, что эквивалентно, 12 логических рядов по 37 → 15 столбцов (модель PolyWollyWin); оба представления проверены как идентичные на всех 312 светодиодах.
- **GIF**: каждый кадр восстанавливается полностью (оптимизированные GIF хранят только различия), переводится в оттенки серого, приводится к 24 рядам и дискретизируется построчно.
- **Анимация**: встроенной памяти устройство не использует; анимацию создаёт хост, отправляя кадры один за другим (~30 кадров/с для эффектов).

Исходные заметки по реверс-инжинирингу (захваты USBPcap, порядок светодиодов, точки калибровки) находятся в **[../PROTOCOL.md](../PROTOCOL.md)**; захваты `*.cap` и утилиты `parse_usbpcap.py` / `rog_flare2_replay_capture.py` остаются в репозитории для желающих копнуть глубже.

⚠️ Не отправляйте клавиатуре пакеты для AniMe Matrix ноутбуков (`0x5E …`, `0xEC …`): это неверный протокол, который может заблокировать клавиатуру (отключите и снова подключите, либо удерживайте **Fn + Esc** 10–15 с).

<a id="depannage"></a>

## Устранение неполадок

| Симптом | Вероятная причина | Решение |
|---|---|---|
| `interface 4 not found` | клавиатура не обнаружена или нет прав | `lsusb \| grep 0b05:19fc` ; установлено ли правило udev? отключить/подключить |
| `Permission denied` / `open failed` | правило udev не применено | `sudo udevadm control --reload-rules && sudo udevadm trigger`, затем переподключить |
| Экран не меняется | уже пишет другая программа | `animematrix-bascule off`, закрыть другие лаунчеры или скрипты |
| Визуализаторы остаются в демо-режиме | нет `parec` или нет звука | установить `pulseaudio-utils`, воспроизвести звук |
| «Реакция на клавиатуру» не реагирует | сессия Wayland или отсутствует `pynput` | сессия X11, `sudo apt install python3-pynput` |
| Фоновая галерея не запускается | папка пуста или отсутствует | выбрать папку в лаунчере (вкладка GIF) |
| Круглое окно отображается как прямоугольник | отсутствует расширение SHAPE или `python3-xlib` | `sudo apt install python3-xlib`, либо *Настройки* → *Интерфейс:* → *Классический* |
| Журнал службы | — | `journalctl --user -u animematrix-galerie.service -f` |

<a id="depot"></a>

## Структура репозитория

| Файл | Назначение |
|---|---|
| `rog_flare2_launcher.py` | графический лаунчер (Tk) |
| `rog_flare2_i18n.py`, `locale/` | перевод интерфейса (19 языков, по одному каталогу JSON на язык) |
| `rog_flare2_themes.py` | темы интерфейса (ROG и розовые) |
| `rog_flare2_ui_ronde.py` | круглые интерфейсы (циферблат + панель, циферблат, скруглённый): отрисовка, форма окна, предпросмотр светодиодов |
| `rog_flare2_effets.py` | эффекты и аудиовизуализаторы (движок PolyWollyWin, адаптированный под Linux) |
| `polywollywin/` | движок эффектов PolyWollyWin, скопирован без изменений (MIT) |
| `rog_flare2_folder_player.py` | фоновая галерея (служба) |
| `rog_flare2_lecture.py` | фоновое воспроизведение: возобновляет то, что лаунчер отображал при закрытии (служба) |
| `rog_flare2_clock_v3.py` | часы (служба) |
| `rog_flare2_bascule.sh` | переключатель галерея / часы / выключено |
| `rog_flare2_convertir.py` | конвертация GIF (ImageMagick) |
| `rog_flare2_matrix_paint.py` | HID-транспорт, порядок светодиодов, редактор рисунка |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | утилиты и захваты для реверс-инжиниринга |
| `systemd/` | пользовательские службы |
| `packaging/` | правило udev, пункт меню, значок, файлы и скрипт пакета .deb |
| `docs/` | руководство по GIF, заметки о протоколе, скриншоты |

<a id="deb"></a>

## Сборка пакета .deb

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

Требуются только `dpkg-deb` и `bash`; версия считывается из `rog_flare2_launcher.py` (`VERSION`).

<a id="credits"></a>

## Благодарности

- **NicRoss512** — реверс-инжиниринг протокола, оригинальные часы и редактор: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol). Этот репозиторий является форком того проекта; его история коммитов сохранена.
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin) (MIT), контроллер для Windows, чей движок эффектов и аудиовизуализаторов используется здесь.
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), за описание поведения светодиодов (ореол, воспринимаемые уровни, частота).

Независимый проект, не аффилированный с ASUS. «ROG», «AniMe Matrix» и «Armoury Crate» — товарные знаки ASUSTeK.

<a id="licence"></a>

## Лицензия

[MIT](../../LICENSE) для кода этого репозитория. `polywollywin/` остаётся под лицензией MIT своего автора ([../../polywollywin/LICENSE](../../polywollywin/LICENSE)). Оригинальные файлы NicRoss512 (`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `../PROTOCOL.md`, захваты) были опубликованы без явной лицензии и остаются собственностью их автора; они распространяются здесь с указанием авторства.

<a id="soutien"></a>

## Поддержать проект

Если этот проект вам полезен, чашка кофе поможет поддерживать его развитие:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=%D0%A3%D0%B3%D0%BE%D1%81%D1%82%D0%B8%D1%82%D0%B5%20%D0%BC%D0%B5%D0%BD%D1%8F%20%D0%BA%D0%BE%D1%84%D0%B5&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — ссылка также есть во вкладке *Настройки* лаунчера.

Сообщения об ошибках и предложения: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues).
