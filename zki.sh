function parse_git_branch() {
  [ -e ./.git/HEAD ] && printf "[ * \033[1;32m%s\033[0m ]\n" "$(awk -F/ '{print $NF}' ./.git/HEAD)"
}
source <(kubectl completion bash)
export GREP_COLORS='ms=1;91'
export EDITOR=vim
export KUBE_EDITOR=vim
export KI_AI_KEY=""
export KI_AI_URL="https://api.openai.com/v1/chat/completions"
export KI_AI_MODEL="gpt-4o"
export KI_LINE=$([ -e ~/.history/.line ] && cat ~/.history/.line || echo 200)
export PS1="\e[1;37m[\e[m\e[1;32m\u\e[m\e[1;32m@\e[m\e[1;35m\H\e[m \e[1;33m\A\e[m \w\e[m\e[1;37m]\e[m\e[1;36m\e[m \$(/usr/local/bin/ki --w) \$(parse_git_branch) \n\\$ "
alias kubectl="kubectl --insecure-skip-tls-verify "
alias vi=vim
alias ls='ls --color'
alias ll='ls -l'
alias kn='cd ~/.kube;for file in $(find . -name "kubeconfig-*-NULL"); do mv "$file" "${file%-NULL}"; done'
[ $USER = root ] && STYLE="\033c\033[5;32m%s\033[1;m\n" || STYLE="\033[5;32m%s\033[1;m\n"
[[ $- == *i* ]] && [ -e ~/.kube/config ] && printf $STYLE "$(/usr/local/bin/ki --w)"
