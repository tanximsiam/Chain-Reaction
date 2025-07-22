import arcade
from constants import *

class ChainReactionGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.board = [[Cell(row, col) for col in range(COLS)] for row in range(ROWS)]

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
        cell_pos = self.get_cell_from_mouse(x, y)
        if cell_pos:
            col, row = cell_pos
            self.board[row][col].add_atom()



    def on_draw(self):
        self.clear()
        self.title_text.draw()
        self.draw_grid()

        for row in range(ROWS):
            for col in range(COLS):
                cell = self.board[row][col]
                x = col * COL_SIZE + COL_SIZE // 2 + OFFSET
                y = row * ROW_SIZE + ROW_SIZE // 2 + OFFSET

                if cell.atom_count == 1:
                    arcade.draw_circle_filled(x, y, 6, arcade.color.GRAY)
                if cell.atom_count == 2:
                    arcade.draw_circle_filled(x - 10, y, 6, arcade.color.GRAY)
                    arcade.draw_circle_filled(x + 10, y, 6, arcade.color.GRAY)
                if cell.atom_count == 3:
                    arcade.draw_circle_filled(x - 10, y - 10, 6, arcade.color.GRAY)
                    arcade.draw_circle_filled(x + 10, y - 10, 6, arcade.color.GRAY)
                    arcade.draw_circle_filled(x, y + 10, 6, arcade.color.GRAY)
                if cell.atom_count == 4:
                    arcade.draw_circle_filled(x - 10, y - 10, 6, arcade.color.GRAY)
                    arcade.draw_circle_filled(x + 10, y - 10, 6, arcade.color.GRAY)
                    arcade.draw_circle_filled(x - 10, y + 10, 6, arcade.color.GRAY)
                    arcade.draw_circle_filled(x + 10, y + 10, 6, arcade.color.GRAY)



class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.atom_count = 0

    def add_atom(self):
        if self.atom_count < 4:
            self.atom_count += 1



if __name__ == "__main__":
    game = ChainReactionGame()
    game.setup()
    arcade.run()
