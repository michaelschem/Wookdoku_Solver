# from pieces import pieces
import math
import random
import numpy as np


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Board:
    dim = 9
    base_box = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

    def __init__(self):
        self.squares = np.array([[False for f in range(0, self.dim)] for f in range(0, self.dim)])

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        string = ""
        for i, row in enumerate(self.squares):
            string += "\n"
            if i % 3 == 0:
                string += ''.join(['-' for i in range(0, self.dim + 4)])
                string += '\n'
            for j, square in enumerate(row):
                if j % 3 == 0:
                    string += '|'
                string += "x" if square else " "
            string += "|"
        string += '\n'
        string += ''.join(['-' for i in range(0, self.dim + 4)])
        # self._last_board = string
        return string

    def can_add(self, piece, position):
        for block in piece.blocks:
            try:
                if position[0] + block[0] <= -1 or position[1] + block[1] <= -1:
                    return False
                if self.squares[position[0] + block[0]][position[1] + block[1]]:
                    return False
            except IndexError:
                return False
        return True

    def add(self, piece, position):
        if not self.can_add(piece, position):
            raise RuntimeError("Can't add piece here")
        for block in piece.blocks:
            self.squares[position[0] + block[0]][position[1] + block[1]] = True

        # Row clears
        if clears and clears[0]:
            # print("ROW CLEAR")
            self.row_set(clears[0], False)
            # for clear in clears[0]:
            #     self.squares[clear] = [False for f in range(0, self.dim)]
        if clears and clears[1]:
            # print("COL CLEAR")
            self.col_set(clears[1], False)

        if clears and clears[2]:
            # print("BOX CLEAR")
            self.box_set(clears[2], False)

    def remove(self, piece, position):
        for block in piece.blocks:
            self.squares[position[0] + block[0]][position[1] + block[1]] = False

    def check_for_clears(self):
        # check for row clears
        row_clears = []
        for i, row in enumerate(self.squares):
            if False not in row:
                row_clears.append(i)

        col_clears = []
        for col in range(0, self.dim):
            col = [i[col] for i in self.squares]
            if False not in col:
                col_clears.append(i)

        box_clears = []
        box = []
        for y_offset in range(0, 2):
            for x_offset in range(0, 2):
                for x,y in self.base_box:
                    box.append(self.squares[x+x_offset][y+y_offset])
                if False not in box:
                    box_clears.append([y_offset, x_offset])

        return [row_clears, col_clears, box_clears]

    def row_set(self, row_clears, set):
        for row_clear in row_clears:
            self.squares[row_clear] = [set for x in range(0, self.dim)]

    def col_set(self, col_clears, set):
        for col_clear in col_clears:
            for row in self.squares:
                row[col_clear] = set

    def box_set(self, box_clears, set):
        for box_clear in box_clears:
            for y, x in self.base_box:
                self.squares[y+box_clear[0]][x+box_clears[1]] = set


class Piece:
    def __init__(self, blocks=None):
        self.blocks = blocks

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        # string = f"{self.blocks}"
        string = ""
        for i in range(int(-Board.dim/2), int(Board.dim/2)):
            string += "\n"
            for j in range(int(-Board.dim/2), int(Board.dim/2)):
                if (i, j) in self.blocks:
                    string += "x"
                else:
                    string += " "

        return string

    @classmethod
    def print_options(cls):
        for i, piece in enumerate(cls.get_all_pieces()):
            print(i, piece)

    @classmethod
    def get_all_pieces(cls):
        all_pieces = []
        for piece in seed_pieces:
            all_pieces.append(piece)
            all_pieces.append(piece.rotate(90))
            all_pieces.append(piece.rotate(180))
            all_pieces.append(piece.rotate(270))
        return all_pieces

    def rotate(self, angle=90):
        angle = math.radians(angle)

        points = []
        for px, py in self.blocks:
            qx = math.cos(angle) * px - math.sin(angle) * py
            qy = math.sin(angle) * px + math.cos(angle) * py
            points.append((int(round(qx, 4)), int(round(qy, 4))))
        return Piece(points)


class Solver:

    def __init__(self, board) -> None:
        self.board = board

    def get_possible_places(self, piece):
        possible_places = []
        for i, row in enumerate(self.board.squares):
            for j, square in enumerate(row):
                if self.board.can_add(piece, (i, j)):
                    possible_places.append((i, j))
        return possible_places

    def get_best_spot(self, scores):
        return scores[max(scores.keys())]

    def scores(self, possible_places, piece):
        scores = {}
        for possible_place in possible_places:
            self.board.add(piece, possible_place)
            clears = self.board.check_for_clears()

            self.board.row_set(clears[0], False)
            self.board.col_set(clears[1], False)
            self.board.box_set(clears[2], False)

            scores[self.score()] = possible_place, clears

            self.board.row_set(clears[0], True)
            self.board.col_set(clears[1], True)
            self.board.box_set(clears[2], True)

            self.board.remove(piece, possible_place)
        return scores

    def score(self) -> int:
        score = 0
        for i, row in enumerate(self.board.squares):
            for j, square in enumerate(row):
                for piece in Piece.get_all_pieces():
                    if self.board.can_add(piece, [i, j]):
                        score += 1
        return score

seed_pieces = [
    # x
    Piece([(0,0)]),

    # xx
    Piece([(0,0), (0,1)]),

    # xxx
    Piece([(0,0), (0,1), (0,2)]),

    # xxxx
    Piece([(0,0), (0,1), (0,2), (0,3)]),

    # xxxxx
    Piece([(0,0), (0,1), (0,2), (0,3), (0,4)]),

    # xxx
    # x
    Piece([(0,0), (0,1), (0,2), (1,0)]),

    # xxx
    #   x
    Piece([(0,0), (0,1), (0,2), (1,2)]),

    # xx
    # x
    Piece([(0,0), (0,1), (1,0)]),

    # xxx
    # x x
    Piece([(0,0), (0,1), (0,2), (1,0), (1,2)]),

    # xx
    # xx
    Piece([(0,0), (0,1), (1,0), (1,1)]),

    # x
    #  x
    Piece([(0,0), (1,1)]),

    # x
    #  x
    #   x
    Piece([(0,0), (1,1), (2,2), (3,3)]),

    # x
    #  x
    #   x
    #    x
    Piece([(0,0), (1,1), (2,2), (3,3), (4,4)]),

    # x
    # xxx
    # x
    Piece([(0,0), (1,0), (1,1), (1,2), (2,0)]),

    # x
    # xx
    # x
    Piece([(0,0), (1,0), (1,1), (2,0)]),

    # xx
    #  xx
    Piece([(0,0), (0,1), (1,1), (1,2)]),

    #  xx
    # xx
    Piece([(0,1), (0,2), (1,0), (1,1)]),

    # xxx
    # x
    # x
    Piece([(0,0), (0,1), (0,2), (1,0), (2,0)]),
]


if __name__ == '__main__':
    print('Woodoku')
    clears = None
    board = Board()
    solver = Solver(board)
    pieces = Piece.get_all_pieces()
    # Piece.print_options()

    moves = 0
    clears_count = [0,0,0]
    while True:
        moves += 1
        # piece_offset = int(input("Piece: "))
        piece_offset = random.randint(0, len(pieces)-1)
        piece = pieces[piece_offset]
        possible_places = solver.get_possible_places(piece)
        scores = solver.scores(possible_places, piece)
        print(piece)
        if len(scores) == 0:
            break
        spot, clears = solver.get_best_spot(scores)
        clears = [c+clears[i] for i,c in enumerate(clears)]
        board.add(piece, spot)
        print(board)
    print(f"Lost after {moves} moves.")
    print(f"Clears: {clears_count}.")


