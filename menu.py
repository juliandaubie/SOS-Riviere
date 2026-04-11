import pygame
import os
import random
from constantes import *
from utils import draw_tower_icon


# ─── Palette latérale ────────────────────────────────────────────────────────
class Palette:
    PANEL_X = MAP_X + COLS * TILE_SIZE + 22
    PANEL_W = 192
    ITEM_H  = 86

    def __init__(self):
        self.items_rects = []
        for i in range(len(TOWER_TYPES)):
            y = MAP_Y + i * self.ITEM_H
            self.items_rects.append(pygame.Rect(self.PANEL_X, y, self.PANEL_W, self.ITEM_H - 5))

    def get_tower_at(self, mx, my):
        for i, rect in enumerate(self.items_rects):
            if rect.collidepoint(mx, my):
                return TOWER_TYPES[i], rect.centerx, rect.centery
        return None, 0, 0

    def draw(self, surface, font, font_small, money=0):
        panel_rect = pygame.Rect(self.PANEL_X - 10, MAP_Y - 10,
                                 self.PANEL_W + 20, ROWS * TILE_SIZE + 20)
        pygame.draw.rect(surface, PANEL_BG, panel_rect, border_radius=12)
        pygame.draw.rect(surface, (50, 130, 60), panel_rect, 2, border_radius=12)

        title = font.render("🌱 TOURS", True, (160, 240, 130))
        surface.blit(title, (self.PANEL_X + 35, MAP_Y - 4))

        for tower, rect in zip(TOWER_TYPES, self.items_rects):
            can_afford = money >= tower["cost"]

            # Fond
            col = tower["color"] if can_afford else (60, 60, 60)
            pygame.draw.rect(surface, col, rect, border_radius=8)
            overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 50 if can_afford else 120),
                             (0, 0, rect.w, rect.h), border_radius=8)
            surface.blit(overlay, rect.topleft)
            border_c = (200, 240, 160) if can_afford else (80, 80, 80)
            pygame.draw.rect(surface, border_c, rect, 1, border_radius=8)

            draw_tower_icon(surface, tower, rect.x + 28, rect.centery - 4)

            name_c = (240, 255, 220) if can_afford else (130, 130, 130)
            name_surf = font.render(tower["name"], True, name_c)
            surface.blit(name_surf, (rect.x + 58, rect.y + 4))

            cost_c = (255, 220, 60) if can_afford else (100, 100, 100)
            cost_surf = font_small.render(f"💰 {tower['cost']}$", True, cost_c)
            surface.blit(cost_surf, (rect.x + 58, rect.y + 22))

            range_surf = font_small.render(f"🎯 {tower['range_tiles']} tiles", True, (160, 220, 255))
            surface.blit(range_surf, (rect.x + 58, rect.y + 37))

            desc_surf = font_small.render(tower["desc"], True, (170, 215, 150))
            surface.blit(desc_surf, (rect.x + 8, rect.y + 63))

        # Légende
        leg_y = MAP_Y + len(TOWER_TYPES) * self.ITEM_H + 12
        pygame.draw.circle(surface, (220, 50, 50), (self.PANEL_X + 12, leg_y), 8)
        surface.blit(font_small.render("Arrivée", True, TEXT_COLOR), (self.PANEL_X + 26, leg_y - 7))


# ─── Panel d'upgrade (affiché quand on survole une tour placée) ──────────────
class UpgradePanel:
    W = 200
    H = 160

    def draw(self, surface, tower, mx, my, font, font_small, money):
        if tower is None:
            return

        # Position intelligente (évite de sortir de l'écran)
        px = min(mx + 15, SCREEN_W - self.W - 10)
        py = max(10, min(my - 20, SCREEN_H - self.H - 10))

        bg = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        pygame.draw.rect(bg, (8, 22, 12, 230), (0, 0, self.W, self.H), border_radius=10)
        pygame.draw.rect(bg, tower.tower_type["color"] + (200,), (0, 0, self.W, self.H), 2, border_radius=10)
        surface.blit(bg, (px, py))

        y = py + 8
        name = font.render(f"🏗 {tower.tower_type['name']}", True, (220, 255, 180))
        surface.blit(name, (px + 10, y))
        y += 20

        # Stats actuelles
        stats = [
            f"DMG: {tower.damage:.0f}",
            f"Rate: {tower.fire_rate:.1f}/s",
            f"Range: {tower.range_px/TILE_SIZE:.1f}t",
        ]
        for s in stats:
            surf = font_small.render(s, True, (180, 230, 160))
            surface.blit(surf, (px + 10, y))
            y += 14

        y += 4
        pygame.draw.line(surface, (60, 120, 60), (px + 8, y), (px + self.W - 8, y))
        y += 6

        if tower.can_upgrade():
            stars = "★" * (tower.upgrade_level + 1)
            lvl = font_small.render(f"Upgrade {stars}", True, (255, 220, 80))
            surface.blit(lvl, (px + 10, y))
            y += 14

            desc = font_small.render(tower.upgrade_desc(), True, (200, 240, 180))
            surface.blit(desc, (px + 10, y))
            y += 14

            cost = tower.upgrade_cost()
            can = money >= cost
            cost_c = (80, 220, 80) if can else (220, 80, 80)
            cost_t = font_small.render(f"💰 {cost}$  [clic droit]", True, cost_c)
            surface.blit(cost_t, (px + 10, y))
        else:
            max_t = font.render("⭐ NIVEAU MAX", True, (255, 200, 50))
            surface.blit(max_t, (px + 10, y))

        # Message éco
        eco = tower.tower_type.get("eco_msg", "")
        if eco:
            y = py + self.H - 22
            eco_s = font_small.render(eco[:30], True, (120, 200, 120))
            surface.blit(eco_s, (px + 6, y))


# ─── Bouton générique ────────────────────────────────────────────────────────
class Button:
    def __init__(self, text, x, y, w, h,
                 color=(40, 120, 60), hover_color=(60, 180, 90),
                 text_color=(220, 255, 210), font=None, border_radius=12):
        self.text          = text
        self.rect          = pygame.Rect(x, y, w, h)
        self.color         = color
        self.hover_color   = hover_color
        self.text_color    = text_color
        self.font          = font
        self.border_radius = border_radius

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        col = self.hover_color if hovered else self.color
        shadow = self.rect.move(4, 4)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow, border_radius=self.border_radius)
        pygame.draw.rect(surface, col, self.rect, border_radius=self.border_radius)
        border_c = (120, 230, 140) if hovered else (60, 140, 80)
        pygame.draw.rect(surface, border_c, self.rect, 2, border_radius=self.border_radius)
        if self.font:
            txt = self.font.render(self.text, True, self.text_color)
            surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─── Écran de menu ───────────────────────────────────────────────────────────
class MenuScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self.w, self.h = screen.get_size()

        self.font_title = pygame.font.SysFont("segoeui", 68, bold=True)
        self.font_sub   = pygame.font.SysFont("segoeui", 20)
        self.font_btn   = pygame.font.SysFont("segoeui", 30, bold=True)

        self.background = self._load_background()
        self.particles  = [self._new_particle(random_y=True) for _ in range(40)]

        btn_w, btn_h = 280, 60
        cx = self.w // 2
        self.btn_start = Button("▶  JOUER", cx - btn_w//2, MENU_BTN_Y,
                                btn_w, btn_h, font=self.font_btn)
        self.btn_quit  = Button("✕  QUITTER", cx - btn_w//2, MENU_BTN_Y + 80,
                                btn_w, btn_h,
                                color=(100, 40, 40), hover_color=(170, 60, 60),
                                text_color=(255, 200, 200), font=self.font_btn)

        self.slogans = [
            "Protège la rivière contre les déchets !",
            "Chaque plastique dans l'eau détruit un écosystème.",
            "Les tours vertes sont nos meilleures alliées.",
            "L'énergie renouvelable : notre bouclier écologique.",
        ]
        self.slogan_idx = 0
        self.slogan_timer = 0

    def _load_background(self):
        if os.path.exists(BG_IMAGE_PATH):
            bg = pygame.image.load(BG_IMAGE_PATH).convert()
            return pygame.transform.scale(bg, (self.w, self.h))
        bg = pygame.Surface((self.w, self.h))
        for y in range(self.h):
            t = y / self.h
            pygame.draw.line(bg, (int(10+t*5), int(60-t*30), int(25-t*15)), (0, y), (self.w, y))
        return bg

    def _new_particle(self, random_y=False):
        return {
            "x":     random.randint(0, self.w),
            "y":     random.randint(0, self.h) if random_y else -10,
            "speed": random.uniform(0.3, 1.0),
            "drift": random.uniform(-0.4, 0.4),
            "size":  random.randint(3, 8),
            "alpha": random.randint(60, 180),
            "color": random.choice([(120, 220, 100), (80, 200, 220), (200, 220, 80)]),
        }

    def _update_particles(self):
        for p in self.particles:
            p["y"] += p["speed"]
            p["x"] += p["drift"]
            if p["y"] > self.h + 10:
                p.update(self._new_particle())

    def _draw_particles(self):
        for p in self.particles:
            s = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(s, p["color"] + (p["alpha"],),
                               (p["size"], p["size"]), p["size"])
            self.screen.blit(s, (int(p["x"]), int(p["y"])))

    def run(self) -> str:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.slogan_timer += dt
            if self.slogan_timer > 4:
                self.slogan_timer = 0
                self.slogan_idx = (self.slogan_idx + 1) % len(self.slogans)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return STATE_QUIT
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return STATE_QUIT
                if self.btn_start.is_clicked(event):
                    return STATE_PLAYING
                if self.btn_quit.is_clicked(event):
                    return STATE_QUIT

            self.screen.blit(self.background, (0, 0))
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))

            self._update_particles()
            self._draw_particles()

            # Titre
            title = self.font_title.render("🌿 EARTHTECH", True, (140, 240, 120))
            shadow = self.font_title.render("🌿 EARTHTECH", True, (0, 0, 0))
            cx = self.w // 2
            ty = self.h // 2 - 160
            self.screen.blit(shadow, shadow.get_rect(center=(cx + 3, ty + 3)))
            self.screen.blit(title,  title.get_rect(center=(cx, ty)))

            sub = self.font_sub.render("Tower Defense Écologique", True, (180, 240, 160))
            self.screen.blit(sub, sub.get_rect(center=(cx, ty + 60)))

            # Slogan rotatif
            slog = self.font_sub.render(self.slogans[self.slogan_idx], True, (200, 255, 200))
            self.screen.blit(slog, slog.get_rect(center=(cx, ty + 90)))

            self.btn_start.draw(self.screen)
            self.btn_quit.draw(self.screen)

            pygame.display.flip()
