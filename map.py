import pygame
from constantes import *
from utils import tile_to_px, px_to_tile, is_valid_tile
from tour import PlacedTower
import os

class Map:
    def __init__(self):
        self.towers = []
        self.hovered_tile = None
        self.bg_image = self._load_bg()

    def _load_bg(self):
        print(f"[DEBUG] Chemin : {MAP_BG_IMAGE_PATH}")
        print(f"[DEBUG] Existe : {os.path.exists(MAP_BG_IMAGE_PATH)}")
        if os.path.exists(MAP_BG_IMAGE_PATH):
            img = pygame.image.load(MAP_BG_IMAGE_PATH).convert()
            print("[DEBUG] Image chargée OK")
            return pygame.transform.scale(img, (COLS * TILE_SIZE, ROWS * TILE_SIZE))
        print("[DEBUG] Image NON trouvée")
        return None

    def can_place(self, col, row):
        if not is_valid_tile(col, row):
            return False
        if (col, row) in PATH_SET:
            return False
        for t in self.towers:
            if t.col == col and t.row == row:
                return False
        return True

    def place_tower(self, tower_type, col, row):
        if self.can_place(col, row):
            self.towers.append(PlacedTower(tower_type, col, row))
            return True
        return False

    def get_tower_at_px(self, mx, my):
        col, row = px_to_tile(mx, my)
        for t in self.towers:
            if t.col == col and t.row == row:
                return t
        return None

    def draw(self, surface, font_small, hovered_tower=None):
        if self.bg_image:
            surface.blit(self.bg_image, (MAP_X, MAP_Y))
        for row in range(ROWS):
            for col in range(COLS):
                x = MAP_X + col * TILE_SIZE
                y = MAP_Y + row * TILE_SIZE

                if not self.bg_image:
                    if (col, row) in PATH_SET:
                        color = PATH_COLOR if (col + row) % 2 == 0 else PATH_DARK
                    else:
                        color = GRASS_COLOR if (col + row) % 2 == 0 else GRASS_DARK

                    pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))

                if self.hovered_tile == (col, row):
                    h_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    fill = (220, 50, 50, 80) if (col, row) in PATH_SET else (100, 220, 100, 80)
                    h_surf.fill(fill)
                    surface.blit(h_surf, (x, y))

                pygame.draw.rect(surface, GRID_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 1)
                coord_text = font_small.render(f"{col},{row}", True, COORD_COLOR)
                surface.blit(coord_text, (x + 2, y + 2))

        for i in range(len(ENEMY_PATH) - 1):
            c1, r1 = ENEMY_PATH[i]
            c2, r2 = ENEMY_PATH[i + 1]
            x1, y1 = tile_to_px(c1, r1)
            x2, y2 = tile_to_px(c2, r2)
            pygame.draw.line(surface, (220, 100, 30), (x1, y1), (x2, y2), 3)

        sx, sy = tile_to_px(*ENEMY_PATH[0])
        ex, ey = tile_to_px(*ENEMY_PATH[-1])
        pygame.draw.circle(surface, (50, 220, 50), (sx, sy), 10)
        pygame.draw.circle(surface, (220, 50, 50), (ex, ey), 10)

        # Dessine d'abord les ranges, puis les tours par-dessus
        for tower in self.towers:
            tower.draw(surface, show_range=(tower is hovered_tower))

        pygame.draw.rect(surface, (80, 180, 80),
                         (MAP_X - 2, MAP_Y - 2, COLS * TILE_SIZE + 4, ROWS * TILE_SIZE + 4), 2)