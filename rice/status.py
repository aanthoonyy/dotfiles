import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time


def command(*args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=2)
        return result.stdout.strip() if result.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''


def handle_clicks():
    for line in sys.stdin:
        try:
            event = json.loads(line.strip().lstrip(','))
            name, button = event.get('name'), event.get('button')
            if name in ('sound', 'network', 'calendar') and button == 1:
                subprocess.Popen(['python3', str(Path(__file__).with_name('controls.py')), json.dumps({'panel': name, 'x': event.get('x', 0) - event.get('relative_x', 0), 'y': event.get('y', 0) - event.get('relative_y', 0), 'height': event.get('height', 26)})], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif name == 'windows' and button == 1:
                subprocess.Popen(['python3', str(Path(__file__).with_name('windows.py')), 'switch'])
            elif name == 'sound' and button in (4, 5):
                subprocess.Popen(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+2%' if button == 4 else '-2%'])
        except (ValueError, AttributeError, OSError):
            pass


threading.Thread(target=handle_clicks, daemon=True).start()
print(json.dumps({'version': 1, 'click_events': True}), flush=True)
print('[', flush=True)
while True:
    volume = command('pactl', 'get-sink-volume', '@DEFAULT_SINK@')
    match = re.search(r'(\d+)%', volume)
    level = int(match.group(1)) if match else 0
    muted = command('pactl', 'get-sink-mute', '@DEFAULT_SINK@').endswith('yes')
    speaker = '\U000f0581' if muted or level == 0 else ('\U000f057f' if level < 50 else '\U000f057e')
    devices = command('nmcli', '-t', '-f', 'TYPE,STATE', 'device').splitlines()
    wired = 'ethernet:connected' in devices
    wireless = 'wifi:connected' in devices
    connected = wired or wireless
    network_icon = '\U000f0200' if wired else ('\U000f05a9' if wireless else '\U000f0202')
    now = datetime.datetime.now()
    blocks = [
        {'name': 'windows', 'full_text': '<span font_family="Symbols Nerd Font Mono" size="11000">\uf2d2</span>'},
        {'name': 'sound', 'full_text': f'<span font_family="Symbols Nerd Font Mono" size="11000">{speaker}</span>'},
        {'name': 'network', 'full_text': f'<span font_family="Symbols Nerd Font Mono" size="11000">{network_icon}</span>', 'color': '#3a3a3c' if connected else '#9a9aa0'},
        {'name': 'calendar', 'full_text': now.strftime('%m-%d-%Y  %I:%M %p').replace('  0', '  ')},
    ]
    for block in blocks:
        block.update(separator=False, separator_block_width=0, markup='pango', min_width=154 if block['name'] == 'calendar' else 26, align='center')
    print(json.dumps(blocks) + ',', flush=True)
    time.sleep(2)
