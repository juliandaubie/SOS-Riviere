import pygame
import math
from constantes import *
from utils import tile_to_px, dist

class Enemy:
    BASE_SPEED = 80  # pixels/sec

    def __init__(self, hp=100, speed_mult=1.0):
        self.path_index = 0
        self.max_hp = hp
        self.hp = hp
        self.base_speed = self.BASE_SPEED * speed_mult
        self.speed = self.base_speed
        self.slow_timer = 0.0      # secondes restantes de ralentissement
        self.slow_factor = 1.0
        self.alive = True
        self.reached_end = False

        # Position initiale = centre de la 1ère tile du chemin
        sx, sy = tile_to_px(*ENEMY_PATH[0])
        self.x = float(sx)
        self.y = float(sy)

    # ── appelé par les tours ──────────────────────────────────────────────────
    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def apply_slow(self, factor, duration=1.5):
        """Ralentit l'ennemi (factor < 1). On garde le slow le plus fort."""
        if factor < self.slow_factor or self.slow_timer <= 0:
            self.slow_factor = factor
            self.slow_timer  = duration

    # ── mise à jour ──────────────────────────────────────────────────────────
    def update(self, dt):
        if not self.alive or self.reached_end:
            return

        # Mise à jour du slow
        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.speed = self.base_speed * self.slow_factor
        else:
            self.slow_factor = 1.0
            self.speed = self.base_speed

        # Avancer vers la prochaine waypoint
        if self.path_index + 1 >= len(ENEMY_PATH):
            self.reached_end = True
            return

        tx, ty = tile_to_px(*ENEMY_PATH[self.path_index + 1])
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        move = self.speed * dt

        if d <= move:
            self.x, self.y = float(tx), float(ty)
            self.path_index += 1
        else:
            self.x += dx / d * move
            self.y += dy / d * move

    # ── dessin ───────────────────────────────────────────────────────────────
    def draw(self, surface):
        if not self.alive:
            return

        ix, iy = int(self.x), int(self.y)
        r = 16

        # Corps
        color = (180, 40, 40) if self.slow_factor == 1.0 else (80, 80, 220)
        pygame.draw.circle(surface, color, (ix, iy), r)
        pygame.draw.circle(surface, (220, 80, 80), (ix, iy), r, 2)

        # Yeux
        pygame.draw.circle(surface, (255, 255, 200), (ix - 5, iy - 4), 4)
        pygame.draw.circle(surface, (255, 255, 200), (ix + 5, iy - 4), 4)
        pygame.draw.circle(surface, (30, 10, 10),   (ix - 5, iy - 4), 2)
        pygame.draw.circle(surface, (30, 10, 10),   (ix + 5, iy - 4), 2)

        # Barre de vie
        bar_w = 34
        bar_h = 5
        bx = ix - bar_w // 2
        by = iy - r - 10
        pygame.draw.rect(surface, (60, 10, 10), (bx, by, bar_w, bar_h))
        hp_ratio = max(0, self.hp / self.max_hp)
        hp_color = (
            int(220 * (1 - hp_ratio)),
            int(200 * hp_ratio),
            20
        )
        pygame.draw.rect(surface, hp_color, (bx, by, int(bar_w * hp_ratio), bar_h))
        pygame.draw.rect(surface, (200, 200, 200), (bx, by, bar_w, bar_h), 1)

        # Indicateur slow
        if self.slow_timer > 0:
            font = pygame.font.SysFont("segoeui", 11)
            s = font.render("❄ slow", True, (140, 180, 255))
            surface.blit(s, (ix - s.get_width()//2, by - 14))
