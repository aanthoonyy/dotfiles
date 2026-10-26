# Login theme

Preview without changing the login screen:

```bash
sddm-greeter-qt6 --test-mode --theme ~/.config/sddm/theme
```

Install the theme and wallpaper into the system theme directory:

```bash
sudo bash ~/.config/sddm/install.sh
```

The theme appears at the next login. The installer does not restart SDDM. Run it again after editing the theme or changing the wallpaper.

To use SDDM's default theme again:

```bash
sudo rm /etc/sddm.conf.d/90-rice.conf
```
