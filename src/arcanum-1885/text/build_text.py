#!/usr/bin/env python3
"""Arcanum 1885 text: nations, leaders, city lists, city-states, natural wonders, Dawn of Man (EN + RU) and the
database rows that depend on them (minor civs, city names, colours)."""
import os, html
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.join(HERE, '..', 'ui')
NL = '[NEWLINE][NEWLINE]'
NATIONS = {  # donor civ -> Arcanum nation
 'ENGLAND': dict(en=dict(name='Tarant', long='The Unified Kingdom of Tarant', adj='Tarantian', leader='The Industrial Council',
     dawn="Tarant, the smoke of ten thousand chimneys hangs over the greatest city the world has ever seen. The Industrial Council rules by patent and by purse, the steam engine has changed everything in a single lifetime, and the old powers of the continent look on with envy and fear." + NL + "Build the factories, lay the rails, fill the sky with airships and make Arcanum a market for Tarantian goods. The age of magick is ending; make sure the age that replaces it bears your name."),
     ru=dict(name='Тарант', long='Объединённое Королевство Тарант', adj='Тарантский', leader='Промышленный совет',
     dawn="Тарант, дым десяти тысяч труб висит над величайшим городом, какой видел мир. Промышленный совет правит патентом и кошельком, паровая машина за одну жизнь изменила всё, а старые державы континента смотрят с завистью и страхом." + NL + "Стройте фабрики, кладите рельсы, наполняйте небо дирижаблями и превратите Арканум в рынок тарантских товаров. Век магии кончается; сделайте так, чтобы век, который его сменит, носил ваше имя."),
     cities=['Tarant', 'Vooriden', 'Blackwater', 'Harrow', 'Ironbridge', 'Kensington Fields', 'Cogsworth', 'Easthaven', 'Gilbert Falls', 'Steamford']),
 'FRANCE': dict(en=dict(name='Caladon', long='The Kingdom of Caladon', adj='Caladonian', leader='The Crown of Caladon',
     dawn="Caladon, oldest of the human kingdoms, the city of white towers at the edge of the southern sea. Your nobles still remember when every court in Arcanum bowed to Caladon, and they intend to see those days return, by steam or by sorcery." + NL + "Arland is yours to settle, the sea lanes are yours to command, and the upstart merchants of Tarant have yet to learn that gold cannot buy a thousand years of history."),
     ru=dict(name='Каладон', long='Королевство Каладон', adj='Каладонский', leader='Корона Каладона',
     dawn="Каладон, старейшее из людских королевств, город белых башен на краю южного моря. Ваша знать ещё помнит времена, когда каждый двор Арканума кланялся Каладону, и намерена вернуть эти дни, паром или колдовством." + NL + "Арланд ваш, чтобы его заселить, морские пути ваши, чтобы ими повелевать, а выскочки-купцы Таранта ещё не поняли, что золото не купит тысячу лет истории."),
     cities=['Caladon', 'Arland', "Razor's Pointe", "Bolo's Landing", 'Southwatch', 'Whitecliff', 'Marrowgate', 'Pellingham', 'Cove of Saints', 'Ostend']),
 'RUSSIA': dict(en=dict(name='Cumbria', long='The Kingdom of Cumbria', adj='Cumbrian', leader='King Praetor',
     dawn="Cumbria, land of knights and old oaths, where King Praetor still holds court in the grey halls of Dernholm and the sword is worth more than the ledger. The engines of Tarant are an insult to everything your fathers stood for, and yet the smoke keeps creeping north." + NL + "Hold the passes of the Stonewall, keep the barons loyal and the orcs in their hills, and decide whether Cumbria will meet the new age with a lance or with a locomotive."),
     ru=dict(name='Камбрия', long='Королевство Камбрия', adj='Камбрийский', leader='Король Претор',
     dawn="Камбрия, земля рыцарей и старых клятв, где король Претор всё ещё держит двор в серых залах Дернхольма, а меч стоит дороже бухгалтерской книги. Машины Таранта это оскорбление всему, за что стояли ваши отцы, но дым всё ползёт на север." + NL + "Держите перевалы Каменной стены, баронов в верности, а орков в их холмах, и решите, встретит ли Камбрия новый век с копьём или с локомотивом."),
     cities=['Dernholm', 'Gorgoth Watch', 'Thornbury', 'Greywall', "Hardin's Pass", 'Ravensmoor', 'Oakhold', 'Kingsmere', 'Ashford', 'Highgarde']),
 'GERMANY': dict(en=dict(name='Wheel Clan', long='The Wheel Clan of the Dwarves', adj='Dwarven', leader='Loghaire Thunder Stone',
     dawn="Loghaire Thunder Stone, king of the Wheel Clan, your people carved the first engines while humans were still counting on their fingers, and your mountain holds the deepest mines on the continent. Now the humans have learned your secrets and are selling them back to you." + NL + "Bring the clans together, dig deeper than anyone has dared, and show the surface world what dwarven engineering can do when it is finally allowed to leave the mountain."),
     ru=dict(name='Колесный клан', long='Колесный клан гномов', adj='Гномий', leader='Логхейр Тандерстоун',
     dawn="Логхейр Тандерстоун, король Колесного клана, ваш народ вырезал первые механизмы, когда люди ещё считали на пальцах, а ваша гора хранит глубочайшие шахты континента. Теперь люди выучили ваши секреты и продают их вам обратно." + NL + "Соберите кланы, копайте глубже, чем кто-либо осмеливался, и покажите наземному миру, на что способна гномья инженерия, когда ей наконец позволят покинуть гору."),
     cities=['Wheel Clan Hold', 'Iron Clan', 'Black Mountain Clan', 'Stonecutter Clan', 'Deepforge', 'Thunder Gate', 'Anvilrest', 'Coalhearth', 'Gearhollow', 'Steelhome']),
 'SWEDEN': dict(en=dict(name='Vendigroth', long='The Technocracy of Vendigroth', adj='Vendigrothian', leader='The Technocrat Council',
     dawn="Vendigroth, the city that was supposed to have died two thousand years ago. In this history the devices still hum beneath the wastes, the Technocrat Council still convenes, and the rest of Arcanum is only now inventing what your ancestors threw away." + NL + "Your province is a desert and your people are few, but your knowledge is centuries ahead. Trade it, guard it, or use it, and remember what happened the last time Vendigroth frightened the world."),
     ru=dict(name='Вендигрот', long='Технократия Вендигрот', adj='Вендигротский', leader='Совет технократов',
     dawn="Вендигрот, город, который должен был погибнуть две тысячи лет назад. В этой истории машины всё ещё гудят под пустошами, Совет технократов всё ещё заседает, а остальной Арканум только теперь изобретает то, что ваши предки выбросили." + NL + "Ваша провинция пустыня, а народ немногочислен, но ваши знания опережают всех на века. Торгуйте ими, храните их или пустите в ход, и помните, что случилось в прошлый раз, когда Вендигрот напугал мир."),
     cities=['Vendigroth City', 'Vendigrothian Harbour', 'Veloric', 'Kerlin', 'Arronax Reach', 'Dustfall', 'Glasshaven', 'Lumen', 'Null Point', 'Saltmarch']),
}
LEADER_KEY = {'ENGLAND': 'TXT_KEY_LEADER_ELIZABETH', 'FRANCE': 'TXT_KEY_LEADER_NAPOLEON', 'RUSSIA': 'TXT_KEY_LEADER_CATHERINE', 'GERMANY': 'TXT_KEY_LEADER_BISMARCK', 'SWEDEN': 'TXT_KEY_LEADER_GUSTAVUS_ADOLPHUS'}
CITY_STATES = [  # type, EN name, RU name
 ('MINOR_CIV_ARC_QINTARRA', 'Qintarra', 'Кинтарра'), ('MINOR_CIV_ARC_ASHBURY', 'Ashbury', 'Эшбери'), ('MINOR_CIV_ARC_BLACKROOT', 'Black Root', 'Чёрный Корень'),
 ('MINOR_CIV_ARC_STILLWATER', 'Stillwater', 'Стиллуотер'), ('MINOR_CIV_ARC_SHROUDED', 'Shrouded Hills', 'Тёмные Холмы'), ('MINOR_CIV_ARC_ROSEBOROUGH', 'Roseborough', 'Роузборо'),
 ('MINOR_CIV_ARC_TULLA', 'Tulla', 'Тулла'), ('MINOR_CIV_ARC_DESPAIR', 'Isle of Despair', 'Остров Отчаяния'), ('MINOR_CIV_ARC_BEDOKAAN', 'Bedokaan', 'Бедокаан'), ('MINOR_CIV_ARC_TSENANG', "T'sen-Ang", 'Тсен-Анг')]
WONDERS = [  # feature text key, EN, RU
 ('TXT_KEY_FEATURE_VOLCANO', "Bellerogrim's Lair", 'Логово Беллерогрима'), ('TXT_KEY_FEATURE_MT_SINAI', 'Ancient Temple of Derian-Ka', 'Древний храм Дериан-Ка'),
 ('TXT_KEY_FEATURE_SRI_PADA', 'Elven Burial Site', 'Эльфийское погребение'), ('TXT_KEY_FEATURE_MESA', 'Ruins of Kree', 'Руины Кри'), ('TXT_KEY_FEATURE_GIBRALTAR', 'Rock of Despair', 'Скала Отчаяния'),
 ('TXT_KEY_FEATURE_ULURU', 'Ring of Brodgar', 'Кольцо Бродгара'), ('TXT_KEY_FEATURE_FOUNTAIN_YOUTH', "Falcon's Ache", 'Пещера Фалькона'), ('TXT_KEY_FEATURE_LAKE_VICTORIA', 'Bangellian Deeps', 'Бангеллианские глубины'),
 ('TXT_KEY_FEATURE_CRATER', "Lethe Wyvern's Lair", 'Логово виверны Лете'), ('TXT_KEY_FEATURE_KILIMANJARO', 'Stonewall Peak', 'Пик Каменной стены'), ('TXT_KEY_FEATURE_EL_DORADO', 'Mines of the Wheel Clan', 'Копи Колесного клана'),
 ('TXT_KEY_FEATURE_GEYSER', "Torg's Altar", 'Алтарь Торга')]
def rows_for(lang):
    rows = []
    def rep(tag, text): rows.append(f'    <Replace Tag="{tag}" Text="{html.escape(text, quote=True)}" />')
    for civ, n in NATIONS.items():
        t = n[lang]
        rep(f'TXT_KEY_CIV_{civ}_DESC', t['long']); rep(f'TXT_KEY_CIV_{civ}_SHORT_DESC', t['name']); rep(f'TXT_KEY_CIV_{civ}_ADJECTIVE', t['adj'])
        rep(LEADER_KEY[civ], t['leader']); rep(f'TXT_KEY_ARC_{civ}_DAWN', t['dawn'])  # Smoky Skies points all five civs at one shared Dawn of Man key; the rules file repoints each to this one
        for i, c in enumerate(n['cities']): rep(f'TXT_KEY_CITY_NAME_ARC_{civ}_{i}', c)
    for mtype, en, ru in CITY_STATES: rep(f'TXT_KEY_CITYSTATE_{mtype[10:]}', en if lang == 'en' else ru)
    for key, en, ru in WONDERS: rep(key, en if lang == 'en' else ru)
    rep('TXT_KEY_ARC_SCENARIO_TITLE', 'Arcanum 1885' if lang == 'en' else 'Арканум 1885')
    return rows
xml = ('<?xml version="1.0" encoding="utf-8"?>\n<!-- Arcanum 1885: nations, leaders, city names, free cities and natural wonders (EN + RU). Applied after the steampunk scenario text. -->\n<GameData>\n  <Language_en_US>\n'
       + '\n'.join(rows_for('en')) + '\n  </Language_en_US>\n  <Language_RU_RU>\n' + '\n'.join(rows_for('ru')) + '\n  </Language_RU_RU>\n</GameData>\n')
open(os.path.join(UI, 'Arcanum1885_Text.xml'), 'w', encoding='utf-8').write(xml)
# ---- database rows: city lists, minor civs, colours
PCOL = {'ENGLAND': ('#C9A227', '#2B2B2B'), 'FRANCE': ('#F2F2F2', '#1F4E9A'), 'RUSSIA': ('#FFFFFF', '#8B1A1A'), 'GERMANY': ('#FFB347', '#5A3A1A'), 'SWEDEN': ('#B5F5EC', '#0F5F5C')}
KEYS = {'ENGLAND': 'TARANT', 'FRANCE': 'CALADON', 'RUSSIA': 'CUMBRIA', 'GERMANY': 'WHEEL', 'SWEDEN': 'VENDIGROTH'}
def rgb(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
lx = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Arcanum 1885 database rows: Arcanum city lists for the five nations, ten free cities as city-states, nation colours. -->', '<GameData>', '  <Civilization_CityNames>']
for civ, n in NATIONS.items():
    lx.append(f'    <Delete CivilizationType="CIVILIZATION_{civ}" />')
    for i in range(len(n['cities'])): lx.append(f'    <Row><CivilizationType>CIVILIZATION_{civ}</CivilizationType><CityName>TXT_KEY_CITY_NAME_ARC_{civ}_{i}</CityName></Row>')
lx += ['  </Civilization_CityNames>', '  <Colors>']
for civ, (icon, bg) in PCOL.items():
    for suf, hx in (('ICON', icon), ('BG', bg)):
        r, g, b = rgb(hx); lx.append(f'    <Row><Type>COLOR_PLAYER_ARC_{KEYS[civ]}_{suf}</Type><Red>{r:.3f}</Red><Green>{g:.3f}</Green><Blue>{b:.3f}</Blue><Alpha>1</Alpha></Row>')
lx += ['  </Colors>', '  <PlayerColors>']
for civ in PCOL: lx.append(f'    <Row><Type>PLAYERCOLOR_ARC_{KEYS[civ]}</Type><PrimaryColor>COLOR_PLAYER_ARC_{KEYS[civ]}_ICON</PrimaryColor><SecondaryColor>COLOR_PLAYER_ARC_{KEYS[civ]}_BG</SecondaryColor><TextColor>COLOR_PLAYER_WHITE_TEXT</TextColor></Row>')
lx += ['  </PlayerColors>', '  <Civilizations>']
for civ in PCOL: lx.append(f'    <Update><Where Type="CIVILIZATION_{civ}" /><Set DefaultPlayerColor="PLAYERCOLOR_ARC_{KEYS[civ]}" DawnOfManQuote="TXT_KEY_ARC_{civ}_DAWN" /></Update>')
lx += ['  </Civilizations>', '  <MinorCivilizations>']
TRAITS = {'QINTARRA': 'MINOR_TRAIT_CULTURED', 'ASHBURY': 'MINOR_TRAIT_MERCANTILE', 'BLACKROOT': 'MINOR_TRAIT_MARITIME', 'STILLWATER': 'MINOR_TRAIT_MILITARISTIC', 'SHROUDED': 'MINOR_TRAIT_MERCANTILE',
          'ROSEBOROUGH': 'MINOR_TRAIT_CULTURED', 'TULLA': 'MINOR_TRAIT_CULTURED', 'DESPAIR': 'MINOR_TRAIT_MILITARISTIC', 'BEDOKAAN': 'MINOR_TRAIT_MARITIME', 'TSENANG': 'MINOR_TRAIT_MILITARISTIC'}
MCOL = ['PLAYERCOLOR_MINOR_LIGHT_GREEN', 'PLAYERCOLOR_MINOR_GOLDENROD', 'PLAYERCOLOR_MINOR_LIGHT_BLUE', 'PLAYERCOLOR_MINOR_GRAY', 'PLAYERCOLOR_MINOR_PEACH', 'PLAYERCOLOR_MINOR_LIGHT_PURPLE', 'PLAYERCOLOR_MINOR_WHITE', 'PLAYERCOLOR_MINOR_DARK_LEMON', 'PLAYERCOLOR_MINOR_MIDDLE_CYAN', 'PLAYERCOLOR_MINOR_PURPLE']
for i, (mtype, en, ru) in enumerate(CITY_STATES):
    k = mtype[14:]; key = f'TXT_KEY_CITYSTATE_{mtype[10:]}'
    lx.append(f'    <Row><Type>{mtype}</Type><Description>{key}</Description><Civilopedia>{key}</Civilopedia><ShortDescription>{key}</ShortDescription><Adjective>{key}</Adjective><ArtDefineTag>ART_DEF_CIVILIZATION_MINOR</ArtDefineTag><DefaultPlayerColor>{MCOL[i]}</DefaultPlayerColor><ArtStyleType>ARTSTYLE_EUROPEAN</ArtStyleType><ArtStyleSuffix>_EURO</ArtStyleSuffix><ArtStylePrefix>EUROPEAN </ArtStylePrefix><MinorCivTrait>{TRAITS[k]}</MinorCivTrait></Row>')
lx += ['  </MinorCivilizations>', '  <MinorCivilization_CityNames>']
for mtype, en, ru in CITY_STATES: lx.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><CityName>TXT_KEY_CITYSTATE_{mtype[10:]}</CityName></Row>')
lx += ['  </MinorCivilization_CityNames>', '  <MinorCivilization_Flavors>']
for mtype, en, ru in CITY_STATES:
    for fl, v in (('FLAVOR_CITY_DEFENSE', 8), ('FLAVOR_DEFENSE', 8), ('FLAVOR_GROWTH', 5), ('FLAVOR_GOLD', 5), ('FLAVOR_PRODUCTION', 5)):
        lx.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><FlavorType>{fl}</FlavorType><Flavor>{v}</Flavor></Row>')
lx += ['  </MinorCivilization_Flavors>', '</GameData>', '']
open(os.path.join(UI, 'Arcanum1885_Rules.xml'), 'w', encoding='utf-8').write('\n'.join(lx))
print('wrote Arcanum1885_Text.xml and Arcanum1885_Rules.xml')

# ---- tourism and calendar fixes around the Smoky Skies rules.
# Stage 1 runs between RemoveModernEras.xml (which deletes the Industrial/Modern techs) and TechTreeUpdate.xml (whose
# DeleteMissingReferences would otherwise drop every building whose PrereqTech is gone). It parks the tourism buildings on a
# surviving tech; stage 2 (in the main rules file, applied last) moves them onto steampunk techs.
TOURISM = [('BUILDING_HOTEL', 'TECH_ECONOMIC_IMPERIALISM'), ('BUILDING_AIRPORT', 'TECH_AIRSHIPS'), ('BUILDING_TOURIST_CENTER', 'TECH_GOSPEL_OF_WEALTH'), ('BUILDING_STADIUM', 'TECH_CIVIL_DEFENSE')]
pre = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Arcanum 1885, stage 1: keep the BNW tourism buildings alive while the steampunk tech tree is being rebuilt. -->', '<GameData>', '  <Buildings>']
pre += [f'    <Update><Where Type="{b}" /><Set PrereqTech="TECH_ARCHAEOLOGY" /></Update>' for b, _ in TOURISM]
pre += ['  </Buildings>',
        '  <!-- The Internet is a Brave New World tech the Gods & Kings scenario never knew about; without this it survives the pruning as a lone Future-era tech. -->',
        '  <Technologies>', '    <Delete Type="TECH_INTERNET" />', '  </Technologies>', '</GameData>', '']
open(os.path.join(UI, 'Arcanum1885_PreTech.xml'), 'w', encoding='utf-8').write('\n'.join(pre))
post = ['  <Buildings>'] + [f'    <Update><Where Type="{b}" /><Set PrereqTech="{t}" /></Update>' for b, t in TOURISM] + ['  </Buildings>',
        '  <!-- The Internet tech is gone with the modern tree; its tourism doubling moves to the last steampunk tech. -->',
        '  <Technologies>', '    <Update><Where Type="TECH_THE_GRAND_IDEA" /><Set InfluenceSpreadModifier="100" /></Update>', '  </Technologies>',
        '  <!-- Calendar: one turn = one year from 1885 (the steampunk rules set 1800). -->',
        '  <Defines>', '    <Update><Where Name="START_YEAR" /><Set Value="1885" /></Update>', '  </Defines>',
        '  <GameSpeed_Turns>', '    <Delete GameSpeedType="GAMESPEED_EPIC" />',
        '    <Row><GameSpeedType>GAMESPEED_EPIC</GameSpeedType><MonthIncrement>12</MonthIncrement><TurnsPerIncrement>100000</TurnsPerIncrement></Row>',
        '    <Delete GameSpeedType="GAMESPEED_QUICK" />',
        '    <Row><GameSpeedType>GAMESPEED_QUICK</GameSpeedType><MonthIncrement>12</MonthIncrement><TurnsPerIncrement>100000</TurnsPerIncrement></Row>',
        '  </GameSpeed_Turns>']
rp = os.path.join(UI, 'Arcanum1885_Rules.xml'); r = open(rp, encoding='utf-8').read()
open(rp, 'w', encoding='utf-8').write(r.replace('</GameData>', '\n'.join(post) + '\n</GameData>'))
print('wrote Arcanum1885_PreTech.xml, extended rules')

# ---- ideologies. The Smoky Skies scenario ran under Gods & Kings and deleted Freedom/Order/Autocracy as ordinary branches;
# under Brave New World they are the ideologies the engine demands in the Modern era. build_mod.py keeps them when copying
# PolicyUpdate.xml. Stage 1 (before PolicyUpdate.xml) removes the two BNW-only branches the scenario does not know about;
# stage 2 (after it) renumbers the surviving rows so IDs stay contiguous for the game core.
pp = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Arcanum 1885, before the Smoky Skies policy tree: drop the Brave New World branches the Gods & Kings scenario never handled. -->',
      '<GameData>', '  <PolicyBranchTypes>', '    <Delete Type="POLICY_BRANCH_AESTHETICS" />', '    <Delete Type="POLICY_BRANCH_EXPLORATION" />', '  </PolicyBranchTypes>', '</GameData>', '']
open(os.path.join(UI, 'Arcanum1885_PrePolicy.xml'), 'w', encoding='utf-8').write('\n'.join(pp))
sql = """-- Arcanum 1885, after the Smoky Skies policy tree: the five scenario branches were inserted with IDs 0-4 and the three
-- Brave New World ideologies keep their stock IDs, so renumber both tables to contiguous 0..N-1 (order preserved).
CREATE TEMP TABLE ArcBranchIds AS SELECT ID AS OldID, (SELECT COUNT(*) FROM PolicyBranchTypes b2 WHERE b2.ID < b1.ID) AS NewID FROM PolicyBranchTypes b1;
UPDATE PolicyBranchTypes SET ID = (SELECT NewID FROM ArcBranchIds WHERE OldID = PolicyBranchTypes.ID) + 10000;
UPDATE PolicyBranchTypes SET ID = ID - 10000;
DROP TABLE ArcBranchIds;
CREATE TEMP TABLE ArcPolicyIds AS SELECT ID AS OldID, (SELECT COUNT(*) FROM Policies p2 WHERE p2.ID < p1.ID) AS NewID FROM Policies p1;
UPDATE Policies SET ID = (SELECT NewID FROM ArcPolicyIds WHERE OldID = Policies.ID) + 10000;
UPDATE Policies SET ID = ID - 10000;
DROP TABLE ArcPolicyIds;
"""
open(os.path.join(UI, 'Arcanum1885_PostPolicy.sql'), 'w', encoding='utf-8').write(sql)
print('wrote Arcanum1885_PrePolicy.xml, Arcanum1885_PostPolicy.sql')
