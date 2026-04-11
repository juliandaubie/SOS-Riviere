import pygame
import math
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
        self.bg_image      = self._load_bg()
        # Pollution : 0.0 = eau propre, 1.0 = eau très polluée
        self.pollution     = 0.0
        self._pollution_surf = None
        self._dirty_surf_cache = {}

    # Charge et scale l'image de fond carte si existe
    def _load_bg(self):
        if os.path.exists(MAP_BG_IMAGE_PATH):
            img = pygame.image.load(MAP_BG_IMAGE_PATH).convert()
            return pygame.transform.scale(img, (COLS * TILE_SIZE, ROWS * TILE_SIZE))
        return None

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

    # Calcule couleur pollution interpolée bleu -> marron + alpha
    def _get_pollution_color(self):
        """Interpolation eau bleue → marron pollué."""
        p = self.pollution
        r = int(30  + p * 140)
        g = int(100 - p * 70)
        b = int(180 - p * 140)
        return (r, g, b, int(80 + p * 130))

    # Rendu carte : fond, pollution overlay, grille (drag), tours, bordure
    def draw(self, surface, font_small, hovered_tower=None, dragging_item=None):
        # ── Fond de carte ────────────────────────────────────────────────────
        if self.bg_image:
            surface.blit(self.bg_image, (MAP_X, MAP_Y))
        else:
            pygame.draw.rect(surface, GRASS_COLOR,
                             (MAP_X, MAP_Y, COLS * TILE_SIZE, ROWS * TILE_SIZE))

        # ── Overlay pollution sur le chemin (eau qui se salit) ───────────────
        if self.pollution > 0.01:
            poll_surf = pygame.Surface((COLS * TILE_SIZE, ROWS * TILE_SIZE), pygame.SRCALPHA)
            pcol = self._get_pollution_color()
            for (col, row) in ENEMY_PATH:
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                pygame.draw.rect(poll_surf, pcol, (x, y, TILE_SIZE, TILE_SIZE))
            # Bulles de pollution
            if self.pollution > 0.3:
                import random
                rng = random.Random(int(self.pollution * 100))
                for _ in range(int(self.pollution * 20)):
                    bx = rng.randint(0, COLS * TILE_SIZE)
                    by = rng.randint(0, ROWS * TILE_SIZE)
                    br = rng.randint(2, 6)
                    pygame.draw.circle(poll_surf, (60, 40, 10, 120), (bx, by), br)
            surface.blit(poll_surf, (MAP_X, MAP_Y))

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

