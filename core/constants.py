import os

# ══════════════════════════════════════════════════════════════════════════════
# GAME LOGIC CONSTANTS  (không thay đổi)
# ══════════════════════════════════════════════════════════════════════════════
RED   =  1
BLACK = -1
EMPTY =  0

KING     = "K"
ADVISOR  = "A"
ELEPHANT = "E"
ROOK     = "R"
KNIGHT   = "N"
CANNON   = "C"
PAWN     = "P"

PIECE_VALUES = {
    KING: 10000, ROOK: 500, CANNON: 300, KNIGHT: 270,
    ADVISOR: 120, ELEPHANT: 110, PAWN: 60,
}

BOARD_ROWS = 10
BOARD_COLS = 9

PALACE_COLS       = {3, 4, 5}
RED_PALACE_ROWS   = {7, 8, 9}
BLACK_PALACE_ROWS = {0, 1, 2}

RED_FORWARD   = -1
BLACK_FORWARD =  1

ONGOING   = "ongoing"
RED_WIN   = "red_win"
BLACK_WIN = "black_win"
DRAW      = "draw"

MENU_STATE             = "menu"
AI_BATTLE_SELECT_STATE = "ai_battle_select"
PLAYING_STATE          = "playing"

PVP_MODE   = "pvp"
PVAI_MODE  = "pvai"
AIVAI_MODE = "aivai"

AI_MINIMAX   = "minimax"
AI_ALPHABETA = "alpha_beta"

MOVE_ANIMATION_DURATION = 0.22
AI_MOVE_DELAY           = 280
FPS                     = 60

# ══════════════════════════════════════════════════════════════════════════════
# WINDOW & LAYOUT  — tất cả tính từ WIN_W / WIN_H, không hardcode chồng chéo
# ══════════════════════════════════════════════════════════════════════════════

WIN_W = 1280
WIN_H =  800

# Tỉ lệ 3 vùng
_LEFT_RATIO  = 0.22
_MID_RATIO   = 0.54
_RIGHT_RATIO = 1.0 - _LEFT_RATIO - _MID_RATIO   # ~0.24

LEFT_W  = int(WIN_W * _LEFT_RATIO)               # 281
RIGHT_W = int(WIN_W * _RIGHT_RATIO)              # 307
MID_W   = WIN_W - LEFT_W - RIGHT_W               # phần còn lại

# Rect của 3 panel chính
LEFT_RECT  = (0,          0, LEFT_W,  WIN_H)
MID_RECT   = (LEFT_W,     0, MID_W,   WIN_H)
RIGHT_RECT = (LEFT_W + MID_W, 0, RIGHT_W, WIN_H)

# Board: square, fit vừa vùng giữa với padding
_BOARD_PAD = 18
_cs_by_w = (MID_W  - _BOARD_PAD * 2) // (BOARD_COLS - 1)
_cs_by_h = (WIN_H  - _BOARD_PAD * 2) // (BOARD_ROWS - 1)
CELL_SIZE = min(_cs_by_w, _cs_by_h)             # 81

BOARD_PX_W = (BOARD_COLS - 1) * CELL_SIZE        # 648
BOARD_PX_H = (BOARD_ROWS - 1) * CELL_SIZE        # 729 (> WIN_H → clamp)

# Nếu board cao hơn window, scale lại
if BOARD_PX_H > WIN_H - _BOARD_PAD * 2:
    CELL_SIZE  = (WIN_H - _BOARD_PAD * 2) // (BOARD_ROWS - 1)
    BOARD_PX_W = (BOARD_COLS - 1) * CELL_SIZE
    BOARD_PX_H = (BOARD_ROWS - 1) * CELL_SIZE

# Offset bàn cờ: căn giữa trong vùng MID, căn giữa dọc màn hình
BOARD_OFFSET_X = LEFT_W + (MID_W  - BOARD_PX_W) // 2
BOARD_OFFSET_Y =          (WIN_H  - BOARD_PX_H) // 2

# Alias ngắn cho các module khác
SCREEN_WIDTH  = WIN_W
SCREEN_HEIGHT = WIN_H

# ── Control panel (phía trên bàn cờ, trong vùng MID) ─────────────────────────
# Không còn cần BOARD_OFFSET_Y_OPEN/CLOSED —
# control panel nằm hoàn toàn trong LEFT panel hoặc pop-up nhỏ
CTRL_PANEL_X = LEFT_W + 4
CTRL_PANEL_Y = 6
CTRL_PANEL_W = MID_W  - 8

# ── Right panel button layout ─────────────────────────────────────────────────
BUTTON_WIDTH  = RIGHT_W - 32
BUTTON_HEIGHT = 46
_BTN_X        = LEFT_W + MID_W + 16    # x gốc của các nút bên phải

UNDO_BUTTON_Y  = 420
RESET_BUTTON_Y = 480
PAUSE_BUTTON_Y = 540
MENU_BUTTON_Y  = 600

# ══════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE
# ══════════════════════════════════════════════════════════════════════════════

# Board
BOARD_BG_OUTER = (148,  95,  35)
BOARD_BG_INNER = (200, 155,  72)
BOARD_LINE     = ( 80,  48,  14)
RIVER_COLOR    = (148, 190, 210)

# Window background
BG_DARK  = ( 18,  11,   4)

# Highlight
SELECT_COLOR     = (255, 210,   0)
VALID_MOVE_COLOR = ( 70, 200,  70)
CAPTURE_COLOR    = (225,  55,  55)
LAST_MOVE_COLOR  = (255, 175,   0)

# Panel
PANEL_BG     = ( 22,  14,   6)
PANEL_BORDER = (130,  82,  24)
TEXT_COLOR   = (230, 210, 165)
TEXT_DIM     = (155, 130,  85)
TEXT_RED_SIDE  = (228,  68,  68)
TEXT_BLK_SIDE  = (105, 158, 230)

# Buttons
BUTTON_BG       = (120,  75,  25)
BUTTON_BG_HOVER = (165, 112,  45)
BUTTON_BG_2     = ( 42, 105,  42)
BUTTON_BG_2_HOV = ( 60, 140,  60)
BUTTON_BG_3     = ( 42,  72, 128)
BUTTON_BG_3_HOV = ( 60, 100, 165)
BUTTON_BG_4     = (118,  38,  26)
BUTTON_BG_4_HOV = (158,  55,  38)
BUTTON_TEXT_COLOR = (245, 235, 210)

# Win overlay
WIN_RED_COLOR = (232,  72,  72)
WIN_BLK_COLOR = ( 95, 152, 230)
WIN_DRW_COLOR = (205, 180,  70)

# Misc
WHITE       = (255, 255, 255)
BLACK_COLOR = (  0,   0,   0)
BEIGE       = (235, 220, 190)
OVERLAY_COLOR = (0, 0, 0, 155)

# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULTY
# ══════════════════════════════════════════════════════════════════════════════
DIFFICULTY_LEVELS = {
    "Beginner": 1, "Easy": 2, "Medium": 3, "Hard": 4, "Master": 5,
}
DIFFICULTY_TIME = {
    "Beginner": 3.0, "Easy": 5.0, "Medium": 10.0, "Hard": 18.0, "Master": 30.0,
}

# ══════════════════════════════════════════════════════════════════════════════
# ASSET PATHS
# ══════════════════════════════════════════════════════════════════════════════
_ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images")

RED_PIECE_IMAGES = {
    KING:     os.path.join(_ASSETS, "red_king.png"),
    ADVISOR:  os.path.join(_ASSETS, "red_advisor.png"),
    ELEPHANT: os.path.join(_ASSETS, "red_elephant.png"),
    ROOK:     os.path.join(_ASSETS, "red_rook.png"),
    KNIGHT:   os.path.join(_ASSETS, "red_knight.png"),
    CANNON:   os.path.join(_ASSETS, "red_cannon.png"),
    PAWN:     os.path.join(_ASSETS, "red_pawn.png"),
}
BLACK_PIECE_IMAGES = {
    KING:     os.path.join(_ASSETS, "black_king.png"),
    ADVISOR:  os.path.join(_ASSETS, "black_advisor.png"),
    ELEPHANT: os.path.join(_ASSETS, "black_elephant.png"),
    ROOK:     os.path.join(_ASSETS, "black_rook.png"),
    KNIGHT:   os.path.join(_ASSETS, "black_knight.png"),
    CANNON:   os.path.join(_ASSETS, "black_cannon.png"),
    PAWN:     os.path.join(_ASSETS, "black_pawn.png"),
}