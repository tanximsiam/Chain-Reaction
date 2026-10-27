import arcade
import arcade.gui as gui

from board import Board
from board_sprites import BoardSprites
from constants import BACKGROUND, MARGIN, MUTED_TEXT
from ui_theme import FONT, TEXT, TITLE_FONT
from widgets import BevelButton, panel

TEXT_WIDTH = 360
SECTIONS = [
    ("Goal", "Capture every atom on the board. The last player with atoms wins."),
    ("Your turn", "Click an empty cell or one of your own to add an atom. "
                  "Cells owned by other players are off limits."),
    ("Critical mass", "A cell explodes when it holds as many atoms as it has neighbours: "
                      "2 in a corner, 3 on an edge, 4 in the middle."),
    ("Chain reactions", "An explosion sends one atom to each neighbour and makes those cells yours. "
                        "Neighbours that fill up explode too."),
    ("Elimination", "After your first move, losing all your atoms knocks you out."),
    ("Keys", "R restart   ·   Esc pause or back"),
]

RED, BLUE = 0, 1
DEMO_CELL, DEMO_GAP = 32, 3
DEMO_SIZE = 3 * DEMO_CELL + 2 * DEMO_GAP
# caption, starting atoms (row, col, player, count), scripted moves (row, col, player)
DEMOS = [
    ("Critical mass", [], [(0, 0, RED), (0, 0, RED), (1, 1, RED), (1, 1, RED), (1, 1, RED), (1, 1, RED)]),
    ("Capture", [(0, 0, RED, 1), (0, 1, BLUE, 2), (1, 0, BLUE, 1), (1, 1, BLUE, 1)], [(0, 0, RED)]),
    ("Chain", [(0, 0, RED, 1), (0, 1, RED, 2), (0, 2, BLUE, 1), (1, 1, BLUE, 3), (1, 2, BLUE, 2), (2, 1, BLUE, 1)],
     [(0, 0, RED)]),
]
CUE_TIME, END_TIME, MAX_WAVES = 0.8, 1.6, 12


class Demo:
    """Loops scripted moves on a tiny board with the real rules and animation."""

    def __init__(self, setup, moves):
        self.setup, self.moves = setup, moves
        self.sprites = None
        self.reset()

    def reset(self):
        board = Board(3, 3)
        for r, c, player, count in self.setup:
            for _ in range(count):
                board.place(r, c, player)
        left, bottom = (self.sprites.left, self.sprites.bottom) if self.sprites else (0, 0)
        self.sprites = BoardSprites(board, left, bottom, cell_size=DEMO_CELL, gap=DEMO_GAP,
                                    tile_color=BACKGROUND)  # darker wells: panel is CELL_COLOR
        self.step, self.timer, self.waves = 0, 0.0, 0

    def update(self, dt):
        sprites = self.sprites
        sprites.update(dt)
        if sprites.animating:
            return
        if sprites.board.unstable() and self.waves < MAX_WAVES:
            sprites.start_wave()
            self.waves += 1
            return
        self.timer += dt
        if self.step < len(self.moves):
            r, c, player = self.moves[self.step]
            sprites.set_highlight((r, c), player)  # cue the cell, like a hover, before "clicking" it
            if self.timer > CUE_TIME:
                sprites.board.place(r, c, player)
                sprites.set_highlight()
                sprites.sync()
                self.step, self.timer, self.waves = self.step + 1, 0.0, 0
        elif self.timer > END_TIME:
            self.reset()


def demo_row(demos):
    """Placeholders the demo boards are drawn over, each with a caption."""
    row = gui.UIBoxLayout(vertical=False, space_between=24)
    slots = []
    for caption, setup, moves in DEMOS:
        column = row.add(gui.UIBoxLayout(space_between=6))
        slots.append(column.add(gui.UISpace(width=DEMO_SIZE, height=DEMO_SIZE)))
        column.add(gui.UILabel(caption, font_name=FONT, font_size=11, text_color=MUTED_TEXT))
        demos.append(Demo(setup, moves))
    return row, slots


class ManualView(gui.UIView):
    """How to play. Returns to `back_to` (the menu or a game in progress)."""

    def __init__(self, back_to):
        super().__init__()
        self.back_to = back_to

        content = gui.UIBoxLayout(space_between=14, align="left")
        for title, body in SECTIONS:
            section = gui.UIBoxLayout(space_between=4, align="left")
            section.add(gui.UILabel(title, font_name=FONT, font_size=13, bold=True, text_color=TEXT))
            section.add(gui.UILabel(body, font_name=FONT, font_size=12, text_color=MUTED_TEXT,
                                    multiline=True, width=TEXT_WIDTH))
            content.add(section)
            if title == "Chain reactions":
                self.demos = []
                row, self.slots = demo_row(self.demos)
                content.add(row)

        root = self.add_widget(gui.UIAnchorLayout())
        header = gui.UIBoxLayout(vertical=False, space_between=14)
        back = header.add(BevelButton(icon="back", width=42, height=42, tooltip="Back  Esc"))
        back.on_click = lambda event: self.back()
        header.add(gui.UILabel("HOW TO PLAY", font_name=TITLE_FONT, font_size=20, text_color=TEXT))
        root.add(header, anchor_x="left", anchor_y="top", align_x=MARGIN, align_y=-MARGIN + 4)
        root.add(panel(content, padding=20), anchor_y="top", align_y=-90)

    def on_update(self, delta_time):
        for demo in self.demos:
            demo.update(delta_time)

    def on_draw_after_ui(self):
        # Sprites go over the panel, so they follow wherever the layout put each placeholder.
        for demo, slot in zip(self.demos, self.slots):
            if (demo.sprites.left, demo.sprites.bottom) != (slot.rect.left, slot.rect.bottom):
                demo.sprites.move_to(slot.rect.left, slot.rect.bottom)
            demo.sprites.draw()

    def back(self):
        self.window.show_view(self.back_to)

    def on_key_press(self, symbol, modifiers):
        if symbol in (arcade.key.ESCAPE, arcade.key.BACKSPACE):
            self.back()
