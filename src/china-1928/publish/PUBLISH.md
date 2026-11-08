# Publishing China 1928

Everything a release needs, in order. The texts at the bottom are ready to paste. The route is the Russia 1918 one
(`src/russia-1918/publish/PUBLISH.md`).

## 1. Build and check

```
python3 src/china-1928/art/build_art.py            # the 27 DDS textures into art/out and the pieces into art/tmp (neither committed)
python3 src/china-1928/text/build_text.py          # only if the text or events changed
python3 src/china-1928/gen_china1928.py            # only if the map changed: needs data/ and data/xml from an INSTALLED game (see below)
python3 -m unittest discover tests
python3 tools/pack_civ5mod.py src/china-1928       # checks every MD5, writes dist/China 1928 (v 1).civ5mod (45 files, 11.4 MB unpacked)
python3 src/china-1928/publish/make_screens.py     # cover.jpg (1024x1024) and the eight 1920x1080 page images in publish/screens/
```

The generator reads `TECH_ERAS.json` and `WORLD_WONDERS.txt` from `data/xml`; regenerate the map only with the game installed, and check that
`git status` shows no change in the map afterwards. For a text-only release, run `build_text.py` and rerun the generator: it also writes the
map spots into the copied `China1928_Events.lua`, so copying `ui/` into `mod/` by hand would leave the spawn spots empty.

## 2. Versioning

- The mod id in `gen_china1928.py` never changes. Each release bumps `version="N"` in the modinfo template and the
  `OUT_DIR` folder name `China 1928 (v N)`.
- Tag the release commit: `git tag china-1928-v1`.

## 3. Steam Workshop (the main channel)

Uploads go only through ModBuddy, part of the free *Sid Meier's Civilization V SDK* (Steam, Library, Tools), Windows only;
a Parallels VM on the Mac works. ModBuddy is needed only as the uploader: the Workshop item is the `.civ5mod` package itself.

1. Copy `dist/China 1928 (v 1).civ5mod`, `publish/cover.jpg` and `publish/screens/` to the Windows side.
2. ModBuddy, Tools, *Publish to Steam Workshop*, *Upload new mod*, pick the `.civ5mod`.
3. Title `China 1928`, preview image `cover.jpg`, the description below, tags *Scenario*, *Map*, *Civilizations*, *Leaders*,
   visibility *Public*.
4. On the new item's page, *Add/edit images & videos*, upload the eight cards from `publish/screens/` in their numbered
   order (the map first), then two or three real in-game screenshots: the load screen, an event popup, the Long March.
5. Later versions: the same wizard, *Update mod*, with the new package; Steam keeps the item id.

## 4. Outside Steam

- Install instructions for players of the `.civ5mod`: drop it into the `MODS` folder; the game unpacks it when the Mods menu opens.
- **CivFanatics** (forums.civfanatics.com/resources, category *Civ5 - Modpacks*, scenario tag): same file, the cover, the eight
  cards, in-game screenshots, the description. Post a thread in the Civ5 Creation & Customization forum linking the resource.

## 5. Rights to state

- Scripts and data files in this repository: MIT (`LICENSE`). Map data: Natural Earth and NOAA ETOPO 2022 (public domain),
  Koppen-Geiger climate classes (Kottek et al. 2006, free for use with attribution).
- Portraits and emblems: Wikimedia Commons, all public domain (PD-China for the photographs; PD-self, PD-user, PD-ROC-exempt and similar for the
  emblems); `CREDITS.txt` inside the mod lists every file. The portraits are of real historical figures; the dialogue lines are invented and the
  description says so.
- Unit, building and UI art: Firaxis / 2K, as for every Civ5 mod; the mod ships no Firaxis files.

## Description (Steam Workshop and CivFanatics; Steam renders the BBCode)

```
[h1]China 1928[/h1]
China in the warlord era from 10 October 1928, the day Chiang Kai-shek became Chairman of the National Government, one turn = one
week. Six sides on a 100 x 112 map from Yunnan to the Ussuri and from the Amur to Tonkin, with the provinces, railways and cities of
that autumn, thirteen neighbours and provincial powers as city-states, and seventy-eight dated events that arrive on their
historical weeks whoever is playing, from the Northeast Flag Replacement to the Marco Polo Bridge.

[b]The sides[/b]
Chiang Kai-shek's National Government at Nanjing, Feng Yuxiang's Guominjun in Henan and the northwest, Yan Xishan's Shanxi with
Beiping and Tianjin, Zhang Xueliang's Fengtian clique in Manchuria, the Guangxi clique of Li Zongren with Wuhan, and the
Communists of Mao Zedong and Zhu De in the Jinggang mountains. The five armies of the Northern Expedition start at peace with open
borders and nothing is locked: the Chiang-Guangxi war and the Central Plains War come by event, and any side may start its own.
All five are at war with the Communists until the Xi'an incident. A side that loses its last city fights on while it has units,
so the Red Army can lose its bases and march. Japan (Kwantung, Korea, Taiwan), the Soviet Far East, Mongolia, Sichuan, Chongqing,
Yunnan, Guizhou, Guangdong, the Ma clique's Qinghai, Hong Kong, Macau, Weihaiwei and French Indochina are city-states; Japan and the
Soviet Union go to war through the events. Bandits, the Red Spears and the honghuzi are raging barbarians.

[b]Unique units and buildings[/b]
Every side builds its own: Nanjing's Central Army Divisions and Central Military Academy, the Guominjun's Big Sword Brigades and
Military Farm Colonies, Shanxi's Taiyuan Mountain Guns and Northwest Industrial Company, Fengtian's Breguet 19 bombers and the
Mukden Arsenal, Guangxi's hill divisions and Militia Training Offices, the Red Army Columns and the Land Revolution Committees.
The donor civilizations' own units and buildings are gone.

[b]The map[/b]
About 36 km per hex, built from Natural Earth and NOAA ETOPO relief with the Koppen climate and the natural lakes of the Yangtze:
the holders of October 1928 province by province (Rehe and the Mongol leagues with Fengtian, western Shandong with the Guominjun,
Hubei with Guangxi, the Kwantung Leased Territory, Weihaiwei, Guangzhouwan), 207 cities at least three hexes apart (Hong Kong and
Macau, two colonies kept on purpose, stand two apart), sized from their populations around 1930, the 1928 railways line by line
(Beiping-Mukden, Beiping-Hankou, Tianjin-Pukou, the Longhai, the Chinese Eastern and South Manchuria railways, Canton-Kowloon, the
Yunnan railway...), and strategic resources balanced for every side.

[b]The rules[/b]
Techs through the Industrial era plus Flight, Combustion, Replaceable Parts, Railroad, Refrigeration and Ballistics; research is
off. Great War Infantry, Riflemen, Lancers and Cavalry, Artillery, Machine Guns, a few tanks, Triplanes and bombers, gunboats and
cruisers. No world wonders, no religion, no happiness, no leagues. The top panel shows the real date and the week. Domination
victory only, no turn limit.

[b]The events[/b]
The Disbandment Conference, the Northeast Flag Replacement and the Yang-Chang incident, the Hunan incident and the Chiang-Guangxi
war, Han Fuju's defection, the northwest famine, the Chinese Eastern Railway crisis and the Soviet offensives of 1929, the Central
Plains War and the Northeast Army entering the pass, the rendition of Weihaiwei, the five encirclement campaigns, the 1931 floods,
the Canton government; the Mukden incident, the Nenjiang Bridge, Manchukuo, the Shanghai incident, Rehe and the Tanggu Truce, the
Chahar Anti-Japanese Allied Army, the Fujian People's Government; Jinggangshan, Changting, Gutian, the Chinese Soviet Republic,
the Ningdu uprising, the Long March with Zunyi and Luding, Wayaobao, the Eastern Expedition; the He-Umezu Agreement, East Hebei,
the currency reform, the Liangguang incident, Bailingmiao, the Xi'an incident and the Marco Polo Bridge. Cities change hands where
history handed them over without a battle. Event texts are neutral and factual.

[b]Requirements[/b]
Civilization V with Gods & Kings and Brave New World. Windows and Mac. Single player. English and Russian text.
Start the scenario from Mods -> Single Player -> Scenarios. Enable this mod alone.

[b]Known limits and simplifications[/b]
Xinjiang, Tibet and most of Qinghai are off the map. Japan is a city-state that acts through events, not a player;
the Shanghai International Settlement and the Tianjin concessions are too small for the hex scale. Guangdong is a city-state until
1936. The Long March is not scripted step by step: the Red Army gets its units at Yudu and in northern Shaanxi. No multiplayer.
The AI plays with the stock logic.

Portraits and emblems: Wikimedia Commons, public domain. The leaders are historical figures, their dialogue is invented. Map data:
Natural Earth, NOAA ETOPO 2022, Koppen-Geiger. Unit and building art: Firaxis.

[b]Changelog[/b]

v1 (2026-11-01): first release. Six sides with their own unique units and buildings, thirteen city-states, the 1928 railways, seventy-eight dated events.
```
