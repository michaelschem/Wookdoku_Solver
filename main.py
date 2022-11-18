import copy

from models import *
from pieces import seed_pieces
from itertools import chain


class Game:
    def __init__(self) -> None:
        self.score = 0

    def play(self):
        # print('Woodoku')
        clears = None
        board = Board()
        solver = Solver(board)
        piece_bag = PieceBag(seed_pieces)
        # Piece.print_options()
        bonus = [10, 20, 30, 40, 50, 60, 70, 80, 90]

        moves = 0
        clears_count = [0,0,0]
        while True:
            last_board = copy.deepcopy(board.squares)
            moves += 1
            piece = piece_bag.get_piece()
            # print(piece)
            possible_places = solver.get_possible_places(piece)
            if len(possible_places) == 0:
                break
            self.score += len(piece.blocks)
            scores = solver.scores(possible_places, piece, piece_bag)
            # scores = {1: possible_places[0]}
            spot = solver.get_best_spot(scores)
            # print(spot)
            board.add(piece, spot)
            print(board.diff(last_board))
            clears = board.clear()
            self.score += bonus[len(list(chain(*clears)))]
            # print(board)

        score_file = open('scores.txt', 'a')
        score_file.writelines(f"Lost after {moves} moves with score {self.score}. ")
        score_file.close()

        return moves, clears_count, self.score


if __name__ == '__main__':
    max_moves = 0
    max_score = 0
    for i in range(0, 10000):
        game = Game()
        moves, clears, score = game.play()
        max_moves = max(moves, max_moves)
        max_score = max(score, max_score)

        score_file = open('scores.txt', 'a')
        score_file.writelines(f" Best {max_score}, {max_moves}\n")
        score_file.close()

    score_file = open('scores.txt', 'a')
    score_file.write(f"Max moves: {max_moves}")
    score_file.write(f"Max score: {max_score}")