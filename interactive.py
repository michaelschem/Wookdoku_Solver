import copy

from models import *
from pieces import seed_pieces
from itertools import chain


class Game:
    def __init__(self) -> None:
        self.score = 0

    def play(self):
        board = Board()
        board_reader = BoardReader(board)
        board_reader.get_board()

        solver = Solver(board)
        piece_bag = PieceBag(seed_pieces)
        piece_bag.print_options()
        rots = [0, 90, 180, 270]

        moves = 0
        clears_count = [0,0,0]
        while True:
            last_board = copy.deepcopy(board.squares)
            moves += 1
            confirm_piece = False

            while not confirm_piece:
                piece_offset = int(input("Piece: "))
                confirm_rotation = False
                piece = piece_bag.pieces[piece_offset]
                rotation = -1
                while not confirm_rotation:
                    rotation += 1
                    piece = piece.rotate(rots[rotation % 4])
                    print(piece)
                    confirm_rotation = input("rotation good?: y/N") == "y"

                print(piece)
                confirm_piece = input('right?: Y/n') != "n"

            possible_places = solver.get_possible_places(piece)
            if len(possible_places) == 0:
                break
            self.score += len(piece.blocks)
            scores = solver.scores(possible_places, piece, piece_bag)
            # scores = {1: possible_places[0]}
            spot = solver.get_best_spot(scores)
            print(spot)
            board.add(piece, spot)

            print(board.diff(last_board))

            clears = board.clear()
            self.score += len(list(chain(*clears))) * 18
            # print(board)
        print(f"Lost after {moves} moves with score {self.score}.")

        return moves, clears_count, self.score



if __name__ == '__main__':
    max_moves = 0
    max_score = 0
    for i in range(0, 100):
        game = Game()
        moves, clears, score = game.play()
        max_moves = max(moves, max_moves)
        max_score = max(score, max_score)

    print(f"Max moves: {max_moves}")
    print(f"Max score: {max_score}")