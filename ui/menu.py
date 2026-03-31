"""
menu.py — Main menu với theme lacquer đỏ-vàng
"""
import pygame
from ui.button import Button
from core.constants import *


class Menu:
    def __init__(self):
        self.title_font  = pygame.font.SysFont("Arial", 46, bold=True)
        self.sub_font    = pygame.font.SysFont("Arial", 20)
        self.button_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.kanji_font  = pygame.font.SysFont("Arial", 72, bold=True)

        cx = SCREEN_WIDTH // 2 - 115
        sy = 275; gap = 68

        self.buttons = {
            "pvsai": Button(cx, sy,        230, 52, "Player vs AI",
                             BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER,   icon="🤖"),
            "aivai": Button(cx, sy+gap,    230, 52, "AI vs AI",
                             BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER,   icon="⚔"),
            "pvp":   Button(cx, sy+gap*2,  230, 52, "Player vs Player",
                             BUTTON_BG_2, BUTTON_TEXT_COLOR, BUTTON_BG_2_HOV,   icon="👥"),
            "quit":  Button(cx, sy+gap*3+10, 230, 48, "Quit",
                             BUTTON_BG_4, BUTTON_TEXT_COLOR, BUTTON_BG_4_HOV,   icon="✕"),
        }

        self.difficulty_names = list(DIFFICULTY_LEVELS.keys())
        self.difficulty_index = 2  # Medium

        self.diff_button = Button(
            cx, sy + gap * 4 + 20, 230, 46,
            f"Difficulty: {self.difficulty_names[self.difficulty_index]}",
            BUTTON_BG_3, BUTTON_TEXT_COLOR, BUTTON_BG_3_HOV, icon="⚙",
        )

        # Decorative particles (static dots)
        import random
        rng = random.Random(42)
        self._dots = [(rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT),
                       rng.randint(1, 3), rng.randint(30, 90))
                      for _ in range(55)]

    def draw(self, screen):
        # Background gradient (manual)
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(22 + 12 * ratio)
            g = int(12 +  6 * ratio)
            b = int(4  +  2 * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Decorative dots
        for dx, dy, dr, dalpha in self._dots:
            s = pygame.Surface((dr*2, dr*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (210, 165, 60, dalpha), (dr, dr), dr)
            screen.blit(s, (dx - dr, dy - dr))

        # Decorative vertical lines
        for xi in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, (255, 200, 80, 12),
                             (xi, 0), (xi, SCREEN_HEIGHT), 1)

        # Side ornament bars
        pygame.draw.rect(screen, (140, 85, 25),  (0, 0, 6, SCREEN_HEIGHT))
        pygame.draw.rect(screen, (140, 85, 25),  (SCREEN_WIDTH-6, 0, 6, SCREEN_HEIGHT))

        # Title card
        card_w, card_h = 420, 160
        card_x = SCREEN_WIDTH // 2 - card_w // 2
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (0, 0, 0, 80), (0, 0, card_w, card_h), border_radius=18)
        pygame.draw.rect(card_surf, (200, 145, 40, 120), (0, 0, card_w, card_h), 2, border_radius=18)
        screen.blit(card_surf, (card_x, 55))

        # Chinese title
        ch = self.kanji_font.render("象棋", True, (215, 165, 50))
        screen.blit(ch, ch.get_rect(center=(SCREEN_WIDTH//2, 100)))

        # English title
        title = self.title_font.render("Chinese Chess", True, (240, 210, 140))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 162)))

        sub = self.sub_font.render("Select a game mode to begin", True, (165, 138, 90))
        screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, 200)))

        # Divider
        pygame.draw.line(screen, (160, 110, 35),
                         (SCREEN_WIDTH//2 - 160, 228),
                         (SCREEN_WIDTH//2 + 160, 228), 2)

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons.values():
            btn.update_hover(mouse_pos)
            btn.draw(screen, self.button_font)

        self.diff_button.text = f"Difficulty: {self.difficulty_names[self.difficulty_index]}"
        self.diff_button.update_hover(mouse_pos)
        self.diff_button.draw(screen, self.button_font)

        # Footer
        footer = self.sub_font.render("Made by Vu Nam Sang & Thai Doan Thinh", True, (100, 78, 45))
        screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 22)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.diff_button.is_clicked(pos):
                self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulty_names)
                return ("difficulty_changed", self.get_selected_depth())
            for key, btn in self.buttons.items():
                if btn.is_clicked(pos):
                    return (key, self.get_selected_depth())
        return None

    def get_selected_depth(self):
        return DIFFICULTY_LEVELS[self.difficulty_names[self.difficulty_index]]

    def get_selected_difficulty_name(self):
        return self.difficulty_names[self.difficulty_index]