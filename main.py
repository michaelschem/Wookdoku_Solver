from models import *
from pieces import seed_pieces

if __name__ == '__main__':
    print('Woodoku')
    clears = None
    board = Board()
    solver = Solver(board)
    piece_bag = PieceBag(seed_pieces)
    # Piece.print_options()

    moves = 0
    clears_count = [0,0,0]
    while True:
        moves += 1
        # piece_offset = int(input("Piece: "))
        piece = piece_bag.get_piece()
        possible_places = solver.get_possible_places(piece)
        scores = solver.scores(possible_places, piece, piece_bag)
        print(piece)
        if len(scores) == 0:
            break
        spot = solver.get_best_spot(scores)
        print(spot)
        # clears = [c+clears[i] for i,c in enumerate(clears)]
        board.add(piece, spot)
        print(board)
        board.clear()
        print(board)
    print(f"Lost after {moves} moves.")
    print(f"Clears: {clears_count}.")