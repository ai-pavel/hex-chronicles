#!/usr/bin/env python3
"""Extract the type-name lists the generators need from an installed Civilization V (with Gods & Kings and Brave New World)
into <repo>/data/xml (or $HEX_XML).

  TECH_.txt                    every TECH_* defined by the base game or either expansion, sorted by name (the map header lists them by name;
                               names the loaded ruleset does not know are ignored by the game)
  TECH_ERAS.json               tech -> era, base game first, each expansion overriding
  TECHS_THROUGH_INDUSTRIAL.txt Brave New World techs up to the Industrial era, in tech-tree (file) order
  WORLD_WONDERS.txt            every building whose class allows one instance in the world, including the DLC wonders, sorted by name
  LEADER_DIALOG_KEYS.txt       every TXT_KEY_LEADER_* tag of the English leader dialogue files (the text builders replace the
                               ones of the donor leaders), sorted

Set CIV5_ASSETS to the game's Assets folder if it is not in the default Steam location.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('HEX_XML', os.path.join(os.path.dirname(HERE), 'data', 'xml'))
DEFAULT_ASSETS = [
    os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/Sid Meier's Civilization V/Civilization V.app/Contents/Assets/Assets"),
    r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization V\Assets",
    os.path.expanduser("~/.steam/steam/steamapps/common/Sid Meier's Civilization V/steamassets/assets"),
]
ASSETS = os.environ.get('CIV5_ASSETS') or next((p for p in DEFAULT_ASSETS if os.path.isdir(p)), None)
if not ASSETS or not os.path.isdir(ASSETS):
    sys.exit('Civilization V Assets folder not found; set CIV5_ASSETS')
RULESETS = ['Gameplay/XML', 'DLC/Expansion/Gameplay/XML', 'DLC/Expansion2/Gameplay/XML']   # base, Gods & Kings, Brave New World
DLC_PACKS = [f'DLC/DLC_0{i}/Gameplay/XML' for i in range(1, 8)]   # civ packs and Wonders of the Ancient World (flat folders)
EARLY_ERAS = {'ERA_ANCIENT', 'ERA_CLASSICAL', 'ERA_MEDIEVAL', 'ERA_RENAISSANCE', 'ERA_INDUSTRIAL'}


def read(rel):
    return open(os.path.join(ASSETS, rel), encoding='utf-8', errors='replace').read()


def rows(text, table):
    """The <Row> elements of one <table> as dicts of child tag -> text (Firaxis XML is flat enough for a regex)."""
    m = re.search(rf'<{table}>(.*?)</{table}>', text, re.S)
    if not m: return []
    return [dict(re.findall(r'<(\w+)>([^<]*)</\1>', r)) for r in re.findall(r'<Row>(.*?)</Row>', m.group(1), re.S)]


def xml_files(subdir, packs=False):
    out = []
    for rs in RULESETS + (DLC_PACKS if packs else []):
        d = os.path.join(ASSETS, rs, subdir)
        if os.path.isdir(d): out += sorted(os.path.join(rs, subdir, f) for f in os.listdir(d) if f.lower().endswith('.xml'))
    return out


def name_order(s):
    """Sort like the game's own listings: underscores as spaces, case ignored (TECH_METAL_CASTING before TECH_METALLURGY)."""
    return s.replace('_', ' ').lower()


def main():
    os.makedirs(OUT, exist_ok=True)
    eras, order_bnw = {}, []
    for rel in xml_files('Technologies'):
        for r in rows(read(rel), 'Technologies'):
            if 'Type' in r and 'Era' in r:
                eras[r['Type']] = r['Era']
                if rel.startswith('DLC/Expansion2/'): order_bnw.append(r['Type'])
    open(os.path.join(OUT, 'TECH_.txt'), 'w').write(''.join(t + '\n' for t in sorted(eras, key=name_order)))
    json.dump(eras, open(os.path.join(OUT, 'TECH_ERAS.json'), 'w'), indent=1, sort_keys=True)
    open(os.path.join(OUT, 'TECHS_THROUGH_INDUSTRIAL.txt'), 'w').write(''.join(t + '\n' for t in order_bnw if eras[t] in EARLY_ERAS))

    world_classes = set()
    for rel in xml_files('Buildings', packs=True) + xml_files('', packs=True):
        for r in rows(read(rel), 'BuildingClasses'):
            if r.get('Type') and r.get('MaxGlobalInstances') == '1': world_classes.add(r['Type'])
    wonders = set()
    for rel in xml_files('Buildings', packs=True) + xml_files('', packs=True):
        for r in rows(read(rel), 'Buildings'):
            if r.get('Type') and r.get('BuildingClass') in world_classes: wonders.add(r['Type'])
    open(os.path.join(OUT, 'WORLD_WONDERS.txt'), 'w').write(''.join(w + '\n' for w in sorted(wonders, key=name_order)))
    keys = set()
    for root, dirs, files in os.walk(ASSETS):
        if os.path.basename(root) == 'LeaderDialog' and os.path.basename(os.path.dirname(root)).lower() == 'en_us':
            for f in files:
                if f.lower().endswith('.xml'): keys.update(re.findall(r'Tag="(TXT_KEY_LEADER_[A-Z0-9_]+)"', read(os.path.join(root, f))))
    open(os.path.join(OUT, 'LEADER_DIALOG_KEYS.txt'), 'w').write(''.join(k + '\n' for k in sorted(keys)))
    print(f'{len(eras)} techs, {len(order_bnw)} in Brave New World, {len(wonders)} world wonders, {len(keys)} leader dialogue keys -> {OUT}')


if __name__ == '__main__':
    main()
