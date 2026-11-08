#!/usr/bin/env python3
"""Workshop and CivFanatics page images for Spain 1936, composed from the art build's intermediates (art/tmp: the static
diplomacy scenes, round portraits and emblem discs that art/build_art.py makes from art/src), the generator's map preview and the
scenario text (text/build_text.py, text/events_text.py, ui/Spain1936_Events.lua) with Pillow.

  python3 src/spain-1936/art/build_art.py             # first: fills art/tmp (not committed)
  python3 src/spain-1936/publish/make_screens.py      -> publish/cover.jpg (1024x1024), publish/screens/*.jpg (1920x1080)

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
SIDES = [('REP', 'Azana', 'Russia'), ('NAT', 'Franco', 'Zulu'), ('NORTH', 'Mola', 'Germany'), ('CAT', 'Companys', 'Shoshone'), ('EUZ', 'Aguirre', 'Ethiopia'), ('CNT', 'Durruti', 'Aztec')]
PCOL = {'REP': ('#F1C40F', '#5B2A6E'), 'NAT': ('#F1BF00', '#AA151B'), 'NORTH': ('#C8102E', '#F2F2F2'), 'CAT': ('#DA121A', '#FCDD09'), 'EUZ': ('#FFFFFF', '#00843D'), 'CNT': ('#E30613', '#141414')}
START = {'REP': 'Madrid, New Castile, the Levante, eastern Andalusia, southern Extremadura, Asturias, Santander and Menorca: the capital, the fleet and the air force, few trained troops.',
         'NAT': 'Seville, Cadiz and Cordoba, the Granada pocket, the Alcazar of Toledo, Mallorca and Spanish Morocco, where the Army of Africa waits for the airlift.',
         'NORTH': 'Old Castile and Leon, Galicia, Navarre, Alava, the Rioja, Caceres, western Aragon and Oviedo from Burgos; columns at the Guadarrama passes. Permanent peace with Franco.',
         'CAT': 'The four Catalan provinces from Barcelona, the Assault Guards and the first militias. At peace with the other Republican sides, but not for certain.',
         'EUZ': 'Biscay and Gipuzkoa from Bilbao, cut off from the rest of the Republic; San Sebastian and the border at Irun on the front line.',
         'CNT': 'Eastern Aragon from Caspe behind the Durruti, Ascaso and Ortiz columns, facing Zaragoza and Huesca.'}
CS = ['Portugal', 'Gibraltar (British)', 'Tangier International Zone', 'Andorra', 'France', 'French North Africa']
SIDE_NAME = {k: build_text.EXTRA_EN[f'TXT_KEY_ESP1936_SIDE_{k}'] for k in ('REP', 'NAT', 'NORTH', 'CAT', 'EUZ', 'CNT', 'BARB')}
F = {k: dict(build_text.F[k], dawn=build_text.F[k]['dawn'].split('[NEWLINE]')[0]) for k, *_ in SIDES}   # the first paragraph of the Dawn of Man
lua = open(os.path.join(MOD, 'ui', 'Spain1936_Events.lua'), encoding='utf-8').read()
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
def preview(): return Image.open(os.path.join(MOD, 'Spain1936_preview.png')).convert('RGBA')

def cover():
    S = 1024; img = Image.new('RGBA', (S, S), BG + (255,)); draw = ImageDraw.Draw(img)
    for i, (key, leader, donor) in enumerate(SIDES):
        p = piece(f'face_{leader}.png', 136); img.paste(p, (round(60 + i * (S - 120 - 136) / 5), 34), p)
    m = preview(); m = m.crop((0, 30, m.width, m.height - 24)); h = 640; m = m.resize((round(m.width * h / m.height), h), Image.LANCZOS)
    img.paste(m, ((S - m.width) // 2, 186))
    t = font(92, 'b'); draw.text(((S - draw.textlength('Spain 1936', font=t)) / 2, 832), 'Spain 1936', font=t, fill=INK)
    n = len(EVENTS); s = f'The Civil War, one turn = one week, six sides, {n} dated events'; f = fit(draw, s, 34, S - 30)
    draw.text(((S - draw.textlength(s, font=f)) / 2, 948), s, font=f, fill=INK2)
    save(img, os.path.join(HERE, 'cover.jpg'))

def map_card():
    img = Image.new('RGBA', (W, H), BG + (255,)); draw = ImageDraw.Draw(img)
    t = font(68, 'b'); draw.text(((W - draw.textlength('Spain 1936', font=t)) / 2, 22), 'Spain 1936', font=t, fill=INK)
    s = '120 x 110 hexes from Finisterre to Menorca and from the Landes to the Rif, about 11 km per hex, as of 25 July 1936. Colours: the six sides; grey: city-states; black triangles: fugitives; dots: the 1936 railways.'
    for i, l in enumerate(wrap(draw, s, font(23), 1600)): draw.text(((W - draw.textlength(l, font=font(23))) / 2, 104 + i * 30), l, font=font(23), fill=INK2)
    m = preview(); h = 880; m = m.resize((round(m.width * h / m.height), h), Image.LANCZOS)
    img.paste(m, (60, 180))
    x, y = 60 + m.width + 50, 182; width = W - x - 50
    for key, leader, donor in SIDES:
        em = piece(f'emb_{leader}.png', 70); img.paste(em, (x, y), em)
        draw.text((x + 90, y - 2), F[key]['civ_short'], font=font(28, 'b'), fill=INK); draw.text((x + 90, y + 34), f"{F[key]['leader']}  ·  {donor}", font=font(20), fill=INK2); y += 84
    y = label(draw, (x, y + 10), 'Six city-states') + 2
    y = block(draw, (x, y), ', '.join(CS) + '.', font(21), width, INK2, 5)
    y = label(draw, (x, y + 14), 'Fugitives') + 2
    block(draw, (x, y), 'Men hiding in the sierras of the Nationalist zone, and after October 1937 in the mountains of Asturias and Leon: raging barbarians, bred by the empty land between the towns.', font(21), width, INK2, 5)
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
    y = label(draw, (x0, y + 16), 'On 25 July 1936'); y = block(draw, (x0, y), START[key], font(26), width, INK2) + 24
    y = label(draw, (x0, y), 'Dawn of Man'); block(draw, (x0, y), f['dawn'], font(23, 'i'), width, INK2, 6, max_y=H - 70)
    draw.text((W - 40 - draw.textlength('Spain 1936', font=font(26, 'b')), H - 56), 'Spain 1936', font=font(26, 'b'), fill=GOLD)
    save(img, os.path.join(OUT, f'{n:02d}_{key.lower()}.jpg'))

def events_card():
    img = Image.new('RGBA', (W, H), BG + (255,)); draw = ImageDraw.Draw(img)
    words = {48: 'Forty-eight'}; title = f'{words.get(len(EVENTS), len(EVENTS))} dated events'
    t = font(60, 'b'); draw.text(((W - draw.textlength(title, font=t)) / 2, 24), title, font=t, fill=INK)
    s = 'Each arrives on its historical week whoever is playing: reinforcements, foreign aid, gold, generals, wars and truces. The human player sees a popup.'
    draw.text(((W - draw.textlength(s, font=font(23))) / 2, 100), s, font=font(23), fill=INK2)
    cols = [('REP', 2), ('NAT', 1), ('NORTH', 1), ('CAT', 1), ('EUZ', 1), ('CNT', 1)]; cw = (W - 100) // 7; slot = 0   # the Republic's list takes two slots
    for side, span in cols:
        x = 50 + slot * cw; y = 160; slot += span
        draw.rectangle((x, y, x + span * cw - 16, y + 8), fill=rgb(PCOL[side][1] if side != 'NORTH' else PCOL[side][0])); y += 20
        draw.text((x, y), SIDE_NAME[side], font=fit(draw, SIDE_NAME[side], 26, span * cw - 20), fill=INK); y0 = y = y + 44
        rows = [(d, eid) for d, sd, eid in EVENTS if sd == side]; per = -(-len(rows) // span)
        for k, (d, eid) in enumerate(rows):
            if k and k % per == 0: x += cw; y = y0
            draw.text((x, y), date_text(d), font=font(20, 'b'), fill=GOLD); y += 26
            y = block(draw, (x, y), events_text.EVENTS[eid][0], font(22), cw - 30, INK2, 3) + 12
    y = 1030; draw.text((50, y), 'Fugitives:', font=font(22, 'b'), fill=INK)
    draw.text((180, y), '   '.join(f'{date_text(d)}  {events_text.EVENTS[eid][0]}' for d, sd, eid in EVENTS if sd == 'BARB'), font=font(21), fill=INK2)
    save(img, os.path.join(OUT, '08_events.jpg'))

cover()
map_card()
for n, (key, leader, donor) in enumerate(SIDES, 2): side_card(n, key, leader, donor)
events_card()
