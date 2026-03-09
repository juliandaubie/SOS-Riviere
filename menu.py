import pygame
from constantes import *
from utils import draw_tower_icon

class Palette:
    """Panneau latéral avec les tours draggables."""
    PANEL_X = MAP_X + COLS * TILE_SIZE + 20
    PANEL_W = 180
    ITEM_H = 90

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
        # Fond panneau
        panel_rect = pygame.Rect(self.PANEL_X - 10, MAP_Y - 10,
                                 self.PANEL_W + 20, ROWS * TILE_SIZE + 20)
        pygame.draw.rect(surface, (20, 45, 25), panel_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 140, 60), panel_rect, 2, border_radius=10)

        title = font.render("TOURS", True, (180, 240, 140))
        surface.blit(title, (self.PANEL_X + 40, MAP_Y - 5))

        for i, (tower, rect) in enumerate(zip(TOWER_TYPES, self.items_rects)):
            # Fond item
            pygame.draw.rect(surface, tower["color"], rect, border_radius=8)
            overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 60), (0, 0, rect.w, rect.h), border_radius=8)
            surface.blit(overlay, rect.topleft)
            pygame.draw.rect(surface, (200, 240, 180), rect, 1, border_radius=8)

            # Icône
            draw_tower_icon(surface, tower, rect.x + 30, rect.centery - 5)

            # Texte
            name_surf = font.render(tower["name"], True, (240, 255, 220))
            surface.blit(name_surf, (rect.x + 60, rect.y + 8))
            cost_surf = font_small.render(f"💰 {tower['cost']}$", True, (255, 220, 80))
            surface.blit(cost_surf, (rect.x + 60, rect.y + 28))
            desc_surf = font_small.render(tower["desc"], True, (180, 220, 160))
            surface.blit(desc_surf, (rect.x + 10, rect.y + 65))

        # Légende
        leg_y = MAP_Y + len(TOWER_TYPES) * self.ITEM_H + 10
        pygame.draw.circle(surface, (50, 220, 50), (self.PANEL_X + 12, leg_y), 8)
        surface.blit(font_small.render("Départ", True, TEXT_COLOR), (self.PANEL_X + 25, leg_y - 7))
        pygame.draw.circle(surface, (220, 50, 50), (self.PANEL_X + 12, leg_y + 22), 8)
        surface.blit(font_small.render("Arrivée", True, TEXT_COLOR), (self.PANEL_X + 25, leg_y + 15))

