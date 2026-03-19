from core.constants import EMPTY


class Move:
    def __init__(self, start_pos, end_pos, board):
        self.start_row = start_pos[0]
        self.start_col = start_pos[1]
        self.end_row = end_pos[0]
        self.end_col = end_pos[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.move_id = (
            self.start_row * 1000
            + self.start_col * 100
            + self.end_row * 10
            + self.end_col
        )

    def __eq__(self, other):
        return isinstance(other, Move) and self.move_id == other.move_id

    def is_capture(self):
        return self.piece_captured != EMPTY

    def get_chess_notation(self):
        return f"({self.start_row}, {self.start_col}) -> ({self.end_row}, {self.end_col})"

    def __str__(self):
        moved = self.piece_moved.piece_type if self.piece_moved != EMPTY else "?"
        if self.is_capture():
            captured = self.piece_captured.piece_type
            return f"[{moved}] từ ({self.start_row}, {self.start_col}) đến ({self.end_row}, {self.end_col}) ăn [{captured}]"
        return f"[{moved}] từ ({self.start_row}, {self.start_col}) đến ({self.end_row}, {self.end_col})"