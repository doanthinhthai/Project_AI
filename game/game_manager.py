import pygame
import random
from core.constants import (
    RED, BLACK, EMPTY, KING, 
    BOARD_ROWS, BOARD_COLS,
    RED_WIN, BLACK_WIN, ONGOING
)
from game.rules import Rules
from game.moves import Move

class GameManager:
    def __init__(self, board, ai_engine=None):
        """
        Khởi tạo quản lý trò chơi.
        ai_engine: (Optional) Đối tượng AI để thực hiện nước đi máy.
        """
        self.board = board
        self.rules = Rules(board)
        self.ai_engine = ai_engine # Giai đoạn 11-14 sẽ truyền vào đây

        self.current_turn = RED  # Đỏ đi trước
        self.selected_piece = None
        self.valid_moves = []
        self.game_state = ONGOING
        
        # Biến để hiển thị thông tin lượt đi lên UI
        self.status_message = "Lượt của: ĐỎ"

    def reset_selection(self):
        """Reset trạng thái chọn quân"""
        self.selected_piece = None
        self.valid_moves = []

    def switch_turn(self):
        """Chuyển lượt đi và cập nhật thông báo"""
        self.current_turn = BLACK if self.current_turn == RED else RED
        turn_text = "ĐỎ" if self.current_turn == RED else "ĐEN"
        self.status_message = f"Lượt của: {turn_text}"
        
        # Nếu đến lượt AI (mặc định là phe Đen trong dự án này)
        if self.current_turn == BLACK and self.ai_engine is not None:
            self.handle_ai_turn()

    # --- TÍNH NĂNG 1: HIỂN THỊ LƯỢT ĐI ---
    def get_status_text(self):
        """Trả về chuỗi văn bản trạng thái để Renderer vẽ lên màn hình"""
        if self.game_state == RED_WIN:
            return "ĐỎ THẮNG!"
        elif self.game_state == BLACK_WIN:
            return "ĐEN THẮNG!"
        return self.status_message

    # --- TÍNH NĂNG 2: NÚT UNDO ---
    def undo_last_move(self):
        """Thực hiện hoàn tác nước đi"""
        # Nếu chơi với AI, undo 1 lần sẽ lùi 2 bước (cả nước của AI và người)
        if self.ai_engine is not None:
            self.board.undo_move() # Undo nước AI
            self.board.undo_move() # Undo nước người chơi
        else:
            self.board.undo_move()
            self.switch_turn()
            
        self.reset_selection()
        self.game_state = ONGOING

    # --- TÍNH NĂNG 3: AI ĐI QUÂN ---
    def handle_ai_turn(self):
        """Xử lý logic cho AI tìm và thực hiện nước đi"""
        # Đây là khung logic, AI Engine sẽ thực hiện thuật toán Minimax ở giai đoạn sau
        print("AI đang suy nghĩ...")
        
        # Giả sử AI lấy nước đi tốt nhất từ engine
        ai_move = self.ai_engine.get_best_move(self.board) 
        
        if ai_move:
            self.board.make_move(ai_move)
            self.check_game_over()
            self.switch_turn()

    # --- TÍNH NĂNG 4: LUẬT CHIẾU TƯỚNG CẢI TIẾN ---
    def is_in_check(self, color):
        """
        Kiểm tra xem phe 'color' có đang bị chiếu tướng không.
        """
        # 1. Tìm vị trí Tướng của phe color
        king_pos = None
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.piece_type == KING and p.color == color:
                    king_pos = (r, c)
                    break
        
        if not king_pos: return False

        # 2. Kiểm tra xem có quân đối phương nào có thể ăn được Tướng không
        enemy_color = -color
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.color == enemy_color:
                    # Lấy các nước đi tiềm năng của quân đối phương
                    moves = self.rules.get_valid_moves(r, c)
                    for m in moves:
                        if (m.end_row, m.end_col) == king_pos:
                            return True
        return False

    def check_game_over(self):
        """Kiểm tra điều kiện kết thúc: Bị ăn Tướng hoặc Chiếu bí"""
        # Đơn giản nhất: Kiểm tra xem Tướng còn trên bàn không
        king_red = False
        king_black = False
        for piece in self.board.get_all_pieces():
            if piece.piece_type == KING:
                if piece.color == RED: king_red = True
                if piece.color == BLACK: king_black = True
        
        if not king_red:
            self.game_state = BLACK_WIN
        elif not king_black:
            self.game_state = RED_WIN

    def handle_mouse_click(self, mouse_x, mouse_y, offset_x, offset_y, cell_size):
        """Xử lý tương tác người dùng"""
        if self.game_state != ONGOING:
            return

        row, col = self.get_clicked_square(mouse_x, mouse_y, offset_x, offset_y, cell_size)
        if not self.rules.is_inside_board(row, col):
            return

        clicked_piece = self.board.get_piece(row, col)

        # Logic chọn quân
        if self.selected_piece is None:
            if clicked_piece != EMPTY and clicked_piece.color == self.current_turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.rules.get_valid_moves(row, col)
        else:
            # Logic thực hiện nước đi
            chosen_move = next((m for m in self.valid_moves if m.end_row == row and m.end_col == col), None)
            
            if chosen_move:
                self.board.make_move(chosen_move)
                self.check_game_over()
                if self.game_state == ONGOING:
                    self.switch_turn()
                self.reset_selection()
            elif clicked_piece != EMPTY and clicked_piece.color == self.current_turn:
                # Đổi quân chọn
                self.selected_piece = (row, col)
                self.valid_moves = self.rules.get_valid_moves(row, col)
            else:
                self.reset_selection()

    def get_clicked_square(self, mx, my, ox, oy, cs):
        """Chuyển tọa độ pixel sang tọa độ bàn cờ"""
        col = round((mx - ox) / cs)
        row = round((my - oy) / cs)
        return row, col
