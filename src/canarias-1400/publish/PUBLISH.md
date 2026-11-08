# Publishing Canarias 1400

Everything a release needs, in order. The texts at the bottom are ready to paste.

## 1. Build and check

```
python3 src/canarias-1400/art/build_art.py          # the 47 DDS textures into art/out (not committed; ~25 s)
python3 src/canarias-1400/text/build_text.py        # only if the text or rules changed
python3 src/canarias-1400/gen_canarias1400.py       # only if the map changed (needs data/, see the root README)
python3 -m unittest discover tests
python3 tools/pack_civ5mod.py src/canarias-1400     # copies the textures into mod/, checks every MD5, writes dist/Canarias 1400 (v 1).civ5mod
python3 src/canarias-1400/publish/make_screens.py   # the nine 1920x1080 page images in publish/screens/ (map, one per people, uniques)
```

The pack script refuses to pack if a listed file is missing, an MD5 differs, an unlisted file lies in the mod folder, or the
modinfo still has a placeholder author. `build_art.py` rewrites the PNGs in `art/cut` and the previews with identical pixels but
new metadata; `git checkout -- src/canarias-1400/art` before committing unless the art really changed.

## 2. Versioning

- The mod id `c4a2e9d1-1400-4b7f-8e63-5d1a9f0c2b77` never changes: Steam and the game's save files are keyed on it.
- Each release bumps `version="N"` in the modinfo (the `MODINFO` template in `gen_canarias1400.py`) and the folder name
  `Canarias 1400 (v N)`; the game ignores a new build under an old version number.
- Tag the release commit: `git tag canarias-1400-v1`.

## 3. Steam Workshop (the main channel)

Uploads go only through ModBuddy, part of the free *Sid Meier's Civilization V SDK* (Steam, Library, Tools). It is Windows
only, so this needs Windows (a Parallels VM on the Mac works) with Steam logged in to the account that publishes, which must
own the game. ModBuddy is needed only as the uploader: the Workshop item is the `.civ5mod` package itself, and the
publish wizard takes a ready package, so the project does not have to be rebuilt in ModBuddy.

1. Copy `dist/Canarias 1400 (v 1).civ5mod`, `publish/cover.jpg` and `publish/screens/` to the Windows side.
2. ModBuddy, Tools, *Publish to Steam Workshop* (the Workshop window), *Upload new mod*, pick the `.civ5mod`.
3. Title `Canarias 1400`, preview image `cover.jpg`, the description below, tags *Scenario*, *Map*, *Civilizations*,
   *Leaders*, visibility *Public*.
4. The wizard takes the one preview image only. Open the new item's page in the Steam client or a browser, *Add/edit images
   & videos* in the owner box on the right, and upload the nine cards from `publish/screens/` in their numbered order (the
   map first).
5. Later versions: the same wizard, *Update mod*, with the new package; Steam keeps the item id. Paste the changelog into the
   change notes.

If the wizard refuses the hand-built package, fall back to a ModBuddy project: New Project, *Empty Mod*, set the project's
`<Guid>` in the `.civ5proj` to the mod id above, *Add Existing Item* for every file in `mod/Canarias 1400 (v 1)/` except the
`.modinfo` (files the modinfo lists with `import="1"` get *Import into VFS* = True), copy Name, Teaser, Description, Authors,
Special Thanks and the flags from the modinfo into Project Properties, add the Gods & Kings and Brave New World
dependencies under *Associations*, the five `UpdateDatabase` actions in the modinfo's order under *Actions* and the
*Custom* entry point `Canarias1400LoadScreen.xml` under *Content*; Build, Deploy, compare the generated modinfo with ours,
then Publish.

## 4. Outside Steam

- Install instructions for players of the `.civ5mod`: drop it into the `MODS` folder; the game unpacks it when the Mods menu opens.
- **CivFanatics** (forums.civfanatics.com/resources, category *Civ5 - Modpacks*, scenario tag): same file, the cover, the
  nine cards from `publish/screens/`, two or three in-game screenshots (the load screen, a diplomacy scene, the policy
  screen), the description.
  Post a thread in the Civ5 Creation & Customization forum linking the resource; that is where feedback comes from.

## 5. Licences to state

- Scripts and data files in this repository: MIT (`LICENSE`).
- Map relief: NOAA ETOPO 2022, public domain.
- Leader art: generated with FLUX.2-dev through Together AI. The Black Forest Labs dev-model licence is non-commercial; a
  free mod fits, but reread the current terms for generated outputs before the first upload and keep the credit line.
- Unit, building and UI art: Firaxis / 2K, as for every Civ5 mod; the mod ships no Firaxis files.

## Description (Steam Workshop and CivFanatics; Steam renders the BBCode)

```
[h1]Canarias 1400[/h1]
The Canary Islands on the eve of the Castilian conquest. Seven islands, seven native peoples, every one starting from a
Settler and a Warrior in the Ancient era at its historical seat of power. Pick an island, raise its menceyato and take the
archipelago before the ships from Europe arrive.

[b]The peoples[/b]
Guanches of Tenerife (Bencomo), Canarii of Gran Canaria (Tenesor Semidan), Benahoaritas of La Palma (Tanausu), Gomeros of
La Gomera (Hautacuperche), Bimbaches of El Hierro (Armiche), Majos of Erbania / Fuerteventura (Guize) and Majos of
Titerogaka / Lanzarote (Guadarfia). Each has its own ability, unique unit and building, city list, leader portrait,
diplomacy scene and emblem.

[b]The map[/b]
160 x 83 hexes, 3 km per hex, built from the NOAA ETOPO 2022 relief model: the real coastlines, the volcanoes, the barrancos.
One natural wonder per island at its real site (Teide, Roque Nublo, Caldera de Taburiente, Garajonay, Garoe, Tindaya,
La Corona), strategic resources balanced per island, no horses. Shallow sills link the islands, so contact starts with Optics.

[b]The rules[/b]
Stock Brave New World rules, one turn = one year from 1400, development capped at the Classical era, the Paradise Found
policy tree in place of the nine stock branches, native cults in place of the world religions, domination victory only.

[b]Requirements[/b]
Civilization V with Gods & Kings and Brave New World. Windows and Mac. Single player.
Start the scenario from Mods -> Single Player -> Scenarios. Enable this mod alone; it replaces civilizations, religions and
policies and will clash with other scenario mods.

[b]Known limits[/b]
No events, no multiplayer. The AI plays the islands with the stock logic.

Relief: NOAA ETOPO 2022 (public domain). Leader art: generated with FLUX.2-dev; the leaders are imagined, no real person is
depicted. Unit and building art: Firaxis.

[b]Changelog[/b]

v1 (2026-10-18): first release. Seven peoples, generated leader art, Paradise Found policies, native cults, Classical cap.
```