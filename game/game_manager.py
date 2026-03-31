import pygame
from core.constants import (
    RED, BLACK, EMPTY, KING,
    BOARD_ROWS, BOARD_COLS,
    RED_WIN, BLACK_WIN, ONGOING, DRAW,
    MENU_STATE, AI_BATTLE_SELECT_STATE, PLAYING_STATE,
    PVP_MODE, PVAI_MODE, AIVAI_MODE,
    MOVE_ANIMATION_DURATION, AI_MOVE_DELAY,
)
from game.rules import Rules
from ai.ai_player import AIPlayer


class GameManager:
    def __init__(self, board, ai_engine=None):
        self.board = board
        self.rules = Rules(board)

        self.current_turn = RED
        self.selected_piece = None
        self.valid_moves = []
        self.game_state = ONGOING
        self.status_message = "Turn: RED"

        self.app_state = MENU_STATE
        self.game_mode = None

        self.red_ai = None
        self.black_ai = None

        self.global_difficulty_name = "Medium"

        self.paused = False
        self.ai_move_pending_time = 0

        self.animating = False
        self.animation_move = None
        self.animation_piece = None
        self.animation_start_time = 0
        self.animation_start_pos = (0, 0)
        self.animation_end_pos = (0, 0)
        self.animation_hide_piece = None

        
        self.board_history: list = []

    # SELECTION & TURN

    def reset_selection(self):
        self.selected_piece = None
        self.valid_moves = []

    def switch_turn(self):
        self.current_turn = BLACK if self.current_turn == RED else RED
        turn_text = "RED" if self.current_turn == RED else "BLACK"
        self.status_message = f"Turn: {turn_text}"

    def get_status_text(self):
        if self.game_state == RED_WIN:   return "RED WIN!"
        if self.game_state == BLACK_WIN: return "BLACK WIN!"
        if self.game_state == DRAW:      return "DRAW!"
        return self.status_message

    # GAME START / RESET

    def reset_board_only(self):
        self.board.reset_board()
        self.board_history = []
        self.current_turn = RED
        self.status_message = "Turn: RED"
        self.game_state = ONGOING
        self.reset_selection()
        self.paused = False
        self.animating = False
        self.animation_move = None
        self.ai_move_pending_time = pygame.time.get_ticks()

    def start_pvp(self):
        self.game_mode = PVP_MODE
        self.app_state = PLAYING_STATE
        self.red_ai = None
        self.black_ai = None
        self.global_difficulty_name = "-"
        self.reset_board_only()

    def start_pvai(self, depth, difficulty_name="Medium",
                   human_color=RED, ai_algorithm="alpha_beta"):
        self.game_mode = PVAI_MODE
        self.app_state = PLAYING_STATE
        self.global_difficulty_name = difficulty_name
        self.red_ai = None
        self.black_ai = None

        if human_color == RED:
            self.black_ai = AIPlayer(self.board, self,
                                     algorithm=ai_algorithm, max_depth=depth)
        else:
            self.red_ai = AIPlayer(self.board, self,
                                   algorithm=ai_algorithm, max_depth=depth)
        self.reset_board_only()

    def start_aivai(self, red_algo, red_depth, black_algo, black_depth):
        self.game_mode = AIVAI_MODE
        self.app_state = PLAYING_STATE
        self.global_difficulty_name = "Custom"
        self.red_ai   = AIPlayer(self.board, self,
                                  algorithm=red_algo,   max_depth=red_depth)
        self.black_ai = AIPlayer(self.board, self,
                                  algorithm=black_algo, max_depth=black_depth)
        self.reset_board_only()

    def back_to_menu(self):
        self.app_state = MENU_STATE
        self.game_mode = None
        self.red_ai = None
        self.black_ai = None
        self.reset_selection()
        self.paused = False
        self.animating = False

    # BOARD HASH & HISTORY

    def get_board_hash(self) -> str:
        """String hash nhẹ của trạng thái bàn cờ + lượt đi."""
        parts = []
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                parts.append("." if p == EMPTY else f"{p.piece_type}{p.color}")
        parts.append(str(self.current_turn))
        return "".join(parts)

    def update_history(self):
        self.board_history.append(self.get_board_hash())

    def is_repetition(self) -> bool:
        """Trả về True nếu trạng thái hiện tại đã xuất hiện ≥ 3 lần."""
        if len(self.board_history) < 4:
            return False
        current = self.get_board_hash()
        return self.board_history.count(current) >= 3

    # AI

    def get_current_ai(self):
        return self.red_ai if self.current_turn == RED else self.black_ai

    def is_human_turn(self):
        return self.get_current_ai() is None

    # LEGAL MOVES & CHECK

    def is_in_check(self, color):
        king_pos = None
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.piece_type == KING and p.color == color:
                    king_pos = (r, c); break
            if king_pos: break

        if king_pos is None:
            return True

        enemy = -color
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.color == enemy:
                    for m in self.rules.get_valid_moves(r, c):
                        if (m.end_row, m.end_col) == king_pos:
                            return True
        return False

    def kings_face_each_other(self):
        rk = bk = None
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.piece_type == KING:
                    if p.color == RED:   rk = (r, c)
                    else:                bk = (r, c)

        if rk is None or bk is None or rk[1] != bk[1]:
            return False

        col   = rk[1]
        start = min(rk[0], bk[0]) + 1
        end   = max(rk[0], bk[0])
        for r in range(start, end):
            if self.board.get_piece(r, col) != EMPTY:
                return False
        return True

    def get_legal_moves(self, row, col):
        piece = self.board.get_piece(row, col)
        if piece == EMPTY:
            return []

        legal = []
        for move in self.rules.get_valid_moves(row, col):
            self.board.make_move(move)
            if not self.is_in_check(piece.color) and not self.kings_face_each_other():
                legal.append(move)
            self.board.undo_move()
        return legal

    def has_any_legal_move(self, color):
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board.get_piece(r, c)
                if p != EMPTY and p.color == color and self.get_legal_moves(r, c):
                    return True
        return False

    # GAME OVER CHECK

    def check_game_over(self, color_to_move=None):
        if color_to_move is None:
            color_to_move = self.current_turn

        # Kiểm tra còn vua không
        king_red = king_black = False
        for p in self.board.get_all_pieces():
            if p.piece_type == KING:
                if p.color == RED:   king_red   = True
                else:                king_black = True

        if not king_red:
            self.game_state = BLACK_WIN; return
        if not king_black:
            self.game_state = RED_WIN;  return

        # Lặp nước → hoà
        if self.is_repetition():
            self.game_state = DRAW
            self.status_message = "HÒA! (lặp nước)"
            return

        # Hết nước đi
        if not self.has_any_legal_move(color_to_move):
            in_chk = self.is_in_check(color_to_move)
            if color_to_move == RED:
                self.game_state = BLACK_WIN
                winner = "BLACK"
            else:
                self.game_state = RED_WIN
                winner = "RED"
            reason = "Chiếu bí" if in_chk else "Hết nước"
            self.status_message = f"{reason}! {winner} THẮNG"
        else:
            self.game_state = ONGOING

    # UNDO
    def undo_last_move(self):
        if self.animating:
            return

        if self.game_mode == AIVAI_MODE:
            if self.board.move_log:
                self.board.undo_move()
                if self.board_history: self.board_history.pop()
                self.current_turn = -self.current_turn

        elif self.game_mode == PVAI_MODE:
            # Undo 2 nước: của AI và của người
            if len(self.board.move_log) >= 2:
                self.board.undo_move()
                if self.board_history: self.board_history.pop()
                self.board.undo_move()
                if self.board_history: self.board_history.pop()
                self.current_turn = RED
                self.status_message = "Turn: RED"
            elif len(self.board.move_log) == 1:
                self.board.undo_move()
                if self.board_history: self.board_history.pop()
                self.current_turn = RED
                self.status_message = "Turn: RED"
        else:
            if self.board.move_log:
                self.board.undo_move()
                if self.board_history: self.board_history.pop()
                self.current_turn = -self.current_turn
                t = "RED" if self.current_turn == RED else "BLACK"
                self.status_message = f"Turn: {t}"

        self.reset_selection()
        self.game_state = ONGOING
        self.ai_move_pending_time = pygame.time.get_ticks()

    # MOUSE / CLICK
    def get_clicked_square(self, mx, my, ox, oy, cs):
        col = round((mx - ox) / cs)
        row = round((my - oy) / cs)
        return row, col

    def is_inside_board(self, row, col):
        return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS

    def handle_mouse_click(self, mouse_x, mouse_y, offset_x, offset_y, cell_size):
        if self.game_state != ONGOING or self.paused or self.animating:
            return
        if not self.is_human_turn():
            return

        row, col = self.get_clicked_square(mouse_x, mouse_y, offset_x, offset_y, cell_size)
        if not self.is_inside_board(row, col):
            return

        clicked = self.board.get_piece(row, col)

        if self.selected_piece is None:
            if clicked != EMPTY and clicked.color == self.current_turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_legal_moves(row, col)
            return

        chosen = next((m for m in self.valid_moves
                       if m.end_row == row and m.end_col == col), None)
        if chosen:
            self.reset_selection()
            self.start_move_animation(chosen)
            return

        if clicked != EMPTY and clicked.color == self.current_turn:
            self.selected_piece = (row, col)
            self.valid_moves = self.get_legal_moves(row, col)
        else:
            self.reset_selection()

    # ANIMATION
    def start_move_animation(self, move):
        piece = self.board.get_piece(move.start_row, move.start_col)
        if piece == EMPTY:
            return False
        self.animating = True
        self.animation_move      = move
        self.animation_piece     = piece
        self.animation_hide_piece = piece
        self.animation_start_time = pygame.time.get_ticks()
        self.animation_start_pos  = (move.start_row, move.start_col)
        self.animation_end_pos    = (move.end_row,   move.end_col)
        return True

    def update_animation(self):
        if not self.animating:
            return False
        elapsed = (pygame.time.get_ticks() - self.animation_start_time) / 1000.0
        if elapsed >= MOVE_ANIMATION_DURATION:
            move = self.animation_move
            self.board.make_move(move)
            self.update_history()            # ghi lịch sử SAU khi đi

            next_turn = -self.current_turn
            self.check_game_over(next_turn)

            self.animating = False
            self.animation_move = self.animation_piece = self.animation_hide_piece = None

            if self.game_state == ONGOING:
                self.switch_turn()
                self.ai_move_pending_time = pygame.time.get_ticks()
            return True
        return False

    def get_animation_draw_data(self):
        if not self.animating or self.animation_piece is None:
            return None
        elapsed = (pygame.time.get_ticks() - self.animation_start_time) / 1000.0
        t  = min(1.0, elapsed / MOVE_ANIMATION_DURATION)
        sr, sc = self.animation_start_pos
        er, ec = self.animation_end_pos
        # Easing: smooth-step
        t = t * t * (3 - 2 * t)
        return {
            "piece":      self.animation_piece,
            "row":        sr + (er - sr) * t,
            "col":        sc + (ec - sc) * t,
            "target_row": er,
            "target_col": ec,
        }

    # AI TURN
    def perform_ai_turn(self):
        if self.paused or self.animating or self.game_state != ONGOING:
            return
        ai = self.get_current_ai()
        if ai is None:
            return
        now = pygame.time.get_ticks()
        if now - self.ai_move_pending_time < AI_MOVE_DELAY:
            return

        # Truyền board_history dưới dạng list (AI sẽ convert sang hash int bên trong)
        ai_move = ai.get_best_move(self.board, self.current_turn,
                                   self.board_history)
        if ai_move:
            self.start_move_animation(ai_move)
            
    # UPDATE LOOP

    def update(self):
        self.update_animation()
        if self.app_state != PLAYING_STATE or self.game_state != ONGOING:
            return
        if self.game_mode in (PVAI_MODE, AIVAI_MODE):
            if not self.is_human_turn():
                self.perform_ai_turn()

    # PAUSE / MISC

    def toggle_pause(self):
        if self.game_mode == AIVAI_MODE:
            self.paused = not self.paused
            if not self.paused:
                self.ai_move_pending_time = pygame.time.get_ticks()

    def get_valid_moves(self):
        return self.valid_moves

    def get_selected_piece(self):
        return self.selected_piece