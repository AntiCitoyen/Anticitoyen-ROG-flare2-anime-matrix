<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# 面向 Linux 的 AniMe Matrix — ROG Strix Flare II Animate

[![发布版本](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![MIT 许可证](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

在 Linux 下直接驱动 **ASUS ROG Strix Flare II Animate** 键盘的 **AniMe Matrix**(312 颗迷你 LED)显示屏,无需 Armoury Crate,也无需 Windows:GIF 与图片、背景图库、时钟、19 种动态效果、7 种音频可视化器,以及逐颗 LED 绘图。

图形界面现已支持 19 种语言,会自动跟随系统语言,也可以在 **设置** 标签页的 *语言：* 中更改。

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · **🇨🇳 简体中文** · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/zh-CN/interface-drawer.png" alt="表盘 + 抽屉" width="760"><br><em>表盘 + 抽屉 (默认界面)</em></p>

| 表盘 | 圆角 | 经典 |
|:---:|:---:|:---:|
| <img src="../captures/zh-CN/interface-dial.png" alt="表盘" width="260"> | <img src="../captures/zh-CN/interface-rounded.png" alt="圆角" width="190"> | <img src="../captures/zh-CN/interface-classic.png" alt="经典" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## 目录

- [项目简介](#projet)
- [支持的硬件](#materiel)
- [安装](#installation)
- [使用方法](#utilisation)
- [制作合适的 GIF](#gif)
- [工作原理](#fonctionnement)
- [故障排查](#depannage)
- [仓库结构](#depot)
- [构建 .deb 软件包](#deb)
- [鸣谢](#credits)
- [许可证](#licence)
- [支持本项目](#soutien)

---

<a id="projet"></a>

## 项目简介

ASUS 仅在 Windows(通过 Armoury Crate)下为该键盘的 AniMe Matrix 屏幕提供官方支持。本项目通过 USB HID 直接与键盘通信,提供:

- **图形启动器**(`animematrix`),可在 **4 种界面**中选择:*表盘 + 抽屉*(圆形窗口,设置面板从右侧滑出,默认)、*表盘*(全部内容都在圆圈中)、*圆角*(圆角很大,带亮度旋钮)以及*经典*(标签页)。圆形界面会**实时显示发送给键盘的 312 颗 LED**。四个功能模块:
  - **GIF / 图片**:播放一个或多个文件,或将整个文件夹作为图库循环播放;将 GIF 转换为适配矩阵屏的格式。
  - **效果**:19 种动画效果(矩阵雨、等离子、火焰、星空、烟花、闪电、融球、波浪、贪吃蛇、滚动文字、花式时钟、按键律动等),运行期间可实时调节。
  - **音频**:7 种随电脑播放声音而变化的可视化效果(频谱条、KITT / KARR、中心爆闪、示波器、音频火焰等)。
  - **设置**:会话开始时显示的内容、语言、主题与界面、绘图编辑器、项目相关链接。
- **HH:MM 时钟**,可从启动器打开,也可作为后台服务运行。
- **背景图库**:一个 `systemd --user` 服务,在会话开始时自动循环播放指定文件夹中的 GIF。
- **一键切换**(`animematrix-bascule`):菜单图标点击可开关屏幕;右键点击可选择 GIF 图库、时钟或关闭屏幕。
- **适配矩阵屏的 GIF 转换**(`animematrix-convertir`):19×24、灰度、3 级灰阶、无抖动处理——详见 [GUIDE-GIF.md](../GUIDE-GIF.md)。
- **逐颗 LED 绘图编辑器**(`animematrix-dessin`)。
- **11 套主题**：5 套 ROG 风格（Classic、Strix、Glitch、Gold、Carbon），5 套粉色（樱花、泡泡糖、玫瑰金、薰衣草粉、粉色之夜），以及系统默认外观，可在 *设置* → *主题：* 中选择。
- **内置更新**：*设置* → *检查更新*；每天自动检查一次（可关闭）。启动器会下载最新 GitHub release 的 `.deb`，校验其 SHA-256，并在请求管理员密码后安装（`pkexec`）。
- **低资源占用**:GIF 按帧解码;400 个 GIF 组成的图库运行时内存占用约 25 MB。

<a id="materiel"></a>

## 支持的硬件

| 键盘 | USB | 接口 |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | HID,接口 4(usage page `0xFF02`) |

ROG **笔记本电脑**(如 Zephyrus G14 等)上的 AniMe Matrix 屏幕使用不同的协议,本项目**不支持**这些设备(请改用 `asusctl`)。

已在 Ubuntu 26.04(X11、PipeWire)上测试通过。任何具备 Python ≥ 3.10、hidapi、Tk 和 systemd 的发行版理论上均可使用。

<a id="installation"></a>

## 安装

### .deb 软件包(Debian、Ubuntu、Mint、Pop!_OS 等)

1. 从 [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) 页面下载 `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb`。
2. 安装(apt 会自动获取依赖):
   ```bash
   sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb
   ```
3. **拔下键盘后重新插上**(udev 规则会为当前登录用户授予访问权限)。
4. 从应用程序菜单启动 **AniMe Matrix**,或在终端中运行 `animematrix`。

软件包安装内容:

| 项目 | 位置 |
|---|---|
| 程序文件 | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| 命令 | `animematrix`、`animematrix-bascule`、`animematrix-effet`、`animematrix-galerie`、`animematrix-horloge`、`animematrix-convertir`、`animematrix-dessin`、`animematrix-lecture` |
| 用户服务 | `/usr/lib/systemd/user/animematrix-galerie.service`、`animematrix-horloge.service`、`animematrix-lecture.service`(默认不启用) |
| udev 规则 | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| 菜单与图标 | `animematrix.desktop`,图标 `animematrix` |

卸载:`sudo apt remove anticitoyen-rog-flare2-anime-matrix`。

### 从源代码安装

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# 无需 root 权限即可访问键盘
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# 然后拔下并重新插上键盘
.venv/bin/python rog_flare2_launcher.py
```

有用的系统工具:`imagemagick`(转换)、`pulseaudio-utils`(`parec`,用于音频)、`zenity`(文件选择器)、`libnotify-bin`(切换时的通知)。

如需从源代码运行后台服务,将 `systemd/*.service` 复制到 `~/.config/systemd/user/`,并将其中的 `ExecStart=` 行替换为 `.venv/bin/python` 及对应脚本(`rog_flare2_folder_player.py`、`rog_flare2_clock_v3.py`)的路径,然后执行 `systemctl --user daemon-reload`。

<a id="utilisation"></a>

## 使用方法

### 启动器

`animematrix`(或菜单中的 **AniMe Matrix** 项)。

在圆形界面中,圆形按钮用于打开 *GIF / 图片*、*效果*、*音频*、*设置* 模块(在抽屉中或圆圈内);*时钟* 和 *停止* 立即生效;底部的弧形用于调节亮度;拖动背景可移动窗口;顶部的小按钮用于最小化或关闭。圆形外观依赖 X11 SHAPE 扩展(`python3-xlib` 包);若没有该扩展,则以矩形窗口显示同一界面。

- **GIF / 图片**:*GIF/图片…*用于选择单个或多个文件,*文件夹（图库）…*用于选择整个文件夹。所选文件夹同时会成为背景图库使用的文件夹。*优先使用已转换版本*会在存在 `dossier/matrix/nom.gif`(由转换功能生成)时优先读取该文件。
- **效果**与 **音频**:选择、调节参数,然后点击 *▶ 启动效果*。滑块参数为实时生效;*节奏*用于加快或减慢动画播放。
- **亮度**、**🕒 时钟**、**■ 停止**(会清空屏幕)在所有标签页中通用。
- **设置**:*会话启动时*可设为 GIF 图库、时钟、上次播放或无;*界面：*在 4 种界面中选择(启动器会重启,当前显示的内容会继续播放)。

**关闭启动器后,当前显示的内容会继续播放**(GIF、带当前参数的效果、音频可视化或时钟):启动器会将其交给后台服务 `animematrix-lecture.service`。下次启动时,只要开始运行其他内容(同一时间只能有一个程序写入键盘),它就会重新接管。关闭前点击 *■ 停止* 会让屏幕保持熄灭。

### 切换与后台服务

```bash
animematrix-bascule            # 开启 → 关闭;关闭 → 恢复上一次的模式
animematrix-bascule gif        # 背景图库,同时设为会话开始时自动启动
animematrix-bascule horloge    # 后台时钟,同时设为会话开始时自动启动
animematrix-bascule lecture    # 启动器的上次播放,同时设为会话开始时自动启动
animematrix-bascule off        # 关闭,会话开始时不启动任何内容
animematrix-bascule etat       # 显示当前模式
```

相同的选项也可在菜单图标的右键菜单中找到。底层实现:`systemctl --user enable --now animematrix-galerie.service`(或 `animematrix-horloge.service`)。

### 命令行方式

| 命令 | 作用 |
|---|---|
| `animematrix-effet --liste` | 列出所有效果和可视化器 |
| `animematrix-effet "Plasma" --brightness 60 --vitesse 1.5` | 启动某个效果(Ctrl+C 停止) |
| `animematrix-galerie [dossier] --brightness 60 [--originaux]` | 循环播放某个文件夹(默认使用启动器中最近选择的文件夹,否则为 `~/Images/AniMe-Matrix`) |
| `animematrix-lecture` | 重新播放启动器的上次播放内容(`~/.config/rog-flare2/lecture.json`) |
| `animematrix-horloge -b 25` | 显示时钟;`--clear` 清空屏幕,`--once --text 12:34` 显示指定文字 |
| `animematrix-convertir dossier/ [--sortie D] [--force]` | 将 GIF 转换为适配矩阵屏的格式(输出至 `dossier/matrix/`) |
| `animematrix-dessin` | 绘图编辑器 |

### 音频

可视化器通过 `parec`(PipeWire 或 PulseAudio)监听**默认音频输出的监视器(monitor)**:它们对电脑播放的声音作出反应,而非麦克风输入。若要更改监听的输出设备,请更改系统的默认音频输出。

### “Keyboard React” 效果

该效果通过 `pynput` 根据按键节奏点亮屏幕,`pynput` 会在效果运行期间监听整个会话中的按键。它在 X11 下可正常工作;在 Wayland 下无法接收按键事件。

<a id="gif"></a>

## 制作合适的 GIF

屏幕并非一个规整的矩形:24 行呈阶梯状排列,顶部 19 颗 LED,底部 7 颗;只有 3 级真正可区分的灰度;相邻 LED 之间存在光晕。剪影、图标、短文字和缓慢的动作效果较好;照片和视频效果不佳。

完整指南(画布尺寸、灰度级别、帧率、亮度、ImageMagick 命令):**[GUIDE-GIF.md](../GUIDE-GIF.md)**。

<a id="fonctionnement"></a>

## 工作原理

- **传输方式**:hidapi 打开键盘的第 4 号 HID 接口,并向其写入 **1024 字节**的数据帧。
- **数据帧结构**:`60 81 00 00` + **312 字节**(每颗 LED 一个 0–255 的亮度值,按硬件顺序排列)+ 补零至 1024 字节。
- **几何结构**:24 行呈对角阶梯排列(19 → 7 颗 LED),等价地也可视为 12 组逻辑行、每行 37 → 15 列(PolyWollyWin 的模型);两种映射方式已在全部 312 颗 LED 上验证一致。
- **GIF 处理**:每一帧先完整重组(经过优化的 GIF 只存储差异部分),转换为灰度,缩放至 24 行,再逐行采样。
- **动画播放**:设备本身不使用任何内建存储;动画效果由主机逐帧连续发送实现(效果约 30 帧/秒)。

原始的逆向工程记录(USBPcap 抓包、LED 顺序、校准点)见 **[PROTOCOL.md](../PROTOCOL.md)**;抓包文件 `*.cap` 以及 `parse_usbpcap.py` / `rog_flare2_replay_capture.py` 工具仍保留在仓库中,供有需要深入研究的人使用。

⚠️ 请勿向键盘发送笔记本电脑版 AniMe Matrix 的数据包(`0x5E …`、`0xEC …`):协议不同,可能导致键盘卡死(需拔插键盘,或按住 **Fn + Esc** 10–15 秒)。

<a id="depannage"></a>

## 故障排查

| 现象 | 可能原因 | 解决方法 |
|---|---|---|
| `interface 4 not found` | 未检测到键盘或权限不足 | `lsusb \| grep 0b05:19fc`;确认 udev 规则已安装;拔插键盘 |
| `Permission denied` / `open failed` | udev 规则未生效 | `sudo udevadm control --reload-rules && sudo udevadm trigger`,然后重新插拔键盘 |
| 屏幕内容不变化 | 另一个程序正在写入屏幕 | `animematrix-bascule off`,关闭其他启动器或脚本 |
| 可视化器一直处于演示模式 | 没有 `parec` 或没有声音输出 | 安装 `pulseaudio-utils`,播放一些声音 |
| “Keyboard React” 无反应 | Wayland 会话或缺少 `pynput` | 改用 X11 会话,`sudo apt install python3-pynput` |
| 背景图库不启动 | 文件夹为空或不存在 | 在启动器的 GIF 标签页中选择一个文件夹 |
| 圆形窗口显示为矩形 | 缺少 SHAPE 扩展或 `python3-xlib` | `sudo apt install python3-xlib`,或在 *设置* → *界面：* → *经典* |
| 查看某个服务的日志 | — | `journalctl --user -u animematrix-galerie.service -f` |

<a id="depot"></a>

## 仓库结构

| 文件 | 作用 |
|---|---|
| `rog_flare2_launcher.py` | 图形启动器(Tk) |
| `rog_flare2_i18n.py`, `locale/` | 界面翻译（19 种语言，每种语言一个 JSON 目录） |
| `rog_flare2_themes.py` | 界面主题（ROG 与粉色） |
| `rog_flare2_ui_ronde.py` | 圆形界面(表盘 + 抽屉、表盘、圆角):绘制、窗口形状、LED 预览 |
| `rog_flare2_effets.py` | 效果与音频可视化器(移植自 PolyWollyWin 的引擎) |
| `polywollywin/` | PolyWollyWin 的效果引擎,原样复制(MIT 许可) |
| `rog_flare2_folder_player.py` | 背景图库(服务) |
| `rog_flare2_lecture.py` | 后台播放:接续启动器关闭时正在显示的内容(服务) |
| `rog_flare2_clock_v3.py` | 时钟(服务) |
| `rog_flare2_bascule.sh` | 图库 / 时钟 / 关闭之间的切换 |
| `rog_flare2_convertir.py` | GIF 转换(ImageMagick) |
| `rog_flare2_matrix_paint.py` | HID 传输、LED 顺序、绘图编辑器 |
| `parse_usbpcap.py`、`rog_flare2_replay_capture.py`、`*.cap` | 逆向工程工具与抓包文件 |
| `systemd/` | 用户服务 |
| `packaging/` | udev 规则、菜单项、图标,以及 .deb 软件包的文件与脚本 |
| `docs/` | GIF 指南、协议说明、截图 |

<a id="deb"></a>

## 构建 .deb 软件包

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

只需要 `dpkg-deb` 和 `bash`;版本号从 `rog_flare2_launcher.py`(`VERSION`)中读取。

<a id="credits"></a>

## 鸣谢

- **NicRoss512** —— 协议逆向工程、最初的时钟与绘图编辑器:[ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol)。本仓库由此衍生而来,并保留了其提交历史。
- **Mike Opitz** —— [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin)(MIT 许可),一个 Windows 控制程序,本项目沿用了其效果与音频可视化引擎。
- **Yoshi Walsh** —— [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/),提供了关于 LED 表现(光晕、感知灰度级别、刷新率)的说明。

本项目为独立项目,与 ASUS 无关联。“ROG”“AniMe Matrix”与“Armoury Crate”均为 ASUSTeK 的商标。

<a id="licence"></a>

## 许可证

本仓库代码采用 [MIT](../../LICENSE) 许可证。`polywollywin/` 目录仍遵循其作者的 MIT 许可([polywollywin/LICENSE](../../polywollywin/LICENSE))。NicRoss512 的原始文件(`rog_flare2_clock_v3.py`、`rog_flare2_matrix_paint.py`、`parse_usbpcap.py`、`rog_flare2_replay_capture.py`、`docs/PROTOCOL.md`、抓包文件)发布时未附带明确许可证,版权仍归其原作者所有;本项目在保留署名的前提下转载这些文件。

<a id="soutien"></a>

## 支持本项目

如果这个项目对你有帮助,一杯咖啡将有助于项目的持续维护:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=%E8%AF%B7%E6%88%91%E5%96%9D%E6%9D%AF%E5%92%96%E5%95%A1&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** —— 该链接同样可以在启动器的 *设置* 标签页中找到。

问题反馈与建议:[Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues)。
