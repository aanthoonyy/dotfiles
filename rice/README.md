# Rice

Apple-inspired light surfaces, near-white highlights, dark text, and restrained blue accents, gapless tiling, square corners, and a compact bottom bar.

The Git repository lives directly in `~/.config`. These are the active configurations; edit them in place. The root `.gitignore` includes selected personal configurations alongside the rice, leaving application databases, caches, and account data untracked.

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

The bottom-right controls open Sound, Network, and Calendar popovers. Click outside or press Escape to close. Scroll over the speaker to adjust volume. The popovers use the system Python GTK 3 bindings.

The clock uses month-day-year and 12-hour time. Speaker and connection icons use the installed Symbols Nerd Font Mono. Sound output buttons set the default device and move existing playback streams. Horizontal i3bar padding stays at zero so its click regions align with the controls.

Sound uses a compact volume view. Click the current output row to open the device list; a blue check marks the active output. Selecting a device returns to the volume view.

The icon buttons use compact 26-pixel targets. Control Center popovers use short Picom fade/scale animations, with brief hover transitions on buttons. Picom 13 or newer supports the animation rules used here.

Sound pages slide over 220 ms and resize while staying anchored above the bar. Device selection shows a spinner, confirms the selected output, then slides back to volume without closing the popover.

Device-page transitions render the actual moving content through a horizontal pixel blur, strongest during fast movement and fading to crisp content at rest. This uses the installed Pillow and Cairo Python libraries.

## Drag-and-snap window controls

New windows stay in automatic horizontal layout: one fills the workspace, two split it. Drag a title bar onto another window to snap into the layout. The drag preview shows the complete proposed arrangement with app titles. Blue identifies the dragged window; gray outlines show where the other windows will land. The only choices are left, right, top, and bottom; there are no center or outer-parent drop zones. Super+left-drag also rearranges tiled windows from anywhere inside them. Drag a divider to resize the split. Freely floating windows remain available through Super+Shift+Space; Super+T returns them to automatic layout.

Right-click an i3 title bar or press Alt+Space for Minimize, Maximize/Restore, Return to automatic layout, and Close. Alt+F4 closes the focused app. Super+Up maximizes/restores while keeping the bar visible; Super+Down minimizes; Super+Shift+Down restores the last minimized window. Super+T returns a floating window to automatic layout.

Alt+Tab toggles recent apps. Alt+Shift+Tab or the overlapping-windows button beside the status controls opens a searchable window list, including minimized apps. Click an entry or press Enter to activate it. Escape cancels.

These are i3 title bars with a window menu. Native minimize/maximize/close buttons require a different window manager. Window geometry and minimized state are kept outside Git in `~/.local/state/rice/windows.json`; focus history is per session. Original settings before this change are in `~/.local/state/rice/backups/`.

Normal windows have short open/close fades and 160 ms movement/resize transitions. Drag-preview regions interpolate over 120 ms. The layout preview accounts for the space freed by the dragged window.

Window and workspace switching is instant: normal-window show/hide fades are disabled. Opening, closing, and layout changes retain their short animations.
