import pygame
import sys
from menu import MenuScreen, STATE_MENU, STATE_PLAYING, STATE_QUIT, SCREEN_W, SCREEN_H


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("🌿 Eco Tower Defense")
    clock = pygame.time.Clock()

    state = STATE_MENU

    while state != STATE_QUIT:

        if state == STATE_MENU:
            state = MenuScreen(screen).run()

        elif state == STATE_PLAYING:
            from game import Game          # import tardif — évite les imports circulaires
            state = Game(screen, clock).run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()