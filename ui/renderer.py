import pygame
from core.constants import (
    BOARD_ROWS, BOARD_COLS,
    CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    SCREEN_WIDTH, SCREEN_HEIGHT, PANEL_WIDTH, BOARD_AREA_WIDTH,
    WHITE, BLACK_COLOR, BEIGE,
    SELECT_COLOR, VALID_MOVE_COLOR,
    TEXT_COLOR, WIN_COLOR, OVERLAY_COLOR,
    RED_WIN, BLACK_WIN, DRAW
)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 22)
        self.big_font = pygame.font.SysFont("arial", 46, bold=True)
        self.tiny_font = pygame.font.SysFont("arial", 18, italic=True)

    def draw_background(self):
        self.screen.fill(BEIGE)

    def draw_board(self):
        x0 = BOARD_OFFSET_X
        y0 = BOARD_OFFSET_Y
        x1 = BOARD_OFFSET_X + (BOARD_COLS - 1) * CELL_SIZE
        y1 = BOARD_OFFSET_Y + (BOARD_ROWS - 1) * CELL_SIZE

        for row in range(BOARD_ROWS):
            y = y0 + row * CELL_SIZE
            pygame.draw.line(self.screen, BLACK_COLOR, (x0, y), (x1, y), 2)

        for col in range(BOARD_COLS):
            x = x0 + col * CELL_SIZE
            if col == 0 or col == BOARD_COLS - 1:
                pygame.draw.line(self.screen, BLACK_COLOR, (x, y0), (x, y1), 2)
            else:
                pygame.draw.line(self.screen, BLACK_COLOR, (x, y0), (x, y0 + 4 * CELL_SIZE), 2)
                pygame.draw.line(self.screen, BLACK_COLOR, (x, y0 + 5 * CELL_SIZE), (x, y1), 2)

        pygame.draw.line(self.screen, BLACK_COLOR,
                         (x0 + 3 * CELL_SIZE, y0),
                         (x0 + 5 * CELL_SIZE, y0 + 2 * CELL_SIZE), 2)
        pygame.draw.line(self.screen, BLACK_COLOR,
                         (x0 + 5 * CELL_SIZE, y0),
                         (x0 + 3 * CELL_SIZE, y0 + 2 * CELL_SIZE), 2)

        pygame.draw.line(self.screen, BLACK_COLOR,
                         (x0 + 3 * CELL_SIZE, y0 + 7 * CELL_SIZE),
                         (x0 + 5 * CELL_SIZE, y0 + 9 * CELL_SIZE), 2)
        pygame.draw.line(self.screen, BLACK_COLOR,
                         (x0 + 5 * CELL_SIZE, y0 + 7 * CELL_SIZE),
                         (x0 + 3 * CELL_SIZE, y0 + 9 * CELL_SIZE), 2)

    def draw_selected_piece(self, selected_piece):
        if selected_piece is None:
            return
        row, col = selected_piece
        x = BOARD_OFFSET_X + col * CELL_SIZE
        y = BOARD_OFFSET_Y + row * CELL_SIZE
        pygame.draw.circle(self.screen, SELECT_COLOR, (x, y), 31, 4)

    def draw_valid_moves(self, moves):
        for move in moves:
            x = BOARD_OFFSET_X + move.end_col * CELL_SIZE
            y = BOARD_OFFSET_Y + move.end_row * CELL_SIZE
            pygame.draw.circle(self.screen, VALID_MOVE_COLOR, (x, y), 10)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 16, 2)

    def draw_piece(self, piece):
        x = BOARD_OFFSET_X + piece.col * CELL_SIZE
        y = BOARD_OFFSET_Y + piece.row * CELL_SIZE
        rect = piece.image.get_rect(center=(x, y))
        self.screen.blit(piece.image, rect)

    def draw_piece_at_float_position(self, piece, row, col):
        x = BOARD_OFFSET_X + col * CELL_SIZE
        y = BOARD_OFFSET_Y + row * CELL_SIZE
        rect = piece.image.get_rect(center=(x, y))
        self.screen.blit(piece.image, rect)

    def draw_pieces(self, pieces, hidden_piece=None):
        for piece in pieces:
            if hidden_piece is not None and piece is hidden_piece:
                continue
            self.draw_piece(piece)

    def draw_footer(self):
        text = self.tiny_font.render("Made by Vu Nam Sang & Thai Doan Thinh", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(BOARD_AREA_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(text, text_rect)

    def draw_game_over_overlay(self, game_state):
        if game_state not in (RED_WIN, BLACK_WIN, DRAW):
            return

        overlay = pygame.Surface((BOARD_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

        if game_state == RED_WIN:
            msg = "RED WIN!"
        elif game_state == BLACK_WIN:
            msg = "BLACK WIN!"
        else:
            msg = "DRAW!"

        text = self.big_font.render(msg, True, WIN_COLOR)
        rect = text.get_rect(center=(BOARD_AREA_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)

    def render(self, board, game_manager, hud):
        self.draw_background()
        self.draw_board()
        self.draw_selected_piece(game_manager.get_selected_piece())
        self.draw_valid_moves(game_manager.get_valid_moves())

        hidden_piece = game_manager.animation_hide_piece if game_manager.animating else None
        self.draw_pieces(board.get_all_pieces(), hidden_piece=hidden_piece)

        anim_data = game_manager.get_animation_draw_data()
        if anim_data is not None:
            self.draw_piece_at_float_position(anim_data["piece"], anim_data["row"], anim_data["col"])

        self.draw_footer()
        hud.draw(self.screen, game_manager)
        self.draw_game_over_overlay(game_manager.game_state)

        pygame.display.flip()