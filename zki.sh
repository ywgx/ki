function parse_git_branch() {
    [ -e ./.git/HEAD ] && printf "[ * \033[1;32m%s\033[0m ]\n" "$(awk -F/ '{print $NF}' ./.git/HEAD)"
}

function get_ki_session_id() {
    local session_id=""
    if [ -n "$XDG_SESSION_ID" ]; then
        session_id="$XDG_SESSION_ID"
    elif [ -n "$SSH_TTY" ]; then
        session_id="${SSH_TTY##*/}"
    elif [ -n "$SSH_AUTH_SOCK" ]; then
        session_id="${SSH_AUTH_SOCK##*.}"
    elif [ -n "$TERM_SESSION_ID" ]; then
        session_id="${TERM_SESSION_ID:0:10}"
    else
        session_id="default"
    fi
    echo "$session_id" | sed 's/[^a-zA-Z0-9_-]/_/g'
}

function init_ki_session_config() {
    local session_id=$(get_ki_session_id)
    local session_config="$HOME/.kube/config-sess-${session_id}"
    local default_config="$HOME/.kube/config"

    if [ ! -e "$session_config" ]; then
        if [ -L "$default_config" ]; then
            local target=$(readlink -f "$default_config")
            if [ -e "$target" ]; then
                ln -s "$target" "$session_config"
            fi
        elif [ -f "$default_config" ]; then
            ln -s "$default_config" "$session_config"
        else
            local first_config=$(find $HOME/.kube -maxdepth 2 -type f -name 'kubeconfig*' ! -name 'kubeconfig-*-NULL' ! -name 'config-sess-*' 2>/dev/null | head -n 1)
            if [ -n "$first_config" ]; then
                ln -s "$first_config" "$session_config"
                [ ! -e "$default_config" ] && ln -s "$first_config" "$default_config"
            fi
        fi
    fi

    if [ -e "$session_config" ]; then
        export KUBECONFIG="$session_config"
    fi
}

function cleanup_ki_session() {
    local session_id=$(get_ki_session_id)
    local session_config="$HOME/.kube/config-sess-${session_id}"

    if [ -L "$session_config" ] || [ -f "$session_config" ]; then
        rm -f "$session_config"
    fi

    find "$HOME/.kube" -maxdepth 1 -type l -name 'config-sess-*' -mtime +3 -delete 2>/dev/null
}

init_ki_session_config

trap cleanup_ki_session EXIT

source <(kubectl completion bash)
export PS1="\e[1;37m[\e[m\e[1;32m\u\e[m\e[1;32m@\e[m\e[1;35m\H\e[m \e[1;33m\A\e[m \w\e[m\e[1;37m]\e[m\e[1;36m\e[m \$(ki --w) \$(parse_git_branch) \n\\$ "
export GREP_COLORS='ms=1;91'
export EDITOR=vim
export KUBE_EDITOR=vim
export KI_AI_URL="https://api.xairouter.com/v1/chat/completions"
export KI_AI_KEY="sk-XvsJhNdiXcDYA3e5hzD1AJP5ploMAaFuMTUxp3bHRfCiZRNt"
export KI_AI_MODEL="MiniMax-M2.1"
export KI_LINE=$([ -e ~/.history/.line ] && cat ~/.history/.line || echo 200)
alias vi=vim
alias ls='ls --color'
alias ll='ls -l'
alias kn='cd ~/.kube;for file in $(find . -name "kubeconfig-*-NULL"); do mv "$file" "${file%-NULL}"; done'
alias kubectl="kubectl --insecure-skip-tls-verify "
[ $USER = root ] && STYLE="\033c\033[5;32m%s\033[1;m\n" || STYLE="\033[5;32m%s\033[1;m\n"
[[ $- == *i* ]] && [ -e "$KUBECONFIG" ] && printf $STYLE "$(/usr/local/bin/ki --w)"
