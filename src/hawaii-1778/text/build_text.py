#!/usr/bin/env python3
"""Hawaii 1778 text and database rows: the five chiefdoms on top of their donor civilizations (names, leaders, unique-ability
text, Dawn of Man, civilopedia, diplomacy dialogue, city lists), the three city-states, natural wonder names, unique units and
buildings, load-screen blurbs, EN + RU.  Writes ui/Hawaii1778_Text.xml, ui/Hawaii1778_Rules.xml (city lists, city-states,
colours, calendar, tech cap) and ui/Hawaii1778_Uniques.sql."""
import os, html, sys
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.join(HERE, '..', 'ui')
sys.path.insert(0, HERE)
from ru import RU, RU_WONDERS, RU_EXTRA, RU_UNIQUES, RU_RENAMES, RU_CS, RU_RELIGIONS
import uniques
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools')); import paradise_policies, build_policy_screen
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
DIALOG_KEYS = [l.strip() for l in open(os.path.join(XMLDIR, 'LEADER_DIALOG_KEYS.txt')) if l.strip()]
KEYS = lambda prefix: [k for k in DIALOG_KEYS if k.startswith(prefix)]
NL = '[NEWLINE][NEWLINE]'

DONOR = {
    'KONA': dict(civ='POLYNESIA', prefix='TXT_KEY_LEADER_KAMEHAMEHA_', leader_key='TXT_KEY_LEADER_KAMEHAMEHA', trait_key='TXT_KEY_TRAIT_WAYFINDING'),
    'HILO': dict(civ='JAPAN', prefix='TXT_KEY_LEADER_ODA_', leader_key='TXT_KEY_LEADER_ODA_NOBUNAGA', trait_key='TXT_KEY_TRAIT_FIGHT_WELL_DAMAGED'),
    'MAUI': dict(civ='ZULU', prefix='TXT_KEY_LEADER_SHAKA_', leader_key='TXT_KEY_LEADER_SHAKA', trait_key='TXT_KEY_TRAIT_BUFFALO_HORNS'),
    'OAHU': dict(civ='CARTHAGE', prefix='TXT_KEY_LEADER_DIDO_', leader_key='TXT_KEY_LEADER_DIDO', trait_key='TXT_KEY_TRAIT_PHOENICIAN_HERITAGE'),
    'KAUAI': dict(civ='ETHIOPIA', prefix='TXT_KEY_LEADER_SELASSIE_', leader_key='TXT_KEY_LEADER_SELASSIE', trait_key='TXT_KEY_TRAIT_BONUS_AGAINST_TECH'),
}
COLORS = {'KONA': ('#FFD700', '#B22222'), 'HILO': ('#F4F4F4', '#1C1C1C'), 'MAUI': ('#FFFFFF', '#C71585'), 'OAHU': ('#FFD54A', '#1F3A93'), 'KAUAI': ('#F0E68C', '#4B0082')}
CITY_STATES = [  # key, minor civ type, trait, EN name, EN city
    ('MOLOKAI', 'MINOR_CIV_HI_MOLOKAI', 'MINOR_TRAIT_RELIGIOUS', 'Molokai', 'Kaunakakai'),
    ('LANAI', 'MINOR_CIV_HI_LANAI', 'MINOR_TRAIT_MARITIME', 'Lanai', 'Kaunolu'),
    ('NIIHAU', 'MINOR_CIV_HI_NIIHAU', 'MINOR_TRAIT_MARITIME', 'Niihau', 'Puuwai'),
]

EN = {
 'KONA': dict(leader='Kamehameha', civ_long='The Chiefdom of Kona and Kohala', civ_short='Kona', adj='Kona', trait_short='Voyagers of the Long Canoe',
   trait='Can embark and cross Ocean from the start; +1 sight for embarked units. Units receive +10% [ICON_STRENGTH] Combat Strength near Kii statues.',
   dawn="Kamehameha, nephew of the king of Hawaii, raised at Kawaihae in the shadow of the volcanoes. The prophecy at your birth said you would kill the chiefs and rule the islands; your uncle Kalaniopuu has died and the Big Island is divided between you and your cousin Keoua. Beyond the channel lie Maui, Oahu and Kauai, each with a king of its own." + NL + "Your people are the finest seafarers on earth and the war canoes of Kona are many. Build the heiau of Puukohola, win the Big Island, then cross the channels one by one. The islands have never had one ruler. Be the first.",
   pedia="Kamehameha I (c. 1758-1819) was a chief of Kohala and Kona on the Big Island who, after the death of his uncle Kalaniopuu in 1782, fought his cousin Keoua for the island, defeated him in 1791, took Maui and Molokai in 1790 and 1794 and Oahu at the battle of Nuuanu in 1795. Kauai submitted by treaty in 1810, and the Kingdom of Hawaii was his." + NL + "He had met Cook's ships in 1779 and used Western arms and advisers without surrendering the kapu system; his law of the splintered paddle protected non-combatants. The scenario starts in 1778 with the Big Island still divided.",
   cities=['Kawaihae', 'Kailua', 'Kealakekua', 'Honaunau', 'Keauhou', 'Holualoa', 'Kapaau', 'Waimea', 'Waipio', 'Lapakahi', 'Honokohau', 'Kukuihaele'],
   lines={
    'FIRSTGREETING': ["I am Kamehameha of Kona. The channel is wide, but my canoes are many. Who are you?", "Welcome to Kawaihae. Sit, and tell me of your island.", "A stranger from the sea. Speak."],
    'GREETING': ["Speak.", "Kona listens.", "Yes?"],
    'GOODBYE': ["Fair winds.", "Until the next council.", "Go."],
    'DECLAREWAR': ["Then the canoes sail. You have chosen this.", "War. The islands will have one ruler, and it will not be you.", "So be it."],
    'ATTACKED': ["You attack Kona? The prophecy did not mention you.", "Good. Now every canoe on the coast has a purpose.", "Treachery. The gods of Puukohola have seen it.", "Come, then. We have fought bigger."],
    'DEFEATED': ["Kona falls. The islands will remember who nearly united them.", "You hold the coast. The volcanoes hold you.", "The paddle is splintered. Finish it."],
    'WINWAR': ["The channel is mine. Go home.", "Kona stands."],
    'LOSEWAR': ["Peace. The fishponds need tending.", "Agreed.", "A truce, then."],
    'TRADE_YES': ["Agreed.", "Yes. Fair.", "Done."],
    'TRADE_NO': ["No.", "That is not an exchange.", "Refused."],
    'TRADEREQUEST': ["Kona offers this.", "A trade between chiefs.", "Consider it."],
    'DEMANDTRIBUTE': ["A gift would keep the canoes ashore.", "Pay.", "Tribute."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Good."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Do not threaten Kona.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["Kona pays nobody.", "No."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
 'HILO': dict(leader='Keoua', civ_long='The Chiefdom of Hilo, Puna and Kau', civ_short='Hilo', adj='Hilo', trait_short='Warriors of the Lua',
   trait='Units fight at full strength when damaged. +1 [ICON_CULTURE] Culture from Fishing Boats and +2 from Atolls.',
   dawn="Keoua Kuahuula, son of the late king Kalaniopuu, lord of Hilo, Puna and Kau on the windward side of the Big Island. Your father's kingdom has been cut in two: the war god and the west went to your cousin Kamehameha, the land and the east to you. The rain falls on your valleys, the lava flows through your districts, and your warriors are the best in the islands." + NL + "Kona will come for you. Hold Hilo, make the lava fields of Kau a trap, and remember that the gods of Kilauea are yours. The Big Island has room for one king, and your father was the last one.",
   pedia="Keoua Kuahuula (died 1791) was a son of Kalaniopuu, king of the Big Island, and the rival of his cousin Kamehameha for the island after 1782. He held Kau, Puna and Hilo through nine years of war; in 1790 a third of his army was killed by an eruption of Kilauea as it crossed the volcano." + NL + "In 1791 he was invited to the dedication of the heiau of Puukohola and killed on landing, with his companions, as the sacrifice that consecrated the temple. His death ended the war for the Big Island.",
   cities=['Hilo', 'Waiohinu', 'Kalapana', 'Laupahoehoe', 'Keaau', 'Pahoa', 'Naalehu', 'Punaluu', 'Honomu', 'Kapoho', 'Pepeekeo', 'Kaimu'],
   lines={
    'FIRSTGREETING': ["I am Keoua, son of Kalaniopuu, lord of Hilo. If you come from Kona, say so now.", "Welcome to the windward side. The rain is ours and so is the land.", "A stranger. Speak."],
    'GREETING': ["Yes?", "Hilo listens.", "Speak."],
    'GOODBYE': ["Go with the rain.", "Farewell.", "Until next time."],
    'DECLAREWAR': ["Then the lua masters will have work.", "War. Kilauea will take her share.", "So be it."],
    'ATTACKED': ["You attack Hilo? My father's land does not fall to strangers.", "The warriors of Puna are coming. Count them.", "Treachery. Pele has seen it.", "Come, then."],
    'DEFEATED': ["Hilo falls. Tell Kona it took him long enough.", "You hold the east. The lava will hold you.", "My father's kingdom ends here."],
    'WINWAR': ["The windward side is free.", "Go home."],
    'LOSEWAR': ["Peace. The taro needs planting.", "Agreed.", "A truce."],
    'TRADE_YES': ["Agreed.", "Yes.", "Done."],
    'TRADE_NO': ["No.", "That is not fair.", "Refused."],
    'TRADEREQUEST': ["Hilo offers this.", "A trade.", "Consider it."],
    'DEMANDTRIBUTE': ["A gift would be wise.", "Pay.", "Tribute."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Good."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Do not threaten Hilo.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["Hilo pays nobody.", "No."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
 'MAUI': dict(leader='Kahekili', civ_long='The Kingdom of Maui', civ_short='Maui', adj='Maui', trait_short='The Tattooed King',
   trait='Melee units cost 50% less maintenance. All units require 25% less experience for their promotions.',
   dawn="Kahekili, king of Maui, Lanai and Kahoolawe, tattooed black on one side of your body in the image of the thunder god. Molokai is yours in all but name, and the king of Oahu is a child you placed on the throne. Only the Big Island, across the channel of Alenuihaha, has ever stood against you." + NL + "Your warriors are the most feared in the islands and your lineage runs to every court. Take Oahu outright, hold the channel, and settle the question of who rules the archipelago before the young chief of Kona does.",
   pedia="Kahekili II (c. 1737-1794) was king of Maui from 1766, the dominant ruler of the islands when Cook arrived. He conquered Oahu in 1783 after Kahahana, whom he had installed there, turned against him, ruled Maui, Molokai, Lanai and Oahu together and twice fought Kamehameha to a standstill." + NL + "He was said to be tattooed black on one side from head to foot, like the thunder god Kanehekili, and some traditions name him Kamehameha's real father. His kingdom broke up after his death at Waikiki in 1794.",
   cities=['Wailuku', 'Lahaina', 'Hana', 'Kahului', 'Kihei', 'Makawao', 'Kula', 'Kaupo', 'Kipahulu', 'Kahakuloa', 'Olowalu', 'Honokowai'],
   lines={
    'FIRSTGREETING': ["I am Kahekili, king of Maui. Half the islands answer to me already. Which half are you?", "Welcome to Wailuku. Look at the tattoo, and remember it.", "A stranger. Speak quickly."],
    'GREETING': ["Speak.", "Maui listens.", "Well?"],
    'GOODBYE': ["Go.", "Until next time.", "Farewell."],
    'DECLAREWAR': ["Then you will learn what Oahu learned.", "War. My warriors have been idle too long.", "So be it."],
    'ATTACKED': ["You attack Maui? Kanehekili will answer you.", "The warriors of Wailuku are coming. All of them.", "Treachery. I expected it.", "Come, then."],
    'DEFEATED': ["Maui falls. Enjoy the islands; they do not stay won.", "You hold Wailuku. You will not hold my people.", "The thunder god is quiet today."],
    'WINWAR': ["Maui is secure. Go.", "The channel is mine."],
    'LOSEWAR': ["Peace. For now.", "Agreed.", "A truce."],
    'TRADE_YES': ["Agreed.", "Yes.", "Done."],
    'TRADE_NO': ["No.", "Maui is not a market.", "Refused."],
    'TRADEREQUEST': ["Maui offers this.", "A trade.", "Consider it."],
    'DEMANDTRIBUTE': ["Pay, and keep your island.", "Tribute.", "A gift for the king of Maui."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Good."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Threaten Maui? Amusing.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["Maui pays nobody.", "No."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
 'OAHU': dict(leader='Kahahana', civ_long='The Kingdom of Oahu', civ_short='Oahu', adj='Oahu', trait_short='Bays of the Gathering Place',
   trait='All coastal cities receive a free Harbor. Units may cross Mountains after the first Great General is earned, taking 50 HP damage if they end a turn on a Mountain.',
   dawn="Kahahana, king of Oahu, raised at the court of Maui and placed on the throne by Kahekili, who now wants his price. Your island is the richest of them all: the fishponds of Puuloa, the taro of Nuuanu, the bays of Waikiki and Waianae, and the gathering place of every canoe in the archipelago." + NL + "Kahekili will not wait long. Build harbours in every bay, fill the fishponds, keep the priests of Kaneohe on your side, and make Oahu too strong to be anyone's gift.",
   pedia="Kahahana (died c. 1785) was king of Oahu from 1773, chosen by the chiefs of the island but raised on Maui by Kahekili, who demanded the lands of Kualoa and the sacred whale-ivory of the shore as his price. Kahahana refused, was persuaded by a rival to execute his own high priest Kaopulupulu, and in 1783 Kahekili invaded Oahu and took it." + NL + "Kahahana hid in the mountains for two years before he was betrayed and killed. Oahu, the gathering place, was the prize of every war of the period.",
   cities=['Waikiki', 'Kou', 'Kailua', 'Kaneohe', 'Waianae', 'Ewa', 'Waialua', 'Nuuanu', 'Manoa', 'Kahuku', 'Hauula', 'Kualoa'],
   lines={
    'FIRSTGREETING': ["I am Kahahana, king of Oahu. Every canoe in the islands stops here. Yours too, it seems.", "Welcome to Waikiki. The fishponds are full; eat.", "A stranger. Speak."],
    'GREETING': ["Yes?", "Oahu listens.", "Speak."],
    'GOODBYE': ["Fair winds.", "Farewell.", "Until next time."],
    'DECLAREWAR': ["Then the bays close to you.", "War. Oahu is nobody's gift.", "So be it."],
    'ATTACKED': ["You attack Oahu? Kahekili tried that too.", "The pali will hold you. It always has.", "Treachery. The priests warned me.", "Come, then."],
    'DEFEATED': ["Oahu falls. Everyone wants the gathering place; nobody keeps it.", "You hold the bays. The mountains are mine still.", "Tell Kahekili he was right about you."],
    'WINWAR': ["Oahu is free.", "Go home."],
    'LOSEWAR': ["Peace. The fishponds need me.", "Agreed.", "A truce."],
    'TRADE_YES': ["Agreed. The harbour is open.", "Yes.", "Done."],
    'TRADE_NO': ["No.", "That is not a trade.", "Refused."],
    'TRADEREQUEST': ["Oahu offers this.", "A trade.", "Consider it."],
    'DEMANDTRIBUTE': ["A gift for the harbour would be wise.", "Pay.", "Tribute."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Good."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Do not threaten Oahu.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["Oahu pays nobody.", "No."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
 'KAUAI': dict(leader='Kamakahelei', civ_long='The Kingdom of Kauai and Niihau', civ_short='Kauai', adj='Kauai', trait_short='The Unconquered Island',
   trait='+20% [ICON_STRENGTH] Combat Strength against civilizations with more cities than you.',
   dawn="Kamakahelei, ruling chiefess of Kauai and Niihau, the oldest islands, the farthest from the rest. A hundred miles of open sea guard your valleys, and no king from the east has ever crossed them in force. Your husband Kaeo commands the warriors; the land, the taro valleys of Wailua and Hanalei and the great canyon of Waimea, is yours." + NL + "The chiefs of the east will come, sooner or later, across the worst channel in the islands. Fill the valleys, fortify the beaches, and let the sea fight for you. Kauai has never been taken. Keep it so.",
   pedia="Kamakahelei (c. 1730-1794) was the ruling chiefess of Kauai and Niihau when Cook's ships anchored at Waimea in January 1778, the first Hawaiian ruler Europeans met; her husband Kaeokulani, a Maui chief, shared the rule and led the warriors. Their son Kaumualii was the last king of Kauai." + NL + "Kauai was the one island Kamehameha never conquered: his invasion fleet of 1796 was wrecked in the channel and the second, in 1804, was destroyed by an epidemic before it sailed. Kaumualii ceded the island by treaty in 1810.",
   cities=['Wailua', 'Waimea', 'Hanalei', 'Koloa', 'Hanapepe', 'Kapaa', 'Kekaha', 'Anahola', 'Haena', 'Kalalau', 'Lihue', 'Kilauea'],
   lines={
    'FIRSTGREETING': ["I am Kamakahelei of Kauai. You crossed the channel, so you are either brave or lost. Which?", "Welcome to Wailua. Few from the east reach it.", "A stranger on the oldest island. Speak."],
    'GREETING': ["Speak.", "Kauai listens.", "Yes?"],
    'GOODBYE': ["May the channel be kind to you.", "Farewell.", "Until next time."],
    'DECLAREWAR': ["Then come across the channel. Others have tried.", "War. The sea is on our side.", "So be it."],
    'ATTACKED': ["You attack Kauai? The channel has drowned better fleets.", "Kaeo is gathering the warriors. You will meet them on the beach.", "Treachery. The old island remembers.", "Come, then."],
    'DEFEATED': ["Kauai falls. No one has ever said that before.", "You hold the valleys. The sea will take them back.", "The oldest island ends with me."],
    'WINWAR': ["Kauai stands, as it always has.", "Go home across the channel."],
    'LOSEWAR': ["Peace. The taro is waiting.", "Agreed.", "A truce."],
    'TRADE_YES': ["Agreed.", "Yes.", "Done."],
    'TRADE_NO': ["No.", "That is not fair.", "Refused."],
    'TRADEREQUEST': ["Kauai offers this.", "A trade.", "Consider it."],
    'DEMANDTRIBUTE': ["A gift would be wise.", "Pay.", "Tribute."],
    'LETSHEARIT': ["Speak.", "Go on.", "Listening."],
    'AGREE_SHORT': ["Agreed.", "Yes.", "Good."],
    'DISAGREE_SHORT': ["No.", "Never.", "No."],
    'WARBLUFF': ["Do not threaten Kauai.", "Careful.", "Think again."],
    'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["Kauai pays nobody.", "No."], 'TRADE_NEEDMORE': ["Not enough.", "More."],
   }),
}
WONDERS_EN = {'TXT_KEY_FEATURE_KILIMANJARO': 'Mauna Kea', 'TXT_KEY_FEATURE_VOLCANO': 'Kilauea', 'TXT_KEY_FEATURE_CRATER': 'Haleakala', 'TXT_KEY_FEATURE_GIBRALTAR': 'Leahi',
              'TXT_KEY_FEATURE_MESA': 'Waimea Canyon', 'TXT_KEY_FEATURE_MT_KAILASH': 'Kalaupapa', 'TXT_KEY_FEATURE_ULURU': 'Keahiakawelo'}
RELIGIONS_EN = {'BUDDHISM': 'Kane', 'CHRISTIANITY': 'Ku', 'CONFUCIANISM': 'Lono', 'HINDUISM': 'Kanaloa', 'ISLAM': 'Pele', 'JUDAISM': 'Hina', 'SHINTO': 'Laka', 'SIKHISM': 'Haumea', 'TAOISM': 'Papa', 'TENGRIISM': 'Kamapuaa', 'ZOROASTRIANISM': 'Kukailimoku', 'ORTHODOXY': 'Kuula', 'PROTESTANTISM': 'Kamohoalii'}
RELIGION_KEY = {r: 'TXT_KEY_RELIGION_' + ('CATHOLICISM' if r == 'CHRISTIANITY' else r) for r in RELIGIONS_EN}
EXTRA_EN = {'TXT_KEY_HI1778_TITLE': 'Hawaii 1778',
            'TXT_KEY_HI1778_INTRO': 'The Hawaiian Islands in 1778, the year the first ships appear. Five chiefdoms, three lesser islands, no iron and no horses. Build your island, learn the sea, cross the channels, unite the archipelago. Win by conquest.'}
POLICY_NAMES = {'CEREMONY': ('Ceremony', 'Церемония'), 'TAPU': ('Kapu', 'Капу'), 'POWHIRI': ('Hookupu', 'Хоокупу'), 'SURFING': ('Heenalu', 'Хеэналу'), 'KAVA': ('Awa', 'Ава'), 'LUAU': ('Luau', 'Луау'), 'THE_ARTS': ('The Arts', 'Искусства'), 'HULA': ('Hula', 'Хула'), 'TIKI': ('Kii', 'Кии'), 'RONGO': ('Oli', 'Оли'), 'TAPACLOTH': ('Kapa', 'Капа'), 'STONECARVING': ('Pohaku', 'Похаку'), 'HONOR': ('Honor', 'Честь'), 'POI': ('Poi', 'Пои'), 'ARIKI': ('Alii', 'Алии'), 'HEALING': ('Kahuna Healing', 'Исцеление кахуна'), 'HAKA': ('Haa', 'Хаа'), 'MANA': ('Mana', 'Мана'),
                'FAITH': ('Akua', 'Акуа'), 'SHRINES': ('Heiau', 'Хеиау'), 'MANDATE': ('Makahiki', 'Макахики'), 'THEOCRACY': ('Luakini', 'Луакини'), 'TOLERANCE': ('Aumakua', 'Аумакуа'), 'REFORMATION': ('Kahuna Nui', 'Кахуна-нуи'),
                'TRADE': ('Auhau', 'Аухау'), 'ROUTES': ('Alaloa', 'Алалоа'), 'POSTS': ('Kuapo', 'Куапо'), 'MERCHANTS': ('Konohiki', 'Конохики'), 'MARKETS': ('Waiwai', 'Ваивай'), 'LUXURIES': ('Ahupuaa', 'Ахупуаа')}
POLICY_PEDIA = {'CEREMONY': ('Ceremonies are the rituals a society uses to mark important events and reinforce its bonds: the kapu that set things apart as sacred, the gift-giving of the hookupu, the awa drunk at every council, the games and surfing of the makahiki season, the luau feast. Whatever their degree of sacredness, they held the islands together.', 'Церемонии это обряды, которыми общество отмечает важные события и скрепляет свои узы: капу, объявлявшие вещи священными, дарение хоокупу, ава на каждом совете, игры и сёрфинг сезона макахики, пир луау. Какой бы ни была их святость, они держали острова вместе.'), 'THE_ARTS': ('Art is a physical work of the imagination that lifts an everyday object above its use. Bark cloth clothes a body; beaten and printed as kapa it becomes art. The hula, the chants of the oli that carried genealogy and knowledge, the carved kii and the stone images of the heiau all sanctified their objects with mana.', 'Искусство это воплощённая работа воображения, которая поднимает обычную вещь над её пользой. Ткань из луба одевает тело; отбитая и расписанная как капа, она становится искусством. Хула, песнопения оли, хранившие родословные и знания, резные кии и каменные изображения хеиау наполняли свои предметы маной.'), 'HONOR': ("In the islands a chief's standing rested on mana and on the warriors who followed him. Honor means an army trained from youth in the lua, led by the alii, healed by the kahuna, and fed by the poi that the war canoes carried across the channels.", 'На островах положение вождя держалось на мане и на воинах, которые шли за ним. Честь это войско, с юности обученное луа, ведомое алии, исцеляемое кахуна и кормимое пои, которое боевые каноэ везли через проливы.'),
                'FAITH': ('The akua were the gods of the islands: Kane the creator, Ku of war, Lono of harvest, Kanaloa of the sea, and the family aumakua that watched over each household. Their heiau rose on every coast, their kahuna read the omens, and the makahiki months of Lono closed the year with tribute and games.', 'Акуа были богами островов: Кане-творец, Ку войны, Лоно урожая, Каналоа моря и семейные аумакуа, хранившие каждый дом. Их хеиау стояли на каждом берегу, их кахуна читали знамения, а месяцы макахики, посвящённые Лоно, закрывали год данью и играми.'),
                'TRADE': ('The islands had no money, but they had wealth: the auhau tribute of pigs, kapa and feathers brought to the chief at the makahiki, the konohiki who ran each ahupuaa, the trails of the alaloa that joined the districts, and the barter of the uplands with the shore.', 'На островах не было денег, но было богатство: дань аухау свиньями, капой и перьями, приносимая вождю на макахики, конохики, правившие каждым ахупуаа, тропы алалоа, соединявшие округа, и мена нагорий с побережьем.')}
MOODS = ('_NEUTRAL', '_HAPPY', '_ANGRY')

def emit(lang, FF, WONDERS, EXTRA, CS):
    rows = []
    def rep(tag, text): rows.append(f'    <Replace Tag="{tag}" Text="{html.escape(text, quote=True)}" />')
    for k, f in FF.items():
        c = DONOR[k]['civ']; prefix = DONOR[k]['prefix']; leader_key = DONOR[k]['leader_key']; trait_key = DONOR[k]['trait_key']
        rep(leader_key, f['leader']); rep(leader_key + '_PEDIA', f['pedia'])
        rep(f'TXT_KEY_CIV_{c}_DESC', f['civ_long']); rep(f'TXT_KEY_CIV_{c}_SHORT_DESC', f['civ_short']); rep(f'TXT_KEY_CIV_{c}_ADJECTIVE', f['adj'])
        rep(f'TXT_KEY_CIV5_DAWN_{c}_TEXT', f['dawn']); rep(trait_key + '_SHORT', f['trait_short']); rep(trait_key, f['trait'])
        rep(f'TXT_KEY_HI1778_BLURB_{k}', f['dawn'])
        for i, city in enumerate(f['cities']): rep(f'TXT_KEY_CITY_NAME_HI1778_{k}_{i}', city)
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
    for r, name in (RELIGIONS_EN if lang == 'en' else RU_RELIGIONS).items(): rep(RELIGION_KEY[r], name)   # the stock religions become the cults of the Hawaiian gods
    rep('TXT_KEY_RELIGION_CHRISTIANITY', (RELIGIONS_EN if lang == 'en' else RU_RELIGIONS)['CHRISTIANITY'])
    for tag, text in paradise_policies.text_rows('HI1778', POLICY_NAMES, lang, POLICY_PEDIA): rep(tag, text)   # the Paradise Found policy tree under local names
    for key, mtype, trait, name, city in CS:
        rep(f'TXT_KEY_CITYSTATE_HI_{key}', name); rep(f'TXT_KEY_CITY_HI_{key}', city)
    for u in uniques.UNITS + uniques.BUILDINGS:
        kind = 'UNIT' if u in uniques.UNITS else 'BUILDING'; t = f'{kind}_HI1778_{u["key"]}'
        name, help_, strategy, pedia = (u['name'], u['help'], u['strategy'], u['pedia']) if lang == 'en' else RU_UNIQUES[u['key']]
        if u['base']:
            rep(f'TXT_KEY_{t}', name); rep(f'TXT_KEY_{t}_HELP', help_); rep(f'TXT_KEY_{t}_STRATEGY', strategy); rep(f'TXT_KEY_CIV5_HI1778_{u["key"]}_TEXT', pedia)
        else:
            for key in u['rename']: rep(key, name)
            for key, text in (u.get('texts', {}) if lang == 'en' else RU_RENAMES.get(u['key'], {})).items(): rep(key, text)   # help, strategy, civilopedia of the donor's unique
    return rows
rows_en = emit('en', EN, WONDERS_EN, EXTRA_EN, CITY_STATES)
rows_ru = emit('ru', RU, RU_WONDERS, RU_EXTRA, [(k, m, t, RU_CS[k][0], RU_CS[k][1]) for k, m, t, n, c in CITY_STATES])
xml = ('<?xml version="1.0" encoding="utf-8"?>\n<!-- Hawaii 1778: the five chiefdoms on their donor civilizations, city-states, natural wonders, uniques, load screen (EN + RU). -->\n<GameData>\n  <Language_en_US>\n'
       + '\n'.join(rows_en) + '\n  </Language_en_US>\n  <Language_RU_RU>\n' + '\n'.join(rows_ru) + '\n  </Language_RU_RU>\n</GameData>\n')
open(os.path.join(UI, 'Hawaii1778_Text.xml'), 'w', encoding='utf-8').write(xml)

# ---- database rows: city lists, city-states, colours, tech cap, calendar
def rgb(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
lx = ['<?xml version="1.0" encoding="utf-8"?>', '<!-- Hawaii 1778 database rows: Hawaiian city lists for the five donor civilizations, three city-states, colours, tech cap, one turn = one year from 1778. -->', '<GameData>', '  <Civilization_CityNames>']
for k, f in EN.items():
    c = DONOR[k]['civ']; lx.append(f'    <Delete CivilizationType="CIVILIZATION_{c}" />')
    for i in range(len(f['cities'])): lx.append(f'    <Row><CivilizationType>CIVILIZATION_{c}</CivilizationType><CityName>TXT_KEY_CITY_NAME_HI1778_{k}_{i}</CityName></Row>')
lx += ['  </Civilization_CityNames>', '  <Colors>']
for k, (icon, bg) in COLORS.items():
    for suf, hx in (('ICON', icon), ('BG', bg)):
        r, g, b = rgb(hx); lx.append(f'    <Row><Type>COLOR_PLAYER_HI1778_{k}_{suf}</Type><Red>{r:.3f}</Red><Green>{g:.3f}</Green><Blue>{b:.3f}</Blue><Alpha>1</Alpha></Row>')
lx += ['  </Colors>', '  <PlayerColors>']
for k in COLORS: lx.append(f'    <Row><Type>PLAYERCOLOR_HI1778_{k}</Type><PrimaryColor>COLOR_PLAYER_HI1778_{k}_ICON</PrimaryColor><SecondaryColor>COLOR_PLAYER_HI1778_{k}_BG</SecondaryColor><TextColor>COLOR_PLAYER_WHITE_TEXT</TextColor></Row>')
lx += ['  </PlayerColors>', '  <Civilizations>']
for k in COLORS: lx.append(f'    <Update><Where Type="CIVILIZATION_{DONOR[k]["civ"]}" /><Set DefaultPlayerColor="PLAYERCOLOR_HI1778_{k}" /></Update>')
lx += ['  </Civilizations>', '  <MinorCivilizations>']
MCOL = ['PLAYERCOLOR_MINOR_LIGHT_PURPLE', 'PLAYERCOLOR_MINOR_LIGHT_BLUE', 'PLAYERCOLOR_MINOR_MIDDLE_CYAN']
for i, (key, mtype, trait, name, city) in enumerate(CITY_STATES):
    tk = f'TXT_KEY_CITYSTATE_HI_{key}'
    lx.append(f'    <Row><Type>{mtype}</Type><Description>{tk}</Description><Civilopedia>{tk}</Civilopedia><ShortDescription>{tk}</ShortDescription><Adjective>{tk}</Adjective><ArtDefineTag>ART_DEF_CIVILIZATION_MINOR</ArtDefineTag><DefaultPlayerColor>{MCOL[i]}</DefaultPlayerColor><ArtStyleType>ARTSTYLE_ASIAN</ArtStyleType><ArtStyleSuffix>_ASIA</ArtStyleSuffix><ArtStylePrefix>ASIAN </ArtStylePrefix><MinorCivTrait>{trait}</MinorCivTrait></Row>')
lx += ['  </MinorCivilizations>', '  <MinorCivilization_CityNames>']
for key, mtype, trait, name, city in CITY_STATES: lx.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><CityName>TXT_KEY_CITY_HI_{key}</CityName></Row>')
lx += ['  </MinorCivilization_CityNames>', '  <MinorCivilization_Flavors>']
for key, mtype, trait, name, city in CITY_STATES:
    for fl, v in (('FLAVOR_CITY_DEFENSE', 8), ('FLAVOR_DEFENSE', 8), ('FLAVOR_GROWTH', 5), ('FLAVOR_GOLD', 5), ('FLAVOR_PRODUCTION', 5)):
        lx.append(f'    <Row><MinorCivType>{mtype}</MinorCivType><FlavorType>{fl}</FlavorType><Flavor>{v}</Flavor></Row>')
lx += ['  </MinorCivilization_Flavors>',
       '  <!-- Development stops at the end of the Classical era: no pikes, crossbows or castles, no Astronomy, no caravels, no Printing Press and no World Congress. The techs stay in the tree but cannot be researched. -->',
       '  <Technologies>'] + [f'    <Update><Where Era="{era}" /><Set Disable="true" /></Update>' for era in ('ERA_MEDIEVAL', 'ERA_RENAISSANCE', 'ERA_INDUSTRIAL', 'ERA_MODERN', 'ERA_POSTMODERN', 'ERA_FUTURE')] + ['    <Update><Where Type="TECH_GUILDS" /><Set Disable="false" /></Update>   <!-- the one Medieval technology: trading posts, the gold of the islands -->', '  </Technologies>',

       '  <!-- Calendar (Standard and Quick speeds): one turn = one year from 1778 on Standard speed; the game ends by time in 2078 (turn 300). -->',
       '  <Defines>', '    <Update><Where Name="START_YEAR" /><Set Value="1778" /></Update>', '  </Defines>',
       '  <GameSpeed_Turns>'] + sum([[f'    <Delete GameSpeedType="{sp}" />', f'    <Row><GameSpeedType>{sp}</GameSpeedType><MonthIncrement>12</MonthIncrement><TurnsPerIncrement>300</TurnsPerIncrement></Row>'] for sp in ('GAMESPEED_STANDARD', 'GAMESPEED_QUICK')], []) + [
       '  </GameSpeed_Turns>', '</GameData>', '']
open(os.path.join(UI, 'Hawaii1778_Rules.xml'), 'w', encoding='utf-8').write('\n'.join(lx))
open(os.path.join(UI, 'Hawaii1778_Uniques.sql'), 'w', encoding='utf-8').write(uniques.sql())
open(os.path.join(UI, 'Hawaii1778_Policies.sql'), 'w', encoding='utf-8').write(paradise_policies.sql('HI1778'))
build_policy_screen.build(UI, [(f'HI1778_{k}', n, tex, f'TXT_KEY_POLICY_BRANCH_HI1778_{k}_HELP', f'TXT_KEY_POLICY_BRANCH_HI1778_{k}_CAP') for (k, tex), n in zip(paradise_policies.BRANCHES, ('Ceremony', 'Arts', 'Honor', 'Faith', 'Trade'))], 'Hawaii 1778:')
print(f'wrote Hawaii1778_Text.xml ({len(rows_en)} EN + {len(rows_ru)} RU rows), Hawaii1778_Rules.xml and Hawaii1778_Uniques.sql')
