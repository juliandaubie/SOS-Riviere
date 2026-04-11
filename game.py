import pygame

import music
from constantes import *
from utils import px_to_tile, is_valid_tile
from map import Map
from menu import Palette, UpgradePanel
from tour import DraggableItem
from enemy import Enemy
from renderer import draw_frame, MUTE_BTN_RECT


# Classe principale du jeu : gère la logique complète (vagues, tours, ennemis, UI, événements)
class Game:
    # Initialisation de la classe Game avec écran et horloge Pygame
    # Setup polices, carte, palette, panneau upgrades, listes ennemis/projectiles,
    # variables économie/vies/score, état des vagues
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock  = clock

        self.font       = pygame.font.SysFont("segoeui", 15, bold=True)
        self.font_small = pygame.font.SysFont("segoeui", 11)
        self.font_big   = pygame.font.SysFont("segoeui", 22, bold=True)

        self.game_map      = Map()
        self.palette       = Palette()
        self.upgrade_panel = UpgradePanel()

        self.enemies     = []
        self.projectiles = []

        self.dragging_item   = None
        self.drag_tower_type = None
        self.hovered_tower   = None

        self.message       = ""
        self.message_timer = 0.0

        self.score       = 0
        self.lives       = 20
        self.spawn_timer = WAVE_SPAWN_INTERVAL
        self.game_over   = False
        self.muted       = False
        # ── Économie ─────────────────────────────────────────────────────────
        self.money = STARTING_MONEY
        self.score = 0
        self.lives = 20

        # ── Vagues ───────────────────────────────────────────────────────────
        self.wave_num      = 0        # commence à 0, incrémenté avant le spawn
        self.wave_state    = "break"  # "break" | "spawning" | "waiting"
        self.wave_queue    = []       # liste d'ennemis à spawner
        self.spawn_timer   = 0.0
        self.break_timer   = 3.0     # délai avant la 1ère vague
        self.wave_countdown= 3.0
        self.wave_banner_timer = 0.0

        self.game_over = False

    # ─── Vagues ──────────────────────────────────────────────────────────────

    # Démarre la vague suivante en générant les ennemis et passant en mode spawning
    def _start_next_wave(self):
        self.wave_num  += 1
        self.wave_queue = generate_wave(self.wave_num)
        self.wave_state = "spawning"
        self.spawn_timer = 0.0
        self.wave_banner_timer = 2.5
        self.message = f"🌊 Vague {self.wave_num} — {len(self.wave_queue)} ennemis !"
        self.message_timer = 3000

    # Vérifie si tous les ennemis de la vague sont morts/queue vide
    def _all_dead(self):
        return len(self.enemies) == 0 and len(self.wave_queue) == 0

    # ─── Mise à jour ─────────────────────────────────────────────────────────

    # Met à jour l'état du jeu : hover tiles, drag, messages, vagues, ennemis, tours, projectiles
    def _update(self, dt, mx, my):
        col, row = px_to_tile(mx, my)
        self.game_map.hovered_tile = (col, row) if is_valid_tile(col, row) else None
        self.hovered_tower = self.game_map.get_tower_at_px(mx, my)

        if self.dragging_item:
            self.dragging_item.update(mx, my)

        if self.message_timer > 0:
            self.message_timer -= dt * 1000

        if self.wave_banner_timer > 0:
            self.wave_banner_timer -= dt

        if self.game_over:
            return

        # ── Gestion des vagues ───────────────────────────────────────────────
        if self.wave_state == "break":
            self.break_timer -= dt
            self.wave_countdown = max(0, self.break_timer)
            if self.break_timer <= 0:
                self._start_next_wave()

        elif self.wave_state == "spawning":
            self.spawn_timer -= dt
            if self.spawn_timer <= 0 and self.wave_queue:
                edata = self.wave_queue.pop(0)
                self.enemies.append(Enemy(
                    hp=edata["hp"],
                    speed_mult=edata["speed_mult"],
                    reward=edata["reward"],
                    is_boss=edata.get("is_boss", False),
                ))
                self.spawn_timer = WAVE_SPAWN_INTERVAL
            if not self.wave_queue:
                self.wave_state = "waiting"

        elif self.wave_state == "waiting":
            if self._all_dead():
                self.wave_state  = "break"
                self.break_timer = WAVE_BREAK_DURATION
                self.message = f"✅ Vague {self.wave_num} terminée ! Préparez-vous…"
                self.message_timer = 3000

        # ── Ennemis ──────────────────────────────────────────────────────────
        killed_this_frame = []
        for e in self.enemies:
            e.update(dt)
            if e.reached_end and e.alive:
                self.lives -= 1
                e.alive = False
                self.game_map.add_pollution(0.04)  # eau plus sale
                if self.lives <= 0:
                    self.game_over = True

        for e in self.enemies:
            if not e.alive and e.hp <= 0:
                self.score += e.reward
                self.money += e.reward
                self.game_map.reduce_pollution(0.003)  # on nettoie un peu
                killed_this_frame.append(e)

        self.enemies = [e for e in self.enemies if e.alive]

        # ── Tours ────────────────────────────────────────────────────────────
        for tower in self.game_map.towers:
            tower.update(dt, self.enemies, self.projectiles)

        # ── Projectiles ──────────────────────────────────────────────────────
        for p in self.projectiles:
            p.update(dt, self.enemies)
        self.projectiles = [p for p in self.projectiles if p.alive]

    # ─── Événements ──────────────────────────────────────────────────────────

    # Gère clic gauche : mute, drag tower depuis palette
    def _on_left_press(self, mx, my):
        if MUTE_BTN_RECT.collidepoint(mx, my):
            self.muted = not self.muted
            pygame.mixer.music.set_volume(0.0 if self.muted else MUSIC_VOLUME)
            return
        if self.dragging_item is not None:
            return
        tower_type, _, _ = self.palette.get_tower_at(mx, my)
        if tower_type:
            if self.money < tower_type["cost"]:
                self.message = f"Pas assez d'argent ! (manque {tower_type['cost'] - self.money}$)"
                self.message_timer = 2000
                return
            self.drag_tower_type = tower_type
            self.dragging_item   = DraggableItem(tower_type, mx, my)
            self.dragging_item.start_drag(mx, my)

    # Relâchement gauche : place tour si valide, sinon message erreur
    def _on_left_release(self, mx, my):
        if not self.dragging_item:
            return
        drop_col, drop_row = px_to_tile(mx, my)
        if is_valid_tile(drop_col, drop_row):
            if self.game_map.place_tower(self.drag_tower_type, drop_col, drop_row):
                self.money -= self.drag_tower_type["cost"]
                eco = self.drag_tower_type.get("eco_msg", "")
                self.message = f" {self.drag_tower_type['name']} placé !  {eco}"
            else:
                self.message = "Impossible de placer ici !"
        else:
            self.message = "Hors de la carte"
        self.message_timer = 2500
        self.dragging_item.stop_drag()
        self.dragging_item   = None
        self.drag_tower_type = None

    # Clic droit : upgrade tour ou suppression
    def _on_right_press(self, mx, my):
        # Sur une tour placée : UPGRADE si possible, sinon supprimer
        tower = self.game_map.get_tower_at_px(mx, my)
        if tower:
            if tower.can_upgrade():
                cost = tower.upgrade_cost()
                if self.money >= cost:
                    self.money -= cost
                    tower.do_upgrade()
                    stars = "★" * tower.upgrade_level
                    self.message = f"⬆{tower.tower_type['name']} amélioré ! {stars}"
                    self.message_timer = 2000
                else:
                    self.message = f"Manque {cost - self.money}$ pour l'upgrade"
                    self.message_timer = 2000
            else:
                self.message = f"{tower.tower_type['name']} est déjà au niveau MAX"
                self.message_timer = 2000
        else:
            # Rien sous le curseur : supprimer si on clique sur une tour
            col, row = px_to_tile(mx, my)
            before = len(self.game_map.towers)
            self.game_map.towers = [t for t in self.game_map.towers
                                     if not (t.col == col and t.row == row)]
            if len(self.game_map.towers) < before:
                self.message = f"Tour supprimée"
                self.message_timer = 1500

    # Traite tous les événements Pygame (quit, ESC, clics)
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

    # Boucle principale du jeu : events, update, render jusqu'à changement d'état
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
                money=self.money,
                wave_num=self.wave_num,
                wave_state=self.wave_state,
                wave_countdown=self.wave_countdown,
                pollution=self.game_map.pollution,
                hovered_tower=self.hovered_tower,
                upgrade_panel=self.upgrade_panel,
                game_over=self.game_over,
                wave_banner_timer=self.wave_banner_timer,
                muted=self.muted,
            )

