#!/bin/bash
# Construit dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
# Usage : packaging/build-deb.sh
set -euo pipefail
umask 022

DEPOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG=anticitoyen-rog-flare2-anime-matrix
VERSION="$(sed -n 's/^VERSION = "\([^"]*\)".*/\1/p' "$DEPOT/rog_flare2_core.py")"
SHARE=/usr/share/$PKG
ROOT="$DEPOT/build/$PKG"

rm -rf "$ROOT"
install -d "$ROOT/DEBIAN" "$ROOT/usr/bin" "$ROOT$SHARE/polywollywin" "$ROOT/usr/lib/systemd/user" \
    "$ROOT/usr/lib/udev/rules.d" "$ROOT/usr/share/applications" \
    "$ROOT/usr/share/icons/hicolor/scalable/apps" "$ROOT/usr/share/doc/$PKG"

for f in rog_flare2_launcher.py rog_flare2_matrix_paint.py rog_flare2_clock_v3.py rog_flare2_convertir.py \
         rog_flare2_folder_player.py rog_flare2_effets.py rog_flare2_i18n.py rog_flare2_themes.py \
         rog_flare2_ui_ronde.py rog_flare2_maj.py rog_flare2_core.py rog_flare2_demon.py rog_flare2_ctl.py \
         rog_flare2_infos.py; do
    install -m 644 "$DEPOT/$f" "$ROOT$SHARE/$f"
done
install -m 755 "$DEPOT/rog_flare2_bascule.sh" "$ROOT$SHARE/rog_flare2_bascule.sh"
install -d "$ROOT$SHARE/locale"
install -d "$ROOT$SHARE/examples/effets"
install -m 644 "$DEPOT"/examples/effets/*.py "$ROOT$SHARE/examples/effets/"
install -m 644 "$DEPOT"/locale/[a-z]*.json "$ROOT$SHARE/locale/"
install -m 644 "$DEPOT"/polywollywin/{effects.py,renderer.py,LICENSE,ORIGINE.md} "$ROOT$SHARE/polywollywin/"

commande() {  # commande <nom> <script>
    printf '#!/bin/sh\nexec /usr/bin/python3 %s/%s "$@"\n' "$SHARE" "$2" > "$ROOT/usr/bin/$1"
    chmod 755 "$ROOT/usr/bin/$1"
}
commande animematrix           rog_flare2_launcher.py
commande animematrix-effet     rog_flare2_effets.py
commande animematrix-galerie   rog_flare2_folder_player.py
commande animematrix-horloge   rog_flare2_clock_v3.py
commande animematrix-convertir rog_flare2_convertir.py
commande animematrix-dessin    rog_flare2_matrix_paint.py
commande animematrixd          rog_flare2_demon.py
commande animematrix-ctl       rog_flare2_ctl.py
ln -s "../share/$PKG/rog_flare2_bascule.sh" "$ROOT/usr/bin/animematrix-bascule"

install -m 644 "$DEPOT"/systemd/*.service "$ROOT/usr/lib/systemd/user/"
install -m 644 "$DEPOT/packaging/72-rog-flare2-animate.rules" "$ROOT/usr/lib/udev/rules.d/"
/usr/bin/python3 "$DEPOT/packaging/gen-desktop.py"
install -m 644 "$DEPOT/packaging/animematrix.desktop" "$ROOT/usr/share/applications/"
install -m 644 "$DEPOT/packaging/animematrix.svg" "$ROOT/usr/share/icons/hicolor/scalable/apps/"
install -m 644 "$DEPOT/packaging/copyright" "$ROOT/usr/share/doc/$PKG/copyright"
install -m 644 "$DEPOT/README.md" "$DEPOT/docs/GUIDE-GIF.md" "$DEPOT/docs/PROTOCOL.md" "$DEPOT/docs/EXTENSIONS.md" "$ROOT/usr/share/doc/$PKG/"
sed "s/@VERSION@/$VERSION/; s/@DATE@/$(date -R)/" "$DEPOT/packaging/changelog" | gzip -9n \
    > "$ROOT/usr/share/doc/$PKG/changelog.gz"

sed "s/@VERSION@/$VERSION/; s/@SIZE@/$(du -sk --exclude=DEBIAN "$ROOT" | cut -f1)/" \
    "$DEPOT/packaging/control" > "$ROOT/DEBIAN/control"
install -m 755 "$DEPOT/packaging/postinst" "$DEPOT/packaging/postrm" "$DEPOT/packaging/prerm" "$ROOT/DEBIAN/"

mkdir -p "$DEPOT/dist"
dpkg-deb --root-owner-group -Zxz --build "$ROOT" "$DEPOT/dist/${PKG}_${VERSION}_all.deb"
