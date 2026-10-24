# Zsh

Recreate the config link and install the two plugins:

```bash
ln -s ~/.config/zsh/.zshrc ~/.zshrc
mkdir -p ~/.local/share/zsh/plugins
git clone --depth 1 https://github.com/zsh-users/zsh-autosuggestions.git ~/.local/share/zsh/plugins/zsh-autosuggestions
git clone --depth 1 https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.local/share/zsh/plugins/zsh-syntax-highlighting
```

Run `exec zsh` to reload. Right arrow accepts a history suggestion when the cursor is at the end of the line.
