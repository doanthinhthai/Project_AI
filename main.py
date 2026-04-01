"""
main.py — Entry point. Layout 3 vùng rõ ràng, không hardcode.
"""
import sys
import pygame

from core.constants import (
    WIN_W, WIN_H, FPS,
    MENU_STATE, AI_BATTLE_SELECT_STATE, PLAYING_STATE,
    PVP_MODE, PVAI_MODE, AIVAI_MODE,
    RED, AI_ALPHABETA, DIFFICULTY_TIME,
)
from game.board         import Board
from game.game_manager  import GameManager
from ui.layout          import Layout
from ui.renderer        import Renderer
from ui.left_panel      import LeftPanel
from ui.right_panel     import RightPanel
from ui.menu            import Menu
from ui.ai_battle_menu  import AIBattleMenu
from ui.history_panel   import HistoryPanel


def main():
    pygame.init()
    pygame.display.set_caption("象棋  Chinese Chess")
    try:
        pygame.display.set_icon(pygame.image.load("assets/icon.png"))
    except Exception:
        pass

    # Window có thể resize
    screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
    clock  = pygame.time.Clock()

    board      = Board()
    gm         = GameManager(board)
    layout     = Layout(WIN_W, WIN_H)
    renderer   = Renderer(screen, layout)
    left_panel = LeftPanel()
    right_panel= RightPanel()
    menu       = Menu()
    ai_menu       = AIBattleMenu()
    history_panel = HistoryPanel()

    running = True
    while running:
        mp = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False; break

            # ── Resize window ──────────────────────────────────────────────
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE)
                layout.rebuild(event.w, event.h)
                renderer.screen = screen
                renderer._board_surf = None   # force rebuild

            # ── MENU ──────────────────────────────────────────────────────
            if gm.app_state == MENU_STATE:
                res = menu.handle_event(event)
                if res:
                    action = res[0]; depth = res[1] if len(res)>1 else 3
                    if action == "pvp":
                        gm.start_pvp()
                    elif action == "pvsai":
                        diff_name = menu.get_selected_difficulty_name()
                        algo      = menu.get_selected_algo()
                        gm.start_pvai(depth=depth, difficulty_name=diff_name,
                                      human_color=RED, ai_algorithm=algo)
                        ai = gm.red_ai or gm.black_ai
                        if ai:
                            ai.set_difficulty(diff_name)
                    elif action == "aivai":
                        gm.app_state = AI_BATTLE_SELECT_STATE
                    elif action == "quit":
                        running = False; break

            # ── AI BATTLE SETUP ───────────────────────────────────────────
            elif gm.app_state == AI_BATTLE_SELECT_STATE:
                res = ai_menu.handle_event(event)
                if res:
                    if res[0]=="back": gm.app_state=MENU_STATE
                    elif res[0]=="start":
                        _, ra, rd, ba, bd = res
                        gm.start_aivai(ra, rd, ba, bd)
                        if gm.red_ai:   gm.red_ai.set_difficulty(ai_menu.red_diff_name)
                        if gm.black_ai: gm.black_ai.set_difficulty(ai_menu.black_diff_name)

            # ── IN-GAME ───────────────────────────────────────────────────
            elif gm.app_state == PLAYING_STATE:
                if event.type == pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        if history_panel.visible: history_panel.hide()
                        else: gm.back_to_menu()
                    elif event.key==pygame.K_z and pygame.key.get_mods()&pygame.KMOD_CTRL:
                        gm.undo_last_move()
                    elif event.key==pygame.K_r:      gm.reset_board_only()
                    elif event.key==pygame.K_SPACE:  gm.toggle_pause()
                    elif event.key==pygame.K_h:      # H = History
                        history_panel.show(gm.match_record)

                # History panel (ưu tiên cao nhất)
                if history_panel.handle_event(event):
                    continue

                # Right panel events
                action = right_panel.handle_event(event, gm, layout)
                if action == "undo":    gm.undo_last_move()
                elif action == "pause":  gm.toggle_pause()
                elif action == "history":
                    history_panel.show(gm.match_record)
                elif action == "menu":   gm.back_to_menu()

                # Board click — chỉ khi click trong vùng MID
                if (event.type==pygame.MOUSEBUTTONDOWN and event.button==1
                        and layout.mid_rect.collidepoint(mp)):
                    cell = layout.cell_at(mp[0], mp[1])
                    if cell:
                        row, col = cell
                        gm.handle_mouse_click(
                            mp[0], mp[1],
                            layout.board_ox, layout.board_oy,
                            layout.cell_size)

        gm.update()

        # Tự động mở history panel khi ván kết thúc lần đầu
        if (gm.app_state == PLAYING_STATE
                and gm.game_state not in ("ongoing",)
                and not history_panel.visible
                and len(gm.match_record.entries) > 0
                and gm.match_record.end_time is not None):
            history_panel.show(gm.match_record)

        # ── Draw ──────────────────────────────────────────────────────────────
        if gm.app_state == MENU_STATE:
            menu.draw(screen); pygame.display.flip()

        elif gm.app_state == AI_BATTLE_SELECT_STATE:
            ai_menu.draw(screen); pygame.display.flip()

        elif gm.app_state == PLAYING_STATE:
            renderer.render(board, gm, left_panel, right_panel)

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()