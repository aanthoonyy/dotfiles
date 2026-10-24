# Dev commands

Recreate the links after cloning the dotfiles into `~/.config`:

```bash
mkdir -p ~/.local/bin
ln -s ~/.config/bin/zathura-dev ~/.local/bin/zathura-dev
ln -s ~/.config/bin/handbrake-dev ~/.local/bin/handbrake-dev
```

Make sure `~/.local/bin` is in your `PATH`. Edit the scripts here; the links use these same files.

`zathura-dev` defaults to `~/Documents/zathura` and opens the Unix programming book when called without arguments. Override the checkout with `ZATHURA_REPO_DIR`.

`handbrake-dev` defaults to `~/Documents/HandBrake`. Override the checkout with `HANDBRAKE_REPO_DIR`, or the build parallelism with `HANDBRAKE_JOBS`.
