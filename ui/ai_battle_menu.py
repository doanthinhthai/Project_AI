
import pygame
from ui.button import Button
from core.constants import *


class AIBattleMenu:
    def __init__(self):
        self.title_font  = pygame.font.SysFont("Arial", 38, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 21, bold=True)
        self.label_font  = pygame.font.SysFont("Arial", 17)
        self.sub_font    = pygame.font.SysFont("Arial", 19)

        self.red_algo   = AI_ALPHABETA
        self.black_algo = AI_ALPHABETA

        self.diff_names      = list(DIFFICULTY_LEVELS.keys())
        self.red_diff_index  = 2
        self.black_diff_index = 2

        cx = SCREEN_WIDTH // 2
        lx = cx - 250   # left column x
        rx = cx + 30    # right column x
        cw = 210        # column width

        #RED column
        self.red_algo_btn  = Button(lx, 240, cw, 46, "", BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER)
        self.red_diff_btn  = Button(lx, 298, cw, 46, "", BUTTON_BG_3, BUTTON_TEXT_COLOR, BUTTON_BG_3_HOV)

        #BLACK column
        self.blk_algo_btn  = Button(rx, 240, cw, 46, "", BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER)
        self.blk_diff_btn  = Button(rx, 298, cw, 46, "", BUTTON_BG_3, BUTTON_TEXT_COLOR, BUTTON_BG_3_HOV)

        #Action
        self.start_btn = Button(cx - 130, 420, 260, 54, "Start Match",
                                 BUTTON_BG_2, BUTTON_TEXT_COLOR, BUTTON_BG_2_HOV, icon="▶")
        self.back_btn  = Button(cx - 130, 490, 260, 46, "Back to Menu",
                                 BUTTON_BG_4, BUTTON_TEXT_COLOR, BUTTON_BG_4_HOV, icon="←")

    def _toggle_algo(self, current):
        return AI_MINIMAX if current == AI_ALPHABETA else AI_ALPHABETA

    def draw(self, screen):
        # Background (same gradient as menu)
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(22 + 12 * ratio); g = int(12 + 6 * ratio); b = int(4 + 2 * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        pygame.draw.rect(screen, (140, 85, 25), (0, 0, 6, SCREEN_HEIGHT))
        pygame.draw.rect(screen, (140, 85, 25), (SCREEN_WIDTH-6, 0, 6, SCREEN_HEIGHT))

        cx = SCREEN_WIDTH // 2

        # Title
        title = self.title_font.render("AI  vs  AI  Setup", True, (240, 205, 120))
        screen.blit(title, title.get_rect(center=(cx, 95)))
        pygame.draw.line(screen, (160, 110, 35), (cx-200, 128), (cx+200, 128), 2)

        # Column headers
        lx, rx = cx - 250, cx + 30
        cw = 210

        red_lbl = self.sub_font.render("🔴  Red Side", True, (230, 90, 90))
        blk_lbl = self.sub_font.render("⚫  Black Side", True, (120, 175, 240))
        screen.blit(red_lbl, red_lbl.get_rect(centerx=lx+cw//2, y=195))
        screen.blit(blk_lbl, blk_lbl.get_rect(centerx=rx+cw//2, y=195))

        # Separator
        pygame.draw.line(screen, (100, 70, 30), (cx, 185), (cx, 390), 1)

        mouse_pos = pygame.mouse.get_pos()

        # Update labels
        self.red_algo_btn.text  = f"Algo: {self.red_algo}"
        self.red_diff_btn.text  = f"Level: {self.diff_names[self.red_diff_index]}"
        self.blk_algo_btn.text  = f"Algo: {self.black_algo}"
        self.blk_diff_btn.text  = f"Level: {self.diff_names[self.black_diff_index]}"

        for btn in (self.red_algo_btn, self.red_diff_btn,
                    self.blk_algo_btn, self.blk_diff_btn,
                    self.start_btn, self.back_btn):
            btn.update_hover(mouse_pos)
            btn.draw(screen, self.button_font)

        # Info summary
        rd = self.diff_names[self.red_diff_index]
        bd = self.diff_names[self.black_diff_index]
        info = self.label_font.render(
            f"Red depth {DIFFICULTY_LEVELS[rd]}  vs  Black depth {DIFFICULTY_LEVELS[bd]}",
            True, (155, 130, 80))
        screen.blit(info, info.get_rect(center=(cx, 382)))

        footer = self.label_font.render("Made by Vu Nam Sang & Thai Doan Thinh", True, (90, 72, 42))
        screen.blit(footer, footer.get_rect(center=(cx, SCREEN_HEIGHT - 22)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.red_algo_btn.is_clicked(pos):
                self.red_algo = self._toggle_algo(self.red_algo); return None
            if self.red_diff_btn.is_clicked(pos):
                self.red_diff_index = (self.red_diff_index + 1) % len(self.diff_names); return None
            if self.blk_algo_btn.is_clicked(pos):
                self.black_algo = self._toggle_algo(self.black_algo); return None
            if self.blk_diff_btn.is_clicked(pos):
                self.black_diff_index = (self.black_diff_index + 1) % len(self.diff_names); return None
            if self.start_btn.is_clicked(pos):
                return (
                    "start",
                    self.red_algo,
                    DIFFICULTY_LEVELS[self.diff_names[self.red_diff_index]],
                    self.black_algo,
                    DIFFICULTY_LEVELS[self.diff_names[self.black_diff_index]],
                )
            if self.back_btn.is_clicked(pos):
                return ("back",)
        return None