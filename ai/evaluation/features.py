from core.constants import (
    RED, BLACK, EMPTY,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN,
    PIECE_VALUES
)


class FeatureExtractor:
    @staticmethod
    def in_bounds(r, c):
        return 0 <= r < 10 and 0 <= c < 9

    @staticmethod
    def normalize_row(piece, row):
        return row if piece.color == RED else 9 - row

    @staticmethod
    def get_piece_square_bonus(piece, row, col):
        """
        Tạm thời viết đơn giản.
        Sau này bạn có thể thay bằng PIECE_SQUARE_TABLE thật.
        """
        nr = FeatureExtractor.normalize_row(piece, row)
        center_distance = abs(col - 4)

        if piece.piece_type == PAWN:
            bonus = 0
            if nr <= 4:   # qua sông
                bonus += 20
            bonus += max(0, 5 - nr) * 4
            bonus += max(0, 4 - center_distance) * 2
            return bonus

        if piece.piece_type == ROOK:
            return 10 + max(0, 4 - center_distance) * 3

        if piece.piece_type == KNIGHT:
            return max(0, 4 - center_distance) * 4

        if piece.piece_type == CANNON:
            return max(0, 4 - center_distance) * 3

        if piece.piece_type == ADVISOR:
            return 8

        if piece.piece_type == ELEPHANT:
            return 6

        if piece.piece_type == KING:
            return 0

        return 0

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
            (2, -1, 1, 0), (2, 1, 1, 0),
            (-1, -2, 0, -1), (1, -2, 0, -1),
            (-1, 2, 0, 1), (1, 2, 0, 1),
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
        moves = [(-2, -2), (-2, 2), (2, -2), (2, 2)]

        for dr, dc in moves:
            nr, nc = row + dr, col + dc
            eye_r, eye_c = row + dr // 2, col + dc // 2

            if not FeatureExtractor.in_bounds(nr, nc):
                continue
            if board.board[eye_r][eye_c] != EMPTY:
                continue

            # tượng không qua sông
            if piece.color == RED and nr < 5:
                continue
            if piece.color == BLACK and nr > 4:
                continue

            squares.append((nr, nc))

        return squares

    @staticmethod
    def piece_control(board, piece, row, col):
        p = piece.piece_type

        if p == ROOK:
            return FeatureExtractor.rook_control(board, row, col)
        if p == CANNON:
            return FeatureExtractor.cannon_control(board, row, col)
        if p == KNIGHT:
            return FeatureExtractor.knight_control(board, row, col)
        if p == PAWN:
            return FeatureExtractor.pawn_control(piece, row, col)
        if p == KING:
            return FeatureExtractor.king_control(row, col)
        if p == ADVISOR:
            return FeatureExtractor.advisor_control(row, col)
        if p == ELEPHANT:
            return FeatureExtractor.elephant_control(board, piece, row, col)

        return []

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

    @staticmethod
    def extract_pst(board):
        red_score = 0
        black_score = 0

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                bonus = FeatureExtractor.get_piece_square_bonus(piece, r, c)
                if piece.color == RED:
                    red_score += bonus
                else:
                    black_score += bonus

        return red_score - black_score

    @staticmethod
    def extract_mobility(board):
        red_score = 0
        black_score = 0

        mobility_weight = {
            ROOK: 4,
            CANNON: 3,
            KNIGHT: 3,
            PAWN: 1,
            ADVISOR: 1,
            ELEPHANT: 1,
            KING: 1,
        }

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY:
                    continue

                controls = FeatureExtractor.piece_control(board, piece, r, c)
                score = len(controls) * mobility_weight.get(piece.piece_type, 1)

                if piece.color == RED:
                    red_score += score
                else:
                    black_score += score

        return red_score - black_score

    @staticmethod
    def extract_pawn_structure(board):
        red_score = 0
        black_score = 0

        red_files = {}
        black_files = {}

        for r in range(10):
            for c in range(9):
                piece = board.board[r][c]
                if piece == EMPTY or piece.piece_type != PAWN:
                    continue

                nr = FeatureExtractor.normalize_row(piece, r)

                bonus = 0
                if nr <= 4:  # qua sông
                    bonus += 15
                bonus += max(0, 5 - nr) * 4

                if piece.color == RED:
                    red_score += bonus
                    red_files[c] = red_files.get(c, 0) + 1
                else:
                    black_score += bonus
                    black_files[c] = black_files.get(c, 0) + 1

        # phạt tốt chồng cột
        for count in red_files.values():
            if count > 1:
                red_score -= (count - 1) * 8

        for count in black_files.values():
            if count > 1:
                black_score -= (count - 1) * 8

        return red_score - black_score

    @staticmethod
    def extract_king_safety(board):
        red_king_pos = None
        black_king_pos = None
        red_guard = 0
        black_guard = 0

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

        red_score = red_guard * 12
        black_score = black_guard * 12

        # vua ở giữa cung ổn hơn chút
        if red_king_pos is not None:
            rr, rc = red_king_pos
            if rc == 4:
                red_score += 8

        if black_king_pos is not None:
            br, bc = black_king_pos
            if bc == 4:
                black_score += 8

        return red_score - black_score

    @staticmethod
    def extract_all(board):
        return {
            "material": FeatureExtractor.extract_material(board),
            "pst": FeatureExtractor.extract_pst(board),
            "mobility": FeatureExtractor.extract_mobility(board),
            "king_safety": FeatureExtractor.extract_king_safety(board),
            "pawn_structure": FeatureExtractor.extract_pawn_structure(board),
        }