import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN, FPS,
    BOARD_OFFSET_X, BOARD_OFFSET_Y, CELL_SIZE
)
from ui.renderer import Renderer
from game.board import Board
from game.game_manager import GameManager


def main():
    pygame.init()

    flags = pygame.FULLSCREEN if FULLSCREEN else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("Chinese Chess Test")

    clock = pygame.time.Clock()
    renderer = Renderer(screen)

    board = Board()
    game_manager = GameManager(board)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                game_manager.handle_mouse_click(
                    mouse_x,
                    mouse_y,
                    BOARD_OFFSET_X,
                    BOARD_OFFSET_Y,
                    CELL_SIZE
                )

        pieces = board.get_all_pieces()
        valid_moves = game_manager.get_valid_moves()
        selected_piece = game_manager.get_selected_piece()

        renderer.render(pieces, valid_moves, selected_piece)
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()