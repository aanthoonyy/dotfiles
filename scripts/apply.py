from datetime import datetime
from pathlib import Path
import shutil

missing = [name for name in ('kitty', 'rofi', 'picom', 'feh') if shutil.which(name) is None]
if missing:
    raise SystemExit('Install required packages first: sudo dnf install ' + ' '.join(missing))

root = Path(__file__).resolve().parents[1]
home = Path.home()
backup = home / '.local/state/rice/backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
files = {home / '.config' / source.relative_to(root / 'config'): source for source in (root / 'config').rglob('*') if source.is_file()}
files[home / '.local/share/rice/wallpaper.png'] = root / 'assets/wallpaper.png'
files[home / '.local/share/rice/status.py'] = root / 'scripts/status.py'
for target, source in files.items():
    if target.exists() and target.read_bytes() == source.read_bytes():
        continue
    if target.exists() or target.is_symlink():
        saved = backup / target.relative_to(home)
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    print(target)
print(f'Backup location: {backup}')
