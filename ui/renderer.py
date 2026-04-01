
import pygame
from core.constants import (
    BOARD_ROWS, BOARD_COLS,
    BOARD_BG_OUTER, BOARD_BG_INNER, BOARD_LINE, RIVER_COLOR,
    SELECT_COLOR, VALID_MOVE_COLOR, CAPTURE_COLOR,
    TEXT_COLOR, TEXT_DIM, TEXT_RED_SIDE, TEXT_BLK_SIDE,
    WIN_RED_COLOR, WIN_BLK_COLOR, WIN_DRW_COLOR,
    PANEL_BG, PANEL_BORDER,
    RED, BLACK, EMPTY, RED_WIN, BLACK_WIN, DRAW, ONGOING,
    SCREEN_WIDTH, SCREEN_HEIGHT,
)


def _f(size, bold=False):
    return pygame.font.SysFont("segoeui,tahoma,arial", size, bold=bold)


class Renderer:
    def __init__(self, screen: pygame.Surface, layout):
        self.screen = screen
        self.lay    = layout
        self._board_surf: pygame.Surface | None = None
        self._last_cell_size = 0
        self._river_font = _f(18, bold=True)
        self._big_font   = _f(60, bold=True)
        self._small_font = _f(19)
        self._tiny_font  = _f(13)

    def _ensure_board_surf(self):
        cs = self.lay.cell_size
        if cs == self._last_cell_size and self._board_surf is not None:
            return
        self._last_cell_size = cs
        self._board_surf = self._build_board_surf(cs)

    def _build_board_surf(self, cs: int) -> pygame.Surface:
        lay  = self.lay
        pw   = (BOARD_COLS - 1) * cs
        ph   = (BOARD_ROWS - 1) * cs
        pad  = self.lay.BOARD_FRAME
        surf = pygame.Surface((pw + pad*2, ph + pad*2))
        ox = oy = pad

        pygame.draw.rect(surf, BOARD_BG_OUTER,
                         (0, 0, pw+pad*2, ph+pad*2), border_radius=8)
        pygame.draw.rect(surf, BOARD_BG_INNER,
                         (pad-8, pad-8, pw+16, ph+16), border_radius=5)

        pygame.draw.rect(surf, RIVER_COLOR,
                         (ox, oy+4*cs+2, pw, cs-4))
        rf = self._river_font
        for txt, x in [("楚  河", ox+pw//4), ("漢  界", ox+3*pw//4)]:
            lbl = rf.render(txt, True, (48, 88, 132))
            surf.blit(lbl, lbl.get_rect(center=(x, oy+int(4.5*cs))))

        for r in range(BOARD_ROWS):
            y = oy + r*cs
            pygame.draw.line(surf, BOARD_LINE, (ox, y), (ox+pw, y), 1)
        for c in range(BOARD_COLS):
            x = ox + c*cs
            pygame.draw.line(surf, BOARD_LINE, (x, oy),          (x, oy+4*cs), 1)
            pygame.draw.line(surf, BOARD_LINE, (x, oy+5*cs),     (x, oy+9*cs), 1)

        for r0,c0,r1,c1 in [(7,3,9,5),(7,5,9,3),(0,3,2,5),(0,5,2,3)]:
            pygame.draw.line(surf, BOARD_LINE,
                             (ox+c0*cs, oy+r0*cs), (ox+c1*cs, oy+r1*cs), 1)

        L=6; G=3
        marks = [(2,1),(2,7),(7,1),(7,7),
                 (3,0),(3,2),(3,4),(3,6),(3,8),
                 (6,0),(6,2),(6,4),(6,6),(6,8)]
        for r,c in marks:
            cx2,cy2 = ox+c*cs, oy+r*cs
            for dx,dy,hx,hy in [(-1,-1,-1,0),(-1,-1,0,-1),(1,-1,1,0),(1,-1,0,-1),
                                  (-1,1,-1,0),(-1,1,0,1),(1,1,1,0),(1,1,0,1)]:
                pygame.draw.line(surf, BOARD_LINE,
                                 (cx2+dx*G, cy2+dy*G),
                                 (cx2+dx*G+hx*L, cy2+dy*G+hy*L), 1)
        return surf

    # background
    def draw_background(self):
        s = self.screen
        sh = s.get_height()
        sw = s.get_width()
        # Dark gradient for entire window
        for y in range(sh):
            t = y / sh
            r = int(18 + 10*t); g = int(10 + 6*t); b = int(4 + 2*t)
            pygame.draw.line(s, (r,g,b), (0,y), (sw,y))

    # board area
    def draw_board(self):
        self._ensure_board_surf()
        lay = self.lay
        pad = lay.BOARD_FRAME
        self.screen.blit(self._board_surf,
                         (lay.board_ox - pad, lay.board_oy - pad))

    # highlights
    def draw_last_move(self, move_log):
        if not move_log: return
        last = move_log[-1]
        cs   = self.lay.cell_size
        for r,c in [(last.start_row,last.start_col),(last.end_row,last.end_col)]:
            x,y = self.lay.px(r,c)
            hl  = pygame.Surface((cs,cs), pygame.SRCALPHA)
            hl.fill((255,175,0,42))
            self.screen.blit(hl, (x-cs//2, y-cs//2))

    def draw_selected_piece(self, sel):
        if sel is None: return
        x,y = self.lay.px(*sel)
        cs  = self.lay.cell_size
        for i in range(3,0,-1):
            g = pygame.Surface((cs+i*4,cs+i*4), pygame.SRCALPHA)
            pygame.draw.circle(g, (*SELECT_COLOR,38+i*22),
                                ((cs+i*4)//2,(cs+i*4)//2), cs//2+i)
            self.screen.blit(g, (x-cs//2-i*2, y-cs//2-i*2))
        pygame.draw.circle(self.screen, SELECT_COLOR, (x,y), cs//2-1, 3)

    def draw_valid_moves(self, moves):
        cs = self.lay.cell_size
        for mv in moves:
            x,y = self.lay.px(mv.end_row, mv.end_col)
            if mv.is_capture():
                pygame.draw.circle(self.screen, CAPTURE_COLOR, (x,y), cs//2-2, 3)
            else:
                r = max(6, cs//10)
                dot = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
                pygame.draw.circle(dot, (*VALID_MOVE_COLOR,195), (r,r), r)
                self.screen.blit(dot, (x-r, y-r))

    # pieces
    def _draw_piece(self, piece, px, py):
        cs = self.lay.cell_size
        r  = cs//2 - 3
        # Shadow
        sh = pygame.Surface((cs,cs), pygame.SRCALPHA)
        pygame.draw.circle(sh,(0,0,0,58),(cs//2+2,cs//2+3),r)
        self.screen.blit(sh,(px-cs//2, py-cs//2))
        # Image
        try:
            img = piece.image
            if img:
                img_s = pygame.transform.smoothscale(img,(cs-4,cs-4))
                self.screen.blit(img_s, img_s.get_rect(center=(px,py)))
                return
        except Exception:
            pass
        # Fallback
        bg = (185,35,35) if piece.color==RED else (25,25,25)
        pygame.draw.circle(self.screen,(200,170,105),(px,py),r)
        pygame.draw.circle(self.screen,bg,(px,py),r,4)
        pygame.draw.circle(self.screen,bg,(px,py),r-5,1)
        lbl = pygame.font.SysFont("Arial",max(12,cs//4),bold=True).render(
            piece.piece_type,True,bg)
        self.screen.blit(lbl,lbl.get_rect(center=(px,py)))

    def draw_pieces(self, pieces, hidden=None):
        for p in pieces:
            if p is not hidden:
                x,y = self.lay.px(p.row, p.col)
                self._draw_piece(p,x,y)

    def draw_anim_piece(self, anim_data):
        if anim_data is None: return
        x = self.lay.board_ox + anim_data["col"] * self.lay.cell_size
        y = self.lay.board_oy + anim_data["row"] * self.lay.cell_size
        self._draw_piece(anim_data["piece"], int(x), int(y))

    #panel separators
    def draw_panel_borders(self):
        s   = self.screen
        sh  = s.get_height()
        lay = self.lay
        # Left border
        pygame.draw.line(s, PANEL_BORDER,
                         (lay.left_rect.right, 0),
                         (lay.left_rect.right, sh), 1)
        # Right border
        pygame.draw.line(s, PANEL_BORDER,
                         (lay.right_rect.left, 0),
                         (lay.right_rect.left, sh), 1)

    # footer
    def draw_footer(self):
        sh = self.screen.get_height()
        lx = self.lay.left_rect.right
        rx = self.lay.right_rect.left
        cx = (lx + rx) // 2
        t  = self._tiny_font.render(
            "Made by Vu Nam Sang & Thai Doan Thinh", True, (80,62,35))
        self.screen.blit(t, t.get_rect(center=(cx, sh-14)))

    # game over overlay
    def draw_game_over_overlay(self, game_state):
        if game_state == ONGOING: return
        s   = self.screen
        sw, sh = s.get_size()
        ov  = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0,0,0,145)); s.blit(ov,(0,0))

        msgs = {RED_WIN:("RED WINS! 🏆",WIN_RED_COLOR),
                BLACK_WIN:("BLACK WINS! 🏆",WIN_BLK_COLOR),
                DRAW:("DRAW!",(205,180,70))}
        msg, color = msgs.get(game_state,("GAME OVER",(200,200,200)))
        cx,cy = sw//2, sh//2
        for off in range(4,0,-1):
            g = self._big_font.render(msg,True,(*color,35))
            s.blit(g, g.get_rect(center=(cx+off,cy)))
        t = self._big_font.render(msg,True,color)
        s.blit(t, t.get_rect(center=(cx,cy)))
        sub = self._small_font.render("Nhấn 'Trò chơi mới' để chơi lại",
                                       True,(200,185,158))
        s.blit(sub, sub.get_rect(center=(cx,cy+72)))

    def render(self, board, gm, left_panel, right_panel):
        self.draw_background()
        self.draw_board()
        self.draw_last_move(board.move_log)
        self.draw_selected_piece(gm.get_selected_piece())
        self.draw_valid_moves(gm.get_valid_moves())

        hidden = gm.animation_hide_piece if gm.animating else None
        self.draw_pieces(board.get_all_pieces(), hidden=hidden)
        self.draw_anim_piece(gm.get_animation_draw_data())

        self.draw_panel_borders()
        left_panel.draw(self.screen, self.lay, gm)
        right_panel.draw(self.screen, self.lay, gm)
        self.draw_footer()
        self.draw_game_over_overlay(gm.game_state)
        pygame.display.flip()