#!/usr/bin/env python3
"""Measure the distances between the cities of built scenario maps (the hex distance between the city plots).

  python3 tools/city_spacing.py                       every src/*/mod/*/*.Civ5Map
  python3 tools/city_spacing.py src/china-1928        the maps under the given folders (a mod, a mod/ folder, the game's MODS)
  python3 tools/city_spacing.py -v ...                also list the pairs closer than 4 hexes
  python3 tools/city_spacing.py --check ...           exit 1 when two cities stand closer than 3 hexes

The rule the generators enforce: no two cities closer than 3 hexes, and 4 within a side unless both are capitals or key
towns. Only the map is read, so the tool cannot tell key towns apart: it reports the pairs at 3 hexes within a side for a
look, and fails only on the hard minimum. EXCEPTIONS lists the few pairs kept closer on purpose. Cities come from the plot scenario records (the last 8 bytes per hex: city id,
unit id, owner, ...) and their names from the city records (136 bytes each, the name first).
"""
import glob, os, struct, sys
from civ5map import read_map

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARD_MIN = 3        # between any two cities
SIDE_MIN = 4        # between two cities of one side, unless both are key towns
CITY_REC = 136
EXCEPTIONS = {('China 1928', frozenset({'Hong Kong', 'Macau'}))}   # kept on purpose: two colonies about 60 km apart


def hexdist(a, b):
    def cube(x, y):
        q = x - (y - (y & 1)) // 2; return q, y, -q - y
    (aq, ar, as_), (bq, br, bs) = cube(*a), cube(*b)
    return max(abs(aq - bq), abs(ar - br), abs(as_ - bs))


def cities(path):
    """[(x, y), name, owner] for every city on the map."""
    m = read_map(path); W, H = m['width'], m['height']; b = open(path, 'rb').read()
    o = b.index(m['plots']) + W * H * 8
    li, lu, ltc, lp, lb, lpr, lud, _, lcd = struct.unpack_from('<64sIIIiBBBB9I', b, o)[9:]
    o += 120 + 8 + li + lu + ltc + lp + lb + lpr + lud
    count = struct.unpack_from('<I', b, o)[0]
    names = [b[o + 4 + i * CITY_REC:o + 4 + i * CITY_REC + 64].split(b'\0')[0].decode('utf-8', 'replace') for i in range(count)]
    plots = b[-W * H * 8:]; out = []
    for y in range(H):
        for x in range(W):
            cid, _, owner = struct.unpack_from('<HHB', plots, (y * W + x) * 8)
            if cid != 0xFFFF: out.append(((x, y), names[cid] if cid < len(names) else f'#{cid}', owner))
    return m['name'], out


def report(path, verbose):
    name, cs = cities(path)
    pairs = sorted((hexdist(a[0], c[0]), a[1], c[1], a[2] == c[2]) for i, a in enumerate(cs) for c in cs[i + 1:])
    low = [p for p in pairs if p[0] < HARD_MIN and (name, frozenset(p[1:3])) not in EXCEPTIONS]
    side = [p for p in pairs if p[3] and HARD_MIN <= p[0] < SIDE_MIN]
    print(f"{name}: {len(cs)} cities, closest {pairs[0][0] if pairs else '-'} hexes; "
          f"closer than {HARD_MIN}: {len(low)}; {HARD_MIN} within a side: {len(side)}")
    if verbose:
        for d, a, c, same in [p for p in pairs if p[0] < SIDE_MIN]:
            print(f"   {d}  {a} - {c}{'  (one side)' if same else ''}")
    return not low


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    roots = args or [os.path.join(ROOT, 'src')]
    maps = sorted({p for r in roots for p in glob.glob(os.path.join(os.path.expanduser(r), '**', '*.Civ5Map'), recursive=True)})
    ok = all([report(p, '-v' in sys.argv) for p in maps])
    if '--check' in sys.argv and not ok: sys.exit(1)
