import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

class ChainReactionGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()

if __name__ == "__main__":
    game = ChainReactionGame()
    arcade.run()
