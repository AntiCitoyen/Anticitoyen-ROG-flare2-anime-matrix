<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# Linux 向け AniMe Matrix — ROG Strix Flare II Animate

[![リリース](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![MIT ライセンス](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

**ASUS ROG Strix Flare II Animate** キーボードの **AniMe Matrix**(312 個のミニ LED)ディスプレイを、Armoury Crate も Windows も使わずに Linux 上で直接制御します。GIF と画像、背景ギャラリー、時計、19 種類のアニメーションエフェクト、7 種類のオーディオビジュアライザー、LED 単位の描画に対応しています。

アプリケーションのインターフェースは19の言語に対応しており、システムの言語に自動的に従います。**設定** タブの *言語：* から変更できます。

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
- [.deb パッケージのビルド](#deb)
- [クレジット](#credits)
- [ライセンス](#licence)
- [プロジェクトを支援する](#soutien)

---

<a id="projet"></a>

## このプロジェクトについて

ASUS はこのキーボードの AniMe Matrix ディスプレイを Windows(Armoury Crate)専用としてしか提供していません。本プロジェクトは USB HID 経由でキーボードと直接通信し、次を提供します。

- **グラフィカルランチャー**(`animematrix`)、**4 種類のインターフェース**から選択可能:*ダイヤル＋ドロワー*(丸いウィンドウと右から出てくる設定パネル、デフォルト)、*ダイヤル*(すべて円の中に収まる)、*角丸*(非常に丸い角、輝度ホイール)、*クラシック*(タブ)。丸いインターフェースは、キーボードに送信される **312 個の LED をライブ表示**します。4 つのコマンドブロック:
  - **GIF / 画像**:1 つまたは複数のファイル、あるいはフォルダー全体をギャラリーとしてループ再生。GIF をマトリクス用に変換。
  - **エフェクト**:19 種類のアニメーション(マトリックスレイン、プラズマ、炎、星空、花火、稲妻、メタボール、波、スネーク、テキストスクロール、装飾時計、キーボード連動など)、実行中でも調整可能。
  - **オーディオ**:PC が再生する音に反応する 7 種類のビジュアライザー(スペクトラムバー、KITT / KARR、中心スターバースト、オシロスコープ、オーディオファイアなど)。
  - **設定**:セッション開始時の表示内容、言語・テーマ・インターフェース、描画エディター、プロジェクト関連リンク。
- **HH:MM 表示の時計**、ランチャーから、またはバックグラウンドサービスとして。
- **背景ギャラリー**:セッション開始時からフォルダー内の GIF を自動的に切り替える `systemd --user` サービス。
- **ワンクリック切り替え**(`animematrix-bascule`):メニューアイコンのクリックでディスプレイのオン/オフを切り替え、右クリックで GIF ギャラリー、時計、画面を消すのいずれかを選択。
- **マトリクス用 GIF 変換**(`animematrix-convertir`):19×24、グレースケール、3 階調、ディザリングなし——詳細は [GUIDE-GIF.md](../GUIDE-GIF.md) を参照。
- **LED 単位の描画エディター**(`animematrix-dessin`)。
- **11 種類のテーマ**：ROG をイメージした 5 種類（Classic、Strix、Glitch、Gold、Carbon）、ピンク系 5 種類（桜、バブルガム、ローズゴールド、ラベンダーローズ、ローズナイト）、システム標準。*設定* → *テーマ：* で選択できます。
- **組み込みアップデート**：*設定* → *アップデートを確認*。1 日 1 回の自動確認（オフにできます）。ランチャーは最新の GitHub リリースの `.deb` をダウンロードし、SHA-256 を検証して、管理者パスワードの入力後にインストールします（`pkexec`）。
- **低消費**:GIF はフレームごとにデコードされ、400 個の GIF からなるギャラリーはメモリ使用量約 25 MB で動作。

<a id="materiel"></a>

## 対応ハードウェア

| キーボード | USB | インターフェース |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | HID、インターフェース 4(usage page `0xFF02`) |

ROG **ノート PC**(Zephyrus G14 など)の AniMe Matrix ディスプレイは別のプロトコルを使用しており、本プロジェクトでは**対応していません**(代わりに `asusctl` を使用してください)。

Ubuntu 26.04(X11、PipeWire)で動作確認済み。Python ≥ 3.10、hidapi、Tk、systemd を備えたディストリビューションであれば動作するはずです。

<a id="installation"></a>

## インストール

### .deb パッケージ(Debian、Ubuntu、Mint、Pop!_OS など)

1. [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) ページから `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` をダウンロード。
2. インストール(依存パッケージは apt が自動取得):
   ```bash
   sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb
   ```
3. **キーボードを抜いてから再度接続**(udev ルールによりログイン中のユーザーにアクセス権が付与されます)。
4. アプリケーションメニューから **AniMe Matrix** を起動、またはターミナルで `animematrix` を実行。

このパッケージがインストールするもの:

| 項目 | 場所 |
|---|---|
| プログラム | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| コマンド | `animematrix`、`animematrix-bascule`、`animematrix-effet`、`animematrix-galerie`、`animematrix-horloge`、`animematrix-convertir`、`animematrix-dessin`、`animematrix-lecture` |
| ユーザーサービス | `/usr/lib/systemd/user/animematrix-galerie.service`、`animematrix-horloge.service`、`animematrix-lecture.service`(デフォルトでは無効) |
| udev ルール | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| メニューとアイコン | `animematrix.desktop`、アイコン `animematrix` |

アンインストール:`sudo apt remove anticitoyen-rog-flare2-anime-matrix`。

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

役立つシステムツール:`imagemagick`(変換用)、`pulseaudio-utils`(オーディオ用の `parec`)、`zenity`(ファイル選択ダイアログ)、`libnotify-bin`(切り替え時の通知)。

ソースからバックグラウンドサービスを使う場合は、`systemd/*.service` を `~/.config/systemd/user/` にコピーし、`ExecStart=` 行を `.venv/bin/python` と対応スクリプト(`rog_flare2_folder_player.py`、`rog_flare2_clock_v3.py`)のパスに置き換えたうえで `systemctl --user daemon-reload` を実行してください。

<a id="utilisation"></a>

## 使い方

### ランチャー

`animematrix`(またはメニューの **AniMe Matrix** 項目)。

丸いインターフェースでは、丸いボタンで *GIF / 画像*、*エフェクト*、*オーディオ*、*設定* の各ブロックを開きます(ドロワー内、または円の中)。*時計* と *停止* はすぐに反映されます。下部のアークで輝度を調整します。背景をドラッグしてウィンドウを移動します。上部の小さなボタンで最小化・終了します。丸い形状は X11 SHAPE 拡張(`python3-xlib` パッケージ)を利用します。これがない場合は、同じインターフェースが長方形のウィンドウで表示されます。

- **GIF / 画像**:*GIF/画像…*で個別選択、*フォルダー（ギャラリー）…*でフォルダー全体を選択。選んだフォルダーは背景ギャラリーのフォルダーにもなります。*変換済みバージョンを優先*は、`dossier/matrix/nom.gif`(変換機能で生成)が存在する場合にそちらを読み込みます。
- **エフェクト**と **オーディオ**:選択・調整して *▶ エフェクトを開始*。スライダーはリアルタイムに反映され、*テンポ*でアニメーションを速く/遅くできます。
- **輝度**、**🕒 時計**、**■ 停止**(画面を消去)はすべてのタブに共通です。
- **設定**:*セッション開始時*を GIF ギャラリー、時計、前回の再生、なしから選択;*インターフェース：*4 種類のインターフェースから 1 つを選択(ランチャーが再起動し、現在の表示はそのまま続きます)。

**ランチャーを閉じても、表示していた内容はそのまま続きます**(GIF、そのときの設定のエフェクト、オーディオビジュアライザー、または時計):ランチャーはそれをバックグラウンドサービス `animematrix-lecture.service` に引き継ぎます。次回起動時は、他の何かを起動した時点で制御を取り戻します(キーボードへの書き込みは同時に1つのプログラムしかできません)。閉じる前に *■ 停止* を押すと、画面は消灯したままになります。

### 切り替えとバックグラウンドサービス

```bash
animematrix-bascule            # オン → オフ、オフ → 直前のモード
animematrix-bascule gif        # 背景ギャラリー、セッション開始時にも自動起動
animematrix-bascule horloge    # バックグラウンド時計、セッション開始時にも自動起動
animematrix-bascule lecture    # ランチャーの前回の再生、セッション開始時にも自動起動
animematrix-bascule off        # オフ、セッション開始時は何も起動しない
animematrix-bascule etat       # 現在のモードを表示
```

同じ選択肢はメニューアイコンの右クリックメニューにもあります。内部的には `systemctl --user enable --now animematrix-galerie.service`(または `animematrix-horloge.service`)を使用しています。

### コマンドラインから

| コマンド | 役割 |
|---|---|
| `animematrix-effet --liste` | エフェクトとビジュアライザーの一覧を表示 |
| `animematrix-effet "Plasma" --brightness 60 --vitesse 1.5` | エフェクトを起動(Ctrl+C で停止) |
| `animematrix-galerie [dossier] --brightness 60 [--originaux]` | フォルダーをループ再生(デフォルトはランチャーで最後に選択したフォルダー、なければ `~/Images/AniMe-Matrix`) |
| `animematrix-lecture` | ランチャーの前回の再生を再生し直す(`~/.config/rog-flare2/lecture.json`) |
| `animematrix-horloge -b 25` | 時計を表示。`--clear` で画面を消去、`--once --text 12:34` で指定文字を表示 |
| `animematrix-convertir dossier/ [--sortie D] [--force]` | GIF をマトリクス用に変換(`dossier/matrix/` に出力) |
| `animematrix-dessin` | 描画エディター |

### オーディオ

ビジュアライザーは `parec`(PipeWire または PulseAudio)を使って**デフォルトの音声出力のモニター**を聴取します。マイクではなく、PC が再生している音に反応します。出力先を変更するには、システムのデフォルト出力を変更してください。

### 「Keyboard React」エフェクト

このエフェクトは `pynput` を使ってキー入力のリズムに合わせて画面を光らせます。`pynput` はエフェクトが動作している間、セッション全体のキー入力を読み取ります。X11 では動作しますが、Wayland ではキー入力を受け取れません。

<a id="gif"></a>

## 適切な GIF を作る

画面は単純な長方形ではありません。24 行が段違いに並び、上端が 19 個、下端が 7 個の LED、実際に区別できるグレースケールは 3 階調、隣接する LED の間にはにじみがあります。シルエット、ピクトグラム、短いテキスト、ゆっくりした動きはきれいに表示されますが、写真や動画は向きません。

完全なガイド(キャンバスサイズ、階調、フレームレート、輝度、ImageMagick コマンド):**[GUIDE-GIF.md](../GUIDE-GIF.md)**。

<a id="fonctionnement"></a>

## 仕組み

- **転送方式**:hidapi がキーボードの HID インターフェース 4 番を開き、**1024 バイト**のフレームを書き込みます。
- **フレーム構造**:`60 81 00 00` + **312 バイト**(LED ごとに 0〜255 の輝度値、ハードウェア順)+ 1024 バイトまでゼロ埋め。
- **ジオメトリ**:対角線状に段違いになった 24 行(19 → 7 LED)、あるいは等価に 37 → 15 列の論理行 12 段(PolyWollyWin のモデル)。この 2 つの対応関係は 312 個すべての LED で一致することが確認されています。
- **GIF**:各フレームは(最適化された GIF は差分のみを保持するため)完全に再構成され、グレースケール化され、24 行に縮小されたうえで行ごとにサンプリングされます。
- **アニメーション**:デバイス側には内蔵メモリを使用せず、アニメーションはホスト側がフレームを次々と送信することで実現しています(エフェクトはおよそ 30 fps)。

オリジナルのリバースエンジニアリングの記録(USBPcap キャプチャ、LED の順序、キャリブレーションポイント)は **[PROTOCOL.md](../PROTOCOL.md)** にあります。キャプチャファイル `*.cap` と `parse_usbpcap.py` / `rog_flare2_replay_capture.py` ツールは、さらに深く調べたい人のためにリポジトリに残されています。

⚠️ ノート PC 版 AniMe Matrix 用のパケット(`0x5E …`、`0xEC …`)をキーボードに送らないでください。プロトコルが異なり、キーボードがフリーズする可能性があります(抜き差しするか、**Fn + Esc** を 10〜15 秒間長押ししてください)。

<a id="depannage"></a>

## トラブルシューティング

| 症状 | 考えられる原因 | 対処法 |
|---|---|---|
| `interface 4 not found` | キーボードが認識されていない、または権限がない | `lsusb \| grep 0b05:19fc`、udev ルールがインストールされているか確認、抜き差し |
| `Permission denied` / `open failed` | udev ルールが適用されていない | `sudo udevadm control --reload-rules && sudo udevadm trigger` の後、再接続 |
| 画面が変化しない | 別のプログラムがすでに書き込み中 | `animematrix-bascule off`、他のランチャーやスクリプトを終了 |
| ビジュアライザーがデモモードのまま | `parec` がない、または音が鳴っていない | `pulseaudio-utils` をインストール、音を再生する |
| 「Keyboard React」が反応しない | Wayland セッション、または `pynput` がない | X11 セッションを使用、`sudo apt install python3-pynput` |
| 背景ギャラリーが起動しない | フォルダーが空、または存在しない | ランチャーの GIF タブでフォルダーを選択 |
| 丸いウィンドウが長方形で表示される | SHAPE 拡張または `python3-xlib` が未導入 | `sudo apt install python3-xlib`、または *設定* → *インターフェース：* → *クラシック* |
| サービスのログを見る | — | `journalctl --user -u animematrix-galerie.service -f` |

<a id="depot"></a>

## リポジトリ構成

| ファイル | 役割 |
|---|---|
| `rog_flare2_launcher.py` | グラフィカルランチャー(Tk) |
| `rog_flare2_i18n.py`, `locale/` | インターフェースの翻訳（19 言語、言語ごとに JSON カタログ 1 つ） |
| `rog_flare2_themes.py` | インターフェースのテーマ（ROG とピンク） |
| `rog_flare2_ui_ronde.py` | 丸いインターフェース(ダイヤル＋ドロワー、ダイヤル、角丸):描画、ウィンドウ形状、LED プレビュー |
| `rog_flare2_effets.py` | エフェクトとオーディオビジュアライザー(PolyWollyWin のエンジンを Linux 用に移植) |
| `polywollywin/` | PolyWollyWin のエフェクトエンジン、無改変でコピー(MIT) |
| `rog_flare2_folder_player.py` | 背景ギャラリー(サービス) |
| `rog_flare2_lecture.py` | バックグラウンド再生:ランチャーが終了時に表示していた内容を引き継ぐ(サービス) |
| `rog_flare2_clock_v3.py` | 時計(サービス) |
| `rog_flare2_bascule.sh` | ギャラリー/時計/オフの切り替え |
| `rog_flare2_convertir.py` | GIF 変換(ImageMagick) |
| `rog_flare2_matrix_paint.py` | HID 転送、LED の順序、描画エディター |
| `parse_usbpcap.py`、`rog_flare2_replay_capture.py`、`*.cap` | リバースエンジニアリング用ツールとキャプチャ |
| `systemd/` | ユーザーサービス |
| `packaging/` | udev ルール、メニュー項目、アイコン、.deb パッケージのファイルとスクリプト |
| `docs/` | GIF ガイド、プロトコルに関するノート、スクリーンショット |

<a id="deb"></a>

## .deb パッケージのビルド

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

必要なのは `dpkg-deb` と `bash` のみ。バージョンは `rog_flare2_launcher.py`(`VERSION`)から読み取られます。

<a id="credits"></a>

## クレジット

- **NicRoss512** — プロトコルのリバースエンジニアリング、オリジナルの時計と描画エディター:[ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol)。本リポジトリはここから派生したもので、その履歴を保持しています。
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin)(MIT)、Windows 用コントローラーで、そのエフェクトとオーディオビジュアライザーのエンジンを本プロジェクトで再利用しています。
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/)、LED の挙動(にじみ、知覚される階調、表示速度)についての情報を提供。

本プロジェクトは独立したもので、ASUS とは提携していません。「ROG」「AniMe Matrix」「Armoury Crate」は ASUSTeK の商標です。

<a id="licence"></a>

## ライセンス

本リポジトリのコードは [MIT](../../LICENSE) ライセンスです。`polywollywin/` はその作者による MIT ライセンスのままです([polywollywin/LICENSE](../../polywollywin/LICENSE))。NicRoss512 によるオリジナルファイル(`rog_flare2_clock_v3.py`、`rog_flare2_matrix_paint.py`、`parse_usbpcap.py`、`rog_flare2_replay_capture.py`、`docs/PROTOCOL.md`、キャプチャファイル)は明示的なライセンスなしで公開されたもので、著作権は原作者に帰属したままですが、クレジットを明記したうえで再配布しています。

<a id="soutien"></a>

## プロジェクトを支援する

このプロジェクトが役に立ったなら、コーヒー一杯分の支援が維持の助けになります。

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC%E3%82%92%E3%81%8A%E3%81%94%E3%82%8B&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — このリンクはランチャーの *設定* タブにもあります。

バグ報告やアイデア:[Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues)。
