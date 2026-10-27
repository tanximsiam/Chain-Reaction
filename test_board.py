import unittest

from board import Board, Game


def play(game, row, col):
    assert game.play(row, col)
    while game.step():
        pass
    game.end_turn()


class BoardTest(unittest.TestCase):
    def test_capacity(self):
        b = Board(9, 6)
        self.assertEqual(b.capacity(0, 0), 2)
        self.assertEqual(b.capacity(0, 3), 3)
        self.assertEqual(b.capacity(4, 3), 4)

    def test_corner_explosion_captures_neighbors(self):
        b = Board(3, 3)
        b.place(0, 1, 1)
        b.place(0, 0, 0)
        b.place(0, 0, 0)
        b.land(b.start_wave())
        self.assertEqual(b.count[0][0], 0)
        self.assertIsNone(b.owner[0][0])
        self.assertEqual((b.count[0][1], b.owner[0][1]), (2, 0))
        self.assertEqual((b.count[1][0], b.owner[1][0]), (1, 0))


class GameTest(unittest.TestCase):
    def test_illegal_move_on_opponent_cell(self):
        g = Game(2, 3, 3)
        play(g, 1, 1)
        self.assertFalse(g.play(1, 1))

    def test_turns_rotate(self):
        g = Game(3, 5, 5)
        self.assertEqual(g.turn, 0)
        play(g, 0, 0)
        self.assertEqual(g.turn, 1)
        play(g, 4, 4)
        self.assertEqual(g.turn, 2)

    def test_elimination_and_winner(self):
        g = Game(2, 3, 3)
        play(g, 0, 0)  # p0
        play(g, 0, 1)  # p1
        play(g, 0, 0)  # p0 corner explodes, captures p1's only cell
        self.assertEqual(g.winner, 0)

    def test_unmoved_player_survives(self):
        g = Game(3, 3, 3)
        play(g, 0, 0)
        self.assertEqual(g.alive, [0, 1, 2])

    def test_chain_terminates_when_one_player_owns_board(self):
        g = Game(2, 2, 2)
        play(g, 0, 0)
        play(g, 1, 1)
        play(g, 0, 1)
        play(g, 1, 0)
        play(g, 0, 0)  # ends with every cell at critical mass; must stop at the winner
        self.assertEqual(g.winner, 0)
        self.assertTrue(g.board.unstable())


if __name__ == "__main__":
    unittest.main()
