from core.constants import (
    BOARD_ROWS, BOARD_COLS,
    RED, BLACK, EMPTY,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN
)
from game.piece import Piece


class Board:
    def __init__(self):
        self.board = [[EMPTY for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.move_log = []
        self.setup_board()

    def setup_board(self):
        """Khởi tạo vị trí ban đầu của bàn cờ tướng"""

        # BLACK SIDE
        self.board[0][0] = Piece(ROOK, BLACK, 0, 0)
        self.board[0][1] = Piece(KNIGHT, BLACK, 0, 1)
        self.board[0][2] = Piece(ELEPHANT, BLACK, 0, 2)
        self.board[0][3] = Piece(ADVISOR, BLACK, 0, 3)
        self.board[0][4] = Piece(KING, BLACK, 0, 4)
        self.board[0][5] = Piece(ADVISOR, BLACK, 0, 5)
        self.board[0][6] = Piece(ELEPHANT, BLACK, 0, 6)
        self.board[0][7] = Piece(KNIGHT, BLACK, 0, 7)
        self.board[0][8] = Piece(ROOK, BLACK, 0, 8)

        self.board[2][1] = Piece(CANNON, BLACK, 2, 1)
        self.board[2][7] = Piece(CANNON, BLACK, 2, 7)

        self.board[3][0] = Piece(PAWN, BLACK, 3, 0)
        self.board[3][2] = Piece(PAWN, BLACK, 3, 2)
        self.board[3][4] = Piece(PAWN, BLACK, 3, 4)
        self.board[3][6] = Piece(PAWN, BLACK, 3, 6)
        self.board[3][8] = Piece(PAWN, BLACK, 3, 8)

        # RED SIDE
        self.board[9][0] = Piece(ROOK, RED, 9, 0)
        self.board[9][1] = Piece(KNIGHT, RED, 9, 1)
        self.board[9][2] = Piece(ELEPHANT, RED, 9, 2)
        self.board[9][3] = Piece(ADVISOR, RED, 9, 3)
        self.board[9][4] = Piece(KING, RED, 9, 4)
        self.board[9][5] = Piece(ADVISOR, RED, 9, 5)
        self.board[9][6] = Piece(ELEPHANT, RED, 9, 6)
        self.board[9][7] = Piece(KNIGHT, RED, 9, 7)
        self.board[9][8] = Piece(ROOK, RED, 9, 8)

        self.board[7][1] = Piece(CANNON, RED, 7, 1)
        self.board[7][7] = Piece(CANNON, RED, 7, 7)

        self.board[6][0] = Piece(PAWN, RED, 6, 0)
        self.board[6][2] = Piece(PAWN, RED, 6, 2)
        self.board[6][4] = Piece(PAWN, RED, 6, 4)
        self.board[6][6] = Piece(PAWN, RED, 6, 6)
        self.board[6][8] = Piece(PAWN, RED, 6, 8)

    def get_piece(self, row, col):
        """Lấy quân tại một ô"""
        return self.board[row][col]

    def set_piece(self, row, col, piece):
        """Đặt quân vào một ô"""
        self.board[row][col] = piece
        if piece != EMPTY:
            piece.set_position(row, col)

    def is_empty(self, row, col):
        """Kiểm tra ô có trống không"""
        return self.board[row][col] == EMPTY

    def get_all_pieces(self):
        """Trả về danh sách tất cả quân cờ để renderer vẽ"""
        pieces = []
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece != EMPTY:
                    pieces.append(piece)
        return pieces

    def make_move(self, move):
        """
        Thực hiện một nước đi.
        move.piece_moved và move.piece_captured được lấy từ board trước đó.
        """
        moved_piece = self.board[move.start_row][move.start_col]

        self.board[move.start_row][move.start_col] = EMPTY
        self.board[move.end_row][move.end_col] = moved_piece

        if moved_piece != EMPTY:
            moved_piece.set_position(move.end_row, move.end_col)

        self.move_log.append(move)

    def undo_move(self):
        """Hoàn tác nước đi gần nhất"""
        if not self.move_log:
            return

        move = self.move_log.pop()

        moved_piece = self.board[move.end_row][move.end_col]

        self.board[move.start_row][move.start_col] = moved_piece
        self.board[move.end_row][move.end_col] = move.piece_captured

        if moved_piece != EMPTY:
            moved_piece.set_position(move.start_row, move.start_col)

        if move.piece_captured != EMPTY:
            move.piece_captured.set_position(move.end_row, move.end_col)

    def get_board_matrix(self):
        """Trả về ma trận bàn cờ hiện tại"""
        return self.board

    def reset_board(self):
        """Reset bàn cờ về trạng thái ban đầu"""
        self.board = [[EMPTY for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.move_log = []
        self.setup_board()

    def print_board(self):
        """In bàn cờ ra console để debug"""
        for row in range(BOARD_ROWS):
            row_data = []
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece == EMPTY:
                    row_data.append(".")
                else:
                    symbol = piece.piece_type.lower() if piece.color == BLACK else piece.piece_type
                    row_data.append(symbol)
            print(" ".join(row_data))
