import math
from pathlib import Path
import cairo

width, height = 3840, 2160
surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
ctx = cairo.Context(surface)
gradient = cairo.LinearGradient(0, 0, width, height)
gradient.add_color_stop_rgb(0, 0.047, 0.063, 0.082)
gradient.add_color_stop_rgb(1, 0.098, 0.137, 0.149)
ctx.set_source(gradient)
ctx.paint()
ctx.set_line_width(1.5)
for i in range(35):
    ctx.new_path()
    for step in range(241):
        x = -160 + step * 18
        y = 1510 + i * 30 + 190 * math.sin(x / 960 + 0.3) - 420 * math.exp(-((x - 2940) / 1000) ** 2)
        if step == 0:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)
    ctx.set_source_rgba(0.57, 0.72, 0.65, 0.055 + 0.04 * (i / 35))
    ctx.stroke()
surface.write_to_png(str(Path(__file__).resolve().parents[1] / 'assets/wallpaper.png'))
