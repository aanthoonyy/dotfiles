import datetime
import json
import subprocess
import time

print(json.dumps({"version": 1}), flush=True)
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
    for block in blocks:
        block.update(separator=False, separator_block_width=28)
    print(json.dumps(blocks) + ",", flush=True)
    time.sleep(5)
