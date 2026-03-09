import pygame

import music
from constantes import *
from utils import px_to_tile, is_valid_tile
from map import Map
from menu import Palette
from tour import DraggableItem
from enemy import Enemy
from renderer import draw_frame

SPAWN_INTERVAL = 3.0


class Game:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock  = clock

        self.font       = pygame.font.SysFont("segoeui", 15, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 11)
        self.font_big   = pygame.font.SysFont("segoeui", 22, bold=True)

        self.game_map = Map()
        self.palette  = Palette()

        self.enemies     = []
        self.projectiles = []

        self.dragging_item   = None
        self.drag_tower_type = None
        self.hovered_tower   = None

        self.message       = ""
        self.message_timer = 0

        self.score       = 0
        self.lives       = 20
        self.spawn_timer = SPAWN_INTERVAL
        self.game_over   = False

    # ── Mise à jour ───────────────────────────────────────────────────────────

    def _update(self, dt, mx, my):
        col, row = px_to_tile(mx, my)
        self.game_map.hovered_tile = (col, row) if is_valid_tile(col, row) else None

        # Tour survolée → affiche sa range
        self.hovered_tower = self.game_map.get_tower_at_px(mx, my)

        if self.dragging_item:
            self.dragging_item.update(mx, my)

        if self.message_timer > 0:
            self.message_timer -= dt * 1000

        if self.game_over:
            return

        # Spawn
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.enemies.append(Enemy(hp=100))
            self.spawn_timer = SPAWN_INTERVAL

        # Mise à jour ennemis
        for e in self.enemies:
            e.update(dt)
            if e.reached_end and e.alive:
                self.lives -= 1
                e.alive = False
                if self.lives <= 0:
                    self.game_over = True

        for e in self.enemies:
            if not e.alive and e.hp <= 0:
                self.score += 10
        self.enemies = [e for e in self.enemies if e.alive]

        # Tours attaquent
        for tower in self.game_map.towers:
            tower.update(dt, self.enemies, self.projectiles)

        # Projectiles
        for p in self.projectiles:
            p.update(dt, self.enemies)
        self.projectiles = [p for p in self.projectiles if p.alive]

    # ── Événements ───────────────────────────────────────────────────────────

    def _on_left_press(self, mx, my):
        if self.dragging_item is not None:
            return
        tower_type, _, _ = self.palette.get_tower_at(mx, my)
        if tower_type:
            self.drag_tower_type = tower_type
            self.dragging_item   = DraggableItem(tower_type, mx, my)
            self.dragging_item.start_drag(mx, my)

    def _on_left_release(self, mx, my):
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
        col, row = px_to_tile(mx, my)
        before = len(self.game_map.towers)
        self.game_map.towers = [t for t in self.game_map.towers
                                 if not (t.col == col and t.row == row)]
        if len(self.game_map.towers) < before:
            self.message       = f"🗑️ Tour supprimée en ({col},{row})"
            self.message_timer = 2000

    def _handle_events(self):
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

    # ── Boucle ───────────────────────────────────────────────────────────────

    def run(self) -> str:
        music.play('jeu')
        while True:
            dt     = self.clock.tick(FPS) / 1000.0
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
                enemies=self.enemies,
                projectiles=self.projectiles,
                score=self.score,
                lives=self.lives,
                hovered_tower=self.hovered_tower,
                game_over=self.game_over,
            )