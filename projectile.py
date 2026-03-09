import pygame
import math
from constantes import *


class Projectile:
    SPEED = 280  # pixels/sec

    def __init__(self, x, y, target, damage, slow_factor, aoe_radius, color):
        self.x = float(x)
        self.y = float(y)
        self.target     = target
        self.damage     = damage
        self.slow_factor = slow_factor
        self.aoe_radius = aoe_radius
        self.color      = color
        self.alive      = True
        self.radius     = 5

    def update(self, dt, enemies):
        if not self.alive:
            return
        if not self.target.alive:
            self.alive = False
            return

        tx, ty = self.target.x, self.target.y
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        move = self.SPEED * dt

        if d <= move + self.radius:
            self._on_hit(enemies)
        else:
            self.x += dx / d * move
            self.y += dy / d * move

    def _on_hit(self, enemies):
        self.alive = False
        if self.aoe_radius > 0:
            for e in enemies:
                if e.alive and math.hypot(e.x - self.target.x, e.y - self.target.y) <= self.aoe_radius:
                    e.take_damage(self.damage)
                    if self.slow_factor < 1.0:
                        e.apply_slow(self.slow_factor)
        else:
            self.target.take_damage(self.damage)
            if self.slow_factor < 1.0:
                self.target.apply_slow(self.slow_factor)

    def draw(self, surface):
        if not self.alive:
            return
        ix, iy = int(self.x), int(self.y)
        glow = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
        pygame.draw.circle(glow, self.color + (60,), (self.radius*2, self.radius*2), self.radius*2)
        surface.blit(glow, (ix - self.radius*2, iy - self.radius*2))
        pygame.draw.circle(surface, self.color, (ix, iy), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), self.radius, 1)