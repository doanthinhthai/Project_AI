"""
alpha_beta.py — Negamax Alpha-Beta với:
  • Zobrist hashing (thay tuple-string → tăng tốc ~5-10x)
  • Repetition detection đúng (list + đếm >= 2 trong search stack)
  • PVS, LMR, Null-Move Pruning, Aspiration Window
  • Killer moves, History heuristic, TT với depth-replace
"""
import time
import random
from core.constants import RED, BLACK, EMPTY, PIECE_VALUES, KING, PAWN, BOARD_ROWS, BOARD_COLS
from ai.evaluation.evaluation import Evaluation

# =============================================================================
# ZOBRIST TABLE — khởi tạo một lần khi import
# =============================================================================
_PIECE_TYPES = ["K", "A", "E", "R", "N", "C", "P"]
_COLORS      = [1, -1]   # RED=1, BLACK=-1

_zobrist_table: dict = {}
_rng = random.Random(20250401)   # seed cố định → reproducible

for _r in range(BOARD_ROWS):
    for _c in range(BOARD_COLS):
        for _pt in _PIECE_TYPES:
            for _col in _COLORS:
                _zobrist_table[(_r, _c, _pt, _col)] = _rng.getrandbits(64)

_ZOBRIST_SIDE = _rng.getrandbits(64)   # XOR khi đổi lượt


def _compute_hash(board, color: int) -> int:
    """Tính Zobrist hash từ đầu. Chỉ dùng lúc khởi tạo."""
    h = 0
    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            p = board.board[r][c]
            if p != EMPTY:
                h ^= _zobrist_table[(r, c, p.piece_type, p.color)]
    if color == BLACK:
        h ^= _ZOBRIST_SIDE
    return h


class AlphaBeta:
    EXACT      = 0
    LOWERBOUND = 1
    UPPERBOUND = 2

    INF              = 10**9
    MATE_SCORE       = 10**7
    NULL_MOVE_REDUCTION = 2

    def __init__(self, move_generator, max_depth=4, time_limit=30.0):
        self.move_generator = move_generator
        self.max_depth  = max_depth
        self.time_limit = time_limit

        # Transposition Table  {hash → entry}
        self.tt          = {}
        self.max_tt_size = 300_000

        # Search stats — đọc từ left_panel sau mỗi lần tìm
        self.node_count      = 0   # tổng node đã visit
        self.pruned_count    = 0   # số nhánh bị cắt (beta cutoff)
        self.best_score      = 0   # điểm đánh giá tốt nhất
        self.best_move_found = None  # nước đi tốt nhất
        self.search_depth    = 0   # depth thực tế đã hoàn thành
        self.tt_hits         = 0   # số lần TT hit

        # Killer moves
        self.killer_moves = {}

        # History heuristic
        self.history_table = {}

        # Time control
        self.start_time  = 0.0
        self.stop_search = False

        # Lịch sử ván thực: list of hash (giữ số lần để đếm)
        self.game_history: list = []

        # Search stack: list of hash (path hiện tại đang tìm)
        self.search_stack: list = []

    # =========================================================================
    # PUBLIC
    # =========================================================================

    def set_history(self, history):
        """
        Nhận lịch sử từ bên ngoài.
        history: list of board-key strings (từ game_manager.board_history).
        Ta convert sang list of int bằng hash() để so sánh O(1).
        """
        self.game_history = [hash(h) for h in history]

    def get_best_move(self, board, color):
        self.node_count      = 0
        self.pruned_count    = 0
        self.tt_hits         = 0
        self.best_score      = 0
        self.best_move_found = None
        self.search_depth    = 0
        self.stop_search     = False
        self.candidate_moves = []   # list of (move, score) top-5
        self.start_time      = time.perf_counter()
        self.search_stack.clear()
        self.killer_moves.clear()
        # Giữ history_table giữa các lần tìm (cho phép học tích luỹ)

        # Tính hash ban đầu
        root_hash = _compute_hash(board, color)

        root_moves = self.move_generator.get_all_moves(color)
        if not root_moves:
            return None

        tt_move    = self._get_tt_move(root_hash)
        root_moves = self._order_moves(board, root_moves, color, 0, tt_move)

        best_move  = root_moves[0]
        best_score = -self.INF

        for depth in range(1, self.max_depth + 1):
            if self._time_up():
                break

            # Aspiration window
            if best_score != -self.INF:
                w = 50
                asp_a, asp_b = best_score - w, best_score + w
            else:
                asp_a, asp_b = -self.INF, self.INF

            cur_best_score = -self.INF
            cur_best_move  = None

            tt_move    = self._get_tt_move(root_hash)
            ord_moves  = self._order_moves(board, root_moves, color, 0, tt_move)

            for i, move in enumerate(ord_moves):
                if self._time_up():
                    self.stop_search = True
                    break

                new_hash = self._move_hash(root_hash, board, move, color)
                board.make_move(move)
                self.search_stack.append(new_hash)

                if i == 0:
                    score = -self._search(board, new_hash, depth-1, -asp_b, -asp_a, -color, ply=1)
                else:
                    score = -self._search(board, new_hash, depth-1, -(asp_a+1), -asp_a, -color, ply=1)
                    if not self.stop_search and asp_a < score < asp_b:
                        score = -self._search(board, new_hash, depth-1, -asp_b, -asp_a, -color, ply=1)

                self.search_stack.pop()
                board.undo_move()

                if self.stop_search:
                    break

                if score > cur_best_score:
                    cur_best_score = score
                    cur_best_move  = move
                if score > asp_a:
                    asp_a = score

            # Aspiration fail → re-search full window
            if (not self.stop_search and cur_best_move is not None
                    and best_score != -self.INF
                    and abs(cur_best_score - best_score) > 50):
                cur_best_score = -self.INF
                cur_best_move  = None
                for i, move in enumerate(ord_moves):
                    if self._time_up():
                        self.stop_search = True; break
                    new_hash = self._move_hash(root_hash, board, move, color)
                    board.make_move(move)
                    self.search_stack.append(new_hash)
                    if i == 0:
                        score = -self._search(board, new_hash, depth-1, -self.INF, self.INF, -color, ply=1)
                    else:
                        score = -self._search(board, new_hash, depth-1, -(cur_best_score if cur_best_score > -self.INF else self.INF)+1,
                                              -(cur_best_score if cur_best_score > -self.INF else self.INF), -color, ply=1)
                        if not self.stop_search and score > (cur_best_score if cur_best_score > -self.INF else -self.INF):
                            score = -self._search(board, new_hash, depth-1, -self.INF, -cur_best_score, -color, ply=1)
                    self.search_stack.pop()
                    board.undo_move()
                    if self.stop_search: break
                    if score > cur_best_score:
                        cur_best_score = score; cur_best_move = move

            if not self.stop_search and cur_best_move is not None:
                best_score = cur_best_score
                best_move  = cur_best_move
                self.best_score      = best_score
                self.best_move_found = best_move
                self.search_depth    = depth
                self._store_tt(root_hash, depth, best_score, self.EXACT, best_move)
                root_moves = self._order_moves(board, root_moves, color, 0, best_move)

        # Lưu top-5 candidate moves cho MatchRecord
        self.candidate_moves = []
        for mv in root_moves[:6]:
            if mv != best_move:
                entry_tt = self.tt.get(self._move_hash(root_hash, board, mv, color))
                s = entry_tt["score"] if entry_tt else 0
                self.candidate_moves.append((mv, s))
                if len(self.candidate_moves) >= 5:
                    break

        return best_move

    # =========================================================================
    # NEGAMAX SEARCH
    # =========================================================================

    def _search(self, board, current_hash, depth, alpha, beta, color, ply):
        # ── Repetition check (dùng hash, O(1) cho game_history) ─────────────
        if ply > 0:
            # Lặp trong nhánh search hiện tại → hoà (tránh vòng lặp vô tận)
            if self.search_stack.count(current_hash) >= 2:
                return 0
            # Lặp với lịch sử ván thực ≥ 2 lần trước → hoà
            if self.game_history.count(current_hash) >= 2:
                return 0

        if self._time_up():
            self.stop_search = True
            return self._eval_rel(board, color)

        self.node_count += 1
        alpha_orig = alpha

        # TT probe
        tt_entry = self.tt.get(current_hash)
        tt_move  = None
        if tt_entry is not None and tt_entry["depth"] >= depth:
            self.tt_hits += 1
            flag, tt_score = tt_entry["flag"], tt_entry["score"]
            tt_move = tt_entry["best_move"]
            if flag == self.EXACT:        return tt_score
            elif flag == self.LOWERBOUND: alpha = max(alpha, tt_score)
            elif flag == self.UPPERBOUND: beta  = min(beta,  tt_score)
            if alpha >= beta:             return tt_score
        elif tt_entry is not None:
            tt_move = tt_entry["best_move"]   # dùng move dù depth thấp hơn

        if depth <= 0:
            return self._quiescence(board, current_hash, alpha, beta, color, ply)

        in_check = self.move_generator.game_manager.is_in_check(color)

        # Check extension
        if in_check:
            depth += 1

        # Null Move Pruning
        if (not in_check and depth >= 3
                and self._has_material(board, color)):
            # "null move": đổi lượt không đi (không thay đổi board hash ngoài XOR side)
            null_hash = current_hash ^ _ZOBRIST_SIDE
            self.search_stack.append(null_hash)
            null_score = -self._search(board, null_hash,
                                       depth - 1 - self.NULL_MOVE_REDUCTION,
                                       -beta, -beta+1, -color, ply+1)
            self.search_stack.pop()
            if self.stop_search: return null_score
            if null_score >= beta: return null_score

        moves = self.move_generator.get_all_moves(color)
        if not moves:
            return (-self.MATE_SCORE + ply) if in_check else 0

        moves = self._order_moves(board, moves, color, ply, tt_move)

        best_score = -self.INF
        best_move  = None

        for i, move in enumerate(moves):
            if self._time_up():
                self.stop_search = True; break

            is_cap    = move.is_capture()
            is_killer = self._is_killer(ply, move)
            reduction = 0

            # LMR
            if (depth >= 3 and i >= 4 and not in_check
                    and not is_cap and not is_killer):
                reduction = 1 if i < 10 else 2

            new_hash = self._move_hash(current_hash, board, move, color)
            board.make_move(move)
            self.search_stack.append(new_hash)

            if i == 0:
                score = -self._search(board, new_hash, depth-1, -beta, -alpha, -color, ply+1)
            else:
                if reduction > 0:
                    score = -self._search(board, new_hash, depth-1-reduction,
                                          -(alpha+1), -alpha, -color, ply+1)
                    if not self.stop_search and score > alpha:
                        score = -self._search(board, new_hash, depth-1,
                                              -(alpha+1), -alpha, -color, ply+1)
                else:
                    score = -self._search(board, new_hash, depth-1,
                                          -(alpha+1), -alpha, -color, ply+1)
                if not self.stop_search and alpha < score < beta:
                    score = -self._search(board, new_hash, depth-1,
                                          -beta, -alpha, -color, ply+1)

            self.search_stack.pop()
            board.undo_move()

            if self.stop_search: break

            if score > best_score:
                best_score = score; best_move = move
            if score > alpha:
                alpha = score
            if alpha >= beta:
                self.pruned_count += 1
                if not is_cap:
                    self._add_killer(ply, move)
                    self._upd_history(color, move, depth)
                break

        if self.stop_search:
            return best_score if best_score != -self.INF else self._eval_rel(board, color)

        flag = (self.EXACT if alpha_orig < best_score < beta
                else self.LOWERBOUND if best_score >= beta
                else self.UPPERBOUND)
        self._store_tt(current_hash, depth, best_score, flag, best_move)
        return best_score

    # =========================================================================
    # QUIESCENCE
    # =========================================================================

    def _quiescence(self, board, current_hash, alpha, beta, color, ply):
        if self._time_up():
            self.stop_search = True
            return self._eval_rel(board, color)

        self.node_count += 1
        stand_pat = self._eval_rel(board, color)

        if stand_pat >= beta: return stand_pat
        if stand_pat > alpha: alpha = stand_pat

        captures = [m for m in self.move_generator.get_all_moves(color) if m.is_capture()]
        if not captures:
            return alpha

        captures = self._order_moves(board, captures, color, ply, None)

        for move in captures:
            if self._time_up():
                self.stop_search = True; break

            new_hash = self._move_hash(current_hash, board, move, color)
            board.make_move(move)
            self.search_stack.append(new_hash)
            score = -self._quiescence(board, new_hash, -beta, -alpha, -color, ply+1)
            self.search_stack.pop()
            board.undo_move()

            if self.stop_search: break
            if score >= beta:    return score
            if score > alpha:    alpha = score

        return alpha

    # =========================================================================
    # ZOBRIST INCREMENTAL UPDATE
    # =========================================================================

    def _move_hash(self, old_hash: int, board, move, color: int) -> int:
        """
        Tính hash sau khi thực hiện `move` mà KHÔNG thay đổi board.
        Incremental XOR → O(1) thay vì O(90).
        """
        h = old_hash

        # Xoá quân đang di chuyển khỏi ô cũ
        mp = move.piece_moved
        h ^= _zobrist_table[(move.start_row, move.start_col, mp.piece_type, mp.color)]

        # Xoá quân bị ăn (nếu có)
        cp = move.piece_captured
        if cp != EMPTY:
            h ^= _zobrist_table[(move.end_row, move.end_col, cp.piece_type, cp.color)]

        # Đặt quân di chuyển lên ô mới
        h ^= _zobrist_table[(move.end_row, move.end_col, mp.piece_type, mp.color)]

        # Đổi lượt
        h ^= _ZOBRIST_SIDE

        return h

    # =========================================================================
    # MOVE ORDERING
    # =========================================================================

    def _order_moves(self, board, moves, color, ply, tt_move):
        killers = self.killer_moves.get(ply, [])

        def score(move):
            s = 0
            if tt_move is not None and move == tt_move:
                return 10_000_000

            cp = move.piece_captured
            mp = move.piece_moved
            if cp != EMPTY:
                s += 1_000_000 + PIECE_VALUES.get(cp.piece_type, 0)*100 \
                               - PIECE_VALUES.get(mp.piece_type, 1)

            if len(killers) > 0 and move == killers[0]: s += 900_000
            elif len(killers) > 1 and move == killers[1]: s += 800_000

            hk = (color, mp.piece_type, move.end_row, move.end_col)
            s += self.history_table.get(hk, 0)

            s += (4 - abs(move.end_col - 4)) * 8
            if mp.piece_type == PAWN:
                if (mp.color == RED and move.end_row <= 4) or \
                   (mp.color == BLACK and move.end_row >= 5):
                    s += 30
            return s

        return sorted(moves, key=score, reverse=True)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _eval_rel(self, board, color):
        raw = Evaluation.evaluate(board, self.move_generator.game_manager)
        return raw if color == RED else -raw

    def _has_material(self, board, color):
        for row in board.board:
            for p in row:
                if p != EMPTY and p.color == color and p.piece_type not in (KING, PAWN):
                    return True
        return False

    def _is_killer(self, ply, move):
        return move in self.killer_moves.get(ply, [])

    def _add_killer(self, ply, move):
        k = self.killer_moves.setdefault(ply, [])
        if move in k: return
        k.insert(0, move)
        if len(k) > 2: k.pop()

    def _upd_history(self, color, move, depth):
        hk = (color, move.piece_moved.piece_type, move.end_row, move.end_col)
        self.history_table[hk] = self.history_table.get(hk, 0) + depth * depth

    # ── TT ────────────────────────────────────────────────────────────────────

    def _store_tt(self, h, depth, score, flag, best_move):
        existing = self.tt.get(h)
        if existing is not None and existing["depth"] > depth:
            return  # giữ entry chất lượng cao hơn
        if len(self.tt) >= self.max_tt_size and existing is None:
            # Xoá ~10% entry nông nhất thay vì clear toàn bộ
            to_del = sorted((k for k,v in self.tt.items() if v["depth"] <= 1),
                            key=lambda k: self.tt[k]["depth"])
            for k in to_del[:self.max_tt_size // 10]:
                del self.tt[k]
            if len(self.tt) >= self.max_tt_size:
                self.tt.clear()
        self.tt[h] = {"depth": depth, "score": score,
                      "flag": flag, "best_move": best_move}

    def _get_tt_move(self, h):
        e = self.tt.get(h)
        return e["best_move"] if e is not None else None

    # ── Time ──────────────────────────────────────────────────────────────────

    def _time_up(self):
        return (time.perf_counter() - self.start_time) >= self.time_limit