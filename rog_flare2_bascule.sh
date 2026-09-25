#!/bin/bash
# Bascule l'écran AniMe Matrix du ROG Strix Flare II Animate (via le démon animematrixd).
# Le mode choisi est aussi celui du démarrage de session.
#
#   rog_flare2_bascule.sh            affiché -> éteint ; éteint -> dernière lecture
#   rog_flare2_bascule.sh gif        galerie GIF (dossier choisi dans le lanceur)
#   rog_flare2_bascule.sh horloge    horloge
#   rog_flare2_bascule.sh lecture    dernière lecture du lanceur
#   rog_flare2_bascule.sh off        éteint, rien au démarrage
#   rog_flare2_bascule.sh etat       affiche l'état du démon

DEPOT="$(dirname "$(readlink -f "$0")")"
PY="$DEPOT/.venv/bin/python"; [ -x "$PY" ] || PY=/usr/bin/python3
CTL=("$PY" "$DEPOT/rog_flare2_ctl.py")
DEMARRAGE="${XDG_CONFIG_HOME:-$HOME/.config}/rog-flare2/demarrage"
t() { "$PY" "$DEPOT/rog_flare2_i18n.py" "$1" 2>/dev/null || echo "$1"; }  # texte traduit

avertir() { notify-send "AniMe Matrix" "$1" -i animematrix 2>/dev/null; echo "$1"; }
demarrage() { mkdir -p "$(dirname "$DEMARRAGE")" && echo "$1" > "$DEMARRAGE"; }
affiche() { "${CTL[@]}" etat 2>/dev/null | grep -q '"show": {'; }  # le démon affiche quelque chose

case "${1:-}" in
    gif)     "${CTL[@]}" gif && demarrage gif && avertir "$(t "Galerie GIF")" ;;
    horloge) "${CTL[@]}" horloge && demarrage horloge && avertir "$(t "Horloge")" ;;
    lecture) "${CTL[@]}" derniere && demarrage derniere && avertir "$(t "Dernière lecture")" ;;
    off)     "${CTL[@]}" stop && demarrage rien && avertir "$(t "Écran éteint")" ;;
    etat)    "${CTL[@]}" etat ;;
    "")
        if affiche; then
            "${CTL[@]}" stop && avertir "$(t "Écran éteint")"
        else
            "${CTL[@]}" derniere && avertir "$(t "Dernière lecture")"
        fi ;;
    *) sed -n '5,10p' "$0" | sed 's/^# *//'; exit 2 ;;
esac
