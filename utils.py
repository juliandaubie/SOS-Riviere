import pygame
import math
from constantes import *

def tile_to_px(col, row):
    """Convertit des coordonnées tile en pixels (centre de la tile)."""
    x = MAP_X + col * TILE_SIZE + TILE_SIZE // 2
    y = MAP_Y + row * TILE_SIZE + TILE_SIZE // 2
    return x, y

def px_to_tile(x, y):
    """Convertit des pixels en coordonnées tile."""
    col = (x - MAP_X) // TILE_SIZE
    row = (y - MAP_Y) // TILE_SIZE
    return col, row

def is_valid_tile(col, row):
    return 0 <= col < COLS and 0 <= row < ROWS

def draw_tree(surface, x, y, size=20, color=(34, 120, 34)):
    """Dessine un arbre stylisé."""
    trunk_w = size // 4
    trunk_h = size // 3
    pygame.draw.rect(surface, (100, 60, 20),
                     (x - trunk_w//2, y + size//4, trunk_w, trunk_h))
    for i in range(3):
        r = size - i * 5
        alpha_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        darker = tuple(max(0, c - i*15) for c in color)
        pygame.draw.circle(alpha_surf, darker + (200,), (r, r), r)
        surface.blit(alpha_surf, (x - r, y - size//2 + i * 4 - r//2))

def draw_tower_icon(surface, tower, x, y, size=22):
    """Dessine une icône de tour selon son type."""
    c = tower["color"]
    if tower["name"] == "Arbre":
        draw_tree(surface, x, y, size, c)
    elif tower["name"] == "Solaire":
        pygame.draw.circle(surface, c, (x, y), size // 2)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            ex = int(x + math.cos(rad) * (size // 2 + 6))
            ey = int(y + math.sin(rad) * (size // 2 + 6))
            pygame.draw.line(surface, c, (x, y), (ex, ey), 2)
    elif tower["name"] == "Éolienne":
        pygame.draw.line(surface, (200, 200, 200), (x, y), (x, y + size), 3)
        for angle in range(0, 360, 120):
            rad = math.radians(angle)
            ex = int(x + math.cos(rad) * size)
            ey = int(y + math.sin(rad) * size)
            pygame.draw.line(surface, c, (x, y), (ex, ey), 4)
    elif tower["name"] == "Compost":
        pygame.draw.ellipse(surface, c, (x - size//2, y - size//4, size, size//2))
        for i in range(3):
            sx = x - size//3 + i * (size//3)
            pygame.draw.line(surface, (34, 80, 20), (sx, y - size//4), (sx - 4, y - size//2), 2)
    elif tower["name"] == "Barrage":
        pygame.draw.rect(surface, c, (x - size//2, y - size//3, size, size//1.5))
        pygame.draw.rect(surface, (60, 140, 255), (x - size//2 + 2, y, size - 4, size//3))
