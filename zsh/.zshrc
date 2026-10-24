typeset -U path
path=("$HOME/.local/bin" "$HOME/bin" $path)
[[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"

HISTFILE="${XDG_STATE_HOME:-$HOME/.local/state}/zsh/history"
HISTSIZE=10000
SAVEHIST=10000
mkdir -p -- "${HISTFILE:h}"
setopt EXTENDED_HISTORY SHARE_HISTORY HIST_IGNORE_DUPS HIST_IGNORE_SPACE
setopt INTERACTIVE_COMMENTS PROMPT_SUBST

bindkey -e
bindkey '^[[A' history-beginning-search-backward
bindkey '^[[B' history-beginning-search-forward
bindkey '^[OA' history-beginning-search-backward
bindkey '^[OB' history-beginning-search-forward
bindkey '^[[3~' delete-char
bindkey '^[[H' beginning-of-line
bindkey '^[[F' end-of-line

zmodload zsh/complist
autoload -Uz compinit
mkdir -p -- "${XDG_CACHE_HOME:-$HOME/.cache}/zsh"
compinit -d "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump"
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'
zstyle ':completion:*' list-colors 'di=34' 'ln=36'

alias ll='ls -lah --group-directories-first --color=auto'

autoload -Uz vcs_info add-zsh-hook
zstyle ':vcs_info:*' enable git
zstyle ':vcs_info:git:*' check-for-changes true
zstyle ':vcs_info:git:*' unstagedstr '*'
zstyle ':vcs_info:git:*' stagedstr '+'
zstyle ':vcs_info:git:*' formats ' %F{#636366}%b%u%c%f'
zstyle ':vcs_info:git:*' actionformats ' %F{#636366}%b|%a%u%c%f'
add-zsh-hook precmd vcs_info

PROMPT='%F{#636366}%n@%m%f %F{#0066cc}%~%f${vcs_info_msg_0_} %(?.%F{#0066cc}.%F{#b83b37})❯%f '

ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#8e8e93'
ZSH_AUTOSUGGEST_STRATEGY=(history)
if [[ -r "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh" ]]; then
  source "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"
fi

if [[ -r "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]]; then
  source "${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
  ZSH_HIGHLIGHT_STYLES[command]='fg=#0066cc'
  ZSH_HIGHLIGHT_STYLES[builtin]='fg=#0066cc'
  ZSH_HIGHLIGHT_STYLES[alias]='fg=#0066cc'
  ZSH_HIGHLIGHT_STYLES[function]='fg=#0066cc'
  ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#b83b37'
  ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#31734a'
  ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#31734a'
  ZSH_HIGHLIGHT_STYLES[path]='fg=#277580'
fi
