# Publishing Hawaii 1778

Everything a release needs, in order. The texts at the bottom are ready to paste. The route is the Canarias one
(`src/canarias-1400/publish/PUBLISH.md`); only the mod's own facts differ.

## 1. Build and check

```
python3 src/hawaii-1778/art/build_art.py            # the 47 DDS textures into art/out (not committed; ~25 s)
python3 src/hawaii-1778/text/build_text.py          # only if the text or rules changed
python3 src/hawaii-1778/gen_hawaii1778.py           # only if the map changed (needs data/, see the root README)
python3 -m unittest discover tests
python3 tools/pack_civ5mod.py src/hawaii-1778       # copies the textures into mod/, checks every MD5, writes dist/Hawaii 1778 (v 1).civ5mod
python3 src/hawaii-1778/publish/make_screens.py     # the seven 1920x1080 page images in publish/screens/ (map, one per chiefdom, uniques)
```

The pack script refuses to pack if a listed file is missing, an MD5 differs, an unlisted file lies in the mod folder, or the
modinfo still has a placeholder author. `build_art.py` rewrites the PNGs in `art/cut` and the previews with identical pixels but
new metadata; `git checkout -- src/hawaii-1778/art` before committing unless the art really changed.

## 2. Versioning

- The mod id `e7b3d1a5-1778-4c2e-9f40-8a6b2c5d7e91` never changes: Steam and the game's save files are keyed on it.
- Each release bumps `version="N"` in the modinfo (the `MODINFO` template in `gen_hawaii1778.py`) and the folder name
  `Hawaii 1778 (v N)`; the game ignores a new build under an old version number.
- Tag the release commit: `git tag hawaii-1778-v1`.

## 3. Steam Workshop (the main channel)

Uploads go only through ModBuddy, part of the free *Sid Meier's Civilization V SDK* (Steam, Library, Tools), Windows only;
a Parallels VM on the Mac works. ModBuddy is needed only as the uploader: the Workshop item is the `.civ5mod` package itself.

1. Copy `dist/Hawaii 1778 (v 1).civ5mod`, `publish/cover.jpg` and `publish/screens/` to the Windows side.
2. ModBuddy, Tools, *Publish to Steam Workshop*, *Upload new mod*, pick the `.civ5mod`.
3. Title `Hawaii 1778`, preview image `cover.jpg`, the description below, tags *Scenario*, *Map*, *Civilizations*,
   *Leaders*, visibility *Public*.
4. On the new item's page, *Add/edit images & videos*, upload the seven cards from `publish/screens/` in their numbered
   order (the map first).
5. Later versions: the same wizard, *Update mod*, with the new package; Steam keeps the item id.

If the wizard refuses the hand-built package, rebuild it as a ModBuddy project as described in the Canarias guide, with this
mod's id, files and the five `UpdateDatabase` actions in the modinfo's order.

## 4. Outside Steam

- Install instructions for players of the `.civ5mod`: drop it into the `MODS` folder; the game unpacks it when the Mods menu opens.
- **CivFanatics** (forums.civfanatics.com/resources, category *Civ5 - Modpacks*, scenario tag): same file, the cover, the
  seven cards, two or three in-game screenshots, the description. Post a thread in the Civ5 Creation & Customization forum
  linking the resource.

## 5. Licences to state

- Scripts and data files in this repository: MIT (`LICENSE`).
- Map relief: NOAA ETOPO 2022, public domain.
- Leader art and the unique icons: generated with FLUX.2-dev through Together AI. The Black Forest Labs dev-model licence is
  non-commercial; a free mod fits, but reread the current terms for generated outputs before the first upload and keep the
  credit line.
- Unit, building and UI art: Firaxis / 2K, as for every Civ5 mod; the mod ships no Firaxis files.

## Description (Steam Workshop and CivFanatics; Steam renders the BBCode)

```
[h1]Hawaii 1778[/h1]
The Hawaiian Islands on the eve of contact, the year Cook's ships anchored at Waimea. Five chiefdoms start from a Settler
and a Warrior in the Ancient era at their historical seats; three lesser islands are city-states. Canoes and crossings come
with Sailing and Optics. Unite the islands before the ships from outside do it for you.

[b]The chiefdoms[/b]
The Big Island is split as it was in 1782: Kamehameha's Kona and Kohala against his cousin Keoua's Hilo, Puna and Kau.
Kahekili's Maui, Kahahana's Oahu and Kamakahelei's Kauai hold the other islands; Molokai, Lanai and Niihau are
city-states. Each chiefdom has its own ability, unique unit and building, city list of ahupuaa and districts, leader
portrait, diplomacy scene and emblem.

[b]The map[/b]
148 x 114 hexes, 4 km per hex, built from the NOAA ETOPO 2022 relief model: trade-wind rainforest to windward, dry lava
coasts to leeward, snow on Mauna Kea. One natural wonder per island (Mauna Kea, Kilauea, Haleakala, Leahi, Waimea Canyon,
Kalaupapa, Keahiakawelo). No iron and no horses: the islands had neither, so the Olohe is the only swordsman you will see.

[b]The rules[/b]
Stock Brave New World rules, one turn = one year from 1778, development capped at the Classical era (plus Guilds for trading
posts), the Paradise Found policy tree in place of the nine stock branches, native cults in place of the world religions,
domination victory only.

[b]Requirements[/b]
Civilization V with Gods & Kings and Brave New World. Windows and Mac. Single player.
Start the scenario from Mods -> Single Player -> Scenarios. Enable this mod alone; it replaces civilizations, religions and
policies and will clash with other scenario mods (including Canarias 1400 from the same author).

[b]Known limits[/b]
No events, no multiplayer. The AI plays the islands with the stock logic.

Relief: NOAA ETOPO 2022 (public domain). Leader art: generated with FLUX.2-dev; the leaders are imagined, no real person is
depicted. Unit and building art: Firaxis.

[b]Changelog[/b]

v1 (2026-10-18): first release. Five chiefdoms, three city-states, generated leader art, Paradise Found policies, native cults, Classical cap.
```
