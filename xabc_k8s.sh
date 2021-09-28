export EDITOR=vim
export KUBE_EDITOR=vim
alias vi=vim
alias ls='ls --color'
alias ll='ls -l'
export PS1="\e[1;37m[\e[m\e[1;36m\u\e[m\e[1;36m@\e[m\e[1;36m\H\e[m \e[1;33m\A\e[m \w\e[m\e[1;37m]\e[m\e[1;36m\e[m\n\\$ "
[[ $- == *i* ]]&&printf "\033c\033[5;32;40m%s\033[1;m\n" "[ $(ls -l ~/.kube/config|awk -F'/' '{print $NF}') ]"
