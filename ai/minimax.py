"""
minimax.py — Minimax với:
  • Độ sâu tối đa = 3
  • 3 cấp độ: Easy(1), Medium(2), Hard(3)
  • Giới hạn thời gian để không bị treo
  • Iterative Deepening + TT + Quiescence
"""
import time
import random
from core.constants import RED, BLACK, EMPTY, PIECE_VALUES, PAWN
from ai.evaluation.evaluation import Evaluation
from ai.alpha_beta import _zobrist_table, _ZOBRIST_SIDE, _compute_hash

# ── 3 cấp độ tương thích ──────────────────────────────────────────────────────
MINIMAX_LEVELS = {
    "Beginner": {"depth": 1, "time_limit": 3.0},
    "Easy":     {"depth": 1, "time_limit": 3.0},
    "Medium":   {"depth": 2, "time_limit": 5.0},
    "Hard":     {"depth": 3, "time_limit": 10.0},
    "Master":   {"depth": 3, "time_limit": 10.0},
}
MAX_DEPTH = 3   # giới hạn cứng


class Minimax:
    INF = 10**9

    def __init__(self, move_generator, max_depth=2, time_limit=5.0):
        self.move_generator = move_generator
        # Giới hạn depth tối đa là 3
        self.max_depth  = min(max_depth, MAX_DEPTH)
        self.time_limit = time_limit

        self.tt          = {}
        self.max_tt_size = 100_000

        # Time control
        self.start_time  = 0.0
        self.stop_search = False

        # Stats — đồng bộ với AlphaBeta để left_panel đọc được
        self.node_count      = 0
        self.pruned_count    = 0
        self.tt_hits         = 0
        self.best_score      = 0
        self.best_move_found = None
        self.search_depth    = 0

    def set_history(self, history):
        """Minimax không dùng history — giữ để tương thích AIPlayer."""
        pass

    def set_difficulty(self, difficulty_name: str):
        """Cập nhật depth + time_limit theo tên cấp độ."""
        preset = MINIMAX_LEVELS.get(difficulty_name, MINIMAX_LEVELS["Medium"])
        self.max_depth  = preset["depth"]
        self.time_limit = preset["time_limit"]

    def _time_up(self) -> bool:
        return (time.perf_counter() - self.start_time) >= self.time_limit

    # =========================================================================
    # PUBLIC
    # =========================================================================

    def get_best_move(self, board, color):
        # Reset stats + timer
        self.node_count      = 0
        self.pruned_count    = 0
        self.tt_hits         = 0
        self.best_score      = 0
        self.best_move_found = None
        self.search_depth    = 0
        self.stop_search     = False
        self.candidate_moves = []   # list of (move, score) top-5
        self.start_time      = time.perf_counter()

        root_hash = _compute_hash(board, color)
        moves     = self.move_generator.get_all_moves(color)
        if not moves:
            return None

        best_move  = moves[0]
        best_score = -self.INF if color == RED else self.INF

        # Iterative Deepening — tối đa MAX_DEPTH = 3
        for depth in range(1, self.max_depth + 1):
            if self._time_up():
                break

            tt_move       = self._get_tt_move(root_hash)
            ordered_moves = self._order_moves(board, moves, color, tt_move)

            cur_best_moves = []
            cur_best_score = -self.INF if color == RED else self.INF

            for move in ordered_moves:
                if self._time_up():
                    self.stop_search = True
                    break

                new_hash = self._move_hash(root_hash, board, move, color)
                board.make_move(move)
                score = self._minimax(board, new_hash, depth - 1, -color)
                board.undo_move()

                if self.stop_search:
                    break

                if color == RED:
                    if score > cur_best_score:
                        cur_best_score = score
                        cur_best_moves = [move]
                    elif score == cur_best_score:
                        cur_best_moves.append(move)
                else:
                    if score < cur_best_score:
                        cur_best_score = score
                        cur_best_moves = [move]
                    elif score == cur_best_score:
                        cur_best_moves.append(move)

            # Chỉ cập nhật nếu depth này hoàn thành (không bị timeout giữa chừng)
            if not self.stop_search and cur_best_moves:
                best_score = cur_best_score
                best_move  = random.choice(cur_best_moves)
                self._store_tt(root_hash, depth, best_score, best_move)
                self.best_score      = best_score
                self.best_move_found = best_move
                self.search_depth    = depth

        # Lưu top-5 candidate moves cho MatchRecord
        self.candidate_moves = []
        for mv, sc in sorted(
            [(mv, -sc if color == BLACK else sc)
             for mv, sc in zip(ordered_moves[:6], [0]*6)],
            key=lambda x: x[1], reverse=True
        ):
            if mv != best_move and len(self.candidate_moves) < 5:
                self.candidate_moves.append((mv, sc))

        return best_move

    # =========================================================================
    # MINIMAX RECURSIVE
    # =========================================================================

    def _minimax(self, board, current_hash, depth, color):
        if self._time_up():
            self.stop_search = True
            return Evaluation.evaluate(board, self.move_generator.game_manager)

        self.node_count += 1

        # TT probe
        entry = self.tt.get(current_hash)
        if entry is not None and entry["depth"] >= depth:
            self.tt_hits += 1
            return entry["score"]

        if depth == 0:
            return self._quiescence(board, current_hash, color, max_ply=2)

        moves = self.move_generator.get_all_moves(color)
        if not moves:
            return Evaluation.evaluate(board, self.move_generator.game_manager)

        tt_move = self._get_tt_move(current_hash)
        moves   = self._order_moves(board, moves, color, tt_move)

        if color == RED:
            best_score = -self.INF
            best_move  = None
            for move in moves:
                if self._time_up():
                    self.stop_search = True
                    break
                new_hash = self._move_hash(current_hash, board, move, color)
                board.make_move(move)
                score = self._minimax(board, new_hash, depth - 1, BLACK)
                board.undo_move()
                if score > best_score:
                    best_score = score
                    best_move  = move
        else:
            best_score = self.INF
            best_move  = None
            for move in moves:
                if self._time_up():
                    self.stop_search = True
                    break
                new_hash = self._move_hash(current_hash, board, move, color)
                board.make_move(move)
                score = self._minimax(board, new_hash, depth - 1, RED)
                board.undo_move()
                if score < best_score:
                    best_score = score
                    best_move  = move

        if not self.stop_search:
            self._store_tt(current_hash, depth, best_score, best_move)
        return best_score

    # =========================================================================
    # QUIESCENCE — giới hạn max_ply = 2 để tránh stack overflow
    # =========================================================================

    def _quiescence(self, board, current_hash, color, max_ply=2):
        if max_ply <= 0 or self._time_up():
            return Evaluation.evaluate(board, self.move_generator.game_manager)

        self.node_count += 1
        stand_pat = Evaluation.evaluate(board, self.move_generator.game_manager)

        tactical = self._get_tactical_moves(board, color)
        if not tactical:
            return stand_pat

        tactical = self._order_moves(board, tactical, color)

        if color == RED:
            best = stand_pat
            for move in tactical:
                if self._time_up(): break
                new_hash = self._move_hash(current_hash, board, move, color)
                board.make_move(move)
                score = self._quiescence(board, new_hash, BLACK, max_ply - 1)
                board.undo_move()
                best = max(best, score)
            return best
        else:
            best = stand_pat
            for move in tactical:
                if self._time_up(): break
                new_hash = self._move_hash(current_hash, board, move, color)
                board.make_move(move)
                score = self._quiescence(board, new_hash, RED, max_ply - 1)
                board.undo_move()
                best = min(best, score)
            return best

    def _get_tactical_moves(self, board, color):
        tactical = []
        for move in self.move_generator.get_all_moves(color):
            if move.is_capture():
                tactical.append(move); continue
            board.make_move(move)
            gives_check = self.move_generator.game_manager.is_in_check(-color)
            board.undo_move()
            if gives_check:
                tactical.append(move)
        return tactical

    # =========================================================================
    # MOVE ORDERING
    # =========================================================================

    def _order_moves(self, board, moves, color, tt_move=None):
        def score(move):
            if tt_move is not None and move == tt_move:
                return 10_000_000
            s  = 0
            cp = move.piece_captured
            mp = move.piece_moved
            if cp != EMPTY:
                s += 10_000 + PIECE_VALUES.get(cp.piece_type, 0) * 20 \
                            - PIECE_VALUES.get(mp.piece_type, 1)
            s += (4 - abs(move.end_col - 4)) * 8
            if mp.piece_type == PAWN:
                if (mp.color == RED   and move.end_row <= 4) or \
                   (mp.color == BLACK and move.end_row >= 5):
                    s += 30
            return s
        return sorted(moves, key=score, reverse=True)

    # =========================================================================
    # ZOBRIST HASH — O(1) per move
    # =========================================================================

    def _move_hash(self, old_hash, board, move, color) -> int:
        h  = old_hash
        mp = move.piece_moved
        h ^= _zobrist_table[(move.start_row, move.start_col, mp.piece_type, mp.color)]
        cp = move.piece_captured
        if cp != EMPTY:
            h ^= _zobrist_table[(move.end_row, move.end_col, cp.piece_type, cp.color)]
        h ^= _zobrist_table[(move.end_row, move.end_col, mp.piece_type, mp.color)]
        h ^= _ZOBRIST_SIDE
        return h

    # =========================================================================
    # TRANSPOSITION TABLE
    # =========================================================================

    def _store_tt(self, h, depth, score, best_move):
        existing = self.tt.get(h)
        if existing is not None and existing["depth"] > depth:
            return
        if len(self.tt) >= self.max_tt_size:
            to_del = [k for k,v in self.tt.items() if v["depth"] <= 1]
            for k in to_del[:self.max_tt_size // 10]:
                del self.tt[k]
            if len(self.tt) >= self.max_tt_size:
                self.tt.clear()
        self.tt[h] = {"depth": depth, "score": score, "best_move": best_move}

    def _get_tt_move(self, h):
        entry = self.tt.get(h)
        return entry["best_move"] if entry else None