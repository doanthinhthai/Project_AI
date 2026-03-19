import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Const.Values import *

class Move:
    def __init__(self, start_pos, end_pos, board):
        self.start_row = start_pos[0]
        self.start_col = start_pos[1]
        self.end_row = end_pos[0]
        self.end_col = end_pos[1]

        self.piece_moved = board[self.start_row][self.start_col]
        
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return f"{self.piece_moved}{self.start_col}{self.start_row} to {self.end_col}{self.end_row}"

    def is_capture(self):
        return self.piece_captured != EMPTY

    def __str__(self):
        capture_str = f" ăn {self.piece_captured}" if self.is_capture() else " di chuyển"
        return f"[{self.piece_moved}] từ ({self.start_row},{self.start_col}) đến ({self.end_row},{self.end_col}){capture_str}"
