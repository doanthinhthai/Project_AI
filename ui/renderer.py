"""
renderer.py — Board renderer với hiệu ứng lacquer đỏ-vàng.
board_offset_y được truyền động từ main để thích nghi với control panel.
"""
import pygame
from core.constants import (
    BOARD_ROWS, BOARD_COLS,
    CELL_SIZE, BOARD_OFFSET_X,
    SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_AREA_WIDTH,
    BOARD_BG_OUTER, BOARD_BG_INNER, BOARD_LINE,
    RIVER_COLOR, SELECT_COLOR, VALID_MOVE_COLOR, CAPTURE_COLOR, LAST_MOVE_COLOR,
    TEXT_COLOR, TEXT_DIM,
    WIN_RED_COLOR, WIN_BLK_COLOR, WIN_DRW_COLOR,
    RED, BLACK, EMPTY,
    RED_WIN, BLACK_WIN, DRAW, ONGOING,
)


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen     = screen
        self.font       = pygame.font.SysFont("arial", 26, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.big_font   = pygame.font.SysFont("arial", 62, bold=True)
        self.tiny_font  = pygame.font.SysFont("arial", 15, italic=True)
        self.river_font = pygame.font.SysFont("Arial", 19, bold=True)

        self._board_surf     = None
        self._board_surf_pad = 18
        self._build_board_surface()

    # =========================================================================
    # PRE-BAKE STATIC BOARD
    # =========================================================================

    def _build_board_surface(self):
        bw  = (BOARD_COLS - 1) * CELL_SIZE
        bh  = (BOARD_ROWS - 1) * CELL_SIZE
        pad = self._board_surf_pad
        s   = pygame.Surface((bw + pad*2, bh + pad*2))
        ox, oy = pad, pad

        pygame.draw.rect(s, BOARD_BG_OUTER, (0, 0, bw+pad*2, bh+pad*2), border_radius=8)
        pygame.draw.rect(s, BOARD_BG_INNER, (pad-8, pad-8, bw+16, bh+16), border_radius=5)

        # River
        pygame.draw.rect(s, RIVER_COLOR,
                         (ox, oy+4*CELL_SIZE+2, bw, CELL_SIZE-4))
        for txt, x in [("楚  河", ox+bw//4), ("漢  界", ox+3*bw//4)]:
            lbl = self.river_font.render(txt, True, (52, 92, 138))
            s.blit(lbl, lbl.get_rect(center=(x, oy+int(4.5*CELL_SIZE))))

        # Grid
        for row in range(BOARD_ROWS):
            y = oy + row*CELL_SIZE
            pygame.draw.line(s, BOARD_LINE, (ox, y), (ox+bw, y), 1)
        for col in range(BOARD_COLS):
            x = ox + col*CELL_SIZE
            pygame.draw.line(s, BOARD_LINE, (x, oy),               (x, oy+4*CELL_SIZE), 1)
            pygame.draw.line(s, BOARD_LINE, (x, oy+5*CELL_SIZE),   (x, oy+9*CELL_SIZE), 1)

        # Palace diagonals
        for r0,c0,r1,c1 in [(7,3,9,5),(7,5,9,3),(0,3,2,5),(0,5,2,3)]:
            pygame.draw.line(s, BOARD_LINE,
                             (ox+c0*CELL_SIZE, oy+r0*CELL_SIZE),
                             (ox+c1*CELL_SIZE, oy+r1*CELL_SIZE), 1)

        self._draw_ticks(s, ox, oy)
        self._board_surf = s

    def _draw_ticks(self, s, ox, oy):
        L=7; G=3
        marks = [(2,1),(2,7),(7,1),(7,7),
                 (3,0),(3,2),(3,4),(3,6),(3,8),
                 (6,0),(6,2),(6,4),(6,6),(6,8)]
        for r,c in marks:
            cx2 = ox+c*CELL_SIZE; cy2 = oy+r*CELL_SIZE
            for dx,dy,hx,hy in [(-1,-1,-1,0),(-1,-1,0,-1),(1,-1,1,0),(1,-1,0,-1),
                                  (-1,1,-1,0),(-1,1,0,1),(1,1,1,0),(1,1,0,1)]:
                pygame.draw.line(s, BOARD_LINE,
                                 (cx2+dx*G, cy2+dy*G),
                                 (cx2+dx*G+hx*L, cy2+dy*G+hy*L), 1)

    # =========================================================================
    # COORDINATE HELPER (nhận board_offset_y động)
    # =========================================================================

    def _px(self, row, col, oy):
        return BOARD_OFFSET_X + col*CELL_SIZE, oy + row*CELL_SIZE

    # =========================================================================
    # DRAW BACKGROUND
    # =========================================================================

    def draw_background(self, board_offset_y: int):
        s = self.screen
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(22+10*ratio); g = int(14+5*ratio); b = int(5+2*ratio)
            pygame.draw.line(s, (r,g,b), (0,y), (BOARD_AREA_WIDTH,y))

    # =========================================================================
    # DRAW BOARD
    # =========================================================================

    def draw_board(self, board_offset_y: int):
        pad = self._board_surf_pad
        self.screen.blit(self._board_surf,
                         (BOARD_OFFSET_X - pad, board_offset_y - pad))

    # =========================================================================
    # HIGHLIGHTS
    # =========================================================================

    def draw_last_move(self, move_log, oy):
        if not move_log: return
        last = move_log[-1]
        for r, c in [(last.start_row, last.start_col), (last.end_row, last.end_col)]:
            x, y = self._px(r, c, oy)
            hl = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            hl.fill((255, 175, 0, 45))
            self.screen.blit(hl, (x-CELL_SIZE//2, y-CELL_SIZE//2))

    def draw_selected_piece(self, sel, oy):
        if sel is None: return
        r, c = sel
        x, y = self._px(r, c, oy)
        for i in range(3, 0, -1):
            gs = pygame.Surface((CELL_SIZE+i*4, CELL_SIZE+i*4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*SELECT_COLOR, 40+i*25),
                               ((CELL_SIZE+i*4)//2, (CELL_SIZE+i*4)//2),
                               CELL_SIZE//2+i)
            self.screen.blit(gs, (x-CELL_SIZE//2-i*2, y-CELL_SIZE//2-i*2))
        pygame.draw.circle(self.screen, SELECT_COLOR, (x,y), CELL_SIZE//2-1, 3)

    def draw_valid_moves(self, moves, oy):
        for move in moves:
            x, y = self._px(move.end_row, move.end_col, oy)
            if move.is_capture():
                pygame.draw.circle(self.screen, CAPTURE_COLOR, (x,y), CELL_SIZE//2-2, 3)
            else:
                dot = pygame.Surface((18,18), pygame.SRCALPHA)
                pygame.draw.circle(dot, (*VALID_MOVE_COLOR, 200), (9,9), 9)
                self.screen.blit(dot, (x-9, y-9))

    # =========================================================================
    # PIECES
    # =========================================================================

    def _draw_single_piece(self, piece, px, py):
        r = CELL_SIZE//2-3
        sh = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(sh, (0,0,0,65), (CELL_SIZE//2+3, CELL_SIZE//2+3), r)
        self.screen.blit(sh, (px-CELL_SIZE//2, py-CELL_SIZE//2))
        try:
            img = piece.image
            if img:
                self.screen.blit(img, img.get_rect(center=(px,py)))
                return
        except Exception:
            pass
        bg = (192,36,36) if piece.color==RED else (28,28,28)
        fg = (255,225,170) if piece.color==RED else (210,210,210)
        pygame.draw.circle(self.screen, (205,175,112), (px,py), r)
        pygame.draw.circle(self.screen, bg, (px,py), r, 4)
        pygame.draw.circle(self.screen, bg, (px,py), r-5, 1)
        lbl = pygame.font.SysFont("Arial",18,bold=True).render(piece.piece_type,True,bg)
        self.screen.blit(lbl, lbl.get_rect(center=(px,py)))

    def draw_piece(self, piece, oy):
        x, y = self._px(piece.row, piece.col, oy)
        self._draw_single_piece(piece, x, y)

    def draw_piece_at_float(self, piece, row, col, oy):
        x = int(BOARD_OFFSET_X + col*CELL_SIZE)
        y = int(oy + row*CELL_SIZE)
        self._draw_single_piece(piece, x, y)

    def draw_pieces(self, pieces, oy, hidden=None):
        for p in pieces:
            if p is not hidden:
                self.draw_piece(p, oy)

    # =========================================================================
    # FOOTER
    # =========================================================================

    def draw_footer(self):
        txt = self.tiny_font.render("Made by Vu Nam Sang & Thai Doan Thinh",
                                     True, (88,68,38))
        self.screen.blit(txt, txt.get_rect(
            center=(BOARD_AREA_WIDTH//2, SCREEN_HEIGHT-16)))

    # =========================================================================
    # GAME OVER OVERLAY
    # =========================================================================

    def draw_game_over_overlay(self, game_state):
        if game_state == ONGOING: return
        ov = pygame.Surface((BOARD_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0,0,0,155)); self.screen.blit(ov, (0,0))

        if game_state == RED_WIN:
            msg, color = "RED WINS! 🏆", WIN_RED_COLOR
        elif game_state == BLACK_WIN:
            msg, color = "BLACK WINS! 🏆", WIN_BLK_COLOR
        else:
            msg, color = "DRAW!", (210,185,75)

        cx = BOARD_AREA_WIDTH//2; cy = SCREEN_HEIGHT//2
        for off in range(4,0,-1):
            g = self.big_font.render(msg, True, (*color,40))
            self.screen.blit(g, g.get_rect(center=(cx+off, cy)))
        text = self.big_font.render(msg, True, color)
        self.screen.blit(text, text.get_rect(center=(cx, cy)))
        sub = self.small_font.render("Nhấn 'Trò chơi mới' để chơi lại",
                                      True, (200,185,155))
        self.screen.blit(sub, sub.get_rect(center=(cx, cy+68)))

    # =========================================================================
    # FULL RENDER (nhận board_offset_y từ main)
    # =========================================================================

    def render(self, board, game_manager, hud, board_offset_y: int):
        oy = board_offset_y
        self.draw_background(oy)
        self.draw_board(oy)
        self.draw_last_move(board.move_log, oy)
        self.draw_selected_piece(game_manager.get_selected_piece(), oy)
        self.draw_valid_moves(game_manager.get_valid_moves(), oy)

        hidden = game_manager.animation_hide_piece if game_manager.animating else None
        self.draw_pieces(board.get_all_pieces(), oy, hidden=hidden)

        anim = game_manager.get_animation_draw_data()
        if anim:
            self.draw_piece_at_float(anim["piece"], anim["row"], anim["col"], oy)

        self.draw_footer()
        hud.draw(self.screen, game_manager)
        self.draw_game_over_overlay(game_manager.game_state)
        pygame.display.flip()