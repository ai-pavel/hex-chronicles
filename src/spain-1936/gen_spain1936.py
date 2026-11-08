#!/usr/bin/env python3
"""Spain 1936: Civilization V scenario map of the Spanish Civil War, 25 July 1936.

Region: the Iberian Peninsula, the Balearics, Spanish Morocco with Tangier and the coast of French North Africa, from Cape
Finisterre to Menorca and from the Landes to the Rif, 120 hexes wide (about 11 km per hex). The Canary Islands, Nationalist
from the first day and 1,100 km from Cadiz, are left out.
Data: Natural Earth 10m (land, rivers, first-level regions), NOAA ETOPO 2022 relief, Koppen-Geiger climate.
Factions (25 July 1936): the Republic (Russia donor), Franco's Army of Africa and the South (Zulu), Mola's Army of the North
(Germany), the Generalitat of Catalonia (Shoshone), the Basque Country (Ethiopia), the CNT-FAI columns in Aragon (Aztec);
Portugal, Gibraltar, Tangier, Andorra, France and French North Africa as city-states; fugitives in the sierras as raging
barbarians. One turn = one week; Quick speed; domination only, no timed victories.
"""
import json, math, os, struct, hashlib, heapq, shutil, glob, pickle
from collections import defaultdict, Counter, deque
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('HEX_DATA', os.path.join(HERE, '..', '..', 'data'))        # tools/fetch_data.py
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
MOD_NAME = 'Spain 1936'
OUT_DIR = os.path.join(HERE, 'mod', 'Spain 1936 (v 2)')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_MAP = os.path.join(OUT_DIR, 'Spain1936.Civ5Map')
OUT_PNG = os.path.join(HERE, 'Spain1936_preview.png')

# ============================================================== projection / grid (Albers equal-area conic)
R = 6371.0; LON0 = -2.6
PHI1, PHI2 = math.radians(36.5), math.radians(42.5)
N = (math.sin(PHI1) + math.sin(PHI2)) / 2.0
C = math.cos(PHI1) ** 2 + 2 * N * math.sin(PHI1)
RHO0 = R * math.sqrt(C - 2 * N * math.sin(math.radians(39.4))) / N
def proj(lon, lat):
    phi = math.radians(lat); lam = math.radians(lon - LON0)
    rho = R * math.sqrt(C - 2 * N * math.sin(phi)) / N; th = N * lam
    return rho * math.sin(th), RHO0 - rho * math.cos(th)
def inv_np(x, y):
    dy = RHO0 - y; rho = np.sign(N) * np.sqrt(x * x + dy * dy)
    th = np.arctan2(np.sign(N) * x, np.sign(N) * dy)
    phi = np.arcsin((C - (rho * N / R) ** 2) / (2 * N))
    return np.degrees(th / N) + LON0, np.degrees(phi)

LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -9.9, 4.6, 34.75, 44.0
W = 120
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
    dict(key='REP', civ='CIVILIZATION_RUSSIA', leader='Manuel Azana', name='Spanish Republic', color='PLAYERCOLOR_ESP1936_REP', gold=2500),
    dict(key='NAT', civ='CIVILIZATION_ZULU', leader='Francisco Franco', name='Nationalists', color='PLAYERCOLOR_ESP1936_NAT', gold=1200),
    dict(key='NORTH', civ='CIVILIZATION_GERMANY', leader='Emilio Mola', name='Army of the North', color='PLAYERCOLOR_ESP1936_NORTH', gold=1000),
    dict(key='CAT', civ='CIVILIZATION_SHOSHONE', leader='Lluis Companys', name='Catalonia', color='PLAYERCOLOR_ESP1936_CAT', gold=1500),
    dict(key='EUZ', civ='CIVILIZATION_ETHIOPIA', leader='Jose Antonio Aguirre', name='Euzkadi', color='PLAYERCOLOR_ESP1936_EUZ', gold=800),
    dict(key='CNT', civ='CIVILIZATION_AZTEC', leader='Buenaventura Durruti', name='CNT-FAI', color='PLAYERCOLOR_ESP1936_CNT', gold=600),
]
PIDX = {p['key']: i for i, p in enumerate(PLAYERS)}
REP, NAT, NORTH, CAT, EUZ, CNT = range(6)
NP = len(PLAYERS)
NATS = {NAT, NORTH}; REPS = {REP, CAT, EUZ, CNT}
BARB = 96
NONE = 0xFF
# City-states: (key, EN name of the capital, type, trait, lon, lat, population in thousands)
CITY_STATES = [
    ('PORTUGAL', 'Lisbon', 'MINOR_CIV_ESP1936_PORTUGAL', 'MINOR_TRAIT_MILITARISTIC', -9.14, 38.72, 594),
    ('GIBRALTAR', 'Gibraltar', 'MINOR_CIV_ESP1936_GIBRALTAR', 'MINOR_TRAIT_MARITIME', -5.35, 36.14, 17),
    ('TANGIER', 'Tangier', 'MINOR_CIV_ESP1936_TANGIER', 'MINOR_TRAIT_MERCANTILE', -5.81, 35.77, 60),
    ('ANDORRA', 'Andorra la Vella', 'MINOR_CIV_ESP1936_ANDORRA', 'MINOR_TRAIT_CULTURED', 1.52, 42.51, 5),
    ('FRANCE', 'Perpignan', 'MINOR_CIV_ESP1936_FRANCE', 'MINOR_TRAIT_CULTURED', 2.90, 42.70, 73),
    ('NAFRICA', 'Oran', 'MINOR_CIV_ESP1936_NAFRICA', 'MINOR_TRAIT_MERCANTILE', -0.64, 35.70, 160),
]
NCS = len(CITY_STATES)
CSIDX = {c[0]: i for i, c in enumerate(CITY_STATES)}
# further towns of the city-states (the larger neighbours hold more than one city, so their land is not empty)
CS_TOWNS = [
    ('Oporto', -8.61, 41.15, 'PORTUGAL', 232), ('Coimbra', -8.43, 40.21, 'PORTUGAL', 27), ('Evora', -7.91, 38.57, 'PORTUGAL', 22), ('Faro', -7.93, 37.02, 'PORTUGAL', 13),
    ('Braga', -8.42, 41.55, 'PORTUGAL', 25), ('Guarda', -7.27, 40.54, 'PORTUGAL', 10), ('Elvas', -7.16, 38.88, 'PORTUGAL', 12), ('Santarem', -8.69, 39.24, 'PORTUGAL', 12),
    ('Viseu', -7.91, 40.66, 'PORTUGAL', 10), ('Braganca', -6.76, 41.81, 'PORTUGAL', 6), ('Beja', -7.86, 38.02, 'PORTUGAL', 12), ('Castelo Branco', -7.49, 39.82, 'PORTUGAL', 12),
    ('Toulouse', 1.44, 43.60, 'FRANCE', 195), ('Bayonne', -1.47, 43.49, 'FRANCE', 30), ('Pau', -0.37, 43.30, 'FRANCE', 38), ('Tarbes', 0.08, 43.23, 'FRANCE', 30),
    ('Carcassonne', 2.35, 43.21, 'FRANCE', 32), ('Narbonne', 3.00, 43.18, 'FRANCE', 30), ('Foix', 1.61, 42.97, 'FRANCE', 7), ('Mont-de-Marsan', -0.50, 43.89, 'FRANCE', 14),
    ('Algiers', 3.06, 36.75, 'NAFRICA', 257), ('Tlemcen', -1.32, 34.88, 'NAFRICA', 40), ('Sidi Bel Abbes', -0.63, 35.19, 'NAFRICA', 45), ('Mostaganem', 0.09, 35.93, 'NAFRICA', 35),
    ('Orleansville', 1.33, 36.16, 'NAFRICA', 12), ('Blida', 2.83, 36.47, 'NAFRICA', 30), ('Ouezzane', -5.58, 34.80, 'NAFRICA', 15), ('Nemours', -1.86, 35.10, 'NAFRICA', 8),
]
# Natural Earth first-level regions -> faction holding them on 25 July 1936 (the provinces split by the front are drawn below).
R_NORTH = ['A Coruña', 'Lugo', 'Ourense', 'Pontevedra', 'León', 'Zamora', 'Salamanca', 'Valladolid', 'Palencia', 'Burgos', 'Soria', 'Segovia', 'Ávila', 'Cáceres',
           'Navarre', 'Araba / Álava', 'La Rioja', 'Zaragoza', 'Huesca', 'Teruel']
R_NAT = ['Seville', 'Cádiz', 'Córdoba', 'Ceuta', 'Melilla', 'Balearic Islands']
R_REP = ['Community of Madrid', 'Toledo', 'Ciudad Real', 'Cuenca', 'Guadalajara', 'Albacete', 'Valencia', 'Alicante', 'Castellón', 'Murcia', 'Jaén', 'Almería',
         'Málaga', 'Granada', 'Huelva', 'Badajoz', 'Asturias', 'Cantabria']
R_CAT = ['Barcelona', 'Tarragona', 'Lleida', 'Girona']
R_EUZ = ['Biscay', 'Gipuzkoa']
REGION_OF = {}
for lst, key in ((R_NORTH, 'NORTH'), (R_NAT, 'NAT'), (R_REP, 'REP'), (R_CAT, 'CAT'), (R_EUZ, 'EUZ')):
    for n in lst: REGION_OF[n] = key
CS_ADMIN = {'Portugal': 'PORTUGAL', 'Gibraltar': 'GIBRALTAR', 'Andorra': 'ANDORRA', 'France': 'FRANCE', 'Algeria': 'NAFRICA', 'Morocco': 'NAFRICA'}
def faction_code(f):
    p = f['properties']; adm = p.get('admin'); nm = p.get('name_en') or p.get('name')
    if adm == 'Spain':
        if nm in REGION_OF: return 1 + PIDX[REGION_OF[nm]]
        return None   # the Canaries
    if adm in CS_ADMIN: return 100 + CSIDX[CS_ADMIN[adm]]
    return None
def code(k): return 1 + PIDX[k] if k in PIDX else 100 + CSIDX[k]
# The front of late July 1936 inside the provinces, as (polygon lon/lat, new holder, only over these holders or None).
OVERRIDES = [
    # the Spanish protectorate in Morocco (the rest of Morocco is French) and the international zone of Tangier
    ([(-6.7, 36.3), (-2.30, 36.3), (-2.30, 35.10), (-2.70, 34.95), (-3.30, 34.90), (-3.90, 34.88), (-4.40, 34.83), (-4.90, 34.88), (-5.30, 34.92), (-5.70, 34.96),
      (-6.00, 34.98), (-6.40, 35.00), (-6.7, 35.0)], 'NAT', ['NAFRICA']),
    ([(-6.1, 35.98), (-5.63, 35.98), (-5.63, 35.64), (-5.85, 35.57), (-6.1, 35.62)], 'TANGIER', ['NAT']),
    # Cordoba: the city and the campina south-west of it rose, the Pedroches, the Guadiato and the east stayed Republican
    ([(-5.70, 38.80), (-4.15, 38.80), (-4.15, 37.25), (-4.50, 37.25), (-4.55, 37.80), (-4.72, 37.97), (-5.70, 37.97)], 'REP', ['NAT']),
    # Menorca stayed with the Republic, Mallorca and Ibiza went with the rising
    ([(3.70, 39.70), (4.50, 39.70), (4.50, 40.20), (3.70, 40.20)], 'REP', ['NAT']),
    # Aragon east of the Huesca - Zaragoza - Teruel front: the Catalan and Valencian columns (the Council of Aragon from October)
    ([(-0.38, 42.90), (1.0, 42.90), (1.0, 39.9), (-0.95, 39.9), (-0.85, 40.25), (-0.95, 40.45), (-0.80, 40.62), (-0.70, 40.92), (-0.58, 41.20),
      (-0.48, 41.45), (-0.45, 41.75), (-0.52, 41.95), (-0.32, 42.08), (-0.30, 42.30), (-0.38, 42.55)], 'CNT', ['NORTH']),
    # northern Alava (Llodio, Amurrio, Aramaio) went with Biscay
    ([(-3.25, 43.30), (-2.70, 43.30), (-2.65, 43.00), (-3.25, 43.00)], 'EUZ', ['NORTH']),
    # Somosierra and the Guadarrama passes, taken by Mola's columns in the first days
    ([(-3.80, 41.00), (-3.40, 41.00), (-3.40, 41.25), (-3.80, 41.25)], 'NORTH', ['REP']),
]

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
        if max(lons) < LON_MIN - 6 or min(lons) > LON_MAX + 6 or max(lats) < LAT_MIN - 4 or min(lats) > LAT_MAX + 4: continue
        if max(lons) - min(lons) > 300: continue
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
def poly_mask(ll):
    img = Image.new('L', (IW, IH), 0); ImageDraw.Draw(img).polygon([to_px(proj(lo, la)) for lo, la in ll], fill=255); return np.array(img) > 127

print('rasterizing land / regions...')
LAND = rasterize(json.load(open(f'{DATA}/ne_10m_land.geojson'))['features'], lambda f: 255) > 127
# no lakes: the large water bodies of Natural Earth in Iberia are post-war reservoirs
admin1 = json.load(open(f'{DATA}/ne_10m_admin_1_states_provinces.geojson'))['features']
FACT = rasterize(admin1, faction_code)
for ll, k, only in OVERRIDES:
    m = poly_mask(ll)
    if only: m &= np.isin(FACT, [code(o) for o in only])
    FACT[m] = code(k)
seen_regions = {(f['properties'].get('name_en') or f['properties'].get('name')) for f in admin1 if f['properties'].get('admin') == 'Spain'}
missing = [n for n in REGION_OF if n not in seen_regions]
if missing: print('  !! regions not found in Natural Earth:', missing)

print('loading ETOPO / Koppen...')
ETOPO = np.array(Image.open(f'{DATA}/etopo_es.tif'))   # bbox -10.5..5.0 E, 34.0..44.5 N, 1550x1050 -> 0.01 deg
def etopo_at(lon, lat):
    c = np.clip(((lon + 10.5) / 0.01).astype(int), 0, 1549); r = np.clip(((44.5 - lat) / 0.01).astype(int), 0, 1049)
    return ETOPO[r, c]
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

CACHE = os.path.join(DATA, 'cache', f'spain1936_sample_{W}x{H}.pkl'); os.makedirs(os.path.dirname(CACHE), exist_ok=True)
landfrac = np.zeros((H, W)); emean = np.zeros((H, W)); emax = np.zeros((H, W))
relief = np.zeros((H, W)); depth = np.zeros((H, W)); fact = np.zeros((H, W), int); clim = [[None] * W for _ in range(H)]
if os.path.exists(CACHE) and not os.environ.get('ES_NOCACHE'):
    print('loading cached hex samples...'); landfrac, emean, emax, relief, depth, fact, clim = pickle.load(open(CACHE, 'rb'))
else:
  print('sampling hexes...')
  for y in range(H):
      for x in range(W):
          cx, cy = center(x, y); sx = SAMP[:, 0] + cx; sy = SAMP[:, 1] + cy
          pc = np.clip(((sx - XMIN) / HW * PX).astype(int), 0, IW - 1); pr = np.clip((IH - (sy - YMIN) / HW * PX).astype(int), 0, IH - 1)
          landfrac[y, x] = LAND[pr, pc].mean()
          cc = FACT[pr, pc][LAND[pr, pc]]
          fact[y, x] = Counter(cc.tolist()).most_common(1)[0][0] if len(cc) else 0
          lon, lat = inv_np(sx, sy); e = etopo_at(lon, lat); el = e[e > 0] if (e > 0).any() else e
          emean[y, x] = el.mean(); emax[y, x] = el.max()
          relief[y, x] = np.percentile(el, 95) - np.percentile(el, 5) if len(el) > 3 else 0
          depth[y, x] = e[e <= 0].mean() if (e <= 0).any() else 0
          comp = defaultdict(float)
          for lo, la in zip(lon[::3], lat[::3]): comp[kop_at(lo, la)] += 1
          clim[y][x] = dict(comp)
  pickle.dump((landfrac, emean, emax, relief, depth, fact, clim), open(CACHE, 'wb'))

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

is_lake = np.zeros((H, W), bool)
is_land = landfrac >= 0.45

# ============================================================== terrain classification
# (lon0, lon1, lat0, lat1, marsh probability): the Guadalquivir marshes, the Ebro delta, the Albufera, the Landes
MARSH_BOXES = [(-6.55, -5.95, 36.80, 37.20, 0.55), (0.55, 0.95, 40.55, 40.80, 0.6), (-0.42, -0.28, 39.22, 39.40, 0.5), (-1.30, -0.80, 43.70, 44.10, 0.15)]
# (lon0, lon1, lat0, lat1, extra forest): the dehesas of Extremadura and the Sierra Morena, the pinewoods of Soria and Cuenca, the Landes
FOREST_BOXES = [(-7.3, -4.6, 37.8, 39.9, 0.22), (-3.3, -2.2, 41.65, 42.15, 0.35), (-2.3, -1.3, 39.8, 40.6, 0.35), (-1.30, 0.2, 43.70, 44.10, 0.5)]
for y in range(H):
    for x in range(W):
        lo, la = lonlat(x, y)
        if not is_land[y, x]:
            shallow = depth[y, x] > -150 or any(is_land[b, a] for a, b in neighbors(x, y))
            terrain[y, x] = COAST if shallow else OCEAN
            continue
        rl, mx, mn = relief[y, x], emax[y, x], emean[y, x]
        if rl >= 720 or (mx >= 2000 and rl >= 500): elev[y, x] = 2
        elif rl >= 340 or (mn >= 1100 and rl >= 180): elev[y, x] = 1
        comp = clim[y][x]; tot = sum(comp.values()) or 1
        def frac(pred): return sum(v for k, v in comp.items() if pred(k)) / tot
        fCf = frac(lambda k: k.startswith('Cf'))
        fCsb = frac(lambda k: k == 'Csb')
        fCsa = frac(lambda k: k == 'Csa')
        fBS = frac(lambda k: k.startswith('BS'))
        fBW = frac(lambda k: k.startswith('BW'))
        fCold = frac(lambda k: k.startswith('D') or k.startswith('E'))
        if mn >= 2300: t = SNOW
        elif fCold > 0.5 and mn >= 1700: t = TUNDRA
        else:
            wts = {GRASS: fCf * 0.85 + fCsb * 0.45 + fCsa * 0.18 + fCold * 0.5, PLAINS: fCf * 0.15 + fCsb * 0.55 + fCsa * 0.77 + fBS * 0.70 + fCold * 0.3,
                   DESERT: fCsa * 0.05 + fBS * 0.30 + fBW, TUNDRA: fCold * 0.2}
            r = rnd(x, y, 'terr'); sw = sum(wts.values()) or 1; acc = 0; t = PLAINS
            for k, v in wts.items():
                acc += v / sw
                if r < acc: t = k; break
        terrain[y, x] = t
        if elev[y, x] == 2 or t == SNOW: continue
        pf = fCf * 0.38 + fCsb * 0.20 + fCsa * 0.08 + fCold * 0.30 + (0.12 if elev[y, x] == 1 else 0)
        for lo0, lo1, la0, la1, pfb in FOREST_BOXES:
            if lo0 <= lo <= lo1 and la0 <= la <= la1: pf += pfb
        if t == DESERT: pf = 0
        pm = 0
        for lo0, lo1, la0, la1, pmb in MARSH_BOXES:
            if lo0 <= lo <= lo1 and la0 <= la <= la1 and elev[y, x] == 0 and t in (GRASS, PLAINS): pm = pmb
        r2 = rnd(x, y, 'feat')
        if r2 < pm: feature[y, x] = MARSH
        elif r2 < pm + pf: feature[y, x] = FOREST

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
        for v in sorted(ADJ[u]):
            if v in prev: continue
            prev[v] = u
            if v == b:
                path = [b]
                while prev[path[-1]] is not None: path.append(prev[path[-1]])
                return path[::-1]
            q.append((v, d + 1))
    return None
river_feats = []
for fn, maxrank in (('ne_10m_rivers_lake_centerlines', 9), ('ne_10m_rivers_europe', 12)):
    for f in json.load(open(f'{DATA}/{fn}.geojson'))['features']:
        p = f['properties']; nm = p.get('name') or ''
        if 'Canal' in nm or 'canal' in nm: continue   # lake centerlines stay: the reservoirs on the Tagus and the Guadiana came after the war
        if (p.get('scalerank') or 99) > maxrank or f['geometry'] is None: continue
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
for nm in sorted(river_edges):
    edges = river_edges[nm]; good = []
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
for y in range(H):   # flood plains on dry river banks (the lower Ebro, the Segura, the Guadalquivir below Seville)
    for x in range(W):
        if is_land[y, x] and terrain[y, x] == DESERT and elev[y, x] == 0 and has_river(x, y) and rnd(x, y, 'flood') < 0.7: feature[y, x] = FLOOD

# ============================================================== resources
def find_tile(lon, lat, pred, radius=2):
    h0 = hex_ll(lon, lat)
    if h0 is None: return None
    px, py = proj(lon, lat); seen = {h0}; q = deque([(h0, 0)])
    while q:
        t, d = q.popleft()
        if pred(*t): return t
        if d >= radius: continue
        for nb in sorted(neighbors(*t), key=lambda n: ((center(*n)[0] - px) ** 2 + (center(*n)[1] - py) ** 2, n)):
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
    if res in ('IRON', 'COAL', 'GOLD', 'SILVER', 'GEMS', 'COPPER') and elev[t[1], t[0]] == 0 and rnd(*t, 'hill') < 0.6: elev[t[1], t[0]] = 1
    if res in ('WHEAT', 'HORSE', 'COW', 'COTTON', 'CITRUS', 'WINE') and feature[t[1], t[0]] in (FOREST, MARSH): feature[t[1], t[0]] = NONE
HAND_RES = [
    # coal: the Asturian basins (Mieres, Langreo), the Bierzo and Laciana, Puertollano, Penarroya-Belmez, the Utrillas and Mequinenza lignites, Berga
    ('COAL', -5.77, 43.25, 6), ('COAL', -5.68, 43.30, 4), ('COAL', -6.55, 42.62, 4), ('COAL', -6.30, 42.94, 2), ('COAL', -4.10, 38.69, 4), ('COAL', -5.27, 38.28, 4),
    ('COAL', -0.85, 40.81, 2), ('COAL', 0.30, 41.37, 2), ('COAL', 1.85, 42.10, 2),
    # iron: Somorrostro in Biscay, Ojos Negros, the Rif mines at Uixan behind Melilla, Alquife, Cartagena
    ('IRON', -3.10, 43.32, 6), ('IRON', -2.95, 43.25, 2), ('IRON', -1.50, 40.73, 4), ('IRON', -3.05, 35.15, 4), ('IRON', -3.12, 37.18, 2), ('IRON', -0.88, 37.62, 2), ('IRON', -6.65, 42.50, 2),
    # horses: Jerez, the Guadalquivir valley, Extremadura, Salamanca, Navarre, the Rif
    ('HORSE', -6.05, 36.72, 4), ('HORSE', -5.70, 37.30, 2), ('HORSE', -4.95, 37.80, 2), ('HORSE', -6.30, 39.30, 2), ('HORSE', -5.90, 40.80, 2), ('HORSE', -1.70, 42.60, 2), ('HORSE', -5.40, 35.20, 2),
    # copper and pyrite (Riotinto, Tharsis), lead and silver (Linares, La Carolina, Cartagena - La Union, Mazarron), mercury at Almaden as silver
    ('COPPER', -6.59, 37.69, 1), ('COPPER', -7.12, 37.60, 1), ('SILVER', -3.64, 38.10, 1), ('SILVER', -3.62, 38.28, 1), ('SILVER', -0.83, 37.60, 1), ('SILVER', -1.31, 37.60, 1), ('SILVER', -4.84, 38.77, 1),
    # salt: Torrevieja, the Cadiz pans, the salt mountain of Cardona, Ibiza; marble from Macael and Estremoz; granite of the Guadarrama
    ('SALT', -0.70, 37.97, 1), ('SALT', -6.19, 36.48, 1), ('SALT', 1.68, 41.91, 1), ('SALT', 1.38, 38.84, 1), ('MARBLE', -2.30, 37.33, 1), ('MARBLE', -7.59, 38.84, 1),
    ('STONE', -3.95, 40.65, 1), ('STONE', -8.20, 42.10, 1), ('STONE', 2.20, 41.90, 1),
    # wine: Rioja, Jerez, Valdepenas, the Penedes, the Priorat, Ribeiro, the Douro, Jumilla, Montilla, Utiel-Requena, Toro, Navarre, Malaga
    ('WINE', -2.70, 42.50, 1), ('WINE', -6.15, 36.75, 1), ('WINE', -3.38, 38.76, 1), ('WINE', 1.70, 41.35, 1), ('WINE', 0.80, 41.18, 1), ('WINE', -8.15, 42.30, 1),
    ('WINE', -7.60, 41.15, 1), ('WINE', -1.33, 38.47, 1), ('WINE', -4.64, 37.59, 1), ('WINE', -1.20, 39.50, 1), ('WINE', -5.40, 41.52, 1), ('WINE', -1.67, 42.30, 1), ('WINE', -4.30, 36.80, 1),
    # oranges of Valencia, Castellon and Murcia; silk of Valencia and Murcia; saffron of La Mancha and the Jiloca; cane and beet sugar of Motril and the Vega
    ('CITRUS', -0.40, 39.40, 1), ('CITRUS', -0.25, 39.95, 1), ('CITRUS', -1.10, 38.00, 1), ('CITRUS', -0.20, 39.00, 1), ('CITRUS', -5.90, 37.40, 1), ('CITRUS', -0.70, 38.25, 1),
    ('SILK', -0.60, 39.25, 1), ('SILK', -1.20, 38.10, 1), ('SPICES', -3.00, 39.40, 1), ('SPICES', -2.60, 39.10, 1), ('SPICES', -1.25, 40.95, 1),
    ('SUGAR', -3.52, 36.75, 1), ('SUGAR', -3.70, 37.15, 1), ('SUGAR', -4.10, 36.75, 1), ('SUGAR', -4.85, 41.65, 1),
    ('TRUFFLES', -2.60, 41.70, 1), ('TRUFFLES', -1.00, 40.30, 1), ('TRUFFLES', 1.40, 41.95, 1), ('DYE', -6.90, 39.30, 1), ('DYE', -6.80, 38.20, 1),   # cork of the dehesas as dye
    # sea: the Galician rias, the Cantabrian coast, the Strait, the Mediterranean, the Balearics
    ('FISH', -8.75, 42.40, 1), ('FISH', -8.95, 42.90, 1), ('FISH', -8.40, 43.45, 1), ('FISH', -6.00, 43.62, 1), ('FISH', -3.50, 43.52, 1), ('FISH', -2.40, 43.45, 1),
    ('FISH', -6.40, 36.50, 1), ('FISH', -7.00, 37.10, 1), ('FISH', -4.50, 36.60, 1), ('FISH', -0.20, 39.40, 1), ('FISH', 2.30, 41.30, 1), ('FISH', 2.60, 39.40, 1),
    ('FISH', -3.90, 35.30, 1), ('FISH', -8.00, 36.95, 1), ('FISH', -9.30, 38.60, 1), ('FISH', -1.65, 43.55, 1), ('FISH', 3.30, 42.30, 1), ('FISH', -1.80, 36.80, 1),
    ('CRAB', -8.85, 42.60, 1), ('CRAB', -8.60, 42.25, 1), ('WHALE', -5.70, 35.98, 1), ('WHALE', -9.40, 43.10, 1),
]
for res, lo, la, amt in HAND_RES: place_res(res, lo, la, amt, water=res in ('FISH', 'CRAB', 'PEARLS', 'WHALE'))
for y in range(H):
    for x in range(W):
        if resource[y, x] != NONE: continue
        r = rnd(x, y, 'scatter'); lo, la = lonlat(x, y)
        if is_land[y, x]:
            if elev[y, x] == 2 or terrain[y, x] == SNOW: continue
            t, f = terrain[y, x], feature[y, x]
            meseta = t in (GRASS, PLAINS) and 38.5 < la < 42.5 and -7.0 < lo < -1.5
            if f == FOREST and r < 0.06: resource[y, x] = RID['DEER']; resamt[y, x] = 1
            elif f == NONE and meseta and elev[y, x] == 0 and r < 0.09: resource[y, x] = RID['WHEAT']; resamt[y, x] = 1
            elif f == NONE and t in (GRASS, PLAINS) and elev[y, x] == 0 and r < 0.045: resource[y, x] = RID['WHEAT']; resamt[y, x] = 1
            elif f == NONE and t == GRASS and r < 0.09: resource[y, x] = RID['COW']; resamt[y, x] = 1
            elif f == NONE and elev[y, x] == 1 and t != DESERT and r < 0.10: resource[y, x] = RID['SHEEP']; resamt[y, x] = 1
            elif f == NONE and t in (DESERT, PLAINS) and 0.90 < r < 0.935: resource[y, x] = RID['SHEEP']; resamt[y, x] = 1
            elif f in (NONE, FOREST) and 0.95 < r < 0.958: resource[y, x] = RID['STONE']; resamt[y, x] = 1
        elif terrain[y, x] == COAST:
            nl = sum(is_land[b, a] for a, b in neighbors(x, y))
            if (nl > 0 and r < 0.05) or (nl == 0 and r < 0.015): resource[y, x] = RID['FISH']; resamt[y, x] = 1

# ============================================================== players / ownership
owner = np.full((H, W), NONE, np.uint8)
for y in range(H):
    for x in range(W):
        if not is_land[y, x] or fact[y, x] == 0: continue
        owner[y, x] = fact[y, x] - 1 if fact[y, x] < 100 else 32 + fact[y, x] - 100

# ============================================================== cities
# (name, lon, lat, owner, population in thousands at the 1930 census, rounded; tags: cap base port)
CITIES = [
    # --- the Republic: Madrid, New Castile, the Levante, eastern Andalusia, Extremadura's south, Asturias, Santander, Menorca
    ('Madrid', -3.70, 40.42, REP, 953, 'cap base'), ('Alcala de Henares', -3.36, 40.48, REP, 12, ''), ('Aranjuez', -3.60, 40.03, REP, 15, ''), ('Talavera', -4.83, 39.96, REP, 16, ''),
    ('Guadalajara', -3.17, 40.63, REP, 15, ''), ('Siguenza', -2.64, 41.07, REP, 5, ''), ('Cuenca', -2.13, 40.07, REP, 17, ''), ('Tarancon', -3.01, 40.01, REP, 7, ''),
    ('Ciudad Real', -3.93, 38.99, REP, 22, ''), ('Puertollano', -4.11, 38.69, REP, 22, ''), ('Almaden', -4.84, 38.77, REP, 9, ''), ('Valdepenas', -3.38, 38.76, REP, 27, ''),
    ('Alcazar de San Juan', -3.21, 39.39, REP, 18, ''), ('Albacete', -1.86, 38.99, REP, 42, 'base'), ('Hellin', -1.70, 38.51, REP, 16, ''), ('Almansa', -1.10, 38.87, REP, 13, ''),
    ('Valencia', -0.38, 39.47, REP, 320, 'base port'), ('Sagunto', -0.27, 39.68, REP, 14, 'port'), ('Requena', -1.10, 39.49, REP, 15, ''), ('Jativa', -0.52, 38.99, REP, 15, ''),
    ('Gandia', -0.18, 38.97, REP, 15, 'port'), ('Alcoy', -0.47, 38.70, REP, 38, ''), ('Alicante', -0.48, 38.35, REP, 73, 'port'), ('Elche', -0.70, 38.27, REP, 37, ''),
    ('Orihuela', -0.94, 38.08, REP, 32, ''), ('Villena', -0.86, 38.63, REP, 14, ''), ('Castellon', -0.04, 39.99, REP, 40, 'port'), ('Vinaroz', 0.47, 40.47, REP, 9, 'port'),
    ('Segorbe', -0.49, 39.85, REP, 7, ''), ('Murcia', -1.13, 37.99, REP, 159, ''), ('Cartagena', -0.98, 37.60, REP, 102, 'base port'), ('Lorca', -1.70, 37.68, REP, 66, ''),
    ('Caravaca', -1.86, 38.10, REP, 22, ''), ('Almeria', -2.46, 36.84, REP, 54, 'port'), ('Baza', -2.77, 37.49, REP, 18, ''), ('Guadix', -3.14, 37.30, REP, 18, ''),
    ('Motril', -3.52, 36.75, REP, 20, 'port'), ('Jaen', -3.79, 37.78, REP, 40, ''), ('Linares', -3.64, 38.10, REP, 42, ''), ('Ubeda', -3.37, 38.01, REP, 25, ''),
    ('Andujar', -4.05, 38.04, REP, 22, ''), ('Malaga', -4.42, 36.72, REP, 188, 'port'), ('Antequera', -4.56, 37.02, REP, 32, ''), ('Ronda', -5.17, 36.74, REP, 30, ''),
    ('Velez-Malaga', -4.10, 36.78, REP, 25, ''), ('Marbella', -4.88, 36.51, REP, 9, 'port'), ('Huelva', -6.95, 37.26, REP, 45, 'port'), ('Riotinto', -6.59, 37.69, REP, 10, ''),
    ('Ayamonte', -7.40, 37.21, REP, 10, 'port'), ('Badajoz', -6.97, 38.88, REP, 44, ''), ('Merida', -6.34, 38.92, REP, 19, ''), ('Don Benito', -5.86, 38.96, REP, 20, ''),
    ('Zafra', -6.42, 38.42, REP, 10, ''), ('Llerena', -6.02, 38.24, REP, 8, ''), ('Jerez de los Caballeros', -6.77, 38.32, REP, 13, ''), ('Almendralejo', -6.41, 38.68, REP, 18, ''),
    ('Castuera', -5.54, 38.72, REP, 10, ''), ('Pozoblanco', -4.85, 38.38, REP, 17, ''), ('Penarroya', -5.27, 38.30, REP, 25, ''), ('Montoro', -4.38, 38.02, REP, 16, ''),
    ('Baena', -4.32, 37.62, REP, 22, ''), ('Gijon', -5.66, 43.54, REP, 78, 'base port'), ('Aviles', -5.92, 43.56, REP, 20, 'port'), ('Mieres', -5.77, 43.25, REP, 40, ''),
    ('Sama de Langreo', -5.68, 43.30, REP, 41, ''), ('Luarca', -6.54, 43.54, REP, 18, 'port'), ('Llanes', -4.75, 43.42, REP, 10, 'port'), ('Cangas de Onis', -5.13, 43.35, REP, 9, ''),
    ('Santander', -3.80, 43.46, REP, 85, 'base port'), ('Torrelavega', -4.05, 43.35, REP, 20, ''), ('Reinosa', -4.14, 43.00, REP, 8, ''), ('Laredo', -3.42, 43.41, REP, 5, 'port'),
    ('Castro Urdiales', -3.22, 43.38, REP, 13, 'port'), ('Mahon', 4.27, 39.89, REP, 18, 'base port'), ('Ciudadela', 3.84, 40.00, REP, 10, 'port'), ('Ocana', -3.50, 39.96, REP, 7, ''),
    ('Villarrobledo', -2.60, 39.27, REP, 15, ''), ('Cieza', -1.42, 38.24, REP, 15, ''), ('Denia', 0.11, 38.84, REP, 12, 'port'), ('Utiel', -1.20, 39.57, REP, 10, ''),
    # --- the Nationalists of the South: Seville, Cadiz, Cordoba, the Granada pocket, the Alcazar of Toledo, Morocco, Mallorca and Ibiza
    ('Seville', -5.98, 37.39, NAT, 229, 'cap base'), ('Cadiz', -6.29, 36.53, NAT, 76, 'base port'), ('Jerez', -6.14, 36.69, NAT, 72, ''), ('San Fernando', -6.20, 36.46, NAT, 30, 'port'),
    ('Algeciras', -5.45, 36.13, NAT, 21, 'base port'), ('Sanlucar', -6.35, 36.78, NAT, 28, 'port'), ('Ecija', -5.08, 37.54, NAT, 34, ''), ('Carmona', -5.64, 37.47, NAT, 23, ''),
    ('Osuna', -5.10, 37.24, NAT, 18, ''), ('Utrera', -5.78, 37.18, NAT, 26, ''), ('Moron', -5.45, 37.12, NAT, 18, ''), ('Cordoba', -4.78, 37.88, NAT, 103, 'base'),
    ('Lucena', -4.49, 37.41, NAT, 29, ''), ('Cabra', -4.44, 37.47, NAT, 18, ''), ('Puente Genil', -4.77, 37.39, NAT, 25, ''), ('Granada', -3.60, 37.18, NAT, 118, 'base'),
    ('Toledo', -4.02, 39.86, NAT, 27, ''), ('Palma', 2.65, 39.57, NAT, 88, 'base port'), ('Manacor', 3.21, 39.57, NAT, 20, ''), ('Inca', 2.91, 39.72, NAT, 12, ''),
    ('Ibiza', 1.43, 38.91, NAT, 9, 'port'), ('Ceuta', -5.32, 35.89, NAT, 49, 'base port'), ('Tetuan', -5.37, 35.57, NAT, 49, 'base'), ('Melilla', -2.94, 35.29, NAT, 63, 'base port'),
    ('Larache', -6.16, 35.19, NAT, 30, 'port'), ('Alcazarquivir', -5.90, 35.00, NAT, 30, ''), ('Xauen', -5.27, 35.17, NAT, 9, ''), ('Villa Sanjurjo', -3.93, 35.25, NAT, 8, 'port'),
    ('Nador', -2.93, 35.17, NAT, 6, ''), ('Arcila', -6.03, 35.46, NAT, 6, 'port'), ('Medina-Sidonia', -5.93, 36.46, NAT, 12, ''), ('Arcos', -5.81, 36.75, NAT, 14, ''),
    # --- the Army of the North: Old Castile and Leon, Galicia, Navarre, Alava, the Rioja, Caceres, western Aragon, the Oviedo pocket
    ('Burgos', -3.70, 42.34, NORTH, 40, 'cap base'), ('Valladolid', -4.72, 41.65, NORTH, 91, 'base'), ('Pamplona', -1.64, 42.81, NORTH, 42, 'base'), ('Vitoria', -2.67, 42.85, NORTH, 41, 'base'),
    ('Logrono', -2.45, 42.47, NORTH, 37, ''), ('Zaragoza', -0.88, 41.65, NORTH, 174, 'base'), ('Huesca', -0.41, 42.14, NORTH, 15, ''), ('Jaca', -0.55, 42.57, NORTH, 7, ''),
    ('Teruel', -1.11, 40.34, NORTH, 13, ''), ('Calatayud', -1.64, 41.35, NORTH, 14, ''), ('Tarazona', -1.73, 41.90, NORTH, 9, ''), ('Tudela', -1.61, 42.06, NORTH, 11, ''),
    ('Estella', -2.03, 42.67, NORTH, 6, ''), ('Miranda de Ebro', -2.95, 42.69, NORTH, 9, ''), ('Aranda de Duero', -3.69, 41.67, NORTH, 8, ''), ('Soria', -2.47, 41.76, NORTH, 10, ''),
    ('Segovia', -4.12, 40.95, NORTH, 17, ''), ('Avila', -4.70, 40.66, NORTH, 15, ''), ('Salamanca', -5.66, 40.97, NORTH, 47, ''), ('Bejar', -5.76, 40.39, NORTH, 14, ''),
    ('Ciudad Rodrigo', -6.53, 40.60, NORTH, 10, ''), ('Zamora', -5.75, 41.50, NORTH, 22, ''), ('Benavente', -5.68, 42.00, NORTH, 6, ''), ('Leon', -5.57, 42.60, NORTH, 29, ''),
    ('Astorga', -6.06, 42.46, NORTH, 7, ''), ('Ponferrada', -6.60, 42.55, NORTH, 7, ''), ('Palencia', -4.53, 42.01, NORTH, 27, ''), ('Medina del Campo', -4.91, 41.31, NORTH, 13, ''),
    ('Caceres', -6.37, 39.48, NORTH, 26, ''), ('Plasencia', -6.09, 40.03, NORTH, 13, ''), ('Trujillo', -5.88, 39.46, NORTH, 13, ''), ('Navalmoral', -5.54, 39.89, NORTH, 7, ''),
    ('Coria', -6.54, 39.99, NORTH, 6, ''), ('La Coruna', -8.41, 43.36, NORTH, 74, 'base port'), ('El Ferrol', -8.23, 43.48, NORTH, 34, 'base port'), ('Santiago', -8.54, 42.88, NORTH, 41, ''),
    ('Lugo', -7.56, 43.01, NORTH, 30, ''), ('Monforte', -7.51, 42.52, NORTH, 11, ''), ('Orense', -7.86, 42.34, NORTH, 22, ''), ('Pontevedra', -8.64, 42.43, NORTH, 30, 'port'),
    ('Vigo', -8.72, 42.24, NORTH, 65, 'port'), ('Villagarcia', -8.77, 42.60, NORTH, 10, 'port'), ('Ribadeo', -7.04, 43.54, NORTH, 8, 'port'), ('Oviedo', -5.85, 43.36, NORTH, 75, 'base'),
    ('Calamocha', -1.30, 40.92, NORTH, 4, ''), ('Daroca', -1.42, 41.11, NORTH, 4, ''), ('Ejea', -1.14, 42.13, NORTH, 9, ''), ('Belchite', -0.75, 41.31, NORTH, 4, ''),
    ('Briviesca', -3.32, 42.55, NORTH, 4, ''), ('Sepulveda', -3.75, 41.30, NORTH, 3, ''), ('Almazan', -2.53, 41.49, NORTH, 4, ''), ('Montalban', -0.80, 40.83, NORTH, 3, ''),
    # --- the Generalitat of Catalonia
    ('Barcelona', 2.17, 41.39, CAT, 1006, 'cap base port'), ('Sabadell', 2.11, 41.55, CAT, 48, ''), ('Terrassa', 2.01, 41.56, CAT, 41, ''), ('Badalona', 2.25, 41.45, CAT, 44, 'port'),
    ('Mataro', 2.44, 41.54, CAT, 27, 'port'), ('Manresa', 1.83, 41.73, CAT, 32, ''), ('Vic', 2.25, 41.93, CAT, 13, ''), ('Igualada', 1.62, 41.58, CAT, 16, ''),
    ('Vilanova', 1.73, 41.22, CAT, 18, 'port'), ('Tarragona', 1.25, 41.12, CAT, 32, 'port'), ('Reus', 1.11, 41.16, CAT, 34, ''), ('Tortosa', 0.52, 40.81, CAT, 36, ''),
    ('Lerida', 0.62, 41.62, CAT, 39, 'base'), ('Cervera', 1.27, 41.67, CAT, 5, ''), ('Balaguer', 0.81, 41.79, CAT, 6, ''), ('Seo de Urgel', 1.46, 42.36, CAT, 4, ''),
    ('Puigcerda', 1.93, 42.43, CAT, 4, ''), ('Gerona', 2.82, 41.98, CAT, 22, ''), ('Figueras', 2.96, 42.27, CAT, 15, ''), ('Olot', 2.49, 42.18, CAT, 13, ''),
    ('Palamos', 3.13, 41.85, CAT, 5, 'port'), ('Tremp', 0.90, 42.17, CAT, 5, ''), ('Gandesa', 0.44, 41.05, CAT, 3, ''), ('Mora de Ebro', 0.64, 41.09, CAT, 3, ''), ('Falset', 0.82, 41.15, CAT, 3, ''),
    # --- the Basque Country (Biscay, Gipuzkoa)
    ('Bilbao', -2.93, 43.26, EUZ, 162, 'cap base port'), ('Guernica', -2.68, 43.32, EUZ, 5, ''), ('Durango', -2.63, 43.17, EUZ, 10, ''), ('Bermeo', -2.72, 43.42, EUZ, 10, 'port'),
    ('Eibar', -2.47, 43.18, EUZ, 12, ''), ('San Sebastian', -1.98, 43.32, EUZ, 78, 'base port'), ('Irun', -1.79, 43.34, EUZ, 15, ''), ('Tolosa', -2.08, 43.14, EUZ, 12, ''),
    ('Mondragon', -2.49, 43.06, EUZ, 9, ''), ('Barakaldo', -2.99, 43.30, EUZ, 31, ''), ('Amurrio', -3.00, 43.05, EUZ, 4, ''),
    # --- the CNT-FAI columns and the Council of Aragon
    ('Caspe', -0.04, 41.23, CNT, 9, 'cap'), ('Alcaniz', -0.13, 41.05, CNT, 9, ''), ('Fraga', 0.35, 41.52, CNT, 7, ''), ('Barbastro', 0.13, 42.04, CNT, 8, ''),
    ('Monzon', 0.19, 41.91, CNT, 7, ''), ('Bujaraloz', -0.15, 41.50, CNT, 2, ''), ('Sarinena', -0.16, 41.79, CNT, 4, ''), ('Ainsa', 0.14, 42.42, CNT, 1, ''),
    ('Mora de Rubielos', -0.75, 40.25, CNT, 3, ''), ('Alcorisa', -0.38, 40.89, CNT, 4, ''), ('Valderrobres', 0.16, 40.88, CNT, 2, ''), ('Graus', 0.34, 42.19, CNT, 3, ''),
]
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES): CITIES.append((name, lo, la, 32 + i, popk, 'cap'))
for name, lo, la, key, popk in CS_TOWNS: CITIES.append((name, lo, la, 32 + CSIDX[key], popk, ''))
# Thin the city list: at ~11 km per hex the towns of the Meseta stand two or three hexes apart. The rule, with no exceptions:
# no two cities closer than 3 hexes; two cities of one side at least 4 apart unless both are key towns (capitals or KEEP), then 3.
# Towns are taken in order of importance (side capitals, city-state capitals, KEEP towns, IMPORTANT towns, the rest, each by
# population, PRIORITY first within a tier); a town that breaks the rule joins the nearest kept city of its owner (population added), or is dropped if none is near.
MIN_SPACING = 4          # between cities of the same side
MIN_SPACING_KEY = 3      # between two key towns (capitals, KEEP) of the same side
MIN_SPACING_FRONT = 3    # between cities of different sides, and the hard floor for any two cities
# every city the events name, plus the towns the history turns on
KEEP = {'Madrid', 'Seville', 'Burgos', 'Barcelona', 'Bilbao', 'Caspe', 'Toledo', 'Oviedo', 'Granada', 'Cordoba', 'Cadiz', 'Algeciras', 'Ceuta', 'Tetuan', 'Melilla', 'Palma',
        'Valencia', 'Cartagena', 'Albacete', 'Guadalajara', 'Siguenza', 'Teruel', 'Zaragoza', 'Huesca', 'Pamplona', 'Vitoria', 'Valladolid', 'Salamanca', 'Caceres', 'Badajoz',
        'Malaga', 'Gijon', 'Santander', 'Leon', 'Guernica', 'San Sebastian', 'Irun', 'Lerida', 'Tortosa', 'Gerona', 'Alcaniz', 'Fraga', 'Barbastro', 'Mahon', 'Alicante',
        'El Ferrol', 'La Coruna', 'Gandesa', 'Belchite', 'Almeria', 'Jaen', 'Huelva', 'Merida', 'Talavera', 'Calamocha', 'Ciudad Real', 'Cuenca', 'Murcia', 'Tarragona', 'Castellon',
        'Logrono', 'Soria', 'Segovia', 'Avila', 'Zamora', 'Palencia', 'Lugo', 'Orense', 'Vigo', 'Santiago', 'Pontevedra', 'Ibiza', 'Larache'}
IMPORTANT = ['Jerez', 'Lorca', 'Alcoy', 'Elche', 'Linares', 'Ubeda', 'Antequera', 'Ronda', 'Puertollano', 'Valdepenas', 'Sagunto', 'Requena', 'Hellin', 'Aranjuez', 'Alcala de Henares',
             'Mieres', 'Aviles', 'Torrelavega', 'Reinosa', 'Eibar', 'Durango', 'Tolosa', 'Manresa', 'Reus', 'Figueras', 'Vic', 'Puigcerda', 'Monzon', 'Plasencia', 'Trujillo', 'Calatayud',
             'Tudela', 'Jaca', 'Miranda de Ebro', 'Aranda de Duero', 'Medina del Campo', 'Astorga', 'Ponferrada', 'Ecija', 'Lucena', 'Pozoblanco', 'Penarroya', 'Don Benito', 'Zafra',
             'Baza', 'Guadix', 'Motril', 'Vinaroz', 'Alcazarquivir', 'Xauen', 'Villa Sanjurjo', 'Seo de Urgel', 'Sarinena', 'Mora de Rubielos', 'Daroca', 'Ejea', 'Montalban']
IMP_RANK = {n: i for i, n in enumerate(IMPORTANT)}
approx = {c[0]: hex_ll(c[1], c[2]) for c in CITIES}
def tier(c): return (0 if c[3] < 32 else 1) if 'cap' in c[5] else 2 if c[0] in KEEP else 3 if c[0] in IMP_RANK else 4
def is_key(c): return tier(c) <= 2
def spacing(a, b):
    """Minimum hex distance between two cities (records of CITIES) under the rule."""
    if a[3] != b[3]: return MIN_SPACING_FRONT
    return MIN_SPACING_KEY if is_key(a) and is_key(b) else MIN_SPACING
def spacing_thin(a, b): return spacing(a, b) + (1 if a[3] == b[3] and tier(a) == 4 else 0)   # minor towns keep an extra hex of air
# within its tier a town of PRIORITY goes before the bigger ones: on a conflict the town that mattered in 1936-39 stays, not today's
PRIORITY = {'El Ferrol'}   # the navy's base of the north, its mutiny of July 1936, the yard that completed the Canarias and Baleares; La Coruna merges into it
order = sorted(range(len(CITIES)), key=lambda i: (tier(CITIES[i]), CITIES[i][0] not in PRIORITY, -CITIES[i][4], CITIES[i][0]))
kept = []; dropped = []; ABSORBED = {}
land_id = {}   # connected land masses: a town merges into a city on its own shore if there is one (Algeciras not into Ceuta)
for y0 in range(H):
    for x0 in range(W):
        if not is_land[y0, x0] or (x0, y0) in land_id: continue
        land_id[(x0, y0)] = (x0, y0); q = deque([(x0, y0)])
        while q:
            for nb in neighbors(*q.popleft()):
                if is_land[nb[1], nb[0]] and nb not in land_id: land_id[nb] = (x0, y0); q.append(nb)
def land_of(i):
    t = find_tile(CITIES[i][1], CITIES[i][2], lambda x, y: is_land[y, x], 2); return land_id.get(t)
def absorb(i, h, pool, final=False):
    """Merge town i into the nearest city of its owner among pool {index: hex} within 8 hexes, on its own land mass if one is there.
    While thinning, a town with no such city on its shore waits for the final plots (Algeciras then joins a town of the Campo, not Ceuta)."""
    name, pl = CITIES[i][0], CITIES[i][3]
    same = [j for j in pool if CITIES[j][3] == pl and hexdist(h, pool[j]) <= 8]
    shore = [j for j in same if land_of(j) == land_of(i)]
    if not shore and not final: dropped.append(i); return
    same = shore or same
    if not same: ABSORBED[name] = None; return   # dropped: no city of its side nearby
    ABSORBED[name] = CITIES[min(same, key=lambda j: (hexdist(h, pool[j]), j))][0]
for i in order:
    h = approx[CITIES[i][0]]
    if h is None: continue
    if all(hexdist(h, approx[CITIES[j][0]]) >= spacing_thin(CITIES[i], CITIES[j]) for j in kept): kept.append(i); continue
    absorb(i, h, {j: approx[CITIES[j][0]] for j in kept})
# Place the kept cities in the same order, each on the nearest fitting hex to its real position (radius 1, then 2, then 3 with any
# terrain); the rule is checked against the cities already placed, so it holds on the final plots. A city that finds no hex merges;
# such towns join the nearest placed city of their owner.
city_tile_of = {}
def friendly(o, pl): return o == NONE or o == pl
for i in kept:
    name, lo, la, pl, popk, tags = CITIES[i]
    def spaced(x, y, i=i): return all(hexdist((x, y), t) >= spacing(CITIES[i], CITIES[j]) for j, t in city_tile_of.items())
    def ok(x, y): return is_land[y, x] and elev[y, x] != 2 and terrain[y, x] != SNOW and spaced(x, y)
    t = find_tile(lo, la, lambda x, y, pl=pl: ok(x, y) and friendly(owner[y, x], pl), 1)
    if t is None: t = find_tile(lo, la, ok, 2)
    if t is None:
        t = find_tile(lo, la, lambda x, y: is_land[y, x] and spaced(x, y), 3)
        if t is not None: elev[t[1], t[0]] = min(int(elev[t[1], t[0]]), 1); terrain[t[1], t[0]] = PLAINS if terrain[t[1], t[0]] == SNOW else terrain[t[1], t[0]]
        print('  !! relaxed placement for', name, t)
    if t is None: dropped.append(i); print('  !! no room for', name); continue
    city_tile_of[i] = t
    owner[t[1], t[0]] = pl; feature[t[1], t[0]] = NONE; wonder[t[1], t[0]] = NONE
    if resource[t[1], t[0]] != NONE and RESOURCES[resource[t[1], t[0]]].split('_', 1)[1] in ('FISH', 'WHALE', 'CRAB'): resource[t[1], t[0]] = NONE
    for nb in neighbors(*t):
        if is_land[nb[1], nb[0]] and nb not in city_tile_of.values() and (owner[nb[1], nb[0]] == NONE or 'cap' in tags or name in ('Toledo', 'Oviedo', 'Granada')): owner[nb[1], nb[0]] = pl
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
      ', '.join(f'{n} -> {ABSORBED[n]}' for n in dropped_key), '; biggest merges:', ', '.join(f'{k} +{v}k' for k, v in extra.most_common(6)))
# the spacing rule on the final plots, no exceptions
gaps = [(hexdist(city_tiles[a], city_tiles[b]), spacing(CITIES[a], CITIES[b]), CITIES[a][3] == CITIES[b][3], CITIES[a][0], CITIES[b][0])
        for a in range(len(CITIES)) for b in range(a + 1, len(CITIES))]
bad = [g for g in gaps if g[0] < g[1]]
assert not bad, f'cities too close: {bad}'
print(f'  city spacing (at least {MIN_SPACING_FRONT} between any two, {MIN_SPACING} within a side unless both are key towns): min {min(g[0] for g in gaps)} hexes overall,',
      f'{min(g[0] for g in gaps if g[2])} within a side, {min(g[0] for g in gaps if g[1] == MIN_SPACING)} between towns of a side that are not both key')
# land farther than 5 hexes from one of its owner's cities (6 for a city-state) is nobody's: the sierras between the towns breed fugitives
near = {}
for ci, t in enumerate(city_tiles): near.setdefault(CITIES[ci][3], []).append(t)
for y in range(H):
    for x in range(W):
        o = owner[y, x]
        if o == NONE or (x, y) in city_at: continue
        lim = 6 if o >= 32 else 5
        if min((hexdist((x, y), t) for t in near.get(int(o), [])), default=99) > lim: owner[y, x] = NONE
# coastal water: nearest land owner within 2 hexes
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
        if cnt: owner[y, x] = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
def civ_pop(popk): return int(max(3, min(24, round(4.2 * math.log(popk * 1000) - 40))))

BUILDINGS = ['BUILDING_PALACE', 'BUILDING_MONUMENT', 'BUILDING_GRANARY', 'BUILDING_LIBRARY', 'BUILDING_MARKET', 'BUILDING_BARRACKS', 'BUILDING_WALLS',
             'BUILDING_AQUEDUCT', 'BUILDING_WORKSHOP', 'BUILDING_AMPHITHEATER', 'BUILDING_UNIVERSITY', 'BUILDING_BANK', 'BUILDING_PUBLIC_SCHOOL',
             'BUILDING_HOSPITAL', 'BUILDING_FACTORY', 'BUILDING_CONSTABLE', 'BUILDING_OPERA_HOUSE', 'BUILDING_MUSEUM', 'BUILDING_STOCK_EXCHANGE',
             'BUILDING_ARMORY', 'BUILDING_CASTLE', 'BUILDING_MILITARY_ACADEMY', 'BUILDING_ARSENAL', 'BUILDING_LIGHTHOUSE', 'BUILDING_HARBOR', 'BUILDING_SEAPORT',
             'BUILDING_COURTHOUSE', 'BUILDING_CARAVANSARY', 'BUILDING_FORGE', 'BUILDING_STABLE', 'BUILDING_WINDMILL', 'BUILDING_GARDEN', 'BUILDING_MINT']
BID = {b: i for i, b in enumerate(BUILDINGS)}
def city_buildings(ci):
    """Lean 1936 building set: gold and defence everywhere, upkeep-heavy buildings only in the big cities."""
    name, lo, la, pl, popk, tags = CITIES[ci]; pop = civ_pop(popk); t = city_tiles[ci]; tags = tags.split()
    b = ['BUILDING_MONUMENT', 'BUILDING_GRANARY', 'BUILDING_MARKET', 'BUILDING_WALLS']
    if pop >= 5: b += ['BUILDING_LIBRARY']
    if pop >= 8: b += ['BUILDING_BANK', 'BUILDING_CASTLE', 'BUILDING_WORKSHOP']
    if pop >= 11: b += ['BUILDING_UNIVERSITY', 'BUILDING_BARRACKS', 'BUILDING_FORGE', 'BUILDING_AQUEDUCT']
    if pop >= 14: b += ['BUILDING_STOCK_EXCHANGE', 'BUILDING_ARMORY', 'BUILDING_ARSENAL', 'BUILDING_AMPHITHEATER', 'BUILDING_WINDMILL']
    if pop >= 17: b += ['BUILDING_FACTORY', 'BUILDING_PUBLIC_SCHOOL', 'BUILDING_HOSPITAL', 'BUILDING_OPERA_HOUSE', 'BUILDING_MUSEUM']
    if 'cap' in tags: b += ['BUILDING_PALACE']
    if 'cap' in tags and pl < 32: b += ['BUILDING_CONSTABLE', 'BUILDING_MILITARY_ACADEMY', 'BUILDING_BARRACKS', 'BUILDING_ARSENAL']
    if 'base' in tags: b += ['BUILDING_BARRACKS', 'BUILDING_ARMORY', 'BUILDING_STABLE']
    if any(not is_land[nb[1], nb[0]] for nb in neighbors(*t)): b += ['BUILDING_HARBOR'] + (['BUILDING_LIGHTHOUSE'] if pop >= 8 else [])
    if pl >= 32: b = ['BUILDING_MONUMENT', 'BUILDING_WALLS', 'BUILDING_GRANARY', 'BUILDING_MARKET'] + (['BUILDING_PALACE'] if 'cap' in tags else []) + (['BUILDING_CASTLE', 'BUILDING_BARRACKS'] if pop >= 10 else [])
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
    for y in range(max(0, cy - rad - 1), min(H, cy + rad + 2)):
        for x in range(max(0, cx - rad - 1), min(W, cx + rad + 2)):
            if hexdist((x, y), (cx, cy)) > rad or (x, y) in city_at or improvement[y, x] != NONE: continue
            if owner[y, x] != pl: continue
            res = RESOURCES[resource[y, x]].split('_', 1)[1] if resource[y, x] != NONE else None
            if not is_land[y, x]:
                if res in RES_IMP: improvement[y, x] = IID['FISHING_BOATS']
                continue
            if elev[y, x] == 2 or terrain[y, x] == SNOW: continue
            if res == 'OIL': improvement[y, x] = IID['WELL']; continue
            if res in RES_IMP:
                if feature[y, x] in (FOREST, MARSH) and RES_IMP[res] in ('FARM', 'PASTURE', 'PLANTATION'): feature[y, x] = NONE
                improvement[y, x] = IID[RES_IMP[res]]; continue
            r = rnd(x, y, 'imp'); dense = 0.75 if civ_pop(popk) >= 12 else 0.5
            if feature[y, x] == FOREST:
                if r < 0.30 * dense: improvement[y, x] = IID['LUMBERMILL']
            elif feature[y, x] in (MARSH, FLOOD) and feature[y, x] == MARSH: pass
            elif elev[y, x] == 1:
                if r < 0.30 * dense: improvement[y, x] = IID['MINE']
            elif terrain[y, x] in (GRASS, PLAINS) or feature[y, x] == FLOOD:
                if r < dense * (0.9 if has_river(x, y) else 0.7): improvement[y, x] = IID['FARM']
                elif r < dense * 0.8: improvement[y, x] = IID['TRADING_POST']

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
# The railway network of 1936, line by line (both ends must be cities above; a town merged away hands its line to the city that absorbed it).
RAIL = [
    # Norte: Madrid - Avila - Medina - Valladolid - Venta de Banos - Burgos - Miranda - Vitoria - Alsasua - San Sebastian - Irun - Hendaye
    ('Madrid', 'Avila'), ('Avila', 'Medina del Campo'), ('Medina del Campo', 'Valladolid'), ('Valladolid', 'Palencia'), ('Palencia', 'Burgos'), ('Burgos', 'Briviesca'), ('Briviesca', 'Miranda de Ebro'),
    ('Miranda de Ebro', 'Vitoria'), ('Vitoria', 'Mondragon'), ('Mondragon', 'Tolosa'), ('Tolosa', 'San Sebastian'), ('San Sebastian', 'Irun'), ('Irun', 'Bayonne'), ('Madrid', 'Segovia'), ('Segovia', 'Medina del Campo'),
    ('Palencia', 'Leon'), ('Leon', 'Oviedo'), ('Oviedo', 'Gijon'), ('Oviedo', 'Aviles'), ('Oviedo', 'Mieres'), ('Mieres', 'Sama de Langreo'), ('Sama de Langreo', 'Gijon'), ('Palencia', 'Reinosa'), ('Reinosa', 'Torrelavega'), ('Torrelavega', 'Santander'),
    ('Leon', 'Astorga'), ('Astorga', 'Ponferrada'), ('Ponferrada', 'Monforte'), ('Monforte', 'Orense'), ('Orense', 'Vigo'), ('Monforte', 'Lugo'), ('Lugo', 'El Ferrol'),
    ('El Ferrol', 'Santiago'), ('Santiago', 'Villagarcia'), ('Villagarcia', 'Pontevedra'), ('Pontevedra', 'Vigo'), ('Vigo', 'Oporto'), ('Medina del Campo', 'Salamanca'), ('Salamanca', 'Ciudad Rodrigo'), ('Ciudad Rodrigo', 'Guarda'),
    ('Medina del Campo', 'Zamora'), ('Zamora', 'Benavente'), ('Benavente', 'Astorga'), ('Salamanca', 'Bejar'), ('Bejar', 'Plasencia'), ('Plasencia', 'Caceres'), ('Caceres', 'Merida'),
    ('Miranda de Ebro', 'Bilbao'), ('Bilbao', 'Barakaldo'), ('Bilbao', 'Durango'), ('Durango', 'Eibar'), ('Eibar', 'San Sebastian'), ('Bilbao', 'Guernica'), ('Guernica', 'Bermeo'), ('Bilbao', 'Castro Urdiales'), ('Castro Urdiales', 'Laredo'), ('Laredo', 'Santander'),
    ('Miranda de Ebro', 'Logrono'), ('Logrono', 'Tudela'), ('Tudela', 'Zaragoza'), ('Tudela', 'Pamplona'), ('Pamplona', 'Vitoria'), ('Tudela', 'Tarazona'), ('Valladolid', 'Aranda de Duero'),
    ('Burgos', 'Aranda de Duero'), ('Aranda de Duero', 'Almazan'), ('Almazan', 'Soria'), ('Almazan', 'Calatayud'), ('Ejea', 'Zaragoza'), ('Pamplona', 'Estella'),
    # MZA: Madrid - Guadalajara - Siguenza - Calatayud - Zaragoza - Lerida - Barcelona; Zaragoza - Caspe - Reus; the coast line to Valencia; Huesca, Jaca, Canfranc
    ('Madrid', 'Alcala de Henares'), ('Alcala de Henares', 'Guadalajara'), ('Guadalajara', 'Siguenza'), ('Siguenza', 'Calatayud'), ('Calatayud', 'Zaragoza'), ('Zaragoza', 'Sarinena'), ('Sarinena', 'Monzon'),
    ('Monzon', 'Lerida'), ('Monzon', 'Barbastro'), ('Lerida', 'Cervera'), ('Cervera', 'Manresa'), ('Manresa', 'Terrassa'), ('Terrassa', 'Barcelona'), ('Sabadell', 'Barcelona'), ('Lerida', 'Reus'), ('Lerida', 'Balaguer'),
    ('Zaragoza', 'Belchite'), ('Belchite', 'Caspe'), ('Zaragoza', 'Caspe'), ('Caspe', 'Fraga'), ('Caspe', 'Mora de Ebro'), ('Mora de Ebro', 'Reus'), ('Reus', 'Tarragona'), ('Tarragona', 'Vilanova'), ('Vilanova', 'Barcelona'),
    ('Caspe', 'Alcaniz'), ('Alcaniz', 'Alcorisa'), ('Lerida', 'Fraga'), ('Lerida', 'Tremp'), ('Barcelona', 'Badalona'), ('Badalona', 'Mataro'), ('Mataro', 'Gerona'), ('Barcelona', 'Vic'), ('Vic', 'Puigcerda'),
    ('Gerona', 'Figueras'), ('Figueras', 'Perpignan'), ('Gerona', 'Olot'), ('Gerona', 'Palamos'), ('Manresa', 'Igualada'), ('Tarragona', 'Tortosa'), ('Tortosa', 'Vinaroz'), ('Vinaroz', 'Castellon'),
    ('Castellon', 'Sagunto'), ('Sagunto', 'Valencia'), ('Zaragoza', 'Huesca'), ('Huesca', 'Jaca'), ('Jaca', 'Pau'), ('Puigcerda', 'Toulouse'),
    ('Calatayud', 'Daroca'), ('Daroca', 'Calamocha'), ('Calamocha', 'Teruel'), ('Teruel', 'Segorbe'), ('Segorbe', 'Sagunto'), ('Teruel', 'Mora de Rubielos'),
    # MZA south: Madrid - Aranjuez - Alcazar - Albacete - Murcia - Cartagena; Alicante; Valencia; Andalusia; Toledo; Cuenca
    ('Madrid', 'Aranjuez'), ('Aranjuez', 'Toledo'), ('Aranjuez', 'Ocana'), ('Ocana', 'Alcazar de San Juan'), ('Alcazar de San Juan', 'Villarrobledo'), ('Villarrobledo', 'Albacete'),
    ('Albacete', 'Hellin'), ('Hellin', 'Cieza'), ('Cieza', 'Murcia'), ('Murcia', 'Cartagena'), ('Albacete', 'Almansa'), ('Almansa', 'Villena'), ('Villena', 'Alicante'), ('Alicante', 'Elche'), ('Elche', 'Orihuela'),
    ('Orihuela', 'Murcia'), ('Almansa', 'Jativa'), ('Jativa', 'Valencia'), ('Jativa', 'Alcoy'), ('Gandia', 'Denia'), ('Gandia', 'Valencia'), ('Valencia', 'Requena'), ('Requena', 'Utiel'),
    ('Aranjuez', 'Tarancon'), ('Tarancon', 'Cuenca'), ('Alcazar de San Juan', 'Valdepenas'), ('Valdepenas', 'Linares'), ('Linares', 'Andujar'), ('Andujar', 'Montoro'), ('Montoro', 'Cordoba'),
    ('Cordoba', 'Seville'), ('Seville', 'Utrera'), ('Utrera', 'Jerez'), ('Jerez', 'Cadiz'), ('Cadiz', 'San Fernando'), ('Jerez', 'Sanlucar'), ('Linares', 'Ubeda'), ('Linares', 'Jaen'),
    ('Cordoba', 'Puente Genil'), ('Puente Genil', 'Antequera'), ('Antequera', 'Malaga'), ('Antequera', 'Granada'), ('Antequera', 'Ronda'), ('Ronda', 'Algeciras'), ('Granada', 'Guadix'),
    ('Linares', 'Guadix'), ('Guadix', 'Almeria'), ('Guadix', 'Baza'), ('Baza', 'Lorca'), ('Lorca', 'Murcia'), ('Seville', 'Huelva'), ('Huelva', 'Riotinto'), ('Huelva', 'Ayamonte'),
    ('Madrid', 'Ciudad Real'), ('Ciudad Real', 'Puertollano'), ('Puertollano', 'Almaden'), ('Almaden', 'Castuera'), ('Castuera', 'Don Benito'), ('Don Benito', 'Merida'), ('Merida', 'Badajoz'), ('Badajoz', 'Elvas'),
    ('Merida', 'Almendralejo'), ('Almendralejo', 'Zafra'), ('Zafra', 'Llerena'), ('Llerena', 'Seville'), ('Zafra', 'Jerez de los Caballeros'), ('Penarroya', 'Cordoba'), ('Penarroya', 'Pozoblanco'), ('Penarroya', 'Castuera'),
    ('Madrid', 'Talavera'), ('Talavera', 'Navalmoral'), ('Navalmoral', 'Caceres'), ('Caceres', 'Castelo Branco'), ('Seville', 'Carmona'), ('Carmona', 'Ecija'), ('Ecija', 'Cordoba'), ('Utrera', 'Moron'), ('Moron', 'Osuna'), ('Osuna', 'Puente Genil'),
    ('Puente Genil', 'Lucena'), ('Lucena', 'Cabra'), ('Malaga', 'Velez-Malaga'),
    # Mallorca, Morocco, Portugal, France, Algeria
    ('Palma', 'Inca'), ('Inca', 'Manacor'), ('Ceuta', 'Tetuan'), ('Tangier', 'Arcila'), ('Arcila', 'Alcazarquivir'), ('Alcazarquivir', 'Larache'), ('Melilla', 'Nador'),
    ('Lisbon', 'Santarem'), ('Santarem', 'Coimbra'), ('Coimbra', 'Oporto'), ('Oporto', 'Braga'), ('Coimbra', 'Viseu'), ('Coimbra', 'Guarda'), ('Santarem', 'Elvas'), ('Lisbon', 'Evora'), ('Evora', 'Elvas'),
    ('Evora', 'Beja'), ('Beja', 'Faro'), ('Santarem', 'Castelo Branco'), ('Bayonne', 'Pau'), ('Pau', 'Tarbes'), ('Tarbes', 'Toulouse'), ('Toulouse', 'Carcassonne'), ('Carcassonne', 'Narbonne'),
    ('Narbonne', 'Perpignan'), ('Bayonne', 'Mont-de-Marsan'), ('Toulouse', 'Foix'), ('Foix', 'Puigcerda'), ('Oran', 'Sidi Bel Abbes'), ('Sidi Bel Abbes', 'Tlemcen'), ('Oran', 'Mostaganem'),
    ('Oran', 'Orleansville'), ('Orleansville', 'Blida'), ('Blida', 'Algiers'), ('Tlemcen', 'Nemours'),
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
UNITS = ['UNIT_GREAT_WAR_INFANTRY', 'UNIT_RIFLEMAN', 'UNIT_CAVALRY', 'UNIT_ARTILLERY', 'UNIT_MACHINE_GUN', 'UNIT_TRIPLANE', 'UNIT_WWI_BOMBER', 'UNIT_WWI_TANK',
         'UNIT_IRONCLAD', 'UNIT_DESTROYER', 'UNIT_BATTLESHIP', 'UNIT_SUBMARINE', 'UNIT_GREAT_GENERAL', 'UNIT_WORKER', 'UNIT_CARAVAN', 'UNIT_CARGO_SHIP']
UID = {u.split('_', 1)[1]: i for i, u in enumerate(UNITS)}
PROMOS = ['PROMOTION_DRILL_1', 'PROMOTION_DRILL_2', 'PROMOTION_SHOCK_1', 'PROMOTION_SHOCK_2', 'PROMOTION_COVER_1', 'PROMOTION_MOBILITY', 'PROMOTION_MARCH',
          'PROMOTION_MEDIC', 'PROMOTION_ACCURACY_1', 'PROMOTION_BARRAGE_1', 'PROMOTION_SENTRY', 'PROMOTION_AMBUSH_1', 'PROMOTION_INTERCEPTION_1', 'PROMOTION_CHARGE', 'PROMOTION_FORMATION_1']
PRID = {p.split('_', 1)[1]: i for i, p in enumerate(PROMOS)}
AIR = {'TRIPLANE', 'WWI_BOMBER'}; NAVAL = {'IRONCLAD', 'DESTROYER', 'BATTLESHIP', 'SUBMARINE', 'CARGO_SHIP'}; CIVIL = {'GREAT_GENERAL', 'WORKER', 'CARAVAN', 'CARGO_SHIP'}
LEGION = ['DRILL_1', 'SHOCK_1']   # the Spanish Legion (named by the setup script from these two promotions)
REGULARES = ['SHOCK_1']           # the Moroccan Regulares
REQUETE = ['SHOCK_1']             # the Carlist requetes of Navarre
GUARD = ['DRILL_1', 'COVER_1']    # the Assault Guards and the loyal Guardia Civil, the defenders of the Alcazar and of Oviedo
COLUMN = ['SHOCK_1', 'MARCH']     # the confederal columns
DEPLOY = [   # (type, owner, lon, lat, promotions, xp, count)
    # --- the Republic: most of the air force and the fleet, the Assault Guards, and militias of every party around Madrid and in the sierras
    ('GREAT_WAR_INFANTRY', REP, -3.70, 40.42, GUARD, 15, 2), ('RIFLEMAN', REP, -3.70, 40.42, [], 5, 3), ('ARTILLERY', REP, -3.70, 40.42, [], 8, 2), ('MACHINE_GUN', REP, -3.70, 40.42, [], 5, 1),
    ('GREAT_GENERAL', REP, -3.70, 40.42, [], 0, 1), ('TRIPLANE', REP, -3.70, 40.42, [], 10, 2), ('WWI_BOMBER', REP, -3.70, 40.42, [], 10, 2), ('WWI_TANK', REP, -3.70, 40.42, [], 5, 1),
    ('RIFLEMAN', REP, -4.05, 40.72, [], 5, 2), ('GREAT_WAR_INFANTRY', REP, -4.00, 40.68, [], 8, 1), ('RIFLEMAN', REP, -3.62, 40.95, [], 5, 2), ('GREAT_WAR_INFANTRY', REP, -3.60, 40.90, [], 8, 1),
    ('RIFLEMAN', REP, -4.00, 39.80, [], 5, 2), ('ARTILLERY', REP, -3.95, 39.82, [], 5, 1), ('RIFLEMAN', REP, -3.17, 40.63, [], 5, 1), ('RIFLEMAN', REP, -2.64, 41.07, [], 5, 1),
    ('GREAT_WAR_INFANTRY', REP, -0.38, 39.47, [], 8, 1), ('RIFLEMAN', REP, -0.38, 39.47, [], 5, 2), ('RIFLEMAN', REP, -1.86, 38.99, [], 5, 1), ('RIFLEMAN', REP, -0.48, 38.35, [], 5, 1),
    ('RIFLEMAN', REP, -1.13, 37.99, [], 5, 1), ('GREAT_WAR_INFANTRY', REP, -0.98, 37.60, [], 8, 1), ('BATTLESHIP', REP, -4.6, 36.55, [], 10, 1), ('DESTROYER', REP, -5.0, 36.30, [], 10, 2),
    ('DESTROYER', REP, -4.3, 36.62, [], 10, 2), ('DESTROYER', REP, -0.95, 37.50, [], 5, 1), ('SUBMARINE', REP, -0.90, 37.45, [], 5, 2), ('RIFLEMAN', REP, -2.46, 36.84, [], 5, 1),
    ('RIFLEMAN', REP, -4.42, 36.72, [], 5, 2), ('RIFLEMAN', REP, -3.79, 37.78, [], 5, 1), ('RIFLEMAN', REP, -3.75, 37.30, [], 5, 2), ('RIFLEMAN', REP, -4.60, 37.98, [], 5, 2),
    ('GREAT_WAR_INFANTRY', REP, -6.97, 38.88, [], 8, 1), ('RIFLEMAN', REP, -6.97, 38.88, [], 5, 1), ('RIFLEMAN', REP, -6.34, 38.92, [], 5, 1), ('RIFLEMAN', REP, -6.95, 37.26, [], 5, 1),
    ('RIFLEMAN', REP, -3.93, 38.99, [], 5, 1), ('RIFLEMAN', REP, -4.83, 39.96, [], 5, 1), ('RIFLEMAN', REP, -5.17, 36.74, [], 5, 1),
    ('GREAT_WAR_INFANTRY', REP, -5.66, 43.54, [], 8, 1), ('RIFLEMAN', REP, -5.66, 43.54, [], 5, 1), ('RIFLEMAN', REP, -5.80, 43.32, ['SHOCK_1'], 10, 3), ('ARTILLERY', REP, -5.75, 43.30, [], 5, 1),
    ('GREAT_WAR_INFANTRY', REP, -3.80, 43.46, [], 8, 1), ('RIFLEMAN', REP, -3.80, 43.46, [], 5, 1), ('RIFLEMAN', REP, -4.14, 43.00, [], 5, 1), ('GREAT_WAR_INFANTRY', REP, 4.27, 39.89, [], 8, 1),
    ('WORKER', REP, -3.70, 40.42, [], 0, 2), ('WORKER', REP, -0.38, 39.47, [], 0, 1), ('WORKER', REP, -5.66, 43.54, [], 0, 1),
    # --- the Nationalists of the South: the Army of Africa, still in Morocco behind the Republican fleet, and the garrisons that held Andalusia
    ('GREAT_WAR_INFANTRY', NAT, -5.32, 35.89, LEGION, 30, 2), ('GREAT_WAR_INFANTRY', NAT, -5.37, 35.57, LEGION, 30, 2), ('RIFLEMAN', NAT, -5.37, 35.57, REGULARES, 20, 2),
    ('CAVALRY', NAT, -5.37, 35.57, REGULARES, 15, 1), ('ARTILLERY', NAT, -5.37, 35.57, [], 10, 1), ('GREAT_GENERAL', NAT, -5.37, 35.57, [], 0, 1), ('TRIPLANE', NAT, -5.37, 35.57, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NAT, -2.94, 35.29, LEGION, 30, 2), ('RIFLEMAN', NAT, -2.94, 35.29, REGULARES, 20, 2), ('RIFLEMAN', NAT, -6.16, 35.19, REGULARES, 15, 1),
    ('IRONCLAD', NAT, -5.30, 35.95, [], 5, 2), ('RIFLEMAN', NAT, -3.93, 35.25, REGULARES, 10, 1),
    ('GREAT_WAR_INFANTRY', NAT, -5.98, 37.39, [], 10, 1), ('RIFLEMAN', NAT, -5.98, 37.39, [], 5, 2), ('ARTILLERY', NAT, -5.98, 37.39, [], 8, 1), ('GREAT_GENERAL', NAT, -5.98, 37.39, [], 0, 1),
    ('GREAT_WAR_INFANTRY', NAT, -6.29, 36.53, REGULARES, 20, 1), ('RIFLEMAN', NAT, -6.14, 36.69, [], 5, 1), ('RIFLEMAN', NAT, -5.45, 36.13, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NAT, -4.78, 37.88, [], 10, 1), ('RIFLEMAN', NAT, -4.78, 37.88, [], 5, 1), ('ARTILLERY', NAT, -4.78, 37.88, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NAT, -3.60, 37.18, [], 10, 1), ('RIFLEMAN', NAT, -3.60, 37.18, [], 5, 1), ('GREAT_WAR_INFANTRY', NAT, -4.02, 39.86, GUARD, 20, 1),
    ('GREAT_WAR_INFANTRY', NAT, 2.65, 39.57, [], 10, 2), ('ARTILLERY', NAT, 2.65, 39.57, [], 5, 1), ('RIFLEMAN', NAT, 1.43, 38.91, [], 5, 1),
    ('WORKER', NAT, -5.98, 37.39, [], 0, 2), ('WORKER', NAT, -5.37, 35.57, [], 0, 1),
    # --- the Army of the North: Mola's columns at the Somosierra and Guadarrama passes, the Navarrese requetes, the garrisons of Old Castile, Galicia, Aragon and Oviedo, the Ferrol squadron
    ('RIFLEMAN', NORTH, -1.64, 42.81, REQUETE, 15, 3), ('GREAT_WAR_INFANTRY', NORTH, -1.64, 42.81, [], 10, 1), ('ARTILLERY', NORTH, -1.64, 42.81, [], 5, 1), ('GREAT_GENERAL', NORTH, -1.64, 42.81, [], 0, 1),
    ('GREAT_WAR_INFANTRY', NORTH, -3.70, 42.34, [], 10, 1), ('CAVALRY', NORTH, -3.70, 42.34, [], 10, 1), ('TRIPLANE', NORTH, -3.70, 42.34, [], 5, 1), ('WWI_BOMBER', NORTH, -5.57, 42.60, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NORTH, -3.62, 41.15, [], 10, 2), ('RIFLEMAN', NORTH, -3.70, 41.20, REQUETE, 10, 1), ('GREAT_WAR_INFANTRY', NORTH, -4.15, 40.78, [], 10, 2), ('RIFLEMAN', NORTH, -4.18, 40.82, [], 5, 1),
    ('ARTILLERY', NORTH, -4.12, 40.85, [], 5, 1), ('GREAT_WAR_INFANTRY', NORTH, -4.72, 41.65, [], 10, 1), ('RIFLEMAN', NORTH, -4.72, 41.65, [], 5, 1), ('CAVALRY', NORTH, -4.72, 41.65, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NORTH, -0.88, 41.65, [], 10, 2), ('ARTILLERY', NORTH, -0.88, 41.65, [], 8, 1), ('RIFLEMAN', NORTH, -0.88, 41.65, [], 5, 1), ('GREAT_GENERAL', NORTH, -0.88, 41.65, [], 0, 1),
    ('GREAT_WAR_INFANTRY', NORTH, -0.41, 42.14, [], 8, 1), ('GREAT_WAR_INFANTRY', NORTH, -1.11, 40.34, [], 8, 1), ('RIFLEMAN', NORTH, -2.67, 42.85, REQUETE, 10, 1), ('RIFLEMAN', NORTH, -2.45, 42.47, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NORTH, -8.41, 43.36, [], 8, 1), ('GREAT_WAR_INFANTRY', NORTH, -8.23, 43.48, [], 8, 1), ('BATTLESHIP', NORTH, -8.30, 43.52, [], 5, 1), ('DESTROYER', NORTH, -8.35, 43.55, [], 5, 1),
    ('RIFLEMAN', NORTH, -8.72, 42.24, [], 5, 1), ('GREAT_WAR_INFANTRY', NORTH, -7.56, 43.01, [], 8, 1), ('GREAT_WAR_INFANTRY', NORTH, -5.85, 43.36, GUARD, 20, 2), ('ARTILLERY', NORTH, -5.85, 43.36, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NORTH, -5.66, 40.97, [], 8, 1), ('GREAT_WAR_INFANTRY', NORTH, -6.37, 39.48, [], 8, 1), ('RIFLEMAN', NORTH, -6.37, 39.48, [], 5, 1), ('GREAT_WAR_INFANTRY', NORTH, -5.57, 42.60, [], 8, 1),
    ('RIFLEMAN', NORTH, -4.70, 40.66, [], 5, 1), ('RIFLEMAN', NORTH, -2.47, 41.76, [], 5, 1), ('WORKER', NORTH, -3.70, 42.34, [], 0, 2), ('WORKER', NORTH, -4.72, 41.65, [], 0, 1),
    # --- the Generalitat: the Assault Guards and the Guardia Civil that crushed the rising on 19-20 July, the first militias, the Aragon front columns of the parties
    ('GREAT_WAR_INFANTRY', CAT, 2.17, 41.39, GUARD, 15, 2), ('RIFLEMAN', CAT, 2.17, 41.39, [], 5, 3), ('ARTILLERY', CAT, 2.17, 41.39, [], 5, 1), ('MACHINE_GUN', CAT, 2.17, 41.39, [], 5, 1),
    ('GREAT_GENERAL', CAT, 2.17, 41.39, [], 0, 1), ('TRIPLANE', CAT, 2.17, 41.39, [], 5, 1), ('RIFLEMAN', CAT, 0.62, 41.62, [], 5, 1), ('RIFLEMAN', CAT, 1.25, 41.12, [], 5, 1),
    ('RIFLEMAN', CAT, 2.82, 41.98, [], 5, 1), ('RIFLEMAN', CAT, 0.52, 40.81, [], 5, 1), ('RIFLEMAN', CAT, -0.30, 42.02, [], 5, 2), ('DESTROYER', CAT, 2.25, 41.30, [], 5, 1),
    ('WORKER', CAT, 2.17, 41.39, [], 0, 2),
    # --- Euzkadi: Biscay and Gipuzkoa, the Basque battalions and the loyal garrison of San Sebastian
    ('GREAT_WAR_INFANTRY', EUZ, -2.93, 43.26, [], 8, 1), ('RIFLEMAN', EUZ, -2.93, 43.26, [], 5, 3), ('ARTILLERY', EUZ, -2.93, 43.26, [], 5, 1), ('GREAT_GENERAL', EUZ, -2.93, 43.26, [], 0, 1),
    ('GREAT_WAR_INFANTRY', EUZ, -1.98, 43.32, [], 8, 1), ('RIFLEMAN', EUZ, -1.98, 43.32, [], 5, 2), ('RIFLEMAN', EUZ, -1.79, 43.34, [], 5, 1), ('RIFLEMAN', EUZ, -2.08, 43.14, [], 5, 1),
    ('IRONCLAD', EUZ, -2.95, 43.40, [], 5, 1), ('WORKER', EUZ, -2.93, 43.26, [], 0, 1),
    # --- the CNT-FAI: the Durruti column on the road to Zaragoza, the Ascaso column before Huesca, the Ortiz column at Caspe, the Iron Column on the Teruel front
    ('RIFLEMAN', CNT, -0.30, 41.50, COLUMN, 15, 3), ('GREAT_GENERAL', CNT, -0.15, 41.50, [], 0, 1), ('MACHINE_GUN', CNT, -0.20, 41.50, [], 5, 1), ('WWI_TANK', CNT, -0.10, 41.45, [], 5, 1),
    ('RIFLEMAN', CNT, -0.20, 42.05, COLUMN, 10, 2), ('RIFLEMAN', CNT, -0.04, 41.23, COLUMN, 10, 2), ('ARTILLERY', CNT, -0.04, 41.23, [], 5, 1), ('RIFLEMAN', CNT, -0.80, 40.20, COLUMN, 10, 2),
    ('RIFLEMAN', CNT, -0.13, 41.05, [], 5, 1), ('WORKER', CNT, -0.04, 41.23, [], 0, 1),
    # --- barbarians: fugitives in the sierras of the Nationalist zone (huidos, fuxidos)
    ('RIFLEMAN', BARB, -7.20, 42.45, [], 5, 2), ('RIFLEMAN', BARB, -6.80, 42.75, [], 5, 1), ('RIFLEMAN', BARB, -6.20, 40.35, [], 5, 2), ('RIFLEMAN', BARB, -5.20, 40.28, [], 5, 1),
    ('RIFLEMAN', BARB, -5.95, 37.92, [], 5, 2), ('RIFLEMAN', BARB, -6.10, 42.25, [], 5, 1),
]
# every city-state keeps a garrison and a worker in its capital, a garrison in its other towns
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES):
    DEPLOY.append(('GREAT_WAR_INFANTRY', 32 + i, lo, la, ['DRILL_1'], 10, 2 if popk >= 150 else 1)); DEPLOY.append(('WORKER', 32 + i, lo, la, [], 0, 1))
units = []
land_occ = set(); naval_occ = set(); civ_occ = set(); air_count = Counter()
def place_unit(tp, pl, lo, la, promos, xp):
    allies = NATS if pl in NATS else REPS if pl in REPS else {pl}
    def ok(x, y):
        o = owner[y, x]
        if tp in AIR: return (x, y) in city_at and CITIES[city_at[(x, y)]][3] == pl and air_count[(x, y)] < 4
        if pl == BARB: return is_land[y, x] and elev[y, x] != 2 and (x, y) not in city_at and (x, y) not in land_occ and o == NONE
        if tp in NAVAL: return (not is_land[y, x]) and (x, y) not in naval_occ and (o == NONE or o in allies) and terrain[y, x] in (COAST, OCEAN)
        if not is_land[y, x] or elev[y, x] == 2: return False
        if o != NONE and o not in allies: return False
        if (x, y) in city_at and CITIES[city_at[(x, y)]][3] != pl: return False
        if tp == 'CARAVAN': return (x, y) in city_at and CITIES[city_at[(x, y)]][3] == pl and 'cap' in CITIES[city_at[(x, y)]][5]
        if tp in CIVIL: return (x, y) not in civ_occ
        return (x, y) not in land_occ
    t = find_tile(lo, la, ok, 6 if pl == BARB else 4)
    if t is None: print('  !! cannot place', tp, pl, lo, la); return
    if tp in AIR: air_count[t] += 1
    elif tp in NAVAL: naval_occ.add(t)
    elif tp == 'CARAVAN': pass
    elif tp in CIVIL: civ_occ.add(t)
    else: land_occ.add(t)
    units.append(dict(type=tp, owner=pl, x=t[0], y=t[1], promos=promos, xp=xp))
for pl in range(NP):
    cap = next(c for c in CITIES if c[3] == pl and 'cap' in c[5])
    DEPLOY.append(('CARAVAN', pl, cap[1], cap[2], [], 0, 2))
for tp, pl, lo, la, promos, xp, cnt in DEPLOY:
    for i in range(cnt): place_unit(tp, pl, lo, la, promos, xp)
STR = {'GREAT_WAR_INFANTRY': 50, 'RIFLEMAN': 34, 'CAVALRY': 34, 'ARTILLERY': 28, 'MACHINE_GUN': 60, 'TRIPLANE': 35, 'WWI_BOMBER': 50, 'WWI_TANK': 60, 'IRONCLAD': 45, 'DESTROYER': 55, 'BATTLESHIP': 65, 'SUBMARINE': 60}
for pl in list(range(NP)) + [BARB]:
    us = [u for u in units if u['owner'] == pl]
    print(f"  {PLAYERS[pl]['key'] if pl != BARB else 'BARB'}: {len(us)} units, strength {sum(STR.get(u['type'], 0) for u in us)}, {dict(Counter(u['type'] for u in us))}")

# ============================================================== strategic resource balance (horses for the cavalry, coal for the gunboats, oil for the aircraft and the
# tanks that arrive by event: Spain had no oil wells, the deposits stand for the CAMPSA depots and the imported fuel, Texaco's on credit for the Nationalists)
UNIT_RES = {'CAVALRY': 'HORSE', 'IRONCLAD': 'COAL', 'WWI_TANK': 'OIL', 'BATTLESHIP': 'OIL', 'TRIPLANE': 'OIL', 'WWI_BOMBER': 'OIL'}
BLD_RES = {'BUILDING_FACTORY': 'COAL'}
STRATEGIC = ('IRON', 'HORSE', 'COAL', 'OIL')
# reserve for the aircraft, tanks and cruisers the events bring (ui/Spain1936_Events.lua)
EVENT_NEED = {REP: {'OIL': 10, 'HORSE': 1}, NAT: {'OIL': 12, 'HORSE': 2}, NORTH: {'OIL': 6, 'HORSE': 1}, CAT: {'OIL': 2}, EUZ: {'OIL': 1}, CNT: {'OIL': 2}}
DEPOSITS = {REP: {'HORSE': [(-3.0, 39.6), (-6.2, 38.6)], 'COAL': [(-4.1, 38.7)], 'OIL': [(-0.98, 37.62), (-3.6, 40.3), (-0.4, 39.45), (-5.70, 43.52)]},
            NAT: {'HORSE': [(-5.8, 37.0), (-5.6, 35.3)], 'COAL': [(-5.3, 38.0)], 'OIL': [(-6.2, 36.6), (-5.9, 37.3), (-5.40, 35.55), (2.70, 39.62)]},
            NORTH: {'HORSE': [(-4.5, 41.8), (-1.7, 42.5)], 'COAL': [(-6.4, 42.7)], 'OIL': [(-8.25, 43.40), (-4.6, 41.6), (-0.95, 41.7)]},
            CAT: {'HORSE': [(1.0, 41.7)], 'COAL': [(1.85, 42.1)], 'OIL': [(1.95, 41.40), (1.20, 41.15)]},
            EUZ: {'HORSE': [(-2.5, 43.1)], 'COAL': [(-2.6, 43.2)], 'OIL': [(-2.98, 43.30)]},
            CNT: {'HORSE': [(-0.2, 41.7)], 'COAL': [(0.3, 41.37)], 'OIL': [(0.0, 41.3)]}}
AMOUNT = {'OIL': 4, 'COAL': 4, 'HORSE': 3, 'IRON': 4}
def res_name(x, y): return RESOURCES[resource[y, x]].split('_', 1)[1] if resource[y, x] != NONE else None
def improve_strategic(x, y):
    r = res_name(x, y)
    if (x, y) in city_at or r not in STRATEGIC or not is_land[y, x] or elev[y, x] == 2: return
    improvement[y, x] = IID['WELL'] if r == 'OIL' else IID['PASTURE'] if r == 'HORSE' else IID['MINE']
    if feature[y, x] in (FOREST, MARSH): feature[y, x] = NONE
need = {pl: Counter(EVENT_NEED.get(pl, {})) for pl in range(NP)}
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
# Brave New World techs through the Industrial era (TECH_ERAS.json also lists base-game techs BNW removed, such as Telegraph)
TECHS = sorted([l.strip() for l in open(f'{XMLDIR}/TECHS_THROUGH_INDUSTRIAL.txt') if l.strip()] + ['TECH_FLIGHT', 'TECH_COMBUSTION', 'TECH_REPLACEABLE_PARTS', 'TECH_RAILROAD', 'TECH_REFRIGERATION', 'TECH_BALLISTICS'])
TRAD = ['POLICY_TRADITION', 'POLICY_ARISTOCRACY', 'POLICY_OLIGARCHY', 'POLICY_LEGALISM', 'POLICY_LANDED_ELITE', 'POLICY_MONARCHY', 'POLICY_TRADITION_FINISHER']
HONOR = ['POLICY_HONOR', 'POLICY_WARRIOR_CODE', 'POLICY_DISCIPLINE', 'POLICY_MILITARY_TRADITION', 'POLICY_MILITARY_CASTE', 'POLICY_PROFESSIONAL_ARMY', 'POLICY_HONOR_FINISHER']
LIBERTY = ['POLICY_LIBERTY', 'POLICY_COLLECTIVE_RULE', 'POLICY_CITIZENSHIP', 'POLICY_REPUBLIC', 'POLICY_REPRESENTATION', 'POLICY_MERITOCRACY', 'POLICY_LIBERTY_FINISHER']
PLAYER_POLICIES = {
    REP: LIBERTY + HONOR[:3],
    NAT: HONOR + TRAD[:3],
    NORTH: TRAD + HONOR[:4],
    CAT: LIBERTY[:5] + HONOR[:2],
    EUZ: TRAD[:4] + HONOR[:2],
    CNT: LIBERTY[:3] + HONOR[:3],
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
war = sorted((a, b) for a in sorted(NATS) for b in sorted(REPS))
nat_peace = [(NAT, NORTH)]
rep_pairs = [(a, b) for a in sorted(REPS) for b in sorted(REPS) if a < b]
# contact: all; war: every Nationalist against every Republican side, locked; the two Nationalist armies locked at peace with open borders;
# the four Republican sides at peace with open borders but not locked: a May Days of their own stays possible
rel = relbits(contact) + relbits(war) + relbits(war + nat_peace) + relbits(nat_peace + rep_pairs) + relbits([])
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
name_b = b'Spain 1936\0'
desc_b = (b'25 July 1936. The Spanish Civil War from Galicia to Menorca and from the Pyrenees to the Rif at ~%d km per hex: the Republic, Catalonia, the Basque '
          b'Country and the CNT-FAI against Franco\'s Army of Africa and Mola\'s Army of the North, with Portugal, Gibraltar, Tangier, Andorra and France as city-states. '
          b'One turn is one week. Domination only.\0' % int(round(HW)))
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
    f.write(struct.pack('<64sIIIiBBBB9I', b'GAMESPEED_QUICK', 0, 0, 0, 1936, P, CS, T, 0,
                        len(imp_b), len(unit_b), len(tech_b), len(pol_b), len(bld_b), len(prom_b), len(unit_data), 0, len(city_data)))
    f.write(struct.pack('<II', len(vict_b), len(opt_b)))
    f.write(imp_b + unit_b + tech_b + pol_b + bld_b + prom_b + unit_data + city_data + vict_b + opt_b + rel + influence + visibility)
    f.write(team_data + player_data + bytes(plot_data))
print('wrote', OUT_MAP, os.path.getsize(OUT_MAP), 'bytes;', len(CITIES), 'cities,', len(units), 'units')
land_n = int(is_land.sum()); print(f'land {land_n} ({land_n/(W*H):.1%}) mountains {int((elev==2).sum())} hills {int((elev==1).sum())} forest {int((feature==FOREST).sum())} marsh {int((feature==MARSH).sum())} tundra {int((terrain==TUNDRA).sum())} snow {int((terrain==SNOW).sum())} desert {int((terrain==DESERT).sum())} grass {int(((terrain==GRASS)&is_land).sum())} plains {int(((terrain==PLAINS)&is_land).sum())}')
print('  owned tiles:', {PLAYERS[k]['key']: int((owner == k).sum()) for k in range(NP)}, 'city-states', int(((owner >= 32) & (owner < 96)).sum()))
print('  cities per side:', {PLAYERS[k]['key']: sum(1 for c in CITIES if c[3] == k) for k in range(NP)}, 'city-states', sum(1 for c in CITIES if c[3] >= 32))
json.dump(dict(W=W, H=H, cities={c[0]: dict(x=city_tiles[i][0], y=city_tiles[i][1], owner=int(c[3])) for i, c in enumerate(CITIES)}), open(os.path.join(HERE, 'map_layout.json'), 'w'), indent=0)

# ============================================================== mod wrapper
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest().upper()
UI_FILES = ['Spain1936LoadScreen.lua', 'Spain1936LoadScreen.xml', 'Spain1936_Production.lua', 'Spain1936_Production.xml', 'Spain1936_Events.lua', 'Spain1936_Events.xml', 'Spain1936_Uniques.sql', 'Spain1936_Text.xml']
for fn in UI_FILES:
    src = os.path.join(HERE, 'ui', fn)
    if os.path.exists(src): shutil.copy(src, os.path.join(OUT_DIR, fn))
    else: print('  !! missing ui file', fn)
WONDERS_OFF = [l.strip() for l in open(f'{XMLDIR}/WORLD_WONDERS.txt') if l.strip()]
rules = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Spain 1936: no world wonders, no Manhattan Project, no Apollo Program; weekly calendar parked; neighbours as city-states; faction colours; European city and unit art for every side. -->', '<GameData>', '  <Buildings>']
for w in WONDERS_OFF: rules.append(f'    <Update><Where Type="{w}" /><Set PrereqTech="TECH_FUTURE_TECH" /></Update>')
rules += ['  </Buildings>', '  <Projects>', '    <Update><Where Type="PROJECT_MANHATTAN_PROJECT" /><Set TechPrereq="TECH_FUTURE_TECH" /></Update>',
          '    <Update><Where Type="PROJECT_APOLLO_PROGRAM" /><Set TechPrereq="TECH_FUTURE_TECH" /></Update>', '  </Projects>',
          '  <GameSpeed_Turns>', '    <Delete GameSpeedType="GAMESPEED_STANDARD" />',
          '    <Row><GameSpeedType>GAMESPEED_STANDARD</GameSpeedType><MonthIncrement>1</MonthIncrement><TurnsPerIncrement>100000</TurnsPerIncrement></Row>',
          '    <Delete GameSpeedType="GAMESPEED_QUICK" />',
          '    <Row><GameSpeedType>GAMESPEED_QUICK</GameSpeedType><MonthIncrement>1</MonthIncrement><TurnsPerIncrement>100000</TurnsPerIncrement></Row>',
          '  </GameSpeed_Turns>', '  <Defines>', '    <Update><Where Name="START_YEAR" /><Set Value="1936" /></Update>', '  </Defines>', '  <Colors>']
def rgb(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
PCOL = {'REP': ('#F1C40F', '#5B2A6E'), 'NAT': ('#F1BF00', '#AA151B'), 'NORTH': ('#C8102E', '#F2F2F2'), 'CAT': ('#DA121A', '#FCDD09'), 'EUZ': ('#FFFFFF', '#00843D'), 'CNT': ('#E30613', '#141414')}
for k, (icon, bg) in PCOL.items():
    for suf, h in (('ICON', icon), ('BG', bg)):
        r, g, b = rgb(h); rules.append(f'    <Row><Type>COLOR_PLAYER_ESP1936_{k}_{suf}</Type><Red>{r:.3f}</Red><Green>{g:.3f}</Green><Blue>{b:.3f}</Blue><Alpha>1</Alpha></Row>')
rules += ['  </Colors>', '  <PlayerColors>']
for k in PCOL: rules.append(f'    <Row><Type>PLAYERCOLOR_ESP1936_{k}</Type><PrimaryColor>COLOR_PLAYER_ESP1936_{k}_ICON</PrimaryColor><SecondaryColor>COLOR_PLAYER_ESP1936_{k}_BG</SecondaryColor><TextColor>COLOR_PLAYER_WHITE_TEXT</TextColor></Row>')
rules += ['  </PlayerColors>', '  <Civilizations>']
for p in PLAYERS: rules.append(f'    <Update><Where Type="{p["civ"]}" /><Set DefaultPlayerColor="{p["color"]}" ArtStyleType="ARTSTYLE_EUROPEAN" ArtStyleSuffix="_EURO" ArtStylePrefix="EUROPEAN " /></Update>')
rules += ['  </Civilizations>', '  <MinorCivilizations>']
MCOL = ['PLAYERCOLOR_MINOR_LIGHT_GREEN', 'PLAYERCOLOR_MINOR_LIGHT_BLUE', 'PLAYERCOLOR_MINOR_GOLDENROD', 'PLAYERCOLOR_MINOR_LIGHT_PURPLE', 'PLAYERCOLOR_MINOR_MIDDLE_CYAN', 'PLAYERCOLOR_MINOR_PEACH']
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES):
    tk = f'TXT_KEY_CITYSTATE_ESP1936_{key}'
    rules.append(f'    <Row><Type>{mtype}</Type><Description>{tk}</Description><Civilopedia>{tk}</Civilopedia><ShortDescription>{tk}</ShortDescription><Adjective>{tk}</Adjective><ArtDefineTag>ART_DEF_CIVILIZATION_MINOR</ArtDefineTag><DefaultPlayerColor>{MCOL[i]}</DefaultPlayerColor><ArtStyleType>ARTSTYLE_EUROPEAN</ArtStyleType><ArtStyleSuffix>_EURO</ArtStyleSuffix><ArtStylePrefix>EUROPEAN </ArtStylePrefix><MinorCivTrait>{trait}</MinorCivTrait></Row>')
rules += ['  </MinorCivilizations>', '  <MinorCivilization_CityNames>']
for key, name, mtype, trait, lo, la, popk in CITY_STATES: rules.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><CityName>TXT_KEY_CITY_ESP1936_{key}</CityName></Row>')
rules += ['  </MinorCivilization_CityNames>', '  <MinorCivilization_Flavors>']
for key, name, mtype, trait, lo, la, popk in CITY_STATES:
    for fl, v in (('FLAVOR_CITY_DEFENSE', 9), ('FLAVOR_DEFENSE', 9), ('FLAVOR_GROWTH', 4), ('FLAVOR_GOLD', 5), ('FLAVOR_PRODUCTION', 5)):
        rules.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><FlavorType>{fl}</FlavorType><Flavor>{v}</Flavor></Row>')
rules += ['  </MinorCivilization_Flavors>', '</GameData>', '']
open(os.path.join(OUT_DIR, 'Spain1936_Rules.xml'), 'w').write('\n'.join(rules))
# --- leader art: static diplomacy scenes, portrait atlas, faction emblem atlases, Dawn of Man images (built by art/build_art.py)
ART = os.path.join(HERE, 'art', 'out'); art_files = []
if os.path.isdir(ART):
    for f in sorted(glob.glob(os.path.join(ART, '*.dds'))):
        shutil.copy(f, os.path.join(OUT_DIR, os.path.basename(f))); art_files.append(os.path.basename(f))
    shutil.copy(os.path.join(HERE, 'art', 'src', 'CREDITS.txt'), os.path.join(OUT_DIR, 'CREDITS.txt'))
LEADER_ART = [('LEADER_CATHERINE', 'CIVILIZATION_RUSSIA', 'Azana'), ('LEADER_SHAKA', 'CIVILIZATION_ZULU', 'Franco'), ('LEADER_BISMARCK', 'CIVILIZATION_GERMANY', 'Mola'),
              ('LEADER_POCATELLO', 'CIVILIZATION_SHOSHONE', 'Companys'), ('LEADER_SELASSIE', 'CIVILIZATION_ETHIOPIA', 'Aguirre'), ('LEADER_MONTEZUMA', 'CIVILIZATION_AZTEC', 'Durruti')]
scene_files = []
if art_files:
    for i, (ld, cv, key) in enumerate(LEADER_ART):
        fn = f'ESP1936_{key}_Scene.xml'; scene_files.append(fn)
        open(os.path.join(OUT_DIR, fn), 'w').write(f'<?xml version="1.0" encoding="utf-8"?>\n<LeaderScene FallbackImage="ESP1936_Scene_{key}.dds">\n</LeaderScene>\n')
    lx = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Spain 1936: static leader scenes, portrait atlas, faction emblems and Dawn of Man images (Firaxis Civil War technique). -->', '<GameData>', '  <IconTextureAtlases>']
    for size in (256, 128, 64): lx.append(f'    <Row><Atlas>ESP1936_LEADER_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>ESP1936_Leaders{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    for size in (256, 128, 80, 64, 45, 32): lx.append(f'    <Row><Atlas>ESP1936_CIV_COLOR_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>ESP1936_CivColor{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    for size in (128, 64, 48, 32, 24, 16): lx.append(f'    <Row><Atlas>ESP1936_CIV_ALPHA_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>ESP1936_CivWhite{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    lx += ['  </IconTextureAtlases>', '  <Leaders>']
    for i, (ld, cv, key) in enumerate(LEADER_ART): lx.append(f'    <Update><Where Type="{ld}" /><Set ArtDefineTag="ESP1936_{key}_Scene.xml" PortraitIndex="{i}" IconAtlas="ESP1936_LEADER_ATLAS" /></Update>')
    lx += ['  </Leaders>', '  <Civilizations>']
    for i, (ld, cv, key) in enumerate(LEADER_ART): lx.append(f'    <Update><Where Type="{cv}" /><Set PortraitIndex="{i}" IconAtlas="ESP1936_CIV_COLOR_ATLAS" AlphaIconAtlas="ESP1936_CIV_ALPHA_ATLAS" DawnOfManImage="ESP1936_DOM_{key}.dds" /></Update>')
    lx += ['  </Civilizations>', '</GameData>', '']
    open(os.path.join(OUT_DIR, 'Spain1936_Leaders.xml'), 'w').write('\n'.join(lx))
def filerow(fn, imp): return f'    <File md5="{md5(os.path.join(OUT_DIR, fn))}" import="{imp}">{fn}</File>'
FILES_XML = '\n'.join([filerow('Spain1936.Civ5Map', 1), filerow('Spain1936_Rules.xml', 0)] + [filerow(fn, 0) for fn in UI_FILES if os.path.exists(os.path.join(OUT_DIR, fn))]
                      + ([filerow('Spain1936_Leaders.xml', 0), filerow('CREDITS.txt', 0)] if art_files else []) + [filerow(f, 1) for f in scene_files] + [filerow(f, 1) for f in art_files])
LEADERS_DB = '      <UpdateDatabase>Spain1936_Leaders.xml</UpdateDatabase>\n' if art_files else ''
MODINFO = f'''<?xml version="1.0" encoding="utf-8"?>
<Mod id="8c4f2a61-1936-4e0b-9d57-3a7e1b5c9f24" version="2">
  <Properties>
    <Name>Spain 1936</Name>
    <Teaser>The Spanish Civil War from 25 July 1936: the Republic, Catalonia, the Basques and the CNT-FAI against Franco and Mola on a {W}x{H} map of Iberia, the Balearics and Spanish Morocco.</Teaser>
    <Description>Spain, Portugal, the Balearics, Spanish Morocco and the French border as of 25 July 1936, one week after the rising. The Spanish Republic (Russia donor), the Generalitat of Catalonia (Shoshone), the Basque Country (Ethiopia) and the CNT-FAI columns in Aragon (Aztec) are at permanent war with Franco's Army of Africa and the South (Zulu) and Mola's Army of the North (Germany); the four Republican sides are allies who can still fall out. Portugal, Gibraltar, Tangier, Andorra, France and French North Africa are city-states; fugitives in the sierras are raging barbarians. One turn is one week; dated events bring the airlift, the International Brigades, Soviet aid, the Condor Legion and the Italian CTV, Guadalajara, Teruel, the Ebro and the Casado coup. The leaders are historical figures; their dialogue is invented. Domination victory only. Start it from the Mods menu via the scenario button.</Description>
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
      <UpdateDatabase>Spain1936_Rules.xml</UpdateDatabase>
      <UpdateDatabase>Spain1936_Uniques.sql</UpdateDatabase>
{LEADERS_DB}      <UpdateDatabase>Spain1936_Text.xml</UpdateDatabase>
    </OnModActivated>
  </Actions>
  <EntryPoints>
    <EntryPoint type="Custom" file="Spain1936LoadScreen.xml">
      <Name>Spain 1936</Name>
      <Description>July 1936: the Republic, Catalonia, the Basques and the anarchists against Franco and Mola. Choose your side and difficulty.</Description>
    </EntryPoint>
    <EntryPoint type="InGameUIAddin" file="Spain1936_Production.xml">
      <Name>Spain 1936 setup</Name>
      <Description>Production queues, unit names, alliances, weekly calendar.</Description>
    </EntryPoint>
    <EntryPoint type="InGameUIAddin" file="Spain1936_Events.xml">
      <Name>Spain 1936 events</Name>
      <Description>Dated events of the Civil War, July 1936 to March 1939.</Description>
    </EntryPoint>
  </EntryPoints>
</Mod>
'''
open(os.path.join(OUT_DIR, 'Spain1936.modinfo'), 'w').write(MODINFO)

# ============================================================== preview
S = 10
img = Image.new('RGB', (int((W + 0.5) * S) + 2, int(H * S * 0.866 + S) + 2), (10, 30, 70)); d = ImageDraw.Draw(img)
TCOL = {GRASS: (96, 168, 64), PLAINS: (196, 178, 96), DESERT: (236, 214, 150), TUNDRA: (170, 170, 150), SNOW: (240, 240, 240), COAST: (70, 140, 210), OCEAN: (20, 60, 130)}
OCOL = {REP: (150, 60, 170), NAT: (200, 30, 40), NORTH: (235, 235, 235), CAT: (250, 215, 30), EUZ: (20, 150, 70), CNT: (25, 25, 25), BARB: (0, 0, 0)}
def pcenter(x, y): return (x + 0.5 + 0.5 * (y & 1)) * S + 1, img.size[1] - (y * 0.866 * S + 0.577 * S) - 1
def pcorners(x, y, f=1.0):
    cx, cy = pcenter(x, y); r = S / math.sqrt(3) * f
    return [(cx + r * math.cos(math.radians(30 + 60 * k)), cy - r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
for y in range(H):
    for x in range(W):
        col = TCOL[terrain[y, x]]
        if feature[y, x] == FOREST: col = tuple(int(c * 0.6) for c in col)
        if feature[y, x] == MARSH: col = (80, 150, 130)
        o = int(owner[y, x])
        if o != NONE:
            oc = OCOL.get(o, (110, 110, 110)); col = tuple(int(c * 0.55 + k * 0.45) for c, k in zip(col, oc))
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
    elif u['type'] not in CIVIL and u['type'] not in AIR: d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=oc, outline=(0, 0, 0) if u['owner'] != CNT else (230, 0, 0))
for ci, (name, lo, la, pl, popk, tags) in enumerate(CITIES):
    cx, cy = pcenter(*city_tiles[ci])
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255) if 'cap' not in tags or pl >= 32 else (255, 0, 255), outline=(0, 0, 0))
    if popk >= 40 or 'cap' in tags: d.text((cx + 4, cy - 5), name, fill=(255, 255, 255))
img.save(OUT_PNG); print('wrote', OUT_PNG, img.size)
