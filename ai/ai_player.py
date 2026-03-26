from game.rules import Rules
from ai.move_generator import MoveGenerator
from ai.minimax import Minimax
from ai.alpha_beta import AlphaBeta


class AIPlayer:
    def __init__(self, board, game_manager, algorithm="alpha_beta", max_depth=3):
        self.board = board
        self.game_manager = game_manager
        self.rules = Rules(board)
        self.move_generator = MoveGenerator(board, self.rules, game_manager)

        if algorithm == "minimax":
            self.engine = Minimax(self.move_generator, max_depth=max_depth)
        else:
            self.engine = AlphaBeta(self.move_generator, max_depth=max_depth)

    def get_best_move(self, board, color):
        return self.engine.get_best_move(board, color)