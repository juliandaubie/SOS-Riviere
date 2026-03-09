import pygame
from constantes import *
from utils import *
from tour import PlacedTower

class Map:
    def __init__(self):
        self.towers = []
        self.hovered_tile = None

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

    def draw(self, surface, font_small):
        for row in range(ROWS):
            for col in range(COLS):
                x = MAP_X + col * TILE_SIZE
                y = MAP_Y + row * TILE_SIZE

                if (col, row) in PATH_SET:
                    color = PATH_COLOR if (col + row) % 2 == 0 else PATH_DARK
                else:
                    color = GRASS_COLOR if (col + row) % 2 == 0 else GRASS_DARK

                pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))


                if self.hovered_tile == (col, row):
                    h_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    if (col, row) in PATH_SET:
                        h_surf.fill((220, 50, 50, 80))
                    else:
                        h_surf.fill((100, 220, 100, 80))
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


        for tower in self.towers:
            tower.draw(surface)


        pygame.draw.rect(surface, (80, 180, 80),
                         (MAP_X - 2, MAP_Y - 2, COLS * TILE_SIZE + 4, ROWS * TILE_SIZE + 4), 2)
