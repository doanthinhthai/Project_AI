from core.constants import (
    BOARD_ROWS, BOARD_COLS,
    RED, BLACK, EMPTY,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN,
    PALACE_COLS, RED_PALACE_ROWS, BLACK_PALACE_ROWS,
    RED_FORWARD, BLACK_FORWARD
)
from game.moves import Move


class Rules:
    def __init__(self, board):
        self.board = board

    def is_inside_board(self, row, col):
        return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS

    def is_empty(self, row, col):
        return self.board.board[row][col] == EMPTY

    def is_enemy(self, row, col, color):
        piece = self.board.board[row][col]
        return piece != EMPTY and piece.color != color

    def is_friend(self, row, col, color):
        piece = self.board.board[row][col]
        return piece != EMPTY and piece.color == color

    def get_valid_moves(self, row, col):
        piece = self.board.get_piece(row, col)

        if piece == EMPTY:
            return []

        piece_type = piece.piece_type

        if piece_type == KING:
            return self.get_king_moves(row, col, piece.color)
        elif piece_type == ADVISOR:
            return self.get_advisor_moves(row, col, piece.color)
        elif piece_type == ELEPHANT:
            return self.get_elephant_moves(row, col, piece.color)
        elif piece_type == ROOK:
            return self.get_rook_moves(row, col, piece.color)
        elif piece_type == KNIGHT:
            return self.get_knight_moves(row, col, piece.color)
        elif piece_type == CANNON:
            return self.get_cannon_moves(row, col, piece.color)
        elif piece_type == PAWN:
            return self.get_pawn_moves(row, col, piece.color)

        return []

    def add_move_if_valid(self, moves, start_row, start_col, end_row, end_col, color):
        if not self.is_inside_board(end_row, end_col):
            return

        if self.is_friend(end_row, end_col, color):
            return

        move = Move((start_row, start_col), (end_row, end_col), self.board.board)
        moves.append(move)

    # KING
    def get_king_moves(self, row, col, color):
        moves = []

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        palace_rows = RED_PALACE_ROWS if color == RED else BLACK_PALACE_ROWS

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if new_row in palace_rows and new_col in PALACE_COLS:
                self.add_move_if_valid(moves, row, col, new_row, new_col, color)

        return moves

    # ADVISOR
    def get_advisor_moves(self, row, col, color):
        moves = []

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        palace_rows = RED_PALACE_ROWS if color == RED else BLACK_PALACE_ROWS

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if new_row in palace_rows and new_col in PALACE_COLS:
                self.add_move_if_valid(moves, row, col, new_row, new_col, color)

        return moves

    # ELEPHANT
    def get_elephant_moves(self, row, col, color):
        moves = []

        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if not self.is_inside_board(new_row, new_col):
                continue

            # Không qua sông
            if color == RED and new_row < 5:
                continue
            if color == BLACK and new_row > 4:
                continue

            # Kiểm tra mắt tượng
            eye_row = row + dr // 2
            eye_col = col + dc // 2

            if not self.is_empty(eye_row, eye_col):
                continue

            self.add_move_if_valid(moves, row, col, new_row, new_col, color)

        return moves

    # ROOK
    def get_rook_moves(self, row, col, color):
        moves = []

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            while self.is_inside_board(new_row, new_col):
                if self.is_empty(new_row, new_col):
                    moves.append(Move((row, col), (new_row, new_col), self.board.board))
                else:
                    if self.is_enemy(new_row, new_col, color):
                        moves.append(Move((row, col), (new_row, new_col), self.board.board))
                    break

                new_row += dr
                new_col += dc

        return moves

    # KNIGHT
    def get_knight_moves(self, row, col, color):
        moves = []

        knight_steps = [
            (-2, -1, -1, 0),
            (-2, 1, -1, 0),
            (2, -1, 1, 0),
            (2, 1, 1, 0),
            (-1, -2, 0, -1),
            (1, -2, 0, -1),
            (-1, 2, 0, 1),
            (1, 2, 0, 1),
        ]

        for dr, dc, leg_r, leg_c in knight_steps:
            leg_row = row + leg_r
            leg_col = col + leg_c
            new_row = row + dr
            new_col = col + dc

            if not self.is_inside_board(new_row, new_col):
                continue

            # Kiểm tra chặn chân mã
            if not self.is_empty(leg_row, leg_col):
                continue

            self.add_move_if_valid(moves, row, col, new_row, new_col, color)

        return moves

    # CANNON
    def get_cannon_moves(self, row, col, color):
        moves = []

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            jumped = False

            while self.is_inside_board(new_row, new_col):
                if not jumped:
                    if self.is_empty(new_row, new_col):
                        # Pháo đi như xe khi chưa nhảy qua quân nào
                        moves.append(Move((row, col), (new_row, new_col), self.board.board))
                    else:
                        jumped = True
                else:
                    # Sau khi đã nhảy qua đúng 1 quân, chỉ được ăn quân đầu tiên gặp
                    if not self.is_empty(new_row, new_col):
                        if self.is_enemy(new_row, new_col, color):
                            moves.append(Move((row, col), (new_row, new_col), self.board.board))
                        break

                new_row += dr
                new_col += dc

        return moves

    # PAWN
    def get_pawn_moves(self, row, col, color):
        moves = []

        forward = RED_FORWARD if color == RED else BLACK_FORWARD

        # Đi thẳng
        new_row = row + forward
        new_col = col
        if self.is_inside_board(new_row, new_col):
            self.add_move_if_valid(moves, row, col, new_row, new_col, color)

        # Qua sông mới được đi ngang
        crossed_river = (color == RED and row <= 4) or (color == BLACK and row >= 5)

        if crossed_river:
            for dc in [-1, 1]:
                new_row = row
                new_col = col + dc
                if self.is_inside_board(new_row, new_col):
                    self.add_move_if_valid(moves, row, col, new_row, new_col, color)

        return moves

    # ALL MOVES OF ONE SIDE
    def get_all_valid_moves(self, color):
        all_moves = []

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece != EMPTY and piece.color == color:
                    all_moves.extend(self.get_valid_moves(row, col))

        return all_moves