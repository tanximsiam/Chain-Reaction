SCREEN_TITLE = "Chain Reaction"

ROWS = 9
COLS = 6
CELL_SIZE = 64
CELL_GAP = 6
CELL_RADIUS = 12
ATOM_RADIUS = 10
ATOM_SPREAD = 11  # distance of each atom from the cell centre when a cell holds 2+
MARGIN = 24
HUD_HEIGHT = 96

BOARD_WIDTH = COLS * CELL_SIZE + (COLS - 1) * CELL_GAP
BOARD_HEIGHT = ROWS * CELL_SIZE + (ROWS - 1) * CELL_GAP
SCREEN_WIDTH = BOARD_WIDTH + 2 * MARGIN
SCREEN_HEIGHT = BOARD_HEIGHT + 2 * MARGIN + HUD_HEIGHT

FLIGHT_TIME = 0.2  # seconds for one explosion wave
SPIN_SPEED = 3.0  # radians/second for cells one atom from exploding

# Tailwind slate
BACKGROUND = (15, 23, 42)
CELL_COLOR = (30, 41, 59)
MUTED_TEXT = (148, 163, 184)

# Tailwind 500/400 hues, readable on slate 900
PLAYER_COLORS = [
    (239, 68, 68),    # red
    (59, 130, 246),   # blue
    (34, 197, 94),    # green
    (250, 204, 21),   # yellow
    (168, 85, 247),   # purple
    (236, 72, 153),   # pink
    (34, 211, 238),   # cyan
    (249, 115, 22),   # orange
]
PLAYER_NAMES = ["Red", "Blue", "Green", "Yellow", "Purple", "Pink", "Cyan", "Orange"]
