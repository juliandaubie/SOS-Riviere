import pygame
import sys
from menu import *
from tour import *
from map import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("🌿 Eco Tower Defense — Carte de base")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("segoeui", 15, bold=True)
    font_small = pygame.font.SysFont("segoeui", 11)
    font_big = pygame.font.SysFont("segoeui", 22, bold=True)

    game_map = Map()
    palette = Palette()

    dragging_item = None
    drag_tower_type = None

    message = ""
    message_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        # Mise à jour hover tile
        col, row = px_to_tile(mx, my)
        if is_valid_tile(col, row):
            game_map.hovered_tile = (col, row)
        else:
            game_map.hovered_tile = None

        # Mise à jour drag
        if dragging_item:
            dragging_item.update(mx, my)

        # Timer message
        if message_timer > 0:
            message_timer -= dt

        # ── EVENTS ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dragging_item is None:
                    tower_type, tx, ty = palette.get_tower_at(mx, my)
                    if tower_type:
                        drag_tower_type = tower_type
                        dragging_item = DraggableItem(tower_type, mx, my)
                        dragging_item.start_drag(mx, my)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_item:
                    # Essayer de poser la tour sur la carte
                    drop_col, drop_row = px_to_tile(mx, my)
                    if is_valid_tile(drop_col, drop_row):
                        if game_map.place_tower(drag_tower_type, drop_col, drop_row):
                            message = f"✅ {drag_tower_type['name']} placé en ({drop_col},{drop_row})"
                        else:
                            message = f"❌ Impossible de placer ici !"
                    else:
                        message = "❌ Hors de la carte"
                    message_timer = 2500
                    dragging_item.stop_drag()
                    dragging_item = None
                    drag_tower_type = None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                # Clic droit : supprimer une tour
                col, row = px_to_tile(mx, my)
                before = len(game_map.towers)
                game_map.towers = [t for t in game_map.towers
                                   if not (t.col == col and t.row == row)]
                if len(game_map.towers) < before:
                    message = f"🗑️ Tour supprimée en ({col},{row})"
                    message_timer = 2000

        # ── DESSIN ──────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # Header
        pygame.draw.rect(screen, HEADER_COLOR, (0, 0, SCREEN_W, 50))
        title_surf = font_big.render("🌿  ECO TOWER DEFENSE  —  Carte de base", True, (160, 230, 130))
        screen.blit(title_surf, (20, 12))
        hint = font_small.render("Glissez une tour sur la carte  •  Clic droit = supprimer  •  ESC = quitter", True, (100, 160, 90))
        screen.blit(hint, (SCREEN_W - hint.get_width() - 15, 17))

        # Carte
        game_map.draw(screen, font_small)

        # Palette
        palette.draw(screen, font, font_small)

        # Item en cours de drag (dessiné au-dessus de tout)
        if dragging_item:
            dragging_item.draw(screen)
            # Afficher les coordonnées de la tile cible
            tc, tr = px_to_tile(mx, my)
            if is_valid_tile(tc, tr):
                coord_hint = font.render(f"({tc}, {tr})", True, (220, 255, 180))
                screen.blit(coord_hint, (mx + 18, my - 10))

        # Message feedback
        if message_timer > 0:
            alpha = min(255, message_timer)
            msg_surf = font.render(message, True, (220, 255, 180))
            bg_msg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(bg_msg, (20, 60, 25, 200), bg_msg.get_rect(), border_radius=6)
            screen.blit(bg_msg, (20, SCREEN_H - 45))
            screen.blit(msg_surf, (30, SCREEN_H - 40))

        # Info tile hovered
        if game_map.hovered_tile:
            hc, hr = game_map.hovered_tile
            info = f"Tile ({hc}, {hr})"
            if (hc, hr) in PATH_SET:
                info += "  —  🚧 Chemin (non plaçable)"
            elif any(t.col == hc and t.row == hr for t in game_map.towers):
                t = next(t for t in game_map.towers if t.col == hc and t.row == hr)
                info += f"  —  {t.tower_type['name']} (clic droit pour supprimer)"
            else:
                info += "  —  ✅ Disponible"
            info_surf = font_small.render(info, True, (180, 230, 160))
            screen.blit(info_surf, (MAP_X, MAP_Y + ROWS * TILE_SIZE + 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()