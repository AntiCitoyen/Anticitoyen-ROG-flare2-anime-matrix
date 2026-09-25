<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# Linux için AniMe Matrix — ROG Strix Flare II Animate

[![Sürüm](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![CI](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml)
[![MIT Lisansı](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

**ASUS ROG Strix Flare II Animate** klavyesinin **AniMe Matrix** ekranını (312 mini-LED) Linux üzerinden, Armoury Crate veya Windows olmadan yönetin: GIF ve galeri, saat, efektler ve ses görselleştiricileri, oyunlar, sistem monitörü, masaüstü bildirimleri, zaman programlama, animasyon düzenleyici, paylaşılan kütüphane, senkronize klavye renkleri.

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · **🇹🇷 Türkçe** · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/tr/interface-drawer.png" alt="Kadran + çekmece" width="760"><br><em>Kadran + çekmece (varsayılan arayüz)</em></p>

| Kadran | Yuvarlatılmış | Klasik |
|:---:|:---:|:---:|
| <img src="../captures/tr/interface-dial.png" alt="Kadran" width="260"> | <img src="../captures/tr/interface-rounded.png" alt="Yuvarlatılmış" width="190"> | <img src="../captures/tr/interface-classic.png" alt="Klasik" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## İçindekiler

- [Projenin yaptıkları](#projet)
- [Desteklenen donanım](#materiel)
- [Kurulum](#installation)
- [Kullanım](#utilisation)
- [İyi GIF'ler hazırlama](#gif)
- [Nasıl çalışır](#fonctionnement)
- [Sorun giderme](#depannage)
- [Depo düzeni](#depot)
- [Paketleri oluşturma](#deb)
- [Emeği geçenler](#credits)
- [Lisans](#licence)
- [Projeyi destekleyin](#soutien)

---

<a id="projet"></a>

## Projenin yaptıkları

ASUS, bu klavyenin AniMe Matrix ekranını yalnızca Windows (Armoury Crate) altında sunar. Bu proje klavyeyle doğrudan USB HID üzerinden konuşur ve şunları sunar:

**Görüntüleme**
- **GIF, görüntüler ve videolar**: tek bir dosya, bir seçim ya da tüm bir klasör galeri olarak, pencereye sürükle-bırak ile; videolar (MP4, WebM, MKV…) ffmpeg ile oynatılır; küçük resim galerisi; dönüştürülen kareler önbellekte tutulur (400 GIF'lik bir galeri yaklaşık 25 MB bellekte çalışır).
- **Saat**: dijital, analog, ikili, kelimelerle (Fransızca, İngilizce, Almanca, İspanyolca, İtalyanca, Portekizce, Felemenkçe) veya stilize kadran.
- **Animasyonlu efektler** (Matrix tarzı yağmur, plazma, ateş, yıldızlar, havai fişekler, şimşekler, metaball'lar, dalga…) ve bilgisayarda çalan sese tepki veren **7 ses görselleştirici**.
- **Metin**: mesajınız, tüm yazı sistemlerinde (aksanlı harfler, Kiril, Arapça, Hintçe, Çince, Japonca, Korece…), sola, sağa, yukarı, aşağı kayan ya da sabit.
- **Web kamerası** (görüntü veya siluet) ve **ekran yansıtma** (tüm ekran, fare çevresi veya etkin pencere).
- **Sistem monitörü**: CPU, RAM, GPU, sıcaklık, ağ hızı ve saat, gösterge şeklinde.
- **Çalan parça**: parça değiştiğinde bir kez « SANATÇI - BAŞLIK » kayan yazı olarak geçer, ardından bir görselleştirici gösterilir (Spotify, VLC, Rhythmbox, tarayıcılar… MPRIS üzerinden).
- **Masaüstü bildirimleri**: « UYGULAMA: BAŞLIK » ekranın üzerinde belirir, ardından oynatma kaldığı yerden devam eder (varsayılan olarak kapalı, izin verilen uygulamalar listesiyle).
- Klavyeyle **oynanabilir oyunlar**: Snake, Pong (tek başına veya iki kişi), Tetris, kırma oyunu, Invaders, Flappy, en yüksek skorlarla.
- **Göstergeler**: mikrofon kapatıldığında veya kullanıldığında, web kamerası çalıştığında, OBS yayın yaptığında veya kayıt aldığında yanan küçük ışıklı bloklar.
- **Klavye belleği**: klavyeye kaydedilen bir animasyon (GIF, görüntü), takılır takılmaz hiçbir yazılım olmadan, başka bir bilgisayarda bile oynar; ayarlanabilir parlaklık (GIF sekmesi, `animematrix-ctl memoire`).

**Oluşturma**
- Ekranın gerçek geometrisi üzerinde kare kare çalışan **animasyon düzenleyici**: 3 seviye, zaman çizelgesi, hayalet katman, kaydırma, kopyala-yapıştır, önizleme, klavyeye gönderme, GIF olarak dışa aktarma.
- Paylaşılan **animasyon kitaplığı**: göz atma, oynatma, kendi galerine ekleme, kendi animasyonlarını önerme.
- GIF'ler için **akıllı dönüştürme**: konuya göre kırpma, siyah zemin üzerinde açık renkli konu, güçlendirilmiş kenarlar, 3 seviye.
- Göndermeden önce **gerçekçi önizleme**: ekranın simüle edilmiş görüntüsü (gerçek yerleşim, LED'ler arası halo).
- **Eklenti olarak efektler**: bir klasöre bırakılan bir Python dosyası yeni bir efekt ekler (bkz. [docs/EXTENSIONS.md](../EXTENSIONS.md)).

**Otomasyon**
- **`animematrixd` arka plan servisi**: ekranın tek sahibi olarak, başlatıcı kapatıldığında da göstermeye devam eder; `animematrix-ctl` komutu ve isteğe bağlı yerel HTTP API'si.
- **Zaman programlama**: saat, galeri, monitör, çalan parça, bir efekt, bir oynatma listesi veya kapalı ekran ile (gece dahil) zaman aralıkları; oturum kilitliyken, uyku modundayken veya bir uygulama tam ekrandayken ekran siyah kalır.
- **Uygulama profilleri**: bir oyun veya uygulama ön planda olduğu sürece ona özel içerik (*Algıla* düğmesi).
- **Oynatma listeleri ve favoriler**: GIF'ler, efektler, saat… her biri kendi süresince, döngü halinde; sistem tepsisi simgesinde ve komut satırında da.
- **Web kumandası**: yerel ağdaki bir telefondan ekranı yönetmek için bir sayfa (QR kod, belirteç).
- **Uzun komutların bitişi**: terminalde uzun bir komut bittiğinde « Tamamlandı: make 2 min 05 » gösterilir.
- **Tuş renkleri ve efektleri**, OpenRGB olmadan: gökkuşağı, sabit, nefes, renk döngüsü, tepkili, dalgalanma, yıldızlı gece, bataklık kumu, akıntı, yağmur — klavyenin kendisi çalıştırır ve çıkarıldıktan sonra da kalır; ya da tema rengi, ekranla nabız.
- **Sistem tepsisi simgesi**: hızlı menü (modlar, parlaklık).

**Kullanım kolaylığı**
- **4 arayüz** (varsayılan olarak *Kadran + çekmece*, *Kadran*, *Yuvarlatılmış*, *Klasik*) ile **312 LED'in canlı önizlemesi**, **11 tema** (5 ROG, 5 pembe, sistem) ve **19 dil**.
- **X11 ve Wayland**: evdev ile klavye tepkisi, etkin pencere Sway, Hyprland, KDE (kdotool) veya GNOME (*Window Calls* uzantısı) üzerinden okunur.
- **Yerleşik güncellemeler**: başlatıcı en son sürümü indirir, SHA-256 özetini doğrular ve kurar (yönetici parolası); ya da APT deposuyla `apt upgrade`.

<a id="materiel"></a>

## Desteklenen donanım

| Cihaz | USB | Durum |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | destekleniyor (HID, arayüz 4, kullanım sayfası `0xFF02`) |
| ROG dizüstü bilgisayarlarının AniMe Matrix ekranları (G14, G16…) | çeşitli | `asusctl` üzerinden **deneysel**, donanımda test edilmedi (bkz. [Kullanım](#utilisation)) |

Ubuntu 26.04 (X11, PipeWire, Cinnamon) üzerinde test edildi. Python ≥ 3.10, hidapi, Tk ve systemd içeren her dağıtım uygun olmalıdır; Wayland altında başlatıcı XWayland üzerinden çalışır.

<a id="installation"></a>

## Kurulum

### APT deposu (Debian, Ubuntu, Mint, Pop!_OS…) — `apt upgrade` ile güncellemeler

```bash
curl -fsSL https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix/animematrix.gpg \
  | sudo tee /usr/share/keyrings/animematrix.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/animematrix.gpg] https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix stable main" \
  | sudo tee /etc/apt/sources.list.d/animematrix.list
sudo apt update && sudo apt install anticitoyen-rog-flare2-anime-matrix
```

Ardından **klavyeyi çıkarıp yeniden takın** (udev kuralı, oturum açmış kullanıcıya erişim verir) ve menüden **AniMe Matrix**'i başlatın.

### Diğer biçimler ([Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) sayfası)

| Sistem | Dosya | Kurulum |
|---|---|---|
| Debian, Ubuntu… | `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` | `sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb` |
| Fedora, openSUSE… | `anticitoyen-rog-flare2-anime-matrix-<version>-1.noarch.rpm` | `sudo dnf install ./anticitoyen-rog-flare2-anime-matrix-*.noarch.rpm` |
| Arch, Manjaro… | `anticitoyen-rog-flare2-anime-matrix-<version>-1-any.pkg.tar.zst` | `sudo pacman -U anticitoyen-rog-flare2-anime-matrix-*.pkg.tar.zst` |
| Hepsi (Flatpak) | `AniMeMatrix-<version>.flatpak` | `flatpak install --user AniMeMatrix-*.flatpak` (aşağıdaki udev kuralını da kurun; ses görselleştiricileri yok) |

Paket şunları kurar:

| Öğe | Konum |
|---|---|
| Programlar | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| Komutlar | `animematrix`, `animematrixd`, `animematrix-ctl`, `animematrix-bascule`, `animematrix-animation`, `animematrix-apercu`, `animematrix-convertir`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-dessin`, `animematrix-tray`, `animematrix-memoire` |
| Kullanıcı servisi | `/usr/lib/systemd/user/animematrixd.service` (tüm oturumlar için etkin) |
| udev kuralı | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| Menü ve simge | `animematrix.desktop`, `animematrix` simgesi |

### Kaynak koddan

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# root olmadan klavyeye erişim
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# ardından klavyeyi çıkarıp yeniden takın
.venv/bin/python rog_flare2_launcher.py
```

Faydalı sistem araçları: `imagemagick` (klasik dönüştürme), `pulseaudio-utils` (`parec`, ses için), `zenity` (dosya seçiciler), `libnotify-bin` (bildirimler), `python3-gi` ve `gir1.2-ayatanaappindicator3-0.1` (sistem tepsisi simgesi), `ffmpeg` (videolar, web kamerası, ekran yansıtma), `python3-evdev` (Wayland altında klavye tepkisi), `x11-utils` (X11 altında etkin pencere), `python3-qrcode` (kumandanın QR kodu), `tkdnd` (sürükle-bırak).

<a id="utilisation"></a>

## Kullanım

### Başlatıcı

`animematrix` (veya menüdeki **AniMe Matrix** girişi).

Yuvarlak arayüzlerde, yuvarlak düğmeler *GIF*, *Efektler*, *Ses* ve *Ayarlar* bloklarını açar (çekmecede veya çemberin içinde); *Saat* ve *Durdur* hemen etkili olur; alttaki yay parlaklığı ayarlar; pencere, arka planından tutularak taşınır; üstteki küçük düğmeler küçültür veya kapatır. Yuvarlak biçim X11 SHAPE uzantısını kullanır (`python3-xlib` paketi); bu uzantı yoksa, aynı arayüz dikdörtgen bir pencerede görüntülenir.

- **GIF / görüntüler**: seçim için *GIF/görüntüler…* veya tüm klasör için *Klasör (galeri)…* (veya pencereye sürükle-bırak); *Gerçek geometri* oranları korur (köşe, görüntüyü uzatmak yerine keser); *👁 Gerçekçi önizleme (göndermeden önce)* hiçbir şey göndermeden görüntüyü gösterir; *🎞 Animasyon oluştur (düzenleyici)*; *📚 Animasyon kitaplığı*; *★ Oynatma listeleri ve favoriler*; *🖼 Küçük resim galerisi* (tıkla: oynat, sağ tık: favori); *🎥 Web kamerası* ve *🖥 Ekran yansıtma*; GIF'leri dönüştürmek için *Akıllı dönüştürme*.
- **Efektler** ve **Ses**: seçin, ayarlayın, *▶ Efekti başlat*. Kaydırıcılar anında etki eder; *Tempo* tüm animasyonu hızlandırır veya yavaşlatır. *Metin* efekti mesajınızı ve kayma yönünü alır. Oyunlar ok tuşları, Boşluk ve Enter ile oynanır, başlatıcı penceresi önde olmalıdır; iki kişilik Pong: sol oyuncu için Z/W ve S.
- **Parlaklık**, **🕒 Saat**, **■ Durdur** (ekranı temizler) tüm sekmelerde ortaktır.
- **Ayarlar**: oturum başlangıcı (GIF galerisi, Saat, Son oynatma veya Hiçbiri), saat kadranı, dil, tema, arayüz, masaüstü bildirimleri, klavye renkleri, *Zamanlama…* (tetikleyiciler, uygulama profilleri, zaman aralıkları), *Göstergeler (mikrofon, web kamerası, OBS)…*, *Web kumandası…*, sistem tepsisi simgesi, uzun komutların bitişi, eklentiler klasörü, güncellemeler.

**Başlatıcıyı kapatmak hiçbir şeyi durdurmaz**: `animematrixd` arka plan servisi göstermeye devam eder. *■ Durdur*, ekranı kapatır.

### Arka plan servisi ve komut satırı

```bash
animematrix-ctl etat                               # şu anda ne gösteriliyor
animematrix-ctl gif ~/Images/AniMe-Matrix --fidele # galeri (klasör veya dosyalar)
animematrix-ctl effet "Plasma" --param speed=250   # efekt ve ayarlar
animematrix-ctl horloge
animematrix-ctl texte "Bonjour"
animematrix-ctl effet "Text" --param message="Salut" --param direction=haut
animematrix-ctl liste "Soirée"                     # oynatma listesi (adsız: listeleri gösterir)
animematrix-ctl favori 2                           # 2 numaralı favori (numarasız: favorileri gösterir)
animematrix-ctl notifier "Café prêt" --duree 5     # üstte gösterilir sonra geri döner
animematrix-ctl memoire anim.gif                   # klavyeye kaydedilir (en fazla 196 kare)
animematrix-ctl clavier                            # kayıtlı animasyonu gösterir
animematrix-ctl luminosite 60
animematrix-ctl stop
```

| Komut | Rol |
|---|---|
| `animematrix-bascule [gif\|horloge\|lecture\|off\|etat]` | geçiş yapar (menü simgesinin sağ tıkında da bulunur); seçilen mod aynı zamanda oturum başlangıcı modudur |
| `animematrixd --http 8765` | yerel HTTP API'li arka plan servisi (`POST http://127.0.0.1:8765/api`, soket ile aynı JSON) |
| `animematrix-animation [fichier.gif]` | animasyon düzenleyici |
| `animematrix-apercu fichier.gif -o apercu.gif` | bir GIF'in (dosya) gerçekçi önizlemesi |
| `animematrix-convertir dossier/ [--fidele] [--classique]` | GIF'leri matris için dönüştürür (`dossier/matrix/` içine) |
| `animematrix-effet --liste` | efektleri ve görselleştiricileri listeler |
| `animematrix-dessin` | LED LED çizim düzenleyici (kapanınca kontrolü arka plan servisine bırakır) |

### Ses

Görselleştiriciler, `parec` (PipeWire veya PulseAudio) ile **varsayılan ses çıkışının monitörünü** dinler: mikrofona değil, bilgisayarın çaldığı sese tepki verirler.

### « Keyboard React » efekti

Efekt çalıştığı sürece yazma ritmine göre ekranı yakar: X11 altında `pynput` ile, Wayland altında klavyeyi `/dev/input` içinden okuyarak (`python3-evdev`). Wayland altında efekt demo modunda kalırsa, yalnızca ROG klavyesinin okunmasına izin verin:

```bash
sudo cp /usr/share/anticitoyen-rog-flare2-anime-matrix/udev/73-rog-flare2-animate-touches.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Göstergeler

*Ayarlar* → *Göstergeler (mikrofon, web kamerası, OBS)…*: ekranın sol üst köşesinde, oynatmanın üzerinde 2 × 2 LED'lik bir blok yanar (1: mikrofon kapalı veya kullanımda, 2: web kamerası kullanımda, 3: OBS canlı yayında veya kayıtta) ve her değişiklik kayan bir yazıyla duyurulabilir. OBS: WebSocket sunucusunu etkinleştirin (*Araçlar* → *WebSocket Sunucu Ayarları*) ve bağlantı noktasını ve parolasını buraya girin.

### Web kumandası

*Ayarlar* → *Web kumandası…*: *Web kumandasını etkinleştir* kutusunu işaretleyin, ardından aynı ağdaki bir telefonda adresi açın (veya QR kodu okutun). Sayfa ekranı canlı gösterir ve saat, galeri, efektler, favoriler, listeler, parlaklık ve mesaj sunar. Adres bir belirteç içerir: paylaşmayın, *Yeni belirteç* ile değiştirin; sayfa şifrelenmemiştir (HTTP): yalnızca güvenilir ağlarda kullanın.

### Uzun komutların bitişi

*Ayarlar* → *Uzun komutların bitişini göster (terminal)*, `~/.bashrc` (ve `~/.zshrc`) dosyasına bir satır ekler: 30 saniyeden uzun süren her komut bittiğinde « Tamamlandı: make 2 min 05 » veya « Başarısız (2): … » gösterir. Eşik: `ANIMEMATRIX_FIN_SECONDES`; etkileşimli komutlar (düzenleyiciler, `ssh`, `less`…) yok sayılır.

### Klavye renkleri

*Ayarlar* → *🌈 Klavye renkleri…*: efekt (gökkuşağı, sabit, nefes, renk döngüsü, tepkili, dalgalanma, yıldızlı gece, bataklık kumu, akıntı, yağmur), renkler, hız, parlaklık, yön. *Dene* uygular, *Klavyeye kaydet* çıkarıldıktan sonra da korur. *Tema rengi* ve *Ekranla nabız* hizmet tarafından tuş tuş gönderilir; bunlardan çıkınca kayıtlı efekt geri gelir. Komut satırından: `animematrix-ctl rgb arc-en-ciel --vitesse 70`, `animematrix-ctl rgb statique --couleur "#ff0000"`.

### ROG dizüstü bilgisayarlar (deneysel)

`~/.config/rog-flare2/materiel` dosyasına `portable-asusctl` yazın, ardından arka plan servisini yeniden başlatın: kareler `asusctl anime image` üzerinden gönderilir (saniyede en fazla 5 kare). Gerçek bir dizüstü bilgisayarda test edilmedi: geri bildirimler ticketlerde memnuniyetle karşılanır.

<a id="gif"></a>

## İyi GIF'ler hazırlama

Ekran bir dikdörtgen değildir: üstte 19'dan alta 7 LED'e kadar kayan 24 satır (sağ kenar dikey, sol kenar köşegen), gerçekten ayrık 3 gri seviyesi, komşu LED'ler arasında bir halo. Silüetler, piktogramlar, kısa metinler ve yavaş hareketler iyi görünür; fotoğraflar ve videolar ise pek görünmez.

Tam kılavuz (tuval, seviyeler, hız, dönüştürme, gerçek geometri): **[docs/GUIDE-GIF.md](../GUIDE-GIF.md)**.

<a id="fonctionnement"></a>

## Nasıl çalışır

- **Aktarım**: hidapi, klavyenin 4 numaralı HID arayüzünü açar ve buraya **1024 baytlık** çerçeveler yazar; klavye her çerçeveyi geri gönderir.
- **Çerçeve**: `60 81 00 00` + **312 bayt** (donanım sırasına göre LED başına 0-255 parlaklık) + 1024'e kadar sıfırlar.
- **Geometri**: 24 kayan satır (r satırı (r+1)//2 ile 18 arasındaki sütunları kapsar), ya da eşdeğer olarak 37 → 15 sütunlu 12 mantıksal satır (PolyWollyWin modeli); iki eşlemenin de 312 LED üzerinde aynı olduğu doğrulanmıştır.
- **Arka plan servisi**: `animematrixd` klavyeyi tek başına elinde tutar; temel oynatma ve üst katman (bildirimler); `$XDG_RUNTIME_DIR/animematrix.sock` JSON soketi; klavyenin otomatik yeniden bağlanması.
- **Animasyon**: ana bilgisayar çerçeveleri art arda gönderir (efektler için ~30 kare/sn); klavyenin dahili belleği kullanılmaz (araştırma: [docs/RECHERCHE-MEMOIRE.md](../RECHERCHE-MEMOIRE.md)).

Orijinal tersine mühendislik notları **[docs/PROTOCOL.md](../PROTOCOL.md)** içindedir; `*.cap` kayıtları ve `parse_usbpcap.py` / `rog_flare2_replay_capture.py` araçları depoda kalmaya devam eder.

⚠️ Dizüstü bilgisayarların AniMe Matrix paketlerini (`0x5E …`, `0xEC …`) klavyeye göndermeyin: bu doğru protokol değildir ve klavyeyi kilitleyebilir (çıkarıp yeniden takın, veya **Fn + Esc**'i 10-15 saniye basılı tutun).

<a id="depannage"></a>

## Sorun giderme

| Belirti | Olası neden | Çözüm |
|---|---|---|
| `interface 4 not found` | klavye görülmüyor veya izin yok | `lsusb \| grep 0b05:19fc`; udev kuralı kurulu mu? çıkarıp yeniden takın |
| `Permission denied` / `open failed` | udev kuralı uygulanmamış | `sudo udevadm control --reload-rules && sudo udevadm trigger`, ardından yeniden takın |
| « animematrixd servisine ulaşılamıyor » | arka plan servisi durmuş | `systemctl --user restart animematrixd.service` veya `animematrixd &` |
| Ekran değişmiyor | başka bir program klavyeye yazıyor | eski betikleri kapatın; `animematrix-ctl etat` |
| Görselleştiriciler demo modunda kalıyor | `parec` yok veya ses yok | `pulseaudio-utils` kurun, ses çalın |
| « Keyboard React » tepki vermiyor | `pynput` (X11) veya `python3-evdev` (Wayland) eksik ya da klavye okunamıyor | paketi kurun; Wayland altında [Keyboard React](#utilisation) bölümündeki udev kuralı |
| Web kamerası, videolar veya ekran yansıtma çalışmıyor | `ffmpeg` eksik | `sudo apt install ffmpeg`; Wayland altında ekran yansıtma portal üzerinden geçer (`gstreamer1.0-pipewire`) |
| Uygulama profilleri veya tam ekran Wayland altında etkisiz | etkin pencere bileşikleyici tarafından bilinmiyor | GNOME: *Window Calls* uzantısı; KDE: `kdotool`; Sway ve Hyprland: yapılacak bir şey yok |
| Yuvarlak pencere dikdörtgen görünüyor | SHAPE uzantısı veya `python3-xlib` eksik | `sudo apt install python3-xlib`, veya *Ayarlar* → *Arayüz:* → *Klasik* |
| Arka plan servisinin günlüğü | — | `journalctl --user -u animematrixd.service -f` |

<a id="depot"></a>

## Depo düzeni

| Dosya | İşlev |
|---|---|
| `rog_flare2_launcher.py` | grafik başlatıcı (Tk) |
| `rog_flare2_ui_ronde.py`, `rog_flare2_themes.py` | yuvarlak arayüzler, temalar |
| `rog_flare2_i18n.py`, `locale/` | çeviri (19 dil; `locale/_cles.json` = çevrilecek metinler; [docs/TRADUIRE.md](../TRADUIRE.md)) |
| `rog_flare2_demon.py`, `rog_flare2_ctl.py` | `animematrixd` arka plan servisi, istemci ve `animematrix-ctl` komutu |
| `rog_flare2_core.py` | GIF akışlı oynatma, kare önbelleği, saat, geometri |
| `rog_flare2_texte.py`, `rog_flare2_horloges.py` | tüm yazı sistemlerinde metin, *Metin* efekti, saat kadranları |
| `rog_flare2_listes.py`, `rog_flare2_vignettes.py` | oynatma listeleri, favoriler, küçük resim galerisi, sürükle-bırak |
| `rog_flare2_video.py`, `rog_flare2_voyants.py`, `rog_flare2_telecommande.py` | videolar, web kamerası, ekran yansıtma; göstergeler; web kumandası |
| `rog_flare2_touches.py`, `rog_flare2_fenetre.py`, `rog_flare2_fin.py`, `rog_flare2_flatpak.py` | tuşlar ve etkin pencere (X11, Wayland), uzun komutların bitişi, Flatpak |
| `rog_flare2_effets.py`, `polywollywin/` | efektler ve görselleştiriciler (PolyWollyWin motoru, MIT), eklentiler |
| `rog_flare2_infos.py`, `rog_flare2_mpris.py`, `rog_flare2_jeux.py` | sistem monitörü, çalan parça, oyunlar |
| `rog_flare2_notifs.py`, `rog_flare2_programme.py`, `rog_flare2_ui_programme.py` | bildirimler, zaman programlama ve tetikleyiciler |
| `rog_flare2_rgb.py`, `rog_flare2_tray.py`, `rog_flare2_portable.py` | tuş renkleri ve efektleri, sistem tepsisi simgesi, dizüstü bilgisayarlar (deneysel) |
| `rog_flare2_animation.py`, `rog_flare2_simulateur.py`, `rog_flare2_convertir.py` | animasyon düzenleyici, simülatör, dönüştürme |
| `rog_flare2_bibliotheque.py`, `bibliotheque/` | animasyon kitaplığı (katalog, CC0 GIF'ler) |
| `rog_flare2_maj.py` | sürümlerden güncellemeler |
| `rog_flare2_matrix_paint.py`, `rog_flare2_clock_v3.py`, `rog_flare2_folder_player.py` | HID aktarımı ve LED düzenleyici, saat, galeri (orijinal araçlar) |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | tersine mühendislik |
| `examples/effets/` | eklenti örneği |
| `tests/` | testler (gerçek tıklamalarla arayüz testleri dahil) |
| `systemd/`, `packaging/` | kullanıcı servisi; .deb, RPM, Arch, Flatpak, APT deposu |
| `docs/` | GIF kılavuzu, eklentiler, protokol, araştırma, ekran görüntüleri, çevrilmiş README'ler |

<a id="deb"></a>

## Paketleri oluşturma

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

`packaging/install.sh`, projeyi herhangi bir dizin ağacına kurar; .deb, RPM (`packaging/rpm/`), Arch paketi (`packaging/aur/`) ve Flatpak (`packaging/flathub/`) için kullanılır. Her yayımlanan sürümde GitHub, RPM'i, Arch paketini ve Flatpak'ı oluşturur ve imzalı APT deposunu günceller. Sürüm numarası `rog_flare2_core.py` (`VERSION`) içinden okunur. Testler: `python -m pytest tests`.

<a id="credits"></a>

## Emeği geçenler

- **NicRoss512** — protokolün tersine mühendisliği, orijinal saat ve düzenleyici: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol). Bu depo buradan yola çıkar; geçmişi korunmuştur.
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin) (MIT), efekt ve ses görselleştirici motoru buradan alınan Windows denetleyicisi.
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), LED davranışı için (halo, algılanan seviyeler, hız).
- **asus-linux** — [asusctl](https://gitlab.com/asus-linux/asusctl), dizüstü bilgisayar ekranları için kullanılmıştır.

Bağımsız bir proje, ASUS ile bağlantılı değildir. "ROG", "AniMe Matrix" ve "Armoury Crate" ASUSTeK'in ticari markalarıdır.

<a id="licence"></a>

## Lisans

Bu deponun kodu için [MIT](../../LICENSE); `bibliotheque/` içindeki animasyonlar CC0 altındadır. `polywollywin/`, yazarının MIT lisansı altında kalır ([polywollywin/LICENSE](../../polywollywin/LICENSE)). NicRoss512'nin orijinal dosyaları (`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `docs/PROTOCOL.md`, kayıtlar) açık bir lisans olmadan yayımlanmıştır ve yazarına aittir; atıfla birlikte yeniden dağıtılmaktadır.

<a id="soutien"></a>

## Projeyi destekleyin

Bu proje işinize yarıyorsa, bir kahve onu sürdürmeye yardımcı olur:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Bir%20kahve%20%C4%B1smarla&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — bağlantı, başlatıcının *Ayarlar* sekmesinde de bulunur.

Hata bildirimleri, fikirler ve paylaşılacak animasyonlar: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues). Çeviriler: [docs/TRADUIRE.md](../TRADUIRE.md).
