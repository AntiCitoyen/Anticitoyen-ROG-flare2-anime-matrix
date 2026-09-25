#!/bin/bash
# Construit dist/anticitoyen-rog-flare2-anime-matrix_<version>_all.deb
# Usage : packaging/build-deb.sh
set -euo pipefail
umask 022

DEPOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG=anticitoyen-rog-flare2-anime-matrix
VERSION="$(sed -n 's/^VERSION = "\([^"]*\)".*/\1/p' "$DEPOT/rog_flare2_core.py")"
ROOT="$DEPOT/build/$PKG"

rm -rf "$ROOT"
"$DEPOT/packaging/install.sh" "$ROOT" /usr /usr/bin/python3
rm -f "$ROOT/usr/share/doc/$PKG/LICENSE"  # la licence est dans copyright (Debian)
install -m 644 "$DEPOT/packaging/copyright" "$ROOT/usr/share/doc/$PKG/copyright"
sed "s/@VERSION@/$VERSION/; s/@DATE@/$(date -R)/" "$DEPOT/packaging/changelog" | gzip -9n \
    > "$ROOT/usr/share/doc/$PKG/changelog.gz"

install -d "$ROOT/DEBIAN"
sed "s/@VERSION@/$VERSION/; s/@SIZE@/$(du -sk --exclude=DEBIAN "$ROOT" | cut -f1)/" \
    "$DEPOT/packaging/control" > "$ROOT/DEBIAN/control"
install -m 755 "$DEPOT/packaging/postinst" "$DEPOT/packaging/postrm" "$ROOT/DEBIAN/"

mkdir -p "$DEPOT/dist"
dpkg-deb --root-owner-group -Zxz --build "$ROOT" "$DEPOT/dist/${PKG}_${VERSION}_all.deb"
