import pygame
from ui.button import Button
from core.constants import *


class Menu:
    def __init__(self):
        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 26, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)

        center_x = SCREEN_WIDTH // 2 - 120
        start_y = 250
        gap = 75

        self.buttons = {
            "pvsai": Button(center_x, start_y, 240, 52, "Player vs AI", BUTTON_BG, BUTTON_TEXT_COLOR),
            "aivai": Button(center_x, start_y + gap, 240, 52, "AI vs AI", BUTTON_BG, BUTTON_TEXT_COLOR),
            "pvp": Button(center_x, start_y + gap * 2, 240, 52, "Player vs Player", BUTTON_BG_2, BUTTON_TEXT_COLOR),
            "quit": Button(center_x, start_y + gap * 3, 240, 52, "Quit", BUTTON_BG_4, BUTTON_TEXT_COLOR),
        }

        self.difficulty_names = list(DIFFICULTY_LEVELS.keys())
        self.difficulty_index = 1  # Medium

        self.diff_button = Button(
            SCREEN_WIDTH // 2 - 120,
            610,
            240,
            52,
            f"Difficulty: {self.difficulty_names[self.difficulty_index]}",
            BUTTON_BG_3,
            BUTTON_TEXT_COLOR,
        )

    def draw(self, screen):
        screen.fill((245, 238, 220))

        title = self.title_font.render("Chinese Chess", True, (40, 40, 40))
        subtitle = self.small_font.render("Choose Game Mode", True, (90, 90, 90))

        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 140)))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 190)))

        mouse_pos = pygame.mouse.get_pos()

        for button in self.buttons.values():
            button.update_hover(mouse_pos)
            button.draw(screen, self.button_font)

        self.diff_button.text = f"Difficulty: {self.difficulty_names[self.difficulty_index]}"
        self.diff_button.update_hover(mouse_pos)
        self.diff_button.draw(screen, self.button_font)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.diff_button.is_clicked(pos):
                self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulty_names)
                return ("difficulty_changed", self.get_selected_depth())

            for key, button in self.buttons.items():
                if button.is_clicked(pos):
                    return (key, self.get_selected_depth())

        return None

    def get_selected_depth(self):
        return DIFFICULTY_LEVELS[self.difficulty_names[self.difficulty_index]]

    def get_selected_difficulty_name(self):
        return self.difficulty_names[self.difficulty_index]