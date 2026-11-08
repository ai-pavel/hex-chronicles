#!/usr/bin/env python3
"""Russia 1918 leader and faction art (ImageMagick): round portraits in Civ-style rings, emblem discs, white glyphs, static diplomacy scenes and Dawn of Man images."""
import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'src'); OUT = os.path.join(HERE, 'out'); TMP = os.path.join(HERE, 'tmp')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
def M(*args):
    r = subprocess.run(['magick'] + [str(a) for a in args], capture_output=True, text=True)
    if r.returncode: raise SystemExit('magick failed: ' + ' '.join(map(str, args)) + '\n' + r.stderr)
# key, portrait (None = emblem portrait), face crop (size,x,y), flag stripe colours, emblem file, disc colour
LEADERS = [
    ('Lenin',       'lenin.jpg',       (1500, 150, 120), ('#B00000', '#FFD700'), 'emb_red.png',   '#8B0000'),
    ('Denikin',     'denikin.jpg',     (518, 0, 0),      ('#FFFFFF', '#1F4E9A'), 'emb_white.png', '#F2F2F2'),
    ('Kolchak',     'kolchak.jpg',     (1000, 80, 160),  ('#FFFFFF', '#2E7D32'), 'emb_sib.png',   '#2E7D32'),
    ('Yudenich',    'yudenich.jpg',    (800, 50, 60),    ('#FFFFFF', '#0B3D91'), 'emb_north.png', '#0B3D91'),
    ('Skoropadsky', 'skoropadsky.jpg', (500, 12, 30),    ('#005BBB', '#FFD500'), 'emb_ukr.png',   '#005BBB'),
    ('Pilsudski',   'pilsudski.jpg',   (1100, 300, 60),  ('#FFFFFF', '#DC143C'), 'emb_pol.png',   '#DC143C'),
]
RING = ['(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60', ')', '-composite',
        '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54', ')', '-composite',
        '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#7a5c1e', '-strokewidth', '4', '-draw', 'circle 256,256 256,70', ')', '-composite']
GLYPH = {'Lenin': ('file', 'glyph_red.png'), 'Kolchak': ('triangle', None), 'Yudenich': ('saltire', None), 'Pilsudski': ('light', None)}
faces = []; emblems = []
for key, img, crop, cols, emb, disc in LEADERS:
    raw = os.path.join(TMP, f'embraw_{key}.png'); col = os.path.join(TMP, f'emb_{key}.png'); wht = os.path.join(TMP, f'embw_{key}.png')
    M(os.path.join(SRC, emb), '-background', 'none', '-gravity', 'center', '-resize', '300x300', '-extent', '512x512', raw)
    M('-size', '512x512', 'xc:none', '-fill', disc, '-draw', 'circle 256,256 256,66', *RING, raw, '-compose', 'over', '-composite', col)
    mode, gfile = GLYPH.get(key, ('alpha', None))
    if mode == 'file':      # separate glyph image (gold hammer and sickle on a red square): knock the red out, then paint white
        M(os.path.join(SRC, gfile), '-fuzz', '15%', '-transparent', 'srgb(204,0,0)', '-background', 'none', '-gravity', 'center', '-resize', '440x440', '-extent', '512x512', '-fill', 'white', '-colorize', '100', wht)
    elif mode == 'light':   # bright parts of the emblem become the glyph (the white eagle on the red shield)
        M(os.path.join(SRC, emb), '-background', 'black', '-flatten', '-colorspace', 'Gray', '-threshold', '60%', '-gravity', 'center', '-resize', '440x440', '-extent', '512x512', '-background', 'black', '-flatten',
          '(', '+clone', ')', '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', '-fill', 'white', '-colorize', '100', wht)
    elif mode == 'triangle':   # the Siberian flag: its green half as a glyph
        M('-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'polygon 66,150 446,362 66,362', wht)
    elif mode == 'saltire':    # St Andrew's cross
        M('-size', '512x512', 'xc:none', '-stroke', 'white', '-strokewidth', '70', '-draw', 'line 70,130 442,382', '-draw', 'line 442,130 70,382', wht)
    else:
        M(raw, '-background', 'none', '-gravity', 'center', '-resize', '440x440', '-extent', '512x512', '-fill', 'white', '-colorize', '100', wht)
    emblems.append((col, wht))
    f = os.path.join(TMP, f'face_{key}.png')   # PNG32 below: a grey photo must not turn the gold ring grey
    if img:
        sz, x, y = crop; sq = os.path.join(TMP, f'facesq_{key}.png')
        M(os.path.join(SRC, img), '-crop', f'{sz}x{sz}+{x}+{y}', '+repage', '-resize', '512x512', '-colorspace', 'sRGB', 'PNG32:' + sq)
        M(sq, '-colorspace', 'sRGB', '(', '-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'circle 256,256 256,66', ')', '-compose', 'CopyOpacity', '-composite', '-compose', 'over', *RING, 'PNG32:' + f)
    else:   # emblem portrait on the faction disc
        M('-size', '512x512', 'xc:none', '-fill', disc, '-draw', 'circle 256,256 256,66', '(', os.path.join(SRC, emb), '-background', 'none', '-resize', '260x260', ')', '-gravity', 'center', '-compose', 'over', '-composite', *RING, 'PNG32:' + f)
    faces.append(f)
def dds(png, out, fmt='dxt5'): M(png, '-define', f'dds:compression={fmt}', '-define', 'dds:mipmaps=0', out)
def row(files, size, out): M(*sum([['(', f, '-resize', f'{size}x{size}', ')'] for f in files], []), '-background', 'none', '+append', out)
for size in (256, 128, 64):
    p = os.path.join(TMP, f'leaders_{size}.png'); row(faces, size, p); dds(p, os.path.join(OUT, f'RUS1918_Leaders{size}.dds'))
for size in (256, 128, 80, 64, 45, 32):
    p = os.path.join(TMP, f'civcol_{size}.png'); row([c for c, w in emblems], size, p); dds(p, os.path.join(OUT, f'RUS1918_CivColor{size}.dds'))
for size in (128, 64, 48, 32, 24, 16):
    p = os.path.join(TMP, f'civwht_{size}.png'); row([w for c, w in emblems], size, p); dds(p, os.path.join(OUT, f'RUS1918_CivWhite{size}.dds'))
for i, (key, img, crop, (c1, c2), emb, disc) in enumerate(LEADERS):
    col, wht = emblems[i]; scene = os.path.join(TMP, f'scene_{key}.png'); dom = os.path.join(TMP, f'dom_{key}.png')
    subject = ['(', os.path.join(SRC, img), '-resize', 'x1000', ')', '-gravity', 'southeast', '-geometry', '+120+0', '-composite'] if img else \
              ['(', os.path.join(SRC, emb), '-background', 'none', '-resize', '700x700', ')', '-gravity', 'east', '-geometry', '+200+0', '-composite']
    M('-size', '2048x1024', 'gradient:#1b1510-#3a2a1c', '(', '-size', '2048x1024', 'radial-gradient:#5a4428-#1b1510', '-alpha', 'set', '-channel', 'A', '-evaluate', 'set', '45%', '+channel', ')', '-compose', 'over', '-composite',
      '(', col, '-resize', '620x620', '-alpha', 'set', '-channel', 'A', '-evaluate', 'multiply', '0.18', '+channel', ')', '-gravity', 'west', '-geometry', '+160+0', '-composite', *subject,
      '(', '-size', '2048x14', f'xc:{c1}', ')', '-gravity', 'south', '-geometry', '+0+14', '-composite', '(', '-size', '2048x14', f'xc:{c2}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', scene)
    dds(scene, os.path.join(OUT, f'RUS1918_Scene_{key}.dds'), 'dxt1')
    dsub = ['(', os.path.join(SRC, img), '-resize', '1024x1024^', '-gravity', 'north', '-extent', '1024x1024', '(', '-size', '1024x1024', 'gradient:white-black', ')', '-compose', 'CopyOpacity', '-composite', ')', '-compose', 'over', '-gravity', 'center', '-composite'] if img else \
           ['(', os.path.join(SRC, emb), '-background', 'none', '-resize', '640x640', ')', '-gravity', 'center', '-compose', 'over', '-composite']
    M('-size', '1024x1024', 'gradient:#3a2a1c-#120e0a', *dsub, '(', '-size', '1024x12', f'xc:{c1}', ')', '-gravity', 'south', '-geometry', '+0+12', '-composite', '(', '-size', '1024x12', f'xc:{c2}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', dom)
    dds(dom, os.path.join(OUT, f'RUS1918_DOM_{key}.dds'), 'dxt1')
M(*faces, '+append', os.path.join(TMP, 'r1.png')); M(*[c for c, w in emblems], '+append', os.path.join(TMP, 'r2.png')); M(*[['(', w, '-background', '#444', '-flatten', ')'] for c, w in emblems][0], *sum([['(', w, '-background', '#444', '-flatten', ')'] for c, w in emblems[1:]], []), '+append', os.path.join(TMP, 'r3.png'))
M(os.path.join(TMP, 'r1.png'), os.path.join(TMP, 'r2.png'), os.path.join(TMP, 'r3.png'), '-background', '#444', '-append', '-resize', '900x', os.path.join(TMP, 'contact.png'))
print('art written:', sorted(os.listdir(OUT)))
