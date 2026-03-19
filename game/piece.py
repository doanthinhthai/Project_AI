class Piece:
    def __init__(self, piece_type, color, row, col):
        self.piece_type = piece_type
        self.color = color
        self.row = row
        self.col = col

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_position(self):
        return self.row, self.col

    def __repr__(self):
        side = "RED" if self.color == 1 else "BLACK"
        return f"Piece({self.piece_type}, {side}, {self.row}, {self.col})"