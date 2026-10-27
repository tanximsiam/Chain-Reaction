"""Fonts, colours and shared textures for every screen."""
import arcade
from arcade.gui import NinePatchTexture
from PIL import Image, ImageDraw

for path in ("Kenney/Kenney_Future.ttf", "Liberation/Liberation_Sans_Regular.ttf",
             "Liberation/Liberation_Sans_Bold.ttf"):
    arcade.load_font(f":system:fonts/ttf/{path}")

TITLE_FONT = "Kenney Future"
FONT = "Liberation Sans"
BOLD_FONT_PATH = arcade.resources.resolve(":system:fonts/ttf/Liberation/Liberation_Sans_Bold.ttf")

TEXT = (241, 245, 249)   # slate 100
INK = (2, 6, 23)         # slate 950, used to darken
WHITE = (255, 255, 255)
SUPERSAMPLE = 4

# Button variants: face, hovered face, content colour.
# Dark UI: primary actions and selected options are light with dark text.
VARIANTS = {
    "primary": ((241, 245, 249), (255, 255, 255), (15, 23, 42)),
    "secondary": ((51, 65, 85), (71, 85, 105), TEXT),
    "raised": ((71, 85, 105), (100, 116, 139), TEXT),  # secondary on a slate 800 panel
}


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def smooth_image(width, height, draw):
    """Draw at SUPERSAMPLE x size and downsample, so edges come out anti-aliased."""
    big = Image.new("RGBA", (width * SUPERSAMPLE, height * SUPERSAMPLE), (0, 0, 0, 0))
    draw(ImageDraw.Draw(big), SUPERSAMPLE)
    return big.resize((width, height), Image.LANCZOS)


_patches = {}


def rounded_patch(color, radius, highlight=None):
    """Stretchable rounded rectangle. `highlight` adds a thin lighter top edge (bevel)."""
    key = (tuple(color), radius, highlight and tuple(highlight))
    if key not in _patches:
        size = 2 * radius + 2

        def draw(d, s):
            if highlight:
                d.rounded_rectangle((0, 0, size * s - 1, size * s - 1), radius * s, fill=tuple(highlight))
            top = 2 * s if highlight else 0
            d.rounded_rectangle((0, top, size * s - 1, size * s - 1), radius * s, fill=tuple(color))

        texture = arcade.Texture(smooth_image(size, size, draw), hash=f"patch-{key}")
        _patches[key] = NinePatchTexture(radius, radius, radius, radius, texture)
    return _patches[key]
