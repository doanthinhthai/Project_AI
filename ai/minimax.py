import random
from core.constants import RED, BLACK
from ai.evaluation import Evaluation


class Minimax:
    def __init__(self, move_generator, max_depth=3):
        self.move_generator = move_generator
        self.max_depth = max_depth

    def get_best_move(self, board, color):
        moves = self.move_generator.get_all_moves(color)

        if not moves:
            return None

        best_moves = []

        if color == RED:
            best_score = float("-inf")

            for move in moves:
                board.make_move(move)
                score = self.minimax(
                    board,
                    self.max_depth - 1,
                    maximizing_player=False
                )
                board.undo_move()

                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

        else:  # BLACK
            best_score = float("inf")

            for move in moves:
                board.make_move(move)
                score = self.minimax(
                    board,
                    self.max_depth - 1,
                    maximizing_player=True
                )
                board.undo_move()

                if score < best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

        return random.choice(best_moves) if best_moves else None

    def minimax(self, board, depth, maximizing_player):
        if depth == 0:
            return Evaluation.evaluate(board, self.move_generator.game_manager)

        color = RED if maximizing_player else BLACK
        moves = self.move_generator.get_all_moves(color)

        if not moves:
            return Evaluation.evaluate(board, self.move_generator.game_manager)

        if maximizing_player:
            max_eval = float("-inf")

            for move in moves:
                board.make_move(move)
                eval_score = self.minimax(board, depth - 1, False)
                board.undo_move()

                max_eval = max(max_eval, eval_score)

            return max_eval

        else:
            min_eval = float("inf")

            for move in moves:
                board.make_move(move)
                eval_score = self.minimax(board, depth - 1, True)
                board.undo_move()

                min_eval = min(min_eval, eval_score)

            return min_eval