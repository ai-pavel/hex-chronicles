#!/usr/bin/env python3
"""Workshop and CivFanatics page images for China 1928, composed from the art build's intermediates (art/tmp: the static
diplomacy scenes, round portraits and emblem discs that art/build_art.py makes from art/src), the generator's map preview and the
scenario text (text/build_text.py, text/events_text.py, ui/China1928_Events.lua) with Pillow.

  python3 src/china-1928/art/build_art.py             # first: fills art/tmp (not committed)
  python3 src/china-1928/publish/make_screens.py      -> publish/cover.jpg (1024x1024), publish/screens/*.jpg (1920x1080)

The cover (six portraits, the map, the title), a map card with the six sides and the city-states, one card per side (scene, emblem,
leader, ability, starting position, Dawn of Man), and a timeline of the dated events."""
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
SIDES = [('NAN', 'Chiang', 'China'), ('GMJ', 'Feng', 'Zulu'), ('SHX', 'Yan', 'Russia'), ('FT', 'Zhang', 'Germany'), ('GX', 'Li', 'Ethiopia'), ('CCP', 'Mao', 'Shoshone')]
PCOL = {'NAN': ('#FFFFFF', '#1F3C99'), 'GMJ': ('#F2E6C8', '#556B2F'), 'SHX': ('#F5D76E', '#7B4A22'), 'FT': ('#1A1A1A', '#E8B400'), 'GX': ('#FFFFFF', '#1E8A8A'), 'CCP': ('#FFD700', '#C8102E'),
        'JAPAN': ('#FFFFFF', '#BC002D')}
START = {'NAN': 'Jiangsu, Zhejiang, Anhui, Jiangxi, Fujian, Hunan and eastern Shandong from Nanjing, with Shanghai and Qingdao: the Central Army, gunboats and a few aircraft.',
         'GMJ': 'Henan, Shaanxi, Gansu, Ningxia and western Shandong from Kaifeng, with Xi\'an, Lanzhou and Jinan: a large, drilled and poor army astride the Longhai railway.',
         'SHX': 'Shanxi behind its passes, and since June Beiping, Tianjin, the Hebei plain, Chahar and Suiyuan, from Taiyuan.',
         'FT': 'The three provinces of Manchuria, Rehe and the eastern Mongol leagues from Mukden: the arsenal, an air force, tanks and a navy, between the Kwantung Army and the Soviet railway.',
         'GX': 'Guangxi from Nanning, and Hubei with Wuhan through the Wuhan Political Council; Bai Chongxi\'s troops still stand at Tangshan in Hebei.',
         'CCP': 'Jinggangshan on the Hunan-Jiangxi border and Fang Zhimin\'s base at Hengfeng, with guerrilla bands in the hills of four provinces. At war with all five armies.'}
# the side colours of the map preview (gen_china1928.py OCOL, CS_COL, FREE_COL), for the legend swatches
MAPCOL = {'NAN': (38, 78, 200), 'GMJ': (112, 142, 46), 'SHX': (150, 92, 42), 'FT': (238, 192, 24), 'GX': (30, 172, 168), 'CCP': (214, 32, 46), 'CS': (150, 150, 150), 'FREE': (226, 221, 205)}
CS = ['Japan', 'Soviet Union', 'Mongolian People\'s Republic', 'Sichuan', 'Chongqing', 'Yunnan', 'Guizhou', 'Guangdong', 'Qinghai', 'Hong Kong', 'Macau', 'Weihaiwei', 'French Indochina']
SIDE_NAME = {k: build_text.EXTRA_EN[f'TXT_KEY_CHN1928_SIDE_{k}'] for k in ('NAN', 'GMJ', 'SHX', 'FT', 'GX', 'CCP', 'BARB', 'JAPAN', 'SOVIET')}
F = {k: dict(build_text.F[k], dawn=build_text.F[k]['dawn'].split('[NEWLINE]')[0]) for k, *_ in SIDES}   # the first paragraph of the Dawn of Man
lua = open(os.path.join(MOD, 'ui', 'China1928_Events.lua'), encoding='utf-8').read()
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
def cover_fit(img, w, h):
    s = max(w / img.width, h / img.height); img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2; return img.crop((x, y, x + w, y + h))
def save(img, path): img.convert('RGB').save(path, quality=90, optimize=True); print('wrote', os.path.relpath(path, MOD))
def date_text(d): y, m, dd = d.split('-'); return f"{int(dd)} {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(m) - 1]} {y}"
def preview(): return Image.open(os.path.join(MOD, 'China1928_preview.png')).convert('RGBA')

def cover():
    S = 1024; img = Image.new('RGBA', (S, S), BG + (255,)); draw = ImageDraw.Draw(img)
    for i, (key, leader, donor) in enumerate(SIDES):
        p = piece(f'face_{leader}.png', 136); img.paste(p, (round(60 + i * (S - 120 - 136) / 5), 34), p)
    m = preview(); m = m.crop((0, 30, m.width, m.height - 24)); h = 640; m = m.resize((round(m.width * h / m.height), h), Image.LANCZOS)
    img.paste(m, ((S - m.width) // 2, 186))
    t = font(92, 'b'); draw.text(((S - draw.textlength('China 1928', font=t)) / 2, 832), 'China 1928', font=t, fill=INK)
    n = len(EVENTS); s = f'The warlord era, one turn = one week, six sides, {n} dated events'; f = fit(draw, s, 34, S - 30)
    draw.text(((S - draw.textlength(s, font=f)) / 2, 948), s, font=f, fill=INK2)
    save(img, os.path.join(HERE, 'cover.jpg'))

def map_card():
    img = Image.new('RGBA', (W, H), BG + (255,)); draw = ImageDraw.Draw(img)
    t = font(68, 'b'); draw.text(((W - draw.textlength('China 1928', font=t)) / 2, 22), 'China 1928', font=t, fill=INK)
    s = '100 x 112 hexes from Yunnan to the Ussuri and from the Amur to Tonkin, about 36 km per hex, as of 10 October 1928. Land in the colour of its holder: the six sides as in the legend, grey: city-states, pale: nobody\'s land; black triangles: bandits; dark dots: the 1928 railways.'
    for i, l in enumerate(wrap(draw, s, font(23), 1600)): draw.text(((W - draw.textlength(l, font=font(23))) / 2, 104 + i * 30), l, font=font(23), fill=INK2)
    m = preview(); h = 880; m = m.resize((round(m.width * h / m.height), h), Image.LANCZOS)
    img.paste(m, (60, 180))
    x, y = 60 + m.width + 50, 182; width = W - x - 50
    for key, leader, donor in SIDES:
        draw.rectangle((x, y + 8, x + 22, y + 62), fill=MAPCOL[key], outline=(0, 0, 0))   # the side's colour on the map
        em = piece(f'emb_{leader}.png', 70); img.paste(em, (x + 34, y), em)
        draw.text((x + 124, y - 2), F[key]['civ_short'], font=font(28, 'b'), fill=INK); draw.text((x + 124, y + 34), f"{F[key]['leader']}  ·  {donor}", font=font(20), fill=INK2); y += 84
    draw.rectangle((x, y + 14, x + 22, y + 36), fill=MAPCOL['CS'], outline=(0, 0, 0)); y = label(draw, (x + 34, y + 10), 'Thirteen city-states') + 2
    y = block(draw, (x, y), ', '.join(CS) + '.', font(21), width, INK2, 5)
    draw.rectangle((x, y + 18, x + 22, y + 40), fill=MAPCOL['FREE'], outline=(0, 0, 0)); y = label(draw, (x + 34, y + 14), "Bandits in nobody's land") + 2
    block(draw, (x, y), 'The bandit armies of Henan and Shandong, the Red Spears, the honghuzi of Manchuria and the hill bandits of the south: raging barbarians, bred by the empty land between the towns.', font(21), width, INK2, 5)
    save(img, os.path.join(OUT, '01_map.jpg'))

def side_card(n, key, leader, donor):
    f = F[key]; img = cover_fit(Image.open(os.path.join(TMP, f'scene_{leader}.png')).convert('RGBA'), W, H)
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
    y = label(draw, (x0, y + 16), 'On 10 October 1928'); y = block(draw, (x0, y), START[key], font(26), width, INK2) + 24
    y = label(draw, (x0, y), 'Dawn of Man'); block(draw, (x0, y), f['dawn'], font(23, 'i'), width, INK2, 6, max_y=H - 70)
    draw.text((W - 40 - draw.textlength('China 1928', font=font(26, 'b')), H - 56), 'China 1928', font=font(26, 'b'), fill=GOLD)
    save(img, os.path.join(OUT, f'{n:02d}_{key.lower()}.jpg'))

def events_card():
    img = Image.new('RGBA', (W, H), BG + (255,)); draw = ImageDraw.Draw(img)
    title = f'{len(EVENTS)} dated events, 1928-1937'
    t = font(60, 'b'); draw.text(((W - draw.textlength(title, font=t)) / 2, 24), title, font=t, fill=INK)
    s = 'Each arrives on its historical week whoever is playing: reinforcements, wars and truces, defections, cities changing hands, invasions. The human player sees a popup.'
    draw.text(((W - draw.textlength(s, font=font(23))) / 2, 100), s, font=font(23), fill=INK2)
    cols = [('NAN', 2, ('NAN',)), ('GMJ', 1, ('GMJ',)), ('SHX', 1, ('SHX',)), ('FT', 1, ('FT',)), ('GX', 1, ('GX',)), ('CCP', 2, ('CCP',)), ('JAPAN', 2, ('JAPAN', 'SOVIET'))]
    cw = (W - 100) // 10; slot = 0
    for side, span, keys in cols:
        x = 50 + slot * cw; y = 160; slot += span
        draw.rectangle((x, y, x + span * cw - 16, y + 8), fill=rgb(PCOL[side][1])); y += 20
        name = 'Japan and the Soviet Union' if side == 'JAPAN' else SIDE_NAME[side]
        draw.text((x, y), name, font=fit(draw, name, 24, span * cw - 20), fill=INK); y0 = y = y + 40
        rows = sorted([(d, eid) for d, sd, eid in EVENTS if sd in keys]); per = -(-len(rows) // span)
        for k, (d, eid) in enumerate(rows):
            if k and k % per == 0: x += cw; y = y0
            draw.text((x, y), date_text(d), font=font(17, 'b'), fill=GOLD); y += 21
            y = block(draw, (x, y), events_text.EVENTS[eid][0], font(18), cw - 22, INK2, 2) + 8
    y = 1030; draw.text((50, y), 'Rebels:', font=font(22, 'b'), fill=INK)
    draw.text((150, y), '   '.join(f'{date_text(d)}  {events_text.EVENTS[eid][0]}' for d, sd, eid in EVENTS if sd == 'BARB'), font=font(21), fill=INK2)
    save(img, os.path.join(OUT, '08_events.jpg'))

cover()
map_card()
for n, (key, leader, donor) in enumerate(SIDES, 2): side_card(n, key, leader, donor)
events_card()
