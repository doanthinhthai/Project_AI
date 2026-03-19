import pygame
from core.constants import (
    BOARD_ROWS, BOARD_COLS,
    CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    WHITE, BLACK_COLOR, RED_COLOR, BEIGE
)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 28, bold=True)

    def draw_background(self):
        self.screen.fill(BEIGE)

    def draw_board(self):
        x0 = BOARD_OFFSET_X
        y0 = BOARD_OFFSET_Y
        x1 = BOARD_OFFSET_X + (BOARD_COLS - 1) * CELL_SIZE
        y1 = BOARD_OFFSET_Y + (BOARD_ROWS - 1) * CELL_SIZE
    
        # 1) Vẽ các đường ngang
        for row in range(BOARD_ROWS):
            y = y0 + row * CELL_SIZE
            pygame.draw.line(self.screen, BLACK_COLOR, (x0, y), (x1, y), 2)
    
        # 2) Vẽ các đường dọc
        for col in range(BOARD_COLS):
            x = x0 + col * CELL_SIZE
    
            # Hai cột biên vẽ full từ trên xuống dưới
            if col == 0 or col == BOARD_COLS - 1:
                pygame.draw.line(self.screen, BLACK_COLOR, (x, y0), (x, y1), 2)
            else:
                # Nửa trên bàn cờ
                pygame.draw.line(
                    self.screen,
                    BLACK_COLOR,
                    (x, y0),
                    (x, y0 + 4 * CELL_SIZE),
                    2
                )
                # Nửa dưới bàn cờ
                pygame.draw.line(
                    self.screen,
                    BLACK_COLOR,
                    (x, y0 + 5 * CELL_SIZE),
                    (x, y1),
                    2
                )
    
        # 3) Vẽ chéo cung tướng phía trên
        pygame.draw.line(
            self.screen, BLACK_COLOR,
            (x0 + 3 * CELL_SIZE, y0),
            (x0 + 5 * CELL_SIZE, y0 + 2 * CELL_SIZE), 2
        )
        pygame.draw.line(
            self.screen, BLACK_COLOR,
            (x0 + 5 * CELL_SIZE, y0),
            (x0 + 3 * CELL_SIZE, y0 + 2 * CELL_SIZE), 2
        )
    
        # 4) Vẽ chéo cung tướng phía dưới
        pygame.draw.line(
            self.screen, BLACK_COLOR,
            (x0 + 3 * CELL_SIZE, y0 + 7 * CELL_SIZE),
            (x0 + 5 * CELL_SIZE, y0 + 9 * CELL_SIZE), 2
        )
        pygame.draw.line(
            self.screen, BLACK_COLOR,
            (x0 + 5 * CELL_SIZE, y0 + 7 * CELL_SIZE),
            (x0 + 3 * CELL_SIZE, y0 + 9 * CELL_SIZE), 2
        )

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

    def render(self, pieces):
        self.draw_background()
        self.draw_board()
        self.draw_pieces(pieces)
        pygame.display.flip()