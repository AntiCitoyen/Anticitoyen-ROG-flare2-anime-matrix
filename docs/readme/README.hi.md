<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# Linux के लिए AniMe Matrix — ROG Strix Flare II Animate

[![रिलीज़](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![CI](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml)
[![MIT लाइसेंस](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

बिना Armoury Crate या Windows के, Linux पर **ASUS ROG Strix Flare II Animate** कीबोर्ड की **AniMe Matrix** स्क्रीन (312 मिनी-LED) को नियंत्रित करें: GIF और गैलरी, घड़ी, इफ़ेक्ट्स और ऑडियो विज़ुअलाइज़र, गेम्स, सिस्टम मॉनिटर, डेस्कटॉप नोटिफ़िकेशन, समय शेड्यूलिंग, एनिमेशन एडिटर, साझा लाइब्रेरी, सिंक्रोनाइज़्ड कीबोर्ड रंग।

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · [🇧🇷 Português](README.pt-BR.md) · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · **🇮🇳 हिन्दी** · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/hi/interface-drawer.png" alt="डायल + ड्रॉअर" width="760"><br><em>डायल + ड्रॉअर (डिफ़ॉल्ट इंटरफ़ेस)</em></p>

| डायल | गोलाकार | क्लासिक |
|:---:|:---:|:---:|
| <img src="../captures/hi/interface-dial.png" alt="डायल" width="260"> | <img src="../captures/hi/interface-rounded.png" alt="गोलाकार" width="190"> | <img src="../captures/hi/interface-classic.png" alt="क्लासिक" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## विषय-सूची

- [प्रोजेक्ट क्या करता है](#projet)
- [समर्थित हार्डवेयर](#materiel)
- [इंस्टॉलेशन](#installation)
- [उपयोग](#utilisation)
- [अच्छे GIF तैयार करना](#gif)
- [यह कैसे काम करता है](#fonctionnement)
- [समस्या निवारण](#depannage)
- [रिपॉज़िटरी संरचना](#depot)
- [पैकेज बनाना](#deb)
- [श्रेय](#credits)
- [लाइसेंस](#licence)
- [प्रोजेक्ट को समर्थन दें](#soutien)

---

<a id="projet"></a>

## प्रोजेक्ट क्या करता है

ASUS इस कीबोर्ड की AniMe Matrix स्क्रीन केवल Windows (Armoury Crate) के अंतर्गत ही उपलब्ध कराता है। यह प्रोजेक्ट कीबोर्ड से सीधे USB HID के ज़रिए संवाद करता है और उपलब्ध कराता है:

**दिखाना**
- **GIF और छवियाँ**: एक फ़ाइल, चयनित फ़ाइलें, या पूरा फ़ोल्डर गैलरी के रूप में; स्ट्रीमिंग प्लेबैक (400 GIF की गैलरी लगभग 25 MB मेमोरी में चलती है)।
- HH:MM फ़ॉर्मैट में **घड़ी**।
- **19 एनिमेटेड इफ़ेक्ट** (Matrix जैसी बारिश, प्लाज़्मा, आग, तारे, आतिशबाज़ी, बिजली, मेटाबॉल, लहर, स्क्रॉलिंग टेक्स्ट…) और PC पर बज रहे साउंड पर प्रतिक्रिया देने वाले **7 ऑडियो विज़ुअलाइज़र**।
- **सिस्टम मॉनिटर**: CPU, RAM, GPU, तापमान, नेटवर्क स्पीड और समय, गेज के रूप में।
- **चल रहा गाना**: ट्रैक बदलने पर, « कलाकार - शीर्षक » एक बार स्क्रॉल होता है, फिर एक विज़ुअलाइज़र दिखता है (Spotify, VLC, Rhythmbox, ब्राउज़र… MPRIS के ज़रिए)।
- **डेस्कटॉप नोटिफ़िकेशन**: « ऐप: शीर्षक » ओवरले के रूप में दिखता है फिर प्लेबैक फिर से शुरू होता है (डिफ़ॉल्ट रूप से बंद, अनुमति प्राप्त ऐप्स की सूची के साथ)।
- कीबोर्ड पर **खेले जाने योग्य गेम्स**: Snake, Pong, Tetris, ब्रेकआउट, रिकॉर्ड्स के साथ।

**बनाना**
- स्क्रीन की वास्तविक ज्यामिति पर, फ़्रेम-दर-फ़्रेम **एनिमेशन एडिटर**: 3 स्तर, टाइमलाइन, घोस्ट लेयर, शिफ़्ट, कॉपी-पेस्ट, पूर्वावलोकन, कीबोर्ड को भेजना, GIF एक्सपोर्ट।
- साझा **एनिमेशन लाइब्रेरी**: ब्राउज़ करना, चलाना, अपनी गैलरी में जोड़ना, अपने खुद के प्रस्तावित करना।
- GIF का **स्मार्ट रूपांतरण**: विषय पर क्रॉपिंग, काली पृष्ठभूमि पर स्पष्ट विषय, मज़बूत किनारे, 3 स्तर।
- भेजने से पहले **सटीक पूर्वावलोकन**: स्क्रीन का सिम्युलेटेड रेंडर (वास्तविक लेआउट, LED के बीच हेलो)।
- **एक्सटेंशन के रूप में इफ़ेक्ट्स**: किसी फ़ोल्डर में रखी गई एक Python फ़ाइल एक इफ़ेक्ट जोड़ती है (देखें [docs/EXTENSIONS.md](../EXTENSIONS.md))।

**ऑटोमेट करना**
- **`animematrixd` बैकग्राउंड सर्विस**: स्क्रीन की अकेली मालिक, लॉन्चर बंद होने पर भी दिखाना जारी रखती है; `animematrix-ctl` कमांड और वैकल्पिक लोकल HTTP API।
- **समय शेड्यूलिंग**: घड़ी, गैलरी, मॉनिटर, चल रहे गाने या बंद स्क्रीन के साथ समय-सीमाएँ (रात सहित); सेशन लॉक होने पर, स्लीप में होने पर, या कोई ऐप फ़ुल-स्क्रीन में होने पर स्क्रीन काली रहती है।
- **OpenRGB के ज़रिए कीबोर्ड के रंग**: कीज़ पर थीम का रंग, या स्क्रीन के साथ पल्स।
- **सिस्टम ट्रे आइकन**: क्विक मेनू (मोड, ब्राइटनेस)।

**सुविधा**
- **4 इंटरफ़ेस** (डिफ़ॉल्ट रूप से *डायल + ड्रॉअर*, फिर *डायल*, *गोलाकार*, *क्लासिक*) **312 LED के लाइव पूर्वावलोकन** के साथ, **11 थीम** (5 ROG, 5 गुलाबी, सिस्टम) और **19 भाषाएँ**।
- **अंतर्निहित अपडेट**: लॉन्चर नवीनतम रिलीज़ डाउनलोड करता है, उसका SHA-256 फ़िंगरप्रिंट जाँचता है और उसे इंस्टॉल करता है (व्यवस्थापक पासवर्ड); या APT रिपॉज़िटरी के साथ `apt upgrade`।

<a id="materiel"></a>

## समर्थित हार्डवेयर

| डिवाइस | USB | स्थिति |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | समर्थित (HID, इंटरफ़ेस 4, यूसेज पेज `0xFF02`) |
| ROG लैपटॉप की AniMe Matrix स्क्रीन (G14, G16…) | विविध | `asusctl` के ज़रिए **प्रायोगिक**, हार्डवेयर पर परीक्षण नहीं किया गया (देखें [उपयोग](#utilisation)) |

Ubuntu 26.04 (X11, PipeWire, Cinnamon) पर परीक्षण किया गया। Python ≥ 3.10, hidapi, Tk और systemd वाला कोई भी डिस्ट्रीब्यूशन उपयुक्त होना चाहिए।

<a id="installation"></a>

## इंस्टॉलेशन

### APT रिपॉज़िटरी (Debian, Ubuntu, Mint, Pop!_OS…) — `apt upgrade` से अपडेट

```bash
curl -fsSL https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix/animematrix.gpg \
  | sudo tee /usr/share/keyrings/animematrix.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/animematrix.gpg] https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix stable main" \
  | sudo tee /etc/apt/sources.list.d/animematrix.list
sudo apt update && sudo apt install anticitoyen-rog-flare2-anime-matrix
```

फिर **कीबोर्ड को निकालें और फिर से लगाएँ** (udev रूल लॉग-इन किए हुए यूज़र को एक्सेस देता है) और मेनू से **AniMe Matrix** लॉन्च करें।

### अन्य फ़ॉर्मैट ([Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest) पेज)

| सिस्टम | फ़ाइल | इंस्टॉलेशन |
|---|---|---|
| Debian, Ubuntu… | `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` | `sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb` |
| Fedora, openSUSE… | `anticitoyen-rog-flare2-anime-matrix-<version>-1.noarch.rpm` | `sudo dnf install ./anticitoyen-rog-flare2-anime-matrix-*.noarch.rpm` |
| Arch, Manjaro… | `anticitoyen-rog-flare2-anime-matrix-<version>-1-any.pkg.tar.zst` | `sudo pacman -U anticitoyen-rog-flare2-anime-matrix-*.pkg.tar.zst` |
| सभी (Flatpak) | `AniMeMatrix-<version>.flatpak` | `flatpak install --user AniMeMatrix-*.flatpak` (नीचे दिया गया udev रूल भी इंस्टॉल करें; ऑडियो विज़ुअलाइज़र नहीं) |

पैकेज इंस्टॉल करता है:

| तत्व | स्थान |
|---|---|
| प्रोग्राम | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| कमांड | `animematrix`, `animematrixd`, `animematrix-ctl`, `animematrix-bascule`, `animematrix-animation`, `animematrix-apercu`, `animematrix-convertir`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-dessin`, `animematrix-tray` |
| यूज़र सर्विस | `/usr/lib/systemd/user/animematrixd.service` (सभी सेशन के लिए सक्रिय) |
| udev रूल | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| मेनू और आइकन | `animematrix.desktop`, आइकन `animematrix` |

### सोर्स से

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# root के बिना कीबोर्ड तक पहुँच
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# फिर कीबोर्ड निकालें और फिर से लगाएँ
.venv/bin/python rog_flare2_launcher.py
```

उपयोगी सिस्टम टूल: `imagemagick` (क्लासिक रूपांतरण), `pulseaudio-utils` (`parec`, ऑडियो के लिए), `zenity` (फ़ाइल चयनकर्ता), `libnotify-bin` (नोटिफ़िकेशन), `python3-gi` और `gir1.2-ayatanaappindicator3-0.1` (सिस्टम ट्रे आइकन), `openrgb` (कीज़ के रंग)।

<a id="utilisation"></a>

## उपयोग

### लॉन्चर

`animematrix` (या मेनू में **AniMe Matrix** एंट्री)।

गोल इंटरफ़ेस में, गोल बटन *GIF*, *इफ़ेक्ट्स*, *ऑडियो* और *सेटिंग्स* ब्लॉक खोलते हैं (ड्रॉअर में या वृत्त के अंदर); *घड़ी* और *रोकें* तुरंत असर करते हैं; नीचे का आर्क ब्राइटनेस सेट करता है; पृष्ठभूमि को खींचकर विंडो को हिलाया जाता है; ऊपर के छोटे बटन छोटा या बंद करते हैं। गोल आकार X11 SHAPE एक्सटेंशन का उपयोग करता है (`python3-xlib` पैकेज); इसके बिना, वही इंटरफ़ेस एक आयताकार विंडो में दिखता है।

- **GIF / छवियाँ**: *GIF/छवियाँ…* या *फ़ोल्डर (गैलरी)…*; *सटीक ज्यामिति* अनुपात बनाए रखती है (कोना छवि को खींचने के बजाय काटता है); *👁 सटीक पूर्वावलोकन (भेजने से पहले)* कुछ भी भेजे बिना रेंडर दिखाता है; *🎞 एनिमेशन बनाएं (एडिटर)*; *📚 एनिमेशन लाइब्रेरी*; GIF बदलने के लिए *स्मार्ट रूपांतरण*।
- **इफ़ेक्ट्स** और **ऑडियो**: चुनें, समायोजित करें, *▶ इफ़ेक्ट चलाएँ*। स्लाइडर तुरंत असर करते हैं; *लय* पूरे एनिमेशन को तेज़ या धीमा करती है। गेम्स ऐरो कीज़, स्पेस और एंटर से खेले जाते हैं, लॉन्चर विंडो सबसे आगे होनी चाहिए।
- **चमक**, **🕒 घड़ी**, **■ रोकें** (जो स्क्रीन साफ़ करता है) सभी टैब में समान रूप से उपलब्ध हैं।
- **सेटिंग्स**: सत्र शुरुआत (GIF गैलरी, घड़ी, पिछला प्लेबैक या कुछ नहीं), भाषा, थीम, इंटरफ़ेस, डेस्कटॉप नोटिफ़िकेशन, कीबोर्ड के रंग (OpenRGB), *शेड्यूल…*, सिस्टम ट्रे आइकन, एक्सटेंशन फ़ोल्डर, अपडेट।

**लॉन्चर बंद करना कुछ भी नहीं रोकता**: `animematrixd` बैकग्राउंड सर्विस दिखाना जारी रखती है। *■ रोकें* स्क्रीन को बंद कर देता है।

### बैकग्राउंड सर्विस और कमांड लाइन

```bash
animematrix-ctl etat                               # क्या दिखाया जा रहा है
animematrix-ctl gif ~/Images/AniMe-Matrix --fidele # गैलरी (फ़ोल्डर या फ़ाइलें)
animematrix-ctl effet "Plasma" --param speed=250   # इफ़ेक्ट और सेटिंग्स
animematrix-ctl horloge
animematrix-ctl texte "Bonjour"
animematrix-ctl notifier "Café prêt" --duree 5     # ओवरले फिर वापसी
animematrix-ctl luminosite 60
animematrix-ctl stop
```

| कमांड | भूमिका |
|---|---|
| `animematrix-bascule [gif\|horloge\|lecture\|off\|etat]` | टॉगल (मेनू आइकन के राइट-क्लिक में भी); चुना गया मोड सत्र शुरुआत का मोड भी होता है |
| `animematrixd --http 8765` | लोकल HTTP API वाली बैकग्राउंड सर्विस (`POST http://127.0.0.1:8765/api`, सॉकेट जैसा ही JSON) |
| `animematrix-animation [fichier.gif]` | एनिमेशन एडिटर |
| `animematrix-apercu fichier.gif -o apercu.gif` | किसी GIF (फ़ाइल) का सटीक पूर्वावलोकन |
| `animematrix-convertir dossier/ [--fidele] [--classique]` | मैट्रिक्स के लिए GIF रूपांतरित करता है (`dossier/matrix/` में) |
| `animematrix-effet --liste` | इफ़ेक्ट्स और विज़ुअलाइज़र की सूची दिखाता है |
| `animematrix-dessin` | LED-दर-LED एडिटर (बंद होने पर नियंत्रण बैकग्राउंड सर्विस को सौंपता है) |

### ऑडियो

विज़ुअलाइज़र `parec` (PipeWire या PulseAudio) के ज़रिए **डिफ़ॉल्ट साउंड आउटपुट के मॉनिटर** को सुनते हैं: वे PC पर बज रहे साउंड पर प्रतिक्रिया देते हैं, माइक्रोफ़ोन पर नहीं।

### « Keyboard React » इफ़ेक्ट

यह `pynput` की मदद से टाइपिंग की लय पर स्क्रीन को जगाता है, जो जब तक इफ़ेक्ट चलता है तब तक पूरे सेशन की-प्रेस पढ़ता रहता है। यह X11 पर काम करता है; Wayland पर यह की-प्रेस प्राप्त नहीं करता।

### कीबोर्ड के रंग (OpenRGB)

*सेटिंग्स* → *कीबोर्ड के रंग (OpenRGB)*: थीम का रंग या स्क्रीन के साथ पल्स। बैकग्राउंड सर्विस ज़रूरत पड़ने पर `openrgb --server` शुरू करती है। OpenRGB को कीबोर्ड की पिछली लाइटिंग पता नहीं होती: कीबोर्ड में सेव किए गए इफ़ेक्ट को वापस पाने के लिए, उसे निकालें और फिर से लगाएँ।

### ROG लैपटॉप (प्रायोगिक)

`~/.config/rog-flare2/materiel` में `portable-asusctl` लिखें फिर बैकग्राउंड सर्विस को फिर से शुरू करें: फ़्रेम `asusctl anime image` के ज़रिए जाते हैं (अधिकतम 5 फ़्रेम प्रति सेकंड)। किसी वास्तविक लैपटॉप पर परीक्षण नहीं किया गया: टिकट्स में फ़ीडबैक का स्वागत है।

<a id="gif"></a>

## अच्छे GIF तैयार करना

स्क्रीन कोई आयत नहीं है: 24 ऑफ़सेट पंक्तियाँ, ऊपर 19 से नीचे 7 LED तक (दायाँ किनारा सीधा, बायाँ किनारा तिरछा), वास्तव में अलग-अलग दिखने वाले 3 ग्रे स्तर, पड़ोसी LED के बीच एक हेलो। सिल्हूट, पिक्टोग्राम, छोटे टेक्स्ट और धीमी गति अच्छी दिखती है; फ़ोटो और वीडियो नहीं।

पूरी गाइड (कैनवस, स्तर, गति, रूपांतरण, सटीक ज्यामिति): **[docs/GUIDE-GIF.md](../GUIDE-GIF.md)**।

<a id="fonctionnement"></a>

## यह कैसे काम करता है

- **ट्रांसपोर्ट**: hidapi कीबोर्ड का HID इंटरफ़ेस नंबर 4 खोलता है और उसमें **1024 बाइट** के फ़्रेम लिखता है; कीबोर्ड हर फ़्रेम वापस भेजता है।
- **फ़्रेम**: `60 81 00 00` + **312 बाइट** (हार्डवेयर क्रम में प्रति LED 0-255 चमक) + 1024 तक शून्य।
- **ज्यामिति**: 24 ऑफ़सेट पंक्तियाँ (पंक्ति r कॉलम (r+1)//2 से 18 तक कवर करती है), या समकक्ष रूप से 37 → 15 कॉलम की 12 लॉजिकल पंक्तियाँ (PolyWollyWin मॉडल); दोनों मैपिंग सभी 312 LED पर समान पाई गई हैं।
- **बैकग्राउंड सर्विस**: `animematrixd` अकेले कीबोर्ड को संभालती है; बुनियादी प्लेबैक और ओवरले (नोटिफ़िकेशन); JSON सॉकेट `$XDG_RUNTIME_DIR/animematrix.sock`; कीबोर्ड का ऑटोमैटिक फिर से कनेक्ट होना।
- **एनिमेशन**: होस्ट फ़्रेम एक के बाद एक भेजता है (इफ़ेक्ट्स के लिए लगभग 30 फ़्रेम/सेकंड); कीबोर्ड की अंतर्निहित मेमोरी इस्तेमाल नहीं होती (रिसर्च: [docs/RECHERCHE-MEMOIRE.md](../RECHERCHE-MEMOIRE.md))।

मूल रिवर्स-इंजीनियरिंग नोट्स **[docs/PROTOCOL.md](../PROTOCOL.md)** में हैं; `*.cap` कैप्चर और `parse_usbpcap.py` / `rog_flare2_replay_capture.py` टूल रिपॉज़िटरी में बने रहते हैं।

⚠️ लैपटॉप के AniMe Matrix पैकेट (`0x5E …`, `0xEC …`) कीबोर्ड को न भेजें: यह सही प्रोटोकॉल नहीं है और कीबोर्ड को ब्लॉक कर सकता है (निकालें और फिर से लगाएँ, या **Fn + Esc** को 10-15 सेकंड दबाए रखें)।

<a id="depannage"></a>

## समस्या निवारण

| लक्षण | संभावित कारण | समाधान |
|---|---|---|
| `interface 4 not found` | कीबोर्ड नहीं दिख रहा या अधिकार नहीं हैं | `lsusb \| grep 0b05:19fc`; क्या udev रूल इंस्टॉल है? निकालें और फिर से लगाएँ |
| `Permission denied` / `open failed` | udev रूल लागू नहीं हुआ | `sudo udevadm control --reload-rules && sudo udevadm trigger`, फिर फिर से लगाएँ |
| « animematrixd सर्विस तक नहीं पहुँचा जा सका » | बैकग्राउंड सर्विस रुकी हुई है | `systemctl --user restart animematrixd.service` या `animematrixd &` |
| स्क्रीन नहीं बदलती | कोई और प्रोग्राम कीबोर्ड पर लिख रहा है | पुरानी स्क्रिप्ट बंद करें; `animematrix-ctl etat` |
| विज़ुअलाइज़र डेमो मोड में बने रहते हैं | `parec` नहीं है या साउंड नहीं है | `pulseaudio-utils` इंस्टॉल करें, साउंड बजाएँ |
| « Keyboard React » प्रतिक्रिया नहीं देता | Wayland सेशन या `pynput` अनुपलब्ध | X11 सेशन, `sudo apt install python3-pynput` |
| गोल विंडो आयताकार दिखती है | SHAPE एक्सटेंशन या `python3-xlib` मौजूद नहीं है | `sudo apt install python3-xlib`, या *सेटिंग्स* → *इंटरफ़ेस:* → *क्लासिक* |
| OpenRGB के बाद कीज़ एक ही रंग में रहती हैं | OpenRGB मूल इफ़ेक्ट को फिर से नहीं बना पाता | कीबोर्ड को निकालें और फिर से लगाएँ |
| बैकग्राउंड सर्विस का लॉग | — | `journalctl --user -u animematrixd.service -f` |

<a id="depot"></a>

## रिपॉज़िटरी संरचना

| फ़ाइल | भूमिका |
|---|---|
| `rog_flare2_launcher.py` | ग्राफ़िकल लॉन्चर (Tk) |
| `rog_flare2_ui_ronde.py`, `rog_flare2_themes.py` | गोल इंटरफ़ेस, थीम |
| `rog_flare2_i18n.py`, `locale/` | अनुवाद (19 भाषाएँ; `locale/_cles.json` = अनुवाद किए जाने वाले टेक्स्ट) |
| `rog_flare2_demon.py`, `rog_flare2_ctl.py` | `animematrixd` बैकग्राउंड सर्विस, क्लाइंट और `animematrix-ctl` कमांड |
| `rog_flare2_core.py` | GIF स्ट्रीमिंग प्लेबैक, घड़ी, ज्यामिति |
| `rog_flare2_effets.py`, `polywollywin/` | इफ़ेक्ट्स और विज़ुअलाइज़र (PolyWollyWin इंजन, MIT), एक्सटेंशन |
| `rog_flare2_infos.py`, `rog_flare2_mpris.py`, `rog_flare2_jeux.py` | सिस्टम मॉनिटर, चल रहा गाना, गेम्स |
| `rog_flare2_notifs.py`, `rog_flare2_programme.py`, `rog_flare2_ui_programme.py` | नोटिफ़िकेशन, समय शेड्यूलिंग और ट्रिगर |
| `rog_flare2_openrgb.py`, `rog_flare2_tray.py`, `rog_flare2_portable.py` | OpenRGB के ज़रिए रंग, सिस्टम ट्रे आइकन, लैपटॉप (प्रायोगिक) |
| `rog_flare2_animation.py`, `rog_flare2_simulateur.py`, `rog_flare2_convertir.py` | एनिमेशन एडिटर, सिम्युलेटर, रूपांतरण |
| `rog_flare2_bibliotheque.py`, `bibliotheque/` | एनिमेशन लाइब्रेरी (कैटलॉग, CC0 GIF) |
| `rog_flare2_maj.py` | रिलीज़ से अपडेट |
| `rog_flare2_matrix_paint.py`, `rog_flare2_clock_v3.py`, `rog_flare2_folder_player.py` | HID ट्रांसपोर्ट और LED एडिटर, घड़ी, गैलरी (मूल टूल) |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | रिवर्स-इंजीनियरिंग |
| `examples/effets/` | एक्सटेंशन का उदाहरण |
| `tests/` | टेस्ट (वास्तविक क्लिक वाले इंटरफ़ेस टेस्ट सहित) |
| `systemd/`, `packaging/` | यूज़र सर्विस; .deb, RPM, Arch, Flatpak, APT रिपॉज़िटरी |
| `docs/` | GIF गाइड, एक्सटेंशन, प्रोटोकॉल, रिसर्च, स्क्रीनशॉट, अनुवादित README |

<a id="deb"></a>

## पैकेज बनाना

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

`packaging/install.sh` प्रोजेक्ट को किसी भी डायरेक्टरी स्ट्रक्चर में इंस्टॉल करता है; यह .deb, RPM (`packaging/rpm/`), Arch पैकेज (`packaging/aur/`) और Flatpak (`packaging/flatpak/`) के लिए इस्तेमाल होता है। हर पब्लिश की गई रिलीज़ पर, GitHub RPM, Arch पैकेज और Flatpak बनाता है, और साइन किए गए APT रिपॉज़िटरी को अपडेट करता है। वर्ज़न `rog_flare2_core.py` (`VERSION`) से पढ़ा जाता है। टेस्ट: `python -m pytest tests`।

<a id="credits"></a>

## श्रेय

- **NicRoss512** — प्रोटोकॉल की रिवर्स-इंजीनियरिंग, मूल घड़ी और एडिटर: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol)। यह रिपॉज़िटरी वहीं से शुरू होती है; इसका इतिहास सुरक्षित रखा गया है।
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin) (MIT), Windows कंट्रोलर जिसका इफ़ेक्ट और ऑडियो विज़ुअलाइज़र इंजन यहाँ इस्तेमाल किया गया है।
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), LED व्यवहार (हेलो, दिखने वाले स्तर, गति) के लिए।
- **asus-linux** — [asusctl](https://gitlab.com/asus-linux/asusctl), लैपटॉप स्क्रीन के लिए इस्तेमाल किया गया।

यह एक स्वतंत्र प्रोजेक्ट है, ASUS से संबद्ध नहीं। "ROG", "AniMe Matrix" और "Armoury Crate" ASUSTeK के ट्रेडमार्क हैं।

<a id="licence"></a>

## लाइसेंस

इस रिपॉज़िटरी के कोड के लिए [MIT](../../LICENSE); `bibliotheque/` के एनिमेशन CC0 के अंतर्गत हैं। `polywollywin/` अपने लेखक के MIT लाइसेंस के अंतर्गत ही रहता है ([polywollywin/LICENSE](../../polywollywin/LICENSE))। NicRoss512 की मूल फ़ाइलें (`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `docs/PROTOCOL.md`, कैप्चर) बिना किसी स्पष्ट लाइसेंस के प्रकाशित की गई थीं और अपने लेखक की ही रहती हैं; इन्हें श्रेय के साथ फिर से वितरित किया जाता है।

<a id="soutien"></a>

## प्रोजेक्ट को समर्थन दें

अगर यह प्रोजेक्ट आपके काम आता है, तो एक कॉफ़ी इसे बनाए रखने में मदद करती है:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=%E0%A4%AE%E0%A5%81%E0%A4%9D%E0%A5%87%20%E0%A4%8F%E0%A4%95%20%E0%A4%95%E0%A5%89%E0%A4%AB%E0%A4%BC%E0%A5%80%20%E0%A4%AA%E0%A4%BF%E0%A4%B2%E0%A4%BE%E0%A4%8F%E0%A4%81&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — यह लिंक लॉन्चर के *सेटिंग्स* टैब में भी मौजूद है।

बग रिपोर्ट, विचार, और साझा करने के लिए एनिमेशन: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues)।
