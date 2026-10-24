# Rice

The Git repository lives directly in `~/.config`. These are the active configurations; edit them in place. The root `.gitignore` allows only the specific rice files, leaving other application settings untracked.

Install dependencies with `sudo dnf install kitty rofi picom feh xrandr`.

After editing i3, validate and reload:

```sh
i3 -C -c ~/.config/i3/config
i3-msg reload
```

Super+Enter opens Kitty; Super+D opens Rofi. Open new Kitty windows to pick up terminal changes. Restart Picom after changing its configuration.

The wallpaper and bar script live in `~/.config/rice/`. Regenerate the wallpaper with `python3 ~/.config/rice/wallpaper.py`, then apply it with `feh --no-fehbg --bg-fill ~/.config/rice/wallpaper.png`.

Original configuration backups remain under `~/.local/state/rice/backups/`. Display findings and the temporary 240 Hz trial are in `display.md`.

Review and commit from the configuration directory:

```sh
cd ~/.config
git add .
git diff --cached
git commit -m "Manage active rice files directly in .config"
```
