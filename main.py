import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN, FPS
from ui.renderer import Renderer
from game.board import Board


def main():
    pygame.init()

    flags = pygame.FULLSCREEN if FULLSCREEN else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("Chinese Chess Test")

    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    board = Board()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pieces = board.get_all_pieces()
        renderer.render(pieces)
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()