import pygame
from constantes import *
from utils import px_to_tile, is_valid_tile


def draw_background(screen):
    screen.fill(BG_COLOR)


def draw_header(screen, font_big, font_small, score=0, lives=20):
    pygame.draw.rect(screen, HEADER_COLOR, (0, 0, SCREEN_W, 50))

    title = font_big.render("🌿  ECO TOWER DEFENSE", True, (160, 230, 130))
    screen.blit(title, (20, 12))

    score_surf = pygame.font.SysFont("segoeui", 15, bold=True).render(
        f"⭐ Score: {score}   ❤️ Vies: {lives}", True, (220, 220, 100)
    )
    screen.blit(score_surf, (400, 15))

    hint = font_small.render(
        "Survole une tour = range  •  Clic droit = supprimer  •  ESC = menu",
        True, (100, 160, 90)
    )
    screen.blit(hint, (SCREEN_W - hint.get_width() - 15, 17))


def draw_drag_item(screen, font, dragging_item, mx, my):
    dragging_item.draw(screen)
    tc, tr = px_to_tile(mx, my)
    if is_valid_tile(tc, tr):
        coord = font.render(f"({tc}, {tr})", True, (220, 255, 180))
        screen.blit(coord, (mx + 18, my - 10))


def draw_feedback_message(screen, font, message, message_timer):
    if message_timer <= 0:
        return
    msg_surf = font.render(message, True, (220, 255, 180))
    bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10), pygame.SRCALPHA)
    pygame.draw.rect(bg, (20, 60, 25, 200), bg.get_rect(), border_radius=6)
    screen.blit(bg,       (20, SCREEN_H - 45))
    screen.blit(msg_surf, (30, SCREEN_H - 40))


def draw_tile_info(screen, font_small, game_map):
    if not game_map.hovered_tile:
        return
    hc, hr = game_map.hovered_tile
    info = f"Tile ({hc}, {hr})"
    if (hc, hr) in PATH_SET:
        info += "  —  🚧 Chemin (non plaçable)"
    elif any(t.col == hc and t.row == hr for t in game_map.towers):
        tower = next(t for t in game_map.towers if t.col == hc and t.row == hr)
        info += f"  —  {tower.tower_type['name']} (clic droit pour supprimer)"
    else:
        info += "  —  ✅ Disponible"
    surf = font_small.render(info, True, (180, 230, 160))
    screen.blit(surf, (MAP_X, MAP_Y + ROWS * TILE_SIZE + 10))


def draw_game_over(screen, font_big):
    go = font_big.render("💀 GAME OVER — Appuie sur ESC", True, (255, 80, 80))
    screen.blit(go, (SCREEN_W//2 - go.get_width()//2, SCREEN_H//2 - 20))


def draw_frame(screen, font, font_small, font_big,
               game_map, palette,
               dragging_item,
               message, message_timer,
               mx, my,
               enemies=None, projectiles=None,
               score=0, lives=20,
               hovered_tower=None,
               game_over=False):

    draw_background(screen)
    draw_header(screen, font_big, font_small, score, lives)

    # Carte (avec range de la tour survolée)
    game_map.draw(screen, font_small, hovered_tower=hovered_tower)

    palette.draw(screen, font, font_small)

    # Projectiles
    if projectiles:
        for p in projectiles:
            p.draw(screen)

    # Ennemis
    if enemies:
        for e in enemies:
            e.draw(screen)

    if dragging_item:
        draw_drag_item(screen, font, dragging_item, mx, my)

    draw_feedback_message(screen, font, message, message_timer)
    draw_tile_info(screen, font_small, game_map)

    if game_over:
        draw_game_over(screen, font_big)

    pygame.display.flip()