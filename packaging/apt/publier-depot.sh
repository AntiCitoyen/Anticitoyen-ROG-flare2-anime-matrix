#!/bin/bash
# Ajoute un .deb au dépôt APT (dossier de la branche gh-pages) et régénère les index.
# Usage : packaging/apt/publier-depot.sh DOSSIER_DEPOT paquet.deb [ID_CLE_GPG]
# Sans clé : dépôt non signé (à éviter). Avec clé : Release.gpg, InRelease et animematrix.gpg.
set -euo pipefail
REPO="$1"; DEB="$2"; KEY="${3:-}"
DIST=stable; COMP=main
mkdir -p "$REPO/pool/$COMP" "$REPO/dists/$DIST/$COMP/binary-all"
cp "$DEB" "$REPO/pool/$COMP/"
cd "$REPO"
dpkg-scanpackages --multiversion pool/ > "dists/$DIST/$COMP/binary-all/Packages"
gzip -9nkf "dists/$DIST/$COMP/binary-all/Packages"
{
    echo "Origin: AntiCitoyen"
    echo "Label: AniMe Matrix"
    echo "Suite: $DIST"
    echo "Codename: $DIST"
    echo "Architectures: all amd64 arm64 i386"
    echo "Components: $COMP"
    echo "Description: AniMe Matrix for Linux (ROG Strix Flare II Animate)"
    echo "Date: $(LC_ALL=C date -Ru)"
    for algo in MD5Sum:md5sum SHA256:sha256sum; do
        echo "${algo%%:*}:"
        for f in "$COMP/binary-all/Packages" "$COMP/binary-all/Packages.gz"; do
            printf ' %s %s %s\n' "$(${algo#*:} "dists/$DIST/$f" | cut -d' ' -f1)" "$(stat -c%s "dists/$DIST/$f")" "$f"
        done
    done
} > "dists/$DIST/Release"
if [ -n "$KEY" ]; then
    gpg --batch --yes --default-key "$KEY" -abs -o "dists/$DIST/Release.gpg" "dists/$DIST/Release"
    gpg --batch --yes --default-key "$KEY" --clearsign -o "dists/$DIST/InRelease" "dists/$DIST/Release"
    gpg --batch --yes --export "$KEY" > animematrix.gpg
fi
echo "dépôt à jour : $(grep -c '^Package:' "dists/$DIST/$COMP/binary-all/Packages") version(s)"
