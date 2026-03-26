from core.constants import PIECE_VALUES, RED, BLACK, EMPTY


class Evaluation:

    @staticmethod
    def evaluate(board):
        score = 0

        for row_idx in range(len(board.board)):
            for col_idx in range(len(board.board[row_idx])):
                piece = board.board[row_idx][col_idx]

                if piece == EMPTY:
                    continue

                base_value = PIECE_VALUES[piece.piece_type]

                # bonus vị trí (đơn giản)
                positional_bonus = 0

                # Pawn qua sông mạnh hơn
                if piece.piece_type == "P":
                    if piece.color == RED and row_idx <= 4:
                        positional_bonus = 30
                    elif piece.color == BLACK and row_idx >= 5:
                        positional_bonus = 30

                value = base_value + positional_bonus

                if piece.color == RED:
                    score += value
                else:
                    score -= value

        return score