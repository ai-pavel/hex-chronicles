# China 1928: the unique units and buildings of the six sides (replacing the donor civilizations' own: Chu-Ko-Nu and Paper Maker,
# Impi and Ikanda, Cossack and Krepost, Panzer and Hanse, Mehal Sefari and Stele, Pathfinder and Comanche Riders), the ability
# whose stock effect is dead in this scenario, and the SQL that does it at mod load, with the English text.  Russian text is
# RU_UNIQUES in ru.py; the ability texts are in build_text.py and ru.py with the rest of each side.
# Each unit/building is cloned from a stock row buildable with the scenario's techs (through the Industrial era plus Flight,
# Combustion, Replaceable Parts, Railroad, Refrigeration and Ballistics: no Cavalry, no Riflemen, no Gatling Guns) and keeps the
# stock 3D model, icon, tech and upgrade path; only stats, promotions, yields and text change.  The event units stay the stock
# types the events name; only what a side builds itself is its unique.

# key, side, base unit, unit class, SQL column changes, free promotions, EN name / help / strategy / civilopedia
UNITS = [
    dict(key='CENTRAL_ARMY', side='NAN', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = 55, Cost = 360", promos=['PROMOTION_SHOCK_1'],
         name='Central Army Division', help='National Government replacement for the Great War Infantry. 55 [ICON_STRENGTH] Combat Strength instead of 50 and the Shock I promotion; about 12% more expensive (360 [ICON_PRODUCTION]).',
         strategy='The Central Army Division is the best infantry in China: stronger and dearer than the provincial troops. Keep it for the decisive battles and let the cheaper divisions hold the line.',
         pedia="The Central Army was the core of the National Revolutionary Army that answered to Chiang Kai-shek himself, officered by graduates of the Whampoa academy. From the end of 1928 a German advisory mission, led in turn by Max Bauer, Hermann Kriebel, Georg Wetzell, Hans von Seeckt and Alexander von Falkenhausen, trained and re-equipped a growing part of it; by 1937 a handful of divisions had German weapons, helmets and training, and they bore the brunt of the battle of Shanghai that year."),
    dict(key='BIG_SWORD', side='GMJ', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = 48, Cost = 270", promos=['PROMOTION_SHOCK_1', 'PROMOTION_MARCH'],
         name='Big Sword Brigade', help='Guominjun replacement for the Great War Infantry. About 15% cheaper (270 [ICON_PRODUCTION]), the Shock I promotion and March (heals every turn, even after moving), but 48 [ICON_STRENGTH] Combat Strength instead of 50.',
         strategy='The Big Sword Brigade is hardy, cheap infantry that closes with the enemy and keeps marching. Raise it in numbers and use it to attack in the open; it is weaker behind walls than the regular divisions.',
         pedia="Short of rifles and ammunition, the armies of Feng Yuxiang issued their soldiers the dadao, a heavy two-handed broadsword, for close fighting and night raids. Feng's Northwest Army was known for its drill, its marches and its discipline: no opium, no gambling, no looting. In March 1933, at Xifengkou and Luowenyu on the Great Wall, the big-sword units of Song Zheyuan's 29th Army, formed from the old Guominjun, made their night attacks on the Japanese and became famous throughout China."),
    dict(key='MOUNTAIN_GUN', side='SHX', base='UNIT_ARTILLERY', cls='UNITCLASS_ARTILLERY', set="Combat = 24, Cost = 200", promos=[],
         name='Taiyuan Mountain Gun', help='Shanxi replacement for the Artillery. 20% cheaper (200 [ICON_PRODUCTION]) and 24 [ICON_STRENGTH] Combat Strength instead of 21.',
         strategy='The Taiyuan Mountain Gun is artillery that Shanxi can afford to build in numbers. Mass it behind the infantry on the passes into the province.',
         pedia="The arsenal at Taiyuan, founded as the Shanxi Machine Bureau in 1898, was enlarged by Yan Xishan in the 1920s into one of the largest in China. It made rifles, machine guns, mortars, ammunition and light mountain guns that could be taken apart and carried on mules over the passes of the Taihang and the Luliang, and it equipped the Shanxi army for the Northern Expedition and the Central Plains War."),
    dict(key='BREGUET', side='FT', base='UNIT_WWI_BOMBER', cls='UNITCLASS_WWI_BOMBER', set="RangedCombat = 55, Cost = 300", promos=[],
         name='Breguet 19', help='Fengtian replacement for the Great War Bomber. 55 [ICON_RANGE_STRENGTH] Ranged Strength instead of 50 and about 8% cheaper (300 [ICON_PRODUCTION]).',
         strategy='The Breguet 19 gives Fengtian the strongest bombers in China. Use it to break enemy infantry before an attack and to strike the railway towns behind the front.',
         pedia="Zhang Zuolin built the largest air arm in China in the 1920s, with French aircraft such as the Breguet 14 and the Breguet 19 and French and Russian instructors, based on the Dongta airfield outside Mukden. Zhang Xueliang kept enlarging it. On the night of the Mukden incident, 18 September 1931, the Kwantung Army seized Dongta and with it most of the Northeast's aircraft, still on the ground."),
    dict(key='GX_DIVISION', side='GX', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = 52", promos=['PROMOTION_DRILL_1', 'PROMOTION_DRILL_2'],
         name='Guangxi Division', help='Guangxi replacement for the Great War Infantry. 52 [ICON_STRENGTH] Combat Strength instead of 50 and the Drill I and Drill II promotions (+30% in rough terrain).',
         strategy='The Guangxi Division is at home in the hills of the south. Fight in forest and on hills, where it is far stronger than its enemies; on the plains it is only a little better than ordinary infantry.',
         pedia="The Seventh Army of the National Revolutionary Army, raised in Guangxi by Li Zongren and Bai Chongxi, fought its way from Hunan to the Yangtze in 1926 and 1927 and, with Chiang's First Army, threw back Sun Chuanfang's counter-attack across the river at Longtan in August 1927. Guangxi's soldiers, hardy hill-country men under young and capable officers, had a reputation as some of the best troops in China."),
    dict(key='RED_ARMY', side='CCP', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = 44, Cost = 220", promos=['PROMOTION_DRILL_1', 'PROMOTION_MARCH'],
         name='Red Army Column', help='Communist replacement for the Great War Infantry. About a third cheaper (220 [ICON_PRODUCTION]), the Drill I (+15% in rough terrain) and March (heals every turn, even after moving) promotions, but 44 [ICON_STRENGTH] Combat Strength instead of 50.',
         strategy='The Red Army Column is a guerrilla force: cheap, at home in the hills and able to heal on the move. Avoid fortified cities and strong divisions in the open; strike isolated units and slip away.',
         pedia="The Fourth Red Army was formed in the Jinggang mountains in the spring of 1928, when the troops of Zhu De and Chen Yi from the Nanchang rising joined Mao Zedong's peasants and miners. Short of everything, it fought by the rules Mao summed up for it: when the enemy advances, retreat; when he halts, harass; when he tires, attack; when he retreats, pursue. By 1930 the Red Armies of the scattered soviet bases numbered tens of thousands."),
]
# key, side, base building, building class, SQL column changes, extra rows (table, statement) after cloning, EN text
BUILDINGS = [
    dict(key='CENTRAL_ACADEMY', side='NAN', base='BUILDING_MILITARY_ACADEMY', cls='BUILDINGCLASS_MILITARY_ACADEMY', set="Cost = 200, GoldMaintenance = 0", extra=[],
         name='Central Military Academy', help='National Government replacement for the Military Academy. A third cheaper (200 [ICON_PRODUCTION]) and no maintenance.',
         strategy='The Central Military Academy gives new units the experience of a Military Academy for much less. Build it in the cities that raise the Central Army.',
         pedia="The Whampoa Military Academy was founded in 1924 on Changzhou Island below Canton, with Soviet money and advisers and Chiang Kai-shek as its commandant. Its cadets became the officers of the Northern Expedition and, for twenty years, the core of the Nationalist officer corps. In 1928 the academy moved to Nanjing as the Central Military Academy, with Chiang still at its head."),
    dict(key='FARM_COLONY', side='GMJ', base='BUILDING_GRANARY', cls='BUILDINGCLASS_GRANARY', set="GoldMaintenance = 0",
         extra=[("Building_YieldChanges", "INSERT INTO Building_YieldChanges (BuildingType, YieldType, Yield) VALUES ('BUILDING_CHN1928_FARM_COLONY', 'YIELD_PRODUCTION', 1)")],
         name='Military Farm Colony', help='Guominjun replacement for the Granary. +1 [ICON_PRODUCTION] Production as well, and no maintenance.',
         strategy='The Military Farm Colony feeds the army and puts it to work at the same time. Build it in every town of the poor northwest.',
         pedia="Feng Yuxiang's soldiers were expected to work as well as fight: they built roads, planted trees and ran their own workshops and farms. As Northwest Border Defence Commissioner at Kalgan in the mid-1920s Feng settled soldiers and refugees on land reclaimed along the Yellow River in Suiyuan, and the Guominjun lived as far as it could off what it produced itself."),
    dict(key='NW_INDUSTRY', side='SHX', base='BUILDING_WORKSHOP', cls='BUILDINGCLASS_WORKSHOP', set="GoldMaintenance = 1",
         extra=[("Building_YieldChanges", "UPDATE Building_YieldChanges SET Yield = 3 WHERE BuildingType = 'BUILDING_CHN1928_NW_INDUSTRY' AND YieldType = 'YIELD_PRODUCTION'")],
         name='Northwest Industrial Company', help='Shanxi replacement for the Workshop. +3 [ICON_PRODUCTION] Production instead of +2, and 1 [ICON_GOLD] maintenance instead of 2.',
         strategy='The Northwest Industrial Company turns Shanxi coal into weapons and goods. Build it in Taiyuan and the mining towns first.',
         pedia="In 1932 Yan Xishan launched a Ten-Year Plan for Shanxi, and in 1933 he gathered the arsenal and the provincial enterprises into the Northwest Industrial Company: steel, cement, chemicals, machinery, textiles, coal and the narrow-gauge Tongpu railway from Datong to the Yellow River. Shanxi, the 'model province', became one of the most industrialised in the interior of China."),
    dict(key='MUKDEN_ARSENAL', side='FT', base='BUILDING_FACTORY', cls='BUILDINGCLASS_FACTORY', set="GoldMaintenance = 2",
         extra=[("Building_YieldChanges", "UPDATE Building_YieldChanges SET Yield = 5 WHERE BuildingType = 'BUILDING_CHN1928_MUKDEN_ARSENAL' AND YieldType = 'YIELD_PRODUCTION'")],
         name='Mukden Arsenal', help='Fengtian replacement for the Factory. +5 [ICON_PRODUCTION] Production instead of +4, and 2 [ICON_GOLD] maintenance instead of 3.',
         strategy='The Mukden Arsenal makes Fengtian the best-armed side in China. Build it in Mukden and Harbin before anything else.',
         pedia="The Arsenal of the Three Eastern Provinces at Mukden, expanded by Zhang Zuolin from the early 1920s with foreign machinery and engineers, became the largest arms works in China, turning out rifles, machine guns, artillery, mortars and millions of rounds of ammunition. The Kwantung Army took it intact in September 1931."),
    dict(key='MILITIA_OFFICE', side='GX', base='BUILDING_BARRACKS', cls='BUILDINGCLASS_BARRACKS', set="GoldMaintenance = 0",
         extra=[("Building_DomainFreeExperiences", "UPDATE Building_DomainFreeExperiences SET Experience = 20 WHERE BuildingType = 'BUILDING_CHN1928_MILITIA_OFFICE' AND DomainType = 'DOMAIN_LAND'")],
         name='Militia Training Office', help='Guangxi replacement for the Barracks. +20 XP for land units instead of +15, and no maintenance.',
         strategy='The Militia Training Office trains better land units than ordinary Barracks and costs nothing to keep. Build it in every Guangxi town.',
         pedia="After 1931 Li Zongren, Bai Chongxi and Huang Xuchu rebuilt Guangxi on the policy of the 'Three Selfs', self-defence, self-government and self-sufficiency. Every able-bodied man was enrolled and trained in the provincial militia, whose officers were also the village heads and schoolteachers; in 1937 the system let Guangxi raise new divisions within weeks."),
    dict(key='LAND_COMMITTEE', side='CCP', base='BUILDING_MONUMENT', cls='BUILDINGCLASS_MONUMENT', set="GoldMaintenance = 0",
         extra=[("Building_YieldChanges", "INSERT INTO Building_YieldChanges (BuildingType, YieldType, Yield) VALUES ('BUILDING_CHN1928_LAND_COMMITTEE', 'YIELD_FOOD', 1)"),
                ("Building_YieldChanges", "INSERT INTO Building_YieldChanges (BuildingType, YieldType, Yield) VALUES ('BUILDING_CHN1928_LAND_COMMITTEE', 'YIELD_PRODUCTION', 1)")],
         name='Land Revolution Committee', help='Communist replacement for the Monument. +1 [ICON_FOOD] Food and +1 [ICON_PRODUCTION] Production as well, and no maintenance.',
         strategy='The Land Revolution Committee wins the villages over and feeds the Red Army. Build it first in every town the Communists hold.',
         pedia="Wherever the Red Army set up a soviet government, a land committee confiscated the land of landlords and redistributed it among the poor peasants: the Jinggangshan Land Law of December 1928 and the Xingguo Land Law of April 1929 set the rules. Land redistribution won the Red Army its recruits and its grain, and it made the soviet bases worth defending for those who lived in them."),
]
# the donor civilizations, whose own uniques are unhooked
DONOR_CIVS = {'NAN': 'CIVILIZATION_CHINA', 'GMJ': 'CIVILIZATION_ZULU', 'SHX': 'CIVILIZATION_RUSSIA', 'FT': 'CIVILIZATION_GERMANY',
              'GX': 'CIVILIZATION_ETHIOPIA', 'CCP': 'CIVILIZATION_SHOSHONE'}
# abilities whose stock effects are dead in this scenario (the Communists found no cities): the effect is replaced, the text is in build_text.py / ru.py
TRAITS = [
    ("TRAIT_GREAT_EXPANSE", "ExtraFoundedCityTerritoryClaimRange = 0, MoveFriendlyWoodsAsRoad = 1"),   # Communists: founded cities' territory -> movement through friendly forest
]
UNIT_CHILD_TABLES = [('Unit_AITypes', 'UnitAIType'), ('Unit_Flavors', 'FlavorType, Flavor'), ('Unit_ClassUpgrades', 'UnitClassType'), ('Unit_FreePromotions', 'PromotionType'),
                     ('Unit_Builds', 'BuildType'), ('Unit_ResourceQuantityRequirements', 'ResourceType, Cost'),
                     ('UnitGameplay2DScripts', 'SelectionSound, FirstSelectionSound')]   # a unit without a 2D-scripts row crashes the game when selected
BUILDING_CHILD_TABLES = [('Building_Flavors', 'FlavorType, Flavor'), ('Building_YieldChanges', 'YieldType, Yield'), ('Building_ResourceYieldChanges', 'ResourceType, YieldType, Yield'),
                         ('Building_ClassesNeededInCity', 'BuildingClassType'), ('Building_LocalResourceOrs', 'ResourceType'), ('Building_DomainFreeExperiences', 'DomainType, Experience'),
                         ('Building_YieldModifiers', 'YieldType, Yield'), ('Building_RiverPlotYieldChanges', 'YieldType, Yield'),
                         ('Building_DomainProductionModifiers', 'DomainType, Modifier'), ('Building_UnitCombatFreeExperiences', 'UnitCombatType, Experience'),
                         ('Building_UnitCombatProductionModifiers', 'UnitCombatType, Modifier'), ('Building_SeaResourceYieldChanges', 'YieldType, Yield')]


def sql():
    out = ["-- China 1928: unique units and buildings of the six sides, cloned from the stock rows at load time, and the ability whose",
           "-- stock effect is dead in the scenario (generated by text/build_text.py from text/uniques.py).",
           "-- The donor civilizations' own uniques are unhooked; stock 3D models, icons, techs and upgrade paths are kept.", ""]
    for u in UNITS:
        t = f"UNIT_CHN1928_{u['key']}"
        out += [f"-- {u['name']} ({u['side']}): {u['base']}",
                f"CREATE TEMP TABLE tmp_u AS SELECT * FROM Units WHERE Type = '{u['base']}';",
                f"UPDATE tmp_u SET ID = (SELECT MAX(ID) + 1 FROM Units), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_CHN1928_{u['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {u['set']};",
                "INSERT INTO Units SELECT * FROM tmp_u; DROP TABLE tmp_u;"]
        for table, cols in UNIT_CHILD_TABLES:
            out.append(f"INSERT INTO {table} (UnitType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE UnitType = '{u['base']}';")
        for p in u['promos']: out.append(f"INSERT INTO Unit_FreePromotions (UnitType, PromotionType) VALUES ('{t}', '{p}');")
        out.append("")
    out.append("-- replace the donors' unique units")
    for civ in DONOR_CIVS.values(): out.append(f"DELETE FROM Civilization_UnitClassOverrides WHERE CivilizationType = '{civ}';")
    for u in UNITS: out.append(f"INSERT INTO Civilization_UnitClassOverrides (CivilizationType, UnitClassType, UnitType) VALUES ('{DONOR_CIVS[u['side']]}', '{u['cls']}', 'UNIT_CHN1928_{u['key']}');")
    out.append("")
    for b in BUILDINGS:
        t = f"BUILDING_CHN1928_{b['key']}"
        out += [f"-- {b['name']} ({b['side']}): {b['base']}",
                f"CREATE TEMP TABLE tmp_b AS SELECT * FROM Buildings WHERE Type = '{b['base']}';",
                f"UPDATE tmp_b SET ID = (SELECT MAX(ID) + 1 FROM Buildings), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_CHN1928_{b['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {b['set']};",
                "INSERT INTO Buildings SELECT * FROM tmp_b; DROP TABLE tmp_b;"]
        for table, cols in BUILDING_CHILD_TABLES:
            out.append(f"INSERT INTO {table} (BuildingType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE BuildingType = '{b['base']}';")
        for table, stmt in b['extra']: out.append(stmt + ';')
        out.append("")
    out.append("-- replace the donors' unique buildings")
    for civ in DONOR_CIVS.values(): out.append(f"DELETE FROM Civilization_BuildingClassOverrides WHERE CivilizationType = '{civ}';")
    for b in BUILDINGS: out.append(f"INSERT INTO Civilization_BuildingClassOverrides (CivilizationType, BuildingClassType, BuildingType) VALUES ('{DONOR_CIVS[b['side']]}', '{b['cls']}', 'BUILDING_CHN1928_{b['key']}');")
    out.append("")
    out.append("-- abilities: the dead stock effects replaced")
    for trait, sets in TRAITS: out.append(f"UPDATE Traits SET {sets} WHERE Type = '{trait}';")
    out.append("")
    return '\n'.join(out)
