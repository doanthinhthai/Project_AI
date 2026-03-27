import pygame
from ui.button import Button
from core.constants import *


class HUD:
    def __init__(self):
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 21)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.button_font = pygame.font.SysFont("Arial", 22, bold=True)

        panel_x = BOARD_AREA_WIDTH + (PANEL_WIDTH - BUTTON_WIDTH) // 2

        self.undo_button = Button(panel_x, UNDO_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Undo", BUTTON_BG, BUTTON_TEXT_COLOR)
        self.reset_button = Button(panel_x, RESET_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Reset", BUTTON_BG_2, BUTTON_TEXT_COLOR)
        self.pause_button = Button(panel_x, PAUSE_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Pause", BUTTON_BG_3, BUTTON_TEXT_COLOR)
        self.menu_button = Button(panel_x, MENU_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "Menu", BUTTON_BG_4, BUTTON_TEXT_COLOR)

    def draw(self, screen, game_manager):
        panel_x = BOARD_AREA_WIDTH
        pygame.draw.rect(screen, PANEL_BG, (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(screen, BLACK_COLOR, (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)

        y = 35

        title = self.title_font.render("CONTROL PANEL", True, TEXT_COLOR)
        screen.blit(title, (panel_x + 35, y))
        y += 55

        info_lines = [
            f"Mode: {game_manager.game_mode}",
            f"Turn: {'RED' if game_manager.current_turn == RED else 'BLACK'}",
            f"Status: {game_manager.get_status_text()}",
            f"Paused: {'Yes' if game_manager.paused else 'No'}",
            f"Difficulty: {game_manager.global_difficulty_name}",
        ]

        if game_manager.red_ai is not None:
            info_lines.append(f"Red AI: {game_manager.red_ai.algorithm} d={game_manager.red_ai.max_depth}")
            info_lines.append(f"Red think: {game_manager.red_ai.last_think_time:.3f}s")

        if game_manager.black_ai is not None:
            info_lines.append(f"Black AI: {game_manager.black_ai.algorithm} d={game_manager.black_ai.max_depth}")
            info_lines.append(f"Black think: {game_manager.black_ai.last_think_time:.3f}s")

        for line in info_lines:
            txt = self.text_font.render(line, True, TEXT_COLOR)
            screen.blit(txt, (panel_x + 18, y))
            y += 34

        mouse_pos = pygame.mouse.get_pos()

        self.undo_button.update_hover(mouse_pos)
        self.reset_button.update_hover(mouse_pos)
        self.pause_button.update_hover(mouse_pos)
        self.menu_button.update_hover(mouse_pos)

        if game_manager.game_mode == AIVAI_MODE:
            self.pause_button.text = "Resume" if game_manager.paused else "Pause"
            self.pause_button.draw(screen, self.button_font)

        self.undo_button.draw(screen, self.button_font)
        self.reset_button.draw(screen, self.button_font)
        self.menu_button.draw(screen, self.button_font)

        footer = self.small_font.render("Made by Vu Nam Sang & Thai Doan Thinh", True, TEXT_COLOR)
        footer_rect = footer.get_rect(center=(panel_x + PANEL_WIDTH // 2, SCREEN_HEIGHT - 32))
        screen.blit(footer, footer_rect)

    def handle_event(self, event, game_manager):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.undo_button.is_clicked(pos):
                return "undo"
            if self.reset_button.is_clicked(pos):
                return "reset"
            if game_manager.game_mode == AIVAI_MODE and self.pause_button.is_clicked(pos):
                return "pause"
            if self.menu_button.is_clicked(pos):
                return "menu"

        return None