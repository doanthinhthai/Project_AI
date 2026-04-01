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
            # Minimax tối đa depth 3
            capped_depth = min(max_depth, 3)
            self.engine = Minimax(self.move_generator,
                                  max_depth=capped_depth,
                                  time_limit=10.0)
        else:
            self.engine = AlphaBeta(
                self.move_generator,
                max_depth=max_depth,
                time_limit=30.0
            )

    def set_difficulty(self, difficulty_name: str):
        """Cập nhật depth + time_limit theo tên cấp độ."""
        from core.constants import DIFFICULTY_LEVELS, DIFFICULTY_TIME, DIFFICULTY_LEVELS_MINIMAX
        if self.algorithm == "minimax":
            preset = DIFFICULTY_LEVELS_MINIMAX.get(
                difficulty_name,
                {"depth": 2, "time_limit": 5.0}
            )
            self.engine.max_depth  = preset["depth"]
            self.engine.time_limit = preset["time_limit"]
            self.max_depth = preset["depth"]
        else:
            self.engine.max_depth  = DIFFICULTY_LEVELS.get(difficulty_name, 4)
            self.engine.time_limit = DIFFICULTY_TIME.get(difficulty_name, 10.0)
            self.max_depth = self.engine.max_depth

    def get_best_move(self, board, color, history=None):
        start = time.perf_counter()
        self.engine.set_history(history or [])
        move = self.engine.get_best_move(board, color)
        end  = time.perf_counter()
        self.last_think_time = end - start
        return move

    def get_candidates(self, color) -> list:
        """
        Trả về list CandidateMove từ lần tìm kiếm vừa xong.
        Gọi sau get_best_move().
        """
        from game.match_record import CandidateMove, build_notation
        raw = getattr(self.engine, "candidate_moves", [])
        result = []
        for mv, score in raw:
            c = CandidateMove(
                move     = mv,
                score    = score,
                notation = build_notation(mv, color),
            )
            result.append(c)
        return result