# Rice

A quiet charcoal and sage desktop for i3, with Kitty, Rofi, soft corners, and a contour wallpaper. The repository is the source; live configs are copied into your home directory. The theme is installed and has been visually checked in the active X11 session. Changes remain uncommitted until you approve the appearance.

## Install and apply

```sh
sudo dnf install kitty rofi picom feh xrandr
python3 scripts/apply.py
i3 -C -c ~/.config/i3/config
i3-msg reload
feh --no-fehbg --bg-fill ~/.local/share/rice/wallpaper.png
pgrep -x picom >/dev/null || picom --config ~/.config/picom/picom.conf --daemon
```

Existing files are backed up under `~/.local/state/rice/backups/` before replacement. The apply script prints the specific backup directory. To undo, copy its saved files back to the matching paths under your home directory and reload i3. Files that did not exist before installation have no backup; remove those individually if reverting the entire theme.

Super+Enter opens Kitty. Super+D opens the launcher. Existing i3 movement, workspace, and resize bindings are preserved. New Kitty windows pick up the terminal theme. Super+Shift+C reloads i3.

The compositor uses XRender initially; driver tuning and high-refresh compositor tuning are deferred. GTK settings request Adwaita dark; applications with their own theme controls may need separate configuration.

## Commit checkpoint

After reviewing the actual desktop, terminal, and launcher:

```sh
git add .
git diff --cached
git commit -m "Add charcoal and sage i3 rice"
```

## Wallpaper

`assets/wallpaper.png` is generated locally with Cairo. Run `python3 scripts/wallpaper.py` to regenerate it. No downloaded assets or additional fonts are required; Source Code Pro is already installed on this machine.
