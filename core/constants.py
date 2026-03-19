import pygame

# INIT PYGAME INFO
pygame.init()
info = pygame.display.Info()

# BOARD SIZE
BOARD_ROWS = 10
BOARD_COLS = 9

# SCREEN SETTINGS
FULLSCREEN = True
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
FPS = 60

# Kích thước mỗi ô cờ
CELL_SIZE = 80

# Vị trí bắt đầu vẽ bàn cờ trên màn hình
BOARD_OFFSET_X = (SCREEN_WIDTH - (BOARD_COLS - 1) * CELL_SIZE) // 2
BOARD_OFFSET_Y = (SCREEN_HEIGHT - (BOARD_ROWS - 1) * CELL_SIZE) // 2

# Bán kính quân cờ nếu vẽ hình tròn
PIECE_RADIUS = 30

# PLAYER / COLOR SIDE
RED = 1
BLACK = -1
EMPTY = 0

# PIECE TYPES
KING = "K"       # Tướng
ADVISOR = "A"    # Sĩ
ELEPHANT = "B"   # Tượng
ROOK = "R"       # Xe
KNIGHT = "N"     # Mã
CANNON = "C"     # Pháo
PAWN = "P"       # Tốt

PIECE_TYPES = [KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN]

# PIECE VALUES FOR AI
PIECE_VALUES = {
    KING: 10000,
    ROOK: 500,
    KNIGHT: 300,
    CANNON: 300,
    ADVISOR: 200,
    ELEPHANT: 200,
    PAWN: 100,
}

# GAME STATES
ONGOING = 0
RED_WIN = 1
BLACK_WIN = -1
DRAW = 2

# UI COLORS
WHITE = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
RED_COLOR = (220, 20, 60)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
YELLOW = (255, 215, 0)
GREEN = (60, 179, 113)
BLUE = (70, 130, 180)
BROWN = (139, 69, 19)
BEIGE = (240, 217, 181)

SELECT_COLOR = (255, 255, 0)
VALID_MOVE_COLOR = (50, 205, 50)
CAPTURE_MOVE_COLOR = (255, 99, 71)
LAST_MOVE_COLOR = (30, 144, 255)

# BOARD / PALACE / SPECIAL ZONES
PALACE_COLS = range(3, 6)
RED_PALACE_ROWS = range(7, 10)
BLACK_PALACE_ROWS = range(0, 3)

RIVER_UPPER_BOUND = 4
RIVER_LOWER_BOUND = 5

# PAWN DIRECTIONS
RED_FORWARD = -1
BLACK_FORWARD = 1

# ASSET PATHS
ASSET_FOLDER = "assets/images/"
BOARD_IMAGE = ASSET_FOLDER + "board.png"

RED_PIECE_IMAGES = {
    KING: ASSET_FOLDER + "red_king.png",
    ADVISOR: ASSET_FOLDER + "red_advisor.png",
    ELEPHANT: ASSET_FOLDER + "red_elephant.png",
    ROOK: ASSET_FOLDER + "red_rook.png",
    KNIGHT: ASSET_FOLDER + "red_knight.png",
    CANNON: ASSET_FOLDER + "red_cannon.png",
    PAWN: ASSET_FOLDER + "red_pawn.png",
}

BLACK_PIECE_IMAGES = {
    KING: ASSET_FOLDER + "black_king.png",
    ADVISOR: ASSET_FOLDER + "black_advisor.png",
    ELEPHANT: ASSET_FOLDER + "black_elephant.png",
    ROOK: ASSET_FOLDER + "black_rook.png",
    KNIGHT: ASSET_FOLDER + "black_knight.png",
    CANNON: ASSET_FOLDER + "black_cannon.png",
    PAWN: ASSET_FOLDER + "black_pawn.png",
}