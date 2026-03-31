import pygame
from core.constants import RED, RED_PIECE_IMAGES, BLACK_PIECE_IMAGES, CELL_SIZE

# Kích thước quân cờ = 94% cell để có viền mỏng quanh quân
PIECE_SIZE = int(CELL_SIZE * 0.94)

# Cache ảnh — load mỗi file một lần duy nhất
_image_cache: dict = {}


def _load_image(path: str) -> pygame.Surface:
    if path not in _image_cache:
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (PIECE_SIZE, PIECE_SIZE))
            _image_cache[path] = img
        except Exception:
            _image_cache[path] = None
    return _image_cache[path]


class Piece:
    def __init__(self, piece_type, color, row, col):
        self.piece_type = piece_type
        self.color      = color
        self.row        = row
        self.col        = col
        self._image     = None   # lazy load

    @property
    def image(self) -> pygame.Surface:
        if self._image is None:
            path = (RED_PIECE_IMAGES if self.color == RED
                    else BLACK_PIECE_IMAGES).get(self.piece_type)
            if path:
                self._image = _load_image(path)
        return self._image

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_position(self):
        return self.row, self.col

    def __repr__(self):
        side = "RED" if self.color == RED else "BLACK"
        return f"Piece({self.piece_type}, {side}, {self.row}, {self.col})"