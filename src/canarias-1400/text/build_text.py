#!/usr/bin/env python3
"""Canarias 1400 text and database rows: the seven native peoples on top of their donor civilizations (names, leaders,
unique-ability text, Dawn of Man, civilopedia, diplomacy dialogue, city lists), natural wonder names, load-screen blurbs,
EN + RU.  Writes ui/Canarias1400_Text.xml and ui/Canarias1400_Rules.xml (city lists, colours, calendar)."""
import os, html, sys
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.join(HERE, '..', 'ui')
sys.path.insert(0, HERE)
from ru import RU, RU_WONDERS, RU_EXTRA, RU_UNIQUES, RU_RENAMES, RU_RELIGIONS
import uniques
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools')); import paradise_policies, build_policy_screen
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
DIALOG_KEYS = [l.strip() for l in open(os.path.join(XMLDIR, 'LEADER_DIALOG_KEYS.txt')) if l.strip()]
KEYS = lambda prefix: [k for k in DIALOG_KEYS if k.startswith(prefix)]
NL = '[NEWLINE][NEWLINE]'

# donor civilization data per faction (slot order = the generator's PLAYERS order)
DONOR = {
    'TENERIFE': dict(civ='SHOSHONE', prefix='TXT_KEY_LEADER_POCATELLO_', leader_key='TXT_KEY_LEADER_POCATELLO', trait_key='TXT_KEY_TRAIT_GREAT_EXPANSE'),
    'GRANCANARIA': dict(civ='EGYPT', prefix='TXT_KEY_LEADER_RAMESSES_', leader_key='TXT_KEY_LEADER_RAMESSES', trait_key='TXT_KEY_TRAIT_WONDER_BUILDER'),
    'LAPALMA': dict(civ='ETHIOPIA', prefix='TXT_KEY_LEADER_SELASSIE_', leader_key='TXT_KEY_LEADER_SELASSIE', trait_key='TXT_KEY_TRAIT_BONUS_AGAINST_TECH'),
    'LAGOMERA': dict(civ='INCA', prefix='TXT_KEY_LEADER_PACHACUTI_', leader_key='TXT_KEY_LEADER_PACHACUTI', trait_key='TXT_KEY_TRAIT_GREAT_ANDEAN_ROAD'),
    'ELHIERRO': dict(civ='CELTS', prefix='TXT_KEY_LEADER_BOUDICCA_', leader_key='TXT_KEY_LEADER_BOUDICCA', trait_key='TXT_KEY_TRAIT_FAITH_FROM_NATURE'),
    'FUERTEVENTURA': dict(civ='MOROCCO', prefix='TXT_KEY_LEADER_AHMAD_ALMANSUR_', leader_key='TXT_KEY_LEADER_AHMAD_ALMANSUR', trait_key='TXT_KEY_TRAIT_GATEWAY_AFRICA'),
    'LANZAROTE': dict(civ='CARTHAGE', prefix='TXT_KEY_LEADER_DIDO_', leader_key='TXT_KEY_LEADER_DIDO', trait_key='TXT_KEY_TRAIT_PHOENICIAN_HERITAGE'),
}
# faction colours (icon, background)
COLORS = {'TENERIFE': ('#F4F4F4', '#1F3A93'), 'GRANCANARIA': ('#FFD54A', '#1B6B3A'), 'LAPALMA': ('#F7F7F7', '#8B1A1A'), 'LAGOMERA': ('#9BE27A', '#1E3B2F'),
          'ELHIERRO': ('#F8E9A1', '#5B3A29'), 'FUERTEVENTURA': ('#2B2B2B', '#E8D7A0'), 'LANZAROTE': ('#F2C14E', '#6B1E2E')}

EN = {
 'TENERIFE': dict(leader='Bencomo', civ_long='The Menceyatos of Tenerife', civ_short='Guanches', adj='Guanche', trait_short='Spirit of Achinet',
   trait='Founded cities start with additional territory. Units receive +15% [ICON_STRENGTH] Combat Strength when fighting inside Guanche territory.',
   dawn="Bencomo, mencey of Taoro, the greatest of the nine kingdoms of Achinet. Your people climbed out of their caves to pasture goats under the white peak of Echeyde, where the evil one is chained and the sacred mountain smokes. Nine menceys share the island; none of them is your equal." + NL + "The island is large, the valleys of the north are green, and the summit belongs to the gods. Unite the menceyatos under Taoro, fill the ravines with herds and tagoror councils, and when strangers one day come out of the sea, let them learn what the Guanches did to the invaders at Acentejo.",
   pedia="Bencomo (c. 1438-1494) was mencey of Taoro, the richest of the nine Guanche kingdoms of Tenerife, and the soul of the resistance to the Castilian conquest. In May 1494 his warriors ambushed Alonso Fernandez de Lugo's army in the ravine of Acentejo and destroyed it, the worst defeat the conquerors suffered in the Canaries." + NL + "He fell in November of the same year at the battle of Aguere, when Lugo returned with a larger army. Tenerife, the last island to resist, submitted in 1496. The scenario places him a century early, as the embodiment of the Guanche menceys.",
   cities=['Taoro', 'Guimar', 'Abona', 'Anaga', 'Tegueste', 'Tacoronte', 'Icod', 'Daute', 'Adeje', 'Achinet', 'Chasna', 'Tegueste Alto'],
   lines={
    'FIRSTGREETING': ["I am Bencomo, mencey of Taoro. You stand on Achinet, the island of Echeyde. State your purpose.", "Welcome to Taoro. The mountain watches us both.", "A stranger on the island. Speak, and speak truthfully."],
    'GREETING': ["The tagoror is in session. Speak.", "Yes?", "Taoro hears you."],
    'GOODBYE': ["Go with Achaman.", "Until the next council.", "Farewell."],
    'DECLAREWAR': ["You have chosen the ravines of Achinet for your grave. So be it.", "The Guanches do not start wars. We finish them.", "Then come. Acentejo is waiting."],
    'ATTACKED': ["You strike at Taoro? Every ravine on this island will fight you.", "The menceys are united now. You did that.", "Achaman sees this treachery. Prepare yourself.", "Fool. The mountain is ours, and so is the island."],
    'DEFEATED': ["Taoro falls. Achinet does not forget.", "You hold the valleys. You will never hold the mountain.", "Our mummies will outlast your banners."],
    'WINWAR': ["The island is ours again. Remember this.", "Go home. Achinet has spoken."],
    'LOSEWAR': ["Enough. Let the goats graze in peace.", "A truce, then.", "Agreed. For now."],
    'TRADE_YES': ["Agreed. A fair exchange.", "Yes. Taoro accepts.", "Done."],
    'TRADE_NO': ["No. That is not an exchange, that is a theft.", "Taoro refuses.", "No."],
    'TRADEREQUEST': ["Here is what Taoro offers.", "Consider this exchange.", "A proposal between neighbours."],
    'DEMANDTRIBUTE': ["The menceyatos require a gift. Give it.", "Pay, and the warriors stay home.", "Tribute. Now."],
    'LETSHEARIT': ["Speak.", "Go on.", "I am listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "So be it."],
    'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
    'WARBLUFF': ["Do not threaten Taoro.", "Careful, stranger.", "You would regret it."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["Taoro pays nobody.", "No."], 'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
   }),
 'GRANCANARIA': dict(leader='Tenesor Semidan', civ_long='The Guanartemato of Tamaran', civ_short='Canarii', adj='Canarian', trait_short='Granaries of Valeron',
   trait='+20% [ICON_PRODUCTION] Production towards Wonder construction.',
   dawn="Tenesor Semidan, guanarteme of Agaldar, lord of the most populous and most ordered of the islands. Your people carve granaries into the cliffs, paint their caves in red and white, raise their dead on stone platforms and plant barley on terraces that climb to Roque Nublo, the sacred rock at the heart of Tamaran." + NL + "Telde in the east and Agaldar in the north have shared the island too long. Bring the faycan priests and the guayres under one guanarteme, build what no other island can build, and make the Canarii the people the archipelago is named after.",
   pedia="Tenesor Semidan (died c. 1496) was the last guanarteme of Galdar, the northern kingdom of Gran Canaria. Captured in 1482 and taken to Castile, he was baptised as Fernando Guanarteme and returned to persuade his people to end a resistance that had lasted five years; he later fought beside the Castilians on Tenerife." + NL + "Pre-conquest Gran Canaria was the most stratified society of the islands: a king, a high priest, a council of nobles, collective granaries such as the Cenobio de Valeron and the painted cave of Galdar. The scenario borrows his name for the island's rulers a century earlier.",
   cities=['Agaldar', 'Telde', 'Arehucas', 'Tejeda', 'Aguimes', 'Tirajana', 'Arguineguin', 'Artenara', 'Moya', 'Tamaran', 'Satautey', 'Gando'],
   lines={
    'FIRSTGREETING': ["I am Tenesor Semidan, guanarteme of Agaldar, in the island of Tamaran. The Canarii welcome you.", "You have reached Tamaran, the island of the Canarii. Speak.", "A guest from across the water. Sit, and tell us of your island."],
    'GREETING': ["The guanarteme listens.", "Speak, friend.", "Yes?"],
    'GOODBYE': ["May your barley grow.", "Farewell.", "Until next time."],
    'DECLAREWAR': ["The guayres have decided. It is war.", "You leave Tamaran no choice.", "Then the granaries will feed an army."],
    'ATTACKED': ["You attack the Canarii? The whole island rises against you.", "Agaldar remembers insults for a long time.", "So. The faycan warned me of you.", "You will find our cliffs harder than our words."],
    'DEFEATED': ["Tamaran falls. Spare the granaries; the people will need them.", "You have the island. May it bring you as much joy as it brought me.", "The caves will keep our paintings long after you are gone."],
    'WINWAR': ["The island is at peace again.", "Tamaran stands. Go."],
    'LOSEWAR': ["Peace. The terraces need tending.", "Enough blood. Agreed.", "A truce."],
    'TRADE_YES': ["A fair bargain. Agreed.", "Yes.", "Agaldar accepts."],
    'TRADE_NO': ["No. The Canarii are not fools.", "Refused.", "That will not do."],
    'TRADEREQUEST': ["An offer from Agaldar.", "Consider this.", "A proposal between neighbours."],
    'DEMANDTRIBUTE': ["A gift for the guanarteme would be wise.", "Pay, and keep the peace.", "Tribute."],
    'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
    'DISAGREE_SHORT': ["No.", "Impossible.", "Refused."],
    'WARBLUFF': ["Do not test Tamaran.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "The Canarii pay nobody."], 'TRADE_NEEDMORE': ["Not enough.", "More.", "Add to it."],
   }),
 'LAPALMA': dict(leader='Tanausu', civ_long='The Cantons of Benahoare', civ_short='Benahoaritas', adj='Benahoarita', trait_short='Lords of the Caldera',
   trait='+20% [ICON_STRENGTH] Combat Strength against civilizations with more cities than you.',
   dawn="Tanausu, lord of Acero, the great caldera at the heart of Benahoare. Twelve cantons share the steepest island of the archipelago, and yours is the one nobody has ever taken: a fortress of cliffs and springs with a single entrance, where the Benahoaritas keep their herds and their freedom." + NL + "Your people are few and their island is a ladder of ravines. Make every ravine a wall, every spring a city, and let the bigger islands learn that numbers mean nothing on the slopes of the Caldera.",
   pedia="Tanausu (died 1493) was the chief of Acero, the canton of the Caldera de Taburiente on La Palma, and the last Benahoarita leader to resist the Castilians. He held the caldera against Alonso Fernandez de Lugo until he was taken by treachery during a truce in May 1493." + NL + "Shipped to Castile, he refused all food and died at sea. The Benahoaritas were goat-herding cave dwellers organised in twelve cantons; their name for the island, Benahoare, means 'my land'.",
   cities=['Aridane', 'Acero', 'Tedote', 'Tihuya', 'Tigalate', 'Ahenguareme', 'Tenagua', 'Adeyahamen', 'Tagaragre', 'Tijarafe', 'Guehebey', 'Tamanca'],
   lines={
    'FIRSTGREETING': ["I am Tanausu, lord of Acero. You have found Benahoare. Few do.", "Welcome to the island of ravines. Mind your step.", "A stranger in the caldera. Speak quickly."],
    'GREETING': ["Speak.", "Acero listens.", "Well?"],
    'GOODBYE': ["Go carefully. The paths are steep.", "Farewell.", "Until next time."],
    'DECLAREWAR': ["Come to the caldera, then. Nobody has left it alive.", "War. The ravines will do the rest.", "So be it. We have fought bigger."],
    'ATTACKED': ["You attack Benahoare? Count your men now; you will not be able to later.", "The cantons are one now. Thank yourself for that.", "Good. We have been waiting.", "Every cliff on this island is a weapon."],
    'DEFEATED': ["You have taken the caldera. I will not eat your bread.", "Benahoare is yours. The springs will outlive you.", "You won by numbers. Remember that."],
    'WINWAR': ["The island is free. Go.", "Acero holds. It always holds."],
    'LOSEWAR': ["Peace. The goats are hungry.", "Enough.", "A truce, then."],
    'TRADE_YES': ["Fair. Agreed.", "Yes.", "Acero accepts."],
    'TRADE_NO': ["No.", "That is no bargain.", "Refused."],
    'TRADEREQUEST': ["Acero offers this.", "Consider it.", "An exchange between islands."],
    'DEMANDTRIBUTE': ["A gift would keep my warriors at home.", "Pay.", "Tribute, or the ravines."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Fine."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Threats? In my caldera?", "Careful.", "Do not."],
    'TRIBUTE_YES': ["Take it and go.", "Very well."], 'TRIBUTE_NO': ["Acero pays nobody.", "No."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
 'LAGOMERA': dict(leader='Hautacuperche', civ_long='The Four Cantons of Gomera', civ_short='Gomeros', adj='Gomero', trait_short='Paths of the Whistlers',
   trait='Units ignore terrain costs when moving into any tile with Hills. No maintenance costs for improvements in Hills; half elsewhere.',
   dawn="Hautacuperche, warrior of the canton of Mulagua on the round island of Gomera. Your people speak across the ravines with whistles, farm terraces cut into cliffs, and climb to Garajonay, the misty forest at the summit, to honour the ancestors." + NL + "Four cantons, Mulagua, Ipalan, Orone and Agana, share a small island with no flat ground at all. Make the ravines your roads, the terraces your wealth, and keep the whistled word of Gomera free of any lord from across the sea.",
   pedia="Hautacuperche (died 1488) was a Gomero of the canton of Mulagua who led the rebellion of 1488 against Hernan Peraza the Younger, the Castilian lord of La Gomera, killing him at the cave of Guahedum. The island had been nominally Castilian since the 1440s under a pact between the cantons and the Perazas." + NL + "The rising was crushed within weeks by Pedro de Vera; Hautacuperche died in the fighting and hundreds of Gomeros were executed or sold. The Gomeros' whistled language, the silbo, is still spoken on the island.",
   cities=['Ipalan', 'Mulagua', 'Orone', 'Agana', 'Guahedum', 'Hilajero', 'Tamargada', 'Aguajilva', 'Arure', 'Tazo', 'Alojera', 'Chipude'],
   lines={
    'FIRSTGREETING': ["I am Hautacuperche of Mulagua. You have reached Gomera, the island of the whistlers.", "A visitor. The ravines told me you were coming.", "Welcome. Speak, or whistle, we understand both."],
    'GREETING': ["Yes?", "The cantons listen.", "Speak."],
    'GOODBYE': ["May the mist hide your path.", "Farewell.", "Until next time."],
    'DECLAREWAR': ["Then the whistles will carry a different message tonight.", "War. You will not find us; we will find you.", "So be it."],
    'ATTACKED': ["You attack Gomera? Every ravine already knows.", "The cantons are warned. You will regret this.", "Peraza thought the same. Ask him.", "Good. We were tired of waiting."],
    'DEFEATED': ["Gomera falls. The whistles will go on without me.", "You hold the island. You will never understand it.", "The forest keeps our names."],
    'WINWAR': ["The island is ours. Go.", "Gomera stands."],
    'LOSEWAR': ["Peace. The terraces are waiting.", "Enough.", "A truce."],
    'TRADE_YES': ["Agreed.", "Yes, that is fair.", "Done."],
    'TRADE_NO': ["No.", "That is not fair.", "Refused."],
    'TRADEREQUEST': ["Gomera offers this.", "Consider it.", "A proposal."],
    'DEMANDTRIBUTE': ["A gift for the cantons.", "Pay, and the whistles stay quiet.", "Tribute."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Fine."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Do not threaten the cantons.", "Careful.", "You would regret it."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["Gomera pays nobody.", "No."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
 'ELHIERRO': dict(leader='Armiche', civ_long='The Kingdom of Esero', civ_short='Bimbaches', adj='Bimbache', trait_short='Water of the Garoe',
   trait='+1 [ICON_PEACE] Faith in every city with an adjacent unimproved Forest tile; +2 with three or more.',
   dawn="Armiche, king of the Bimbaches on Esero, the smallest and westernmost of the islands, the last land before the edge of the world. Your people have no rivers; they drink the water that the sacred tree Garoe gathers from the clouds, and they guard it as the island's life." + NL + "Esero is small, but it is yours alone. Keep the Garoe green, keep the people together, and make the farthest island a place the gods remember.",
   pedia="Armiche was the king of El Hierro when Jean de Bethencourt's Normans arrived in 1405. Lured to a meeting by a Bimbache interpreter under promise of safe conduct, he and his people were seized and most were sold as slaves; the island was then settled by Normans and Castilians." + NL + "The Bimbaches, perhaps a thousand people, lived from goats, shellfish and a little barley on an island without springs; the Garoe, a laurel tree on which the mist condensed, was their main water source and became the island's emblem.",
   cities=['Tigulahe', 'Isora', 'Erese', 'Tinor', 'Azofa', 'Echedo', 'Guarazoca', 'Tigaday', 'Taibique', 'Sabinosa', 'Jinama', 'Tejeguate'],
   lines={
    'FIRSTGREETING': ["I am Armiche, king of Esero. You have sailed to the end of the world and found people here.", "Welcome to Esero. The water is scarce; the welcome is not.", "A stranger on the last island. Speak."],
    'GREETING': ["Yes?", "Esero listens.", "Speak."],
    'GOODBYE': ["Go well.", "Farewell.", "May the Garoe give you water."],
    'DECLAREWAR': ["You would fight the Bimbaches? Then you will fight all of us.", "War, then. The island is small; you will not get lost.", "So be it."],
    'ATTACKED': ["You attack Esero? The gods of the tree will remember.", "We are few, but we are all here.", "Treachery. Esero has seen it before.", "Come, then."],
    'DEFEATED': ["Esero falls. Guard the Garoe, or the island dies with us.", "You hold the island. May the tree give you nothing.", "The last island, the last to fall."],
    'WINWAR': ["Esero is free.", "Go home."],
    'LOSEWAR': ["Peace. We have lost enough.", "Agreed.", "A truce."],
    'TRADE_YES': ["Agreed.", "Yes.", "Fair enough."],
    'TRADE_NO': ["No.", "Esero cannot spare that.", "Refused."],
    'TRADEREQUEST': ["Esero offers this.", "Consider it.", "A proposal."],
    'DEMANDTRIBUTE': ["A gift would be welcome.", "Pay.", "Tribute."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Fine."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Do not threaten Esero.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "Esero pays nobody."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
 'FUERTEVENTURA': dict(leader='Guize', civ_long='The Kingdoms of Maxorata and Jandia', civ_short='Majos of Erbania', adj='Majo', trait_short='Walls of Erbania',
   trait='+3 [ICON_GOLD] Gold and +1 [ICON_CULTURE] Culture for each Trade Route with a different civilization. Trade Routes other civilizations send to you give +2 [ICON_GOLD] Gold to you and +1 to them.',
   dawn="Guize, king of Maxorata, the northern half of Erbania, the long dry island that the Majos divided with a wall from coast to coast. Your people are shepherds of goats on a land of sand and wind, where every well is a treasure and the sacred mountain Tindaya carries the footprints of the gods." + NL + "Ayoze rules Jandia beyond the wall. Unite the island, dig the wells, fill the plains with herds, and make the dry east of the archipelago the crossroads of its trade.",
   pedia="Guize was king of Maxorata, the northern of the two Majo kingdoms of Fuerteventura, at the time of Jean de Bethencourt's conquest. He and Ayoze, king of Jandia, submitted and were baptised in January 1405 after two years of raids and a famine; both kept a place in the Norman settlement." + NL + "The Majos of Fuerteventura and Lanzarote were related peoples who lived from goats, barley and shellfish on the driest islands of the archipelago; the wall across the isthmus of La Pared that divided the two kingdoms gave the island its later Castilian name.",
   cities=['Tefia', 'Tetir', 'Tuineje', 'Tiscamanita', 'Tesejerague', 'Ajuy', 'Toto', 'Jandia', 'Guisguey', 'Esquinzo', 'Tebeto', 'Teguital'],
   lines={
    'FIRSTGREETING': ["I am Guize, king of Maxorata. Erbania is dry, but its welcome is wide.", "You have crossed to Erbania. Water first, then talk.", "A stranger. Sit in the shade and speak."],
    'GREETING': ["Yes?", "Maxorata listens.", "Speak."],
    'GOODBYE': ["Go well, and carry water.", "Farewell.", "Until next time."],
    'DECLAREWAR': ["Then the wall will have a new purpose.", "War. The sand will cover your bones.", "So be it."],
    'ATTACKED': ["You attack the Majos? The island has swallowed better men.", "Maxorata and Jandia stand together today. You did that.", "Treachery in the dry season. We will remember.", "Come, then. The wells are ours."],
    'DEFEATED': ["Erbania falls. The wind will erase you too.", "You hold the island. Good luck finding water.", "The Majos are shepherds. We will be here when you leave."],
    'WINWAR': ["Erbania is free.", "Go home."],
    'LOSEWAR': ["Peace. The herds need us.", "Agreed.", "A truce."],
    'TRADE_YES': ["Agreed. Trade is the breath of Erbania.", "Yes.", "Done."],
    'TRADE_NO': ["No.", "That is not a trade.", "Refused."],
    'TRADEREQUEST': ["Maxorata offers this.", "A trade between islands.", "Consider it."],
    'DEMANDTRIBUTE': ["A gift for the king would be wise.", "Pay.", "Tribute."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Fine."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Do not threaten Maxorata.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "The Majos pay nobody."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
 'LANZAROTE': dict(leader='Guadarfia', civ_long='The Kingdom of Titerogaka', civ_short='Majos of Titerogaka', adj='Majo', trait_short='Harbours of the Majos',
   trait='All coastal cities receive a free Harbor. Units may cross Mountains after the first Great General is earned, taking 50 HP damage if they end a turn on a Mountain.',
   dawn="Guadarfia, king of Titerogaka, the first island that every ship from the north reaches. Your people live between the lava fields of the volcanoes and the sea, in a land where it almost never rains and where strangers have already come to take slaves more than once." + NL + "The sea brought the raiders; it can bring trade as well. Build harbours in every bay, fortify Zonzamas, and make Titerogaka the gate of the archipelago rather than its victim.",
   pedia="Guadarfia was king of Lanzarote when Jean de Bethencourt and Gadifer de La Salle landed in 1402. His people, perhaps three hundred after decades of slave raids, made a pact with the Normans; after a betrayal by Bethencourt's own men he rose against them, was defeated and baptised as Luis in 1404." + NL + "Lanzarote had been known to Europeans since Lancelotto Malocello's visit of about 1312, which gave the island its European name; its native name was Titerogaka. The royal seat was at Zonzamas, whose ruins survive near Teguise.",
   cities=['Zonzamas', 'Acatife', 'Tinajo', 'Tias', 'Yaiza', 'Guatiza', 'Haria', 'Mala', 'Tahiche', 'Macher', 'Femes', 'Tiagua'],
   lines={
    'FIRSTGREETING': ["I am Guadarfia, king of Titerogaka. Ships reach my island first; so do the troubles. Which are you?", "Welcome to Titerogaka. We have seen sails before.", "A stranger from the sea. Speak plainly."],
    'GREETING': ["Yes?", "Zonzamas listens.", "Speak."],
    'GOODBYE': ["Fair winds.", "Farewell.", "Until next time."],
    'DECLAREWAR': ["Then the lava fields will have you.", "War. We have fought raiders before.", "So be it."],
    'ATTACKED': ["You attack Titerogaka? We are used to it. We are also used to winning.", "The harbours are closed to you now.", "Treachery. Bethencourt would be proud of you.", "Come, then."],
    'DEFEATED': ["Titerogaka falls. The sea will bring others after you.", "You hold the island. The volcanoes hold you.", "The Majos endure."],
    'WINWAR': ["Titerogaka is free.", "Go home."],
    'LOSEWAR': ["Peace. The harbours are open.", "Agreed.", "A truce."],
    'TRADE_YES': ["Agreed. The harbour is open.", "Yes.", "Done."],
    'TRADE_NO': ["No.", "That is piracy, not trade.", "Refused."],
    'TRADEREQUEST': ["Zonzamas offers this.", "A trade.", "Consider it."],
    'DEMANDTRIBUTE': ["A gift for the harbour would be wise.", "Pay.", "Tribute."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Fine."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Do not threaten Titerogaka.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "Titerogaka pays nobody."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
}
WONDERS_EN = {'TXT_KEY_FEATURE_FUJI': 'Teide', 'TXT_KEY_FEATURE_MT_KAILASH': 'Roque Nublo', 'TXT_KEY_FEATURE_MESA': 'Caldera de Taburiente', 'TXT_KEY_FEATURE_SRI_PADA': 'Garajonay',
              'TXT_KEY_FEATURE_FOUNTAIN_YOUTH': 'Garoe', 'TXT_KEY_FEATURE_ULURU': 'Tindaya', 'TXT_KEY_FEATURE_VOLCANO': 'La Corona'}
RELIGIONS_EN = {'BUDDHISM': 'Achaman', 'CHRISTIANITY': 'Magec', 'CONFUCIANISM': 'Chaxiraxi', 'HINDUISM': 'Achuguayo', 'ISLAM': 'Achuhucanac', 'JUDAISM': 'Acoran', 'SHINTO': 'Alcorac', 'SIKHISM': 'Abora', 'TAOISM': 'Orahan', 'TENGRIISM': 'Eraoranhan', 'ZOROASTRIANISM': 'Moneiba', 'ORTHODOXY': 'Chijoraji', 'PROTESTANTISM': 'Guayota'}
RELIGION_KEY = {r: 'TXT_KEY_RELIGION_' + ('CATHOLICISM' if r == 'CHRISTIANITY' else r) for r in RELIGIONS_EN}
EXTRA_EN = {'TXT_KEY_CAN1400_TITLE': 'Canarias 1400',
            'TXT_KEY_CAN1400_INTRO': 'The Canary Islands in the year 1400. Seven islands, seven peoples, no boats. Build your island first; the sea comes later. Win by conquest.'}
POLICY_NAMES = {'CEREMONY': ('Beñesmen', 'Беньесмен'), 'TAPU': ('Guañameñe', 'Гуаньямене'), 'POWHIRI': ('Tagoror', 'Тагорор'), 'SURFING': ('Lucha', 'Луча'), 'KAVA': ('Gofio', 'Гофио'), 'LUAU': ('Guatatiboa', 'Гуататибоа'), 'THE_ARTS': ('Pintaderas', 'Пинтадеры'), 'HULA': ('Tajaraste', 'Тахарасте'), 'TIKI': ('Tara', 'Тара'), 'RONGO': ('Harimaguadas', 'Аримагуады'), 'TAPACLOTH': ('Tamarco', 'Тамарко'), 'STONECARVING': ('Petroglyphs', 'Петроглифы'), 'HONOR': ('Guayres', 'Гуайры'), 'POI': ('Mariscadores', 'Марискадоры'), 'ARIKI': ('Menceyes', 'Менсеи'), 'HEALING': ('Tabona', 'Табона'), 'HAKA': ('Magado', 'Магадо'), 'MANA': ('Guatimac', 'Гуатимак'),
                'FAITH': ('Achamán', 'Ачаман'), 'SHRINES': ('Efequén', 'Эфекен'), 'MANDATE': ('Almogarén', 'Альмогарен'), 'THEOCRACY': ('Faycán', 'Файкан'), 'TOLERANCE': ('Chaxiraxi', 'Чахирахи'), 'REFORMATION': ('Baladero', 'Баладеро'),
                'TRADE': ('Añepa', 'Аньепа'), 'ROUTES': ('Guanil', 'Гуаниль'), 'POSTS': ('Gánigos', 'Ганигос'), 'MERCHANTS': ('Achimencey', 'Ачименсей'), 'MARKETS': ('Guañac', 'Гуаньяк'), 'LUXURIES': ('Achicaxna', 'Ачикасна')}
POLICY_PEDIA = {'CEREMONY': ('The Beñesmen was the harvest festival of the Guanches, when the menceyatos set their quarrels aside, the gofio of the new barley was shared, and the strongest competed in wrestling and stick fighting. The guañameñe prophets and the councils of the tagoror gave the year its order.', 'Беньесмен был праздником урожая гуанчей, когда менсейяты откладывали распри, делили гофио нового ячменя, а сильнейшие состязались в борьбе и бое на палках. Пророки гуаньямене и советы тагорор давали году порядок.'), 'THE_ARTS': ('The islands had no metal and no writing, but they had art: the pintaderas, clay stamps of geometric pattern; the painted caves of Galdar; the spirals cut into the rock of La Palma; the tamarco cloaks of goat skin sewn with bone needles; the idol of Tara; the tajaraste dances of the feasts.', 'На островах не было металла и письма, но было искусство: пинтадеры, глиняные печати с геометрическим узором; расписные пещеры Гальдара; спирали, выбитые в скалах Ла-Пальмы; плащи тамарко из козьих шкур, сшитые костяными иглами; идол Тара; танцы тахарасте на праздниках.'), 'HONOR': ('The guayres and sigones were the warrior nobility of the islands, the menceyes their kings. Honor means warriors trained in the stone-throwing and stick-fighting of their youth, wounds dressed with the obsidian tabona, and the magado club that answered every landing on the beaches.', 'Гуайры и сигоне были воинской знатью островов, менсеи их королями. Честь это воины, с юности обученные метанию камней и бою на палках, раны, перевязанные обсидиановой табоной, и палица магадо, встречавшая каждую высадку на берегах.'),
                'FAITH': ('Achamán was the sky god of Tenerife, Alcorac of Gran Canaria, Abora of La Palma; Magec the sun and Chaxiraxi the mother. The faycán and the harimaguadas kept the almogarén sanctuaries and the efequén temples, and in drought the whole people climbed to the baladero to make the goats bleat to the sky for rain.', 'Ачаман был богом неба на Тенерифе, Алькорак на Гран-Канарии, Абора на Ла-Пальме; Магек был солнцем, а Чахирахи матерью. Файкан и аримагуады хранили святилища альмогарен и храмы эфекен, а в засуху весь народ поднимался к баладеро, чтобы блеяние коз вымолило у неба дождь.'),
                'TRADE': ('The añepa, the wooden sceptre of the mencey, stood for the tribute of the island: the goats of the guanil herds, the gánigo pots, the barley of the terraces. Nobles, the achimencey, and commoners, the achicaxna, each had their share in the guañac, the commonwealth of the valley.', 'Аньепа, деревянный скипетр менсея, означала дань острова: козы стад гуаниль, горшки ганигос, ячмень террас. Знать, ачименсей, и простолюдины, ачикасна, имели свою долю в гуаньяк, общине долины.')}
MOODS = ('_NEUTRAL', '_HAPPY', '_ANGRY')

def emit(lang, FF, WONDERS, EXTRA):
    rows = []
    def rep(tag, text): rows.append(f'    <Replace Tag="{tag}" Text="{html.escape(text, quote=True)}" />')
    for k, f in FF.items():
        c = DONOR[k]['civ']; prefix = DONOR[k]['prefix']; leader_key = DONOR[k]['leader_key']; trait_key = DONOR[k]['trait_key']
        rep(leader_key, f['leader']); rep(leader_key + '_PEDIA', f['pedia'])
        rep(f'TXT_KEY_CIV_{c}_DESC', f['civ_long']); rep(f'TXT_KEY_CIV_{c}_SHORT_DESC', f['civ_short']); rep(f'TXT_KEY_CIV_{c}_ADJECTIVE', f['adj'])
        rep(f'TXT_KEY_CIV5_DAWN_{c}_TEXT', f['dawn']); rep(trait_key + '_SHORT', f['trait_short']); rep(trait_key, f['trait'])
        rep(f'TXT_KEY_CAN1400_BLURB_{k}', f['dawn'])
        for i, city in enumerate(f['cities']): rep(f'TXT_KEY_CITY_NAME_CAN1400_{k}_{i}', city)
        for key in KEYS(prefix):
            suf = key[len(prefix):]; base = suf; mood = ''
            for m in MOODS:
                if suf.endswith(m): base, mood = suf[:-len(m)], m
            parts = base.rsplit('_', 1)
            if parts[-1].isdigit(): base, n = parts[0], int(parts[1]) - 1
            else: n = {'_NEUTRAL': 0, '_HAPPY': 1, '_ANGRY': 2}.get(mood, 0)
            if base in f['lines']: lines = f['lines'][base]; rep(key, lines[n % len(lines)])
    for key, name in WONDERS.items(): rep(key, name)
    for k2, v in EXTRA.items(): rep(k2, v)
    for r, name in (RELIGIONS_EN if lang == 'en' else RU_RELIGIONS).items(): rep(RELIGION_KEY[r], name)   # the stock religions become the cults of the islands' gods
    rep('TXT_KEY_RELIGION_CHRISTIANITY', (RELIGIONS_EN if lang == 'en' else RU_RELIGIONS)['CHRISTIANITY'])
    for tag, text in paradise_policies.text_rows('CAN1400', POLICY_NAMES, lang, POLICY_PEDIA): rep(tag, text)   # the Paradise Found policy tree under local names
    # unique units and buildings (text/uniques.py; Russian in ru.py)
    for u in uniques.UNITS + uniques.BUILDINGS:
        if not u['base']: continue
        t = ('UNIT' if u in uniques.UNITS else 'BUILDING') + '_CAN1400_' + u['key']
        name, help_, strategy, pedia = (u['name'], u['help'], u['strategy'], u['pedia']) if lang == 'en' else RU_UNIQUES[u['key']]
        rep(f'TXT_KEY_{t}', name); rep(f'TXT_KEY_{t}_HELP', help_); rep(f'TXT_KEY_{t}_STRATEGY', strategy); rep(f'TXT_KEY_CIV5_CAN1400_{u["key"]}_TEXT', pedia)
    # the Inca Terrace Farm stays as the Gomeros' improvement under its local name
    bancal = 'Bancales' if lang == 'en' else RU_UNIQUES['BANCALES'][0]
    rep('TXT_KEY_IMPROVEMENT_TERRACE_FARM', bancal); rep('TXT_KEY_BUILD_TERRACE_FARM', bancal)
    for key, text in (next(u for u in uniques.BUILDINGS if u['key'] == 'BANCALES')['texts'] if lang == 'en' else RU_RENAMES['BANCALES']).items(): rep(key, text)
    return rows
rows_en = emit('en', EN, WONDERS_EN, EXTRA_EN); rows_ru = emit('ru', RU, RU_WONDERS, RU_EXTRA)
xml = ('<?xml version="1.0" encoding="utf-8"?>\n<!-- Canarias 1400: the seven native peoples on their donor civilizations, natural wonders, load screen (EN + RU). -->\n<GameData>\n  <Language_en_US>\n'
       + '\n'.join(rows_en) + '\n  </Language_en_US>\n  <Language_RU_RU>\n' + '\n'.join(rows_ru) + '\n  </Language_RU_RU>\n</GameData>\n')
open(os.path.join(UI, 'Canarias1400_Text.xml'), 'w', encoding='utf-8').write(xml)

# ---- database rows: city lists, colours, calendar
def rgb(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
lx = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Canarias 1400 database rows: native city lists for the seven donor civilizations, faction colours, one turn = one year from 1400. -->', '<GameData>', '  <Civilization_CityNames>']
for k, f in EN.items():
    c = DONOR[k]['civ']; lx.append(f'    <Delete CivilizationType="CIVILIZATION_{c}" />')
    for i in range(len(f['cities'])): lx.append(f'    <Row><CivilizationType>CIVILIZATION_{c}</CivilizationType><CityName>TXT_KEY_CITY_NAME_CAN1400_{k}_{i}</CityName></Row>')
lx += ['  </Civilization_CityNames>', '  <Colors>']
for k, (icon, bg) in COLORS.items():
    for suf, hx in (('ICON', icon), ('BG', bg)):
        r, g, b = rgb(hx); lx.append(f'    <Row><Type>COLOR_PLAYER_CAN1400_{k}_{suf}</Type><Red>{r:.3f}</Red><Green>{g:.3f}</Green><Blue>{b:.3f}</Blue><Alpha>1</Alpha></Row>')
lx += ['  </Colors>', '  <PlayerColors>']
for k in COLORS: lx.append(f'    <Row><Type>PLAYERCOLOR_CAN1400_{k}</Type><PrimaryColor>COLOR_PLAYER_CAN1400_{k}_ICON</PrimaryColor><SecondaryColor>COLOR_PLAYER_CAN1400_{k}_BG</SecondaryColor><TextColor>COLOR_PLAYER_WHITE_TEXT</TextColor></Row>')
lx += ['  </PlayerColors>', '  <Civilizations>']
for k in COLORS: lx.append(f'    <Update><Where Type="CIVILIZATION_{DONOR[k]["civ"]}" /><Set DefaultPlayerColor="PLAYERCOLOR_CAN1400_{k}" /></Update>')
lx += ['  </Civilizations>',
       '  <!-- Development stops at the end of the Classical era: no pikes, crossbows or castles, no Astronomy, no caravels or ocean crossing, no Printing Press and no World Congress. The techs stay in the tree but cannot be researched. -->',
       '  <Technologies>'] + [f'    <Update><Where Era="{era}" /><Set Disable="true" /></Update>' for era in ('ERA_MEDIEVAL', 'ERA_RENAISSANCE', 'ERA_INDUSTRIAL', 'ERA_MODERN', 'ERA_POSTMODERN', 'ERA_FUTURE')] + ['    <Update><Where Type="TECH_GUILDS" /><Set Disable="false" /></Update>   <!-- the one Medieval technology: trading posts, the gold of the islands -->', '  </Technologies>',

       '  <!-- Calendar (Standard and Quick speeds): one turn = one year from 1400 on Standard speed; the game ends by time in 2000 (turn 600). -->',
       '  <Defines>', '    <Update><Where Name="START_YEAR" /><Set Value="1400" /></Update>', '  </Defines>',
       '  <GameSpeed_Turns>'] + sum([[f'    <Delete GameSpeedType="{sp}" />', f'    <Row><GameSpeedType>{sp}</GameSpeedType><MonthIncrement>12</MonthIncrement><TurnsPerIncrement>600</TurnsPerIncrement></Row>'] for sp in ('GAMESPEED_STANDARD', 'GAMESPEED_QUICK')], []) + [
       '  </GameSpeed_Turns>', '</GameData>', '']
open(os.path.join(UI, 'Canarias1400_Rules.xml'), 'w', encoding='utf-8').write('\n'.join(lx))
open(os.path.join(UI, 'Canarias1400_Uniques.sql'), 'w', encoding='utf-8').write(uniques.sql())
open(os.path.join(UI, 'Canarias1400_Policies.sql'), 'w', encoding='utf-8').write(paradise_policies.sql('CAN1400'))
build_policy_screen.build(UI, [(f'CAN1400_{k}', n, tex, f'TXT_KEY_POLICY_BRANCH_CAN1400_{k}_HELP', f'TXT_KEY_POLICY_BRANCH_CAN1400_{k}_CAP') for (k, tex), n in zip(paradise_policies.BRANCHES, ('Ceremony', 'Arts', 'Honor', 'Faith', 'Trade'))], 'Canarias 1400:')
print(f'wrote Canarias1400_Text.xml ({len(rows_en)} EN + {len(rows_ru)} RU rows), Canarias1400_Rules.xml and Canarias1400_Uniques.sql')
