import time
from core.constants import RED, BLACK, EMPTY, PIECE_VALUES, KING, PAWN
from ai.evaluation.evaluation import Evaluation


class AlphaBeta:
    EXACT = 0
    LOWERBOUND = 1
    UPPERBOUND = 2

    INF = 10**9
    MATE_SCORE = 10**7
    NULL_MOVE_REDUCTION = 2

    def __init__(self, move_generator, max_depth=4, time_limit=30.0):
        self.move_generator = move_generator
        self.max_depth = max_depth
        self.time_limit = time_limit

        # Transposition Table
        self.tt = {}
        self.max_tt_size = 200000

        # Search stats
        self.node_count = 0

        # Killer moves: mỗi ply giữ 2 killer tốt nhất
        self.killer_moves = {}

        # History heuristic: {(color, piece_type, end_row, end_col): score}
        self.history_table = {}

        # Time control
        self.start_time = 0.0
        self.stop_search = False

    # =========================
    # PUBLIC API
    # =========================
    def get_best_move(self, board, color):
        self.node_count = 0
        self.stop_search = False
        self.start_time = time.perf_counter()

        best_move = None
        best_score = -self.INF

        root_moves = self.move_generator.get_all_moves(color)
        if not root_moves:
            return None

        tt_move = self._get_tt_move(board, color)
        root_moves = self._order_moves(
            board=board,
            moves=root_moves,
            color=color,
            ply=0,
            tt_move=tt_move,
        )

        completed_depth_best_move = root_moves[0]

        for depth in range(1, self.max_depth + 1):
            if self._time_up():
                break

            alpha = -self.INF
            beta = self.INF
            current_best_score = -self.INF
            current_best_move = None

            tt_move = self._get_tt_move(board, color)
            ordered_moves = self._order_moves(
                board=board,
                moves=root_moves,
                color=color,
                ply=0,
                tt_move=tt_move,
            )

            for i, move in enumerate(ordered_moves):
                if self._time_up():
                    self.stop_search = True
                    break

                board.make_move(move)

                if i == 0:
                    score = -self.search(
                        board=board,
                        depth=depth - 1,
                        alpha=-beta,
                        beta=-alpha,
                        color=-color,
                        ply=1,
                        allow_null=True,
                    )
                else:
                    score = -self.search(
                        board=board,
                        depth=depth - 1,
                        alpha=-(alpha + 1),
                        beta=-alpha,
                        color=-color,
                        ply=1,
                        allow_null=True,
                    )

                    if not self.stop_search and alpha < score < beta:
                        score = -self.search(
                            board=board,
                            depth=depth - 1,
                            alpha=-beta,
                            beta=-alpha,
                            color=-color,
                            ply=1,
                            allow_null=True,
                        )

                board.undo_move()

                if self.stop_search:
                    break

                if score > current_best_score:
                    current_best_score = score
                    current_best_move = move

                if score > alpha:
                    alpha = score

            # Chỉ cập nhật kết quả nếu depth này chạy xong trọn vẹn
            if not self.stop_search and current_best_move is not None:
                best_move = current_best_move
                best_score = current_best_score
                completed_depth_best_move = current_best_move

                self._store_tt(
                    board=board,
                    color=color,
                    depth=depth,
                    score=current_best_score,
                    flag=self.EXACT,
                    best_move=current_best_move,
                )

                # Sắp xếp root cho depth sau theo PV move
                root_moves = self._order_moves(
                    board=board,
                    moves=root_moves,
                    color=color,
                    ply=0,
                    tt_move=current_best_move,
                )
            else:
                break

        return best_move if best_move is not None else completed_depth_best_move

    # =========================
    # NEGAMAX + ALPHA-BETA + PVS + LMR
    # =========================
    def search(self, board, depth, alpha, beta, color, ply=0, allow_null=True):
        if self._time_up():
            self.stop_search = True
            return self._evaluate_relative(board, color)

        self.node_count += 1
        alpha_orig = alpha

        # TT probe
        tt_entry = self._probe_tt(board, color, depth)
        if tt_entry is not None:
            flag = tt_entry["flag"]
            tt_score = tt_entry["score"]

            if flag == self.EXACT:
                return tt_score
            elif flag == self.LOWERBOUND:
                alpha = max(alpha, tt_score)
            elif flag == self.UPPERBOUND:
                beta = min(beta, tt_score)

            if alpha >= beta:
                return tt_score

        # Depth 0 -> quiescence
        if depth <= 0:
            return self.quiescence(board, alpha, beta, color, ply)

        in_check = self.move_generator.game_manager.is_in_check(color)

        # Nếu đang bị chiếu thì nới thêm 1 ply
        if in_check:
            depth += 1

        # Null Move Pruning
        if (
            allow_null
            and depth >= 3
            and not in_check
            and self._has_enough_material_for_null(board, color)
        ):
            reduction = self.NULL_MOVE_REDUCTION
            null_score = -self.search(
                board=board,
                depth=depth - 1 - reduction,
                alpha=-beta,
                beta=-beta + 1,
                color=-color,
                ply=ply + 1,
                allow_null=False,
            )
            if self.stop_search:
                return null_score
            if null_score >= beta:
                return null_score

        moves = self.move_generator.get_all_moves(color)

        if not moves:
            if in_check:
                return -self.MATE_SCORE + ply
            return 0

        tt_move = tt_entry["best_move"] if tt_entry is not None else None
        moves = self._order_moves(
            board=board,
            moves=moves,
            color=color,
            ply=ply,
            tt_move=tt_move,
        )

        best_score = -self.INF
        best_move = None

        for i, move in enumerate(moves):
            if self._time_up():
                self.stop_search = True
                break

            is_capture = move.is_capture()
            is_killer = self._is_killer(ply, move)
            reduction = 0

            # LMR nhẹ:
            # giảm depth cho late quiet moves không quan trọng
            if (
                depth >= 3
                and i >= 4
                and not in_check
                and not is_capture
                and not is_killer
                and tt_move is not None
                and move != tt_move
            ):
                reduction = 1

            board.make_move(move)

            if i == 0:
                score = -self.search(
                    board=board,
                    depth=depth - 1,
                    alpha=-beta,
                    beta=-alpha,
                    color=-color,
                    ply=ply + 1,
                    allow_null=True,
                )
            else:
                # Late Move Reduction search trước
                if reduction > 0:
                    score = -self.search(
                        board=board,
                        depth=depth - 1 - reduction,
                        alpha=-(alpha + 1),
                        beta=-alpha,
                        color=-color,
                        ply=ply + 1,
                        allow_null=True,
                    )

                    if not self.stop_search and score > alpha:
                        score = -self.search(
                            board=board,
                            depth=depth - 1,
                            alpha=-(alpha + 1),
                            beta=-alpha,
                            color=-color,
                            ply=ply + 1,
                            allow_null=True,
                        )
                else:
                    score = -self.search(
                        board=board,
                        depth=depth - 1,
                        alpha=-(alpha + 1),
                        beta=-alpha,
                        color=-color,
                        ply=ply + 1,
                        allow_null=True,
                    )

                if not self.stop_search and alpha < score < beta:
                    score = -self.search(
                        board=board,
                        depth=depth - 1,
                        alpha=-beta,
                        beta=-alpha,
                        color=-color,
                        ply=ply + 1,
                        allow_null=True,
                    )

            board.undo_move()

            if self.stop_search:
                break

            if score > best_score:
                best_score = score
                best_move = move

            if score > alpha:
                alpha = score

            if alpha >= beta:
                if not is_capture:
                    self._add_killer_move(ply, move)
                    self._update_history(color, move, depth)
                break

        if self.stop_search:
            return best_score if best_score != -self.INF else self._evaluate_relative(board, color)

        flag = self.EXACT
        if best_score <= alpha_orig:
            flag = self.UPPERBOUND
        elif best_score >= beta:
            flag = self.LOWERBOUND

        self._store_tt(
            board=board,
            color=color,
            depth=depth,
            score=best_score,
            flag=flag,
            best_move=best_move,
        )

        return best_score

    # =========================
    # QUIESCENCE
    # =========================
    def quiescence(self, board, alpha, beta, color, ply=0):
        if self._time_up():
            self.stop_search = True
            return self._evaluate_relative(board, color)

        self.node_count += 1

        stand_pat = self._evaluate_relative(board, color)

        if stand_pat >= beta:
            return stand_pat
        if stand_pat > alpha:
            alpha = stand_pat

        # Chỉ search capture để tránh nở cây quá mạnh
        tactical_moves = self._get_capture_moves(board, color)
        if not tactical_moves:
            return alpha

        tactical_moves = self._order_moves(
            board=board,
            moves=tactical_moves,
            color=color,
            ply=ply,
            tt_move=None,
        )

        for move in tactical_moves:
            if self._time_up():
                self.stop_search = True
                break

            board.make_move(move)
            score = -self.quiescence(board, -beta, -alpha, -color, ply + 1)
            board.undo_move()

            if self.stop_search:
                break

            if score >= beta:
                return score
            if score > alpha:
                alpha = score

        return alpha

    # =========================
    # MOVE HELPERS
    # =========================
    def _get_capture_moves(self, board, color):
        moves = self.move_generator.get_all_moves(color)
        return [move for move in moves if move.is_capture()]

    def _order_moves(self, board, moves, color, ply, tt_move=None):
        if not moves:
            return moves

        killers = self.killer_moves.get(ply, [])

        def score_move(move):
            score = 0
            moved_piece = move.piece_moved
            captured_piece = move.piece_captured

            # 1) TT move cao nhất
            if tt_move is not None and move == tt_move:
                score += 10_000_000

            # 2) Capture: MVV-LVA
            if captured_piece != EMPTY:
                victim_value = PIECE_VALUES.get(captured_piece.piece_type, 0)
                attacker_value = PIECE_VALUES.get(moved_piece.piece_type, 1)
                score += 1_000_000 + victim_value * 100 - attacker_value

            # 3) Killer
            if len(killers) > 0 and move == killers[0]:
                score += 900_000
            elif len(killers) > 1 and move == killers[1]:
                score += 800_000

            # 4) History
            history_key = (
                color,
                moved_piece.piece_type,
                move.end_row,
                move.end_col,
            )
            score += self.history_table.get(history_key, 0)

            # 5) Bonus nhẹ theo vị trí trung tâm
            center_bonus = 4 - abs(move.end_col - 4)
            score += center_bonus * 8

            # 6) Bonus tốt qua sông
            if moved_piece.piece_type == PAWN:
                if (moved_piece.color == RED and move.end_row <= 4) or (
                    moved_piece.color == BLACK and move.end_row >= 5
                ):
                    score += 30

            return score

        return sorted(moves, key=score_move, reverse=True)

    # =========================
    # EVAL / HEURISTIC HELPERS
    # =========================
    def _evaluate_relative(self, board, color):
        raw_score = Evaluation.evaluate(board, self.move_generator.game_manager)
        return raw_score if color == RED else -raw_score

    def _has_enough_material_for_null(self, board, color):
        for row in board.board:
            for piece in row:
                if piece == EMPTY:
                    continue
                if piece.color != color:
                    continue
                if piece.piece_type not in (KING, PAWN):
                    return True
        return False

    def _is_killer(self, ply, move):
        killers = self.killer_moves.get(ply, [])
        return move in killers

    def _add_killer_move(self, ply, move):
        killers = self.killer_moves.setdefault(ply, [])

        if move in killers:
            return

        killers.insert(0, move)
        if len(killers) > 2:
            killers.pop()

    def _update_history(self, color, move, depth):
        moved_piece = move.piece_moved
        key = (color, moved_piece.piece_type, move.end_row, move.end_col)
        self.history_table[key] = self.history_table.get(key, 0) + depth * depth

    # =========================
    # TT HELPERS
    # =========================
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

    def _store_tt(self, board, color, depth, score, flag, best_move):
        if len(self.tt) >= self.max_tt_size:
            self.tt.clear()

        key = self._board_key(board, color)
        self.tt[key] = {
            "depth": depth,
            "score": score,
            "flag": flag,
            "best_move": best_move,
        }

    def _get_tt_move(self, board, color):
        key = self._board_key(board, color)
        entry = self.tt.get(key)
        if entry is None:
            return None
        return entry.get("best_move")

    # =========================
    # TIME HELPERS
    # =========================
    def _time_up(self):
        return (time.perf_counter() - self.start_time) >= self.time_limit