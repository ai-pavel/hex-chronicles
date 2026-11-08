# Spain 1936: the unique units and buildings of the six sides (replacing the donor civilizations' own: Impi and Ikanda, Cossack
# and Krepost, Panzer and Hanse, Pathfinder and Comanche Riders, Mehal Sefari and Stele, Jaguar and Floating Gardens), with the
# SQL that clones them from the stock rows at mod load, and their English text.  Russian text is RU_UNIQUES in ru.py.
# Each unit/building keeps the stock 3D model, icon and tech; only stats, promotions, yields and text change.
# The event units stay the stock types the events name; only what a side builds itself is its unique.

# key, side, base unit, unit class, SQL column changes, free promotions, EN name / help / strategy / civilopedia
UNITS = [
    dict(key='T26', side='REP', base='UNIT_WWI_TANK', cls='UNITCLASS_WWI_TANK', set="Combat = 65", promos=[],
         name='T-26', help='Republican replacement for the Landship. 65 [ICON_STRENGTH] Combat Strength instead of 60.',
         strategy='The T-26 is the Republican Landship: the best tank in Spain in 1936. Use it with infantry to break a line or to counter-attack a breakthrough.',
         pedia="The T-26 was a Soviet light tank armed with a 45 mm gun, which outgunned every German and Italian tank sent to Spain. About 280 were delivered to the Republic from October 1936; the first went into action at Sesena south of Madrid on 29 October 1936, and T-26s fought in every great battle of the war, from the Jarama to the Ebro."),
    dict(key='LEGION', side='NAT', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = 52, Cost = 352", promos=['PROMOTION_DRILL_1', 'PROMOTION_SHOCK_1'],
         name='Spanish Legion', help='Nationalist replacement for the Great War Infantry. 52 [ICON_STRENGTH] Combat Strength instead of 50, the Drill I and Shock I promotions; 10% more expensive.',
         strategy='The Legion is the shock infantry of the Army of Africa: stronger, already promoted, and dearer. Put it at the head of every attack and let the militias hold the line behind it.',
         pedia="The Spanish Legion (Tercio de Extranjeros) was founded in 1920 by Jose Millan-Astray on the model of the French Foreign Legion, to fight the Rif War in Morocco; Franco was its second commander. Its banderas, flown across the Strait in July and August 1936, were with the Regulares the only battle-hardened troops in Spain, and spearheaded the march from Seville to Madrid."),
    dict(key='REQUETE', side='NORTH', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = Combat", promos=['PROMOTION_DRILL_1'],
         name='Requetes', help='Army of the North replacement for the Great War Infantry. The Drill I promotion: +15% in rough terrain (hills, forest).',
         strategy='The Requetes are the infantry of the Army of the North, at home in the mountains of Navarre, the Basque Country and the Sierra de Guadarrama. Send them where the front climbs.',
         pedia="The requetes were the militia of the Carlist movement, trained in secret in Navarre before the rising. On 19 July 1936 thousands of them in red berets came into Pamplona; organised in tercios by the Carlist War Junta of Navarre, they fought on the Guadarrama passes, in Gipuzkoa and Biscay and on every front to the end of the war."),
    dict(key='BLINDAT', side='CAT', base='UNIT_WWI_TANK', cls='UNITCLASS_WWI_TANK', set="Combat = 52, Cost = 280, Moves = 5", promos=[],
         name='Blindat', help='Catalan replacement for the Landship. 20% cheaper (280 [ICON_PRODUCTION]) and +1 [ICON_MOVES] Movement, but 52 [ICON_STRENGTH] Combat Strength instead of 60.',
         strategy='The Blindat is an armoured car from the factories of Barcelona: cheap and fast, weaker than a tank. Use it to rush reinforcements along the roads and to pick off broken units.',
         pedia="Within days of the rising the metal works of Barcelona were building armoured cars on lorry chassis for the militia columns leaving for Aragon. From August 1936 the Generalitat's War Industries Commission put the city's industry on a war footing, and the Catalan factories turned out armoured cars, lorries, shells and rifles for the whole Republican army."),
    dict(key='GUDARI', side='EUZ', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Cost = 340", promos=['PROMOTION_DRILL_1', 'PROMOTION_COVER_1'],
         name='Gudaris', help='Basque replacement for the Great War Infantry. The Drill I promotion (+15% in rough terrain) and Cover I (+25% defence against ranged attacks); a little more expensive (340 [ICON_PRODUCTION]).',
         strategy='The Gudaris are defenders: on the hills around Bilbao, under bombing and shelling, they hold. Dig them into the mountains and let the enemy come to them.',
         pedia="Gudari is Basque for warrior. The Euzko Gudarostea, the army of the Basque Government, was formed from the autumn of 1936 out of battalions raised by the Basque nationalists, the socialists, the communists and the anarchists of Biscay. Short of artillery and aircraft, the gudaris held the mountains of Biscay against the Navarrese brigades and the Condor Legion until June 1937."),
    dict(key='MILICIA', side='CNT', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = 46, Cost = 240", promos=['PROMOTION_MARCH'],
         name='Confederal Militia', help='CNT-FAI replacement for the Great War Infantry. 25% cheaper (240 [ICON_PRODUCTION]) and the March promotion (heals every turn, even after moving), but 46 [ICON_STRENGTH] Combat Strength instead of 50.',
         strategy='The Confederal Militia is cheap and keeps going: raise it in numbers, keep it moving and let it heal on the march. It is weaker than a regular division; do not throw it at fortified cities alone.',
         pedia="On 24 July 1936 the first anarchist column, led by Buenaventura Durruti, left Barcelona for Aragon; the Ascaso, Ortiz, Aguiluchos and other confederal columns followed. They elected their delegates and refused military ranks, and they collectivised the villages they passed through. In 1937 they were militarised into divisions of the Popular Army, the Durruti Column becoming the 26th Division."),
]
# key, side, base building, building class, SQL column changes, extra rows (table, statement) after cloning, EN text
BUILDINGS = [
    dict(key='COMISARIADO', side='REP', base='BUILDING_MILITARY_ACADEMY', cls='BUILDINGCLASS_MILITARY_ACADEMY', set="Cost = 200, GoldMaintenance = 0", extra=[],
         name='War Commissariat', help='Republican replacement for the Military Academy. A third cheaper (200 [ICON_PRODUCTION]) and no maintenance.',
         strategy='The War Commissariat gives new units the experience of a Military Academy for much less. Build it in the cities that raise the Popular Army.',
         pedia="The General Commissariat of War, created on 15 October 1936, put a political commissar beside the commander of every unit of the new Popular Army: to keep up morale, to explain why they fought, and to watch the professional officers. Thousands of commissars, most of them socialists and communists, turned militia columns into brigades."),
    dict(key='BANDERIN', side='NAT', base='BUILDING_BARRACKS', cls='BUILDINGCLASS_BARRACKS', set="GoldMaintenance = 0",
         extra=[("Building_DomainFreeExperiences", "UPDATE Building_DomainFreeExperiences SET Experience = 20 WHERE BuildingType = 'BUILDING_ESP1936_BANDERIN' AND DomainType = 'DOMAIN_LAND'")],
         name='Recruiting Office', help='Nationalist replacement for the Barracks. +20 XP for land units instead of +15, and no maintenance.',
         strategy='The Recruiting Office trains better land units than ordinary Barracks and costs nothing to keep. Build it everywhere the Nationalists raise troops.',
         pedia="The banderines de enganche were the recruiting offices of the Legion, which enlisted volunteers with no questions asked about their past. Behind the Nationalist lines they multiplied in 1936, alongside the recruitment of tens of thousands of Moroccan Regulares in the protectorate."),
    dict(key='JUNTA', side='NORTH', base='BUILDING_ARMORY', cls='BUILDINGCLASS_ARMORY', set="Cost = 120, GoldMaintenance = 0", extra=[],
         name='Carlist War Junta', help='Army of the North replacement for the Armory. A quarter cheaper (120 [ICON_PRODUCTION]) and no maintenance.',
         strategy='The Carlist War Junta gives new land units the experience of an Armory for less. Build it in every city that raises requetes.',
         pedia="The Carlist War Junta of Navarre took charge of the requetes in Pamplona in July 1936: it raised, armed and supplied the Navarrese tercios, and ran Navarre almost as a state of its own until the Decree of Unification of April 1937 merged the Carlists into Franco's single party."),
    dict(key='COMISSIO', side='CAT', base='BUILDING_FACTORY', cls='BUILDINGCLASS_FACTORY', set="GoldMaintenance = 2",
         extra=[("Building_YieldChanges", "UPDATE Building_YieldChanges SET Yield = 5 WHERE BuildingType = 'BUILDING_ESP1936_COMISSIO' AND YieldType = 'YIELD_PRODUCTION'")],
         name='War Industries Commission', help='Catalan replacement for the Factory. +5 [ICON_PRODUCTION] Production instead of +4, and 2 [ICON_GOLD] maintenance instead of 3.',
         strategy='The War Industries Commission makes Catalonia the arsenal of the Republic. Build it in Barcelona and the industrial towns first.',
         pedia="The Generalitat set up the War Industries Commission on 7 August 1936 under Josep Tarradellas to convert the factories of Catalonia, the most industrial region of Spain, to war production. Textile mills, car works and metal shops turned to shells, cartridges, rifles, aircraft engines and armoured cars."),
    dict(key='CINTURON', side='EUZ', base='BUILDING_CASTLE', cls='BUILDINGCLASS_CASTLE', set="Defense = 1000, ExtraCityHitPoints = 50", extra=[],
         name='Iron Ring', help='Basque replacement for the Castle. +10 [ICON_STRENGTH] City Defense Strength instead of +7, and +50 Hit Points instead of +25.',
         strategy='The Iron Ring makes a Basque city very hard to take. Build it in Bilbao before the Biscay offensive comes.',
         pedia="The Iron Ring (Cinturon de Hierro) was the line of trenches, bunkers and wire built around Bilbao from the autumn of 1936. Its plans were taken to the Nationalists by one of its engineers, and on 12 June 1937, after a massive bombardment, the Navarrese brigades broke through it; Bilbao fell a week later."),
    dict(key='COLECTIVIDAD', side='CNT', base='BUILDING_WORKSHOP', cls='BUILDINGCLASS_WORKSHOP', set="GoldMaintenance = 1",
         extra=[("Building_YieldChanges", "INSERT INTO Building_YieldChanges (BuildingType, YieldType, Yield) VALUES ('BUILDING_ESP1936_COLECTIVIDAD', 'YIELD_FOOD', 1)")],
         name='Collective', help='CNT-FAI replacement for the Workshop. +1 [ICON_FOOD] Food as well, and 1 [ICON_GOLD] maintenance instead of 2.',
         strategy='The Collective feeds and equips the columns at once, and costs half as much to keep. Build it in every Aragonese town.',
         pedia="In the summer of 1936 the land and workshops of hundreds of villages in Aragon were collectivised: money was abolished in some, the harvest was shared, and the produce went to the columns at the front. The Council of Aragon ran the region until August 1937, when the government dissolved it and broke up many of the collectives."),
]
# the donor civilizations, whose own uniques are unhooked
DONOR_CIVS = {'REP': 'CIVILIZATION_RUSSIA', 'NAT': 'CIVILIZATION_ZULU', 'NORTH': 'CIVILIZATION_GERMANY', 'CAT': 'CIVILIZATION_SHOSHONE',
              'EUZ': 'CIVILIZATION_ETHIOPIA', 'CNT': 'CIVILIZATION_AZTEC'}
UNIT_CHILD_TABLES = [('Unit_AITypes', 'UnitAIType'), ('Unit_Flavors', 'FlavorType, Flavor'), ('Unit_ClassUpgrades', 'UnitClassType'), ('Unit_FreePromotions', 'PromotionType'),
                     ('Unit_Builds', 'BuildType'), ('Unit_ResourceQuantityRequirements', 'ResourceType, Cost'),
                     ('UnitGameplay2DScripts', 'SelectionSound, FirstSelectionSound')]   # a unit without a 2D-scripts row crashes the game when selected
BUILDING_CHILD_TABLES = [('Building_Flavors', 'FlavorType, Flavor'), ('Building_YieldChanges', 'YieldType, Yield'), ('Building_ResourceYieldChanges', 'ResourceType, YieldType, Yield'),
                         ('Building_ClassesNeededInCity', 'BuildingClassType'), ('Building_LocalResourceOrs', 'ResourceType'), ('Building_DomainFreeExperiences', 'DomainType, Experience'),
                         ('Building_YieldModifiers', 'YieldType, Yield'), ('Building_RiverPlotYieldChanges', 'YieldType, Yield')]


def sql():
    out = ["-- Spain 1936: unique units and buildings of the six sides, cloned from the stock rows at load time (generated by text/build_text.py).",
           "-- The donor civilizations' own uniques are unhooked; stock 3D models, icons, techs and upgrade paths are kept.", ""]
    for u in UNITS:
        t = f"UNIT_ESP1936_{u['key']}"
        out += [f"-- {u['name']} ({u['side']}): {u['base']}",
                f"CREATE TEMP TABLE tmp_u AS SELECT * FROM Units WHERE Type = '{u['base']}';",
                f"UPDATE tmp_u SET ID = (SELECT MAX(ID) + 1 FROM Units), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_ESP1936_{u['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {u['set']};",
                "INSERT INTO Units SELECT * FROM tmp_u; DROP TABLE tmp_u;"]
        for table, cols in UNIT_CHILD_TABLES:
            out.append(f"INSERT INTO {table} (UnitType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE UnitType = '{u['base']}';")
        for p in u['promos']: out.append(f"INSERT INTO Unit_FreePromotions (UnitType, PromotionType) VALUES ('{t}', '{p}');")
        out.append("")
    out.append("-- replace the donors' unique units")
    for civ in DONOR_CIVS.values(): out.append(f"DELETE FROM Civilization_UnitClassOverrides WHERE CivilizationType = '{civ}';")
    for u in UNITS: out.append(f"INSERT INTO Civilization_UnitClassOverrides (CivilizationType, UnitClassType, UnitType) VALUES ('{DONOR_CIVS[u['side']]}', '{u['cls']}', 'UNIT_ESP1936_{u['key']}');")
    out.append("")
    for b in BUILDINGS:
        t = f"BUILDING_ESP1936_{b['key']}"
        out += [f"-- {b['name']} ({b['side']}): {b['base']}",
                f"CREATE TEMP TABLE tmp_b AS SELECT * FROM Buildings WHERE Type = '{b['base']}';",
                f"UPDATE tmp_b SET ID = (SELECT MAX(ID) + 1 FROM Buildings), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_ESP1936_{b['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {b['set']};",
                "INSERT INTO Buildings SELECT * FROM tmp_b; DROP TABLE tmp_b;"]
        for table, cols in BUILDING_CHILD_TABLES:
            out.append(f"INSERT INTO {table} (BuildingType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE BuildingType = '{b['base']}';")
        for table, stmt in b['extra']: out.append(stmt + ';')
        out.append("")
    out.append("-- replace the donors' unique buildings")
    for civ in DONOR_CIVS.values(): out.append(f"DELETE FROM Civilization_BuildingClassOverrides WHERE CivilizationType = '{civ}';")
    for b in BUILDINGS: out.append(f"INSERT INTO Civilization_BuildingClassOverrides (CivilizationType, BuildingClassType, BuildingType) VALUES ('{DONOR_CIVS[b['side']]}', '{b['cls']}', 'BUILDING_ESP1936_{b['key']}');")
    out.append("")
    return '\n'.join(out)
