#!/usr/bin/env python3
"""Spain 1936 leader and side art (ImageMagick): round portraits in Civ-style rings, emblem discs, white glyphs, static diplomacy scenes and Dawn of Man images."""
import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'src'); OUT = os.path.join(HERE, 'out'); TMP = os.path.join(HERE, 'tmp')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
def M(*args):
    r = subprocess.run(['magick'] + [str(a) for a in args], capture_output=True, text=True)
    if r.returncode: raise SystemExit('magick failed: ' + ' '.join(map(str, args)) + '\n' + r.stderr)
# key, portrait (None = emblem portrait), face crop (size,x,y), flag stripe colours, emblem file, disc colour
LEADERS = [
    ('Azana',    'azana.jpg',    (640, 110, 50),   ('#F1BF00', '#5B2A6E'), 'emb_rep.png',   '#5B2A6E'),
    ('Franco',   'franco.jpg',   (1000, 75, 70),   ('#AA151B', '#F1BF00'), 'emb_nat.png',   '#AA151B'),
    ('Mola',     'mola.jpg',     (600, 315, 20),   ('#F2F2F2', '#C8102E'), 'emb_north.png', '#F2F2F2'),
    ('Companys', 'companys.jpg', (800, 30, 130),   ('#FCDD09', '#DA121A'), 'emb_cat.png',   '#FCDD09'),
    ('Aguirre',  'aguirre.jpg',  (230, 4, 8),      ('#D52B1E', '#00843D'), 'emb_euz.png',   '#00843D'),
    ('Durruti',  'durruti.jpg',  (640, 130, 90),   ('#E30613', '#141414'), 'emb_cnt.png',   '#141414'),
]
RING = ['(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60', ')', '-composite',
        '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54', ')', '-composite',
        '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#7a5c1e', '-strokewidth', '4', '-draw', 'circle 256,256 256,70', ')', '-composite']
# white glyphs for the unit flags and the alpha atlas: flags are drawn as simple shapes, the Republican arms as a silhouette
GLYPH = {'Franco': ('bands', None), 'Mola': ('saltire', None), 'Companys': ('bars', None), 'Aguirre': ('ikurrina', None), 'Durruti': ('diagonal', None)}
# Franco's photo is the only colour one: shown in grey like the other five, so the leader screens match
GREY = {'franco.jpg'}
for img in sorted(GREY): M(os.path.join(SRC, img), '-colorspace', 'Gray', '-colorspace', 'sRGB', os.path.join(TMP, 'grey_' + img))
def photo(img): return os.path.join(TMP, 'grey_' + img) if img in GREY else os.path.join(SRC, img)
faces = []; emblems = []
for key, img, crop, cols, emb, disc in LEADERS:
    raw = os.path.join(TMP, f'embraw_{key}.png'); col = os.path.join(TMP, f'emb_{key}.png'); wht = os.path.join(TMP, f'embw_{key}.png')
    M(os.path.join(SRC, emb), '-background', 'none', '-gravity', 'center', '-resize', '300x300', '-extent', '512x512', raw)
    M('-size', '512x512', 'xc:none', '-fill', disc, '-draw', 'circle 256,256 256,66', *RING, raw, '-compose', 'over', '-composite', col)
    mode, gfile = GLYPH.get(key, ('alpha', None))
    if mode == 'bands':      # the red-yellow-red flag: a broad middle band between two thin ones
        M('-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'rectangle 66,150 446,180', '-draw', 'rectangle 66,206 446,306', '-draw', 'rectangle 66,332 446,362', wht)
    elif mode == 'saltire':    # the Cross of Burgundy
        M('-size', '512x512', 'xc:none', '-stroke', 'white', '-strokewidth', '70', '-draw', 'line 90,110 422,402', '-draw', 'line 422,110 90,402', wht)
    elif mode == 'bars':       # the four bars of the Senyera
        M('-size', '512x512', 'xc:none', '-fill', 'white', *sum([['-draw', f'rectangle 66,{140 + 64 * i} 446,{172 + 64 * i}'] for i in range(4)], []), wht)
    elif mode == 'ikurrina':   # saltire and cross
        M('-size', '512x512', 'xc:none', '-stroke', 'white', '-strokewidth', '44', '-draw', 'line 80,120 432,392', '-draw', 'line 432,120 80,392', '-strokewidth', '60', '-draw', 'line 256,90 256,422', '-draw', 'line 70,256 442,256', wht)
    elif mode == 'diagonal':   # the red-and-black flag of the CNT-FAI: its black half
        M('-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'polygon 86,110 426,110 426,402', wht)
    else:
        M(raw, '-background', 'none', '-gravity', 'center', '-resize', '440x440', '-extent', '512x512', '-fill', 'white', '-colorize', '100', wht)
    emblems.append((col, wht))
    f = os.path.join(TMP, f'face_{key}.png')   # PNG32 below: a grey photo must not turn the gold ring grey
    if img:
        sz, x, y = crop; sq = os.path.join(TMP, f'facesq_{key}.png')
        M(photo(img), '-crop', f'{sz}x{sz}+{x}+{y}', '+repage', '-resize', '512x512', '-colorspace', 'sRGB', 'PNG32:' + sq)
        M(sq, '-colorspace', 'sRGB', '(', '-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'circle 256,256 256,66', ')', '-compose', 'CopyOpacity', '-composite', '-compose', 'over', *RING, 'PNG32:' + f)
    else:   # emblem portrait on the faction disc
        M('-size', '512x512', 'xc:none', '-fill', disc, '-draw', 'circle 256,256 256,66', '(', os.path.join(SRC, emb), '-background', 'none', '-resize', '260x260', ')', '-gravity', 'center', '-compose', 'over', '-composite', *RING, 'PNG32:' + f)
    faces.append(f)
def dds(png, out, fmt='dxt5'): M(png, '-define', f'dds:compression={fmt}', '-define', 'dds:mipmaps=0', out)
def row(files, size, out): M(*sum([['(', f, '-resize', f'{size}x{size}', ')'] for f in files], []), '-background', 'none', '+append', out)
for size in (256, 128, 64):
    p = os.path.join(TMP, f'leaders_{size}.png'); row(faces, size, p); dds(p, os.path.join(OUT, f'ESP1936_Leaders{size}.dds'))
for size in (256, 128, 80, 64, 45, 32):
    p = os.path.join(TMP, f'civcol_{size}.png'); row([c for c, w in emblems], size, p); dds(p, os.path.join(OUT, f'ESP1936_CivColor{size}.dds'))
for size in (128, 64, 48, 32, 24, 16):
    p = os.path.join(TMP, f'civwht_{size}.png'); row([w for c, w in emblems], size, p); dds(p, os.path.join(OUT, f'ESP1936_CivWhite{size}.dds'))
for i, (key, img, crop, (c1, c2), emb, disc) in enumerate(LEADERS):
    col, wht = emblems[i]; scene = os.path.join(TMP, f'scene_{key}.png'); dom = os.path.join(TMP, f'dom_{key}.png')
    subject = ['(', photo(img), '-resize', 'x1000', ')', '-gravity', 'southeast', '-geometry', '+120+0', '-composite'] if img else \
              ['(', os.path.join(SRC, emb), '-background', 'none', '-resize', '700x700', ')', '-gravity', 'east', '-geometry', '+200+0', '-composite']
    M('-size', '2048x1024', 'gradient:#1b1510-#3a2a1c', '(', '-size', '2048x1024', 'radial-gradient:#5a4428-#1b1510', '-alpha', 'set', '-channel', 'A', '-evaluate', 'set', '45%', '+channel', ')', '-compose', 'over', '-composite',
      '(', col, '-resize', '620x620', '-alpha', 'set', '-channel', 'A', '-evaluate', 'multiply', '0.18', '+channel', ')', '-gravity', 'west', '-geometry', '+160+0', '-composite', *subject,
      '(', '-size', '2048x14', f'xc:{c1}', ')', '-gravity', 'south', '-geometry', '+0+14', '-composite', '(', '-size', '2048x14', f'xc:{c2}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', scene)
    dds(scene, os.path.join(OUT, f'ESP1936_Scene_{key}.dds'), 'dxt1')
    dsub = ['(', photo(img), '-resize', '1024x1024^', '-gravity', 'north', '-extent', '1024x1024', '(', '-size', '1024x1024', 'gradient:white-black', ')', '-compose', 'CopyOpacity', '-composite', ')', '-compose', 'over', '-gravity', 'center', '-composite'] if img else \
           ['(', os.path.join(SRC, emb), '-background', 'none', '-resize', '640x640', ')', '-gravity', 'center', '-compose', 'over', '-composite']
    M('-size', '1024x1024', 'gradient:#3a2a1c-#120e0a', *dsub, '(', '-size', '1024x12', f'xc:{c1}', ')', '-gravity', 'south', '-geometry', '+0+12', '-composite', '(', '-size', '1024x12', f'xc:{c2}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', dom)
    dds(dom, os.path.join(OUT, f'ESP1936_DOM_{key}.dds'), 'dxt1')
M(*faces, '+append', os.path.join(TMP, 'r1.png')); M(*[c for c, w in emblems], '+append', os.path.join(TMP, 'r2.png')); M(*[['(', w, '-background', '#444', '-flatten', ')'] for c, w in emblems][0], *sum([['(', w, '-background', '#444', '-flatten', ')'] for c, w in emblems[1:]], []), '+append', os.path.join(TMP, 'r3.png'))
M(os.path.join(TMP, 'r1.png'), os.path.join(TMP, 'r2.png'), os.path.join(TMP, 'r3.png'), '-background', '#444', '-append', '-resize', '900x', os.path.join(TMP, 'contact.png'))
print('art written:', sorted(os.listdir(OUT)))
