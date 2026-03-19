import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN, FPS
from game.piece import Piece
from ui.renderer import Renderer


def main():
    pygame.init()

    flags = pygame.FULLSCREEN if FULLSCREEN else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("Chinese Chess Test")

    clock = pygame.time.Clock()
    renderer = Renderer(screen)

    pieces = [
        Piece("R", 1, 9, 0),
        Piece("N", 1, 9, 1),
        Piece("K", 1, 9, 4),
        Piece("K", -1, 0, 4),
        Piece("R", -1, 0, 0),
        Piece("C", -1, 2, 1),
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        renderer.render(pieces)
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()