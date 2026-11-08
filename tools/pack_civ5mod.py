#!/usr/bin/env python3
"""Pack a built mod into a release archive for distribution outside the Steam Workshop (CivFanatics, Nexus).

  python3 tools/pack_civ5mod.py src/canarias-1400            check the mod folder and write dist/<Mod> (v N).civ5mod
  python3 tools/pack_civ5mod.py src/canarias-1400 --check    check only

A .civ5mod is a 7-Zip archive with the mod's files at its root; the game unpacks it into MODS/<archive name>/ when the Mods menu
is opened. Before packing, the script copies the DDS textures from art/out into the mod folder when they are missing (the textures
are committed in mod/ but art/out is the build output), then checks that every file the .modinfo lists exists with the listed MD5 and that no unlisted file lies in
the folder. The archive goes to dist/ (not committed). Needs 7zz (brew install sevenzip) or 7z (p7zip)."""
import glob, hashlib, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) < 2 or sys.argv[1].startswith('-'): raise SystemExit(__doc__)
src = os.path.abspath(sys.argv[1]); check_only = '--check' in sys.argv
modinfos = glob.glob(os.path.join(src, 'mod', '*', '*.modinfo'))
if len(modinfos) != 1: raise SystemExit(f'expected one mod/*/*.modinfo under {src}, found {len(modinfos)}')
modinfo = modinfos[0]; mod_dir = os.path.dirname(modinfo); name = os.path.basename(mod_dir)
text = open(modinfo, encoding='utf-8').read()
entries = re.findall(r'<File md5="([0-9A-F]{32})" import="[01]">([^<]+)</File>', text)
version = re.search(r'<Mod id="[^"]+" version="(\d+)"', text).group(1)
if not name.endswith(f'(v {version})'): raise SystemExit(f'folder {name!r} does not match modinfo version {version}')

copied = 0; art_out = os.path.join(src, 'art', 'out')
for _, fn in entries:
    p = os.path.join(mod_dir, fn)
    if not os.path.exists(p) and fn.lower().endswith('.dds') and os.path.exists(os.path.join(art_out, fn)):
        shutil.copy(os.path.join(art_out, fn), p); copied += 1
if copied: print(f'copied {copied} textures from art/out')

errors = []
for md5, fn in entries:
    p = os.path.join(mod_dir, fn)
    if not os.path.exists(p): errors.append(f'missing: {fn}' + (' (run art/build_art.py)' if fn.lower().endswith('.dds') else '')); continue
    if hashlib.md5(open(p, 'rb').read()).hexdigest().upper() != md5: errors.append(f'md5 differs: {fn}')
listed = {fn for _, fn in entries} | {os.path.basename(modinfo)}
for fn in sorted(os.listdir(mod_dir)):
    if fn not in listed and fn not in ('.DS_Store', 'CREDITS.txt'): errors.append(f'not in modinfo: {fn}')   # credits ride along unlisted in some mods
for fn in ('Authors', 'Teaser', 'Description'):
    m = re.search(rf'<{fn}>([^<]*)</{fn}>', text)
    if not m or not m.group(1).strip() or 'Claude' in m.group(1): errors.append(f'modinfo <{fn}> needs a real value')
if errors: raise SystemExit('\n'.join(errors))
size = sum(os.path.getsize(os.path.join(mod_dir, fn)) for fn in os.listdir(mod_dir))
print(f'{name}: {len(entries)} files listed, all present, MD5s match, {size / 1e6:.1f} MB unpacked')
if check_only: sys.exit(0)

seven = shutil.which('7zz') or shutil.which('7z')
if not seven: raise SystemExit('7zz not found: brew install sevenzip')
dist = os.path.join(ROOT, 'dist'); os.makedirs(dist, exist_ok=True)
out = os.path.join(dist, name + '.civ5mod')
if os.path.exists(out): os.remove(out)
r = subprocess.run([seven, 'a', '-t7z', '-mx=7', '-x!.DS_Store', out, '.'], cwd=mod_dir, capture_output=True, text=True)
if r.returncode: raise SystemExit(r.stdout + r.stderr)
print(f'wrote {os.path.relpath(out, ROOT)} ({os.path.getsize(out) / 1e6:.2f} MB)')
