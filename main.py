import pygame
import sys
from constantes import *
from menu import MenuScreen


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Eco Tower Defense")
    clock = pygame.time.Clock()

    state = STATE_MENU

    while state != STATE_QUIT:
        if state == STATE_MENU:
            state = MenuScreen(screen).run()
        elif state == STATE_PLAYING:
            from game import Game
            state = Game(screen, clock).run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()