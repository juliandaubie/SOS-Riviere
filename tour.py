import pygame
from constantes import *
from utils import *

class PlacedTower:
    def __init__(self, tower_type, col, row):
        self.tower_type = tower_type
        self.col = col
        self.row = row

    def draw(self, surface):
        x, y = tile_to_px(self.col, self.row)
        # Fond de la tour
        bg_surf = pygame.Surface((TILE_SIZE - 4, TILE_SIZE - 4), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, self.tower_type["color"] + (180,),
                         (0, 0, TILE_SIZE - 4, TILE_SIZE - 4), border_radius=6)
        surface.blit(bg_surf, (x - TILE_SIZE//2 + 2, y - TILE_SIZE//2 + 2))
        draw_tower_icon(surface, self.tower_type, x, y - 2)


class DraggableItem:
    """Un objet qu'on glisse depuis la palette vers la carte."""
    def __init__(self, tower_type, origin_x, origin_y):
        self.tower_type = tower_type
        self.x = origin_x
        self.y = origin_y
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def start_drag(self, mouse_x, mouse_y):
        self.dragging = True
        self.offset_x = self.x - mouse_x
        self.offset_y = self.y - mouse_y

    def update(self, mouse_x, mouse_y):
        if self.dragging:
            self.x = mouse_x + self.offset_x
            self.y = mouse_y + self.offset_y

    def stop_drag(self):
        self.dragging = False

    def draw(self, surface, alpha=255):
        size = 30
        # Ombre
        shadow = pygame.Surface((size * 2 + 10, size * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 80), (size + 5, size + 8), size)
        surface.blit(shadow, (self.x - size - 1, self.y - size + 3))
        # Cercle de fond
        bg = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(bg, self.tower_type["color"] + (220,), (size, size), size)
        pygame.draw.circle(bg, (255, 255, 255, 80), (size, size), size, 2)
        surface.blit(bg, (self.x - size, self.y - size))
        draw_tower_icon(surface, self.tower_type, self.x, self.y - 2, size - 4)
