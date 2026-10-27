"""Sprites and explosion animation for a Board, at any position and cell size."""
import math

import arcade
from PIL import Image, ImageDraw

from constants import (ATOM_RADIUS, ATOM_SPREAD, CELL_COLOR, CELL_GAP, CELL_RADIUS, CELL_SIZE, FLIGHT_TIME,
                       PLAYER_COLORS, SPIN_SPEED)
from ui_theme import lerp

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


class BoardSprites:
    def __init__(self, board, left, bottom, cell_size=CELL_SIZE, gap=CELL_GAP, tile_color=CELL_COLOR):
        self.board = board
        self.cell_size = cell_size
        self.gap = gap
        self.tile_color = tile_color
        self.scale = cell_size / CELL_SIZE
        self.time = 0.0
        self.flights = []
        self.flight_time = 0.0
        self.highlight = None  # (cell, player): tile tinted in that player's colour

        self.tiles = arcade.SpriteList()
        for _ in range(board.rows * board.cols):
            self.tiles.append(arcade.Sprite(TILE_TEXTURE, scale=self.scale / SUPERSAMPLE))
        self.atoms = arcade.SpriteList()
        self.flying = arcade.SpriteList()
        self.move_to(left, bottom)
        self.sync()

    @property
    def height(self):
        return self.board.rows * (self.cell_size + self.gap) - self.gap

    @property
    def animating(self):
        return bool(self.flights)

    def move_to(self, left, bottom):
        self.left, self.bottom = left, bottom
        for i, tile in enumerate(self.tiles):
            tile.position = self.cell_center(*divmod(i, self.board.cols))

    # Row 0 is the top row.
    def cell_center(self, row, col):
        step = self.cell_size + self.gap
        return (self.left + col * step + self.cell_size / 2,
                self.bottom + self.height - row * step - self.cell_size / 2)

    def cell_at(self, x, y):
        step = self.cell_size + self.gap
        col, dx = divmod(x - self.left, step)
        row, dy = divmod(self.bottom + self.height - y, step)
        if 0 <= row < self.board.rows and 0 <= col < self.board.cols and dx < self.cell_size and dy < self.cell_size:
            return int(row), int(col)
        return None

    def atom_sprite(self, player):
        sprite = arcade.Sprite(ATOM_TEXTURE, scale=self.scale / SUPERSAMPLE)
        sprite.color = PLAYER_COLORS[player]
        return sprite

    def sync(self):
        """Rebuild atom sprites and tile tints from the board state."""
        board = self.board
        self.atoms.clear()
        for r in range(board.rows):
            for c in range(board.cols):
                count = board.count[r][c]
                for _ in range(count):
                    atom = self.atom_sprite(board.owner[r][c])
                    atom.properties.update(cell=(r, c), count=count, spin=count == board.capacity(r, c) - 1)
                    self.atoms.append(atom)
        self.place_atoms()
        self.tint()

    def place_atoms(self):
        index = {}
        spread = ATOM_SPREAD * self.scale
        for atom in self.atoms:
            cell, count = atom.properties["cell"], atom.properties["count"]
            angle = self.time * SPIN_SPEED if atom.properties["spin"] else math.pi / 2
            i = index[cell] = index.get(cell, -1) + 1
            x, y = self.cell_center(*cell)
            if count > 1:
                x += spread * math.cos(angle + i * 2 * math.pi / count)
                y += spread * math.sin(angle + i * 2 * math.pi / count)
            atom.position = (x, y)

    def set_highlight(self, cell=None, player=None):
        highlight = (cell, player) if cell is not None else None
        if highlight != self.highlight:
            self.highlight = highlight
            self.tint()

    def tint(self):
        # Opaque blend: an RGB colour set later keeps a sprite's old alpha, so a translucent tint would stick.
        for i, tile in enumerate(self.tiles):
            lit = self.highlight and divmod(i, self.board.cols) == self.highlight[0]
            color = lerp(self.tile_color, PLAYER_COLORS[self.highlight[1]], 0.3) if lit else self.tile_color
            tile.color = (*color, 255)

    def start_wave(self):
        """Pop every unstable cell and start flying its atoms to the neighbours."""
        self.flights = self.board.start_wave()
        self.flight_time = 0.0
        for src, _, player in self.flights:
            sprite = self.atom_sprite(player)
            sprite.position = self.cell_center(*src)  # else it is drawn at (0, 0) until the next update
            self.flying.append(sprite)
        self.sync()

    def update(self, dt):
        """Advance animations. Returns True on the frame a wave lands."""
        self.time += dt
        landed = False
        if self.flights:
            self.flight_time += dt
            t = min(self.flight_time / FLIGHT_TIME, 1.0)
            ease = 1 - (1 - t) ** 3
            for sprite, (src, dst, _) in zip(self.flying, self.flights):
                (x0, y0), (x1, y1) = self.cell_center(*src), self.cell_center(*dst)
                sprite.position = (x0 + (x1 - x0) * ease, y0 + (y1 - y0) * ease)
            if t >= 1.0:
                self.board.land(self.flights)
                self.flights = []
                self.flying.clear()
                self.sync()
                landed = True
        self.place_atoms()
        return landed

    def draw(self):
        self.tiles.draw()
        self.atoms.draw()
        self.flying.draw()
