# ─── CONFIG ───────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 700
TILE_SIZE = 60
COLS = 14
ROWS = 10
MAP_X = 20
MAP_Y = 60
FPS = 60

# ─── COULEURS ÉCOLOGIE ────────────────────────────────────────────────────────
BG_COLOR         = (15, 30, 20)
GRASS_COLOR      = (45, 100, 50)
GRASS_DARK       = (35, 80, 40)
PATH_COLOR       = (180, 140, 80)
PATH_DARK        = (160, 120, 60)
GRID_COLOR       = (20, 60, 25)
COORD_COLOR      = (120, 200, 100)
HEADER_COLOR     = (10, 25, 15)
TEXT_COLOR       = (200, 240, 180)
HIGHLIGHT        = (100, 220, 100, 80)
SHADOW_COLOR     = (0, 0, 0, 120)
TOWER_ZONE_COLOR  = (60, 130, 60)
TOWER_ZONE_BORDER = (80, 180, 80)

# ─── CHEMIN DU MONSTRE ───────────────────────────────────────────────────────
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

PATH_SET = set(ENEMY_PATH)

# ─── TOURS DISPONIBLES ───────────────────────────────────────────────────────
# range_tiles : rayon d'attaque en tiles
# damage      : dégâts par tir
# fire_rate   : tirs par seconde
# slow        : facteur de ralentissement (1.0 = aucun, 0.5 = vitesse /2)
# aoe         : rayon de zone en pixels (0 = pas d'AoE)
# proj_color  : couleur du projectile
TOWER_TYPES = [
    {
        "name": "Arbre",    "emoji": "🌳",
        "color": (34, 120, 34),  "cost": 50,
        "desc": "Ralentit les ennemis",
        "range_tiles": 2.5, "damage": 5,  "fire_rate": 1.0,
        "slow": 0.5,        "aoe": 0,
        "proj_color": (100, 220, 80),
        "image": r"assets\arbre.png",
    },
    {
        "name": "Solaire",  "emoji": "☀️",
        "color": (220, 180, 0),  "cost": 100,
        "desc": "Dégâts zone",
        "range_tiles": 3.0, "damage": 20, "fire_rate": 0.6,
        "slow": 1.0,        "aoe": 55,
        "proj_color": (255, 220, 50),
        "image": r"assets\solaire.png",
    },
    {
        "name": "Éolienne", "emoji": "💨",
        "color": (80, 160, 220), "cost": 80,
        "desc": "Tir rapide",
        "range_tiles": 2.0, "damage": 8,  "fire_rate": 2.5,
        "slow": 1.0,        "aoe": 0,
        "proj_color": (180, 230, 255),
        "image": r"assets\eolienne.png",
    },
    {
        "name": "Compost",  "emoji": "🌿",
        "color": (100, 160, 50), "cost": 60,
        "desc": "Affaiblit ennemis",
        "range_tiles": 2.0, "damage": 10, "fire_rate": 0.8,
        "slow": 0.7,        "aoe": 0,
        "proj_color": (180, 255, 100),
        "image": r"assets\compost.png",
    },
    {
        "name": "Barrage",  "emoji": "💧",
        "color": (40, 100, 200), "cost": 120,
        "desc": "Haute portée",
        "range_tiles": 4.5, "damage": 15, "fire_rate": 0.9,
        "slow": 0.8,        "aoe": 0,
        "proj_color": (100, 180, 255),
        "image": r"assets\barrage.png",
    },
]


# ── ÉTAT DU JEU ──────────────────────────────────────────────────────────────
STATE_MENU    = "menu"
STATE_PLAYING = "playing"
STATE_QUIT    = "quit"


# ─ IMAGE ─────────────────────────────────────────────────────────────────
BG_IMAGE_PATH = "assets/sos_riviere.png"
MUSIC_MENU_PATH = "assets/musique_menu.mp3"
MUSIC_JEU_PATH  = "assets/musique_jeu.mp3"
MUSIC_VOLUME = 0.3

MENU_BTN_Y = SCREEN_H // 2 + 160

MAP_BG_IMAGE_PATH = "assets/map_bg.png"

ENEMY_IMAGE_PATH = r"assets\dechet.png"