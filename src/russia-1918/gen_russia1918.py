#!/usr/bin/env python3
"""Russia 1918: Civilization V scenario map of the Russian Civil War, 1 June 1918.

Region: from East Prussia and Finland to Irkutsk, from Murmansk to Transcaspia, 160 hexes wide (about 43 km per hex).
Data: Natural Earth 10m (land, lakes, rivers, first-level regions), NOAA ETOPO 2022 relief, Koppen-Geiger climate.
Factions (June 1918): RSFSR (Russia), the White South (Germany donor), Siberia / Kolchak (Shoshone), the Northern Region and
later Yudenich (England), the Ukrainian State (Ethiopia), Poland (Poland); border states as city-states; Makhno, the Greens
and the Basmachi as raging barbarians. One turn = one week; Quick speed; domination only, no timed victories.
"""
import json, math, os, struct, hashlib, heapq, shutil, glob
from collections import defaultdict, Counter, deque
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('HEX_DATA', os.path.join(HERE, '..', '..', 'data'))        # tools/fetch_data.py
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
MOD_NAME = 'Russia 1918'
OUT_DIR = os.path.join(HERE, 'mod', 'Russia 1918 (v 3)')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_MAP = os.path.join(OUT_DIR, 'Russia1918.Civ5Map')
OUT_PNG = os.path.join(HERE, 'Russia1918_preview.png')

# ============================================================== projection / grid (Albers equal-area conic)
R = 6371.0; LON0 = 62.0
PHI1, PHI2 = math.radians(47.0), math.radians(65.0)
N = (math.sin(PHI1) + math.sin(PHI2)) / 2.0
C = math.cos(PHI1) ** 2 + 2 * N * math.sin(PHI1)
RHO0 = R * math.sqrt(C - 2 * N * math.sin(math.radians(56.0))) / N
def proj(lon, lat):
    phi = math.radians(lat); lam = math.radians(lon - LON0)
    rho = R * math.sqrt(C - 2 * N * math.sin(phi)) / N; th = N * lam
    return rho * math.sin(th), RHO0 - rho * math.cos(th)
def inv_np(x, y):
    dy = RHO0 - y; rho = np.sign(N) * np.sqrt(x * x + dy * dy)
    th = np.arctan2(np.sign(N) * x, np.sign(N) * dy)
    phi = np.arcsin((C - (rho * N / R) ** 2) / (2 * N))
    return np.degrees(th / N) + LON0, np.degrees(phi)

LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = 18.0, 106.0, 37.5, 70.5
W = 160
pts = [proj(LON_MIN + (LON_MAX - LON_MIN) * i / 200, la) for i in range(201) for la in (LAT_MIN, LAT_MAX)] + \
      [proj(lo, LAT_MIN + (LAT_MAX - LAT_MIN) * i / 200) for i in range(201) for lo in (LON_MIN, LON_MAX)]
XMIN = min(p[0] for p in pts); XMAX = max(p[0] for p in pts); YMIN = min(p[1] for p in pts); YMAX = max(p[1] for p in pts)
HW = (XMAX - XMIN) / W; HR = HW / math.sqrt(3); ROWH = 1.5 * HR
H = int(math.ceil((YMAX - YMIN - 2 * HR) / ROWH)) + 1
print(f'grid {W}x{H}, hex {HW:.1f} km, extent {XMAX-XMIN:.0f} x {YMAX-YMIN:.0f} km')

def center(x, y): return XMIN + (x + 0.5 + 0.5 * (y & 1)) * HW, YMIN + HR + y * ROWH
def corners(x, y):
    cx, cy = center(x, y)
    return [(cx + HR * math.cos(math.radians(30 + 60 * k)), cy + HR * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
def neighbors(x, y):
    cand = [(x + 1, y), (x - 1, y), (x, y + 1), (x + 1, y + 1), (x, y - 1), (x + 1, y - 1)] if y & 1 else \
           [(x + 1, y), (x - 1, y), (x - 1, y + 1), (x, y + 1), (x - 1, y - 1), (x, y - 1)]
    return [(a, b) for a, b in cand if 0 <= a < W and 0 <= b < H]
def hex_at(px, py):
    ry = int(round((py - YMIN - HR) / ROWH)); best = None
    for yy in range(ry - 1, ry + 2):
        if not 0 <= yy < H: continue
        rx = int(round((px - XMIN) / HW - 0.5 - 0.5 * (yy & 1)))
        for xx in range(rx - 1, rx + 2):
            if not 0 <= xx < W: continue
            cx, cy = center(xx, yy); d = (cx - px) ** 2 + (cy - py) ** 2
            if best is None or d < best[0]: best = (d, xx, yy)
    return (best[1], best[2]) if best else None
def hex_ll(lon, lat): return hex_at(*proj(lon, lat))
def lonlat(x, y):
    cx, cy = center(x, y); lo, la = inv_np(np.array([cx]), np.array([cy])); return float(lo[0]), float(la[0])
def hexdist(a, b):
    def cube(x, y):
        q = x - (y - (y & 1)) // 2; return q, y, -q - y
    aq, ar, as_ = cube(*a); bq, br, bs = cube(*b)
    return max(abs(aq - bq), abs(ar - br), abs(as_ - bs))
def rnd(x, y, salt):
    return int.from_bytes(hashlib.md5(f'{x},{y},{salt}'.encode()).digest()[:4], 'little') / 2 ** 32

SAMP = []
for i in range(9):
    for j in range(9):
        sx = (i + 0.5) / 9 * HW - HW / 2; sy = (j + 0.5) / 9 * 2 * HR - HR
        if abs(sx) <= HW / 2 and abs(sy) <= HR - abs(sx) / math.sqrt(3) + 1e-9: SAMP.append((sx, sy))
SAMP = np.array(SAMP)

# ============================================================== factions and regions
# Major players (map slot order). Donor civs are chosen for their traits; names and leaders are replaced by the text file.
PLAYERS = [
    dict(key='RED', civ='CIVILIZATION_RUSSIA', leader='Vladimir Lenin', name='Russian SFSR', color='PLAYERCOLOR_RUS1918_RED', gold=2500),
    dict(key='SOUTH', civ='CIVILIZATION_GERMANY', leader='Anton Denikin', name='White South', color='PLAYERCOLOR_RUS1918_SOUTH', gold=1200),
    dict(key='SIB', civ='CIVILIZATION_SHOSHONE', leader='Alexander Kolchak', name='Siberia', color='PLAYERCOLOR_RUS1918_SIB', gold=1500),
    dict(key='NORTH', civ='CIVILIZATION_ENGLAND', leader='Nikolai Yudenich', name='Northern Region', color='PLAYERCOLOR_RUS1918_NORTH', gold=1800),
    dict(key='UKR', civ='CIVILIZATION_ETHIOPIA', leader='Pavlo Skoropadsky', name='Ukrainian State', color='PLAYERCOLOR_RUS1918_UKR', gold=1000),
    dict(key='POL', civ='CIVILIZATION_POLAND', leader='Jozef Pilsudski', name='Poland', color='PLAYERCOLOR_RUS1918_POL', gold=1200),
]
PIDX = {p['key']: i for i, p in enumerate(PLAYERS)}
RED, SOUTH, SIB, NORTH, UKR, POL = range(6)
NP = len(PLAYERS)
BARB = 96
NONE = 0xFF
# City-states: (key, EN name of the city, type, trait, lon, lat, population in thousands)
CITY_STATES = [
    ('FINLAND', 'Helsinki', 'MINOR_CIV_RUS1918_FINLAND', 'MINOR_TRAIT_MILITARISTIC', 24.94, 60.17, 180),
    ('ESTONIA', 'Reval', 'MINOR_CIV_RUS1918_ESTONIA', 'MINOR_TRAIT_MARITIME', 24.75, 59.44, 150),
    ('LATVIA', 'Riga', 'MINOR_CIV_RUS1918_LATVIA', 'MINOR_TRAIT_MILITARISTIC', 24.10, 56.95, 500),
    ('LITHUANIA', 'Vilna', 'MINOR_CIV_RUS1918_LITHUANIA', 'MINOR_TRAIT_MERCANTILE', 25.28, 54.69, 200),   # the Taryba's seat; Kovno became the capital only in 1920
    ('GERMANY', 'Konigsberg', 'MINOR_CIV_RUS1918_GERMANY', 'MINOR_TRAIT_MILITARISTIC', 20.50, 54.71, 250),
    ('ROMANIA', 'Kishinev', 'MINOR_CIV_RUS1918_ROMANIA', 'MINOR_TRAIT_MILITARISTIC', 28.86, 47.01, 120),
    ('GEORGIA', 'Tiflis', 'MINOR_CIV_RUS1918_GEORGIA', 'MINOR_TRAIT_CULTURED', 44.80, 41.72, 350),
    ('AZERBAIJAN', 'Baku', 'MINOR_CIV_RUS1918_AZERBAIJAN', 'MINOR_TRAIT_MERCANTILE', 49.87, 40.40, 250),
    ('ARMENIA', 'Erivan', 'MINOR_CIV_RUS1918_ARMENIA', 'MINOR_TRAIT_CULTURED', 44.51, 40.18, 30),
    ('OTTOMAN', 'Kars', 'MINOR_CIV_RUS1918_OTTOMAN', 'MINOR_TRAIT_MILITARISTIC', 43.10, 40.61, 20),
    ('PERSIA', 'Tabriz', 'MINOR_CIV_RUS1918_PERSIA', 'MINOR_TRAIT_MERCANTILE', 46.30, 38.08, 200),
    ('BUKHARA', 'Bukhara', 'MINOR_CIV_RUS1918_BUKHARA', 'MINOR_TRAIT_MERCANTILE', 64.43, 39.78, 75),
    ('KHIVA', 'Khiva', 'MINOR_CIV_RUS1918_KHIVA', 'MINOR_TRAIT_MERCANTILE', 60.36, 41.38, 20),
]
NCS = len(CITY_STATES)
CSIDX = {c[0]: i for i, c in enumerate(CITY_STATES)}
# Natural Earth first-level regions -> faction holding them on 1 June 1918. Values: player key or city-state key.
R_RED = ['Moscow', 'Saint Petersburg', 'Leningrad', 'Novgorod', 'Pskov', 'Tver', 'Smolensk', 'Bryansk', 'Kaluga', 'Tula', 'Oryol', 'Kursk', 'Voronezh',
         'Lipetsk', 'Tambov', 'Ryazan', 'Vladimir', 'Ivanovo', 'Yaroslavl', 'Kostroma', 'Vologda', 'Nizhny Novgorod', 'Mari El Republic', 'Chuvash Republic',
         'Republic of Mordovia', 'Penza', 'Ulyanovsk', 'Republic of Tatarstan', 'Kirov', 'Udmurt Republic', 'Perm Krai', 'Sverdlovsk', 'Saratov', 'Volgograd',
         'Astrakhan', 'Republic of Kalmykia', 'Stavropol Krai', 'Karachay-Cherkess Republic', 'Kabardino-Balkaria', 'Republic of North Ossetia-Alania',
         'Republic of Ingushetia', 'Chechen Republic', 'Republic of Dagestan', 'Karelia', 'Komi Republic', 'Vitebsk', 'Mahilioŭ', 'Gomel', 'Minsk',
         'Aktobe', 'Almaty', 'Jambyl', 'Turkistan', 'Kyzylorda', 'Tashkent', 'Fergana', 'Andijan', 'Namangan', 'Jizzakh', 'Sirdaryo', 'Samarqand',
         'Ahal', 'Balkan', 'Mary', 'Lebap', 'Chuy', 'Bishkek', 'Talas', 'Issyk-Kul', 'Naryn', 'Jalal-Abad', 'Osh', 'Batken', 'Khujand']
R_SOUTH = ['Rostov', 'Krasnodar Krai', 'Republic of Adygea']
R_SIB = ['Samara', 'Bashkortostan', 'Orenburg', 'Chelyabinsk', 'Kurgan', 'Tyumen', 'Omsk', 'Novosibirsk', 'Tomsk', 'Kemerovo', 'Altai Republic',
         'Krasnoyarsk Krai', 'Republic of Khakassia', 'Irkutsk', 'West Kazakhstan', 'Atyrau', 'Kostanay', 'North Kazakhstan', 'Akmola', 'Nur-Sultan',
         'Pavlodar', 'Karaganda', 'East Kazakhstan']
R_NORTH = ['Arkhangelsk', 'Murmansk', 'Nenets Autonomous Okrug']
R_UKR = ['Cherkasy', 'Chernihiv', 'Dnipropetrovsk', 'Donetsk', 'Kharkiv', 'Kherson', 'Khmelnytskyi', 'Kirovohrad', 'Kyiv', 'Luhansk', 'Mykolaiv', 'Odessa',
         'Poltava', 'Rivne', 'Sumy', 'Vinnytsia', 'Volyn', 'Zaporizhzhia', 'Zhytomyr', 'Ternopil', 'Ivano-Frankivsk', 'Autonomous Republic of Crimea',
         'Sevastopol', 'Belgorod', 'Transnistria']
R_POL = ['Greater Poland Voivodeship', 'Kuyavian-Pomeranian Voivodeship', 'Lesser Poland Voivodeship', 'Lower Silesian Voivodeship', 'Lublin Voivodeship',
         'Lubusz Voivodeship', 'Masovian Voivodeship', 'Opole Voivodeship', 'Podkarpackie Voivodeship', 'Podlaskie Voivodeship', 'Pomeranian Voivodeship',
         'Silesian Voivodeship', 'Warmian-Masurian Voivodeship', 'West Pomeranian Voivodeship', 'Łódź Voivodeship', 'Świętokrzyskie Voivodeship',
         'Lviv', 'Alytus', 'Marijampolė', 'Grodno', 'Brest']
REGION_OF = {}
for lst, key in ((R_RED, 'RED'), (R_SOUTH, 'SOUTH'), (R_SIB, 'SIB'), (R_NORTH, 'NORTH'), (R_UKR, 'UKR'), (R_POL, 'POL')):
    for n in lst: REGION_OF[n] = key
CS_ADMIN = {'Finland': 'FINLAND', 'Estonia': 'ESTONIA', 'Latvia': 'LATVIA', 'Lithuania': 'LITHUANIA', 'Romania': 'ROMANIA', 'Moldova': 'ROMANIA',
            'Georgia': 'GEORGIA', 'Azerbaijan': 'AZERBAIJAN', 'Armenia': 'ARMENIA', 'Turkey': 'OTTOMAN', 'Iran': 'PERSIA'}
CS_REGION = {'Kaliningrad': 'GERMANY', 'Bukhara': 'BUKHARA', 'Navoiy': 'BUKHARA', 'Qashqadaryo': 'BUKHARA', 'Surxondaryo': 'BUKHARA',
             'Xorazm': 'KHIVA', 'Karakalpakstan': 'KHIVA', 'Daşoguz': 'KHIVA'}
def faction_code(f):
    p = f['properties']; adm = p.get('admin'); nm = p.get('name_en') or p.get('name')
    if nm in CS_REGION: return 100 + CSIDX[CS_REGION[nm]]
    if nm in REGION_OF and adm in ('Russia', 'Ukraine', 'Belarus', 'Kazakhstan', 'Poland', 'Lithuania', 'Uzbekistan', 'Turkmenistan', 'Kyrgyzstan', 'Tajikistan', 'Moldova'):
        return 1 + PIDX[REGION_OF[nm]]
    if adm in CS_ADMIN: return 100 + CSIDX[CS_ADMIN[adm]]
    return None

# ============================================================== rasters
PX = 12
IW, IH = W * PX, int(math.ceil((YMAX - YMIN) / HW * PX))
def to_px(p): return ((p[0] - XMIN) / HW * PX, IH - (p[1] - YMIN) / HW * PX)
def rings_of(f):
    g = f['geometry']
    if g is None: return
    geoms = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
    for poly in geoms:
        ring = poly[0]; lons = [p[0] for p in ring]; lats = [p[1] for p in ring]
        if max(lons) < LON_MIN - 12 or min(lons) > LON_MAX + 12 or max(lats) < LAT_MIN - 6 or min(lats) > LAT_MAX + 6: continue
        if max(lons) - min(lons) > 300: continue   # antimeridian-wrapping polygons (Russia's whole outline in some files)
        yield poly
def rasterize(feats, value_of):
    img = Image.new('L', (IW, IH), 0); d = ImageDraw.Draw(img)
    for f in feats:
        v = value_of(f)
        if v is None: continue
        for poly in rings_of(f):
            d.polygon([to_px(proj(lo, la)) for lo, la in poly[0]], fill=v)
            for hole in poly[1:]: d.polygon([to_px(proj(lo, la)) for lo, la in hole], fill=0)
    return np.array(img)

print('rasterizing land / lakes / regions...')
LAND = rasterize(json.load(open(f'{DATA}/ne_10m_land.geojson'))['features'], lambda f: 255) > 127
lakes = json.load(open(f'{DATA}/ne_10m_lakes.geojson'))['features'] + json.load(open(f'{DATA}/ne_10m_lakes_europe.geojson'))['features']
LAKES = rasterize(lakes, lambda f: 255) > 127
LAND = LAND & ~LAKES
admin1 = json.load(open(f'{DATA}/ne_10m_admin_1_states_provinces.geojson'))['features']
FACT = rasterize(admin1, faction_code)
seen_regions = {(f['properties'].get('name_en') or f['properties'].get('name')) for f in admin1 if faction_code(f) is not None}
missing = [n for n in REGION_OF if n not in seen_regions]
if missing: print('  !! regions not found in Natural Earth:', missing)

print('loading ETOPO / Koppen...')
ETOPO = np.array(Image.open(f'{DATA}/etopo_ru.tif'))   # bbox 17..108 E, 37..72 N, 1820x700 -> 0.05 deg
def etopo_at(lon, lat):
    c = np.clip(((lon - 17.0) / 0.05).astype(int), 0, 1819); r = np.clip(((72.0 - lat) / 0.05).astype(int), 0, 699)
    return ETOPO[r, c]
# Koppen 0.5 deg grid as a nearest-filled raster over the region (the ASCII file lists land cells only)
KLAT0, KLON0, KN, KM = LAT_MIN - 2, LON_MIN - 2, int((LAT_MAX - LAT_MIN + 4) * 2) + 1, int((LON_MAX - LON_MIN + 4) * 2) + 1
kgrid = np.full((KN, KM), -1, int); kclasses = []
for line in open(f'{DATA}/koppen/Koeppen-Geiger-ASCII.txt'):
    p = line.split()
    if len(p) != 3 or p[0] == 'Lat': continue
    la, lo = float(p[0]), float(p[1])
    if KLAT0 <= la < LAT_MAX + 2 and KLON0 <= lo < LON_MAX + 2:
        if p[2] not in kclasses: kclasses.append(p[2])
        kgrid[int((la - KLAT0) * 2), int((lo - KLON0) * 2)] = kclasses.index(p[2])
idx = ndimage.distance_transform_edt(kgrid < 0, return_distances=False, return_indices=True)
kgrid = kgrid[idx[0], idx[1]]
def kop_at(lon, lat):
    return kclasses[kgrid[int(np.clip((lat - KLAT0) * 2, 0, KN - 1)), int(np.clip((lon - KLON0) * 2, 0, KM - 1))]]

import pickle
CACHE = os.path.join(DATA, 'cache', f'russia1918_sample_{W}x{H}.pkl'); os.makedirs(os.path.dirname(CACHE), exist_ok=True)
landfrac = np.zeros((H, W)); lakefrac = np.zeros((H, W)); emean = np.zeros((H, W)); emax = np.zeros((H, W))
relief = np.zeros((H, W)); depth = np.zeros((H, W)); fact = np.zeros((H, W), int); clim = [[None] * W for _ in range(H)]
if os.path.exists(CACHE) and not os.environ.get('RU_NOCACHE'):
    print('loading cached hex samples...'); landfrac, lakefrac, emean, emax, relief, depth, fact, clim = pickle.load(open(CACHE, 'rb'))
else:
  print('sampling hexes...')
  for y in range(H):
      for x in range(W):
          cx, cy = center(x, y); sx = SAMP[:, 0] + cx; sy = SAMP[:, 1] + cy
          pc = np.clip(((sx - XMIN) / HW * PX).astype(int), 0, IW - 1); pr = np.clip((IH - (sy - YMIN) / HW * PX).astype(int), 0, IH - 1)
          landfrac[y, x] = LAND[pr, pc].mean(); lakefrac[y, x] = LAKES[pr, pc].mean()
          cc = FACT[pr, pc][LAND[pr, pc]]
          fact[y, x] = Counter(cc.tolist()).most_common(1)[0][0] if len(cc) else 0
          lon, lat = inv_np(sx, sy); e = etopo_at(lon, lat); el = e[e > 0] if (e > 0).any() else e
          emean[y, x] = el.mean(); emax[y, x] = el.max()
          relief[y, x] = np.percentile(el, 95) - np.percentile(el, 5) if len(el) > 3 else 0
          depth[y, x] = e[e <= 0].mean() if (e <= 0).any() else 0
          comp = defaultdict(float)
          for lo, la in zip(lon[::3], lat[::3]): comp[kop_at(lo, la)] += 1
          clim[y][x] = comp
  pickle.dump((landfrac, lakefrac, emean, emax, relief, depth, fact, clim), open(CACHE, 'wb'))

# ============================================================== type lists
TERRAINS = ['TERRAIN_GRASS', 'TERRAIN_PLAINS', 'TERRAIN_DESERT', 'TERRAIN_TUNDRA', 'TERRAIN_SNOW', 'TERRAIN_COAST', 'TERRAIN_OCEAN']
GRASS, PLAINS, DESERT, TUNDRA, SNOW, COAST, OCEAN = range(7)
FEATURES = ['FEATURE_ICE', 'FEATURE_JUNGLE', 'FEATURE_MARSH', 'FEATURE_OASIS', 'FEATURE_FLOOD_PLAINS', 'FEATURE_FOREST', 'FEATURE_FALLOUT']
ICE, JUNGLE, MARSH, OASIS, FLOOD, FOREST, FALLOUT = range(7)
WONDERS = ['FEATURE_CRATER', 'FEATURE_FUJI', 'FEATURE_MESA', 'FEATURE_REEF', 'FEATURE_VOLCANO', 'FEATURE_GIBRALTAR', 'FEATURE_GEYSER',
           'FEATURE_FOUNTAIN_YOUTH', 'FEATURE_POTOSI', 'FEATURE_EL_DORADO', 'FEATURE_SRI_PADA', 'FEATURE_MT_SINAI', 'FEATURE_MT_KAILASH', 'FEATURE_ULURU']
RESOURCES = ['RESOURCE_IRON', 'RESOURCE_HORSE', 'RESOURCE_COAL', 'RESOURCE_OIL', 'RESOURCE_ALUMINUM', 'RESOURCE_URANIUM', 'RESOURCE_WHEAT',
             'RESOURCE_COW', 'RESOURCE_SHEEP', 'RESOURCE_DEER', 'RESOURCE_BANANA', 'RESOURCE_FISH', 'RESOURCE_STONE', 'RESOURCE_WHALE',
             'RESOURCE_PEARLS', 'RESOURCE_GOLD', 'RESOURCE_SILVER', 'RESOURCE_GEMS', 'RESOURCE_MARBLE', 'RESOURCE_IVORY', 'RESOURCE_FUR',
             'RESOURCE_DYE', 'RESOURCE_SPICES', 'RESOURCE_SILK', 'RESOURCE_SUGAR', 'RESOURCE_COTTON', 'RESOURCE_WINE', 'RESOURCE_INCENSE',
             'RESOURCE_COPPER', 'RESOURCE_SALT', 'RESOURCE_CRAB', 'RESOURCE_TRUFFLES', 'RESOURCE_CITRUS']
RID = {n.split('_', 1)[1]: i for i, n in enumerate(RESOURCES)}
terrain = np.full((H, W), OCEAN, np.uint8); elev = np.zeros((H, W), np.uint8); feature = np.full((H, W), NONE, np.uint8)
wonder = np.full((H, W), NONE, np.uint8); resource = np.full((H, W), NONE, np.uint8); resamt = np.zeros((H, W), np.uint8); river = np.zeros((H, W), np.uint8)

is_lake = lakefrac >= 0.5
is_land = (landfrac >= 0.45) & ~is_lake

# ============================================================== terrain classification
MARSH_BOXES = [(23.5, 31.0, 51.0, 53.0, 0.30), (62.0, 88.0, 56.0, 63.5, 0.22), (39.0, 41.5, 55.0, 56.0, 0.15), (30.0, 34.0, 56.5, 60.0, 0.10)]   # Polesia, West Siberian plain, Meshchera, Ilmen lowland
for y in range(H):
    for x in range(W):
        if is_lake[y, x]: terrain[y, x] = COAST; continue
        lo, la = lonlat(x, y)
        if not is_land[y, x]:
            shallow = depth[y, x] > -120 or any(is_land[b, a] for a, b in neighbors(x, y))
            terrain[y, x] = COAST if shallow else OCEAN
            if la > 69.8 and lo > 44: feature[y, x] = ICE
            continue
        rl, mx, mn = relief[y, x], emax[y, x], emean[y, x]
        if rl >= 750 or (mx >= 2700 and rl >= 500): elev[y, x] = 2
        elif rl >= 230 or (mn >= 1200 and rl >= 130): elev[y, x] = 1
        comp = clim[y][x]; tot = sum(comp.values()) or 1
        def frac(pred): return sum(v for k, v in comp.items() if pred(k)) / tot
        fET = frac(lambda k: k.startswith('E'))
        fSub = frac(lambda k: k in ('Dfc', 'Dfd', 'Dwc', 'Dwd', 'Dsc'))
        fCont = frac(lambda k: k in ('Dfb', 'Dwb', 'Dsb'))
        fWarm = frac(lambda k: k in ('Dfa', 'Dwa', 'Dsa') or k.startswith('Cf') or k.startswith('Cs'))
        fSteppe = frac(lambda k: k.startswith('BS'))
        fDesert = frac(lambda k: k.startswith('BW'))
        if mn >= 2800 or (fET > 0.5 and mn > 1200) or la > 71: t = SNOW
        else:
            wts = {TUNDRA: fET + fSub * (0.75 if la >= 61 else 0.35), PLAINS: fSub * (0.25 if la >= 61 else 0.50) + fCont * 0.45 + fWarm * 0.55 + fSteppe * 0.70,
                   GRASS: fSub * (0.0 if la >= 61 else 0.15) + fCont * 0.55 + fWarm * 0.45 + fSteppe * 0.05, DESERT: fDesert + fSteppe * 0.25}
            r = rnd(x, y, 'terr'); sw = sum(wts.values()) or 1; acc = 0; t = PLAINS
            for k, v in wts.items():
                acc += v / sw
                if r < acc: t = k; break
        terrain[y, x] = t
        if elev[y, x] == 2 or t == SNOW: continue
        pf = fSub * 0.65 + fCont * (0.50 if la >= 55 else 0.32) + fWarm * 0.12 + fET * 0.10
        if t == DESERT: pf = 0
        pm = 0
        for lo0, lo1, la0, la1, pmb in MARSH_BOXES:
            if lo0 <= lo <= lo1 and la0 <= la <= la1 and elev[y, x] == 0 and t in (GRASS, PLAINS, TUNDRA): pm = pmb
        r2 = rnd(x, y, 'feat')
        if r2 < pm: feature[y, x] = MARSH
        elif r2 < pm + pf: feature[y, x] = FOREST
        elif t == DESERT and elev[y, x] == 0 and r2 > 0.97: feature[y, x] = OASIS

# ============================================================== rivers
print('tracing rivers...')
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
    if hx is None: return None
    return ckey(min(corners(*hx), key=lambda p: (p[0] - px) ** 2 + (p[1] - py) ** 2))
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
river_feats = []
for f in json.load(open(f'{DATA}/ne_10m_rivers_lake_centerlines.geojson'))['features']:
    p = f['properties']; nm = p.get('name') or ''
    if 'Canal' in nm or 'canal' in nm or p.get('featurecla') == 'Lake Centerline': continue
    if (p.get('scalerank') or 99) > 7: continue
    g = f['geometry']; lines = [g['coordinates']] if g['type'] == 'LineString' else g['coordinates']
    for line in lines:
        if any(LON_MIN < lo < LON_MAX and LAT_MIN < la < LAT_MAX for lo, la in line): river_feats.append((nm or f'r{len(river_feats)}', line))
river_edges = defaultdict(list)
for nm, line in river_feats:
    P = [proj(lo, la) for lo, la in line]
    e0 = float(etopo_at(np.array([line[0][0]]), np.array([line[0][1]]))[0]); e1 = float(etopo_at(np.array([line[-1][0]]), np.array([line[-1][1]]))[0])
    if e1 > e0: P = P[::-1]
    dense = []
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
    river_edges[nm].extend(zip(clean, clean[1:]))
def land_tile(t): return 0 <= t[0] < W and 0 <= t[1] < H and is_land[t[1], t[0]]
n_edges = 0
for nm, edges in river_edges.items():
    good = []
    for a, b in edges:
        e = EDGES.get(frozenset((a, b)))
        if not e: continue
        x, y, side, ff = e
        if land_tile((x, y)) and land_tile(across(x, y, side)): good.append((x, y, side, a == ff))
    if len(good) < 3: continue
    for x, y, side, fwd in good:
        bit, flow = {'E': (1, 8), 'SE': (2, 16), 'SW': (4, 32)}[side]
        if river[y, x] & bit: continue
        river[y, x] |= bit | (flow if fwd else 0); n_edges += 1
print(f'  {n_edges} river edges from {len(river_edges)} rivers')
def has_river(x, y):
    if river[y, x] & 7: return True
    for a, b in neighbors(x, y):
        for side, bit in (('E', 1), ('SE', 2), ('SW', 4)):
            if across(a, b, side) == (x, y) and river[b, a] & bit: return True
    return False
for y in range(H):   # flood plains on desert river banks (Amu Darya, Syr Darya, lower Volga)
    for x in range(W):
        if is_land[y, x] and terrain[y, x] == DESERT and elev[y, x] == 0 and has_river(x, y) and rnd(x, y, 'flood') < 0.6: feature[y, x] = FLOOD

# ============================================================== resources
def find_tile(lon, lat, pred, radius=2):
    h0 = hex_ll(lon, lat)
    if h0 is None: return None
    px, py = proj(lon, lat); seen = {h0}; q = deque([(h0, 0)])
    while q:
        t, d = q.popleft()
        if pred(*t): return t
        if d >= radius: continue
        for nb in sorted(neighbors(*t), key=lambda n: (center(*n)[0] - px) ** 2 + (center(*n)[1] - py) ** 2):
            if nb not in seen: seen.add(nb); q.append((nb, d + 1))
    return None
def place_res(res, lon, lat, amt=1, water=False):
    def ok(x, y):
        if resource[y, x] != NONE: return False
        if water: return not is_land[y, x]
        return is_land[y, x] and elev[y, x] != 2 and feature[y, x] != MARSH and terrain[y, x] != SNOW
    t = find_tile(lon, lat, ok, 2)
    if t is None: print('  !! no tile for', res, lon, lat); return
    resource[t[1], t[0]] = RID[res]; resamt[t[1], t[0]] = amt
    if res in ('IRON', 'COAL', 'GOLD', 'SILVER', 'GEMS', 'COPPER', 'SALT') and elev[t[1], t[0]] == 0 and rnd(*t, 'hill') < 0.6: elev[t[1], t[0]] = 1
    if res in ('WHEAT', 'HORSE', 'COW', 'COTTON') and feature[t[1], t[0]] in (FOREST, MARSH): feature[t[1], t[0]] = NONE
HAND_RES = [
    # coal: Donbass, Kuzbass, Karaganda, Cheremkhovo, Kizel, Dombrowa
    ('COAL', 37.8, 48.1, 6), ('COAL', 38.4, 48.3, 6), ('COAL', 39.0, 48.0, 4), ('COAL', 87.1, 54.0, 6), ('COAL', 86.5, 55.3, 4), ('COAL', 73.1, 49.8, 4),
    ('COAL', 103.1, 53.15, 4), ('COAL', 57.6, 59.05, 4), ('COAL', 19.2, 50.3, 4), ('COAL', 38.2, 54.0, 2), ('COAL', 65.6, 54.8, 2),
    # iron: Krivoy Rog, Kerch, Urals (Magnitnaya, Nizhny Tagil, Bakal), Tula, Kursk anomaly, Olonets
    ('IRON', 33.4, 47.9, 6), ('IRON', 33.6, 48.1, 4), ('IRON', 36.4, 45.25, 2), ('IRON', 59.05, 53.4, 6), ('IRON', 59.95, 57.9, 4), ('IRON', 58.8, 54.95, 4),
    ('IRON', 37.4, 54.3, 2), ('IRON', 37.0, 51.3, 2), ('IRON', 33.2, 61.2, 2), ('IRON', 85.5, 53.5, 2),
    # oil: Baku, Grozny, Maikop, Emba, Cheleken, Fergana, Ukhta
    ('OIL', 49.6, 40.5, 6), ('OIL', 49.3, 40.7, 4), ('OIL', 45.6, 43.4, 6), ('OIL', 40.0, 44.7, 3), ('OIL', 56.3, 47.4, 3), ('OIL', 53.1, 39.4, 2), ('OIL', 71.8, 40.4, 2), ('OIL', 53.7, 63.5, 2),
    # horses: Don, Kuban, Orenburg and Kazakh steppe, Trans-Volga, Transbaikal fringe
    ('HORSE', 41.5, 47.8, 4), ('HORSE', 43.0, 48.6, 2), ('HORSE', 40.5, 45.6, 4), ('HORSE', 42.5, 46.5, 2), ('HORSE', 54.0, 51.5, 4), ('HORSE', 56.5, 52.5, 2), ('HORSE', 62.0, 52.5, 2),
    ('HORSE', 66.5, 51.5, 4), ('HORSE', 71.0, 51.6, 2), ('HORSE', 78.0, 50.5, 2), ('HORSE', 48.0, 50.5, 2), ('HORSE', 77.0, 43.6, 2), ('HORSE', 92.0, 54.3, 2), ('HORSE', 37.0, 49.0, 2),
    ('HORSE', 46.0, 44.5, 2), ('HORSE', 26.5, 50.0, 2), ('HORSE', 22.5, 51.5, 2), ('HORSE', 83.0, 51.0, 2), ('HORSE', 51.0, 50.5, 2),
    # gold, silver, gems, copper, salt, marble, stone
    ('GOLD', 60.8, 56.9, 1), ('GOLD', 61.6, 54.4, 1), ('GOLD', 61.3, 52.9, 1), ('GOLD', 86.7, 52.7, 1), ('GOLD', 104.6, 54.8, 1), ('SILVER', 82.2, 51.2, 1), ('SILVER', 60.7, 59.0, 1),
    ('GEMS', 61.5, 57.6, 1), ('GEMS', 60.2, 56.6, 1), ('COPPER', 60.2, 55.5, 1), ('COPPER', 67.7, 47.8, 1), ('COPPER', 59.4, 58.3, 1), ('COPPER', 44.2, 43.4, 1),
    ('SALT', 46.9, 48.2, 1), ('SALT', 46.6, 49.1, 1), ('SALT', 42.0, 51.2, 1), ('SALT', 19.9, 49.9, 1), ('SALT', 33.6, 45.8, 1), ('SALT', 57.9, 51.9, 1), ('SALT', 90.0, 55.0, 1),
    ('MARBLE', 34.0, 61.5, 1), ('MARBLE', 33.4, 44.6, 1), ('MARBLE', 59.5, 56.6, 1), ('STONE', 36.0, 56.3, 1), ('STONE', 30.5, 59.0, 1), ('STONE', 24.0, 50.4, 1), ('STONE', 50.4, 53.4, 1),
    # luxuries: wine, cotton, silk, citrus, furs, dyes, truffles, sugar beet as sugar, incense none
    ('WINE', 34.0, 44.5, 1), ('WINE', 28.5, 46.7, 1), ('WINE', 45.5, 41.8, 1), ('WINE', 30.1, 46.3, 1), ('WINE', 39.9, 44.9, 1), ('WINE', 48.1, 46.5, 1),
    ('COTTON', 71.4, 40.5, 1), ('COTTON', 72.3, 40.9, 1), ('COTTON', 68.5, 40.6, 1), ('COTTON', 61.9, 37.7, 1), ('COTTON', 60.5, 41.6, 1), ('COTTON', 48.3, 40.0, 1),
    ('SILK', 71.0, 41.0, 1), ('SILK', 66.8, 39.7, 1), ('SILK', 47.0, 41.0, 1), ('CITRUS', 41.6, 41.7, 1), ('CITRUS', 39.7, 43.6, 1),
    ('FUR', 83.5, 60.5, 1), ('FUR', 90.0, 60.0, 1), ('FUR', 97.0, 57.5, 1), ('FUR', 75.0, 60.0, 1), ('FUR', 55.0, 63.5, 1), ('FUR', 48.0, 64.5, 1), ('FUR', 42.0, 66.0, 1),
    ('FUR', 62.0, 60.5, 1), ('FUR', 102.0, 56.5, 1), ('FUR', 68.0, 62.5, 1), ('FUR', 31.0, 62.5, 1), ('FUR', 86.0, 58.0, 1),
    ('DYE', 31.0, 49.0, 1), ('DYE', 34.7, 50.3, 1), ('TRUFFLES', 29.0, 52.5, 1), ('TRUFFLES', 24.6, 53.3, 1), ('TRUFFLES', 41.0, 56.5, 1),
    ('SUGAR', 29.9, 49.6, 1), ('SUGAR', 35.0, 50.2, 1), ('SUGAR', 37.5, 51.5, 1), ('SUGAR', 33.5, 50.7, 1), ('SUGAR', 21.5, 50.7, 1),
    ('SPICES', 69.5, 41.8, 1), ('INCENSE', 44.9, 40.5, 1),
    # sea: fish, whales
    ('FISH', 28.0, 59.7, 1), ('FISH', 23.0, 57.5, 1), ('FISH', 22.5, 59.3, 1), ('FISH', 20.0, 55.3, 1), ('FISH', 37.0, 65.0, 1), ('FISH', 39.5, 64.7, 1), ('FISH', 35.5, 69.3, 1),
    ('FISH', 32.0, 46.4, 1), ('FISH', 36.5, 46.1, 1), ('FISH', 38.0, 46.8, 1), ('FISH', 33.0, 44.3, 1), ('FISH', 48.3, 45.5, 1), ('FISH', 50.5, 44.0, 1), ('FISH', 51.3, 46.3, 1), ('FISH', 49.5, 41.5, 1),
    ('FISH', 60.5, 45.5, 1), ('FISH', 74.5, 46.5, 1), ('FISH', 107.5, 52.5, 1), ('FISH', 31.5, 60.8, 1), ('FISH', 35.5, 61.8, 1), ('FISH', 53.0, 40.8, 1), ('FISH', 73.0, 61.0, 1),
    ('WHALE', 36.0, 66.0, 1), ('WHALE', 34.0, 69.9, 1), ('WHALE', 44.0, 69.6, 1), ('WHALE', 50.0, 70.0, 1), ('CRAB', 39.0, 69.4, 1), ('CRAB', 37.5, 65.6, 1),
]
for res, lo, la, amt in HAND_RES: place_res(res, lo, la, amt, water=res in ('FISH', 'CRAB', 'PEARLS', 'WHALE'))
for y in range(H):
    for x in range(W):
        if resource[y, x] != NONE: continue
        r = rnd(x, y, 'scatter'); lo, la = lonlat(x, y)
        if is_land[y, x]:
            if elev[y, x] == 2 or terrain[y, x] == SNOW: continue
            t, f = terrain[y, x], feature[y, x]
            black_earth = t in (GRASS, PLAINS) and 44 < la < 56 and lo < 90
            if f == FOREST and t == TUNDRA and r < 0.07: resource[y, x] = RID['FUR']; resamt[y, x] = 1
            elif f == FOREST and r < 0.08: resource[y, x] = RID['DEER']; resamt[y, x] = 1
            elif f == NONE and black_earth and elev[y, x] == 0 and r < 0.11: resource[y, x] = RID['WHEAT']; resamt[y, x] = 1
            elif f == NONE and t in (GRASS, PLAINS) and elev[y, x] == 0 and r < 0.045: resource[y, x] = RID['WHEAT']; resamt[y, x] = 1
            elif f == NONE and t == GRASS and r < 0.09: resource[y, x] = RID['COW']; resamt[y, x] = 1
            elif f == NONE and elev[y, x] == 1 and t != DESERT and r < 0.09: resource[y, x] = RID['SHEEP']; resamt[y, x] = 1
            elif f == NONE and t in (DESERT, PLAINS) and 0.90 < r < 0.925: resource[y, x] = RID['SHEEP']; resamt[y, x] = 1
            elif f == NONE and t == PLAINS and elev[y, x] == 0 and 0.95 < r < 0.958: resource[y, x] = RID['HORSE']; resamt[y, x] = 2
            elif f in (NONE, FOREST) and 0.93 < r < 0.94: resource[y, x] = RID['STONE']; resamt[y, x] = 1
            elif elev[y, x] == 1 and 0.96 < r < 0.968: resource[y, x] = RID['IRON']; resamt[y, x] = 2
            elif t == TUNDRA and f == NONE and r < 0.05: resource[y, x] = RID['DEER']; resamt[y, x] = 1
        elif terrain[y, x] == COAST and not is_lake[y, x]:
            nl = sum(is_land[b, a] for a, b in neighbors(x, y))
            if (nl > 0 and r < 0.08) or (nl == 0 and r < 0.03): resource[y, x] = RID['FISH']; resamt[y, x] = 1

# ============================================================== players / ownership
owner = np.full((H, W), NONE, np.uint8)
for y in range(H):
    for x in range(W):
        if not is_land[y, x] or fact[y, x] == 0: continue
        owner[y, x] = fact[y, x] - 1 if fact[y, x] < 100 else 32 + fact[y, x] - 100

# ============================================================== cities
# (name, lon, lat, owner, population in thousands around 1917, tags: cap base port)
CITIES = [
    # --- RSFSR
    ('Moscow', 37.62, 55.75, RED, 1800, 'cap base'), ('Petrograd', 30.32, 59.94, RED, 2300, 'base port'), ('Tver', 35.90, 56.86, RED, 60, ''), ('Yaroslavl', 39.87, 57.63, RED, 120, ''),
    ('Kostroma', 40.93, 57.77, RED, 70, ''), ('Ivanovo-Voznesensk', 40.98, 57.00, RED, 150, ''), ('Vladimir', 40.41, 56.13, RED, 40, ''), ('Nizhny Novgorod', 44.00, 56.33, RED, 150, 'base'),
    ('Ryazan', 39.74, 54.63, RED, 50, ''), ('Tula', 37.62, 54.20, RED, 140, 'base'), ('Kaluga', 36.26, 54.51, RED, 55, ''), ('Smolensk', 32.05, 54.78, RED, 75, ''),
    ('Bryansk', 34.37, 53.24, RED, 30, ''), ('Oryol', 36.08, 52.97, RED, 90, ''), ('Kursk', 36.19, 51.73, RED, 80, ''), ('Voronezh', 39.20, 51.67, RED, 95, ''),
    ('Tambov', 41.45, 52.72, RED, 70, ''), ('Penza', 45.00, 53.20, RED, 80, ''), ('Saratov', 46.03, 51.53, RED, 240, 'base'), ('Tsaritsyn', 44.52, 48.70, RED, 130, 'base'),
    ('Astrakhan', 48.04, 46.35, RED, 150, 'port'), ('Kazan', 49.12, 55.79, RED, 200, 'base'), ('Simbirsk', 48.40, 54.32, RED, 70, ''), ('Vyatka', 49.67, 58.60, RED, 50, ''),
    ('Perm', 56.25, 58.01, RED, 70, ''), ('Ekaterinburg', 60.60, 56.84, RED, 70, ''), ('Vologda', 39.89, 59.22, RED, 50, ''), ('Petrozavodsk', 34.36, 61.79, RED, 20, ''),
    ('Novgorod', 31.27, 58.52, RED, 30, ''), ('Pskov', 28.33, 57.82, RED, 35, ''), ('Velikie Luki', 30.52, 56.34, RED, 15, ''), ('Vitebsk', 30.20, 55.19, RED, 110, ''),
    ('Mogilev', 30.33, 53.90, RED, 70, ''), ('Gomel', 30.98, 52.44, RED, 100, ''), ('Minsk', 27.56, 53.90, RED, 100, ''), ('Orsha', 30.42, 54.51, RED, 20, ''),
    ('Polotsk', 28.78, 55.49, RED, 25, ''), ('Rzhev', 34.33, 56.26, RED, 25, ''), ('Kozlov', 40.50, 52.90, RED, 45, ''), ('Borisoglebsk', 42.08, 51.37, RED, 35, ''),
    ('Balashov', 43.17, 51.55, RED, 25, ''), ('Kamyshin', 45.40, 50.08, RED, 25, ''), ('Syzran', 48.47, 53.16, RED, 50, ''), ('Stavropol', 41.97, 45.05, RED, 60, ''),
    ('Pyatigorsk', 43.05, 44.04, RED, 30, ''), ('Vladikavkaz', 44.68, 43.03, RED, 75, ''), ('Grozny', 45.69, 43.32, RED, 35, ''), ('Petrovsk', 47.50, 42.98, RED, 25, 'port'),
    ('Derbent', 48.29, 42.06, RED, 30, ''), ('Kizlyar', 46.72, 43.85, RED, 10, ''), ('Izhevsk', 53.20, 56.85, RED, 40, ''), ('Sarapul', 53.80, 56.47, RED, 25, ''),
    ('Yelets', 38.50, 52.62, RED, 50, ''), ('Rybinsk', 38.86, 58.05, RED, 30, ''), ('Cherepovets', 37.90, 59.13, RED, 10, ''),     ('Staraya Russa', 31.36, 57.99, RED, 20, ''), ('Vyshny Volochyok', 34.56, 57.59, RED, 20, ''), ('Murom', 42.05, 55.57, RED, 15, ''), ('Arzamas', 43.84, 55.39, RED, 15, ''),
    ('Saransk', 45.18, 54.19, RED, 15, ''), ('Kineshma', 42.17, 57.44, RED, 20, ''), ('Morshansk', 41.83, 53.44, RED, 30, ''),
    ('Ust-Sysolsk', 50.84, 61.67, RED, 7, ''), ('Kotlas', 46.65, 61.25, RED, 5, ''), ('Alatyr', 46.58, 54.84, RED, 20, ''),
    ('Bobruisk', 29.23, 53.15, RED, 40, ''), ('Borisov', 28.50, 54.23, RED, 15, ''), ('Chistopol', 50.64, 55.36, RED, 20, ''), ('Yelabuga', 52.06, 55.76, RED, 10, ''),
    ('Orsk', 58.57, 51.20, RED, 20, ''), ('Aktyubinsk', 57.17, 50.28, RED, 15, ''), ('Tuapse', 39.08, 44.10, RED, 10, 'port'),     ('Tashkent', 69.27, 41.30, RED, 270, 'base'), ('Samarkand', 66.96, 39.65, RED, 100, ''), ('Kokand', 70.94, 40.53, RED, 120, ''), ('Andijan', 72.35, 40.78, RED, 75, ''),
    ('Verny', 76.95, 43.25, RED, 40, ''), ('Pishpek', 74.60, 42.87, RED, 20, ''), ('Aulie-Ata', 71.37, 42.90, RED, 25, ''),
    ('Chimkent', 69.60, 42.30, RED, 20, ''), ('Perovsk', 65.50, 44.85, RED, 15, ''), ('Ashkhabad', 58.38, 37.95, RED, 45, ''), ('Krasnovodsk', 53.00, 40.02, RED, 10, 'port'),
    ('Merv', 61.83, 37.60, RED, 15, ''), ('Chardzhui', 63.57, 39.08, RED, 15, ''), 
    # --- White South (Don Host and the Volunteer Army)
    ('Novocherkassk', 40.08, 47.42, SOUTH, 70, 'cap base'), ('Rostov-on-Don', 39.72, 47.23, SOUTH, 170, 'base port'), ('Taganrog', 38.90, 47.22, SOUTH, 70, 'port'),
    ('Ekaterinodar', 38.98, 45.04, SOUTH, 110, 'base'), ('Novorossiysk', 37.77, 44.72, SOUTH, 70, 'port'), ('Yeysk', 38.27, 46.71, SOUTH, 45, 'port'), ('Maikop', 40.10, 44.60, SOUTH, 55, ''),
    ('Armavir', 41.13, 45.00, SOUTH, 45, ''), ('Kamensk', 40.27, 48.32, SOUTH, 20, ''),
    ('Millerovo', 40.40, 48.92, SOUTH, 10, ''), ('Ust-Medveditskaya', 42.74, 49.57, SOUTH, 10, ''), ('Uryupinsk', 42.00, 50.80, SOUTH, 15, ''), ('Salsk', 41.53, 46.48, SOUTH, 10, ''),
        # --- Siberia (Komuch, Orenburg and Ural Cossacks, the Provisional Siberian Government)
    ('Omsk', 73.37, 54.99, SIB, 140, 'cap base'), ('Samara', 50.15, 53.20, SIB, 150, 'base'), ('Ufa', 55.97, 54.73, SIB, 110, ''), ('Orenburg', 55.10, 51.77, SIB, 110, 'base'),
    ('Uralsk', 51.37, 51.23, SIB, 45, ''), ('Guryev', 51.90, 47.12, SIB, 10, 'port'), ('Chelyabinsk', 61.40, 55.16, SIB, 70, 'base'), ('Troitsk', 61.57, 54.09, SIB, 40, ''),
    ('Kurgan', 65.34, 55.45, SIB, 35, ''), ('Petropavlovsk', 69.14, 54.87, SIB, 45, ''), ('Kustanai', 63.63, 53.21, SIB, 30, ''), ('Akmolinsk', 71.45, 51.17, SIB, 15, ''),
    ('Semipalatinsk', 80.25, 50.41, SIB, 35, ''), ('Pavlodar', 76.95, 52.29, SIB, 20, ''), ('Ust-Kamenogorsk', 82.60, 49.95, SIB, 15, ''), ('Tyumen', 65.53, 57.15, SIB, 50, ''),
    ('Tobolsk', 68.26, 58.20, SIB, 20, ''), ('Ishim', 69.49, 56.11, SIB, 15, ''), ('Tomsk', 84.95, 56.49, SIB, 115, ''), ('Novonikolaevsk', 82.93, 55.03, SIB, 70, 'base'),
    ('Barnaul', 83.78, 53.35, SIB, 55, ''), ('Biysk', 85.21, 52.54, SIB, 30, ''), ('Krasnoyarsk', 92.87, 56.01, SIB, 80, 'base'), ('Achinsk', 90.50, 56.27, SIB, 15, ''),
    ('Kansk', 95.70, 56.20, SIB, 15, ''), ('Irkutsk', 104.28, 52.29, SIB, 125, 'base'), ('Nizhneudinsk', 99.03, 54.90, SIB, 10, ''), ('Minusinsk', 91.69, 53.71, SIB, 15, ''),
    ('Buzuluk', 52.26, 52.78, SIB, 15, ''), ('Bugulma', 52.80, 54.54, SIB, 15, ''), ('Sterlitamak', 55.95, 53.63, SIB, 15, ''), ('Zlatoust', 59.67, 55.17, SIB, 35, ''),
    ('Shadrinsk', 63.63, 56.09, SIB, 15, ''), ('Mariinsk', 87.75, 56.21, SIB, 15, ''), ('Tara', 74.38, 56.90, SIB, 10, ''), ('Kokchetav', 69.40, 53.28, SIB, 10, ''),
    ('Verkhneuralsk', 59.22, 53.88, SIB, 10, ''), ('Buguruslan', 52.45, 53.65, SIB, 15, ''), ('Yeniseysk', 92.17, 58.45, SIB, 10, ''), ('Kainsk', 78.30, 55.35, SIB, 10, ''),
    ('Slavgorod', 78.65, 53.00, SIB, 10, ''), ('Kuznetsk', 87.10, 53.76, SIB, 5, ''), ('Nikolaevsk', 48.80, 52.02, SIB, 15, ''), ('Atbasar', 68.35, 51.80, SIB, 8, ''),
    # --- Northern Region (Allied intervention zone)
    ('Arkhangelsk', 40.54, 64.54, NORTH, 45, 'cap base port'), ('Murmansk', 33.08, 68.97, NORTH, 10, 'port'), ('Kem', 34.60, 64.95, NORTH, 3, 'port'), ('Onega', 38.10, 63.90, NORTH, 3, 'port'),
    ('Kandalaksha', 32.40, 67.15, NORTH, 2, ''), ('Shenkursk', 42.90, 62.10, NORTH, 2, ''), ('Mezen', 44.25, 65.85, NORTH, 2, ''),
    # --- Ukrainian State (Hetmanate under German occupation)
    ('Kiev', 30.52, 50.45, UKR, 600, 'cap base'), ('Kharkov', 36.23, 50.00, UKR, 250, 'base'), ('Odessa', 30.73, 46.48, UKR, 500, 'base port'), ('Ekaterinoslav', 35.05, 48.47, UKR, 220, ''),
    ('Nikolaev', 31.99, 46.97, UKR, 100, 'port'), ('Kherson', 32.62, 46.64, UKR, 75, 'port'), ('Poltava', 34.55, 49.59, UKR, 60, ''), ('Zhitomir', 28.66, 50.26, UKR, 90, ''),
    ('Vinnitsa', 28.47, 49.23, UKR, 40, ''), ('Chernigov', 31.30, 51.50, UKR, 35, ''), ('Sumy', 34.80, 50.91, UKR, 50, ''), ('Lugansk', 39.30, 48.57, UKR, 60, ''),
    ('Yuzovka', 37.80, 48.00, UKR, 50, ''), ('Mariupol', 37.55, 47.10, UKR, 55, 'port'), ('Berdyansk', 36.79, 46.76, UKR, 40, 'port'), ('Aleksandrovsk', 35.14, 47.84, UKR, 60, ''),
    ('Elisavetgrad', 32.26, 48.50, UKR, 75, ''), ('Kremenchug', 33.42, 49.07, UKR, 65, ''), ('Uman', 30.22, 48.75, UKR, 40, ''), ('Kamenets-Podolsky', 26.58, 48.68, UKR, 40, ''),
    ('Rovno', 26.25, 50.62, UKR, 35, ''), ('Lutsk', 25.33, 50.75, UKR, 30, ''), ('Proskurov', 26.98, 49.42, UKR, 30, ''), ('Berdichev', 28.60, 49.90, UKR, 55, ''),
    ('Simferopol', 34.10, 44.95, UKR, 90, ''), ('Sevastopol', 33.52, 44.60, UKR, 80, 'base port'), ('Kerch', 36.47, 45.36, UKR, 40, 'port'),
    ('Melitopol', 35.37, 46.85, UKR, 30, ''),
    ('Belgorod', 36.58, 50.60, UKR, 40, ''), ('Bakhmut', 38.00, 48.60, UKR, 30, ''), ('Konotop', 33.20, 51.24, UKR, 20, ''),
    ('Nezhin', 31.88, 51.05, UKR, 30, ''), ('Tiraspol', 29.60, 46.84, UKR, 30, ''), ('Tarnopol', 25.60, 49.55, UKR, 35, ''), ('Stanislav', 24.71, 48.92, UKR, 60, ''),
    ('Kolomyia', 25.03, 48.53, UKR, 45, ''), ('Kovel', 24.70, 51.22, UKR, 25, ''), ('Mogilev-Podolsky', 27.80, 48.45, UKR, 25, ''),
    ('Balta', 29.62, 47.94, UKR, 20, ''), ('Pavlograd', 35.87, 48.53, UKR, 25, ''), ('Nikopol', 34.40, 47.57, UKR, 20, ''), ('Starobelsk', 38.90, 49.28, UKR, 10, ''),
    ('Izyum', 37.26, 49.21, UKR, 15, ''), ('Glukhov', 33.90, 51.68, UKR, 15, ''), ('Romny', 33.47, 50.75, UKR, 20, ''), ('Lubny', 33.00, 50.02, UKR, 15, ''),
    ('Cherkassy', 32.06, 49.44, UKR, 40, ''), ('Genichesk', 34.80, 46.17, UKR, 10, ''), ('Vladimir-Volynsky', 24.32, 50.85, UKR, 15, ''), ('Stryi', 23.85, 49.26, UKR, 30, ''),
    ('Drohobych', 23.50, 49.35, UKR, 35, ''), ('Akhtyrka', 34.90, 50.31, UKR, 25, ''), ('Gulyai-Pole', 36.26, 47.66, UKR, 15, ''),
    # --- Poland
    ('Warsaw', 21.01, 52.23, POL, 900, 'cap base'), ('Lodz', 19.46, 51.77, POL, 500, ''), ('Lublin', 22.57, 51.25, POL, 90, ''), ('Krakow', 19.94, 50.06, POL, 180, 'base'),
    ('Lwow', 24.03, 49.84, POL, 210, 'base'), ('Bialystok', 23.16, 53.13, POL, 80, ''), ('Grodno', 23.83, 53.68, POL, 60, ''),
    ('Brest-Litovsk', 23.70, 52.10, POL, 50, ''), ('Kielce', 20.63, 50.87, POL, 45, ''), ('Radom', 21.15, 51.40, POL, 50, ''), ('Czestochowa', 19.12, 50.81, POL, 80, ''),
    ('Plock', 19.70, 52.55, POL, 30, ''), ('Siedlce', 22.29, 52.17, POL, 30, ''), ('Lomza', 22.08, 53.18, POL, 25, ''), ('Suwalki', 22.93, 54.10, POL, 25, ''),
    ('Przemysl', 22.77, 49.78, POL, 55, ''), ('Rzeszow', 22.00, 50.04, POL, 25, ''), ('Tarnow', 20.99, 50.01, POL, 40, ''), ('Pinsk', 26.10, 52.12, POL, 35, ''),
    ('Baranovichi', 26.02, 53.13, POL, 15, ''), ('Lida', 25.30, 53.89, POL, 15, ''), ('Chelm', 23.47, 51.13, POL, 25, ''), ('Zamosc', 23.25, 50.72, POL, 15, ''),
    ('Slonim', 25.32, 53.09, POL, 15, ''), ('Sambor', 23.20, 49.52, POL, 20, ''), ('Kalisz', 18.09, 51.76, POL, 50, ''), ('Novogrudok', 25.83, 53.60, POL, 8, ''),
]
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES): CITIES.append((name, lo, la, 32 + i, popk, 'cap'))
CITIES.append(('Kovno', 23.90, 54.90, 32 + CSIDX['LITHUANIA'], 90, ''))   # Lithuania's second town, 2 hexes from Vilna: it merges into the capital
# Thin the city list: at ~47 km per hex the European provinces would put towns two hexes apart. The rule, with no exceptions:
# no two cities closer than 3 hexes; two cities of one side at least 4 apart unless both are key towns (capitals or KEEP), then 3.
# Towns are taken in order of importance (side capitals, city-state capitals, KEEP towns, IMPORTANT towns, the rest, each by
# population); a town that breaks the rule joins the nearest kept city of its owner (population added), or is dropped if none is near.
MIN_SPACING = 4          # between cities of the same side
MIN_SPACING_KEY = 3      # between two key towns (capitals, KEEP) of the same side
MIN_SPACING_FRONT = 3    # between cities of different sides, and the hard floor for any two cities
# every city the events name (Russia1918_Events.lua), plus the towns the history turns on
# (Brest-Litovsk, the town of the March 1918 treaty, and Lublin, seat of the Austrian occupation and of Daszynski's government of
# November 1918, stand three hexes apart; Bialystok yields to Grodno, the provincial capital, and merges into it)
KEEP = {'Kazan', 'Voronezh', 'Novocherkassk', 'Novorossiysk', 'Kharkov', 'Sevastopol', 'Samara', 'Omsk', 'Ufa', 'Arkhangelsk', 'Reval', 'Vinnitsa', 'Kiev', 'Tarnopol',
        'Warsaw', 'Lodz', 'Lwow', 'Elisavetgrad', 'Tambov', 'Moscow', 'Petrograd', 'Tsaritsyn', 'Orenburg', 'Ekaterinburg', 'Rostov-on-Don', 'Ekaterinodar', 'Odessa', 'Irkutsk', 'Tashkent', 'Smolensk', 'Simbirsk',
        'Brest-Litovsk', 'Lublin'}
# historically important towns: placed before the rest, but still subject to the spacing rule
IMPORTANT = ['Yaroslavl', 'Smolensk', 'Kursk', 'Oryol', 'Tula', 'Simbirsk', 'Penza', 'Saratov', 'Astrakhan', 'Perm', 'Vyatka', 'Vologda', 'Nizhny Novgorod', 'Tver', 'Pskov', 'Novgorod', 'Minsk',
             'Vitebsk', 'Gomel', 'Mogilev', 'Stavropol', 'Vladikavkaz', 'Grozny', 'Petrovsk', 'Taganrog', 'Lugansk', 'Yuzovka', 'Mariupol', 'Poltava', 'Zhitomir', 'Chernigov', 'Nikolaev', 'Kherson',
             'Simferopol', 'Kamenets-Podolsky', 'Rovno', 'Grodno', 'Brest-Litovsk', 'Krakow', 'Lublin', 'Chelyabinsk', 'Tyumen', 'Tomsk', 'Krasnoyarsk', 'Uralsk', 'Troitsk',
             'Semipalatinsk', 'Barnaul', 'Murmansk', 'Kem', 'Verny', 'Samarkand', 'Kokand', 'Ashkhabad', 'Krasnovodsk', 'Izhevsk', 'Ekaterinoslav', 'Aleksandrovsk', 'Kremenchug', 'Ryazan', 'Kaluga',
             'Kostroma', 'Vladimir', 'Syzran', 'Kamyshin', 'Petropavlovsk', 'Kurgan', 'Novonikolaevsk', 'Berdichev', 'Lutsk', 'Sumy', 'Konotop', 'Kerch', 'Melitopol', 'Berdyansk', 'Pinsk']
IMP_RANK = {n: i for i, n in enumerate(IMPORTANT)}
approx = {c[0]: hex_ll(c[1], c[2]) for c in CITIES}
def tier(c): return (0 if c[3] < 32 else 1) if 'cap' in c[5] else 2 if c[0] in KEEP else 3 if c[0] in IMP_RANK else 4
def is_key(c): return tier(c) <= 2
def spacing(a, b):
    """Minimum hex distance between two cities (records of CITIES) under the rule."""
    if a[3] != b[3]: return MIN_SPACING_FRONT
    return MIN_SPACING_KEY if is_key(a) and is_key(b) else MIN_SPACING
def spacing_thin(a, b): return spacing(a, b) + (1 if a[3] == b[3] and tier(a) == 4 else 0)   # minor towns keep an extra hex of air
order = sorted(range(len(CITIES)), key=lambda i: (tier(CITIES[i]), -CITIES[i][4], CITIES[i][0]))
kept = []; dropped = []; ABSORBED = {}
def absorb(i, h, pool, final=False):
    """Merge town i into the nearest city of its owner among pool {index: hex} within 8 hexes. While thinning, a town with no such
    city yet waits for the final plots (a big town taken before the smaller towns of its side around it); after placement, with none it is dropped."""
    name, pl = CITIES[i][0], CITIES[i][3]
    same = [j for j in pool if CITIES[j][3] == pl and hexdist(h, pool[j]) <= 8]
    if not same and not final: dropped.append(i); return
    ABSORBED[name] = CITIES[min(same, key=lambda j: (hexdist(h, pool[j]), j))][0] if same else None
for i in order:
    h = approx[CITIES[i][0]]
    if h is None: continue
    if all(hexdist(h, approx[CITIES[j][0]]) >= spacing_thin(CITIES[i], CITIES[j]) for j in kept): kept.append(i); continue
    absorb(i, h, {j: approx[CITIES[j][0]] for j in kept})
# Place the kept cities in the same order, each on the nearest fitting hex to its real position (radius 2 on friendly land, then 3,
# then 3 on any land, a mountain flattened to hills); the rule is checked against the cities already placed, so it holds on the final plots.
# A city that finds no hex joins the nearest placed city of its owner.
city_tile_of = {}
def friendly(o, pl): return o == NONE or o == pl
for i in kept:
    name, lo, la, pl, popk, tags = CITIES[i]
    def spaced(x, y, i=i): return all(hexdist((x, y), t) >= spacing(CITIES[i], CITIES[j]) for j, t in city_tile_of.items())
    def ok(x, y): return is_land[y, x] and elev[y, x] != 2 and terrain[y, x] != SNOW and spaced(x, y)
    t = find_tile(lo, la, lambda x, y, pl=pl: ok(x, y) and friendly(owner[y, x], pl), 2)
    if t is None: t = find_tile(lo, la, ok, 3)
    if t is None:
        t = find_tile(lo, la, lambda x, y: is_land[y, x] and spaced(x, y), 3)   # Kars in the Armenian highland: a mountain hex becomes hills
        if t is not None: elev[t[1], t[0]] = min(int(elev[t[1], t[0]]), 1); terrain[t[1], t[0]] = PLAINS if terrain[t[1], t[0]] == SNOW else terrain[t[1], t[0]]
        print('  !! relaxed placement for', name, t)
    if t is None: dropped.append(i); print('  !! no room for', name); continue
    city_tile_of[i] = t
    owner[t[1], t[0]] = pl; feature[t[1], t[0]] = NONE; wonder[t[1], t[0]] = NONE
    if resource[t[1], t[0]] != NONE and RESOURCES[resource[t[1], t[0]]].split('_', 1)[1] in ('FISH', 'WHALE', 'CRAB'): resource[t[1], t[0]] = NONE
    for nb in neighbors(*t):
        if is_land[nb[1], nb[0]] and (owner[nb[1], nb[0]] == NONE or owner[nb[1], nb[0]] != pl) and nb not in city_tile_of.values(): owner[nb[1], nb[0]] = pl
for i in dropped: absorb(i, approx[CITIES[i][0]], city_tile_of, final=True)
extra = Counter()
for name, tgt in ABSORBED.items():
    if tgt: extra[tgt] += next(c[4] for c in CITIES if c[0] == name)
dropped_key = sorted(n for n in ABSORBED if is_key(next(c for c in CITIES if c[0] == n)))
idx = sorted(city_tile_of)
city_tiles = [city_tile_of[i] for i in idx]
CITIES = [(c[0], c[1], c[2], c[3], c[4] + (extra[c[0]] if c[3] < 32 else 0), c[5]) for c in (CITIES[i] for i in idx)]
city_at = {t: k for k, t in enumerate(city_tiles)}
print(f'  cities: kept {len(CITIES)}, merged {sum(1 for v in ABSORBED.values() if v)}, dropped {sum(1 for v in ABSORBED.values() if not v)}; key towns merged:',
      ', '.join(f'{n} -> {ABSORBED[n]}' for n in dropped_key) or 'none', '; biggest merges:', ', '.join(f'{k} +{v}k' for k, v in extra.most_common(6)))
# the spacing rule on the final plots, no exceptions
gaps = [(hexdist(city_tiles[a], city_tiles[b]), spacing(CITIES[a], CITIES[b]), CITIES[a][3] == CITIES[b][3], CITIES[a][0], CITIES[b][0])
        for a in range(len(CITIES)) for b in range(a + 1, len(CITIES))]
bad = [g for g in gaps if g[0] < g[1]]
assert not bad, f'cities too close: {bad}'
print(f'  city spacing (at least {MIN_SPACING_FRONT} between any two, {MIN_SPACING} within a side unless both are key towns): min {min(g[0] for g in gaps)} hexes overall,',
      f'{min(g[0] for g in gaps if g[2])} within a side, {min(g[0] for g in gaps if g[1] == MIN_SPACING)} between towns of a side that are not both key')
# the state exists along the railways: land farther than 7 hexes (4 for a city-state) from one of its owner's cities is nobody's
near = {}
for ci, t in enumerate(city_tiles): near.setdefault(CITIES[ci][3], []).append(t)
for y in range(H):
    for x in range(W):
        o = owner[y, x]
        if o == NONE or (x, y) in city_at: continue
        lim = 4 if o >= 32 else 8
        if min((hexdist((x, y), t) for t in near.get(int(o), [])), default=99) > lim: owner[y, x] = NONE
# coastal / lake water: nearest land owner within 2 hexes
for y in range(H):
    for x in range(W):
        if is_land[y, x] or terrain[y, x] == OCEAN: continue
        cnt = Counter(); seen = {(x, y)}; q = deque([((x, y), 0)])
        while q:
            t, d = q.popleft()
            if d >= 2: continue
            for nb in neighbors(*t):
                if nb in seen: continue
                seen.add(nb)
                if is_land[nb[1], nb[0]] and owner[nb[1], nb[0]] != NONE: cnt[int(owner[nb[1], nb[0]])] += 3 - d
                else: q.append((nb, d + 1))
        if cnt: owner[y, x] = cnt.most_common(1)[0][0]
def civ_pop(popk): return int(max(3, min(24, round(4.2 * math.log(popk * 1000) - 40))))

BUILDINGS = ['BUILDING_PALACE', 'BUILDING_MONUMENT', 'BUILDING_GRANARY', 'BUILDING_LIBRARY', 'BUILDING_MARKET', 'BUILDING_BARRACKS', 'BUILDING_WALLS',
             'BUILDING_AQUEDUCT', 'BUILDING_WORKSHOP', 'BUILDING_AMPHITHEATER', 'BUILDING_UNIVERSITY', 'BUILDING_BANK', 'BUILDING_PUBLIC_SCHOOL',
             'BUILDING_HOSPITAL', 'BUILDING_FACTORY', 'BUILDING_CONSTABLE', 'BUILDING_OPERA_HOUSE', 'BUILDING_MUSEUM', 'BUILDING_STOCK_EXCHANGE',
             'BUILDING_ARMORY', 'BUILDING_CASTLE', 'BUILDING_MILITARY_ACADEMY', 'BUILDING_ARSENAL', 'BUILDING_LIGHTHOUSE', 'BUILDING_HARBOR', 'BUILDING_SEAPORT',
             'BUILDING_COURTHOUSE', 'BUILDING_CARAVANSARY', 'BUILDING_FORGE', 'BUILDING_STABLE', 'BUILDING_WINDMILL', 'BUILDING_GARDEN', 'BUILDING_MINT']
BID = {b: i for i, b in enumerate(BUILDINGS)}
def city_buildings(ci):
    """Lean 1918 building set: gold and defence everywhere, upkeep-heavy buildings only in the big cities."""
    name, lo, la, pl, popk, tags = CITIES[ci]; pop = civ_pop(popk); t = city_tiles[ci]; tags = tags.split()
    b = ['BUILDING_MONUMENT', 'BUILDING_GRANARY', 'BUILDING_MARKET', 'BUILDING_WALLS', 'BUILDING_LIBRARY']
    if pop >= 8: b += ['BUILDING_BANK', 'BUILDING_CASTLE', 'BUILDING_WORKSHOP']
    if pop >= 11: b += ['BUILDING_UNIVERSITY', 'BUILDING_BARRACKS', 'BUILDING_FORGE', 'BUILDING_AQUEDUCT']
    if pop >= 14: b += ['BUILDING_STOCK_EXCHANGE', 'BUILDING_ARMORY', 'BUILDING_ARSENAL', 'BUILDING_AMPHITHEATER', 'BUILDING_WINDMILL']
    if pop >= 17: b += ['BUILDING_FACTORY', 'BUILDING_PUBLIC_SCHOOL', 'BUILDING_HOSPITAL', 'BUILDING_OPERA_HOUSE', 'BUILDING_MUSEUM']
    if 'cap' in tags: b += ['BUILDING_PALACE']
    if 'cap' in tags and pl < 32: b += ['BUILDING_CONSTABLE', 'BUILDING_MILITARY_ACADEMY', 'BUILDING_BARRACKS', 'BUILDING_ARSENAL']
    if 'base' in tags: b += ['BUILDING_BARRACKS', 'BUILDING_ARMORY', 'BUILDING_STABLE']
    if 'port' in tags or any(not is_land[nb[1], nb[0]] and not is_lake[nb[1], nb[0]] for nb in neighbors(*t)):
        if any(not is_land[nb[1], nb[0]] for nb in neighbors(*t)): b += ['BUILDING_HARBOR'] + (['BUILDING_LIGHTHOUSE'] if pop >= 8 else [])
    if pl >= 32: b = ['BUILDING_MONUMENT', 'BUILDING_WALLS', 'BUILDING_GRANARY', 'BUILDING_MARKET', 'BUILDING_PALACE'] + (['BUILDING_CASTLE', 'BUILDING_BARRACKS'] if pop >= 10 else [])
    return sorted(set(b))
UPKEEP = {'MONUMENT': 1, 'GRANARY': 1, 'LIBRARY': 1, 'BARRACKS': 1, 'AQUEDUCT': 1, 'WORKSHOP': 2, 'AMPHITHEATER': 2, 'UNIVERSITY': 2, 'PUBLIC_SCHOOL': 3, 'HOSPITAL': 2,
          'FACTORY': 3, 'CONSTABLE': 1, 'OPERA_HOUSE': 1, 'MUSEUM': 1, 'ARMORY': 1, 'MILITARY_ACADEMY': 1, 'LIGHTHOUSE': 1, 'HARBOR': 2, 'FORGE': 1, 'STABLE': 1, 'WINDMILL': 2, 'CASTLE': 0}
upkeep = Counter()
for ci, c in enumerate(CITIES): upkeep[c[3]] += sum(UPKEEP.get(b.split('_', 1)[1], 0) for b in city_buildings(ci))
print('  building upkeep per turn:', {PLAYERS[k]['key']: upkeep[k] for k in range(NP)})

# ============================================================== improvements & railways
IMPROVEMENTS = ['IMPROVEMENT_FARM', 'IMPROVEMENT_MINE', 'IMPROVEMENT_PASTURE', 'IMPROVEMENT_CAMP', 'IMPROVEMENT_PLANTATION', 'IMPROVEMENT_QUARRY',
                'IMPROVEMENT_LUMBERMILL', 'IMPROVEMENT_TRADING_POST', 'IMPROVEMENT_FISHING_BOATS', 'IMPROVEMENT_OFFSHORE_PLATFORM', 'IMPROVEMENT_WELL', 'IMPROVEMENT_FORT']
IID = {b.split('_', 1)[1]: i for i, b in enumerate(IMPROVEMENTS)}
improvement = np.full((H, W), NONE, np.uint8); route = np.full((H, W), NONE, np.uint8)
RES_IMP = {'WHEAT': 'FARM', 'COW': 'PASTURE', 'SHEEP': 'PASTURE', 'HORSE': 'PASTURE', 'DEER': 'CAMP', 'FUR': 'CAMP', 'TRUFFLES': 'CAMP',
           'IRON': 'MINE', 'COAL': 'MINE', 'GOLD': 'MINE', 'SILVER': 'MINE', 'GEMS': 'MINE', 'COPPER': 'MINE', 'SALT': 'MINE',
           'STONE': 'QUARRY', 'MARBLE': 'QUARRY', 'WINE': 'PLANTATION', 'SUGAR': 'PLANTATION', 'COTTON': 'PLANTATION', 'CITRUS': 'PLANTATION', 'DYE': 'PLANTATION',
           'SPICES': 'PLANTATION', 'SILK': 'PLANTATION', 'INCENSE': 'PLANTATION', 'FISH': 'FISHING_BOATS', 'CRAB': 'FISHING_BOATS', 'WHALE': 'FISHING_BOATS'}
for ci, (name, lo, la, pl, popk, tags) in enumerate(CITIES):
    cx, cy = city_tiles[ci]; rad = 3 if civ_pop(popk) >= 12 else 2
    for y in range(max(0, cy - rad), min(H, cy + rad + 1)):
        for x in range(max(0, cx - rad), min(W, cx + rad + 1)):
            if hexdist((x, y), (cx, cy)) > rad or (x, y) in city_at or improvement[y, x] != NONE: continue
            if owner[y, x] != pl: continue
            res = RESOURCES[resource[y, x]].split('_', 1)[1] if resource[y, x] != NONE else None
            if not is_land[y, x]:
                if res in RES_IMP and not is_lake[y, x]: improvement[y, x] = IID['FISHING_BOATS']
                continue
            if elev[y, x] == 2 or terrain[y, x] == SNOW: continue
            if res == 'OIL': improvement[y, x] = IID['WELL']; continue
            if res in RES_IMP:
                if feature[y, x] in (FOREST, MARSH) and RES_IMP[res] in ('FARM', 'PASTURE', 'PLANTATION'): feature[y, x] = NONE
                improvement[y, x] = IID[RES_IMP[res]]; continue
            r = rnd(x, y, 'imp'); dense = 0.75 if civ_pop(popk) >= 12 else 0.5
            if feature[y, x] == FOREST:
                if r < 0.35 * dense: improvement[y, x] = IID['LUMBERMILL']
            elif feature[y, x] == MARSH: pass
            elif elev[y, x] == 1:
                if r < 0.35 * dense: improvement[y, x] = IID['MINE']
            elif terrain[y, x] in (GRASS, PLAINS):
                if r < dense * (0.9 if has_river(x, y) else 0.7): improvement[y, x] = IID['FARM']
                elif r < dense * 0.8: improvement[y, x] = IID['TRADING_POST']
            elif terrain[y, x] == TUNDRA and r < 0.15 * dense: improvement[y, x] = IID['TRADING_POST']

def dijkstra(src, dst, pass_mountains=False):
    def cost(x, y):
        if not is_land[y, x] or (elev[y, x] == 2 and not pass_mountains): return None
        c = 1.0 + (0.8 if elev[y, x] == 1 else 0) + (0.4 if feature[y, x] in (FOREST, MARSH) else 0) + (6.0 if elev[y, x] == 2 else 0)
        if route[y, x] != NONE: c *= 0.4
        return c
    dist = {src: 0}; prev = {}; pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst: break
        if d > dist.get(u, 1e9): continue
        for v in neighbors(*u):
            c = cost(*v)
            if c is None: continue
            nd = d + c
            if nd < dist.get(v, 1e9): dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if dst not in prev: return None
    path = [dst]
    while path[-1] != src: path.append(prev[path[-1]])
    return path[::-1]
CNAME = {c[0]: i for i, c in enumerate(CITIES)}
def rail(a, b):
    p = dijkstra(city_tiles[CNAME[a]], city_tiles[CNAME[b]])
    if p is None:
        p = dijkstra(city_tiles[CNAME[a]], city_tiles[CNAME[b]], pass_mountains=True)
        if p is None: print('  !! no rail path', a, b); return
        for x, y in p:
            if elev[y, x] == 2: elev[y, x] = 1; feature[y, x] = NONE
    for x, y in p:
        if (x, y) not in city_at: route[y, x] = 1
# The railway network of 1918, line by line (both ends must be cities above).
RAIL = [
    # Nikolaev line and the north
    ('Petrograd', 'Tver'), ('Tver', 'Moscow'), ('Petrograd', 'Pskov'), ('Pskov', 'Polotsk'), ('Polotsk', 'Vitebsk'), ('Petrograd', 'Novgorod'), ('Novgorod', 'Staraya Russa'),
    ('Petrograd', 'Petrozavodsk'), ('Petrozavodsk', 'Kem'), ('Kem', 'Kandalaksha'), ('Kandalaksha', 'Murmansk'), ('Petrograd', 'Reval'), ('Petrograd', 'Helsinki'),
    ('Vologda', 'Arkhangelsk'), ('Moscow', 'Yaroslavl'), ('Yaroslavl', 'Vologda'), ('Vologda', 'Vyatka'), ('Vyatka', 'Perm'), ('Perm', 'Ekaterinburg'), ('Ekaterinburg', 'Tyumen'), ('Tyumen', 'Omsk'),
    ('Yaroslavl', 'Rybinsk'), ('Rybinsk', 'Cherepovets'), ('Cherepovets', 'Petrograd'), ('Yaroslavl', 'Kostroma'), ('Moscow', 'Ivanovo-Voznesensk'), ('Ivanovo-Voznesensk', 'Kineshma'),
    ('Moscow', 'Vladimir'), ('Vladimir', 'Nizhny Novgorod'), ('Moscow', 'Murom'), ('Murom', 'Arzamas'), ('Arzamas', 'Kazan'), ('Moscow', 'Ryazan'), ('Ryazan', 'Saransk'), ('Saransk', 'Kazan'),
    ('Kazan', 'Ekaterinburg'), ('Vyatka', 'Kotlas'), ('Perm', 'Izhevsk'), ('Izhevsk', 'Sarapul'), ('Sarapul', 'Kazan'),
    # Moscow south and the Volga
    ('Moscow', 'Tula'), ('Tula', 'Oryol'), ('Oryol', 'Kursk'), ('Kursk', 'Belgorod'), ('Belgorod', 'Kharkov'), ('Moscow', 'Kaluga'), ('Kaluga', 'Bryansk'), ('Bryansk', 'Gomel'), ('Bryansk', 'Oryol'),
    ('Ryazan', 'Kozlov'), ('Kozlov', 'Tambov'), ('Tambov', 'Saratov'), ('Kozlov', 'Voronezh'), ('Voronezh', 'Rostov-on-Don'), ('Yelets', 'Oryol'), ('Yelets', 'Kozlov'),
    ('Tambov', 'Balashov'), ('Balashov', 'Kamyshin'), ('Kamyshin', 'Tsaritsyn'), ('Saratov', 'Uralsk'), ('Saratov', 'Astrakhan'), ('Tsaritsyn', 'Ekaterinodar'),
    ('Tsaritsyn', 'Kamensk'), ('Kamensk', 'Novocherkassk'), ('Ryazan', 'Penza'), ('Penza', 'Syzran'), ('Syzran', 'Samara'), ('Syzran', 'Simbirsk'), ('Simbirsk', 'Kazan'), ('Simbirsk', 'Bugulma'),
    ('Samara', 'Buzuluk'), ('Buzuluk', 'Orenburg'), ('Orenburg', 'Aktyubinsk'), ('Aktyubinsk', 'Perovsk'), ('Perovsk', 'Tashkent'), ('Orenburg', 'Orsk'), ('Samara', 'Ufa'), ('Ufa', 'Zlatoust'),
    ('Zlatoust', 'Chelyabinsk'), ('Chelyabinsk', 'Ekaterinburg'), ('Chelyabinsk', 'Kurgan'), ('Kurgan', 'Petropavlovsk'), ('Petropavlovsk', 'Omsk'), ('Chelyabinsk', 'Troitsk'), ('Troitsk', 'Kustanai'),
    ('Penza', 'Morshansk'), ('Morshansk', 'Ryazan'), ('Saratov', 'Balashov'), ('Voronezh', 'Borisoglebsk'), ('Borisoglebsk', 'Balashov'), ('Kozlov', 'Morshansk'),
    # Trans-Siberian
    ('Omsk', 'Kainsk'), ('Kainsk', 'Novonikolaevsk'), ('Novonikolaevsk', 'Tomsk'), ('Novonikolaevsk', 'Mariinsk'), ('Mariinsk', 'Achinsk'), ('Achinsk', 'Krasnoyarsk'), ('Krasnoyarsk', 'Kansk'),
    ('Kansk', 'Nizhneudinsk'), ('Nizhneudinsk', 'Irkutsk'), ('Novonikolaevsk', 'Barnaul'), ('Barnaul', 'Semipalatinsk'), ('Barnaul', 'Biysk'), ('Tyumen', 'Ishim'), ('Ishim', 'Omsk'),
    ('Tomsk', 'Mariinsk'), ('Mariinsk', 'Kuznetsk'), ('Achinsk', 'Minusinsk'),
    # Ukraine, Belarus, Poland
    ('Kharkov', 'Poltava'), ('Poltava', 'Kiev'), ('Kiev', 'Vinnitsa'), ('Vinnitsa', 'Odessa'), ('Vinnitsa', 'Proskurov'), ('Proskurov', 'Tarnopol'), ('Tarnopol', 'Lwow'), ('Lwow', 'Przemysl'),
    ('Przemysl', 'Krakow'), ('Krakow', 'Czestochowa'), ('Czestochowa', 'Warsaw'), ('Warsaw', 'Lodz'), ('Lodz', 'Kalisz'), ('Warsaw', 'Lublin'), ('Lublin', 'Kovel'), ('Kovel', 'Rovno'),
    ('Rovno', 'Berdichev'), ('Berdichev', 'Kiev'), ('Kiev', 'Konotop'), ('Konotop', 'Kursk'), ('Konotop', 'Gomel'), ('Gomel', 'Mogilev'), ('Mogilev', 'Orsha'), ('Orsha', 'Vitebsk'), ('Orsha', 'Smolensk'),
    ('Smolensk', 'Moscow'), ('Smolensk', 'Minsk'), ('Minsk', 'Baranovichi'), ('Baranovichi', 'Brest-Litovsk'), ('Brest-Litovsk', 'Warsaw'), ('Minsk', 'Vilna'), ('Vilna', 'Grodno'), ('Grodno', 'Bialystok'),
    ('Bialystok', 'Warsaw'), ('Vilna', 'Kovno'), ('Kovno', 'Konigsberg'), ('Vilna', 'Polotsk'), ('Vilna', 'Riga'), ('Riga', 'Pskov'), ('Riga', 'Reval'), ('Warsaw', 'Plock'), ('Warsaw', 'Siedlce'),
    ('Siedlce', 'Brest-Litovsk'), ('Brest-Litovsk', 'Pinsk'), ('Pinsk', 'Gomel'), ('Brest-Litovsk', 'Kovel'), ('Lublin', 'Chelm'), ('Chelm', 'Kovel'), ('Kielce', 'Radom'), ('Radom', 'Warsaw'),
    ('Kharkov', 'Ekaterinoslav'), ('Ekaterinoslav', 'Aleksandrovsk'), ('Aleksandrovsk', 'Melitopol'), ('Melitopol', 'Simferopol'), ('Simferopol', 'Sevastopol'), ('Simferopol', 'Kerch'),
    ('Kharkov', 'Yuzovka'), ('Yuzovka', 'Mariupol'), ('Yuzovka', 'Taganrog'), ('Taganrog', 'Rostov-on-Don'), ('Kharkov', 'Lugansk'), ('Lugansk', 'Kamensk'),
    ('Ekaterinoslav', 'Elisavetgrad'), ('Elisavetgrad', 'Odessa'), ('Elisavetgrad', 'Kremenchug'), ('Kremenchug', 'Poltava'), ('Kiev', 'Cherkassy'), ('Odessa', 'Nikolaev'), ('Nikolaev', 'Kherson'),
    ('Odessa', 'Kishinev'), ('Kishinev', 'Mogilev-Podolsky'), ('Kiev', 'Chernigov'), ('Kharkov', 'Sumy'), ('Sumy', 'Konotop'), ('Kiev', 'Uman'), ('Uman', 'Elisavetgrad'),
    ('Lwow', 'Stanislav'), ('Stanislav', 'Kolomyia'), ('Lwow', 'Stryi'), ('Lwow', 'Rovno'), ('Rovno', 'Lutsk'), ('Lutsk', 'Kovel'), ('Zhitomir', 'Berdichev'), ('Kamenets-Podolsky', 'Proskurov'),
    ('Berdyansk', 'Melitopol'), ('Nikopol', 'Aleksandrovsk'), ('Pavlograd', 'Ekaterinoslav'), ('Pavlograd', 'Bakhmut'), ('Bakhmut', 'Lugansk'), ('Izyum', 'Kharkov'),
    ('Izyum', 'Bakhmut'), ('Belgorod', 'Sumy'), ('Lubny', 'Kiev'), ('Lubny', 'Poltava'), ('Romny', 'Konotop'), ('Nezhin', 'Kiev'), ('Nezhin', 'Konotop'),
    # South, Caucasus, Transcaspia
    ('Rostov-on-Don', 'Novocherkassk'), ('Rostov-on-Don', 'Ekaterinodar'), ('Ekaterinodar', 'Novorossiysk'), ('Ekaterinodar', 'Armavir'), ('Armavir', 'Pyatigorsk'),
    ('Armavir', 'Stavropol'), ('Armavir', 'Maikop'), ('Armavir', 'Tuapse'), ('Pyatigorsk', 'Vladikavkaz'), ('Pyatigorsk', 'Grozny'), ('Grozny', 'Petrovsk'), ('Petrovsk', 'Derbent'), ('Derbent', 'Baku'),
    ('Baku', 'Tiflis'), ('Tiflis', 'Erivan'), ('Tiflis', 'Kars'), ('Erivan', 'Tabriz'), ('Rostov-on-Don', 'Yeysk'), ('Novocherkassk', 'Millerovo'), ('Millerovo', 'Voronezh'),
    ('Ekaterinodar', 'Salsk'), ('Salsk', 'Tsaritsyn'), ('Astrakhan', 'Kizlyar'),
    ('Krasnovodsk', 'Ashkhabad'), ('Ashkhabad', 'Merv'), ('Merv', 'Chardzhui'), ('Chardzhui', 'Bukhara'), ('Bukhara', 'Samarkand'), ('Samarkand', 'Tashkent'), ('Tashkent', 'Kokand'), ('Kokand', 'Andijan'),
    ('Tashkent', 'Chimkent'), ('Chimkent', 'Aulie-Ata'), ('Chimkent', 'Perovsk'), ('Orenburg', 'Uralsk'), ('Uralsk', 'Guryev'),
    # Finland, Baltic, East Prussia, Romania
    ('Helsinki', 'Reval'), ('Konigsberg', 'Suwalki'), ('Suwalki', 'Grodno'), ('Kishinev', 'Tiraspol'), ('Tiraspol', 'Odessa'), ('Vitebsk', 'Smolensk'), ('Velikie Luki', 'Rzhev'), ('Rzhev', 'Moscow'),
    ('Velikie Luki', 'Vitebsk'), ('Novgorod', 'Vyshny Volochyok'), ('Vyshny Volochyok', 'Tver'),
]
rail_pairs = set()
for a, b in RAIL:
    a = ABSORBED.get(a, a); b = ABSORBED.get(b, b)
    if a == b or a is None or b is None: continue   # merged into one city, or a town dropped without a city of its own side nearby
    if a not in CNAME or b not in CNAME: print('  !! rail endpoint missing', a, b); continue
    rail_pairs.add((a, b) if a < b else (b, a))
for a, b in sorted(rail_pairs): rail(a, b)
route_owner = np.where(route != NONE, owner, NONE).astype(np.uint8)
print(f'  {int((route != NONE).sum())} railroad tiles, {int((improvement != NONE).sum())} improvements')

# ============================================================== units
UNITS = ['UNIT_GREAT_WAR_INFANTRY', 'UNIT_RIFLEMAN', 'UNIT_CAVALRY', 'UNIT_ARTILLERY', 'UNIT_GATLINGGUN', 'UNIT_TRIPLANE', 'UNIT_WWI_BOMBER', 'UNIT_WWI_TANK',
         'UNIT_IRONCLAD', 'UNIT_DESTROYER', 'UNIT_BATTLESHIP', 'UNIT_SUBMARINE', 'UNIT_GREAT_GENERAL', 'UNIT_WORKER', 'UNIT_CARAVAN', 'UNIT_CARGO_SHIP']
UID = {u.split('_', 1)[1]: i for i, u in enumerate(UNITS)}
PROMOS = ['PROMOTION_DRILL_1', 'PROMOTION_DRILL_2', 'PROMOTION_SHOCK_1', 'PROMOTION_SHOCK_2', 'PROMOTION_COVER_1', 'PROMOTION_MOBILITY', 'PROMOTION_MARCH',
          'PROMOTION_MEDIC', 'PROMOTION_ACCURACY_1', 'PROMOTION_BARRAGE_1', 'PROMOTION_SENTRY', 'PROMOTION_AMBUSH_1', 'PROMOTION_INTERCEPTION_1', 'PROMOTION_CHARGE', 'PROMOTION_FORMATION_1']
PRID = {p.split('_', 1)[1]: i for i, p in enumerate(PROMOS)}
AIR = {'TRIPLANE', 'WWI_BOMBER'}; NAVAL = {'IRONCLAD', 'DESTROYER', 'BATTLESHIP', 'SUBMARINE', 'CARGO_SHIP'}; CIVIL = {'GREAT_GENERAL', 'WORKER', 'CARAVAN', 'CARGO_SHIP'}
VET = ['DRILL_1', 'SHOCK_1']; COSSACK = ['MOBILITY', 'SHOCK_1']; GERMAN = ['DRILL_1', 'COVER_1']
DEPLOY = [   # (type, owner, lon, lat, promotions, xp, count)
    # --- RSFSR: a big, green army around Moscow and Petrograd, thin screens on the Volga, the Don and in the Urals
    ('GREAT_WAR_INFANTRY', RED, 37.62, 55.75, [], 8, 4), ('ARTILLERY', RED, 37.62, 55.75, [], 8, 2), ('GATLINGGUN', RED, 37.62, 55.75, [], 8, 1), ('CAVALRY', RED, 37.62, 55.75, [], 8, 1),
    ('GREAT_WAR_INFANTRY', RED, 37.7, 55.6, ['DRILL_1'], 20, 2), ('GREAT_GENERAL', RED, 37.62, 55.75, [], 0, 1), ('TRIPLANE', RED, 37.62, 55.75, [], 10, 2), ('WWI_BOMBER', RED, 37.62, 55.75, [], 10, 1),
    ('GREAT_WAR_INFANTRY', RED, 30.32, 59.94, [], 8, 3), ('RIFLEMAN', RED, 30.32, 59.94, [], 5, 2), ('ARTILLERY', RED, 30.32, 59.94, [], 8, 1), ('GATLINGGUN', RED, 30.32, 59.94, [], 5, 1),
    ('BATTLESHIP', RED, 29.6, 60.0, [], 15, 2), ('DESTROYER', RED, 29.3, 59.95, [], 10, 2), ('SUBMARINE', RED, 29.0, 60.0, [], 10, 1), ('TRIPLANE', RED, 30.32, 59.94, [], 10, 1),
    ('GREAT_WAR_INFANTRY', RED, 28.33, 57.82, [], 5, 1), ('RIFLEMAN', RED, 31.27, 58.52, [], 5, 1), ('RIFLEMAN', RED, 34.36, 61.79, [], 5, 1), ('RIFLEMAN', RED, 39.89, 59.22, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 32.05, 54.78, [], 8, 2), ('RIFLEMAN', RED, 30.2, 55.19, [], 5, 1), ('RIFLEMAN', RED, 27.56, 53.9, [], 5, 1), ('GREAT_WAR_INFANTRY', RED, 30.98, 52.44, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 36.08, 52.97, [], 8, 1), ('GREAT_WAR_INFANTRY', RED, 36.19, 51.73, [], 8, 2), ('GATLINGGUN', RED, 36.19, 51.73, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 39.2, 51.67, [], 8, 2), ('CAVALRY', RED, 39.2, 51.67, [], 5, 1), ('ARTILLERY', RED, 39.2, 51.67, [], 5, 1), ('GREAT_WAR_INFANTRY', RED, 41.45, 52.72, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 44.52, 48.7, ['COVER_1'], 10, 3), ('ARTILLERY', RED, 44.52, 48.7, [], 8, 2), ('GATLINGGUN', RED, 44.52, 48.7, [], 8, 1), ('CAVALRY', RED, 44.5, 48.9, [], 5, 1),
    ('GREAT_GENERAL', RED, 44.52, 48.7, [], 0, 1), ('IRONCLAD', RED, 48.0, 46.1, [], 5, 1), ('GREAT_WAR_INFANTRY', RED, 48.04, 46.35, [], 5, 1), ('IRONCLAD', RED, 48.3, 45.8, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 46.03, 51.53, [], 8, 2), ('ARTILLERY', RED, 46.03, 51.53, [], 5, 1), ('GREAT_WAR_INFANTRY', RED, 45.0, 53.2, [], 5, 1), ('RIFLEMAN', RED, 48.47, 53.16, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 48.4, 54.32, [], 5, 1), ('GREAT_WAR_INFANTRY', RED, 49.12, 55.79, [], 8, 2), ('ARTILLERY', RED, 49.12, 55.79, [], 5, 1), ('RIFLEMAN', RED, 49.12, 55.79, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 44.0, 56.33, [], 8, 1), ('RIFLEMAN', RED, 56.25, 58.01, [], 5, 1), ('GREAT_WAR_INFANTRY', RED, 60.6, 56.84, [], 8, 2), ('GATLINGGUN', RED, 60.6, 56.84, [], 5, 1),
    ('RIFLEMAN', RED, 49.67, 58.6, [], 5, 1), ('RIFLEMAN', RED, 53.2, 56.85, [], 5, 1), ('RIFLEMAN', RED, 58.57, 51.2, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 41.97, 45.05, [], 5, 2), ('RIFLEMAN', RED, 44.68, 43.03, [], 5, 1), ('RIFLEMAN', RED, 45.69, 43.32, [], 5, 1), ('RIFLEMAN', RED, 43.05, 44.04, [], 5, 1),
    ('CAVALRY', RED, 42.2, 45.4, [], 5, 1), ('RIFLEMAN', RED, 47.5, 42.98, [], 5, 1),
    ('GREAT_WAR_INFANTRY', RED, 69.27, 41.3, [], 5, 2), ('RIFLEMAN', RED, 69.27, 41.3, [], 5, 1), ('RIFLEMAN', RED, 66.96, 39.65, [], 5, 1), ('RIFLEMAN', RED, 70.94, 40.53, [], 5, 1),
    ('RIFLEMAN', RED, 58.38, 37.95, [], 5, 1), ('RIFLEMAN', RED, 76.95, 43.25, [], 5, 1), ('CAVALRY', RED, 69.6, 42.0, [], 5, 1),
    ('WORKER', RED, 37.62, 55.75, [], 0, 3), ('WORKER', RED, 30.32, 59.94, [], 0, 1), ('WORKER', RED, 46.03, 51.53, [], 0, 1), ('WORKER', RED, 69.27, 41.3, [], 0, 1),
    # --- White South: the Don Army and the small, elite Volunteer Army before the Second Kuban campaign
    ('GREAT_WAR_INFANTRY', SOUTH, 40.08, 47.42, VET, 30, 2), ('CAVALRY', SOUTH, 40.08, 47.42, COSSACK, 15, 2), ('ARTILLERY', SOUTH, 40.08, 47.42, [], 10, 1), ('GREAT_GENERAL', SOUTH, 40.08, 47.42, [], 0, 1),
    ('GREAT_WAR_INFANTRY', SOUTH, 40.9, 46.8, VET, 30, 3), ('CAVALRY', SOUTH, 41.0, 46.6, VET, 20, 1), ('ARTILLERY', SOUTH, 40.8, 46.9, [], 10, 1), ('GREAT_GENERAL', SOUTH, 40.9, 46.8, [], 0, 1),
    ('CAVALRY', SOUTH, 39.72, 47.23, COSSACK, 15, 1), ('GREAT_WAR_INFANTRY', SOUTH, 39.72, 47.23, [], 10, 1), ('GATLINGGUN', SOUTH, 39.72, 47.23, [], 10, 1), ('IRONCLAD', SOUTH, 38.5, 47.0, [], 5, 1),
    ('CAVALRY', SOUTH, 40.27, 48.32, COSSACK, 15, 2), ('RIFLEMAN', SOUTH, 40.27, 48.32, [], 5, 1), ('CAVALRY', SOUTH, 42.74, 49.57, COSSACK, 15, 1), ('CAVALRY', SOUTH, 42.0, 50.8, COSSACK, 10, 1),
    ('CAVALRY', SOUTH, 43.05, 48.37, COSSACK, 15, 1), ('RIFLEMAN', SOUTH, 43.05, 48.37, [], 5, 1), ('GATLINGGUN', SOUTH, 42.74, 49.57, [], 5, 1), ('RIFLEMAN', SOUTH, 38.9, 47.22, [], 5, 1),
    ('RIFLEMAN', SOUTH, 38.98, 45.04, [], 5, 1), ('CAVALRY', SOUTH, 38.98, 45.04, COSSACK, 10, 1), ('RIFLEMAN', SOUTH, 37.77, 44.72, [], 5, 1),
    ('WORKER', SOUTH, 40.08, 47.42, [], 0, 2), ('WORKER', SOUTH, 38.98, 45.04, [], 0, 1),
    # --- Siberia: the Czechoslovak Legion along the Trans-Siberian, Komuch's People's Army, Orenburg and Ural Cossacks, Siberian militia
    ('GREAT_WAR_INFANTRY', SIB, 50.15, 53.2, VET, 30, 2), ('ARTILLERY', SIB, 50.15, 53.2, [], 10, 1), ('RIFLEMAN', SIB, 50.15, 53.2, [], 5, 2), ('GREAT_GENERAL', SIB, 50.15, 53.2, [], 0, 1),
    ('GREAT_WAR_INFANTRY', SIB, 61.4, 55.16, VET, 30, 2), ('GATLINGGUN', SIB, 61.4, 55.16, [], 10, 1), ('GREAT_WAR_INFANTRY', SIB, 73.37, 54.99, VET, 30, 1), ('RIFLEMAN', SIB, 73.37, 54.99, [], 5, 2),
    ('ARTILLERY', SIB, 73.37, 54.99, [], 8, 1), ('GREAT_GENERAL', SIB, 73.37, 54.99, [], 0, 1), ('GREAT_WAR_INFANTRY', SIB, 82.93, 55.03, VET, 25, 1), ('RIFLEMAN', SIB, 82.93, 55.03, [], 5, 1),
    ('GREAT_WAR_INFANTRY', SIB, 92.87, 56.01, VET, 25, 1), ('RIFLEMAN', SIB, 104.28, 52.29, [], 5, 1), ('RIFLEMAN', SIB, 84.95, 56.49, [], 5, 1), ('RIFLEMAN', SIB, 65.53, 57.15, [], 5, 1),
    ('CAVALRY', SIB, 55.1, 51.77, COSSACK, 15, 3), ('GREAT_WAR_INFANTRY', SIB, 55.1, 51.77, [], 10, 1), ('ARTILLERY', SIB, 55.1, 51.77, [], 5, 1), ('CAVALRY', SIB, 51.37, 51.23, COSSACK, 15, 2),
    ('RIFLEMAN', SIB, 51.37, 51.23, [], 5, 1), ('GREAT_WAR_INFANTRY', SIB, 55.97, 54.73, [], 10, 1), ('RIFLEMAN', SIB, 55.97, 54.73, [], 5, 1), ('CAVALRY', SIB, 61.57, 54.09, COSSACK, 10, 1),
    ('CAVALRY', SIB, 69.14, 54.87, COSSACK, 10, 1), ('RIFLEMAN', SIB, 65.34, 55.45, [], 5, 1), ('GATLINGGUN', SIB, 50.15, 53.2, [], 10, 1), ('CAVALRY', SIB, 80.25, 50.41, [], 5, 1),
    ('WORKER', SIB, 73.37, 54.99, [], 0, 2), ('WORKER', SIB, 50.15, 53.2, [], 0, 1), ('WORKER', SIB, 55.1, 51.77, [], 0, 1),
    # --- Northern Region: Allied landing force and the Slavo-British Legion
    ('GREAT_WAR_INFANTRY', NORTH, 40.54, 64.54, ['DRILL_1'], 20, 2), ('RIFLEMAN', NORTH, 40.54, 64.54, [], 5, 2), ('ARTILLERY', NORTH, 40.54, 64.54, [], 10, 1), ('GREAT_GENERAL', NORTH, 40.54, 64.54, [], 0, 1),
    ('DESTROYER', NORTH, 40.0, 64.8, [], 10, 2), ('IRONCLAD', NORTH, 39.5, 64.9, [], 5, 1), ('GREAT_WAR_INFANTRY', NORTH, 33.08, 68.97, ['DRILL_1'], 20, 2), ('GATLINGGUN', NORTH, 33.08, 68.97, [], 10, 1),
    ('RIFLEMAN', NORTH, 34.6, 64.95, [], 5, 1), ('RIFLEMAN', NORTH, 38.1, 63.9, [], 5, 1), ('WORKER', NORTH, 40.54, 64.54, [], 0, 2),
    # --- Ukrainian State: German garrisons (leave in November), the Hetman's Serdiuk division, Sich Riflemen, Black Sea fleet remnant
    ('GREAT_WAR_INFANTRY', UKR, 30.52, 50.45, GERMAN, 25, 2), ('GREAT_WAR_INFANTRY', UKR, 36.23, 50.0, GERMAN, 25, 1), ('GREAT_WAR_INFANTRY', UKR, 30.73, 46.48, GERMAN, 25, 1),
    ('GREAT_WAR_INFANTRY', UKR, 35.05, 48.47, GERMAN, 25, 1), ('GREAT_WAR_INFANTRY', UKR, 37.8, 48.0, GERMAN, 25, 1), ('GREAT_WAR_INFANTRY', UKR, 34.1, 44.95, GERMAN, 25, 1), ('GREAT_WAR_INFANTRY', UKR, 36.58, 50.6, GERMAN, 25, 1),
    ('GREAT_WAR_INFANTRY', UKR, 30.52, 50.45, ['DRILL_1'], 10, 2), ('ARTILLERY', UKR, 30.52, 50.45, [], 8, 2), ('GATLINGGUN', UKR, 30.52, 50.45, [], 8, 1), ('CAVALRY', UKR, 30.52, 50.45, [], 5, 1), ('GREAT_GENERAL', UKR, 30.52, 50.45, [], 0, 1),
    ('RIFLEMAN', UKR, 36.23, 50.0, [], 5, 2), ('RIFLEMAN', UKR, 35.05, 48.47, [], 5, 1), ('RIFLEMAN', UKR, 30.73, 46.48, [], 5, 1), ('RIFLEMAN', UKR, 34.55, 49.59, [], 5, 1), ('RIFLEMAN', UKR, 28.66, 50.26, [], 5, 1),
    ('CAVALRY', UKR, 32.26, 48.5, [], 5, 1), ('RIFLEMAN', UKR, 31.3, 51.5, [], 5, 1), ('RIFLEMAN', UKR, 39.3, 48.57, [], 5, 1), ('IRONCLAD', UKR, 33.3, 44.5, [], 5, 1), ('ARTILLERY', UKR, 36.23, 50.0, [], 5, 1),
    ('GREAT_WAR_INFANTRY', UKR, 24.71, 48.92, ['DRILL_1'], 15, 1), ('RIFLEMAN', UKR, 25.6, 49.55, [], 5, 1), ('CAVALRY', UKR, 33.42, 49.07, [], 5, 1),
    ('WORKER', UKR, 30.52, 50.45, [], 0, 2), ('WORKER', UKR, 36.23, 50.0, [], 0, 1), ('WORKER', UKR, 30.73, 46.48, [], 0, 1),
    # --- Poland: the Polnische Wehrmacht and legion cadres; the real army arrives in November
    ('GREAT_WAR_INFANTRY', POL, 21.01, 52.23, ['DRILL_1'], 15, 2), ('RIFLEMAN', POL, 21.01, 52.23, [], 5, 2), ('CAVALRY', POL, 21.01, 52.23, ['MOBILITY'], 10, 1), ('ARTILLERY', POL, 21.01, 52.23, [], 5, 1), ('GREAT_GENERAL', POL, 21.01, 52.23, [], 0, 1),
    ('GREAT_WAR_INFANTRY', POL, 19.94, 50.06, ['DRILL_1'], 15, 1), ('RIFLEMAN', POL, 19.46, 51.77, [], 5, 1), ('GREAT_WAR_INFANTRY', POL, 24.03, 49.84, ['DRILL_1'], 15, 1), ('CAVALRY', POL, 24.03, 49.84, ['MOBILITY'], 10, 1),
    ('RIFLEMAN', POL, 22.57, 51.25, [], 5, 1), ('CAVALRY', POL, 25.28, 54.69, [], 5, 1), ('RIFLEMAN', POL, 23.16, 53.13, [], 5, 1), ('RIFLEMAN', POL, 23.7, 52.1, [], 5, 1), ('ARTILLERY', POL, 24.03, 49.84, [], 5, 1),
    ('WORKER', POL, 21.01, 52.23, [], 0, 2), ('WORKER', POL, 24.03, 49.84, [], 0, 1),
    # --- barbarians: Makhno's anarchists, the Basmachi of Fergana, Dagestani murids, Semirechye bands
    ('CAVALRY', BARB, 36.4, 47.5, ['MOBILITY'], 15, 2), ('RIFLEMAN', BARB, 36.1, 47.75, ['SHOCK_1'], 10, 2), ('CAVALRY', BARB, 71.5, 40.2, ['MOBILITY'], 10, 2), ('RIFLEMAN', BARB, 72.0, 40.6, [], 5, 1),
    ('RIFLEMAN', BARB, 46.6, 42.5, ['DRILL_1'], 10, 2), ('CAVALRY', BARB, 78.5, 44.5, [], 5, 1), ('CAVALRY', BARB, 60.0, 50.0, [], 5, 1),
]
# every city-state keeps a garrison and a worker
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES):
    DEPLOY.append(('GREAT_WAR_INFANTRY', 32 + i, lo, la, ['DRILL_1'], 10, 2 if popk >= 150 else 1)); DEPLOY.append(('WORKER', 32 + i, lo, la, [], 0, 1))
units = []
land_occ = set(); naval_occ = set(); civ_occ = set(); air_count = Counter()
WHITES = {SOUTH, SIB, NORTH}
def place_unit(tp, pl, lo, la, promos, xp):
    allies = WHITES if pl in WHITES else {pl}
    def ok(x, y):
        o = owner[y, x]
        if tp in AIR: return (x, y) in city_at and CITIES[city_at[(x, y)]][3] == pl and air_count[(x, y)] < 4
        if pl == BARB: return is_land[y, x] and elev[y, x] != 2 and (x, y) not in city_at and (x, y) not in land_occ
        if tp in NAVAL: return (not is_land[y, x]) and (not is_lake[y, x] or True) and (x, y) not in naval_occ and (o == NONE or o in allies) and terrain[y, x] in (COAST, OCEAN)
        if not is_land[y, x] or elev[y, x] == 2: return False
        if o != NONE and o not in allies: return False
        if tp == 'CARAVAN': return (x, y) in city_at and CITIES[city_at[(x, y)]][3] == pl and 'cap' in CITIES[city_at[(x, y)]][5]
        if tp in CIVIL: return (x, y) not in civ_occ
        return (x, y) not in land_occ
    t = find_tile(lo, la, ok, 5)
    if t is None: print('  !! cannot place', tp, pl, lo, la); return
    if tp in AIR: air_count[t] += 1
    elif tp in NAVAL: naval_occ.add(t)
    elif tp == 'CARAVAN': pass
    elif tp in CIVIL: civ_occ.add(t)
    else: land_occ.add(t)
    units.append(dict(type=tp, owner=pl, x=t[0], y=t[1], promos=promos, xp=xp))
for pl in range(NP):
    cap = next(c for c in CITIES if c[3] == pl and 'cap' in c[5])
    DEPLOY.append(('CARAVAN', pl, cap[1], cap[2], [], 0, 4))
for tp, pl, lo, la, promos, xp, cnt in DEPLOY:
    for i in range(cnt): place_unit(tp, pl, lo, la, promos, xp)
STR = {'GREAT_WAR_INFANTRY': 50, 'RIFLEMAN': 34, 'CAVALRY': 34, 'ARTILLERY': 28, 'GATLINGGUN': 30, 'TRIPLANE': 35, 'WWI_BOMBER': 50, 'WWI_TANK': 60, 'IRONCLAD': 45, 'DESTROYER': 55, 'BATTLESHIP': 65, 'SUBMARINE': 60}
for pl in list(range(NP)) + [BARB]:
    us = [u for u in units if u['owner'] == pl]
    print(f"  {PLAYERS[pl]['key'] if pl != BARB else 'BARB'}: {len(us)} units, strength {sum(STR.get(u['type'], 0) for u in us)}, {dict(Counter(u['type'] for u in us))}")

# ============================================================== strategic resource balance (horses for the cavalry, coal for ironclads, oil for the few modern pieces)
UNIT_RES = {'CAVALRY': 'HORSE', 'IRONCLAD': 'COAL', 'WWI_TANK': 'OIL', 'BATTLESHIP': 'OIL', 'DESTROYER': 'OIL', 'SUBMARINE': 'OIL', 'TRIPLANE': 'OIL', 'WWI_BOMBER': 'OIL'}
BLD_RES = {'BUILDING_FACTORY': 'COAL'}
STRATEGIC = ('IRON', 'HORSE', 'COAL', 'OIL')
DEPOSITS = {RED: {'HORSE': [(40.5, 54.5), (43.0, 52.0), (47.0, 52.5)], 'COAL': [(38.5, 54.1), (37.0, 55.3)], 'OIL': [(47.0, 48.0), (54.0, 55.0)]},
            SOUTH: {'HORSE': [(41.0, 47.0), (39.5, 46.0)], 'COAL': [(40.0, 48.5)], 'OIL': [(40.0, 44.8)]},
            SIB: {'HORSE': [(57.0, 53.0), (70.0, 54.5)], 'COAL': [(86.0, 55.5)], 'OIL': [(52.5, 48.5)]},
            NORTH: {'HORSE': [(41.0, 64.0)], 'COAL': [(33.5, 68.5)], 'OIL': [(40.0, 65.0)]},
            UKR: {'HORSE': [(33.0, 49.5), (31.0, 47.5)], 'COAL': [(38.0, 48.3)], 'OIL': [(34.5, 45.0)]},
            POL: {'HORSE': [(22.0, 52.5), (20.5, 51.0)], 'COAL': [(19.3, 50.4)], 'OIL': [(23.5, 49.4)]}}
AMOUNT = {'OIL': 4, 'COAL': 6, 'HORSE': 4, 'IRON': 4}
def res_name(x, y): return RESOURCES[resource[y, x]].split('_', 1)[1] if resource[y, x] != NONE else None
def improve_strategic(x, y):
    r = res_name(x, y)
    if (x, y) in city_at or r not in STRATEGIC or not is_land[y, x] or elev[y, x] == 2: return
    improvement[y, x] = IID['WELL'] if r == 'OIL' else IID['PASTURE'] if r == 'HORSE' else IID['MINE']
    if feature[y, x] in (FOREST, MARSH): feature[y, x] = NONE
need = {pl: Counter() for pl in range(NP)}
for u in units:
    if u['type'] in UNIT_RES and u['owner'] < NP: need[u['owner']][UNIT_RES[u['type']]] += 1
for ci, c in enumerate(CITIES):
    if c[3] < NP:
        for b in city_buildings(ci):
            if b in BLD_RES: need[c[3]][BLD_RES[b]] += 1
def supply_of(pl):
    sup = Counter()
    for y in range(H):
        for x in range(W):
            r = res_name(x, y)
            if r in STRATEGIC and owner[y, x] == pl and is_land[y, x] and elev[y, x] != 2: sup[r] += int(resamt[y, x])
    return sup
for pl in range(NP):
    sup = supply_of(pl)
    for r in ('HORSE', 'COAL', 'OIL'):
        cands = list(DEPOSITS.get(pl, {}).get(r, []))
        while sup[r] < need[pl][r] + 2:
            t = None
            while cands and t is None:
                lo, la = cands.pop(0)
                t = find_tile(lo, la, lambda x, y, pl=pl: is_land[y, x] and owner[y, x] == pl and resource[y, x] == NONE and elev[y, x] != 2 and (x, y) not in city_at and terrain[y, x] != SNOW, 3)
            if t is None:
                for k in range(20000):
                    x = int(rnd(pl, k, 'fbx') * W); y = int(rnd(pl, k, 'fby') * H)
                    if is_land[y, x] and owner[y, x] == pl and resource[y, x] == NONE and elev[y, x] != 2 and (x, y) not in city_at and feature[y, x] != MARSH and terrain[y, x] != SNOW: t = (x, y); break
            if t is None: print('  !! cannot add', r, 'for', PLAYERS[pl]['key']); break
            resource[t[1], t[0]] = RID[r]; resamt[t[1], t[0]] = AMOUNT[r]
            if r == 'COAL' and elev[t[1], t[0]] == 0: elev[t[1], t[0]] = 1
            if r == 'HORSE' and feature[t[1], t[0]] in (FOREST, MARSH): feature[t[1], t[0]] = NONE
            sup[r] += AMOUNT[r]
for y in range(H):
    for x in range(W):
        if owner[y, x] != NONE and owner[y, x] < 32: improve_strategic(x, y)
for pl in range(NP):
    sup = supply_of(pl)
    print(f"  {PLAYERS[pl]['key']} strategic: " + ', '.join(f"{r} {sup[r]}/{need[pl][r]}" for r in STRATEGIC))

# ============================================================== scenario data
TECH_ERAS = json.load(open(f'{XMLDIR}/TECH_ERAS.json'))
EARLY = {'ERA_ANCIENT', 'ERA_CLASSICAL', 'ERA_MEDIEVAL', 'ERA_RENAISSANCE', 'ERA_INDUSTRIAL'}
TECHS = sorted([t for t, e in TECH_ERAS.items() if e in EARLY] + ['TECH_FLIGHT', 'TECH_COMBUSTION', 'TECH_REPLACEABLE_PARTS', 'TECH_RAILROAD', 'TECH_REFRIGERATION'])
TRAD = ['POLICY_TRADITION', 'POLICY_ARISTOCRACY', 'POLICY_OLIGARCHY', 'POLICY_LEGALISM', 'POLICY_LANDED_ELITE', 'POLICY_MONARCHY', 'POLICY_TRADITION_FINISHER']
HONOR = ['POLICY_HONOR', 'POLICY_WARRIOR_CODE', 'POLICY_DISCIPLINE', 'POLICY_MILITARY_TRADITION', 'POLICY_MILITARY_CASTE', 'POLICY_PROFESSIONAL_ARMY', 'POLICY_HONOR_FINISHER']
LIBERTY = ['POLICY_LIBERTY', 'POLICY_COLLECTIVE_RULE', 'POLICY_CITIZENSHIP', 'POLICY_REPUBLIC', 'POLICY_REPRESENTATION', 'POLICY_MERITOCRACY', 'POLICY_LIBERTY_FINISHER']
PLAYER_POLICIES = {
    RED: LIBERTY + HONOR + ['POLICY_HERO_OF_THE_PEOPLE', 'POLICY_SOCIALIST_REALISM', 'POLICY_YOUNG_PIONEERS'],
    SOUTH: TRAD + HONOR[:4] + ['POLICY_ELITE_FORCES', 'POLICY_MOBILIZATION'],
    SIB: TRAD + HONOR[:3] + ['POLICY_ELITE_FORCES', 'POLICY_FORTIFIED_BORDERS'],
    NORTH: TRAD + HONOR[:3] + ['POLICY_FORTIFIED_BORDERS', 'POLICY_MOBILIZATION'],
    UKR: TRAD + HONOR[:3],
    POL: TRAD + HONOR[:4],
}
POLICIES = sorted({p for v in PLAYER_POLICIES.values() for p in v})
VICTORIES = ['VICTORY_DOMINATION']
GAMEOPTIONS = ['GAMEOPTION_RAGING_BARBARIANS', 'GAMEOPTION_NO_GOODY_HUTS', 'GAMEOPTION_NO_LEAGUES', 'GAMEOPTION_NO_RELIGION', 'GAMEOPTION_NO_HAPPINESS',
               'GAMEOPTION_NO_TUTORIAL', 'GAMEOPTION_DISABLE_START_BIAS', 'GAMEOPTION_NO_SCIENCE', 'GAMEOPTION_POLICY_SAVING']

def cfix(s, n):
    b = s.encode('utf-8')[:n - 1]; return b + b'\0' * (n - len(b))
def strlist(names): return b''.join(n.encode() + b'\0' for n in names)
def plist(names): return b''.join(bytes([len(n)]) + n.encode() + b'\0' for n in names)
def bitset(names, index, nbytes):
    b = bytearray(nbytes)
    for n in names:
        i = index[n]; b[i // 8] |= 1 << (i % 8)
    return bytes(b)
def pow2(n, lo=64):
    c = lo
    while c < n: c *= 2
    return c
P = NP; CS = NCS; T = P + CS
tile_units = defaultdict(list)
for i, u in enumerate(units): tile_units[(u['x'], u['y'])].append(i)
for t in tile_units: tile_units[t].sort(key=lambda i: (units[i]['type'] in CIVIL, units[i]['type'] in AIR, i))
ucap = pow2(len(units) + 1); urec = bytearray(); next_of = {}
for t, lst in tile_units.items():
    for a, b in zip(lst, lst[1:]): next_of[a] = b
for i in range(ucap):
    if i < len(units):
        u = units[i]; tp = u['type']; t = (u['x'], u['y']); status = 0
        if tp not in CIVIL: status |= 0x01
        if t in city_at and tp not in AIR and tp not in CIVIL and tile_units[t][0] == i: status |= 0x04
        # experience is written as 0: pre-placed promotions stay, but nobody starts with a promotion pending
        urec += struct.pack('<HHIIIBBBB', next_of.get(i, 0xFFFF), 0xFFFF, 0, 100000, UID[tp], u['owner'], 0, status, 0)
        urec += bitset(['PROMOTION_' + p for p in u['promos']], {p: i2 for i2, p in enumerate(PROMOS)}, 64)
    else:
        urec += struct.pack('<HHIIIBBBB', i + 1 if i + 1 < ucap else 0xFFFF, 0xFFFF, 0, 0, 0xFFFFFFFF, 0, 0, 0, 0) + bytes(64)
unit_data = struct.pack('<I', len(units)) + bytes(urec)
ccap = pow2(len(CITIES) + 1); crec = bytearray()
for i in range(ccap):
    if i < len(CITIES):
        name, lo, la, pl, popk, tags = CITIES[i]
        crec += cfix(name, 64) + struct.pack('<BBHI', pl, 0, civ_pop(popk), 100000) + bitset(city_buildings(i), BID, 64)
    else: crec += bytes(136)
city_data = struct.pack('<I', len(CITIES)) + bytes(crec)
def relbits(pairs):
    nbits = T * (T - 1) // 2; b = bytearray((nbits + 7) // 8)
    for i, j in pairs:
        lg, sm = max(i, j), min(i, j); k = lg * (lg - 1) // 2 + sm; b[k // 8] |= 1 << (k % 8)
    return bytes(b)
majors = [(i, j) for i in range(P) for j in range(i)]
contact = majors + [(i, P + k) for i in range(P) for k in range(CS)]
war = [(RED, SOUTH), (RED, SIB), (RED, NORTH)]
white_peace = [(SOUTH, SIB), (SOUTH, NORTH), (SIB, NORTH)]
rel = relbits(contact) + relbits(war) + relbits(war + white_peace) + relbits(white_peace) + relbits([])
influence = bytes(P * 64 * 4)
visibility = b'\xff' * ((W * H * T + 7) // 8)
team_data = b''.join(cfix(f'Team {i + 1}', 32) + bitset(TECHS, {t: k for k, t in enumerate(TECHS)}, 32) for i in range(T))
player_data = b''
for i, p in enumerate(PLAYERS):
    cap = city_tiles[next(ci for ci, c in enumerate(CITIES) if c[3] == i and 'cap' in c[5])]
    player_data += bitset(PLAYER_POLICIES[i], {n: k for k, n in enumerate(POLICIES)}, 32)
    player_data += cfix(p['leader'], 64) + cfix(p['name'], 64) + cfix(p['civ'], 64) + cfix(p['color'], 64) + cfix('ERA_MODERN', 64) + cfix('HANDICAP_PRINCE', 64)
    player_data += struct.pack('<IIIIBB2s', 0, p['gold'], cap[0], cap[1], i, 1, b'\0\0')
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES):
    t = city_tiles[CNAME[name]]
    player_data += bytes(32) + cfix('', 64) + cfix('', 64) + cfix(mtype, 64) + cfix('PLAYERCOLOR_MINOR_WHITE', 64) + cfix('ERA_MODERN', 64) + cfix('HANDICAP_CHIEFTAIN', 64)
    player_data += struct.pack('<IIIIBB2s', 0, 200, t[0], t[1], P + i, 0, b'\0\0')
plot_data = bytearray()
for y in range(H):
    for x in range(W):
        cid = city_at.get((x, y), 0xFFFF); uid = tile_units[(x, y)][0] if (x, y) in tile_units else 0xFFFF
        plot_data += struct.pack('<HHBBBB', cid, uid, owner[y, x], improvement[y, x], route[y, x], route_owner[y, x] if route[y, x] != NONE else NONE)

# ============================================================== write map
terr_b, feat_b, wond_b, res_b = strlist(TERRAINS), strlist(FEATURES), strlist(WONDERS), strlist(RESOURCES)
name_b = b'Russia 1918\0'
desc_b = (b'1 June 1918. The Russian Civil War from East Prussia to Irkutsk at ~%d km per hex: the RSFSR against the Don and Volunteer armies, the Czechoslovak Legion and Siberia, '
          b'the Allied north, with the Ukrainian State and Poland as players and the border states as city-states. One turn is one week. Domination only.\0' % int(round(HW)))
world_b = b'WORLDSIZE_HUGE'.ljust(64, b'\0')
imp_b, unit_b, tech_b, pol_b, bld_b, prom_b = strlist(IMPROVEMENTS), strlist(UNITS), strlist(TECHS), strlist(POLICIES), strlist(BUILDINGS), strlist(PROMOS)
vict_b, opt_b = plist(VICTORIES), plist(GAMEOPTIONS)
with open(OUT_MAP, 'wb') as f:
    f.write(struct.pack('<BIIB', 0x8C, W, H, P)); f.write(bytes(4))
    f.write(struct.pack('<7I', len(terr_b), len(feat_b), len(wond_b), len(res_b), 0, len(name_b), len(desc_b)))
    f.write(terr_b + feat_b + wond_b + res_b + name_b + desc_b + struct.pack('<I', 64) + world_b)
    for y in range(H):
        for x in range(W):
            f.write(bytes([terrain[y, x], resource[y, x], feature[y, x], river[y, x], elev[y, x], 4 if is_land[y, x] else 0, wonder[y, x], resamt[y, x]]))
    f.write(struct.pack('<64sIIIiBBBB9I', b'GAMESPEED_QUICK', 0, 0, 0, 1918, P, CS, T, 0,
                        len(imp_b), len(unit_b), len(tech_b), len(pol_b), len(bld_b), len(prom_b), len(unit_data), 0, len(city_data)))
    f.write(struct.pack('<II', len(vict_b), len(opt_b)))
    f.write(imp_b + unit_b + tech_b + pol_b + bld_b + prom_b + unit_data + city_data + vict_b + opt_b + rel + influence + visibility)
    f.write(team_data + player_data + bytes(plot_data))
print('wrote', OUT_MAP, os.path.getsize(OUT_MAP), 'bytes;', len(CITIES), 'cities,', len(units), 'units')
land_n = int(is_land.sum()); print(f'land {land_n} ({land_n/(W*H):.1%}) mountains {int((elev==2).sum())} hills {int((elev==1).sum())} forest {int((feature==FOREST).sum())} marsh {int((feature==MARSH).sum())} tundra {int((terrain==TUNDRA).sum())} snow {int((terrain==SNOW).sum())} desert {int((terrain==DESERT).sum())} lakes {int(is_lake.sum())}')
print('  owned tiles:', {PLAYERS[k]['key']: int((owner == k).sum()) for k in range(NP)}, 'city-states', int(((owner >= 32) & (owner < 96)).sum()))
json.dump(dict(W=W, H=H, cities={c[0]: dict(x=city_tiles[i][0], y=city_tiles[i][1], owner=int(c[3])) for i, c in enumerate(CITIES)}), open(os.path.join(HERE, 'map_layout.json'), 'w'), indent=0)

# ============================================================== mod wrapper
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest().upper()
UI_FILES = ['Russia1918LoadScreen.lua', 'Russia1918LoadScreen.xml', 'Russia1918_Production.lua', 'Russia1918_Production.xml', 'Russia1918_Events.lua', 'Russia1918_Events.xml', 'Russia1918_Uniques.sql', 'Russia1918_Text.xml']
for fn in UI_FILES:
    src = os.path.join(HERE, 'ui', fn)
    if os.path.exists(src): shutil.copy(src, os.path.join(OUT_DIR, fn))
    else: print('  !! missing ui file', fn)
WONDERS_OFF = [l.strip() for l in open(f'{XMLDIR}/WORLD_WONDERS.txt') if l.strip()]
rules = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Russia 1918: no world wonders, no Manhattan Project, no Apollo Program; weekly calendar parked; border states as city-states; faction colours. -->', '<GameData>', '  <Buildings>']
for w in WONDERS_OFF: rules.append(f'    <Update><Where Type="{w}" /><Set PrereqTech="TECH_FUTURE_TECH" /></Update>')
rules += ['  </Buildings>', '  <Projects>', '    <Update><Where Type="PROJECT_MANHATTAN_PROJECT" /><Set TechPrereq="TECH_FUTURE_TECH" /></Update>',
          '    <Update><Where Type="PROJECT_APOLLO_PROGRAM" /><Set TechPrereq="TECH_FUTURE_TECH" /></Update>', '  </Projects>',
          '  <GameSpeed_Turns>', '    <Delete GameSpeedType="GAMESPEED_STANDARD" />',
          '    <Row><GameSpeedType>GAMESPEED_STANDARD</GameSpeedType><MonthIncrement>1</MonthIncrement><TurnsPerIncrement>100000</TurnsPerIncrement></Row>',
          '    <Delete GameSpeedType="GAMESPEED_QUICK" />',
          '    <Row><GameSpeedType>GAMESPEED_QUICK</GameSpeedType><MonthIncrement>1</MonthIncrement><TurnsPerIncrement>100000</TurnsPerIncrement></Row>',
          '  </GameSpeed_Turns>', '  <Defines>', '    <Update><Where Name="START_YEAR" /><Set Value="1918" /></Update>', '  </Defines>', '  <Colors>']
def rgb(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
PCOL = {'RED': ('#FFD700', '#B00000'), 'SOUTH': ('#1F4E9A', '#F2F2F2'), 'SIB': ('#FFFFFF', '#2E7D32'), 'NORTH': ('#FFFFFF', '#0B3D91'), 'UKR': ('#FFD500', '#005BBB'), 'POL': ('#FFFFFF', '#DC143C')}
for k, (icon, bg) in PCOL.items():
    for suf, h in (('ICON', icon), ('BG', bg)):
        r, g, b = rgb(h); rules.append(f'    <Row><Type>COLOR_PLAYER_RUS1918_{k}_{suf}</Type><Red>{r:.3f}</Red><Green>{g:.3f}</Green><Blue>{b:.3f}</Blue><Alpha>1</Alpha></Row>')
rules += ['  </Colors>', '  <PlayerColors>']
for k in PCOL: rules.append(f'    <Row><Type>PLAYERCOLOR_RUS1918_{k}</Type><PrimaryColor>COLOR_PLAYER_RUS1918_{k}_ICON</PrimaryColor><SecondaryColor>COLOR_PLAYER_RUS1918_{k}_BG</SecondaryColor><TextColor>COLOR_PLAYER_WHITE_TEXT</TextColor></Row>')
rules += ['  </PlayerColors>', '  <Civilizations>']
for p in PLAYERS: rules.append(f'    <Update><Where Type="{p["civ"]}" /><Set DefaultPlayerColor="{p["color"]}" /></Update>')
rules += ['  </Civilizations>', '  <MinorCivilizations>']
MCOL = ['PLAYERCOLOR_MINOR_LIGHT_BLUE', 'PLAYERCOLOR_MINOR_LIGHT_GREEN', 'PLAYERCOLOR_MINOR_GOLDENROD', 'PLAYERCOLOR_MINOR_LIGHT_PURPLE', 'PLAYERCOLOR_MINOR_GRAY', 'PLAYERCOLOR_MINOR_DARK_LEMON',
        'PLAYERCOLOR_MINOR_PEACH', 'PLAYERCOLOR_MINOR_MIDDLE_CYAN', 'PLAYERCOLOR_MINOR_PURPLE', 'PLAYERCOLOR_MINOR_WHITE', 'PLAYERCOLOR_MINOR_LIGHT_GREEN', 'PLAYERCOLOR_MINOR_GOLDENROD', 'PLAYERCOLOR_MINOR_PEACH']
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES):
    tk = f'TXT_KEY_CITYSTATE_RUS1918_{key}'
    rules.append(f'    <Row><Type>{mtype}</Type><Description>{tk}</Description><Civilopedia>{tk}</Civilopedia><ShortDescription>{tk}</ShortDescription><Adjective>{tk}</Adjective><ArtDefineTag>ART_DEF_CIVILIZATION_MINOR</ArtDefineTag><DefaultPlayerColor>{MCOL[i]}</DefaultPlayerColor><ArtStyleType>ARTSTYLE_EUROPEAN</ArtStyleType><ArtStyleSuffix>_EURO</ArtStyleSuffix><ArtStylePrefix>EUROPEAN </ArtStylePrefix><MinorCivTrait>{trait}</MinorCivTrait></Row>')
rules += ['  </MinorCivilizations>', '  <MinorCivilization_CityNames>']
for key, name, mtype, trait, lo, la, popk in CITY_STATES: rules.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><CityName>TXT_KEY_CITY_RUS1918_{key}</CityName></Row>')
rules += ['  </MinorCivilization_CityNames>', '  <MinorCivilization_Flavors>']
for key, name, mtype, trait, lo, la, popk in CITY_STATES:
    for fl, v in (('FLAVOR_CITY_DEFENSE', 9), ('FLAVOR_DEFENSE', 9), ('FLAVOR_GROWTH', 4), ('FLAVOR_GOLD', 5), ('FLAVOR_PRODUCTION', 5)):
        rules.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><FlavorType>{fl}</FlavorType><Flavor>{v}</Flavor></Row>')
rules += ['  </MinorCivilization_Flavors>', '</GameData>', '']
open(os.path.join(OUT_DIR, 'Russia1918_Rules.xml'), 'w').write('\n'.join(rules))
# --- leader art: static diplomacy scenes, portrait atlas, faction emblem atlases, Dawn of Man images (built by art/build_art.py)
ART = os.path.join(HERE, 'art', 'out'); art_files = []
if os.path.isdir(ART):
    for f in sorted(glob.glob(os.path.join(ART, '*.dds'))):
        shutil.copy(f, os.path.join(OUT_DIR, os.path.basename(f))); art_files.append(os.path.basename(f))
    shutil.copy(os.path.join(HERE, 'art', 'src', 'CREDITS.txt'), os.path.join(OUT_DIR, 'CREDITS.txt'))
LEADER_ART = [('LEADER_CATHERINE', 'CIVILIZATION_RUSSIA', 'Lenin'), ('LEADER_BISMARCK', 'CIVILIZATION_GERMANY', 'Denikin'), ('LEADER_POCATELLO', 'CIVILIZATION_SHOSHONE', 'Kolchak'),
              ('LEADER_ELIZABETH', 'CIVILIZATION_ENGLAND', 'Yudenich'), ('LEADER_SELASSIE', 'CIVILIZATION_ETHIOPIA', 'Skoropadsky'), ('LEADER_CASIMIR', 'CIVILIZATION_POLAND', 'Pilsudski')]
scene_files = []
if art_files:
    for i, (ld, cv, key) in enumerate(LEADER_ART):
        fn = f'RUS1918_{key}_Scene.xml'; scene_files.append(fn)
        open(os.path.join(OUT_DIR, fn), 'w').write(f'<?xml version="1.0" encoding="utf-8"?>\n<LeaderScene FallbackImage="RUS1918_Scene_{key}.dds">\n</LeaderScene>\n')
    lx = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Russia 1918: static leader scenes, portrait atlas, faction emblems and Dawn of Man images (Firaxis Civil War technique). -->', '<GameData>', '  <IconTextureAtlases>']
    for size in (256, 128, 64): lx.append(f'    <Row><Atlas>RUS1918_LEADER_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>RUS1918_Leaders{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    for size in (256, 128, 80, 64, 45, 32): lx.append(f'    <Row><Atlas>RUS1918_CIV_COLOR_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>RUS1918_CivColor{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    for size in (128, 64, 48, 32, 24, 16): lx.append(f'    <Row><Atlas>RUS1918_CIV_ALPHA_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>RUS1918_CivWhite{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    lx += ['  </IconTextureAtlases>', '  <Leaders>']
    for i, (ld, cv, key) in enumerate(LEADER_ART): lx.append(f'    <Update><Where Type="{ld}" /><Set ArtDefineTag="RUS1918_{key}_Scene.xml" PortraitIndex="{i}" IconAtlas="RUS1918_LEADER_ATLAS" /></Update>')
    lx += ['  </Leaders>', '  <Civilizations>']
    for i, (ld, cv, key) in enumerate(LEADER_ART): lx.append(f'    <Update><Where Type="{cv}" /><Set PortraitIndex="{i}" IconAtlas="RUS1918_CIV_COLOR_ATLAS" AlphaIconAtlas="RUS1918_CIV_ALPHA_ATLAS" DawnOfManImage="RUS1918_DOM_{key}.dds" /></Update>')
    lx += ['  </Civilizations>', '</GameData>', '']
    open(os.path.join(OUT_DIR, 'Russia1918_Leaders.xml'), 'w').write('\n'.join(lx))
def filerow(fn, imp): return f'    <File md5="{md5(os.path.join(OUT_DIR, fn))}" import="{imp}">{fn}</File>'
FILES_XML = '\n'.join([filerow('Russia1918.Civ5Map', 1), filerow('Russia1918_Rules.xml', 0)] + [filerow(fn, 0) for fn in UI_FILES if os.path.exists(os.path.join(OUT_DIR, fn))]
                      + ([filerow('Russia1918_Leaders.xml', 0), filerow('CREDITS.txt', 0)] if art_files else []) + [filerow(f, 1) for f in scene_files] + [filerow(f, 1) for f in art_files])
LEADERS_DB = '      <UpdateDatabase>Russia1918_Leaders.xml</UpdateDatabase>\n' if art_files else ''
MODINFO = f'''<?xml version="1.0" encoding="utf-8"?>
<Mod id="5e2a9d1c-1918-4c7b-8a3f-9d4b6e0c2f17" version="3">
  <Properties>
    <Name>Russia 1918</Name>
    <Teaser>The Russian Civil War from 1 June 1918: Reds, the White South, Siberia, the Allied North, Ukraine and Poland on a {W}x{H} map from East Prussia to Irkutsk.</Teaser>
    <Description>Russia, Ukraine, Belarus, Poland, the Baltic, the Caucasus, Central Asia and Siberia to Lake Baikal as of 1 June 1918. The RSFSR (Russia) is at permanent war with the Don and Volunteer armies (Germany donor), the Czechoslovak Legion and Siberia (Shoshone) and the Allied Northern Region (England); the Ukrainian State (Ethiopia) and Poland (Poland) decide for themselves; Finland, the Baltic states, Romania, the Caucasus republics, the Ottomans, Persia, Bukhara and Khiva are city-states; Makhno, the Basmachi and the Greens are raging barbarians. One turn is one week; dated events bring the Allied landings, Kolchak, the Red cavalry, the Polish army and the German withdrawal. Domination victory only. Start it from the Mods menu via the scenario button.</Description>
    <Authors>cryptoboy2283</Authors>
    <SpecialThanks>Natural Earth, NOAA ETOPO 2022, Koppen-Geiger, Civ5MapImage</SpecialThanks>
    <AffectsSavedGames>1</AffectsSavedGames>
    <MinCompatibleSaveVersion>0</MinCompatibleSaveVersion>
    <SupportsSinglePlayer>1</SupportsSinglePlayer>
    <SupportsMultiplayer>1</SupportsMultiplayer>
    <SupportsHotSeat>1</SupportsHotSeat>
    <SupportsMac>1</SupportsMac>
    <ReloadAudioSystem>0</ReloadAudioSystem>
    <ReloadLandmarkSystem>0</ReloadLandmarkSystem>
    <ReloadLeaderSystem>1</ReloadLeaderSystem>
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
{FILES_XML}
  </Files>
  <Actions>
    <OnModActivated>
      <UpdateDatabase>Russia1918_Rules.xml</UpdateDatabase>
      <UpdateDatabase>Russia1918_Uniques.sql</UpdateDatabase>
{LEADERS_DB}      <UpdateDatabase>Russia1918_Text.xml</UpdateDatabase>
    </OnModActivated>
  </Actions>
  <EntryPoints>
    <EntryPoint type="Custom" file="Russia1918LoadScreen.xml">
      <Name>Russia 1918</Name>
      <Description>June 1918: Reds, Whites, the Allied North, Ukraine and Poland. Choose your side and difficulty.</Description>
    </EntryPoint>
    <EntryPoint type="InGameUIAddin" file="Russia1918_Production.xml">
      <Name>Russia 1918 setup</Name>
      <Description>Production queues, unit names, White cooperation, weekly calendar.</Description>
    </EntryPoint>
    <EntryPoint type="InGameUIAddin" file="Russia1918_Events.xml">
      <Name>Russia 1918 events</Name>
      <Description>Dated events of the Civil War, June 1918 to 1921.</Description>
    </EntryPoint>
  </EntryPoints>
</Mod>
'''
open(os.path.join(OUT_DIR, 'Russia1918.modinfo'), 'w').write(MODINFO)

# ============================================================== preview
S = 8
img = Image.new('RGB', (int((W + 0.5) * S) + 2, int(H * S * 0.866 + S) + 2), (10, 30, 70)); d = ImageDraw.Draw(img)
TCOL = {GRASS: (96, 168, 64), PLAINS: (196, 178, 96), DESERT: (236, 214, 150), TUNDRA: (170, 170, 150), SNOW: (240, 240, 240), COAST: (70, 140, 210), OCEAN: (20, 60, 130)}
OCOL = {RED: (210, 30, 30), SOUTH: (240, 240, 240), SIB: (40, 150, 70), NORTH: (30, 60, 170), UKR: (230, 200, 30), POL: (220, 90, 160), BARB: (0, 0, 0)}
def pcenter(x, y): return (x + 0.5 + 0.5 * (y & 1)) * S + 1, img.size[1] - (y * 0.866 * S + 0.577 * S) - 1
def pcorners(x, y, f=1.0):
    cx, cy = pcenter(x, y); r = S / math.sqrt(3) * f
    return [(cx + r * math.cos(math.radians(30 + 60 * k)), cy - r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
for y in range(H):
    for x in range(W):
        col = TCOL[terrain[y, x]]
        if is_lake[y, x]: col = (90, 170, 230)
        if feature[y, x] == FOREST: col = tuple(int(c * 0.6) for c in col)
        if feature[y, x] == MARSH: col = (80, 150, 130)
        if feature[y, x] == ICE: col = (225, 235, 245)
        o = int(owner[y, x])
        if o != NONE:
            oc = OCOL.get(o, (160, 160, 160)); col = tuple(int(c * 0.55 + k * 0.45) for c, k in zip(col, oc))
        d.polygon(pcorners(x, y), fill=col)
        cx, cy = pcenter(x, y)
        if elev[y, x] == 2: d.polygon([(cx - 3, cy + 2), (cx, cy - 3), (cx + 3, cy + 2)], fill=(70, 60, 60))
        elif elev[y, x] == 1: d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], outline=(100, 70, 40))
        if route[y, x] != NONE: d.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=(40, 40, 40))
for y in range(H):
    for x in range(W):
        rv = river[y, x]
        if not rv & 7: continue
        pc = pcorners(x, y)
        if rv & 1: d.line([pc[0], pc[5]], fill=(40, 90, 255), width=1)
        if rv & 2: d.line([pc[4], pc[5]], fill=(40, 90, 255), width=1)
        if rv & 4: d.line([pc[3], pc[4]], fill=(40, 90, 255), width=1)
for u in units:
    cx, cy = pcenter(u['x'], u['y']); oc = OCOL.get(u['owner'], (160, 160, 160))
    if u['owner'] == BARB: d.polygon([(cx - 3, cy + 3), (cx + 3, cy + 3), (cx, cy - 3)], fill=(0, 0, 0), outline=(255, 255, 255))
    elif u['type'] in NAVAL: d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], outline=oc)
    elif u['type'] not in CIVIL and u['type'] not in AIR: d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=oc, outline=(0, 0, 0))
for ci, (name, lo, la, pl, popk, tags) in enumerate(CITIES):
    cx, cy = pcenter(*city_tiles[ci])
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255) if 'cap' not in tags or pl >= 32 else (255, 0, 255), outline=(0, 0, 0))
    if popk >= 60 or 'cap' in tags: d.text((cx + 4, cy - 5), name, fill=(255, 255, 255))
img.save(OUT_PNG); print('wrote', OUT_PNG, img.size)
