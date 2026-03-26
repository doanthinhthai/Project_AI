import pygame

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BOARD_OFFSET_X, BOARD_OFFSET_Y,
    CELL_SIZE, FPS
)

from game.board import Board
from game.game_manager import GameManager
from ui.renderer import Renderer
from ai.ai_player import AIPlayer


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Xiangqi Test")

    clock = pygame.time.Clock()

    # INIT GAME
    board = Board()
    game_manager = GameManager(board)
    ai_engine = AIPlayer(board, game_manager, algorithm="alpha_beta", max_depth=3)
    game_manager.ai_engine = ai_engine

    renderer = Renderer(screen)

    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Nếu bạn chưa làm panel button thì comment dòng dưới
                action = renderer.get_panel_button_clicked((mx, my))

                if action == "undo":
                    game_manager.undo_last_move()

                elif action == "reset":
                    board.reset_board()
                    game_manager = GameManager(board)
                    ai_engine = AIPlayer(board, game_manager, algorithm="alpha_beta", max_depth=3)
                    game_manager.ai_engine = ai_engine

                else:
                    game_manager.handle_mouse_click(
                        mx, my,
                        BOARD_OFFSET_X,
                        BOARD_OFFSET_Y,
                        CELL_SIZE
                    )

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    game_manager.undo_last_move()

                elif event.key == pygame.K_r:
                    board.reset_board()
                    game_manager = GameManager(board)
                    ai_engine = AIPlayer(board, game_manager, algorithm="alpha_beta", max_depth=3)
                    game_manager.ai_engine = ai_engine

                elif event.key == pygame.K_ESCAPE:
                    running = False

        renderer.render(
            board.get_all_pieces(),
            game_manager.get_valid_moves(),
            game_manager.get_selected_piece(),
            game_manager.get_status_text()
        )

    pygame.quit()


if __name__ == "__main__":
    main()