#!/usr/bin/env python3
"""Workshop and CivFanatics page images for Arcanum 1885, composed from the generator's map preview and the scenario text
(text/build_text.py) with Pillow.  The mod has no art of its own (the leader scenes are Firaxis' Smoky Skies ones), so the cards
are a map with the nations and free cities, a card of the five nations, and a card of the rules and the natural wonders.

  python3 src/arcanum-1885/publish/make_screens.py      -> publish/screens/*.jpg, 1920x1080"""
import os, re, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(HERE); OUT = os.path.join(HERE, 'screens'); os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080
FONTS = '/System/Library/Fonts/Supplemental/'
def font(size, style=''): return ImageFont.truetype(FONTS + {'': 'Georgia.ttf', 'b': 'Georgia Bold.ttf', 'i': 'Georgia Italic.ttf'}[style], size)
INK = (232, 212, 160); INK2 = (196, 188, 172); GOLD = (226, 185, 106); BG = (26, 22, 19); PANEL = (40, 34, 28)
ORDER = ['ENGLAND', 'FRANCE', 'RUSSIA', 'GERMANY', 'SWEDEN']
DONOR = {'ENGLAND': 'England', 'FRANCE': 'France', 'RUSSIA': 'Russia', 'GERMANY': 'Germany', 'SWEDEN': 'Sweden'}
PCOL = {'ENGLAND': ('#C9A227', '#2B2B2B'), 'FRANCE': ('#F2F2F2', '#1F4E9A'), 'RUSSIA': ('#FFFFFF', '#8B1A1A'), 'GERMANY': ('#FFB347', '#5A3A1A'), 'SWEDEN': ('#B5F5EC', '#0F5F5C')}
CS = [('Qintarra', 'cultured'), ('Ashbury', 'mercantile'), ('Black Root', 'maritime'), ('Stillwater', 'militaristic'), ('Shrouded Hills', 'mercantile'),
      ('Roseborough', 'cultured'), ('Tulla', 'cultured'), ('Isle of Despair', 'militaristic'), ('Bedokaan', 'maritime'), ("T'sen-Ang", 'militaristic')]
WONDERS = ["Bellerogrim's Lair", 'Ancient Temple of Derian-Ka', 'Elven Burial Site', 'Ruins of Kree', 'Rock of Despair', 'Ring of Brodgar',
           "Falcon's Ache", 'Bangellian Deeps', "Lethe Wyvern's Lair", 'Stonewall Peak', 'Mines of the Wheel Clan', "Torg's Altar"]

# the English nation table of text/build_text.py (name, long, leader, dawn), read from the source so the cards follow the text
src = open(os.path.join(MOD, 'text', 'build_text.py'), encoding='utf-8').read()
NATIONS = {}
for civ in ORDER:
    block = src[src.index(f" '{civ}': dict(en=dict("):]
    f = {k: re.search(rf"\b{k}='([^']*)'", block).group(1) for k in ('name', 'long', 'adj', 'leader')}
    f['dawn'] = eval(re.search(r'dawn=((?:"[^"]*"\s*\+\s*NL\s*\+\s*)*"[^"]*")', block).group(1), {'NL': '[NEWLINE][NEWLINE]'})   # both paragraphs
    NATIONS[civ] = f

def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def wrap(draw, text, f, width):
    lines, line = [], ''
    for word in text.split():
        t = (line + ' ' + word).strip()
        if draw.textlength(t, font=f) <= width: line = t
        else: lines.append(line); line = word
    return lines + [line]
def block(draw, xy, text, f, width, fill, gap=7):
    x, y = xy
    for l in wrap(draw, text, f, width): draw.text((x, y), l, font=f, fill=fill); y += f.size + gap
    return y
def label(draw, xy, text): draw.text(xy, text.upper(), font=font(22, 'b'), fill=GOLD); return xy[1] + 34
def title(draw, text, y=28, size=72):
    t = font(size, 'b'); draw.text(((W - draw.textlength(text, font=t)) / 2, y), text, font=t, fill=INK)
def disc(img, xy, civ, size=72):
    d = ImageDraw.Draw(img); x, y = xy; icon, bg = PCOL[civ]
    d.ellipse((x, y, x + size, y + size), fill=rgb(bg), outline=GOLD, width=3); d.ellipse((x + size * 0.3, y + size * 0.3, x + size * 0.7, y + size * 0.7), fill=rgb(icon))
def save(img, name): img.convert('RGB').save(os.path.join(OUT, name), quality=90, optimize=True); print('wrote', name)

def map_card():
    img = Image.new('RGB', (W, H), BG); draw = ImageDraw.Draw(img)
    title(draw, 'Arcanum 1885')
    s = 'The continent of Arcanum on 92 x 112 hexes, parsed from a fan map. Gold squares: the five nations. White circles: the ten free cities. Magenta: twelve natural wonders at lore sites.'
    for i, l in enumerate(wrap(draw, s, font(24), 1500)): draw.text(((W - draw.textlength(l, font=font(24))) / 2, 112 + i * 32), l, font=font(24), fill=INK2)
    m = Image.open(os.path.join(MOD, 'Arcanum1885_preview.png')).convert('RGB'); m = m.resize((round(m.width * 860 / m.height), 860), Image.LANCZOS)
    img.paste(m, (120, 200))
    x, y = 1060, 250; label(draw, (x, 208), 'Nations')
    for civ in ORDER:
        n = NATIONS[civ]; disc(img, (x, y), civ, 64)
        draw.text((x + 84, y - 2), n['name'], font=font(30, 'b'), fill=INK); draw.text((x + 84, y + 36), f"{n['leader']}  ·  Smoky Skies {DONOR[civ]}", font=font(21), fill=INK2); y += 80
    y = label(draw, (x, y + 22), 'Free cities (city-states)') + 12
    for i, (name, trait) in enumerate(CS):
        cx = x + (i % 2) * 400; cy = y + (i // 2) * 62
        draw.ellipse((cx + 18, cy + 14, cx + 46, cy + 42), outline=INK, width=3)
        draw.text((cx + 64, cy + 4), name, font=font(26, 'b'), fill=INK); draw.text((cx + 64, cy + 34), trait, font=font(19, 'i'), fill=INK2)
    save(img, '01_map.jpg')

def nations_card():
    img = Image.new('RGB', (W, H), BG); draw = ImageDraw.Draw(img)
    title(draw, 'Five nations, one continent', 24, 60)
    s = 'Each nation is one of the five re-skinned civilizations of Empires of the Smoky Skies: its leader scene, traits and steampunk units under an Arcanum name, starting with a Settler, a guard and a Worker at its lore capital.'
    for i, l in enumerate(wrap(draw, s, font(23), 1500)): draw.text(((W - draw.textlength(l, font=font(23))) / 2, 104 + i * 30), l, font=font(23), fill=INK2)
    cw, gap = 352, 20; x0 = (W - 5 * cw - 4 * gap) // 2; y0 = 190
    for i, civ in enumerate(ORDER):
        n = NATIONS[civ]; x = x0 + i * (cw + gap)
        draw.rectangle((x, y0, x + cw, H - 60), fill=PANEL); draw.rectangle((x, y0, x + cw, y0 + 10), fill=rgb(PCOL[civ][1]))
        disc(img, (x + 20, y0 + 30), civ, 60)
        nf = font(34, 'b')
        while draw.textlength(n['name'], font=nf) > cw - 110: nf = font(nf.size - 2, 'b')
        draw.text((x + 96, y0 + 36), n['name'], font=nf, fill=INK)
        y = block(draw, (x + 20, y0 + 110), n['long'], font(22, 'i'), cw - 40, INK2) + 2
        y = block(draw, (x + 20, y), n['leader'], font(22), cw - 40, INK) + 16
        for para in n['dawn'].split('[NEWLINE][NEWLINE]'): y = block(draw, (x + 20, y), para, font(22), cw - 40, INK2, 6) + 16
        draw.text((x + 20, H - 110), f'Smoky Skies {DONOR[civ]}', font=font(19, 'i'), fill=GOLD)
    save(img, '02_nations.jpg')

def rules_card():
    img = Image.new('RGB', (W, H), BG); draw = ImageDraw.Draw(img)
    title(draw, 'Steam against magick', 24, 60)
    x = 110; y = label(draw, (x, 140), 'The rules of Empires of the Smoky Skies')
    for s in ('The pruned tech tree with 23 steampunk technologies, 6 air and land units, the five-branch policy tree of the scenario, plus the three Brave New World ideologies with their tenets.',
              'Industrial-era start in the year 1885 of the Arcanum calendar, one turn = one year, Huge map, no turn limit, Quick speed.',
              'Raging barbarians, no goody huts, no religion, policy saving on. Resources are randomised by the game at every start, so no two games are alike.',
              'Victories: domination, cultural (tourism, with the Hotel, Airport, Visitor Centre and Stadium rescued onto steampunk techs) and diplomatic (World Congress, United Nations). Science victory off.'):
        y = block(draw, (x, y), s, font(24), 860, INK2) + 14
    y += 6; y = label(draw, (x, y), 'Free cities')
    y = block(draw, (x, y), ', '.join(f'{n} ({t})' for n, t in CS) + '. Population 3, a Monument and Walls, a guard and a worker each.', font(22), 860, INK2)
    x = 1060; y = label(draw, (x, 140), 'Twelve natural wonders at their lore sites')
    for i, w in enumerate(WONDERS):
        draw.ellipse((x + 2, y + 10, x + 14, y + 22), fill=(230, 80, 220)); draw.text((x + 30, y), w, font=font(27), fill=INK); y += 44
    y += 20; y = label(draw, (x, y), 'Requirements')
    block(draw, (x, y), 'Civilization V with Gods & Kings and Brave New World. Single player. Windows and Mac. Enable this mod alone.', font(22), 760, INK2)
    draw.text((W - 40 - draw.textlength('Arcanum 1885', font=font(26, 'b')), H - 56), 'Arcanum 1885', font=font(26, 'b'), fill=GOLD)
    save(img, '03_rules.jpg')

map_card(); nations_card(); rules_card()
