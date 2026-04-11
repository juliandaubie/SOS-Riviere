import pygame
import math
from constantes import *
from utils import tile_to_px, dist, draw_tower_icon
from projectile import Projectile, TRAJ_LINEAR, TRAJ_PARABOLIC, TRAJ_LOBBED, TRAJ_WAVE

TOWER_TRAJECTORY = {
    "Arbre":    TRAJ_PARABOLIC,
    "Solaire":  TRAJ_LOBBED,
    "Éolienne": TRAJ_LINEAR,
    "Compost":  TRAJ_PARABOLIC,
    "Barrage":  TRAJ_WAVE,
}


class PlacedTower:
    def __init__(self, tower_type, col, row):
        self.tower_type  = tower_type
        self.col = col
        self.row = row
        self.cx, self.cy = tile_to_px(col, row)
        self.upgrade_level = 0   # 0 = base, 1/2/3 = upgrades

        self._apply_stats()
        self._cooldown = 0.0
        self._shoot_anim = 0.0   # flash visuel au tir

    def _apply_stats(self):
        t = self.tower_type
        self.range_px  = t["range_tiles"] * TILE_SIZE
        self.damage    = t["damage"]
        self.fire_rate = t["fire_rate"]
        self.slow      = t["slow"]
        self.aoe       = t["aoe"]
        self.proj_color = t["proj_color"]
        self.traj       = TOWER_TRAJECTORY.get(t["name"], TRAJ_LINEAR)

        for i in range(self.upgrade_level):
            up = t["upgrades"][i]
            self.damage    += up["damage_bonus"]
            self.range_px  += up["range_bonus"] * TILE_SIZE
            self.fire_rate += up["fire_rate_bonus"]
            self.slow       = max(0.1, self.slow + up.get("slow_bonus", 0))

    def can_upgrade(self):
        return self.upgrade_level < len(self.tower_type["upgrades"])

    def upgrade_cost(self):
        if not self.can_upgrade():
            return None
        return self.tower_type["upgrades"][self.upgrade_level]["cost"]

    def upgrade_desc(self):
        if not self.can_upgrade():
            return "MAX"
        return self.tower_type["upgrades"][self.upgrade_level]["desc"]

    def do_upgrade(self):
        if self.can_upgrade():
            self.upgrade_level += 1
            self._apply_stats()

    # ── Attaque ──────────────────────────────────────────────────────────────

    def update(self, dt, enemies, projectiles):
        self._cooldown -= dt
        if self._shoot_anim > 0:
            self._shoot_anim -= dt

        if self._cooldown > 0:
            return

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
            self.cx, self.cy, target,
            self.damage, self.slow, self.aoe, self.proj_color,
            traj=self.traj,
        ))
        self._cooldown  = 1.0 / self.fire_rate
        self._shoot_anim = 0.12

    # ── Dessin ───────────────────────────────────────────────────────────────

    def draw(self, surface, show_range=False):
        x, y = self.cx, self.cy

        if show_range:
            r = int(self.range_px)
            rs = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
            col = self.tower_type["color"]
            pygame.draw.circle(rs, col + (25,), (r+2, r+2), r)
            for angle in range(0, 360, 7):
                rad = math.radians(angle)
                px  = int((r+2) + math.cos(rad) * r)
                py  = int((r+2) + math.sin(rad) * r)
                pygame.draw.circle(rs, col + (200,), (px, py), 2)
            surface.blit(rs, (x - r - 2, y - r - 2))

        # Flash au tir
        if self._shoot_anim > 0:
            flash = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            alpha = int(self._shoot_anim / 0.12 * 100)
            flash.fill((255, 255, 255, alpha))
            surface.blit(flash, (x - TILE_SIZE//2, y - TILE_SIZE//2))

        # Fond
        bg = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4), pygame.SRCALPHA)
        pygame.draw.rect(bg, self.tower_type["color"] + (200,),
                         (0, 0, TILE_SIZE-4, TILE_SIZE-4), border_radius=8)
        surface.blit(bg, (x - TILE_SIZE//2 + 2, y - TILE_SIZE//2 + 2))

        draw_tower_icon(surface, self.tower_type, x, y - 2)

        # Badge niveau upgrade
        if self.upgrade_level > 0:
            stars = "★" * self.upgrade_level
            font = pygame.font.SysFont("segoeui", 10, bold=True)
            s = font.render(stars, True, (255, 220, 50))
            surface.blit(s, (x - s.get_width()//2, y + TILE_SIZE//2 - 14))


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
        pygame.draw.circle(shadow, (0, 0, 0, 100), (size+5, size+8), size)
        surface.blit(shadow, (self.x - size - 1, self.y - size + 3))

        bg = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(bg, self.tower_type["color"] + (230,), (size, size), size)
        pygame.draw.circle(bg, (255, 255, 255, 100), (size, size), size, 2)
        surface.blit(bg, (self.x - size, self.y - size))
        draw_tower_icon(surface, self.tower_type, self.x, self.y - 2, size - 4)

        r = int(self.tower_type["range_tiles"] * TILE_SIZE)
        rs = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        col = self.tower_type["color"]
        pygame.draw.circle(rs, col + (18,), (r+2, r+2), r)
        for angle in range(0, 360, 7):
            rad = math.radians(angle)
            px  = int((r+2) + math.cos(rad) * r)
            py  = int((r+2) + math.sin(rad) * r)
            pygame.draw.circle(rs, col + (150,), (px, py), 2)
        surface.blit(rs, (self.x - r - 2, self.y - r - 2))
