import os

# ══════════════════════════════════════════════════════════════════════════════
# LOGIC CONSTANTS
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

# ── Game / App states ─────────────────────────────────────────────────────────
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

# ── Timing ────────────────────────────────────────────────────────────────────
MOVE_ANIMATION_DURATION = 0.22
AI_MOVE_DELAY           = 280
FPS                     = 60

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

CELL_SIZE      = 62
BOARD_OFFSET_X = 42

BOARD_AREA_WIDTH = BOARD_OFFSET_X * 2 + (BOARD_COLS - 1) * CELL_SIZE   # 580
PANEL_WIDTH      = 295
SCREEN_WIDTH     = BOARD_AREA_WIDTH + PANEL_WIDTH                        # 875

# Control panel (panel điều khiển phía TRÊN bàn cờ)
# Tính từ thực tế: PAD(12) + ROW1(40) + GAP(8) + ROW2(34) + PAD(12) + MARGIN(14)
CTRL_PANEL_X        = 4     # lề trái
CTRL_PANEL_Y        = 6     # lề trên

BOARD_OFFSET_Y_CLOSED = 120   # panel đóng (không có box tùy chỉnh)
BOARD_OFFSET_Y_OPEN   = 238   # panel mở (có box tùy chỉnh + slider)
BOARD_OFFSET_Y        = BOARD_OFFSET_Y_CLOSED  # mặc định

BOARD_H = (BOARD_ROWS - 1) * CELL_SIZE          # 558
SCREEN_HEIGHT = BOARD_OFFSET_Y_OPEN + BOARD_H + 30   # 826

BUTTON_WIDTH  = 220
BUTTON_HEIGHT = 46

UNDO_BUTTON_Y  = 440
RESET_BUTTON_Y = 500
PAUSE_BUTTON_Y = 560
MENU_BUTTON_Y  = 620

# ══════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE  (warm lacquer theme)
# ══════════════════════════════════════════════════════════════════════════════

# Board
BOARD_BG_OUTER = (168, 112,  46)
BOARD_BG_INNER = (210, 162,  82)
BOARD_LINE     = ( 90,  55,  18)
RIVER_COLOR    = (160, 200, 218)

# Background
BG_DARK   = ( 28,  18,   8)
BG_PANEL  = ( 22,  14,   5)

# Piece highlight
SELECT_COLOR     = (255, 210,   0)
VALID_MOVE_COLOR = ( 80, 205,  80)
CAPTURE_COLOR    = (230,  60,  60)
LAST_MOVE_COLOR  = (255, 180,   0)

# Panel / text
PANEL_BG       = ( 30,  20,   8)
PANEL_BORDER   = (140,  88,  28)
TEXT_COLOR     = (235, 215, 175)
TEXT_DIM       = (165, 140,  95)
TEXT_RED_SIDE  = (230,  70,  70)
TEXT_BLK_SIDE  = (110, 165, 235)

# Buttons  (5 variants)
BUTTON_BG        = (130,  82,  30)
BUTTON_BG_HOVER  = (175, 118,  50)
BUTTON_BG_2      = ( 48, 112,  48)
BUTTON_BG_2_HOV  = ( 68, 148,  68)
BUTTON_BG_3      = ( 48,  80, 138)
BUTTON_BG_3_HOV  = ( 68, 108, 175)
BUTTON_BG_4      = (128,  42,  30)
BUTTON_BG_4_HOV  = (172,  62,  46)
BUTTON_TEXT_COLOR = (248, 238, 215)

# Win overlay
WIN_BG_COLOR  = (  0,   0,   0, 165)
WIN_RED_COLOR = (235,  75,  75)
WIN_BLK_COLOR = (100, 160, 235)
WIN_DRW_COLOR = (210, 185,  75)

# Misc
WHITE       = (255, 255, 255)
BLACK_COLOR = (  0,   0,   0)
BEIGE       = (238, 225, 195)
OVERLAY_COLOR = (0, 0, 0, 160)

# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULTY
# ══════════════════════════════════════════════════════════════════════════════

DIFFICULTY_LEVELS = {
    "Beginner": 1,
    "Easy":     2,
    "Medium":   3,
    "Hard":     4,
    "Master":   5,
}

DIFFICULTY_TIME = {
    "Beginner": 3.0,
    "Easy":     5.0,
    "Medium":  10.0,
    "Hard":    18.0,
    "Master":  30.0,
}

# ── Asset paths ───────────────────────────────────────────────────────────────
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