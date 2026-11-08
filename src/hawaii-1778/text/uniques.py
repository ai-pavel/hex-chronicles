# Hawaii 1778: the unique units and buildings of the five chiefdoms.  Two kinds: SQL clones of stock rows (base set) and
# renames of the donor civilization's own unique (base None, rename = text keys), e.g. Polynesia's Maori Warrior becomes the Koa.
# Development stops at the end of the Classical era, so nothing here needs a Medieval technology.
# Russian text is RU_UNIQUES in ru.py.

UNITS = [
    dict(key='KOA', people='KONA', base=None, unit_type='UNIT_POLYNESIAN_MAORI_WARRIOR', rename=['TXT_KEY_UNIT_POLYNESIAN_MAORI_WARRIOR'], name='Koa', help='', strategy='', pedia='',
         texts={'TXT_KEY_CIV5_POLYNESIAN_MAORI_WARRIOR_HELP': 'Ancient Era unit that strikes fear into nearby enemies, making them less effective in combat. Only Kona may build it. Replaces the Warrior.',
                'TXT_KEY_CIV5_POLYNESIAN_MAORI_WARRIOR_STRATEGY': 'The Koa works like a Great General in reverse: instead of strengthening friendly units it weakens the enemy units next to it. Build plenty early, the promotion stays with them as they are upgraded.',
                'TXT_KEY_CIV5_POLYNESIAN_MAORI_WARRIOR_TEXT': "The koa were the professional warriors of the Hawaiian chiefs, trained from boyhood in lua and in the spear, the club and the sling, and named after the hard koa wood of their weapons and canoes. The koa of Kona and Kohala, led by Kamehameha's uncles and by the twins Kamanawa and Kameeiamoku, won him the Big Island and then the whole archipelago."}),
    dict(key='OLOHE', people='HILO', base='UNIT_SWORDSMAN', cls='UNITCLASS_SWORDSMAN', set="Combat = Combat - 1", promos=[], noresource=True,
         name='Olohe', help='Hilo replacement for the Swordsman. Needs no [ICON_RES_IRON] Iron (there is none in the islands); 13 [ICON_STRENGTH] Combat Strength instead of 14.',
         strategy='The Olohe is the only Swordsman-class unit that can be built in the islands: a strong Classical melee unit with no iron behind it, and the strongest foot soldier the islands will ever see.',
         pedia="The olohe were the masters of lua, the Hawaiian art of bone-breaking hand-to-hand combat, and the champions who fought the single combats before a battle. Hilo, Puna and Kau were the strongholds of Keoua Kuahuula, Kamehameha's cousin and rival for the Big Island from 1782 until his death at Puukohola in 1791."),
    dict(key='POLOLU', people='MAUI', base='UNIT_SPEARMAN', cls='UNITCLASS_SPEARMAN', set="Combat = Combat + 1", promos=['PROMOTION_SHOCK_1'],
         name='Pololu', help='Maui replacement for the Spearman. +1 [ICON_STRENGTH] Combat Strength and the Shock I promotion: +15% in open terrain.',
         strategy='The Pololu is the Maui Spearman: stronger, and at its best on the open ground of the Maui lowlands and beaches where Kahekili met his enemies. With the cheap upkeep of the chiefdom, field them in numbers.',
         pedia="The pololu was the long spear of the Hawaiian warrior, up to five metres of hard kauila wood, carried by the ranks that met a landing on the beach; the shorter ihe was thrown. Kahekili's armies of Maui were the most feared in the islands and twice held the Big Island's invasions on their beaches."),
    dict(key='PELELEU', people='OAHU', base=None, unit_type='UNIT_CARTHAGINIAN_QUINQUEREME', rename=['TXT_KEY_UNIT_CARTHAGINIAN_QUINQUEREME'], name='Peleleu', help='', strategy='', pedia='',
         texts={'TXT_KEY_UNIT_HELP_CARTHAGINIAN_QUINQUEREME': 'Strong Ancient Era naval unit for melee attacks on ships and cities. Only Oahu may build it. Replaces the Trireme.',
                'TXT_KEY_UNIT_CARTHAGINIAN_QUINQUEREME_STRATEGY': 'The Peleleu is a stronger Trireme, in Combat Strength above all. Like the Trireme it is a melee unit that attacks ships and cities, and it cannot leave the coast.',
                'TXT_KEY_CIV5_CARTHAGINIAN_QUINQUEREME_TEXT': "Peleleu was the name of the great double-hulled war canoes, up to twenty metres long with a fighting platform lashed between the hulls, that carried the armies of the chiefs between the islands. The sheltered bays of Oahu, Waikiki and Kaneohe, held the largest fleets of the archipelago; Kamehameha later built eight hundred peleleu for the conquest of Kauai."}),
    dict(key='MAA', people='KAUAI', base='UNIT_ARCHER', cls='UNITCLASS_ARCHER', set="Cost = 30", promos=['PROMOTION_WITHDRAW_BEFORE_MELEE'],
         name='Maa Slinger', help='Kauai replacement for the Archer. 25% cheaper (30 [ICON_PRODUCTION]) and may withdraw from melee attacks.',
         strategy='The Maa slinger is a cheap skirmisher: it shoots two tiles, falls back when charged and costs little to lose. Screen your spearmen with them and bleed any landing on the beaches of Kauai.',
         pedia="The maa was the Hawaiian sling, a cord of olona fibre with a pocket for a smooth beach stone; slingers opened every battle, and a volley of stones from a ridge was the first thing an invader met. Kauai, the oldest island, is the only one Kamehameha never took: his fleets of 1796 and 1804 were turned back by a storm and by disease."),
]
BUILDINGS = [
    dict(key='KII', people='KONA', base=None, improvement='IMPROVEMENT_MOAI', build='BUILD_MOAI', rename=['TXT_KEY_IMPROVEMENT_MOAI', 'TXT_KEY_BUILD_MOAI'], name='Kii', help='', strategy='', pedia='',
         texts={'TXT_KEY_CIV5_IMPROVEMENTS_MOAI_HELP': 'Kii can only be built on the coast. If built next to another Kii it provides additional [ICON_CULTURE] Culture.',
                'TXT_KEY_BUILD_MOAI_HELP': 'Adds a Kii (+1 [ICON_CULTURE] Culture) to the tile. Create a line of Kii along the coast for additional culture.',
                'TXT_KEY_BUILD_MOAI_REC': 'It will permit the tile to generate [ICON_CULTURE] Culture.',
                'TXT_KEY_CIV5_IMPROVEMENTS_MOAI_TEXT': "The kii were the carved images of the gods: wooden figures with the grimacing mouths and crested heads of Ku and Lono that stood on the platforms of the heiau and in rows along the shore, and the smaller stone kii of the fishing shrines. The rebuilt heiau and the puuhonua of Honaunau on the Kona coast still carry them."}),
    dict(key='PUUHONUA', people='HILO', base='BUILDING_SHRINE', cls='BUILDINGCLASS_SHRINE', set="Happiness = 1", extra=[],
         name='Puuhonua', help='Hilo replacement for the Shrine. +1 [ICON_HAPPINESS_1] Happiness as well as the faith.',
         strategy='The Puuhonua gives the faith of a Shrine and a point of happiness: a place of refuge calms the city. Build it early in every city.',
         pedia="A puuhonua was a place of refuge: a walled sanctuary where a defeated warrior, a breaker of kapu or a fugitive could reach safety and, after rites of absolution, go free. The best preserved is Honaunau on the Kona coast; Hilo and Puna had their own, and the system softened the harshness of the kapu laws."),
    dict(key='HALAU', people='MAUI', base=None, rename=['TXT_KEY_BUILDING_IKANDA', 'TXT_KEY_BUILDING_IKANDA_DESC'], name='Halau', help='', strategy='', pedia='',   # the building's Description is the _DESC key
         texts={'TXT_KEY_BUILDING_IKANDA_HELP': 'Maui replacement for the Barracks. Grants unique promotions to pre-gunpowder melee units: faster movement and greater combat strength.',
                'TXT_KEY_BUILDING_IKANDA_STRATEGY': 'In addition to the experience of the Barracks it replaces, the Halau gives every melee unit trained in the city the promotions of the lua schools: an extra move and more strength. Only Maui may build it.',
                'TXT_KEY_CIV5_BUILDINGS_IKANDA_TEXT': "A halau was the long house of a school: a halau hula for the dancers, a halau waa for the canoe builders, a halau lua where the masters taught the bone-breaking art of lua and the use of the spear, the club and the sling. Kahekili of Maui kept the most feared warriors of the islands, the pahupu, tattooed black over one half of the body."}),
    dict(key='LOKOIA', people='OAHU', base='BUILDING_LIGHTHOUSE', cls='BUILDINGCLASS_LIGHTHOUSE', set="GoldMaintenance = 0",
         extra=[("Building_ResourceYieldChanges", "INSERT INTO Building_ResourceYieldChanges (BuildingType, ResourceType, YieldType, Yield) VALUES ('BUILDING_HI1778_LOKOIA', 'RESOURCE_FISH', 'YIELD_FOOD', 1)")],
         name='Loko Ia', help='Oahu replacement for the Lighthouse. No maintenance, and +1 [ICON_FOOD] Food from Fish in addition to the +1 Food on ocean tiles.',
         strategy='The Loko Ia makes the sea feed Oahu: every coastal city should have one, and with the free harbour of the chiefdom the fish tiles become the best tiles on the map.',
         pedia="The loko ia were the Hawaiian fishponds: stone walls built across a bay or reef flat with sluice gates (makaha) that let fry in and kept the grown fish, an aquaculture system unique in Polynesia. Oahu had the largest number; the walls of the ponds of Pearl Harbor, Kaneohe Bay and Waikiki fed the chiefs of the island."),
    dict(key='LOIKALO', people='KAUAI', base='BUILDING_GRANARY', cls='BUILDINGCLASS_GRANARY', set="Cost = Cost",
         extra=[("Building_YieldChanges", "UPDATE Building_YieldChanges SET Yield = 3 WHERE BuildingType = 'BUILDING_HI1778_LOIKALO' AND YieldType = 'YIELD_FOOD'"),
                ("Building_ResourceYieldChanges", "INSERT INTO Building_ResourceYieldChanges (BuildingType, ResourceType, YieldType, Yield) VALUES ('BUILDING_HI1778_LOIKALO', 'RESOURCE_SUGAR', 'YIELD_FOOD', 1)")],
         name='Loi Kalo', help='Kauai replacement for the Granary. +3 [ICON_FOOD] Food instead of +2, and +1 [ICON_FOOD] Food from Sugar as well as Wheat, Bananas and Deer.',
         strategy='The Loi Kalo feeds a city faster than a Granary; with the taro valleys (Bananas) and cane of Kauai it is the best growth building in the islands. Build it first.',
         pedia="Loi kalo are the irrigated taro terraces of the Hawaiian valleys, fed by ditches (auwai) from the streams; the Hanalei and Wailua valleys of Kauai were among the richest. Taro, pounded into poi, was the staple of the islands, and the legendary menehune were said to have built the great ditch of Kikiaola at Waimea in one night."),
]
DONOR_CIVS = {'KONA': 'CIVILIZATION_POLYNESIA', 'HILO': 'CIVILIZATION_JAPAN', 'MAUI': 'CIVILIZATION_ZULU', 'OAHU': 'CIVILIZATION_CARTHAGE', 'KAUAI': 'CIVILIZATION_ETHIOPIA'}
# donors whose own uniques are unhooked entirely (the others keep theirs under new names)
DROP_UNIT_OVERRIDES = ['CIVILIZATION_JAPAN', 'CIVILIZATION_ETHIOPIA', 'CIVILIZATION_ZULU']   # the Zulu Impi needs Civil Service, which is beyond the cap
DROP_BUILDING_OVERRIDES = ['CIVILIZATION_ETHIOPIA']
UNIT_CHILD_TABLES = [('Unit_AITypes', 'UnitAIType'), ('Unit_Flavors', 'FlavorType, Flavor'), ('Unit_ClassUpgrades', 'UnitClassType'), ('Unit_FreePromotions', 'PromotionType'),
                     ('Unit_Builds', 'BuildType'), ('Unit_ResourceQuantityRequirements', 'ResourceType, Cost'), ('UnitGameplay2DScripts', 'SelectionSound, FirstSelectionSound')]
BUILDING_CHILD_TABLES = [('Building_Flavors', 'FlavorType, Flavor'), ('Building_YieldChanges', 'YieldType, Yield'), ('Building_ResourceYieldChanges', 'ResourceType, YieldType, Yield'),
                         ('Building_ClassesNeededInCity', 'BuildingClassType'), ('Building_LocalResourceOrs', 'ResourceType'), ('Building_DomainFreeExperiences', 'DomainType, Experience'),
                         ('Building_YieldModifiers', 'YieldType, Yield'), ('Building_RiverPlotYieldChanges', 'YieldType, Yield'), ('Building_SeaPlotYieldChanges', 'YieldType, Yield'),
                         ('Building_SeaResourceYieldChanges', 'YieldType, Yield')]


def sql():
    out = ["-- Hawaii 1778: unique units and buildings of the five chiefdoms, cloned from the stock rows at load time (generated by text/build_text.py).",
           "-- Japan's and Ethiopia's uniques are unhooked; Polynesia, Zulu and Carthage keep theirs under Hawaiian names (text only).", ""]
    for u in UNITS:
        if not u['base']: continue
        t = f"UNIT_HI1778_{u['key']}"
        out += [f"-- {u['name']} ({u['people']}): {u['base']}",
                f"CREATE TEMP TABLE tmp_u AS SELECT * FROM Units WHERE Type = '{u['base']}';",
                f"UPDATE tmp_u SET ID = (SELECT MAX(ID) + 1 FROM Units), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_HI1778_{u['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {u['set']};",
                "INSERT INTO Units SELECT * FROM tmp_u; DROP TABLE tmp_u;"]
        for table, cols in UNIT_CHILD_TABLES:
            if table == 'Unit_ResourceQuantityRequirements' and u.get('noresource'): continue
            out.append(f"INSERT INTO {table} (UnitType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE UnitType = '{u['base']}';")
        for p in u['promos']: out.append(f"INSERT INTO Unit_FreePromotions (UnitType, PromotionType) VALUES ('{t}', '{p}');")
        out.append("")
    out.append("-- replace the donors' unique units")
    for civ in DROP_UNIT_OVERRIDES: out.append(f"DELETE FROM Civilization_UnitClassOverrides WHERE CivilizationType = '{civ}';")
    for u in UNITS:
        if u['base']: out.append(f"INSERT INTO Civilization_UnitClassOverrides (CivilizationType, UnitClassType, UnitType) VALUES ('{DONOR_CIVS[u['people']]}', '{u['cls']}', 'UNIT_HI1778_{u['key']}');")
    out.append("")
    for b in BUILDINGS:
        if not b['base']: continue
        t = f"BUILDING_HI1778_{b['key']}"
        out += [f"-- {b['name']} ({b['people']}): {b['base']}",
                f"CREATE TEMP TABLE tmp_b AS SELECT * FROM Buildings WHERE Type = '{b['base']}';",
                f"UPDATE tmp_b SET ID = (SELECT MAX(ID) + 1 FROM Buildings), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_HI1778_{b['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {b['set']};",
                "INSERT INTO Buildings SELECT * FROM tmp_b; DROP TABLE tmp_b;"]
        for table, cols in BUILDING_CHILD_TABLES:
            out.append(f"INSERT INTO {table} (BuildingType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE BuildingType = '{b['base']}';")
        for table, stmt in b['extra']: out.append(stmt + ';')
        out.append("")
    out.append("-- replace the donors' unique buildings")
    for civ in DROP_BUILDING_OVERRIDES: out.append(f"DELETE FROM Civilization_BuildingClassOverrides WHERE CivilizationType = '{civ}';")
    for b in BUILDINGS:
        if b['base']: out.append(f"INSERT INTO Civilization_BuildingClassOverrides (CivilizationType, BuildingClassType, BuildingType) VALUES ('{DONOR_CIVS[b['people']]}', '{b['cls']}', 'BUILDING_HI1778_{b['key']}');")
    out += ["", "-- No horses in the islands: every mounted unit, every unit that needs Horses and the stables move to a technology nobody can research,",
            "-- so that neither the chiefdoms nor the barbarians ever field them.",
            "UPDATE Units SET PrereqTech = 'TECH_ASTRONOMY' WHERE CombatClass = 'UNITCOMBAT_MOUNTED' OR Type IN (SELECT UnitType FROM Unit_ResourceQuantityRequirements WHERE ResourceType = 'RESOURCE_HORSE');",
            "UPDATE Buildings SET PrereqTech = 'TECH_ASTRONOMY' WHERE BuildingClass = 'BUILDINGCLASS_STABLE';", ""]
    return '\n'.join(out)
