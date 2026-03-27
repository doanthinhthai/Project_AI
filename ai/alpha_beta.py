import random
from core.constants import RED, BLACK, EMPTY, PIECE_VALUES, KING, PAWN
from ai.evaluation.evaluation import Evaluation


class AlphaBeta:
    EXACT = 0
    LOWERBOUND = 1
    UPPERBOUND = 2

    INF = 10**9
    MATE_SCORE = 10**7
    NULL_MOVE_REDUCTION = 2

    def __init__(self, move_generator, max_depth=3):
        self.move_generator = move_generator
        self.max_depth = max_depth

        # Transposition Table
        self.tt = {}
        self.max_tt_size = 200000

        # Search stats
        self.node_count = 0

        # Killer moves: mỗi ply giữ 2 killer tốt nhất
        self.killer_moves = {}

        # History heuristic: {(color, piece_type, end_row, end_col): score}
        self.history_table = {}

    # PUBLIC API
    def get_best_move(self, board, color):
        self.node_count = 0
        best_move = None

        root_moves = self.move_generator.get_all_moves(color)
        if not root_moves:
            return None

        alpha = -self.INF
        beta = self.INF

        # Iterative Deepening
        for depth in range(1, self.max_depth + 1):
            current_best_score = -self.INF
            current_best_moves = []

            tt_move = self._get_tt_move(board, color)
            ordered_moves = self._order_moves(
                board=board,
                moves=root_moves,
                color=color,
                ply=0,
                tt_move=tt_move,
            )

            alpha = -self.INF
            beta = self.INF

            for i, move in enumerate(ordered_moves):
                board.make_move(move)

                # PVS ở root:
                # - move đầu: full window
                # - move sau: zero window trước, fail-high thì search lại full window
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

                    if alpha < score < beta:
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

                if score > current_best_score:
                    current_best_score = score
                    current_best_moves = [move]
                elif score == current_best_score:
                    current_best_moves.append(move)

                alpha = max(alpha, current_best_score)

            if current_best_moves:
                best_move = random.choice(current_best_moves)

                self._store_tt(
                    board=board,
                    color=color,
                    depth=depth,
                    score=current_best_score,
                    flag=self.EXACT,
                    best_move=best_move,
                )

        return best_move

    # NEGAMAX + ALPHA-BETA + PVS
    def search(self, board, depth, alpha, beta, color, ply=0, allow_null=True):
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

        # Nếu đang bị chiếu, nên mở rộng thêm một chút
        in_check = self.move_generator.game_manager.is_in_check(color)
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
            if null_score >= beta:
                return null_score

        moves = self.move_generator.get_all_moves(color)

        # No legal moves
        if not moves:
            # Nếu không có nước và đang bị chiếu -> mate
            if in_check:
                return -self.MATE_SCORE + ply
            # Không bị chiếu mà hết nước -> hòa / bế tắc
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
            board.make_move(move)

            # Principal Variation Search
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
                # Zero-window search trước
                score = -self.search(
                    board=board,
                    depth=depth - 1,
                    alpha=-(alpha + 1),
                    beta=-alpha,
                    color=-color,
                    ply=ply + 1,
                    allow_null=True,
                )

                # Nếu fail-high trong khoảng thì re-search full window
                if alpha < score < beta:
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

            if score > best_score:
                best_score = score
                best_move = move

            if score > alpha:
                alpha = score

            if alpha >= beta:
                # Beta cutoff -> cập nhật killer + history cho non-capture
                if not move.is_capture():
                    self._add_killer_move(ply, move)
                    self._update_history(color, move, depth)
                break

        # Ghi TT flag
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

    # QUIESCENCE SEARCH
    def quiescence(self, board, alpha, beta, color, ply=0):
        self.node_count += 1

        stand_pat = self._evaluate_relative(board, color)

        if stand_pat >= beta:
            return stand_pat
        if stand_pat > alpha:
            alpha = stand_pat

        tactical_moves = self._get_tactical_moves(board, color)
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
            board.make_move(move)
            score = -self.quiescence(board, -beta, -alpha, -color, ply + 1)
            board.undo_move()

            if score >= beta:
                return score
            if score > alpha:
                alpha = score

        return alpha

    # MOVE GENERATION HELPERS
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

    def _order_moves(self, board, moves, color, ply, tt_move=None):
        if not moves:
            return moves

        killers = self.killer_moves.get(ply, [])

        def score_move(move):
            score = 0
            moved_piece = move.piece_moved
            captured_piece = move.piece_captured

            # 1) TT move ưu tiên cao nhất
            if tt_move is not None and move == tt_move:
                score += 10_000_000

            # 2) Capture: MVV-LVA
            if captured_piece != EMPTY:
                victim_value = PIECE_VALUES.get(captured_piece.piece_type, 0)
                attacker_value = PIECE_VALUES.get(moved_piece.piece_type, 1)
                score += 1_000_000 + victim_value * 100 - attacker_value

            # 3) Killer moves
            if len(killers) > 0 and move == killers[0]:
                score += 900_000
            elif len(killers) > 1 and move == killers[1]:
                score += 800_000

            # 4) History heuristic
            history_key = (
                color,
                moved_piece.piece_type,
                move.end_row,
                move.end_col,
            )
            score += self.history_table.get(history_key, 0)

            # 5) Bonus gây chiếu
            board.make_move(move)
            if self.move_generator.game_manager.is_in_check(-color):
                score += 50_000
            board.undo_move()

            # 6) Bonus vị trí trung tâm
            center_bonus = 4 - abs(move.end_col - 4)
            score += center_bonus * 8

            # 7) Bonus tốt qua sông / tiến
            if moved_piece.piece_type == PAWN:
                if (moved_piece.color == RED and move.end_row <= 4) or (
                    moved_piece.color == BLACK and move.end_row >= 5
                ):
                    score += 30

            return score

        return sorted(moves, key=score_move, reverse=True)

    # HEURISTIC HELPERS
    def _evaluate_relative(self, board, color):
        raw_score = Evaluation.evaluate(board, self.move_generator.game_manager)
        return raw_score if color == RED else -raw_score

    def _has_enough_material_for_null(self, board, color):
        """
        Null move pruning không nên dùng trong thế quá ít quân.
        Ở đây dùng bản đơn giản:
        - nếu bên đang đi còn quân khác ngoài KING/PAWN thì cho phép
        """
        for row in board.board:
            for piece in row:
                if piece == EMPTY:
                    continue
                if piece.color != color:
                    continue
                if piece.piece_type not in (KING, PAWN):
                    return True
        return False

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

    # TT HELPERS
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