# Publishing Arcanum 1885

Everything a release needs, in order. The texts at the bottom are ready to paste. The route is the Canarias one
(`src/canarias-1400/publish/PUBLISH.md`); this mod has no art of its own and carries Firaxis files, see section 5.

## 1. Build and check

```
python3 src/arcanum-1885/gen_arcanum1885.py         # only if the map changed (parses art/arcanum_map_source.png; needs SciPy)
python3 src/arcanum-1885/text/build_text.py         # only if the text or rules changed
python3 src/arcanum-1885/ui/build_policy_screen.py  # only with the game installed (reads its Brave New World UI files)
python3 src/arcanum-1885/build_mod.py               # assembles mod/, patches the three Firaxis files, writes the modinfo, installs into MODS (--no-install: build only)
python3 -m unittest discover tests
python3 tools/pack_civ5mod.py src/arcanum-1885      # checks every MD5, writes dist/Arcanum 1885 (v 2).civ5mod (24 files, 0.6 MB unpacked)
python3 src/arcanum-1885/publish/make_screens.py    # the three 1920x1080 page images in publish/screens/ (map, nations, rules)
```

`build_mod.py` also copies the mod into the game's `MODS` folder (`CIV5_MODS` overrides the path); remove that copy before testing
the Workshop download, or the game sees two mods with the same id.

## 2. Versioning

- The mod id `a7c1e5b2-1885-4d3f-9e8a-2b6c4d0f7a31` never changes.
- Each release bumps `version="N"` in the modinfo (the `MODINFO` template in `build_mod.py`), the `OUT` folder name
  `Arcanum 1885 (v N)` in `build_mod.py` and `OUT_DIR` in `gen_arcanum1885.py`.
- Tag the release commit: `git tag arcanum-1885-v1`.
- **Game speed.** The build ships on Quick speed (`SPEED` in `gen_arcanum1885.py`, the load screen, the modinfo description and the
  page text all say so). If a later release moves to Epic, the intended pace, change all four together.

## 3. Steam Workshop (the main channel)

Uploads go only through ModBuddy, part of the free *Sid Meier's Civilization V SDK* (Steam, Library, Tools), Windows only;
a Parallels VM on the Mac works. ModBuddy is needed only as the uploader: the Workshop item is the `.civ5mod` package itself.

1. Copy `dist/Arcanum 1885 (v 2).civ5mod`, `publish/cover.jpg` and `publish/screens/` to the Windows side.
2. ModBuddy, Tools, *Publish to Steam Workshop*, *Upload new mod*, pick the `.civ5mod`.
3. Title `Arcanum 1885`, preview image `cover.jpg`, the description below, tags *Scenario*, *Map*, *Civilizations*, visibility *Public*.
4. On the new item's page, *Add/edit images & videos*, upload the three cards from `publish/screens/` (the map first), then
   two or three real in-game screenshots: the load screen, a leader scene, the policy screen with the five branches, an airship.
5. Later versions: the same wizard, *Update mod*, with the new package; Steam keeps the item id.

## 4. Outside Steam

- Install instructions for players of the `.civ5mod`: drop it into the `MODS` folder; the game unpacks it when the Mods menu opens.
- **CivFanatics** (forums.civfanatics.com/resources, category *Civ5 - Modpacks*, scenario tag): same file, the cover, the three
  cards, in-game screenshots, the description. Post a thread in the Civ5 Creation & Customization forum linking the resource.

## 5. Rights to state, and to decide on

This mod is the one in the repository that leans on other people's work, so read this before uploading.

- **Firaxis files.** The package carries six rule and text files of *Empires of the Smoky Skies* (Gods & Kings), three of them
  patched, plus the scenario's five leader-scene XMLs. Copying and modifying the game's own XML and SQL is how every Civ5 mod
  works and the Workshop is full of it; the leader art, units and buildings themselves are not in the package, they come from
  the player's installed DLC. State it in the description, as below.
- **The fan map.** The hex map is parsed from kriss80858's "Tarantian Geographical Society" world map of Arcanum (DeviantArt).
  The image itself is not in the package, only the derived hex map, but the map is recognisably that map. Ask the author before
  publishing, or at least credit them by name and link in the description (done below) and take the mod down if they object.
- **The Arcanum name and lore.** *Arcanum: Of Steamworks and Magick Obscura* belongs to its rights holders (Activision after
  Troika). Fan scenarios with lore names are common on the Workshop and are normally left alone, but it is their call, not
  yours; the description says the mod is an unofficial, non-commercial fan work and does not use the game's logo or art.
- Scripts and data files in this repository: MIT (`LICENSE`). No generated art in this mod.

## Description (Steam Workshop and CivFanatics; Steam renders the BBCode)

```
[h1]Arcanum 1885[/h1]
Steam against magick. The units, buildings, technologies and policies of Firaxis' steampunk scenario [i]Empires of the Smoky
Skies[/i] on the continent of Arcanum, from [i]Arcanum: Of Steamworks and Magick Obscura[/i]. A long game rather than a war
scenario: five nations, ten free cities, twelve natural wonders at their lore sites, no turn limit.

[b]The nations[/b]
Tarant and its Industrial Council, the Kingdom of Caladon, King Praetor's Cumbria, the Wheel Clan of the dwarves under Loghaire
Thunder Stone, and the Technocracy of Vendigroth, which in this history never fell. Each is one of the five Smoky Skies
civilizations with its leader scene and traits, starting in 1885 with a Settler, a guard and a Worker at its lore capital,
Industrial technologies known. Ten free cities as city-states: Qintarra, Ashbury, Black Root, Stillwater, Shrouded Hills,
Roseborough, Tulla, the Isle of Despair, Bedokaan and T'sen-Ang.

[b]The map[/b]
92 x 112 hexes of Arcanum: the Glimmering Forest, the Stonewall and Grey Mountains, the Morbihan Plains, the Bangellian Swamp,
the Vendigroth wastes, Cattan and Thanatos. Resources are randomised by the game at every start, then topped up:
strategic deposits doubled and added, iron, coal and horses near every start, more luxuries. Natural wonders renamed after
the lore: Bellerogrim's Lair, the Ancient Temple of Derian-Ka, the Elven Burial Site, the Ruins of Kree, the Rock of Despair,
the Ring of Brodgar, Falcon's Ache, the Bangellian Deeps, the Lethe Wyvern's Lair, Stonewall Peak, the Mines of the Wheel
Clan and Torg's Altar.

[b]The rules[/b]
The Smoky Skies tech tree (23 steampunk technologies, 6 air and land units) and its five-branch policy tree, with the three
Brave New World ideologies and their tenets kept. Quick speed, one turn = one year from 1885, Huge map, raging barbarians, no goody
huts, no religion. Victories: domination, cultural (tourism, with the Hotel, Airport, Visitor Centre and Stadium moved onto
steampunk techs) and diplomatic (World Congress, United Nations). No science victory, no time limit.

[b]Requirements[/b]
Civilization V with Gods & Kings and Brave New World (the scenario's art and units come from Gods & Kings). Windows and Mac.
Single player. Start the scenario from Mods -> Single Player -> Scenarios. Enable this mod alone.

[b]Known limits[/b]
No events, no multiplayer. The AI plays with the stock logic. The scenario's own token victory and turn counter are removed.

Unofficial, non-commercial fan work. Arcanum: Of Steamworks and Magick Obscura and its names belong to their rights holders;
Empires of the Smoky Skies belongs to Firaxis Games. The hex map is derived from the "Tarantian Geographical Society" map of
Arcanum by kriss80858 (DeviantArt).

[b]Changelog[/b]

v2 (2026-11-01): more resources: strategic deposits doubled and topped up, every start gets iron, coal and horses nearby, more luxuries; still random every game.
v1 (2026-10-18): first release. Five nations, ten free cities, twelve natural wonders, Smoky Skies rules on Brave New World.
```
