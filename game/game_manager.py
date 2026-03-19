import pygame
from core.constants import RED, BLACK, EMPTY
from game.rules import Rules
from game.moves import Move


class GameManager:
    def __init__(self, board):
        self.board = board
        self.rules = Rules(board)

        self.current_turn = RED
        self.selected_piece = None
        self.valid_moves = []

    def reset_selection(self):
        self.selected_piece = None
        self.valid_moves = []

    def get_clicked_square(self, mouse_x, mouse_y, board_offset_x, board_offset_y, cell_size):
        col = round((mouse_x - board_offset_x) / cell_size)
        row = round((mouse_y - board_offset_y) / cell_size)
        return row, col

    def is_inside_board(self, row, col):
        return 0 <= row < 10 and 0 <= col < 9

    def handle_mouse_click(self, mouse_x, mouse_y, board_offset_x, board_offset_y, cell_size):
        row, col = self.get_clicked_square(mouse_x, mouse_y, board_offset_x, board_offset_y, cell_size)

        if not self.is_inside_board(row, col):
            return

        clicked_piece = self.board.get_piece(row, col)

        # Nếu chưa chọn quân nào
        if self.selected_piece is None:
            if clicked_piece != EMPTY and clicked_piece.color == self.current_turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.rules.get_valid_moves(row, col)
            return

        # Nếu đã chọn quân rồi
        selected_row, selected_col = self.selected_piece

        # Nếu click lại đúng quân cùng phe khác -> đổi quân được chọn
        if clicked_piece != EMPTY and clicked_piece.color == self.current_turn:
            self.selected_piece = (row, col)
            self.valid_moves = self.rules.get_valid_moves(row, col)
            return

        # Kiểm tra xem ô được click có nằm trong valid_moves không
        chosen_move = None
        for move in self.valid_moves:
            if move.end_row == row and move.end_col == col:
                chosen_move = move
                break

        if chosen_move is not None:
            self.board.make_move(chosen_move)
            self.switch_turn()

        self.reset_selection()

    def switch_turn(self):
        self.current_turn = BLACK if self.current_turn == RED else RED

    def get_valid_moves(self):
        return self.valid_moves

    def get_selected_piece(self):
        return self.selected_piece