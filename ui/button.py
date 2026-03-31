"""
button.py — Button widget với hover animation và icon support
"""
import pygame
from core.constants import BUTTON_BG, BUTTON_BG_HOVER, BUTTON_TEXT_COLOR


class Button:
    """
    Button đa năng: hỗ trợ hover animation, icon prefix, active state.
    """
    def __init__(self, x, y, w, h, text,
                 bg_color=None, text_color=None,
                 hover_color=None, radius=10, icon=None):
        self.rect        = pygame.Rect(x, y, w, h)
        self.text        = text
        self.bg_color    = bg_color    or BUTTON_BG
        self.text_color  = text_color  or BUTTON_TEXT_COLOR
        self.hover_color = hover_color or BUTTON_BG_HOVER
        self.radius      = radius
        self.icon        = icon         # optional emoji / text prefix
        self.hovered     = False
        self.active      = False        # selected / toggled state

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen, font, active_color=None):
        if self.active and active_color:
            bg = active_color
        elif self.hovered:
            bg = self.hover_color
        else:
            bg = self.bg_color

        # Shadow
        shadow_surf = pygame.Surface((self.rect.w+2, self.rect.h+3), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0,0,0,55),
                         (2,3,self.rect.w,self.rect.h), border_radius=self.radius)
        screen.blit(shadow_surf, (self.rect.x, self.rect.y))

        # Body
        pygame.draw.rect(screen, bg, self.rect, border_radius=self.radius)

        # Top shine
        shine = pygame.Rect(self.rect.x+4, self.rect.y+3,
                            self.rect.w-8, self.rect.h//3)
        shine_surf = pygame.Surface((shine.w, shine.h), pygame.SRCALPHA)
        shine_surf.fill((255,255,255,16))
        screen.blit(shine_surf, (shine.x, shine.y))

        # Border
        pygame.draw.rect(screen, (0,0,0,100), self.rect, 2,
                         border_radius=self.radius)

        # Label — chỉ dùng text, không dùng emoji icon
        surf = font.render(self.text, True, self.text_color)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def clicked_event(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))