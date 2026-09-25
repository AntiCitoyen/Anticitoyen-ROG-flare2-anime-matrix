#!/bin/bash
# Installe AniMe Matrix dans une arborescence : commun au .deb, au RPM, au paquet Arch et au Flatpak.
# Usage : packaging/install.sh DESTDIR [PREFIX=/usr] [PYTHON=/usr/bin/python3]
set -euo pipefail
umask 022

DEPOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$1"
PREFIX="${2:-/usr}"
PYTHON="${3:-/usr/bin/python3}"
PKG=anticitoyen-rog-flare2-anime-matrix
SHARE="$PREFIX/share/$PKG"

install -d "$DEST$PREFIX/bin" "$DEST$SHARE/polywollywin" "$DEST$SHARE/locale" "$DEST$SHARE/examples/effets" \
    "$DEST$PREFIX/lib/systemd/user" "$DEST$PREFIX/lib/udev/rules.d" "$DEST$PREFIX/share/applications" \
    "$DEST$PREFIX/share/icons/hicolor/scalable/apps" "$DEST$PREFIX/share/doc/$PKG"

install -m 644 "$DEPOT"/rog_flare2_*.py "$DEST$SHARE/"   # tous les modules du projet
install -m 755 "$DEPOT/rog_flare2_bascule.sh" "$DEST$SHARE/"
install -m 644 "$DEPOT"/locale/[a-z]*.json "$DEST$SHARE/locale/"
install -m 644 "$DEPOT"/examples/effets/*.py "$DEST$SHARE/examples/effets/"
install -m 644 "$DEPOT"/polywollywin/{effects.py,renderer.py,LICENSE,ORIGINE.md} "$DEST$SHARE/polywollywin/"

commande() {  # commande <nom> <script> [python]
    printf '#!/bin/sh\nexec %s %s/%s "$@"\n' "${3:-$PYTHON}" "$SHARE" "$2" > "$DEST$PREFIX/bin/$1"
    chmod 755 "$DEST$PREFIX/bin/$1"
}
commande animematrix           rog_flare2_launcher.py
commande animematrix-effet     rog_flare2_effets.py
commande animematrix-galerie   rog_flare2_folder_player.py
commande animematrix-horloge   rog_flare2_clock_v3.py
commande animematrix-convertir rog_flare2_convertir.py
commande animematrix-dessin    rog_flare2_matrix_paint.py
commande animematrixd          rog_flare2_demon.py
commande animematrix-ctl       rog_flare2_ctl.py
commande animematrix-apercu    rog_flare2_simulateur.py
commande animematrix-animation rog_flare2_animation.py
commande animematrix-tray      rog_flare2_tray.py
ln -sf "../share/$PKG/rog_flare2_bascule.sh" "$DEST$PREFIX/bin/animematrix-bascule"

sed "s|^ExecStart=/usr/bin/|ExecStart=$PREFIX/bin/|" "$DEPOT/systemd/animematrixd.service" \
    > "$DEST$PREFIX/lib/systemd/user/animematrixd.service"
chmod 644 "$DEST$PREFIX/lib/systemd/user/animematrixd.service"
install -m 644 "$DEPOT/packaging/72-rog-flare2-animate.rules" "$DEST$PREFIX/lib/udev/rules.d/"
install -D -m 644 "$DEPOT/packaging/shell/animematrix-fin.sh" "$DEST$SHARE/shell/animematrix-fin.sh"
install -D -m 644 "$DEPOT/packaging/73-rog-flare2-animate-touches.rules" "$DEST$SHARE/udev/73-rog-flare2-animate-touches.rules"  # optionnel (Wayland)
"$PYTHON" "$DEPOT/packaging/gen-desktop.py"
install -m 644 "$DEPOT/packaging/animematrix.desktop" "$DEST$PREFIX/share/applications/"
install -m 644 "$DEPOT/packaging/animematrix.svg" "$DEST$PREFIX/share/icons/hicolor/scalable/apps/"
install -m 644 "$DEPOT/README.md" "$DEPOT/LICENSE" "$DEPOT/docs/GUIDE-GIF.md" "$DEPOT/docs/PROTOCOL.md" \
    "$DEPOT/docs/EXTENSIONS.md" "$DEST$PREFIX/share/doc/$PKG/"
