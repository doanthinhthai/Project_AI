from core.constants import (
    PIECE_VALUES, RED, BLACK, EMPTY,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN
)


class Evaluation:
    PIECE_SQUARE_TABLE = {
        PAWN: [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [8, 12, 16, 20, 24, 20, 16, 12, 8],
            [10, 14, 18, 24, 28, 24, 18, 14, 10],
            [12, 18, 24, 30, 36, 30, 24, 18, 12],
            [18, 24, 30, 38, 45, 38, 30, 24, 18],
            [25, 32, 38, 46, 55, 46, 38, 32, 25],
            [16, 22, 26, 32, 36, 32, 26, 22, 16],
            [8, 10, 12, 16, 20, 16, 12, 10, 8],
            [3, 4, 6, 8, 10, 8, 6, 4, 3],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        ROOK: [
            [10, 14, 18, 22, 24, 22, 18, 14, 10],
            [12, 16, 20, 24, 28, 24, 20, 16, 12],
            [12, 16, 20, 26, 30, 26, 20, 16, 12],
            [12, 16, 22, 28, 34, 28, 22, 16, 12],
            [14, 18, 24, 30, 36, 30, 24, 18, 14],
            [14, 18, 24, 30, 36, 30, 24, 18, 14],
            [12, 16, 22, 28, 34, 28, 22, 16, 12],
            [12, 16, 20, 26, 30, 26, 20, 16, 12],
            [12, 16, 20, 24, 28, 24, 20, 16, 12],
            [10, 14, 18, 22, 24, 22, 18, 14, 10],
        ],
        KNIGHT: [
            [4, 8, 10, 12, 14, 12, 10, 8, 4],
            [6, 10, 14, 18, 20, 18, 14, 10, 6],
            [8, 14, 18, 22, 26, 22, 18, 14, 8],
            [10, 16, 22, 28, 32, 28, 22, 16, 10],
            [10, 18, 24, 30, 34, 30, 24, 18, 10],
            [10, 18, 24, 30, 34, 30, 24, 18, 10],
            [10, 16, 22, 28, 32, 28, 22, 16, 10],
            [8, 14, 18, 22, 26, 22, 18, 14, 8],
            [6, 10, 14, 18, 20, 18, 14, 10, 6],
            [4, 8, 10, 12, 14, 12, 10, 8, 4],
        ],
        CANNON: [
            [6, 8, 10, 12, 14, 12, 10, 8, 6],
            [8, 10, 12, 16, 18, 16, 12, 10, 8],
            [8, 12, 16, 20, 24, 20, 16, 12, 8],
            [10, 14, 18, 24, 28, 24, 18, 14, 10],
            [12, 16, 22, 26, 30, 26, 22, 16, 12],
            [12, 16, 22, 26, 30, 26, 22, 16, 12],
            [10, 14, 18, 24, 28, 24, 18, 14, 10],
            [8, 12, 16, 20, 24, 20, 16, 12, 8],
            [8, 10, 12, 16, 18, 16, 12, 10, 8],
            [6, 8, 10, 12, 14, 12, 10, 8, 6],
        ],
        ADVISOR: [
            [0, 0, 0, 8, 10, 8, 0, 0, 0],
            [0, 0, 0, 6, 8, 6, 0, 0, 0],
            [0, 0, 0, 8, 10, 8, 0, 0, 0],
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0, 0, 0, 8, 10, 8, 0, 0, 0],
            [0, 0, 0, 6, 8, 6, 0, 0, 0],
            [0, 0, 0, 8, 10, 8, 0, 0, 0],
        ],
        ELEPHANT: [
            [4, 0, 6, 0, 8, 0, 6, 0, 4],
            [0] * 9,
            [2, 0, 8, 0, 10, 0, 8, 0, 2],
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [2, 0, 8, 0, 10, 0, 8, 0, 2],
            [0] * 9,
            [4, 0, 6, 0, 8, 0, 6, 0, 4],
        ],
        KING: [
            [0, 0, 0, 8, 14, 8, 0, 0, 0],
            [0, 0, 0, 6, 12, 6, 0, 0, 0],
            [0, 0, 0, 8, 14, 8, 0, 0, 0],
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0] * 9,
            [0, 0, 0, 8, 14, 8, 0, 0, 0],
            [0, 0, 0, 6, 12, 6, 0, 0, 0],
            [0, 0, 0, 8, 14, 8, 0, 0, 0],
        ],
    }

    PHASE_OPENING = "opening"
    PHASE_MIDDLEGAME = "middlegame"
    PHASE_ENDGAME = "endgame"

    @staticmethod
    def _in_bounds(r, c):
        return 0 <= r < 10 and 0 <= c < 9

    @staticmethod
    def _is_red_side(row):
        return row >= 5

    @staticmethod
    def _is_black_side(row):
        return row <= 4

    @staticmethod
    def _normalize_row(piece, row):
        return row if piece.color == RED else 9 - row

    @staticmethod
    def _enemy(color):
        return BLACK if color == RED else RED

    @staticmethod
    def _is_in_palace(color, row, col):
        if col < 3 or col > 5:
            return False
        if color == RED:
            return 7 <= row <= 9
        return 0 <= row <= 2

    @staticmethod
    def _find_king(board, color):
        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece != EMPTY and piece.color == color and piece.piece_type == KING:
                    return (r, c)
        return None

    @staticmethod
    def _count_piece(board, color, piece_type):
        count = 0
        for r in range(10):
            for c in range(9):
                p = board.board[r][c]
                if p != EMPTY and p.color == color and p.piece_type == piece_type:
                    count += 1
        return count

    @staticmethod
    def _game_phase(red_material, black_material):
        total = red_material + black_material
        # tùy PIECE_VALUES của bạn, có thể chỉnh lại ngưỡng
        if total >= 7000:
            return Evaluation.PHASE_OPENING
        elif total >= 4200:
            return Evaluation.PHASE_MIDDLEGAME
        return Evaluation.PHASE_ENDGAME

    @staticmethod
    def _phase_weights(phase):
        if phase == Evaluation.PHASE_OPENING:
            return {
                "mobility": 1.2,
                "king_safety": 1.0,
                "pawn_structure": 0.9,
                "attack": 0.9,
                "material_scale": 0.05,
            }
        elif phase == Evaluation.PHASE_MIDDLEGAME:
            return {
                "mobility": 1.0,
                "king_safety": 1.3,
                "pawn_structure": 1.0,
                "attack": 1.2,
                "material_scale": 0.07,
            }
        else:
            return {
                "mobility": 0.8,
                "king_safety": 0.9,
                "pawn_structure": 1.2,
                "attack": 1.0,
                "material_scale": 0.10,
            }

    @staticmethod
    def get_piece_square_bonus(piece, row, col):
        table = Evaluation.PIECE_SQUARE_TABLE.get(piece.piece_type)
        if table is None:
            return 0
        normalized_row = Evaluation._normalize_row(piece, row)
        return table[normalized_row][col]

    @staticmethod
    def get_position_bonus(piece, row, col, phase):
        """
        Giảm bớt so với bản cũ để tránh đếm trùng PST.
        Chỉ giữ các ý 'đặc thù chiến lược'.
        """
        normalized_row = Evaluation._normalize_row(piece, row)
        center_distance = abs(col - 4)
        bonus = 0

        if piece.piece_type == PAWN:
            if normalized_row <= 4:  # qua sông
                bonus += 28
            if phase == Evaluation.PHASE_ENDGAME:
                bonus += max(0, 6 - normalized_row) * 5
            else:
                bonus += max(0, 6 - normalized_row) * 3
            bonus += max(0, 3 - center_distance) * 3

        elif piece.piece_type == KING:
            if col == 4:
                bonus += 10
            if (piece.color == RED and row == 9) or (piece.color == BLACK and row == 0):
                bonus += 6

        elif piece.piece_type == ADVISOR:
            if Evaluation._is_in_palace(piece.color, row, col):
                bonus += 6

        elif piece.piece_type == ELEPHANT:
            # tượng ở nhà thủ vẫn có giá trị
            if piece.color == RED and row >= 5:
                bonus += 5
            elif piece.color == BLACK and row <= 4:
                bonus += 5

        elif piece.piece_type == ROOK:
            bonus += max(0, 2 - center_distance) * 2

        elif piece.piece_type == KNIGHT:
            bonus += max(0, 2 - center_distance) * 3

        elif piece.piece_type == CANNON:
            bonus += max(0, 2 - center_distance) * 2

        return bonus

    # =========================
    # ATTACK MAP / PIECE CONTROL
    # =========================

    @staticmethod
    def _rook_control(board, row, col):
        squares = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while Evaluation._in_bounds(r, c):
                squares.append((r, c))
                if board.board[r][c] != EMPTY:
                    break
                r += dr
                c += dc
        return squares

    @staticmethod
    def _cannon_control(board, row, col):
        """
        control để đo pressure:
        - ô trống trên đường đi vẫn tính là pháo khống chế theo di chuyển
        - sau đúng 1 màn chắn, quân đầu tiên tiếp theo là ô ăn được
        """
        squares = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            jumped = False
            while Evaluation._in_bounds(r, c):
                piece = board.board[r][c]
                if not jumped:
                    squares.append((r, c))
                    if piece != EMPTY:
                        jumped = True
                else:
                    if piece != EMPTY:
                        squares.append((r, c))
                        break
                r += dr
                c += dc
        return squares

    @staticmethod
    def _knight_control(board, row, col):
        squares = []
        knight_steps = [
            (-2, -1, -1, 0), (-2, 1, -1, 0),
            (2, -1, 1, 0), (2, 1, 1, 0),
            (-1, -2, 0, -1), (1, -2, 0, -1),
            (-1, 2, 0, 1), (1, 2, 0, 1),
        ]
        for dr, dc, leg_r, leg_c in knight_steps:
            br, bc = row + leg_r, col + leg_c
            nr, nc = row + dr, col + dc
            if not Evaluation._in_bounds(nr, nc):
                continue
            if board.board[br][bc] == EMPTY:
                squares.append((nr, nc))
        return squares

    @staticmethod
    def _pawn_control(board, piece, row, col):
        squares = []
        if piece.color == RED:
            forward = (-1, 0)
            side_allowed = row <= 4
        else:
            forward = (1, 0)
            side_allowed = row >= 5

        nr, nc = row + forward[0], col + forward[1]
        if Evaluation._in_bounds(nr, nc):
            squares.append((nr, nc))

        if side_allowed:
            for dc in (-1, 1):
                nr, nc = row, col + dc
                if Evaluation._in_bounds(nr, nc):
                    squares.append((nr, nc))
        return squares

    @staticmethod
    def _king_control(piece, row, col):
        squares = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if Evaluation._in_bounds(nr, nc) and Evaluation._is_in_palace(piece.color, nr, nc):
                squares.append((nr, nc))
        return squares

    @staticmethod
    def _advisor_control(piece, row, col):
        squares = []
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row + dr, col + dc
            if Evaluation._in_bounds(nr, nc) and Evaluation._is_in_palace(piece.color, nr, nc):
                squares.append((nr, nc))
        return squares

    @staticmethod
    def _elephant_control(board, piece, row, col):
        squares = []
        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            eye_r, eye_c = row + dr // 2, col + dc // 2
            nr, nc = row + dr, col + dc
            if not Evaluation._in_bounds(nr, nc):
                continue
            if board.board[eye_r][eye_c] != EMPTY:
                continue

            # tượng không qua sông
            if piece.color == RED and nr <= 4:
                continue
            if piece.color == BLACK and nr >= 5:
                continue

            squares.append((nr, nc))
        return squares

    @staticmethod
    def _piece_control(board, piece, row, col):
        if piece.piece_type == ROOK:
            return Evaluation._rook_control(board, row, col)
        if piece.piece_type == CANNON:
            return Evaluation._cannon_control(board, row, col)
        if piece.piece_type == KNIGHT:
            return Evaluation._knight_control(board, row, col)
        if piece.piece_type == PAWN:
            return Evaluation._pawn_control(board, piece, row, col)
        if piece.piece_type == KING:
            return Evaluation._king_control(piece, row, col)
        if piece.piece_type == ADVISOR:
            return Evaluation._advisor_control(piece, row, col)
        if piece.piece_type == ELEPHANT:
            return Evaluation._elephant_control(board, piece, row, col)
        return []

    @staticmethod
    def _attack_map(board, color):
        attack_count = {}
        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY or piece.color != color:
                    continue
                for sq in Evaluation._piece_control(board, piece, r, c):
                    attack_count[sq] = attack_count.get(sq, 0) + 1
        return attack_count

    # =========================
    # MOBILITY
    # =========================

    @staticmethod
    def get_mobility_bonus(board, phase):
        """
        Không còn gán cứng Xe=5, Mã=4... như bản cũ.
        Dùng số ô kiểm soát/thao tác thực tế.
        """
        red_score = 0
        black_score = 0

        piece_weights = {
            ROOK: 2.0,
            KNIGHT: 2.2,
            CANNON: 2.0,
            PAWN: 1.2,
            ADVISOR: 0.4,
            ELEPHANT: 0.5,
            KING: 0.3,
        }

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                control = Evaluation._piece_control(board, piece, r, c)
                mobility = len(control) * piece_weights.get(piece.piece_type, 1.0)

                # thưởng thêm nếu khống chế ô trống nhiều
                empty_control = 0
                for rr, cc in control:
                    if board.board[rr][cc] == EMPTY:
                        empty_control += 1
                mobility += empty_control * 0.4

                if piece.color == RED:
                    red_score += mobility
                else:
                    black_score += mobility

        phase_factor = 1.2 if phase == Evaluation.PHASE_OPENING else 1.0
        return int((red_score - black_score) * phase_factor)

    # =========================
    # PAWN STRUCTURE
    # =========================

    @staticmethod
    def get_structure_bonus(board, phase):
        red_bonus = 0
        black_bonus = 0
        red_pawns = []
        black_pawns = []

        for row in range(10):
            for col in range(9):
                piece = board.board[row][col]
                if piece == EMPTY:
                    continue
                if piece.piece_type == PAWN:
                    if piece.color == RED:
                        red_pawns.append((row, col))
                    else:
                        black_pawns.append((row, col))

        def evaluate_side(pawns, color):
            bonus = 0
            files = {}

            for r, c in pawns:
                files[c] = files.get(c, 0) + 1

                # qua sông thưởng
                if color == RED and r <= 4:
                    bonus += 14 if phase != Evaluation.PHASE_ENDGAME else 20
                if color == BLACK and r >= 5:
                    bonus += 14 if phase != Evaluation.PHASE_ENDGAME else 20

                # áp sát cung địch
                if color == RED and r <= 2:
                    bonus += 10
                if color == BLACK and r >= 7:
                    bonus += 10

            # tốt chồng cột
            for count in files.values():
                if count > 1:
                    bonus -= (count - 1) * 10

            # trải đều cột
            bonus += len(files) * 4

            return bonus

        red_bonus = evaluate_side(red_pawns, RED)
        black_bonus = evaluate_side(black_pawns, BLACK)
        return red_bonus - black_bonus

    # =========================
    # THREAT / KING SAFETY
    # =========================

    @staticmethod
    def _is_open_file_to_king(board, king_pos, attacker_color):
        """
        Kiểm tra cột tướng có đang bị Xe/Pháo đối phương ép trực diện không.
        """
        kr, kc = king_pos

        # lên trên
        blockers = 0
        r = kr - 1
        while r >= 0:
            piece = board.board[r][kc]
            if piece != EMPTY:
                if piece.color == attacker_color:
                    if piece.piece_type == ROOK and blockers == 0:
                        return True
                    if piece.piece_type == CANNON and blockers == 1:
                        return True
                    if piece.piece_type == KING and blockers == 0:
                        return True
                blockers += 1
            r -= 1

        # xuống dưới
        blockers = 0
        r = kr + 1
        while r < 10:
            piece = board.board[r][kc]
            if piece != EMPTY:
                if piece.color == attacker_color:
                    if piece.piece_type == ROOK and blockers == 0:
                        return True
                    if piece.piece_type == CANNON and blockers == 1:
                        return True
                    if piece.piece_type == KING and blockers == 0:
                        return True
                blockers += 1
            r += 1

        return False

    @staticmethod
    def _count_attackers_near_king(board, king_pos, attacker_color):
        kr, kc = king_pos
        count = 0
        threat_value = 0

        values = {
            ROOK: 18,
            CANNON: 16,
            KNIGHT: 14,
            PAWN: 10,
            KING: 8,
            ADVISOR: 2,
            ELEPHANT: 2,
        }

        for r in range(max(0, kr - 2), min(10, kr + 3)):
            for c in range(max(0, kc - 2), min(9, kc + 3)):
                piece = board.board[r][c]
                if piece == EMPTY or piece.color != attacker_color:
                    continue
                control = Evaluation._piece_control(board, piece, r, c)
                if king_pos in control:
                    count += 1
                    threat_value += values.get(piece.piece_type, 5)

        return count, threat_value

    @staticmethod
    def _king_escape_count(board, color):
        king_pos = Evaluation._find_king(board, color)
        if king_pos is None:
            return 0

        kr, kc = king_pos
        enemy_attacks = Evaluation._attack_map(board, Evaluation._enemy(color))

        escape = 0
        for nr, nc in Evaluation._king_control(type("Tmp", (), {"color": color}), kr, kc):
            piece = board.board[nr][nc]
            if piece != EMPTY and piece.color == color:
                continue
            if (nr, nc) not in enemy_attacks:
                escape += 1

        return escape

    @staticmethod
    def get_king_safety_bonus(board, color, phase, game_manager=None):
        king_pos = Evaluation._find_king(board, color)
        if king_pos is None:
            return -100000

        enemy = Evaluation._enemy(color)
        enemy_attacks = Evaluation._attack_map(board, enemy)
        kr, kc = king_pos

        score = 0

        advisors = Evaluation._count_piece(board, color, ADVISOR)
        elephants = Evaluation._count_piece(board, color, ELEPHANT)

        # quân thủ quanh vua
        score += advisors * 18
        score += elephants * 14

        # vua đứng đúng cung giữa an toàn hơn
        if kc == 4:
            score += 8

        # các ô trong cung bị địch kiểm soát
        palace_pressure = 0
        palace_safe = 0
        for r in range(10):
            for c in range(9):
                if Evaluation._is_in_palace(color, r, c):
                    atk = enemy_attacks.get((r, c), 0)
                    palace_pressure += atk
                    if atk == 0:
                        palace_safe += 1

        score -= palace_pressure * 8
        score += palace_safe * 3

        # cột vua bị ép trực diện bởi xe/pháo/tướng
        if Evaluation._is_open_file_to_king(board, king_pos, enemy):
            score -= 35 if phase != Evaluation.PHASE_ENDGAME else 24

        # đang bị nhiều quân nhắm trực tiếp
        attacker_count, threat_value = Evaluation._count_attackers_near_king(board, king_pos, enemy)
        score -= threat_value
        if attacker_count >= 2:
            score -= 22
        if attacker_count >= 3:
            score -= 35

        # ít ô chạy
        escape_count = Evaluation._king_escape_count(board, color)
        if escape_count == 0:
            score -= 45
        elif escape_count == 1:
            score -= 20
        else:
            score += min(escape_count, 3) * 4

        # ô vua đang đứng bị khống chế
        king_square_pressure = enemy_attacks.get((kr, kc), 0)
        score -= king_square_pressure * 18

        # nếu engine hiện tại có is_in_check thì dùng luôn
        if game_manager is not None:
            try:
                if game_manager.is_in_check(color):
                    score -= 80
            except Exception:
                pass

        # ========= near-mate pressure =========
        # Đây là phần bạn đang cần:
        # chưa chiếu ngay nhưng thế ép rất mạnh, gần như 1-2 nước nữa thành chiếu bí
        near_mate_pressure = 0

        if palace_pressure >= 5 and escape_count <= 1:
            near_mate_pressure += 30

        if attacker_count >= 2 and king_square_pressure >= 1 and escape_count <= 1:
            near_mate_pressure += 35

        if Evaluation._is_open_file_to_king(board, king_pos, enemy) and palace_pressure >= 4:
            near_mate_pressure += 28

        # thiếu sĩ/tượng lại còn đang bị ép
        if advisors + elephants <= 1 and attacker_count >= 2:
            near_mate_pressure += 30

        score -= near_mate_pressure

        return score

    @staticmethod
    def get_attack_bonus(board, phase):
        red_attacks = Evaluation._attack_map(board, RED)
        black_attacks = Evaluation._attack_map(board, BLACK)

        red_score = 0
        black_score = 0

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                base = PIECE_VALUES[piece.piece_type]

                if piece.color == RED:
                    atk = black_attacks.get((r, c), 0)
                    guard = red_attacks.get((r, c), 0)
                    if atk > 0:
                        # quân bị treo / bị đè nhiều hơn bảo vệ
                        if atk > guard:
                            red_score -= int(base * 0.08)
                        elif atk == guard:
                            red_score -= int(base * 0.03)
                else:
                    atk = red_attacks.get((r, c), 0)
                    guard = black_attacks.get((r, c), 0)
                    if atk > 0:
                        if atk > guard:
                            black_score -= int(base * 0.08)
                        elif atk == guard:
                            black_score -= int(base * 0.03)

        return int((red_score - black_score) * (1.2 if phase == Evaluation.PHASE_MIDDLEGAME else 1.0))

    @staticmethod
    def get_check_bonus(board, game_manager=None):
        if game_manager is None:
            return 0

        bonus = 0
        try:
            if game_manager.is_in_check(BLACK):
                bonus += 55
            if game_manager.is_in_check(RED):
                bonus -= 55
        except Exception:
            pass

        try:
            if game_manager.kings_face_each_other():
                bonus += 90 if game_manager.current_turn == RED else -90
        except Exception:
            pass

        return bonus

    @staticmethod
    def evaluate(board, game_manager=None):
        score = 0
        red_material = 0
        black_material = 0

        # 1. material trước
        for row in range(10):
            for col in range(9):
                piece = board.board[row][col]
                if piece == EMPTY:
                    continue

                base_value = PIECE_VALUES[piece.piece_type]
                if piece.color == RED:
                    red_material += base_value
                else:
                    black_material += base_value

        phase = Evaluation._game_phase(red_material, black_material)
        weights = Evaluation._phase_weights(phase)

        # 2. material + pst + position
        for row in range(10):
            for col in range(9):
                piece = board.board[row][col]
                if piece == EMPTY:
                    continue

                base_value = PIECE_VALUES[piece.piece_type]
                pst_bonus = Evaluation.get_piece_square_bonus(piece, row, col)
                pos_bonus = Evaluation.get_position_bonus(piece, row, col, phase)
                value = base_value + pst_bonus + pos_bonus

                if piece.color == RED:
                    score += value
                else:
                    score -= value

        # 3. mobility
        score += int(Evaluation.get_mobility_bonus(board, phase) * weights["mobility"])

        # 4. pawn structure
        score += int(Evaluation.get_structure_bonus(board, phase) * weights["pawn_structure"])

        # 5. attack pressure
        score += int(Evaluation.get_attack_bonus(board, phase) * weights["attack"])

        # 6. king safety
        red_king_safety = Evaluation.get_king_safety_bonus(board, RED, phase, game_manager)
        black_king_safety = Evaluation.get_king_safety_bonus(board, BLACK, phase, game_manager)
        score += int((red_king_safety - black_king_safety) * weights["king_safety"])

        # 7. check / face-to-face
        score += Evaluation.get_check_bonus(board, game_manager)

        # 8. material lead scaling theo phase
        material_balance = red_material - black_material
        score += int(material_balance * weights["material_scale"])

        return score