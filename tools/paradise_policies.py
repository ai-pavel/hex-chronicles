"""The social policy tree of Firaxis' Paradise Found (Polynesia) scenario, for reuse by the island scenarios.

Three branches of five policies each (Ceremony, The Arts, Honor) replace the nine stock branches, plus two of our own made from the
stock Piety and Commerce policies (FAITH, TRADE); the three Brave New World ideologies and their tenets stay (the Industrial era
is unreachable in those scenarios anyway).  The mechanics are the scenario's own, the names, help and civilopedia text are the
caller's (EN + RU), the icons are the Polynesia DLC's and the stock policy atlases.  sql(prefix) writes the database changes (run
after the mod's rules, before its text); text_rows(prefix, names, lang, pedia) gives the text file rows; BRANCHES lists the
(key, box texture) pairs for build_policy_screen.build.  VARIANTS swaps the effect of a policy for one scenario (Canarias has no
city-states and no Moai).

Effects (unchanged from the scenario):
  CEREMONY  opener: -33% unhappiness from population in the capital.  Tapu: policy cost -10%.  Powhiri: gold gifts to
            city-states +25% influence.  Surfing: +1 happiness per city.  Kava: +10 happiness.  Luau: +2 happiness per luxury type.
  THE_ARTS  opener: +2 culture from Monuments and Temples.  Hula: golden ages need 25% less happiness.  Rongo-Rongo: +100%
            science from Libraries and Observatories.  Tapa Cloth: +2 culture per city.  Stone Carving: +1 culture from culture
            improvements (Moai).  Tiki: 50% of excess happiness becomes culture.
  HONOR     opener: +15 XP for new land units.  Poi: +1 move embarked.  Ariki: great generals +100%.  Mana: great people
            +100%.  Kahuna Healing: melee units get Medic.  Haka: culture from kills x3.
  FAITH     (stock Piety) opener: Shrines and Temples built twice as fast.  +1 faith from Shrines and Temples; faith purchases
            -20%; Temples +25% gold; second religion's pantheon; a Reformation belief.
  TRADE     (stock Commerce, Classical era) opener: +25% gold in the capital.  +2 gold from land trade routes and road upkeep
            -50%; +1 gold from Trading Posts (instead of the Landsknechts, who need an unreachable era); Great Merchants +25% and
            double trade missions; purchases -25% and +1 science from Mints and Markets; +2 happiness per luxury.
"""
STOCK_BRANCHES = ['TRADITION', 'LIBERTY', 'HONOR', 'PIETY', 'PATRONAGE', 'AESTHETICS', 'COMMERCE', 'EXPLORATION', 'RATIONALISM']
# key, stock texture for the screen box
# key, box texture for the screen: Paradise Found's own (Polynesia DLC) for its three, stock Piety and Commerce for ours
BRANCHES = [('CEREMONY', 'Polynesia_PolicyBranch_Ceremony.dds'), ('THE_ARTS', 'Polynesia_PolicyBranch_TheArts.dds'), ('HONOR', 'Polynesia_PolicyBranch_Honor.dds'), ('FAITH', 'SocialPoliciesPiety.dds'), ('TRADE', 'SocialPoliciesCommerce.dds')]
BRANCH_ERA = {'TRADE': 'ERA_CLASSICAL'}
# reachable wonders that the stock tree tied to a branch; the rest lose their branch
WONDER_BRANCH = {'BUILDING_HANGING_GARDEN': 'CEREMONY', 'BUILDING_PYRAMID': 'THE_ARTS', 'BUILDING_STATUE_ZEUS': 'HONOR', 'BUILDING_MOSQUE_OF_DJENNE': 'FAITH', 'BUILDING_BIG_BEN': 'TRADE'}
# key, branch (None = the branch opener), grid x, y, columns to set, (atlas, achieved atlas, portrait index)
POLICIES = [
    ('CEREMONY', None, 0, 0, {'CapitalUnhappinessMod': -33}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 0)),
    ('TAPU', 'CEREMONY', 2, 1, {'PolicyCostModifier': -10}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 10)),
    ('POWHIRI', 'CEREMONY', 4, 1, {'MinorGoldFriendshipMod': 25}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 40)),
    ('SURFING', 'CEREMONY', 1, 2, {'ExtraHappinessPerCity': 1}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 8)),
    ('KAVA', 'CEREMONY', 3, 2, {'ExtraHappiness': 10}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 3)),
    ('LUAU', 'CEREMONY', 5, 2, {'ExtraHappinessPerLuxury': 2}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 4)),
    ('THE_ARTS', None, 0, 0, {}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 0)),
    ('HULA', 'THE_ARTS', 3, 1, {'GoldenAgeMeterMod': -25}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 1)),
    ('TIKI', 'THE_ARTS', 5, 2, {'HappinessToCulture': 50}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 11)),
    ('RONGO', 'THE_ARTS', 1, 1, {}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 6)),
    ('TAPACLOTH', 'THE_ARTS', 3, 2, {'CulturePerCity': 2}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 9)),
    ('STONECARVING', 'THE_ARTS', 5, 1, {'CultureImprovementChange': 1}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 7)),
    ('HONOR', None, 0, 0, {}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 0)),
    ('POI', 'HONOR', 2, 1, {'EmbarkedExtraMoves': 1}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 5)),
    ('ARIKI', 'HONOR', 2, 2, {'GreatGeneralRateModifier': 100}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 19)),
    ('HEALING', 'HONOR', 4, 3, {}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 2)),
    ('HAKA', 'HONOR', 2, 3, {'CultureFromKills': 300}, ('POLYNESIA_POLICY_ATLAS', 'POLYNESIA_POLICY_A_ATLAS', 0)),
    ('MANA', 'HONOR', 4, 2, {'GreatPeopleRateModifier': 100}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 46)),
    ('FAITH', None, 0, 0, {}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 42)),
    ('SHRINES', 'FAITH', 2, 1, {}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 43)),
    ('MANDATE', 'FAITH', 5, 1, {'FaithCostModifier': -20}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 44)),
    ('THEOCRACY', 'FAITH', 1, 2, {}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 45)),
    ('TOLERANCE', 'FAITH', 3, 2, {'SecondReligionPantheon': 1}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 47)),
    ('REFORMATION', 'FAITH', 3, 3, {'AddReformationBelief': 1, 'OneShot': 1}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 46)),
    ('TRADE', None, 0, 0, {}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 6)),
    ('ROUTES', 'TRADE', 2, 1, {'RouteGoldMaintenanceMod': -50, 'LandTradeRouteGoldChange': 200}, ('POLICY_ATLAS_EXP2', 'POLICY_A_ATLAS_EXP2', 9)),
    ('POSTS', 'TRADE', 4, 1, {}, ('EXPANSIONPATCH_POLICY_ATLAS', 'EXPANSIONPATCH_POLICY_ACHIEVED_ATLAS', 0)),
    ('MERCHANTS', 'TRADE', 2, 2, {'EmbarkedExtraMoves': 1, 'GreatMerchantRateModifier': 25, 'TradeMissionGoldModifier': 100}, ('POLICY_ATLAS_EXP2', 'POLICY_A_ATLAS_EXP2', 3)),
    ('MARKETS', 'TRADE', 4, 2, {}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 9)),
    ('LUXURIES', 'TRADE', 4, 3, {'ExtraHappinessPerLuxury': 2}, ('POLICY_ATLAS', 'POLICY_A_ATLAS', 11)),
]
# rows in the policy child tables (table, columns) that carry the effects the Policies columns cannot
ROWS = {
    'HEALING': [('Policy_FreePromotions', {'PromotionType': 'PROMOTION_MEDIC'})],
    'HONOR': [('Policy_UnitCombatFreeExperiences', {'UnitCombatType': f'UNITCOMBAT_{uc}', 'FreeExperience': 15}) for uc in ('MELEE', 'RECON', 'ARCHER', 'SIEGE', 'GUN')],
    'THE_ARTS': [('Policy_BuildingClassCultureChanges', {'BuildingClassType': f'BUILDINGCLASS_{bc}', 'CultureChange': 2}) for bc in ('MONUMENT', 'TEMPLE')],
    'RONGO': [('Policy_BuildingClassYieldModifiers', {'BuildingClassType': f'BUILDINGCLASS_{bc}', 'YieldType': 'YIELD_SCIENCE', 'YieldMod': 100}) for bc in ('LIBRARY', 'OBSERVATORY')],
    'FAITH': [('Policy_BuildingClassProductionModifiers', {'BuildingClassType': f'BUILDINGCLASS_{bc}', 'ProductionModifier': 100}) for bc in ('SHRINE', 'TEMPLE')],
    'SHRINES': [('Policy_BuildingClassYieldChanges', {'BuildingClassType': f'BUILDINGCLASS_{bc}', 'YieldType': 'YIELD_FAITH', 'YieldChange': 1}) for bc in ('SHRINE', 'TEMPLE')],
    'THEOCRACY': [('Policy_BuildingClassYieldModifiers', {'BuildingClassType': 'BUILDINGCLASS_TEMPLE', 'YieldType': 'YIELD_GOLD', 'YieldMod': 25})],
    'TRADE': [('Policy_CapitalYieldModifiers', {'YieldType': 'YIELD_GOLD', 'Yield': 25})],
    'POSTS': [('Policy_ImprovementYieldChanges', {'ImprovementType': 'IMPROVEMENT_TRADING_POST', 'YieldType': 'YIELD_GOLD', 'Yield': 1})],
    'MARKETS': [('Policy_HurryModifiers', {'HurryType': 'HURRY_GOLD', 'HurryCostModifier': -25})] +
               [('Policy_BuildingClassYieldChanges', {'BuildingClassType': f'BUILDINGCLASS_{bc}', 'YieldType': 'YIELD_SCIENCE', 'YieldChange': 1}) for bc in ('MINT', 'MARKET')],
}
# per-scenario replacements: key -> (columns, rows, (EN help, RU help)); the stock effect is dead there
VARIANTS = {
    'CAN1400': {
        'POWHIRI': ({}, [('Policy_CityYieldChanges', {'YieldType': 'YIELD_PRODUCTION', 'Yield': 1})],
                    ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_PRODUCTION] Production in every City.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_PRODUCTION] производства в каждом городе.")),
        'STONECARVING': ({}, [('Policy_BuildingClassCultureChanges', {'BuildingClassType': 'BUILDINGCLASS_PALACE', 'CultureChange': 3})],
                         ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+3 [ICON_CULTURE] Culture in the [ICON_CAPITAL] Capital.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+3 [ICON_CULTURE] культуры в [ICON_CAPITAL] столице.")),
    },
}
PREREQS = [('ARIKI', 'POI'), ('MANA', 'POI'), ('HEALING', 'ARIKI'), ('HEALING', 'MANA'), ('HAKA', 'ARIKI'), ('SURFING', 'TAPU'), ('KAVA', 'TAPU'), ('KAVA', 'POWHIRI'),
           ('LUAU', 'POWHIRI'), ('TAPACLOTH', 'HULA'), ('TIKI', 'STONECARVING'),
           ('THEOCRACY', 'SHRINES'), ('TOLERANCE', 'SHRINES'), ('REFORMATION', 'TOLERANCE'), ('MERCHANTS', 'ROUTES'), ('MARKETS', 'POSTS'), ('LUXURIES', 'MARKETS'), ('LUXURIES', 'MERCHANTS')]
FLAVORS = {'CEREMONY': [('HAPPINESS', 20)], 'TAPU': [('CULTURE', 20)], 'POWHIRI': [('DIPLOMACY', 20)], 'SURFING': [('HAPPINESS', 20)], 'KAVA': [('HAPPINESS', 20)],
           'LUAU': [('HAPPINESS', 20)], 'THE_ARTS': [('CULTURE', 20)], 'HULA': [('GOLD', 10), ('PRODUCTION', 10)], 'TIKI': [('CULTURE', 20)], 'RONGO': [('SCIENCE', 20)],
           'TAPACLOTH': [('CULTURE', 20)], 'STONECARVING': [('CULTURE', 15), ('TILE_IMPROVEMENT', 5)], 'HONOR': [('OFFENSE', 10), ('DEFENSE', 10)],
           'POI': [('NAVAL', 10), ('NAVAL_RECON', 10)], 'ARIKI': [('OFFENSE', 10), ('DEFENSE', 10)], 'HEALING': [('OFFENSE', 10), ('DEFENSE', 10)],
           'HAKA': [('OFFENSE', 10), ('CULTURE', 10)], 'MANA': [('GREAT_PEOPLE', 20)],
           'FAITH': [('RELIGION', 20)], 'SHRINES': [('RELIGION', 20)], 'MANDATE': [('RELIGION', 20)], 'THEOCRACY': [('RELIGION', 10), ('GOLD', 10)], 'TOLERANCE': [('RELIGION', 20)], 'REFORMATION': [('RELIGION', 20)],
           'TRADE': [('GOLD', 20)], 'ROUTES': [('GOLD', 20)], 'POSTS': [('GOLD', 20)], 'MERCHANTS': [('GOLD', 10), ('GREAT_PEOPLE', 10)], 'MARKETS': [('GOLD', 10), ('SCIENCE', 10)], 'LUXURIES': [('HAPPINESS', 20)]}
# English help texts of the scenario with {name} for the policy's name; the Russian ones alongside
HELP = {
    'CEREMONY': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] improves the happiness of your empire allowing it to grow larger.[NEWLINE][NEWLINE]Adopting {name} reduces [ICON_HAPPINESS_4] Unhappiness from [ICON_CITIZEN] Population in the [ICON_CAPITAL] Capital by 33%.",
                 "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] повышает счастье вашей державы и позволяет ей расти.[NEWLINE][NEWLINE]Принятие ветки «{name}» снижает [ICON_HAPPINESS_4] недовольство от [ICON_CITIZEN] населения в [ICON_CAPITAL] столице на 33%."),
    'TAPU': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE][ICON_CULTURE] Culture cost of future Policies reduced by 10%.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Стоимость будущих институтов в [ICON_CULTURE] культуре снижена на 10%."),
    'POWHIRI': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE][ICON_GOLD] Gold gifts to City-States produce 25% more [ICON_INFLUENCE] Influence.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Дары [ICON_GOLD] золота городам-государствам дают на 25% больше [ICON_INFLUENCE] влияния."),
    'SURFING': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_HAPPINESS_1] Happiness for each City in your empire.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_HAPPINESS_1] счастья за каждый город державы."),
    'KAVA': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Immediately gain +10 [ICON_HAPPINESS_1] Happiness.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Немедленно +10 [ICON_HAPPINESS_1] счастья."),
    'LUAU': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+2 [ICON_HAPPINESS_1] Happiness from each different type of Luxury resource.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+2 [ICON_HAPPINESS_1] счастья за каждый вид редкого ресурса."),
    'THE_ARTS': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] improves the cultural output of your empire allowing you to adopt more policies.[NEWLINE][NEWLINE]Adopting {name} increases [ICON_CULTURE] Culture from Monuments and Temples by 2 each.",
                 "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] повышает культуру державы и позволяет принимать больше институтов.[NEWLINE][NEWLINE]Принятие ветки «{name}» даёт +2 [ICON_CULTURE] культуры от каждого монумента и храма."),
    'HULA': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Amount of [ICON_HAPPINESS_1] Happiness required to start a [ICON_GOLDEN_AGE] Golden Age reduced by 25%.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Для начала [ICON_GOLDEN_AGE] золотого века нужно на 25% меньше [ICON_HAPPINESS_1] счастья."),
    'TIKI': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]50% of excess [ICON_HAPPINESS_1] Happiness added each turn to the amount of [ICON_CULTURE] Culture that may be spent on Social Policies.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]50% избыточного [ICON_HAPPINESS_1] счастья каждый ход добавляется к [ICON_CULTURE] культуре для институтов."),
    'RONGO': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Increases [ICON_RESEARCH] Science output from Libraries and Observatories by 100%.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+100% [ICON_RESEARCH] науки от библиотек и обсерваторий."),
    'TAPACLOTH': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+2 [ICON_CULTURE] Culture in every City.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+2 [ICON_CULTURE] культуры в каждом городе."),
    'STONECARVING': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_CULTURE] Culture from each improvement that already yields Culture.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_CULTURE] культуры с каждого улучшения, которое уже даёт культуру."),
    'HONOR': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] improves the effectiveness of one's army in a variety of ways.[NEWLINE][NEWLINE]Adopting {name} gives +15 XP to all land combat units constructed from this point forward in the game.",
              "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] делает войско сильнее на разные лады.[NEWLINE][NEWLINE]Принятие ветки «{name}» даёт +15 опыта всем сухопутным боевым юнитам, созданным с этого момента."),
    'POI': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_MOVES] Movement for embarked units.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_MOVES] к передвижению погружённых юнитов."),
    'ARIKI': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Rate at which Great Generals are born increased by 100%.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Великие полководцы появляются на 100% быстрее."),
    'HEALING': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Melee combat units gain the Medic promotion.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Юниты ближнего боя получают повышение «Медик»."),
    'HAKA': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Gain [ICON_CULTURE] Culture for the empire equal to TRIPLE the [ICON_STRENGTH] Combat Strength of each enemy unit killed.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]За каждого убитого врага держава получает [ICON_CULTURE] культуру, равную ТРОЙНОЙ [ICON_STRENGTH] боевой силе юнита."),
    'MANA': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Rate at which [ICON_GREAT_PEOPLE] Great People are born increased by 100%.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE][ICON_GREAT_PEOPLE] Великие люди появляются на 100% быстрее."),
    'FAITH': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] increases the [ICON_PEACE] Faith of your people.[NEWLINE][NEWLINE]Adopting {name} allows you to build Shrines and Temples in half the usual time.",
              "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] умножает [ICON_PEACE] веру вашего народа.[NEWLINE][NEWLINE]Принятие ветки «{name}» позволяет строить святилища и храмы вдвое быстрее."),
    'SHRINES': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_PEACE] Faith from Shrines and Temples.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_PEACE] веры от святилищ и храмов."),
    'MANDATE': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]20% discount on all purchases of religious units and buildings with [ICON_PEACE] Faith.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Покупка религиозных юнитов и зданий за [ICON_PEACE] веру на 20% дешевле."),
    'THEOCRACY': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Temples increase a city's [ICON_GOLD] Gold output by 25%.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Храмы увеличивают доход города в [ICON_GOLD] золоте на 25%."),
    'TOLERANCE': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Cities with a majority religion also get the Pantheon belief bonus of the second most popular religion.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Города с господствующей религией получают и бонус пантеона второй по численности религии."),
    'REFORMATION': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]If you founded a religion, gain a bonus Reformation belief.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Если вы основали религию, получаете дополнительное верование Реформации."),
    'TRADE': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] provides bonuses to empires focused on [ICON_GOLD] Gold.[NEWLINE][NEWLINE]Adopting {name} will boost [ICON_GOLD] Gold output in the [ICON_CAPITAL] Capital by 25%.",
              "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR] помогает державам, сосредоточенным на [ICON_GOLD] золоте.[NEWLINE][NEWLINE]Принятие ветки «{name}» увеличивает доход [ICON_CAPITAL] столицы в [ICON_GOLD] золоте на 25%."),
    'ROUTES': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+2 [ICON_GOLD] Gold from all your land trade routes. Maintenance paid on Roads reduced by 50%.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+2 [ICON_GOLD] золота от каждого сухопутного торгового пути. Содержание дорог дешевле на 50%."),
    'POSTS': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_GOLD] Gold from every Trading Post.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+1 [ICON_GOLD] золота с каждой фактории."),
    'MERCHANTS': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Great Merchants are earned 25% faster. Receive double [ICON_GOLD] Gold from Great Merchant trade missions. +1 [ICON_MOVES] Movement for embarked units.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Великие торговцы появляются на 25% быстрее. Торговые миссии приносят вдвое больше [ICON_GOLD] золота. +1 [ICON_MOVES] к передвижению погружённых юнитов."),
    'MARKETS': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Purchasing items in Cities requires 25% less [ICON_GOLD] Gold. +1 [ICON_RESEARCH] Science from every Mint and Market.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]Покупки в городах на 25% дешевле в [ICON_GOLD] золоте. +1 [ICON_RESEARCH] науки от каждого монетного двора и рынка."),
    'LUXURIES': ("[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+2 [ICON_HAPPINESS_1] Happiness from each Luxury resource.", "[COLOR_POSITIVE_TEXT]{name}[ENDCOLOR][NEWLINE]+2 [ICON_HAPPINESS_1] счастья за каждый редкий ресурс."),
}
TITLE = {'CEREMONY': ('{1_PlayerName:textkey} the Revered of {2_CivName:textkey}', '{1_PlayerName:textkey} Почитаемый, {2_CivName:textkey}'),
         'THE_ARTS': ('{1_PlayerName:textkey} the Artful of {2_CivName:textkey}', '{1_PlayerName:textkey} Искусный, {2_CivName:textkey}'),
         'HONOR': ('{1_PlayerName:textkey} the Great of {2_CivName:textkey}', '{1_PlayerName:textkey} Великий, {2_CivName:textkey}'),
         'FAITH': ('{1_PlayerName:textkey} the Pious of {2_CivName:textkey}', '{1_PlayerName:textkey} Благочестивый, {2_CivName:textkey}'),
         'TRADE': ('{1_PlayerName:textkey} the Wealthy of {2_CivName:textkey}', '{1_PlayerName:textkey} Богатый, {2_CivName:textkey}')}
POLICY_CHILD_TABLES = ['Policy_CityYieldChanges', 'Policy_CoastalCityYieldChanges', 'Policy_CapitalYieldChanges', 'Policy_CapitalYieldPerPopChanges', 'Policy_CapitalYieldModifiers', 'Policy_Disables',
                       'Policy_Flavors', 'Policy_GreatWorkYieldChanges', 'Policy_HurryModifiers', 'Policy_PrereqPolicies', 'Policy_PrereqORPolicies', 'Policy_SpecialistExtraYields',
                       'Policy_BuildingClassYieldModifiers', 'Policy_BuildingClassYieldChanges', 'Policy_BuildingClassCultureChanges', 'Policy_BuildingClassProductionModifiers',
                       'Policy_BuildingClassTourismModifiers', 'Policy_BuildingClassHappiness', 'Policy_ImprovementYieldChanges', 'Policy_ImprovementCultureChanges', 'Policy_ValidSpecialists',
                       'Policy_YieldModifiers', 'Policy_FreePromotions', 'Policy_UnitCombatFreeExperiences', 'Policy_FreePromotionUnitCombats', 'Policy_UnitCombatProductionModifiers',
                       'Policy_FreeUnitClasses', 'Policy_TourismOnUnitCreation', 'Policy_FreeItems']


def ptype(prefix, key): return f'POLICY_{prefix}_{key}'
def btype(prefix, key): return f'POLICY_BRANCH_{prefix}_{key}'


def effects(prefix, key, cols, rows):
    """(columns, rows) of a policy in one scenario: the scenario's variant if it has one."""
    v = VARIANTS.get(prefix, {}).get(key)
    return (v[0], v[1]) if v else (cols, rows)


def sql(prefix):
    """Database changes: the nine stock branches and all their policies go, the five scenario branches come, IDs are renumbered."""
    branches = ', '.join(f"'POLICY_BRANCH_{b}'" for b in STOCK_BRANCHES)
    out = [f"-- {prefix}: the social policy tree of Paradise Found plus a faith and a trade branch in place of the nine stock branches (generated by tools/paradise_policies.py).",
           "-- The three Brave New World ideologies and their tenets stay; the Industrial era that triggers them is unreachable.",
           f"DELETE FROM Policies WHERE PolicyBranchType IN ({branches}) OR Type IN (SELECT FreePolicy FROM PolicyBranchTypes WHERE Type IN ({branches})) OR Type IN (SELECT FreeFinishingPolicy FROM PolicyBranchTypes WHERE Type IN ({branches}));",
           f"DELETE FROM PolicyBranch_Disables WHERE PolicyBranchType IN ({branches}) OR PolicyBranchDisable IN ({branches});",
           f"DELETE FROM PolicyBranchTypes WHERE Type IN ({branches});"]
    for t in POLICY_CHILD_TABLES: out.append(f"DELETE FROM {t} WHERE PolicyType NOT IN (SELECT Type FROM Policies);")
    out.append("DELETE FROM Policy_PrereqPolicies WHERE PrereqPolicy NOT IN (SELECT Type FROM Policies);")
    out.append("DELETE FROM Policy_PrereqORPolicies WHERE PrereqPolicy NOT IN (SELECT Type FROM Policies);")
    out.append("")
    for key, branch, gx, gy, cols, (atlas, atlas_a, idx) in POLICIES:
        t = ptype(prefix, key); names = ['Type', 'Description', 'Civilopedia', 'Help', 'PortraitIndex', 'IconAtlas', 'IconAtlasAchieved']
        vals = [f"'{t}'", f"'TXT_KEY_{t}'", f"'TXT_KEY_{t}_TEXT'", f"'TXT_KEY_{t}_HELP'", str(idx), f"'{atlas}'", f"'{atlas_a}'"]
        if branch: names += ['PolicyBranchType', 'CultureCost', 'GridX', 'GridY']; vals += [f"'{btype(prefix, branch)}'", '10', str(gx), str(gy)]
        cols, rows = effects(prefix, key, cols, ROWS.get(key, []))
        for c, v in cols.items(): names.append(c); vals.append(str(v))
        out.append(f"INSERT INTO Policies ({', '.join(names)}) VALUES ({', '.join(vals)});")
        for table, r in rows:
            out.append(f"INSERT INTO {table} (PolicyType, {', '.join(r)}) VALUES ('{t}', {', '.join(repr(v) if isinstance(v, str) else str(v) for v in r.values())});")
    for key, tex in BRANCHES:
        b = btype(prefix, key)
        era = f"'{BRANCH_ERA[key]}'" if key in BRANCH_ERA else 'NULL'
        out.append(f"INSERT INTO PolicyBranchTypes (Type, Description, Help, Title, FreePolicy, EraPrereq) VALUES ('{b}', 'TXT_KEY_{b}', 'TXT_KEY_{b}_HELP', 'TXT_KEY_{b}_TITLE', '{ptype(prefix, key)}', {era});")
    out.append("-- wonders that needed a stock branch")
    for w, key in WONDER_BRANCH.items(): out.append(f"UPDATE Buildings SET PolicyBranchType = '{btype(prefix, key)}' WHERE Type = '{w}';")
    out.append("UPDATE Buildings SET PolicyBranchType = NULL WHERE PolicyBranchType NOT IN (SELECT Type FROM PolicyBranchTypes);")
    out.append("")
    for key, fl in FLAVORS.items():
        for f, v in fl: out.append(f"INSERT INTO Policy_Flavors (PolicyType, FlavorType, Flavor) VALUES ('{ptype(prefix, key)}', 'FLAVOR_{f}', {v});")
    for key, pre in PREREQS: out.append(f"INSERT INTO Policy_PrereqPolicies (PolicyType, PrereqPolicy) VALUES ('{ptype(prefix, key)}', '{ptype(prefix, pre)}');")
    out += ["", "-- the Polynesia DLC's policy icons",
            "INSERT OR REPLACE INTO IconTextureAtlases (Atlas, IconSize, Filename, IconsPerRow, IconsPerColumn) VALUES ('POLYNESIA_POLICY_ATLAS', 256, 'SocialPolicies_Polynesia256.dds', 4, 4), ('POLYNESIA_POLICY_ATLAS', 64, 'SocialPolicies_Polynesia64.dds', 4, 4), ('POLYNESIA_POLICY_A_ATLAS', 64, 'SocialPoliciesAchieved_Polynesia64.dds', 4, 4);",
            "", "-- contiguous IDs, the scenario branches first: the policy screen walks branches from ID 0 and stops at the first ideology (PurchaseByLevel)",
            "CREATE TEMP TABLE pb_ids AS SELECT ID AS OldID, (SELECT COUNT(*) FROM PolicyBranchTypes b2 WHERE b2.PurchaseByLevel < b1.PurchaseByLevel OR (b2.PurchaseByLevel = b1.PurchaseByLevel AND b2.ID < b1.ID)) AS NewID FROM PolicyBranchTypes b1;",
            "UPDATE PolicyBranchTypes SET ID = (SELECT NewID FROM pb_ids WHERE OldID = PolicyBranchTypes.ID) + 10000; UPDATE PolicyBranchTypes SET ID = ID - 10000; DROP TABLE pb_ids;",
            "CREATE TEMP TABLE p_ids AS SELECT ID AS OldID, (SELECT COUNT(*) FROM Policies p2 WHERE p2.ID < p1.ID) AS NewID FROM Policies p1;",
            "UPDATE Policies SET ID = (SELECT NewID FROM p_ids WHERE OldID = Policies.ID) + 10000; UPDATE Policies SET ID = ID - 10000; DROP TABLE p_ids;", ""]
    return '\n'.join(out)


def text_rows(prefix, names, lang, pedia=None):
    """(tag, text) pairs for one language.  names: key -> (EN, RU) display name; pedia: key -> (EN, RU) civilopedia text for the openers."""
    i = 0 if lang == 'en' else 1; rows = []
    for key, branch, *_ in POLICIES:
        t = ptype(prefix, key); name = names[key][i]
        v = VARIANTS.get(prefix, {}).get(key); help = (v[2] if v else HELP[key])[i]
        rows.append((f'TXT_KEY_{t}', name)); rows.append((f'TXT_KEY_{t}_HELP', help.replace('{name}', name)))
        rows.append((f'TXT_KEY_{t}_TEXT', (pedia or {}).get(key, (name, name))[i]))
    for key, tex in BRANCHES:
        b = btype(prefix, key); name = names[key][i]
        rows += [(f'TXT_KEY_{b}', name), (f'TXT_KEY_{b}_CAP', name.upper()), (f'TXT_KEY_{b}_HELP', HELP[key][i].replace('{name}', name)), (f'TXT_KEY_{b}_TITLE', TITLE[key][i])]
    return rows
