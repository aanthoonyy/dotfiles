from pathlib import Path
import cairo

surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 3840, 2160)
ctx = cairo.Context(surface)
ctx.set_source_rgb(229 / 255, 229 / 255, 234 / 255)
ctx.paint()
surface.write_to_png(str(Path(__file__).resolve().parent / 'wallpaper.png'))
