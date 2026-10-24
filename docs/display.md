# Display investigation

Observed on 2026-10-23 in the active X11 session:

- GPU: NVIDIA GeForce RTX 3060 Lite Hash Rate.
- Kernel driver: Nouveau.
- Active connector: DP-2, ZOWIE XL LCD (BNQ).
- Current XRandR mode: 1920×1080 at 60.000 Hz.
- XRandR advertises 1920×1080 at 239.964 Hz, 143.981 Hz, and 120.000 Hz, among other modes.
- The saved GNOME monitor configuration already selects 1920×1080 at 239.964 Hz.

These timings were read directly from the running X server through libXrandr because the xrandr command was not installed. The 240 Hz mode is already exposed with the current driver; an NVIDIA driver change is not a prerequisite for trying it. Actual stability and smoothness still need to be checked on screen.

After installing xrandr, inspect:

```sh
xrandr --query
```

Try the advertised mode with an automatic 20-second fallback:

```sh
(sleep 20; xrandr --output DP-2 --mode 1920x1080 --rate 60) &
fallback=$!
xrandr --output DP-2 --mode 1920x1080 --rate 239.964
```

If the image is stable, cancel the fallback in the same shell before the timer expires:

```sh
kill "$fallback"
```

Verify the selected mode using `xrandr --query` (the current rate has an asterisk). Only after confirming stability should a startup command be added to i3. No refresh-rate setting has been applied or persisted yet.
