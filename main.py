import pygame
from core.constants import *
from game.board import Board
from game.game_manager import GameManager
from ui.renderer import Renderer
from ui.menu import Menu
from ui.ai_battle_menu import AIBattleMenu
from ui.hud import HUD


def main():
    pygame.init()

    if FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Chinese Chess")
    clock = pygame.time.Clock()

    board = Board()
    game_manager = GameManager(board)
    renderer = Renderer(screen)
    menu = Menu()
    ai_battle_menu = AIBattleMenu()
    hud = HUD()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_manager.app_state == MENU_STATE:
                result = menu.handle_event(event)
                if result:
                    action = result[0]

                    if action == "pvsai":
                        _, depth = result
                        game_manager.start_pvai(
                            depth=depth,
                            difficulty_name=menu.get_selected_difficulty_name(),
                            human_color=RED,
                            ai_algorithm="alpha_beta",
                        )

                    elif action == "aivai":
                        game_manager.app_state = AI_BATTLE_SELECT_STATE

                    elif action == "pvp":
                        game_manager.start_pvp()

                    elif action == "quit":
                        running = False

            elif game_manager.app_state == AI_BATTLE_SELECT_STATE:
                result = ai_battle_menu.handle_event(event)
                if result:
                    if result[0] == "start":
                        _, red_algo, red_depth, black_algo, black_depth = result
                        game_manager.start_aivai(red_algo, red_depth, black_algo, black_depth)
                    elif result[0] == "back":
                        game_manager.app_state = MENU_STATE

            elif game_manager.app_state == PLAYING_STATE:
                hud_action = hud.handle_event(event, game_manager)

                if hud_action == "undo":
                    game_manager.undo_last_move()
                elif hud_action == "reset":
                    game_manager.reset_board_only()
                elif hud_action == "pause":
                    game_manager.toggle_pause()
                elif hud_action == "menu":
                    game_manager.back_to_menu()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if event.pos[0] < BOARD_AREA_WIDTH:
                        game_manager.handle_mouse_click(
                            event.pos[0], event.pos[1],
                            BOARD_OFFSET_X, BOARD_OFFSET_Y, CELL_SIZE
                        )

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        game_manager.undo_last_move()
                    elif event.key == pygame.K_r:
                        game_manager.reset_board_only()
                    elif event.key == pygame.K_ESCAPE:
                        game_manager.back_to_menu()
                    elif event.key == pygame.K_SPACE:
                        game_manager.toggle_pause()

        game_manager.update()

        if game_manager.app_state == MENU_STATE:
            menu.draw(screen)
            pygame.display.flip()
        elif game_manager.app_state == AI_BATTLE_SELECT_STATE:
            ai_battle_menu.draw(screen)
            pygame.display.flip()
        elif game_manager.app_state == PLAYING_STATE:
            renderer.render(board, game_manager, hud)

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()