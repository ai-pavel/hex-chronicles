#!/usr/bin/env python3
"""Build the Hawaii 1778 art with ImageMagick from the generated sources.

  python3 build_art.py pick      copy the variants named in SELECT from art/gen (generate_art.py output) into art/src
  python3 build_art.py           build art/out from art/src: round portrait atlases (faces cut from the scenes), civ symbol atlases
                                 (colour + white), unit, unit-flag and building icon atlases, diplomacy fallback scenes (2048x1024)
                                 and Dawn of Man images (1024x1024), all DDS; the processed pieces go to art/cut and the preview rows
                                 to art/preview_*.png
  python3 build_art.py preview   contact sheet of the processed faces, emblems and icons in art/tmp
"""
import os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.join(HERE, 'gen'); SRC = os.path.join(HERE, 'src'); OUT = os.path.join(HERE, 'out'); TMP = os.path.join(HERE, 'tmp'); CUT = os.path.join(HERE, 'cut')
for d in (SRC, OUT, TMP, CUT): os.makedirs(d, exist_ok=True)
sys.path.insert(0, os.path.join(HERE, '..', 'text')); import uniques
def M(*args):
    r = subprocess.run(['magick'] + [str(a) for a in args], capture_output=True, text=True)
    if r.returncode: raise SystemExit('magick failed: ' + ' '.join(map(str, args)) + '\n' + r.stderr)

# slot order = the generator's PLAYERS order; (icon colour, disc colour) as in text/build_text.py
LEADERS = [('KONA', 'Kamehameha', '#FFD700', '#B22222'), ('HILO', 'Keoua', '#F4F4F4', '#1C1C1C'), ('MAUI', 'Kahekili', '#FFFFFF', '#C71585'),
           ('OAHU', 'Kahahana', '#FFD54A', '#1F3A93'), ('KAUAI', 'Kamakahelei', '#F0E68C', '#4B0082')]
UNIT_KEYS = [u['key'] for u in uniques.UNITS]                        # icon order = PortraitIndex order in the generator (clones and renamed donor units alike)
IMP_KEYS = [b['key'] for b in uniques.BUILDINGS if b.get('improvement')]
BLD_KEYS = [b['key'] for b in uniques.BUILDINGS if b['base']]
# chosen variant per key and kind
SELECT = {'KONA': dict(scene=2, emblem=2), 'HILO': dict(scene=1, emblem=1), 'MAUI': dict(scene=2, emblem=2), 'OAHU': dict(scene=2, emblem=1), 'KAUAI': dict(scene=2, emblem=2),
          'OLOHE': dict(unit=2), 'MAA': dict(unit=2), 'KOA': dict(unit=1), 'POLOLU': dict(unit=2), 'PELELEU': dict(unit=1),
          'PUUHONUA': dict(building=2), 'LOKOIA': dict(building=1), 'LOIKALO': dict(building=1), 'KII': dict(improvement=1, action=2),
          **{r: dict(religion=v) for r, v in zip(('BUDDHISM', 'CHRISTIANITY', 'CONFUCIANISM', 'HINDUISM', 'ISLAM', 'JUDAISM', 'SHINTO', 'SIKHISM', 'TAOISM', 'TENGRIISM', 'ZOROASTRIANISM', 'ORTHODOXY', 'PROTESTANTISM'), [2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1])}}
RELIGIONS = ['BUDDHISM', 'CHRISTIANITY', 'CONFUCIANISM', 'HINDUISM', 'ISLAM', 'JUDAISM', 'SHINTO', 'SIKHISM', 'TAOISM', 'TENGRIISM', 'ZOROASTRIANISM', 'ORTHODOXY', 'PROTESTANTISM']   # stock slots the native cults replace, in PortraitIndex order
# face square in the 1792x1024 scene: (size, x, y)
FACE = {'KONA': (300, 375, 60), 'HILO': (260, 240, 60), 'MAUI': (320, 290, 100), 'OAHU': (260, 290, 60), 'KAUAI': (200, 185, 220)}

stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
if stage == 'pick':
    for k, sel in SELECT.items():
        for kind, v in sel.items():
            src = os.path.join(GEN, f'{k}_{kind}_{v}.png')
            if not os.path.exists(src): raise SystemExit('missing ' + src)
            shutil.copy(src, os.path.join(SRC, f'{k}_{kind}.png'))
    print('picked into', SRC); sys.exit(0)

RING = ['-compose', 'over', '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60', ')', '-composite',
        '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54', ')', '-composite']
def round_frame(sq, out):
    M(sq, '(', '-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'circle 256,256 256,66', ')', '-compose', 'CopyOpacity', '-composite', *RING,
      '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#7a5c1e', '-strokewidth', '4', '-draw', 'circle 256,256 256,70', ')', '-composite', out)
def glyph_from(src, mask, out, fill, size=400):
    M(src, '-colorspace', 'Gray', '-blur', '0x1', '-threshold', '55%', '-negate', '-trim', '+repage', '-background', 'black', '-gravity', 'center', '-resize', f'{size}x{size}', '-extent', '512x512', mask)
    M('-size', '512x512', f'xc:{fill}', mask, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', out)

# ---- 1. round portraits cut from the scenes
faces = []
for k, name, icon, bg in LEADERS:
    sq = os.path.join(TMP, f'facesq_{k}.png'); f = os.path.join(TMP, f'face_{k}.png'); size, x, y = FACE[k]
    M(os.path.join(SRC, f'{k}_scene.png'), '-crop', f'{size}x{size}+{x}+{y}', '+repage', '-filter', 'Lanczos', '-resize', '512x512', '-unsharp', '0x1+0.5+0', sq)
    round_frame(sq, f); faces.append(f)
# ---- 2. emblems: white glyph for the alpha atlas, coloured glyph on a disc for the colour atlas
emblems = []
for k, name, icon, bg in LEADERS:
    glyph = os.path.join(TMP, f'glyph_{k}.png'); col = os.path.join(TMP, f'emb_{k}.png'); wht = os.path.join(TMP, f'embw_{k}.png')
    glyph_from(os.path.join(SRC, f'{k}_emblem.png'), os.path.join(TMP, f'embmask_{k}.png'), glyph, 'white')
    M('-size', '512x512', 'xc:none', '-fill', bg, '-draw', 'circle 256,256 256,66', '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60',
      '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54', '(', glyph, '-resize', '300x300', '-fill', icon, '-colorize', '100', ')', '-gravity', 'center', '-compose', 'over', '-composite', col)
    M(glyph, '-background', 'none', '-gravity', 'center', '-resize', '440x440', '-extent', '512x512', wht)
    emblems.append((col, wht))
# ---- 3. unit icons (white glyphs) and building icons (painted, round frame)
unit_icons = []; unit_glyphs = []
COLOR_OF = {k: (icon, bg) for k, name, icon, bg in LEADERS}
PEOPLE_OF = {u['key']: u['people'] for u in uniques.UNITS}
for k in UNIT_KEYS:
    gw = os.path.join(TMP, f'unitw_{k}.png'); g = os.path.join(TMP, f'unit_{k}.png'); icon, bg = COLOR_OF[PEOPLE_OF[k]]
    glyph_from(os.path.join(SRC, f'{k}_unit.png'), os.path.join(TMP, f'umask_{k}.png'), gw, 'white', 340)   # white glyph for the flag atlas
    # the icon itself: the chiefdom's disc and ring, the silhouette in the chiefdom's icon colour
    M('-size', '512x512', 'xc:none', '-fill', bg, '-draw', 'circle 256,256 256,66', '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60',
      '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54', '(', gw, '-fill', icon, '-colorize', '100', ')', '-gravity', 'center', '-compose', 'over', '-composite', g)
    unit_icons.append(g); unit_glyphs.append(gw)
bld_icons = []
for k in BLD_KEYS:
    sq = os.path.join(TMP, f'bsq_{k}.png'); b = os.path.join(TMP, f'bld_{k}.png')
    M(os.path.join(SRC, f'{k}_building.png'), '-resize', '512x512^', '-gravity', 'center', '-extent', '512x512', sq)
    M(sq, '(', '-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'circle 256,256 256,66', ')', '-compose', 'CopyOpacity', '-composite', *RING, b); bld_icons.append(b)
imp_icons = []; act_icons = []
for k in IMP_KEYS:
    sq = os.path.join(TMP, f'isq_{k}.png'); b = os.path.join(TMP, f'imp_{k}.png'); a = os.path.join(TMP, f'act_{k}.png')
    M(os.path.join(SRC, f'{k}_improvement.png'), '-resize', '512x512^', '-gravity', 'center', '-extent', '512x512', sq)
    M(sq, '(', '-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'circle 256,256 256,66', ')', '-compose', 'CopyOpacity', '-composite', *RING, b); imp_icons.append(b)
    glyph_from(os.path.join(SRC, f'{k}_action.png'), os.path.join(TMP, f'amask_{k}.png'), a, 'white', 440); act_icons.append(a)
rel_icons = []
for k in RELIGIONS:
    if not os.path.exists(os.path.join(SRC, f'{k}_religion.png')): continue
    g = os.path.join(TMP, f'rel_{k}.png'); glyph_from(os.path.join(SRC, f'{k}_religion.png'), os.path.join(TMP, f'rmask_{k}.png'), g, 'white', 440); rel_icons.append(g)
if stage == 'preview':
    sheet = os.path.join(TMP, 'contact.png')
    M(*faces, '+append', os.path.join(TMP, 'row1.png')); M(*[c for c, w in emblems], '+append', os.path.join(TMP, 'row2.png'))
    M(*sum([['(', w, '-background', '#444', '-flatten', ')'] for c, w in emblems], []), '+append', os.path.join(TMP, 'row3.png'))
    M(*unit_icons, '+append', os.path.join(TMP, 'row4.png'))
    M(*bld_icons, '+append', os.path.join(TMP, 'row5.png'))
    M(os.path.join(TMP, 'row1.png'), os.path.join(TMP, 'row2.png'), os.path.join(TMP, 'row3.png'), os.path.join(TMP, 'row4.png'), os.path.join(TMP, 'row5.png'), '-background', '#444', '-append', '-resize', '1400x', sheet)
    print('preview', sheet); sys.exit(0)

def dds(png, out, fmt='dxt5'): M(png, '-define', f'dds:compression={fmt}', '-define', 'dds:mipmaps=0', out)
def atlas(items, sizes, name, extra=()):
    for size in sizes:
        row = os.path.join(TMP, f'{name}_{size}.png')
        M(*sum([['(', f, *extra, '-resize', f'{size}x{size}', ')'] for f in items], []), '-background', 'none', '+append', row)
        dds(row, os.path.join(OUT, f'HI1778_{name}{size}.dds'))
atlas(faces, (256, 128, 64), 'Leaders')
atlas([c for c, w in emblems], (256, 128, 80, 64, 45, 32), 'CivColor')
atlas([w for c, w in emblems], (128, 64, 48, 32, 24, 16), 'CivWhite')
atlas(unit_icons, (256, 128, 80, 64, 45, 32), 'Units')
atlas(unit_glyphs, (32,), 'UnitFlags')
atlas(bld_icons, (256, 128, 64, 45), 'Buildings')
atlas(imp_icons, (256, 64), 'Improvements')
atlas(act_icons, (64, 45), 'Actions')
if rel_icons: atlas(rel_icons, (128, 80, 64, 48, 32, 24, 16), 'Religions')
# ---- 4. diplomacy fallback scene (2048x1024) and Dawn of Man image (1024x1024), both from the scene
for i, (k, name, icon, bg) in enumerate(LEADERS):
    scene_src = os.path.join(SRC, f'{k}_scene.png'); scene = os.path.join(TMP, f'scene_{k}.png'); dom = os.path.join(TMP, f'dom_{k}.png')
    M(scene_src, '-resize', '2048x', '-gravity', 'center', '-extent', '2048x1024',
      '(', '-size', '2048x14', f'xc:{icon}', ')', '-gravity', 'south', '-geometry', '+0+14', '-composite', '(', '-size', '2048x14', f'xc:{bg}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', scene)
    dds(scene, os.path.join(OUT, f'HI1778_Scene_{k}.dds'), 'dxt1')
    size, fx, fy = FACE[k]; dx = max(0, min(1792 - 1024, fx + size // 2 - 512))
    M('-size', '1024x1024', 'gradient:#1a2230-#0b0f16', '(', scene_src, '-crop', f'1024x1024+{dx}+0', '+repage', '(', '-size', '1024x1024', 'gradient:white-black', ')', '-compose', 'CopyOpacity', '-composite', ')',
      '-compose', 'over', '-gravity', 'center', '-composite', '(', '-size', '1024x12', f'xc:{icon}', ')', '-gravity', 'south', '-geometry', '+0+12', '-composite', '(', '-size', '1024x12', f'xc:{bg}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', dom)
    dds(dom, os.path.join(OUT, f'HI1778_DOM_{k}.dds'), 'dxt1')
# ---- 5. the pieces for the repository and the README rows
for k, name, icon, bg in LEADERS:
    shutil.copy(os.path.join(TMP, f'face_{k}.png'), os.path.join(CUT, f'{k}_face.png')); shutil.copy(os.path.join(TMP, f'emb_{k}.png'), os.path.join(CUT, f'{k}_emblem.png'))
    shutil.copy(os.path.join(TMP, f'embw_{k}.png'), os.path.join(CUT, f'{k}_glyph.png'))
    M(os.path.join(TMP, f'scene_{k}.png'), '-quality', '95', os.path.join(CUT, f'{k}_scene.jpg')); M(os.path.join(TMP, f'dom_{k}.png'), '-quality', '95', os.path.join(CUT, f'{k}_dom.jpg'))
for k in UNIT_KEYS: shutil.copy(os.path.join(TMP, f'unit_{k}.png'), os.path.join(CUT, f'{k}_unit.png'))
for k in BLD_KEYS: shutil.copy(os.path.join(TMP, f'bld_{k}.png'), os.path.join(CUT, f'{k}_building.png'))
for k in IMP_KEYS: shutil.copy(os.path.join(TMP, f'imp_{k}.png'), os.path.join(CUT, f'{k}_improvement.png')); shutil.copy(os.path.join(TMP, f'act_{k}.png'), os.path.join(CUT, f'{k}_action.png'))
for k in RELIGIONS:
    if os.path.exists(os.path.join(TMP, f'rel_{k}.png')): shutil.copy(os.path.join(TMP, f'rel_{k}.png'), os.path.join(CUT, f'{k}_religion.png'))
if rel_icons: M(*sum([['(', r, '-resize', '120x120', '-background', '#3a3a3a', '-flatten', ')'] for r in rel_icons], []), '+append', os.path.join(HERE, 'preview_religions.png'))
M(*sum([['(', f, '-resize', '200x200', ')'] for f in faces], []), '-background', 'none', '+append', os.path.join(HERE, 'preview_faces.png'))
M(*sum([['(', c, '-resize', '200x200', ')'] for c, w in emblems], []), '-background', 'none', '+append', os.path.join(TMP, 'prow1.png'))
M(*sum([['(', w, '-resize', '200x200', '-background', '#3a3a3a', '-flatten', ')'] for c, w in emblems], []), '+append', os.path.join(TMP, 'prow2.png'))
M(os.path.join(TMP, 'prow1.png'), os.path.join(TMP, 'prow2.png'), '-background', 'none', '-append', os.path.join(HERE, 'preview_emblems.png'))
M(*sum([['(', u, '-resize', '200x200', ')'] for u in unit_icons], []), *sum([['(', b, '-resize', '200x200', ')'] for b in bld_icons + imp_icons], []), '-background', 'none', '+append', os.path.join(HERE, 'preview_uniques.png'))
print('art written to', OUT, 'and', CUT); print(sorted(os.listdir(OUT)))
