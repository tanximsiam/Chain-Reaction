"""Stroke icons drawn once with PIL. Arcade ships no glyph-only icon set (its control icons sit on tiles)."""
import math

import arcade
from PIL import Image, ImageDraw, ImageFont

from ui_theme import BOLD_FONT_PATH

GRID = 24   # icons are designed on a 24-unit grid
SCALE = 8   # pixels per unit when drawing; downsampled afterwards for smooth edges
STROKE = 2


def _draw(name, d):
    w = STROKE * SCALE

    def p(x, y):
        return x * SCALE, y * SCALE

    def cap(x, y):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill="white")

    def line(*points):
        points = [p(*pt) for pt in points]
        d.line(points, fill="white", width=w, joint="curve")
        cap(*points[0])
        cap(*points[-1])

    def arc(cx, cy, r, start, end):
        # PIL strokes inward from the bounding box, so pad by half a stroke; angles run clockwise.
        pad = STROKE / 2
        d.arc((p(cx - r - pad, cy - r - pad), p(cx + r + pad, cy + r + pad)), start, end, fill="white", width=w)
        for a in (start, end):
            cap(*p(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))

    def speaker():
        d.polygon([p(3, 9), p(7, 9), p(12, 4.5), p(12, 19.5), p(7, 15), p(3, 15)], fill="white")

    def note():
        for x, y in ((7, 18), (17, 16)):
            d.ellipse((*p(x - 2.8, y - 2.4), *p(x + 2.8, y + 2.4)), fill="white")
        line((9.6, 18), (9.6, 5.5))
        line((19.6, 16), (19.6, 3.5))
        d.line([p(9.6, 5.5), p(19.6, 3.5)], fill="white", width=3 * SCALE)

    if name == "menu":
        line((4, 7), (20, 7))
        line((4, 12), (20, 12))
        line((4, 17), (20, 17))
    elif name == "restart":
        arc(12, 13, 8, -30, 270)
        line((9, 2), (12, 5), (9, 8))
    elif name == "sound_on":
        speaker()
        arc(12, 12, 4, -45, 45)
        arc(12, 12, 8, -45, 45)
    elif name == "sound_off":
        speaker()
        line((16, 9), (22, 15))
        line((22, 9), (16, 15))
    elif name == "music_on":
        note()
    elif name == "music_off":
        note()
        line((3, 3), (21, 21))
    elif name == "help":
        font = ImageFont.truetype(BOLD_FONT_PATH, 21 * SCALE)
        d.text(p(12, 12.5), "?", fill="white", font=font, anchor="mm")
    elif name == "exit":
        arc(12, 13, 8, -60, 240)
        line((12, 2.5), (12, 11))
    elif name == "back":
        line((19, 12), (5, 12))
        line((11, 6), (5, 12), (11, 18))
    elif name == "close":
        line((6, 6), (18, 18))
        line((18, 6), (6, 18))
    else:
        raise ValueError(f"unknown icon {name!r}")


_cache = {}


def icon_texture(name, color, size):
    key = (name, tuple(color), size)
    if key not in _cache:
        big = Image.new("RGBA", (GRID * SCALE, GRID * SCALE), (0, 0, 0, 0))
        _draw(name, ImageDraw.Draw(big))
        alpha = big.resize((size, size), Image.LANCZOS).getchannel("A")
        image = Image.new("RGBA", (size, size), tuple(color))
        image.putalpha(alpha)
        _cache[key] = arcade.Texture(image, hash=f"icon-{key}")
    return _cache[key]
