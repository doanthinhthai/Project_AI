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

    def reset_selection(self):
        self.selected_piece = None
        self.valid_moves = []

    def switch_turn(self):
        self.current_turn = BLACK if self.current_turn == RED else RED
        turn_text = "RED" if self.current_turn == RED else "BLACK"
        self.status_message = f"Turn: {turn_text}"

    def get_status_text(self):
        if self.game_state == RED_WIN:
            return "RED WIN!"
        elif self.game_state == BLACK_WIN:
            return "BLACK WIN!"
        elif self.game_state == DRAW:
            return "DRAW!"
        return self.status_message

    def reset_board_only(self):
        self.board.reset_board()
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

    def start_pvai(self, depth, difficulty_name="Medium", human_color=RED, ai_algorithm="alpha_beta"):
        self.game_mode = PVAI_MODE
        self.app_state = PLAYING_STATE
        self.global_difficulty_name = difficulty_name

        self.red_ai = None
        self.black_ai = None

        if human_color == RED:
            self.black_ai = AIPlayer(self.board, self, algorithm=ai_algorithm, max_depth=depth)
        else:
            self.red_ai = AIPlayer(self.board, self, algorithm=ai_algorithm, max_depth=depth)

        self.reset_board_only()

    def start_aivai(self, red_algo, red_depth, black_algo, black_depth):
        self.game_mode = AIVAI_MODE
        self.app_state = PLAYING_STATE
        self.global_difficulty_name = "Custom"

        self.red_ai = AIPlayer(self.board, self, algorithm=red_algo, max_depth=red_depth)
        self.black_ai = AIPlayer(self.board, self, algorithm=black_algo, max_depth=black_depth)

        self.reset_board_only()

    def back_to_menu(self):
        self.app_state = MENU_STATE
        self.game_mode = None
        self.red_ai = None
        self.black_ai = None
        self.reset_selection()
        self.paused = False
        self.animating = False

    def get_current_ai(self):
        if self.current_turn == RED:
            return self.red_ai
        return self.black_ai

    def is_human_turn(self):
        return self.get_current_ai() is None

    def undo_last_move(self):
        if self.animating:
            return

        if self.game_mode == AIVAI_MODE:
            if len(self.board.move_log) >= 1:
                self.board.undo_move()
                self.current_turn = BLACK if self.current_turn == RED else RED

        elif self.game_mode == PVAI_MODE:
            if len(self.board.move_log) >= 2:
                self.board.undo_move()
                self.board.undo_move()
                self.current_turn = RED
                self.status_message = "Turn: RED"

        else:
            if len(self.board.move_log) >= 1:
                self.board.undo_move()
                self.current_turn = BLACK if self.current_turn == RED else RED
                self.status_message = f"Turn: {'RED' if self.current_turn == RED else 'BLACK'}"

        self.reset_selection()
        self.game_state = ONGOING
        self.ai_move_pending_time = pygame.time.get_ticks()

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
            return True

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

    def has_any_legal_move(self, color):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece != EMPTY and piece.color == color:
                    legal_moves = self.get_legal_moves(row, col)
                    if legal_moves:
                        return True
        return False

    def check_game_over(self, color_to_move=None):
        if color_to_move is None:
            color_to_move = self.current_turn

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
            return
        elif not king_black:
            self.game_state = RED_WIN
            return

        if not self.has_any_legal_move(color_to_move):
            if self.is_in_check(color_to_move) or self.kings_face_each_other():
                self.game_state = BLACK_WIN if color_to_move == RED else RED_WIN
            else:
                self.game_state = DRAW
        else:
            self.game_state = ONGOING

    def start_move_animation(self, move):
        moved_piece = self.board.get_piece(move.start_row, move.start_col)
        if moved_piece == EMPTY:
            return False

        self.animating = True
        self.animation_move = move
        self.animation_piece = moved_piece
        self.animation_hide_piece = moved_piece
        self.animation_start_time = pygame.time.get_ticks()

        self.animation_start_pos = (move.start_row, move.start_col)
        self.animation_end_pos = (move.end_row, move.end_col)
        return True

    def update_animation(self):
        if not self.animating:
            return False

        elapsed = (pygame.time.get_ticks() - self.animation_start_time) / 1000.0
        if elapsed >= MOVE_ANIMATION_DURATION:
            move = self.animation_move
            self.board.make_move(move)

            next_turn = BLACK if self.current_turn == RED else RED
            self.check_game_over(next_turn)

            self.animating = False
            self.animation_move = None
            self.animation_piece = None
            self.animation_hide_piece = None

            if self.game_state == ONGOING:
                self.switch_turn()
                self.ai_move_pending_time = pygame.time.get_ticks()

            return True

        return False

    def get_animation_draw_data(self):
        if not self.animating or self.animation_piece is None:
            return None

        elapsed = (pygame.time.get_ticks() - self.animation_start_time) / 1000.0
        t = min(1.0, elapsed / MOVE_ANIMATION_DURATION)

        sr, sc = self.animation_start_pos
        er, ec = self.animation_end_pos

        current_row = sr + (er - sr) * t
        current_col = sc + (ec - sc) * t

        return {
            "piece": self.animation_piece,
            "row": current_row,
            "col": current_col,
            "target_row": er,
            "target_col": ec,
        }

    def perform_ai_turn(self):
        if self.paused or self.animating or self.game_state != ONGOING:
            return

        ai_player = self.get_current_ai()
        if ai_player is None:
            return

        now = pygame.time.get_ticks()
        if now - self.ai_move_pending_time < AI_MOVE_DELAY:
            return

        ai_move = ai_player.get_best_move(self.board, self.current_turn)
        if ai_move:
            self.start_move_animation(ai_move)

    def update(self):
        self.update_animation()

        if self.app_state != PLAYING_STATE:
            return

        if self.game_state != ONGOING:
            return

        if self.game_mode in (PVAI_MODE, AIVAI_MODE):
            if not self.is_human_turn():
                self.perform_ai_turn()

    def handle_mouse_click(self, mouse_x, mouse_y, offset_x, offset_y, cell_size):
        if self.game_state != ONGOING or self.paused or self.animating:
            return

        if not self.is_human_turn():
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
            self.reset_selection()
            self.start_move_animation(chosen_move)
            return

        if clicked_piece != EMPTY and clicked_piece.color == self.current_turn:
            self.selected_piece = (row, col)
            self.valid_moves = self.get_legal_moves(row, col)
        else:
            self.reset_selection()

    def toggle_pause(self):
        if self.game_mode == AIVAI_MODE:
            self.paused = not self.paused
            self.ai_move_pending_time = pygame.time.get_ticks()

    def get_valid_moves(self):
        return self.valid_moves

    def get_selected_piece(self):
        return self.selected_piece