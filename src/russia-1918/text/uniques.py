# Russia 1918: the unique units and buildings of the six sides (replacing the donor civilizations' own: Cossack and Krepost,
# Panzer and Hanse, Pathfinder and Comanche Riders, Longbowman and Ship of the Line, Mehal Sefari and Stele, Winged Hussar and
# Ducal Stable), the abilities whose stock effects are dead in this scenario, and the SQL that does it at mod load, with the
# English text.  Russian text is RU_UNIQUES in ru.py; the ability texts are in build_text.py and ru.py with the rest of each side.
# Each unit/building is cloned from a stock row buildable with the scenario's techs (through the Industrial era plus Flight,
# Combustion, Replaceable Parts and Refrigeration: no Cavalry, no Riflemen, no Ironclads) and keeps the stock 3D model, icon,
# tech and upgrade path; only stats, promotions, yields and text change.  The event units stay the stock types the events name;
# only what a side builds itself is its unique.

# key, side, base unit, unit class, SQL column changes, free promotions, EN name / help / strategy / civilopedia
UNITS = [
    dict(key='TACHANKA', side='RED', base='UNIT_GATLINGGUN', cls='UNITCLASS_GATLINGGUN', set="Moves = 3", promos=[],
         name='Tachanka', help='Soviet replacement for the Gatling Gun. 3 [ICON_MOVES] Movement instead of 2.',
         strategy='The Tachanka is a machine gun on a horse cart: as strong as a Gatling Gun and a third faster. Bring it up behind the cavalry and the infantry to hold what they take.',
         pedia="The tachanka was a light sprung cart drawn by two to four horses, with a Maxim machine gun mounted to fire over the back. It became the emblem of the mobile war in the steppe: Nestor Makhno's insurgent army in southern Ukraine made it famous, and the Red cavalry took it up in numbers, Budyonny's First Cavalry Army above all. A tachanka could keep pace with the horsemen, wheel round and open fire in moments."),
    dict(key='COLOURED', side='SOUTH', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = 54, Cost = 352", promos=['PROMOTION_SHOCK_1'],
         name='Coloured Regiment', help='White South replacement for the Great War Infantry. 54 [ICON_STRENGTH] Combat Strength instead of 50 and the Shock I promotion; 10% more expensive.',
         strategy='The Coloured Regiments are the shock troops of the Volunteer Army: stronger and dearer than ordinary infantry. Lead every attack with them and leave the line to the Cossacks and the mobilised.',
         pedia="The Kornilov, Markov, Drozdovsky and Alekseev regiments of the Volunteer Army were called the coloured units after the distinctive colours of their caps and shoulder boards. They were raised in 1917 and 1918 largely from officers serving in the ranks: the Kornilov Shock Regiment dated from the summer of 1917, Markov's Officer Regiment fought through the Ice March of 1918, and Drozdovsky's brigade marched some 1,200 km from the Romanian front to the Don that spring. Expanded into divisions, they led the 1919 drive on Moscow, and the Kornilov division took Oryol in October."),
    dict(key='ARMOURED_TRAIN', side='SIB', base='UNIT_ARTILLERY', cls='UNITCLASS_ARTILLERY', set="Combat = 30, Moves = 3, Cost = 275", promos=[],
         name='Armoured Train', help='Siberian replacement for the Artillery. 30 [ICON_STRENGTH] Combat Strength instead of 21 and 3 [ICON_MOVES] Movement instead of 2; 10% more expensive.',
         strategy='The Armoured Train hits as hard as Artillery, defends itself better and moves faster. Use it to shell the enemy from behind the infantry, and move it along the railway to where the front breaks.',
         pedia="In May 1918 the Czechoslovak Legion, some forty thousand former Austro-Hungarian soldiers strung out along the Trans-Siberian on their way to Vladivostok, rose against the Soviets and within weeks held the railway from the Volga to the Pacific. Its war was fought along the line, and its spearheads were armoured trains: some improvised in the railway workshops from flatcars, sandbags and boiler plate, some captured from the Red Guards. The best known, Orlik, had begun life in 1916 as the Russian army's Zaamurets."),
    dict(key='MARK_V', side='NORTH', base='UNIT_WWI_TANK', cls='UNITCLASS_WWI_TANK', set="Combat = 65, Moves = 3", promos=[],
         name='Mark V Tank', help='Northern Region replacement for the Landship. 65 [ICON_STRENGTH] Combat Strength instead of 60, but 3 [ICON_MOVES] Movement instead of 4.',
         strategy='The Mark V is a slow, heavy tank that breaks a line the infantry cannot. Send it against entrenched positions and towns, with infantry beside it.',
         pedia="The Mark V, the last of the British rhomboid heavy tanks of the World War, entered service in 1918; it was the first that one driver could steer alone. In 1919 Britain shipped tanks with instructors to the White armies: most went to the south through Novorossiysk, and a small detachment went to Yudenich's Northwestern Army in Estonia, whose tanks joined its October advance on Petrograd."),
    dict(key='SERDIUK', side='UKR', base='UNIT_GREAT_WAR_INFANTRY', cls='UNITCLASS_GREAT_WAR_INFANTRY', set="Combat = 52, Cost = 340", promos=['PROMOTION_COVER_1'],
         name='Serdiuk Division', help='Ukrainian replacement for the Great War Infantry. 52 [ICON_STRENGTH] Combat Strength instead of 50 and the Cover I promotion (+25% defence against ranged attacks); a little more expensive (340 [ICON_PRODUCTION]).',
         strategy='The Serdiuk Division is a guard infantry that holds well under shelling. Put it in the cities and on the lines the enemy artillery will hit first.',
         pedia="The Serdiuk Division was the guard of the Hetman, raised in the summer of 1918 from the sons of land-owning peasants of the Left-Bank governorates and named after the Cossack guard of the old hetmans. It was one of the best equipped formations of the Ukrainian State, some five thousand strong. When the Directory rose against the Hetman in November 1918, much of it went over to the insurgents."),
    dict(key='UHLAN', side='POL', base='UNIT_LANCER', cls='UNITCLASS_LANCER', set="Combat = 32, Cost = 200", promos=[],
         name='Uhlans', help='Polish replacement for the Lancer. 32 [ICON_STRENGTH] Combat Strength instead of 25; a little more expensive (200 [ICON_PRODUCTION]).',
         strategy='The Uhlans are the Polish cavalry: fast and strong for horsemen, but no match for entrenched infantry. Use them to raid, to pursue and to hit the enemy where the line is thin.',
         pedia="The uhlan regiments of the reborn Polish Army were raised from 1918 from the Legions, from Polish units of the three partitioning armies and from volunteers, and they kept the lance and the traditions of the Polish cavalry. In the war of 1920 they fought the Soviet cavalry on its own terms: at Komarow on 31 August 1920 Polish cavalry defeated Budyonny's First Cavalry Army in one of the last great cavalry battles in Europe."),
]
# key, side, base building, building class, SQL column changes, extra rows (table, statement) after cloning, EN text
BUILDINGS = [
    dict(key='VOENKOMAT', side='RED', base='BUILDING_BARRACKS', cls='BUILDINGCLASS_BARRACKS', set="GoldMaintenance = 0",
         extra=[("Building_DomainProductionModifiers", "INSERT INTO Building_DomainProductionModifiers (BuildingType, DomainType, Modifier) VALUES ('BUILDING_RUS1918_VOENKOMAT', 'DOMAIN_LAND', 15)")],
         name='Military Commissariat', help='Soviet replacement for the Barracks. +15% [ICON_PRODUCTION] Production of land units as well, and no maintenance.',
         strategy='The Military Commissariat trains new units like Barracks and raises them faster. Build it in every city that sends men to the front.',
         pedia="A decree of the Council of People's Commissars of 8 April 1918 set up military commissariats in every volost, uezd, governorate and military district. They registered the men liable for service, carried out the mobilisations that followed the decree on compulsory service of 29 May 1918, and turned the volunteer Red Army into a conscript army of millions."),
    dict(key='STANITSA', side='SOUTH', base='BUILDING_STABLE', cls='BUILDINGCLASS_STABLE', set="GoldMaintenance = 0",
         extra=[("Building_UnitCombatFreeExperiences", "INSERT INTO Building_UnitCombatFreeExperiences (BuildingType, UnitCombatType, Experience) VALUES ('BUILDING_RUS1918_STANITSA', 'UNITCOMBAT_MOUNTED', 15)")],
         name='Cossack Stanitsa', help='White South replacement for the Stable. Mounted units built here get +15 XP, and no maintenance.',
         strategy='The Cossack Stanitsa trains horsemen who start their war already promoted. Build it in the Don and Kuban towns with horses nearby.',
         pedia="The stanitsa was the self-governing village of the Cossack hosts, whose men owed the state military service with their own horse and equipment in exchange for their land. The Don and Kuban stanitsas rose against the Soviets in the spring of 1918 and gave the White South the bulk of its cavalry; Krasnov's Don Army and the Kuban regiments fought beside the Volunteers to the end of the war."),
    dict(key='RAILWAY_WORKSHOPS', side='SIB', base='BUILDING_WORKSHOP', cls='BUILDINGCLASS_WORKSHOP', set="GoldMaintenance = 1",
         extra=[("Building_YieldChanges", "UPDATE Building_YieldChanges SET Yield = 3 WHERE BuildingType = 'BUILDING_RUS1918_RAILWAY_WORKSHOPS' AND YieldType = 'YIELD_PRODUCTION'")],
         name='Railway Workshops', help='Siberian replacement for the Workshop. +3 [ICON_PRODUCTION] Production instead of +2, and 1 [ICON_GOLD] maintenance instead of 2.',
         strategy='The Railway Workshops are the industry of Siberia. Build them in the towns along the Trans-Siberian.',
         pedia="Along the Trans-Siberian the railway workshops at Omsk, Krasnoyarsk, Irkutsk and the other division points were the largest industrial plants east of the Urals. In 1918 and 1919 they kept the locomotives running, repaired the rolling stock and fitted out the armoured trains of the Czechoslovaks and the Siberian army."),
    dict(key='SUPPLY_BASE', side='NORTH', base='BUILDING_SEAPORT', cls='BUILDINGCLASS_SEAPORT', set="Cost = 200",
         extra=[("Building_YieldChanges", "INSERT INTO Building_YieldChanges (BuildingType, YieldType, Yield) VALUES ('BUILDING_RUS1918_SUPPLY_BASE', 'YIELD_PRODUCTION', 2)")],
         name='Allied Supply Base', help='Northern Region replacement for the Seaport. +2 [ICON_PRODUCTION] Production as well, and cheaper (200 [ICON_PRODUCTION] instead of 250).',
         strategy='The Allied Supply Base turns a harbour into a depot for Allied munitions. Build it in Arkhangelsk and Murmansk first.',
         pedia="The Allies first came to Murmansk and Arkhangelsk to guard the war stores they had shipped to Russia since 1914, a great mass of munitions, metal and equipment piled on the quays. From 1918 the two ports became the bases of the Allied intervention in the north, and through them came the guns, uniforms and food of the Northern Region's army until the Allies left in the autumn of 1919."),
    dict(key='SUGAR_MILL', side='UKR', base='BUILDING_WINDMILL', cls='BUILDINGCLASS_WINDMILL', set="GoldMaintenance = 2",
         extra=[("Building_YieldChanges", "INSERT INTO Building_YieldChanges (BuildingType, YieldType, Yield) VALUES ('BUILDING_RUS1918_SUGAR_MILL', 'YIELD_GOLD', 2)")],
         name='Sugar Refinery', help='Ukrainian replacement for the Windmill. +2 [ICON_GOLD] Gold as well.',
         strategy='The Sugar Refinery adds gold to the production of a Windmill. Build it in the farming towns of the Right Bank and the Left Bank.',
         pedia="Before the World War the sugar mills of the Ukrainian governorates, about two hundred of them on the beet fields of Kiev, Podolia, Volhynia, Kharkov and Poltava, made some four fifths of the sugar of the Russian Empire. The industry made the fortunes of the Tereshchenko, Brodsky and Kharitonenko families and was one of the riches of the Ukrainian State."),
    dict(key='OFFICER_SCHOOL', side='POL', base='BUILDING_MILITARY_ACADEMY', cls='BUILDINGCLASS_MILITARY_ACADEMY', set="Cost = 200, GoldMaintenance = 0",
         extra=[("Building_ClassesNeededInCity", "DELETE FROM Building_ClassesNeededInCity WHERE BuildingType = 'BUILDING_RUS1918_OFFICER_SCHOOL'")],
         name='Officer School', help='Polish replacement for the Military Academy. Needs no Armory, costs a third less (200 [ICON_PRODUCTION]) and has no maintenance.',
         strategy='The Officer School gives new units the experience of a Military Academy in any city. Build it early where the army is raised.',
         pedia="The Polish Army of 1918 had to make one officer corps out of men of the Legions and of the Austrian, Russian and German armies, with different drill, languages of command and habits. Officer schools opened in Warsaw and other cities from the first months of independence, and short courses turned out the thousands of junior officers the army needed for the wars of 1919 and 1920."),
]
# the donor civilizations, whose own uniques are unhooked
DONOR_CIVS = {'RED': 'CIVILIZATION_RUSSIA', 'SOUTH': 'CIVILIZATION_GERMANY', 'SIB': 'CIVILIZATION_SHOSHONE', 'NORTH': 'CIVILIZATION_ENGLAND',
              'UKR': 'CIVILIZATION_ETHIOPIA', 'POL': 'CIVILIZATION_POLAND'}
# abilities whose stock effects are dead in this scenario (no city is ever founded, the era never changes, spies come only with
# era changes): the effect is replaced, the text is in build_text.py / ru.py
TRAITS = [
    ("TRAIT_GREAT_EXPANSE", "ExtraFoundedCityTerritoryClaimRange = 0, MoveFriendlyWoodsAsRoad = 1"),   # Siberia: founded cities' territory -> taiga movement
    ("TRAIT_OCEAN_MOVEMENT", "ExtraSpies = 0, CityStateFriendshipModifier = 100"),                       # Northern Region: extra spy -> city-state influence
    ("TRAIT_SOLIDARITY", "FreeSocialPoliciesPerEra = 0, GreatGeneralRateModifier = 50, GreatGeneralExtraBonus = 15"),   # Poland: policy per era -> Great Generals
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
    out = ["-- Russia 1918: unique units and buildings of the six sides, cloned from the stock rows at load time, and the abilities whose",
           "-- stock effects are dead in the scenario (generated by text/build_text.py from text/uniques.py).",
           "-- The donor civilizations' own uniques are unhooked; stock 3D models, icons, techs and upgrade paths are kept.", ""]
    for u in UNITS:
        t = f"UNIT_RUS1918_{u['key']}"
        out += [f"-- {u['name']} ({u['side']}): {u['base']}",
                f"CREATE TEMP TABLE tmp_u AS SELECT * FROM Units WHERE Type = '{u['base']}';",
                f"UPDATE tmp_u SET ID = (SELECT MAX(ID) + 1 FROM Units), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_RUS1918_{u['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {u['set']};",
                "INSERT INTO Units SELECT * FROM tmp_u; DROP TABLE tmp_u;"]
        for table, cols in UNIT_CHILD_TABLES:
            out.append(f"INSERT INTO {table} (UnitType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE UnitType = '{u['base']}';")
        for p in u['promos']: out.append(f"INSERT INTO Unit_FreePromotions (UnitType, PromotionType) VALUES ('{t}', '{p}');")
        out.append("")
    out.append("-- replace the donors' unique units")
    for civ in DONOR_CIVS.values(): out.append(f"DELETE FROM Civilization_UnitClassOverrides WHERE CivilizationType = '{civ}';")
    for u in UNITS: out.append(f"INSERT INTO Civilization_UnitClassOverrides (CivilizationType, UnitClassType, UnitType) VALUES ('{DONOR_CIVS[u['side']]}', '{u['cls']}', 'UNIT_RUS1918_{u['key']}');")
    out.append("")
    for b in BUILDINGS:
        t = f"BUILDING_RUS1918_{b['key']}"
        out += [f"-- {b['name']} ({b['side']}): {b['base']}",
                f"CREATE TEMP TABLE tmp_b AS SELECT * FROM Buildings WHERE Type = '{b['base']}';",
                f"UPDATE tmp_b SET ID = (SELECT MAX(ID) + 1 FROM Buildings), Type = '{t}', Description = 'TXT_KEY_{t}', Civilopedia = 'TXT_KEY_CIV5_RUS1918_{b['key']}_TEXT', Strategy = 'TXT_KEY_{t}_STRATEGY', Help = 'TXT_KEY_{t}_HELP', {b['set']};",
                "INSERT INTO Buildings SELECT * FROM tmp_b; DROP TABLE tmp_b;"]
        for table, cols in BUILDING_CHILD_TABLES:
            out.append(f"INSERT INTO {table} (BuildingType, {cols}) SELECT '{t}', {cols} FROM {table} WHERE BuildingType = '{b['base']}';")
        for table, stmt in b['extra']: out.append(stmt + ';')
        out.append("")
    out.append("-- replace the donors' unique buildings")
    for civ in DONOR_CIVS.values(): out.append(f"DELETE FROM Civilization_BuildingClassOverrides WHERE CivilizationType = '{civ}';")
    for b in BUILDINGS: out.append(f"INSERT INTO Civilization_BuildingClassOverrides (CivilizationType, BuildingClassType, BuildingType) VALUES ('{DONOR_CIVS[b['side']]}', '{b['cls']}', 'BUILDING_RUS1918_{b['key']}');")
    out.append("")
    out.append("-- abilities: the dead stock effects replaced")
    for trait, sets in TRAITS: out.append(f"UPDATE Traits SET {sets} WHERE Type = '{trait}';")
    out.append("")
    return '\n'.join(out)
