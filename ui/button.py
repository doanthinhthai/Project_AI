import pygame


class Button:
    def __init__(self, x, y, w, h, text, bg_color, text_color, radius=10):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.radius = radius
        self.hovered = False

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen, font):
        color = self.bg_color
        if self.hovered:
            color = tuple(min(255, c + 20) for c in self.bg_color)

        pygame.draw.rect(screen, color, self.rect, border_radius=self.radius)
        pygame.draw.rect(screen, (20, 20, 20), self.rect, 2, border_radius=self.radius)

        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)