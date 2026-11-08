#!/usr/bin/env python3
"""Generate the Canarias 1400 leader art with Together AI (FLUX.2-dev by default): per people a wide diplomacy scene,
a flat emblem (and optionally a square portrait), several variants of each, into art/gen/.  Then run build_art.py,
which picks the variants named in its SELECT table and turns them into the DDS atlases, scenes and Dawn of Man images.

Key: $TOGETHER_API_KEY, or the file ~/.together_api_key.  Existing files in art/gen are kept, so a rerun only fills gaps;
delete a file to regenerate it.  Options: --model, --variants N, --only tenerife,lapalma, --kinds scene,portrait,emblem.

Cost at the default model is about 1.5 cents per image; the full set (7 peoples x 2 kinds x 2 variants) is about half a dollar.
"""
import argparse, base64, json, os, sys, time, urllib.request, subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.join(HERE, 'gen'); os.makedirs(GEN, exist_ok=True)
URL = 'https://api.together.xyz/v1/images/generations'

STYLE = ('Realistic oil painting in the style of a Civilization V leader screen, dignified and heroic, dramatic warm light, rich detail, '
         'no text, no letters, no signature, no watermark, no border.')
# key, name, person, place
PEOPLES = [
    ('TENERIFE', 'Bencomo', 'Bencomo, mencey of Taoro, a Guanche chieftain of 15th-century Tenerife: a tall bearded man with long dark hair in a goat-skin tamarco cloak, leather sandals, a long wooden staff',
     'a green slope of the Orotava valley with the snow-capped volcano Teide behind him under a clear blue sky'),
    ('GRANCANARIA', 'Tenesor Semidan', 'Tenesor Semidan, guanarteme of Galdar, king of the Canarii of Gran Canaria: a mature man with a short grey beard, a long goat-skin cloak dyed red and white, a wooden sceptre, a necklace of clay beads',
     'the painted cave of Galdar with red, white and black geometric murals on the rock, terraces and the sacred rock Roque Nublo in the distance'),
    ('LAPALMA', 'Tanausu', 'Tanausu, chief of Acero on La Palma: a lean, hard-faced warrior with long black hair, a goat-skin cloak and a heavy wooden club',
     'the rim of the Caldera de Taburiente, a vast green volcanic crater with pine trees and steep cliffs, mist in the depths'),
    ('LAGOMERA', 'Hautacuperche', 'Hautacuperche, a young Gomero warrior of La Gomera: a wiry man with curly black hair, a short goat-skin tunic, fingers raised to his mouth as if whistling, a sling at his belt',
     'a deep green ravine of La Gomera with terraced fields on the cliffs and the misty laurel forest of Garajonay above'),
    ('ELHIERRO', 'Armiche', 'Armiche, king of the Bimbaches of El Hierro: an older man with weathered skin and white hair, a simple goat-skin cloak, holding a clay water jar',
     'the sacred laurel tree Garoe dripping mist water into stone basins, dry volcanic slopes and the Atlantic ocean behind'),
    ('FUERTEVENTURA', 'Guize', 'Guize, king of Maxorata on Fuerteventura: a sun-darkened shepherd king with a short beard, a goat-skin cloak, a staff, goats at his feet',
     'a dry plain of sand and wind-swept hills, the sacred mountain Tindaya, a low stone wall running to the horizon'),
    ('LANZAROTE', 'Guadarfia', 'Guadarfia, king of Titerogaka on Lanzarote: a strong middle-aged man with dark braided hair, a goat-skin cloak and a necklace of shells, a spear in hand',
     'black lava fields and red volcanic cones by the sea, a stone-walled village, a sail on the horizon'),
]
# flat emblems: a single bold symbol, black on white, later turned into the white glyph and the coloured disc by build_art.py
EMBLEMS = {
    'TENERIFE': 'a stylised volcano peak with a spiral sun above it',
    'GRANCANARIA': 'a Guanche pintadera stamp: concentric triangles and zigzag lines inside a circle',
    'LAPALMA': 'a large spiral petroglyph, a single thick spiral line',
    'LAGOMERA': 'three nested curved sound waves above a mountain silhouette',
    'ELHIERRO': 'a round laurel tree with three water drops falling from its crown',
    'FUERTEVENTURA': 'a pair of bare footprints side by side, like the Tindaya rock engravings',
    'LANZAROTE': 'a volcanic crater ring with a wave below it',
}
# unit icons: black silhouettes on white, turned into the white glyphs of a Civ V unit atlas by build_art.py
UNIT_ICONS = {
    'TENERIFE': 'a Guanche warrior in a goat-skin cloak holding a long wooden spear upright and a round wooden shield',
    'GRANCANARIA': 'a warrior in a short goat-skin tunic winding up to throw a stone, one arm back',
    'LAPALMA': 'a warrior in a goat-skin cloak raising a heavy wooden club over his shoulder',
    'LAGOMERA': 'a slim man whistling with two fingers at his mouth, the other hand shading his eyes',
    'ELHIERRO': 'a small dugout boat seen from the side with one man and a basket of shellfish',
    'FUERTEVENTURA': 'a warrior holding a very long lance diagonally with both hands',
    'LANZAROTE': 'a warrior with a short spear and a shield stepping forward out of a wave',
}
UNIT_ICON_STYLE = ('Solid black silhouette icon on a plain white background, one figure only, full body, clear readable outline, '
                   'thick simple shapes in the style of a strategy game unit icon, no text, no frame, no background scene, no shading.')
# building icons: painted, later cut into the same round frame as the leader portraits
BUILDING_ICONS = {
    'TENERIFE': 'a ring of standing stones on a grassy hilltop with one larger stone seat, the Guanche council place tagoror',
    'GRANCANARIA': 'a cliff face honeycombed with small square cave chambers under a natural rock arch, the Cenobio de Valeron granary',
    'LAPALMA': 'cave dwellings cut into a volcanic cliff in terraces with ladders and small walls',
    'ELHIERRO': 'a small stone altar with a clay bowl at the mouth of a cave, mist and clouds gathering above, a shepherd praying',
    'FUERTEVENTURA': 'a round dry-stone corral full of goats on a sandy plain with a stone wall',
    'LANZAROTE': 'a walled rain cistern, a stone-lined pond full of water in black volcanic ground',
}
BUILDING_ICON_STYLE = ('Painted icon in the style of a Civilization V building icon: warm colours, clear central object, soft background, '
                       'square composition, no text, no letters, no frame, no people in the foreground unless mentioned.')
# the eleven stock religions become the cults of the islands' gods; keys are the stock religion names (the slots), prompts the symbols
RELIGION_ICONS = {
    'BUDDHISM': 'a sun disc above a mountain peak with rays (Achaman, the sky father of Tenerife)',
    'CHRISTIANITY': 'a sun with wavy rays in a circle, like a Guanche spiral petroglyph (Magec, the sun)',
    'CONFUCIANISM': 'a stylised mother figure with a child, in simple strokes, inside a circle (Chaxiraxi)',
    'HINDUISM': 'a crescent moon with a small star, thick strokes (Achuguayo, the moon)',
    'ISLAM': 'a cloud with three falling rain drops (Achuhucanac, the rain)',
    'JUDAISM': 'a Guanche pintadera stamp of concentric circles with a dot in the middle (Acoran, the god of Gran Canaria)',
    'SHINTO': 'a triangle inside a circle with a zigzag band, a pintadera stamp (Alcorac)',
    'SIKHISM': 'a six-pointed star made of straight strokes (Abora, the god of La Palma)',
    'TAOISM': 'an open hand with the palm forward and rays around it (Orahan, the god of La Gomera)',
    'TENGRIISM': 'a ram\'s head with curled horns seen from the front (Eraoranhan, the god of El Hierro)',
    'ZOROASTRIANISM': 'a wave with a seashell above it (Moneiba, the goddess of El Hierro)',
    'ORTHODOXY': 'a small child figure standing inside a sun disc with rays (Chijoraji, the child of Chaxiraxi)',
    'PROTESTANTISM': 'a black dog head with pointed ears and bared teeth in front of a mountain peak (Guayota, the spirit of Echeyde)',
}
EMBLEM_STYLE = ('Flat vector emblem, one solid black symbol centered on a plain white background, bold simple shapes, thick lines, '
                'symmetrical, no shading, no gradients, no text, no letters, no frame, no background scene.')

def prompts(key):
    name, person, place = next((n, p, pl) for k, n, p, pl in PEOPLES if k == key)
    return {
        'scene': (f'{person}, standing full-length in {place}. Wide cinematic composition, the figure on the left third, landscape on the right. {STYLE}', 1792, 1024),
        'portrait': (f'Head-and-shoulders portrait of {person}, looking slightly past the viewer, {place} softly blurred behind. {STYLE}', 1024, 1024),
        'emblem': (f'{EMBLEMS[key]}. {EMBLEM_STYLE}', 1024, 1024),
        'unit': (f'{UNIT_ICONS[key]}. {UNIT_ICON_STYLE}', 1024, 1024),
        'building': (f'{BUILDING_ICONS[key]}. {BUILDING_ICON_STYLE}', 1024, 1024) if key in BUILDING_ICONS else None,
    }

def religion_jobs(variants, only):
    return [(os.path.join(GEN, f'{k}_religion_{v}.png'), f'{p}. {EMBLEM_STYLE}', 1024, 1024, 1000 + v) for k, p in RELIGION_ICONS.items() if not only or k in only for v in range(1, variants + 1)]

def api_key():
    k = os.environ.get('TOGETHER_API_KEY')
    if not k:
        p = os.path.expanduser('~/.together_api_key')
        if os.path.exists(p): k = open(p).read().strip()
    if not k: sys.exit('no API key: set TOGETHER_API_KEY or create ~/.together_api_key')
    return k

def generate(key_, model, prompt, w, h, steps, seed):
    body = dict(model=model, prompt=prompt, width=w, height=h, steps=steps, n=1, seed=seed, response_format='b64_json')
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Bearer ' + key_, 'Content-Type': 'application/json', 'User-Agent': 'curl/8.7.1', 'Accept': 'application/json'})
    for attempt in range(8):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=300))
            return base64.b64decode(r['data'][0]['b64_json'])
        except urllib.error.HTTPError as e:
            msg = e.read()[:200]
            if e.code in (429, 500, 502, 503) and attempt < 7:
                wait = 3 * 2 ** attempt; print(f'  HTTP {e.code}, retry in {wait}s'); time.sleep(wait); continue
            raise RuntimeError(f'HTTP {e.code}: {msg}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='black-forest-labs/FLUX.2-dev')
    ap.add_argument('--variants', type=int, default=2)
    ap.add_argument('--steps', type=int, default=28)
    ap.add_argument('--only', default='', help='comma-separated people keys (case-insensitive)')
    ap.add_argument('--kinds', default='scene,emblem,unit,building,religion', help='portrait is also available, but the build cuts the portrait from the scene')
    ap.add_argument('--parallel', type=int, default=2)
    a = ap.parse_args()
    key_ = api_key()
    only = {s.strip().upper() for s in a.only.split(',') if s.strip()}
    jobs = []
    for k, name, _, _ in PEOPLES:
        if only and k not in only: continue
        for kind, spec in prompts(k).items():
            if kind not in a.kinds.split(',') or spec is None: continue
            prompt, w, h = spec
            for v in range(1, a.variants + 1):
                out = os.path.join(GEN, f'{k}_{kind}_{v}.png')
                if os.path.exists(out): continue
                jobs.append((out, prompt, w, h, 1000 + v))
    if 'religion' in a.kinds.split(','): jobs += [j for j in religion_jobs(a.variants, only) if not os.path.exists(j[0])]
    print(f'{len(jobs)} images to generate with {a.model}')
    failed = []
    def run(job):
        out, prompt, w, h, seed = job; t = time.time()
        try:
            png = generate(key_, a.model, prompt, w, h, a.steps, seed)
            open(out, 'wb').write(png); print(f'  {os.path.basename(out)} ({time.time() - t:.0f}s)', flush=True)
        except Exception as e:
            failed.append(out); print(f'  FAILED {os.path.basename(out)}: {e}', flush=True)
    with ThreadPoolExecutor(a.parallel) as ex: list(ex.map(run, jobs))
    if failed: print(f'{len(failed)} failed; rerun to retry them')
    # contact sheet per kind
    for kind in ('scene', 'portrait', 'emblem', 'unit', 'building', 'religion'):
        files = sorted(f for f in os.listdir(GEN) if f'_{kind}_' in f and f.endswith('.png'))
        if not files: continue
        rows = []
        for k in ([k for k, *_ in PEOPLES] + list(RELIGION_ICONS)):
            mine = [os.path.join(GEN, f) for f in files if f.startswith(k + '_')]
            if mine: rows.append(mine)
        args = ['magick']
        for r in rows: args += ['('] + sum([[f, '-resize', 'x300'] for f in r], []) + ['+append', ')']
        args += ['-background', '#333', '-append', os.path.join(GEN, f'contact_{kind}.jpg')]
        subprocess.run(args, check=True)
    print('contact sheets in', GEN)

if __name__ == '__main__':
    main()
