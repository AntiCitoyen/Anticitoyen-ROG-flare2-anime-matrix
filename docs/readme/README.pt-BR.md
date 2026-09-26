<p align="center">
  <img src="../../packaging/animematrix.svg" alt="AniMe Matrix" width="160">
</p>

# AniMe Matrix para Linux — ROG Strix Flare II Animate

[![Release](https://img.shields.io/github/v/release/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest)
[![CI](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/actions/workflows/ci.yml)
[![Licença MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](../../LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-soutenir-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/anticitoyen)

Controle no Linux a tela **AniMe Matrix** (312 mini-LEDs) do teclado **ASUS ROG Strix Flare II Animate**, sem Armoury Crate nem Windows: GIFs e galeria, relógio, efeitos e visualizadores de áudio, jogos, monitor do sistema, notificações da área de trabalho, programação horária, editor de animação, biblioteca compartilhada, cores do teclado sincronizadas.

<div align="center">

[🇫🇷 Français](../../README.md) · [🇬🇧 English](README.en.md) · [🇪🇸 Español](README.es.md) · [🇩🇪 Deutsch](README.de.md) · [🇮🇹 Italiano](README.it.md) · **🇧🇷 Português** · [🇳🇱 Nederlands](README.nl.md) · [🇵🇱 Polski](README.pl.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇹🇼 繁體中文](README.zh-TW.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇮🇩 Bahasa Indonesia](README.id.md)

</div>

<p align="center"><img src="../captures/pt-BR/interface-drawer.png" alt="Mostrador + gaveta" width="760"><br><em>Mostrador + gaveta (interface padrão)</em></p>

| Mostrador | Arredondada | Clássica |
|:---:|:---:|:---:|
| <img src="../captures/pt-BR/interface-dial.png" alt="Mostrador" width="260"> | <img src="../captures/pt-BR/interface-rounded.png" alt="Arredondada" width="190"> | <img src="../captures/pt-BR/interface-classic.png" alt="Clássica" width="220"> |

<p align="center"><img src="../captures/themes-en.png" alt="Themes" width="100%"></p>

---

## Sumário

- [O que o projeto faz](#projet)
- [Hardware compatível](#materiel)
- [Instalação](#installation)
- [Uso](#utilisation)
- [Preparar bons GIFs](#gif)
- [Como funciona](#fonctionnement)
- [Solução de problemas](#depannage)
- [Organização do repositório](#depot)
- [Compilar os pacotes](#deb)
- [Créditos](#credits)
- [Licença](#licence)
- [Apoiar o projeto](#soutien)

---

<a id="projet"></a>

## O que o projeto faz

A ASUS só fornece a tela AniMe Matrix deste teclado no Windows (Armoury Crate). Este projeto fala diretamente com o teclado via USB HID e traz:

**Exibir**
- **GIFs, imagens e vídeos**: um arquivo, uma seleção ou uma pasta inteira em galeria, para arrastar e soltar na janela; vídeos (MP4, WebM, MKV…) reproduzidos pelo ffmpeg; galeria de miniaturas; quadros convertidos mantidos em cache (uma galeria de 400 GIFs cabe em ~25 MB de memória).
- **Relógio**: mostrador digital, analógico, binário, por extenso (francês, inglês, alemão, espanhol, italiano, português, holandês) ou estilizado.
- **Efeitos animados** (chuva estilo Matrix, plasma, fogo, estrelas, fogos de artifício, raios, metaballs, onda…) e **7 visualizadores de áudio** que reagem ao som reproduzido pelo PC.
- **Texto**: sua mensagem, em todas as escritas (acentos, cirílico, árabe, hindi, chinês, japonês, coreano…), rolando para a esquerda, para a direita, para cima, para baixo, ou fixa.
- **Webcam** (imagem ou silhueta) e **espelhamento de tela** (tela inteira, ao redor do mouse ou janela ativa).
- **Monitor do sistema**: CPU, RAM, GPU, temperatura, taxa de rede e hora, em medidores.
- **Música tocando agora**: ao trocar de faixa, « ARTISTA - TÍTULO » desliza uma vez, depois um visualizador (Spotify, VLC, Rhythmbox, navegadores… via MPRIS).
- **Notificações da área de trabalho**: « APP: TÍTULO » aparece em sobreposição e depois a reprodução retoma (desativado por padrão, lista de aplicativos autorizados).
- **Jogos** jogáveis pelo teclado: Snake, Pong (sozinho ou a dois), Tetris, quebra-blocos, Invaders, Flappy, com recordes.
- **Indicadores**: pequenos blocos luminosos quando o microfone está mudo ou em uso, quando a webcam está ligada, quando o OBS transmite ou grava.
- **Memória do teclado**: uma animação (GIF, imagem) salva no teclado aparece sem nenhum software, assim que ele é conectado, até em outro PC; brilho ajustável (aba GIF, `animematrix-ctl memoire`). As 6 animações integradas (KO, Meteorito, Olho, Love, Halloween, Inicialização) também podem ser escolhidas: `animematrix-ctl clavier 1`…`6`.

**Criar**
- **Editor de animação** quadro a quadro, na geometria real da tela: 3 níveis, tira de quadros, camada fantasma, deslocamento, copiar e colar, prévia, envio ao teclado, exportação em GIF.
- **Biblioteca de animações** compartilhada: navegar, reproduzir, adicionar à própria galeria, propor as suas.
- **Conversão inteligente** de GIFs: recorte no assunto, assunto claro sobre fundo preto, contornos reforçados, 3 níveis.
- **Prévia fiel** antes do envio: renderização simulada da tela (disposição real, halo entre LEDs).
- **Efeitos em extensões**: um arquivo Python colocado em uma pasta adiciona um efeito (veja [../EXTENSIONS.md](../EXTENSIONS.md)).

**Automatizar**
- **Daemon `animematrixd`**: único dono da tela, continua exibindo quando o lançador é fechado; comando `animematrix-ctl` e API HTTP local opcional.
- **Programação horária**: faixas (dias, incluindo a noite) com relógio, galeria, monitor, música tocando, um efeito, uma playlist ou tela apagada; tela preta quando a sessão está bloqueada, em suspensão ou quando um aplicativo está em tela cheia.
- **Perfis por aplicativo**: um conteúdo próprio de um jogo ou aplicativo enquanto ele estiver em primeiro plano (botão *Detectar*).
- **Playlists e favoritos**: GIFs, efeitos, relógio… cada um durante seu tempo, em loop; também no ícone da bandeja do sistema e na linha de comando.
- **Controle remoto web**: uma página para controlar a tela a partir de um celular da rede local (QR code, token).
- **Fim de comandos longos**: no terminal, « Concluído : make 2 min 05 » é exibido quando um comando longo termina.
- **Cores e efeitos das teclas**, sem OpenRGB: arco-íris, estático, respiração, ciclo, reativo, ondulação, noite estrelada, areia movediça, corrente, chuva — executados pelo teclado e mantidos após desconectá-lo; ou a cor do tema, pulsar com a tela.
- **Ícone na bandeja do sistema**: menu rápido (modos, brilho).

**Conforto**
- **4 interfaces** (*Mostrador + gaveta* padrão, *Mostrador*, *Arredondada*, *Clássica*) com **prévia ao vivo dos 312 LEDs**, **11 temas** (5 ROG, 5 rosa, sistema) e **19 idiomas**.
- **X11 e Wayland**: reação ao teclado via evdev, janela ativa lida no Sway, Hyprland, KDE (kdotool) ou GNOME (extensão *Window Calls*).
- **Atualizações integradas**: o lançador baixa a última release, verifica sua soma SHA-256 e a instala (senha de administrador); ou `apt upgrade` com o repositório APT.

<a id="materiel"></a>

## Hardware compatível

| Dispositivo | USB | Estado |
|---|---|---|
| ASUS ROG Strix Flare II Animate | `0b05:19fc` | compatível (HID, interface 4, usage page `0xFF02`) |
| Telas AniMe Matrix dos notebooks ROG (G14, G16…) | vários | **experimental** via `asusctl`, não testado em hardware (veja [Uso](#utilisation)) |

Testado no Ubuntu 26.04 (X11, PipeWire, Cinnamon). Qualquer distribuição com Python ≥ 3.10, hidapi, Tk e systemd deve funcionar; no Wayland, o lançador usa o XWayland.

<a id="installation"></a>

## Instalação

### Repositório APT (Debian, Ubuntu, Mint, Pop!_OS…) — atualizações com `apt upgrade`

```bash
curl -fsSL https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix/animematrix.gpg \
  | sudo tee /usr/share/keyrings/animematrix.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/animematrix.gpg] https://anticitoyen.github.io/Anticitoyen-ROG-flare2-anime-matrix stable main" \
  | sudo tee /etc/apt/sources.list.d/animematrix.list
sudo apt update && sudo apt install anticitoyen-rog-flare2-anime-matrix
```

Depois **desconectar e reconectar o teclado** (a regra udev concede o acesso ao usuário conectado) e iniciar **AniMe Matrix** pelo menu.

### Outros formatos (página [Releases](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/releases/latest))

| Sistema | Arquivo | Instalação |
|---|---|---|
| Debian, Ubuntu… | `anticitoyen-rog-flare2-anime-matrix_<version>_all.deb` | `sudo apt install ./anticitoyen-rog-flare2-anime-matrix_*_all.deb` |
| Fedora, openSUSE… | `anticitoyen-rog-flare2-anime-matrix-<version>-1.noarch.rpm` | `sudo dnf install ./anticitoyen-rog-flare2-anime-matrix-*.noarch.rpm` |
| Arch, Manjaro… | `anticitoyen-rog-flare2-anime-matrix-<version>-1-any.pkg.tar.zst` | `sudo pacman -U anticitoyen-rog-flare2-anime-matrix-*.pkg.tar.zst` |
| Todos (Flatpak) | `AniMeMatrix-<version>.flatpak` | `flatpak install --user AniMeMatrix-*.flatpak` (instalar também a regra udev abaixo; sem visualizadores de áudio) |
| AUR | `aur-<version>.tar.gz` | PKGBUILD e .SRCINFO: `tar xf aur-*.tar.gz && cd anticitoyen-rog-flare2-anime-matrix && makepkg -si` |
| Copr | `anticitoyen-rog-flare2-anime-matrix-<version>-1.<fc>.src.rpm` | RPM fonte: `rpmbuild --rebuild anticitoyen-rog-flare2-anime-matrix-*.src.rpm`, ou enviar a um projeto Copr |
| Flathub | `flathub-<version>.tar.gz` | manifesto fixado nesta versão e `python3-modules.json`: envio ao Flathub ou `flatpak-builder` |
| Weblate | `translations-<version>.zip` | arquivos de tradução (`locale/*.json`, base `_source.json`) para importar no Weblate |

O pacote instala:

| Item | Local |
|---|---|
| Programas | `/usr/share/anticitoyen-rog-flare2-anime-matrix/` |
| Comandos | `animematrix`, `animematrixd`, `animematrix-ctl`, `animematrix-bascule`, `animematrix-animation`, `animematrix-apercu`, `animematrix-convertir`, `animematrix-effet`, `animematrix-galerie`, `animematrix-horloge`, `animematrix-dessin`, `animematrix-tray`, `animematrix-memoire` |
| Serviço de usuário | `/usr/lib/systemd/user/animematrixd.service` (ativado para todas as sessões) |
| Regra udev | `/usr/lib/udev/rules.d/72-rog-flare2-animate.rules` |
| Menu e ícone | `animematrix.desktop`, ícone `animematrix` |

### A partir do código-fonte

```bash
git clone https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix.git
cd Anticitoyen-ROG-flare2-anime-matrix
python3 -m venv .venv
.venv/bin/pip install hidapi pillow numpy pynput python-xlib
# acesso ao teclado sem root
sudo cp packaging/72-rog-flare2-animate.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
# depois desconectar/reconectar o teclado
.venv/bin/python rog_flare2_launcher.py
```

Ferramentas de sistema úteis: `imagemagick` (conversão clássica), `pulseaudio-utils` (`parec`, para áudio), `zenity` (seletores de arquivo), `libnotify-bin` (notificações), `python3-gi` e `gir1.2-ayatanaappindicator3-0.1` (ícone na bandeja do sistema), `ffmpeg` (vídeos, webcam, espelhamento de tela), `python3-evdev` (reação ao teclado no Wayland), `x11-utils` (janela ativa no X11), `python3-qrcode` (QR code do controle remoto), `tkdnd` (arrastar e soltar).

<a id="utilisation"></a>

## Uso

### O lançador

`animematrix` (ou a entrada **AniMe Matrix** do menu).

Nas interfaces redondas, os botões redondos abrem os blocos *GIF*, *Efeitos*, *Áudio* e *Configurações* (na gaveta ou no círculo); *Relógio* e *Parar* agem imediatamente; o arco inferior ajusta o brilho; a janela é movida arrastando-a pelo fundo; os pequenos botões no topo minimizam ou fecham. A forma redonda usa a extensão X11 SHAPE (pacote `python3-xlib`); sem ela, a mesma interface é exibida em uma janela retangular.

- **GIF / imagens**: *GIF/imagens…* ou *Pasta (galeria)…* (ou arrastar e soltar na janela); *Geometria fiel* mantém as proporções (o canto corta a imagem em vez de esticá-la); *👁 Prévia fiel (antes de enviar)* mostra a renderização sem enviar nada; *🎞 Criar uma animação (editor)*; *📚 Biblioteca de animações*; *★ Playlists e favoritos*; *🖼 Galeria de miniaturas* (clique: reproduzir, clique direito: favorito); *🎥 Webcam* e *🖥 Espelhamento de tela*; *Conversão inteligente* para converter GIFs.
- **Efeitos** e **Áudio**: escolher, ajustar, *▶ Iniciar o efeito*. Os controles deslizantes agem em tempo real; *Ritmo* acelera ou desacelera toda a animação. O efeito *Texto* recebe sua mensagem e o sentido de rolagem. Os jogos se jogam com as setas, Espaço e Enter, com a janela do lançador em primeiro plano; Pong a dois: Z/W e S para o jogador da esquerda.
- **Brilho**, **🕒 Relógio**, **■ Parar** (que apaga a tela) são comuns a todas as abas.
- **Configurações**: início da sessão (Galeria de GIF, Relógio, Última reprodução ou Nada), mostrador do relógio, idioma, tema, interface, notificações da área de trabalho, cores do teclado, *Programação…* (gatilhos, perfis por aplicativo, faixas horárias), *Indicadores…*, *Controle remoto web…*, ícone na bandeja do sistema, fim de comandos longos, pasta de extensões, atualizações.

**Fechar o lançador não interrompe nada**: o daemon `animematrixd` continua exibindo. *■ Parar* apaga a tela.

### Daemon e linha de comando

```bash
animematrix-ctl etat                               # o que está sendo exibido
animematrix-ctl gif ~/Images/AniMe-Matrix --fidele # galeria (pasta ou arquivos)
animematrix-ctl effet "Plasma" --param speed=250   # efeito e ajustes
animematrix-ctl horloge
animematrix-ctl texte "Bonjour"
animematrix-ctl effet "Text" --param message="Salut" --param direction=haut
animematrix-ctl liste "Soirée"                     # playlist (sem nome: lista as playlists)
animematrix-ctl favori 2                           # favorito nº 2 (sem número: lista os favoritos)
animematrix-ctl notifier "Café prêt" --duree 5     # sobreposição e depois retorno
animematrix-ctl memoire anim.gif                   # salva no teclado (no máximo 196 quadros)
animematrix-ctl clavier                            # mostra a animação salva
animematrix-ctl luminosite 60
animematrix-ctl stop
```

| Comando | Função |
|---|---|
| `animematrix-bascule [gif\|horloge\|lecture\|off\|etat]` | alternador (também no clique direito do ícone do menu); o modo escolhido é também o do início da sessão |
| `animematrixd --http 8765` | daemon com API HTTP local (`POST http://127.0.0.1:8765/api`, `Content-Type: application/json`, mesmo JSON do socket) |
| `animematrix-animation [arquivo.gif]` | editor de animação |
| `animematrix-apercu arquivo.gif -o previa.gif` | prévia fiel de um GIF (arquivo) |
| `animematrix-convertir pasta/ [--fidele] [--classique]` | converte GIFs para a matriz (em `pasta/matrix/`) |
| `animematrix-effet --liste` | lista os efeitos e visualizadores |
| `animematrix-dessin` | editor LED por LED (devolve o controle ao daemon ao fechar) |
| `animematrix-ctl sauvegarde reglages.zip`, `animematrix-ctl restaurer reglages.zip` | exporta ou restaura todas as configurações (também em *Configurações*); sem o token nem a senha do OBS, exceto com `--secrets` |

### Áudio

Os visualizadores escutam o **monitor da saída de áudio padrão** com `parec` (PipeWire ou PulseAudio): reagem ao que o PC reproduz, não ao microfone.

### Efeito « Keyboard React »

Ele acende a tela no ritmo da digitação, enquanto o efeito está ativo: no X11 via `pynput`, no Wayland lendo o teclado em `/dev/input` (`python3-evdev`). No Wayland, se o efeito ficar em modo demonstração, autorize a leitura apenas do teclado ROG:

```bash
sudo cp /usr/share/anticitoyen-rog-flare2-anime-matrix/udev/73-rog-flare2-animate-touches.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Indicadores

*Configurações* → *Indicadores (microfone, webcam, OBS)…*: um bloco de 2 × 2 LEDs acende no canto superior esquerdo da tela, por cima da reprodução (1: microfone mudo ou em uso, 2: webcam em uso, 3: OBS ao vivo ou gravando), e cada mudança pode ser anunciada por um texto rolante. OBS: ative o servidor WebSocket (*Ferramentas* → *Configurações do servidor WebSocket*) e informe a porta e a senha dele.

### Controle remoto web

*Configurações* → *Controle remoto web…*: marque *Ativar*, depois abra o endereço (ou leia o QR code) em um celular da mesma rede. A página mostra a tela ao vivo e oferece relógio, galeria, efeitos, favoritos, playlists, brilho e mensagem. O endereço contém um token: não o compartilhe, troque-o com *Novo token*; a página não é criptografada (HTTP): use somente em rede confiável.

### Fim de comandos longos

*Configurações* → *Exibir o fim de comandos longos (terminal)* adiciona uma linha ao `~/.bashrc` (e ao `~/.zshrc`): todo comando de mais de 30 segundos exibe ao terminar « Concluído : make 2 min 05 » ou « Falha (2) : … ». Limite: `ANIMEMATRIX_FIN_SECONDES`; os comandos interativos (editores, `ssh`, `less`…) são ignorados.

### Cores do teclado

*Configurações* → *🌈 Cores do teclado…*: efeito (arco-íris, estático, respiração, ciclo de cores, reativo, ondulação, noite estrelada, areia movediça, corrente, chuva), cores, velocidade, brilho, direção. *Testar* aplica, *Salvar no teclado* mantém após desconectar. *Cor do tema* e *Pulsar com a tela* são enviados tecla por tecla pelo daemon; ao sair deles, o efeito salvo volta. Na linha de comando: `animematrix-ctl rgb arc-en-ciel --vitesse 70`, `animematrix-ctl rgb statique --couleur "#ff0000"`. Mais dois modos de software: *Imagem da tela* (as teclas reproduzem a tela, ampliada) e *Espectro de áudio* (uma barra por coluna). Cada faixa horária e cada perfil de aplicativo também pode escolher as cores das teclas (*Programação…*). *Tecla por tecla*: uma cor por tecla, pintada com o mouse em um mapa do teclado (AZERTY ou QWERTY). *Digitação luminosa*: cada tecla pressionada acende e depois se apaga. Os indicadores de microfone, webcam e OBS também podem acender F1, F2 e F3, e cada notificação faz as teclas piscarem.

<p align="center"><img src="../captures/pt-BR/couleurs.png" alt="🌈" width="330"> <img src="../captures/pt-BR/touches.png" alt="⌨" width="620"></p>

### Notebooks ROG (experimental)

Escrever `portable-asusctl` em `~/.config/rog-flare2/materiel` e depois reiniciar o daemon: os quadros passam por `asusctl anime image` (no máximo 5 imagens por segundo). Não testado em um notebook real: retornos são bem-vindos nos tickets.

<a id="gif"></a>

## Preparar bons GIFs

A tela não é um retângulo: 24 fileiras deslocadas, de 19 LEDs no topo a 7 na base (borda direita vertical, borda esquerda em diagonal), 3 níveis de cinza realmente distintos, um halo entre LEDs vizinhos. Silhuetas, pictogramas, textos curtos e movimentos lentos ficam bons; fotos e vídeos, pouco.

O guia completo (tela, níveis, ritmo, conversão, geometria fiel): **[../GUIDE-GIF.md](../GUIDE-GIF.md)**.

<a id="fonctionnement"></a>

## Como funciona

- **Transporte**: o hidapi abre a interface HID nº 4 do teclado e nela escreve quadros de **1024 bytes**; o teclado devolve cada quadro.
- **Quadro**: `60 81 00 00` + **312 bytes** (um brilho de 0–255 por LED, na ordem do hardware) + zeros até 1024.
- **Geometria**: 24 fileiras deslocadas (a fileira r cobre as colunas (r+1)//2 até 18), ou de forma equivalente 12 fileiras lógicas de 37 → 15 colunas (modelo do PolyWollyWin); as duas correspondências foram verificadas como idênticas nos 312 LEDs.
- **Daemon**: `animematrixd` controla sozinho o teclado; reprodução básica e sobreposição (notificações); socket JSON `$XDG_RUNTIME_DIR/animematrix.sock`; reconexão automática do teclado.
- **Animação**: o host envia os quadros um após o outro (~30 q/s para os efeitos); a memória interna do teclado não é usada (pesquisa: [../RECHERCHE-MEMOIRE.md](../RECHERCHE-MEMOIRE.md)).

As notas originais de engenharia reversa estão em **[../PROTOCOL.md](../PROTOCOL.md)**; as capturas `*.cap` e as ferramentas `parse_usbpcap.py` / `rog_flare2_replay_capture.py` permanecem no repositório.

⚠️ Não envie ao teclado os pacotes dos AniMe Matrix de notebooks (`0x5E …`, `0xEC …`): não é o protocolo correto e pode travar o teclado (desconectar/reconectar, ou manter pressionado **Fn + Esc** por 10–15 s).

<a id="depannage"></a>

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `interface 4 not found` | teclado não detectado ou sem permissões | `lsusb \| grep 0b05:19fc`; regra udev instalada? desconectar/reconectar |
| `Permission denied` / `open failed` | regra udev não aplicada | `sudo udevadm control --reload-rules && sudo udevadm trigger`, depois reconectar |
| « Serviço animematrixd inacessível » | daemon parado | `systemctl --user restart animematrixd.service` ou `animematrixd &` |
| A tela não muda | outro programa está escrevendo no teclado | fechar scripts antigos; `animematrix-ctl etat` |
| Os visualizadores ficam em modo demonstração | sem `parec` ou sem som | instalar `pulseaudio-utils`, reproduzir som |
| « Keyboard React » não reage | `pynput` (X11) ou `python3-evdev` (Wayland) ausente, ou teclado ilegível | instalar o pacote; no Wayland, a regra udev de [Keyboard React](#utilisation) |
| Webcam, vídeos ou espelhamento de tela inativos | `ffmpeg` ausente | `sudo apt install ffmpeg`; no Wayland, o espelhamento de tela passa pelo portal (`gstreamer1.0-pipewire`) |
| Perfis por aplicativo ou tela cheia sem efeito no Wayland | janela ativa desconhecida pelo compositor | GNOME: extensão *Window Calls*; KDE: `kdotool`; Sway e Hyprland: nada a fazer |
| A janela redonda aparece como um retângulo | extensão SHAPE ou `python3-xlib` ausente | `sudo apt install python3-xlib`, ou *Configurações* → *Interface:* → *Clássica* |
| Log do daemon | — | `journalctl --user -u animematrixd.service -f` |

<a id="depot"></a>

## Organização do repositório

| Arquivo | Função |
|---|---|
| `rog_flare2_launcher.py` | lançador gráfico (Tk) |
| `rog_flare2_ui_ronde.py`, `rog_flare2_themes.py` | interfaces redondas, temas |
| `rog_flare2_i18n.py`, `locale/` | tradução (19 idiomas; `locale/_cles.json` = textos a traduzir; [../TRADUIRE.md](../TRADUIRE.md)) |
| `rog_flare2_demon.py`, `rog_flare2_ctl.py` | daemon `animematrixd`, cliente e comando `animematrix-ctl` |
| `rog_flare2_core.py` | reprodução de GIF em fluxo, cache de quadros, relógio, geometria |
| `rog_flare2_texte.py`, `rog_flare2_horloges.py` | texto em todas as escritas, efeito *Texto*, mostradores do relógio |
| `rog_flare2_listes.py`, `rog_flare2_vignettes.py` | playlists, favoritos, galeria de miniaturas, arrastar e soltar |
| `rog_flare2_video.py`, `rog_flare2_voyants.py`, `rog_flare2_telecommande.py` | vídeos, webcam, espelhamento de tela; indicadores; controle remoto web |
| `rog_flare2_touches.py`, `rog_flare2_fenetre.py`, `rog_flare2_fin.py`, `rog_flare2_flatpak.py` | teclas e janela ativa (X11, Wayland), fim de comandos longos, Flatpak |
| `rog_flare2_effets.py`, `polywollywin/` | efeitos e visualizadores (motor PolyWollyWin, MIT), extensões |
| `rog_flare2_infos.py`, `rog_flare2_mpris.py`, `rog_flare2_jeux.py` | monitor do sistema, música tocando, jogos |
| `rog_flare2_notifs.py`, `rog_flare2_programme.py`, `rog_flare2_ui_programme.py` | notificações, programação horária e gatilhos |
| `rog_flare2_rgb.py`, `rog_flare2_tray.py`, `rog_flare2_portable.py` | cores e efeitos das teclas, ícone na bandeja do sistema, notebooks (experimental) |
| `rog_flare2_animation.py`, `rog_flare2_simulateur.py`, `rog_flare2_convertir.py` | editor de animação, simulador, conversão |
| `rog_flare2_bibliotheque.py`, `bibliotheque/` | biblioteca de animações (catálogo, GIFs CC0) |
| `rog_flare2_maj.py` | atualizações a partir das releases |
| `rog_flare2_matrix_paint.py`, `rog_flare2_clock_v3.py`, `rog_flare2_folder_player.py` | transporte HID e editor LED, relógio, galeria (ferramentas originais) |
| `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `*.cap` | engenharia reversa |
| `examples/effets/` | exemplo de extensão |
| `tests/` | testes (incluindo interfaces com cliques reais) |
| `systemd/`, `packaging/` | serviço de usuário; .deb, RPM, Arch, Flatpak, repositório APT |
| `docs/` | guia de GIF, extensões, protocolo, pesquisa, capturas de tela, READMEs traduzidos |

<a id="deb"></a>

## Compilar os pacotes

```bash
packaging/build-deb.sh
# → dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
```

`packaging/install.sh` instala o projeto em qualquer estrutura de diretórios; ele é usado pelo .deb, pelo RPM (`packaging/rpm/`), pelo pacote Arch (`packaging/aur/`) e pelo Flatpak (`packaging/flathub/`). A cada release publicada, o GitHub compila o RPM, o pacote Arch e o Flatpak, e atualiza o repositório APT assinado. A versão é lida em `rog_flare2_core.py` (`VERSION`). Testes: `python -m pytest tests`.

<a id="credits"></a>

## Créditos

- **NicRoss512** — engenharia reversa do protocolo, relógio e editor originais: [ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol](https://github.com/NicRoss512/ASUS-ROG-Strix-Flare-II-Animate-AniMe-Matrix-Protocol). Este repositório parte dele; seu histórico é preservado.
- **Mike Opitz** — [PolyWollyWin](https://github.com/MikeOpitz99/PolyWollyWin) (MIT), controlador Windows cujo motor de efeitos e visualizadores de áudio é reaproveitado aqui.
- **Yoshi Walsh** — [Mastering the AniMe Matrix](https://blog.yoshiwalsh.me/asus-anime-matrix/), pelo comportamento dos LEDs (halo, níveis percebidos, ritmo).
- **asus-linux** — [asusctl](https://gitlab.com/asus-linux/asusctl), usado para as telas dos notebooks.

Projeto independente, não afiliado à ASUS. « ROG », « AniMe Matrix » e « Armoury Crate » são marcas da ASUSTeK.

<a id="licence"></a>

## Licença

[MIT](../../LICENSE) para o código deste repositório; as animações de `bibliotheque/` são sob CC0. `polywollywin/` permanece sob a licença MIT de seu autor ([../../polywollywin/LICENSE](../../polywollywin/LICENSE)). Os arquivos originais de NicRoss512 (`rog_flare2_clock_v3.py`, `rog_flare2_matrix_paint.py`, `parse_usbpcap.py`, `rog_flare2_replay_capture.py`, `../PROTOCOL.md`, capturas) foram publicados sem licença explícita e permanecem de seu autor; são redistribuídos com atribuição.

<a id="soutien"></a>

## Apoiar o projeto

Se este projeto for útil para você, um café ajuda a mantê-lo:

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Pague-me%20um%20café&emoji=☕&slug=anticitoyen&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/anticitoyen)

**https://buymeacoffee.com/anticitoyen** — o link também está na aba *Configurações* do lançador.

Relatos de bugs, ideias e animações para compartilhar: [Issues](https://github.com/AntiCitoyen/Anticitoyen-ROG-flare2-anime-matrix/issues). Traduções: [../TRADUIRE.md](../TRADUIRE.md).
