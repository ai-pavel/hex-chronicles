#!/usr/bin/env python3
"""Workshop and CivFanatics page images for Hawaii 1778, composed from the committed art (art/src scenes, art/cut pieces, the
generator's map preview) and the scenario text (text/build_text.py, text/uniques.py) with Pillow.

  python3 src/hawaii-1778/publish/make_screens.py      -> publish/screens/*.jpg, 1920x1080

One card per chiefdom (scene as background, emblem, leader, unique ability, unique unit and building), one map card with the
emblems and the city-states, one card with all the uniques. cover.jpg (the thumbnail) is made separately by ImageMagick."""
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, 'art'); OUT = os.path.join(HERE, 'screens'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(MOD, 'text')); import uniques   # noqa: E402  (pure data, no game files needed)
W, H = 1920, 1080
FONTS = '/System/Library/Fonts/Supplemental/'
def font(size, style=''): return ImageFont.truetype(FONTS + {'': 'Georgia.ttf', 'b': 'Georgia Bold.ttf', 'i': 'Georgia Italic.ttf'}[style], size)
INK = (244, 232, 190); INK2 = (200, 216, 226); GOLD = (214, 178, 94); NAVY = (15, 42, 51); PANEL = (7, 20, 26)
PEOPLES = ['KONA', 'HILO', 'MAUI', 'OAHU', 'KAUAI']
ISLAND = {'KONA': 'Hawaii: Kona and Kohala', 'HILO': 'Hawaii: Hilo, Puna and Kau', 'MAUI': 'Maui, Lanai and Kahoolawe', 'OAHU': 'Oahu', 'KAUAI': 'Kauai and Niihau'}
CITY_STATES = [('Molokai', 'religious city-state, Kaunakakai'), ('Lanai', 'maritime city-state, Kaunolu'), ('Niihau', 'maritime city-state, Puuwai')]

src = open(os.path.join(MOD, 'text', 'build_text.py'), encoding='utf-8').read()
EN = {}
for key in PEOPLES:
    block = src[src.index(f"\n '{key}': dict(leader="):]
    EN[key] = {f: re.search(rf"\b{f}='([^']*)'", block).group(1) for f in ('leader', 'civ_long', 'civ_short', 'trait_short', 'trait')}

def clean(s): return re.sub(r'\s+\)', ')', re.sub(r'\s+', ' ', re.sub(r'\[ICON_[A-Z_0-9]+\]\s*', '', s))).replace(' ,', ',').strip()
def describe(it):
    """(what it replaces, the help text without the replacement sentence) for a cloned or a renamed unique."""
    help_ = it['help'] or next(v for k, v in it['texts'].items() if '_HELP' in k)
    m = re.search(r'\b(?:replacement for|Replaces) the ([A-Z][A-Za-z ]+?)\.', help_)
    rest = re.sub(r'(?:\w+ replacement for the [A-Za-z ]+\.|Replaces the [A-Za-z ]+\.|Only \w+ may build it\.)\s*', '', help_)
    return (m.group(1) if m else None), clean(rest)
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
def fit(draw, text, size, width, style='b'):
    f = font(size, style)
    while draw.textlength(text, font=f) > width: f = font(f.size - 2, style)
    return f
def cover(img, w, h):
    s = max(w / img.width, h / img.height); img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2; return img.crop((x, y, x + w, y + h))
def piece(name, size): return Image.open(os.path.join(ART, 'cut', name)).convert('RGBA').resize((size, size), Image.LANCZOS)
def icon_of(it, kind):
    for name in (f"{it['key']}_{kind}.png", f"{it['key']}_improvement.png"):
        if os.path.exists(os.path.join(ART, 'cut', name)): return name
    return None
def save(img, name): img.convert('RGB').save(os.path.join(OUT, name), quality=90, optimize=True); print('wrote', name)
def shadow_text(draw, xy, text, f, fill):
    draw.text((xy[0] + 2, xy[1] + 3), text, font=f, fill=(0, 0, 0, 160)); draw.text(xy, text, font=f, fill=fill)
def item_row(img, draw, x0, y, width, it, kind, fallback_glyph):
    """icon, name, 'replaces the X', help; returns the next y"""
    ic = icon_of(it, kind); replaces, text = describe(it)
    if ic: img.paste(piece(ic, 120), (x0, y), piece(ic, 120))
    else:
        draw.ellipse((x0, y, x0 + 120, y + 120), outline=GOLD, width=3); g = piece(fallback_glyph, 76); img.paste(g, (x0 + 22, y + 22), g)
    nf = font(36, 'b'); draw.text((x0 + 145, y - 4), it['name'], font=nf, fill=INK)
    sub = f"replaces the {replaces}" if replaces else {'KII': 'the Moai improvement of Kona', 'HALAU': 'replaces the Barracks'}.get(it['key'], '')
    if sub: draw.text((x0 + 145 + draw.textlength(it['name'], font=nf) + 16, y + 6), sub, font=font(24, 'i'), fill=INK2)
    return max(block(draw, (x0 + 145, y + 48), text, font(25), width - 145, INK2, 6), y + 130) + 22

def people_card(n, key):
    e = EN[key]; u = next(x for x in uniques.UNITS if x['people'] == key); b = next(x for x in uniques.BUILDINGS if x['people'] == key)
    img = cover(Image.open(os.path.join(ART, 'src', f'{key}_scene.png')).convert('RGBA'), W, H)
    alpha = np.clip((np.arange(W) - 940) / 220, 0, 1) ** 1.5 * 0.86   # dark panel on the right; the chiefs stand in the left third
    mask = Image.fromarray((np.tile(alpha, (H, 1)) * 255).astype('uint8'), 'L')
    img.paste(Image.new('RGBA', (W, H), PANEL + (255,)), (0, 0), mask)
    draw = ImageDraw.Draw(img); x0, width = 1150, 700
    img.paste(piece(f'{key}_emblem.png', 150), (x0, 60), piece(f'{key}_emblem.png', 150))
    tf = fit(draw, e['civ_short'], 62, W - 40 - (x0 + 175)); shadow_text(draw, (x0 + 175, 62 + (62 - tf.size) * 2 // 3), e['civ_short'], tf, INK)
    draw.text((x0 + 178, 140), e['civ_long'], font=font(28, 'i'), fill=INK2)
    draw.text((x0 + 178, 178), f"{e['leader']}  ·  {ISLAND[key]}", font=font(28), fill=INK2)
    y = label(draw, (x0, 270), 'Unique ability')
    draw.text((x0, y), e['trait_short'], font=fit(draw, e['trait_short'], 40, width), fill=INK); y += 56
    y = block(draw, (x0, y), clean(e['trait']), font(27), width, INK2) + 26
    y = label(draw, (x0, y), 'Unique unit'); y = item_row(img, draw, x0, y, width, u, 'unit', f'{key}_glyph.png')
    y = label(draw, (x0, y), 'Unique improvement' if b.get('improvement') else 'Unique building'); item_row(img, draw, x0, y, width, b, 'building', f'{key}_glyph.png')
    draw.text((W - 40 - draw.textlength('Hawaii 1778', font=font(26, 'b')), H - 56), 'Hawaii 1778', font=font(26, 'b'), fill=GOLD)
    save(img, f'{n:02d}_{key.lower()}.jpg')

def map_card():
    img = Image.new('RGBA', (W, H), NAVY + (255,)); draw = ImageDraw.Draw(img)
    t = font(72, 'b'); draw.text(((W - draw.textlength('Hawaii 1778', font=t)) / 2, 28), 'Hawaii 1778', font=t, fill=INK)
    s = 'Eight islands in real relief, 148 x 114 hexes, 4 km per hex. Gold: starting positions. White circles: city-states. Magenta: natural wonders.'
    draw.text(((W - draw.textlength(s, font=font(26))) / 2, 118), s, font=font(26), fill=INK2)
    m = Image.open(os.path.join(MOD, 'Hawaii1778_preview.png')).convert('RGBA'); m = m.resize((1230, round(m.height * 1230 / m.width)), Image.LANCZOS)
    img.paste(m, (60, 180))
    x, y = 1360, 190
    for key in PEOPLES:
        em = piece(f'{key}_emblem.png', 88); img.paste(em, (x, y), em)
        draw.text((x + 110, y + 8), EN[key]['civ_short'], font=font(32, 'b'), fill=INK)
        draw.text((x + 110, y + 50), f"{EN[key]['leader']}, {ISLAND[key]}", font=fit(draw, f"{EN[key]['leader']}, {ISLAND[key]}", 22, W - 40 - (x + 110), ''), fill=INK2)
        y += 112
    y += 10
    for name, what in CITY_STATES:
        draw.ellipse((x + 26, y + 10, x + 62, y + 46), outline=INK, width=4)
        draw.text((x + 110, y + 2), name, font=font(30, 'b'), fill=INK); draw.text((x + 110, y + 40), what, font=font(22), fill=INK2); y += 86
    save(img, '01_map.jpg')

def uniques_card():
    img = Image.new('RGBA', (W, H), NAVY + (255,)); draw = ImageDraw.Draw(img); col = W // 5
    t = font(60, 'b'); draw.text(((W - draw.textlength('Five chiefdoms, five ways of war and water', font=t)) / 2, 36), 'Five chiefdoms, five ways of war and water', font=t, fill=INK)
    for items, kind, y in ((uniques.UNITS, 'unit', 150), (uniques.BUILDINGS, 'building', 600)):
        label(draw, (60, y), 'Unique units' if kind == 'unit' else 'Unique buildings and improvements')
        for i, it in enumerate(items):
            key = it['people']; cx = col * i + col // 2; ic = icon_of(it, kind); replaces, _ = describe(it)
            if ic: im = piece(ic, 190); img.paste(im, (cx - 95, y + 44), im)
            else:
                draw.ellipse((cx - 95, y + 44, cx + 95, y + 234), outline=GOLD, width=4); g = piece(f'{key}_glyph.png', 120); img.paste(g, (cx - 60, y + 79), g)
            sub = f"replaces the {replaces}" if replaces else {'KII': 'the Moai improvement', 'HALAU': 'replaces the Barracks'}.get(it['key'], '')
            nf = fit(draw, it['name'], 30, col - 16)
            draw.text((cx - draw.textlength(it['name'], font=nf) / 2, y + 250 + (30 - nf.size) // 2), it['name'], font=nf, fill=INK)
            draw.text((cx - draw.textlength(sub, font=font(21, 'i')) / 2, y + 290), sub, font=font(21, 'i'), fill=INK2)
            draw.text((cx - draw.textlength(EN[key]['civ_short'], font=font(21)) / 2, y + 318), EN[key]['civ_short'], font=font(21), fill=GOLD)
    save(img, '07_uniques.jpg')

map_card()
for n, key in enumerate(PEOPLES, 2): people_card(n, key)
uniques_card()
