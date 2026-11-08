"""Consistency checks on the built mods in */mod: the map parses, the modinfo lists the map with correct MD5s, and
(when data/xml exists) the type lists inside the maps and rules match what the extractor produces.
Run: python3 -m unittest discover tests"""
import glob, hashlib, os, re, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from civ5map import read_map  # noqa: E402

XML = os.environ.get('HEX_XML', os.path.join(ROOT, 'data', 'xml'))
MODS = sorted(glob.glob(os.path.join(ROOT, 'src', '*', 'mod', '*', '*.modinfo')))
EXPECTED = {'Russia 1918': (160, 104, 6), 'Arcanum 1885': (92, 112, 5), 'Canarias 1400': (160, 83, 7), 'Hawaii 1778': (148, 114, 5), 'Spain 1936': (120, 110, 6), 'China 1928': (100, 112, 6)}


def mod_dir_of(modinfo): return os.path.dirname(modinfo)
def map_of(modinfo): return glob.glob(os.path.join(mod_dir_of(modinfo), '*.Civ5Map'))[0]
def lines(path): return [l.strip() for l in open(path) if l.strip()]


class BuiltMods(unittest.TestCase):
    def test_four_mods_present(self):
        self.assertEqual(sorted(os.path.basename(mod_dir_of(m)).split(' (')[0] for m in MODS), sorted(EXPECTED))

    def test_map_header(self):
        for modinfo in MODS:
            m = read_map(map_of(modinfo))
            with self.subTest(map=m['name']):
                self.assertEqual((m['width'], m['height'], m['players']), EXPECTED[m['name']])
                self.assertEqual(m['scenario_players'], m['players'])
                self.assertEqual(len(m['plots']), m['width'] * m['height'] * 8)
                self.assertTrue(m['city_count'] > 0 or m['unit_count'] > 0, 'neither cities nor starting units')
                self.assertIn('VICTORY_DOMINATION', m['victories'])
                self.assertTrue(m['techs'] and m['buildings'] and m['units'] and m['promotions'])
                for lst in ('terrains', 'features', 'resources', 'techs', 'policies', 'buildings', 'promotions', 'units'):
                    self.assertEqual(len(m[lst]), len(set(m[lst])), f'duplicate names in {lst}')

    def test_city_spacing(self):
        from city_spacing import cities, hexdist, HARD_MIN, EXCEPTIONS
        for modinfo in MODS:
            name, cs = cities(map_of(modinfo))
            close = [(a[1], c[1]) for i, a in enumerate(cs) for c in cs[i + 1:]
                     if hexdist(a[0], c[0]) < HARD_MIN and (name, frozenset((a[1], c[1]))) not in EXCEPTIONS]
            with self.subTest(map=name): self.assertEqual(close, [], f'cities closer than {HARD_MIN} hexes')

    def test_modinfo_md5s(self):
        for modinfo in MODS:
            text = open(modinfo).read(); d = mod_dir_of(modinfo)
            entries = re.findall(r'<File md5="([0-9A-F]{32})" import="[01]">([^<]+)</File>', text)
            with self.subTest(mod=os.path.basename(d)):
                self.assertIn(os.path.basename(map_of(modinfo)), [n for _, n in entries])
                for md5, name in entries:
                    p = os.path.join(d, name)
                    self.assertTrue(os.path.exists(p), name)
                    self.assertEqual(hashlib.md5(open(p, 'rb').read()).hexdigest().upper(), md5, name)
                for name in os.listdir(d):
                    if name.endswith('.modinfo') or name == 'CREDITS.txt': continue   # credits ride along unlisted in some mods
                    self.assertIn(name, [n for _, n in entries], f'{name} not listed in modinfo')


class PolicyScreens(unittest.TestCase):
    """A scenario's SocialPolicyPopup must dispatch on the branch types its Policies.sql creates, in the order of its branch boxes
    (the screen walks branch IDs from 0 and the SQL renumbers the scenario branches first)."""
    def test_branches_match_sql(self):
        for lua in sorted(glob.glob(os.path.join(ROOT, 'src', '*', 'ui', 'SocialPolicyPopup.lua'))):
            ui = os.path.dirname(lua); sqls = glob.glob(os.path.join(ui, '*_Policies.sql'))
            if not sqls: continue   # Arcanum's branches come from XML
            with self.subTest(mod=os.path.basename(os.path.dirname(ui))):
                sql = open(sqls[0], encoding='utf-8').read()
                created = re.findall(r"INSERT INTO PolicyBranchTypes \(Type[^)]*\) VALUES \('(POLICY_BRANCH_\w+)'", sql)
                used = re.findall(r'branchType == "(POLICY_BRANCH_\w+)"', open(lua, encoding='utf-8').read())
                self.assertTrue(created and used)
                self.assertEqual(used[:len(created)], created)
                self.assertIn('PurchaseByLevel < b1.PurchaseByLevel', sql)
                xml = open(os.path.join(ui, 'SocialPolicyPopup.xml'), encoding='utf-8').read()
                self.assertEqual(len(re.findall(r'ID="BranchButton\d"', xml)), len(created))
                self.assertNotIn('SocialPoliciesAesthetics.dds', xml)   # no such texture in the game (the Aesthetics box uses PolicyBranch_Aesthetics.dds)
import shutil, subprocess


@unittest.skipUnless(shutil.which('luac'), 'luac not installed (brew install lua)')
class LuaSyntax(unittest.TestCase):
    def test_lua_files_parse(self):
        for path in sorted(glob.glob(os.path.join(ROOT, 'src', '*', 'ui', '*.lua')) + glob.glob(os.path.join(ROOT, 'src', '*', 'mod', '*', '*.lua'))):
            with self.subTest(file=os.path.relpath(path, ROOT)):
                r = subprocess.run(['luac', '-p', path], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr.strip())


@unittest.skipUnless(os.path.isdir(XML), 'run tools/extract_game_xml.py first')
class GameXmlExtracts(unittest.TestCase):
    def test_tech_lists(self):
        techs = lines(os.path.join(XML, 'TECH_.txt'))
        self.assertEqual(techs, sorted(techs, key=lambda s: s.replace('_', ' ').lower()))
        for modinfo in MODS:
            m = read_map(map_of(modinfo))
            with self.subTest(map=m['name']):
                self.assertTrue(set(m['techs']) <= set(techs), set(m['techs']) - set(techs))

    def test_world_wonders_disabled(self):
        wonders = lines(os.path.join(XML, 'WORLD_WONDERS.txt'))
        self.assertEqual(len(wonders), 48)
        for modinfo in MODS:
            rules = glob.glob(os.path.join(mod_dir_of(modinfo), '*_Rules.xml'))
            if not rules: continue
            off = re.findall(r'<Update><Where Type="(BUILDING_[A-Z_]+)" /><Set PrereqTech="TECH_FUTURE_TECH"', open(rules[0]).read())
            if not off: continue   # this mod keeps the wonders
            with self.subTest(mod=os.path.basename(modinfo)): self.assertEqual(off, wonders)


if __name__ == '__main__':
    unittest.main()
