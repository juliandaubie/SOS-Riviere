import os

"""
Module constantes.py : Toutes les configurations du jeu SOS-Riviere
Définit dimensions écran, couleurs, chemin ennemis, système vagues, tours (5 types + upgrades),
argent initial, états, chemins assets.
"""

# ─── CONFIG ───────────────────────────────────────────────────────────────────
# Dimensions écran, taille tiles, grille carte, FPS
SCREEN_W, SCREEN_H = 1200, 750
TILE_SIZE = 60
COLS = 14
ROWS = 10
MAP_X = 20
MAP_Y = 70
FPS = 60

# ─── COULEURS ─────────────────────────────────────────────────────────────────
# Palette couleurs pour fond, herbe, chemin, grille, textes, effets
BG_COLOR          = (8, 18, 12)
GRASS_COLOR       = (45, 100, 50)
GRASS_DARK        = (35, 80, 40)
PATH_COLOR        = (160, 130, 70)
PATH_DARK         = (140, 110, 55)
GRID_COLOR        = (20, 60, 25)
COORD_COLOR       = (120, 200, 100)
HEADER_COLOR      = (6, 18, 10)
TEXT_COLOR        = (200, 240, 180)
HIGHLIGHT         = (100, 220, 100, 80)
SHADOW_COLOR      = (0, 0, 0, 120)
TOWER_ZONE_COLOR  = (60, 130, 60)
TOWER_ZONE_BORDER = (80, 180, 80)
PANEL_BG          = (10, 28, 15)

# ─── CHEMIN DU MONSTRE ───────────────────────────────────────────────────────
# Coordonnées tiles du chemin que suivent les ennemis (pollution)
ENEMY_PATH = [
    (0, 4), (1, 4), (2, 4), (3, 4),
    (3, 3), (3, 2), (4, 2), (5, 2),
    (5, 3), (5, 4), (5, 5), (5, 6),
    (6, 6), (7, 6), (8, 6),
    (8, 5), (8, 4), (8, 3), (8, 2),
    (9, 2), (10, 2), (11, 2),
    (11, 3), (11, 4), (11, 5), (11, 6), (11, 7),
    (12, 7), (13, 7),
]
PATH_SET = set(ENEMY_PATH)  # Pour vérifications rapides

# ─── SYSTEME DE VAGUES ────────────────────────────────────────────────────────
# Intervalles spawn et pause entre vagues
WAVE_SPAWN_INTERVAL = 2   # secondes entre chaque ennemi dans une vague
WAVE_BREAK_DURATION = 8.0   # secondes entre les vagues

# Génère liste d'ennemis pour une vague (hp, speed, reward croissants)
# Ajoute boss tous les 5 vagues
def generate_wave(wave_num):
    """
    Génère les ennemis d'une vague basée sur le numéro de vague.
    
    Args:
        wave_num (int): Numéro de vague (1+)
    
    Returns:
        list[dict]: Liste d'ennemis {"hp": int, "speed_mult": float, "reward": int, "is_boss": bool?}
    """
    enemies = []
    count = 5 + wave_num * 2
    hp = int(80 * (1.3 ** (wave_num - 1)))
    speed = 1.0 + wave_num * 0.05
    reward = 10 + wave_num * 2
    for _ in range(count):
        enemies.append({"hp": hp, "speed_mult": speed, "reward": reward})
    # Boss tous les 5 vagues (x5 hp, x0.7 speed, x5 reward)
    if wave_num % 5 == 0:
        enemies.append({"hp": hp * 5, "speed_mult": speed * 0.7, "reward": reward * 5, "is_boss": True})
    return enemies

# ─── ARGENT ──────────────────────────────────────────────────────────────────
STARTING_MONEY = 200  # Argent de départ pour acheter tours

# ─── TOURS ───────────────────────────────────────────────────────────────────
# Liste de 5 types de tours écologiques avec stats, upgrades (3 niveaux chacun)
# Clés: name, emoji/color/cost/desc/eco_msg, range_tiles, damage, fire_rate, slow/aoe, proj_color, image, upgrades[list dict]
TOWER_TYPES = [
    {
        "name": "Arbre",    "emoji": "",
        "color": (34, 120, 34),  "cost": 50,
        "desc": "Ralentit les ennemis",
        "eco_msg": "Les arbres absorbent le CO₂ !",
        "range_tiles": 2.5, "damage": 8,  "fire_rate": 1.0,
        "slow": 0.45,       "aoe": 0,
        "proj_color": (100, 220, 80),
        "image": os.path.join("assets", "arbre.png"),
        "upgrades": [
            {"cost": 40,  "damage_bonus": 4,  "range_bonus": 0.3, "fire_rate_bonus": 0.0, "slow_bonus": -0.05, "desc": "Racines renforcées"},
            {"cost": 80,  "damage_bonus": 8,  "range_bonus": 0.5, "fire_rate_bonus": 0.2, "slow_bonus": -0.05, "desc": "Forêt dense"},
            {"cost": 150, "damage_bonus": 15, "range_bonus": 0.7, "fire_rate_bonus": 0.3, "slow_bonus": -0.10, "desc": "Arbre millénaire"},
        ]
    },
    {
        "name": "Solaire",  "emoji": "☀",
        "color": (220, 180, 0),  "cost": 100,
        "desc": "Dégâts zone",
        "eco_msg": "L'énergie solaire, propre et infinie !",
        "range_tiles": 3.0, "damage": 20, "fire_rate": 0.6,
        "slow": 1.0,        "aoe": 55,
        "proj_color": (255, 220, 50),
        "image": os.path.join("assets", "solaire.png"),
        "upgrades": [
            {"cost": 60,  "damage_bonus": 10, "range_bonus": 0.3, "fire_rate_bonus": 0.1, "slow_bonus": 0.0, "desc": "Panneaux améliorés"},
            {"cost": 120, "damage_bonus": 20, "range_bonus": 0.5, "fire_rate_bonus": 0.2, "slow_bonus": 0.0, "desc": "Ferme solaire"},
            {"cost": 200, "damage_bonus": 40, "range_bonus": 0.8, "fire_rate_bonus": 0.3, "slow_bonus": 0.0, "desc": "Supernova éclair"},
        ]
    },
    {
        "name": "Éolienne", "emoji": "",
        "color": (80, 160, 220), "cost": 80,
        "desc": "Tir rapide",
        "eco_msg": "Le vent, une énergie inépuisable !",
        "range_tiles": 2.0, "damage": 8,  "fire_rate": 2.5,
        "slow": 1.0,        "aoe": 0,
        "proj_color": (180, 230, 255),
        "image": os.path.join("assets", "eolienne.png"),
        "upgrades": [
            {"cost": 50,  "damage_bonus": 4,  "range_bonus": 0.2, "fire_rate_bonus": 0.5, "slow_bonus": 0.0, "desc": "Rotors optimisés"},
            {"cost": 100, "damage_bonus": 8,  "range_bonus": 0.4, "fire_rate_bonus": 1.0, "slow_bonus": 0.0, "desc": "Turbine ultra"},
            {"cost": 180, "damage_bonus": 16, "range_bonus": 0.6, "fire_rate_bonus": 2.0, "slow_bonus": 0.0, "desc": "Tempête déchaînée"},
        ]
    },
    {
        "name": "Compost",  "emoji": "",
        "color": (100, 160, 50), "cost": 60,
        "desc": "Affaiblit ennemis",
        "eco_msg": "Le compost enrichit les sols.",
        "range_tiles": 2.0, "damage": 10, "fire_rate": 0.8,
        "slow": 0.65,       "aoe": 0,
        "proj_color": (180, 255, 100),
        "image": os.path.join("assets", "compost.png"),
        "upgrades": [
            {"cost": 40,  "damage_bonus": 5,  "range_bonus": 0.3, "fire_rate_bonus": 0.2, "slow_bonus": -0.05, "desc": "Bio-accélérateur"},
            {"cost": 80,  "damage_bonus": 10, "range_bonus": 0.5, "fire_rate_bonus": 0.3, "slow_bonus": -0.10, "desc": "Toxines naturelles"},
            {"cost": 140, "damage_bonus": 20, "range_bonus": 0.7, "fire_rate_bonus": 0.5, "slow_bonus": -0.15, "desc": "Mycélium ravageur"},
        ]
    },
    {
        "name": "Barrage",  "emoji": "",
        "color": (40, 100, 200), "cost": 120,
        "desc": "Haute portée",
        "eco_msg": "L'eau dans 20~30 ans il n'y en aura plus.",
        "range_tiles": 4.5, "damage": 15, "fire_rate": 0.9,
        "slow": 0.75,       "aoe": 0,
        "proj_color": (100, 180, 255),
        "image": os.path.join("assets", "barrage.png"),
        "upgrades": [
            {"cost": 70,  "damage_bonus": 8,  "range_bonus": 0.5, "fire_rate_bonus": 0.2, "slow_bonus": -0.05, "desc": "Turbines renforcées"},
            {"cost": 140, "damage_bonus": 16, "range_bonus": 1.0, "fire_rate_bonus": 0.4, "slow_bonus": -0.10, "desc": "Grand barrage"},
            {"cost": 240, "damage_bonus": 30, "range_bonus": 1.5, "fire_rate_bonus": 0.6, "slow_bonus": -0.15, "desc": "Déluge libéré"},
        ]
    },
]

# ─── ÉTATS ───────────────────────────────────────────────────────────────────
STATE_MENU    = "menu"
STATE_PLAYING = "playing"
STATE_QUIT    = "quit"

# ─── ASSETS ──────────────────────────────────────────────────────────────────
# Chemins images/musiques (relatifs à assets/)
BG_IMAGE_PATH     = os.path.join("assets", "sos_riviere.png")
MUSIC_MENU_PATH   = os.path.join("assets", "musique_menu.mp3")
MUSIC_JEU_PATH    = os.path.join("assets", "musique_jeu.mp3")
MUSIC_VOLUME      = 0.15
MAP_BG_IMAGE_PATH = os.path.join("assets", "map_bg.png")
ENEMY_IMAGE_PATH  = os.path.join("assets", "dechet.png")
MENU_BTN_Y        = SCREEN_H // 2 + 160

# Types de trajectoires projectiles
TRAJ_LINEAR = "linear"
TRAJ_PARABOLIC = "parabolic"
TRAJ_LOBBED = "lobbed"
TRAJ_WAVE = "wave"

