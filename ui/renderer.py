import pygame
from core.constants import (
    BOARD_ROWS, BOARD_COLS,
    CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    SCREEN_WIDTH, SCREEN_HEIGHT, PANEL_WIDTH,
    WHITE, BLACK_COLOR, RED_COLOR, BEIGE,
    SELECT_COLOR, VALID_MOVE_COLOR,
    PANEL_BG, TEXT_COLOR, WIN_COLOR,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_RADIUS,
    UNDO_BUTTON_Y, RESET_BUTTON_Y,
    BUTTON_BG, BUTTON_BG_2, BUTTON_TEXT_COLOR,
    OVERLAY_COLOR
)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 22)
        self.big_font = pygame.font.SysFont("arial", 40, bold=True)
        self.tiny_font = pygame.font.SysFont("arial", 18, italic=True)
    
        panel_x = SCREEN_WIDTH - PANEL_WIDTH
        button_x = panel_x + (PANEL_WIDTH - BUTTON_WIDTH) // 2
    
        self.undo_button_rect = pygame.Rect(
            button_x, UNDO_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT
        )
        self.reset_button_rect = pygame.Rect(
            button_x, RESET_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT
        )

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
        pygame.draw.circle(self.screen, SELECT_COLOR, (x, y), 30, 4)

    def draw_valid_moves(self, moves):
        for move in moves:
            x = BOARD_OFFSET_X + move.end_col * CELL_SIZE
            y = BOARD_OFFSET_Y + move.end_row * CELL_SIZE
            pygame.draw.circle(self.screen, VALID_MOVE_COLOR, (x, y), 10)

    def draw_piece(self, piece):
        x = BOARD_OFFSET_X + piece.col * CELL_SIZE
        y = BOARD_OFFSET_Y + piece.row * CELL_SIZE
        color = RED_COLOR if piece.color == 1 else BLACK_COLOR

        pygame.draw.circle(self.screen, WHITE, (x, y), 25)
        pygame.draw.circle(self.screen, color, (x, y), 25, 3)

        text = self.font.render(piece.piece_type, True, color)
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)

    def draw_pieces(self, pieces):
        for piece in pieces:
            self.draw_piece(piece)

    def draw_button(self, rect, text, bg_color):
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(self.screen, BLACK_COLOR, rect, 2, border_radius=BUTTON_RADIUS)
    
        text_surface = self.small_font.render(text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)    

    def draw_side_panel(self, status_text):
        panel_x = SCREEN_WIDTH - PANEL_WIDTH
        pygame.draw.rect(self.screen, PANEL_BG, (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, BLACK_COLOR, (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)
    
        title = self.font.render("MENU", True, TEXT_COLOR)
        self.screen.blit(title, (panel_x + 75, 40))
    
        status_title = self.small_font.render("Status:", True, TEXT_COLOR)
        self.screen.blit(status_title, (panel_x + 20, 120))
    
        status_color = TEXT_COLOR
        if "RED WIN" in status_text:
            status_color = RED_COLOR
        elif "BLACK WIN" in status_text:
            status_color = BLACK_COLOR
        elif "DRAW" in status_text:
            status_color = WIN_COLOR
    
        status_surface = self.small_font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (panel_x + 20, 155))
    
        guide_title = self.small_font.render("Shortcut:", True, TEXT_COLOR)
        self.screen.blit(guide_title, (panel_x + 20, 240))
    
        guide1 = self.small_font.render("U: Undo", True, TEXT_COLOR)
        guide2 = self.small_font.render("R: Reset", True, TEXT_COLOR)
        guide3 = self.small_font.render("ESC: Exit", True, TEXT_COLOR)
    
        self.screen.blit(guide1, (panel_x + 20, 275))
        self.screen.blit(guide2, (panel_x + 20, 305))
        self.screen.blit(guide3, (panel_x + 20, 335))
    
        self.draw_button(self.undo_button_rect, "Undo", BUTTON_BG)
        self.draw_button(self.reset_button_rect, "Reset", BUTTON_BG_2)
        
        pygame.draw.line(
            self.screen,
            BLACK_COLOR,
            (panel_x + 20, SCREEN_HEIGHT - 75),
            (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 75),
            1
        )
        
        creator_text = self.tiny_font.render("Made by Thinh & Sang", True, TEXT_COLOR)
        creator_rect = creator_text.get_rect(center=(panel_x + PANEL_WIDTH // 2, SCREEN_HEIGHT - 35))
        self.screen.blit(creator_text, creator_rect)

    def draw_game_over_overlay(self, status_text):
        if ("THẮNG" not in status_text) and ("HÒA" not in status_text):
            return
    
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))
    
        text = self.big_font.render(status_text, True, WIN_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2 - PANEL_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)
        
    def get_panel_button_clicked(self, mouse_pos):
        if self.undo_button_rect.collidepoint(mouse_pos):
            return "undo"
        if self.reset_button_rect.collidepoint(mouse_pos):
            return "reset"
        return None

    def render(self, pieces, valid_moves=None, selected_piece=None, status_text=""):
        self.draw_background()
        self.draw_board()
        self.draw_selected_piece(selected_piece)
        self.draw_valid_moves(valid_moves or [])
        self.draw_pieces(pieces)
        self.draw_side_panel(status_text)
        self.draw_game_over_overlay(status_text)
        pygame.display.flip()