from core.constants import (
    PIECE_VALUES, RED, BLACK, EMPTY,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN
)


class Evaluation:

    @staticmethod
    def get_position_bonus(piece, row, col):
        normalized_row = row if piece.color == RED else 9 - row
        center_distance = abs(col - 4)

        if piece.piece_type == PAWN:
            bonus = 0
            if normalized_row <= 4:
                bonus += 40
            bonus += (6 - normalized_row) * 5
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
    def evaluate(board):
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

        return score