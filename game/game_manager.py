from core.constants import (
    RED, BLACK, EMPTY, KING,
    BOARD_ROWS, BOARD_COLS,
    RED_WIN, BLACK_WIN, ONGOING
)
from game.rules import Rules


class GameManager:
    def __init__(self, board, ai_engine=None):
        self.board = board
        self.rules = Rules(board)
        self.ai_engine = ai_engine

        self.current_turn = RED
        self.selected_piece = None
        self.valid_moves = []
        self.game_state = ONGOING
        self.status_message = "Lượt của: ĐỎ"

    def reset_selection(self):
        self.selected_piece = None
        self.valid_moves = []

    def switch_turn(self):
        self.current_turn = BLACK if self.current_turn == RED else RED
        turn_text = "ĐỎ" if self.current_turn == RED else "ĐEN"
        self.status_message = f"Lượt của: {turn_text}"

    def get_status_text(self):
        if self.game_state == RED_WIN:
            return "ĐỎ THẮNG!"
        elif self.game_state == BLACK_WIN:
            return "ĐEN THẮNG!"
        return self.status_message

    def undo_last_move(self):
        if self.ai_engine is not None:
            if len(self.board.move_log) >= 2:
                self.board.undo_move()
                self.board.undo_move()
                self.current_turn = RED
                self.status_message = "Lượt của: ĐỎ"
        else:
            if len(self.board.move_log) >= 1:
                self.board.undo_move()
                self.switch_turn()

        self.reset_selection()
        self.game_state = ONGOING

    def get_clicked_square(self, mx, my, ox, oy, cs):
        col = round((mx - ox) / cs)
        row = round((my - oy) / cs)
        return row, col

    def is_inside_board(self, row, col):
        return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS

    def is_in_check(self, color):
        king_pos = None
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.piece_type == KING and p.color == color:
                    king_pos = (r, c)
                    break
            if king_pos is not None:
                break

        if king_pos is None:
            return False

        enemy_color = -color
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.color == enemy_color:
                    moves = self.rules.get_valid_moves(r, c)
                    for m in moves:
                        if (m.end_row, m.end_col) == king_pos:
                            return True
        return False

    def kings_face_each_other(self):
        red_king = None
        black_king = None

        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.piece_type == KING:
                    if p.color == RED:
                        red_king = (r, c)
                    else:
                        black_king = (r, c)

        if red_king is None or black_king is None:
            return False

        if red_king[1] != black_king[1]:
            return False

        col = red_king[1]
        start = min(red_king[0], black_king[0]) + 1
        end = max(red_king[0], black_king[0])

        for r in range(start, end):
            if self.board.get_piece(r, col) != EMPTY:
                return False

        return True

    def get_legal_moves(self, row, col):
        piece = self.board.get_piece(row, col)
        if piece == EMPTY:
            return []

        candidate_moves = self.rules.get_valid_moves(row, col)
        legal_moves = []

        for move in candidate_moves:
            self.board.make_move(move)
            if not self.is_in_check(piece.color) and not self.kings_face_each_other():
                legal_moves.append(move)
            self.board.undo_move()

        return legal_moves

    def check_game_over(self):
        king_red = False
        king_black = False

        for piece in self.board.get_all_pieces():
            if piece.piece_type == KING:
                if piece.color == RED:
                    king_red = True
                elif piece.color == BLACK:
                    king_black = True

        if not king_red:
            self.game_state = BLACK_WIN
        elif not king_black:
            self.game_state = RED_WIN

    def handle_ai_turn(self):
        if self.ai_engine is None or self.game_state != ONGOING:
            return

        ai_move = self.ai_engine.get_best_move(self.board)
        if ai_move:
            self.board.make_move(ai_move)
            self.check_game_over()
            if self.game_state == ONGOING:
                self.switch_turn()

    def handle_mouse_click(self, mouse_x, mouse_y, offset_x, offset_y, cell_size):
        if self.game_state != ONGOING:
            return

        row, col = self.get_clicked_square(mouse_x, mouse_y, offset_x, offset_y, cell_size)

        if not self.is_inside_board(row, col):
            return

        clicked_piece = self.board.get_piece(row, col)

        if self.selected_piece is None:
            if clicked_piece != EMPTY and clicked_piece.color == self.current_turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_legal_moves(row, col)
            return

        chosen_move = next(
            (m for m in self.valid_moves if m.end_row == row and m.end_col == col),
            None
        )

        if chosen_move:
            self.board.make_move(chosen_move)
            self.check_game_over()
            self.reset_selection()

            if self.game_state == ONGOING:
                self.switch_turn()
                if self.current_turn == BLACK and self.ai_engine is not None:
                    self.handle_ai_turn()
            return

        if clicked_piece != EMPTY and clicked_piece.color == self.current_turn:
            self.selected_piece = (row, col)
            self.valid_moves = self.get_legal_moves(row, col)
        else:
            self.reset_selection()
    def get_valid_moves(self):
        return self.valid_moves

    def get_selected_piece(self):
        return self.selected_piece