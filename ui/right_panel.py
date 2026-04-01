"""
right_panel.py — Menu Panel (bên phải).
Chứa: Game Info, Turn indicator, Action buttons + nút Match History.
"""
import pygame
from core.constants import (
    TEXT_COLOR, TEXT_DIM, TEXT_RED_SIDE, TEXT_BLK_SIDE,
    BUTTON_BG, BUTTON_BG_HOVER, BUTTON_BG_2, BUTTON_BG_2_HOV,
    BUTTON_BG_3, BUTTON_BG_3_HOV, BUTTON_BG_4, BUTTON_BG_4_HOV,
    BUTTON_TEXT_COLOR,
    RED, BLACK, PVP_MODE, PVAI_MODE, AIVAI_MODE,
)

# Màu riêng cho nút History (tím xanh)
C_HISTORY     = ( 55,  75, 130)
C_HISTORY_HOV = ( 75, 100, 168)


def _f(size, bold=False):
    return pygame.font.SysFont("segoeui,tahoma,arial", size, bold=bold)


class _Btn:
    def __init__(self, label, bg, bg_h):
        self.label = label
        self.bg    = bg
        self.bg_h  = bg_h
        self.rect  = pygame.Rect(0, 0, 0, 0)

    def draw(self, surf, mp, font):
        hov = self.rect.collidepoint(mp)
        sh  = pygame.Surface((self.rect.w+2, self.rect.h+3), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0,0,0,52),
                         (2,3,self.rect.w,self.rect.h), border_radius=10)
        surf.blit(sh, (self.rect.x, self.rect.y))
        pygame.draw.rect(surf, self.bg_h if hov else self.bg,
                         self.rect, border_radius=10)
        shine = pygame.Rect(self.rect.x+4, self.rect.y+3,
                            self.rect.w-8, self.rect.h//3)
        sh2 = pygame.Surface((shine.w, shine.h), pygame.SRCALPHA)
        sh2.fill((255,255,255,14))
        surf.blit(sh2, (shine.x, shine.y))
        pygame.draw.rect(surf, (0,0,0,90), self.rect, 1, border_radius=10)
        lbl = font.render(self.label, True, BUTTON_TEXT_COLOR)
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


class RightPanel:
    PAD   = 14
    BTN_H = 46
    GAP   = 10

    def __init__(self):
        self._head_f  = _f(16, bold=True)
        self._info_f  = _f(14)
        self._turn_f  = _f(20, bold=True)
        self._small_f = _f(13)
        self._btn_f   = _f(16, bold=True)

        self._btn_undo    = _Btn("Undo Move",      BUTTON_BG,   BUTTON_BG_HOVER)
        self._btn_new     = _Btn("New Game",        BUTTON_BG_2, BUTTON_BG_2_HOV)
        self._btn_pause   = _Btn("Pause",           BUTTON_BG_3, BUTTON_BG_3_HOV)
        self._btn_history = _Btn("Match History",   C_HISTORY,   C_HISTORY_HOV)
        self._btn_menu    = _Btn("Main Menu",       BUTTON_BG_4, BUTTON_BG_4_HOV)

        self._bg_surf = None
        self._bg_size = (0, 0)

    def _get_bg(self, w, h):
        if self._bg_surf is None or self._bg_size != (w, h):
            s = pygame.Surface((w, h))
            for yi in range(h):
                t = yi/h
                r=int(20+8*t); g=int(12+4*t); b=int(5+2*t)
                pygame.draw.line(s,(r,g,b),(0,yi),(w,yi))
            self._bg_surf = s
            self._bg_size = (w, h)
        return self._bg_surf

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface, layout, game_manager):
        rect = layout.right_rect
        P    = self.PAD
        x0   = rect.x + P
        w    = rect.width - P * 2
        mp   = pygame.mouse.get_pos()
        gm   = game_manager

        screen.blit(self._get_bg(rect.width, rect.height), (rect.x, rect.y))

        # Left glow border
        for xi in range(3):
            s2 = pygame.Surface((1, rect.height), pygame.SRCALPHA)
            s2.fill((190,140,38, 68-xi*20))
            screen.blit(s2, (rect.x+xi, rect.y))

        y = rect.y + P

        # ── Header ────────────────────────────────────────────────────────────
        hdr = self._head_f.render("GAME INFO", True, (195,148,42))
        screen.blit(hdr, (x0, y)); y += 24
        pygame.draw.line(screen,(130,90,28),(x0,y),(rect.right-P,y),1); y += 8

        mode_str = {PVP_MODE:"Player vs Player",
                    PVAI_MODE:"Player vs AI",
                    AIVAI_MODE:"AI vs AI"}.get(gm.game_mode,"-")
        for lbl,val in [("Mode:", mode_str),
                        ("Diff:", gm.global_difficulty_name),
                        ("Moves:", str(len(gm.board.move_log)))]:
            ll = self._small_f.render(lbl, True, TEXT_DIM)
            vl = self._small_f.render(val, True, TEXT_COLOR)
            screen.blit(ll,(x0,y))
            screen.blit(vl,(x0+52,y)); y += 18

        y += 6
        pygame.draw.line(screen,(80,55,20),(x0,y),(rect.right-P,y),1); y += 10

        # ── Turn indicator ────────────────────────────────────────────────────
        turn_str   = "RED"   if gm.current_turn==RED else "BLACK"
        turn_color = TEXT_RED_SIDE if gm.current_turn==RED else TEXT_BLK_SIDE
        tl = self._turn_f.render(f"Turn: {turn_str}", True, turn_color)
        screen.blit(tl, tl.get_rect(centerx=rect.centerx, y=y)); y += 30

        status = gm.get_status_text()
        sc = (TEXT_RED_SIDE if "RED" in status else
              TEXT_BLK_SIDE if "BLACK" in status else (205,178,70))
        sl = self._info_f.render(status, True, sc)
        screen.blit(sl, sl.get_rect(centerx=rect.centerx, y=y)); y += 24

        if gm.paused:
            pl = self._info_f.render("PAUSED", True, (218,175,48))
            screen.blit(pl, pl.get_rect(centerx=rect.centerx, y=y)); y += 22

        y += 6
        pygame.draw.line(screen,(80,55,20),(x0,y),(rect.right-P,y),1); y += 14

        # ── Action buttons ────────────────────────────────────────────────────
        buttons = [self._btn_undo, self._btn_new]
        if gm.game_mode == AIVAI_MODE:
            self._btn_pause.label = "Resume" if gm.paused else "Pause"
            buttons.append(self._btn_pause)

        # Nút History — hiển thị số nước đi trong ngoặc
        n_moves = len(getattr(gm, "match_record", None).entries
                       if hasattr(gm, "match_record") else []) \
                  if hasattr(gm, "match_record") else 0
        self._btn_history.label = f"Match History ({n_moves})"
        buttons.append(self._btn_history)
        buttons.append(self._btn_menu)

        for btn in buttons:
            btn.rect = pygame.Rect(x0, y, w, self.BTN_H)
            btn.draw(screen, mp, self._btn_f)
            y += self.BTN_H + self.GAP

        # Hint phím tắt H
        hint = self._small_f.render("[ H ] để mở lịch sử", True, (85, 108, 155))
        screen.blit(hint, hint.get_rect(centerx=rect.centerx, y=y))

        # Footer
        footer = self._small_f.render("Made by Vu Nam Sang & Thai Doan Thinh",
                                       True, (72,55,32))
        screen.blit(footer, footer.get_rect(
            centerx=rect.centerx, y=rect.bottom-18))

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event, game_manager, layout):
        if self._btn_undo.clicked(event):    return "undo"
        if self._btn_new.clicked(event):
            game_manager.reset_board_only(); return "new_game_done"
        if self._btn_pause.clicked(event):   return "pause"
        if self._btn_history.clicked(event): return "history"   # ← MỚI
        if self._btn_menu.clicked(event):    return "menu"
        return None