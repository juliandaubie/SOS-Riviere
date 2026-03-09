import pygame
import math
from constantes import *

# ─── Types de trajectoire ────────────────────────────────────────────────────
TRAJ_LINEAR    = "linear"     # Éolienne  — droit, rapide
TRAJ_PARABOLIC = "parabolic"  # Arbre, Compost — arc flèche
TRAJ_LOBBED    = "lobbed"     # Solaire   — bombe arc haut + AoE
TRAJ_WAVE      = "wave"       # Barrage   — onde sinusoïdale amortie


def predict_position(enemy, proj_speed, src_x, src_y):
    """
    Prédit où sera l'ennemi quand le projectile l'atteint.
    Résolution itérative en avançant l'ennemi sur sa trajectoire.
    """
    from utils import tile_to_px

    ex, ey = enemy.x, enemy.y
    speed  = max(enemy.speed, 1.0)

    for _ in range(8):
        d     = math.hypot(ex - src_x, ey - src_y)
        t_fly = d / proj_speed

        remaining = t_fly
        idx  = enemy.path_index
        nx, ny = enemy.x, enemy.y

        while remaining > 0 and idx + 1 < len(ENEMY_PATH):
            tx, ty  = tile_to_px(*ENEMY_PATH[idx + 1])
            seg_d   = math.hypot(tx - nx, ty - ny)
            if seg_d < 0.001:
                idx += 1
                continue
            step = speed * remaining
            if step >= seg_d:
                remaining -= seg_d / speed
                nx, ny = float(tx), float(ty)
                idx += 1
            else:
                ratio  = step / seg_d
                nx    += (tx - nx) * ratio
                ny    += (ty - ny) * ratio
                remaining = 0

        ex, ey = nx, ny

    return ex, ey


class Projectile:

    SPEEDS = {
        TRAJ_LINEAR:    340,
        TRAJ_PARABOLIC: 220,
        TRAJ_LOBBED:    180,
        TRAJ_WAVE:      260,
    }

    def __init__(self, src_x, src_y, target, damage, slow_factor,
                 aoe_radius, color, traj=TRAJ_LINEAR):
        self.src_x = float(src_x)
        self.src_y = float(src_y)
        self.color       = color
        self.damage      = damage
        self.slow_factor = slow_factor
        self.aoe_radius  = aoe_radius
        self.traj        = traj
        self.alive       = True
        self.radius      = 5
        self.speed       = self.SPEEDS[traj]

        # ── Destination prédite (point fixe) ─────────────────────────────────
        self.dst_x, self.dst_y = predict_position(
            target, self.speed, src_x, src_y
        )

        self.x = float(src_x)
        self.y = float(src_y)

        dist_total      = math.hypot(self.dst_x - src_x, self.dst_y - src_y)
        self.total_time = dist_total / self.speed if self.speed > 0 else 0.01
        self.elapsed    = 0.0

        # Onde : amplitude et fréquence
        self._wave_amp  = 20.0
        self._wave_freq = 3.5

        # Traînée
        self.trail = []

    # ── Mise à jour ──────────────────────────────────────────────────────────

    def update(self, dt, enemies):
        if not self.alive:
            return

        self.elapsed += dt
        t = min(self.elapsed / self.total_time, 1.0)

        sx, sy = self.src_x, self.src_y
        dx_total = self.dst_x - sx
        dy_total = self.dst_y - sy
        dist_total = math.hypot(dx_total, dy_total)

        if self.traj == TRAJ_LINEAR:
            self.x = sx + dx_total * t
            self.y = sy + dy_total * t

        elif self.traj == TRAJ_PARABOLIC:
            arc_h  = dist_total * 0.35
            self.x = sx + dx_total * t
            self.y = sy + dy_total * t - arc_h * 4 * t * (1 - t)

        elif self.traj == TRAJ_LOBBED:
            arc_h  = dist_total * 0.65
            self.x = sx + dx_total * t
            self.y = sy + dy_total * t - arc_h * 4 * t * (1 - t)

        elif self.traj == TRAJ_WAVE:
            if dist_total > 0:
                perp_x = -dy_total / dist_total
                perp_y =  dx_total / dist_total
            else:
                perp_x, perp_y = 0.0, 0.0
            amp  = self._wave_amp * (1.0 - t)
            wave = amp * math.sin(self._wave_freq * math.pi * t * 4)
            self.x = sx + dx_total * t + perp_x * wave
            self.y = sy + dy_total * t + perp_y * wave

        # Traînée
        self.trail.append((self.x, self.y))
        if len(self.trail) > 14:
            self.trail.pop(0)

        if t >= 1.0:
            self._on_hit(enemies)

    def _on_hit(self, enemies):
        self.alive = False
        ix, iy = self.dst_x, self.dst_y

        if self.aoe_radius > 0:
            for e in enemies:
                if e.alive and math.hypot(e.x - ix, e.y - iy) <= self.aoe_radius:
                    e.take_damage(self.damage)
                    if self.slow_factor < 1.0:
                        e.apply_slow(self.slow_factor)
        else:
            # Touche l'ennemi le plus proche du point d'impact
            best, best_d = None, float("inf")
            for e in enemies:
                if not e.alive:
                    continue
                d = math.hypot(e.x - ix, e.y - iy)
                if d < best_d:
                    best_d, best = d, e
            if best and best_d < 48:
                best.take_damage(self.damage)
                if self.slow_factor < 1.0:
                    best.apply_slow(self.slow_factor)

    # ── Dessin ───────────────────────────────────────────────────────────────

    def draw(self, surface):
        if not self.alive:
            return

        ix, iy = int(self.x), int(self.y)

        # Traînée
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(160 * (i / max(len(self.trail), 1)))
            r     = max(1, self.radius - 2 - (len(self.trail) - i) // 4)
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, self.color + (alpha,), (r, r), r)
            surface.blit(s, (int(tx) - r, int(ty) - r))

        # Corps selon trajectoire
        if self.traj == TRAJ_LINEAR:
            dx = self.dst_x - self.src_x
            dy = self.dst_y - self.src_y
            d  = math.hypot(dx, dy)
            if d > 0:
                nx, ny = dx/d, dy/d
                pygame.draw.line(surface, self.color,
                                 (int(ix - nx*10), int(iy - ny*10)),
                                 (int(ix + nx*4),  int(iy + ny*4)), 3)
            glow = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(glow, self.color + (130,), (7, 7), 7)
            surface.blit(glow, (ix - 7, iy - 7))

        elif self.traj == TRAJ_PARABOLIC:
            pygame.draw.circle(surface, self.color, (ix, iy), self.radius)
            glow = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            pygame.draw.circle(glow, self.color + (80,),
                               (self.radius*2, self.radius*2), self.radius*2)
            surface.blit(glow, (ix - self.radius*2, iy - self.radius*2))

        elif self.traj == TRAJ_LOBBED:
            r = self.radius + 3
            # Ombre au sol
            t = min(self.elapsed / self.total_time, 1.0)
            sh_x = int(self.src_x + (self.dst_x - self.src_x) * t)
            sh_y = int(self.dst_y)
            sh = pygame.Surface((24, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0, 0, 0, 70), (0, 0, 24, 10))
            surface.blit(sh, (sh_x - 12, sh_y - 5))
            # Corps
            pygame.draw.circle(surface, self.color, (ix, iy), r)
            pygame.draw.circle(surface, (255, 255, 255), (ix, iy), r, 2)
            glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.circle(glow, self.color + (60,), (r*2, r*2), r*2)
            surface.blit(glow, (ix - r*2, iy - r*2))

        elif self.traj == TRAJ_WAVE:
            pygame.draw.circle(surface, self.color, (ix, iy), self.radius)
            glow = pygame.Surface((self.radius*3, self.radius*3), pygame.SRCALPHA)
            pygame.draw.circle(glow, self.color + (100,),
                               (self.radius + 2, self.radius + 2), self.radius + 2)
            surface.blit(glow, (ix - self.radius, iy - self.radius))