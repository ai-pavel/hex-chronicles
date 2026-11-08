# Publishing Spain 1936

Everything a release needs, in order. The texts at the bottom are ready to paste. The route is the Russia 1918 one
(`src/russia-1918/publish/PUBLISH.md`).

## 1. Build and check

```
python3 src/spain-1936/art/build_art.py            # the 27 DDS textures into art/out and the pieces into art/tmp (neither committed)
python3 src/spain-1936/text/build_text.py          # only if the text or events changed
python3 src/spain-1936/gen_spain1936.py            # only if the map changed: needs data/ and data/xml from an INSTALLED game (see below)
python3 -m unittest discover tests
python3 tools/pack_civ5mod.py src/spain-1936       # checks every MD5, writes dist/Spain 1936 (v 1).civ5mod (44 files, 11.2 MB unpacked)
python3 src/spain-1936/publish/make_screens.py     # cover.jpg (1024x1024) and the eight 1920x1080 page images in publish/screens/
```

The generator reads `TECH_ERAS.json` and `WORLD_WONDERS.txt` from `data/xml`; regenerate the map only with the game installed, and check that
`git status` shows no change in the map afterwards. For a text-only release, run `build_text.py`, copy `ui/` into `mod/` and refresh the MD5s in
the modinfo instead (the `filerow` lines in `gen_spain1936.py` show which files are listed), or simply rerun the generator.

## 2. Versioning

- The mod id in `gen_spain1936.py` never changes. Each release bumps `version="N"` in the modinfo template and the
  `OUT_DIR` folder name `Spain 1936 (v N)`.
- Tag the release commit: `git tag spain-1936-v1`.

## 3. Steam Workshop (the main channel)

Uploads go only through ModBuddy, part of the free *Sid Meier's Civilization V SDK* (Steam, Library, Tools), Windows only;
a Parallels VM on the Mac works. ModBuddy is needed only as the uploader: the Workshop item is the `.civ5mod` package itself.

1. Copy `dist/Spain 1936 (v 1).civ5mod`, `publish/cover.jpg` and `publish/screens/` to the Windows side.
2. ModBuddy, Tools, *Publish to Steam Workshop*, *Upload new mod*, pick the `.civ5mod`.
3. Title `Spain 1936`, preview image `cover.jpg`, the description below, tags *Scenario*, *Map*, *Civilizations*, *Leaders*,
   visibility *Public*.
4. On the new item's page, *Add/edit images & videos*, upload the eight cards from `publish/screens/` in their numbered
   order (the map first), then two or three real in-game screenshots: the load screen, an event popup, the Madrid front.
5. Later versions: the same wizard, *Update mod*, with the new package; Steam keeps the item id.

## 4. Outside Steam

- Install instructions for players of the `.civ5mod`: drop it into the `MODS` folder; the game unpacks it when the Mods menu opens.
- **CivFanatics** (forums.civfanatics.com/resources, category *Civ5 - Modpacks*, scenario tag): same file, the cover, the eight
  cards, in-game screenshots, the description. Post a thread in the Civ5 Creation & Customization forum linking the resource.

## 5. Rights to state

- Scripts and data files in this repository: MIT (`LICENSE`). Map data: Natural Earth and NOAA ETOPO 2022 (public domain),
  Koppen-Geiger climate classes (Kottek et al. 2006, free for use with attribution).
- Portraits and emblems: Wikimedia Commons. Public domain or CC0, except three files under CC BY-SA (the Aguirre portrait by Jesus Elosegui /
  GureGipuzkoa, CC BY-SA 3.0; the arms of the Second Republic by Heralder, CC BY-SA 3.0; the Ikurrina by Daniele Schirmo, CC BY-SA 2.5): the
  textures made from them are shared under the same licences, and the attribution is in `CREDITS.txt` inside the mod and in the description below.
  The portraits are of real historical figures; the dialogue lines are invented and the description says so.
- Unit, building and UI art: Firaxis / 2K, as for every Civ5 mod; the mod ships no Firaxis files.

## Description (Steam Workshop and CivFanatics; Steam renders the BBCode)

```
[h1]Spain 1936[/h1]
The Spanish Civil War from 25 July 1936, one week after the rising, one turn = one week. Six sides on a 120 x 110 map from Cape
Finisterre to Menorca and from the Landes to the Rif, with the fronts, railways and cities of that summer, six neighbours as
city-states, and forty-eight dated events that arrive on their historical weeks whoever is playing.

[b]The sides[/b]
The Spanish Republic (Azana), Catalonia (Companys), the Basque Country (Aguirre) and the CNT-FAI columns of Aragon (Durruti),
at permanent war with Franco's Nationalists of the South and the Army of Africa and with Mola's Army of the North. The two
Nationalist armies are locked in alliance; the four Republican sides are at peace with each other, but that peace is not locked:
the May Days of 1937 set Catalonia and the anarchists fighting for a week, and nothing stops a Republican civil war of your own.
Portugal, British Gibraltar, the Tangier International Zone, Andorra, France and French North Africa are city-states. Fugitives
in the sierras of the Nationalist zone are raging barbarians.

[b]Unique units and buildings[/b]
Every side builds its own: the Republic's Soviet T-26 tanks and War Commissariat, Franco's Spanish Legion and Recruiting Office,
Mola's Requetes and Carlist War Junta, Catalonia's Blindat armoured cars and War Industries Commission, the Basque Gudaris and the
Iron Ring of Bilbao, the anarchists' Confederal Militia and the Collective. The donor civilizations' own units and buildings are gone.

[b]The map[/b]
About 11 km per hex, built from Natural Earth and NOAA ETOPO relief with the Koppen climate: the control lines of late July 1936
drawn inside the provinces (the Cordoba front, the Alcazar of Toledo, Oviedo, Menorca, eastern Aragon), 158 cities with their
1930 census populations, the 1936 railway network line by line, and strategic resources balanced so that every side can fuel the
aircraft and tanks its events bring.

[b]The rules[/b]
Techs through the Industrial era plus Flight, Combustion, Replaceable Parts, Railroad, Refrigeration and Ballistics; research is
off, new weapons come only by event. Great War Infantry, militia Riflemen, Cavalry, Artillery, Machine Guns and Anti-aircraft
guns, Triplanes and bombers, the battleships Jaime I and Espana; German, Italian and Soviet aircraft and tanks arrive by event.
No world wonders, no religion, no happiness, no leagues. The top panel shows the real date and the week of the war. Domination
victory only, no turn limit.

[b]The events[/b]
The airlift and the Convoy of Victory, the relief of the Alcazar, Franco as Generalisimo, the Condor Legion, the Italian
Blackshirts, Guadalajara, the Decree of Unification, Teruel, the Aragon and Catalonia offensives; the requetes of Navarre, the
cruiser Canarias, the Biscay, Santander and Asturias campaigns, the death of Mola; non-intervention, the Largo Caballero and
Negrin governments, Soviet aid, the Popular Army, the defence of Madrid, the International Brigades, the Jarama, Brunete, the
Ebro, the farewell to the Brigades, the Casado coup; the War Industries Commission, Bayo's landing on Mallorca, the May Days, La
Retirada; the Basque government, Guernica, the Habana, Santona; the Council of Aragon, the anarchist ministers, Durruti in Madrid.
Event texts are neutral and factual. Guernica, the evacuation of the Basque children and La Retirada are told, not played.

[b]Requirements[/b]
Civilization V with Gods & Kings and Brave New World. Windows and Mac. Single player. English and Russian text.
Start the scenario from Mods -> Single Player -> Scenarios. Enable this mod alone.

[b]Known limits and simplifications[/b]
Franco and Mola are two players for the whole war (the commands merged on 1 October 1936). The Basque government
formed only in October 1936 but plays from the start. The CNT-FAI is a side, not a set of militias. The Canary Islands are left
out. Portugal, France and French North Africa hold several towns each. No multiplayer. The AI plays with the stock logic.

Portraits and emblems: Wikimedia Commons, public domain or CC0, except the Aguirre portrait (Jesus Elosegui / GureGipuzkoa,
CC BY-SA 3.0), the arms of the Second Republic (Heralder, CC BY-SA 3.0) and the Ikurrina (Daniele Schirmo, CC BY-SA 2.5). The
leaders are historical figures, their dialogue is invented. Map data: Natural Earth, NOAA ETOPO 2022, Koppen-Geiger. Unit and
building art: Firaxis.

[b]Changelog[/b]

v2 (2026-11-01): cities at least 3 hexes apart (4 within a side unless both are key towns), 158 cities instead of 162: Irun joins San Sebastian, La Coruna El Ferrol (the naval base), Pontevedra Vigo, Alcaniz Caspe, Algeciras Arcos (Gibraltar keeps its hex).
v1 (2026-10-31): first release. Six sides with their own unique units and buildings, six city-states, the 1936 railways, forty-eight dated events.
```
