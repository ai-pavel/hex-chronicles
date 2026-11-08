# Canarias 1400: the unique units and buildings of the seven peoples (replacing the donor civilizations' own), with the SQL
# that clones them from the stock rows at mod load, and their English text.  Russian text is RU_UNIQUES in ru.py.
# Each unit/building keeps the stock 3D model and tech; only stats, promotions, yields and text change.

# key, people, base unit, unit class, SQL column changes, free promotions, EN name / help / strategy / civilopedia
UNITS = [
    dict(key='SIGONE', people='TENERIFE', base='UNIT_SPEARMAN', cls='UNITCLASS_SPEARMAN', set="Combat = Combat + 1", promos=['PROMOTION_DRILL_1'],
         name='Sigone', help='Guanche replacement for the Spearman. +1 [ICON_STRENGTH] Combat Strength and the Drill I promotion: +15% in rough terrain (hills, forest).',
         strategy='The Sigone is the Guanche Spearman: a little stronger, and at home in the ravines and hill slopes where the Guanches ambushed their enemies. Use it to hold rough ground and ravines.',
         pedia="The sigones were the captains of a Guanche mencey, nobles who led the warriors of a menceyato in war. The Guanche weapon was the banot, a fire-hardened wooden spear, used with a wooden shield (tarja) and backed by stones thrown with great accuracy; at Acentejo in 1494 the sigones of Taoro used the ravine to destroy a Castilian army."),
    dict(key='TIRADOR', people='GRANCANARIA', base='UNIT_ARCHER', cls='UNITCLASS_ARCHER', set="Combat = Combat + 1, RangedCombat = RangedCombat + 1", promos=[],
         name='Tirador', help='Canarii replacement for the Archer. +1 [ICON_STRENGTH] Combat Strength and +1 [ICON_RANGE_STRENGTH] Ranged Combat Strength for the same cost.',
         strategy='The Tirador is the Canarii Archer: stronger at range and in defence, same price. Put it behind your Warriors and on hills, where its stones reach two tiles. It upgrades to the Composite Bowman.',
         pedia="Every chronicler of the conquest remarked on the Canarii's skill with thrown stones: they could hit a chosen target at a distance, parry stones in flight, and a volley from a hillside could stop an armoured column. Stone throwing was trained from childhood and was the first weapon of every island, but the Canarii of Gran Canaria were the acknowledged masters."),
    dict(key='MAGADO', people='LAPALMA', base='UNIT_WARRIOR', cls='UNITCLASS_WARRIOR', set="Combat = Combat + 1", promos=['PROMOTION_COVER_1'],
         name='Magado', help='Benahoarita replacement for the Warrior. +1 [ICON_STRENGTH] Combat Strength and the Cover I promotion: +25% defence against ranged attacks.',
         strategy='The Magado is the Benahoarita Warrior: tougher, and hard to soften up with archers. It is the unit to garrison a ravine or a city with; it upgrades to the Swordsman.',
         pedia="The magado was the Benahoarita war club, a heavy wooden mace, and the name passed to the warriors who carried it. The Benahoaritas of La Palma were goat-herding cave dwellers who fought in the ravines of the steepest island of the archipelago; the caldera of Acero under Tanausu was never taken by assault."),
    dict(key='SILBADOR', people='LAGOMERA', base='UNIT_SCOUT', cls='UNITCLASS_SCOUT', set="Combat = Combat + 1", promos=['PROMOTION_SENTRY'],
         name='Silbador', help='Gomero replacement for the Scout. +1 [ICON_STRENGTH] Combat Strength and the Sentry promotion: +1 sight range.',
         strategy='The Silbador is the Gomero Scout: it sees one tile further and survives a little longer. Use it to map the island early and to watch the coast for landings.',
         pedia="The Gomeros spoke across the ravines of their island with the silbo, a whistled form of their language that carries for several kilometres. News of a landing, a raid or a council travelled from canton to canton faster than any runner; the silbo survived the conquest and is still taught on La Gomera."),
    dict(key='MARISCADOR', people='ELHIERRO', base='UNIT_WORKBOAT', cls='UNITCLASS_WORKBOAT', set="Cost = 25, Moves = Moves + 1", promos=[],
         name='Mariscador', help='Bimbache replacement for the Work Boat. Half the cost (25 [ICON_PRODUCTION]) and +1 [ICON_MOVES] Movement.',
         strategy='The Mariscador is the Bimbache Work Boat: cheap and quick. Build it early to improve every fish and shellfish tile around the small island; the sea feeds El Hierro.',
         pedia="The Bimbaches of El Hierro lived from goats, a little barley and the sea: their shell middens (concheros) line the coast of the island. On an island without springs, where water came from the mist on the Garoe tree, limpets, crabs and fish gathered from the rocks were a large part of every meal."),
    dict(key='AHEPA', people='FUERTEVENTURA', base='UNIT_SPEARMAN', cls='UNITCLASS_SPEARMAN', set="Cost = 42", promos=['PROMOTION_SHOCK_1'],
         name='Ahepa', help='Majo replacement for the Spearman. 25% cheaper (42 [ICON_PRODUCTION]) and the Shock I promotion: +15% in open terrain.',
         strategy='The Ahepa is the Majo Spearman: cheap and strong on the open plains of Erbania. Field them in numbers.',
         pedia="The ahepa was the lance of the Majos of Fuerteventura, a long wooden spear with a fire-hardened point. The Majos fought on the open plains of the driest island of the archipelago, shepherd kingdoms divided by the wall of La Pared; their warriors also carried stones and the tezzeses, a fighting stick."),
    dict(key='GUARDIA', people='LANZAROTE', base='UNIT_WARRIOR', cls='UNITCLASS_WARRIOR', set="Combat = Combat", promos=['PROMOTION_AMPHIBIOUS'],
         name='Guard of Zonzamas', help='Majo replacement for the Warrior. The Amphibious promotion: no penalty when attacking from the sea or across a river.',
         strategy='The Guard of Zonzamas is the Majo Warrior of Lanzarote: the same strength, but it lands fighting. The unit for the first crossings to the next island once Optics allows embarkation; it upgrades to the Swordsman.',
         pedia="Zonzamas was the seat of the kings of Lanzarote, a walled complex near Teguise whose ruins survive. Lanzarote was the first island Europeans reached, and from the fourteenth century its people fought off slave raiders landing on their beaches; by 1402 the Majos of Guadarfia were a few hundred, hardened by a century of defending the shore."),
]
# key, people, base building, building class, SQL column changes, extra yield rows (table, values) after cloning, EN text
BUILDINGS = [
    dict(key='TAGOROR', people='TENERIFE', base='BUILDING_MONUMENT', cls='BUILDINGCLASS_MONUMENT', set="GoldMaintenance = 0, Happiness = 1", extra=[],
         name='Tagoror', help='Guanche replacement for the Monument. +1 [ICON_HAPPINESS_1] Happiness and no maintenance cost.',
         strategy='The Tagoror gives the culture of a Monument, a point of happiness and costs nothing to keep. Build it first in every city.',
         pedia="The tagoror was the council place of the Guanches: a ring of stones, with a larger seat for the mencey, where the nobles met to judge, to decide on war and to receive envoys. Every menceyato had one, and the word survives in place names across Tenerife."),
    dict(key='CENOBIO', people='GRANCANARIA', base='BUILDING_GRANARY', cls='BUILDINGCLASS_GRANARY', set="Cost = Cost", extra=[("Building_YieldChanges", "UPDATE Building_YieldChanges SET Yield = 3 WHERE BuildingType = 'BUILDING_CAN1400_CENOBIO' AND YieldType = 'YIELD_FOOD'"), ("Building_ResourceYieldChanges", "INSERT INTO Building_ResourceYieldChanges (BuildingType, ResourceType, YieldType, Yield) VALUES ('BUILDING_CAN1400_CENOBIO', 'RESOURCE_SHEEP', 'YIELD_FOOD', 1)")],
         name='Cenobio', help='Canarii replacement for the Granary. +3 [ICON_FOOD] Food instead of +2, and +1 [ICON_FOOD] Food from Sheep as well as Wheat, Bananas and Deer.',
         strategy='The Cenobio feeds a city faster than a Granary and turns the goat pastures of the hills into food. Build it early in every city that is to grow.',
         pedia="The Cenobio de Valeron on the north coast of Gran Canaria is a cliff honeycombed with more than three hundred chambers cut into the rock under a natural arch: the collective granary of the Canarii, where the harvest of the valley was stored under the guard of the harimaguadas. Similar fortified granaries exist across the island."),
    dict(key='CUEVAS', people='LAPALMA', base='BUILDING_WALLS', cls='BUILDINGCLASS_WALLS', set="Defense = 800, ExtraCityHitPoints = 75, GoldMaintenance = 0", extra=[],
         name='Cuevas', help='Benahoarita replacement for the Walls. +8 [ICON_STRENGTH] City Defense Strength instead of +5, +75 Hit Points instead of +50, no maintenance.',
         strategy='The Cuevas make a city much harder to take than ordinary Walls, for the same cost. With the Magado garrisoned behind them a Benahoarita city on a ravine is a fortress.',
         pedia="The peoples of the islands lived in caves, natural or cut into the volcanic tuff, and on La Palma the cave villages of the ravines of Aridane and Tedote climb the cliff faces in terraces. A cave settlement on a ledge, reached by one path, needed no wall; the conquerors had to take them one at a time."),
    dict(key='BANCALES', people='LAGOMERA', base=None, cls=None, set=None, extra=[], name='Bancales', help='', strategy='', pedia='',   # the Terrace Farm improvement, renamed in the text file
         texts={'TXT_KEY_CIV5_IMPROVEMENTS_TERRACE_FARM_HELP': 'Bancales can only be built on hills and need no fresh water. Next to a mountain they provide additional food.',
                'TXT_KEY_CIV5_IMPROVEMENTS_TERRACE_FARM_TEXT': "The bancales are the dry-stone terraces that climb the sides of the ravines of La Gomera, holding the thin volcanic soil on slopes too steep for any field. The Gomeros grew barley and beans on them, watered by channels from the springs of the laurel cloud forest of the summit, and the island is still ringed with their walls."}),
    dict(key='ARANFAYBO', people='ELHIERRO', base='BUILDING_SHRINE', cls='BUILDINGCLASS_SHRINE', set="Cost = Cost", extra=[("Building_YieldChanges", "UPDATE Building_YieldChanges SET Yield = 2 WHERE BuildingType = 'BUILDING_CAN1400_ARANFAYBO' AND YieldType = 'YIELD_FAITH'"), ("Building_YieldChanges", "INSERT INTO Building_YieldChanges (BuildingType, YieldType, Yield) VALUES ('BUILDING_CAN1400_ARANFAYBO', 'YIELD_FOOD', 1)")],
         name='Aranfaybo', help='Bimbache replacement for the Shrine. +2 [ICON_PEACE] Faith instead of +1, and +1 [ICON_FOOD] Food.',
         strategy='The Aranfaybo doubles the faith of a Shrine and feeds the city a little: rain is life on El Hierro. Build it early to found a pantheon before the bigger islands.',
         pedia="Aranfaybo was the spirit the Bimbaches invoked for rain: when the mist failed and the Garoe gave no water, the priests climbed to the cave of Asteheyta and called on it, and a pig-like creature was said to appear and bring the clouds. The rituals of the islands were almost all about water."),
    dict(key='GAMBUESA', people='FUERTEVENTURA', base='BUILDING_CIRCUS', cls='BUILDINGCLASS_CIRCUS', set="Cost = Cost", extra=[("Building_ResourceYieldChanges", "INSERT INTO Building_ResourceYieldChanges (BuildingType, ResourceType, YieldType, Yield) VALUES ('BUILDING_CAN1400_GAMBUESA', 'RESOURCE_SHEEP', 'YIELD_PRODUCTION', 1)")], nolocal=True,
         name='Gambuesa', help='Majo replacement for the Circus. Does not require Horses or Ivory nearby, and gives +1 [ICON_PRODUCTION] Production from Sheep.',
         strategy='The Gambuesa gives the two points of happiness of a Circus to any city, not only one with horses or ivory, and makes the goat pastures productive. Build it as the cities grow.',
         pedia="The gambuesa is the communal stone corral of Fuerteventura and Lanzarote, where the free-ranging goats of a whole district were driven once a year to be counted, marked and milked, a custom that outlived the conquest. The Majos were shepherds above all; the goat was food, clothing, leather and wealth."),
    dict(key='MARETA', people='LANZAROTE', base='BUILDING_WATERMILL', cls='BUILDINGCLASS_WATERMILL', set="River = 0, GoldMaintenance = 1", extra=[],
         name='Mareta', help='Majo replacement for the Water Mill. Does not need a river, and costs 1 [ICON_GOLD] maintenance instead of 2.',
         strategy='There are no rivers in the islands, so nobody else can build a Water Mill: the Mareta gives Lanzarote +2 Food and +1 Production in every city, for half the upkeep.',
         pedia="The maretas of Lanzarote are rain cisterns: walled hollows and ponds that catch the run-off of the rare storms on an island with no springs. The Gran Mareta of Teguise watered the capital for centuries; the Majos of Zonzamas lived by the same art of catching every drop."),
]
# donor overrides to remove (unit classes and building classes), so that the stock unit or building returns where no replacement is given
DONOR_CIVS = {'TENERIFE': 'CIVILIZATION_SHOSHONE', 'GRANCANARIA': 'CIVILIZATION_EGYPT', 'LAPALMA': 'CIVILIZATION_ETHIOPIA', 'LAGOMERA': 'CIVILIZATION_INCA',
              'ELHIERRO': 'CIVILIZATION_CELTS', 'FUERTEVENTURA': 'CIVILIZATION_MOROCCO', 'LANZAROTE': 'CIVILIZATION_CARTHAGE'}
UNIT_CHILD_TABLES = [('Unit_AITypes', 'UnitAIType'), ('Unit_Flavors', 'FlavorType, Flavor'), ('Unit_ClassUpgrades', 'UnitClassType'), ('Unit_FreePromotions', 'PromotionType'),
                     ('Unit_Builds', 'BuildType'), ('Unit_ResourceQuantityRequirements', 'ResourceType, Cost'),
                     ('UnitGameplay2DScripts', 'SelectionSound, FirstSelectionSound')]   # a unit without a 2D-scripts row crashes the game when selected
BUILDING_CHILD_TABLES = [('Building_Flavors', 'FlavorType, Flavor'), ('Building_YieldChanges', 'YieldType, Yield'), ('Building_ResourceYieldChanges', 'ResourceType, YieldType, Yield'),
                         ('Building_ClassesNeededInCity', 'BuildingClassType'), ('Building_LocalResourceOrs', 'ResourceType'), ('Building_DomainFreeExperiences', 'DomainType, Experience'),
                         ('Building_YieldModifiers', 'YieldType, Yield'), ('Building_RiverPlotYieldChanges', 'YieldType, Yield')]


def sql():
    out = ["-- Canarias 1400: unique units and buildings of the seven peoples, cloned from the stock rows at load time (generated by text/build_text.py).",
           "-- The donor civilizations' own uniques are unhooked; stock 3D models, techs and upgrade paths are kept.", ""]
    for u in UNITS:
        t = f"UNIT_CAN1400_{u['key']}"
        out += [f"-- {u['name']} ({u['people']}): {u['base']}",
                f"CREATE TEMP TABLE tmp_u AS SELECT * FROM Units WHERE Type = '{u['base']}';",
                f"UPDATE tmp_u SET ID = (SELECT MAX(ID) + 1 FROM Units), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_CAN1400_{u['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {u['set']};",
                "INSERT INTO Units SELECT * FROM tmp_u; DROP TABLE tmp_u;"]
        for table, cols in UNIT_CHILD_TABLES:
            out.append(f"INSERT INTO {table} (UnitType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE UnitType = '{u['base']}';")
        for p in u['promos']: out.append(f"INSERT INTO Unit_FreePromotions (UnitType, PromotionType) VALUES ('{t}', '{p}');")
        out.append("")
    out.append("-- replace the donors' unique units")
    for people, civ in DONOR_CIVS.items(): out.append(f"DELETE FROM Civilization_UnitClassOverrides WHERE CivilizationType = '{civ}';")
    for u in UNITS: out.append(f"INSERT INTO Civilization_UnitClassOverrides (CivilizationType, UnitClassType, UnitType) VALUES ('{DONOR_CIVS[u['people']]}', '{u['cls']}', 'UNIT_CAN1400_{u['key']}');")
    out.append("")
    for b in BUILDINGS:
        if not b['base']: continue
        t = f"BUILDING_CAN1400_{b['key']}"
        out += [f"-- {b['name']} ({b['people']}): {b['base']}",
                f"CREATE TEMP TABLE tmp_b AS SELECT * FROM Buildings WHERE Type = '{b['base']}';",
                f"UPDATE tmp_b SET ID = (SELECT MAX(ID) + 1 FROM Buildings), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_CAN1400_{b['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {b['set']};",
                "INSERT INTO Buildings SELECT * FROM tmp_b; DROP TABLE tmp_b;"]
        for table, cols in BUILDING_CHILD_TABLES:
            if table == 'Building_LocalResourceOrs' and b.get('nolocal'): continue
            out.append(f"INSERT INTO {table} (BuildingType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE BuildingType = '{b['base']}';")
        for table, stmt in b['extra']: out.append(stmt + ';')
        out.append("")
    out.append("-- replace the donors' unique buildings")
    for people, civ in DONOR_CIVS.items(): out.append(f"DELETE FROM Civilization_BuildingClassOverrides WHERE CivilizationType = '{civ}';")
    for b in BUILDINGS:
        if b['base']: out.append(f"INSERT INTO Civilization_BuildingClassOverrides (CivilizationType, BuildingClassType, BuildingType) VALUES ('{DONOR_CIVS[b['people']]}', '{b['cls']}', 'BUILDING_CAN1400_{b['key']}');")
    out += ["-- No horses on the islands: every mounted unit, every unit that needs Horses and the stables move to a technology nobody can research,",
            "-- so that neither the peoples nor the barbarians ever field them.",
            "UPDATE Units SET PrereqTech = 'TECH_ASTRONOMY' WHERE CombatClass = 'UNITCOMBAT_MOUNTED' OR Type IN (SELECT UnitType FROM Unit_ResourceQuantityRequirements WHERE ResourceType = 'RESOURCE_HORSE');",
            "UPDATE Buildings SET PrereqTech = 'TECH_ASTRONOMY' WHERE BuildingClass = 'BUILDINGCLASS_STABLE';", ""]
    return '\n'.join(out)
