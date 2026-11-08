#!/usr/bin/env python3
"""Workshop and CivFanatics page images for Canarias 1400, composed from the committed art (art/src scenes, art/cut pieces,
the generator's map preview) and the scenario text (text/build_text.py, text/uniques.py) with Pillow.

  python3 src/canarias-1400/publish/make_screens.py      -> publish/screens/*.jpg, 1920x1080

One card per people (scene as background, emblem, leader, unique ability, unique unit and building), one map card with the
seven emblems, one card with all the unique units and buildings. cover.jpg (the thumbnail) is made separately by ImageMagick."""
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, 'art'); OUT = os.path.join(HERE, 'screens'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(MOD, 'text')); import uniques   # noqa: E402  (pure data, no game files needed)
W, H = 1920, 1080
FONTS = '/System/Library/Fonts/Supplemental/'
def font(size, style=''): return ImageFont.truetype(FONTS + {'': 'Georgia.ttf', 'b': 'Georgia Bold.ttf', 'i': 'Georgia Italic.ttf'}[style], size)
INK = (244, 232, 190); INK2 = (200, 208, 226); GOLD = (214, 178, 94); NAVY = (19, 33, 63); PANEL = (9, 15, 32)
PEOPLES = ['TENERIFE', 'GRANCANARIA', 'LAPALMA', 'LAGOMERA', 'ELHIERRO', 'FUERTEVENTURA', 'LANZAROTE']
ISLAND = {'TENERIFE': 'Tenerife (Achinet)', 'GRANCANARIA': 'Gran Canaria (Tamaran)', 'LAPALMA': 'La Palma (Benahoare)', 'LAGOMERA': 'La Gomera',
          'ELHIERRO': 'El Hierro (Esero)', 'FUERTEVENTURA': 'Fuerteventura (Erbania)', 'LANZAROTE': 'Lanzarote (Titerogaka)'}
BASE_NAMES = {'WATERMILL': 'Water Mill', 'WORKBOAT': 'Work Boat'}

# the EN table of build_text.py cannot be imported without the game extracts; read the few fields the cards need
src = open(os.path.join(MOD, 'text', 'build_text.py'), encoding='utf-8').read()
EN = {}
for key in PEOPLES:
    block = src[src.index(f"\n '{key}': dict(leader="):]
    EN[key] = {f: re.search(rf"\b{f}='([^']*)'", block).group(1) for f in ('leader', 'civ_long', 'civ_short', 'trait_short', 'trait')}

def clean(s): return re.sub(r'\s+\)', ')', re.sub(r'\s+', ' ', re.sub(r'\[ICON_[A-Z_0-9]+\]\s*', '', s))).replace(' ,', ',').strip()
def base_name(t): k = t.split('_', 1)[1]; return BASE_NAMES.get(k, k.replace('_', ' ').title())
def wrap(draw, text, f, width):
    lines, line = [], ''
    for word in text.split():
        t = (line + ' ' + word).strip()
        if draw.textlength(t, font=f) <= width: line = t
        else: lines.append(line); line = word
    return lines + [line]
def block(draw, xy, text, f, width, fill, gap=8):
    x, y = xy
    for l in wrap(draw, text, f, width): draw.text((x, y), l, font=f, fill=fill); y += f.size + gap
    return y
def label(draw, xy, text): draw.text(xy, text.upper(), font=font(22, 'b'), fill=GOLD); return xy[1] + 34
def cover(img, w, h):
    s = max(w / img.width, h / img.height); img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2; return img.crop((x, y, x + w, y + h))
def piece(name, size): return Image.open(os.path.join(ART, 'cut', name)).convert('RGBA').resize((size, size), Image.LANCZOS)
def save(img, name): img.convert('RGB').save(os.path.join(OUT, name), quality=90, optimize=True); print('wrote', name)
def shadow_text(draw, xy, text, f, fill):
    draw.text((xy[0] + 2, xy[1] + 3), text, font=f, fill=(0, 0, 0, 160)); draw.text(xy, text, font=f, fill=fill)

def people_card(n, key):
    e, u = EN[key], next(x for x in uniques.UNITS if x['people'] == key); b = next(x for x in uniques.BUILDINGS if x['people'] == key)
    img = cover(Image.open(os.path.join(ART, 'src', f'{key}_scene.png')).convert('RGBA'), W, H)
    # dark panel on the right with a soft left edge (the leaders stand in the left third of every scene)
    alpha = np.clip((np.arange(W) - 940) / 220, 0, 1) ** 1.5 * 0.86
    mask = Image.fromarray((np.tile(alpha, (H, 1)) * 255).astype('uint8'), 'L')
    img.paste(Image.new('RGBA', (W, H), PANEL + (255,)), (0, 0), mask)
    draw = ImageDraw.Draw(img); x0, width = 1150, 700
    img.paste(piece(f'{key}_emblem.png', 150), (x0, 60), piece(f'{key}_emblem.png', 150))
    tf = font(62, 'b')
    while draw.textlength(e['civ_short'], font=tf) > W - 40 - (x0 + 175): tf = font(tf.size - 2, 'b')
    shadow_text(draw, (x0 + 175, 62 + (62 - tf.size) * 2 // 3), e['civ_short'], tf, INK)
    draw.text((x0 + 178, 140), e['civ_long'], font=font(28, 'i'), fill=INK2)
    draw.text((x0 + 178, 178), f"{e['leader']}  ·  {ISLAND[key]}", font=font(28), fill=INK2)
    y = label(draw, (x0, 270), 'Unique ability')
    draw.text((x0, y), e['trait_short'], font=font(40, 'b'), fill=INK); y += 56
    y = block(draw, (x0, y), clean(e['trait']), font(27), width, INK2) + 26
    y = label(draw, (x0, y), 'Unique unit')
    img.paste(piece(f'{key}_unit.png', 120), (x0, y), piece(f'{key}_unit.png', 120))
    draw.text((x0 + 145, y - 4), f"{u['name']}", font=font(36, 'b'), fill=INK)
    draw.text((x0 + 145 + draw.textlength(u['name'], font=font(36, 'b')) + 16, y + 6), f"replaces the {base_name(u['base'])}", font=font(24, 'i'), fill=INK2)
    y = max(block(draw, (x0 + 145, y + 48), clean(u['help'].split('. ', 1)[1]), font(25), width - 145, INK2, 6), y + 130) + 22
    y = label(draw, (x0, y), 'Unique building' if b['base'] else 'Unique improvement')
    if b['base']:
        img.paste(piece(f'{key}_building.png', 120), (x0, y), piece(f'{key}_building.png', 120))
        draw.text((x0 + 145, y - 4), b['name'], font=font(36, 'b'), fill=INK)
        draw.text((x0 + 145 + draw.textlength(b['name'], font=font(36, 'b')) + 16, y + 6), f"replaces the {base_name(b['base'])}", font=font(24, 'i'), fill=INK2)
        block(draw, (x0 + 145, y + 48), clean(b['help'].split('. ', 1)[1]), font(25), width - 145, INK2, 6)
    else:
        draw.text((x0, y - 4), b['name'], font=font(36, 'b'), fill=INK)
        draw.text((x0 + draw.textlength(b['name'], font=font(36, 'b')) + 16, y + 6), 'the Terrace Farm of the Gomeros', font=font(24, 'i'), fill=INK2)
        block(draw, (x0, y + 48), b['texts']['TXT_KEY_CIV5_IMPROVEMENTS_TERRACE_FARM_HELP'], font(25), width, INK2, 6)
    draw.text((W - 40 - draw.textlength('Canarias 1400', font=font(26, 'b')), H - 56), 'Canarias 1400', font=font(26, 'b'), fill=GOLD)
    save(img, f'{n:02d}_{key.lower()}.jpg')

def map_card():
    img = Image.new('RGBA', (W, H), NAVY + (255,)); draw = ImageDraw.Draw(img)
    t = font(72, 'b'); draw.text(((W - draw.textlength('Canarias 1400', font=t)) / 2, 28), 'Canarias 1400', font=t, fill=INK)
    s = 'Seven islands in real relief, 160 x 83 hexes, 3 km per hex. Gold: starting positions. Magenta: the natural wonder of each island.'
    draw.text(((W - draw.textlength(s, font=font(26))) / 2, 118), s, font=font(26), fill=INK2)
    m = Image.open(os.path.join(MOD, 'Canarias1400_preview.png')).convert('RGBA'); m = m.resize((1500, round(m.height * 1500 / m.width)), Image.LANCZOS)
    img.paste(m, ((W - m.width) // 2, 170))
    y = 170 + m.height + 34; col = W // 7
    for i, key in enumerate(PEOPLES):
        cx = col * i + col // 2; em = piece(f'{key}_emblem.png', 96); img.paste(em, (cx - 48, y), em)
        for j, (txt, f, fill) in enumerate(((EN[key]['civ_short'], font(26, 'b'), INK), (ISLAND[key].split(' (')[0], font(22), INK2))):
            draw.text((cx - draw.textlength(txt, font=f) / 2, y + 104 + j * 30), txt, font=f, fill=fill)
    save(img, '01_map.jpg')

def uniques_card():
    img = Image.new('RGBA', (W, H), NAVY + (255,)); draw = ImageDraw.Draw(img); col = W // 7
    t = font(60, 'b'); draw.text(((W - draw.textlength('Seven peoples, seven ways of war and water', font=t)) / 2, 36), 'Seven peoples, seven ways of war and water', font=t, fill=INK)
    for row, (items, kind, y) in enumerate(((uniques.UNITS, 'unit', 150), (uniques.BUILDINGS, 'building', 600))):
        label(draw, (60, y), 'Unique units' if kind == 'unit' else 'Unique buildings')
        for i, it in enumerate(items):
            key = it['people']; cx = col * i + col // 2
            if it['base']:
                ic = piece(f'{key}_{kind}.png', 190); img.paste(ic, (cx - 95, y + 44), ic); sub = f"replaces the {base_name(it['base'])}"
            else:
                draw.ellipse((cx - 95, y + 44, cx + 95, y + 234), outline=GOLD, width=4); g = piece(f'{key}_glyph.png', 120); img.paste(g, (cx - 60, y + 79), g); sub = 'the Terrace Farm'
            nf = font(30, 'b')
            while draw.textlength(it['name'], font=nf) > col - 16: nf = font(nf.size - 2, 'b')
            draw.text((cx - draw.textlength(it['name'], font=nf) / 2, y + 250 + (30 - nf.size) // 2), it['name'], font=nf, fill=INK)
            draw.text((cx - draw.textlength(sub, font=font(21, 'i')) / 2, y + 290), sub, font=font(21, 'i'), fill=INK2)
            draw.text((cx - draw.textlength(EN[key]['civ_short'], font=font(21)) / 2, y + 318), EN[key]['civ_short'], font=font(21), fill=GOLD)
    save(img, '09_uniques.jpg')

map_card()
for n, key in enumerate(PEOPLES, 2): people_card(n, key)
uniques_card()
