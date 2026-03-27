import pygame
from ui.button import Button
from core.constants import *


class AIBattleMenu:
    def __init__(self):
        self.title_font = pygame.font.SysFont("Arial", 38, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)

        self.red_algo = AI_MINIMAX
        self.black_algo = AI_ALPHABETA

        self.diff_names = list(DIFFICULTY_LEVELS.keys())
        self.red_diff_index = 1
        self.black_diff_index = 1

        self.red_button = Button(170, 240, 320, 50, "", BUTTON_BG, BUTTON_TEXT_COLOR)
        self.red_diff_button = Button(170, 305, 320, 50, "", BUTTON_BG_3, BUTTON_TEXT_COLOR)

        self.black_button = Button(170, 395, 320, 50, "", BUTTON_BG, BUTTON_TEXT_COLOR)
        self.black_diff_button = Button(170, 460, 320, 50, "", BUTTON_BG_3, BUTTON_TEXT_COLOR)

        self.start_button = Button(170, 560, 320, 52, "Start Match", BUTTON_BG_2, BUTTON_TEXT_COLOR)
        self.back_button = Button(170, 625, 320, 52, "Back", BUTTON_BG_4, BUTTON_TEXT_COLOR)

    def toggle_algo(self, current):
        return AI_ALPHABETA if current == AI_MINIMAX else AI_MINIMAX

    def draw(self, screen):
        screen.fill((245, 238, 220))

        title = self.title_font.render("AI vs AI Setup", True, (40, 40, 40))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        mouse_pos = pygame.mouse.get_pos()

        self.red_button.text = f"Red AI: {self.red_algo}"
        self.red_diff_button.text = f"Red Difficulty: {self.diff_names[self.red_diff_index]}"

        self.black_button.text = f"Black AI: {self.black_algo}"
        self.black_diff_button.text = f"Black Difficulty: {self.diff_names[self.black_diff_index]}"

        for button in [
            self.red_button,
            self.red_diff_button,
            self.black_button,
            self.black_diff_button,
            self.start_button,
            self.back_button,
        ]:
            button.update_hover(mouse_pos)
            button.draw(screen, self.button_font)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.red_button.is_clicked(pos):
                self.red_algo = self.toggle_algo(self.red_algo)
                return None

            if self.red_diff_button.is_clicked(pos):
                self.red_diff_index = (self.red_diff_index + 1) % len(self.diff_names)
                return None

            if self.black_button.is_clicked(pos):
                self.black_algo = self.toggle_algo(self.black_algo)
                return None

            if self.black_diff_button.is_clicked(pos):
                self.black_diff_index = (self.black_diff_index + 1) % len(self.diff_names)
                return None

            if self.start_button.is_clicked(pos):
                return (
                    "start",
                    self.red_algo,
                    DIFFICULTY_LEVELS[self.diff_names[self.red_diff_index]],
                    self.black_algo,
                    DIFFICULTY_LEVELS[self.diff_names[self.black_diff_index]],
                )

            if self.back_button.is_clicked(pos):
                return ("back",)

        return None