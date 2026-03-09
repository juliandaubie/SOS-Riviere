import pygame
import math
from constantes import *
from utils import tile_to_px, dist, draw_tower_icon
from projectile import Projectile, TRAJ_LINEAR, TRAJ_PARABOLIC, TRAJ_LOBBED, TRAJ_WAVE

# ── Trajectoire assignée à chaque type de tour ───────────────────────────────
TOWER_TRAJECTORY = {
    "Arbre":    TRAJ_PARABOLIC,  # arc flèche végétale
    "Solaire":  TRAJ_LOBBED,     # bombe solaire arc haut + AoE
    "Éolienne": TRAJ_LINEAR,     # tir rapide direct
    "Compost":  TRAJ_PARABOLIC,  # arc organique
    "Barrage":  TRAJ_WAVE,       # onde d'eau sinusoïdale
}


class PlacedTower:
    def __init__(self, tower_type, col, row):
        self.tower_type = tower_type
        self.col = col
        self.row = row
        self.cx, self.cy = tile_to_px(col, row)

        self.range_px   = tower_type["range_tiles"] * TILE_SIZE
        self.damage     = tower_type["damage"]
        self.fire_rate  = tower_type["fire_rate"]
        self.slow       = tower_type["slow"]
        self.aoe        = tower_type["aoe"]
        self.proj_color = tower_type["proj_color"]
        self.traj       = TOWER_TRAJECTORY.get(tower_type["name"], TRAJ_LINEAR)

        self._cooldown = 0.0

    # ── Attaque ──────────────────────────────────────────────────────────────

    def update(self, dt, enemies, projectiles):
        self._cooldown -= dt
        if self._cooldown > 0:
            return

        # Cible la plus avancée sur le chemin dans la portée
        target   = None
        best_idx = -1
        for e in enemies:
            if not e.alive:
                continue
            if dist(self.cx, self.cy, e.x, e.y) <= self.range_px and e.path_index > best_idx:
                best_idx = e.path_index
                target   = e

        if target is None:
            return

        projectiles.append(Projectile(
            self.cx, self.cy,
            target,
            self.damage,
            self.slow,
            self.aoe,
            self.proj_color,
            traj=self.traj,
        ))
        self._cooldown = 1.0 / self.fire_rate

    # ── Dessin ───────────────────────────────────────────────────────────────

    def draw(self, surface, show_range=False):
        x, y = self.cx, self.cy

        if show_range:
            r = int(self.range_px)
            rs = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
            col = self.tower_type["color"]
            pygame.draw.circle(rs, col + (30,), (r+2, r+2), r)
            for angle in range(0, 360, 8):
                rad = math.radians(angle)
                px  = int((r+2) + math.cos(rad) * r)
                py  = int((r+2) + math.sin(rad) * r)
                pygame.draw.circle(rs, col + (180,), (px, py), 2)
            surface.blit(rs, (x - r - 2, y - r - 2))

        bg = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4), pygame.SRCALPHA)
        pygame.draw.rect(bg, self.tower_type["color"] + (180,),
                         (0, 0, TILE_SIZE-4, TILE_SIZE-4), border_radius=6)
        surface.blit(bg, (x - TILE_SIZE//2 + 2, y - TILE_SIZE//2 + 2))
        draw_tower_icon(surface, self.tower_type, x, y - 2)


class DraggableItem:
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
        shadow = pygame.Surface((size*2+10, size*2+10), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 80), (size+5, size+8), size)
        surface.blit(shadow, (self.x - size - 1, self.y - size + 3))

        bg = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(bg, self.tower_type["color"] + (220,), (size, size), size)
        pygame.draw.circle(bg, (255, 255, 255, 80), (size, size), size, 2)
        surface.blit(bg, (self.x - size, self.y - size))
        draw_tower_icon(surface, self.tower_type, self.x, self.y - 2, size - 4)

        # Range preview
        r = int(self.tower_type["range_tiles"] * TILE_SIZE)
        rs = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        col = self.tower_type["color"]
        pygame.draw.circle(rs, col + (20,), (r+2, r+2), r)
        for angle in range(0, 360, 8):
            rad = math.radians(angle)
            px  = int((r+2) + math.cos(rad) * r)
            py  = int((r+2) + math.sin(rad) * r)
            pygame.draw.circle(rs, col + (140,), (px, py), 2)
        surface.blit(rs, (self.x - r - 2, self.y - r - 2))