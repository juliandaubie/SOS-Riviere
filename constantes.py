# ─── CONFIG ───────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 700
TILE_SIZE = 60
COLS = 14
ROWS = 10
MAP_X = 20
MAP_Y = 60
FPS = 60

# ─── COULEURS ÉCOLOGIE ────────────────────────────────────────────────────────
BG_COLOR        = (15, 30, 20)
GRASS_COLOR     = (45, 100, 50)
GRASS_DARK      = (35, 80, 40)
PATH_COLOR      = (180, 140, 80)
PATH_DARK       = (160, 120, 60)
GRID_COLOR      = (20, 60, 25)
COORD_COLOR     = (120, 200, 100)
HEADER_COLOR    = (10, 25, 15)
TEXT_COLOR      = (200, 240, 180)
HIGHLIGHT       = (100, 220, 100, 80)
SHADOW_COLOR    = (0, 0, 0, 120)

TOWER_ZONE_COLOR = (60, 130, 60)
TOWER_ZONE_BORDER = (80, 180, 80)

# ─── CHEMIN DU MONSTRE (coordonnées en tiles) ─────────────────────────────────

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

# ─── TOURS DISPONIBLES ────────────────────────────────────
TOWER_TYPES = [
    {"name": "Arbre",    "emoji": "🌳", "color": (34, 120, 34),  "cost": 50,  "desc": "Ralentit les ennemis"},
    {"name": "Solaire",  "emoji": "☀️",  "color": (220, 180, 0),  "cost": 100, "desc": "Dégâts zone"},
    {"name": "Éolienne", "emoji": "💨",  "color": (80, 160, 220), "cost": 80,  "desc": "Tir rapide"},
    {"name": "Compost",  "emoji": "🌿",  "color": (100, 160, 50), "cost": 60,  "desc": "Affaiblit ennemis"},
    {"name": "Barrage",  "emoji": "💧",  "color": (40, 100, 200), "cost": 120, "desc": "Haute portée"},
]


# ── ÉTAT DU JEU ──────────────────────────────────────────────────────────────
STATE_MENU    = "menu"
STATE_PLAYING = "playing"
STATE_QUIT    = "quit"


# ─ IMAGE ─────────────────────────────────────────────────────────────────
BG_IMAGE_PATH = "assets/sos_riviere.png"


MENU_BTN_Y = SCREEN_H // 2 + 160