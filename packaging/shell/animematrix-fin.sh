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
    mot=${__amx_cmd%% *}
    case " $ANIMEMATRIX_FIN_IGNORE " in *" $mot "*) return 0 ;; esac
    command -v animematrix-ctl >/dev/null 2>&1 || return 0
    (animematrix-ctl fin "$code" "$duree" "$__amx_cmd" >/dev/null 2>&1 &)
}

if [ -n "$ZSH_VERSION" ]; then
    autoload -Uz add-zsh-hook
    __amx_preexec() { __amx_debut "$1"; }
    __amx_precmd() { __amx_fin $?; }
    add-zsh-hook preexec __amx_preexec
    add-zsh-hook precmd __amx_precmd
    __amx_pret=1
elif [ -n "$BASH_VERSION" ]; then
    # DEBUG : avant chaque commande ; seule la première après l'invite compte (__amx_pret).
    trap '__amx_debut "$BASH_COMMAND"' DEBUG
    if [[ "$(declare -p PROMPT_COMMAND 2>/dev/null)" == "declare -a"* ]]; then
        PROMPT_COMMAND=('__amx_code=$?' "${PROMPT_COMMAND[@]}" '__amx_fin $__amx_code')
    else
        PROMPT_COMMAND="__amx_code=\$?;${PROMPT_COMMAND:+$PROMPT_COMMAND;}__amx_fin \$__amx_code"
    fi
    __amx_pret=1
fi
