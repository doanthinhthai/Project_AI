"""
right_panel.py — Menu Panel (bên phải ~24% màn hình).
Chứa: Game Info, Turn indicator, Control Panel (diff/new game), Buttons.
"""
import pygame
from core.constants import (
    PANEL_BG, PANEL_BORDER, TEXT_COLOR, TEXT_DIM,
    TEXT_RED_SIDE, TEXT_BLK_SIDE,
    BUTTON_BG, BUTTON_BG_HOVER, BUTTON_BG_2, BUTTON_BG_2_HOV,
    BUTTON_BG_3, BUTTON_BG_3_HOV, BUTTON_BG_4, BUTTON_BG_4_HOV,
    BUTTON_TEXT_COLOR,
    RED, BLACK, PVP_MODE, PVAI_MODE, AIVAI_MODE,
    ONGOING, RED_WIN, BLACK_WIN, DRAW,
    DIFFICULTY_LEVELS, DIFFICULTY_TIME, AI_ALPHABETA,
)


def _f(size, bold=False):
    return pygame.font.SysFont("segoeui,tahoma,arial", size, bold=bold)


class _Btn:
    def __init__(self, label, bg, bg_h):
        self.label = label
        self.bg    = bg
        self.bg_h  = bg_h
        self.icon  = ""
        self.rect  = pygame.Rect(0,0,0,0)

    def draw(self, surf, mp, font):
        hov = self.rect.collidepoint(mp)
        # Shadow
        sh = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(sh,(0,0,0,50),(2,3,self.rect.w,self.rect.h),border_radius=10)
        surf.blit(sh,(self.rect.x,self.rect.y))
        # Body
        pygame.draw.rect(surf, self.bg_h if hov else self.bg,
                         self.rect, border_radius=10)
        pygame.draw.rect(surf,(0,0,0,80), self.rect, 1, border_radius=10)
        # Top shine
        shine = pygame.Rect(self.rect.x+4, self.rect.y+3,
                            self.rect.w-8, self.rect.h//3)
        sh2   = pygame.Surface((shine.w,shine.h), pygame.SRCALPHA)
        sh2.fill((255,255,255,15))
        surf.blit(sh2,(shine.x,shine.y))
        # Label
        lbl = font.render(self.label,
                          True, BUTTON_TEXT_COLOR)
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


class RightPanel:
    PAD = 14
    BTN_H = 44
    BTN_GAP = 10

    # Difficulty rows
    DIFF_LEVELS = [
        ("Bắt đầu",      1,  3.0),
        ("Sơ đẳng",      2,  5.0),
        ("Trung cấp",    3, 10.0),
        ("Trình độ cao", 4, 15.0),
        ("Bậc thầy",     5, 30.0),
    ]

    def __init__(self):
        self._head_f  = _f(16, bold=True)
        self._info_f  = _f(14)
        self._turn_f  = _f(20, bold=True)
        self._small_f = _f(13)
        self._btn_f   = _f(16, bold=True)
        self._diff_f  = _f(12)

        # Action buttons
        self._btn_undo  = _Btn("Undo Move",  BUTTON_BG,   BUTTON_BG_HOVER)
        self._btn_new   = _Btn("New Game",   BUTTON_BG_2, BUTTON_BG_2_HOV)
        self._btn_menu  = _Btn("Main Menu",  BUTTON_BG_4, BUTTON_BG_4_HOV)
        self._btn_pause = _Btn("Pause",      BUTTON_BG_3, BUTTON_BG_3_HOV)
        self._buttons   = [self._btn_undo, self._btn_new,
                           self._btn_pause, self._btn_menu]

        # Diff selection state
        self._sel_diff    = 1
        self._custom_open = False
        self._sl_depth    = 4
        self._sl_time     = 10
        self._dd_sel      = 0   # 0=red first, 1=black first

        # Diff button rects (built in draw)
        self._diff_rects  = []
        self._cust_rect   = pygame.Rect(0,0,0,0)
        self._new_game_rect = pygame.Rect(0,0,0,0)
        self._undo_rect   = pygame.Rect(0,0,0,0)

        # Custom box slider rects
        self._depth_slider_rect = pygame.Rect(0,0,0,0)
        self._time_slider_rect  = pygame.Rect(0,0,0,0)
        self._depth_drag = False
        self._time_drag  = False

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface, layout, game_manager):
        rect = layout.right_rect
        P    = self.PAD
        x0   = rect.x + P
        w    = rect.width - P*2
        mp   = pygame.mouse.get_pos()
        gm   = game_manager

        # Panel background gradient
        ps = pygame.Surface((rect.width, rect.height))
        for yi in range(rect.height):
            t=yi/rect.height
            r=int(20+8*t); g=int(12+4*t); b=int(5+2*t)
            pygame.draw.line(ps,(r,g,b),(0,yi),(rect.width,yi))
        screen.blit(ps,(rect.x,rect.y))

        # Left glow border
        for xi in range(3):
            s2 = pygame.Surface((1,rect.height),pygame.SRCALPHA)
            s2.fill((190,140,38,70-xi*22))
            screen.blit(s2,(rect.x+xi,rect.y))

        y = P

        # ── Header ────────────────────────────────────────────────────────────
        hdr = self._head_f.render("GAME INFO", True, (195,148,42))
        screen.blit(hdr,(x0,y)); y+=24
        pygame.draw.line(screen,(130,90,28),(x0,y),(rect.right-P,y),1); y+=8

        # Mode / Diff / Moves
        mode_str = {PVP_MODE:"Player vs Player",
                    PVAI_MODE:"Player vs AI",
                    AIVAI_MODE:"AI vs AI"}.get(gm.game_mode,"-")
        for lbl,val in [("Mode:", mode_str),
                        ("Diff:", gm.global_difficulty_name),
                        ("Moves:", str(len(gm.board.move_log)))]:
            ll = self._small_f.render(lbl, True, TEXT_DIM)
            vl = self._small_f.render(val, True, TEXT_COLOR)
            screen.blit(ll,(x0,y))
            screen.blit(vl,(x0+52,y)); y+=18

        y+=6
        pygame.draw.line(screen,(80,55,20),(x0,y),(rect.right-P,y),1); y+=8

        # Turn indicator
        turn_str   = "RED"   if gm.current_turn==RED else "BLACK"
        turn_color = TEXT_RED_SIDE if gm.current_turn==RED else TEXT_BLK_SIDE
        tl = self._turn_f.render(f"Turn: {turn_str}", True, turn_color)
        screen.blit(tl, tl.get_rect(centerx=rect.centerx, y=y)); y+=28

        status = gm.get_status_text()
        sc = TEXT_RED_SIDE if "RED" in status else \
             TEXT_BLK_SIDE if "BLACK" in status else (205,178,70)
        sl2 = self._info_f.render(status, True, sc)
        screen.blit(sl2, sl2.get_rect(centerx=rect.centerx, y=y)); y+=22

        if gm.paused:
            pl = self._info_f.render("⏸ PAUSED", True,(218,175,48))
            screen.blit(pl, pl.get_rect(centerx=rect.centerx,y=y)); y+=20

        y+=6
        pygame.draw.line(screen,(80,55,20),(x0,y),(rect.right-P,y),1); y+=10

        # ── Control row: Trò chơi mới + Hoàn tác ─────────────────────────────
        bh = 36
        hw = (w-6)//2
        self._new_game_rect = pygame.Rect(x0, y, hw, bh)
        self._undo_rect     = pygame.Rect(x0+hw+6, y, hw, bh)
        for r2,lbl2,bg,bg_h in [
            (self._new_game_rect,"Trò chơi mới",(85,58,25),(115,82,42)),
            (self._undo_rect,    "Hoàn tác",    (58,45,30),(88,68,45)),
        ]:
            hov = r2.collidepoint(mp)
            pygame.draw.rect(screen, bg_h if hov else bg, r2, border_radius=8)
            pygame.draw.rect(screen,(0,0,0,80),r2,1,border_radius=8)
            ll2 = self._small_f.render(lbl2,True,BUTTON_TEXT_COLOR)
            screen.blit(ll2, ll2.get_rect(center=r2.center))
        y += bh+8

        # ── Difficulty row ────────────────────────────────────────────────────
        n = len(self.DIFF_LEVELS)
        dw = (w - 8*(n) - 2) // (n+1)   # +1 for Tùy chỉnh
        cw = dw + 14
        self._diff_rects = []
        dx = x0
        for i,(name,_,_) in enumerate(self.DIFF_LEVELS):
            r3 = pygame.Rect(dx, y, dw, 28)
            self._diff_rects.append(r3)
            is_sel = (i==self._sel_diff and not self._custom_open)
            bg3 = (62,44,24) if is_sel else \
                  (95,72,42) if r3.collidepoint(mp) else (72,55,32)
            tc3 = (250,240,210) if is_sel else TEXT_DIM
            pygame.draw.rect(screen,bg3,r3,border_radius=6)
            pygame.draw.rect(screen,(0,0,0,60),r3,1,border_radius=6)
            ll3 = self._diff_f.render(name,True,tc3)
            screen.blit(ll3,ll3.get_rect(center=r3.center))
            dx += dw+4
        # Tùy chỉnh
        self._cust_rect = pygame.Rect(dx,y,cw,28)
        is_c = self._custom_open
        bg_c = (62,44,24) if is_c else \
               (95,72,42) if self._cust_rect.collidepoint(mp) else (72,55,32)
        pygame.draw.rect(screen,bg_c,self._cust_rect,border_radius=6)
        pygame.draw.rect(screen,(0,0,0,60),self._cust_rect,1,border_radius=6)
        cl4 = self._diff_f.render("★ Tùy chỉnh",True,(250,240,210) if is_c else TEXT_DIM)
        screen.blit(cl4,cl4.get_rect(center=self._cust_rect.center))
        y += 36

        # ── Custom box ────────────────────────────────────────────────────────
        if self._custom_open:
            box_h = 90
            box   = pygame.Rect(x0, y, w, box_h)
            pygame.draw.rect(screen,(30,20,8),box,border_radius=8)
            pygame.draw.rect(screen,(100,72,28),box,1,border_radius=8)
            # Depth slider
            self._draw_slider(screen, x0+8, y+18, w-16,
                              "Độ sâu", self._sl_depth, 1, 12,
                              self._depth_slider_rect, mp)
            # Time slider
            self._draw_slider(screen, x0+8, y+56, w-16,
                              "Thời gian", self._sl_time, 0, 60,
                              self._time_slider_rect, mp)
            # Update rects for events
            self._depth_slider_rect = pygame.Rect(x0+8, y+18, w-16, 14)
            self._time_slider_rect  = pygame.Rect(x0+8, y+56, w-16, 14)
            y += box_h + 6

        y += 4
        pygame.draw.line(screen,(80,55,20),(x0,y),(rect.right-P,y),1); y+=10

        # ── Action buttons ────────────────────────────────────────────────────
        bw2 = w
        for btn in self._buttons:
            if btn is self._btn_pause and gm.game_mode != AIVAI_MODE:
                continue
            btn.rect = pygame.Rect(x0, y, bw2, self.BTN_H)
            if btn is self._btn_pause:
                btn.label = "Resume" if gm.paused else "Pause"

            btn.draw(screen, mp, self._btn_f)
            y += self.BTN_H + self.BTN_GAP

        # Footer
        footer = self._small_f.render("Made by Vu Nam Sang & Thai Doan Thinh",
                                       True,(72,55,32))
        screen.blit(footer, footer.get_rect(
            centerx=rect.centerx, y=rect.bottom-18))

    def _draw_slider(self, surf, x, y, w, label, val, mn, mx, rect, mp):
        kx = x + int((val-mn)/(mx-mn)*w)
        ky = y+4
        # Track
        pygame.draw.rect(surf,(55,40,20),(x,ky,w,6),border_radius=3)
        if kx>x:
            pygame.draw.rect(surf,(130,95,42),(x,ky,kx-x,6),border_radius=3)
        # Knob
        kdrag = rect.collidepoint(mp)
        pygame.draw.circle(surf,(140,100,45) if kdrag else (115,82,38),(kx,ky+3),8)
        pygame.draw.circle(surf,(220,190,140),(kx,ky+3),8,2)
        # Label
        val_str = "∞" if (val==0 and label=="Thời gian") else \
                  f"{val}s" if label=="Thời gian" else str(val)
        lbl = pygame.font.SysFont("segoeui",12).render(
            f"{label}: {val_str}", True, TEXT_DIM)
        surf.blit(lbl,(x, y-14))

    # ── events ────────────────────────────────────────────────────────────────
    def handle_event(self, event, game_manager, layout):
        """Trả về action string hoặc None."""
        gm = game_manager
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            pos = event.pos

            if self._new_game_rect.collidepoint(pos):
                return self._do_new_game(gm)

            if self._undo_rect.collidepoint(pos):
                return "undo"

            for i,r in enumerate(self._diff_rects):
                if r.collidepoint(pos):
                    self._sel_diff    = i
                    self._custom_open = False
                    return None

            if self._cust_rect.collidepoint(pos):
                self._custom_open = not self._custom_open
                return None

            if self._btn_menu.clicked(event):  return "menu"
            if self._btn_pause.clicked(event): return "pause"

            # Depth slider drag start
            if self._depth_slider_rect.collidepoint(pos):
                self._depth_drag = True
            if self._time_slider_rect.collidepoint(pos):
                self._time_drag = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self._depth_drag = False
            self._time_drag  = False

        elif event.type == pygame.MOUSEMOTION:
            r = self._depth_slider_rect
            if self._depth_drag and r.width > 0:
                ratio = max(0.0,min(1.0,(event.pos[0]-r.x)/r.width))
                self._sl_depth = max(1, int(round(1 + ratio*11)))
            r = self._time_slider_rect
            if self._time_drag and r.width > 0:
                ratio = max(0.0,min(1.0,(event.pos[0]-r.x)/r.width))
                self._sl_time = int(round(ratio*60))

        return None

    def _do_new_game(self, gm):
        depth  = self._sl_depth if self._custom_open else self.DIFF_LEVELS[self._sel_diff][1]
        tlimit = (float(self._sl_time) if self._sl_time>0 else 9999.0) \
                  if self._custom_open else self.DIFF_LEVELS[self._sel_diff][2]
        name   = "Tùy chỉnh" if self._custom_open else self.DIFF_LEVELS[self._sel_diff][0]
        hc     = RED if self._dd_sel==0 else BLACK
        if gm.game_mode in (None, PVAI_MODE):
            gm.start_pvai(depth=depth, difficulty_name=name,
                          human_color=hc, ai_algorithm=AI_ALPHABETA)
            ai = gm.red_ai or gm.black_ai
            if ai and hasattr(ai,"engine"):
                ai.engine.time_limit = tlimit
        elif gm.game_mode == "pvp":
            gm.start_pvp()
        elif gm.game_mode == AIVAI_MODE:
            gm.start_aivai(AI_ALPHABETA,depth,AI_ALPHABETA,depth)
        return "new_game_done"