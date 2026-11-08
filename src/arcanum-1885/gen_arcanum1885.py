#!/usr/bin/env python3
"""Arcanum 1885: a Civilization V (BNW) scenario map parsed from a fan map of Arcanum, with the steampunk
content of Firaxis' "Empires of the Smoky Skies" (units, buildings, tech tree) and five Arcanum nations
starting from a settler each, ten free cities as city-states, raging barbarians and lore natural wonders."""
import math, struct, os, hashlib, json
import numpy as np
from PIL import Image, ImageDraw
from collections import defaultdict, deque, Counter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
OUT_DIR = os.path.join(HERE, 'mod', 'Arcanum 1885 (v 2)'); os.makedirs(OUT_DIR, exist_ok=True)
OUT_MAP = os.path.join(OUT_DIR, 'Arcanum1885.Civ5Map'); OUT_PNG = os.path.join(HERE, 'Arcanum1885_preview.png')
SPEED = 'GAMESPEED_QUICK'   # temporary for testing; the intended pace is GAMESPEED_EPIC (one turn = one year either way)

# ============================================================== source image -> masks
im = Image.open(os.path.join(HERE, 'art', 'arcanum_map_source.png')).convert('RGBA'); A4 = np.array(im).astype(int)
R, G, B, AL = A4[..., 0], A4[..., 1], A4[..., 2], A4[..., 3]
opaque = AL > 128
light = opaque & (np.minimum(np.minimum(R, G), B) > 200)
grey = opaque & (np.abs(R - G) < 24) & (np.abs(G - B) < 24) & (R > 55) & (R < 205)
LAND = ndimage.binary_opening(ndimage.binary_fill_holes(ndimage.binary_closing(light, iterations=2)), iterations=2)
IMH, IMW = LAND.shape
print(f'source {IMW}x{IMH}, land {LAND.mean():.1%}')

# ============================================================== hex grid in image pixel space (y up)
W = 92
HW = IMW / W; HR = HW / math.sqrt(3); ROWH = 1.5 * HR
H = int((IMH - 2 * HR) / ROWH) + 1
print(f'grid {W}x{H} = {W*H} tiles, hex {HW:.1f} px')
def center(x, y): return (x + 0.5 + 0.5 * (y & 1)) * HW, HR + y * ROWH          # map coords: y up from image bottom
def to_img(px, py): return px, IMH - py
def from_img(ix, iy): return ix, IMH - iy
def corners(x, y):
    cx, cy = center(x, y)
    return [(cx + HR * math.cos(math.radians(30 + 60 * k)), cy + HR * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
def neighbors(x, y):
    cand = [(x + 1, y), (x - 1, y), (x, y + 1), (x + 1, y + 1), (x, y - 1), (x + 1, y - 1)] if y & 1 else \
           [(x + 1, y), (x - 1, y), (x - 1, y + 1), (x, y + 1), (x - 1, y - 1), (x, y - 1)]
    return [(a, b) for a, b in cand if 0 <= a < W and 0 <= b < H]
def hex_at(px, py):
    ry = int(round((py - HR) / ROWH)); best = None
    for yy in range(ry - 1, ry + 2):
        if not 0 <= yy < H: continue
        rx = int(round(px / HW - 0.5 - 0.5 * (yy & 1)))
        for xx in range(rx - 1, rx + 2):
            if not 0 <= xx < W: continue
            cx, cy = center(xx, yy); d = (cx - px) ** 2 + (cy - py) ** 2
            if best is None or d < best[0]: best = (d, xx, yy)
    return (best[1], best[2]) if best else None
def hex_img(ix, iy): return hex_at(*from_img(ix, iy))
def hexdist(a, b):
    def cube(x, y): q = x - (y - (y & 1)) // 2; return q, y, -q - y
    aq, ar, as_ = cube(*a); bq, br, bs = cube(*b); return max(abs(aq - bq), abs(ar - br), abs(as_ - bs))
def rnd(x, y, salt): return int.from_bytes(hashlib.md5(f'{x},{y},{salt}'.encode()).digest()[:4], 'little') / 2 ** 32
SAMP = np.array([(i, j) for i in np.linspace(-0.45, 0.45, 7) for j in np.linspace(-0.5, 0.5, 7) if abs(i) * 2 + abs(j) <= 1.15])
landfrac = np.zeros((H, W)); mtn = np.zeros((H, W))
for y in range(H):
    for x in range(W):
        cx, cy = center(x, y)
        xs = np.clip((cx + SAMP[:, 0] * HW).astype(int), 0, IMW - 1); ys = np.clip((IMH - (cy + SAMP[:, 1] * 2 * HR)).astype(int), 0, IMH - 1)
        landfrac[y, x] = LAND[ys, xs].mean(); mtn[y, x] = grey[ys, xs].mean()
is_land = landfrac >= 0.5
is_lake = np.zeros((H, W), bool)

# ============================================================== regions (image pixel polygons) -> biomes
def in_poly(pt, poly):
    x, y = pt; inside = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1: inside = not inside
    return inside
REGIONS = [  # name, polygon in image pixels, dict of terrain weights and feature probabilities
    ('Glimmering Forest', [(0, 0), (650, 0), (560, 420), (440, 480), (420, 700), (330, 840), (0, 900)], dict(grass=0.75, plains=0.25, forest=0.70)),
    ('Bangellian Swamp', [(560, 40), (830, 40), (820, 400), (640, 420), (560, 420)], dict(grass=0.8, plains=0.2, forest=0.35, marsh=0.45)),
    ('Northern coast', [(830, 0), (1300, 0), (1250, 380), (820, 400)], dict(grass=0.55, plains=0.35, tundra=0.10, forest=0.30)),
    ('Vendigroth Wastes', [(1250, 150), (1628, 150), (1628, 650), (1200, 650)], dict(desert=0.55, plains=0.40, grass=0.05, forest=0.02)),
    ('Isle of Despair', [(1380, 630), (1560, 630), (1560, 820), (1380, 820)], dict(desert=0.4, plains=0.5, grass=0.1, forest=0.05)),
    ('Morbihan Plains', [(800, 560), (1300, 560), (1300, 1200), (760, 1200)], dict(grass=0.45, plains=0.55, forest=0.10)),
    ('Cumbria', [(300, 1100), (800, 1100), (800, 1700), (300, 1700)], dict(grass=0.6, plains=0.4, forest=0.25)),
    ('Arland', [(0, 1150), (300, 1150), (300, 1850), (0, 1850)], dict(grass=0.65, plains=0.35, forest=0.30)),
    ('Cattan', [(400, 1650), (560, 1650), (560, 1760), (400, 1760)], dict(grass=0.4, plains=0.6, forest=0.1)),
    ('Thanatos', [(900, 1380), (1300, 1380), (1300, 1736), (900, 1736)], dict(grass=0.7, plains=0.3, jungle=0.65)),
]
DEFAULT = dict(grass=0.5, plains=0.5, forest=0.20)
def region_at(ix, iy):
    for name, poly, w in REGIONS:
        if in_poly((ix, iy), poly): return w
    return DEFAULT

TERRAINS = ['TERRAIN_GRASS', 'TERRAIN_PLAINS', 'TERRAIN_DESERT', 'TERRAIN_TUNDRA', 'TERRAIN_SNOW', 'TERRAIN_COAST', 'TERRAIN_OCEAN']
GRASS, PLAINS, DESERT, TUNDRA, SNOW, COAST, OCEAN = range(7)
FEATURES = ['FEATURE_ICE', 'FEATURE_JUNGLE', 'FEATURE_MARSH', 'FEATURE_OASIS', 'FEATURE_FLOOD_PLAINS', 'FEATURE_FOREST', 'FEATURE_FALLOUT']
ICE, JUNGLE, MARSH, OASIS, FLOOD, FOREST, FALLOUT = range(7)
WONDERS = ['FEATURE_CRATER', 'FEATURE_FUJI', 'FEATURE_MESA', 'FEATURE_REEF', 'FEATURE_VOLCANO', 'FEATURE_GIBRALTAR', 'FEATURE_GEYSER', 'FEATURE_FOUNTAIN_YOUTH',
           'FEATURE_POTOSI', 'FEATURE_EL_DORADO', 'FEATURE_SRI_PADA', 'FEATURE_MT_SINAI', 'FEATURE_MT_KAILASH', 'FEATURE_ULURU', 'FEATURE_LAKE_VICTORIA', 'FEATURE_KILIMANJARO', 'FEATURE_SOLOMONS_MINES']
WID = {w.split('_', 1)[1]: i for i, w in enumerate(WONDERS)}
RESOURCES = ['RESOURCE_IRON']   # resources are randomised by the game (map flag); the list only has to be non-empty
NONE = 0xFF
terrain = np.full((H, W), OCEAN, np.uint8); elev = np.zeros((H, W), np.uint8); feature = np.full((H, W), NONE, np.uint8)
wonder = np.full((H, W), NONE, np.uint8); resource = np.full((H, W), NONE, np.uint8); resamt = np.zeros((H, W), np.uint8); river = np.zeros((H, W), np.uint8)
for y in range(H):
    for x in range(W):
        if not is_land[y, x]:
            near = any(is_land[b, a] for a, b in neighbors(x, y)) or any(is_land[b2, a2] for a, b in neighbors(x, y) for a2, b2 in neighbors(a, b))
            terrain[y, x] = COAST if near else OCEAN; continue
        cx, cy = center(x, y); ix, iy = to_img(cx, cy); w = region_at(ix, iy)
        # relief from the drawn mountain shading
        m = mtn[y, x]
        if m >= 0.14: elev[y, x] = 2
        elif m >= 0.07 or (m > 0 and rnd(x, y, 'h') < 0.5): elev[y, x] = 1
        elif rnd(x, y, 'hills') < 0.10: elev[y, x] = 1
        wts = {GRASS: w.get('grass', 0), PLAINS: w.get('plains', 0), DESERT: w.get('desert', 0), TUNDRA: w.get('tundra', 0)}
        if iy < 110: wts[TUNDRA] = wts.get(TUNDRA, 0) + 0.5     # the far northern shore
        r = rnd(x, y, 'terr'); s = sum(wts.values()) or 1; acc = 0; t = GRASS
        for k, v in wts.items():
            acc += v / s
            if r < acc: t = k; break
        terrain[y, x] = t
        if elev[y, x] == 2: continue
        r2 = rnd(x, y, 'feat'); pm = w.get('marsh', 0) if elev[y, x] == 0 and t != DESERT else 0; pj = w.get('jungle', 0) if t != DESERT else 0
        pf = (w.get('forest', 0) * (1.3 if elev[y, x] == 1 else 1.0)) if t not in (DESERT,) else 0
        if r2 < pm: feature[y, x] = MARSH
        elif r2 < pm + pj: feature[y, x] = JUNGLE
        elif r2 < pm + pj + pf: feature[y, x] = FOREST
        elif t == DESERT and elev[y, x] == 0 and rnd(x, y, 'oasis') < 0.03: feature[y, x] = OASIS

# ============================================================== rivers (image-pixel polylines) -> hex edges
def ckey(p): return (int(round(p[0] / HW * 100)), int(round(p[1] / HW * 100)))
EDGES = {}; ADJ = defaultdict(set)
for y in range(H):
    for x in range(W):
        c = [ckey(p) for p in corners(x, y)]
        for a, b, side, ff in ((c[0], c[5], 'E', c[0]), (c[4], c[5], 'SE', c[4]), (c[4], c[3], 'SW', c[4])):
            EDGES[frozenset((a, b))] = (x, y, side, ff); ADJ[a].add(b); ADJ[b].add(a)
def across(x, y, side):
    if side == 'E': return (x + 1, y)
    if side == 'SE': return (x + 1, y - 1) if y & 1 else (x, y - 1)
    return (x, y - 1) if y & 1 else (x - 1, y - 1)
def nearest_corner(px, py):
    hx = hex_at(px, py)
    return ckey(min(corners(*hx), key=lambda p: (p[0] - px) ** 2 + (p[1] - py) ** 2)) if hx else None
def bfs(a, b, limit=8):
    if b in ADJ[a]: return [a, b]
    prev = {a: None}; q = deque([(a, 0)])
    while q:
        u, d = q.popleft()
        if d >= limit: continue
        for v in ADJ[u]:
            if v in prev: continue
            prev[v] = u
            if v == b:
                path = [b]
                while prev[path[-1]] is not None: path.append(prev[path[-1]])
                return path[::-1]
            q.append((v, d + 1))
    return None
RIVERS = {   # source -> mouth, image pixels
    'Hadrian': [(640, 560), (700, 600), (760, 650), (790, 720), (810, 800), (835, 870), (850, 915)],
    'Hadrian West Fork': [(860, 560), (830, 600), (790, 650)],
    'Bangellian': [(620, 170), (640, 250), (680, 320), (650, 380), (620, 440), (600, 500)],
    'Lethe': [(330, 880), (300, 860), (250, 845), (180, 850), (120, 870), (40, 865)],
    'Cumbrian': [(370, 1150), (450, 1170), (520, 1190), (570, 1200), (610, 1250), (660, 1270), (690, 1300)],
    'Vendigroth': [(1230, 560), (1270, 590), (1320, 605)],
}
def land_tile(t): return 0 <= t[0] < W and 0 <= t[1] < H and is_land[t[1], t[0]]
n_edges = 0
for nm, line in RIVERS.items():
    P = [from_img(ix, iy) for ix, iy in line]; dense = []
    for (x0, y0), (x1, y1) in zip(P, P[1:]):
        d = math.hypot(x1 - x0, y1 - y0); n = max(1, int(d / (0.1 * HW)))
        for i in range(n): dense.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    dense.append(P[-1]); path = []
    for px, py in dense:
        c = nearest_corner(px, py)
        if c is None or (path and c == path[-1]): continue
        if path and c not in ADJ[path[-1]]:
            seg = bfs(path[-1], c)
            if seg is None: path.append(c); continue
            path.extend(seg[1:])
        else: path.append(c)
    clean = []
    for c in path:
        if len(clean) >= 2 and clean[-2] == c: clean.pop()
        else: clean.append(c)
    for a, b in zip(clean, clean[1:]):
        e = EDGES.get(frozenset((a, b)))
        if not e: continue
        x, y, side, ff = e
        if not (land_tile((x, y)) and land_tile(across(x, y, side))): continue
        bit, flow = {'E': (1, 8), 'SE': (2, 16), 'SW': (4, 32)}[side]
        if river[y, x] & bit: continue
        river[y, x] |= bit | (flow if a == ff else 0); n_edges += 1
print(f'  {n_edges} river edges')
def has_river(x, y):
    if river[y, x] & 7: return True
    for a, b in neighbors(x, y):
        for side, bit in (('E', 1), ('SE', 2), ('SW', 4)):
            if across(a, b, side) == (x, y) and river[b, a] & bit: return True
    return False
for y in range(H):
    for x in range(W):
        if is_land[y, x] and terrain[y, x] == DESERT and elev[y, x] == 0 and has_river(x, y) and feature[y, x] == NONE: feature[y, x] = FLOOD

# ============================================================== natural wonders at lore sites
def find_tile(ix, iy, pred, radius=3):
    h0 = hex_img(ix, iy)
    if h0 is None: return None
    seen = {h0}; q = deque([(h0, 0)])
    while q:
        t, d = q.popleft()
        if pred(*t): return t
        if d >= radius: continue
        for nb in neighbors(*t):
            if nb not in seen: seen.add(nb); q.append((nb, d + 1))
    return None
LORE_WONDERS = [  # name, donor wonder, image px, needs-coast
    ("Bellerogrim's Lair", 'VOLCANO', (1020, 675), False), ('Ancient Temple of Derian-Ka', 'MT_SINAI', (1010, 760), False), ('Elven Burial Site', 'SRI_PADA', (1080, 860), False),
    ('Ruins of Kree', 'MESA', (1150, 1040), False), ('Isle of Despair', 'GIBRALTAR', (1420, 700), True), ('Ring of Brodgar', 'ULURU', (130, 1380), False),
    ("Falcon's Ache", 'FOUNTAIN_YOUTH', (165, 405), False), ('Bangellian Deeps', 'LAKE_VICTORIA', (610, 125), False), ("Lethe Wyvern's Lair", 'CRATER', (180, 845), False),
    ('Stonewall Peak', 'KILIMANJARO', (330, 1060), False), ('Mines of the Wheel Clan', 'EL_DORADO', (870, 440), False), ("Torg's Altar", 'GEYSER', (575, 1125), False),
]
wonder_tiles = {}
for name, w, (ix, iy), coast in LORE_WONDERS:
    def ok(x, y, coast=coast):
        if not is_land[y, x] or wonder[y, x] != NONE: return False
        if any(wonder[b, a] != NONE for a, b in neighbors(x, y)): return False
        if coast and not any(not is_land[b, a] for a, b in neighbors(x, y)): return False
        return True
    t = find_tile(ix, iy, ok, 4)
    if t is None: print('  !! no tile for wonder', name); continue
    wonder[t[1], t[0]] = WID[w]; feature[t[1], t[0]] = NONE; elev[t[1], t[0]] = 2 if w in ('VOLCANO', 'MT_SINAI', 'SRI_PADA', 'KILIMANJARO', 'GIBRALTAR') else 0
    if w in ('LAKE_VICTORIA', 'FOUNTAIN_YOUTH', 'MESA', 'ULURU', 'CRATER', 'EL_DORADO', 'GEYSER'): elev[t[1], t[0]] = 0
    terrain[t[1], t[0]] = PLAINS if terrain[t[1], t[0]] == TUNDRA else terrain[t[1], t[0]]
    wonder_tiles[name] = t
print(f'  {len(wonder_tiles)} natural wonders placed')

# ============================================================== players, city-states, starts
PLAYERS = [   # donor civ (steampunk re-skin) -> Arcanum nation
    dict(key='TARANT', civ='CIVILIZATION_ENGLAND', leader='The Industrial Council', name='Tarant', color='PLAYERCOLOR_ARC_TARANT', start=(840, 905)),
    dict(key='CALADON', civ='CIVILIZATION_FRANCE', leader='Crown of Caladon', name='Caladon', color='PLAYERCOLOR_ARC_CALADON', start=(175, 1645)),
    dict(key='CUMBRIA', civ='CIVILIZATION_RUSSIA', leader='King Praetor', name='Cumbria', color='PLAYERCOLOR_ARC_CUMBRIA', start=(540, 1475)),
    dict(key='WHEEL', civ='CIVILIZATION_GERMANY', leader='Loghaire Thunder Stone', name='Wheel Clan', color='PLAYERCOLOR_ARC_WHEEL', start=(880, 545)),
    dict(key='VENDIGROTH', civ='CIVILIZATION_SWEDEN', leader='Technocrat Council', name='Vendigroth', color='PLAYERCOLOR_ARC_VENDIGROTH', start=(1480, 385)),
]
NP = len(PLAYERS)
CITY_STATES = [  # name, minor civ type, trait, image px
    ('Qintarra', 'MINOR_CIV_ARC_QINTARRA', 'MINOR_TRAIT_CULTURED', (245, 495)), ('Ashbury', 'MINOR_CIV_ARC_ASHBURY', 'MINOR_TRAIT_MERCANTILE', (1265, 825)),
    ('Black Root', 'MINOR_CIV_ARC_BLACKROOT', 'MINOR_TRAIT_MARITIME', (675, 1290)), ('Stillwater', 'MINOR_CIV_ARC_STILLWATER', 'MINOR_TRAIT_MILITARISTIC', (605, 590)),
    ('Shrouded Hills', 'MINOR_CIV_ARC_SHROUDED', 'MINOR_TRAIT_MERCANTILE', (345, 1150)), ('Roseborough', 'MINOR_CIV_ARC_ROSEBOROUGH', 'MINOR_TRAIT_CULTURED', (55, 1355)),
    ('Tulla', 'MINOR_CIV_ARC_TULLA', 'MINOR_TRAIT_CULTURED', (1340, 325)), ('Isle of Despair', 'MINOR_CIV_ARC_DESPAIR', 'MINOR_TRAIT_MILITARISTIC', (1465, 690)),
    ('Bedokaan', 'MINOR_CIV_ARC_BEDOKAAN', 'MINOR_TRAIT_MARITIME', (605, 160)), ("T'sen-Ang", 'MINOR_CIV_ARC_TSENANG', 'MINOR_TRAIT_MILITARISTIC', (275, 140)),
]
NCS = len(CITY_STATES)
owner = np.full((H, W), NONE, np.uint8)
city_at = {}; city_tiles = []
def settle_ok(x, y):
    return is_land[y, x] and elev[y, x] != 2 and wonder[y, x] == NONE and (x, y) not in city_at and all(hexdist((x, y), t) >= 4 for t in city_tiles) and all(hexdist((x, y), t) >= 2 for t in wonder_tiles.values())
for i, (name, mtype, trait, (ix, iy)) in enumerate(CITY_STATES):
    t = find_tile(ix, iy, settle_ok, 4)
    if t is None: raise SystemExit('cannot place ' + name)
    city_at[t] = i; city_tiles.append(t); feature[t[1], t[0]] = NONE
    for yy in range(H):
        for xx in range(W):
            if hexdist((xx, yy), t) <= 2 and (is_land[yy, xx] or any(is_land[b, a] for a, b in neighbors(xx, yy))): owner[yy, xx] = 32 + i
starts = []
for p in PLAYERS:
    t = find_tile(*p['start'], lambda x, y: settle_ok(x, y) and owner[y, x] == NONE and all(hexdist((x, y), s) >= 6 for s in starts), 5)
    if t is None: raise SystemExit('cannot place start ' + p['key'])
    starts.append(t); feature[t[1], t[0]] = NONE
print('  starts:', {p['key']: s for p, s in zip(PLAYERS, starts)})

# ============================================================== units
UNITS = ['UNIT_SETTLER', 'UNIT_GREAT_WAR_INFANTRY', 'UNIT_WORKER']
UID = {u.split('_', 1)[1]: i for i, u in enumerate(UNITS)}
PROMOS = ['PROMOTION_DRILL_1']
units = []
for i, s in enumerate(starts):
    units.append(dict(type='SETTLER', owner=i, x=s[0], y=s[1], promos=[], xp=0))
    units.append(dict(type='GREAT_WAR_INFANTRY', owner=i, x=s[0], y=s[1], promos=[], xp=0))
    units.append(dict(type='WORKER', owner=i, x=s[0], y=s[1], promos=[], xp=0))
for i, t in enumerate(city_tiles):
    units.append(dict(type='GREAT_WAR_INFANTRY', owner=32 + i, x=t[0], y=t[1], promos=['DRILL_1'], xp=10))
    units.append(dict(type='WORKER', owner=32 + i, x=t[0], y=t[1], promos=[], xp=0))

# ============================================================== scenario data
# Stock techs the Smoky Skies rules delete (TECH_RADIO is re-created there as a late steampunk tech, so it must not be a starting tech).
STEAMPUNK_DELETED = {'TECH_REPLACEABLE_PARTS', 'TECH_RAILROAD', 'TECH_ELECTRICITY', 'TECH_REFRIGERATION', 'TECH_TELEGRAPH', 'TECH_RADIO', 'TECH_FLIGHT', 'TECH_COMBUSTION'}
TECHS = [l.strip() for l in open(f'{XMLDIR}/TECHS_THROUGH_INDUSTRIAL.txt') if l.strip() and l.strip() not in STEAMPUNK_DELETED]
BUILDINGS = ['BUILDING_PALACE', 'BUILDING_MONUMENT', 'BUILDING_WALLS', 'BUILDING_GRANARY', 'BUILDING_BARRACKS']
POLICIES = ['POLICY_TRADITION']
IMPROVEMENTS = ['IMPROVEMENT_FARM']
VICTORIES = ['VICTORY_DOMINATION', 'VICTORY_CULTURAL', 'VICTORY_DIPLOMATIC']
GAMEOPTIONS = ['GAMEOPTION_RAGING_BARBARIANS', 'GAMEOPTION_NO_GOODY_HUTS', 'GAMEOPTION_NO_RELIGION', 'GAMEOPTION_NO_TUTORIAL', 'GAMEOPTION_POLICY_SAVING', 'GAMEOPTION_DISABLE_START_BIAS']
def cfix(s, n): b = s.encode('utf-8')[:n - 1]; return b + b'\0' * (n - len(b))
def strlist(names): return b''.join(n.encode() + b'\0' for n in names)
def plist(names): return b''.join(bytes([len(n)]) + n.encode() + b'\0' for n in names)
def bitset(names, index, nbytes):
    b = bytearray(nbytes)
    for n in names: i = index[n]; b[i // 8] |= 1 << (i % 8)
    return bytes(b)
def pow2(n, lo=64):
    c = lo
    while c < n: c *= 2
    return c
P = NP; CS = NCS; T = P + CS
tile_units = defaultdict(list)
for i, u in enumerate(units): tile_units[(u['x'], u['y'])].append(i)
next_of = {}
for lst in tile_units.values():
    for a, b in zip(lst, lst[1:]): next_of[a] = b
ucap = pow2(len(units) + 1); urec = bytearray()
for i in range(ucap):
    if i < len(units):
        u = units[i]; status = 0x01 if u['type'] == 'GREAT_WAR_INFANTRY' else 0
        # experience is written as 0: pre-placed promotions stay, but nobody starts with a promotion pending
        urec += struct.pack('<HHIIIBBBB', next_of.get(i, 0xFFFF), 0xFFFF, 0, 100000, UID[u['type']], u['owner'], 0, status, 0)
        urec += bitset(['PROMOTION_' + p for p in u['promos']], {p: k for k, p in enumerate(PROMOS)}, 64)
    else:
        urec += struct.pack('<HHIIIBBBB', i + 1 if i + 1 < ucap else 0xFFFF, 0xFFFF, 0, 0, 0xFFFFFFFF, 0, 0, 0, 0) + bytes(64)
unit_data = struct.pack('<I', len(units)) + bytes(urec)
ccap = pow2(len(CITY_STATES) + 1); crec = bytearray()
BID = {b: i for i, b in enumerate(BUILDINGS)}
for i in range(ccap):
    if i < len(CITY_STATES):
        name = CITY_STATES[i][0]
        crec += cfix(name, 64) + struct.pack('<BBHI', 32 + i, 0, 3, 100000) + bitset(['BUILDING_MONUMENT', 'BUILDING_WALLS'], BID, 64)
    else: crec += bytes(136)
city_data = struct.pack('<I', len(CITY_STATES)) + bytes(crec)
def relbits(pairs):
    nbits = T * (T - 1) // 2; b = bytearray((nbits + 7) // 8)
    for i, j in pairs:
        lg, sm = max(i, j), min(i, j); k = lg * (lg - 1) // 2 + sm; b[k // 8] |= 1 << (k % 8)
    return bytes(b)
rel = relbits([]) * 5          # nobody has met anybody: normal exploration game
influence = bytes(P * 64 * 4)
visibility = bytes((W * H * T + 7) // 8)   # nothing revealed
team_data = b''.join(cfix(f'Team {i + 1}', 32) + bitset(TECHS, {t: k for k, t in enumerate(TECHS)}, 32) for i in range(T))
player_data = b''
for i, p in enumerate(PLAYERS):
    player_data += bitset([], {n: k for k, n in enumerate(POLICIES)}, 32)
    player_data += cfix(p['leader'], 64) + cfix(p['name'], 64) + cfix(p['civ'], 64) + cfix(p['color'], 64) + cfix('ERA_MODERN', 64) + cfix('HANDICAP_PRINCE', 64)
    player_data += struct.pack('<IIIIBB2s', 0, 100, starts[i][0], starts[i][1], i, 1, b'\0\0')
for i, (name, mtype, trait, pos) in enumerate(CITY_STATES):
    player_data += bytes(32) + cfix('', 64) + cfix('', 64) + cfix(mtype, 64) + cfix('PLAYERCOLOR_MINOR_WHITE', 64) + cfix('ERA_MODERN', 64) + cfix('HANDICAP_CHIEFTAIN', 64)
    player_data += struct.pack('<IIIIBB2s', 0, 0, city_tiles[i][0], city_tiles[i][1], P + i, 0, b'\0\0')
plot_data = bytearray()
for y in range(H):
    for x in range(W):
        cid = city_at.get((x, y), 0xFFFF); uid = tile_units[(x, y)][0] if (x, y) in tile_units else 0xFFFF
        plot_data += struct.pack('<HHBBBB', cid, uid, owner[y, x], NONE, NONE, NONE)
terr_b, feat_b, wond_b, res_b = strlist(TERRAINS), strlist(FEATURES), strlist(WONDERS), strlist(RESOURCES)
name_b = b'Arcanum 1885\0'
desc_b = b'The continent of Arcanum in the year 1885: Tarant, Caladon, Cumbria, the Wheel Clan and Vendigroth start from a settler each; ten free cities; raging barbarians; natural wonders at the sites of legend. Steampunk units and technologies of Empires of the Smoky Skies. Domination, cultural and diplomatic victories.\0'
world_b = b'WORLDSIZE_HUGE'.ljust(64, b'\0')
imp_b, unit_b, tech_b, pol_b, bld_b, prom_b = strlist(IMPROVEMENTS), strlist(UNITS), strlist(TECHS), strlist(POLICIES), strlist(BUILDINGS), strlist(PROMOS)
vict_b, opt_b = plist(VICTORIES), plist(GAMEOPTIONS)
with open(OUT_MAP, 'wb') as f:
    f.write(struct.pack('<BIIB', 0x8C, W, H, P)); f.write(bytes([0x02, 0, 0, 0]))     # bit1: randomise resources
    f.write(struct.pack('<7I', len(terr_b), len(feat_b), len(wond_b), len(res_b), 0, len(name_b), len(desc_b)))
    f.write(terr_b + feat_b + wond_b + res_b + name_b + desc_b + struct.pack('<I', 64) + world_b)
    for y in range(H):
        for x in range(W):
            f.write(bytes([terrain[y, x], NONE, feature[y, x], river[y, x], elev[y, x], 4 if is_land[y, x] else 0, wonder[y, x], 0]))
    f.write(struct.pack('<64sIIIiBBBB9I', SPEED.encode(), 0, 0, 0, 1885, P, CS, T, 0, len(imp_b), len(unit_b), len(tech_b), len(pol_b), len(bld_b), len(prom_b), len(unit_data), 0, len(city_data)))
    f.write(struct.pack('<II', len(vict_b), len(opt_b)))
    f.write(imp_b + unit_b + tech_b + pol_b + bld_b + prom_b + unit_data + city_data + vict_b + opt_b + rel + influence + visibility)
    f.write(team_data + player_data + bytes(plot_data))
land_n = int(is_land.sum())
print(f'wrote {OUT_MAP} {os.path.getsize(OUT_MAP)} bytes; land {land_n} ({land_n/(W*H):.1%}) mountains {int((elev==2).sum())} hills {int((elev==1).sum())} forest {int((feature==FOREST).sum())} jungle {int((feature==JUNGLE).sum())} marsh {int((feature==MARSH).sum())}')
json.dump(dict(starts=starts, city_tiles=city_tiles, wonders={k: list(v) for k, v in wonder_tiles.items()}, W=W, H=H), open(os.path.join(HERE, 'map_layout.json'), 'w'), indent=1)

# ============================================================== preview
S = 9
img = Image.new('RGB', (int((W + 0.5) * S) + 2, int(H * S * 0.866 + S) + 2), (24, 60, 120)); d = ImageDraw.Draw(img)
TCOL = {GRASS: (96, 168, 64), PLAINS: (196, 178, 96), DESERT: (236, 214, 150), TUNDRA: (170, 170, 150), SNOW: (240, 240, 240), COAST: (70, 140, 210), OCEAN: (24, 60, 120)}
def pcenter(x, y): return (x + 0.5 + 0.5 * (y & 1)) * S + 1, img.size[1] - (y * 0.866 * S + 0.577 * S) - 1
def pcorners(x, y):
    cx, cy = pcenter(x, y); r = S / math.sqrt(3)
    return [(cx + r * math.cos(math.radians(30 + 60 * k)), cy - r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
for y in range(H):
    for x in range(W):
        col = TCOL[terrain[y, x]]
        if feature[y, x] == FOREST: col = tuple(int(c * 0.6) for c in col)
        if feature[y, x] == JUNGLE: col = (30, 110, 60)
        if feature[y, x] == MARSH: col = (80, 150, 130)
        d.polygon(pcorners(x, y), fill=col); cx, cy = pcenter(x, y)
        if elev[y, x] == 2: d.polygon([(cx - 4, cy + 3), (cx, cy - 4), (cx + 4, cy + 3)], fill=(70, 60, 60))
        elif elev[y, x] == 1: d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], outline=(100, 70, 40))
        if wonder[y, x] != NONE: d.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 0, 255))
        if owner[y, x] != NONE: d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255))
for y in range(H):
    for x in range(W):
        rv = river[y, x]
        if not rv & 7: continue
        pc = pcorners(x, y)
        if rv & 1: d.line([pc[0], pc[5]], fill=(40, 90, 255), width=2)
        if rv & 2: d.line([pc[4], pc[5]], fill=(40, 90, 255), width=2)
        if rv & 4: d.line([pc[3], pc[4]], fill=(40, 90, 255), width=2)
for i, (name, mtype, trait, pos) in enumerate(CITY_STATES):
    cx, cy = pcenter(*city_tiles[i]); d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255), outline=(0, 0, 0)); d.text((cx + 6, cy - 6), name, fill=(255, 255, 255))
for p, s in zip(PLAYERS, starts):
    cx, cy = pcenter(*s); d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 215, 0), outline=(0, 0, 0)); d.text((cx + 7, cy - 6), p['name'], fill=(255, 230, 120))
for name, t in wonder_tiles.items():
    cx, cy = pcenter(*t); d.text((cx + 6, cy - 6), name, fill=(255, 150, 255))
img.save(OUT_PNG); print('preview', OUT_PNG)
