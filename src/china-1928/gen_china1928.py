#!/usr/bin/env python3
"""China 1928: Civilization V scenario map of the Chinese warlord era, 10 October 1928.

Region: China from Yunnan and Gansu to the Ussuri and from the Amur to Hainan Strait, with Korea, Taiwan, northern Kyushu,
Outer Mongolia's south and Tonkin, 100 hexes wide (about 36 km per hex). Xinjiang, Tibet and western Qinghai lie outside.
Data: Natural Earth 10m (land, lakes, rivers, first-level regions), NOAA ETOPO 2022 relief, Koppen-Geiger climate.
Factions (10 October 1928, the day Chiang Kai-shek became Chairman of the National Government): Nanjing (China donor),
Feng Yuxiang's Guominjun (Zulu), Yan Xishan's Shanxi (Russia), Zhang Xueliang's Fengtian clique (Germany), the New Guangxi
clique (Ethiopia), the Chinese Communists (Shoshone); Japan, the Soviet Union, Mongolia, the provincial militarists of
Sichuan, Chongqing, Yunnan, Guizhou, Guangdong and Qinghai and the colonies of Hong Kong, Macau, Weihaiwei and French
Indochina as city-states; bandits and secret societies as raging barbarians. One turn = one week; Quick speed; domination only.
"""
import json, math, os, struct, hashlib, heapq, shutil, glob, pickle
from collections import defaultdict, Counter, deque
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('HEX_DATA', os.path.join(HERE, '..', '..', 'data'))        # tools/fetch_data.py
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
MOD_NAME = 'China 1928'
OUT_DIR = os.path.join(HERE, 'mod', 'China 1928 (v 1)')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_MAP = os.path.join(OUT_DIR, 'China1928.Civ5Map')
OUT_PNG = os.path.join(HERE, 'China1928_preview.png')

# ============================================================== projection / grid (Albers equal-area conic)
R = 6371.0; LON0 = 115.5
PHI1, PHI2 = math.radians(25.0), math.radians(45.0)
N = (math.sin(PHI1) + math.sin(PHI2)) / 2.0
C = math.cos(PHI1) ** 2 + 2 * N * math.sin(PHI1)
RHO0 = R * math.sqrt(C - 2 * N * math.sin(math.radians(35.3))) / N
def proj(lon, lat):
    phi = math.radians(lat); lam = math.radians(lon - LON0)
    rho = R * math.sqrt(C - 2 * N * math.sin(phi)) / N; th = N * lam
    return rho * math.sin(th), RHO0 - rho * math.cos(th)
def inv_np(x, y):
    dy = RHO0 - y; rho = np.sign(N) * np.sqrt(x * x + dy * dy)
    th = np.arctan2(np.sign(N) * x, np.sign(N) * dy)
    phi = np.arcsin((C - (rho * N / R) ** 2) / (2 * N))
    return np.degrees(th / N) + LON0, np.degrees(phi)

LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = 98.5, 132.5, 20.2, 50.4
W = 100
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
    dict(key='NAN', civ='CIVILIZATION_CHINA', leader='Chiang Kai-shek', name='National Government', color='PLAYERCOLOR_CHN1928_NAN', gold=2500),
    dict(key='GMJ', civ='CIVILIZATION_ZULU', leader='Feng Yuxiang', name='Guominjun', color='PLAYERCOLOR_CHN1928_GMJ', gold=900),
    dict(key='SHX', civ='CIVILIZATION_RUSSIA', leader='Yan Xishan', name='Shanxi', color='PLAYERCOLOR_CHN1928_SHX', gold=1500),
    dict(key='FT', civ='CIVILIZATION_GERMANY', leader='Zhang Xueliang', name='Fengtian', color='PLAYERCOLOR_CHN1928_FT', gold=2200),
    dict(key='GX', civ='CIVILIZATION_ETHIOPIA', leader='Li Zongren', name='Guangxi', color='PLAYERCOLOR_CHN1928_GX', gold=1000),
    dict(key='CCP', civ='CIVILIZATION_SHOSHONE', leader='Mao Zedong', name='Chinese Communists', color='PLAYERCOLOR_CHN1928_CCP', gold=300),
]
PIDX = {p['key']: i for i, p in enumerate(PLAYERS)}
NAN, GMJ, SHX, FT, GX, CCP = range(6)
NP = len(PLAYERS)
KMT = {NAN, GMJ, SHX, FT, GX}   # the five armies nominally united under the National Government in 1928
BARB = 96
NONE = 0xFF
# City-states: (key, EN name of the capital, type, trait, lon, lat, population in thousands around 1930)
CITY_STATES = [
    ('JAPAN', 'Dairen', 'MINOR_CIV_CHN1928_JAPAN', 'MINOR_TRAIT_MILITARISTIC', 121.61, 38.91, 360),
    ('SOVIET', 'Vladivostok', 'MINOR_CIV_CHN1928_SOVIET', 'MINOR_TRAIT_MILITARISTIC', 131.89, 43.12, 110),
    ('MONGOLIA', 'Ulan Bator', 'MINOR_CIV_CHN1928_MONGOLIA', 'MINOR_TRAIT_MILITARISTIC', 106.92, 47.92, 60),
    ('SICHUAN', 'Chengdu', 'MINOR_CIV_CHN1928_SICHUAN', 'MINOR_TRAIT_MILITARISTIC', 104.07, 30.67, 450),
    ('CHONGQING', 'Chongqing', 'MINOR_CIV_CHN1928_CHONGQING', 'MINOR_TRAIT_MERCANTILE', 106.55, 29.56, 280),
    ('YUNNAN', 'Kunming', 'MINOR_CIV_CHN1928_YUNNAN', 'MINOR_TRAIT_MILITARISTIC', 102.71, 25.04, 150),
    ('GUIZHOU', 'Guiyang', 'MINOR_CIV_CHN1928_GUIZHOU', 'MINOR_TRAIT_MILITARISTIC', 106.71, 26.58, 100),
    ('GUANGDONG', 'Canton', 'MINOR_CIV_CHN1928_GUANGDONG', 'MINOR_TRAIT_MERCANTILE', 113.26, 23.13, 860),
    ('QINGHAI', 'Xining', 'MINOR_CIV_CHN1928_QINGHAI', 'MINOR_TRAIT_MILITARISTIC', 101.78, 36.62, 50),
    ('HONGKONG', 'Hong Kong', 'MINOR_CIV_CHN1928_HONGKONG', 'MINOR_TRAIT_MARITIME', 114.17, 22.28, 840),
    ('MACAU', 'Macau', 'MINOR_CIV_CHN1928_MACAU', 'MINOR_TRAIT_MERCANTILE', 113.54, 22.20, 160),
    ('WEIHAIWEI', 'Weihaiwei', 'MINOR_CIV_CHN1928_WEIHAIWEI', 'MINOR_TRAIT_MARITIME', 122.12, 37.50, 25),
    ('INDOCHINA', 'Hanoi', 'MINOR_CIV_CHN1928_INDOCHINA', 'MINOR_TRAIT_MERCANTILE', 105.85, 21.03, 130),
]
NCS = len(CITY_STATES)
CSIDX = {c[0]: i for i, c in enumerate(CITY_STATES)}
# further towns of the city-states (the larger neighbours hold more than one city, so their land is not empty)
CS_TOWNS = [
    # Japan: the Kwantung Leased Territory, Korea, Taiwan, Kyushu
    ('Port Arthur', 121.25, 38.81, 'JAPAN', 25), ('Seoul', 126.98, 37.57, 'JAPAN', 355), ('Pyongyang', 125.75, 39.03, 'JAPAN', 140), ('Busan', 129.04, 35.10, 'JAPAN', 145),
    ('Daegu', 128.60, 35.87, 'JAPAN', 95), ('Sinuiju', 124.40, 40.10, 'JAPAN', 50), ('Wonsan', 127.44, 39.15, 'JAPAN', 45), ('Hamhung', 127.53, 39.92, 'JAPAN', 45),
    ('Chongjin', 129.78, 41.80, 'JAPAN', 35), ('Mokpo', 126.39, 34.79, 'JAPAN', 50), ('Gwangju', 126.85, 35.16, 'JAPAN', 45), ('Incheon', 126.63, 37.46, 'JAPAN', 70),
    ('Taipei', 121.52, 25.05, 'JAPAN', 250), ('Tainan', 120.20, 22.99, 'JAPAN', 90), ('Kaohsiung', 120.30, 22.62, 'JAPAN', 55), ('Taichung', 120.68, 24.14, 'JAPAN', 50),
    ('Keelung', 121.74, 25.13, 'JAPAN', 70), ('Hualien', 121.60, 23.98, 'JAPAN', 20), ('Fukuoka', 130.40, 33.59, 'JAPAN', 230), ('Nagasaki', 129.87, 32.75, 'JAPAN', 200),
    ('Kumamoto', 130.71, 32.80, 'JAPAN', 165), ('Kagoshima', 130.56, 31.60, 'JAPAN', 180), ('Shimonoseki', 130.94, 33.96, 'JAPAN', 100), ('Naha', 127.68, 26.21, 'JAPAN', 60),
    ('Miyazaki', 131.42, 31.91, 'JAPAN', 40), ('Oita', 131.61, 33.24, 'JAPAN', 60), ('Hiroshima', 132.46, 34.39, 'JAPAN', 270), ('Matsue', 133.05, 35.47, 'JAPAN', 40),
    # the Soviet Far East
    ('Khabarovsk', 135.07, 48.48, 'SOVIET', 50), ('Blagoveshchensk', 127.53, 50.26, 'SOVIET', 60), ('Nikolsk-Ussuriysky', 131.95, 43.80, 'SOVIET', 45), ('Iman', 133.73, 45.90, 'SOVIET', 10),
    ('Bikin', 134.27, 46.82, 'SOVIET', 8),
    # Mongolia
    ('Bayan Tumen', 114.53, 48.07, 'MONGOLIA', 4), ('Sainshand', 110.14, 44.89, 'MONGOLIA', 2), ('Mandalgovi', 106.27, 45.76, 'MONGOLIA', 2), ('Undurkhaan', 110.66, 47.32, 'MONGOLIA', 3),
    ('Dalanzadgad', 104.42, 43.57, 'MONGOLIA', 2), ('Arvaikheer', 102.78, 46.27, 'MONGOLIA', 2), ('Bulgan', 103.53, 48.81, 'MONGOLIA', 2), ('Baruun-Urt', 113.28, 46.68, 'MONGOLIA', 2),
    # Sichuan (Liu Wenhui, Deng Xihou, Tian Songyao) and Chongqing (Liu Xiang, Yang Sen)
    ('Leshan', 103.76, 29.55, 'SICHUAN', 50), ('Ya\'an', 103.00, 29.98, 'SICHUAN', 30), ('Mianyang', 104.73, 31.47, 'SICHUAN', 30), ('Zigong', 104.78, 29.35, 'SICHUAN', 200),
    ('Neijiang', 105.06, 29.58, 'SICHUAN', 50), ('Suining', 105.59, 30.53, 'SICHUAN', 40), ('Guangyuan', 105.84, 32.44, 'SICHUAN', 20), ('Kangding', 101.96, 30.05, 'SICHUAN', 20),
    ('Songpan', 103.60, 32.64, 'SICHUAN', 5), ('Xichang', 102.26, 27.89, 'SICHUAN', 20), ('Yibin', 104.63, 28.76, 'SICHUAN', 60),
    ('Wanxian', 108.39, 30.81, 'CHONGQING', 80), ('Luzhou', 105.44, 28.87, 'CHONGQING', 60), ('Fuling', 107.39, 29.70, 'CHONGQING', 40), ('Dazhou', 107.50, 31.21, 'CHONGQING', 30),
    ('Nanchong', 106.08, 30.80, 'CHONGQING', 60), ('Bazhong', 106.75, 31.86, 'CHONGQING', 20), ('Youyang', 108.77, 28.84, 'CHONGQING', 10),
    # Yunnan (Long Yun), Guizhou (Zhou Xicheng), Qinghai (Ma Qi and Ma Lin)
    ('Gejiu', 103.15, 23.36, 'YUNNAN', 50), ('Mengzi', 103.38, 23.36, 'YUNNAN', 20), ('Dali', 100.16, 25.69, 'YUNNAN', 40), ('Zhaotong', 103.72, 27.34, 'YUNNAN', 30),
    ('Qujing', 103.80, 25.49, 'YUNNAN', 20), ('Lijiang', 100.23, 26.87, 'YUNNAN', 20), ('Simao', 100.97, 22.79, 'YUNNAN', 10), ('Baoshan', 99.16, 25.11, 'YUNNAN', 20),
    ('Wenshan', 104.24, 23.37, 'YUNNAN', 10), ('Chuxiong', 101.55, 25.03, 'YUNNAN', 10),
    ('Zunyi', 106.93, 27.73, 'GUIZHOU', 50), ('Anshun', 105.93, 26.25, 'GUIZHOU', 40), ('Tongren', 109.19, 27.72, 'GUIZHOU', 20), ('Bijie', 105.29, 27.30, 'GUIZHOU', 30),
    ('Duyun', 107.52, 26.26, 'GUIZHOU', 20), ('Xingyi', 104.90, 25.09, 'GUIZHOU', 20), ('Zhenyuan', 108.43, 27.05, 'GUIZHOU', 10), ('Liping', 109.14, 26.23, 'GUIZHOU', 10),
    ('Linxia', 103.21, 35.60, 'QINGHAI', 50), ('Guide', 101.43, 36.04, 'QINGHAI', 5),
    # Guangdong (Li Jishen, then Chen Jitang)
    ('Shantou', 116.68, 23.35, 'GUANGDONG', 180), ('Chaozhou', 116.63, 23.66, 'GUANGDONG', 60), ('Meixian', 116.12, 24.29, 'GUANGDONG', 40), ('Shaoguan', 113.59, 24.80, 'GUANGDONG', 40),
    ('Huizhou', 114.42, 23.11, 'GUANGDONG', 50), ('Jiangmen', 113.08, 22.58, 'GUANGDONG', 70), ('Zhaoqing', 112.47, 23.05, 'GUANGDONG', 50), ('Gaozhou', 110.85, 21.92, 'GUANGDONG', 30),
    ('Beihai', 109.12, 21.48, 'GUANGDONG', 50), ('Qinzhou', 108.62, 21.95, 'GUANGDONG', 30), ('Heyuan', 114.70, 23.74, 'GUANGDONG', 20), ('Lianzhou', 112.38, 24.78, 'GUANGDONG', 15),
    ('Shanwei', 115.37, 22.79, 'GUANGDONG', 20), ('Yangjiang', 111.98, 21.86, 'GUANGDONG', 30), ('Foshan', 113.12, 23.02, 'GUANGDONG', 100),
    # French Indochina (Tonkin, northern Laos, Guangzhouwan)
    ('Haiphong', 106.68, 20.86, 'INDOCHINA', 120), ('Lang Son', 106.76, 21.85, 'INDOCHINA', 10), ('Lao Cai', 103.97, 22.49, 'INDOCHINA', 10), ('Cao Bang', 106.26, 22.67, 'INDOCHINA', 10),
    ('Fort-Bayard', 110.40, 21.20, 'INDOCHINA', 20), ('Nam Dinh', 106.17, 20.42, 'INDOCHINA', 50), ('Lai Chau', 103.15, 22.05, 'INDOCHINA', 3), ('Phongsaly', 102.10, 21.68, 'INDOCHINA', 3),
    ('Mong Cai', 107.97, 21.53, 'INDOCHINA', 8), ('Son La', 103.91, 21.33, 'INDOCHINA', 3), ('Hoa Binh', 105.34, 20.82, 'INDOCHINA', 5),
]
# Natural Earth first-level regions -> faction holding them on 10 October 1928 (the provinces split between holders are drawn below).
R_NAN = ['Jiangsu', 'Shanghai', 'Zhejiang', 'Anhui', 'Jiangxi', 'Fujian', 'Hunan', 'Shandong']
R_GMJ = ['Henan', 'Shaanxi', 'Gansu', 'Ningxia']
R_SHX = ['Shanxi', 'Hebei', 'Beijing', 'Tianjin', 'Inner Mongolia']
R_FT = ['Liaoning', 'Jilin', 'Heilongjiang']
R_GX = ['Guangxi', 'Hubei']
CS_REGION = {'Sichuan': 'SICHUAN', 'Chongqing': 'CHONGQING', 'Yunnan': 'YUNNAN', 'Guizhou': 'GUIZHOU', 'Guangdong': 'GUANGDONG', 'Hainan': 'GUANGDONG', 'Qinghai': 'QINGHAI'}
REGION_OF = {}
for lst, key in ((R_NAN, 'NAN'), (R_GMJ, 'GMJ'), (R_SHX, 'SHX'), (R_FT, 'FT'), (R_GX, 'GX')):
    for n in lst: REGION_OF[n] = key
CS_ADMIN = {'Japan': 'JAPAN', 'South Korea': 'JAPAN', 'North Korea': 'JAPAN', 'Taiwan': 'JAPAN', 'Russia': 'SOVIET', 'Mongolia': 'MONGOLIA',
            'Vietnam': 'INDOCHINA', 'Laos': 'INDOCHINA', 'Hong Kong S.A.R.': 'HONGKONG', 'Macau S.A.R': 'MACAU'}
def faction_code(f):
    p = f['properties']; adm = p.get('admin'); nm = p.get('name_en') or p.get('name')
    if adm == 'China':
        if nm in REGION_OF: return 1 + PIDX[REGION_OF[nm]]
        if nm in CS_REGION: return 100 + CSIDX[CS_REGION[nm]]
        return None   # Xinjiang, Tibet
    if adm in CS_ADMIN: return 100 + CSIDX[CS_ADMIN[adm]]
    return None       # Burma, Siam: outside the scenario
def code(k): return 1 + PIDX[k] if k in PIDX else 100 + CSIDX[k]
# The holders of October 1928 inside the modern provinces, as (polygon lon/lat, new holder, only over these holders or None).
OVERRIDES = [
    # Rehe (Tang Yulin) and the eastern Inner Mongolian leagues went with Fengtian; the Barga (Hulunbuir) belonged to Heilongjiang
    ([(116.3, 41.3), (117.0, 40.55), (118.0, 40.35), (119.2, 40.10), (121.0, 40.5), (127.0, 44.0), (127.0, 53.0), (114.0, 53.0), (115.5, 47.5), (119.3, 46.4),
      (119.5, 44.5), (117.5, 43.6), (116.0, 42.5)], 'FT', ['SHX']),
    # Alashan, part of the new province of Ningxia (1929) under the Guominjun
    ([(96.0, 37.0), (106.75, 37.0), (106.75, 39.3), (105.9, 40.4), (104.5, 42.5), (96.0, 43.5)], 'GMJ', ['SHX']),
    # western Shandong: Sun Liangcheng's Guominjun held the provincial seat; the Japanese occupied Jinan itself until May 1929
    ([(114.5, 34.2), (117.55, 34.2), (117.55, 38.5), (114.5, 38.5)], 'GMJ', ['NAN']),
    # the Kwantung Leased Territory (Japanese since 1905)
    ([(120.9, 38.6), (122.6, 38.6), (122.6, 39.42), (121.75, 39.55), (121.3, 39.45), (120.9, 39.1)], 'JAPAN', ['FT']),
    # Weihaiwei (British lease until 1 October 1930) and Guangzhouwan (French lease, Fort-Bayard)
    ([(121.85, 37.15), (122.7, 37.15), (122.7, 37.62), (121.85, 37.62)], 'WEIHAIWEI', ['NAN']),
    ([(110.05, 20.85), (110.75, 20.85), (110.75, 21.45), (110.05, 21.45)], 'INDOCHINA', ['GUANGDONG']),
    # eastern Sichuan: Liu Xiang's defence zone around Chongqing and down the Yangtze
    ([(105.25, 28.0), (110.5, 28.0), (110.5, 32.5), (106.3, 32.5), (105.9, 31.0), (105.25, 29.4)], 'CHONGQING', ['SICHUAN']),
    # the Jinggangshan base of Mao Zedong and Zhu De on the Hunan-Jiangxi border; Fang Zhimin's base in northeastern Jiangxi
    ([(113.75, 26.25), (114.45, 26.25), (114.45, 27.05), (113.75, 27.05)], 'CCP', ['NAN']),
    ([(117.15, 28.15), (117.75, 28.15), (117.75, 28.65), (117.15, 28.65)], 'CCP', ['NAN']),
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
        if max(lons) < LON_MIN - 12 or min(lons) > LON_MAX + 12 or max(lats) < LAT_MIN - 6 or min(lats) > LAT_MAX + 6: continue
        if max(lons) - min(lons) > 300: continue   # antimeridian-wrapping polygons (Russia's outline)
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

print('rasterizing land / lakes / regions...')
LAND = rasterize(json.load(open(f'{DATA}/ne_10m_land.geojson'))['features'], lambda f: 255) > 127
# natural lakes only: the reservoirs of Natural Earth (Danjiangkou, Xin'anjiang, Guanting, Fengman's Songhua Hu, Sup'ung) are later dams
def natural_lake(f):
    p = f['properties']
    if p.get('featurecla') == 'Reservoir' or p.get('name') in ('Songhua Hu',): return None
    return 255
LAKES = rasterize(json.load(open(f'{DATA}/ne_10m_lakes.geojson'))['features'], natural_lake) > 127
LAND = LAND & ~LAKES
admin1 = json.load(open(f'{DATA}/ne_10m_admin_1_states_provinces.geojson'))['features']
FACT = rasterize(admin1, faction_code)
for ll, k, only in OVERRIDES:
    m = poly_mask(ll)
    if only: m &= np.isin(FACT, [code(o) for o in only])
    FACT[m] = code(k)
seen_regions = {(f['properties'].get('name_en') or f['properties'].get('name')) for f in admin1 if f['properties'].get('admin') == 'China'}
missing = [n for n in list(REGION_OF) + list(CS_REGION) if n not in seen_regions]
if missing: print('  !! regions not found in Natural Earth:', missing)

print('loading ETOPO / Koppen...')
ETOPO = np.array(Image.open(f'{DATA}/etopo_cn.tif'))   # bbox 84..136 E, 17..52 N, 1040x700 -> 0.05 deg
def etopo_at(lon, lat):
    c = np.clip(((lon - 84.0) / 0.05).astype(int), 0, 1039); r = np.clip(((52.0 - lat) / 0.05).astype(int), 0, 699)
    return ETOPO[r, c]
KLAT0, KLON0, KN, KM = LAT_MIN - 4, LON_MIN - 6, int((LAT_MAX - LAT_MIN + 8) * 2) + 1, int((LON_MAX - LON_MIN + 12) * 2) + 1
kgrid = np.full((KN, KM), -1, int); kclasses = []
for line in open(f'{DATA}/koppen/Koeppen-Geiger-ASCII.txt'):
    p = line.split()
    if len(p) != 3 or p[0] == 'Lat': continue
    la, lo = float(p[0]), float(p[1])
    if KLAT0 <= la < LAT_MAX + 4 and KLON0 <= lo < LON_MAX + 6:
        if p[2] not in kclasses: kclasses.append(p[2])
        kgrid[int((la - KLAT0) * 2), int((lo - KLON0) * 2)] = kclasses.index(p[2])
idx = ndimage.distance_transform_edt(kgrid < 0, return_distances=False, return_indices=True)
kgrid = kgrid[idx[0], idx[1]]
def kop_at(lon, lat):
    return kclasses[kgrid[int(np.clip((lat - KLAT0) * 2, 0, KN - 1)), int(np.clip((lon - KLON0) * 2, 0, KM - 1))]]

CACHE = os.path.join(DATA, 'cache', f'china1928_sample_{W}x{H}.pkl'); os.makedirs(os.path.dirname(CACHE), exist_ok=True)
landfrac = np.zeros((H, W)); lakefrac = np.zeros((H, W)); emean = np.zeros((H, W)); emax = np.zeros((H, W))
relief = np.zeros((H, W)); depth = np.zeros((H, W)); fact = np.zeros((H, W), int); clim = [[None] * W for _ in range(H)]
if os.path.exists(CACHE) and not os.environ.get('CN_NOCACHE'):
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
          clim[y][x] = dict(comp)
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
# (lon0, lon1, lat0, lat1, marsh probability): the lake country of Hubei and Hunan, the Huai and Grand Canal lakes, the Sanjiang plain of the Amur and Ussuri,
# the Songnen plain, the Poyang shore, the Liao delta
MARSH_BOXES = [(111.8, 115.2, 29.2, 30.9, 0.40), (116.2, 120.0, 32.4, 34.5, 0.18), (130.0, 135.5, 46.0, 48.5, 0.35), (122.5, 125.5, 45.0, 47.5, 0.20),
               (115.8, 116.8, 28.5, 29.6, 0.30), (121.5, 122.5, 40.7, 41.3, 0.30)]
# (lon0, lon1, lat0, lat1, extra forest): the Greater and Lesser Khingan, the Changbai and eastern Manchurian mountains, the Wuyi and Nanling hills, western Hunan,
# the Qinling, southwestern Yunnan
FOREST_BOXES = [(119.5, 127.5, 47.0, 53.0, 0.45), (126.5, 131.5, 41.5, 48.5, 0.40), (123.5, 128.5, 40.5, 43.5, 0.30), (115.5, 120.5, 25.5, 28.8, 0.20),
                (109.5, 116.0, 24.0, 26.5, 0.15), (108.5, 111.5, 26.5, 30.5, 0.15), (105.5, 111.0, 32.8, 34.3, 0.20), (98.5, 102.0, 21.5, 26.5, 0.20)]
for y in range(H):
    for x in range(W):
        if is_lake[y, x]: terrain[y, x] = COAST; continue
        lo, la = lonlat(x, y)
        if not is_land[y, x]:
            shallow = depth[y, x] > -120 or any(is_land[b, a] for a, b in neighbors(x, y))
            terrain[y, x] = COAST if shallow else OCEAN
            continue
        rl, mx, mn = relief[y, x], emax[y, x], emean[y, x]
        if rl >= 960 or (mx >= 3500 and rl >= 700): elev[y, x] = 2
        elif rl >= 480 or (mn >= 1400 and rl >= 250): elev[y, x] = 1
        comp = clim[y][x]; tot = sum(comp.values()) or 1
        def frac(pred): return sum(v for k, v in comp.items() if pred(k)) / tot
        fTrop = frac(lambda k: k.startswith('A'))
        fCf = frac(lambda k: k.startswith('Cf') or k == 'Cwa')
        fCw = frac(lambda k: k in ('Cwb', 'Cwc'))
        fDw = frac(lambda k: k in ('Dwa', 'Dfa', 'Dsa'))
        fDb = frac(lambda k: k in ('Dwb', 'Dfb', 'Dsb'))
        fDc = frac(lambda k: k in ('Dwc', 'Dfc', 'Dwd', 'Dfd'))
        fBS = frac(lambda k: k.startswith('BS'))
        fBW = frac(lambda k: k.startswith('BW'))
        fET = frac(lambda k: k.startswith('E'))
        if mn >= 4300 or (fET > 0.6 and mn >= 3800): t = SNOW
        elif fET > 0.5 or (mn >= 3300 and fDc + fET > 0.3): t = TUNDRA
        else:
            wts = {GRASS: fTrop * 0.85 + fCf * 0.75 + fCw * 0.55 + fDw * 0.30 + fDb * 0.45 + fDc * 0.40 + fBS * 0.10,
                   PLAINS: fTrop * 0.15 + fCf * 0.25 + fCw * 0.45 + fDw * 0.70 + fDb * 0.55 + fDc * 0.40 + fBS * 0.70 + fBW * 0.15,
                   DESERT: fBS * 0.20 + fBW * 0.85, TUNDRA: fDc * 0.20 + fET * 0.5}
            r = rnd(x, y, 'terr'); sw = sum(wts.values()) or 1; acc = 0; t = PLAINS
            for k, v in wts.items():
                acc += v / sw
                if r < acc: t = k; break
        terrain[y, x] = t
        if elev[y, x] == 2 or t == SNOW: continue
        pf = fCf * 0.22 + fCw * 0.25 + fDb * 0.20 + fDc * 0.45 + fDw * 0.05 + fTrop * 0.15 + (0.12 if elev[y, x] == 1 else 0)
        for lo0, lo1, la0, la1, pfb in FOREST_BOXES:
            if lo0 <= lo <= lo1 and la0 <= la <= la1: pf += pfb
        if t == DESERT: pf = 0
        pj = fTrop * 0.45 if t in (GRASS, PLAINS) else 0   # Hainan Strait, Tonkin, the Leizhou peninsula, southern Taiwan: jungle
        pm = 0
        for lo0, lo1, la0, la1, pmb in MARSH_BOXES:
            if lo0 <= lo <= lo1 and la0 <= la <= la1 and elev[y, x] == 0 and t in (GRASS, PLAINS, TUNDRA): pm = pmb
        r2 = rnd(x, y, 'feat')
        if r2 < pm: feature[y, x] = MARSH
        elif r2 < pm + pj: feature[y, x] = JUNGLE
        elif r2 < pm + pj + pf: feature[y, x] = FOREST
        elif t == DESERT and elev[y, x] == 0 and r2 > 0.97: feature[y, x] = OASIS
if os.environ.get('CN_TERRAIN_ONLY'):
    land_n = int(is_land.sum()); print(f'grid {W}x{H} land {land_n} mountains {int((elev==2).sum())} hills {int((elev==1).sum())} forest {int((feature==FOREST).sum())} jungle {int((feature==JUNGLE).sum())} marsh {int((feature==MARSH).sum())} tundra {int((terrain==TUNDRA).sum())} snow {int((terrain==SNOW).sum())} desert {int((terrain==DESERT).sum())} grass {int(((terrain==GRASS)&is_land).sum())} plains {int(((terrain==PLAINS)&is_land).sum())} lakes {int(is_lake.sum())}')
    S = 8; img = Image.new('RGB', (W * S + S, int(H * S * 0.866) + S)); d = ImageDraw.Draw(img)
    TC = {GRASS: (96, 168, 64), PLAINS: (196, 178, 96), DESERT: (236, 214, 150), TUNDRA: (170, 170, 150), SNOW: (240, 240, 240), COAST: (70, 140, 210), OCEAN: (20, 60, 130)}
    FC = {(0, 0, 0)}
    for y in range(H):
        for x in range(W):
            col = TC[terrain[y, x]]
            if feature[y, x] == FOREST: col = tuple(int(c * 0.6) for c in col)
            if feature[y, x] == JUNGLE: col = (20, 90, 30)
            if feature[y, x] == MARSH: col = (80, 150, 130)
            if elev[y, x] == 2: col = (90, 70, 60)
            elif elev[y, x] == 1: col = tuple(int(c * 0.8) for c in col)
            f = fact[y, x]; cx = (x + 0.5 * (y & 1)) * S; cy = (H - 1 - y) * S * 0.866
            d.rectangle([cx, cy, cx + S - 1, cy + S * 0.866], fill=col)
            if is_land[y, x] and f and any(fact[b, a] != f and is_land[b, a] for a, b in neighbors(x, y)): d.rectangle([cx + 3, cy + 2, cx + 4, cy + 3], fill=(255, 0, 0))
    img.save(os.environ['CN_TERRAIN_ONLY']); raise SystemExit

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
for f in json.load(open(f'{DATA}/ne_10m_rivers_lake_centerlines.geojson'))['features']:
    p = f['properties']; nm = p.get('name') or ''
    if 'Canal' in nm or 'canal' in nm or p.get('featurecla') == 'Lake Centerline': continue   # the Grand Canal is no river
    if (p.get('scalerank') or 99) > 7 or f['geometry'] is None: continue
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
for y in range(H):   # flood plains on dry river banks (the Yellow River through the Ordos loop and the Hetao)
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
        if water: return not is_land[y, x] and not is_lake[y, x]
        return is_land[y, x] and elev[y, x] != 2 and feature[y, x] != MARSH and terrain[y, x] != SNOW
    t = find_tile(lon, lat, ok, 2)
    if t is None: print('  !! no tile for', res, lon, lat); return
    resource[t[1], t[0]] = RID[res]; resamt[t[1], t[0]] = amt
    if res in ('IRON', 'COAL', 'GOLD', 'SILVER', 'GEMS', 'COPPER') and elev[t[1], t[0]] == 0 and rnd(*t, 'hill') < 0.6: elev[t[1], t[0]] = 1
    if res in ('WHEAT', 'HORSE', 'COW', 'COTTON', 'CITRUS', 'WINE') and feature[t[1], t[0]] in (FOREST, MARSH): feature[t[1], t[0]] = NONE
HAND_RES = [
    # coal: Fushun, Benxi, Yantai (Liaoning), Kailuan (Tangshan), Mentougou, Jingxing, Yangquan, Datong, Taiyuan's Xishan, Jiaozuo, Liuhegou, Boshan and Zichuan,
    # Zaozhuang, Huainan, Pingxiang, Fengfeng, Mu-Leng and Hegang, Sakhalin's mainland opposite (none), Pyongyang's anthracite
    ('COAL', 123.90, 41.85, 6), ('COAL', 123.75, 41.30, 4), ('COAL', 118.18, 39.63, 6), ('COAL', 116.10, 39.94, 2), ('COAL', 114.00, 38.03, 2), ('COAL', 113.58, 37.86, 4),
    ('COAL', 113.15, 40.08, 4), ('COAL', 112.45, 37.85, 2), ('COAL', 113.24, 35.24, 4), ('COAL', 117.93, 36.48, 4), ('COAL', 117.55, 34.85, 2), ('COAL', 116.99, 32.63, 2),
    ('COAL', 113.85, 27.62, 4), ('COAL', 114.21, 36.42, 2), ('COAL', 130.30, 47.35, 2), ('COAL', 125.90, 39.20, 2), ('COAL', 110.95, 35.10, 2), ('COAL', 105.80, 39.10, 2),
    # iron: Anshan and Benxi (Japanese-run), Longyan near Xuanhua, Daye of the Hanyeping company, Ma'anshan, Musan in Korea, Kyushu's Yawata works
    ('IRON', 122.99, 41.11, 6), ('IRON', 123.80, 41.40, 2), ('IRON', 115.05, 40.60, 2), ('IRON', 114.98, 30.10, 4), ('IRON', 118.50, 31.70, 2), ('IRON', 129.20, 42.25, 2),
    ('IRON', 130.80, 33.87, 2), ('IRON', 112.50, 37.85, 2),
    # oil: the Yanchang wells in northern Shaanxi and the Fushun oil shale; the rest is imported fuel (the depots below)
    ('OIL', 110.00, 36.60, 2), ('OIL', 123.95, 41.88, 2),
    # horses: the Mongol banners, the Barga, Ningxia and Qinghai, the Hetao, the Horqin, Xilingol
    ('HORSE', 119.70, 49.20, 4), ('HORSE', 122.20, 45.50, 2), ('HORSE', 106.20, 38.60, 2), ('HORSE', 101.70, 36.70, 4), ('HORSE', 108.00, 40.80, 2), ('HORSE', 115.50, 43.50, 2),
    ('HORSE', 103.20, 35.70, 2), ('HORSE', 111.80, 40.80, 2), ('HORSE', 124.10, 47.30, 2), ('HORSE', 106.90, 47.50, 4),
    # tin of Gejiu as copper, copper of Dongchuan, gold of the Amur and Jiapigou, silver and lead of Hunan, antimony of Xikuangshan as silver, Yunnan's jade as gems
    ('COPPER', 103.15, 23.36, 1), ('COPPER', 103.10, 26.10, 1), ('GOLD', 127.00, 50.00, 1), ('GOLD', 127.30, 42.90, 1), ('GOLD', 125.40, 39.70, 1), ('SILVER', 111.48, 27.75, 1),
    ('SILVER', 113.00, 25.80, 1), ('GEMS', 99.50, 24.80, 1), ('GOLD', 117.20, 41.00, 1),
    # salt: Zigong's brine wells, the Changlu and Huaibei pans, the Lianghuai coast, Jilantai in Alashan, Yuncheng's salt lake
    ('SALT', 104.78, 29.35, 1), ('SALT', 117.70, 38.90, 1), ('SALT', 119.60, 34.30, 1), ('SALT', 120.50, 32.90, 1), ('SALT', 105.70, 39.75, 1), ('SALT', 110.98, 35.03, 1),
    # marble of Dali, stone of Quyang and Fangshan
    ('MARBLE', 100.16, 25.80, 1), ('STONE', 114.70, 38.60, 1), ('STONE', 116.00, 39.70, 1), ('STONE', 119.30, 26.10, 1),
    # silk: Huzhou, Wuxi, Suzhou, Hangzhou, the Pearl delta (Shunde), Nanchong and Leshan, Shandong's tussah
    ('SILK', 120.09, 30.87, 1), ('SILK', 120.30, 31.57, 1), ('SILK', 120.60, 31.30, 1), ('SILK', 120.15, 30.40, 1), ('SILK', 113.25, 22.84, 1), ('SILK', 106.08, 30.80, 1),
    ('SILK', 103.76, 29.55, 1), ('SILK', 121.40, 36.90, 1),
    # cotton: Nantong, the Hebei and Henan plains, Shandong, Hubei's Jianghan plain, Shaanxi's Guanzhong
    ('COTTON', 120.86, 32.01, 1), ('COTTON', 115.00, 37.50, 1), ('COTTON', 114.40, 35.80, 1), ('COTTON', 116.30, 36.80, 1), ('COTTON', 113.00, 30.40, 1), ('COTTON', 108.80, 34.40, 1),
    ('COTTON', 121.30, 31.00, 1),
    # sugar of Taiwan and Guangdong, citrus of Huangyan, Fujian and Guangdong, more cane in Taiwan, Leizhou and Tonkin, Yantai's grapes, Hepu's pearls
    ('SUGAR', 120.40, 23.30, 1), ('SUGAR', 116.60, 23.40, 1), ('SUGAR', 113.30, 22.70, 1), ('CITRUS', 121.26, 28.64, 1), ('CITRUS', 117.65, 24.51, 1), ('CITRUS', 116.10, 24.30, 1),
    ('CITRUS', 112.10, 26.90, 1), ('SUGAR', 120.60, 22.70, 1), ('SUGAR', 110.30, 21.00, 1), ('SUGAR', 106.40, 21.20, 1), ('WINE', 121.40, 37.50, 1), ('PEARLS', 109.30, 21.40, 1, ),
    # tea and the tung-oil and lacquer of the hills as spices and dye: Anhui's Qimen and Huangshan, Hangzhou's Longjing, Wuyi, Hunan's Anhua, Yunnan's Pu'er; indigo of Jiangxi
    ('SPICES', 117.70, 29.90, 1), ('SPICES', 120.10, 30.25, 1), ('SPICES', 118.00, 27.70, 1), ('SPICES', 111.20, 28.40, 1), ('SPICES', 100.97, 22.79, 1), ('SPICES', 103.00, 29.98, 1),
    ('DYE', 115.80, 28.20, 1), ('DYE', 109.50, 28.30, 1), ('DYE', 106.90, 27.10, 1),
    # furs and ginseng of Manchuria (fur), deer of the Khingan
    ('FUR', 128.50, 47.00, 1), ('FUR', 122.50, 50.00, 1), ('FUR', 127.50, 42.20, 1), ('DEER', 120.80, 47.50, 1),
    # sea: the Zhoushan fishing grounds, the Bohai, the Yellow Sea banks, the Taiwan Strait, the Gulf of Tonkin
    ('FISH', 122.20, 30.00, 1), ('FISH', 122.60, 30.70, 1), ('FISH', 119.50, 38.80, 1), ('FISH', 121.30, 38.20, 1), ('FISH', 122.80, 36.80, 1), ('FISH', 119.90, 35.30, 1),
    ('FISH', 119.70, 25.50, 1), ('FISH', 118.20, 24.30, 1), ('FISH', 116.90, 23.10, 1), ('FISH', 114.60, 22.40, 1), ('FISH', 108.80, 21.20, 1), ('FISH', 121.90, 28.00, 1),
    ('FISH', 120.80, 32.50, 1), ('FISH', 126.20, 34.40, 1), ('FISH', 129.50, 35.70, 1), ('CRAB', 121.60, 31.50, 1), ('WHALE', 129.80, 37.50, 1),
]
for res, lo, la, amt in HAND_RES: place_res(res, lo, la, amt, water=res in ('FISH', 'CRAB', 'PEARLS', 'WHALE'))
for y in range(H):
    for x in range(W):
        if resource[y, x] != NONE or is_lake[y, x]: continue
        r = rnd(x, y, 'scatter'); lo, la = lonlat(x, y)
        if is_land[y, x]:
            if elev[y, x] == 2 or terrain[y, x] == SNOW: continue
            t, f = terrain[y, x], feature[y, x]
            north_plain = t in (GRASS, PLAINS) and 32.0 < la < 40.5 and 112.0 < lo < 121.0   # the wheat and millet of the North China Plain
            manchuria = t in (GRASS, PLAINS) and la > 41.0 and lo > 121.0                      # soybeans and kaoliang of Manchuria
            if f == FOREST and r < 0.06: resource[y, x] = RID['DEER']; resamt[y, x] = 1
            elif f == NONE and (north_plain or manchuria) and elev[y, x] == 0 and r < 0.10: resource[y, x] = RID['WHEAT']; resamt[y, x] = 1
            elif f == NONE and t in (GRASS, PLAINS) and elev[y, x] == 0 and r < 0.04: resource[y, x] = RID['WHEAT']; resamt[y, x] = 1
            elif f == NONE and t == GRASS and la < 32 and r < 0.08: resource[y, x] = RID['COW']; resamt[y, x] = 1          # water buffalo
            elif f == NONE and t in (PLAINS, DESERT) and la > 36 and lo < 116 and r < 0.10: resource[y, x] = RID['SHEEP']; resamt[y, x] = 1
            elif f == NONE and elev[y, x] == 1 and t != DESERT and r < 0.07: resource[y, x] = RID['SHEEP']; resamt[y, x] = 1
            elif f in (NONE, FOREST) and 0.95 < r < 0.957: resource[y, x] = RID['STONE']; resamt[y, x] = 1
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
# (name, lon, lat, owner, population in thousands around 1928-1931, rounded; tags: cap base port)
CITIES = [
    # --- the National Government: Jiangsu, Zhejiang, Anhui, Jiangxi, Fujian, Hunan, eastern Shandong
    ('Nanjing', 118.78, 32.06, NAN, 500, 'cap base'), ('Shanghai', 121.47, 31.23, NAN, 3100, 'base port'), ('Suzhou', 120.62, 31.30, NAN, 260, ''), ('Wuxi', 120.30, 31.57, NAN, 180, ''),
    ('Changzhou', 119.95, 31.78, NAN, 125, ''), ('Zhenjiang', 119.45, 32.20, NAN, 200, ''), ('Yangzhou', 119.42, 32.39, NAN, 125, ''), ('Nantong', 120.86, 32.01, NAN, 150, 'port'),
    ('Xuzhou', 117.18, 34.26, NAN, 160, 'base'), ('Haizhou', 119.17, 34.60, NAN, 40, 'port'), ('Huaiyin', 119.02, 33.60, NAN, 60, ''), ('Yancheng', 120.15, 33.38, NAN, 50, ''),
    ('Hangzhou', 120.16, 30.27, NAN, 500, 'base'), ('Ningbo', 121.55, 29.87, NAN, 220, 'port'), ('Shaoxing', 120.58, 30.00, NAN, 150, ''), ('Jiaxing', 120.75, 30.75, NAN, 60, ''),
    ('Huzhou', 120.09, 30.87, NAN, 70, ''), ('Wenzhou', 120.70, 28.00, NAN, 160, 'port'), ('Jinhua', 119.65, 29.08, NAN, 40, ''), ('Quzhou', 118.87, 28.94, NAN, 30, ''),
    ('Linhai', 121.13, 28.85, NAN, 40, 'port'), ('Lishui', 119.92, 28.45, NAN, 20, ''), ('Anqing', 117.05, 30.53, NAN, 120, ''), ('Wuhu', 118.38, 31.33, NAN, 140, ''),
    ('Bengbu', 117.39, 32.92, NAN, 100, ''), ('Hefei', 117.28, 31.86, NAN, 70, ''), ('Bozhou', 115.78, 33.85, NAN, 60, ''), ('Lu\'an', 116.51, 31.73, NAN, 40, ''),
    ('Tunxi', 118.33, 29.71, NAN, 30, ''), ('Fuyang', 115.81, 32.89, NAN, 40, ''), ('Nanchang', 115.86, 28.68, NAN, 280, 'base'), ('Jiujiang', 116.00, 29.71, NAN, 70, ''),
    ('Ji\'an', 114.99, 27.11, NAN, 60, ''), ('Ganzhou', 114.93, 25.83, NAN, 70, ''), ('Ruijin', 116.03, 25.89, NAN, 20, ''), ('Ningdu', 116.01, 26.47, NAN, 15, ''),
    ('Linchuan', 116.36, 27.95, NAN, 60, ''), ('Shangrao', 117.97, 28.45, NAN, 40, ''), ('Jingdezhen', 117.18, 29.27, NAN, 90, ''), ('Pingxiang', 113.85, 27.62, NAN, 50, ''),
    ('Yuanzhou', 114.38, 27.80, NAN, 30, ''), ('Fuzhou', 119.30, 26.08, NAN, 320, 'base port'), ('Xiamen', 118.09, 24.48, NAN, 160, 'port'), ('Quanzhou', 118.59, 24.91, NAN, 100, 'port'),
    ('Zhangzhou', 117.65, 24.51, NAN, 90, ''), ('Nanping', 118.18, 26.64, NAN, 30, ''), ('Changting', 116.36, 25.84, NAN, 30, ''), ('Longyan', 117.03, 25.08, NAN, 25, ''),
    ('Jian\'ou', 118.32, 27.04, NAN, 40, ''), ('Funing', 119.53, 26.66, NAN, 20, 'port'), ('Changsha', 112.94, 28.23, NAN, 400, 'base'), ('Hengyang', 112.57, 26.89, NAN, 100, ''),
    ('Yueyang', 113.13, 29.37, NAN, 50, ''), ('Changde', 111.69, 29.03, NAN, 100, ''), ('Shaoyang', 111.47, 27.24, NAN, 80, ''), ('Xiangtan', 112.94, 27.83, NAN, 80, ''),
    ('Chenzhou', 113.01, 25.77, NAN, 40, ''), ('Hongjiang', 109.99, 27.11, NAN, 30, ''), ('Yuanling', 110.39, 28.45, NAN, 30, ''), ('Sangzhi', 110.16, 29.40, NAN, 5, ''),
    ('Yongzhou', 111.61, 26.42, NAN, 30, ''), ('Yiyang', 112.36, 28.55, NAN, 40, ''), ('Liling', 113.49, 27.65, NAN, 20, ''), ('Qingdao', 120.38, 36.07, NAN, 390, 'base port'),
    ('Yantai', 121.39, 37.54, NAN, 130, 'port'), ('Weixian', 119.10, 36.70, NAN, 100, ''), ('Linyi', 118.35, 35.05, NAN, 40, ''), ('Rizhao', 119.46, 35.42, NAN, 20, 'port'),
    ('Laiyang', 120.71, 36.98, NAN, 30, ''), ('Yizhou', 117.95, 36.30, NAN, 30, ''),
    # --- the Guominjun of Feng Yuxiang: Henan, Shaanxi, Gansu, Ningxia, western Shandong
    ('Kaifeng', 114.31, 34.80, GMJ, 280, 'cap base'), ('Zhengzhou', 113.65, 34.76, GMJ, 100, 'base'), ('Luoyang', 112.45, 34.62, GMJ, 70, ''), ('Xinyang', 114.07, 32.13, GMJ, 40, ''),
    ('Nanyang', 112.53, 33.00, GMJ, 50, ''), ('Xuchang', 113.82, 34.03, GMJ, 50, ''), ('Zhoukou', 114.65, 33.63, GMJ, 50, ''), ('Shangqiu', 115.65, 34.44, GMJ, 60, ''),
    ('Anyang', 114.39, 36.10, GMJ, 50, ''), ('Xinxiang', 113.93, 35.30, GMJ, 40, ''), ('Luohe', 114.02, 33.58, GMJ, 30, ''), ('Lingbao', 110.89, 34.52, GMJ, 15, ''),
    ('Jiaozuo', 113.24, 35.24, GMJ, 30, ''), ('Runan', 114.36, 33.01, GMJ, 30, ''), ('Xi\'an', 108.94, 34.34, GMJ, 300, 'base'), ('Tongguan', 110.25, 34.54, GMJ, 20, ''),
    ('Baoji', 107.14, 34.36, GMJ, 30, ''), ('Hanzhong', 107.02, 33.07, GMJ, 60, ''), ('Yan\'an', 109.49, 36.59, GMJ, 10, ''), ('Yulin', 109.73, 38.28, GMJ, 30, ''),
    ('Sanyuan', 108.94, 34.61, GMJ, 30, ''), ('Ankang', 109.03, 32.68, GMJ, 40, ''), ('Shangzhou', 109.94, 33.87, GMJ, 15, ''), ('Suide', 110.26, 37.50, GMJ, 15, ''),
    ('Lanzhou', 103.83, 36.06, GMJ, 120, 'base'), ('Tianshui', 105.72, 34.58, GMJ, 60, ''), ('Pingliang', 106.67, 35.54, GMJ, 40, ''), ('Wuwei', 102.64, 37.93, GMJ, 50, ''),
    ('Zhangye', 100.45, 38.93, GMJ, 40, ''), ('Qingyang', 107.64, 35.71, GMJ, 15, ''), ('Wudu', 104.92, 33.39, GMJ, 15, ''), ('Ningxia', 106.27, 38.47, GMJ, 50, ''),
    ('Guyuan', 106.28, 36.01, GMJ, 20, ''), ('Wuzhong', 106.20, 37.99, GMJ, 15, ''), ('Jinan', 117.00, 36.67, GMJ, 400, 'base'), ('Tai\'an', 117.09, 36.20, GMJ, 60, ''),
    ('Jining', 116.59, 35.41, GMJ, 120, ''), ('Dezhou', 116.30, 37.45, GMJ, 50, ''), ('Linqing', 115.70, 36.84, GMJ, 50, ''), ('Heze', 115.48, 35.25, GMJ, 50, ''),
    ('Liaocheng', 115.98, 36.46, GMJ, 30, ''), ('Yanzhou', 116.83, 35.55, GMJ, 30, ''),
    # --- Yan Xishan: Shanxi, Hebei with Beiping and Tianjin, Chahar and Suiyuan
    ('Taiyuan', 112.55, 37.87, SHX, 140, 'cap base'), ('Datong', 113.30, 40.08, SHX, 80, 'base'), ('Linfen', 111.52, 36.09, SHX, 50, ''), ('Yuncheng', 111.00, 35.03, SHX, 30, ''),
    ('Changzhi', 113.12, 36.20, SHX, 40, ''), ('Fenyang', 111.79, 37.27, SHX, 40, ''), ('Xinzhou', 112.73, 38.42, SHX, 30, ''), ('Jincheng', 112.85, 35.49, SHX, 30, ''),
    ('Lishi', 111.14, 37.52, SHX, 20, ''), ('Shuozhou', 112.43, 39.33, SHX, 20, ''), ('Yangquan', 113.58, 37.86, SHX, 40, ''), ('Puzhou', 110.32, 34.84, SHX, 20, ''),
    ('Beiping', 116.40, 39.90, SHX, 1370, 'base'), ('Tianjin', 117.20, 39.13, SHX, 1390, 'base port'), ('Baoding', 115.46, 38.87, SHX, 100, ''), ('Shijiazhuang', 114.51, 38.04, SHX, 60, ''),
    ('Shunde', 114.50, 37.07, SHX, 50, ''), ('Handan', 114.49, 36.61, SHX, 30, ''), ('Daming', 115.15, 36.28, SHX, 40, ''), ('Cangzhou', 116.84, 38.30, SHX, 40, ''),
    ('Tangshan', 118.18, 39.63, SHX, 150, ''), ('Shanhaiguan', 119.75, 40.00, SHX, 30, ''), ('Qinhuangdao', 119.60, 39.93, SHX, 30, 'port'), ('Hejian', 116.10, 38.44, SHX, 30, ''),
    ('Tongzhou', 116.66, 39.91, SHX, 40, ''), ('Zhuozhou', 115.97, 39.49, SHX, 20, ''), ('Zhengding', 114.57, 38.15, SHX, 20, ''), ('Zhangjiakou', 114.88, 40.82, SHX, 80, 'base'),
    ('Xuanhua', 115.06, 40.61, SHX, 30, ''), ('Duolun', 116.48, 42.20, SHX, 20, ''), ('Zhangbei', 114.70, 41.16, SHX, 10, ''), ('Guisui', 111.67, 40.82, SHX, 100, 'base'),
    ('Baotou', 109.84, 40.66, SHX, 70, ''), ('Fengzhen', 113.15, 40.44, SHX, 20, ''), ('Wuyuan', 108.27, 41.09, SHX, 10, ''), ('Pingdiquan', 113.12, 41.03, SHX, 10, ''),
    ('Dongsheng', 109.98, 39.82, SHX, 5, ''), ('Bailingmiao', 110.43, 41.70, SHX, 2, ''), ('Pangjiang', 113.70, 42.55, SHX, 2, ''),
    # --- the Fengtian clique of Zhang Xueliang: the Three Eastern Provinces, Rehe and the eastern Mongol leagues
    ('Mukden', 123.43, 41.80, FT, 420, 'cap base'), ('Harbin', 126.63, 45.75, FT, 330, 'base'), ('Changchun', 125.32, 43.88, FT, 130, 'base'), ('Jilin', 126.55, 43.84, FT, 130, ''),
    ('Qiqihar', 123.92, 47.35, FT, 70, 'base'), ('Hailar', 119.74, 49.21, FT, 20, ''), ('Manzhouli', 117.43, 49.60, FT, 10, ''), ('Heihe', 127.50, 50.24, FT, 20, ''),
    ('Jiamusi', 130.36, 46.80, FT, 30, ''), ('Yilan', 129.56, 46.32, FT, 20, ''), ('Ningguta', 129.45, 44.35, FT, 20, ''), ('Suifenhe', 131.15, 44.40, FT, 10, ''),
    ('Yanji', 129.51, 42.89, FT, 30, ''), ('Tonghua', 125.94, 41.73, FT, 30, ''), ('Andong', 124.38, 40.13, FT, 130, 'port'), ('Yingkou', 122.23, 40.67, FT, 150, 'port'),
    ('Jinzhou', 121.13, 41.10, FT, 80, 'base'), ('Fushun', 123.90, 41.88, FT, 180, ''), ('Anshan', 122.99, 41.11, FT, 60, ''), ('Liaoyang', 123.17, 41.27, FT, 70, ''),
    ('Tieling', 123.84, 42.29, FT, 40, ''), ('Siping', 124.37, 43.17, FT, 40, ''), ('Taonan', 122.79, 45.33, FT, 30, ''), ('Liaoyuan', 125.14, 42.89, FT, 40, ''),
    ('Huludao', 120.84, 40.71, FT, 10, 'port'), ('Chengde', 117.94, 40.95, FT, 30, ''), ('Chifeng', 118.89, 42.26, FT, 50, ''), ('Tongliao', 122.24, 43.62, FT, 30, ''),
    ('Chaoyang', 120.45, 41.57, FT, 30, ''), ('Fuxin', 121.65, 42.01, FT, 20, ''), ('Hailun', 126.93, 47.46, FT, 30, ''), ('Bei\'an', 126.48, 48.24, FT, 20, ''),
    ('Fujin', 132.04, 47.25, FT, 15, ''), ('Mudanjiang', 129.62, 44.58, FT, 10, ''), ('Zhalantun', 122.72, 48.00, FT, 5, ''), ('Lingyuan', 119.40, 41.24, FT, 20, ''),
    ('Ulanhot', 122.08, 46.08, FT, 10, ''), ('Benxi', 123.77, 41.29, FT, 40, ''), ('Zhuanghe', 122.97, 39.70, FT, 20, 'port'), ('Dunhua', 128.23, 43.37, FT, 20, ''),
    ('Hunchun', 130.37, 42.87, FT, 10, ''), ('Linjiang', 126.92, 41.81, FT, 10, ''), ('Keshan', 125.87, 48.04, FT, 15, ''), ('Shuangcheng', 126.31, 45.38, FT, 30, ''),
    # --- the New Guangxi clique: Guangxi, and Hubei under the Wuhan Political Council
    ('Nanning', 108.37, 22.82, GX, 70, 'cap base'), ('Guilin', 110.29, 25.27, GX, 100, 'base'), ('Wuzhou', 111.28, 23.48, GX, 80, ''), ('Liuzhou', 109.41, 24.33, GX, 60, ''),
    ('Baise', 106.62, 23.90, GX, 20, ''), ('Longzhou', 106.85, 22.34, GX, 15, ''), ('Pingle', 110.64, 24.63, GX, 20, ''),
    ('Hechi', 108.06, 24.70, GX, 15, ''), ('Guiping', 110.08, 23.39, GX, 40, ''), ('Hezhou', 111.57, 24.41, GX, 20, ''), 
    ('Hankou', 114.27, 30.58, GX, 1000, 'base port'), ('Yichang', 111.29, 30.70, GX, 100, ''), ('Shashi', 112.24, 30.32, GX, 100, ''), ('Xiangyang', 112.14, 32.04, GX, 60, ''),
    ('Laohekou', 111.67, 32.39, GX, 50, ''), ('Macheng', 115.02, 31.17, GX, 30, ''), ('Suizhou', 113.37, 31.69, GX, 30, ''), ('Yunyang', 110.80, 32.83, GX, 20, ''),
    ('Enshi', 109.49, 30.27, GX, 20, ''), ('Daye', 114.98, 30.10, GX, 40, ''), ('Xiaogan', 113.92, 30.92, GX, 30, ''), ('Huangzhou', 114.87, 30.45, GX, 30, ''),
    ('Jingmen', 112.20, 31.03, GX, 30, ''), ('Honghu', 113.47, 29.82, GX, 20, ''), ('Puqi', 113.88, 29.72, GX, 20, ''),
    # --- the Chinese Communists: the Jinggangshan base and Fang Zhimin's base in northeastern Jiangxi
    ('Jinggangshan', 114.17, 26.57, CCP, 8, 'cap'), ('Hengfeng', 117.60, 28.42, CCP, 10, ''),
]
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES): CITIES.append((name, lo, la, 32 + i, popk, 'cap'))
for name, lo, la, key, popk in CS_TOWNS: CITIES.append((name, lo, la, 32 + CSIDX[key], popk, ''))
# Thin the city list: no two cities closer than 3 hexes, whoever holds them; two cities of one side at least 4 hexes apart unless both are key towns
# (capitals and the KEEP towns below), which may stand 3 apart. Where cities collide the more important one stays (a capital, then a city-state
# capital, then a key town, then the bigger town) and the other merges into it: its population joins the nearest kept city of its owner.
MIN_SPACING = 3          # between any two cities (about 110 km), and between two key towns of the same side
MIN_SPACING_SIDE = 4     # between two cities of the same side when one of them is a minor town
# The one deliberate exception: Hong Kong and Macau, two colonies 60 km apart across the Pearl River estuary, both kept on purpose as city-states.
# They may stand SPACING_EXCEPTION_GAP hexes apart (never adjacent); the thinning, the placement and the final check all honour it.
SPACING_EXCEPTIONS = {frozenset({'Hong Kong', 'Macau'})}
SPACING_EXCEPTION_GAP = 2
# every city the events name, plus the towns the history turns on
KEEP = {'Nanjing', 'Shanghai', 'Suzhou', 'Hangzhou', 'Xuzhou', 'Nanchang', 'Ruijin', 'Ningdu', 'Changting', 'Ganzhou', 'Ji\'an', 'Fuzhou', 'Xiamen', 'Changsha', 'Hengyang', 'Pingxiang',
        'Qingdao', 'Bengbu', 'Anqing', 'Wuhu', 'Kaifeng', 'Zhengzhou', 'Luoyang', 'Xi\'an', 'Lanzhou', 'Tongguan', 'Yan\'an', 'Jinan', 'Shangqiu', 'Xinyang', 'Taiyuan', 'Datong',
        'Beiping', 'Tianjin', 'Baoding', 'Shijiazhuang', 'Zhangjiakou', 'Guisui', 'Baotou', 'Shanhaiguan', 'Tangshan', 'Duolun', 'Bailingmiao', 'Mukden', 'Harbin', 'Changchun',
        'Jilin', 'Qiqihar', 'Manzhouli', 'Hailar', 'Jinzhou', 'Chengde', 'Andong', 'Yingkou', 'Fujin', 'Heihe', 'Suifenhe', 'Nanning', 'Guilin', 'Wuzhou', 'Liuzhou', 'Hankou',
        'Yichang', 'Xiangyang', 'Honghu', 'Jinggangshan', 'Hengfeng', 'Sangzhi', 'Zunyi', 'Dairen', 'Port Arthur', 'Seoul', 'Sinuiju', 'Taipei', 'Fukuoka', 'Vladivostok',
        'Blagoveshchensk', 'Ulan Bator', 'Chengdu', 'Chongqing', 'Kunming', 'Guiyang', 'Canton', 'Xining', 'Hong Kong', 'Macau', 'Weihaiwei', 'Hanoi', 'Fort-Bayard', 'Shantou',
        'Kangding', 'Lingbao', 'Yulin', 'Lishi', 'Linfen', 'Fenyang', 'Wuyuan', 'Zhangye', 'Ningxia', 'Tianshui', 'Linchuan', 'Lu\'an', 'Macheng', 'Yanji', 'Jiamusi', 'Shaoguan',
        'Linxia', 'Hanzhong', 'Guangyuan', 'Wanxian', 'Luzhou', 'Yibin', 'Daye', 'Changde', 'Yueyang', 'Haiphong', 'Busan', 'Pyongyang', 'Khabarovsk', 'Nikolsk-Ussuriysky'}
IMPORTANT = ['Suzhou', 'Wuxi', 'Ningbo', 'Wenzhou', 'Jiujiang', 'Jingdezhen', 'Quanzhou', 'Zhangzhou', 'Shaoyang', 'Xiangtan', 'Yantai', 'Weixian', 'Nanyang', 'Xuchang', 'Anyang',
             'Xinxiang', 'Baoji', 'Jining', 'Dezhou', 'Tai\'an', 'Changzhi', 'Yangquan', 'Shunde', 'Handan', 'Cangzhou', 'Qinhuangdao', 'Fushun', 'Anshan', 'Liaoyang', 'Siping',
             'Tieling', 'Taonan', 'Chifeng', 'Shashi', 'Laohekou', 'Huaiyin', 'Haizhou', 'Nantong', 'Yangzhou', 'Zhenjiang', 'Changzhou', 'Hefei', 'Tonghua', 'Liaoyuan', 'Hailun',
             'Yuncheng', 'Jincheng', 'Pingliang', 'Wuwei', 'Ankang', 'Guiping', 'Baise', 'Longzhou', 'Benxi', 'Chaoyang', 'Fuxin', 'Mudanjiang', 'Ningguta']
IMP_RANK = {n: i for i, n in enumerate(IMPORTANT)}
# key towns that outrank bigger key towns when they collide: the seat of the Chinese Soviet Republic over Changting and Ningdu
KEY_FIRST = ['Ruijin']
def inside(lo, la):
    px, py = proj(lo, la); return XMIN + HW * 0.5 < px < XMAX - HW * 0.5 and YMIN + HR < py < YMAX - HR
outside = [c[0] for c in CITIES if not inside(c[1], c[2])]
if outside: print('  outside the map:', ', '.join(outside))
CITIES = [c for c in CITIES if inside(c[1], c[2])]
dups = [n for n, k in Counter(c[0] for c in CITIES).items() if k > 1]
assert not dups, dups
approx = {c[0]: hex_ll(c[1], c[2]) for c in CITIES}
def is_key(c): return 'cap' in c[5] or c[0] in KEEP
def tier(c): return 0 if 'cap' in c[5] and c[3] < 32 else 1 if 'cap' in c[5] else 2 if c[0] in KEY_FIRST else 3 if c[0] in KEEP else 4 if c[0] in IMP_RANK else 5
def min_gap(a, b):
    if frozenset((a[0], b[0])) in SPACING_EXCEPTIONS: return SPACING_EXCEPTION_GAP
    return MIN_SPACING if a[3] != b[3] or (is_key(a) and is_key(b)) else MIN_SPACING_SIDE
order = sorted(range(len(CITIES)), key=lambda i: (tier(CITIES[i]), -CITIES[i][4], CITIES[i][0]))
ALL_CITIES = CITIES; NOT_PLACED = set()   # towns the placement below could not seat clear of their neighbours (dropped on a rerun)
# the plot arrays the placement writes to, restored before a rerun
PLACE_ARRAYS = (owner, feature, wonder, resource, elev, terrain); place_backup = [a.copy() for a in PLACE_ARRAYS]
while True:
    for a, b in zip(PLACE_ARRAYS, place_backup): a[...] = b
    CITIES = ALL_CITIES; kept = []; ABSORBED = {}
    for i in order:
        name, lo, la, pl, popk, tags = CITIES[i]; h = approx[name]
        if h is None: continue
        if name not in NOT_PLACED and all(hexdist(h, approx[CITIES[j][0]]) >= min_gap(CITIES[i], CITIES[j]) for j in kept): kept.append(i); continue
        same = [j for j in kept if CITIES[j][3] == pl and hexdist(h, approx[CITIES[j][0]]) <= 8]
        if not same: ABSORBED[name] = None; continue      # a small town wedged between other sides' cities: dropped
        tgt = min(same, key=lambda j: (hexdist(h, approx[CITIES[j][0]]), j))
        ABSORBED[name] = CITIES[tgt][0]
    assert all(t not in ABSORBED for t in ABSORBED.values())
    extra = Counter()
    for name, tgt in ABSORBED.items():
        if tgt: extra[tgt] += next(c[4] for c in CITIES if c[0] == name)
    kept_set = set(kept)
    CITIES = [(c[0], c[1], c[2], c[3], c[4] + (extra[c[0]] if c[3] < 32 else 0), c[5]) for i, c in enumerate(CITIES) if i in kept_set]
    city_at = {}; city_tiles = []; failed = []
    def friendly(o, pl): return o == NONE or o == pl
    def clear(x, y, ci): return all(hexdist((x, y), t) >= min_gap(CITIES[ci], CITIES[k]) for k, t in enumerate(city_tiles) if t)
    for ci, (name, lo, la, pl, popk, tags) in enumerate(CITIES):
        def ok(x, y, ci=ci):
            if not is_land[y, x] or elev[y, x] == 2 or terrain[y, x] == SNOW or (x, y) in city_at: return False
            return clear(x, y, ci)
        t = find_tile(lo, la, lambda x, y, pl=pl, ci=ci: ok(x, y, ci) and friendly(owner[y, x], pl), 1)
        if t is None: t = find_tile(lo, la, ok, 2)
        if t is None:
            t = find_tile(lo, la, lambda x, y, ci=ci: is_land[y, x] and (x, y) not in city_at and clear(x, y, ci), 3)
            if t is not None: elev[t[1], t[0]] = min(int(elev[t[1], t[0]]), 1); terrain[t[1], t[0]] = PLAINS if terrain[t[1], t[0]] == SNOW else terrain[t[1], t[0]]
            print('  !! relaxed placement for', name, t)
        if t is None: failed.append(name); city_tiles.append(None); continue
        city_at[t] = ci; city_tiles.append(t)
        owner[t[1], t[0]] = pl; feature[t[1], t[0]] = NONE; wonder[t[1], t[0]] = NONE
        if resource[t[1], t[0]] != NONE and RESOURCES[resource[t[1], t[0]]].split('_', 1)[1] in ('FISH', 'WHALE', 'CRAB'): resource[t[1], t[0]] = NONE
        for nb in neighbors(*t):
            if is_land[nb[1], nb[0]] and nb not in city_at and (owner[nb[1], nb[0]] == NONE or 'cap' in tags or name in ('Jinggangshan', 'Hengfeng', 'Weihaiwei', 'Dairen', 'Macau', 'Hong Kong', 'Fort-Bayard')): owner[nb[1], nb[0]] = pl
    if not failed: break
    print('  no clear plot, merging on a rerun:', ', '.join(failed)); NOT_PLACED |= set(failed)
# the rule on the final plots: never closer than 3, 4 within a side unless both are key towns (SPACING_EXCEPTIONS aside)
gaps = sorted((hexdist(city_tiles[a], city_tiles[b]), CITIES[b][0], CITIES[a][0], CITIES[a][3] == CITIES[b][3]) for a in range(len(CITIES)) for b in range(a))
bad = [g for g in gaps if g[0] < min_gap(*(next(c for c in CITIES if c[0] == n) for n in g[1:3]))]
assert not bad, bad
merged = {k: v for k, v in ABSORBED.items() if v}
print(f'  cities: kept {len(CITIES)}, merged {len(merged)}, dropped {len(ABSORBED) - len(merged)}; closest pair {gaps[0][0]} hexes, closest within a side',
      min(g[0] for g in gaps if g[3]), 'hexes; biggest merges:', ', '.join(f'{k} +{v}k' for k, v in extra.most_common(6)))
if os.environ.get('CN_SPACING'):   # the merges and the closest pairs, for checking
    for k in sorted(ABSORBED): print(f'    {k} -> {ABSORBED[k]}')
    for g in gaps:
        if g[0] <= 4: print('    pair', *g)
# land farther than 5 hexes from one of its owner's cities (4 for a city-state) is nobody's: the hills, steppes and deserts between the towns breed bandits
near = {}
for ci, t in enumerate(city_tiles): near.setdefault(CITIES[ci][3], []).append(t)
for y in range(H):
    for x in range(W):
        o = owner[y, x]
        if o == NONE or (x, y) in city_at: continue
        lim = 4 if o >= 32 else 5
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
    """Lean 1928 building set: gold and defence everywhere, upkeep-heavy buildings only in the big cities; no universities or public schools (science is off)."""
    name, lo, la, pl, popk, tags = CITIES[ci]; pop = civ_pop(popk); t = city_tiles[ci]; tags = tags.split()
    b = ['BUILDING_MONUMENT', 'BUILDING_GRANARY', 'BUILDING_MARKET', 'BUILDING_WALLS']
    if pop >= 5: b += ['BUILDING_LIBRARY']
    if pop >= 8: b += ['BUILDING_BANK', 'BUILDING_CASTLE', 'BUILDING_WORKSHOP']
    if pop >= 11: b += ['BUILDING_BARRACKS', 'BUILDING_FORGE', 'BUILDING_AQUEDUCT']
    if pop >= 14: b += ['BUILDING_STOCK_EXCHANGE', 'BUILDING_ARMORY', 'BUILDING_ARSENAL', 'BUILDING_AMPHITHEATER', 'BUILDING_WINDMILL']
    if pop >= 17: b += ['BUILDING_FACTORY', 'BUILDING_HOSPITAL', 'BUILDING_OPERA_HOUSE', 'BUILDING_MUSEUM']
    if 'cap' in tags: b += ['BUILDING_PALACE']
    if 'cap' in tags and pl < 32: b += ['BUILDING_CONSTABLE', 'BUILDING_MILITARY_ACADEMY', 'BUILDING_BARRACKS', 'BUILDING_ARSENAL']
    if 'base' in tags: b += ['BUILDING_BARRACKS', 'BUILDING_ARMORY', 'BUILDING_STABLE']
    if any(not is_land[nb[1], nb[0]] and not is_lake[nb[1], nb[0]] for nb in neighbors(*t)): b += ['BUILDING_HARBOR'] + (['BUILDING_LIGHTHOUSE'] if pop >= 8 else [])
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
# The railway network of 1928, line by line (both ends must be cities above; a town merged away hands its line to the city that absorbed it).
RAIL = [
    # Beiping - Mukden (Beining): Beiping - Tianjin - Tangshan - Shanhaiguan - Jinzhou - Mukden, with the Yingkou and Huludao branches
    ('Beiping', 'Tongzhou'), ('Beiping', 'Tianjin'), ('Tianjin', 'Tangshan'), ('Tangshan', 'Qinhuangdao'), ('Qinhuangdao', 'Shanhaiguan'), ('Shanhaiguan', 'Huludao'), ('Huludao', 'Jinzhou'),
    ('Jinzhou', 'Mukden'), ('Jinzhou', 'Yingkou'), ('Jinzhou', 'Chaoyang'),
    # Beiping - Hankou (Pinghan) and the Zhengzhou - Taiyuan line
    ('Beiping', 'Zhuozhou'), ('Zhuozhou', 'Baoding'), ('Baoding', 'Zhengding'), ('Zhengding', 'Shijiazhuang'), ('Shijiazhuang', 'Shunde'), ('Shunde', 'Handan'), ('Handan', 'Anyang'),
    ('Anyang', 'Xinxiang'), ('Xinxiang', 'Zhengzhou'), ('Xinxiang', 'Jiaozuo'), ('Zhengzhou', 'Xuchang'), ('Xuchang', 'Luohe'), ('Luohe', 'Runan'), ('Runan', 'Xinyang'), ('Xinyang', 'Xiaogan'), ('Xiaogan', 'Hankou'),
    ('Shijiazhuang', 'Yangquan'), ('Yangquan', 'Taiyuan'),
    # Tianjin - Pukou (Jinpu): Tianjin - Cangzhou - Dezhou - Jinan - Tai'an - Yanzhou - Xuzhou - Bengbu - Pukou (Nanjing)
    ('Tianjin', 'Cangzhou'), ('Cangzhou', 'Dezhou'), ('Dezhou', 'Jinan'), ('Jinan', 'Tai\'an'), ('Tai\'an', 'Yanzhou'), ('Yanzhou', 'Jining'), ('Yanzhou', 'Xuzhou'), ('Xuzhou', 'Bengbu'), ('Bengbu', 'Nanjing'),
    # Jiaoji: Qingdao - Weixian - Jinan
    ('Qingdao', 'Weixian'), ('Weixian', 'Yizhou'), ('Yizhou', 'Jinan'),
    # Longhai, as far as it ran in 1928: Haizhou - Xuzhou - Shangqiu - Kaifeng - Zhengzhou - Luoyang - Lingbao
    ('Haizhou', 'Xuzhou'), ('Xuzhou', 'Shangqiu'), ('Shangqiu', 'Kaifeng'), ('Kaifeng', 'Zhengzhou'), ('Zhengzhou', 'Luoyang'), ('Luoyang', 'Lingbao'),
    # Beiping - Suiyuan (Pingsui): Beiping - Zhangjiakou - Datong - Guisui - Baotou
    ('Beiping', 'Xuanhua'), ('Xuanhua', 'Zhangjiakou'), ('Zhangjiakou', 'Datong'), ('Datong', 'Fengzhen'), ('Fengzhen', 'Guisui'), ('Guisui', 'Baotou'), ('Fengzhen', 'Pingdiquan'),
    # Shanghai - Nanjing, Shanghai - Hangzhou, Nanxun (Nanchang - Jiujiang), Canton - Hankou in two halves, Pingxiang - Zhuzhou
    ('Shanghai', 'Suzhou'), ('Suzhou', 'Wuxi'), ('Wuxi', 'Changzhou'), ('Changzhou', 'Zhenjiang'), ('Zhenjiang', 'Nanjing'), ('Shanghai', 'Jiaxing'), ('Jiaxing', 'Hangzhou'),
    ('Nanchang', 'Jiujiang'), ('Hankou', 'Puqi'), ('Puqi', 'Yueyang'), ('Yueyang', 'Changsha'), ('Changsha', 'Xiangtan'), ('Xiangtan', 'Liling'), ('Liling', 'Pingxiang'),
    ('Canton', 'Shaoguan'), ('Canton', 'Hong Kong'), ('Canton', 'Foshan'), ('Shantou', 'Chaozhou'), ('Xiamen', 'Zhangzhou'),
    # Manchuria: the Chinese Eastern Railway (Manzhouli - Hailar - Qiqihar - Harbin - Suifenhe - Vladivostok) and its southern branch to Changchun;
    # the South Manchuria Railway (Changchun - Mukden - Dairen - Port Arthur; Mukden - Andong; Fushun); the Chinese-built lines: Jilin, Siping - Taonan - Qiqihar,
    # Mukden - Hailong - Jilin, Dahushan - Tongliao, Hulan - Hailun, Jilin - Dunhua, the Tumen line
    ('Manzhouli', 'Hailar'), ('Hailar', 'Zhalantun'), ('Zhalantun', 'Qiqihar'), ('Qiqihar', 'Harbin'), ('Harbin', 'Yilan'), ('Harbin', 'Mudanjiang'), ('Mudanjiang', 'Ningguta'),
    ('Mudanjiang', 'Suifenhe'), ('Suifenhe', 'Nikolsk-Ussuriysky'), ('Nikolsk-Ussuriysky', 'Vladivostok'), ('Nikolsk-Ussuriysky', 'Iman'), ('Iman', 'Bikin'), ('Bikin', 'Khabarovsk'),
    ('Harbin', 'Shuangcheng'), ('Shuangcheng', 'Changchun'), ('Changchun', 'Siping'), ('Siping', 'Tieling'), ('Tieling', 'Mukden'), ('Mukden', 'Liaoyang'), ('Liaoyang', 'Anshan'),
    ('Anshan', 'Yingkou'), ('Anshan', 'Zhuanghe'), ('Zhuanghe', 'Dairen'), ('Dairen', 'Port Arthur'), ('Mukden', 'Fushun'), ('Mukden', 'Benxi'), ('Benxi', 'Andong'), ('Andong', 'Sinuiju'),
    ('Changchun', 'Jilin'), ('Jilin', 'Dunhua'), ('Siping', 'Taonan'), ('Taonan', 'Qiqihar'), ('Taonan', 'Ulanhot'), ('Mukden', 'Liaoyuan'), ('Liaoyuan', 'Jilin'), ('Liaoyuan', 'Tonghua'),
    ('Mukden', 'Tongliao'), ('Harbin', 'Hailun'), ('Qiqihar', 'Keshan'), ('Yanji', 'Hunchun'), ('Yanji', 'Dunhua'),
    # Korea: Busan - Daegu - Seoul - Pyongyang - Sinuiju; Seoul - Incheon; Seoul - Wonsan - Hamhung - Chongjin; Seoul - Gwangju - Mokpo
    ('Busan', 'Daegu'), ('Daegu', 'Seoul'), ('Seoul', 'Incheon'), ('Seoul', 'Pyongyang'), ('Pyongyang', 'Sinuiju'), ('Seoul', 'Wonsan'), ('Wonsan', 'Hamhung'), ('Hamhung', 'Chongjin'),
    ('Seoul', 'Gwangju'), ('Gwangju', 'Mokpo'),
    # Taiwan, Kyushu, Tonkin and the Yunnan railway (Haiphong - Hanoi - Lao Cai - Kunming)
    ('Keelung', 'Taipei'), ('Taipei', 'Taichung'), ('Taichung', 'Tainan'), ('Tainan', 'Kaohsiung'), ('Shimonoseki', 'Fukuoka'), ('Fukuoka', 'Kumamoto'), ('Kumamoto', 'Kagoshima'),
    ('Fukuoka', 'Nagasaki'), ('Shimonoseki', 'Hiroshima'), ('Shimonoseki', 'Oita'), ('Oita', 'Miyazaki'), ('Haiphong', 'Hanoi'), ('Hanoi', 'Nam Dinh'), ('Hanoi', 'Lang Son'),
    ('Hanoi', 'Lao Cai'), ('Lao Cai', 'Mengzi'), ('Mengzi', 'Gejiu'), ('Mengzi', 'Kunming'),
]
rail_pairs = set()
for a, b in RAIL:
    a = ABSORBED.get(a, a); b = ABSORBED.get(b, b)
    if a == b: continue
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
# special troops (named by the setup script from these promotions, see ui/China1928_Production.lua)
WHAMPOA = ['DRILL_1', 'SHOCK_1']   # Nanjing's central divisions, officered from the Whampoa academy
NWARMY = ['DRILL_1', 'MARCH']      # Feng Yuxiang's drilled Northwest Army
GARRISON = ['COVER_1']             # Yan Xishan's provincial garrisons and the Japanese railway guards
GXARMY = ['DRILL_1', 'DRILL_2']    # the Guangxi divisions, hill fighters
RED = ['DRILL_1', 'MARCH']         # the Red Army: guerrillas who heal on the move
DEPLOY = [   # (type, owner, lon, lat, promotions, xp, count)
    # --- the National Government: the First Group Army of the Northern Expedition, the Hunan army of Lu Diping, the river gunboats and the small navy
    ('GREAT_WAR_INFANTRY', NAN, 118.78, 32.06, WHAMPOA, 15, 3), ('ARTILLERY', NAN, 118.78, 32.06, [], 5, 2), ('MACHINE_GUN', NAN, 118.78, 32.06, [], 5, 1),
    ('GREAT_GENERAL', NAN, 118.78, 32.06, [], 0, 1), ('TRIPLANE', NAN, 118.78, 32.06, [], 5, 1), ('WWI_BOMBER', NAN, 118.78, 32.06, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NAN, 121.47, 31.23, [], 8, 2), ('MACHINE_GUN', NAN, 121.47, 31.23, [], 5, 1), ('IRONCLAD', NAN, 121.9, 31.3, [], 5, 2), ('DESTROYER', NAN, 122.1, 31.0, [], 5, 1),
    ('GREAT_WAR_INFANTRY', NAN, 120.16, 30.27, [], 8, 1), ('RIFLEMAN', NAN, 120.16, 30.27, [], 5, 1), ('GREAT_WAR_INFANTRY', NAN, 117.18, 34.26, WHAMPOA, 15, 2),
    ('ARTILLERY', NAN, 117.18, 34.26, [], 5, 1), ('CAVALRY', NAN, 117.18, 34.26, [], 5, 1), ('GREAT_WAR_INFANTRY', NAN, 117.39, 32.92, [], 8, 1),
    ('GREAT_WAR_INFANTRY', NAN, 115.86, 28.68, [], 8, 2), ('RIFLEMAN', NAN, 115.86, 28.68, [], 5, 1), ('RIFLEMAN', NAN, 114.99, 27.11, [], 5, 2), ('GREAT_WAR_INFANTRY', NAN, 114.60, 26.90, [], 8, 1),
    ('RIFLEMAN', NAN, 114.93, 25.83, [], 5, 1), ('GREAT_WAR_INFANTRY', NAN, 112.94, 28.23, [], 8, 2), ('RIFLEMAN', NAN, 112.94, 28.23, [], 5, 2), ('ARTILLERY', NAN, 112.94, 28.23, [], 5, 1),
    ('RIFLEMAN', NAN, 113.80, 26.80, [], 5, 1), ('RIFLEMAN', NAN, 112.57, 26.89, [], 5, 1), ('RIFLEMAN', NAN, 111.69, 29.03, [], 5, 1), ('GREAT_WAR_INFANTRY', NAN, 119.30, 26.08, [], 8, 1),
    ('RIFLEMAN', NAN, 119.30, 26.08, [], 5, 1), ('RIFLEMAN', NAN, 118.09, 24.48, [], 5, 1), ('GREAT_WAR_INFANTRY', NAN, 120.38, 36.07, [], 8, 1), ('RIFLEMAN', NAN, 121.39, 37.54, [], 5, 1),
    ('RIFLEMAN', NAN, 117.05, 30.53, [], 5, 1), ('RIFLEMAN', NAN, 117.97, 28.45, [], 5, 1),
    ('WORKER', NAN, 118.78, 32.06, [], 0, 2), ('WORKER', NAN, 121.47, 31.23, [], 0, 1), ('WORKER', NAN, 112.94, 28.23, [], 0, 1),
    # --- the Guominjun: the Second Group Army in Henan, Shaanxi and Gansu, Sun Liangcheng in western Shandong
    ('GREAT_WAR_INFANTRY', GMJ, 114.31, 34.80, NWARMY, 15, 2), ('ARTILLERY', GMJ, 114.31, 34.80, [], 5, 1), ('GREAT_GENERAL', GMJ, 114.31, 34.80, [], 0, 1),
    ('GREAT_WAR_INFANTRY', GMJ, 113.65, 34.76, NWARMY, 15, 2), ('MACHINE_GUN', GMJ, 113.65, 34.76, [], 5, 1), ('CAVALRY', GMJ, 113.65, 34.76, [], 5, 1),
    ('GREAT_WAR_INFANTRY', GMJ, 112.45, 34.62, [], 8, 1), ('GREAT_WAR_INFANTRY', GMJ, 114.07, 32.13, [], 8, 1), ('RIFLEMAN', GMJ, 112.53, 33.00, [], 5, 1),
    ('GREAT_WAR_INFANTRY', GMJ, 115.65, 34.44, [], 8, 1), ('GREAT_WAR_INFANTRY', GMJ, 108.94, 34.34, NWARMY, 10, 2), ('CAVALRY', GMJ, 108.94, 34.34, [], 5, 1),
    ('ARTILLERY', GMJ, 108.94, 34.34, [], 5, 1), ('GREAT_WAR_INFANTRY', GMJ, 110.25, 34.54, [], 8, 1), ('GREAT_WAR_INFANTRY', GMJ, 103.83, 36.06, [], 8, 1),
    ('CAVALRY', GMJ, 103.83, 36.06, [], 5, 2), ('CAVALRY', GMJ, 106.27, 38.47, [], 5, 1), ('RIFLEMAN', GMJ, 105.72, 34.58, [], 5, 1), ('GREAT_WAR_INFANTRY', GMJ, 117.00, 36.67, NWARMY, 10, 2),
    ('ARTILLERY', GMJ, 117.00, 36.67, [], 5, 1), ('RIFLEMAN', GMJ, 116.59, 35.41, [], 5, 1), ('RIFLEMAN', GMJ, 117.09, 36.20, [], 5, 1), ('GREAT_WAR_INFANTRY', GMJ, 114.39, 36.10, [], 8, 1),
    ('RIFLEMAN', GMJ, 107.02, 33.07, [], 5, 1), ('WORKER', GMJ, 114.31, 34.80, [], 0, 2), ('WORKER', GMJ, 108.94, 34.34, [], 0, 1),
    # --- Shanxi: the Third Group Army, now holding Beiping, Tianjin and the Hebei plain, and the garrisons of Chahar and Suiyuan
    ('GREAT_WAR_INFANTRY', SHX, 112.55, 37.87, GARRISON, 10, 2), ('ARTILLERY', SHX, 112.55, 37.87, [], 5, 2), ('MACHINE_GUN', SHX, 112.55, 37.87, [], 5, 1),
    ('GREAT_GENERAL', SHX, 112.55, 37.87, [], 0, 1), ('GREAT_WAR_INFANTRY', SHX, 113.30, 40.08, GARRISON, 10, 1), ('RIFLEMAN', SHX, 111.52, 36.09, [], 5, 1),
    ('GREAT_WAR_INFANTRY', SHX, 116.40, 39.90, [], 8, 2), ('ARTILLERY', SHX, 116.40, 39.90, [], 5, 1), ('MACHINE_GUN', SHX, 116.40, 39.90, [], 5, 1), ('TRIPLANE', SHX, 112.55, 37.87, [], 5, 1),
    ('GREAT_WAR_INFANTRY', SHX, 117.20, 39.13, [], 8, 2), ('GREAT_WAR_INFANTRY', SHX, 115.46, 38.87, [], 8, 1), ('GREAT_WAR_INFANTRY', SHX, 114.51, 38.04, [], 8, 1),
    ('CAVALRY', SHX, 114.88, 40.82, [], 5, 1), ('GREAT_WAR_INFANTRY', SHX, 114.88, 40.82, [], 8, 1), ('CAVALRY', SHX, 111.67, 40.82, [], 5, 1), ('RIFLEMAN', SHX, 111.67, 40.82, [], 5, 1),
    ('RIFLEMAN', SHX, 109.84, 40.66, [], 5, 1), ('RIFLEMAN', SHX, 113.12, 36.20, [], 5, 1),
    ('WORKER', SHX, 112.55, 37.87, [], 0, 2), ('WORKER', SHX, 116.40, 39.90, [], 0, 1),
    # --- Fengtian: the Northeast Army withdrawn beyond the Great Wall, its air force, its tanks and its arsenal at Mukden, Tang Yulin's Rehe army, the Northeast Navy
    ('GREAT_WAR_INFANTRY', FT, 123.43, 41.80, ['DRILL_1'], 10, 3), ('ARTILLERY', FT, 123.43, 41.80, [], 5, 2), ('MACHINE_GUN', FT, 123.43, 41.80, [], 5, 1),
    ('GREAT_GENERAL', FT, 123.43, 41.80, [], 0, 1), ('WWI_TANK', FT, 123.43, 41.80, [], 5, 1), ('TRIPLANE', FT, 123.43, 41.80, [], 5, 2), ('WWI_BOMBER', FT, 123.43, 41.80, [], 5, 2),
    ('GREAT_WAR_INFANTRY', FT, 121.13, 41.10, ['DRILL_1'], 10, 2), ('ARTILLERY', FT, 121.13, 41.10, [], 5, 1), ('GREAT_WAR_INFANTRY', FT, 126.63, 45.75, [], 8, 2),
    ('CAVALRY', FT, 126.63, 45.75, [], 5, 1), ('GREAT_WAR_INFANTRY', FT, 125.32, 43.88, [], 8, 1), ('GREAT_WAR_INFANTRY', FT, 126.55, 43.84, [], 8, 1),
    ('GREAT_WAR_INFANTRY', FT, 123.92, 47.35, [], 8, 1), ('CAVALRY', FT, 123.92, 47.35, [], 5, 1), ('CAVALRY', FT, 119.74, 49.21, [], 5, 1), ('RIFLEMAN', FT, 117.43, 49.60, [], 5, 1),
    ('GREAT_WAR_INFANTRY', FT, 117.94, 40.95, [], 8, 1), ('CAVALRY', FT, 117.94, 40.95, [], 5, 1), ('CAVALRY', FT, 118.89, 42.26, [], 5, 1), ('RIFLEMAN', FT, 124.38, 40.13, [], 5, 1),
    ('RIFLEMAN', FT, 127.50, 50.24, [], 5, 1), ('RIFLEMAN', FT, 129.51, 42.89, [], 5, 1), ('DESTROYER', FT, 120.95, 40.55, [], 5, 1), ('IRONCLAD', FT, 121.10, 40.45, [], 5, 1),
    ('WORKER', FT, 123.43, 41.80, [], 0, 2), ('WORKER', FT, 126.63, 45.75, [], 0, 1),
    # --- Guangxi: the Fourth Group Army in Wuhan, the home divisions in Guangxi, and Bai Chongxi's troops still in eastern Hebei
    ('GREAT_WAR_INFANTRY', GX, 114.27, 30.58, GXARMY, 15, 3), ('ARTILLERY', GX, 114.27, 30.58, [], 5, 1), ('MACHINE_GUN', GX, 114.27, 30.58, [], 5, 1),
    ('GREAT_GENERAL', GX, 114.27, 30.58, [], 0, 1), ('GREAT_WAR_INFANTRY', GX, 111.29, 30.70, [], 8, 1), ('GREAT_WAR_INFANTRY', GX, 112.14, 32.04, [], 8, 1),
    ('RIFLEMAN', GX, 112.24, 30.32, [], 5, 1), ('GREAT_WAR_INFANTRY', GX, 108.37, 22.82, GXARMY, 10, 1), ('RIFLEMAN', GX, 108.37, 22.82, [], 5, 1),
    ('GREAT_WAR_INFANTRY', GX, 110.29, 25.27, GXARMY, 10, 2), ('GREAT_WAR_INFANTRY', GX, 111.28, 23.48, [], 8, 1), ('RIFLEMAN', GX, 109.41, 24.33, [], 5, 1),
    ('GREAT_WAR_INFANTRY', GX, 118.40, 39.75, GXARMY, 10, 2), ('ARTILLERY', GX, 118.40, 39.75, [], 5, 1),
    ('WORKER', GX, 108.37, 22.82, [], 0, 1), ('WORKER', GX, 114.27, 30.58, [], 0, 1),
    # --- the Chinese Communists: the Fourth Red Army of Zhu De and Mao Zedong at Jinggangshan, Peng Dehuai's Fifth Red Army after the Pingjiang rising, Fang Zhimin
    # in northeastern Jiangxi, He Long in western Hunan, the guerrillas of the Hong Lake, the Dabie mountains and Hailufeng
    ('RIFLEMAN', CCP, 114.17, 26.57, RED, 15, 3), ('GREAT_GENERAL', CCP, 114.17, 26.57, [], 0, 1), ('RIFLEMAN', CCP, 117.60, 28.42, RED, 10, 2),
    ('RIFLEMAN', CCP, 113.60, 28.75, RED, 10, 2), ('RIFLEMAN', CCP, 110.30, 29.55, RED, 10, 1), ('RIFLEMAN', CCP, 113.40, 29.85, RED, 5, 1), ('RIFLEMAN', CCP, 115.10, 31.35, RED, 5, 1),
    ('RIFLEMAN', CCP, 115.35, 22.95, RED, 5, 1), ('WORKER', CCP, 114.17, 26.57, [], 0, 1),
    # --- barbarians: the bandit armies of western Henan and southern Shandong, the Red Spears, the honghuzi of Manchuria, the hill bandits of the south and the northwest
    ('RIFLEMAN', BARB, 111.90, 33.60, [], 5, 2), ('RIFLEMAN', BARB, 118.00, 35.70, [], 5, 2), ('RIFLEMAN', BARB, 115.20, 34.90, [], 5, 1), ('CAVALRY', BARB, 128.30, 45.40, [], 5, 1),
    ('RIFLEMAN', BARB, 125.00, 47.80, [], 5, 1), ('RIFLEMAN', BARB, 111.00, 25.60, [], 5, 1), ('RIFLEMAN', BARB, 117.40, 25.80, [], 5, 1), ('CAVALRY', BARB, 104.80, 35.20, [], 5, 1),
    ('CAVALRY', BARB, 108.60, 39.20, [], 5, 1), ('RIFLEMAN', BARB, 109.50, 27.00, [], 5, 1),
    # --- Japan: the Kwantung Army and the railway guards, the Korea Army, the fleet; the Soviet Far East
    ('ARTILLERY', 32 + CSIDX['JAPAN'], 121.61, 38.91, [], 5, 1), ('GREAT_WAR_INFANTRY', 32 + CSIDX['JAPAN'], 121.25, 38.81, GARRISON, 10, 1), ('GREAT_WAR_INFANTRY', 32 + CSIDX['JAPAN'], 126.98, 37.57, [], 10, 1),
    ('BATTLESHIP', 32 + CSIDX['JAPAN'], 121.20, 38.60, [], 5, 1), ('DESTROYER', 32 + CSIDX['JAPAN'], 129.20, 34.90, [], 5, 1), ('DESTROYER', 32 + CSIDX['JAPAN'], 121.90, 38.70, [], 5, 1),
    ('GREAT_WAR_INFANTRY', 32 + CSIDX['SOVIET'], 131.89, 43.12, [], 10, 1), ('CAVALRY', 32 + CSIDX['SOVIET'], 131.95, 43.80, [], 5, 1),
]
# every city-state keeps a garrison and a worker in its capital, a garrison in its towns of 40,000 and more
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES):
    DEPLOY.append(('GREAT_WAR_INFANTRY', 32 + i, lo, la, ['DRILL_1'], 10, 2 if popk >= 150 else 1)); DEPLOY.append(('WORKER', 32 + i, lo, la, [], 0, 1))
for name, lo, la, key, popk in CS_TOWNS:
    if popk >= 40: DEPLOY.append(('RIFLEMAN', 32 + CSIDX[key], lo, la, [], 5, 1))
units = []
land_occ = set(); naval_occ = set(); civ_occ = set(); air_count = Counter()
def place_unit(tp, pl, lo, la, promos, xp):
    allies = KMT if pl in KMT else {pl}
    def ok(x, y):
        o = owner[y, x]
        if tp in AIR: return (x, y) in city_at and CITIES[city_at[(x, y)]][3] == pl and air_count[(x, y)] < 4
        if pl == BARB: return is_land[y, x] and elev[y, x] != 2 and (x, y) not in city_at and (x, y) not in land_occ and all(nb not in city_at for nb in neighbors(x, y))
        if tp in NAVAL: return (not is_land[y, x]) and (x, y) not in naval_occ and (o == NONE or o in allies) and terrain[y, x] in (COAST, OCEAN)
        if not is_land[y, x] or elev[y, x] == 2: return False
        if o != NONE and o not in allies and pl != CCP: return False   # the Red Army's guerrillas stand in enemy country
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
# tanks: China drilled almost no oil; the deposits stand for the depots of imported fuel at the treaty ports and the arsenals)
UNIT_RES = {'CAVALRY': 'HORSE', 'IRONCLAD': 'COAL', 'WWI_TANK': 'OIL', 'BATTLESHIP': 'OIL', 'TRIPLANE': 'OIL', 'WWI_BOMBER': 'OIL'}
BLD_RES = {'BUILDING_FACTORY': 'COAL'}
STRATEGIC = ('IRON', 'HORSE', 'COAL', 'OIL')
# reserve for the aircraft, tanks and cavalry the events bring (ui/China1928_Events.lua)
EVENT_NEED = {NAN: {'OIL': 8, 'HORSE': 1}, GMJ: {'OIL': 1, 'HORSE': 3}, SHX: {'OIL': 2, 'HORSE': 2}, FT: {'OIL': 6, 'HORSE': 2}, GX: {'OIL': 1}, CCP: {}}
DEPOSITS = {NAN: {'HORSE': [(117.5, 34.0)], 'COAL': [(117.0, 32.6)], 'OIL': [(121.3, 31.3), (118.7, 32.1), (120.4, 36.1), (119.3, 26.1)]},
            GMJ: {'HORSE': [(106.3, 37.5), (104.5, 36.2)], 'COAL': [(113.3, 35.2)], 'OIL': [(114.3, 34.8)]},
            SHX: {'HORSE': [(112.0, 40.6), (115.0, 41.2)], 'COAL': [(112.6, 38.0)], 'OIL': [(117.3, 39.1), (112.6, 37.8)]},
            FT: {'HORSE': [(122.5, 44.5), (120.0, 47.0)], 'COAL': [(123.8, 41.9)], 'OIL': [(123.5, 41.7), (126.6, 45.7), (122.3, 40.7)]},
            GX: {'HORSE': [(108.5, 23.5)], 'COAL': [(109.4, 24.4)], 'OIL': [(114.3, 30.6)]},
            CCP: {'HORSE': [(114.2, 26.6)], 'COAL': [(114.2, 26.7)], 'OIL': [(114.2, 26.6)]}}
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
    NAN: TRAD[:4] + HONOR[:4],
    GMJ: HONOR + LIBERTY[:2],
    SHX: TRAD + HONOR[:2],
    FT: HONOR[:5] + TRAD[:3],
    GX: HONOR[:4] + LIBERTY[:3],
    CCP: LIBERTY[:5] + HONOR[:2],
}
POLICIES = sorted({p for v in PLAYER_POLICIES.values() for p in v})
VICTORIES = ['VICTORY_DOMINATION']
GAMEOPTIONS = ['GAMEOPTION_RAGING_BARBARIANS', 'GAMEOPTION_NO_GOODY_HUTS', 'GAMEOPTION_NO_LEAGUES', 'GAMEOPTION_NO_RELIGION', 'GAMEOPTION_NO_HAPPINESS',
               'GAMEOPTION_NO_TUTORIAL', 'GAMEOPTION_DISABLE_START_BIAS', 'GAMEOPTION_NO_SCIENCE', 'GAMEOPTION_POLICY_SAVING',
               'GAMEOPTION_COMPLETE_KILLS']   # complete kills: a side that loses its last city lives on while it has units (the Red Army on the Long March)

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
war = sorted((CCP, k) for k in sorted(KMT))
kmt_pairs = [(a, b) for a in sorted(KMT) for b in sorted(KMT) if a < b]
# contact: all; war: the Communists against the five armies of the National Government, not locked (the Xi'an incident ends it);
# the five armies at peace with open borders, nothing locked: the Chiang-Guangxi war, the Central Plains War and the rest come by event or by choice
rel = relbits(contact) + relbits(war) + relbits([]) + relbits(kmt_pairs) + relbits([])
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
name_b = b'China 1928\0'
desc_b = (b'10 October 1928. The Chinese warlord era from the Amur to Tonkin at ~%d km per hex: Chiang Kai-shek\'s National Government, Feng Yuxiang\'s Guominjun, Yan Xishan, '
          b'Zhang Xueliang\'s Fengtian clique, the Guangxi clique and the Communists, with Japan, the Soviet Union, the provincial militarists and the colonies as city-states. '
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
    f.write(struct.pack('<64sIIIiBBBB9I', b'GAMESPEED_QUICK', 0, 0, 0, 1928, P, CS, T, 0,
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
# places the events name that are not cities (ui/China1928_Events.lua): the generator writes their plots into the copied Lua
SPOTS = {'FENGTAI': (116.22, 39.85), 'YELLOW_RIVER_CROSSING': (110.75, 37.20), 'SUIYUAN_NORTH': (111.20, 42.30), 'LAHASUSU': (132.40, 47.60),
         'MANZHOULI_FRONT': (117.60, 49.75), 'MUKDEN_ZONE': (123.25, 41.90), 'CHANGCHUN_ZONE': (125.20, 43.80), 'ANDONG_ZONE': (124.50, 40.30),
         'JINZHOU_FRONT': (121.60, 41.35), 'WUSONG': (121.48, 31.40), 'WUSONG_SEA': (122.10, 31.35), 'HARBIN_FRONT': (126.40, 45.40),
         'SHANHAIGUAN_FRONT': (119.95, 40.15), 'REHE_FRONT': (120.40, 41.90), 'YUDU': (115.41, 25.95), 'LUDING': (102.23, 29.92),
         'WUQI': (108.17, 36.93), 'WAYAOBAO': (109.66, 37.14), 'HUINING': (105.05, 35.69)}
lua_spots = []
for k in sorted(SPOTS):
    sea = k.endswith('_SEA')
    def spot_ok(x, y, sea=sea): return (not is_land[y, x] and not is_lake[y, x]) if sea else (is_land[y, x] and elev[y, x] != 2 and (x, y) not in city_at)
    t = find_tile(*SPOTS[k], spot_ok, 2); assert t is not None, k   # never a city tile: invaders appear beside the city
    lua_spots.append(f'{k} = {{ {t[0]}, {t[1]} }}')
UI_FILES = ['China1928LoadScreen.lua', 'China1928LoadScreen.xml', 'China1928_Production.lua', 'China1928_Production.xml', 'China1928_Events.lua', 'China1928_Events.xml', 'China1928_Uniques.sql', 'China1928_Text.xml']
for fn in UI_FILES:
    src = os.path.join(HERE, 'ui', fn)
    if fn == 'China1928_Events.lua' and os.path.exists(src):
        lua = open(src, encoding='utf-8').read(); assert '{} -- @SPOTS@' in lua
        open(os.path.join(OUT_DIR, fn), 'w', encoding='utf-8').write(lua.replace('{} -- @SPOTS@', '{ ' + ', '.join(lua_spots) + ' }'))
    elif os.path.exists(src): shutil.copy(src, os.path.join(OUT_DIR, fn))
    else: print('  !! missing ui file', fn)
WONDERS_OFF = [l.strip() for l in open(f'{XMLDIR}/WORLD_WONDERS.txt') if l.strip()]
rules = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- China 1928: no world wonders, no Manhattan Project, no Apollo Program; weekly calendar parked; neighbours as city-states; faction colours; Asian city art for every side. -->', '<GameData>', '  <Buildings>']
for w in WONDERS_OFF: rules.append(f'    <Update><Where Type="{w}" /><Set PrereqTech="TECH_FUTURE_TECH" /></Update>')
rules += ['  </Buildings>', '  <Projects>', '    <Update><Where Type="PROJECT_MANHATTAN_PROJECT" /><Set TechPrereq="TECH_FUTURE_TECH" /></Update>',
          '    <Update><Where Type="PROJECT_APOLLO_PROGRAM" /><Set TechPrereq="TECH_FUTURE_TECH" /></Update>', '  </Projects>',
          '  <GameSpeed_Turns>', '    <Delete GameSpeedType="GAMESPEED_STANDARD" />',
          '    <Row><GameSpeedType>GAMESPEED_STANDARD</GameSpeedType><MonthIncrement>1</MonthIncrement><TurnsPerIncrement>100000</TurnsPerIncrement></Row>',
          '    <Delete GameSpeedType="GAMESPEED_QUICK" />',
          '    <Row><GameSpeedType>GAMESPEED_QUICK</GameSpeedType><MonthIncrement>1</MonthIncrement><TurnsPerIncrement>100000</TurnsPerIncrement></Row>',
          '  </GameSpeed_Turns>', '  <Defines>', '    <Update><Where Name="START_YEAR" /><Set Value="1928" /></Update>', '  </Defines>', '  <Colors>']
def rgb(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
PCOL = {'NAN': ('#FFFFFF', '#1F3C99'), 'GMJ': ('#F2E6C8', '#556B2F'), 'SHX': ('#F5D76E', '#7B4A22'), 'FT': ('#1A1A1A', '#E8B400'), 'GX': ('#FFFFFF', '#1E8A8A'), 'CCP': ('#FFD700', '#C8102E')}
for k, (icon, bg) in PCOL.items():
    for suf, h in (('ICON', icon), ('BG', bg)):
        r, g, b = rgb(h); rules.append(f'    <Row><Type>COLOR_PLAYER_CHN1928_{k}_{suf}</Type><Red>{r:.3f}</Red><Green>{g:.3f}</Green><Blue>{b:.3f}</Blue><Alpha>1</Alpha></Row>')
rules += ['  </Colors>', '  <PlayerColors>']
for k in PCOL: rules.append(f'    <Row><Type>PLAYERCOLOR_CHN1928_{k}</Type><PrimaryColor>COLOR_PLAYER_CHN1928_{k}_ICON</PrimaryColor><SecondaryColor>COLOR_PLAYER_CHN1928_{k}_BG</SecondaryColor><TextColor>COLOR_PLAYER_WHITE_TEXT</TextColor></Row>')
rules += ['  </PlayerColors>', '  <Civilizations>']
for p in PLAYERS: rules.append(f'    <Update><Where Type="{p["civ"]}" /><Set DefaultPlayerColor="{p["color"]}" ArtStyleType="ARTSTYLE_ASIAN" ArtStyleSuffix="_ASIA" ArtStylePrefix="ASIAN " /></Update>')
rules += ['  </Civilizations>', '  <MinorCivilizations>']
MCOL = ['PLAYERCOLOR_MINOR_WHITE', 'PLAYERCOLOR_MINOR_PURPLE', 'PLAYERCOLOR_MINOR_LIGHT_BLUE', 'PLAYERCOLOR_MINOR_PEACH', 'PLAYERCOLOR_MINOR_LIGHT_ORANGE', 'PLAYERCOLOR_MINOR_DARK_LEMON',
        'PLAYERCOLOR_MINOR_LIGHT_GREEN', 'PLAYERCOLOR_MINOR_GOLDENROD', 'PLAYERCOLOR_MINOR_GRAY', 'PLAYERCOLOR_MINOR_MIDDLE_CYAN', 'PLAYERCOLOR_MINOR_LIGHT_YELLOW', 'PLAYERCOLOR_MINOR_MIDDLE_BLUE',
        'PLAYERCOLOR_MINOR_LIGHT_PURPLE']
# city art: the colonial cities and Japan European-styled, the Chinese provinces and Mongolia Asian
CS_EURO = {'SOVIET', 'HONGKONG', 'MACAU', 'WEIHAIWEI', 'INDOCHINA'}
for i, (key, name, mtype, trait, lo, la, popk) in enumerate(CITY_STATES):
    tk = f'TXT_KEY_CITYSTATE_CHN1928_{key}'
    rules.append(f'    <Row><Type>{mtype}</Type><Description>{tk}</Description><Civilopedia>{tk}</Civilopedia><ShortDescription>{tk}</ShortDescription><Adjective>{tk}</Adjective><ArtDefineTag>ART_DEF_CIVILIZATION_MINOR</ArtDefineTag><DefaultPlayerColor>{MCOL[i]}</DefaultPlayerColor>{'<ArtStyleType>ARTSTYLE_EUROPEAN</ArtStyleType><ArtStyleSuffix>_EURO</ArtStyleSuffix><ArtStylePrefix>EUROPEAN </ArtStylePrefix>' if key in CS_EURO else '<ArtStyleType>ARTSTYLE_ASIAN</ArtStyleType><ArtStyleSuffix>_ASIA</ArtStyleSuffix><ArtStylePrefix>ASIAN </ArtStylePrefix>'}<MinorCivTrait>{trait}</MinorCivTrait></Row>')
rules += ['  </MinorCivilizations>', '  <MinorCivilization_CityNames>']
for key, name, mtype, trait, lo, la, popk in CITY_STATES: rules.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><CityName>TXT_KEY_CITY_CHN1928_{key}</CityName></Row>')
rules += ['  </MinorCivilization_CityNames>', '  <MinorCivilization_Flavors>']
for key, name, mtype, trait, lo, la, popk in CITY_STATES:
    for fl, v in (('FLAVOR_CITY_DEFENSE', 9), ('FLAVOR_DEFENSE', 9), ('FLAVOR_GROWTH', 4), ('FLAVOR_GOLD', 5), ('FLAVOR_PRODUCTION', 5)):
        rules.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><FlavorType>{fl}</FlavorType><Flavor>{v}</Flavor></Row>')
rules += ['  </MinorCivilization_Flavors>', '</GameData>', '']
open(os.path.join(OUT_DIR, 'China1928_Rules.xml'), 'w').write('\n'.join(rules))
# --- leader art: static diplomacy scenes, portrait atlas, faction emblem atlases, Dawn of Man images (built by art/build_art.py)
ART = os.path.join(HERE, 'art', 'out'); art_files = []
if os.path.isdir(ART):
    for f in sorted(glob.glob(os.path.join(ART, '*.dds'))):
        shutil.copy(f, os.path.join(OUT_DIR, os.path.basename(f))); art_files.append(os.path.basename(f))
    shutil.copy(os.path.join(HERE, 'art', 'src', 'CREDITS.txt'), os.path.join(OUT_DIR, 'CREDITS.txt'))
LEADER_ART = [('LEADER_WU_ZETIAN', 'CIVILIZATION_CHINA', 'Chiang'), ('LEADER_SHAKA', 'CIVILIZATION_ZULU', 'Feng'), ('LEADER_CATHERINE', 'CIVILIZATION_RUSSIA', 'Yan'),
              ('LEADER_BISMARCK', 'CIVILIZATION_GERMANY', 'Zhang'), ('LEADER_SELASSIE', 'CIVILIZATION_ETHIOPIA', 'Li'), ('LEADER_POCATELLO', 'CIVILIZATION_SHOSHONE', 'Mao')]
scene_files = []
if art_files:
    for i, (ld, cv, key) in enumerate(LEADER_ART):
        fn = f'CHN1928_{key}_Scene.xml'; scene_files.append(fn)
        open(os.path.join(OUT_DIR, fn), 'w').write(f'<?xml version="1.0" encoding="utf-8"?>\n<LeaderScene FallbackImage="CHN1928_Scene_{key}.dds">\n</LeaderScene>\n')
    lx = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- China 1928: static leader scenes, portrait atlas, faction emblems and Dawn of Man images (Firaxis Civil War technique). -->', '<GameData>', '  <IconTextureAtlases>']
    for size in (256, 128, 64): lx.append(f'    <Row><Atlas>CHN1928_LEADER_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>CHN1928_Leaders{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    for size in (256, 128, 80, 64, 45, 32): lx.append(f'    <Row><Atlas>CHN1928_CIV_COLOR_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>CHN1928_CivColor{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    for size in (128, 64, 48, 32, 24, 16): lx.append(f'    <Row><Atlas>CHN1928_CIV_ALPHA_ATLAS</Atlas><IconSize>{size}</IconSize><Filename>CHN1928_CivWhite{size}.dds</Filename><IconsPerRow>6</IconsPerRow><IconsPerColumn>1</IconsPerColumn></Row>')
    lx += ['  </IconTextureAtlases>', '  <Leaders>']
    for i, (ld, cv, key) in enumerate(LEADER_ART): lx.append(f'    <Update><Where Type="{ld}" /><Set ArtDefineTag="CHN1928_{key}_Scene.xml" PortraitIndex="{i}" IconAtlas="CHN1928_LEADER_ATLAS" /></Update>')
    lx += ['  </Leaders>', '  <Civilizations>']
    for i, (ld, cv, key) in enumerate(LEADER_ART): lx.append(f'    <Update><Where Type="{cv}" /><Set PortraitIndex="{i}" IconAtlas="CHN1928_CIV_COLOR_ATLAS" AlphaIconAtlas="CHN1928_CIV_ALPHA_ATLAS" DawnOfManImage="CHN1928_DOM_{key}.dds" /></Update>')
    lx += ['  </Civilizations>', '</GameData>', '']
    open(os.path.join(OUT_DIR, 'China1928_Leaders.xml'), 'w').write('\n'.join(lx))
def filerow(fn, imp): return f'    <File md5="{md5(os.path.join(OUT_DIR, fn))}" import="{imp}">{fn}</File>'
FILES_XML = '\n'.join([filerow('China1928.Civ5Map', 1), filerow('China1928_Rules.xml', 0)] + [filerow(fn, 0) for fn in UI_FILES if os.path.exists(os.path.join(OUT_DIR, fn))]
                      + ([filerow('China1928_Leaders.xml', 0), filerow('CREDITS.txt', 0)] if art_files else []) + [filerow(f, 1) for f in scene_files] + [filerow(f, 1) for f in art_files])
LEADERS_DB = '      <UpdateDatabase>China1928_Leaders.xml</UpdateDatabase>\n' if art_files else ''
MODINFO = f'''<?xml version="1.0" encoding="utf-8"?>
<Mod id="3b7d9e42-1928-4a6c-8f15-c2e0d4b7a913" version="1">
  <Properties>
    <Name>China 1928</Name>
    <Teaser>China in the warlord era from 10 October 1928: Chiang Kai-shek, Feng Yuxiang, Yan Xishan, Zhang Xueliang, the Guangxi clique and the Communists on a {W}x{H} map from the Amur to Tonkin.</Teaser>
    <Description>China from Manchuria to Yunnan as of 10 October 1928, the day Chiang Kai-shek became Chairman of the National Government after the Northern Expedition. Six sides: the National Government at Nanjing (China donor), Feng Yuxiang's Guominjun (Zulu), Yan Xishan's Shanxi (Russia), Zhang Xueliang's Fengtian clique in Manchuria (Germany), the New Guangxi clique of Li Zongren (Ethiopia) and the Chinese Communists of Mao Zedong and Zhu De (Shoshone). Japan with Korea, Taiwan and the Kwantung Leased Territory, the Soviet Far East, Mongolia, the militarists of Sichuan, Chongqing, Yunnan, Guizhou, Guangdong and Qinghai, Hong Kong, Macau, Weihaiwei and French Indochina are city-states; bandits and secret societies are raging barbarians. One turn is one week; dated events bring the Northeast Flag Replacement, the Chiang-Guangxi war, the Sino-Soviet conflict of 1929, the Central Plains War, the encirclement campaigns, the Mukden incident, Manchukuo, the Shanghai incident, the Long March, the Xi'an incident and the Marco Polo Bridge. A unique unit and building for every side. The leaders are historical figures; their dialogue is invented. Domination victory only. Start it from the Mods menu via the scenario button.</Description>
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
      <UpdateDatabase>China1928_Rules.xml</UpdateDatabase>
      <UpdateDatabase>China1928_Uniques.sql</UpdateDatabase>
{LEADERS_DB}      <UpdateDatabase>China1928_Text.xml</UpdateDatabase>
    </OnModActivated>
  </Actions>
  <EntryPoints>
    <EntryPoint type="Custom" file="China1928LoadScreen.xml">
      <Name>China 1928</Name>
      <Description>October 1928: Nanjing, the Guominjun, Shanxi, Fengtian, Guangxi and the Communists. Choose your side and difficulty.</Description>
    </EntryPoint>
    <EntryPoint type="InGameUIAddin" file="China1928_Production.xml">
      <Name>China 1928 setup</Name>
      <Description>Production queues, unit names, alliances, weekly calendar.</Description>
    </EntryPoint>
    <EntryPoint type="InGameUIAddin" file="China1928_Events.xml">
      <Name>China 1928 events</Name>
      <Description>Dated events of the warlord era, October 1928 to July 1937.</Description>
    </EntryPoint>
  </EntryPoints>
</Mod>
'''
open(os.path.join(OUT_DIR, 'China1928.modinfo'), 'w').write(MODINFO)

# ============================================================== preview
S = 10
img = Image.new('RGB', (int((W + 0.5) * S) + 2, int(H * S * 0.866 + S) + 2), (10, 30, 70)); d = ImageDraw.Draw(img)
TCOL = {GRASS: (96, 168, 64), PLAINS: (196, 178, 96), DESERT: (236, 214, 150), TUNDRA: (170, 170, 150), SNOW: (240, 240, 240), COAST: (70, 140, 210), OCEAN: (20, 60, 130)}
# side colours, also used for the legend swatches of publish/make_screens.py: land is filled in its holder's colour, relief only as a shade
OCOL = {NAN: (38, 78, 200), GMJ: (112, 142, 46), SHX: (150, 92, 42), FT: (238, 192, 24), GX: (30, 172, 168), CCP: (214, 32, 46), BARB: (0, 0, 0)}
CS_COL = (150, 150, 150); FREE_COL = (226, 221, 205)
def pcenter(x, y): return (x + 0.5 + 0.5 * (y & 1)) * S + 1, img.size[1] - (y * 0.866 * S + 0.577 * S) - 1
def pcorners(x, y, f=1.0):
    cx, cy = pcenter(x, y); r = S / math.sqrt(3) * f
    return [(cx + r * math.cos(math.radians(30 + 60 * k)), cy - r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
def shade(c, k): return tuple(int(v * k) for v in c)
for y in range(H):
    for x in range(W):
        o = int(owner[y, x])
        if not is_land[y, x]: col = (90, 170, 230) if is_lake[y, x] else TCOL[terrain[y, x]]
        else:
            base = OCOL[o] if o < NP else CS_COL if o != NONE else FREE_COL
            col = shade(base, 0.82 if elev[y, x] == 2 else 0.92 if elev[y, x] == 1 else 1.0)
        d.polygon(pcorners(x, y), fill=col)
        cx, cy = pcenter(x, y)
        if is_land[y, x] and elev[y, x] == 2: d.polygon([(cx - 3, cy + 2), (cx, cy - 3), (cx + 3, cy + 2)], fill=shade(col, 0.7))
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
    if popk >= 40 or 'cap' in tags: d.text((cx + 4, cy - 5), name, fill=(255, 255, 255))
img.save(OUT_PNG); print('wrote', OUT_PNG, img.size)
