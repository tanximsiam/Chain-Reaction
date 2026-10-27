"""Chain Reaction rules, independent of any rendering."""


class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.count = [[0] * cols for _ in range(rows)]
        self.owner = [[None] * cols for _ in range(rows)]

    def neighbors(self, row, col):
        return [(r, c) for r, c in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1))
                if 0 <= r < self.rows and 0 <= c < self.cols]

    def capacity(self, row, col):
        """Critical mass: a cell explodes once it holds this many atoms."""
        return len(self.neighbors(row, col))

    def can_place(self, row, col, player):
        return self.owner[row][col] in (None, player)

    def place(self, row, col, player):
        self.count[row][col] += 1
        self.owner[row][col] = player

    def unstable(self):
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.count[r][c] >= self.capacity(r, c)]

    def start_wave(self):
        """Pop every unstable cell at once. Returns flights (src, dst, player) still to land."""
        flights = []
        for r, c in self.unstable():
            player = self.owner[r][c]
            self.count[r][c] -= self.capacity(r, c)
            if self.count[r][c] == 0:
                self.owner[r][c] = None
            flights += [((r, c), n, player) for n in self.neighbors(r, c)]
        return flights

    def land(self, flights):
        for _, (r, c), player in flights:
            self.place(r, c, player)  # landing captures the cell

    def atoms_by_player(self):
        totals = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if self.owner[r][c] is not None:
                    totals[self.owner[r][c]] = totals.get(self.owner[r][c], 0) + self.count[r][c]
        return totals


class Game:
    """Turn order, elimination and winner on top of a Board."""

    def __init__(self, players, rows, cols):
        self.board = Board(rows, cols)
        self.players = players
        self.alive = list(range(players))
        self.moved = set()
        self.turn = 0

    @property
    def winner(self):
        return self.alive[0] if len(self.alive) == 1 else None

    def play(self, row, col):
        """Place an atom for the current player. Returns False for an illegal move."""
        if self.winner is not None or not self.board.can_place(row, col, self.turn):
            return False
        self.board.place(row, col, self.turn)
        self.moved.add(self.turn)
        return True

    def update_alive(self):
        # A player who has not moved yet cannot be eliminated.
        totals = self.board.atoms_by_player()
        self.alive = [p for p in self.alive if p not in self.moved or totals.get(p)]

    def step(self):
        """Run one explosion wave instantly. Returns False when the board has settled."""
        if self.winner is not None or not self.board.unstable():
            return False
        self.board.land(self.board.start_wave())
        self.update_alive()
        return True

    def end_turn(self):
        self.update_alive()
        if self.winner is None:
            for offset in range(1, self.players + 1):
                p = (self.turn + offset) % self.players
                if p in self.alive:
                    self.turn = p
                    break
