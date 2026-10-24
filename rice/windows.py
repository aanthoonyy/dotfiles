import ctypes as c
import copy
import fcntl
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import time


class I3:
    def __init__(self):
        path = subprocess.check_output(['i3', '--get-socketpath'], text=True).strip()
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(path)

    def receive(self, length):
        data = b''
        while len(data) < length:
            chunk = self.socket.recv(length - len(data))
            if not chunk:
                raise RuntimeError('i3 connection closed')
            data += chunk
        return data

    def request(self, kind, payload=''):
        encoded = payload.encode()
        self.socket.sendall(b'i3-ipc' + struct.pack('<II', len(encoded), kind) + encoded)
        header = self.receive(14)
        size, _ = struct.unpack('<II', header[6:])
        return json.loads(self.receive(size))

    def command(self, value):
        results = self.request(0, value)
        if any(not result.get('success') for result in results):
            raise RuntimeError(str(results))

    def windows(self):
        found = []
        def visit(node, workspace=None):
            if node['type'] == 'workspace':
                workspace = node
            if node.get('window') and workspace is not None and node.get('window_type') != 'dock':
                found.append((node, workspace))
            children = node.get('nodes', []) + node.get('floating_nodes', [])
            order = node.get('focus', [])
            for child in sorted(children, key=lambda child: order.index(child['id']) if child['id'] in order else len(order)):
                visit(child, workspace)
        visit(self.request(4))
        return found


def pointer():
    root_return, child = c.c_ulong(), c.c_ulong()
    x, y, local_x, local_y = c.c_int(), c.c_int(), c.c_int(), c.c_int()
    mask = c.c_uint()
    xlib.XQueryPointer(display, root, c.byref(root_return), c.byref(child), c.byref(x), c.byref(y), c.byref(local_x), c.byref(local_y), c.byref(mask))
    return x.value, y.value, mask.value


def geometry(cid, rect):
    i3.command(f'[con_id={cid}] resize set {rect["width"]} px {rect["height"]} px, move absolute position {rect["x"]} px {rect["y"]} px')


def save():
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state))
    temporary.replace(state_path)


def minimize(node, workspace):
    state['minimized'][str(node['id'])] = {'workspace': workspace['name'], 'floating': node['floating'].endswith('on'), 'rect': node['rect']}
    save()
    i3.command(f'[con_id={node["id"]}] move scratchpad')


def restore(node):
    cid = node['id']
    saved = state['minimized'].pop(str(cid), None)
    workspace = saved['workspace'] if saved else next(ws['name'] for ws in i3.request(1) if ws['focused'])
    floating = saved['floating'] if saved else True
    i3.command(f'[con_id={cid}] move container to workspace {json.dumps(workspace)}, floating {"enable" if floating else "disable"}; workspace {json.dumps(workspace)}; [con_id={cid}] focus')
    if saved and floating:
        geometry(cid, saved['rect'])
    save()


def maximize(node, workspace):
    cid = node['id']
    saved = state['maximized'].pop(str(cid), None)
    if saved:
        if saved['floating']:
            geometry(cid, saved['rect'])
        else:
            i3.command(f'[con_id={cid}] floating disable, border pixel 1')
    else:
        state['maximized'][str(cid)] = {'floating': node['floating'].endswith('on'), 'rect': node['rect']}
        i3.command(f'[con_id={cid}] fullscreen disable, floating enable, border pixel 3')
        geometry(cid, workspace['rect'])
    save()


def snap_side(rect, x, y):
    nx = (x - rect['x']) / rect['width']
    ny = (y - rect['y']) / rect['height']
    return min((('left', nx), ('right', 1 - nx), ('top', ny), ('bottom', 1 - ny)), key=lambda pair: pair[1])[0]


def snap_plan(workspace, source, target, side):
    tree = copy.deepcopy(workspace)
    def remove(node):
        if node['id'] == source['id']:
            return None
        children = [result for child in node.get('nodes', []) if (result := remove(child)) is not None]
        node['nodes'] = children
        if not node.get('window') and node['type'] != 'workspace':
            if not children:
                return None
            if len(children) == 1:
                child = children[0]
                child['percent'] = node.get('percent')
                return child
        return node
    tree = remove(tree)
    if tree is None:
        return {}
    def insert(node):
        if node['id'] == target['id']:
            share = node.get('percent')
            incoming = copy.deepcopy(source)
            incoming['percent'] = node['percent'] = .5
            children = [incoming, node] if side in ('left', 'top') else [node, incoming]
            return {'id': -1, 'type': 'con', 'layout': 'splith' if side in ('left', 'right') else 'splitv', 'percent': share, 'nodes': children}
        node['nodes'] = [insert(child) for child in node.get('nodes', [])]
        return node
    tree = insert(tree)
    result = {}
    def allocate(node, rect):
        if node.get('window'):
            result[node['id']] = {'rect': dict(rect), 'name': node.get('name', 'Window')}
            return
        children = node.get('nodes', [])
        if not children:
            return
        vertical = node.get('layout') == 'splitv'
        axis, length = ('y', 'height') if vertical else ('x', 'width')
        weights = [child.get('percent') or 1 / len(children) for child in children]
        total = sum(weights)
        consumed = 0
        fraction = 0
        for index, child in enumerate(children):
            fraction += weights[index] / total
            edge = rect[length] if index == len(children) - 1 else round(rect[length] * fraction)
            child_rect = dict(rect)
            child_rect[axis] += consumed
            child_rect[length] = edge - consumed
            allocate(child, child_rect)
            consumed = edge
    allocate(tree, workspace['rect'])
    return result


def place_snap(source, target, side):
    cid, tid = source['id'], target['id']
    mark = f'rice-drop-{os.getpid()}'
    orientation = 'h' if side in ('left', 'right') else 'v'
    opposite = 'v' if orientation == 'h' else 'h'
    i3.command(f'[con_id={cid}] fullscreen disable, floating disable, border pixel 1')
    try:
        i3.command(f'[con_id={tid}] mark --add {mark}, split {opposite}, split {orientation}')
        i3.command(f'[con_id={cid}] move container to mark {mark}')
        if side in ('left', 'top'):
            direction = 'left' if side == 'left' else 'up'
            i3.command(f'[con_id={cid}] move {direction}')
        i3.command(f'[con_id={cid}] focus')
        state['maximized'].pop(str(cid), None)
        save()
    finally:
        i3.command(f'unmark {mark}')


def snap_drag(node, workspace):
    start_x, start_y, mask = pointer()
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('PangoCairo', '1.0')
    from gi.repository import Gdk, GLib, Gtk, Pango, PangoCairo
    import cairo
    preview = Gtk.Window(type=Gtk.WindowType.POPUP)
    preview.set_title('Snap preview')
    preview.set_accept_focus(False)
    preview.set_app_paintable(True)
    visual = preview.get_screen().get_rgba_visual()
    if visual:
        preview.set_visual(visual)
    drawing = Gtk.DrawingArea()
    preview.add(drawing)
    selected = None
    started = False
    previous_point = None
    candidates = []
    planned = {}
    positions = {}
    origins = {}
    animation_start = 0
    area = workspace['rect']
    def draw(widget, context):
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.set_source_rgba(0, 0, 0, 0)
        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)
        for cid, item in planned.items():
            rect = positions.get(cid, item['rect'])
            x, y = rect['x'] - area['x'], rect['y'] - area['y']
            width, height = rect['width'], rect['height']
            active = cid == node['id']
            context.set_source_rgba(0, .4, .8, .22) if active else context.set_source_rgba(.3, .35, .4, .08)
            context.rectangle(x + 1, y + 1, max(0, width - 2), max(0, height - 2))
            context.fill_preserve()
            context.set_source_rgba(0, .4, .8, .95) if active else context.set_source_rgba(.3, .35, .4, .65)
            context.set_line_width(2)
            context.stroke()
            layout = widget.create_pango_layout(item['name'].replace('\n', ' '))
            layout.set_font_description(Pango.FontDescription('Noto Sans 10'))
            layout.set_width(max(1, int(width - 32)) * Pango.SCALE)
            layout.set_ellipsize(Pango.EllipsizeMode.END)
            text_width, text_height = layout.get_pixel_size()
            tx, ty = x + (width - text_width) / 2, y + (height - text_height) / 2
            context.set_source_rgba(.96, .96, .97, .94)
            context.rectangle(tx - 8, ty - 5, text_width + 16, text_height + 10)
            context.fill()
            context.set_source_rgb(.11, .11, .12)
            context.move_to(tx, ty)
            PangoCairo.show_layout(context, layout)
        return False
    drawing.connect('draw', draw)
    def update():
        nonlocal selected, started, previous_point, candidates, planned, positions, origins, animation_start
        x, y, mask = pointer()
        if not mask & (1 << 8):
            preview.hide()
            try:
                if started and selected:
                    target, side = selected
                    current = {n['id']: n for n, ws in i3.windows()}
                    if node['id'] in current and target['id'] in current:
                        place_snap(current[node['id']], current[target['id']], side)
            finally:
                Gtk.main_quit()
            return False
        if not started:
            if abs(x - start_x) + abs(y - start_y) < 5:
                return True
            started = True
            candidates = [n for n, ws in i3.windows() if n['id'] != node['id'] and ws['id'] == workspace['id'] and n['floating'].endswith('off') and not n.get('fullscreen_mode')]
        if planned:
            progress = min(1, (time.monotonic() - animation_start) / .12)
            eased = 1 - (1 - progress) ** 3
            positions = {cid: {key: origins[cid][key] + (item['rect'][key] - origins[cid][key]) * eased for key in ('x', 'y', 'width', 'height')} for cid, item in planned.items()}
            if progress < 1:
                drawing.queue_draw()
        if previous_point == (x, y):
            return True
        previous_point = x, y
        target = next((n for n in candidates if n['rect']['x'] <= x < n['rect']['x'] + n['rect']['width'] and n['rect']['y'] <= y < n['rect']['y'] + n['rect']['height']), None)
        if target is None:
            selected = None
            preview.hide()
            return True
        side = snap_side(target['rect'], x, y)
        if selected and selected[0]['id'] == target['id'] and selected[1] == side:
            return True
        selected = target, side
        planned = snap_plan(workspace, node, target, side)
        actual = {n['id']: n['rect'] for n in candidates + [node]}
        origins = {cid: dict(positions.get(cid, actual.get(cid, item['rect']))) for cid, item in planned.items()}
        animation_start = time.monotonic()
        preview.resize(area['width'], area['height'])
        preview.move(area['x'], area['y'])
        drawing.queue_draw()
        preview.show_all()
        preview.get_window().set_pass_through(True)
        return True
    GLib.timeout_add(8, update)
    Gtk.main()
    preview.destroy()


def choose(labels, prompt):
    args = ['rofi', '-dmenu', '-i', '-no-custom', '-format', 'i', '-p', prompt]
    result = subprocess.run(args, input='\n'.join(labels), capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip().isdigit():
        index = int(result.stdout.strip())
        return index if index < len(labels) else None
    return None


def history_path():
    return Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / f'rice-window-history-{os.getuid()}.json'


def track_focus():
    daemon_lock = open(Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / f'rice-window-tracker-{os.getuid()}.lock', 'a')
    try:
        fcntl.flock(daemon_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return
    while True:
        try:
            connection = I3()
            order = [n['id'] for n, ws in connection.windows()]
            connection.request(2, json.dumps(['window']))
            while True:
                temporary = history_path().with_suffix('.tmp')
                temporary.write_text(json.dumps(order))
                temporary.replace(history_path())
                header = connection.receive(14)
                size, kind = struct.unpack('<II', header[6:])
                event = json.loads(connection.receive(size))
                cid = event.get('container', {}).get('id')
                if cid and event.get('change') in ('focus', 'close'):
                    order = [value for value in order if value != cid]
                    if event['change'] == 'focus':
                        order.insert(0, cid)
                    order = order[:100]
        except (OSError, RuntimeError, subprocess.CalledProcessError):
            time.sleep(.25)


def main():
    global i3, state_path, state, xlib, display, root
    action = sys.argv[1] if len(sys.argv) > 1 else 'switch'
    if action == 'daemon':
        track_focus()
        sys.exit(0)
    lock = open(Path(os.environ.get('XDG_RUNTIME_DIR', '/tmp')) / f'rice-windows-{os.getuid()}.lock', 'a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    i3 = I3()
    state_path = Path.home() / '.local/state/rice/windows.json'
    try:
        state = json.loads(state_path.read_text())
    except (FileNotFoundError, ValueError):
        state = {'minimized': {}, 'maximized': {}}
    windows = i3.windows()
    try:
        order = json.loads(history_path().read_text())
        windows.sort(key=lambda pair: order.index(pair[0]['id']) if pair[0]['id'] in order else len(order))
    except (FileNotFoundError, ValueError):
        pass
    if not windows:
        sys.exit(0)
    valid = {str(n['id']) for n, ws in windows}
    for key in ('minimized', 'maximized'):
        state[key] = {cid: value for cid, value in state[key].items() if cid in valid}
    node, workspace = next(((n, ws) for n, ws in windows if n.get('focused')), windows[0])
    if action == 'snap':
        xlib = c.CDLL('libX11.so.6')
        xlib.XOpenDisplay.argtypes = [c.c_char_p]
        xlib.XOpenDisplay.restype = c.c_void_p
        xlib.XDefaultRootWindow.argtypes = [c.c_void_p]
        xlib.XDefaultRootWindow.restype = c.c_ulong
        xlib.XQueryPointer.argtypes = [c.c_void_p, c.c_ulong, c.POINTER(c.c_ulong), c.POINTER(c.c_ulong), c.POINTER(c.c_int), c.POINTER(c.c_int), c.POINTER(c.c_int), c.POINTER(c.c_int), c.POINTER(c.c_uint)]
        display = xlib.XOpenDisplay(None)
        if display:
            root = xlib.XDefaultRootWindow(display)
            snap_drag(node, workspace)
    elif action in ('switch', 'alt-tab'):
        candidates = [(n, ws) for n, ws in windows if n['id'] != node['id']]
        if action == 'alt-tab':
            index = windows.index(candidates[0]) if candidates else None
        else:
            index = choose([n.get('name', 'Window').replace('\n', ' ') + ('  —  minimized' if ws['name'] == '__i3_scratch' else '  —  ' + ws['name']) for n, ws in windows], 'Windows')
        if index is not None:
            selected, ws = windows[index]
            if ws['name'] == '__i3_scratch':
                restore(selected)
            else:
                i3.command(f'[con_id={selected["id"]}] focus')
    elif action == 'restore':
        hidden = [(n, ws) for n, ws in windows if ws['name'] == '__i3_scratch']
        ordered = list(state['minimized'])
        if hidden:
            selected = max(hidden, key=lambda pair: ordered.index(str(pair[0]['id'])) if str(pair[0]['id']) in ordered else -1)[0]
            restore(selected)
    else:
        if action == 'minimize':
            minimize(node, workspace)
        elif action == 'maximize':
            maximize(node, workspace)
        elif action == 'retile':
            state['maximized'].pop(str(node['id']), None)
            i3.command(f'[con_id={node["id"]}] floating disable, border pixel 1')
            save()


if __name__ == '__main__':
    main()
