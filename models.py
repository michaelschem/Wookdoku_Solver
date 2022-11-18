import math
import random
import cv2
import pyautogui

import numpy as np
from typing import List
from PIL import Image, ImageDraw
import pyscreenshot as ImageGrab


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

    def diff(self, other):
        string = ""
        for i, row in enumerate(self.squares):
            string += "\n"
            if i % 3 == 0:
                string += ''.join(['-' for i in range(0, self.dim + 4)])
                string += '\n'
            for j, square in enumerate(row):
                if j % 3 == 0:
                    string += '|'
                if square and other[i][j]:
                    string += "x"
                elif square:
                    string += f"{bcolors.OKGREEN}x{bcolors.ENDC}"
                else:
                    string += " "
            string += "|"
        string += '\n'
        string += ''.join(['-' for i in range(0, self.dim + 4)])
        # self._last_board = string
        return string

    def can_add(self, piece, position):
        for block in piece.blocks:
            try:
                if position[0] + block[0] < 0 or position[1] + block[1] < 0:
                    return False
                if self.squares[position[0] + block[0]][position[1] + block[1]]:
                    return False
            except IndexError:
                return False
        return True

    def add(self, piece, position):
        if not self.can_add(piece, position):
            raise RuntimeError(f"Can't add piece here, {piece} {position} {self}")
        for block in piece.blocks:
            self.squares[position[0] + block[0]][position[1] + block[1]] = True

    def remove(self, piece, position):
        for block in piece.blocks:
            self.squares[position[0] + block[0]][position[1] + block[1]] = False

    def clear(self):
        clears = self.check_for_clears()

        # Row clears
        if clears[0]:
            # print("ROW CLEAR")
            self.row_set(clears[0], False)
            # for clear in clears[0]:
            #     self.squares[clear] = [False for f in range(0, self.dim)]
        if clears[1]:
            # print("COL CLEAR")
            self.col_set(clears[1], False)

        if clears[2]:
            # print("BOX CLEAR")
            self.box_set(clears[2], False)

        return clears

    def check_for_clears(self):
        # check for row clears
        row_clears = []
        for i, row in enumerate(self.squares):
            if False not in row:
                row_clears.append(i)

        col_clears = []
        for x in range(0, self.dim):
            col = []
            for y in range(0, self.dim):
                col.append(self.squares[y][x])
            if False not in col:
                col_clears.append(x)

        box_clears = []
        for y_offset in range(0, 3):
            for x_offset in range(0, 3):
                box = []
                for y, x in self.base_box:
                    box.append(self.squares[y+y_offset*3][x+x_offset*3])
                if False not in box:
                    box_clears.append([y_offset*3, x_offset*3])

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
                self.squares[y+box_clear[0]][x+box_clear[1]] = set


class PieceBag:
    def __init__(self, pieces) -> None:
        self.pieces: List[Piece] = pieces

    def get_piece(self):
        piece_offset = random.randint(0, len(self.pieces) - 1)
        return self.pieces[piece_offset]

    @property
    def all_pieces(self):
        if hasattr(self, '_all_pieces'):
            return self._all_pieces
        all_pieces = []
        for piece in self.pieces:
            all_pieces.append(piece)
            all_pieces.append(piece.rotate(90))
            all_pieces.append(piece.rotate(180))
            all_pieces.append(piece.rotate(270))
        self._all_pieces = all_pieces
        return all_pieces

    def print_options(self):
        for i, piece in enumerate(self.pieces):
            print(i, piece)


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
        self.board: Board = board

    def get_possible_places(self, piece):
        possible_places = []
        for i, row in enumerate(self.board.squares):
            for j, square in enumerate(row):
                if self.board.can_add(piece, (i, j)):
                    possible_places.append((i, j))
        return possible_places

    def get_best_spot(self, scores):
        return scores[max(scores.keys())]

    def scores(self, possible_places, piece, piece_bag: PieceBag):
        scores = {}
        for possible_place in possible_places:
            self.board.add(piece, possible_place)
            clears = self.board.check_for_clears()

            self.board.row_set(clears[0], False)
            self.board.col_set(clears[1], False)
            self.board.box_set(clears[2], False)

            scores[self.score(piece_bag)] = possible_place

            self.board.row_set(clears[0], True)
            self.board.col_set(clears[1], True)
            self.board.box_set(clears[2], True)

            self.board.remove(piece, possible_place)
        return scores

    def score(self, piece_bag: PieceBag) -> int:
        score = 0
        for i, row in enumerate(self.board.squares):
            for j, square in enumerate(row):
                for piece in piece_bag.all_pieces:
                    if self.board.can_add(piece, [i, j]):
                        score += 1
        return score


class BoardReader:
    # Screenshot vals
    # clear_color = [[75, 36, 25], [119, 53, 39]]
    # piece_color = [198, 154, 103]

    clear_color = [[22, 16, 5], [119, 53, 39]]
    piece_color = [52, 41, 27]

    def __init__(self, board, image_path=None) -> None:
        self.board = board

        if image_path:
            self.image = Image.open(image_path, 'r')
        else:
            self.image = None

        # Screenshot vals
        # self.base = [40, 730, 140, 830]
        # self.size = 125, 125

        self.base = [90, 872]
        self.size = [50] * 2
        self.padding = 45
        self.base.extend([self.base[0] + self.size[0], self.base[1] + self.size[0]])

        self.error_threshold = 70

    def get_piece(self, color):
        if abs(np.sum(np.subtract(self.clear_color[0], color))) < self.error_threshold or \
                abs(np.sum(np.subtract(self.clear_color[1], color))) < self.error_threshold:
            return False
        if abs(np.sum(np.subtract(self.piece_color, color))) < self.error_threshold:
            return True

        raise RuntimeError("Can't resolve piece!")

    def get_screenshot(self):
        image = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imwrite("screen.png", image)
        self.image = Image.open("screen.png", 'r')

    def get_board(self):
        self.get_screenshot()

        draw = ImageDraw.Draw(self.image)
        for y in range(0, self.board.dim):
            for x in range(0, self.board.dim):
                ellipse = [self.base[0] + (y*self.size[0]) + (y*self.padding),
                               self.base[1] + (x*self.size[0]) + (x*self.padding),
                               self.base[2] + (y*self.size[0]) + (y*self.padding),
                               self.base[3] + (x*self.size[0]) + (x*self.padding)]
                pixel_sum = (0, 0, 0)
                for xp in range(ellipse[0], ellipse[2]):
                    for yp in range(ellipse[1], ellipse[3]):
                        pixel_sum = np.add(pixel_sum, self.image.getpixel((xp, yp)))
                avg_pixel = np.divide(pixel_sum, (10000, 10000, 10000))

                # draw.ellipse(ellipse)
                # self.image.save('out.png', "PNG")

                self.board.squares[x][y] = self.get_piece(avg_pixel)
        self.image.save('out.png', "PNG")

    def get_next_pieces(self):
        self.get_screenshot()
        draw = ImageDraw.Draw(self.image)
        draw.ellipse([200, 2000, 300, 2100])
        self.image.save('out.png', "PNG")

        print('')