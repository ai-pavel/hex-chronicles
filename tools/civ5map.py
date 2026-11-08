#!/usr/bin/env python3
"""Read the header and type-name lists of a .Civ5Map written by the generators (format 0x8C with scenario data).

    python3 tools/civ5map.py path/to/Map.Civ5Map     prints a summary
    from civ5map import read_map                     returns a dict (see below)

Only the parts the tests and tooling need are decoded: the map size, player count, name, the terrain / feature /
wonder / resource / improvement / unit / tech / policy / building / promotion name lists, the victory and game-option
lists, the game speed and start year, plus the raw plot bytes (8 per hex) and the raw scenario section.
"""
import struct, sys


def _strlist(buf):
    return [s.decode() for s in buf.split(b'\0') if s]


def _plist(buf):
    out, i = [], 0
    while i < len(buf):
        n = buf[i]; out.append(buf[i + 1:i + 1 + n].decode()); i += n + 2
    return out


def read_map(path):
    b = open(path, 'rb').read()
    version, W, H, P = struct.unpack_from('<BIIB', b, 0); o = 14
    lt, lf, lw, lr, _, ln, ld = struct.unpack_from('<7I', b, o); o += 28
    terrains = _strlist(b[o:o + lt]); o += lt
    features = _strlist(b[o:o + lf]); o += lf
    wonders = _strlist(b[o:o + lw]); o += lw
    resources = _strlist(b[o:o + lr]); o += lr
    name = b[o:o + ln].rstrip(b'\0').decode(); o += ln
    desc = b[o:o + ld].rstrip(b'\0').decode(); o += ld
    (wl,) = struct.unpack_from('<I', b, o); o += 4
    world = b[o:o + wl].rstrip(b'\0').decode(); o += wl
    plots = b[o:o + W * H * 8]; o += W * H * 8
    hdr = struct.unpack_from('<64sIIIiBBBB9I', b, o); o += 120
    speed = hdr[0].rstrip(b'\0').decode(); year = hdr[4]; players, city_states, teams = hdr[5], hdr[6], hdr[7]
    li, lu, ltc, lp, lb, lpr, lud, _, lcd = hdr[9:]
    lv, lo = struct.unpack_from('<II', b, o); o += 8
    improvements = _strlist(b[o:o + li]); o += li
    units = _strlist(b[o:o + lu]); o += lu
    techs = _strlist(b[o:o + ltc]); o += ltc
    policies = _strlist(b[o:o + lp]); o += lp
    buildings = _strlist(b[o:o + lb]); o += lb
    promotions = _strlist(b[o:o + lpr]); o += lpr
    (unit_count,) = struct.unpack_from('<I', b, o); o += lud
    (city_count,) = struct.unpack_from('<I', b, o); o += lcd
    victories = _plist(b[o:o + lv]); o += lv
    options = _plist(b[o:o + lo]); o += lo
    return dict(version=version, width=W, height=H, players=P, name=name, description=desc, world_size=world,
                terrains=terrains, features=features, wonders=wonders, resources=resources, plots=plots,
                speed=speed, year=year, scenario_players=players, city_states=city_states, teams=teams,
                improvements=improvements, units=units, techs=techs, policies=policies, buildings=buildings,
                promotions=promotions, unit_count=unit_count, city_count=city_count, victories=victories,
                options=options, scenario=b[o:])


if __name__ == '__main__':
    for p in sys.argv[1:]:
        m = read_map(p)
        print(f"{m['name']}: {m['width']}x{m['height']}, {m['players']} players + {m['city_states']} city-states, {m['speed']}, year {m['year']}, "
              f"{m['city_count']} cities, {m['unit_count']} units, {len(m['techs'])} techs, {len(m['policies'])} policies, {len(m['buildings'])} buildings")
        print('  victories:', ', '.join(m['victories'])); print('  options:', ', '.join(m['options']))
