<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# Linux 向け AniMe Matrix — ROG Strix Flare II Animate

[![リリース](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![CI](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml)
[![MIT ライセンス](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

**ASUS ROG Strix Flare II Animate** キーボードの **AniMe Matrix**(312 個のミニ LED)ディスプレイを、Armoury Crate も Windows も使わずに Linux 上で直接制御します。GIF とギャラリー、時計、エフェクトとオーディオビジュアライザー、ゲーム、システムモニター、デスクトップ通知、スケジュール機能、アニメーションエディター、共有アニメーションライブラリ、キーボードの色の同期。

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · **🇯🇵 日本語** · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/ja/interface-drawer.png" alt="ダイヤル＋ドロワー" width="760"><br><em>ダイヤル＋ドロワー (既定のインターフェース)</em></p>

| ダイヤル | 角丸 | クラシック |
|:---:|:---:|:---:|
| <img src="../captures/ja/interface-dial.png" alt="ダイヤル" width="260"> | <img src="../captures/ja/interface-rounded.png" alt="角丸" width="190"> | <img src="../captures/ja/interface-classic.png" alt="クラシック" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## 目次

- [このプロジェクトについて](#projet)
- [対応ハードウェア](#materiel)
- [インストール](#installation)
- [使い方](#utilisation)
- [適切な GIF を作る](#gif)
- [仕組み](#fonctionnement)
- [トラブルシューティング](#depannage)
- [リポジトリ構成](#depot)
- [パッケージのビルド](#deb)
- [クレジット](#credits)
- [ライセンス](#licence)
- [プロジェクトを支援する](#soutien)

---

<a id="projet"></a>

## このプロジェクトについて

ASUS はこのキーボードの AniMe Matrix ディスプレイを Windows(Armoury Crate)専用としてしか提供していません。本プロジェクトは USB HID 経由でキーボードと直接通信し、次を提供します。

**表示**
- **GIF と画像**:1 つのファイル、複数選択、またはフォルダー全体をギャラリーとして再生。ストリーミング再生(400 個の GIF からなるギャラリーはメモリ使用量約 25 MB)。
- **時計** HH:MM 表示。
- **19 種類のアニメーションエフェクト**(マトリックスレイン、プラズマ、炎、星空、花火、稲妻、メタボール、波、テキストスクロールなど)と、PC が再生する音に反応する**7 種類のオーディオビジュアライザー**。
- **システムモニター**:CPU、メモリ、GPU、温度、ネットワーク速度、時刻をゲージ表示。
- **再生中の曲**:曲が変わると「アーティスト - タイトル」が一度スクロール表示され、その後ビジュアライザーに切り替わります(Spotify、VLC、Rhythmbox、ブラウザーなど、MPRIS 経由)。
- **デスクトップ通知**:「アプリ名:タイトル」がオーバーレイ表示され、その後再生に戻ります(デフォルトでは無効、許可するアプリのリストあり)。
- **キーボードで遊べるゲーム**:スネーク、ポン、テトリス、ブロック崩し、ハイスコア記録付き。

**作成**
- **フレームごとのアニメーションエディター**、画面の実際の形状に基づく:3 階調、タイムライン、ゴーストレイヤー、オフセット、コピー&ペースト、プレビュー、キーボードへの送信、GIF エクスポート。
- **共有アニメーションライブラリ**:閲覧、再生、自分のギャラリーに追加、自作アニメーションの投稿。
- **スマート GIF 変換**:被写体でのトリミング、黒背景に浮かぶ被写体、強調された輪郭、3 階調。
- **忠実なプレビュー**(送信前):画面のシミュレーション表示(実際の配置、LED 間のにじみ)。
- **拡張エフェクト**:Python ファイルをフォルダーに置くだけでエフェクトを追加できます([EXTENSIONS.md](../EXTENSIONS.md) を参照)。

**自動化**
- **`animematrixd` デーモン**:画面の唯一の所有者で、ランチャーを閉じても表示を継続します。`animematrix-ctl` コマンドとオプションのローカル HTTP API を提供。
- **スケジュール機能**:時間帯(夜間を含む)ごとに時計、ギャラリー、モニター、再生中の曲、または画面オフを設定;セッションのロック中、スリープ中、アプリのフルスクリーン時は画面を消灯。
- **OpenRGB によるキーボードの色**:テーマカラーをキーに反映、または画面と同期して明滅。
- **システムトレイアイコン**:クイックメニュー(モード、輝度)。

**快適性**
- **4 種類のインターフェース**(デフォルトは *ダイヤル＋ドロワー*、ほかに *ダイヤル*、*角丸*、*クラシック*)、**312 個の LED をライブプレビュー**、**11 種類のテーマ**(ROG 系 5 種、ピンク系 5 種、システム標準)、**19 の言語**に対応。
- **組み込みアップデート**:ランチャーが最新のリリースをダウンロードし、SHA-256 のフィンガープリントを検証してからインストール(管理者パスワードが必要);または APT リポジトリ経由で `apt upgrade`。

<a id="materiel"></a>

## 対応ハードウェア

| デバイス | USB | 状態 |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | 対応(HID、インターフェース 4、usage page `0xFF02`) |
| ROG ノート PC の AniMe Matrix ディスプレイ(G14、G16 など) | 各種 | **実験的**、`asusctl` 経由、実機での未検証(「[使い方](#utilisation)」参照) |

Ubuntu 26.04(X11、PipeWire、Cinnamon)で動作確認済み。Python ≥ 3.10、hidapi、Tk、systemd を備えたディストリビューションであれば動作するはずです。

<a id="installation"></a>

## インストール

### APT リポジトリ(Debian、Ubuntu、Mint、Pop!_OS など)— `apt upgrade` でアップデート

```bash
curl -fsSL https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix/animematrix.gpg \
  | sudo tee /usr/share/keyrings/animematrix.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/animematrix.gpg] https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix stable main" \
  | sudo tee /etc/apt/sources.list.d/animematrix.list
sudo apt update && sudo apt install anticitoyen-rog-flare2-anime-matrix
```

その後、**キーボードを抜いてから再度接続**し(udev ルールによりログイン中のユーザーにアクセス権が付与されます)、メニューから **AniMe Matrix** を起動します。

### その他の形式([Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) ページ)

| システム | ファイル | インストール方法 |
|---|---|---|
| Debian、Ubuntu など | `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` | `sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb` |
| Fedora、openSUSE など | `anticitoyen-rog-flare2-anime-matrix-<version>-1.noarch.rpm` | `sudo dnf install ./anticitoyen-rog-flare2-anime-matrix-*.noarch.rpm` |
| Arch、Manjaro など | `anticitoyen-rog-flare2-anime-matrix-<version>-1-any.pkg.tar.zst` | `sudo pacman -U anticitoyen-rog-flare2-anime-matrix-*.pkg.tar.zst` |
| すべて(Flatpak) | `AniMeMatrix-<version>.flatpak` | `flatpak install --user AniMeMatrix-*.flatpak`(下記の udev ルールも別途インストールが必要;オーディオビジュアライザーは非対応) |

このパッケージがインストールするもの:

| 項目 | 場所 |
|---|---|
| プログラム | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| コマンド | `animematrix`、`animematrixd`、`animematrix-ctl`、`animematrix-bascule`、`animematrix-animation`、`animematrix-apercu`、`animematrix-convertir`、`animematrix-effet`、`animematrix-galerie`、`animematrix-horloge`、`animematrix-dessin`、`animematrix-tray` |
| ユーザーサービス | `/usr/lib/systemd/user/animematrixd.service`(すべてのセッションで有効) |
| udev ルール | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| メニューとアイコン | `animematrix.desktop`、アイコン `animematrix` |

### ソースから

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# root 権限なしでキーボードにアクセスできるようにする
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# その後、キーボードを抜き差しする
.venv/bin/python rog_flare2_launcher.py
```

役立つシステムツール:`imagemagick`(従来型の変換用)、`pulseaudio-utils`(オーディオ用の `parec`)、`zenity`(ファイル選択ダイアログ)、`libnotify-bin`(通知)、`python3-gi` と `gir1.2-ayatanaappindicator3-0.1`(システムトレイアイコン)、`openrgb`(キーボードの色)。

<a id="utilisation"></a>

## 使い方

### ランチャー

`animematrix`(またはメニューの **AniMe Matrix** 項目)。

丸いインターフェースでは、丸いボタンで *GIF*、*エフェクト*、*オーディオ*、*設定* の各ブロックを開きます(ドロワー内、または円の中)。*時計* と *停止* はすぐに反映されます。下部のアークで輝度を調整します。背景をドラッグしてウィンドウを移動します。上部の小さなボタンで最小化・終了します。丸い形状は X11 SHAPE 拡張(`python3-xlib` パッケージ)を利用します。これがない場合は、同じインターフェースが長方形のウィンドウで表示されます。

- **GIF / 画像**:*GIF/画像…* または *フォルダー（ギャラリー）…*;*忠実なジオメトリ* は比率を保ちます(引き伸ばす代わりに角を切り取ります);*👁 忠実なプレビュー（送信前）* は何も送信せずに表示を確認できます;*🎞 アニメーションを作成（エディター）*;*📚 アニメーションライブラリ*;*スマート変換* で GIF を変換します。
- **エフェクト**と **オーディオ**:選択・調整して *▶ エフェクトを開始*。スライダーはリアルタイムに反映され、*テンポ*でアニメーション全体を速く/遅くできます。ゲームは矢印キー、スペース、Enter で操作し、ランチャーのウィンドウを最前面にする必要があります。
- **輝度**、**🕒 時計**、**■ 停止**(画面を消去)はすべてのタブに共通です。
- **設定**:セッション開始時の表示内容(GIF ギャラリー、時計、前回の再生、なし)、言語、テーマ、インターフェース、デスクトップ通知、キーボードの色(OpenRGB)、*スケジュール…*、システムトレイアイコン、拡張機能フォルダー、アップデート。

**ランチャーを閉じても、表示は途切れません**:`animematrixd` デーモンが表示を継続します。*■ 停止* を押すと画面が消灯します。

### デーモンとコマンドライン

```bash
animematrix-ctl etat                               # 現在表示されている内容
animematrix-ctl gif ~/Images/AniMe-Matrix --fidele # ギャラリー(フォルダーまたはファイル)
animematrix-ctl effet "Plasma" --param speed=250   # エフェクトと設定値
animematrix-ctl horloge
animematrix-ctl texte "Bonjour"
animematrix-ctl notifier "Café prêt" --duree 5     # オーバーレイ表示後に復帰
animematrix-ctl luminosite 60
animematrix-ctl stop
```

| コマンド | 役割 |
|---|---|
| `animematrix-bascule [gif\|horloge\|lecture\|off\|etat]` | モードを切り替え(メニューアイコンの右クリックメニューからも可能);選んだモードはセッション開始時のモードにもなります |
| `animematrixd --http 8765` | ローカル HTTP API を備えたデーモン(`POST http://127.0.0.1:8765/api`、ソケットと同じ JSON) |
| `animematrix-animation [fichier.gif]` | アニメーションエディター |
| `animematrix-apercu fichier.gif -o apercu.gif` | GIF ファイルの忠実なプレビューを生成 |
| `animematrix-convertir dossier/ [--fidele] [--classique]` | GIF をマトリクス用に変換(`dossier/matrix/` に出力) |
| `animematrix-effet --liste` | エフェクトとビジュアライザーの一覧を表示 |
| `animematrix-dessin` | LED 単位の描画エディター(終了するとデーモンに制御を返します) |

### オーディオ

ビジュアライザーは `parec`(PipeWire または PulseAudio)を使って**デフォルトの音声出力のモニター**を聴取します。マイクではなく、PC が再生している音に反応します。

### 「Keyboard React」エフェクト

このエフェクトは `pynput` を使ってキー入力のリズムに合わせて画面を光らせます。`pynput` はエフェクトが動作している間、セッション全体のキー入力を読み取ります。X11 では動作しますが、Wayland ではキー入力を受け取れません。

### キーボードの色(OpenRGB)

*設定* → *キーボードの色（OpenRGB）*:テーマカラーをキーに反映、または画面と同期して明滅。デーモンは必要に応じて `openrgb --server` を起動します。OpenRGB はキーボードの以前のライティングを把握していません。キーボードに保存されたエフェクトを取り戻すには、抜き差ししてください。

### ROG ノート PC(実験的)

`~/.config/rog-flare2/materiel` に `portable-asusctl` と記述し、デーモンを再起動します。フレームは `asusctl anime image` 経由で送られます(最大毎秒 5 フレーム)。実機での動作は未検証です。フィードバックはチケットまでお願いします。

<a id="gif"></a>

## 適切な GIF を作る

画面は単純な長方形ではありません。24 行が段違いに並び、上端が 19 個、下端が 7 個の LED(右端は垂直、左端は対角線)、実際に区別できるグレースケールは 3 階調、隣接する LED の間にはにじみがあります。シルエット、ピクトグラム、短いテキスト、ゆっくりした動きはきれいに表示されますが、写真や動画は向きません。

完全なガイド(キャンバス、階調、フレームレート、変換、忠実なジオメトリ):**[GUIDE-GIF.md](../GUIDE-GIF.md)**。

<a id="fonctionnement"></a>

## 仕組み

- **転送方式**:hidapi がキーボードの HID インターフェース 4 番を開き、**1024 バイト**のフレームを書き込みます。キーボードは各フレームを送り返します。
- **フレーム構造**:`60 81 00 00` + **312 バイト**(LED ごとに 0〜255 の輝度値、ハードウェア順)+ 1024 バイトまでゼロ埋め。
- **ジオメトリ**:対角線状に段違いになった 24 行(行 r は列 (r+1)//2 から 18 までをカバー)、あるいは等価に 37 → 15 列の論理行 12 段(PolyWollyWin のモデル)。この 2 つの対応関係は 312 個すべての LED で一致することが確認されています。
- **デーモン**:`animematrixd` が単独でキーボードを扱います。基本的な再生とオーバーレイ表示(通知)を担当;JSON ソケット `$XDG_RUNTIME_DIR/animematrix.sock`;キーボードの自動再接続。
- **アニメーション**:ホスト側がフレームを次々と送信することで実現しています(エフェクトはおよそ 30 fps)。キーボード内部の記憶領域は使用していません(調査内容は [RECHERCHE-MEMOIRE.md](../RECHERCHE-MEMOIRE.md) を参照)。

オリジナルのリバースエンジニアリングの記録は **[PROTOCOL.md](../PROTOCOL.md)** にあります。キャプチャファイル `*.cap` と `parse_usbpcap.py` / `rog_flare2_replay_capture.py` ツールは、リポジトリに残されています。

⚠️ ノート PC 版 AniMe Matrix 用のパケット(`0x5E …`、`0xEC …`)をキーボードに送らないでください。プロトコルが異なり、キーボードがフリーズする可能性があります(抜き差しするか、**Fn + Esc** を 10〜15 秒間長押ししてください)。

<a id="depannage"></a>

## トラブルシューティング

| 症状 | 考えられる原因 | 対処法 |
|---|---|---|
| `interface 4 not found` | キーボードが認識されていない、または権限がない | `lsusb \| grep 0b05:19fc`、udev ルールがインストールされているか確認、抜き差し |
| `Permission denied` / `open failed` | udev ルールが適用されていない | `sudo udevadm control --reload-rules && sudo udevadm trigger` の後、再接続 |
| 「animematrixd サービスに接続できません」 | デーモンが停止している | `systemctl --user restart animematrixd.service` または `animematrixd &` |
| 画面が変化しない | 別のプログラムがキーボードに書き込み中 | 古いスクリプトを終了;`animematrix-ctl etat` |
| ビジュアライザーがデモモードのまま | `parec` がない、または音が鳴っていない | `pulseaudio-utils` をインストール、音を再生する |
| 「Keyboard React」が反応しない | Wayland セッション、または `pynput` がない | X11 セッションを使用、`sudo apt install python3-pynput` |
| 丸いウィンドウが長方形で表示される | SHAPE 拡張または `python3-xlib` が未導入 | `sudo apt install python3-xlib`、または *設定* → *インターフェース：* → *クラシック* |
| OpenRGB 使用後にキーが同じ色のまま | OpenRGB が元のエフェクトを再現できない | キーボードを抜き差しする |
| デーモンのログ | — | `journalctl --user -u animematrixd.service -f` |

<a id="depot"></a>

## リポジトリ構成

| ファイル | 役割 |
|---|---|
| `rog_flare2_launcher.py` | グラフィカルランチャー(Tk) |
| `rog_flare2_ui_ronde.py`、`rog_flare2_themes.py` | 丸いインターフェース、テーマ |
| `rog_flare2_i18n.py`、`locale/` | 翻訳(19 言語;`locale/_cles.json` = 翻訳対象のテキスト) |
| `rog_flare2_demon.py`、`rog_flare2_ctl.py` | `animematrixd` デーモン、クライアント、`animematrix-ctl` コマンド |
| `rog_flare2_core.py` | GIF のストリーミング再生、時計、ジオメトリ |
| `rog_flare2_effets.py`、`polywollywin/` | エフェクトとビジュアライザー(PolyWollyWin のエンジン、MIT)、拡張機能 |
| `rog_flare2_infos.py`、`rog_flare2_mpris.py`、`rog_flare2_jeux.py` | システムモニター、再生中の曲、ゲーム |
| `rog_flare2_notifs.py`、`rog_flare2_programme.py`、`rog_flare2_ui_programme.py` | 通知、スケジュール機能とトリガー |
| `rog_flare2_openrgb.py`、`rog_flare2_tray.py`、`rog_flare2_portable.py` | OpenRGB 経由の色、システムトレイアイコン、ノート PC(実験的) |
| `rog_flare2_animation.py`、`rog_flare2_simulateur.py`、`rog_flare2_convertir.py` | アニメーションエディター、シミュレーター、変換 |
| `rog_flare2_bibliotheque.py`、`bibliotheque/` | アニメーションライブラリ(カタログ、CC0 の GIF) |
| `rog_flare2_maj.py` | リリースからのアップデート |
| `rog_flare2_matrix_paint.py`、`rog_flare2_clock_v3.py`、`rog_flare2_folder_player.py` | HID 転送と LED 単位の描画エディター、時計、ギャラリー(オリジナルツール) |
| `parse_usbpcap.py`、`rog_flare2_replay_capture.py`、`*.cap` | リバースエンジニアリング |
| `examples/effets/` | 拡張機能の例 |
| `tests/` | テスト(実際のクリック操作によるインターフェーステストを含む) |
| `systemd/`、`packaging/` | ユーザーサービス;.deb、RPM、Arch、Flatpak、APT リポジトリ |
| `docs/` | GIF ガイド、拡張機能、プロトコル、調査資料、スクリーンショット、翻訳された README |

<a id="deb"></a>

## パッケージのビルド

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

`packaging/install.sh` は本プロジェクトを任意のディレクトリツリーにインストールします。この仕組みは .deb、RPM(`packaging/rpm/`)、Arch パッケージ(`packaging/aur/`)、Flatpak(`packaging/flatpak/`)で使われています。リリースが公開されるたびに、GitHub が RPM、Arch パッケージ、Flatpak をビルドし、署名済みの APT リポジトリを更新します。バージョンは `rog_flare2_core.py`(`VERSION`)から読み取られます。テスト:`python -m pytest tests`。

<a id="credits"></a>

## クレジット

- **NicRoss512** — プロトコルのリバースエンジニアリング、オリジナルの時計と描画エディター:[ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol)。本リポジトリはここから派生したもので、その履歴を保持しています。
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin)(MIT)、Windows 用コントローラーで、そのエフェクトとオーディオビジュアライザーのエンジンを本プロジェクトで再利用しています。
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/)、LED の挙動(にじみ、知覚される階調、表示速度)についての情報を提供。
- **asus-linux** — [asusctl](https://gitlab.com/asus-linux/asusctl)、ノート PC のディスプレイに使用。

本プロジェクトは独立したもので、ASUS とは提携していません。「ROG」「AniMe Matrix」「Armoury Crate」は ASUSTeK の商標です。

<a id="licence"></a>

## ライセンス

本リポジトリのコードは [MIT](../../LICENSE) ライセンスです。`bibliotheque/` 内のアニメーションは CC0 ライセンスです。`polywollywin/` はその作者による MIT ライセンスのままです([polywollywin/LICENSE](../../polywollywin/LICENSE))。NicRoss512 によるオリジナルファイル(`rog_flare2_clock_v3.py`、`rog_flare2_matrix_paint.py`、`parse_usbpcap.py`、`rog_flare2_replay_capture.py`、`docs/PROTOCOL.md`、キャプチャファイル)は明示的なライセンスなしで公開されたもので、著作権は原作者に帰属したままですが、クレジットを明記したうえで再配布しています。

<a id="soutien"></a>

## プロジェクトを支援する

このプロジェクトが役に立ったなら、コーヒー一杯分の支援が維持の助けになります。

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC%E3%82%92%E3%81%8A%E3%81%94%E3%82%8B&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — このリンクはランチャーの *設定* タブにもあります。

バグ報告、アイデア、アニメーションの共有:[Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues)。
