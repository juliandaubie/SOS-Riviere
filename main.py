import pygame
import sys
from constantes import *
from menu import MenuScreen


# Point d'entrée principal du jeu SOS-Riviere - Eco Tower Defense écologique
# Initialise Pygame, crée la fenêtre et l'horloge, gère la boucle d'états (menu -> jeu -> quit)


def main():
    # Fonction principale : setup initial, boucle while sur états jusqu'à quit
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


# Lance le jeu si ce fichier est exécuté directement
if __name__ == "__main__":
    main()

