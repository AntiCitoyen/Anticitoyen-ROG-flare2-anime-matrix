<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# 리눅스용 AniMe Matrix — ROG Strix Flare II Animate

[![릴리스](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![CI](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml)
[![MIT 라이선스](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

Armoury Crate나 Windows 없이 리눅스에서 **ASUS ROG Strix Flare II Animate** 키보드의 **AniMe Matrix** 화면(312개 미니 LED)을 직접 제어합니다: GIF와 갤러리, 시계, 효과와 오디오 시각화, 게임, 시스템 모니터, 데스크톱 알림, 시간별 예약, 애니메이션 편집기, 공유 라이브러리, 동기화된 키보드 색상.

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · **🇰🇷 한국어** · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/ko/interface-drawer.png" alt="다이얼 + 서랍" width="760"><br><em>다이얼 + 서랍 (기본 인터페이스)</em></p>

| 다이얼 | 둥근 모서리 | 클래식 |
|:---:|:---:|:---:|
| <img src="../captures/ko/interface-dial.png" alt="다이얼" width="260"> | <img src="../captures/ko/interface-rounded.png" alt="둥근 모서리" width="190"> | <img src="../captures/ko/interface-classic.png" alt="클래식" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## 목차

- [프로젝트 소개](#projet)
- [지원 하드웨어](#materiel)
- [설치](#installation)
- [사용법](#utilisation)
- [좋은 GIF 만들기](#gif)
- [작동 원리](#fonctionnement)
- [문제 해결](#depannage)
- [저장소 구성](#depot)
- [패키지 빌드](#deb)
- [크레딧](#credits)
- [라이선스](#licence)
- [프로젝트 후원](#soutien)

---

<a id="projet"></a>

## 프로젝트 소개

ASUS는 이 키보드의 AniMe Matrix 화면을 Windows(Armoury Crate)에서만 제공합니다. 이 프로젝트는 USB HID를 통해 키보드와 직접 통신하며 다음을 제공합니다.

**표시**
- **GIF, 이미지, 동영상**: 파일 하나, 선택한 여러 파일, 또는 폴더 전체를 갤러리로 재생하며, 창에 끌어다 놓을 수도 있습니다 ; 동영상(MP4, WebM, MKV…)은 ffmpeg로 재생 ; 썸네일 갤러리 ; 변환된 프레임은 캐시에 보관(400개 GIF로 이루어진 갤러리도 메모리 약 25MB로 실행).
- **시계**: 디지털, 아날로그, 이진, 단어(프랑스어, 영어, 독일어, 스페인어, 이탈리아어, 포르투갈어, 네덜란드어) 또는 스타일 문자판.
- **애니메이션 효과**(매트릭스 풍 비, 플라즈마, 불, 별, 불꽃놀이, 번개, 메타볼, 파도…)와 PC에서 재생되는 소리에 반응하는 **7가지 오디오 시각화**.
- **텍스트**: 원하는 메시지를 모든 문자(악센트, 키릴 문자, 아랍 문자, 힌디어, 중국어, 일본어, 한국어…)로 왼쪽, 오른쪽, 위, 아래로 스크롤하거나 고정해서 표시.
- **웹캠**(영상 또는 실루엣)과 **화면 미러링**(전체 화면, 마우스 주변 또는 활성 창).
- **시스템 모니터**: CPU, RAM, GPU, 온도, 네트워크 속도, 시간을 게이지로 표시.
- **재생 중인 곡**: 트랙이 바뀌면 "아티스트 - 제목"이 한 번 스크롤된 뒤 시각화가 표시됩니다(Spotify, VLC, Rhythmbox, 브라우저… MPRIS 사용).
- **데스크톱 알림**: "앱 이름 : 제목"이 화면 위에 겹쳐 표시된 뒤 원래 재생으로 돌아갑니다(기본적으로 꺼져 있으며, 허용할 앱 목록 지정 가능).
- 키보드로 **즐길 수 있는 게임**: 스네이크, 퐁(혼자 또는 둘이서), 테트리스, 벽돌 깨기, 인베이더, 플래피, 기록 저장.
- **표시등**: 마이크가 음소거되었거나 사용 중일 때, 웹캠이 켜져 있을 때, OBS가 방송 또는 녹화 중일 때 켜지는 작은 빛 블록.
- **키보드 메모리**: 키보드에 저장한 애니메이션(GIF, 이미지)은 연결하자마자 소프트웨어 없이 재생되며 다른 PC에서도 마찬가지입니다. 밝기 조절 가능(GIF 탭, `animematrix-ctl memoire`).

**만들기**
- 화면의 실제 기하 구조를 반영한 프레임 단위 **애니메이션 편집기**: 3단계, 필름스트립, 어니언 스킨, 이동, 복사-붙여넣기, 미리 보기, 키보드로 전송, GIF 내보내기.
- 공유되는 **애니메이션 라이브러리**: 둘러보기, 재생, 내 갤러리에 추가, 직접 만든 애니메이션 제안.
- GIF의 **스마트 변환**: 피사체 기준 자르기, 검은 배경에 밝은 피사체, 윤곽 강화, 3단계.
- 전송 전 **실제와 같은 미리 보기**: 화면을 그대로 시뮬레이션한 렌더링(실제 배치, LED 간 번짐 포함).
- **확장 효과**: 폴더에 Python 파일을 넣으면 효과가 추가됩니다([docs/EXTENSIONS.md](../EXTENSIONS.md) 참고).

**자동화**
- **`animematrixd` 데몬**: 화면의 유일한 소유자로, 런처를 닫아도 계속 표시를 유지합니다 ; `animematrix-ctl` 명령과 선택적 로컬 HTTP API 제공.
- **시간별 예약**: 시계, 갤러리, 모니터, 재생 중인 곡, 효과, 재생 목록, 또는 화면 끄기를 요일별(야간 포함) 구간으로 지정 ; 세션이 잠기거나 절전 상태이거나 앱이 전체 화면일 때 화면 자동 꺼짐.
- **앱별 프로필**: 게임이나 앱이 맨 앞에 있는 동안 그 앱 전용 콘텐츠 표시(*감지* 버튼).
- **재생 목록 및 즐겨찾기**: GIF, 효과, 시계… 각각 정해진 시간 동안 반복 재생 ; 시스템 트레이 아이콘과 명령줄에서도 사용 가능.
- **웹 리모컨**: 로컬 네트워크의 휴대폰에서 화면을 제어하는 페이지(QR 코드, 토큰).
- **긴 명령 완료 알림**: 터미널에서 긴 명령이 끝나면 "완료: make 2 min 05"가 표시됩니다.
- **키 색상과 효과**, OpenRGB 없이: 무지개, 고정, 호흡, 색상 순환, 반응형, 물결, 별이 빛나는 밤, 유사, 전류, 비 — 키보드가 직접 실행하며 분리한 뒤에도 유지됩니다. 또는 테마 색상, 화면과 함께 맥동.
- **시스템 트레이 아이콘**: 빠른 메뉴(모드, 밝기).

**편의성**
- 실시간 **312 LED 미리 보기**, **11가지 테마**(ROG 5종, 핑크 5종, 시스템), **19개 언어**를 갖춘 **4가지 인터페이스**(*다이얼 + 서랍* 기본, *다이얼*, *둥근 모서리*, *클래식*).
- **X11과 Wayland**: evdev를 통한 키보드 반응, Sway, Hyprland, KDE(kdotool) 또는 GNOME(*Window Calls* 확장)에서 활성 창 정보 읽기.
- **내장 업데이트**: 런처가 최신 릴리스를 내려받아 SHA-256 지문을 확인한 뒤 설치(관리자 비밀번호 필요) ; 또는 APT 저장소로 `apt upgrade`.

<a id="materiel"></a>

## 지원 하드웨어

| 기기 | USB | 상태 |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | 지원됨(HID, interface 4, usage page `0xFF02`) |
| ROG 노트북(G14, G16 등)의 AniMe Matrix 화면 | 다양함 | `asusctl`을 통한 **실험적** 지원, 실제 기기에서 테스트되지 않음([사용법](#utilisation) 참고) |

Ubuntu 26.04(X11, PipeWire, Cinnamon)에서 테스트되었습니다. Python ≥ 3.10, hidapi, Tk, systemd를 갖춘 배포판이라면 모두 사용할 수 있을 것입니다 ; Wayland에서는 런처가 XWayland를 통해 실행됩니다.

<a id="installation"></a>

## 설치

### APT 저장소 (Debian, Ubuntu, Mint, Pop!_OS 등) — `apt upgrade`로 업데이트

```bash
curl -fsSL https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix/animematrix.gpg \
  | sudo tee /usr/share/keyrings/animematrix.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/animematrix.gpg] https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix stable main" \
  | sudo tee /etc/apt/sources.list.d/animematrix.list
sudo apt update && sudo apt install anticitoyen-rog-flare2-anime-matrix
```

그다음 **키보드를 분리했다가 다시 연결하고**(udev 규칙이 로그인한 사용자에게 접근 권한을 부여합니다) 메뉴에서 **AniMe Matrix**를 실행하세요.

### 그 밖의 형식 ([Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) 페이지)

| 시스템 | 파일 | 설치 |
|---|---|---|
| Debian, Ubuntu… | `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` | `sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb` |
| Fedora, openSUSE… | `anticitoyen-rog-flare2-anime-matrix-<version>-1.noarch.rpm` | `sudo dnf install ./anticitoyen-rog-flare2-anime-matrix-*.noarch.rpm` |
| Arch, Manjaro… | `anticitoyen-rog-flare2-anime-matrix-<version>-1-any.pkg.tar.zst` | `sudo pacman -U anticitoyen-rog-flare2-anime-matrix-*.pkg.tar.zst` |
| 모든 배포판 (Flatpak) | `AniMeMatrix-<version>.flatpak` | `flatpak install --user AniMeMatrix-*.flatpak`(아래의 udev 규칙도 설치해야 하며, 오디오 시각화는 지원되지 않습니다) |

패키지가 설치하는 항목:

| 항목 | 위치 |
|---|---|
| 프로그램 | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| 명령어 | `animematrix`, `animematrixd`, `animematrix-ctl`, `animematrix-bascule`, `animematrix-animation`, `animematrix-apercu`, `animematrix-convertir`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-dessin`, `animematrix-tray`, `animematrix-memoire` |
| 사용자 서비스 | `/usr/lib/systemd/user/animematrixd.service`(모든 세션에서 활성화됨) |
| udev 규칙 | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| 메뉴 및 아이콘 | `animematrix.desktop`, 아이콘 `animematrix` |

### 소스에서 빌드

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# root 권한 없이 키보드에 접근
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# 이후 키보드를 분리했다가 다시 연결
.venv/bin/python rog_flare2_launcher.py
```

유용한 시스템 도구: `imagemagick`(기본 변환), `pulseaudio-utils`(`parec`, 오디오용), `zenity`(파일 선택 대화상자), `libnotify-bin`(알림), `python3-gi` 및 `gir1.2-ayatanaappindicator3-0.1`(시스템 트레이 아이콘), `ffmpeg`(동영상, 웹캠, 화면 미러링), `python3-evdev`(Wayland에서 키보드 반응), `x11-utils`(X11에서 활성 창), `python3-qrcode`(리모컨 QR 코드), `tkdnd`(끌어다 놓기).

<a id="utilisation"></a>

## 사용법

### 런처

`animematrix` (또는 메뉴의 **AniMe Matrix** 항목).

둥근 인터페이스에서는 둥근 버튼을 눌러 *GIF*, *효과*, *오디오*, *설정* 블록을 엽니다(서랍 안이나 원 안에서) ; *시계*와 *정지*는 즉시 실행됩니다 ; 아래쪽 호는 밝기를 조절합니다 ; 배경을 드래그해 창을 이동합니다 ; 위쪽의 작은 버튼은 최소화 또는 닫기입니다. 둥근 형태는 X11 SHAPE 확장(`python3-xlib` 패키지)을 사용합니다 ; 이 확장이 없으면 같은 인터페이스가 사각형 창으로 표시됩니다.

- **GIF / 이미지**: *GIF/이미지…* 또는 *폴더 (갤러리)…*(또는 창에 끌어다 놓기) ; *실제 비율*은 비율을 유지합니다(이미지를 늘리는 대신 모서리를 잘라냄) ; *👁 실제와 같은 미리 보기(보내기 전)*는 아무것도 전송하지 않고 결과를 보여줍니다 ; *🎞 애니메이션 만들기 (편집기)* ; *📚 애니메이션 라이브러리* ; *★ 재생 목록 및 즐겨찾기* ; *🖼 썸네일 갤러리*(클릭: 재생, 오른쪽 클릭: 즐겨찾기) ; *🎥 웹캠*과 *🖥 화면 미러링* ; GIF 변환을 위한 *스마트 변환*.
- **효과**와 **오디오**: 선택하고, 조정한 뒤 *▶ 효과 실행*. 슬라이더는 실시간으로 작동하며, *템포*는 전체 애니메이션을 빠르거나 느리게 만듭니다. *텍스트* 효과는 메시지와 스크롤 방향을 입력받습니다. 게임은 화살표 키, 스페이스, 엔터로 플레이하며, 런처 창이 맨 앞에 있어야 합니다 ; 2인용 퐁: 왼쪽 플레이어는 Z/W와 S.
- **밝기**, **🕒 시계**, **■ 정지**(화면을 지움)는 모든 탭에 공통입니다.
- **설정**: 세션 시작 시(GIF 갤러리, 시계, 마지막 재생, 또는 없음), 시계 문자판, 언어, 테마, 인터페이스, 데스크톱 알림, 키보드 색상, *일정…*(트리거, 앱별 프로필, 시간 구간), *표시등…*, *웹 리모컨…*, 시스템 트레이 아이콘, 긴 명령 완료 알림, 확장 폴더, 업데이트.

**런처를 닫아도 아무것도 멈추지 않습니다**: `animematrixd` 데몬이 계속 화면을 표시합니다. *■ 정지*를 누르면 화면이 꺼집니다.

### 데몬과 명령줄

```bash
animematrix-ctl etat                               # 현재 표시 중인 내용
animematrix-ctl gif ~/Images/AniMe-Matrix --fidele # 갤러리(폴더 또는 파일)
animematrix-ctl effet "Plasma" --param speed=250   # 효과와 설정
animematrix-ctl horloge
animematrix-ctl texte "Bonjour"
animematrix-ctl effet "Text" --param message="Salut" --param direction=haut
animematrix-ctl liste "Soirée"                     # 재생 목록(이름 없이: 목록 표시)
animematrix-ctl favori 2                           # 즐겨찾기 2번(번호 없이: 목록 표시)
animematrix-ctl notifier "Café prêt" --duree 5     # 겹쳐 표시 후 복귀
animematrix-ctl memoire anim.gif                   # 키보드에 저장(최대 196프레임)
animematrix-ctl clavier                            # 저장된 애니메이션 표시
animematrix-ctl luminosite 60
animematrix-ctl stop
```

| 명령어 | 역할 |
|---|---|
| `animematrix-bascule [gif\|horloge\|lecture\|off\|etat]` | 전환(메뉴 아이콘 오른쪽 클릭에도 있음) ; 선택한 모드는 세션 시작 시의 모드도 됩니다 |
| `animematrixd --http 8765` | 로컬 HTTP API를 갖춘 데몬(`POST http://127.0.0.1:8765/api`, `Content-Type: application/json`, 소켓과 동일한 JSON) |
| `animematrix-animation [fichier.gif]` | 애니메이션 편집기 |
| `animematrix-apercu fichier.gif -o apercu.gif` | GIF 파일의 실제와 같은 미리 보기 |
| `animematrix-convertir dossier/ [--fidele] [--classique]` | 매트릭스용으로 GIF 변환(`dossier/matrix/`에 저장) |
| `animematrix-effet --liste` | 효과와 시각화 목록 표시 |
| `animematrix-dessin` | LED 단위 편집기(종료 시 데몬에 제어권을 돌려줌) |

### 오디오

시각화는 `parec`(PipeWire 또는 PulseAudio)로 **기본 오디오 출력의 모니터**를 수신합니다: 마이크가 아니라 PC에서 재생되는 소리에 반응합니다.

### "Keyboard React" 효과

이 효과가 실행되는 동안 타이핑 리듬에 맞춰 화면을 켭니다: X11에서는 `pynput`으로, Wayland에서는 `/dev/input`의 키보드를 읽어서 작동합니다(`python3-evdev`). Wayland에서 효과가 데모 모드에 머문다면, ROG 키보드만 읽을 수 있도록 허용하세요:

```bash
sudo cp /usr/share/anticitoyen-rog-flare2-anime-matrix/udev/73-rog-flare2-animate-touches.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 표시등

*설정* → *표시등(마이크, 웹캠, OBS)…*: 화면 왼쪽 위에 2 × 2 LED 블록이 재생 중인 내용 위에 켜지며(1: 마이크 음소거 또는 사용 중, 2: 웹캠 사용 중, 3: OBS 방송 또는 녹화 중), 변경될 때마다 스크롤 텍스트로 알릴 수 있습니다. OBS: WebSocket 서버를 활성화하고(*도구* → *WebSocket 서버 설정*) 포트와 비밀번호를 입력하세요.

### 웹 리모컨

*설정* → *웹 리모컨…*: *웹 리모컨 켜기*를 선택한 뒤, 같은 네트워크의 휴대폰에서 주소를 여세요(또는 QR 코드를 스캔). 페이지에서 화면을 실시간으로 보면서 시계, 갤러리, 효과, 즐겨찾기, 목록, 밝기, 메시지를 제어할 수 있습니다. 주소에는 토큰이 포함되어 있습니다: 공유하지 말고, *새 토큰*으로 변경하세요 ; 페이지는 암호화되지 않으므로(HTTP) 신뢰할 수 있는 네트워크에서만 사용하세요.

### 긴 명령 완료 알림

*설정* → *긴 명령 완료 알림(터미널)*은 `~/.bashrc`(및 `~/.zshrc`)에 한 줄을 추가합니다: 30초 이상 걸린 명령은 끝날 때 "완료: make 2 min 05" 또는 "실패(2): …"를 표시합니다. 기준 시간: `ANIMEMATRIX_FIN_SECONDES` ; 대화형 명령(편집기, `ssh`, `less`…)은 무시됩니다.

### 키보드 색상

*설정* → *🌈 키보드 색상…*: 효과(무지개, 고정, 호흡, 색상 순환, 반응형, 물결, 별이 빛나는 밤, 유사, 전류, 비), 색상, 속도, 밝기, 방향. *시험*은 바로 적용하고, *키보드에 저장*은 분리한 뒤에도 유지합니다. *테마 색상*과 *화면과 함께 맥동*은 데몬이 키마다 보내며, 끄면 저장된 효과로 돌아갑니다. 명령줄: `animematrix-ctl rgb arc-en-ciel --vitesse 70`, `animematrix-ctl rgb statique --couleur "#ff0000"`. 소프트웨어 모드 두 가지 추가: *화면 이미지*(키가 화면을 확대해 보여 줌)와 *오디오 스펙트럼*(열마다 막대 하나). 각 시간대와 각 앱 프로필마다 키 색상도 고를 수 있습니다(*일정…*).

### ROG 노트북(실험적)

`~/.config/rog-flare2/materiel`에 `portable-asusctl`을 입력한 뒤 데몬을 다시 시작하세요: 프레임은 `asusctl anime image`를 통해 전달됩니다(초당 최대 5프레임). 실제 노트북에서 테스트되지 않았습니다: 티켓으로 의견을 알려 주세요.

<a id="gif"></a>

## 좋은 GIF 만들기

화면은 직사각형이 아닙니다: 위쪽 19개에서 아래쪽 7개로 어긋나게 배열된 24개의 행(오른쪽 가장자리는 수직, 왼쪽 가장자리는 대각선), 확실히 구분되는 3단계의 회색조, 인접한 LED 사이의 번짐 효과가 있습니다. 실루엣, 픽토그램, 짧은 텍스트, 느린 움직임은 잘 표현되지만 사진과 영상은 그렇지 않습니다.

전체 가이드(캔버스, 단계, 프레임 속도, 변환, 실제 비율): **[docs/GUIDE-GIF.md](../GUIDE-GIF.md)**.

<a id="fonctionnement"></a>

## 작동 원리

- **전송 방식**: hidapi가 키보드의 4번 HID 인터페이스를 열고 **1024바이트** 프레임을 씁니다 ; 키보드는 각 프레임을 그대로 되돌려줍니다.
- **프레임**: `60 81 00 00` + **312바이트**(하드웨어 순서대로 LED당 0–255의 밝기값 1개) + 1024바이트까지 0으로 채움.
- **기하 구조**: 24개의 엇갈린 행(행 r은 (r+1)//2부터 18까지의 열을 포함), 또는 이와 동등하게 37 → 15개의 열을 가진 12개의 논리적 행(PolyWollyWin 모델) ; 두 대응 방식이 312개 LED 전체에서 동일함이 확인되었습니다.
- **데몬**: `animematrixd`가 키보드를 단독으로 관리 ; 기본 재생과 겹쳐 표시(알림) ; JSON 소켓 `$XDG_RUNTIME_DIR/animematrix.sock` ; 키보드 자동 재연결.
- **애니메이션**: 호스트가 프레임을 차례로 전송합니다(효과의 경우 초당 약 30프레임) ; 키보드 내장 메모리는 사용되지 않습니다(연구 자료: [docs/RECHERCHE-MEMOIRE.md](../RECHERCHE-MEMOIRE.md)).

원본 리버스 엔지니어링 노트는 **[docs/PROTOCOL.md](../PROTOCOL.md)**에 있습니다 ; `*.cap` 캡처 파일과 `parse_usbpcap.py` / `rog_flare2_replay_capture.py` 도구는 저장소에 남아 있습니다.

⚠️ 노트북용 AniMe Matrix의 패킷(`0x5E …`, `0xEC …`)을 이 키보드로 보내지 마세요: 올바른 프로토콜이 아니며 키보드가 멈출 수 있습니다(분리 후 재연결하거나, **Fn + Esc**를 10~15초간 눌러 유지하세요).

<a id="depannage"></a>

## 문제 해결

| 증상 | 예상 원인 | 해결책 |
|---|---|---|
| `interface 4 not found` | 키보드가 인식되지 않거나 권한 없음 | `lsusb \| grep 0b05:19fc` ; udev 규칙이 설치되었는지 확인 ; 분리 후 재연결 |
| `Permission denied` / `open failed` | udev 규칙이 적용되지 않음 | `sudo udevadm control --reload-rules && sudo udevadm trigger` 실행 후 재연결 |
| "animematrixd 서비스에 연결할 수 없음" | 데몬이 정지됨 | `systemctl --user restart animematrixd.service` 또는 `animematrixd &` |
| 화면이 바뀌지 않음 | 다른 프로그램이 키보드에 쓰고 있음 | 이전 스크립트 종료 ; `animematrix-ctl etat` |
| 시각화가 데모 모드에 머무름 | `parec`이 없거나 소리가 없음 | `pulseaudio-utils` 설치, 소리 재생 |
| "Keyboard React"가 반응하지 않음 | `pynput`(X11) 또는 `python3-evdev`(Wayland)가 없거나 키보드를 읽을 수 없음 | 패키지 설치 ; Wayland에서는 [Keyboard React](#utilisation)의 udev 규칙 |
| 웹캠, 동영상 또는 화면 미러링이 작동하지 않음 | `ffmpeg` 없음 | `sudo apt install ffmpeg` ; Wayland에서는 화면 미러링이 포털을 거침(`gstreamer1.0-pipewire`) |
| Wayland에서 앱별 프로필이나 전체 화면 감지가 작동하지 않음 | 컴포지터가 활성 창을 알려 주지 않음 | GNOME: *Window Calls* 확장 ; KDE: `kdotool` ; Sway와 Hyprland: 별도 작업 불필요 |
| 둥근 창이 사각형으로 표시됨 | SHAPE 확장 또는 `python3-xlib` 누락 | `sudo apt install python3-xlib`, 또는 *설정* → *인터페이스:* → *클래식* |
| 데몬 로그 확인 | — | `journalctl --user -u animematrixd.service -f` |

<a id="depot"></a>

## 저장소 구성

| 파일 | 역할 |
|---|---|
| `rog_flare2_launcher.py` | 그래픽 런처 (Tk) |
| `rog_flare2_ui_ronde.py`, `rog_flare2_themes.py` | 둥근 인터페이스, 테마 |
| `rog_flare2_i18n.py`, `locale/` | 번역(19개 언어 ; `locale/_cles.json` = 번역할 텍스트 ; [docs/TRADUIRE.md](../TRADUIRE.md)) |
| `rog_flare2_demon.py`, `rog_flare2_ctl.py` | `animematrixd` 데몬, 클라이언트와 `animematrix-ctl` 명령 |
| `rog_flare2_core.py` | GIF 스트리밍 재생, 프레임 캐시, 시계, 기하 구조 |
| `rog_flare2_texte.py`, `rog_flare2_horloges.py` | 모든 문자 체계의 텍스트, *텍스트* 효과, 시계 문자판 |
| `rog_flare2_listes.py`, `rog_flare2_vignettes.py` | 재생 목록, 즐겨찾기, 썸네일 갤러리, 끌어다 놓기 |
| `rog_flare2_video.py`, `rog_flare2_voyants.py`, `rog_flare2_telecommande.py` | 동영상, 웹캠, 화면 미러링 ; 표시등 ; 웹 리모컨 |
| `rog_flare2_touches.py`, `rog_flare2_fenetre.py`, `rog_flare2_fin.py`, `rog_flare2_flatpak.py` | 키 입력과 활성 창(X11, Wayland), 긴 명령 완료 알림, Flatpak |
| `rog_flare2_effets.py`, `polywollywin/` | 효과와 시각화(PolyWollyWin 엔진, MIT), 확장 |
| `rog_flare2_infos.py`, `rog_flare2_mpris.py`, `rog_flare2_jeux.py` | 시스템 모니터, 재생 중인 곡, 게임 |
| `rog_flare2_notifs.py`, `rog_flare2_programme.py`, `rog_flare2_ui_programme.py` | 알림, 시간별 예약과 트리거 |
| `rog_flare2_rgb.py`, `rog_flare2_tray.py`, `rog_flare2_portable.py` | 키 색상과 효과, 시스템 트레이 아이콘, 노트북(실험적) |
| `rog_flare2_animation.py`, `rog_flare2_simulateur.py`, `rog_flare2_convertir.py` | 애니메이션 편집기, 시뮬레이터, 변환 |
| `rog_flare2_bibliotheque.py`, `bibliotheque/` | 애니메이션 라이브러리(카탈로그, CC0 GIF) |
| `rog_flare2_maj.py` | 릴리스로부터 업데이트 |
| `rog_flare2_matrix_paint.py`, `rog_flare2_clock_v3.py`, `rog_flare2_folder_player.py` | HID 전송과 LED 편집기, 시계, 갤러리(원본 도구) |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | 리버스 엔지니어링 |
| `examples/effets/` | 확장 예제 |
| `tests/` | 테스트(실제 클릭 기반 인터페이스 테스트 포함) |
| `systemd/`, `packaging/` | 사용자 서비스 ; .deb, RPM, Arch, Flatpak, APT 저장소 |
| `docs/` | GIF 가이드, 확장, 프로토콜, 연구, 스크린샷, 번역된 README |

<a id="deb"></a>

## 패키지 빌드

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

`packaging/install.sh`는 프로젝트를 임의의 디렉터리 구조에 설치하며, .deb, RPM(`packaging/rpm/`), Arch 패키지(`packaging/aur/`), Flatpak(`packaging/flathub/`)에 공통으로 사용됩니다. 릴리스가 게시될 때마다 GitHub가 RPM, Arch 패키지, Flatpak을 빌드하고 서명된 APT 저장소를 업데이트합니다. 버전은 `rog_flare2_core.py`(`VERSION`)에서 읽어옵니다. 테스트: `python -m pytest tests`.

<a id="credits"></a>

## 크레딧

- **NicRoss512** — 프로토콜 리버스 엔지니어링, 원본 시계와 편집기: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol). 이 저장소는 여기서 갈라져 나왔으며, 커밋 히스토리가 보존되어 있습니다.
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin)(MIT), 효과 및 오디오 시각화 엔진을 가져온 Windows용 컨트롤러.
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), LED 동작(번짐, 체감 밝기 단계, 프레임 속도)에 대한 자료.
- **asus-linux** — [asusctl](https://gitlab.com/asus-linux/asusctl), 노트북 화면에 사용됨.

독립적인 프로젝트이며 ASUS와 제휴하지 않았습니다. "ROG", "AniMe Matrix", "Armoury Crate"는 ASUSTeK의 상표입니다.

<a id="licence"></a>

## 라이선스

이 저장소의 코드는 [MIT](../../LICENSE) 라이선스를 따릅니다 ; `bibliotheque/`의 애니메이션은 CC0 라이선스입니다. `polywollywin/`은 원저작자의 MIT 라이선스를 그대로 유지합니다([polywollywin/LICENSE](../../polywollywin/LICENSE)). NicRoss512의 원본 파일들(`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `docs/PROTOCOL.md`, 캡처 파일)은 명시적인 라이선스 없이 공개되었으며 원저작자에게 저작권이 있고, 출처를 표기하여 재배포됩니다.

<a id="soutien"></a>

## 프로젝트 후원

이 프로젝트가 도움이 되었다면, 커피 한 잔이 유지 관리에 힘이 됩니다.

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=커피%20한%20잔%20사주기&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — 이 링크는 런처의 *설정* 탭에도 있습니다.

버그 리포트, 아이디어, 공유하고 싶은 애니메이션: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues). 번역: [docs/TRADUIRE.md](../TRADUIRE.md).
