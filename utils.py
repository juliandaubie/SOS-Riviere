import pygame
import math
from constantes import *

def tile_to_px(col, row):
    x = MAP_X + col * TILE_SIZE + TILE_SIZE // 2
    y = MAP_Y + row * TILE_SIZE + TILE_SIZE // 2
    return x, y

def px_to_tile(x, y):
    col = (x - MAP_X) // TILE_SIZE
    row = (y - MAP_Y) // TILE_SIZE
    return col, row

def is_valid_tile(col, row):
    return 0 <= col < COLS and 0 <= row < ROWS

def dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)

def draw_tree(surface, x, y, size=20, color=(34, 120, 34)):
    trunk_w = max(2, size // 4)
    trunk_h = max(2, size // 3)
    pygame.draw.rect(surface, (100, 60, 20),
                     (x - trunk_w//2, y + size//4, trunk_w, trunk_h))
    for i in range(3):
        r = max(1, size - i * 5)
        alpha_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        darker = tuple(max(0, c - i*15) for c in color)
        pygame.draw.circle(alpha_surf, darker + (200,), (r, r), r)
        surface.blit(alpha_surf, (x - r, y - size//2 + i * 4 - r//2))

_tower_images = {}

def draw_tower_icon(surface, tower, x, y, size=22):
    img_path = tower.get("image")
    if img_path:
        if img_path not in _tower_images:
            import os
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                _tower_images[img_path] = img
            else:
                _tower_images[img_path] = None

        img = _tower_images[img_path]
        if img:
            scaled = pygame.transform.scale(img, (size * 2, size * 2))
            surface.blit(scaled, (x - size, y - size))
            return

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
        pygame.draw.rect(surface, c, (x - size//2, y - size//3, size, int(size//1.5)))
        pygame.draw.rect(surface, (60, 140, 255), (x - size//2 + 2, y, size - 4, size//3))