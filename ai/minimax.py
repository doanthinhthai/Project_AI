import random
from core.constants import RED, BLACK, EMPTY, PIECE_VALUES
from ai.evaluation.evaluation import Evaluation


class Minimax:
    def __init__(self, move_generator, max_depth=3):
        self.move_generator = move_generator
        self.max_depth = max_depth
        self.tt = {}
        self.max_tt_size = 100000

    def get_best_move(self, board, color):
        moves = self.move_generator.get_all_moves(color)
        if not moves:
            return None

        best_move = None
        best_score = float("-inf") if color == RED else float("inf")

        # Iterative Deepening
        for depth in range(1, self.max_depth + 1):
            tt_move = self._get_tt_move(board, color)
            ordered_moves = self._order_moves(board, moves, color, tt_move=tt_move)

            current_best_moves = []
            current_best_score = float("-inf") if color == RED else float("inf")

            for move in ordered_moves:
                board.make_move(move)
                score = self.minimax(board, depth - 1, -color)
                board.undo_move()

                if color == RED:
                    if score > current_best_score:
                        current_best_score = score
                        current_best_moves = [move]
                    elif score == current_best_score:
                        current_best_moves.append(move)
                else:
                    if score < current_best_score:
                        current_best_score = score
                        current_best_moves = [move]
                    elif score == current_best_score:
                        current_best_moves.append(move)

            if current_best_moves:
                best_score = current_best_score
                best_move = random.choice(current_best_moves)
                self._store_tt(board, color, depth, best_score, best_move)

        return best_move

    def minimax(self, board, depth, color):
        tt_entry = self._probe_tt(board, color, depth)
        if tt_entry is not None:
            return tt_entry["score"]

        if depth == 0:
            return self.quiescence(board, color)

        moves = self.move_generator.get_all_moves(color)
        if not moves:
            return Evaluation.evaluate(board, self.move_generator.game_manager)

        tt_move = self._get_tt_move(board, color)
        moves = self._order_moves(board, moves, color, tt_move=tt_move)

        if color == RED:
            best_score = float("-inf")
            best_move = None

            for move in moves:
                board.make_move(move)
                score = self.minimax(board, depth - 1, BLACK)
                board.undo_move()

                if score > best_score:
                    best_score = score
                    best_move = move

            self._store_tt(board, color, depth, best_score, best_move)
            return best_score

        else:
            best_score = float("inf")
            best_move = None

            for move in moves:
                board.make_move(move)
                score = self.minimax(board, depth - 1, RED)
                board.undo_move()

                if score < best_score:
                    best_score = score
                    best_move = move

            self._store_tt(board, color, depth, best_score, best_move)
            return best_score

    def quiescence(self, board, color):
        stand_pat = Evaluation.evaluate(board, self.move_generator.game_manager)
        tactical_moves = self._get_tactical_moves(board, color)

        if not tactical_moves:
            return stand_pat

        tactical_moves = self._order_moves(board, tactical_moves, color)

        if color == RED:
            best_score = stand_pat
            for move in tactical_moves:
                board.make_move(move)
                score = self.quiescence(board, BLACK)
                board.undo_move()
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = stand_pat
            for move in tactical_moves:
                board.make_move(move)
                score = self.quiescence(board, RED)
                board.undo_move()
                best_score = min(best_score, score)
            return best_score

    def _get_tactical_moves(self, board, color):
        moves = self.move_generator.get_all_moves(color)
        tactical = []

        for move in moves:
            if move.is_capture():
                tactical.append(move)
                continue

            board.make_move(move)
            gives_check = self.move_generator.game_manager.is_in_check(-color)
            board.undo_move()

            if gives_check:
                tactical.append(move)

        return tactical

    def _order_moves(self, board, moves, color, tt_move=None):
        def score_move(move):
            score = 0

            if tt_move is not None and move == tt_move:
                score += 1_000_000

            moved_piece = move.piece_moved
            captured_piece = move.piece_captured

            if captured_piece != EMPTY:
                victim_value = PIECE_VALUES.get(captured_piece.piece_type, 0)
                attacker_value = PIECE_VALUES.get(moved_piece.piece_type, 1)
                score += 10000 + victim_value * 20 - attacker_value

            center_bonus = 4 - abs(move.end_col - 4)
            score += center_bonus * 8

            if moved_piece.piece_type == "P":
                if (moved_piece.color == RED and move.end_row <= 4) or (
                    moved_piece.color == BLACK and move.end_row >= 5
                ):
                    score += 30

            board.make_move(move)
            if self.move_generator.game_manager.is_in_check(-color):
                score += 500
            board.undo_move()

            return score

        return sorted(moves, key=score_move, reverse=True)

    def _board_key(self, board, color):
        state = [color]
        for row in board.board:
            for piece in row:
                if piece == EMPTY:
                    state.append(".")
                else:
                    state.append(f"{piece.color}{piece.piece_type}")
        return tuple(state)

    def _probe_tt(self, board, color, depth):
        key = self._board_key(board, color)
        entry = self.tt.get(key)

        if entry is None:
            return None
        if entry["depth"] < depth:
            return None

        return entry

    def _store_tt(self, board, color, depth, score, best_move):
        if len(self.tt) > self.max_tt_size:
            self.tt.clear()

        key = self._board_key(board, color)
        self.tt[key] = {
            "depth": depth,
            "score": score,
            "best_move": best_move,
        }

    def _get_tt_move(self, board, color):
        key = self._board_key(board, color)
        entry = self.tt.get(key)

        if entry is None:
            return None

        return entry.get("best_move")