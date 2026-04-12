import pygame
from constantes import *
from utils import tile_to_px, px_to_tile, is_valid_tile
from tour import PlacedTower
import os


# Classe Map : gère la carte de jeu (placement tours, pollution, rendu)
class Map:
    # Initialisation de la carte : liste tours, hover, bg image, pollution=0.0
    def __init__(self):
        self.towers        = []
        self.hovered_tile  = None
        self.pollution_images = self._load_pollution_images()
        # Pollution : 0.0 = eau propre, 1.0 = eau très polluée
        self.pollution     = 0.0

    def _load_pollution_images(self):
        images = []
        target_size = (COLS * TILE_SIZE, ROWS * TILE_SIZE)
        for path in POLLUTION_IMAGES:
            if os.path.exists(path):
                img = pygame.image.load(path).convert()
                images.append(pygame.transform.scale(img, target_size))
            else:
                images.append(None)
        return images


    # Retourne l'index d'image selon le niveau de pollution (0-4)
    def _get_pollution_image_index(self):
        if self.pollution < 0.2:
            return 0
        elif self.pollution < 0.4:
            return 1
        elif self.pollution < 0.6:
            return 2
        elif self.pollution < 0.8:
            return 3
        else:
            return 4

    # Augmente pollution quand déchet atteint fin ou meurt dans l'eau
    def add_pollution(self, amount=0.015):
        """Appelé quand un déchet atteint la fin ou meurt dans l'eau."""
        self.pollution = min(1.0, self.pollution + amount)

    # Réduit pollution quand déchet détruit par tour
    def reduce_pollution(self, amount=0.005):
        """Appelé quand un déchet est détruit par une tour."""
        self.pollution = max(0.0, self.pollution - amount)

    # Vérifie si placement tour possible (pas chemin, pas occupé, valide)
    def can_place(self, col, row):
        if not is_valid_tile(col, row):
            return False
        if (col, row) in PATH_SET:
            return False
        for t in self.towers:
            if t.col == col and t.row == row:
                return False
        return True

    # Place nouvelle tour si possible, retourne True/False
    def place_tower(self, tower_type, col, row):
        if self.can_place(col, row):
            self.towers.append(PlacedTower(tower_type, col, row))
            return True
        return False

    # Retourne tour à position px (pour hover/upgrade)
    def get_tower_at_px(self, mx, my):
        col, row = px_to_tile(mx, my)
        for t in self.towers:
            if t.col == col and t.row == row:
                return t
        return None

    def draw(self, surface, font_small, hovered_tower=None, dragging_item=None):
        # ── Fond de carte selon niveau pollution ────────────────────────────
        img_index = self._get_pollution_image_index()
        bg_image = self.pollution_images[img_index]
        if bg_image:
            surface.blit(bg_image, (MAP_X, MAP_Y))
        else:
            pygame.draw.rect(surface, GRASS_COLOR,
                             (MAP_X, MAP_Y, COLS * TILE_SIZE, ROWS * TILE_SIZE))

        # ── Marqueur fin ────────────────────────────────────────────────────
        ex, ey = tile_to_px(*ENEMY_PATH[-1])
        pygame.draw.circle(surface, (220, 50, 50), (ex, ey), 12)
        pygame.draw.circle(surface, (255, 100, 80), (ex, ey), 8)

        # ── Grille pendant drag ─────────────────────────────────────────────
        if dragging_item:
            for row in range(ROWS):
                for col in range(COLS):
                    x = MAP_X + col * TILE_SIZE
                    y = MAP_Y + row * TILE_SIZE

                    if self.hovered_tile == (col, row):
                        h_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        fill = (220, 50, 50, 90) if (col, row) in PATH_SET else (80, 220, 100, 90)
                        h_surf.fill(fill)
                        surface.blit(h_surf, (x, y))

                    pygame.draw.rect(surface, GRID_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 1)
                    coord_text = font_small.render(f"{col},{row}", True, COORD_COLOR)
                    surface.blit(coord_text, (x + 2, y + 2))

        # ── Tours ────────────────────────────────────────────────────────────
        for tower in self.towers:
            tower.draw(surface, show_range=(tower is hovered_tower))

        # ── Bordure carte ────────────────────────────────────────────────────
        border_color = (80, 180, 80) if self.pollution < 0.3 else \
            (180, 120, 40) if self.pollution < 0.7 else (180, 60, 40)
        pygame.draw.rect(surface, border_color,
                         (MAP_X - 2, MAP_Y - 2, COLS * TILE_SIZE + 4, ROWS * TILE_SIZE + 4), 3)