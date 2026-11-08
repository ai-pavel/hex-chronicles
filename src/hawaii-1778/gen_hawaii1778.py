"""Hawaii 1778: the Hawaiian Islands on the eve of contact, for Civilization V (Brave New World).

Eight islands, five chiefdoms and three lesser-chief islands as city-states, each major starting from a Settler and a Warrior in
the Ancient era at its historical seat.  Real geography from
NOAA ETOPO 2022 at 15 arc-seconds, trade-wind climate (jungle to windward, dry leeward coasts, snow on Mauna Kea and Mauna Loa),
one natural wonder per island at its real site, no iron and no horses, stock rules, normal barbarians, Standard speed with one
turn = one year from 1778, development capped at the Classical era.

Factions (donor civ in brackets): Kona / Kamehameha (Polynesia), Hilo / Keoua (Japan), Maui / Kahekili (Zulu), Oahu / Kahahana (Carthage),
Kauai / Kamakahelei (Ethiopia).  City-states: Molokai (religious), Lanai and Niihau (maritime).
"""
import math, struct, os, sys, hashlib, json, shutil
import numpy as np
from PIL import Image, ImageDraw
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('HEX_DATA', os.path.join(HERE, '..', '..', 'data'))        # tools/fetch_data.py
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
MOD_NAME = 'Hawaii 1778'; MOD_ID = 'e7b3d1a5-1778-4c2e-9f40-8a6b2c5d7e91'
OUT_DIR = os.path.join(HERE, 'mod', 'Hawaii 1778 (v 1)'); os.makedirs(OUT_DIR, exist_ok=True)
SPEED = 'GAMESPEED_QUICK'   # Quick for play testing; the intended pace is GAMESPEED_STANDARD (one turn = one year either way)
OUT_MAP = os.path.join(OUT_DIR, 'Hawaii1778.Civ5Map'); OUT_PNG = os.path.join(HERE, 'Hawaii1778_preview.png')

# ============================================================== grid: equirectangular, ~3 km hexes
# 160 hexes wide: a 196x101 version of this map (2.5 km hexes, 19,796 plots) crashed the game engine at game start; 160x83 runs.
LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -160.40, -154.70, 18.80, 22.35
LAT0 = 20.6; KX = 111.32 * math.cos(math.radians(LAT0)); KY = 110.7     # km per degree
def proj(lon, lat): return (lon - LON_MIN) * KX, (lat - LAT_MIN) * KY
XMAX, YMAX = proj(LON_MAX, LAT_MAX)
HW = float(os.environ.get('HI_HEX_KM', '4.0')); W = int(round(XMAX / HW)); HR = HW / math.sqrt(3); ROWH = 1.5 * HR   # 4 km -> ~148 hexes wide (maps wider than 160 crash the engine)
H = int(math.ceil((YMAX - 2 * HR) / ROWH)) + 1
print(f'grid {W}x{H} = {W*H} tiles, hex {HW:.1f} km, extent {XMAX:.0f} x {YMAX:.0f} km')
def center(x, y): return (x + 0.5 + 0.5 * (y & 1)) * HW, HR + y * ROWH
def lonlat(px, py): return LON_MIN + px / KX, LAT_MIN + py / KY
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
def hex_ll(lon, lat): return hex_at(*proj(lon, lat))
def hexdist(a, b):
    def cube(x, y): q = x - (y - (y & 1)) // 2; return q, y, -q - y
    aq, ar, as_ = cube(*a); bq, br, bs = cube(*b); return max(abs(aq - bq), abs(ar - br), abs(as_ - bs))
def rnd(x, y, salt): return int.from_bytes(hashlib.md5(f'{x},{y},{salt}'.encode()).digest()[:4], 'little') / 2 ** 32
def ring(t, r):
    return [(x, y) for y in range(max(0, t[1] - r), min(H, t[1] + r + 1)) for x in range(max(0, t[0] - r), min(W, t[0] + r + 1)) if hexdist((x, y), t) <= r]

# ============================================================== relief raster (land, elevation, depth all from ETOPO 2022)
E_LON0, E_LAT1, E_RES = -160.45, 22.40, 0.005
ETOPO = np.array(Image.open(f'{DATA}/etopo_hi.tif'))   # 1160x730, 0.005 deg (~0.5 km)
EH, EW = ETOPO.shape
def etopo_at(lon, lat):
    c = np.clip(((lon - E_LON0) / E_RES).astype(int), 0, EW - 1); r = np.clip(((E_LAT1 - lat) / E_RES).astype(int), 0, EH - 1)
    return ETOPO[r, c]
SAMP = np.array([(i, j) for i in np.linspace(-0.45, 0.45, 7) for j in np.linspace(-0.5, 0.5, 7) if abs(i) * 2 + abs(j) <= 1.15])
landfrac = np.zeros((H, W)); emean = np.zeros((H, W)); emax = np.zeros((H, W)); emin = np.zeros((H, W)); depth = np.zeros((H, W))
print('sampling hexes...')
for y in range(H):
    for x in range(W):
        cx, cy = center(x, y)
        lo, la = lonlat(cx + SAMP[:, 0] * HW, cy + SAMP[:, 1] * 2 * HR)
        e = etopo_at(lo, la); land = e > 0
        landfrac[y, x] = land.mean()
        if land.any(): emean[y, x] = e[land].mean(); emax[y, x] = e[land].max(); emin[y, x] = e[land].min()
        if (~land).any(): depth[y, x] = e[~land].mean()
is_land = landfrac >= 0.5
# keep Kahoolawe and Niihau whole even where a hex is mostly water
for lon, lat in ((-156.6, 20.55), (-160.15, 21.9)):
    t = hex_ll(lon, lat)
    if landfrac[t[1], t[0]] >= 0.2: is_land[t[1], t[0]] = True

# ============================================================== islands
ISLANDS = [  # key, name, centre lon/lat
    ('HAWAII', 'Hawaii', (-155.45, 19.6)), ('MAUI', 'Maui', (-156.33, 20.8)), ('OAHU', 'Oahu', (-157.97, 21.48)), ('KAUAI', 'Kauai', (-159.53, 22.05)),
    ('MOLOKAI', 'Molokai', (-157.0, 21.13)), ('LANAI', 'Lanai', (-156.93, 20.83)), ('NIIHAU', 'Niihau', (-160.15, 21.9)), ('KAHOOLAWE', 'Kahoolawe', (-156.6, 20.55)),
]
IKEY = {k: i for i, (k, _, _) in enumerate(ISLANDS)}
island = np.full((H, W), -1, int)
seen = set()
for y in range(H):
    for x in range(W):
        if not is_land[y, x] or (x, y) in seen: continue
        comp = []; q = deque([(x, y)]); seen.add((x, y))
        while q:
            t = q.popleft(); comp.append(t)
            for nb in neighbors(*t):
                if is_land[nb[1], nb[0]] and nb not in seen: seen.add(nb); q.append(nb)
        cx = sum(center(*t)[0] for t in comp) / len(comp); cy = sum(center(*t)[1] for t in comp) / len(comp)
        k = min(range(len(ISLANDS)), key=lambda i: (proj(*ISLANDS[i][2])[0] - cx) ** 2 + (proj(*ISLANDS[i][2])[1] - cy) ** 2)
        for t in comp: island[t[1], t[0]] = k
isl_c = {}
for i, (k, name, _) in enumerate(ISLANDS):
    ys, xs = np.where(island == i); isl_c[i] = (float(np.mean([center(x, y)[0] for x, y in zip(xs, ys)])), float(np.mean([center(x, y)[1] for x, y in zip(xs, ys)])))
    print(f'  {name}: {len(xs)} hexes ({len(xs) * HW * HW * math.sqrt(3) / 2:.0f} km2), highest {emax[island == i].max():.0f} m')

# ============================================================== terrain
TERRAINS = ['TERRAIN_GRASS', 'TERRAIN_PLAINS', 'TERRAIN_DESERT', 'TERRAIN_TUNDRA', 'TERRAIN_SNOW', 'TERRAIN_COAST', 'TERRAIN_OCEAN']
GRASS, PLAINS, DESERT, TUNDRA, SNOW, COAST, OCEAN = range(7)
FEATURES = ['FEATURE_ICE', 'FEATURE_JUNGLE', 'FEATURE_MARSH', 'FEATURE_OASIS', 'FEATURE_FLOOD_PLAINS', 'FEATURE_FOREST', 'FEATURE_FALLOUT']
ICE, JUNGLE, MARSH, OASIS, FLOOD, FOREST, FALLOUT = range(7)
WONDERS = ['FEATURE_CRATER', 'FEATURE_FUJI', 'FEATURE_MESA', 'FEATURE_REEF', 'FEATURE_VOLCANO', 'FEATURE_GIBRALTAR', 'FEATURE_GEYSER', 'FEATURE_FOUNTAIN_YOUTH',
           'FEATURE_POTOSI', 'FEATURE_EL_DORADO', 'FEATURE_SRI_PADA', 'FEATURE_MT_SINAI', 'FEATURE_MT_KAILASH', 'FEATURE_ULURU', 'FEATURE_LAKE_VICTORIA', 'FEATURE_KILIMANJARO', 'FEATURE_SOLOMONS_MINES']
WID = {w.split('_', 1)[1]: i for i, w in enumerate(WONDERS)}
RESOURCES = ['RESOURCE_IRON', 'RESOURCE_HORSE', 'RESOURCE_COAL', 'RESOURCE_OIL', 'RESOURCE_ALUMINUM', 'RESOURCE_URANIUM',
             'RESOURCE_WHEAT', 'RESOURCE_COW', 'RESOURCE_SHEEP', 'RESOURCE_DEER', 'RESOURCE_FISH', 'RESOURCE_STONE', 'RESOURCE_BANANA',
             'RESOURCE_WHALE', 'RESOURCE_PEARLS', 'RESOURCE_DYE', 'RESOURCE_SALT', 'RESOURCE_WINE', 'RESOURCE_SPICES', 'RESOURCE_INCENSE', 'RESOURCE_MARBLE', 'RESOURCE_CRAB', 'RESOURCE_COPPER', 'RESOURCE_SUGAR']
RID = {r.split('_', 1)[1]: i for i, r in enumerate(RESOURCES)}
NONE = 0xFF
terrain = np.full((H, W), OCEAN, np.uint8); elev = np.zeros((H, W), np.uint8); feature = np.full((H, W), NONE, np.uint8)
wonder = np.full((H, W), NONE, np.uint8); resource = np.full((H, W), NONE, np.uint8); resamt = np.zeros((H, W), np.uint8); river = np.zeros((H, W), np.uint8)
def pick(x, y, salt, wts):
    r = rnd(x, y, salt); s = sum(wts.values()) or 1; acc = 0; last = None
    for k, v in wts.items():
        acc += v / s; last = k
        if r < acc: return k
    return last
for y in range(H):
    for x in range(W):
        if not is_land[y, x]:
            near = any(is_land[b, a] for a, b in neighbors(x, y)) or any(is_land[b2, a2] for a, b in neighbors(x, y) for a2, b2 in neighbors(a, b))
            terrain[y, x] = COAST if (near or depth[y, x] > -120) else OCEAN; continue
        key = ISLANDS[island[y, x]][0]; mn, mx, me = emin[y, x], emax[y, x], emean[y, x]; rl = mx - mn
        cx, cy = center(x, y); icx, icy = isl_c[island[y, x]]
        windward = (cx - icx) * 0.707 + (cy - icy) * 0.707 > -0.15 * HW * 3   # the north-east trade winds: wet windward, dry leeward
        # relief: shield volcanoes are gentle, the old islands are cut by deep valleys and pali cliffs
        if me >= 3400 or (rl >= 900 and me >= 600): elev[y, x] = 2
        elif rl >= 350 or me >= 1500 or (rl >= 200 and rnd(x, y, 'hill') < 0.5): elev[y, x] = 1
        elif rnd(x, y, 'hill') < 0.08: elev[y, x] = 1
        lava = key == 'HAWAII' and (lonlat(cx, cy)[1] < 19.45 or (lonlat(cx, cy)[0] > -155.4 and lonlat(cx, cy)[1] < 19.6))   # Kau and Puna lava fields
        if me >= 3800: wts = {SNOW: 0.8, TUNDRA: 0.2}; pf = 0.0; pj = 0.0
        elif me >= 2600: wts = {TUNDRA: 0.65, DESERT: 0.35}; pf = 0.0; pj = 0.0
        elif me >= 1500: wts = {PLAINS: 0.6, TUNDRA: 0.25, GRASS: 0.15}; pf = 0.45; pj = 0.0        # koa and ohia forest, the upland pastures
        elif key in ('NIIHAU', 'KAHOOLAWE'): wts = {DESERT: 0.5, PLAINS: 0.5}; pf = 0.0; pj = 0.0
        elif windward:
            if me >= 500: wts = {GRASS: 0.6, PLAINS: 0.4}; pf = 0.55; pj = 0.25
            else: wts = {GRASS: 0.7, PLAINS: 0.3}; pf = 0.1; pj = 0.55                                 # windward lowlands: rainforest and taro valleys
        else:
            if lava: wts = {DESERT: 0.7, PLAINS: 0.3}; pf = 0.0; pj = 0.0
            elif me >= 600: wts = {PLAINS: 0.55, GRASS: 0.35, DESERT: 0.1}; pf = 0.35; pj = 0.05
            else: wts = {PLAINS: 0.5, DESERT: 0.3, GRASS: 0.2}; pf = 0.05; pj = 0.05                    # leeward coasts: Kona, Kihei, Ewa, Waianae
        t = pick(x, y, 'terr', wts); terrain[y, x] = t
        if elev[y, x] == 2: continue
        r2 = rnd(x, y, 'feat')
        if t in (GRASS, PLAINS) and r2 < pj: feature[y, x] = JUNGLE
        elif t not in (DESERT, SNOW) and r2 < pj + pf: feature[y, x] = FOREST
        elif t == DESERT and elev[y, x] == 0 and not lava and rnd(x, y, 'oasis') < 0.03: feature[y, x] = OASIS

# shallow sills between neighbouring islands: coast tiles along the shortest crossing, so that embarked units and canoes can cross after Optics
# (the deep channels, above all the Kauai channel, would otherwise need Astronomy, which is disabled)
CROSSINGS = [('NIIHAU', 'KAUAI'), ('KAUAI', 'OAHU'), ('OAHU', 'MOLOKAI'), ('MOLOKAI', 'LANAI'), ('MOLOKAI', 'MAUI'), ('LANAI', 'MAUI'), ('MAUI', 'KAHOOLAWE'), ('MAUI', 'HAWAII')]
def shore(i): return [(x, y) for y in range(H) for x in range(W) if island[y, x] == i and any(not is_land[b, a] for a, b in neighbors(x, y))]
for a, b in CROSSINGS:
    sa, sb = shore(IKEY[a]), shore(IKEY[b])
    ta, tb = min(((p, q) for p in sa for q in sb), key=lambda pq: hexdist(*pq))
    # walk from ta to tb through the sea, greedily by hex distance, widening to two tiles
    cur = ta; path = []
    while cur != tb:
        cur = min(neighbors(*cur), key=lambda n: (hexdist(n, tb), rnd(n[0], n[1], 'sill'))); path.append(cur)
    for t in path:
        for u in [t] + neighbors(*t):
            if not is_land[u[1], u[0]] and rnd(u[0], u[1], 'sillw') < 0.7: terrain[u[1], u[0]] = COAST
    for t in path:
        if not is_land[t[1], t[0]]: terrain[t[1], t[0]] = COAST

# ============================================================== natural wonders, one per island
def find_tile(lon, lat, pred, radius=3):
    h0 = hex_ll(lon, lat)
    if h0 is None: return None
    seen = {h0}; q = deque([(h0, 0)])
    while q:
        t, d = q.popleft()
        if pred(*t): return t
        if d >= radius: continue
        for nb in neighbors(*t):
            if nb not in seen: seen.add(nb); q.append((nb, d + 1))
    return None
MOUNTAIN_WONDERS = {'FUJI', 'VOLCANO', 'SRI_PADA', 'MT_KAILASH', 'KILIMANJARO', 'MT_SINAI', 'GIBRALTAR'}
NATURAL_WONDERS = [  # island, English name, donor wonder, real site, needs coast
    ('HAWAII', 'Mauna Kea', 'KILIMANJARO', (-155.468, 19.821), False),
    ('HAWAII', 'Kilauea', 'VOLCANO', (-155.287, 19.41), False),
    ('MAUI', 'Haleakala', 'CRATER', (-156.17, 20.71), False),
    ('OAHU', 'Leahi', 'GIBRALTAR', (-157.805, 21.26), True),
    ('KAUAI', 'Waimea Canyon', 'MESA', (-159.66, 22.08), False),
    ('MOLOKAI', 'Kalaupapa', 'MT_KAILASH', (-156.97, 21.17), True),
    ('LANAI', 'Keahiakawelo', 'ULURU', (-156.98, 20.87), False),
]
wonder_tiles = {}
for key, name, w, (lon, lat), coast in NATURAL_WONDERS:
    def ok(x, y, coast=coast, key=key):
        if not is_land[y, x] or island[y, x] != IKEY[key] or wonder[y, x] != NONE: return False
        if coast and not any(not is_land[b, a] for a, b in neighbors(x, y)): return False
        return True
    t = find_tile(lon, lat, ok, 4)
    if t is None: raise SystemExit('no tile for wonder ' + name)
    wonder[t[1], t[0]] = WID[w]; feature[t[1], t[0]] = NONE; elev[t[1], t[0]] = 2 if w in MOUNTAIN_WONDERS else 0
    if terrain[t[1], t[0]] in (DESERT, SNOW, TUNDRA) and w in ('MESA', 'CRATER', 'ULURU', 'MT_KAILASH', 'GIBRALTAR'): terrain[t[1], t[0]] = PLAINS
    wonder_tiles[name] = t
print(f'  {len(wonder_tiles)} natural wonders placed')

# ============================================================== players and starts
PLAYERS = [  # slot order; 'island' is the island of the start, 'side' splits the Big Island between Kona and Hilo
    dict(key='KONA', island='HAWAII', civ='CIVILIZATION_POLYNESIA', leader='Kamehameha', name='Kona', start=(-155.83, 19.95)),          # Kawaihae, Kohala
    dict(key='HILO', island='HAWAII', civ='CIVILIZATION_JAPAN', leader='Keoua', name='Hilo', start=(-155.08, 19.72)),                   # Hilo bay
    dict(key='MAUI', island='MAUI', civ='CIVILIZATION_ZULU', leader='Kahekili', name='Maui', start=(-156.5, 20.89)),                    # Wailuku
    dict(key='OAHU', island='OAHU', civ='CIVILIZATION_CARTHAGE', leader='Kahahana', name='Oahu', start=(-157.84, 21.28)),              # Waikiki
    dict(key='KAUAI', island='KAUAI', civ='CIVILIZATION_ETHIOPIA', leader='Kamakahelei', name='Kauai', start=(-159.36, 22.05)),        # Wailua
]
CITY_STATES = [  # key, minor civ type, trait, site
    ('MOLOKAI', 'MINOR_CIV_HI_MOLOKAI', 'MINOR_TRAIT_RELIGIOUS', (-157.02, 21.09)),   # Kaunakakai
    ('LANAI', 'MINOR_CIV_HI_LANAI', 'MINOR_TRAIT_MARITIME', (-156.97, 20.74)),         # Kaunolu
    ('NIIHAU', 'MINOR_CIV_HI_NIIHAU', 'MINOR_TRAIT_MARITIME', (-160.15, 21.9)),        # Puuwai
]
NP = len(PLAYERS)
starts = []
for p in PLAYERS:
    def ok(x, y, p=p):
        if not is_land[y, x] or island[y, x] != IKEY[p['island']] or elev[y, x] == 2 or wonder[y, x] != NONE: return False
        if any(hexdist((x, y), t) <= 2 for t in wonder_tiles.values()): return False
        return any(not is_land[b, a] for a, b in neighbors(x, y))   # coastal capital
    t = find_tile(*p['start'], ok, 5)
    if t is None: raise SystemExit('cannot place start ' + p['key'])
    starts.append(t); feature[t[1], t[0]] = NONE
    if terrain[t[1], t[0]] == DESERT: terrain[t[1], t[0]] = PLAINS
print('  starts:', {p['key']: s for p, s in zip(PLAYERS, starts)})
# city-states: one city each with a little territory, as in Arcanum
owner = np.full((H, W), NONE, np.uint8); city_at = {}; city_tiles = []
for i, (key, mtype, trait, (lon, lat)) in enumerate(CITY_STATES):
    def ok(x, y, key=key):
        return is_land[y, x] and island[y, x] == IKEY[key] and elev[y, x] != 2 and wonder[y, x] == NONE and not any(hexdist((x, y), t) <= 1 for t in wonder_tiles.values()) \
               and any(not is_land[b, a] for a, b in neighbors(x, y))
    t = find_tile(lon, lat, ok, 5)
    if t is None: raise SystemExit('cannot place city-state ' + key)
    city_at[t] = i; city_tiles.append(t); feature[t[1], t[0]] = NONE
    if terrain[t[1], t[0]] in (DESERT, TUNDRA): terrain[t[1], t[0]] = PLAINS
    for xx, yy in ring(t, 2):
        if is_land[yy, xx] or any(is_land[b, a] for a, b in neighbors(xx, yy)): owner[yy, xx] = 32 + i
print('  city-states:', {k[0]: t for k, t in zip(CITY_STATES, city_tiles)})

# ============================================================== resources: balanced per island
def place(res, t, amt=1):
    resource[t[1], t[0]] = RID[res]; resamt[t[1], t[0]] = amt
def candidates(i, pred): return [(x, y) for y in range(H) for x in range(W) if island[y, x] == i and resource[y, x] == NONE and wonder[y, x] == NONE and (x, y) not in city_at and pred(x, y)]
def spread(i, res, n, pred, amt=1, salt='', mind=3):
    cs = sorted(candidates(i, pred), key=lambda t: rnd(t[0], t[1], res + salt)); placed = []
    for t in cs:
        if len(placed) >= n: break
        if all(hexdist(t, u) >= mind for u in placed) and all(hexdist(t, s) >= 2 for s in starts + city_tiles): placed.append(t); place(res, t, amt)
    return len(placed)
def sea_near(i, pred):   # sea tiles within two hexes of island i
    out = []
    for y in range(H):
        for x in range(W):
            if is_land[y, x] or terrain[y, x] != COAST or resource[y, x] != NONE: continue
            if any(0 <= a < W and 0 <= b < H and island[b, a] == i for a, b in ring((x, y), 2)) and pred(x, y): out.append((x, y))
    return out
flat = lambda x, y: elev[y, x] == 0 and feature[y, x] == NONE
hill = lambda x, y: elev[y, x] == 1 and feature[y, x] == NONE
jungle = lambda x, y: feature[y, x] == JUNGLE and elev[y, x] < 2
forest = lambda x, y: feature[y, x] == FOREST and elev[y, x] < 2
nomtn = lambda x, y: elev[y, x] < 2 and feature[y, x] != OASIS and terrain[y, x] not in (SNOW, TUNDRA)
# no iron and no horses: the islands had no metal and no large animals; Hawaiian food is taro, sweet potato, breadfruit, pigs and the sea
for i, (key, name, _) in enumerate(ISLANDS):
    n = int((island == i).sum()); big = n >= 300; mid = n >= 90; small = n < 40
    q = (lambda a, b, c: a if big else b if mid else c)
    spread(i, 'BANANA', q(6, 3, 1), lambda x, y: jungle(x, y) or (flat(x, y) and terrain[y, x] == GRASS), mind=3)   # taro and breadfruit
    spread(i, 'WHEAT', q(4, 2, 1), lambda x, y: flat(x, y) and terrain[y, x] in (GRASS, PLAINS), mind=4)              # sweet potato fields
    spread(i, 'DEER', q(3, 2, 0), forest, mind=4)                                                                      # pigs and fowl of the forest
    spread(i, 'STONE', q(4, 2, 1), lambda x, y: nomtn(x, y) and feature[y, x] == NONE, mind=5)
    lux = {'HAWAII': ['INCENSE', 'SALT', 'DYE', 'SUGAR', 'INCENSE'], 'MAUI': ['SUGAR', 'INCENSE', 'DYE'], 'OAHU': ['SALT', 'SUGAR', 'DYE'], 'KAUAI': ['INCENSE', 'SUGAR', 'SALT'],
           'MOLOKAI': ['SALT', 'DYE'], 'LANAI': ['DYE'], 'NIIHAU': ['SALT'], 'KAHOOLAWE': []}[key]   # sandalwood (incense), salt pans, olena dye, sugarcane
    for k, r in enumerate(lux):
        spread(i, r, 1, lambda x, y, r=r: nomtn(x, y) and (feature[y, x] == NONE or r in ('DYE', 'SUGAR', 'INCENSE')) and (terrain[y, x] != DESERT or r == 'SALT'), mind=4, salt=str(k))
    sea = sorted(sea_near(i, lambda x, y: True), key=lambda t: rnd(t[0], t[1], 'sea'))
    quota = {'FISH': q(8, 4, 2), 'WHALE': q(2, 1, 0), 'CRAB': q(2, 1, 0), 'PEARLS': q(2, 1, 1)}
    placed = []
    for res, qn in quota.items():
        for t in sea:
            if qn <= 0: break
            if resource[t[1], t[0]] == NONE and all(hexdist(t, u) >= 3 for u in placed): place(res, t); placed.append(t); qn -= 1
print('  resources:', {r.split('_', 1)[1]: int((resource == i).sum()) for i, r in enumerate(RESOURCES) if (resource == i).any()})

# ============================================================== units and scenario data
# the escort is the chiefdom's own warrior where the Warrior class is replaced
START_WARRIOR = {'KONA': 'POLYNESIAN_MAORI_WARRIOR'}
UNITS = ['UNIT_SETTLER', 'UNIT_WARRIOR', 'UNIT_WORKER'] + ['UNIT_' + u for u in START_WARRIOR.values()]
UID = {u.split('_', 1)[1]: i for i, u in enumerate(UNITS)}
PROMOS = ['PROMOTION_DRILL_1']
units = []
for i, s in enumerate(starts):
    units.append(dict(type='SETTLER', owner=i, x=s[0], y=s[1])); units.append(dict(type=START_WARRIOR.get(PLAYERS[i]['key'], 'WARRIOR'), owner=i, x=s[0], y=s[1]))
for i, t in enumerate(city_tiles):
    units.append(dict(type='WARRIOR', owner=32 + i, x=t[0], y=t[1])); units.append(dict(type='WORKER', owner=32 + i, x=t[0], y=t[1]))
TECHS = ['TECH_AGRICULTURE']    # everyone's free tech anyway; the list must not be empty
BUILDINGS = ['BUILDING_PALACE', 'BUILDING_MONUMENT', 'BUILDING_WALLS']
POLICIES = ['POLICY_TRADITION']
IMPROVEMENTS = ['IMPROVEMENT_FARM', 'IMPROVEMENT_GOODY_HUT']
VICTORIES = ['VICTORY_DOMINATION']    # no science (tech stops after the Classical era), no diplomacy (no World Congress without Printing Press), no culture (no tourism to speak of before the Renaissance); VICTORY_TIME is not listed either, so the game does not end at the turn limit
GAMEOPTIONS = ['GAMEOPTION_NO_TUTORIAL', 'GAMEOPTION_NO_LEAGUES']
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
P = NP; CS = len(CITY_STATES); T = P + CS
tile_units = defaultdict(list)
for i, u in enumerate(units): tile_units[(u['x'], u['y'])].append(i)
next_of = {}
for lst in tile_units.values():
    for a, b in zip(lst, lst[1:]): next_of[a] = b
ucap = pow2(len(units) + 1); urec = bytearray()
for i in range(ucap):
    if i < len(units):
        u = units[i]
        status = 0x01 if u['type'] not in ('SETTLER', 'WORKER') else 0
        if (u['x'], u['y']) in city_at and u['type'] == 'WARRIOR': status |= 0x04   # garrison
        urec += struct.pack('<HHIIIBBBB', next_of.get(i, 0xFFFF), 0xFFFF, 0, 100000, UID[u['type']], u['owner'], 0, status, 0)
        urec += bytes(64)
    else:
        urec += struct.pack('<HHIIIBBBB', i + 1 if i + 1 < ucap else 0xFFFF, 0xFFFF, 0, 0, 0xFFFFFFFF, 0, 0, 0, 0) + bytes(64)
unit_data = struct.pack('<I', len(units)) + bytes(urec)
ccap = pow2(len(CITY_STATES) + 1); crec = bytearray(); BID = {b: i for i, b in enumerate(BUILDINGS)}
for i in range(ccap):
    if i < len(CITY_STATES):
        crec += cfix(CITY_STATES[i][0].title(), 64) + struct.pack('<BBHI', 32 + i, 0, 3, 100000) + bitset(['BUILDING_MONUMENT', 'BUILDING_WALLS'], BID, 64)
    else: crec += bytes(136)
city_data = struct.pack('<I', len(CITY_STATES)) + bytes(crec)
def relbits(pairs):
    nbits = T * (T - 1) // 2; b = bytearray((nbits + 7) // 8)
    for i, j in pairs:
        lg, sm = max(i, j), min(i, j); k = lg * (lg - 1) // 2 + sm; b[k // 8] |= 1 << (k % 8)
    return bytes(b)
rel = relbits([]) * 5           # nobody has met anybody
influence = bytes(P * 64 * 4)
visibility = bytes((W * H * T + 7) // 8)
team_data = b''.join(cfix(f'Team {i + 1}', 32) + bitset(TECHS, {t: k for k, t in enumerate(TECHS)}, 32) for i in range(T))
player_data = b''
for i, p in enumerate(PLAYERS):
    player_data += bitset([], {n: k for k, n in enumerate(POLICIES)}, 32)
    player_data += cfix(p['leader'], 64) + cfix(p['name'], 64) + cfix(p['civ'], 64) + cfix(f"PLAYERCOLOR_HI1778_{p['key']}", 64) + cfix('ERA_ANCIENT', 64) + cfix('HANDICAP_PRINCE', 64)
    player_data += struct.pack('<IIIIBB2s', 0, 0, starts[i][0], starts[i][1], i, 1, b'\0\0')
for i, (key, mtype, trait, pos) in enumerate(CITY_STATES):
    player_data += bytes(32) + cfix('', 64) + cfix('', 64) + cfix(mtype, 64) + cfix('PLAYERCOLOR_MINOR_WHITE', 64) + cfix('ERA_ANCIENT', 64) + cfix('HANDICAP_CHIEFTAIN', 64)
    player_data += struct.pack('<IIIIBB2s', 0, 0, city_tiles[i][0], city_tiles[i][1], P + i, 0, b'\0\0')
# ancient ruins: placed here rather than by the game's randomiser, about one per 25 land tiles, away from the starts and wonders
improvement = np.full((H, W), NONE, np.uint8); huts = []
for y in range(H):
    for x in range(W):
        if is_land[y, x] and elev[y, x] < 2 and wonder[y, x] == NONE and resource[y, x] == NONE and rnd(x, y, 'hut') < 0.08 \
           and all(hexdist((x, y), s) >= 3 for s in starts + city_tiles) and owner[y, x] == NONE and all(hexdist((x, y), h) >= 4 for h in huts):
            improvement[y, x] = IMPROVEMENTS.index('IMPROVEMENT_GOODY_HUT'); huts.append((x, y))
print(f'  {len(huts)} ancient ruins')
plot_data = bytearray()
for y in range(H):
    for x in range(W):
        uid = tile_units[(x, y)][0] if (x, y) in tile_units else 0xFFFF
        plot_data += struct.pack('<HHBBBB', city_at.get((x, y), 0xFFFF), uid, owner[y, x], improvement[y, x], NONE, NONE)
terr_b, feat_b, wond_b, res_b = strlist(TERRAINS), strlist(FEATURES), strlist(WONDERS), strlist(RESOURCES)
name_b = MOD_NAME.encode() + b'\0'
desc_b = (b'The Hawaiian Islands in 1778, on the eve of contact: Hawaii, Maui, Oahu, Kauai, Molokai, Lanai, Niihau and Kahoolawe at 4 km per hex from NOAA ETOPO 2022 relief. '
          b'Five chiefdoms start from a Settler in the Ancient era, three lesser islands are city-states, one natural wonder per island, '
          b'no iron and no horses, normal barbarians, one turn = one year, development capped at the Classical era. Domination victory only.\0')
world_b = b'WORLDSIZE_STANDARD'.ljust(64, b'\0')
imp_b, unit_b, tech_b, pol_b, bld_b, prom_b = strlist(IMPROVEMENTS), strlist(UNITS), strlist(TECHS), strlist(POLICIES), strlist(BUILDINGS), strlist(PROMOS)
vict_b, opt_b = plist(VICTORIES), plist(GAMEOPTIONS)
with open(OUT_MAP, 'wb') as f:
    f.write(struct.pack('<BIIB', 0x8C, W, H, P)); f.write(bytes(4))     # no randomisation flags: resources and ruins are placed above
    f.write(struct.pack('<7I', len(terr_b), len(feat_b), len(wond_b), len(res_b), 0, len(name_b), len(desc_b)))
    f.write(terr_b + feat_b + wond_b + res_b + name_b + desc_b + struct.pack('<I', 64) + world_b)
    for y in range(H):
        for x in range(W):
            f.write(bytes([terrain[y, x], resource[y, x], feature[y, x], river[y, x], elev[y, x], 4 if is_land[y, x] else 0, wonder[y, x], resamt[y, x]]))
    f.write(struct.pack('<64sIIIiBBBB9I', SPEED.encode(), 0, 0, 0, 1778, P, CS, T, 0, len(imp_b), len(unit_b), len(tech_b), len(pol_b), len(bld_b), len(prom_b), len(unit_data), 0, len(city_data)))
    f.write(struct.pack('<II', len(vict_b), len(opt_b)))
    f.write(imp_b + unit_b + tech_b + pol_b + bld_b + prom_b + unit_data + city_data + vict_b + opt_b + rel + influence + visibility)
    f.write(team_data + player_data + bytes(plot_data))
land_n = int(is_land.sum())
print(f'wrote {OUT_MAP} {os.path.getsize(OUT_MAP)} bytes; land {land_n} ({land_n/(W*H):.1%}) mountains {int((elev==2).sum())} hills {int((elev==1).sum())} forest {int((feature==FOREST).sum())} coast {int((terrain==COAST).sum())}')
json.dump(dict(starts=starts, city_tiles=city_tiles, wonders={k: list(v) for k, v in wonder_tiles.items()}, W=W, H=H), open(os.path.join(HERE, 'map_layout.json'), 'w'), indent=1)

# ============================================================== preview
S = 7
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
        if feature[y, x] == OASIS: col = (60, 190, 120)
        d.polygon(pcorners(x, y), fill=col); cx, cy = pcenter(x, y)
        if elev[y, x] == 2: d.polygon([(cx - 3, cy + 2), (cx, cy - 3), (cx + 3, cy + 2)], fill=(70, 60, 60))
        elif elev[y, x] == 1: d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5], outline=(100, 70, 40))
        if wonder[y, x] != NONE: d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 0, 255))
        elif resource[y, x] != NONE: d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5], fill=(255, 255, 255))
for p, s in zip(PLAYERS, starts):
    cx, cy = pcenter(*s); d.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 215, 0), outline=(0, 0, 0)); d.text((cx + 6, cy - 6), p['name'], fill=(255, 230, 120))
for name, t in wonder_tiles.items():
    cx, cy = pcenter(*t); d.text((cx + 5, cy + 2), name, fill=(255, 150, 255))
for (key, *_), t in zip(CITY_STATES, city_tiles):
    cx, cy = pcenter(*t); d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255), outline=(0, 0, 0)); d.text((cx + 6, cy - 6), key.title(), fill=(255, 255, 255))
img.save(OUT_PNG); print('preview', OUT_PNG)

# ============================================================== mod wrapper
import glob
UI_FILES = ['Hawaii1778LoadScreen.lua', 'Hawaii1778LoadScreen.xml', 'Hawaii1778_Rules.xml', 'Hawaii1778_Uniques.sql', 'Hawaii1778_Policies.sql', 'Hawaii1778_Text.xml']
VFS_FILES = ['SocialPolicyPopup.lua', 'SocialPolicyPopup.xml']   # the policy screen with the scenario branches (imported into the game's VFS)
for fn in UI_FILES: shutil.copy(os.path.join(HERE, 'ui', fn), os.path.join(OUT_DIR, fn))
for fn in VFS_FILES: shutil.copy(os.path.join(HERE, 'ui', fn), os.path.join(OUT_DIR, fn))
shutil.copy(os.path.join(HERE, 'CREDITS.txt'), os.path.join(OUT_DIR, 'CREDITS.txt'))
# --- leader art (art/build_art.py output): static diplomacy scenes, portrait atlas, civ symbol atlases, Dawn of Man images
ART = os.path.join(HERE, 'art', 'out'); art_files = []
for f in sorted(glob.glob(os.path.join(ART, '*.dds'))):
    shutil.copy(f, os.path.join(OUT_DIR, os.path.basename(f))); art_files.append(os.path.basename(f))
DONOR_LEADER = {'KONA': 'LEADER_KAMEHAMEHA', 'HILO': 'LEADER_ODA_NOBUNAGA', 'MAUI': 'LEADER_SHAKA', 'OAHU': 'LEADER_DIDO', 'KAUAI': 'LEADER_SELASSIE'}
scene_files = []
if art_files:
    for p in PLAYERS:
        fn = f"HI1778_{p['key']}_Scene.xml"; scene_files.append(fn)
        open(os.path.join(OUT_DIR, fn), 'w').write(f'<?xml version="1.0" encoding="utf-8"?>\n<LeaderScene FallbackImage="HI1778_Scene_{p["key"]}.dds">\n</LeaderScene>\n')
    lx = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Hawaii 1778: generated leader art wired in (Firaxis Civil War technique): static scenes, portrait atlas, civ symbols, Dawn of Man images. -->', '<GameData>', '  <IconTextureAtlases>']
    for size in (256, 128, 64): lx.append(f'    <Row><Atlas>HI1778_LEADER_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>HI1778_Leaders{size}.dds</Filename><IconsPerRow>{NP}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    for size in (256, 128, 80, 64, 45, 32): lx.append(f'    <Row><Atlas>HI1778_CIV_COLOR_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>HI1778_CivColor{size}.dds</Filename><IconsPerRow>{NP}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    for size in (128, 64, 48, 32, 24, 16): lx.append(f'    <Row><Atlas>HI1778_CIV_ALPHA_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>HI1778_CivWhite{size}.dds</Filename><IconsPerRow>{NP}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    lx += ['  </IconTextureAtlases>', '  <Leaders>']
    for i, p in enumerate(PLAYERS): lx.append(f'    <Update><Where Type="{DONOR_LEADER[p["key"]]}" /><Set ArtDefineTag="HI1778_{p["key"]}_Scene.xml" PortraitIndex="{i}" IconAtlas="HI1778_LEADER_ATLAS" /></Update>')
    lx += ['  </Leaders>', '  <Civilizations>']
    for i, p in enumerate(PLAYERS): lx.append(f'    <Update><Where Type="{p["civ"]}" /><Set PortraitIndex="{i}" IconAtlas="HI1778_CIV_COLOR_ATLAS" AlphaIconAtlas="HI1778_CIV_ALPHA_ATLAS" DawnOfManImage="HI1778_DOM_{p["key"]}.dds" /></Update>')
    lx += ['  </Civilizations>']
    if 'HI1778_Units256.dds' in art_files:   # unique unit and building icons (art/build_art.py)
        sys.path.insert(0, os.path.join(HERE, 'text')); import uniques
        lx += ['  <IconTextureAtlases>']
        for size in (256, 128, 80, 64, 45, 32): lx.append(f'    <Row><Atlas>HI1778_UNIT_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>HI1778_Units{size}.dds</Filename><IconsPerRow>{NP}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
        lx.append(f'    <Row><Atlas>HI1778_UNIT_FLAG_ATLAS</Atlas><IconSize>32</IconSize><Filename>HI1778_UnitFlags32.dds</Filename><IconsPerRow>{NP}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
        nb = len([b for b in uniques.BUILDINGS if b['base']])
        for size in (256, 128, 64, 45): lx.append(f'    <Row><Atlas>HI1778_BUILDING_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>HI1778_Buildings{size}.dds</Filename><IconsPerRow>{nb}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
        lx += ['  </IconTextureAtlases>', '  <Units>']
        for i, u in enumerate(uniques.UNITS): lx.append(f'    <Update><Where Type="{"UNIT_HI1778_" + u["key"] if u["base"] else u["unit_type"]}" /><Set PortraitIndex="{i}" IconAtlas="HI1778_UNIT_ATLAS" UnitFlagAtlas="HI1778_UNIT_FLAG_ATLAS" UnitFlagIconOffset="{i}" /></Update>')
        lx += ['  </Units>', '  <Buildings>']
        for i, b in enumerate([b for b in uniques.BUILDINGS if b['base']]): lx.append(f'    <Update><Where Type="BUILDING_HI1778_{b["key"]}" /><Set PortraitIndex="{i}" IconAtlas="HI1778_BUILDING_ATLAS" /></Update>')
        lx += ['  </Buildings>']
        imps = [b for b in uniques.BUILDINGS if b.get('improvement')]
        if imps:
            lx += ['  <IconTextureAtlases>']
            for size in (256, 64): lx.append(f'    <Row><Atlas>HI1778_IMPROVEMENT_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>HI1778_Improvements{size}.dds</Filename><IconsPerRow>{len(imps)}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
            for size in (64, 45): lx.append(f'    <Row><Atlas>HI1778_ACTION_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>HI1778_Actions{size}.dds</Filename><IconsPerRow>{len(imps)}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
            lx += ['  </IconTextureAtlases>', '  <Improvements>'] + [f'    <Update><Where Type="{b["improvement"]}" /><Set PortraitIndex="{i}" IconAtlas="HI1778_IMPROVEMENT_ATLAS" /></Update>' for i, b in enumerate(imps)]
            lx += ['  </Improvements>', '  <Builds>'] + [f'    <Update><Where Type="{b["build"]}" /><Set IconIndex="{i}" IconAtlas="HI1778_ACTION_ATLAS" /></Update>' for i, b in enumerate(imps)] + ['  </Builds>']
        if 'HI1778_Religions128.dds' in art_files:   # the stock religions become Hawaiian cults (names in the text file, symbols here)
            RELIGIONS = ['BUDDHISM', 'CHRISTIANITY', 'CONFUCIANISM', 'HINDUISM', 'ISLAM', 'JUDAISM', 'SHINTO', 'SIKHISM', 'TAOISM', 'TENGRIISM', 'ZOROASTRIANISM', 'ORTHODOXY', 'PROTESTANTISM']
            lx += ['  <IconTextureAtlases>'] + [f'    <Row><Atlas>HI1778_RELIGION_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>HI1778_Religions{size}.dds</Filename><IconsPerRow>{len(RELIGIONS)}</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>' for size in (128, 80, 64, 48, 32, 24, 16)]
            lx += ['  </IconTextureAtlases>', '  <Religions>'] + [f'    <Update><Where Type="RELIGION_{r}" /><Set PortraitIndex="{i}" IconAtlas="HI1778_RELIGION_ATLAS" /></Update>' for i, r in enumerate(RELIGIONS)] + ['  </Religions>']
    lx += ['</GameData>', '']
    open(os.path.join(OUT_DIR, 'Hawaii1778_Leaders.xml'), 'w').write('\n'.join(lx))
    print(f'  art: {len(art_files)} textures, {len(scene_files)} scenes')
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest().upper()
FILES = [('Hawaii1778.Civ5Map', 1)] + [(fn, 0) for fn in UI_FILES] + [(fn, 1) for fn in VFS_FILES] + [('CREDITS.txt', 0)]
if art_files: FILES += [('Hawaii1778_Leaders.xml', 0)] + [(f, 1) for f in scene_files] + [(f, 1) for f in art_files]
files_xml = '\n'.join(f'    <File md5="{md5(os.path.join(OUT_DIR, fn))}" import="{imp}">{fn}</File>' for fn, imp in FILES)
leaders_db = '      <UpdateDatabase>Hawaii1778_Leaders.xml</UpdateDatabase>\n' if art_files else ''
MODINFO = f'''<?xml version="1.0" encoding="utf-8"?>
<Mod id="{MOD_ID}" version="1">
  <Properties>
    <Name>Hawaii 1778</Name>
    <Teaser>The Hawaiian Islands on the eve of contact: five chiefdoms, three lesser islands, one natural wonder per island.</Teaser>
    <Description>The Hawaiian Islands in 1778, on a {W}x{H} hex map (4 km per hex) built from NOAA ETOPO 2022 relief: trade-wind rainforest to windward, dry coasts to leeward, snow on Mauna Kea. Kamehameha's Kona and Keoua's Hilo share the Big Island; Kahekili's Maui, Kahahana's Oahu and Kamakahelei's Kauai each start from a Settler and a Warrior in the Ancient era; Molokai, Lanai and Niihau are city-states. One natural wonder per island (Mauna Kea, Kilauea, Haleakala, Leahi, Waimea Canyon, Kalaupapa, Keahiakawelo), no iron and no horses, stock rules, normal barbarians, Standard speed, one turn = one year, development capped at the Classical era, domination victory only. Start it from Mods, Single Player, Scenarios.</Description>
    <Authors>cryptoboy2283</Authors>
    <SpecialThanks>NOAA ETOPO 2022, Civ5MapImage, Black Forest Labs FLUX (leader art)</SpecialThanks>
    <AffectsSavedGames>1</AffectsSavedGames>
    <MinCompatibleSaveVersion>0</MinCompatibleSaveVersion>
    <SupportsSinglePlayer>1</SupportsSinglePlayer>
    <SupportsMultiplayer>0</SupportsMultiplayer>
    <SupportsHotSeat>0</SupportsHotSeat>
    <SupportsMac>1</SupportsMac>
    <ReloadAudioSystem>0</ReloadAudioSystem>
    <ReloadLandmarkSystem>0</ReloadLandmarkSystem>
    <ReloadLeaderSystem>{1 if art_files else 0}</ReloadLeaderSystem>
    <ReloadStrategicViewSystem>0</ReloadStrategicViewSystem>
    <ReloadUnitSystem>0</ReloadUnitSystem>
  </Properties>
  <Dependencies>
    <Dlc id="0E3751A1-F840-4e1b-9706-519BF484E59D" minversion="0" maxversion="999" />
    <Dlc id="6DA07636-4123-4018-B643-6575B4EC336B" minversion="0" maxversion="999" />
  </Dependencies>
  <References />
  <Blocks />
  <Files>
{files_xml}
  </Files>
  <Actions>
    <OnModActivated>
      <UpdateDatabase>Hawaii1778_Rules.xml</UpdateDatabase>
      <UpdateDatabase>Hawaii1778_Uniques.sql</UpdateDatabase>
      <UpdateDatabase>Hawaii1778_Policies.sql</UpdateDatabase>
{leaders_db}      <UpdateDatabase>Hawaii1778_Text.xml</UpdateDatabase>
    </OnModActivated>
  </Actions>
  <EntryPoints>
    <EntryPoint type="Custom" file="Hawaii1778LoadScreen.xml">
      <Name>Hawaii 1778</Name>
      <Description>The Hawaiian Islands before contact. Choose your chiefdom and difficulty.</Description>
    </EntryPoint>
  </EntryPoints>
</Mod>
'''
open(os.path.join(OUT_DIR, 'Hawaii1778.modinfo'), 'w').write(MODINFO)
print('wrote modinfo')
