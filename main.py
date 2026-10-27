from pathlib import Path

import arcade
import pyglet

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, BACKGROUND
from menu_view import MenuView

ICON = Path(__file__).parent / "assets" / "icon.png"  # also valid inside a PyInstaller bundle

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.set_icon(pyglet.image.load(str(ICON)))
    window.background_color = BACKGROUND
    window.show_view(MenuView())
    arcade.run()
