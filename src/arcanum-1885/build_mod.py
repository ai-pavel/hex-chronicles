#!/usr/bin/env python3
"""Assemble the Arcanum 1885 mod folder: Firaxis' Empires of the Smoky Skies rules and UI, the Arcanum map, load screen,
text and rules, plus the .modinfo. Then install it into the Civ5 MODS folder (not with --no-install)."""
import os, sys, shutil, hashlib, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'mod', 'Arcanum 1885 (v 2)'); SRC = os.path.join(HERE, 'steampunk_src'); UI = os.path.join(HERE, 'ui')
MODS = os.environ.get('CIV5_MODS') or os.path.expanduser("~/Library/Application Support/Sid Meier's Civilization 5/MODS")   # where the built mod is installed
os.makedirs(OUT, exist_ok=True)
# (file, import flag). Scenario rules and text are plain database updates; UI overrides and leader scenes must be imported into the VFS.
STEAMPUNK = [('ScenarioText.sql', 0), ('NewCivilizations.xml', 0), ('NewMajorCivCities.xml', 0), ('RemoveModernEras.xml', 0), ('TechTreeUpdate.xml', 0), ('PolicyUpdate.xml', 0),
             ('Alderdice_Scenario_Scene.xml', 1), ('Curnow_Scenario_Scene.xml', 1), ('Cutler_Scenario_Scene.xml', 1), ('Griggs_Scenario_Scene.xml', 1), ('Roffenburg_Scenario_Scene.xml', 1)]
# The scenario's own SocialPolicyPopup is the Gods & Kings one (no ideologies); ui/ holds a merged BNW version (see build_policy_screen.py).
ARC = [('Arcanum1885LoadScreen.lua', 0), ('Arcanum1885LoadScreen.xml', 0), ('Arcanum1885_Setup.lua', 0), ('Arcanum1885_Setup.xml', 0), ('Arcanum1885_PreTech.xml', 0),
       ('Arcanum1885_PrePolicy.xml', 0), ('Arcanum1885_PostPolicy.sql', 0), ('Arcanum1885_Rules.xml', 0), ('Arcanum1885_Text.xml', 0), ('SocialPolicyPopup.lua', 1), ('SocialPolicyPopup.xml', 1)]
import re
def drop(text, pattern, count):
    """Remove exactly `count` matches of a regex from a copied Firaxis file, so a Firaxis update that changes the file is noticed."""
    text, n = re.subn(pattern, '', text, flags=re.S)
    assert n == count, (pattern, n)
    return text
PATCHES = {
    # The scenario ran under Gods & Kings, where Freedom/Order/Autocracy were ordinary branches. Under Brave New World they are the
    # ideologies the engine demands in the Modern era, so they stay, together with the tenets the scenario deleted by their G&K names
    # (except the three names the scenario reuses for its own policies: Nationalism, Militarism, United Front).
    'PolicyUpdate.xml': [(r'\s*<Delete Type="POLICY_BRANCH_(?:FREEDOM|ORDER|AUTOCRACY)"/>', 3),
                         (r'\s*<Delete>\s*<Type>POLICY_(?:CIVIL_SOCIETY|POLICE_STATE|TOTAL_WAR|UNIVERSAL_SUFFRAGE)</Type>\s*</Delete>', 4)],
    # BNW's Culture Overview screen dies if these two national wonders are missing; they also give Great Work slots.
    'RemoveModernEras.xml': [(r'\s*<Delete Type="BUILDING(?:CLASS)?_(?:NATIONAL_EPIC|HEROIC_EPIC)"/>', 4)],
}
for fn, _ in STEAMPUNK:
    text = open(os.path.join(SRC, fn), encoding='utf-8', errors='surrogateescape').read()
    for pattern, count in PATCHES.get(fn, []): text = drop(text, pattern, count)
    open(os.path.join(OUT, fn), 'w', encoding='utf-8', errors='surrogateescape').write(text)
for fn, _ in ARC: shutil.copy(os.path.join(UI, fn), os.path.join(OUT, fn))
shutil.copy(os.path.join(HERE, 'art', 'CREDITS.txt'), os.path.join(OUT, 'CREDITS.txt'))
FILES = STEAMPUNK + ARC + [('Arcanum1885.Civ5Map', 1), ('CREDITS.txt', 0)]
def md5(fn): return hashlib.md5(open(os.path.join(OUT, fn), 'rb').read()).hexdigest().upper()
files_xml = '\n'.join(f'    <File md5="{md5(fn)}" import="{imp}">{fn}</File>' for fn, imp in FILES)
# Database order matters: Firaxis text and rules first, the tourism rescue between RemoveModernEras and TechTreeUpdate, the ideology fixes around PolicyUpdate, Arcanum rules and text last.
DB = ['ScenarioText.sql', 'NewCivilizations.xml', 'NewMajorCivCities.xml', 'RemoveModernEras.xml', 'Arcanum1885_PreTech.xml', 'TechTreeUpdate.xml', 'Arcanum1885_PrePolicy.xml', 'PolicyUpdate.xml', 'Arcanum1885_PostPolicy.sql', 'Arcanum1885_Rules.xml', 'Arcanum1885_Text.xml']
db_xml = '\n'.join(f'      <UpdateDatabase>{f}</UpdateDatabase>' for f in DB)
MODINFO = f'''<?xml version="1.0" encoding="utf-8"?>
<Mod id="a7c1e5b2-1885-4d3f-9e8a-2b6c4d0f7a31" version="2">
  <Properties>
    <Name>Arcanum 1885</Name>
    <Teaser>Empires of the Smoky Skies on the continent of Arcanum: Tarant, Caladon, Cumbria, the Wheel Clan and Vendigroth.</Teaser>
    <Description>The steampunk rules, units and tech tree of Firaxis' Empires of the Smoky Skies scenario on a 92x112 hex map of Arcanum (Arcanum: Of Steamworks and Magick Obscura). Five nations start in 1885 with a Settler and a guard at their lore capitals; ten free cities (Qintarra, Ashbury, Black Root, Stillwater, Shrouded Hills, Roseborough, Tulla, the Isle of Despair, Bedokaan, T'sen-Ang) are city-states; twelve natural wonders stand at lore sites. Raging barbarians, Quick speed, one turn per year, no religion, no turn limit. Win by domination, culture or diplomacy. Start it from Mods, Single Player, Scenarios.</Description>
    <Authors>cryptoboy2283</Authors>
    <SpecialThanks>Firaxis Games (Empires of the Smoky Skies), Troika Games (Arcanum), Civ5MapImage</SpecialThanks>
    <AffectsSavedGames>1</AffectsSavedGames>
    <MinCompatibleSaveVersion>0</MinCompatibleSaveVersion>
    <SupportsSinglePlayer>1</SupportsSinglePlayer>
    <SupportsMultiplayer>0</SupportsMultiplayer>
    <SupportsHotSeat>0</SupportsHotSeat>
    <SupportsMac>1</SupportsMac>
    <ReloadAudioSystem>0</ReloadAudioSystem>
    <ReloadLandmarkSystem>0</ReloadLandmarkSystem>
    <ReloadLeaderSystem>1</ReloadLeaderSystem>
    <ReloadStrategicViewSystem>0</ReloadStrategicViewSystem>
    <ReloadUnitSystem>0</ReloadUnitSystem>
  </Properties>
  <Dependencies>
    <Dlc id="0E3751A1-F840-4e1b-9706-519BF484E59D" minversion="0" maxversion="999" />
    <Dlc id="6DA07636-4123-4018-B643-6575B4EC336B" minversion="0" maxversion="999" />
  </Dependencies>
  <References />
  <Blocks />
  <Files>
{files_xml}
  </Files>
  <Actions>
    <OnModActivated>
{db_xml}
    </OnModActivated>
  </Actions>
  <EntryPoints>
    <EntryPoint type="Custom" file="Arcanum1885LoadScreen.xml">
      <Name>Arcanum 1885</Name>
      <Description>Steam against magick on the continent of Arcanum. Choose your nation and difficulty.</Description>
    </EntryPoint>
    <EntryPoint type="InGameUIAddin" file="Arcanum1885_Setup.xml">
      <Name>Arcanum 1885 setup</Name>
      <Description>On turn 1: more resources (strategic deposits doubled and topped up, iron, coal and horses near every start, more luxuries) and the five policy branches opened for every nation.</Description>
    </EntryPoint>
  </EntryPoints>
</Mod>
'''
open(os.path.join(OUT, 'Arcanum1885.modinfo'), 'w').write(MODINFO)
print('built', OUT)
if '--no-install' in sys.argv: sys.exit(0)
dest = os.path.join(MODS, os.path.basename(OUT))
if os.path.isdir(dest): shutil.rmtree(dest)
shutil.copytree(OUT, dest)
print('installed', dest); print(sorted(os.listdir(dest)))
