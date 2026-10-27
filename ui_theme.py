"""Fonts and arcade.gui widget styles shared by every screen."""
import arcade
from arcade.gui import UIFlatButton

from constants import BACKGROUND, CELL_COLOR

for path in ("Kenney/Kenney_Future.ttf", "Liberation/Liberation_Sans_Regular.ttf",
             "Liberation/Liberation_Sans_Bold.ttf"):
    arcade.load_font(f":system:fonts/ttf/{path}")

TITLE_FONT = "Kenney Future"
FONT = "Liberation Sans"

TEXT = (241, 245, 249)          # slate 100
HOVER = (51, 65, 85)            # slate 700
PRESS = (71, 85, 105)           # slate 600
LIGHT_HOVER = (203, 213, 225)   # slate 300


def _style(bg, fg, hover, press, size):
    def s(fill):
        return UIFlatButton.UIStyle(font_size=size, font_name=FONT, font_color=fg, bg=fill)
    return {"normal": s(bg), "hover": s(hover), "press": s(press), "disabled": s(bg)}


# Dark UI: primary actions and selected options are light pills with dark text.
PRIMARY = _style(TEXT, BACKGROUND, LIGHT_HOVER, LIGHT_HOVER, 15)
SECONDARY = _style(CELL_COLOR, TEXT, HOVER, PRESS, 15)
RAISED = _style(HOVER, TEXT, PRESS, PRESS, 15)  # secondary button on a slate 800 panel
SMALL =_style(CELL_COLOR, TEXT, HOVER, PRESS, 12)
