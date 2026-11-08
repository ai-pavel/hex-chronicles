#!/usr/bin/env python3
"""Build the Canarias 1400 leader art with ImageMagick from the generated sources.

  python3 build_art.py pick      copy the variants named in SELECT from art/gen (generate_art.py output) into art/src;
                                 art/src (the chosen originals) and art/cut (the processed pieces) are what the repository keeps
  python3 build_art.py           build art/out from art/src: round portrait atlases, civ symbol atlases (colour + white),
                                 diplomacy fallback scenes (2048x1024) and Dawn of Man images (1024x1024), all DDS;
                                 also writes the pieces to art/cut and the preview rows art/preview_faces.png, art/preview_emblems.png
  python3 build_art.py preview   contact sheet of the processed faces and emblems in art/tmp
"""
import os, subprocess, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.join(HERE, 'gen'); SRC = os.path.join(HERE, 'src'); OUT = os.path.join(HERE, 'out'); TMP = os.path.join(HERE, 'tmp'); CUT = os.path.join(HERE, 'cut')
for d in (SRC, OUT, TMP, CUT): os.makedirs(d, exist_ok=True)
def M(*args):
    r = subprocess.run(['magick'] + [str(a) for a in args], capture_output=True, text=True)
    if r.returncode: raise SystemExit('magick failed: ' + ' '.join(map(str, args)) + '\n' + r.stderr)

# slot order = the generator's PLAYERS order; (icon colour, disc colour) as in text/build_text.py
LEADERS = [('TENERIFE', 'Bencomo', '#F4F4F4', '#1F3A93'), ('GRANCANARIA', 'Tenesor', '#FFD54A', '#1B6B3A'), ('LAPALMA', 'Tanausu', '#F7F7F7', '#8B1A1A'),
           ('LAGOMERA', 'Hautacuperche', '#9BE27A', '#1E3B2F'), ('ELHIERRO', 'Armiche', '#F8E9A1', '#5B3A29'), ('FUERTEVENTURA', 'Guize', '#2B2B2B', '#E8D7A0'),
           ('LANZAROTE', 'Guadarfia', '#F2C14E', '#6B1E2E')]
# chosen variant per (people, kind): scene, emblem (the portrait and the Dawn of Man image are cut from the scene, so the face is the same everywhere)
SELECT = {'TENERIFE': dict(scene=1, emblem=1, unit=1, building=2), 'GRANCANARIA': dict(scene=2, emblem=2, unit=2, building=2), 'LAPALMA': dict(scene=2, emblem=2, unit=1, building=2),
          'LAGOMERA': dict(scene=2, emblem=2, unit=2), 'ELHIERRO': dict(scene=2, emblem=2, unit=1, building=2), 'FUERTEVENTURA': dict(scene=1, emblem=2, unit=1, building=2),
          'LANZAROTE': dict(scene=2, emblem=2, unit=2, building=2),
          **{r: dict(religion=v) for r, v in zip(('BUDDHISM', 'CHRISTIANITY', 'CONFUCIANISM', 'HINDUISM', 'ISLAM', 'JUDAISM', 'SHINTO', 'SIKHISM', 'TAOISM', 'TENGRIISM', 'ZOROASTRIANISM', 'ORTHODOXY', 'PROTESTANTISM'), [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])}}
RELIGIONS = ['BUDDHISM', 'CHRISTIANITY', 'CONFUCIANISM', 'HINDUISM', 'ISLAM', 'JUDAISM', 'SHINTO', 'SIKHISM', 'TAOISM', 'TENGRIISM', 'ZOROASTRIANISM', 'ORTHODOXY', 'PROTESTANTISM']   # stock slots the native cults replace, in PortraitIndex order
# face square in the 1792x1024 scene: (size, x, y)
FACE = {'TENERIFE': (230, 315, 35), 'GRANCANARIA': (250, 365, 120), 'LAPALMA': (230, 295, 5), 'LAGOMERA': (230, 295, 35), 'ELHIERRO': (250, 345, 180),
        'FUERTEVENTURA': (230, 295, 45), 'LANZAROTE': (270, 285, 50)}

stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
if stage == 'pick':
    for k in SELECT:
        for kind, v in SELECT[k].items():
            if kind == 'building' and k == 'LAGOMERA': continue   # the Gomeros keep the Inca Terrace Farm
            src = os.path.join(GEN, f'{k}_{kind}_{v}.png')
            if not os.path.exists(src): raise SystemExit('missing ' + src)
            shutil.copy(src, os.path.join(SRC, f'{k}_{kind}.png'))
    print('picked into', SRC); sys.exit(0)

# ---- 1. round portraits (Civ V style: dark bronze ring, thin gold rim, transparent corners)
faces = []
for k, name, icon, bg in LEADERS:
    src = os.path.join(SRC, f'{k}_scene.png'); sq = os.path.join(TMP, f'facesq_{k}.png'); f = os.path.join(TMP, f'face_{k}.png')
    size, x, y = FACE[k]
    M(src, '-crop', f'{size}x{size}+{x}+{y}', '+repage', '-filter', 'Lanczos', '-resize', '512x512', '-unsharp', '0x1+0.5+0', sq)
    M(sq, '(', '-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'circle 256,256 256,66', ')', '-compose', 'CopyOpacity', '-composite',
      '-compose', 'over', '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60', ')', '-composite',
      '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54', ')', '-composite',
      '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#7a5c1e', '-strokewidth', '4', '-draw', 'circle 256,256 256,70', ')', '-composite', f)
    faces.append(f)
# ---- 2. emblems: the generated black-on-white symbol becomes an alpha mask; white glyph for the alpha atlas, coloured glyph on a disc for the colour atlas
emblems = []
for k, name, icon, bg in LEADERS:
    src = os.path.join(SRC, f'{k}_emblem.png'); mask = os.path.join(TMP, f'embmask_{k}.png'); glyph = os.path.join(TMP, f'glyph_{k}.png')
    col = os.path.join(TMP, f'emb_{k}.png'); wht = os.path.join(TMP, f'embw_{k}.png')
    # dark pixels -> opaque; trim to the symbol; fit into the cell
    M(src, '-colorspace', 'Gray', '-blur', '0x1', '-threshold', '55%', '-negate', '-trim', '+repage', '-background', 'black', '-gravity', 'center',
      '-resize', '400x400', '-extent', '512x512', mask)
    M('-size', '512x512', 'xc:white', mask, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', glyph)
    M('-size', '512x512', 'xc:none', '-fill', bg, '-draw', 'circle 256,256 256,66',
      '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60',
      '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54',
      '(', glyph, '-resize', '300x300', '-fill', icon, '-colorize', '100', ')', '-gravity', 'center', '-compose', 'over', '-composite', col)
    M(glyph, '-background', 'none', '-gravity', 'center', '-resize', '440x440', '-extent', '512x512', wht)
    emblems.append((col, wht))
# ---- 2b. unit icons (white glyph, Civ V unit atlas style) and building icons (painted, in the round frame)
unit_icons = []; unit_glyphs = []; bld_icons = []
for k, name, icon, bg in LEADERS:
    src = os.path.join(SRC, f'{k}_unit.png'); mask = os.path.join(TMP, f'umask_{k}.png'); g = os.path.join(TMP, f'unit_{k}.png')
    M(src, '-colorspace', 'Gray', '-blur', '0x1', '-threshold', '55%', '-negate', '-trim', '+repage', '-background', 'black', '-gravity', 'center', '-resize', '340x340', '-extent', '512x512', mask)
    gw = os.path.join(TMP, f'unitw_{k}.png'); M('-size', '512x512', 'xc:white', mask, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', gw)   # white glyph for the flag atlas
    # the icon itself: the people's disc and ring, the silhouette in the people's icon colour
    M('-size', '512x512', 'xc:none', '-fill', bg, '-draw', 'circle 256,256 256,66',
      '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60',
      '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54',
      '(', gw, '-fill', icon, '-colorize', '100', ')', '-gravity', 'center', '-compose', 'over', '-composite', g)
    unit_icons.append(g); unit_glyphs.append(gw)
    bsrc = os.path.join(SRC, f'{k}_building.png')
    if os.path.exists(bsrc):
        sq = os.path.join(TMP, f'bsq_{k}.png'); b = os.path.join(TMP, f'bld_{k}.png')
        M(bsrc, '-resize', '512x512^', '-gravity', 'center', '-extent', '512x512', sq)
        M(sq, '(', '-size', '512x512', 'xc:none', '-fill', 'white', '-draw', 'circle 256,256 256,66', ')', '-compose', 'CopyOpacity', '-composite',
          '-compose', 'over', '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#2a1f12', '-strokewidth', '20', '-draw', 'circle 256,256 256,60', ')', '-composite',
          '(', '-size', '512x512', 'xc:none', '-fill', 'none', '-stroke', '#c9a227', '-strokewidth', '6', '-draw', 'circle 256,256 256,54', ')', '-composite', b)
        bld_icons.append(b)
rel_icons = []
for k in RELIGIONS:
    if not os.path.exists(os.path.join(SRC, f'{k}_religion.png')): continue
    mask = os.path.join(TMP, f'rmask_{k}.png'); g = os.path.join(TMP, f'rel_{k}.png')
    M(os.path.join(SRC, f'{k}_religion.png'), '-colorspace', 'Gray', '-blur', '0x1', '-threshold', '55%', '-negate', '-trim', '+repage', '-background', 'black', '-gravity', 'center', '-resize', '440x440', '-extent', '512x512', mask)
    M('-size', '512x512', 'xc:white', mask, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', g); rel_icons.append(g)
if stage == 'preview':
    sheet = os.path.join(TMP, 'contact.png')
    M(*faces, '+append', os.path.join(TMP, 'row1.png')); M(*[c for c, w in emblems], '+append', os.path.join(TMP, 'row2.png'))
    M(*sum([['(', w, '-background', '#444', '-flatten', ')'] for c, w in emblems], []), '+append', os.path.join(TMP, 'row3.png'))
    M(*unit_icons, '+append', os.path.join(TMP, 'row4.png'))
    M(*bld_icons, '+append', os.path.join(TMP, 'row5.png'))
    M(os.path.join(TMP, 'row1.png'), os.path.join(TMP, 'row2.png'), os.path.join(TMP, 'row3.png'), os.path.join(TMP, 'row4.png'), os.path.join(TMP, 'row5.png'), '-background', '#444', '-append', '-resize', '1400x', sheet)
    print('preview', sheet); sys.exit(0)

def dds(png, out, fmt='dxt5'): M(png, '-define', f'dds:compression={fmt}', '-define', 'dds:mipmaps=0', out)
# ---- 3. leader portrait atlas (7 per row) at 256 / 128 / 64
for size in (256, 128, 64):
    row = os.path.join(TMP, f'leaders_{size}.png')
    M(*sum([['(', f, '-resize', f'{size}x{size}', ')'] for f in faces], []), '-background', 'none', '+append', row)
    dds(row, os.path.join(OUT, f'CAN1400_Leaders{size}.dds'))
# ---- 4. civ symbol atlases: colour (256,128,80,64,45,32) and white (128,64,48,32,24,16)
for size in (256, 128, 80, 64, 45, 32):
    row = os.path.join(TMP, f'civcol_{size}.png')
    M(*sum([['(', c, '-resize', f'{size}x{size}', ')'] for c, w in emblems], []), '-background', 'none', '+append', row)
    dds(row, os.path.join(OUT, f'CAN1400_CivColor{size}.dds'))
for size in (128, 64, 48, 32, 24, 16):
    row = os.path.join(TMP, f'civwht_{size}.png')
    M(*sum([['(', w, '-resize', f'{size}x{size}', ')'] for c, w in emblems], []), '-background', 'none', '+append', row)
    dds(row, os.path.join(OUT, f'CAN1400_CivWhite{size}.dds'))
# ---- 4b. unit icon atlas (256,128,80,64,45,32), unit flag atlas (32) and building icon atlas (256,128,64,45)
for size in (256, 128, 80, 64, 45, 32):
    row = os.path.join(TMP, f'units_{size}.png')
    M(*sum([['(', u, '-resize', f'{size}x{size}', ')'] for u in unit_icons], []), '-background', 'none', '+append', row)
    dds(row, os.path.join(OUT, f'CAN1400_Units{size}.dds'))
row = os.path.join(TMP, 'flags_32.png')
M(*sum([['(', u, '-resize', '32x32', ')'] for u in unit_glyphs], []), '-background', 'none', '+append', row)
dds(row, os.path.join(OUT, 'CAN1400_UnitFlags32.dds'))
for size in (256, 128, 64, 45):
    row = os.path.join(TMP, f'blds_{size}.png')
    M(*sum([['(', b, '-resize', f'{size}x{size}', ')'] for b in bld_icons], []), '-background', 'none', '+append', row)
    dds(row, os.path.join(OUT, f'CAN1400_Buildings{size}.dds'))
if rel_icons:
    for size in (128, 80, 64, 48, 32, 24, 16):
        row = os.path.join(TMP, f'rels_{size}.png'); M(*sum([['(', r, '-resize', f'{size}x{size}', ')'] for r in rel_icons], []), '-background', 'none', '+append', row); dds(row, os.path.join(OUT, f'CAN1400_Religions{size}.dds'))
# ---- 5. diplomacy fallback scene (2048x1024) and Dawn of Man image (1024x1024)
for i, (k, name, icon, bg) in enumerate(LEADERS):
    scene_src = os.path.join(SRC, f'{k}_scene.png'); col, wht = emblems[i]
    scene = os.path.join(TMP, f'scene_{k}.png')
    # the generated scene is 1792x1024: scale to width 2048 and crop the middle 1024 rows (this also drops the model's occasional corner signature)
    M(scene_src, '-resize', '2048x', '-gravity', 'center', '-extent', '2048x1024',
      '(', '-size', '2048x14', f'xc:{icon}', ')', '-gravity', 'south', '-geometry', '+0+14', '-composite',
      '(', '-size', '2048x14', f'xc:{bg}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', scene)
    dds(scene, os.path.join(OUT, f'CAN1400_Scene_{k}.dds'), 'dxt1')
    dom = os.path.join(TMP, f'dom_{k}.png')
    size, fx, fy = FACE[k]; dx = max(0, min(1792 - 1024, fx + size // 2 - 512))   # 1024x1024 of the scene around the figure
    M('-size', '1024x1024', 'gradient:#1a2230-#0b0f16', '(', scene_src, '-crop', f'1024x1024+{dx}+0', '+repage',
      '(', '-size', '1024x1024', 'gradient:white-black', ')', '-compose', 'CopyOpacity', '-composite', ')', '-compose', 'over', '-gravity', 'center', '-composite',
      '(', '-size', '1024x12', f'xc:{icon}', ')', '-gravity', 'south', '-geometry', '+0+12', '-composite', '(', '-size', '1024x12', f'xc:{bg}', ')', '-gravity', 'south', '-geometry', '+0+0', '-composite', dom)
    dds(dom, os.path.join(OUT, f'CAN1400_DOM_{k}.dds'), 'dxt1')
# ---- 6. the pieces for the repository and the README rows
for k, name, icon, bg in LEADERS:
    shutil.copy(os.path.join(TMP, f'face_{k}.png'), os.path.join(CUT, f'{k}_face.png'))
    shutil.copy(os.path.join(TMP, f'emb_{k}.png'), os.path.join(CUT, f'{k}_emblem.png')); shutil.copy(os.path.join(TMP, f'embw_{k}.png'), os.path.join(CUT, f'{k}_glyph.png'))
    M(os.path.join(TMP, f'scene_{k}.png'), '-quality', '95', os.path.join(CUT, f'{k}_scene.jpg')); M(os.path.join(TMP, f'dom_{k}.png'), '-quality', '95', os.path.join(CUT, f'{k}_dom.jpg'))
    shutil.copy(os.path.join(TMP, f'unit_{k}.png'), os.path.join(CUT, f'{k}_unit.png'))
    if os.path.exists(os.path.join(TMP, f'bld_{k}.png')): shutil.copy(os.path.join(TMP, f'bld_{k}.png'), os.path.join(CUT, f'{k}_building.png'))
M(*sum([['(', f, '-resize', '200x200', ')'] for f in faces], []), '-background', 'none', '+append', os.path.join(HERE, 'preview_faces.png'))
M(*sum([['(', u, '-resize', '200x200', ')'] for u in unit_icons], []), '-background', 'none', '+append', os.path.join(TMP, 'prow3.png'))
M(*sum([['(', b, '-resize', '200x200', ')'] for b in bld_icons], []), '-background', 'none', '+append', os.path.join(TMP, 'prow4.png'))
M(os.path.join(TMP, 'prow3.png'), os.path.join(TMP, 'prow4.png'), '-background', 'none', '-append', os.path.join(HERE, 'preview_uniques.png'))
for k in RELIGIONS:
    if os.path.exists(os.path.join(TMP, f'rel_{k}.png')): shutil.copy(os.path.join(TMP, f'rel_{k}.png'), os.path.join(CUT, f'{k}_religion.png'))
if rel_icons: M(*sum([['(', r, '-resize', '120x120', '-background', '#3a3a3a', '-flatten', ')'] for r in rel_icons], []), '+append', os.path.join(HERE, 'preview_religions.png'))
M(*sum([['(', c, '-resize', '200x200', ')'] for c, w in emblems], []), '-background', 'none', '+append', os.path.join(TMP, 'prow1.png'))
M(*sum([['(', w, '-resize', '200x200', '-background', '#3a3a3a', '-flatten', ')'] for c, w in emblems], []), '+append', os.path.join(TMP, 'prow2.png'))
M(os.path.join(TMP, 'prow1.png'), os.path.join(TMP, 'prow2.png'), '-background', 'none', '-append', os.path.join(HERE, 'preview_emblems.png'))
print('art written to', OUT, 'and', CUT); print(sorted(os.listdir(OUT)))
