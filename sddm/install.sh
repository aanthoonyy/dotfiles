#!/usr/bin/env bash
set -euo pipefail

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
theme_dir=/usr/share/sddm/themes/rice
config_file=/etc/sddm.conf.d/90-rice.conf

if (( EUID != 0 )); then
  printf 'Run with: sudo bash %q\n' "$0" >&2
  exit 1
fi

if [[ -f "$config_file" ]]; then
  backup_dir="/var/lib/sddm/theme-backups/$(date +%Y%m%d-%H%M%S)"
  install -d -m 700 "$backup_dir"
  cp -a "$config_file" "$backup_dir/"
fi

install -d -m 755 "$theme_dir" /etc/sddm.conf.d
install -m 644 "$source_dir/theme/Main.qml" "$source_dir/theme/metadata.desktop" "$theme_dir/"
install -m 644 "$source_dir/theme/background.png" "$theme_dir/background.png"
printf '[Theme]\nCurrent=rice\n' > "$config_file"
chmod 644 "$config_file"
if command -v restorecon >/dev/null 2>&1; then
  restorecon -RF "$theme_dir" "$config_file"
fi
printf 'Theme installed. It will appear at your next login.\n'
