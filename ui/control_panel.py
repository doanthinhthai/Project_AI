"""
control_panel.py — Panel điều khiển phía TRÊN bàn cờ.

Layout (từ trên xuống):
  Hàng 1 : [Trò chơi mới]  [Hoàn tác]  Chơi như: [Dropdown ▼]
  Hàng 2 : [Bắt đầu][Sơ đẳng][Trung cấp][Trình độ cao][Bậc thầy]  [Tùy chỉnh★]
  Hàng 3 : (box) Slider độ sâu + Slider thời gian + ghi chú
"""
import pygame
from core.constants import (
    RED, BLACK,
    PVP_MODE, PVAI_MODE, AIVAI_MODE,
    DIFFICULTY_LEVELS, DIFFICULTY_TIME,
    AI_ALPHABETA,
)

# ── Palette (kem nhạt / nâu đất) ──────────────────────────────────────────────
C_BG        = (245, 230, 211)   # #F5E6D3  nền panel
C_CARD      = (255, 245, 235)   # card nội dung box
C_BTN       = (193, 167, 139)   # #C1A78B  nút thường
C_BTN_HOV   = (175, 148, 118)   # hover
C_BTN_ACT   = ( 74,  55,  40)   # #4A3728  đang chọn / active
C_BTN_NEW   = ( 90,  62,  38)   # Trò chơi mới (đậm hơn)
C_BTN_NEW_H = (115,  82,  52)
C_BTN_UNDO  = (160, 130, 100)
C_BTN_UNDO_H= (140, 108,  80)
C_TEXT_DARK = ( 40,  25,  12)
C_TEXT_LIGHT= (252, 246, 238)
C_TEXT_DIM  = (130, 100,  72)
C_SLIDER_BG = (210, 190, 168)
C_SLIDER_FG = ( 74,  55,  40)
C_KNOB      = ( 74,  55,  40)
C_KNOB_HOV  = (110,  82,  55)
C_BORDER    = (180, 155, 128)
C_DD_BG     = (250, 242, 232)
C_SHADOW    = (180, 155, 128, 60)

# Độ khó
DIFF_LEVELS = [
    ("Bắt đầu",      1,  3.0),
    ("Sơ đẳng",      2,  5.0),
    ("Trung cấp",    3, 10.0),
    ("Trình độ cao", 4, 15.0),
    ("Bậc thầy",     5, 30.0),
]

# ── Font helper ────────────────────────────────────────────────────────────────
_fc: dict = {}
def _f(size, bold=False):
    k = (size, bold)
    if k not in _fc:
        _fc[k] = pygame.font.SysFont("segoeui,tahoma,arial", size, bold=bold)
    return _fc[k]


# ── Rounded rect helper ────────────────────────────────────────────────────────
def _rrect(surf, color, rect, r=10, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=r)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=r)


def _shadow_rect(surf, rect, r=10, offset=3, alpha=55):
    sh = pygame.Surface((rect.w + offset, rect.h + offset), pygame.SRCALPHA)
    pygame.draw.rect(sh, (100, 70, 40, alpha),
                     (0, 0, rect.w + offset, rect.h + offset), border_radius=r)
    surf.blit(sh, (rect.x + 1, rect.y + offset))


# ── Slider ────────────────────────────────────────────────────────────────────
class _Slider:
    KR = 9

    def __init__(self, label, mn, mx, val, step=1, unit=""):
        self.label    = label
        self.mn       = mn
        self.mx       = mx
        self.value    = val
        self.step     = step
        self.unit     = unit
        self.dragging = False
        # geometry set by ControlPanel.layout()
        self.x = self.y = self.w = 0

    @property
    def _kx(self):
        r = (self.value - self.mn) / max(1, self.mx - self.mn)
        return int(self.x + r * self.w)

    def _ky(self): return self.y + 6 + 4

    def draw(self, surf):
        ky = self._ky()
        # Track
        trk = pygame.Rect(self.x, self.y + 6, self.w, 8)
        _rrect(surf, C_SLIDER_BG, trk, r=4)
        # Fill
        fw = max(0, self._kx - self.x)
        if fw:
            _rrect(surf, C_SLIDER_FG, pygame.Rect(self.x, self.y+6, fw, 8), r=4)
        # Knob shadow
        ksh = pygame.Surface((self.KR*2+4, self.KR*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ksh, (80, 50, 20, 50), (self.KR+4, self.KR+4), self.KR)
        surf.blit(ksh, (self._kx - self.KR + 1, ky - self.KR))
        # Knob
        kc = C_KNOB_HOV if self.dragging else C_KNOB
        pygame.draw.circle(surf, kc, (self._kx, ky), self.KR)
        pygame.draw.circle(surf, (255, 245, 230), (self._kx, ky), self.KR, 2)
        # Label + value
        if self.value == 0 and self.unit == "giây":
            val_str = "0 (không giới hạn)"
        elif self.unit:
            val_str = f"{self.value} {self.unit}"
        else:
            val_str = str(self.value)
        lbl = _f(14).render(f"{self.label}:  {val_str}", True, C_TEXT_DARK)
        surf.blit(lbl, (self.x, self.y - 20))

    def handle_event(self, event):
        ky = self._ky()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if (abs(event.pos[0]-self._kx) <= self.KR+6
                    and abs(event.pos[1]-ky) <= self.KR+6):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            r = max(0.0, min(1.0, (event.pos[0] - self.x) / max(1, self.w)))
            self.value = int(round((self.mn + r*(self.mx-self.mn)) / self.step) * self.step)
            return True
        return False


# ── Dropdown ──────────────────────────────────────────────────────────────────
class _Dropdown:
    def __init__(self, x, y, w, h, options, selected=0):
        self.rect     = pygame.Rect(x, y, w, h)
        self.options  = options
        self.selected = selected
        self.open     = False

    @property
    def value(self): return self.options[self.selected]

    def draw(self, surf, mp):
        _shadow_rect(surf, self.rect, r=8)
        _rrect(surf, C_DD_BG, self.rect, r=8,
               border=1, border_color=C_BORDER)
        lbl = _f(15).render(self.options[self.selected], True, C_TEXT_DARK)
        surf.blit(lbl, lbl.get_rect(midleft=(self.rect.x+10, self.rect.centery)))
        # Arrow
        ax, ay = self.rect.right-14, self.rect.centery
        col = C_BTN_ACT if self.open else C_TEXT_DIM
        pygame.draw.polygon(surf, col, [(ax-5,ay-3),(ax+5,ay-3),(ax,ay+5)])

        if self.open:
            for i, opt in enumerate(self.options):
                ir = pygame.Rect(self.rect.x,
                                 self.rect.bottom + i*self.rect.height,
                                 self.rect.width, self.rect.height)
                bg = C_BTN_HOV if ir.collidepoint(mp) else C_DD_BG
                _rrect(surf, bg, ir, r=6, border=1, border_color=C_BORDER)
                tl = _f(15).render(opt, True, C_TEXT_DARK)
                surf.blit(tl, tl.get_rect(midleft=(ir.x+10, ir.centery)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open; return True
            if self.open:
                for i in range(len(self.options)):
                    ir = pygame.Rect(self.rect.x,
                                     self.rect.bottom + i*self.rect.height,
                                     self.rect.width, self.rect.height)
                    if ir.collidepoint(event.pos):
                        self.selected = i; self.open = False; return True
                self.open = False
        return False


# ═════════════════════════════════════════════════════════════════════════════
# CONTROL PANEL
# ═════════════════════════════════════════════════════════════════════════════
class ControlPanel:
    """
    Vẽ panel điều khiển vào một vùng (x, y, w) trên màn hình.
    Trả về chiều cao thực tế đã dùng (để renderer biết board bắt đầu ở đâu).
    """
    PANEL_PAD  = 12   # padding trong panel
    ROW1_H     = 40
    ROW2_H     = 34
    BOX_H      = 110  # chiều cao box tùy chỉnh
    ROW_GAP    = 8

    def __init__(self, x: int, y: int, w: int):
        self.x = x
        self.y = y
        self.w = w

        self._custom_open = False
        self._sel_diff    = 1            # "Sơ đẳng" mặc định

        P = self.PANEL_PAD
        iw = w - P*2   # inner width
        ix = x + P
        iy = y + P

        # ── Row 1 ─────────────────────────────────────────────────────────────
        self._btn_new  = pygame.Rect(ix,        iy, 155, self.ROW1_H)
        self._btn_undo = pygame.Rect(ix+163,    iy,  90, self.ROW1_H)
        dd_x = ix + 163 + 90 + 12
        self._lbl_side_x = dd_x
        self._dd = _Dropdown(dd_x + 62, iy+4, 168, 32,
                              ["Màu đỏ đi trước", "Màu đen đi trước"], 0)

        iy2 = iy + self.ROW1_H + self.ROW_GAP

        # ── Row 2: diff buttons ────────────────────────────────────────────────
        diff_labels = [d[0] for d in DIFF_LEVELS]
        n_diff = len(diff_labels)
        cust_w = 100
        gap    = 6
        avail  = iw - cust_w - gap
        bw     = (avail - gap*(n_diff-1)) // n_diff

        self._diff_rects = []
        for i in range(n_diff):
            bx = ix + i*(bw+gap)
            self._diff_rects.append(pygame.Rect(bx, iy2, bw, self.ROW2_H))
        self._cust_rect = pygame.Rect(ix + avail + gap, iy2, cust_w, self.ROW2_H)

        iy3 = iy2 + self.ROW2_H + self.ROW_GAP

        # ── Row 3: custom box ─────────────────────────────────────────────────
        self._box_rect = pygame.Rect(ix, iy3, iw, self.BOX_H)
        sx = ix + 14
        sw = iw - 28
        self._sl_depth = _Slider("Độ sâu tìm kiếm", 1, 12, 6, step=1)
        self._sl_time  = _Slider("Giới hạn thời gian", 0, 60, 5, step=1, unit="giây")
        # Slider y: label trên (y-20), track ở y+6 → cần đủ chỗ: 20px label + 18px track
        self._sl_depth.x = sx; self._sl_depth.y = iy3 + 32; self._sl_depth.w = sw
        self._sl_time.x  = sx; self._sl_time.y  = iy3 + 76; self._sl_time.w  = sw

        self._iy3 = iy3

        # hover tracking
        self._hov_new  = False
        self._hov_undo = False
        self._hov_diff = [False]*n_diff
        self._hov_cust = False

    # ── height ────────────────────────────────────────────────────────────────
    @property
    def height(self) -> int:
        """Chiều cao panel khớp với BOARD_OFFSET_Y_CLOSED/OPEN trong constants."""
        from core.constants import BOARD_OFFSET_Y_CLOSED, BOARD_OFFSET_Y_OPEN, CTRL_PANEL_Y
        if self._custom_open:
            return BOARD_OFFSET_Y_OPEN  - CTRL_PANEL_Y - 14
        return BOARD_OFFSET_Y_CLOSED - CTRL_PANEL_Y - 14

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw(self, surf, mp, game_manager=None):
        h = self.height

        # Panel background + shadow
        panel_rect = pygame.Rect(self.x, self.y, self.w, h)
        _shadow_rect(surf, panel_rect, r=12, offset=4, alpha=45)
        _rrect(surf, C_BG, panel_rect, r=12,
               border=1, border_color=C_BORDER)

        # ── Row 1 ─────────────────────────────────────────────────────────────
        self._hov_new  = self._btn_new.collidepoint(mp)
        self._hov_undo = self._btn_undo.collidepoint(mp)

        _shadow_rect(surf, self._btn_new,  r=10, offset=3)
        _shadow_rect(surf, self._btn_undo, r=10, offset=3)

        _rrect(surf, C_BTN_NEW_H if self._hov_new else C_BTN_NEW,
               self._btn_new, r=10)
        nl = _f(16, bold=True).render("Trò chơi mới", True, C_TEXT_LIGHT)
        surf.blit(nl, nl.get_rect(center=self._btn_new.center))

        _rrect(surf, C_BTN_UNDO_H if self._hov_undo else C_BTN_UNDO,
               self._btn_undo, r=10, border=1, border_color=C_BORDER)
        ul = _f(15).render("Hoàn tác", True, C_TEXT_DARK)
        surf.blit(ul, ul.get_rect(center=self._btn_undo.center))

        # "Chơi như:" label
        sl = _f(14).render("Chơi như:", True, C_TEXT_DIM)
        surf.blit(sl, sl.get_rect(midleft=(self._lbl_side_x + 163 + 8,
                                            self._btn_new.centery)))
        self._dd.draw(surf, mp)

        # ── Row 2: difficulty ─────────────────────────────────────────────────
        diff_labels = [d[0] for d in DIFF_LEVELS]
        for i, (r, lbl) in enumerate(zip(self._diff_rects, diff_labels)):
            self._hov_diff[i] = r.collidepoint(mp)
            is_act = (i == self._sel_diff and not self._custom_open)
            bg = C_BTN_ACT if is_act else (C_BTN_HOV if self._hov_diff[i] else C_BTN)
            tc = C_TEXT_LIGHT if is_act else C_TEXT_DARK
            _shadow_rect(surf, r, r=8, offset=2, alpha=40)
            _rrect(surf, bg, r, r=8, border=1, border_color=C_BORDER)
            tl = _f(13).render(lbl, True, tc)
            surf.blit(tl, tl.get_rect(center=r.center))

        # Tùy chỉnh button
        self._hov_cust = self._cust_rect.collidepoint(mp)
        is_cust = self._custom_open
        cust_bg = C_BTN_ACT if is_cust else (C_BTN_HOV if self._hov_cust else C_BTN)
        cust_tc = C_TEXT_LIGHT
        _shadow_rect(surf, self._cust_rect, r=8, offset=2, alpha=40)
        _rrect(surf, cust_bg, self._cust_rect, r=8, border=1, border_color=C_BORDER)
        ctl = _f(13, bold=True).render("★ Tùy chỉnh", True, cust_tc)
        surf.blit(ctl, ctl.get_rect(center=self._cust_rect.center))

        # ── Row 3: custom box ─────────────────────────────────────────────────
        if self._custom_open:
            box = self._box_rect
            _shadow_rect(surf, box, r=10, offset=3, alpha=35)
            _rrect(surf, C_CARD, box, r=10, border=1, border_color=C_BORDER)

            self._sl_depth.draw(surf)
            self._sl_time.draw(surf)

            note = _f(11).render(
                "Giá trị thời gian bằng 0 biểu thị không có giới hạn thời gian "
                "(chỉ tìm kiếm theo chiều sâu).",
                True, C_TEXT_DIM)
            surf.blit(note, (box.x + 14, box.bottom - 18))

    # ── events ────────────────────────────────────────────────────────────────
    def handle_event(self, event, mp):
        """
        Trả về dict với action hoặc None.
        Các action: "new_game", "undo", None
        """
        # Dropdown
        if self._dd.handle_event(event):
            return None

        # Sliders
        if self._custom_open:
            if self._sl_depth.handle_event(event): return None
            if self._sl_time.handle_event(event):  return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Trò chơi mới
            if self._btn_new.collidepoint(pos):
                return {"action": "new_game",
                        "depth":  self._get_depth(),
                        "time":   self._get_time(),
                        "human_color": RED if self._dd.selected == 0 else BLACK}

            # Hoàn tác
            if self._btn_undo.collidepoint(pos):
                return {"action": "undo"}

            # Difficulty buttons
            for i, r in enumerate(self._diff_rects):
                if r.collidepoint(pos):
                    self._sel_diff    = i
                    self._custom_open = False
                    return None

            # Tùy chỉnh
            if self._cust_rect.collidepoint(pos):
                self._custom_open = not self._custom_open
                return None

        return None

    # ── helpers ───────────────────────────────────────────────────────────────
    def _get_depth(self) -> int:
        if self._custom_open:
            return self._sl_depth.value
        return DIFF_LEVELS[self._sel_diff][1]

    def _get_time(self) -> float:
        if self._custom_open:
            t = self._sl_time.value
            return float(t) if t > 0 else 9999.0
        return DIFF_LEVELS[self._sel_diff][2]

    def get_diff_name(self) -> str:
        if self._custom_open:
            return "Tùy chỉnh"
        return DIFF_LEVELS[self._sel_diff][0]