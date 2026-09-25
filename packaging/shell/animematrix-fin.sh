# animematrix-fin — affiche la fin d'une commande longue sur l'écran AniMe Matrix.
# À charger depuis ~/.bashrc ou ~/.zshrc (le lanceur peut l'ajouter : Réglages) :
#     . /usr/share/anticitoyen-rog-flare2-anime-matrix/shell/animematrix-fin.sh
# Réglages : ANIMEMATRIX_FIN_SECONDES (défaut 30) ; ANIMEMATRIX_FIN_IGNORE (commandes interactives ignorées).
[ -n "$__amx_charge" ] && return 0
__amx_charge=1
: "${ANIMEMATRIX_FIN_SECONDES:=30}"
: "${ANIMEMATRIX_FIN_IGNORE:=vim nvim vi nano emacs less more man ssh top htop btop watch tail python python3 ipython bash zsh fish sudo su tmux screen}"

__amx_debut() {  # $1 : ligne de commande
    [ -n "$__amx_pret" ] || return 0
    __amx_pret=
    __amx_cmd=$1
    __amx_t=$SECONDS
}

__amx_fin() {  # $1 : code de sortie de la commande
    local code=$1 duree mot
    __amx_pret=1
    [ -n "$__amx_t" ] || return 0
    duree=$((SECONDS - __amx_t))
    __amx_t=
    [ "$duree" -ge "$ANIMEMATRIX_FIN_SECONDES" ] || return 0
    mot=$__amx_cmd
    while :; do  # « JETON=… commande » : les affectations ne partent pas
        case ${mot%% *} in
            *=*) [ "$mot" != "${mot#* }" ] || return 0; mot=${mot#* } ;;
            *) break ;;
        esac
    done
    mot=${mot%% *}
    case " $ANIMEMATRIX_FIN_IGNORE " in *" $mot "*) return 0 ;; esac
    command -v animematrix-ctl >/dev/null 2>&1 || return 0
    # seul le nom du programme part : le reste de la ligne peut contenir un mot de passe ou un jeton
    (animematrix-ctl fin "$code" "$duree" "$mot" >/dev/null 2>&1 &)
}

if [ -n "$ZSH_VERSION" ]; then
    autoload -Uz add-zsh-hook
    __amx_preexec() { __amx_debut "$1"; }
    __amx_precmd() { __amx_fin $?; }
    add-zsh-hook preexec __amx_preexec
    add-zsh-hook precmd __amx_precmd
    __amx_pret=1
elif [ -n "$BASH_VERSION" ] && declare -p preexec_functions >/dev/null 2>&1; then
    # bash-preexec (atuin, starship…) tient déjà le piège DEBUG : on s'y inscrit.
    __amx_bp_pre() { __amx_debut "$1"; }
    __amx_bp_post() { __amx_fin "$__bp_last_ret_value"; }
    preexec_functions+=(__amx_bp_pre)
    precmd_functions+=(__amx_bp_post)
    __amx_pret=1
elif [ -n "$BASH_VERSION" ]; then
    # DEBUG : avant chaque commande ; seule la première après l'invite compte (__amx_pret).
    # __amx_fin reste la dernière commande de l'invite (après elle, __amx_pret compte la suivante).
    # Posé à la première invite, au niveau du shell (ni ici ni dans une fonction : à la fin d'un
    # « . fichier » ou d'une fonction, bash rétablit le piège DEBUG d'avant et effacerait le nôtre).
    # Un piège DEBUG existant est gardé et appelé après le nôtre ; trap -p passe par un fichier.
    __amx_lit() {  # $1 : fichier contenant « trap -- '…' DEBUG »
        local texte
        texte=$(<"$1")
        rm -f -- "$1"
        __amx_capture() { __amx_debug_avant=$3; }
        eval "__amx_capture $texte"
        unset -f __amx_capture
    }
    __amx_piege='__amx_debut "$BASH_COMMAND"; [ -z "$__amx_debug_avant" ] || eval "$__amx_debug_avant"'
    __amx_pose='[ -n "$__amx_pose_fait" ] || { __amx_pose_fait=1; __amx_f=$(mktemp) && trap -p DEBUG > "$__amx_f" && __amx_lit "$__amx_f"; trap "$__amx_piege" DEBUG; }'
    if [[ "$(declare -p PROMPT_COMMAND 2>/dev/null)" == "declare -a"* ]]; then
        PROMPT_COMMAND=('__amx_code=$?' "${PROMPT_COMMAND[@]}" "$__amx_pose" '__amx_fin $__amx_code')
    else
        PROMPT_COMMAND="__amx_code=\$?;${PROMPT_COMMAND:+$PROMPT_COMMAND;}$__amx_pose;__amx_fin \$__amx_code"
    fi
    __amx_pret=1
fi
