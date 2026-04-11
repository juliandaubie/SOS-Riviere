import pygame
import math
from constantes import *
from utils import tile_to_px


class Enemy:
    _image      = None
    _image_boss = None

    def __init__(self, hp=100, speed_mult=1.0, reward=10, is_boss=False):
        self.path_index  = 0
        self.max_hp      = hp
        self.hp          = hp
        self.base_speed  = (60 if is_boss else 80) * speed_mult
        self.speed       = self.base_speed
        self.slow_timer  = 0.0
        self.slow_factor = 1.0
        self.alive       = True
        self.reached_end = False
        self.reward      = reward
        self.is_boss     = is_boss

        sx, sy = tile_to_px(*ENEMY_PATH[0])
        self.x = float(sx)
        self.y = float(sy)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def apply_slow(self, factor, duration=1.5):
        if factor < self.slow_factor or self.slow_timer <= 0:
            self.slow_factor = factor
            self.slow_timer  = duration

    def update(self, dt):
        if not self.alive or self.reached_end:
            return

        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.speed = self.base_speed * self.slow_factor
        else:
            self.slow_factor = 1.0
            self.speed = self.base_speed

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

    def draw(self, surface):
        if not self.alive:
            return
        ix, iy = int(self.x), int(self.y)
        r = 40 if self.is_boss else 28

        # Charger image
        if self.is_boss:
            if Enemy._image_boss is None:
                import os
                if os.path.exists(ENEMY_IMAGE_PATH):
                    img = pygame.image.load(ENEMY_IMAGE_PATH).convert_alpha()
                    Enemy._image_boss = img
                else:
                    Enemy._image_boss = False
            img = Enemy._image_boss
        else:
            if Enemy._image is None:
                import os
                if os.path.exists(ENEMY_IMAGE_PATH):
                    img = pygame.image.load(ENEMY_IMAGE_PATH).convert_alpha()
                    Enemy._image = img
                else:
                    Enemy._image = False
            img = Enemy._image

        size = r * 2
        if img:
            # Teinte rouge si boss
            scaled = pygame.transform.scale(img, (size, size))
            if self.is_boss:
                tinted = scaled.copy()
                tinted.fill((255, 80, 80, 120), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(scaled, (ix - r, iy - r))
                surface.blit(tinted, (ix - r, iy - r))
            else:
                if self.slow_timer > 0:
                    # Overlay bleu si ralenti
                    surface.blit(scaled, (ix - r, iy - r))
                    overlay = pygame.Surface((size, size), pygame.SRCALPHA)
                    overlay.fill((80, 130, 255, 90))
                    surface.blit(overlay, (ix - r, iy - r))
                else:
                    surface.blit(scaled, (ix - r, iy - r))
        else:
            color = (200, 50, 50) if self.is_boss else (180, 40, 40)
            if self.slow_timer > 0:
                color = (80, 80, 220)
            pygame.draw.circle(surface, color, (ix, iy), r)
            pygame.draw.circle(surface, (255, 100, 100), (ix, iy), r, 2)

        # Étiquette BOSS
        if self.is_boss:
            font = pygame.font.SysFont("segoeui", 11, bold=True)
            b = font.render("☠ BOSS", True, (255, 80, 50))
            surface.blit(b, (ix - b.get_width()//2, iy - r - 18))

        # Barre de vie
        bar_w = 50 if self.is_boss else 36
        bar_h = 6  if self.is_boss else 5
        bx = ix - bar_w // 2
        by = iy - r - 12
        pygame.draw.rect(surface, (40, 8, 8), (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        hp_ratio = max(0, self.hp / self.max_hp)
        bar_color = (
            int(220 * (1 - hp_ratio)),
            int(200 * hp_ratio),
            20
        )
        pygame.draw.rect(surface, bar_color, (bx, by, int(bar_w * hp_ratio), bar_h))
        pygame.draw.rect(surface, (180, 180, 180), (bx, by, bar_w, bar_h), 1)

        if self.slow_timer > 0:
            font = pygame.font.SysFont("segoeui", 10)
            s = font.render("❄", True, (140, 200, 255))
            surface.blit(s, (ix + r - 8, iy - r))
