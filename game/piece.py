import pygame
from core.constants import RED, RED_PIECE_IMAGES, BLACK_PIECE_IMAGES

class Piece:
    def __init__(self, piece_type, color, row, col):
        self.piece_type = piece_type
        self.color = color
        self.row = row
        self.col = col
        self.image = self.load_image()

    def load_image(self):
        if self.color == RED:
            path = RED_PIECE_IMAGES[self.piece_type]
        else:
            path = BLACK_PIECE_IMAGES[self.piece_type]

        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (56, 56))
        return image

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_position(self):
        return self.row, self.col

    def __repr__(self):
        side = "RED" if self.color == 1 else "BLACK"
        return f"Piece({self.piece_type}, {side}, {self.row}, {self.col})"