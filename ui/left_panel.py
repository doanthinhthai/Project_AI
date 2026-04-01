
import pygame
from core.constants import (
    PANEL_BG, PANEL_BORDER, TEXT_COLOR, TEXT_DIM,
    TEXT_RED_SIDE, TEXT_BLK_SIDE,
    RED, BLACK, EMPTY,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN,
    PVP_MODE, PVAI_MODE, AIVAI_MODE,
)

_PIECE_NAME = {
    KING: "Tướng", ADVISOR: "Sĩ", ELEPHANT: "Tượng",
    ROOK: "Xe",    KNIGHT:  "Mã", CANNON:   "Pháo", PAWN: "Tốt",
}

def _f(size, bold=False):
    return pygame.font.SysFont("segoeui,tahoma,arial", size, bold=bold)


def _fmt_score(score: int) -> str:
    if score >= 9_000_000:   return "CHECKMATE +"
    if score <= -9_000_000:  return "CHECKMATE -"
    if score > 0:            return f"+{score}"
    return str(score)


def _fmt_move(move) -> str:
    if move is None:
        return "—"
    pname = _PIECE_NAME.get(move.piece_moved.piece_type, move.piece_moved.piece_type)
    return f"{pname} ({move.start_row},{move.start_col})→({move.end_row},{move.end_col})"


def _fmt_nodes(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)


class LeftPanel:
    PAD   = 12
    ROW_H = 19

    C_HDR_MAIN = (195, 148, 42)
    C_HDR_SUB  = (155, 118, 62)
    C_GOOD     = ( 80, 200,  80)
    C_BAD      = (220,  70,  70)
    C_NEUTRAL  = (180, 165, 120)

    def __init__(self):
        self._head_f  = _f(15, bold=True)
        self._sec_f   = _f(13, bold=True)
        self._lbl_f   = _f(13)
        self._val_f   = _f(13, bold=True)
        self._log_f   = _f(12)
        self._tiny_f  = _f(11)

        self._bg_surf  = None
        self._bg_size  = (0, 0)

    def _get_bg(self, w, h):
        if self._bg_surf is None or self._bg_size != (w, h):
            s = pygame.Surface((w, h))
            for yi in range(h):
                t = yi / h
                r=int(20+8*t); g=int(12+4*t); b=int(5+2*t)
                pygame.draw.line(s,(r,g,b),(0,yi),(w,yi))
            self._bg_surf = s
            self._bg_size = (w, h)
        return self._bg_surf

    def _section_title(self, surf, x, y, w, title, color=None):
        c = color or self.C_HDR_SUB
        lbl = self._sec_f.render(title, True, c)
        surf.blit(lbl, (x, y))
        y += 17
        pygame.draw.line(surf, (75, 52, 18), (x, y), (x + w, y), 1)
        return y + 5

    def _row(self, surf, x, y, label, value, vc=None):
        ll = self._lbl_f.render(label, True, TEXT_DIM)
        vl = self._val_f.render(str(value), True, vc or self.C_NEUTRAL)
        surf.blit(ll, (x, y))
        surf.blit(vl, (x + 95, y))
        return y + self.ROW_H

    def _divider(self, surf, x, y, w):
        pygame.draw.line(surf, (55, 38, 14), (x, y), (x + w, y), 1)
        return y + 7


    def draw(self, screen: pygame.Surface, layout, game_manager):
        rect = layout.left_rect
        P    = self.PAD
        x    = rect.x + P
        w    = rect.width - P * 2
        gm   = game_manager

        bg = self._get_bg(rect.width, rect.height)
        screen.blit(bg, (rect.x, rect.y))

        for xi in range(3):
            s2 = pygame.Surface((1, rect.height), pygame.SRCALPHA)
            s2.fill((185, 138, 38, 65 - xi * 20))
            screen.blit(s2, (rect.right - 1 - xi, rect.y))

        y = rect.y + P

        hdr = self._head_f.render("AI  ANALYSIS", True, self.C_HDR_MAIN)
        screen.blit(hdr, hdr.get_rect(centerx=rect.centerx, y=y))
        y += 22
        pygame.draw.line(screen, (140, 100, 30),
                         (rect.x + P, y), (rect.right - P, y), 1)
        y += 8

        red_ai = gm.red_ai
        blk_ai = gm.black_ai
        has_ai = red_ai or blk_ai

        if not has_ai:
            no_ai = self._lbl_f.render("No AI active (PvP mode)", True, TEXT_DIM)
            screen.blit(no_ai, (x, y)); y += 22
        else:
            for ai_obj, side_label, side_color in [
                (red_ai,  "RED  AI",   TEXT_RED_SIDE),
                (blk_ai,  "BLACK AI",  TEXT_BLK_SIDE),
            ]:
                if ai_obj is None:
                    continue

                engine = getattr(ai_obj, "engine", None)

                y = self._section_title(screen, x, y, w, side_label, side_color)

                algo = ai_obj.algorithm
                max_d = ai_obj.max_depth
                done_d = getattr(engine, "search_depth", 0) if engine else 0
                y = self._row(screen, x, y, "Algorithm:", algo.replace("_"," ").title())
                y = self._row(screen, x, y, "Max depth:", f"{max_d}")
                y = self._row(screen, x, y, "Done depth:", f"{done_d}",
                              self.C_GOOD if done_d >= max_d else self.C_NEUTRAL)

                if engine:
                    raw_score = getattr(engine, "best_score", 0)
                    display_score = raw_score if ai_obj is red_ai else -raw_score
                    score_str = _fmt_score(display_score)
                    sc_color = (self.C_GOOD if display_score > 50
                                else self.C_BAD if display_score < -50
                                else self.C_NEUTRAL)
                    y = self._row(screen, x, y, "Evaluation:", score_str, sc_color)

                # Best Move
                if engine:
                    bm = getattr(engine, "best_move_found", None)
                    bm_str = _fmt_move(bm)
                    bm_surf = self._val_f.render(bm_str, True, self.C_NEUTRAL)
                    lbl_surf = self._lbl_f.render("Best move:", True, TEXT_DIM)
                    screen.blit(lbl_surf, (x, y))
                    y += self.ROW_H
                    screen.blit(bm_surf, (x + 8, y))
                    y += self.ROW_H

                # Nodes & Pruning
                if engine:
                    nodes   = getattr(engine, "node_count",   0)
                    pruned  = getattr(engine, "pruned_count", 0)
                    tt_hits = getattr(engine, "tt_hits",      0)
                    tt_size = len(getattr(engine, "tt",       {}))

                    y = self._row(screen, x, y, "Nodes:",
                                  _fmt_nodes(nodes), self.C_NEUTRAL)
                    y = self._row(screen, x, y, "Pruned:",
                                  _fmt_nodes(pruned),
                                  self.C_GOOD if pruned > nodes * 0.3 else self.C_NEUTRAL)
                    y = self._row(screen, x, y, "TT hits:",
                                  _fmt_nodes(tt_hits), self.C_NEUTRAL)
                    y = self._row(screen, x, y, "TT size:",
                                  _fmt_nodes(tt_size), TEXT_DIM)

                    # Pruning ratio bar
                    if nodes > 0:
                        ratio = min(1.0, pruned / nodes)
                        bar_w = w - 8
                        bar_rect = pygame.Rect(x, y, bar_w, 7)
                        pygame.draw.rect(screen, (45, 32, 12), bar_rect, border_radius=3)
                        fill_w = int(bar_w * ratio)
                        if fill_w > 0:
                            pygame.draw.rect(screen, (68, 168, 68),
                                             pygame.Rect(x, y, fill_w, 7), border_radius=3)
                        pct_lbl = self._tiny_f.render(
                            f"Pruning ratio: {ratio*100:.0f}%", True, TEXT_DIM)
                        screen.blit(pct_lbl, (x, y + 9))
                        y += 22

                # Think time
                think = getattr(ai_obj, "last_think_time", 0.0)
                tc = (self.C_GOOD if think < 1.0
                      else self.C_NEUTRAL if think < 5.0
                      else self.C_BAD)
                y = self._row(screen, x, y, "Think time:", f"{think:.3f}s", tc)

                y = self._divider(screen, x, y, w)

        y = self._section_title(screen, x, y, w, "MOVE  LOG")

        log    = gm.board.move_log
        total  = len(log)
        bottom = rect.bottom - P - 16   # dừng trước footer
        avail  = bottom - y
        n_show = min(total, avail // 17)
        recent = log[-n_show:] if n_show > 0 else []

        for i, mv in enumerate(recent):
            n   = total - len(recent) + i + 1
            col = TEXT_RED_SIDE if n % 2 == 1 else TEXT_BLK_SIDE
            side = "R" if n % 2 == 1 else "B"
            pname = _PIECE_NAME.get(mv.piece_moved.piece_type,
                                     mv.piece_moved.piece_type)
            capture = f" x{_PIECE_NAME.get(mv.piece_captured.piece_type,'?')}" \
                      if mv.is_capture() else ""
            txt = f"{n:2}. [{side}] {pname}{capture}"
            lbl = self._log_f.render(txt, True, col)
            screen.blit(lbl, (x, y))
            y += 17
            if y + 17 > bottom:
                break