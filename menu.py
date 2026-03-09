import pygame
import os
import random
from constantes import *
from utils import draw_tower_icon


class Palette:
    PANEL_X = MAP_X + COLS * TILE_SIZE + 20
    PANEL_W = 180
    ITEM_H  = 90

    def __init__(self):
        self.items_rects = []
        for i, t in enumerate(TOWER_TYPES):
            y = MAP_Y + i * self.ITEM_H
            self.items_rects.append(pygame.Rect(self.PANEL_X, y, self.PANEL_W, self.ITEM_H - 6))

    def get_tower_at(self, mx, my):
        for i, rect in enumerate(self.items_rects):
            if rect.collidepoint(mx, my):
                return TOWER_TYPES[i], rect.centerx, rect.centery
        return None, 0, 0

    def draw(self, surface, font, font_small):
        panel_rect = pygame.Rect(self.PANEL_X - 10, MAP_Y - 10,
                                 self.PANEL_W + 20, ROWS * TILE_SIZE + 20)
        pygame.draw.rect(surface, (20, 45, 25), panel_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 140, 60), panel_rect, 2, border_radius=10)

        title = font.render("TOURS", True, (180, 240, 140))
        surface.blit(title, (self.PANEL_X + 40, MAP_Y - 5))

        for i, (tower, rect) in enumerate(zip(TOWER_TYPES, self.items_rects)):
            pygame.draw.rect(surface, tower["color"], rect, border_radius=8)
            overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 60), (0, 0, rect.w, rect.h), border_radius=8)
            surface.blit(overlay, rect.topleft)
            pygame.draw.rect(surface, (200, 240, 180), rect, 1, border_radius=8)

            draw_tower_icon(surface, tower, rect.x + 30, rect.centery - 5)

            name_surf  = font.render(tower["name"], True, (240, 255, 220))
            cost_surf  = font_small.render(f"💰 {tower['cost']}$", True, (255, 220, 80))
            range_surf = font_small.render(f"🎯 {tower['range_tiles']} tiles", True, (180, 230, 255))
            desc_surf  = font_small.render(tower["desc"], True, (180, 220, 160))

            surface.blit(name_surf,  (rect.x + 60, rect.y + 5))
            surface.blit(cost_surf,  (rect.x + 60, rect.y + 23))
            surface.blit(range_surf, (rect.x + 60, rect.y + 40))
            surface.blit(desc_surf,  (rect.x + 10, rect.y + 67))

        leg_y = MAP_Y + len(TOWER_TYPES) * self.ITEM_H + 10
        pygame.draw.circle(surface, (50, 220, 50),  (self.PANEL_X + 12, leg_y),      8)
        surface.blit(font_small.render("Départ",  True, TEXT_COLOR), (self.PANEL_X + 25, leg_y - 7))
        pygame.draw.circle(surface, (220, 50, 50),  (self.PANEL_X + 12, leg_y + 22), 8)
        surface.blit(font_small.render("Arrivée", True, TEXT_COLOR), (self.PANEL_X + 25, leg_y + 15))


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
        self._hovered      = False

    def draw(self, surface):
        self._hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        col = self.hover_color if self._hovered else self.color
        shadow = self.rect.move(4, 4)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow, border_radius=self.border_radius)
        pygame.draw.rect(surface, col, self.rect, border_radius=self.border_radius)
        border_col = (120, 230, 140) if self._hovered else (60, 140, 80)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=self.border_radius)
        if self.font:
            txt_surf = self.font.render(self.text, True, self.text_color)
            surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


class MenuScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self.w, self.h = screen.get_size()

        self.font_title = pygame.font.SysFont("segoeui", 72, bold=True)
        self.font_sub   = pygame.font.SysFont("segoeui", 22)
        self.font_btn   = pygame.font.SysFont("segoeui", 32, bold=True)
        self.font_hint  = pygame.font.SysFont("segoeui", 14)

        self.background = self._load_background()
        self.particles  = [self._new_particle(random_y=True) for _ in range(30)]

        btn_w, btn_h = 260, 58
        cx = self.w // 2
        self.btn_start = Button(
            "▶  JOUER", cx - btn_w//2, MENU_BTN_Y,
            btn_w, btn_h, font=self.font_btn
        )
        self.btn_quit = Button(
            "✕  QUITTER", cx - btn_w//2, MENU_BTN_Y + 80,
            btn_w, btn_h,
            color=(100, 40, 40), hover_color=(170, 60, 60),
            text_color=(255, 200, 200), font=self.font_btn
        )

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
            "speed": random.uniform(0.4, 1.2),
            "drift": random.uniform(-0.3, 0.3),
            "size":  random.randint(3, 7),
            "alpha": random.randint(80, 180),
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
            pygame.draw.circle(s, (120, 220, 100, p["alpha"]),
                               (p["size"], p["size"]), p["size"])
            self.screen.blit(s, (int(p["x"]), int(p["y"])))

    def run(self) -> str:
        while True:
            self.clock.tick(FPS)
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
            overlay.fill((0, 0, 0, 90))
            self.screen.blit(overlay, (0, 0))
            self._update_particles()
            self._draw_particles()
            self.btn_start.draw(self.screen)
            self.btn_quit.draw(self.screen)
            pygame.display.flip()