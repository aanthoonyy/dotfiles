# Dotfiles

Personal configuration for Anthony's Fedora desktop. This repository lives directly in `~/.config`; tracked files are the live configs, with no separate copy or apply step.

## Included

| Configuration | Location |
| --- | --- |
| i3, Kitty, Rofi, Picom | `i3/`, `kitty/`, `rofi/`, `picom/` |
| Flameshot screenshot settings | `flameshot/` |
| Control center, window controls, wallpaper | `rice/` |
| Neovim settings, plugins, and lockfile | `nvim/` |
| VS Code settings and extension list | `Code/User/` |
| clangd project settings | `clangd/` |
| GTK preferences and bookmarks | `gtk-3.0/`, `gtk-4.0/` |
| GitHub CLI preferences | `gh/config.yml` |
| Minecraft launcher settings and theme | `rmcl/config.toml`, `rmcl/theme.toml` |
| User services and autostart | `systemd/user/`, `autostart/` |
| Display, default apps, and user folders | `monitors.xml`, `mimeapps.list`, `user-dirs.*` |

The ignore rules allow these configuration sources while excluding application data, caches, cookies, login tokens, account files, chat history, and generated files. Add new applications deliberately to `.gitignore` so their settings are included without their runtime data.

## Save changes

```sh
cd ~/.config
git add .
git diff --cached
git commit -m "Update configuration"
git push
```

Neovim is tracked as ordinary files in this repository. Its former standalone Git metadata is preserved locally under `~/.local/state/dotfiles/backups/`; the existing GitHub Neovim repository is unchanged.

## Setup notes

Desktop packages: `i3 kitty rofi picom feh xrandr`. The control center also uses Python GTK 3, Cairo, and Pillow. Status icons use Symbols Nerd Font Mono. Neovim plugins are specified in its configuration and lockfile.

Review machine-specific paths in clangd, VS Code, and systemd settings when using another machine. `monitors.xml` and the i3 display command describe this machine's monitor.

The VS Code extension list can be restored with `xargs -r -n 1 code --install-extension < Code/User/extensions.txt`.

See `rice/README.md` for desktop controls and `rice/display.md` for the 240 Hz setup.
