import atexit
import datetime
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib, Gtk


def command(*args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=3)
        return result.stdout.strip() if result.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''


runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))
address = str(runtime / 'rice-controls.sock')
section = sys.argv[1] if len(sys.argv) > 1 else 'sound'
client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
try:
    client.sendto(section.encode(), address)
    sys.exit(0)
except (FileNotFoundError, ConnectionRefusedError):
    Path(address).unlink(missing_ok=True)
client.bind(address)
atexit.register(lambda: Path(address).unlink(missing_ok=True))

css = Gtk.CssProvider()
css.load_from_data(b'''
window { background-color: transparent; }
.card { background-color: #f5f5f7; color: #1d1d1f; border: 1px solid #c7c7cc; border-radius: 12px; padding: 20px; }
.card label { color: #1d1d1f; font-family: Noto Sans; font-size: 10pt; }
.card .heading { font-size: 14pt; font-weight: 600; }
.card .secondary { color: #616166; font-size: 9pt; }
.card button { background-image: none; background-color: #ffffff; color: #1d1d1f; border: 1px solid #d1d1d6; border-radius: 7px; box-shadow: none; padding: 6px 10px; }
.card button:hover { background-color: #e5edfa; }
.card button:checked { background-color: #d6e8ff; }
.card .output-row { padding: 12px; border-color: transparent; background-color: transparent; }
.card .output-row:hover { background-color: #e9e9ed; }
.card .active-output { background-color: #e4efff; border-color: #c8def7; }
.card .device-name { font-weight: 600; }
.card .check { color: #0066cc; font-size: 12pt; }
.card .icon-button { padding: 6px; min-width: 24px; min-height: 24px; }
.card scale trough { background-color: #d1d1d6; border: none; min-height: 5px; }
.card scale highlight { background-color: #0088ff; border: none; }
.card scale slider { background-image: none; background-color: #ffffff; border: 1px solid #bdbdc2; min-width: 16px; min-height: 16px; box-shadow: 0 1px 2px alpha(black, 0.12); }
.card calendar { background-color: #ffffff; color: #1d1d1f; border: 1px solid #d1d1d6; border-radius: 7px; padding: 8px; }
.card calendar:selected { background-color: #0088ff; color: #ffffff; }
.card calendar.header { background-color: #ececf0; }
''')
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


class Controls(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_title('Control Center')
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.set_app_paintable(True)
        self.panel = None
        self.targets = {}
        self.seat = None
        self.volume_timer = None
        self.pending_volume = None
        self.connect('key-press-event', self.key_pressed)
        self.connect('button-press-event', self.pointer_pressed)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

    def label(self, text, style=None):
        label = Gtk.Label(label=text, xalign=0)
        label.set_line_wrap(True)
        label.set_max_width_chars(34)
        if style:
            label.get_style_context().add_class(style)
        return label

    def add_item(self, widget):
        self.card.pack_start(widget, False, False, 0)
        return widget

    def dismiss(self):
        if self.seat:
            self.seat.ungrab()
            self.seat = None
        self.hide()
        return False

    def key_pressed(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.dismiss()
            return True
        return False

    def pointer_pressed(self, widget, event):
        x, y = self.get_position()
        width, height = self.get_size()
        if not (x <= event.x_root < x + width and y <= event.y_root < y + height):
            target = next((name for name, rect in self.targets.items() if rect[0] <= event.x_root < rect[0] + rect[2] and rect[1] <= event.y_root < rect[1] + rect[3]), None)
            if target:
                self.show_panel(target)
            else:
                self.dismiss()
            return True
        return False

    def show_panel(self, name, toggle=True):
        if name.startswith('{'):
            event = json.loads(name)
            name = event['panel']
            widths = {'sound': 40, 'network': 40, 'calendar': 176}
            left = event['x'] - sum(width for key, width in list(widths.items())[:list(widths).index(name)])
            self.targets = {}
            for key, width in widths.items():
                self.targets[key] = (left, event['y'], width, event['height'])
                left += width
        if name not in ('sound', 'sound_outputs', 'network', 'calendar'):
            return False
        if toggle and self.get_visible() and self.panel == name:
            return self.dismiss()
        self.dismiss()
        self.panel = name
        if self.get_child():
            self.remove(self.get_child())
        self.card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.card.get_style_context().add_class('card')
        self.card.set_size_request(360 if name in ('sound', 'sound_outputs') else 330, -1)
        self.add(self.card)
        getattr(self, name)()
        self.show_all()
        display = Gdk.Display.get_default()
        pointer = display.get_default_seat().get_pointer()
        screen, x, y = pointer.get_position()
        monitor = display.get_monitor_at_point(x, y)
        area = monitor.get_geometry()
        minimum, natural = self.get_preferred_size()
        width, height = natural.width, natural.height
        self.resize(width, height)
        self.move(area.x + area.width - width - 8, area.y + area.height - height - 34)
        self.present()
        self.seat = display.get_default_seat()
        status = self.seat.grab(self.get_window(), Gdk.SeatCapabilities.ALL, True, None, None, None, None)
        if status != Gdk.GrabStatus.SUCCESS:
            self.dismiss()
        return False

    def outputs(self):
        try:
            return json.loads(command('pactl', '-f', 'json', 'list', 'sinks') or '[]')
        except ValueError:
            return []

    def device_details(self, sink):
        properties = sink.get('properties', {})
        description = sink.get('description', 'Audio output')
        name = properties.get('alsa.card_name') or properties.get('device.description') or description
        if 'hdmi' in sink.get('name', '').lower():
            return 'HDMI audio', 'Monitor or TV', 'video-display-symbolic'
        if any(word in name.lower() for word in ('earpod', 'headphone', 'headset')):
            return name, 'Headphones', 'audio-headphones-symbolic'
        return name, 'Speakers', 'audio-speakers-symbolic'

    def device_row(self, sink, selected=False, chooser=False):
        name, detail, icon = self.device_details(sink)
        button = Gtk.Button()
        button.get_style_context().add_class('output-row')
        if selected and chooser:
            button.get_style_context().add_class('active-output')
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.pack_start(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        text.pack_start(self.label(name, 'device-name'), False, False, 0)
        text.pack_start(self.label(detail, 'secondary'), False, False, 0)
        row.pack_start(text, True, True, 0)
        row.pack_end(self.label(('✓' if selected else '') if chooser else '›', 'check'), False, False, 0)
        button.add(row)
        if chooser:
            button.connect('clicked', self.change_output, sink['name'])
        else:
            button.set_tooltip_text('Choose sound output')
            button.connect('clicked', lambda *_: self.show_panel('sound_outputs', toggle=False))
        return button

    def sound(self):
        self.add_item(self.label('Sound', 'heading'))
        outputs = self.outputs()
        default = command('pactl', 'get-default-sink')
        sink = next((output for output in outputs if output['name'] == default), {})
        self.selected_sink = default
        if not sink:
            self.add_item(self.label('No audio output available', 'secondary'))
            return
        self.add_item(self.device_row(sink))
        channels = list(sink.get('volume', {}).values())
        volume = round(sum(channel['value'] for channel in channels) / max(len(channels), 1) / 65536 * 100)
        muted = sink.get('mute', False)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.mute_button = Gtk.ToggleButton()
        self.mute_button.get_style_context().add_class('icon-button')
        self.mute_button.set_active(muted)
        self.update_speaker_icon(self.mute_button, muted, volume)
        self.mute_button.connect('toggled', self.mute_changed)
        row.pack_start(self.mute_button, False, False, 0)
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_draw_value(False)
        slider.set_value(min(volume, 100))
        slider.connect('value-changed', self.volume_changed)
        row.pack_start(slider, True, True, 0)
        self.level = self.label(str(volume), 'secondary')
        self.level.set_width_chars(3)
        self.level.set_xalign(1)
        row.pack_end(self.level, False, False, 0)
        self.add_item(row)

    def sound_outputs(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        back = Gtk.Button(label='‹')
        back.get_style_context().add_class('icon-button')
        back.set_tooltip_text('Back to volume')
        back.connect('clicked', lambda *_: self.show_panel('sound', toggle=False))
        header.pack_start(back, False, False, 0)
        header.pack_start(self.label('Sound output', 'heading'), True, True, 0)
        self.add_item(header)
        self.add_item(self.label('Choose where to play sound', 'secondary'))
        default = command('pactl', 'get-default-sink')
        outputs = self.outputs()
        if not outputs:
            self.add_item(self.label('No audio output available', 'secondary'))
        for output in outputs:
            self.add_item(self.device_row(output, output['name'] == default, chooser=True))

    def update_speaker_icon(self, button, muted, volume=100):
        state = 'muted' if muted or volume == 0 else ('low' if volume < 34 else ('medium' if volume < 67 else 'high'))
        button.set_image(Gtk.Image.new_from_icon_name('audio-volume-' + state + '-symbolic', Gtk.IconSize.BUTTON))
        button.set_tooltip_text('Unmute' if muted else 'Mute')

    def change_output(self, button, name):
        self.card.set_sensitive(False)
        def update():
            message = ''
            try:
                result = subprocess.run(['pactl', 'set-default-sink', name], capture_output=True, text=True, timeout=3)
                if result.returncode:
                    message = 'Could not switch output device.'
                else:
                    streams = json.loads(command('pactl', '-f', 'json', 'list', 'sink-inputs') or '[]')
                    for stream in streams:
                        result = subprocess.run(['pactl', 'move-sink-input', str(stream['index']), name], capture_output=True, text=True, timeout=3)
                        if result.returncode:
                            message = 'Output changed. Some apps may need playback restarted.'
            except (OSError, subprocess.TimeoutExpired, ValueError):
                message = 'Could not finish switching audio. Try again.'
            def finish():
                if self.panel in ('sound', 'sound_outputs'):
                    visible = self.get_visible()
                    self.show_panel('sound', toggle=False)
                    if message:
                        self.add_item(self.label(message, 'secondary'))
                        self.card.show_all()
                    if not visible:
                        self.dismiss()
                return False
            GLib.idle_add(finish)
        threading.Thread(target=update, daemon=True).start()

    def volume_changed(self, slider):
        value = round(slider.get_value())
        self.level.set_text(str(value))
        self.update_speaker_icon(self.mute_button, self.mute_button.get_active(), value)
        self.pending_volume = (self.selected_sink, value)
        if self.volume_timer:
            GLib.source_remove(self.volume_timer)
        self.volume_timer = GLib.timeout_add(60, self.set_volume)

    def set_volume(self):
        self.volume_timer = None
        sink, volume = self.pending_volume
        subprocess.Popen(['pactl', 'set-sink-volume', sink, f'{volume}%'])
        return False

    def mute_changed(self, button):
        subprocess.Popen(['pactl', 'set-sink-mute', self.selected_sink, '1' if button.get_active() else '0'])
        self.update_speaker_icon(button, button.get_active(), int(self.level.get_text()))

    def network(self):
        self.add_item(self.label('Network', 'heading'))
        devices = command('nmcli', '-t', '--escape', 'no', '-f', 'DEVICE,TYPE,STATE,CONNECTION', 'device').splitlines()
        active = False
        for line in devices:
            parts = line.split(':', 3)
            if len(parts) != 4:
                continue
            device, kind, state, connection = parts
            if kind in ('ethernet', 'wifi') and state == 'connected':
                active = True
                self.add_item(self.label('Ethernet' if kind == 'ethernet' else 'Wi-Fi'))
                self.add_item(self.label(connection, 'secondary'))
        if not active:
            self.add_item(self.label('No active connection', 'secondary'))
        self.network_message = self.add_item(self.label('Manage wireless and saved connections below.', 'secondary'))
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.pack_start(self.label('Wi-Fi'), True, True, 0)
        switch = Gtk.Switch()
        switch.set_active(command('nmcli', 'radio', 'wifi') == 'enabled')
        switch.set_sensitive(any(':wifi:' in line for line in devices))
        switch.connect('state-set', self.wifi_changed)
        row.pack_end(switch, False, False, 0)
        self.add_item(row)
        button = Gtk.Button(label='Network settings…')
        button.connect('clicked', self.network_settings)
        self.add_item(button)

    def wifi_changed(self, switch, state):
        def update():
            try:
                result = subprocess.run(['nmcli', 'radio', 'wifi', 'on' if state else 'off'], capture_output=True, text=True, timeout=10)
                success = result.returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                success = False
            def finish():
                switch.set_state(state if success else not state)
                switch.set_sensitive(True)
                self.network_message.set_text(('Wi-Fi enabled' if state else 'Wi-Fi disabled') if success else 'Could not change Wi-Fi. Open Network settings to continue.')
                return False
            GLib.idle_add(finish)
        switch.set_sensitive(False)
        threading.Thread(target=update, daemon=True).start()
        return True

    def network_settings(self, button):
        self.dismiss()
        subprocess.Popen(['nm-connection-editor'])

    def calendar(self):
        now = datetime.datetime.now()
        self.add_item(self.label(now.strftime('%A'), 'heading'))
        self.add_item(self.label(now.strftime('%m-%d-%Y'), 'secondary'))
        calendar = Gtk.Calendar()
        calendar.set_display_options(Gtk.CalendarDisplayOptions.SHOW_HEADING | Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES)
        self.add_item(calendar)
        button = Gtk.Button(label='Today')
        def today(button):
            now = datetime.datetime.now()
            calendar.select_month(now.month - 1, now.year)
            calendar.select_day(now.day)
        button.connect('clicked', today)
        self.add_item(button)


window = Controls()

def incoming(source, condition):
    data = client.recv(128).decode()
    window.show_panel(data)
    return True

GLib.io_add_watch(client.fileno(), GLib.IO_IN, incoming)
GLib.idle_add(window.show_panel, section)
signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
Gtk.main()
