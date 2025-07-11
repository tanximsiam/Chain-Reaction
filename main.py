import arcade
from constants import *

class ChainReactionGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def setup(self):
        self.title_text = arcade.Text(
            "Chain Reaction",
            200,
            400,
            color=arcade.color.WHITE,
            font_size=24
        )

    def draw_grid(self):
        for row in range(ROWS + 1):
            y = row * ROW_SIZE
            arcade.draw_line(0, y, SCREEN_WIDTH, y, arcade.color.LIGHT_GRAY, GRID_LINE_WIDTH)

        for col in range(COLS + 1):
            x = col * COL_SIZE
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, arcade.color.LIGHT_GRAY, GRID_LINE_WIDTH)


    def on_draw(self):
        self.clear()
        self.title_text.draw()
        self.draw_grid()

if __name__ == "__main__":
    game = ChainReactionGame()
    game.setup()
    arcade.run()
