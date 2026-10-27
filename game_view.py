import math

import arcade
import arcade.gui as gui
from PIL import Image, ImageDraw

from board import Game
from constants import *
from menu_view import MenuView
from ui_theme import FONT, TITLE_FONT
from widgets import BevelButton, panel

ELIMINATED = (71, 85, 105)  # slate 600


SUPERSAMPLE = 4


def shape_texture(name, size, draw):
    """White shape rendered large so GPU downscaling smooths its edges; tint via sprite.color."""
    s = size * SUPERSAMPLE
    image = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw(ImageDraw.Draw(image), s)
    return arcade.Texture(image, hash=name)


TILE_TEXTURE = shape_texture("tile", CELL_SIZE, lambda d, s: d.rounded_rectangle(
    (0, 0, s - 1, s - 1), CELL_RADIUS * SUPERSAMPLE, fill="white"))
ATOM_TEXTURE = shape_texture("atom", ATOM_RADIUS * 2, lambda d, s: d.ellipse((0, 0, s - 1, s - 1), fill="white"))


def atom_sprite(player):
    sprite = arcade.Sprite(ATOM_TEXTURE, scale=1 / SUPERSAMPLE)
    sprite.color = PLAYER_COLORS[player]
    return sprite


def atom_offsets(count, angle):
    if count == 1:
        return [(0, 0)]
    return [(ATOM_SPREAD * math.cos(angle + i * 2 * math.pi / count),
             ATOM_SPREAD * math.sin(angle + i * 2 * math.pi / count)) for i in range(count)]


class GameView(gui.UIView):
    def __init__(self, players):
        super().__init__()
        self.players = players
        self.game = Game(players, ROWS, COLS)
        self.time = 0.0
        self.hover = None
        self.resolving = False
        self.flights = []
        self.flight_time = 0.0

        self.tiles = arcade.SpriteList()
        for r in range(ROWS):
            for c in range(COLS):
                x, y = self.cell_center(r, c)
                self.tiles.append(arcade.Sprite(TILE_TEXTURE, scale=1 / SUPERSAMPLE, center_x=x, center_y=y))
        self.atoms = arcade.SpriteList()
        self.flying = arcade.SpriteList()
        # Built up front: the winner can appear mid-chain, frames before the game-over panel.
        self.dim = arcade.SpriteList()
        self.dim.append(arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                                (*BACKGROUND, 200)))
        self.sync()
        self.build_hud()

    def build_hud(self):
        root = self.hud = self.add_widget(gui.UIAnchorLayout())
        info = gui.UIBoxLayout(space_between=8, align="left")
        self.turn_label = info.add(gui.UILabel("", font_name=FONT, font_size=20, bold=True))
        roster = info.add(gui.UIBoxLayout(vertical=False, space_between=12))
        self.roster = [roster.add(gui.UILabel(PLAYER_NAMES[p], font_name=FONT, font_size=12))
                       for p in range(self.players)]
        root.add(info, anchor_x="left", anchor_y="top", align_x=MARGIN, align_y=-MARGIN)

        side = gui.UIBoxLayout(space_between=6, align="right")
        actions = side.add(gui.UIBoxLayout(vertical=False, space_between=8))
        self.icon_buttons = []
        for icon, tooltip, action in (("restart", "Restart  R", self.restart), ("menu", "Menu  Esc", self.to_menu)):
            button = actions.add(BevelButton(icon=icon, width=42, height=42, tooltip=tooltip))
            button.on_click = lambda event, action=action: action()
            self.icon_buttons.append(button)
        self.hint = side.add(gui.UILabel("", font_name=FONT, font_size=11, text_color=MUTED_TEXT,
                                         width=150, align="right"))
        root.add(side, anchor_x="right", anchor_y="top", align_x=-MARGIN, align_y=-MARGIN + 4)
        self.update_hud()

    def update_hud(self):
        game = self.game
        player = game.turn if game.winner is None else game.winner
        self.turn_label.text = f"{PLAYER_NAMES[player]}'s turn" if game.winner is None else f"{PLAYER_NAMES[player]} wins"
        self.turn_label.update_font(font_color=PLAYER_COLORS[player])
        self.turn_label.fit_content()
        for p, label in enumerate(self.roster):
            label.update_font(font_color=PLAYER_COLORS[p] if p in game.alive else ELIMINATED)

    def show_game_over(self):
        winner = self.game.winner
        self.hud.visible = False
        overlay = gui.UIAnchorLayout()
        card = gui.UIBoxLayout(space_between=14)
        card.add(gui.UILabel(f"{PLAYER_NAMES[winner].upper()} WINS", font_name=TITLE_FONT, font_size=26,
                             text_color=PLAYER_COLORS[winner]))
        card.add(gui.UILabel("Every other atom has been captured.", font_name=FONT, font_size=12,
                             text_color=MUTED_TEXT))
        card.add(gui.UISpace(height=6))
        buttons = card.add(gui.UIBoxLayout(vertical=False, space_between=10))
        again = buttons.add(BevelButton("Play again", icon=None, width=140, height=50, variant="primary"))
        again.on_click = lambda event: self.restart()
        menu = buttons.add(BevelButton("Menu", width=110, height=50, variant="raised"))
        menu.on_click = lambda event: self.to_menu()
        overlay.add(panel(card, padding=32))
        self.add_widget(overlay)

    def restart(self):
        self.window.show_view(GameView(self.players))

    def to_menu(self):
        self.window.show_view(MenuView(self.players))

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.R:
            self.restart()
        elif symbol == arcade.key.ESCAPE:
            self.to_menu()

    # Layout: row 0 is the top row of the board.
    def cell_center(self, row, col):
        step = CELL_SIZE + CELL_GAP
        return (MARGIN + col * step + CELL_SIZE / 2,
                MARGIN + BOARD_HEIGHT - row * step - CELL_SIZE / 2)

    def cell_at(self, x, y):
        step = CELL_SIZE + CELL_GAP
        col, dx = divmod(x - MARGIN, step)
        row, dy = divmod(MARGIN + BOARD_HEIGHT - y, step)
        if 0 <= row < ROWS and 0 <= col < COLS and dx < CELL_SIZE and dy < CELL_SIZE:
            return int(row), int(col)
        return None

    @property
    def busy(self):
        return self.resolving or self.game.winner is not None

    def sync(self):
        """Rebuild atom sprites and tile tints from the board state."""
        board = self.game.board
        self.atoms.clear()
        for r in range(ROWS):
            for c in range(COLS):
                count = board.count[r][c]
                for _ in range(count):
                    atom = atom_sprite(board.owner[r][c])
                    atom.properties.update(cell=(r, c), count=count,
                                           spin=count == board.capacity(r, c) - 1)
                    self.atoms.append(atom)
        self.place_atoms()
        self.tint_tiles()

    def place_atoms(self):
        index = {}
        for atom in self.atoms:
            r, c = atom.properties["cell"]
            angle = self.time * SPIN_SPEED if atom.properties["spin"] else math.pi / 2
            i = index[(r, c)] = index.get((r, c), -1) + 1
            dx, dy = atom_offsets(atom.properties["count"], angle)[i]
            x, y = self.cell_center(r, c)
            atom.position = (x + dx, y + dy)

    def tint_tiles(self):
        # Opaque blend: an RGB colour set later keeps a sprite's old alpha, so a translucent tint would stick.
        highlight = tuple(round(c + (p - c) * 0.3) for c, p in zip(CELL_COLOR, PLAYER_COLORS[self.game.turn]))
        for i, tile in enumerate(self.tiles):
            r, c = divmod(i, COLS)
            legal = not self.busy and (r, c) == self.hover and self.game.board.can_place(r, c, self.game.turn)
            tile.color = (*(highlight if legal else CELL_COLOR), 255)

    def on_mouse_motion(self, x, y, dx, dy):
        self.hover = self.cell_at(x, y)
        self.tint_tiles()

    def on_mouse_press(self, x, y, button, modifiers):
        cell = self.cell_at(x, y)
        if cell and not self.busy and self.game.play(*cell):
            self.resolving = True
            self.sync()

    def on_update(self, delta_time):
        self.time += delta_time
        hovered = next((b.tooltip for b in self.icon_buttons if b.hovered), "")
        if self.hint.text != hovered:
            self.hint.text = hovered
        if self.flights:
            self.flight_time += delta_time
            t = min(self.flight_time / FLIGHT_TIME, 1.0)
            ease = 1 - (1 - t) ** 3
            for sprite, (src, dst, _) in zip(self.flying, self.flights):
                (x0, y0), (x1, y1) = self.cell_center(*src), self.cell_center(*dst)
                sprite.position = (x0 + (x1 - x0) * ease, y0 + (y1 - y0) * ease)
            if t >= 1.0:
                self.game.board.land(self.flights)
                self.game.update_alive()
                self.flights = []
                self.flying.clear()
                self.sync()
        elif self.resolving:
            if self.game.winner is None and self.game.board.unstable():
                self.flights = self.game.board.start_wave()
                self.flight_time = 0.0
                for src, _, player in self.flights:
                    self.flying.append(atom_sprite(player))
                self.sync()
            else:
                self.resolving = False
                self.game.end_turn()
                self.on_turn_end()
                self.tint_tiles()
        self.place_atoms()

    def on_turn_end(self):
        self.update_hud()
        if self.game.winner is not None:
            self.show_game_over()

    def on_draw_before_ui(self):
        self.tiles.draw()
        self.atoms.draw()
        self.flying.draw()
        if self.game.winner is not None:
            self.dim.draw()
