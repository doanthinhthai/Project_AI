import random
from core.constants import RED, BLACK
from ai.evaluation import Evaluation


class AlphaBeta:
    def __init__(self, move_generator, max_depth=3):
        self.move_generator = move_generator
        self.max_depth = max_depth

    def get_best_move(self, board, color):
        alpha = float("-inf")
        beta = float("inf")
        moves = self.move_generator.get_all_moves(color)

        if not moves:
            return None

        best_moves = []

        if color == RED:
            best_score = float("-inf")

            for move in moves:
                board.make_move(move)
                score = self.search(
                    board,
                    self.max_depth - 1,
                    alpha,
                    beta,
                    maximizing_player=False
                )
                board.undo_move()

                if score > best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

                alpha = max(alpha, best_score)

        else:  # BLACK
            best_score = float("inf")

            for move in moves:
                board.make_move(move)
                score = self.search(
                    board,
                    self.max_depth - 1,
                    alpha,
                    beta,
                    maximizing_player=True
                )
                board.undo_move()

                if score < best_score:
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

                beta = min(beta, best_score)

        return random.choice(best_moves) if best_moves else None

    def search(self, board, depth, alpha, beta, maximizing_player):
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
                eval_score = self.search(board, depth - 1, alpha, beta, False)
                board.undo_move()

                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)

                if beta <= alpha:
                    break

            return max_eval

        else:
            min_eval = float("inf")

            for move in moves:
                board.make_move(move)
                eval_score = self.search(board, depth - 1, alpha, beta, True)
                board.undo_move()

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                if beta <= alpha:
                    break

            return min_eval