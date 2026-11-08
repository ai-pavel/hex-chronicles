# Publishing Russia 1918

Everything a release needs, in order. The texts at the bottom are ready to paste. The route is the Canarias one
(`src/canarias-1400/publish/PUBLISH.md`).

## 1. Build and check

```
python3 src/russia-1918/art/build_art.py            # the 27 DDS textures into art/out and the pieces into art/tmp (neither committed)
python3 src/russia-1918/text/build_text.py          # only if the text or events changed
python3 src/russia-1918/gen_russia1918.py           # only if the map changed: needs data/ and data/xml from an INSTALLED game (see below)
python3 -m unittest discover tests
python3 tools/pack_civ5mod.py src/russia-1918       # checks every MD5, writes dist/Russia 1918 (v 3).civ5mod (45 files, 11.4 MB unpacked)
python3 src/russia-1918/publish/make_screens.py     # the eight 1920x1080 page images in publish/screens/ (map, six sides, events); needs HEX_XML
```

The generator reads `TECHS_THROUGH_INDUSTRIAL.txt` in tech-tree order; the cache fallback of `tools/extract_game_xml.py` (used
when no game is installed) writes that list in database order, so regenerate the map only with the game installed, and check
that `git status` shows no change in the map afterwards. For a text-only release, run `build_text.py`, copy `ui/` into `mod/`
and refresh the MD5s in the modinfo instead (the `filerow` lines in `gen_russia1918.py` show which files are listed).

## 2. Versioning

- The mod id in `gen_russia1918.py` never changes. Each release bumps `version="N"` in the modinfo template and the
  `OUT_DIR` folder name `Russia 1918 (v N)`.
- Tag the release commit: `git tag russia-1918-vN` (`russia-1918-v1`, `russia-1918-v2`, ...).

## 3. Steam Workshop (the main channel)

Uploads go only through ModBuddy, part of the free *Sid Meier's Civilization V SDK* (Steam, Library, Tools), Windows only;
a Parallels VM on the Mac works. ModBuddy is needed only as the uploader: the Workshop item is the `.civ5mod` package itself.

1. Copy `dist/Russia 1918 (v 3).civ5mod`, `publish/cover.jpg` and `publish/screens/` to the Windows side.
2. ModBuddy, Tools, *Publish to Steam Workshop*, *Upload new mod*, pick the `.civ5mod`.
3. Title `Russia 1918`, preview image `cover.jpg`, the description below, tags *Scenario*, *Map*, *Civilizations*, *Leaders*,
   visibility *Public*.
4. On the new item's page, *Add/edit images & videos*, upload the eight cards from `publish/screens/` in their numbered
   order (the map first), then two or three real in-game screenshots: the load screen, an event popup, the Volga front.
5. Later versions: the same wizard, *Update mod*, with the new package; Steam keeps the item id.

## 4. Outside Steam

- Install instructions for players of the `.civ5mod`: drop it into the `MODS` folder; the game unpacks it when the Mods menu opens.
- **CivFanatics** (forums.civfanatics.com/resources, category *Civ5 - Modpacks*, scenario tag): same file, the cover, the eight
  cards, in-game screenshots, the description. Post a thread in the Civ5 Creation & Customization forum linking the resource.

## 5. Rights to state

- Scripts and data files in this repository: MIT (`LICENSE`). Map data: Natural Earth and NOAA ETOPO 2022 (public domain),
  Koppen-Geiger climate classes (Kottek et al. 2006, free for use with attribution).
- Portraits and emblems: Wikimedia Commons, all public domain (photographs of 1910-1920 by authors dead more than 70 years or
  unknown, official state symbols); the file names, authors and licences are in `CREDITS.txt` inside the mod. The portraits are
  of real historical figures; the dialogue lines are invented and the description says so.
- Unit, building and UI art: Firaxis / 2K, as for every Civ5 mod; the mod ships no Firaxis files.

## Description (Steam Workshop and CivFanatics; Steam renders the BBCode)

```
[h1]Russia 1918[/h1]
The Russian Civil War from 1 June 1918, one turn = one week. Six sides on a 160 x 104 map from East Prussia and Finland to
Irkutsk and from Murmansk to Transcaspia, with the fronts, railways and cities of that summer, thirteen border states as
city-states, and thirty-six dated events that arrive on their historical weeks whoever is playing.

[b]The sides[/b]
The Russian SFSR (Lenin), at permanent war with the three White governments: the White South (Denikin), Siberia (Kolchak)
and the Allied Northern Region (Yudenich). The Ukrainian State (Skoropadsky) and Poland (Pilsudski) start neutral and decide
for themselves; the events bring the Soviet-Ukrainian war in December 1918 and the Polish-Soviet war in February 1919.
Finland, Estonia, Latvia, Lithuania at Vilna, East Prussia, Romania, Georgia, Azerbaijan, Armenia, the Ottomans at Kars, Persia at
Tabriz, Bukhara and Khiva are city-states. Makhno, the Basmachi, the Dagestani murids and later Grigoriev and Antonov are
raging barbarians, and the empty steppe and taiga breed partisans.

[b]Unique units and buildings[/b]
Every side builds its own: the Reds' Tachanka and Military Commissariat, the White South's Coloured Regiments and Cossack
Stanitsa, Siberia's Armoured Train and Railway Workshops, the Northern Region's Mark V tanks and Allied Supply Base, the
Ukrainian Serdiuk Division and Sugar Refinery, the Polish Uhlans and Officer School. The donor civilizations' own units and
buildings are gone. Poland's ability is the Miracle on the Vistula: Great Generals come 50% faster and lead 15% better.

[b]The map[/b]
About 47 km per hex, built from Natural Earth and NOAA ETOPO relief with the Koppen climate: the 1918 fronts drawn from the
June positions, about 120 cities with their 1917 populations, the railway network line by line, strategic resources balanced
so that every side can keep its cavalry and gunboats supplied.

[b]The rules[/b]
Techs through the Industrial era plus Flight, Combustion, Replaceable Parts, Railroad and Refrigeration; research is off, new
weapons come only by event. Great War Infantry, Riflemen, Cavalry, Artillery, Gatling guns, a few Triplanes and bombers, the
Baltic Fleet, Caspian and White Sea gunboats; British tanks arrive by event. No world wonders, no religion, no happiness, no
leagues. The top panel shows the real date and the week of the war. Domination victory only, no turn limit.

[b]The events[/b]
Compulsory service and the Latvian Riflemen, Trotsky at Sviyazhsk, the First Cavalry Army; the Second Kuban campaign, British
tanks at Novorossiysk, the Moscow Directive, Mamontov's raid, Wrangel; Komuch, Kolchak's coup, supplies via Vladivostok, the
spring offensive; the Allied landing at Arkhangelsk, the Polar Bears, the Northern Corps, the evacuation, Yudenich's march on
Petrograd; the German withdrawal, the Directory, the Act of Unity, the Warsaw agreement; Polish independence, Haller's Blue
Army, the Kiev offensive, the volunteers of 1920; Grigoriev's mutiny and the Tambov rising.

[b]Requirements[/b]
Civilization V with Gods & Kings and Brave New World. Windows and Mac. Single player. English and Russian text.
Start the scenario from Mods -> Single Player -> Scenarios. Enable this mod alone.

[b]Known limits and simplifications[/b]
First playable build. Arkhangelsk is Allied from turn 1 (historically 2 August); Minsk and eastern Belarus are Red though German
troops held them until December; Komuch and the Siberian Government are one faction from the start; Bessarabia is Romania's
territory; East Prussia is a German city-state. No multiplayer. The AI plays with the stock logic.

Portraits and emblems: Wikimedia Commons, public domain; the leaders are historical figures, their dialogue is invented. Map
data: Natural Earth, NOAA ETOPO 2022, Koppen-Geiger. Unit and building art: Firaxis.

[b]Changelog[/b]

v3 (2026-11-01): cities at least 3 hexes apart (4 within a side unless both are key towns); 119 cities instead of 121:
Rostov-on-Don joins Novocherkassk, Novorossiysk Ekaterinodar (the British tanks of 1919 now arrive there), Kovno Vilna;
Brest-Litovsk and Grodno stand as Polish cities again (Bialystok joins Grodno), Taganrog stays in Novocherkassk, Mogilev in Smolensk.
Vilna, where the Taryba declared independence, is Lithuania's capital instead of Kovno and no longer Polish. Saved games
of v2 do not carry over.
v2 (2026-10-31): a unique unit and building for every side instead of the donor civilizations' Cossacks, Panzers, Hussars,
Ships of the Line and the rest; Poland's Solidarity, which never fired, is now the Miracle on the Vistula (Great Generals);
Siberia's and the Northern Region's dead ability effects replaced (forest movement, city-state influence). Same map; saved
games of v1 do not carry over.
v1 (2026-10-18): first release. Six sides, thirteen city-states, the 1918 railways, thirty-six dated events.
```
