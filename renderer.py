import pygame
from constantes import *
from utils import px_to_tile, is_valid_tile


# Rect bouton mute audio (coin haut droit)
MUTE_BTN_RECT = pygame.Rect(SCREEN_W - 54, 8, 36, 34)

# En-tête HUD : score/vies/argent/vague/pollution/hint + bouton mute
def draw_header(screen, font_big, font_small, score=0, lives=20,money=0, wave_num=1,wave_state="playing",wave_countdown=0,pollution=0.0, muted=False):
    pygame.draw.rect(screen, HEADER_COLOR, (0, 0, SCREEN_W, 50))
    font15 = pygame.font.SysFont("segoeui",15,bold=True)
    font12 = pygame.font.SysFont("segoeui",15)

    # Score & Vies
    score_surf = font15.render(f"score : {score}", True, (240, 220, 80))
    screen.blit(score_surf, (300, 8))

    lives_c = (80, 220, 80) if lives > 10 else (220, 140, 40) if lives > 5 else (220, 60, 60)
    lives_surf = font15.render(f"vies : {lives}", True, lives_c)
    screen.blit(lives_surf, (300, 26))

    # Argent
    money_surf = font15.render(f"{money}$", True, (255, 210, 50))
    screen.blit(money_surf, (420, 8))

    # Vague
    if wave_state == "break":
        wave_txt = f"Prochaine vague dans {wave_countdown:.0f}s"
        wc = (200, 240, 140)
    else:
        wave_txt = f"Vague {wave_num}"
        wc = (100, 200, 255)
    wave_surf = font15.render(wave_txt, True, wc)
    screen.blit(wave_surf, (420, 26))

    # Jauge pollution
    pol_x = 620
    pol_w = 200
    pol_h = 14
    pol_y = 12
    hint = font_small.render(
        "Survole une tour = range  •  Clic droit = supprimer  •  ESC = menu",
        True, (100, 160, 90)
    )
    screen.blit(hint, (SCREEN_W - hint.get_width() - 15 - 50, 17))

    # ── Bouton muet ──────────────────────────────────────────────────────────
    hovered = MUTE_BTN_RECT.collidepoint(pygame.mouse.get_pos())
    btn_col = (80, 50, 50) if muted else ((60, 110, 65) if not hovered else (80, 150, 85))
    pygame.draw.rect(screen, btn_col, MUTE_BTN_RECT, border_radius=8)
    border_col = (200, 80, 80) if muted else (100, 200, 110)
    pygame.draw.rect(screen, border_col, MUTE_BTN_RECT, 2, border_radius=8)
    cx, cy = MUTE_BTN_RECT.center
    # Corps du haut-parleur
    pygame.draw.polygon(screen, (255, 255, 255), [
        (cx - 9, cy - 4), (cx - 4, cy - 4),
        (cx + 2, cy - 9), (cx + 2, cy + 9),
        (cx - 4, cy + 4), (cx - 9, cy + 4),
    ])
    if not muted:
        # Ondes sonores
        pygame.draw.arc(screen, (255, 255, 255),
                        (cx + 3, cy - 6, 8, 12), -0.6, 0.6, 2)
        pygame.draw.arc(screen, (255, 255, 255),
                        (cx + 6, cy - 10, 12, 20), -0.6, 0.6, 2)
    else:
        pygame.draw.line(screen, (255, 60, 60), (cx - 8, cy - 8), (cx + 8, cy + 8), 3)
        pygame.draw.line(screen, (255, 60, 60), (cx + 8, cy - 8), (cx - 8, cy + 8), 3)


    pygame.draw.rect(screen, (30, 50, 35), (pol_x, pol_y, pol_w, pol_h), border_radius=6)
    fill_w = int(pol_w * pollution)
    if fill_w > 0:
        r = int(30  + pollution * 180)
        g = int(140 - pollution * 120)
        b = int(200 - pollution * 180)
        pygame.draw.rect(screen, (r, g, b), (pol_x, pol_y, fill_w, pol_h), border_radius=6)
    pygame.draw.rect(screen, (80, 160, 80), (pol_x, pol_y, pol_w, pol_h), 1, border_radius=6)

    pol_label = font12.render(f"Pollution {int(pollution*100)}%", True, (180, 230, 180))
    screen.blit(pol_label, (pol_x, pol_y + pol_h + 2))

# Message feedback temporaire (placement, argent etc.)
def draw_feedback_message(screen, font, message, message_timer):
    if message_timer <= 0:
        return
    alpha = min(255, int(message_timer / 2500 * 255 + 80))
    msg_surf = font.render(message, True, (220, 255, 180))
    bg = pygame.Surface((msg_surf.get_width() + 22, msg_surf.get_height() + 12), pygame.SRCALPHA)
    pygame.draw.rect(bg, (12, 40, 18, 210), bg.get_rect(), border_radius=8)
    screen.blit(bg,       (18, SCREEN_H - 48))
    screen.blit(msg_surf, (29, SCREEN_H - 42))

# Overlay game over avec score/vague/pollution + message éco + hint ESC
def draw_game_over(screen, font_big, score, wave_num, pollution):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    screen.blit(ov, (0, 0))

    font36 = pygame.font.SysFont("segoeui", 36, bold=True)
    font22 = pygame.font.SysFont("segoeui", 22)
    font16 = pygame.font.SysFont("segoeui", 16)

    cx, cy = SCREEN_W // 2, SCREEN_H // 2 - 80

    go = font36.render("RIVIÈRE POLLUÉE — GAME OVER", True, (255, 80, 60))
    screen.blit(go, go.get_rect(center=(cx, cy)))

    s1 = font22.render(f"Score final : {score}  |  Vague atteinte : {wave_num}", True, (220, 240, 180))
    screen.blit(s1, s1.get_rect(center=(cx, cy + 55)))

    pol_msg = "Continuez à protéger nos rivières dans la vraie vie !" \
              if pollution > 0.5 else "Bravo pour vos efforts écologiques !"
    s2 = font16.render(pol_msg, True, (160, 240, 160))
    screen.blit(s2, s2.get_rect(center=(cx, cy + 90)))

    hint = font16.render("Appuyez sur ESC pour revenir au menu", True, (180, 180, 180))
    screen.blit(hint, hint.get_rect(center=(cx, cy + 130)))

# Bannière flash début vague
def draw_wave_banner(screen, font_big, wave_num):
    """Bannière flash au début de chaque vague."""
    font30 = pygame.font.SysFont("segoeui", 30, bold=True)
    bg = pygame.Surface((400, 50), pygame.SRCALPHA)
    pygame.draw.rect(bg, (10, 80, 20, 200), (0, 0, 400, 50), border_radius=10)
    screen.blit(bg, (SCREEN_W//2 - 200, SCREEN_H//2 - 25))
    txt = font30.render(f"VAGUE {wave_num}  —  EN ROUTE !", True, (140, 255, 160))
    screen.blit(txt, txt.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))

# Frame complète : header + map + palette + proj/ennemis + UI + over
def draw_frame(screen, font, font_small, font_big,
               game_map, palette,
               dragging_item,
               message, message_timer,
               mx, my,
               enemies=None, projectiles=None,
               score=0, lives=20, money=0,
               wave_num=1, wave_state="playing", wave_countdown=0,
               pollution=0.0,
               hovered_tower=None,
               upgrade_panel=None,
               game_over=False,
               wave_banner_timer=0,
               muted=False):
    screen.fill(BG_COLOR)

    draw_header(screen, font_big, font_small, score, lives, money,
                wave_num, wave_state, wave_countdown, pollution,muted)

    game_map.draw(screen, font_small, hovered_tower=hovered_tower,
                  dragging_item=dragging_item)

    palette.draw(screen, font, font_small, money=money)

    if projectiles:
        for p in projectiles:
            p.draw(screen)

    # Ennemis
    if enemies:
        for e in enemies:
            e.draw(screen)

    if dragging_item:
        dragging_item.draw(screen)
        tc, tr = px_to_tile(mx, my)
        if is_valid_tile(tc, tr):
            coord = font.render(f"({tc}, {tr})", True, (220, 255, 180))
            screen.blit(coord, (mx + 18, my - 10))

    # Panel upgrade (hover sur tour)
    if upgrade_panel and hovered_tower:
        upgrade_panel.draw(screen, hovered_tower, mx, my, font, font_small, money)

    draw_feedback_message(screen, font, message, message_timer)

    if wave_banner_timer > 0:
        draw_wave_banner(screen, font_big, wave_num)

    if game_over:
        draw_game_over(screen, font_big, score, wave_num, pollution)

    pygame.display.flip()

