from core.constants import (
    PIECE_VALUES, RED, BLACK, EMPTY,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN
)


class Evaluation:
    @staticmethod
    def get_position_bonus(piece, row, col):
        # Chuẩn hóa về góc nhìn phe ĐỎ
        normalized_row = row if piece.color == RED else 9 - row
        center_distance = abs(col - 4)

        if piece.piece_type == PAWN:
            bonus = 0

            # Qua sông mạnh hơn
            if normalized_row <= 4:
                bonus += 40

            # Tiến càng sâu càng mạnh
            bonus += (6 - normalized_row) * 5

            # Gần trung tâm tốt hơn
            bonus += max(0, 4 - center_distance) * 3
            return bonus

        if piece.piece_type == ROOK:
            bonus = 20
            bonus += max(0, 4 - center_distance) * 4
            bonus += (6 - normalized_row) * 2
            return bonus

        if piece.piece_type == KNIGHT:
            bonus = 15
            bonus += max(0, 4 - center_distance) * 6
            bonus += (6 - normalized_row) * 2
            return bonus

        if piece.piece_type == CANNON:
            bonus = 15
            bonus += max(0, 4 - center_distance) * 5
            bonus += (6 - normalized_row) * 2
            return bonus

        if piece.piece_type == ELEPHANT:
            bonus = 8
            if normalized_row in [7, 9]:
                bonus += 4
            return bonus

        if piece.piece_type == ADVISOR:
            bonus = 8
            if col in [3, 4, 5]:
                bonus += 4
            return bonus

        if piece.piece_type == KING:
            bonus = 0
            if col == 4:
                bonus += 10
            return bonus

        return 0

    @staticmethod
    def get_mobility_bonus(board):
        red_mobility = 0
        black_mobility = 0

        for row in range(len(board.board)):
            for col in range(len(board.board[row])):
                piece = board.board[row][col]

                if piece == EMPTY:
                    continue

                move_count = 0

                if piece.piece_type == ROOK:
                    move_count += 4
                elif piece.piece_type == KNIGHT:
                    move_count += 3
                elif piece.piece_type == CANNON:
                    move_count += 4
                elif piece.piece_type == PAWN:
                    move_count += 2
                else:
                    move_count += 1

                if piece.color == RED:
                    red_mobility += move_count
                else:
                    black_mobility += move_count

        return (red_mobility - black_mobility) * 2

    @staticmethod
    def get_check_bonus(board, game_manager=None):
        if game_manager is None:
            return 0

        bonus = 0

        if game_manager.is_in_check(BLACK):
            bonus += 50

        if game_manager.is_in_check(RED):
            bonus -= 50

        return bonus

    @staticmethod
    def evaluate(board, game_manager=None):
        score = 0

        for row in range(len(board.board)):
            for col in range(len(board.board[row])):
                piece = board.board[row][col]

                if piece == EMPTY:
                    continue

                base_value = PIECE_VALUES[piece.piece_type]
                positional_bonus = Evaluation.get_position_bonus(piece, row, col)
                value = base_value + positional_bonus

                if piece.color == RED:
                    score += value
                else:
                    score -= value

        score += Evaluation.get_mobility_bonus(board)
        score += Evaluation.get_check_bonus(board, game_manager)

        return score