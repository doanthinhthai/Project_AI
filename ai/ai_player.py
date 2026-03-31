import time
from game.rules import Rules
from ai.move_generator import MoveGenerator
from ai.minimax import Minimax
from ai.alpha_beta import AlphaBeta


class AIPlayer:
    def __init__(self, board, game_manager, algorithm="alpha_beta", max_depth=4):
        self.board = board
        self.game_manager = game_manager
        self.rules = Rules(board)
        self.move_generator = MoveGenerator(board, self.rules, game_manager)
        self.algorithm = algorithm
        self.max_depth = max_depth
        self.last_think_time = 0.0

        if algorithm == "minimax":
            self.engine = Minimax(self.move_generator, max_depth=max_depth)
        else:
            self.engine = AlphaBeta(
                self.move_generator,
                max_depth=max_depth,
                time_limit=30.0
            )

    def get_best_move(self, board, color,history=None):
        start = time.perf_counter()
        if history:
            self.engine.set_history(history)
        else:
            self.engine.set_history([])
        move = self.engine.get_best_move(board, color)
        end = time.perf_counter()
        self.last_think_time = end - start
        return move