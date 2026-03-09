import pygame
from constantes import *
from map import Map, px_to_tile, is_valid_tile
from menu import Palette
from tour import  DraggableItem
from renderer import draw_frame


class Game:
    """Encapsule l'état et la boucle de jeu."""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock  = clock

        # Polices
        self.font       = pygame.font.SysFont("segoeui", 15, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 11)
        self.font_big   = pygame.font.SysFont("segoeui", 22, bold=True)

        # Objets de jeu
        self.game_map = Map()
        self.palette  = Palette()

        # État du drag & drop
        self.dragging_item   = None
        self.drag_tower_type = None

        # Feedback utilisateur
        self.message       = ""
        self.message_timer = 0

    # ── Mise à jour ───────────────────────────────────────────────────────────

    def _update(self, dt, mx, my):
        col, row = px_to_tile(mx, my)
        self.game_map.hovered_tile = (col, row) if is_valid_tile(col, row) else None

        if self.dragging_item:
            self.dragging_item.update(mx, my)

        if self.message_timer > 0:
            self.message_timer -= dt

    # ── Gestion des événements ────────────────────────────────────────────────

    def _on_left_press(self, mx, my):
        """Début d'un drag depuis la palette."""
        if self.dragging_item is not None:
            return
        tower_type, _, _ = self.palette.get_tower_at(mx, my)
        if tower_type:
            self.drag_tower_type = tower_type
            self.dragging_item   = DraggableItem(tower_type, mx, my)
            self.dragging_item.start_drag(mx, my)

    def _on_left_release(self, mx, my):
        """Dépôt d'une tour sur la carte."""
        if not self.dragging_item:
            return
        drop_col, drop_row = px_to_tile(mx, my)
        if is_valid_tile(drop_col, drop_row):
            if self.game_map.place_tower(self.drag_tower_type, drop_col, drop_row):
                self.message = f"✅ {self.drag_tower_type['name']} placé en ({drop_col},{drop_row})"
            else:
                self.message = "❌ Impossible de placer ici !"
        else:
            self.message = "❌ Hors de la carte"

        self.message_timer = 2500
        self.dragging_item.stop_drag()
        self.dragging_item   = None
        self.drag_tower_type = None

    def _on_right_press(self, mx, my):
        """Suppression d'une tour au clic droit."""
        col, row = px_to_tile(mx, my)
        before = len(self.game_map.towers)
        self.game_map.towers = [
            t for t in self.game_map.towers
            if not (t.col == col and t.row == row)
        ]
        if len(self.game_map.towers) < before:
            self.message       = f"🗑️ Tour supprimée en ({col},{row})"
            self.message_timer = 2000

    def _handle_events(self) -> str | None:
        """
        Traite tous les événements Pygame.
        Retourne un état (STATE_*) si une transition est demandée, sinon None.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return STATE_QUIT

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return STATE_MENU

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    self._on_left_press(mx, my)
                elif event.button == 3:
                    self._on_right_press(mx, my)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._on_left_release(*event.pos)

        return None

    # ── Boucle principale ─────────────────────────────────────────────────────

    def run(self) -> str:
        """Lance la boucle de jeu. Retourne l'état suivant (STATE_MENU ou STATE_QUIT)."""
        while True:
            dt    = self.clock.tick(FPS)
            mx, my = pygame.mouse.get_pos()

            next_state = self._handle_events()
            if next_state:
                return next_state

            self._update(dt, mx, my)

            draw_frame(
                self.screen,
                self.font, self.font_small, self.font_big,
                self.game_map, self.palette,
                self.dragging_item,
                self.message, self.message_timer,
                mx, my,
            )