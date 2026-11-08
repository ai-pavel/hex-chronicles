#!/usr/bin/env python3
"""China 1928 leader and side art (ImageMagick): round portraits in Civ-style rings, emblem discs, white glyphs, static diplomacy scenes and Dawn of Man images."""
import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'src'); OUT = os.path.join(HERE, 'out'); TMP = os.path.join(HERE, 'tmp')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
def M(*args):
    r = subprocess.run(['magick'] + [str(a) for a in args], capture_output=True, text=True)
    if r.returncode: raise SystemExit('magick failed: ' + ' '.join(map(str, args)) + '\n' + r.stderr)
# key, portrait (None = emblem portrait), face crop (size,x,y), flag stripe colours, emblem file, disc colour
LEADERS = [
    ('Chiang', 'chiang.jpg', (620, 125, 40),   ('#FFFFFF', '#1F3C99'), 'emb_nan.png',      '#1F3C99'),
    ('Feng',   'feng.jpg',   (640, 250, 20),   ('#F2E6C8', '#556B2F'), 'emb_feng.png',     '#556B2F'),
    ('Yan',    'yan.jpg',    (1000, 360, 120), ('#F5D76E', '#7B4A22'), 'emb_yan.png',      '#E9DCC0'),
    ('Zhang',  'zhang.jpg',  (700, 300, 200),  ('#1A1A1A', '#E8B400'), 'emb_fengtian.png', '#E8B400'),
    ('Li',     'li.jpg',     (384, 0, 140),   ('#FFFFFF', '#1E8A8A'), 'emb_gx.png',       '#1E8A8A'),
    ('Mao',    'mao.jpg',    (400, 10, 20),    ('#FFD700', '#C8102E'), 'emb_ccp.png',      '#C8102E'),
]
RING = ['(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60', ')', '-composite',
        '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54', ')', '-composite',
        '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#7a5c1e', '-strokewidth', '4', '-draw', 'circle 256,256 256,70', ')', '-composite']
# white glyphs for the unit flags and the alpha atlas: silhouettes of the star and the seal, simple shapes for the flags, the hammer and sickle
SUN = ['-draw', 'circle 256,256 256,166'] + sum([['-draw', 'polygon %d,%d %d,%d %d,%d' % (256 + 200 * __import__('math').cos(a0), 256 + 200 * __import__('math').sin(a0),
        256 + 110 * __import__('math').cos(a0 - 0.2618), 256 + 110 * __import__('math').sin(a0 - 0.2618), 256 + 110 * __import__('math').cos(a0 + 0.2618), 256 + 110 * __import__('math').sin(a0 + 0.2618))]
        for a0 in [i * 3.14159265 / 6 - 3.14159265 / 2 for i in range(12)]], [])
GLYPH = {'Chiang': ('sun', None), 'Zhang': ('stripes', None), 'Li': ('canton', None), 'Mao': ('keyed', 'glyph_ccp.png')}
faces = []; emblems = []
for key, img, crop, cols, emb, disc in LEADERS:
    raw = os.path.join(TMP, f'embraw_{key}.png'); col = os.path.join(TMP, f'emb_{key}.png'); wht = os.path.join(TMP, f'embw_{key}.png')
    M(os.path.join(SRC, emb), '-background', 'none', '-gravity', 'center', '-resize', '250x250' if key == 'Yan' else '300x300', '-extent', '512x512', raw)   # the square seal must fit the disc
    M('-size', '512x512', 'xc:none', '-fill', disc, '-draw', 'circle 256,256 256,66', *RING, raw, '-compose', 'over', '-composite', col)
    mode, gfile = GLYPH.get(key, ('alpha', None))
    if mode == 'sun':         # the white sun of the Kuomintang emblem
        M('-size', '512x512', 'xc:none', '-fill', 'white', *SUN, wht)
    elif mode == 'stripes':   # the five stripes of the Beiyang flag
        M('-size', '512x512', 'xc:none', '-fill', 'white', *sum([['-draw', f'rectangle 66,{110 + 62 * i} 446,{148 + 62 * i}'] for i in range(5)], []), wht)
    elif mode == 'canton':    # the national flag: the canton with its sun, the red field as a frame
        M('-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', 'white', '-strokewidth', '28', '-draw', 'rectangle 70,120 442,392', '-stroke', 'none', '-fill', 'white',
          '-draw', 'rectangle 70,120 270,270', wht)
    elif mode == 'keyed':     # the yellow hammer and sickle on its red field
        M(os.path.join(SRC, gfile), '-fuzz', '35%', '-fill', 'none', '-opaque', '#CC0000', '-fill', 'white', '-colorize', '100', '-background', 'none', '-gravity', 'center', '-resize', '400x400', '-extent', '512x512', wht)
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
    p = os.path.join(TMP, f'leaders_{size}.png'); row(faces, size, p); dds(p, os.path.join(OUT, f'CHN1928_Leaders{size}.dds'))
for size in (256, 128, 80, 64, 45, 32):
    p = os.path.join(TMP, f'civcol_{size}.png'); row([c for c, w in emblems], size, p); dds(p, os.path.join(OUT, f'CHN1928_CivColor{size}.dds'))
for size in (128, 64, 48, 32, 24, 16):
    p = os.path.join(TMP, f'civwht_{size}.png'); row([w for c, w in emblems], size, p); dds(p, os.path.join(OUT, f'CHN1928_CivWhite{size}.dds'))
# the scenes and Dawn of Man images use the photograph only: Zhang's portrait is a scanned page with its frame and caption
SCENE_CROP = {'Zhang': '1170x1690+65+75'}
for i, (key, img, crop, (c1, c2), emb, disc) in enumerate(LEADERS):
    src = os.path.join(SRC, img) if img else None
    if key in SCENE_CROP: src = os.path.join(TMP, f'photo_{key}.png'); M(os.path.join(SRC, img), '-crop', SCENE_CROP[key], '+repage', src)
    col, wht = emblems[i]; scene = os.path.join(TMP, f'scene_{key}.png'); dom = os.path.join(TMP, f'dom_{key}.png')
    subject = ['(', src, '-resize', 'x1000', ')', '-gravity', 'southeast', '-geometry', '+120+0', '-composite'] if img else \
              ['(', os.path.join(SRC, emb), '-background', 'none', '-resize', '700x700', ')', '-gravity', 'east', '-geometry', '+200+0', '-composite']
    M('-size', '2048x1024', 'gradient:#1b1510-#3a2a1c', '(', '-size', '2048x1024', 'radial-gradient:#5a4428-#1b1510', '-alpha', 'set', '-channel', 'A', '-evaluate', 'set', '45%', '+channel', ')', '-compose', 'over', '-composite',
      '(', col, '-resize', '620x620', '-alpha', 'set', '-channel', 'A', '-evaluate', 'multiply', '0.18', '+channel', ')', '-gravity', 'west', '-geometry', '+160+0', '-composite', *subject,
      '(', '-size', '2048x14', f'xc:{c1}', ')', '-gravity', 'south', '-geometry', '+0+14', '-composite', '(', '-size', '2048x14', f'xc:{c2}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', scene)
    dds(scene, os.path.join(OUT, f'CHN1928_Scene_{key}.dds'), 'dxt1')
    dsub = ['(', src, '-resize', '1024x1024^', '-gravity', 'north', '-extent', '1024x1024', '(', '-size', '1024x1024', 'gradient:white-black', ')', '-compose', 'CopyOpacity', '-composite', ')', '-compose', 'over', '-gravity', 'center', '-composite'] if img else \
           ['(', os.path.join(SRC, emb), '-background', 'none', '-resize', '640x640', ')', '-gravity', 'center', '-compose', 'over', '-composite']
    M('-size', '1024x1024', 'gradient:#3a2a1c-#120e0a', *dsub, '(', '-size', '1024x12', f'xc:{c1}', ')', '-gravity', 'south', '-geometry', '+0+12', '-composite', '(', '-size', '1024x12', f'xc:{c2}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', dom)
    dds(dom, os.path.join(OUT, f'CHN1928_DOM_{key}.dds'), 'dxt1')
M(*faces, '+append', os.path.join(TMP, 'r1.png')); M(*[c for c, w in emblems], '+append', os.path.join(TMP, 'r2.png')); M(*[['(', w, '-background', '#444', '-flatten', ')'] for c, w in emblems][0], *sum([['(', w, '-background', '#444', '-flatten', ')'] for c, w in emblems[1:]], []), '+append', os.path.join(TMP, 'r3.png'))
M(os.path.join(TMP, 'r1.png'), os.path.join(TMP, 'r2.png'), os.path.join(TMP, 'r3.png'), '-background', '#444', '-append', '-resize', '900x', os.path.join(TMP, 'contact.png'))
print('art written:', sorted(os.listdir(OUT)))
