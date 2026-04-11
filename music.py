import pygame
import os
from constantes import MUSIC_MENU_PATH, MUSIC_JEU_PATH, MUSIC_VOLUME



def play(track: str, loops: int = -1):

    path = MUSIC_MENU_PATH if track == "menu" else MUSIC_JEU_PATH

    if not os.path.exists(path):
        print(f"[music] Fichier introuvable : {path}")
        return

    current = getattr(play, "_current", None)
    if current == track and pygame.mixer.music.get_busy():
        return

    pygame.mixer.music.stop()
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    pygame.mixer.music.play(loops)
    play._current = track


def stop():
    """Arrête la musique en cours."""
    pygame.mixer.music.stop()
    play._current = None