"""
layout.py — 3-panel layout, responsive, không overlap.

  LEFT  (22%) | MID (56%) | RIGHT (22%)
              |  [BOARD]  |

Board luôn fit trong MID với padding đủ lớn để không chạm 2 panel bên.
"""
import pygame
from core.constants import BOARD_ROWS, BOARD_COLS


class Layout:
    LEFT_RATIO  = 0.22
    RIGHT_RATIO = 0.22
    # MID = phần còn lại (~56%)

    # Padding tối thiểu quanh board (px)
    BOARD_PAD_H = 24   # trái/phải trong vùng MID
    BOARD_PAD_V = 28   # trên/dưới màn hình
    BOARD_FRAME = 14   # frame gỗ vẽ thêm ra ngoài grid

    # Giới hạn cell size để board không quá lớn
    MAX_CELL = 72

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self._compute()

    def _compute(self):
        sw, sh = self.sw, self.sh

        #3 vùng ngang
        lw = int(sw * self.LEFT_RATIO)
        rw = int(sw * self.RIGHT_RATIO)
        mw = sw - lw - rw          # MID chiếm phần còn lại

        self.left_rect  = pygame.Rect(0,       0, lw, sh)
        self.mid_rect   = pygame.Rect(lw,      0, mw, sh)
        self.right_rect = pygame.Rect(lw + mw, 0, rw, sh)

        #Cell size: fit vào MID với padding, không vượt MAX_CELL
        avail_w = mw - self.BOARD_PAD_H * 2
        avail_h = sh - self.BOARD_PAD_V * 2

        cs = min(
            avail_w // (BOARD_COLS - 1),
            avail_h // (BOARD_ROWS - 1),
            self.MAX_CELL,
        )
        cs = max(cs, 40)   # tối thiểu 40px

        bpw = (BOARD_COLS - 1) * cs    # pixel width  của grid (giao điểm)
        bph = (BOARD_ROWS - 1) * cs    # pixel height của grid

        # Căn giữa board trong vùng MID (ngang) và màn hình (dọc)
        bx = lw + (mw - bpw) // 2
        by = (sh - bph) // 2

        self.cell_size = cs
        self.board_ox  = bx
        self.board_oy  = by

        # Rect bao gồm frame gỗ (dùng để vẽ nền board)
        f = self.BOARD_FRAME
        self.board_rect = pygame.Rect(bx - f, by - f, bpw + f*2, bph + f*2)

        #Kiểm tra không overlap
        # Board phải nằm hoàn toàn trong MID
        assert bx >= lw,           f"Board tràn trái: bx={bx} < lw={lw}"
        assert bx + bpw <= lw + mw, f"Board tràn phải: {bx+bpw} > {lw+mw}"
        assert by >= 0,             f"Board tràn trên: by={by}"
        assert by + bph <= sh,      f"Board tràn dưới: {by+bph} > {sh}"

    #Helpers

    def px(self, row: int, col: int) -> tuple:
        """Tọa độ pixel của giao điểm (row, col)."""
        return (self.board_ox + col * self.cell_size,
                self.board_oy + row * self.cell_size)

    def cell_at(self, mx: int, my: int):
        """(row, col) từ tọa độ chuột, None nếu ngoài board."""
        if not self.mid_rect.collidepoint(mx, my):
            return None
        cs = self.cell_size
        col = round((mx - self.board_ox) / cs)
        row = round((my - self.board_oy) / cs)
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return (row, col)
        return None

    def rebuild(self, screen_w: int, screen_h: int):
        """Gọi khi VIDEORESIZE."""
        self.sw = screen_w
        self.sh = screen_h
        self._compute()

    def debug_print(self):
        print(f"Screen  : {self.sw}x{self.sh}")
        print(f"Left    : {self.left_rect}")
        print(f"Mid     : {self.mid_rect}")
        print(f"Right   : {self.right_rect}")
        print(f"Cell    : {self.cell_size}px")
        print(f"Board   : ox={self.board_ox} oy={self.board_oy} "
              f"w={(BOARD_COLS-1)*self.cell_size} h={(BOARD_ROWS-1)*self.cell_size}")