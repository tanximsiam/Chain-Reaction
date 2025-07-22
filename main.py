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
            600,
            color=arcade.color.WHITE,
            font_size=24
        )

    def draw_grid(self):
        for row in range(ROWS + 1):
            y = row * ROW_SIZE
            arcade.draw_line(OFFSET, y + OFFSET, SCREEN_WIDTH - OFFSET, y + OFFSET, arcade.color.LIGHT_GRAY, GRID_LINE_WIDTH)

        for col in range(COLS + 1):
            x = col * COL_SIZE
            arcade.draw_line(x + OFFSET, OFFSET , x + OFFSET, SCREEN_HEIGHT - (2 * ROW_SIZE) - OFFSET, arcade.color.LIGHT_GRAY, GRID_LINE_WIDTH)

    def get_cell_from_mouse(self, x, y):
        grid_left = OFFSET
        grid_bottom = OFFSET
        grid_top = SCREEN_HEIGHT - OFFSET - (2 * ROW_SIZE)

        col = (x - grid_left) // COL_SIZE
        row = (y - grid_bottom) // ROW_SIZE

        if 0 <= col < COLS and 0 <= row < ROWS and y < grid_top:
            return int(col), int(row)
        return None

    def on_mouse_press(self, x, y, button, modifiers):
        print(f"Mouse clicked at: ({x}, {y})")
        cell = self.get_cell_from_mouse(x, y)
        if cell:
            col, row = cell
            print(f"Clicked cell: ({col}, {row})")
        else:
            print("Clicked outside board.")


    def on_draw(self):
        self.clear()
        self.title_text.draw()
        self.draw_grid()

if __name__ == "__main__":
    game = ChainReactionGame()
    game.setup()
    arcade.run()
