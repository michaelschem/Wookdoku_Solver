import random
from unittest import TestCase

from models import Board, Piece, Solver, seed_pieces
# from pieces import pieces

class TestBoard(TestCase):

    def setUp(self):
        self.board = Board()
        piece = Piece(blocks=[(0, 0), (0, 1)])
        self.board.add(piece, (2, 2))
        piece = Piece(blocks=[(0, 0), (0, 1), (1, 1)])
        self.board.add(piece, (4, 4))

    def test_can_add(self):
        # In bounds piece
        piece = Piece(blocks=[(0, 0), (0, 1)])
        self.assertFalse(self.board.can_add(piece, (2, 2)))

        # Out of bounds piece
        piece = Piece(blocks=[(0, 100), (0, 100)])
        self.assertFalse(self.board.can_add(piece, (2, 2)))

    def test_score(self):
        print(self.board.score())
        piece = Piece(blocks=[(0, 0), (0, 1)])
        self.board.add(piece, [6,4])
        print(self.board.score())


class TestPieces(TestCase):
    def setUp(self) -> None:
        self.piece = Piece(blocks=[(0, 0), (0, 1)])

    def test_print(self):
        for piece in Piece.get_all_pieces():
            print('----------')
            print(piece.blocks)
            print(piece)

    def test_rotate(self):
        piece = seed_pieces[1]
        piece.rotate(90)


class TestSolver(TestCase):
    def setUp(self) -> None:
        self.board = Board()

    def test_get_best_spot(self):
        solver = Solver(self.board)
        for piece in Piece.get_all_pieces():
            get_possible_places = solver.get_possible_places(piece)
            scores = solver.scores(get_possible_places, piece)
            spot = solver.get_best_spot(scores)
            print(spot)
            self.board.add(piece, spot)
            print(self.board)

