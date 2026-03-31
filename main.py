
import sys
import pygame

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BOARD_OFFSET_X, BOARD_OFFSET_Y_CLOSED, BOARD_OFFSET_Y_OPEN,
    CTRL_PANEL_X, CTRL_PANEL_Y,
    BOARD_AREA_WIDTH,
    MENU_STATE, AI_BATTLE_SELECT_STATE, PLAYING_STATE,
    PVP_MODE, PVAI_MODE, AIVAI_MODE,
    RED, BLACK, AI_ALPHABETA, DIFFICULTY_LEVELS, DIFFICULTY_TIME,
    CELL_SIZE,
)
from game.board         import Board
from game.game_manager  import GameManager
from ui.renderer        import Renderer
from ui.hud             import HUD
from ui.menu            import Menu
from ui.ai_battle_menu  import AIBattleMenu
from ui.control_panel   import ControlPanel


def main():
    pygame.init()
    pygame.display.set_caption(" Chinese Chess")
    try:
        icon = pygame.image.load("assets/icon.png")
        pygame.display.set_icon(icon)
    except Exception:
        pass

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock  = pygame.time.Clock()

    board    = Board()
    gm       = GameManager(board)
    renderer = Renderer(screen)
    hud      = HUD()
    menu     = Menu()
    ai_menu  = AIBattleMenu()
    ctrl     = ControlPanel(CTRL_PANEL_X, CTRL_PANEL_Y,
                             BOARD_AREA_WIDTH - CTRL_PANEL_X * 2)

    def _oy() -> int:
        return BOARD_OFFSET_Y_OPEN if ctrl._custom_open else BOARD_OFFSET_Y_CLOSED

    def _apply_new_game():
        depth  = ctrl._get_depth()
        tlimit = ctrl._get_time()
        name   = ctrl.get_diff_name()
        hc     = RED if ctrl._dd.selected == 0 else BLACK
        if gm.game_mode in (None, PVAI_MODE):
            gm.start_pvai(depth=depth, difficulty_name=name,
                          human_color=hc, ai_algorithm=AI_ALPHABETA)
            ai = gm.red_ai or gm.black_ai
            if ai and hasattr(ai, "engine"):
                ai.engine.time_limit = tlimit
        elif gm.game_mode == PVP_MODE:
            gm.start_pvp()
        elif gm.game_mode == AIVAI_MODE:
            gm.start_aivai(AI_ALPHABETA, depth, AI_ALPHABETA, depth)

    running = True
    while running:
        mp = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False; break

            if gm.app_state == MENU_STATE:
                result = menu.handle_event(event)
                if result:
                    action = result[0]; depth = result[1] if len(result)>1 else 3
                    if action == "pvp":
                        gm.start_pvp()
                    elif action == "pvsai":
                        diff_name = menu.get_selected_difficulty_name()
                        gm.start_pvai(depth=depth, difficulty_name=diff_name,
                                      human_color=RED, ai_algorithm=AI_ALPHABETA)
                        ai = gm.red_ai or gm.black_ai
                        if ai and hasattr(ai,"engine"):
                            ai.engine.time_limit = DIFFICULTY_TIME.get(diff_name, 10.0)
                    elif action == "aivai":
                        gm.app_state = AI_BATTLE_SELECT_STATE
                    elif action == "quit":
                        running = False; break

            elif gm.app_state == AI_BATTLE_SELECT_STATE:
                result = ai_menu.handle_event(event)
                if result:
                    if result[0] == "back": gm.app_state = MENU_STATE
                    elif result[0] == "start":
                        _, ra, rd, ba, bd = result
                        gm.start_aivai(ra, rd, ba, bd)

            elif gm.app_state == PLAYING_STATE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:   gm.back_to_menu()
                    elif event.key == pygame.K_z and pygame.key.get_mods()&pygame.KMOD_CTRL:
                        gm.undo_last_move()
                    elif event.key == pygame.K_r:      gm.reset_board_only()
                    elif event.key == pygame.K_SPACE:  gm.toggle_pause()

                #Control panel
                cp = ctrl.handle_event(event, mp)
                if cp:
                    if cp.get("action") == "new_game": _apply_new_game()
                    elif cp.get("action") == "undo":   gm.undo_last_move()

                #HUD
                ha = hud.handle_event(event, gm)
                if ha == "undo":    gm.undo_last_move()
                elif ha == "reset": gm.reset_board_only()
                elif ha == "pause": gm.toggle_pause()
                elif ha == "menu":  gm.back_to_menu()

                #Board click
                board_oy = _oy()
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                        and mp[0] < BOARD_AREA_WIDTH
                        and mp[1] >= board_oy - 5):
                    gm.handle_mouse_click(mp[0], mp[1],
                                          BOARD_OFFSET_X, board_oy, CELL_SIZE)

        gm.update()

        #Draw
        if gm.app_state == MENU_STATE:
            menu.draw(screen); pygame.display.flip()

        elif gm.app_state == AI_BATTLE_SELECT_STATE:
            ai_menu.draw(screen); pygame.display.flip()

        elif gm.app_state == PLAYING_STATE:
            board_oy = _oy()

            # 1. Vẽ background + board + pieces (không flip)
            renderer.draw_background(board_oy)
            renderer.draw_board(board_oy)
            renderer.draw_last_move(board.move_log, board_oy)
            renderer.draw_selected_piece(gm.get_selected_piece(), board_oy)
            renderer.draw_valid_moves(gm.get_valid_moves(), board_oy)

            hidden = gm.animation_hide_piece if gm.animating else None
            renderer.draw_pieces(board.get_all_pieces(), board_oy, hidden=hidden)
            anim = gm.get_animation_draw_data()
            if anim:
                renderer.draw_piece_at_float(anim["piece"], anim["row"], anim["col"], board_oy)

            renderer.draw_footer()

            hud.draw(screen, gm)

            #Control Panel (trên bàn cờ, đè lên background)
            ctrl.draw(screen, mp, gm)

            #Overlay game over
            renderer.draw_game_over_overlay(gm.game_state)

            pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()