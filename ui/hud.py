"""
hud.py — Right-side HUD panel
"""
import pygame
from ui.button import Button
from core.constants import *


class HUD:
    def __init__(self):
        self.title_font  = pygame.font.SysFont("Arial", 17, bold=True)
        self.info_font   = pygame.font.SysFont("Arial", 16)
        self.small_font  = pygame.font.SysFont("Arial", 14)
        self.button_font = pygame.font.SysFont("Arial", 19, bold=True)
        self.kanji_font  = pygame.font.SysFont("Arial", 28, bold=True)

        px = BOARD_AREA_WIDTH + (PANEL_WIDTH - BUTTON_WIDTH) // 2

        self.undo_btn  = Button(px, UNDO_BUTTON_Y,  BUTTON_WIDTH, BUTTON_HEIGHT,
                                 "Undo Move",  BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER,  icon="↩")
        self.reset_btn = Button(px, RESET_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT,
                                 "New Game",   BUTTON_BG_2, BUTTON_TEXT_COLOR, BUTTON_BG_2_HOV,  icon="↺")
        self.pause_btn = Button(px, PAUSE_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT,
                                 "Pause",      BUTTON_BG_3, BUTTON_TEXT_COLOR, BUTTON_BG_3_HOV,  icon="⏸")
        self.menu_btn  = Button(px, MENU_BUTTON_Y,  BUTTON_WIDTH, BUTTON_HEIGHT,
                                 "Main Menu",  BUTTON_BG_4, BUTTON_TEXT_COLOR, BUTTON_BG_4_HOV,  icon="🏠")

    #helpers
    def _draw_section(self, screen, px, y, title, lines, title_color=None):
        tc = title_color or (200, 165, 80)
        tl = self.title_font.render(title, True, tc)
        screen.blit(tl, (px + 14, y))
        y += 22
        for line, color in lines:
            lbl = self.info_font.render(line, True, color or TEXT_DIM)
            screen.blit(lbl, (px + 18, y))
            y += 22
        return y + 6

    def _draw_move_log(self, screen, px, y, move_log):
        """Hiển thị 6 nước đi gần nhất."""
        lbl = self.title_font.render("Recent Moves", True, (200, 165, 80))
        screen.blit(lbl, (px + 14, y)); y += 22

        recent = move_log[-6:]
        total  = len(move_log)
        for i, move in enumerate(recent):
            n   = total - len(recent) + i + 1
            col = TEXT_RED_SIDE if (n % 2 == 1) else TEXT_BLK_SIDE
            notation = f"{n:2}. {move.get_chess_notation()}"
            lbl = self.small_font.render(notation, True, col)
            screen.blit(lbl, (px + 18, y)); y += 18
        return y + 4

    #main draw

    def draw(self, screen, game_manager):
        px = BOARD_AREA_WIDTH

        # Panel background with gradient feel
        panel_surf = pygame.Surface((PANEL_WIDTH, SCREEN_HEIGHT))
        for yi in range(SCREEN_HEIGHT):
            ratio = yi / SCREEN_HEIGHT
            r = int(28 + 8 * ratio); g = int(18 + 4 * ratio); b = int(6 + 2 * ratio)
            pygame.draw.line(panel_surf, (r, g, b), (0, yi), (PANEL_WIDTH, yi))
        screen.blit(panel_surf, (px, 0))

        # Left border glow
        for xi in range(3):
            alpha = 80 - xi * 25
            s = pygame.Surface((1, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((200, 148, 40, alpha))
            screen.blit(s, (px + xi, 0))

        #Header
        hdr = pygame.Surface((PANEL_WIDTH, 58), pygame.SRCALPHA)
        pygame.draw.rect(hdr, (0, 0, 0, 60), (0, 0, PANEL_WIDTH, 58))
        screen.blit(hdr, (px, 0))

        kanji = self.kanji_font.render("象棋", True, (195, 148, 42))
        screen.blit(kanji, kanji.get_rect(centerx=px + PANEL_WIDTH//2, y=10))

        pygame.draw.line(screen, (160, 110, 30),
                         (px + 12, 56), (px + PANEL_WIDTH - 12, 56), 1)

        y = 70

        #Game Info section
        gm = game_manager
        mode_map = {PVP_MODE: "Player vs Player",
                    PVAI_MODE: "Player vs AI",
                    AIVAI_MODE: "AI vs AI"}
        mode_str = mode_map.get(gm.game_mode, "-")

        turn_str   = "RED"   if gm.current_turn == RED else "BLACK"
        turn_color = TEXT_RED_SIDE if gm.current_turn == RED else TEXT_BLK_SIDE

        status_str   = gm.get_status_text()
        status_color = TEXT_RED_SIDE if "RED" in status_str else \
                       TEXT_BLK_SIDE if "BLACK" in status_str else (210, 185, 75)

        y = self._draw_section(screen, px, y, "GAME INFO", [
            (f"Mode:   {mode_str}",             TEXT_DIM),
            (f"Diff:    {gm.global_difficulty_name}", TEXT_DIM),
            (f"Moves:  {len(gm.board.move_log)}",     TEXT_DIM),
        ])

        # Turn indicator (larger)
        pygame.draw.line(screen, (80, 55, 20),
                         (px+12, y-4), (px+PANEL_WIDTH-12, y-4), 1)
        turn_lbl = pygame.font.SysFont("Arial", 22, bold=True).render(
            f"Turn: {turn_str}", True, turn_color)
        screen.blit(turn_lbl, turn_lbl.get_rect(centerx=px+PANEL_WIDTH//2, y=y))
        y += 30

        status_lbl = pygame.font.SysFont("Arial", 17).render(
            status_str, True, status_color)
        screen.blit(status_lbl, status_lbl.get_rect(centerx=px+PANEL_WIDTH//2, y=y))
        y += 30

        if gm.paused:
            paused_lbl = pygame.font.SysFont("Arial", 16, bold=True).render(
                "⏸  PAUSED", True, (220, 180, 50))
            screen.blit(paused_lbl, paused_lbl.get_rect(centerx=px+PANEL_WIDTH//2, y=y))
            y += 26

        pygame.draw.line(screen, (80, 55, 20),
                         (px+12, y), (px+PANEL_WIDTH-12, y), 1)
        y += 8

        #AI info
        if gm.red_ai or gm.black_ai:
            ai_lines = []
            if gm.red_ai:
                ai_lines.append((f"Red  AI: {gm.red_ai.algorithm}  d={gm.red_ai.max_depth}",
                                  TEXT_RED_SIDE))
                ai_lines.append((f"  think: {gm.red_ai.last_think_time:.3f}s", TEXT_DIM))
            if gm.black_ai:
                ai_lines.append((f"Black AI: {gm.black_ai.algorithm}  d={gm.black_ai.max_depth}",
                                  TEXT_BLK_SIDE))
                ai_lines.append((f"  think: {gm.black_ai.last_think_time:.3f}s", TEXT_DIM))
            y = self._draw_section(screen, px, y, "AI STATUS", ai_lines)
            pygame.draw.line(screen, (80, 55, 20),
                             (px+12, y-4), (px+PANEL_WIDTH-12, y-4), 1)
            y += 4

        #Move log
        y = self._draw_move_log(screen, px, y, gm.board.move_log)
        pygame.draw.line(screen, (80, 55, 20),
                         (px+12, y), (px+PANEL_WIDTH-12, y), 1)

        #buttons
        mouse_pos = pygame.mouse.get_pos()
        self.undo_btn.update_hover(mouse_pos)
        self.reset_btn.update_hover(mouse_pos)
        self.pause_btn.update_hover(mouse_pos)
        self.menu_btn.update_hover(mouse_pos)

        if gm.game_mode == AIVAI_MODE:
            self.pause_btn.text = "Resume" if gm.paused else "Pause"
            self.pause_btn.icon = "▶" if gm.paused else "⏸"
            self.pause_btn.draw(screen, self.button_font)

        self.undo_btn.draw(screen, self.button_font)
        self.reset_btn.draw(screen, self.button_font)
        self.menu_btn.draw(screen, self.button_font)

        #Footer
        footer = self.small_font.render("Made by Vu Nam Sang & Thai Doan Thinh",
                                         True, (80, 62, 35))
        screen.blit(footer, footer.get_rect(center=(px + PANEL_WIDTH//2, SCREEN_HEIGHT - 18)))

    def handle_event(self, event, game_manager):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.undo_btn.is_clicked(pos):  return "undo"
            if self.reset_btn.is_clicked(pos): return "reset"
            if game_manager.game_mode == AIVAI_MODE and self.pause_btn.is_clicked(pos):
                return "pause"
            if self.menu_btn.is_clicked(pos):  return "menu"
        return None