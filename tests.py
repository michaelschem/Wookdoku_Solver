import random
from unittest import TestCase

from models import Board, Piece, Solver, BoardReader
from pieces import seed_pieces


class TestBoard(TestCase):

    def setUp(self):
        self.board = Board()
        self.solver = Solver(self.board)

    def test_can_add(self):
        piece = Piece(blocks=[(0, 0), (0, 1)])
        self.board.add(piece, (2, 2))
        piece = Piece(blocks=[(0, 0), (0, 1), (1, 1)])
        self.board.add(piece, (4, 4))

        # In bounds piece
        piece = Piece(blocks=[(0, 0), (0, 1)])
        self.assertFalse(self.board.can_add(piece, (2, 2)))

        # Out of bounds piece
        piece = Piece(blocks=[(0, 100), (0, 100)])
        self.assertFalse(self.board.can_add(piece, (2, 2)))

    def test_score(self):
        piece = Piece(blocks=[(0, 0), (0, 1)])
        self.board.add(piece, (2, 2))
        piece = Piece(blocks=[(0, 0), (0, 1), (1, 1)])
        self.board.add(piece, (4, 4))

        print(self.board.score())
        piece = Piece(blocks=[(0, 0), (0, 1)])
        self.board.add(piece, [6,4])
        print(self.board.score())

    def test_box_clear(self):
        box = Piece(Board.base_box)

        for y in [0, 3, 6]:
            for x in [0, 3, 6]:
                print(y,x)
                self.board.add(box, (y, x))
                print(self.board)
                clears = self.board.check_for_clears()
                self.board.box_set(clears[2], False)
                self.assertNotIn(True, self.board.squares)

    def test_row_clear(self):
        row = Piece([(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8)])

        for y in range(0,9):
            print(y)
            self.board.add(row, (y, 0))
            print(self.board)
            clears = self.board.check_for_clears()
            self.board.row_set(clears[0], False)
            self.assertNotIn(True, self.board.squares)

    def test_col_clear(self):
        col = Piece([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0)])

        for x in range(0,9):
            print(x)
            self.board.add(col, (0, x))
            print(self.board)
            clears = self.board.check_for_clears()
            self.board.col_set(clears[1], False)
            self.assertNotIn(True, self.board.squares)

    def test_bug_1(self):
        self.board.squares = [
            #  0      1      2      3      4     5      6      7       8
            [False, False, False,   False, False, True,    True,  True,  True, ],# 0
            [False, False, False,   False, True,  False,   True,  True,  True, ],# 1
            [False, False, False,   False, False, True,    True,  False, True, ],# 2

            [False, False, False,   False, False, False,   True,  False, True, ],# 3
            [False, False, False,   False, True,  True,    True,  True,  True, ],# 4
            [False, False, False,   False, True,  True,    True,  True,  True, ],# 5

            [False, False, False,   False, True,  True,    True,  True,  True, ],# 6
            [False, False, False,   False, False, True,    True,  False, True, ],# 7
            [False, False, False,   False, False, True,    False, False, True, ]]# 8
        places = self.solver.get_possible_places(Piece([(0,0)]))

        print('')



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


class TestImageReader(TestCase):
    def test_board_reading(self):
        board = Board()
        image_reader = BoardReader(None, board)
        image_reader.get_board()

    def test_next_pieces_reading(self):
        board = Board()
        image_reader = BoardReader(None, board)
        image_reader.get_next_pieces()
