#!/usr/bin/env python3
"""Workshop and CivFanatics page images for Russia 1918, composed from the art build's intermediates (art/tmp: the static
diplomacy scenes, round portraits and emblem discs that art/build_art.py makes from art/src), the generator's map preview and the
scenario text (text/build_text.py, text/events_text.py, ui/Russia1918_Events.lua) with Pillow.

  python3 src/russia-1918/art/build_art.py             # first: fills art/tmp (not committed)
  python3 src/russia-1918/publish/make_screens.py      -> publish/screens/*.jpg, 1920x1080

A map card with the six sides and the city-states, one card per side (scene, emblem, leader, ability, unique unit and building,
starting position, Dawn of Man), and a timeline of the dated events. build_text.py reads LEADER_DIALOG_KEYS.txt from $HEX_XML on import."""
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(HERE); TMP = os.path.join(MOD, 'art', 'tmp'); OUT = os.path.join(HERE, 'screens'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(MOD, 'text'))
import events_text, build_text, uniques   # noqa: E402  (pure data; build_text writes nothing on import)
W, H = 1920, 1080
FONTS = '/System/Library/Fonts/Supplemental/'
def font(size, style=''): return ImageFont.truetype(FONTS + {'': 'Georgia.ttf', 'b': 'Georgia Bold.ttf', 'i': 'Georgia Italic.ttf'}[style], size)
INK = (240, 220, 176); INK2 = (200, 190, 170); GOLD = (214, 172, 94); BG = (29, 22, 18); PANEL = (16, 12, 10)
SIDES = [('RED', 'Lenin', 'Russia'), ('SOUTH', 'Denikin', 'Germany'), ('SIB', 'Kolchak', 'Shoshone'), ('NORTH', 'Yudenich', 'England'), ('UKR', 'Skoropadsky', 'Ethiopia'), ('POL', 'Pilsudski', 'Poland')]
PCOL = {'RED': ('#FFD700', '#B00000'), 'SOUTH': ('#1F4E9A', '#F2F2F2'), 'SIB': ('#FFFFFF', '#2E7D32'), 'NORTH': ('#FFFFFF', '#0B3D91'), 'UKR': ('#FFD500', '#005BBB'), 'POL': ('#FFFFFF', '#DC143C')}
START = {'RED': 'Central Russia, the Volga, the North Caucasus and Turkestan from Moscow: the biggest army, and the greenest.',
         'SOUTH': 'The Don and the Kuban from Novocherkassk: few units, all veterans. Permanent peace and open borders with the other Whites.',
         'SIB': 'Samara to Irkutsk along the Trans-Siberian from Omsk, the Orenburg and Ural Cossacks, the Czechoslovak Legion.',
         'NORTH': 'Murmansk and Arkhangelsk with the Allied landing force, two months early. The Royal Navy on the White Sea.',
         'UKR': 'All of Ukraine, the Donbass, Crimea and Belgorod from Kiev, under German garrisons that leave in November. Neutral at start.',
         'POL': 'Congress Poland, Galicia with Lwow, Grodno and Brest from Warsaw; Wilno is Lithuanian. Neutral at start; the war with the Soviets comes in February 1919.'}
CS = ['Finland', 'Estonia', 'Latvia', 'Lithuania (Vilna)', 'Germany (Konigsberg)', 'Romania (Kishinev)', 'Georgia', 'Azerbaijan', 'Armenia', 'Ottoman Empire (Kars)', 'Persia (Tabriz)', 'Bukhara', 'Khiva']
SIDE_NAME = {k: build_text.EXTRA_EN[f'TXT_KEY_RUS1918_SIDE_{k}'] for k in ('RED', 'SOUTH', 'SIB', 'NORTH', 'UKR', 'POL', 'BARB')}
F = {k: dict(build_text.F[k], dawn=build_text.F[k]['dawn'].split('[NEWLINE]')[0]) for k, *_ in SIDES}   # the first paragraph of the Dawn of Man
lua = open(os.path.join(MOD, 'ui', 'Russia1918_Events.lua'), encoding='utf-8').read()
EVENTS = re.findall(r'date = "([0-9-]+)", side = "([A-Z]+)", id = "([A-Z_0-9]+)"', lua)

def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def wrap(draw, text, f, width):
    lines, line = [], ''
    for word in text.split():
        t = (line + ' ' + word).strip()
        if draw.textlength(t, font=f) <= width: line = t
        else: lines.append(line); line = word
    return lines + [line]
def block(draw, xy, text, f, width, fill, gap=7, max_y=None):
    x, y = xy; lines = wrap(draw, text, f, width)
    if max_y is not None:   # cut to the lines that fit above max_y, ending on an ellipsis
        n = max(1, (max_y - y) // (f.size + gap))
        if n < len(lines): lines = lines[:n]; lines[-1] = lines[-1].rstrip(',;:') + ' ...'
    for l in lines: draw.text((x, y), l, font=f, fill=fill); y += f.size + gap
    return y
def label(draw, xy, text): draw.text(xy, text.upper(), font=font(22, 'b'), fill=GOLD); return xy[1] + 34
def fit(draw, text, size, width, style='b'):
    f = font(size, style)
    while draw.textlength(text, font=f) > width: f = font(f.size - 2, style)
    return f
def piece(name, size): return Image.open(os.path.join(TMP, name)).convert('RGBA').resize((size, size), Image.LANCZOS)
def cover(img, w, h):
    s = max(w / img.width, h / img.height); img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2; return img.crop((x, y, x + w, y + h))
def save(img, name): img.convert('RGB').save(os.path.join(OUT, name), quality=90, optimize=True); print('wrote', name)
def date_text(d): y, m, dd = d.split('-'); return f"{int(dd)} {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(m) - 1]} {y}"

def map_card():
    img = Image.new('RGBA', (W, H), BG + (255,)); draw = ImageDraw.Draw(img)
    t = font(68, 'b'); draw.text(((W - draw.textlength('Russia 1918', font=t)) / 2, 22), 'Russia 1918', font=t, fill=INK)
    s = '160 x 104 hexes from East Prussia to Irkutsk, about 47 km per hex, as of 1 June 1918. Colours: the six sides; grey: city-states; black triangles: insurgents; dots: the 1918 railways.'
    for i, l in enumerate(wrap(draw, s, font(23), 1600)): draw.text(((W - draw.textlength(l, font=font(23))) / 2, 104 + i * 30), l, font=font(23), fill=INK2)
    m = Image.open(os.path.join(MOD, 'Russia1918_preview.png')).convert('RGBA'); m = m.resize((1240, round(m.height * 1240 / m.width)), Image.LANCZOS)
    img.paste(m, (60, 180))
    x, y = 1350, 182
    for key, leader, donor in SIDES:
        em = piece(f'emb_{leader}.png', 70); img.paste(em, (x, y), em)
        draw.text((x + 90, y - 2), F[key]['civ_short'], font=font(28, 'b'), fill=INK); draw.text((x + 90, y + 34), f"{F[key]['leader']}  ·  {donor}", font=font(20), fill=INK2); y += 84
    y = label(draw, (x, y + 10), 'Thirteen city-states') + 2
    y = block(draw, (x, y), ', '.join(CS) + '.', font(21), 520, INK2, 5)
    y = label(draw, (x, y + 14), 'Insurgents') + 2
    block(draw, (x, y), 'Makhno, the Basmachi, the Dagestani murids, later Grigoriev and Antonov: raging barbarians, bred by the empty steppe and taiga.', font(21), 520, INK2, 5)
    save(img, '01_map.jpg')

def side_card(n, key, leader, donor):
    f = F[key]; img = cover(Image.open(os.path.join(TMP, f'scene_{leader}.png')).convert('RGBA'), W, H)
    alpha = np.clip((1060 - np.arange(W)) / 240, 0, 1) ** 1.5 * 0.9   # dark panel on the left; the portraits stand on the right of every scene
    mask = Image.fromarray((np.tile(alpha, (H, 1)) * 255).astype('uint8'), 'L')
    img.paste(Image.new('RGBA', (W, H), PANEL + (255,)), (0, 0), mask)
    draw = ImageDraw.Draw(img); x0, width = 90, 780
    img.paste(piece(f'emb_{leader}.png', 150), (x0, 60), piece(f'emb_{leader}.png', 150))
    tf = fit(draw, f['civ_short'], 62, width - 175); draw.text((x0 + 175, 62 + (62 - tf.size) * 2 // 3), f['civ_short'], font=tf, fill=INK)
    draw.text((x0 + 178, 140), f['civ_long'], font=fit(draw, f['civ_long'], 28, width - 178, 'i'), fill=INK2)
    draw.text((x0 + 178, 178), f"{f['leader']}  ·  on the {donor} slot", font=font(28), fill=INK2)
    y = label(draw, (x0, 270), 'Ability')
    draw.text((x0, y), f['trait_short'], font=fit(draw, f['trait_short'], 40, width), fill=INK); y += 56
    y = block(draw, (x0, y), re.sub(r'\[ICON_\w+\] ?', '', f['trait']), font(26), width, INK2) + 24
    y = label(draw, (x0, y), 'Unique unit and building')
    for u in [u for u in uniques.UNITS + uniques.BUILDINGS if u['side'] == key]:
        draw.text((x0, y), u['name'], font=font(26, 'b'), fill=INK); y += 34
        y = block(draw, (x0, y), re.sub(r' ?\[ICON_\w+\]', '', u['help']), font(22), width, INK2, 5) + 8
    y = label(draw, (x0, y + 16), 'On 1 June 1918'); y = block(draw, (x0, y), START[key], font(26), width, INK2) + 24
    y = label(draw, (x0, y), 'Dawn of Man'); block(draw, (x0, y), f['dawn'], font(23, 'i'), width, INK2, 6, max_y=H - 70)
    draw.text((W - 40 - draw.textlength('Russia 1918', font=font(26, 'b')), H - 56), 'Russia 1918', font=font(26, 'b'), fill=GOLD)
    save(img, f'{n:02d}_{key.lower()}.jpg')

def events_card():
    img = Image.new('RGBA', (W, H), BG + (255,)); draw = ImageDraw.Draw(img)
    t = font(60, 'b'); draw.text(((W - draw.textlength('Thirty-six dated events', font=t)) / 2, 24), 'Thirty-six dated events', font=t, fill=INK)
    s = 'Each arrives on its historical week whoever is playing: reinforcements, gold, generals, wars and withdrawals. The human player sees a popup.'
    draw.text(((W - draw.textlength(s, font=font(23))) / 2, 100), s, font=font(23), fill=INK2)
    cols = ['RED', 'SOUTH', 'SIB', 'NORTH', 'UKR', 'POL']; cw = (W - 100) // 6
    for i, side in enumerate(cols):
        x = 50 + i * cw; y = 160
        draw.rectangle((x, y, x + cw - 16, y + 8), fill=rgb(PCOL[side][1])); y += 20
        draw.text((x, y), SIDE_NAME[side], font=font(26, 'b'), fill=INK); y += 44
        for d, sd, eid in EVENTS:
            if sd != side: continue
            draw.text((x, y), date_text(d), font=font(21, 'b'), fill=GOLD); y += 28
            y = block(draw, (x, y), events_text.EVENTS[eid][0], font(25), cw - 30, INK2, 3) + 14
    y = 980; draw.text((50, y), 'Insurgents:', font=font(22, 'b'), fill=INK)
    draw.text((190, y), '   '.join(f'{date_text(d)}  {events_text.EVENTS[eid][0]}' for d, sd, eid in EVENTS if sd == 'BARB'), font=font(21), fill=INK2)
    save(img, '08_events.jpg')

map_card()
for n, (key, leader, donor) in enumerate(SIDES, 2): side_card(n, key, leader, donor)
events_card()
