import shlex
from pathlib import Path


def on_cmd_startstop(boss, window, data):
    try:
        command = shlex.split(data.get('cmdline', ''))
    except ValueError:
        return
    if not command or Path(command[0]).name != 'nvim':
        return
    padding = 0 if data['is_start'] else None
    for edge in ('left', 'right', 'top', 'bottom'):
        window.patch_edge_width('padding', edge, padding)
    tab = window.tabref()
    if tab is not None:
        tab.relayout()
