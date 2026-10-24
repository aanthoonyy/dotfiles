import datetime
import json
import subprocess
import sys
import threading
import time

def handle_clicks():
    for line in sys.stdin:
        try:
            event = json.loads(line.strip().lstrip(","))
            if event.get("name") == "network" and event.get("button") == 1:
                subprocess.Popen(["nm-connection-editor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (ValueError, AttributeError, OSError):
            pass


threading.Thread(target=handle_clicks, daemon=True).start()
print(json.dumps({"version": 1, "click_events": True}), flush=True)
print("[", flush=True)
while True:
    blocks = []
    try:
        volume = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], capture_output=True, text=True, timeout=2)
        muted = subprocess.run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], capture_output=True, text=True, timeout=2)
        if volume.returncode == 0 and muted.returncode == 0:
            level = next(part for part in volume.stdout.split() if part.endswith("%"))
            blocks.append({"full_text": "MUTED" if "yes" in muted.stdout else "VOL  " + level})
    except (OSError, subprocess.TimeoutExpired, StopIteration):
        pass
    now = datetime.datetime.now()
    blocks.extend([
        {"full_text": now.strftime("%a  %d %b"), "color": "#616166"},
        {"full_text": now.strftime("%H:%M"), "color": "#3a3a3c"},
    ])
    try:
        network = subprocess.run(["nmcli", "-t", "-f", "STATE", "general"], capture_output=True, text=True, timeout=2)
        connected = network.returncode == 0 and network.stdout.strip().startswith("connected")
        blocks.append({
            "name": "network",
            "full_text": '<span font_family="Noto Sans Symbols 2">🌐︎</span>' + ("" if connected else " ×"),
            "markup": "pango",
            "color": "#3a3a3c" if connected else "#9a9aa0",
        })
    except (OSError, subprocess.TimeoutExpired):
        pass
    for block in blocks:
        block.update(separator=False, separator_block_width=10)
    print(json.dumps(blocks) + ",", flush=True)
    time.sleep(5)
