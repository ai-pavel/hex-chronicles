#!/usr/bin/env python3
"""Generate the Hawaii 1778 art with Together AI (FLUX.2-dev by default): per chiefdom a wide diplomacy scene and a flat emblem,
plus icons for the cloned unique units and buildings, several variants of each, into art/gen/.  Then art/build_art.py pick
copies the variants named in its SELECT table into art/src, and art/build_art.py builds the DDS atlases, scenes and
Dawn of Man images (the round portrait is cut from the scene).

Key: $TOGETHER_API_KEY, or the file ~/.together_api_key.  Existing files in art/gen are kept, so a rerun only fills gaps;
delete a file to regenerate it.  Options: --model, --variants N, --only kona,maui, --kinds scene,emblem,unit,building.
"""
import argparse, base64, json, os, sys, time, urllib.request, subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.join(HERE, 'gen'); os.makedirs(GEN, exist_ok=True)
URL = 'https://api.together.xyz/v1/images/generations'

STYLE = ('Realistic oil painting in the style of a Civilization V leader screen, dignified and heroic, dramatic warm light, rich detail, '
         'no text, no letters, no signature, no watermark, no border.')
# key, name, person, place
PEOPLES = [
    ('KONA', 'Kamehameha', 'Kamehameha, a tall powerful young Hawaiian chief with a red and yellow feather cloak (ahuula) and a crested feather helmet (mahiole), holding a long wooden spear',
     'the black stone platform of a heiau temple on the dry Kohala coast with carved wooden kii images, war canoes drawn up on the beach, the snow-capped Mauna Kea far behind'),
    ('HILO', 'Keoua', 'Keoua Kuahuula, a fierce Hawaiian chief with long dark hair, a tapa cloth kihei knotted on one shoulder, a bone and shark-tooth weapon in his hand, tattooed arms',
     'the rainy green coast of Hilo with waterfalls, taro terraces, a steaming volcanic crater glowing red in the distance'),
    ('MAUI', 'Kahekili', 'Kahekili, king of Maui, an older Hawaiian chief tattooed solid black on the right half of his face and body, a feather cloak and a mahiole helmet, stern and commanding',
     'the green Iao valley of Maui with sharp cliffs and clouds, warriors with spears on the slopes'),
    ('OAHU', 'Kahahana', 'Kahahana, a young Hawaiian king in a yellow feather cloak with a kahili feather standard beside him, a necklace of braided hair with a whale-tooth pendant (lei niho palaoa)',
     'the bay of Waikiki with stone-walled fishponds, outrigger canoes, coconut palms and the crater of Leahi (Diamond Head) behind'),
    ('KAUAI', 'Kamakahelei', 'Kamakahelei, a dignified middle-aged Hawaiian chiefess in a long tapa cloth skirt and a short feather cape, a lei of maile leaves, holding a kahili feather standard',
     'the Wailua river valley of Kauai with taro terraces, high green cliffs streaked with waterfalls and mist'),
]
EMBLEMS = {
    'KONA': 'a carved Hawaiian kii tiki face with wide eyes and bared teeth',
    'HILO': 'a shark tooth weapon, a flat paddle-shaped club edged with triangular shark teeth',
    'MAUI': 'a stylised crested feather helmet (mahiole) seen in profile',
    'OAHU': 'an outrigger canoe with a crab-claw sail seen from the side',
    'KAUAI': 'a stylised taro plant with a heart-shaped leaf and a corm',
}
EMBLEM_STYLE = ('Flat vector emblem, one solid black symbol centered on a plain white background, bold simple shapes, thick lines, '
                'symmetrical, no shading, no gradients, no text, no letters, no frame, no background scene.')
# unit icons by unique key (text/uniques.py): black silhouettes turned into white glyphs by build_art.py
UNIT_ICONS = {
    'KOA': 'a Hawaiian warrior in a feather cape and crested helmet holding a flat club edged with shark teeth and a short spear',
    'POLOLU': 'a Hawaiian warrior in a loincloth holding a very long thin spear diagonally with both hands',   # a Spearman clone
    'PELELEU': 'a Hawaiian double-hulled war canoe with a crab-claw sail and warriors standing on the platform, seen from the side',
    'OLOHE': 'a Hawaiian lua fighter in a loincloth in a wide fighting stance, arms raised to grapple, bare-handed',
    'MAA': 'a Hawaiian warrior in a loincloth whirling a sling over his head, a stone in the pocket',
}
UNIT_ICON_STYLE = ('Solid black silhouette icon on a plain white background, one figure only, full body, clear readable outline, '
                   'thick simple shapes in the style of a strategy game unit icon, no text, no frame, no background scene, no shading.')
BUILDING_ICONS = {
    'PUUHONUA': 'a massive dry-stone wall of black lava rock with a thatched temple house and carved wooden kii figures inside, palms behind, the Hawaiian place of refuge',
    'LOKOIA': 'a Hawaiian fishpond: a curved stone wall across a shallow turquoise bay with a wooden sluice gate, fish in the water, palms on the shore',
    'LOIKALO': 'terraced taro paddies with heart-shaped leaves in flooded plots fed by a stone-lined ditch, green cliffs behind',
}
IMPROVEMENT_ICONS = {'KII': 'a tall carved wooden Hawaiian kii statue with a grimacing face and crested head standing on a black stone platform among palms'}
ACTION_ICONS = {'KII': 'a carved Hawaiian kii statue, a tall totem-like wooden figure with a grimacing face and a crest, seen from the front'}
# the eleven stock religions become Hawaiian cults; keys are the stock religion names (the slots), prompts the symbols
RELIGION_ICONS = {
    'BUDDHISM': 'a stylised sun with straight rays rising over a horizon line (Kane, the light)',
    'CHRISTIANITY': 'a fierce carved kii war-god head with a wide crested helmet and staring eyes (Ku)',
    'CONFUCIANISM': 'a tall pole with a crossbar hung with a long banner of tapa cloth and a bird on top, the Lono standard (Lono)',
    'HINDUISM': 'an octopus with eight curling arms seen from above (Kanaloa)',
    'ISLAM': 'a volcano cone with a crater and lava flames at the top (Pele)',
    'JUDAISM': 'a crescent moon with a woman\'s profile inside (Hina)',
    'SHINTO': 'a lei garland of flowers in a ring around a lehua blossom (Laka)',
    'SIKHISM': 'a breadfruit with its leaf, round and textured (Haumea)',
    'TAOISM': 'an island mountain rising from waves with a sun above (Papa, the earth)',
    'TENGRIISM': 'a boar\'s head with tusks seen from the front (Kamapuaa)',
    'ZOROASTRIANISM': 'a feathered god head with a crest and a wide grimacing mouth of dog teeth, the feather god (Kukailimoku)',
    'ORTHODOXY': 'a fish on a hook above two waves (Kuula, the god of fishermen)',
    'PROTESTANTISM': 'a shark seen from the side with a curved tail (Kamohoalii, the shark god)',
}
BUILDING_ICON_STYLE = ('Painted icon in the style of a Civilization V building icon: warm colours, clear central object, soft background, '
                       'square composition, no text, no letters, no frame, no people in the foreground unless mentioned.')

def jobs_for(variants, kinds, only):
    out = []
    for k, name, person, place in PEOPLES:
        if only and k not in only: continue
        if 'scene' in kinds: out.append((k, 'scene', f'{person}, standing full-length in {place}. Wide cinematic composition, the figure on the left third, landscape on the right. {STYLE}', 1792, 1024))
        if 'emblem' in kinds: out.append((k, 'emblem', f'{EMBLEMS[k]}. {EMBLEM_STYLE}', 1024, 1024))
    if 'unit' in kinds:
        for k, p in UNIT_ICONS.items():
            if not only or k in only: out.append((k, 'unit', f'{p}. {UNIT_ICON_STYLE}', 1024, 1024))
    if 'building' in kinds:
        for k, p in BUILDING_ICONS.items():
            if not only or k in only: out.append((k, 'building', f'{p}. {BUILDING_ICON_STYLE}', 1024, 1024))
    if 'improvement' in kinds:
        for k, p in IMPROVEMENT_ICONS.items():
            if not only or k in only: out.append((k, 'improvement', f'{p}. {BUILDING_ICON_STYLE}', 1024, 1024))
    if 'action' in kinds:
        for k, p in ACTION_ICONS.items():
            if not only or k in only: out.append((k, 'action', f'{p}. {UNIT_ICON_STYLE}', 1024, 1024))
    if 'religion' in kinds:
        for k, p in RELIGION_ICONS.items():
            if not only or k in only: out.append((k, 'religion', f'{p}. {EMBLEM_STYLE}', 1024, 1024))
    return [(os.path.join(GEN, f'{k}_{kind}_{v}.png'), prompt, w, h, 1000 + v) for k, kind, prompt, w, h in out for v in range(1, variants + 1)]

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
    ap.add_argument('--only', default='', help='comma-separated people or unique keys')
    ap.add_argument('--kinds', default='scene,emblem,unit,building,improvement,action,religion')
    ap.add_argument('--parallel', type=int, default=2)
    a = ap.parse_args()
    key_ = api_key()
    only = {s.strip().upper() for s in a.only.split(',') if s.strip()}
    jobs = [j for j in jobs_for(a.variants, a.kinds.split(','), only) if not os.path.exists(j[0])]
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
    for kind in ('scene', 'emblem', 'unit', 'building', 'improvement', 'action', 'religion'):
        files = sorted(f for f in os.listdir(GEN) if f'_{kind}_' in f and f.endswith('.png'))
        if not files: continue
        keys = []
        for f in files:
            k = f.split(f'_{kind}_')[0]
            if k not in keys: keys.append(k)
        args = ['magick']
        for k in keys: args += ['('] + sum([[os.path.join(GEN, f), '-resize', 'x300'] for f in files if f.startswith(k + f'_{kind}_')], []) + ['+append', ')']
        args += ['-background', '#333', '-append', os.path.join(GEN, f'contact_{kind}.jpg')]
        subprocess.run(args, check=True)
    print('contact sheets in', GEN)

if __name__ == '__main__':
    main()
