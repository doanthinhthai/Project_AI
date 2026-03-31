from core.constants import (
    RED, BLACK, EMPTY,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN,
    PIECE_VALUES
)

# =============================================================================
# PIECE-SQUARE TABLES (PST)
# Góc nhìn từ phía ĐỎ (hàng 9 = hàng đầu của đỏ, hàng 0 = hàng đầu của đen)
# Giá trị cao = vị trí tốt hơn
# =============================================================================

PST_ROOK = [
    [206, 208, 207, 213, 214, 213, 207, 208, 206],
    [206, 212, 209, 216, 233, 216, 209, 212, 206],
    [206, 208, 207, 214, 216, 214, 207, 208, 206],
    [206, 213, 213, 216, 216, 216, 213, 213, 206],
    [208, 211, 211, 214, 215, 214, 211, 211, 208],
    [208, 212, 212, 214, 215, 214, 212, 212, 208],
    [204, 209, 204, 212, 214, 212, 204, 209, 204],
    [198, 208, 204, 212, 212, 212, 204, 208, 198],
    [200, 208, 206, 212, 200, 212, 206, 208, 200],
    [194, 206, 204, 212, 200, 212, 204, 206, 194],
]

PST_KNIGHT = [
    [ 90,  90,  90,  96,  90,  96,  90,  90,  90],
    [ 90,  96,  103, 97,  94,  97,  103, 96,  90],
    [ 92,  98,  99,  103, 99,  103, 99,  98,  92],
    [ 93,  108, 100, 107, 100, 107, 100, 108, 93],
    [ 90,  100, 99,  103, 104, 103, 99,  100, 90],
    [ 90,  98,  101, 102, 103, 102, 101, 98,  90],
    [ 92,  94,  98,  95,  98,  95,  98,  94,  92],
    [ 93,  92,  94,  95,  92,  95,  94,  92,  93],
    [ 85,  90,  92,  93,  78,  93,  92,  90,  85],
    [ 88,  85,  90,  88,  90,  88,  90,  85,  88],
]

PST_CANNON = [
    [100, 100,  96, 91, 90, 91,  96, 100, 100],
    [ 98,  98,  96, 92, 89, 92,  96,  98,  98],
    [ 97,  96,  100, 91, 90, 91, 100,  96,  97],
    [ 96,  96,  96,  96, 100, 96,  96,  96,  96],
    [ 95,  96,  99,  96, 100, 96,  99,  96,  95],
    [ 96,  96,  96,  96,  96,  96,  96,  96,  96],
    [ 96,  97,  98,  98,  98,  98,  98,  97,  96],
    [ 97,  96,  100, 99, 101, 99, 100,  96,  97],
    [ 96,  97,  96,  100, 101, 100, 96,  97,  96],
    [ 96,  96,  97,  99,  99,  99,  97,  96,  96],
]

PST_PAWN = [
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],  # hàng đen (chưa qua sông)
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [18,  36,  36,  45,  45,  45,  36,  36,  18],  # qua sông → giá trị tăng mạnh
    [28,  36,  45,  55,  55,  55,  45,  36,  28],
    [36,  45,  55,  65,  65,  65,  55,  45,  36],
    [39,  45,  55,  65,  69,  65,  55,  45,  39],
    [45,  49,  55,  65,  69,  65,  55,  49,  45],  # hàng gần tướng đen nhất
]

PST_ADVISOR = [
    [ 0,   0,   0,  20,   0,  20,   0,   0,   0],
    [ 0,   0,   0,   0,  23,   0,   0,   0,   0],
    [ 0,   0,   0,  20,   0,  20,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,  20,   0,  20,   0,   0,   0],
    [ 0,   0,   0,   0,  23,   0,   0,   0,   0],
    [ 0,   0,   0,  20,   0,  20,   0,   0,   0],
]

PST_ELEPHANT = [
    [ 0,   0,  20,   0,   0,   0,  20,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [18,   0,   0,   0,  23,   0,   0,   0,  18],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,  20,   0,   0,   0,  20,   0,   0],
    [ 0,   0,  20,   0,   0,   0,  20,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [18,   0,   0,   0,  23,   0,   0,   0,  18],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,  20,   0,   0,   0,  20,   0,   0],
]

PST_KING = [
    [ 0,   0,   0,  10,  -15, 10,   0,   0,   0],
    [ 0,   0,   0,   4,  -15,  4,   0,   0,   0],
    [ 0,   0,   0,  -1,  -15, -1,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,   0,   0,   0,   0,   0,   0],
    [ 0,   0,   0,  -1,  -15, -1,   0,   0,   0],
    [ 0,   0,   0,   4,  -15,  4,   0,   0,   0],
    [ 0,   0,   0,  10,  -15, 10,   0,   0,   0],
]

PST_MAP = {
    ROOK:     PST_ROOK,
    KNIGHT:   PST_KNIGHT,
    CANNON:   PST_CANNON,
    PAWN:     PST_PAWN,
    ADVISOR:  PST_ADVISOR,
    ELEPHANT: PST_ELEPHANT,
    KING:     PST_KING,
}

# Vị trí cung vua
RED_PALACE   = frozenset((r, c) for r in range(7, 10) for c in range(3, 6))
BLACK_PALACE = frozenset((r, c) for r in range(0, 3)  for c in range(3, 6))

# Vị trí lý tưởng của sĩ
RED_ADVISOR_IDEAL   = frozenset([(9, 3), (9, 5), (8, 4)])
BLACK_ADVISOR_IDEAL = frozenset([(0, 3), (0, 5), (1, 4)])

# Trọng số mobility theo loại quân
MOBILITY_WEIGHT = {
    ROOK:     5,
    CANNON:   4,
    KNIGHT:   4,
    PAWN:     2,
    ADVISOR:  1,
    ELEPHANT: 1,
    KING:     0,
}


class FeatureExtractor:

    # =========================================================================
    # HELPERS
    # =========================================================================

    @staticmethod
    def in_bounds(r, c):
        return 0 <= r < 10 and 0 <= c < 9

    @staticmethod
    def normalize_row(piece, row):
        """Chuẩn hoá hàng về góc nhìn của quân đỏ (hàng 9 = hàng nhà)."""
        return row if piece.color == RED else 9 - row

    # =========================================================================
    # PIECE CONTROL (không đổi logic, giữ nguyên)
    # =========================================================================

    @staticmethod
    def rook_control(board, row, col):
        squares = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row + dr, col + dc
            while FeatureExtractor.in_bounds(r, c):
                squares.append((r, c))
                if board.board[r][c] != EMPTY:
                    break
                r += dr
                c += dc
        return squares

    @staticmethod
    def cannon_control(board, row, col):
        squares = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row + dr, col + dc
            jumped = False
            while FeatureExtractor.in_bounds(r, c):
                if not jumped:
                    squares.append((r, c))
                    if board.board[r][c] != EMPTY:
                        jumped = True
                else:
                    if board.board[r][c] != EMPTY:
                        squares.append((r, c))
                        break
                r += dr
                c += dc
        return squares

    @staticmethod
    def knight_control(board, row, col):
        squares = []
        knight_moves = [
            (-2, -1, -1, 0), (-2, 1, -1, 0),
            (2, -1,  1, 0),  (2,  1,  1, 0),
            (-1, -2, 0, -1), (1, -2, 0, -1),
            (-1,  2, 0,  1), (1,  2, 0,  1),
        ]
        for dr, dc, lr, lc in knight_moves:
            leg_r, leg_c = row + lr, col + lc
            nr, nc = row + dr, col + dc
            if not FeatureExtractor.in_bounds(nr, nc):
                continue
            if not FeatureExtractor.in_bounds(leg_r, leg_c):
                continue
            if board.board[leg_r][leg_c] != EMPTY:
                continue
            squares.append((nr, nc))
        return squares

    @staticmethod
    def pawn_control(piece, row, col):
        squares = []
        if piece.color == RED:
            forward = -1
            crossed_river = row <= 4
        else:
            forward = 1
            crossed_river = row >= 5

        nr = row + forward
        if FeatureExtractor.in_bounds(nr, col):
            squares.append((nr, col))

        if crossed_river:
            for dc in [-1, 1]:
                nc = col + dc
                if FeatureExtractor.in_bounds(row, nc):
                    squares.append((row, nc))
        return squares

    @staticmethod
    def king_control(row, col):
        squares = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if FeatureExtractor.in_bounds(nr, nc):
                squares.append((nr, nc))
        return squares

    @staticmethod
    def advisor_control(row, col):
        squares = []
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row + dr, col + dc
            if FeatureExtractor.in_bounds(nr, nc):
                squares.append((nr, nc))
        return squares

    @staticmethod
    def elephant_control(board, piece, row, col):
        squares = []
        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            nr, nc = row + dr, col + dc
            eye_r, eye_c = row + dr // 2, col + dc // 2
            if not FeatureExtractor.in_bounds(nr, nc):
                continue
            if board.board[eye_r][eye_c] != EMPTY:
                continue
            if piece.color == RED and nr < 5:
                continue
            if piece.color == BLACK and nr > 4:
                continue
            squares.append((nr, nc))
        return squares

    @staticmethod
    def piece_control(board, piece, row, col):
        p = piece.piece_type
        if p == ROOK:     return FeatureExtractor.rook_control(board, row, col)
        if p == CANNON:   return FeatureExtractor.cannon_control(board, row, col)
        if p == KNIGHT:   return FeatureExtractor.knight_control(board, row, col)
        if p == PAWN:     return FeatureExtractor.pawn_control(piece, row, col)
        if p == KING:     return FeatureExtractor.king_control(row, col)
        if p == ADVISOR:  return FeatureExtractor.advisor_control(row, col)
        if p == ELEPHANT: return FeatureExtractor.elephant_control(board, piece, row, col)
        return []

    # =========================================================================
    # FEATURE 1: MATERIAL — không thay đổi, đã tốt
    # =========================================================================

    @staticmethod
    def extract_material(board):
        red_score = 0
        black_score = 0
        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue
                value = PIECE_VALUES[piece.piece_type]
                if piece.color == RED:
                    red_score += value
                else:
                    black_score += value
        return red_score - black_score

    # =========================================================================
    # FEATURE 2: PST — dùng bảng lookup thay vì công thức
    # =========================================================================

    @staticmethod
    def extract_pst(board):
        """
        Dùng bảng PST cứng thay vì công thức.
        Bảng được xây dựng từ góc nhìn của đỏ,
        đen được chuẩn hoá bằng normalize_row.
        """
        red_score = 0
        black_score = 0

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                table = PST_MAP.get(piece.piece_type)
                if table is None:
                    continue

                nr = FeatureExtractor.normalize_row(piece, r)
                bonus = table[nr][c]

                if piece.color == RED:
                    red_score += bonus
                else:
                    black_score += bonus

        return red_score - black_score

    # =========================================================================
    # FEATURE 3: MOBILITY — đã có nhưng chưa được gọi, sửa trọng số
    # =========================================================================

    @staticmethod
    def extract_mobility(board):
        """
        Đánh giá số ô mỗi quân kiểm soát được, nhân với trọng số.
        Xe và pháo được ưu tiên cao hơn vì cơ động nhiều = uy hiếp nhiều.
        """
        red_score = 0
        black_score = 0

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                controls = FeatureExtractor.piece_control(board, piece, r, c)
                weight = MOBILITY_WEIGHT.get(piece.piece_type, 1)
                score = len(controls) * weight

                if piece.color == RED:
                    red_score += score
                else:
                    black_score += score

        return red_score - black_score

    # =========================================================================
    # FEATURE 4: PAWN STRUCTURE — bỏ phần trùng với PST
    # =========================================================================

    @staticmethod
    def extract_pawn_structure(board):
        """
        Chỉ đánh giá cấu trúc tốt thuần túy:
        - Phạt tốt chồng cột (doubled pawns)
        - Thưởng tốt liên kết (connected pawns — cùng hàng, kề cột)
        PST đã lo bonus vị trí, không tính lại ở đây.
        """
        red_score = 0
        black_score = 0

        red_pawns   = []  # list (row, col)
        black_pawns = []

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY or piece.piece_type != PAWN:
                    continue
                if piece.color == RED:
                    red_pawns.append((r, c))
                else:
                    black_pawns.append((r, c))

        def evaluate_pawns(pawns, color):
            score = 0
            # Doubled pawn penalty
            from collections import Counter
            col_count = Counter(c for _, c in pawns)
            for count in col_count.values():
                if count > 1:
                    score -= (count - 1) * 10

            # Connected pawn bonus: 2 tốt cùng hàng, cột kề nhau
            crossed = [
                (r, c) for r, c in pawns
                if (color == RED and r <= 4) or (color == BLACK and r >= 5)
            ]
            crossed_set = set(crossed)
            for r, c in crossed:
                if (r, c - 1) in crossed_set or (r, c + 1) in crossed_set:
                    score += 15

            return score

        red_score   = evaluate_pawns(red_pawns,   RED)
        black_score = evaluate_pawns(black_pawns, BLACK)

        return red_score - black_score

    # =========================================================================
    # FEATURE 5: KING SAFETY — nâng cấp toàn diện
    # =========================================================================

    @staticmethod
    def extract_king_safety(board):
        """
        Đánh giá an toàn vua gồm:
        1. Số sĩ/tượng còn lại
        2. Sĩ ở vị trí lý tưởng
        3. Vua ở giữa cung (cột 4)
        4. Phạt nặng nếu vua ra ngoài cung (lỗi logic game)
        5. Phạt vùng xung quanh vua bị tấn công bởi quân địch
        """
        red_king_pos   = None
        black_king_pos = None
        red_guard      = 0
        black_guard    = 0
        red_advisor_positions   = []
        black_advisor_positions = []

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                if piece.piece_type == KING:
                    if piece.color == RED:
                        red_king_pos = (r, c)
                    else:
                        black_king_pos = (r, c)

                if piece.piece_type in (ADVISOR, ELEPHANT):
                    if piece.color == RED:
                        red_guard += 1
                    else:
                        black_guard += 1

                if piece.piece_type == ADVISOR:
                    if piece.color == RED:
                        red_advisor_positions.append((r, c))
                    else:
                        black_advisor_positions.append((r, c))

        red_score   = red_guard   * 12
        black_score = black_guard * 12

        # Sĩ ở vị trí lý tưởng
        for pos in red_advisor_positions:
            if pos in RED_ADVISOR_IDEAL:
                red_score += 10
        for pos in black_advisor_positions:
            if pos in BLACK_ADVISOR_IDEAL:
                black_score += 10

        # Vua ở giữa cung
        if red_king_pos   and red_king_pos[1]   == 4:
            red_score   += 8
        if black_king_pos and black_king_pos[1] == 4:
            black_score += 8

        # Phạt vua ra ngoài cung (không hợp lệ trong cờ tướng)
        if red_king_pos   and red_king_pos   not in RED_PALACE:
            red_score   -= 200
        if black_king_pos and black_king_pos not in BLACK_PALACE:
            black_score -= 200

        # Phạt vùng xung quanh vua bị quân địch tấn công
        red_zone_attacked   = 0
        black_zone_attacked = 0

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                controls = FeatureExtractor.piece_control(board, piece, r, c)
                controls_set = set(controls)

                if piece.color == BLACK and red_king_pos is not None:
                    kr, kc = red_king_pos
                    # Đếm ô trong vùng 1 bước quanh vua đỏ bị tấn công
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if (kr + dr, kc + dc) in controls_set:
                                red_zone_attacked += 1

                if piece.color == RED and black_king_pos is not None:
                    kr, kc = black_king_pos
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if (kr + dr, kc + dc) in controls_set:
                                black_zone_attacked += 1

        red_score   -= red_zone_attacked   * 8
        black_score -= black_zone_attacked * 8

        return red_score - black_score

    # =========================================================================
    # FEATURE 6: FLYING GENERAL — hoàn toàn mới
    # =========================================================================

    @staticmethod
    def extract_flying_general(board):
        """
        Phát hiện trạng thái 'phi tướng': hai vua đối mặt trực tiếp trên
        cùng một cột mà không có quân nào chắn giữa.
        Đây là trạng thái bất hợp lệ/cực kỳ nguy hiểm → phạt nặng.

        Trả về âm nếu đỏ đang bị flying general (bất lợi cho đỏ),
        dương nếu đen đang bị.
        """
        red_king_pos   = None
        black_king_pos = None

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY or piece.piece_type != KING:
                    continue
                if piece.color == RED:
                    red_king_pos = (r, c)
                else:
                    black_king_pos = (r, c)

        if red_king_pos is None or black_king_pos is None:
            return 0

        rr, rc = red_king_pos
        br, bc = black_king_pos

        if rc != bc:
            return 0  # Khác cột → không bao giờ flying general

        # Đếm quân giữa hai vua trên cùng cột
        min_row = min(rr, br) + 1
        max_row = max(rr, br)
        pieces_between = 0
        for row in range(min_row, max_row):
            if board.board[row][rc] != EMPTY:
                pieces_between += 1

        if pieces_between == 0:
            # Hai vua đối mặt — trạng thái bất hợp lệ
            # Phạt bên nào đang đến lượt (gây ra tình trạng này)
            return -500

        return 0

    # =========================================================================
    # FEATURE 7: THREAT DETECTION — hoàn toàn mới
    # =========================================================================

    @staticmethod
    def extract_threats(board):
        """
        Đánh giá các mối đe doạ trên bàn cờ:
        - Quân bị tấn công mà không có quân bảo vệ → bị "treo"
        - Quân giá trị cao bị tấn công bởi quân giá trị thấp → bị trao đổi bất lợi

        Trả về điểm lợi thế cho đỏ (dương = đỏ lợi).
        """
        # Tính tập hợp ô bị tấn công bởi mỗi bên
        red_attacks   = set()
        black_attacks = set()

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue
                controls = FeatureExtractor.piece_control(board, piece, r, c)
                if piece.color == RED:
                    red_attacks.update(controls)
                else:
                    black_attacks.update(controls)

        red_score   = 0
        black_score = 0

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY or piece.piece_type == KING:
                    continue

                piece_val = PIECE_VALUES.get(piece.piece_type, 0)
                is_attacked_by_enemy = (
                    (piece.color == RED   and (r, c) in black_attacks) or
                    (piece.color == BLACK and (r, c) in red_attacks)
                )
                is_defended_by_own = (
                    (piece.color == RED   and (r, c) in red_attacks) or
                    (piece.color == BLACK and (r, c) in black_attacks)
                )

                if is_attacked_by_enemy and not is_defended_by_own:
                    # Quân bị treo (hanging piece) — phạt bên sở hữu
                    penalty = piece_val // 8
                    if piece.color == RED:
                        red_score   -= penalty
                    else:
                        black_score -= penalty

                elif is_attacked_by_enemy and is_defended_by_own:
                    # Quân bị tấn công nhưng có bảo vệ — phạt nhẹ hơn
                    penalty = piece_val // 20
                    if piece.color == RED:
                        red_score   -= penalty
                    else:
                        black_score -= penalty

        return red_score - black_score

    # =========================================================================
    # FEATURE 8: GAME PHASE — hoàn toàn mới
    # =========================================================================

    @staticmethod
    def get_game_phase(board):
        """
        Trả về giá trị phase trong [0.0, 1.0]:
        - 1.0 = khai cuộc (nhiều quân)
        - 0.0 = tàn cuộc (ít quân)

        Dùng để blend trọng số feature theo giai đoạn ván đấu.
        """
        max_material = (
            2 * PIECE_VALUES[ROOK]   +
            2 * PIECE_VALUES[KNIGHT] +
            2 * PIECE_VALUES[CANNON] +
            5 * PIECE_VALUES[PAWN]   +
            2 * PIECE_VALUES[ADVISOR] +
            2 * PIECE_VALUES[ELEPHANT]
        ) * 2  # cả 2 bên

        current_material = 0
        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY or piece.piece_type == KING:
                    continue
                current_material += PIECE_VALUES.get(piece.piece_type, 0)

        return min(1.0, current_material / max_material)

    # =========================================================================
    # EXTRACT ALL — tổng hợp tất cả features
    # =========================================================================

    @staticmethod
    def extract_all(board):
        """
        Trả về dict tất cả features. Evaluation.evaluate() sẽ dùng dict này
        để tính tổng điểm có trọng số.
        """
        phase = FeatureExtractor.get_game_phase(board)

        return {
            "material":       FeatureExtractor.extract_material(board),
            "pst":            FeatureExtractor.extract_pst(board),
            "mobility":       FeatureExtractor.extract_mobility(board),      # đã có nhưng bị bỏ quên
            "king_safety":    FeatureExtractor.extract_king_safety(board),
            "pawn_structure": FeatureExtractor.extract_pawn_structure(board),
            "flying_general": FeatureExtractor.extract_flying_general(board),  # mới
            "threats":        FeatureExtractor.extract_threats(board),          # mới
            "phase":          phase,                                             # mới — dùng để blend
        }