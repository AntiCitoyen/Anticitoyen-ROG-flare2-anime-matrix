#!/bin/bash
# Bascule l'écran AniMe Matrix du ROG Strix Flare II Animate entre galerie GIF,
# horloge et extinction. Le mode choisi est aussi celui du démarrage de session.
#
#   rog_flare2_bascule.sh            actif -> éteint ; éteint -> dernier mode
#   rog_flare2_bascule.sh gif        galerie GIF (animematrix-galerie.service)
#   rog_flare2_bascule.sh horloge    horloge (animematrix-horloge.service)
#   rog_flare2_bascule.sh off        éteint, rien au démarrage
#   rog_flare2_bascule.sh etat       affiche le mode courant

DEPOT="$(dirname "$(readlink -f "$0")")"
PY="$DEPOT/.venv/bin/python"; [ -x "$PY" ] || PY=/usr/bin/python3
ETAT="${XDG_CONFIG_HOME:-$HOME/.config}/rog-flare2/mode"
declare -A SERVICE=([gif]=animematrix-galerie.service [horloge]=animematrix-horloge.service)
declare -A NOM=([gif]="Galerie GIF" [horloge]="Horloge" [off]="Écran éteint")

mode_actif() {
    for m in gif horloge; do
        systemctl --user is-active --quiet "${SERVICE[$m]}" && { echo "$m"; return; }
    done
    echo off
}

avertir() { notify-send "AniMe Matrix" "$1" -i input-keyboard 2>/dev/null; echo "$1"; }

eteindre() {
    systemctl --user disable --now "${SERVICE[gif]}" "${SERVICE[horloge]}" 2>/dev/null
    "$PY" "$DEPOT/rog_flare2_clock_v3.py" --clear >/dev/null 2>&1
}

passer_a() {
    local m=$1
    eteindre
    if [ "$m" != off ]; then
        systemctl --user enable --now "${SERVICE[$m]}" || { avertir "Échec : ${NOM[$m]}"; exit 1; }
        mkdir -p "$(dirname "$ETAT")" && echo "$m" > "$ETAT"
    fi
    avertir "${NOM[$m]}"
}

case "${1:-}" in
    gif|horloge|off) passer_a "$1" ;;
    etat) echo "$(mode_actif) (dernier mode : $(cat "$ETAT" 2>/dev/null || echo gif))" ;;
    "")
        if [ "$(mode_actif)" != off ]; then
            passer_a off
        else
            passer_a "$(cat "$ETAT" 2>/dev/null || echo gif)"
        fi ;;
    *) sed -n '5,9p' "$0" | sed 's/^# *//'; exit 2 ;;
esac
