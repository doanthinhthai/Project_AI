"""
history_panel.py — Scrollable panel hiển thị lịch sử ván đấu.

Hiện ra sau khi ván kết thúc (overlay toàn màn hình).
Click vào một nước đi → hiển thị phân tích AI bên phải.
"""
import pygame
from core.constants import (
    RED, BLACK,
    TEXT_COLOR, TEXT_DIM, TEXT_RED_SIDE, TEXT_BLK_SIDE,
    BUTTON_BG, BUTTON_BG_HOVER, BUTTON_BG_2, BUTTON_BG_2_HOV,
    BUTTON_BG_4, BUTTON_BG_4_HOV, BUTTON_TEXT_COLOR,
)


def _f(size, bold=False):
    return pygame.font.SysFont("segoeui,tahoma,arial", size, bold=bold)


# ── Colours ───────────────────────────────────────────────────────────────────
C_BG         = (14,  8,  3, 215)   # overlay SRCALPHA
C_PANEL      = (22, 14,  5)
C_PANEL2     = (28, 18,  8)
C_BORDER     = (130, 88, 25)
C_ROW_EVEN   = (30, 20,  8)
C_ROW_ODD    = (38, 26, 10)
C_ROW_SEL    = (72, 50, 18)
C_ROW_HOV    = (50, 34, 12)
C_GOLD       = (210, 165, 45)
C_LIGHT      = (230, 210, 165)
C_DIM        = (140, 115, 72)


class HistoryPanel:
    """
    Overlay toàn màn hình hiện sau khi ván kết thúc.
    Gọi show(match_record) để mở, ẩn khi nhấn "Đóng".
    """
    ROW_H    = 26
    LIST_PAD = 10

    def __init__(self):
        self._visible        = False
        self._record         = None
        self._selected_idx   = None   # index entry đang xem
        self._scroll_offset  = 0      # pixel offset scroll
        self._drag_scroll    = False
        self._drag_y         = 0

        # Fonts
        self._title_f  = _f(22, bold=True)
        self._head_f   = _f(14, bold=True)
        self._row_f    = _f(13)
        self._ana_f    = _f(13)
        self._small_f  = _f(12)
        self._btn_f    = _f(15, bold=True)

        # Rects — tính lại trong draw() theo screen size
        self._panel_rect   = pygame.Rect(0, 0, 0, 0)
        self._list_rect    = pygame.Rect(0, 0, 0, 0)
        self._ana_rect     = pygame.Rect(0, 0, 0, 0)
        self._close_rect   = pygame.Rect(0, 0, 0, 0)
        self._scroll_rect  = pygame.Rect(0, 0, 0, 0)
        self._row_rects    = []

        # Cache bg
        self._bg_surf  = None
        self._bg_size  = (0, 0)

    # ── Public API ────────────────────────────────────────────────────────────

    def show(self, match_record):
        self._record       = match_record
        self._visible      = True
        self._selected_idx = None
        self._scroll_offset = 0

    def hide(self):
        self._visible = False

    @property
    def visible(self) -> bool:
        return self._visible

    # ── Layout ────────────────────────────────────────────────────────────────

    def _layout(self, sw, sh):
        pw = min(1100, int(sw * 0.90))
        ph = min(720,  int(sh * 0.90))
        px = (sw - pw) // 2
        py = (sh - ph) // 2
        self._panel_rect = pygame.Rect(px, py, pw, ph)

        # Close button
        self._close_rect = pygame.Rect(px + pw - 110, py + ph - 54, 100, 40)

        # Left: move list  |  Right: analysis
        split     = int(pw * 0.42)
        lp        = self.LIST_PAD
        hdr_h     = 52
        footer_h  = 58

        self._list_rect = pygame.Rect(
            px + lp,
            py + hdr_h,
            split - lp * 2,
            ph - hdr_h - footer_h,
        )
        self._ana_rect = pygame.Rect(
            px + split + lp,
            py + hdr_h,
            pw - split - lp * 2,
            ph - hdr_h - footer_h,
        )

        # Scrollbar
        self._scroll_rect = pygame.Rect(
            self._list_rect.right + 2,
            self._list_rect.y,
            8,
            self._list_rect.height,
        )

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        if not self._visible or self._record is None:
            return

        sw, sh = screen.get_size()
        self._layout(sw, sh)

        # Dimmed full-screen overlay
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 188))
        screen.blit(ov, (0, 0))

        # Main panel background
        pr = self._panel_rect
        _draw_panel(screen, pr, C_PANEL, C_BORDER, radius=12)

        # ── Title + summary ───────────────────────────────────────────────────
        rec = self._record
        title = self._title_f.render("Lịch Sử Ván Đấu", True, C_GOLD)
        screen.blit(title, title.get_rect(
            centerx=pr.centerx, y=pr.y + 10))

        summ = self._small_f.render(rec.summary(), True, C_DIM)
        screen.blit(summ, summ.get_rect(
            centerx=pr.centerx, y=pr.y + 35))

        pygame.draw.line(screen, C_BORDER,
                         (pr.x + 10, pr.y + 52),
                         (pr.right - 10, pr.y + 52), 1)

        # ── Left: move list ───────────────────────────────────────────────────
        self._draw_move_list(screen)

        # ── Divider ───────────────────────────────────────────────────────────
        pygame.draw.line(screen, C_BORDER,
                         (self._list_rect.right + 10, self._ana_rect.y),
                         (self._list_rect.right + 10, self._ana_rect.bottom), 1)

        # ── Right: analysis ───────────────────────────────────────────────────
        self._draw_analysis(screen)

        # ── Close button ──────────────────────────────────────────────────────
        mp = pygame.mouse.get_pos()
        hov = self._close_rect.collidepoint(mp)
        _draw_btn(screen, self._close_rect, "Đóng  ✕",
                  BUTTON_BG_4, BUTTON_BG_4_HOV, hov, self._btn_f)

    def _draw_move_list(self, screen):
        lr      = self._list_rect
        entries = self._record.entries if self._record else []
        n       = len(entries)
        mp      = pygame.mouse.get_pos()

        # Clipping surface
        clip_surf = pygame.Surface((lr.width, lr.height), pygame.SRCALPHA)

        total_h = n * self.ROW_H
        max_scroll = max(0, total_h - lr.height)
        self._scroll_offset = max(0, min(self._scroll_offset, max_scroll))

        self._row_rects = []
        for i, entry in enumerate(entries):
            ry = i * self.ROW_H - self._scroll_offset
            if ry + self.ROW_H < 0 or ry > lr.height:
                self._row_rects.append(None)
                continue

            row_rect_clip = pygame.Rect(0, ry, lr.width, self.ROW_H)
            is_sel   = (i == self._selected_idx)
            is_hov   = pygame.Rect(lr.x, lr.y + ry, lr.width, self.ROW_H).collidepoint(mp)
            bg       = C_ROW_SEL if is_sel else (C_ROW_HOV if is_hov else
                       C_ROW_EVEN if i % 2 == 0 else C_ROW_ODD)

            pygame.draw.rect(clip_surf, bg, row_rect_clip)

            # Number
            num_c = C_DIM
            n_lbl = self._small_f.render(f"{entry.move_number:2}.", True, num_c)
            clip_surf.blit(n_lbl, (4, ry + 5))

            # Side dot
            dot_c = (200, 55, 55) if entry.color == RED else (85, 140, 215)
            pygame.draw.circle(clip_surf, dot_c, (32, ry + 13), 4)

            # Notation
            txt_c = TEXT_RED_SIDE if entry.color == RED else TEXT_BLK_SIDE
            notation_lbl = self._row_f.render(entry.notation, True, txt_c)
            clip_surf.blit(notation_lbl, (42, ry + 5))

            # AI badge + think time
            if entry.is_ai:
                ai_lbl = self._small_f.render(
                    f"AI  {entry.think_time_str}", True, (140, 185, 100))
                clip_surf.blit(ai_lbl, (lr.width - 80, ry + 5))

            # Eval score
            if entry.eval_score is not None:
                ec = (80, 190, 80) if entry.eval_score > 50 else \
                     (200, 70, 70) if entry.eval_score < -50 else C_DIM
                el = self._small_f.render(entry.eval_str, True, ec)
                clip_surf.blit(el, (lr.width - 80, ry + 14))

            # Row separator
            pygame.draw.line(clip_surf, (50, 35, 12),
                             (0, ry + self.ROW_H - 1),
                             (lr.width, ry + self.ROW_H - 1), 1)

            # Store screen-space rect for click detection
            self._row_rects.append(
                pygame.Rect(lr.x, lr.y + ry, lr.width, self.ROW_H))

        screen.blit(clip_surf, (lr.x, lr.y))

        # ── Column headers ────────────────────────────────────────────────────
        hdr_y = lr.y - 18
        for txt, x in [("#", lr.x + 4), ("Nước đi", lr.x + 42),
                        ("AI / thời gian", lr.right - 80)]:
            h = self._small_f.render(txt, True, C_DIM)
            screen.blit(h, (x, hdr_y))

        # ── Scrollbar ─────────────────────────────────────────────────────────
        total_h = n * self.ROW_H
        if total_h > lr.height:
            sr = self._scroll_rect
            pygame.draw.rect(screen, (40, 28, 10), sr, border_radius=4)
            ratio  = lr.height / total_h
            knob_h = max(20, int(sr.height * ratio))
            knob_y = sr.y + int((self._scroll_offset / total_h) * sr.height)
            pygame.draw.rect(screen, C_BORDER,
                             pygame.Rect(sr.x, knob_y, sr.width, knob_h),
                             border_radius=4)

    def _draw_analysis(self, screen):
        ar = self._ana_rect

        if self._selected_idx is None or self._record is None:
            hint = self._ana_f.render(
                "← Nhấn vào một nước đi để xem phân tích", True, C_DIM)
            screen.blit(hint, hint.get_rect(
                center=(ar.centerx, ar.y + 40)))
            return

        entry = self._record.entries[self._selected_idx]

        y = ar.y + 8
        x = ar.x + 8
        w = ar.width - 16

        # Header
        hdr = self._head_f.render(
            f"Nước #{entry.move_number}  —  {entry.side}", True, C_GOLD)
        screen.blit(hdr, (x, y)); y += 22

        not_lbl = self._ana_f.render(entry.notation, True,
                                      TEXT_RED_SIDE if entry.color == RED else TEXT_BLK_SIDE)
        screen.blit(not_lbl, (x, y)); y += 20

        pygame.draw.line(screen, C_BORDER, (x, y), (x + w, y), 1); y += 8

        # Stats
        stats = [
            ("Loại:", "AI" if entry.is_ai else "Người"),
            ("Đánh giá:", entry.eval_str),
            ("Độ sâu:", str(entry.depth_searched) if entry.depth_searched else "—"),
            ("Thời gian:", entry.think_time_str),
        ]
        for lbl, val in stats:
            ll = self._small_f.render(lbl, True, C_DIM)
            vl = self._small_f.render(val, True, C_LIGHT)
            screen.blit(ll, (x, y))
            screen.blit(vl, (x + 85, y)); y += 18

        y += 6
        pygame.draw.line(screen, C_BORDER, (x, y), (x + w, y), 1); y += 8

        # Explanation
        explain_title = self._head_f.render("Phân tích:", True, C_GOLD)
        screen.blit(explain_title, (x, y)); y += 20

        for line in entry.why_chosen().split("\n"):
            surf = self._small_f.render(line, True, C_LIGHT)
            # Word wrap đơn giản nếu dài
            if surf.get_width() > w:
                words   = line.split()
                cur_line = ""
                for word in words:
                    test = cur_line + (" " if cur_line else "") + word
                    if self._small_f.size(test)[0] <= w:
                        cur_line = test
                    else:
                        if cur_line:
                            s = self._small_f.render(cur_line, True, C_LIGHT)
                            screen.blit(s, (x + 4, y)); y += 16
                        cur_line = word
                if cur_line:
                    s = self._small_f.render(cur_line, True, C_LIGHT)
                    screen.blit(s, (x + 4, y)); y += 16
            else:
                screen.blit(surf, (x + 4, y)); y += 16
            if y > ar.bottom - 10:
                break

        # Candidate moves
        if entry.candidates:
            y += 4
            pygame.draw.line(screen, C_BORDER, (x, y), (x + w, y), 1); y += 8
            ct = self._head_f.render("Nước đã cân nhắc:", True, C_GOLD)
            screen.blit(ct, (x, y)); y += 20

            best_s = entry.eval_score or 0
            for i, cand in enumerate(entry.candidates[:5]):
                if y > ar.bottom - 18: break
                diff    = cand.score - best_s
                diff_s  = f"{'+' if diff >= 0 else ''}{diff}"
                color_c = (80, 190, 80) if diff >= 0 else (200, 80, 80)
                row_txt = f"{i+1}. {cand.notation}"
                sc_txt  = f"{cand.score}  (Δ{diff_s})"
                rl = self._small_f.render(row_txt, True, C_LIGHT)
                sl = self._small_f.render(sc_txt,  True, color_c)
                screen.blit(rl, (x + 4, y))
                screen.blit(sl, (ar.right - sl.get_width() - 4, y))
                y += 17

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event) -> bool:
        """Trả về True nếu event đã được dùng."""
        if not self._visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Close
            if self._close_rect.collidepoint(pos):
                self.hide(); return True

            # Row click
            for i, r in enumerate(self._row_rects):
                if r and r.collidepoint(pos):
                    self._selected_idx = i
                    return True

            # Scrollbar drag start
            if self._scroll_rect.collidepoint(pos):
                self._drag_scroll = True
                self._drag_y      = pos[1]
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            self._drag_scroll = False

        elif event.type == pygame.MOUSEMOTION and self._drag_scroll:
            dy = event.pos[1] - self._drag_y
            self._drag_y = event.pos[1]
            if self._record:
                total_h = len(self._record.entries) * self.ROW_H
                ratio   = total_h / max(1, self._list_rect.height)
                self._scroll_offset += int(dy * ratio)
            return True

        elif event.type == pygame.MOUSEWHEEL:
            if self._list_rect.collidepoint(pygame.mouse.get_pos()):
                self._scroll_offset -= event.y * self.ROW_H * 3
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide(); return True
            if event.key == pygame.K_UP and self._selected_idx is not None:
                self._selected_idx = max(0, self._selected_idx - 1)
                self._ensure_visible(self._selected_idx); return True
            if event.key == pygame.K_DOWN and self._selected_idx is not None:
                if self._record:
                    self._selected_idx = min(len(self._record.entries)-1,
                                             self._selected_idx + 1)
                    self._ensure_visible(self._selected_idx); return True

        return False

    def _ensure_visible(self, idx):
        row_y  = idx * self.ROW_H
        lr_h   = self._list_rect.height
        if row_y < self._scroll_offset:
            self._scroll_offset = row_y
        elif row_y + self.ROW_H > self._scroll_offset + lr_h:
            self._scroll_offset = row_y + self.ROW_H - lr_h


# ── Helpers ───────────────────────────────────────────────────────────────────

def _draw_panel(surf, rect, bg, border, radius=10):
    pygame.draw.rect(surf, bg,     rect, border_radius=radius)
    pygame.draw.rect(surf, border, rect, 2, border_radius=radius)


def _draw_btn(surf, rect, text, bg, bg_h, hovered, font):
    pygame.draw.rect(surf, bg_h if hovered else bg, rect, border_radius=8)
    pygame.draw.rect(surf, (0, 0, 0, 80), rect, 1, border_radius=8)
    lbl = font.render(text, True, BUTTON_TEXT_COLOR)
    surf.blit(lbl, lbl.get_rect(center=rect.center))