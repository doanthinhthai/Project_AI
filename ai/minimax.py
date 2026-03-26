from core.constants import RED, BLACK
from ai.evaluation import Evaluation


class Minimax:
    def __init__(self, move_generator, max_depth=3):
        self.move_generator = move_generator
        self.max_depth = max_depth

    def get_best_move(self, board, color):
        best_move = None

        if color == RED:
            best_score = float("-inf")
            moves = self.move_generator.get_all_moves(color)

            for move in moves:
                board.make_move(move)
                score = self.minimax(board, self.max_depth - 1, float("-inf"), float("inf"), False)
                board.undo_move()

                if score > best_score:
                    best_score = score
                    best_move = move

        else:  # BLACK
            best_score = float("inf")
            moves = self.move_generator.get_all_moves(color)

            for move in moves:
                board.make_move(move)
                score = self.minimax(board, self.max_depth - 1, float("-inf"), float("inf"), True)
                board.undo_move()

                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return Evaluation.evaluate(board)

        color = RED if maximizing_player else BLACK
        moves = self.move_generator.get_all_moves(color)

        if not moves:
            return Evaluation.evaluate(board)

        if maximizing_player:
            max_eval = float("-inf")

            for move in moves:
                board.make_move(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
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
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.undo_move()

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)

                if beta <= alpha:
                    break

            return min_eval