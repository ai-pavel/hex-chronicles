#!/usr/bin/env python3
"""Generate Russia1918_Text.xml (Language_en_US + Language_RU_RU overrides for the six factions, the thirteen city-states, the events and the
unique units and buildings) and Russia1918_Uniques.sql (text/uniques.py)."""
import os, html, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ru import RU, RU_CS, RU_EXTRA, RU_UNIQUES
import uniques
from events_text import EVENTS
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
DIALOG_KEYS = [l.strip() for l in open(os.path.join(XMLDIR, 'LEADER_DIALOG_KEYS.txt')) if l.strip()]
KEYS = lambda prefix: [k for k in DIALOG_KEYS if k.startswith(prefix)]
OUT = os.path.join(HERE, '..', 'ui', 'Russia1918_Text.xml')
NL = '[NEWLINE][NEWLINE]'
F = {}
F['RED'] = dict(prefix='TXT_KEY_LEADER_CATHERINE_', leader_key='TXT_KEY_LEADER_CATHERINE', civ='RUSSIA', trait_key='TXT_KEY_TRAIT_STRATEGIC_RICHES',
    leader='Vladimir Lenin', civ_long='Russian Socialist Federative Soviet Republic', civ_short='Russian SFSR', adj='Soviet', trait_short='Arsenal of the Revolution',
    trait='Horses and Iron provide double quantity, and tiles with a strategic resource +1 [ICON_PRODUCTION] Production. The factories of Petrograd, Tula and the Urals arm the Red Army.',
    dawn="Vladimir Ilyich, the revolution holds Moscow, Petrograd and the heart of the country, and nothing else is certain. The Czechoslovak Legion has seized the Trans-Siberian in a fortnight, the Don Cossacks have risen, the Germans sit in Kiev under a hetman of their choosing, and the Allies are landing in the north." + NL + "You have what the Whites do not: the railways, the arsenals and the manpower of central Russia. Hold the Volga, turn the Red Guards into an army, and strike the fronts one at a time before they can join hands. The Whites are many, but they are far apart.",
    pedia="Vladimir Ilyich Ulyanov, Lenin (1870-1924), led the Bolshevik seizure of power in October 1917 and chaired the Council of People's Commissars through the Civil War. He signed the Brest-Litovsk peace to save the revolution, built the Red Army with Trotsky and held the centre while every border province fell away." + NL + "By 1921 his government had defeated the Whites, lost the war with Poland and faced a country in ruins; the New Economic Policy was his answer. He suffered his first stroke in 1922 and died in January 1924.",
    lines={
        'FIRSTGREETING': ["I am Lenin. The Council of People's Commissars speaks for the workers and peasants of Russia; who speaks for you?", "Welcome to Moscow. The old order is gone, and you are talking to what replaced it.", "The Soviet Republic receives you. Be brief, there is a war on."],
        'GREETING': ["Comrade?", "Yes. What is it?", "The Soviet government is listening."],
        'GOODBYE': ["Until the next time.", "We have work to do.", "Goodbye."],
        'DECLAREWAR': ["The revolution will defend itself. You have chosen the wrong side of history.", "Then the Red Army will settle this.", "So be it. Every worker is a soldier now."],
        'ATTACKED': ["You attack the Soviet Republic? Then you will learn what a people in arms can do.", "The world bourgeoisie sends another hireling. We have beaten better.", "Very well. The workers of your own country will judge you.", "You will not take Moscow. Nobody takes Moscow."],
        'DEFEATED': ["You have won a battle against history. History will have the last word.", "Take the cities. The idea does not surrender.", "The revolution is not finished. It has only changed its address."],
        'WINWAR': ["The counter-revolution is broken. Now we build.", "The Red Army has done what the Whites said was impossible."],
        'LOSEWAR': ["A breathing space. We accept.", "Peace, for now. Brest-Litovsk taught us patience.", "Let the guns rest. We will need them later."],
        'TRADE_YES': ["Agreed. The Republic honours its bargains, whatever they say in Paris.", "Yes. Grain and iron do not care about ideology.", "Done."],
        'TRADE_NO': ["No. The Republic is not a shop.", "Unacceptable.", "We cannot."],
        'TRADEREQUEST': ["A proposal from the Soviet government. Purely practical.", "Business, nothing more.", "Consider this."],
        'DEMANDTRIBUTE': ["A contribution to the revolution, in advance.", "Pay, and we overlook your past.", "The Republic requires this."],
        'LETSHEARIT': ["Go on.", "Speak.", "I am listening."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Out of the question.", "Refused."],
        'WARBLUFF': ["Threats? The Entente threatens us daily.", "Do not test the Red Army.", "Careful."],
        'TRIBUTE_YES': ["Take it. It costs us less than a war.", "Very well."], 'TRIBUTE_NO': ["The Republic pays nobody.", "No."],
        'TRADE_NEEDMORE': ["Not enough.", "You can do better than that.", "Add something."],
    })
F['SOUTH'] = dict(prefix='TXT_KEY_LEADER_BISMARCK_', leader_key='TXT_KEY_LEADER_BISMARCK', civ='GERMANY', trait_key='TXT_KEY_TRAIT_CONVERTS_LAND_BARBARIANS',
    leader='Anton Denikin', civ_long='Armed Forces of South Russia', civ_short='White South', adj='White', trait_short="Officers' Army",
    trait='When a land unit defeats a barbarian unit inside an encampment there is a 67% chance it joins your army. Land unit maintenance reduced by 25%.',
    dawn="General Denikin, the Volunteer Army is nine thousand officers, cadets and students in the Don steppe, and the Don Cossacks of Ataman Krasnov hold Novocherkassk and Rostov with German blessing. Kuban is Red, Tsaritsyn is Red, and between you and the Siberians lies the whole of the Volga." + NL + "Your soldiers are the best in Russia and there are not enough of them. Take Ekaterinodar and the Kuban, bring the Cossack hosts into the fold, open the Black Sea ports to British tanks, and march on Moscow before the Reds learn how to fight.",
    pedia="Anton Ivanovich Denikin (1872-1947), a general of peasant stock, took command of the Volunteer Army after Kornilov's death in April 1918 and of the Armed Forces of South Russia from January 1919. His 1919 offensive reached Oryol, two hundred miles from Moscow, before Red cavalry and overstretched supply lines broke it." + NL + "He handed command to Wrangel after the Novorossiysk evacuation of March 1920 and spent the rest of his life in exile, writing a five-volume history of the Russian turmoil and refusing to serve the Germans in 1941.",
    lines={
        'FIRSTGREETING': ["General Denikin. I speak for Russia, one and indivisible; the people in Moscow speak for a party.", "Welcome to the Don. Here Russia is still Russia.", "The Armed Forces of South Russia receive you."],
        'GREETING': ["Yes?", "What brings you to the Don?", "Speak, I have a front to run."],
        'GOODBYE': ["God be with you.", "Farewell.", "Until we meet again."],
        'DECLAREWAR': ["Then it is war. We have been at war since 1917 anyway.", "You have chosen the Bolsheviks' side. You will share their fate.", "So be it."],
        'ATTACKED': ["You attack officers of the Russian army? You will regret it.", "One more enemy. Russia has survived worse.", "Very well. The Volunteers do not retreat without a fight.", "A stab in the back, while we fight the Reds. We will remember."],
        'DEFEATED': ["The army is beaten. Russia is not.", "Take the Don. The cause survives in exile.", "We leave the way we came: with our honour."],
        'WINWAR': ["Russia is whole again. Now to heal her.", "The Reds are finished. Thank God."],
        'LOSEWAR': ["A truce. We need to breathe.", "Peace, then. For now.", "Agreed, with a heavy heart."],
        'TRADE_YES': ["Agreed. Russia pays her debts.", "Yes.", "Acceptable."],
        'TRADE_NO': ["No.", "We cannot accept that.", "Impossible."],
        'TRADEREQUEST': ["A proposal from the South. We are honest partners.", "Russia offers this.", "Consider it."],
        'DEMANDTRIBUTE': ["The army needs boots and shells. You will provide them.", "Pay, or explain yourself to my Cossacks.", "A contribution to the Russian cause."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Please."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten Russian officers.", "You would not dare.", "Careful."],
        'TRIBUTE_YES': ["Take it, and leave us to the Reds.", "Very well."], 'TRIBUTE_NO': ["The Volunteer Army does not pay tribute.", "No."],
        'TRADE_NEEDMORE': ["Not enough.", "You can do better.", "Add something."],
    })
F['SIB'] = dict(prefix='TXT_KEY_LEADER_POCATELLO_', leader_key='TXT_KEY_LEADER_POCATELLO', civ='SHOSHONE', trait_key='TXT_KEY_TRAIT_GREAT_EXPANSE',
    leader='Alexander Kolchak', civ_long='Provisional All-Russian Government', civ_short='Siberia', adj='Siberian', trait_short='Endless Siberia',
    trait='Land units receive +15% [ICON_STRENGTH] Combat Strength in friendly territory, and move through forest in friendly territory as along a road. The taiga is home ground.',
    dawn="Admiral Kolchak, from Samara to Irkutsk the Czechoslovak Legion has thrown the Soviets off the Trans-Siberian in a fortnight. Komuch sits in Samara with its People's Army, the Siberian Government in Omsk, the Orenburg and Ural Cossacks guard the steppe, and in November the generals will make you Supreme Ruler." + NL + "Your land is endless and empty, your army is a railway and a few regiments, your supplies come from Vladivostok, five thousand miles away. Take the Volga crossings, link up with the Don, and bring the Supreme Ruler to Moscow before the winter.",
    pedia="Alexander Vasilyevich Kolchak (1874-1920), polar explorer and admiral of the Black Sea Fleet, was made Supreme Ruler of Russia by a coup in Omsk on 18 November 1918. His armies reached the Volga at Kazan and Samara in the spring of 1919 and then collapsed eastward along the Trans-Siberian." + NL + "Abandoned by the Czechoslovak Legion and handed to the Irkutsk revolutionaries, he was shot on 7 February 1920 and his body pushed under the ice of the Angara.",
    lines={
        'FIRSTGREETING': ["Admiral Kolchak, Supreme Ruler of Russia. The capital is in Omsk until Moscow is free.", "Welcome to Siberia. It is larger than you think.", "The All-Russian Government receives you."],
        'GREETING': ["Yes?", "Speak.", "What do you want of Siberia?"],
        'GOODBYE': ["Farewell.", "God keep you.", "Until next time."],
        'DECLAREWAR': ["You side with the Bolsheviks. Then you are my enemy.", "Very well. Siberia has swallowed armies before.", "So be it."],
        'ATTACKED': ["You attack the lawful government of Russia. You will answer for it.", "Another enemy. The taiga has room for all of them.", "A sailor does not strike his colours. Fight, then.", "You chose a poor moment. We will remember it."],
        'DEFEATED': ["Siberia is lost. Russia is not finished.", "Take Omsk. You will find it harder to keep.", "I have done my duty. Do yours."],
        'WINWAR': ["Russia is one again. The Supreme Ruler lays down his title.", "The Reds are broken. Now the hard part."],
        'LOSEWAR': ["A truce. Siberia needs to breathe.", "Peace, for now.", "Accepted."],
        'TRADE_YES': ["Agreed. Siberia has furs and gold enough.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "Siberia cannot afford that.", "Impossible."],
        'TRADEREQUEST': ["A proposal from Omsk.", "Siberia offers this.", "Consider it."],
        'DEMANDTRIBUTE': ["The Supreme Ruler requires a contribution.", "Pay, and keep your railway.", "You will provide this."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten the admiral.", "You would regret it.", "Careful."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["Siberia pays nobody.", "No."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "Siberia deserves better."],
    })
F['NORTH'] = dict(prefix='TXT_KEY_LEADER_ELIZABETH_', leader_key='TXT_KEY_LEADER_ELIZABETH', civ='ENGLAND', trait_key='TXT_KEY_TRAIT_OCEAN_MOVEMENT',
    leader='Nikolai Yudenich', civ_long='Northern Region and Northwestern Army', civ_short='Northern Region', adj='Northern', trait_short='Royal Navy Behind Us',
    trait='+2 [ICON_MOVES] Movement for all naval units. Influence with city-states degrades at half and recovers at twice the normal rate. The White Sea and the Baltic belong to the Allied fleets.',
    dawn="General Yudenich, the north is Murmansk and Arkhangelsk, British battalions, American infantry and a few thousand Russians of the Slavo-British Legion, with the Royal Navy behind you and the taiga in front. The Allies came to guard their war stores and stayed to fight the Bolsheviks." + NL + "Push down the Dvina and the Murmansk railway towards Vologda and Petrograd, and when the Baltic states break free, raise the Northwestern Army on the Estonian border for the drive on the old capital. The Allies will not stay forever; use them while they are here.",
    pedia="Nikolai Nikolayevich Yudenich (1862-1933), the most successful Russian commander of the World War, beat the Ottomans at Sarikamish and took Erzurum in 1916. In 1919 he led the Northwestern Army from Estonia to the suburbs of Petrograd, reaching Pulkovo Heights in October before Trotsky's counter-attack threw it back." + NL + "The army was interned and disbanded in Estonia; Yudenich died in exile in Nice. The separate Northern Region government in Arkhangelsk, under General Miller, fell in February 1920 after the Allies had gone.",
    lines={
        'FIRSTGREETING': ["General Yudenich. The Northwestern Army and the Allied Northern Region stand for Russia against the Bolsheviks.", "Welcome to Arkhangelsk. Mind the mud.", "The North receives you."],
        'GREETING': ["Yes?", "Speak.", "What news?"],
        'GOODBYE': ["Farewell.", "Good luck.", "Until next time."],
        'DECLAREWAR': ["You have chosen the Reds. The Royal Navy will have something to say about it.", "Then it is war.", "So be it."],
        'ATTACKED': ["You attack the Allied North? London and Paris are watching.", "Another enemy. The Navy has guns enough.", "Very well. We will fight.", "A mistake you will pay for."],
        'DEFEATED': ["The North is lost. We leave by sea, as we came.", "Take Arkhangelsk. Russia will remember who sold her.", "The army is finished. The cause is not."],
        'WINWAR': ["Petrograd is free. Russia is whole.", "The Reds are beaten. Thank God and the Navy."],
        'LOSEWAR': ["A truce. We accept.", "Peace, for now.", "Very well."],
        'TRADE_YES': ["Agreed. Allied stores for Russian timber.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "We cannot.", "Impossible."],
        'TRADEREQUEST': ["A proposal from the North.", "The Allies offer this.", "Consider it."],
        'DEMANDTRIBUTE': ["The army needs supplies. You will provide them.", "Pay, and the Navy stays out of your harbours.", "A contribution to the cause."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten us.", "Careful.", "You would regret it."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "The North pays nobody."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
    })
F['UKR'] = dict(prefix='TXT_KEY_LEADER_SELASSIE_', leader_key='TXT_KEY_LEADER_SELASSIE', civ='ETHIOPIA', trait_key='TXT_KEY_TRAIT_BONUS_AGAINST_TECH',
    leader='Pavlo Skoropadsky', civ_long='Ukrainian State', civ_short='Ukraine', adj='Ukrainian', trait_short='Spirit of the Haidamaks',
    trait='+20% [ICON_STRENGTH] Combat Strength against civilizations that have more cities than you.',
    dawn="Hetman Skoropadsky, you rule in Kiev under German bayonets: the richest provinces of the old empire, Odessa, Kharkov, the Donbass and Crimea, a treasury of grain, and an army that exists mostly on paper. In November the Germans will go home and the Directory, the Reds, Denikin and the Poles will all want what you hold." + NL + "Build a Ukrainian army while the occupation still shields you, decide between the Whites and the Poles, and keep the state alive through the winter of 1919. Nobody will do it for you.",
    pedia="Pavlo Skoropadsky (1873-1945), a lieutenant-general of the Imperial Russian army and descendant of an eighteenth-century hetman, was installed as Hetman of the Ukrainian State by a German-backed coup on 29 April 1918. His government minted money, opened universities and shipped grain west; its army and its popularity never caught up." + NL + "When Germany collapsed in November 1918 Petliura's Directory rose against him and he fled to Berlin in a German hospital train. He died in 1945, hit by an Allied bomb in Bavaria.",
    lines={
        'FIRSTGREETING': ["I am Hetman Skoropadsky. Ukraine is a state again, and it will remain one.", "Welcome to Kiev. The Germans are our guests, not our masters, whatever you have heard.", "The Ukrainian State receives you."],
        'GREETING': ["Yes?", "Speak.", "What does Ukraine owe this visit to?"],
        'GOODBYE': ["Farewell.", "God be with you.", "Until next time."],
        'DECLAREWAR': ["You want Ukrainian grain by force? Come and take it.", "Then it is war.", "So be it."],
        'ATTACKED': ["You attack Ukraine? Every neighbour has tried.", "Another enemy. We are used to it.", "Very well. The haidamaks will answer.", "You will find Ukraine harder to swallow than to invade."],
        'DEFEATED': ["Kiev has fallen before and risen before.", "Take the cities. The idea of Ukraine does not surrender.", "The Hetmanate is finished. Ukraine is not."],
        'WINWAR': ["Ukraine is secure. Now to build it.", "The enemy is beaten."],
        'LOSEWAR': ["A truce. Ukraine needs time.", "Peace, for now.", "Agreed."],
        'TRADE_YES': ["Agreed. Grain for guns is the oldest trade in Ukraine.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "Ukraine cannot afford that.", "Impossible."],
        'TRADEREQUEST': ["A proposal from Kiev.", "Ukraine offers this.", "Consider it."],
        'DEMANDTRIBUTE': ["The Hetmanate requires a contribution.", "Pay, and keep the peace.", "You will provide this."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten Ukraine.", "Careful.", "You would regret it."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "Ukraine pays nobody."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
    })
F['POL'] = dict(prefix='TXT_KEY_LEADER_CASIMIR_', leader_key='TXT_KEY_LEADER_CASIMIR', civ='POLAND', trait_key='TXT_KEY_TRAIT_SOLIDARITY',
    leader='Jozef Pilsudski', civ_long='Republic of Poland', civ_short='Poland', adj='Polish', trait_short='Miracle on the Vistula',
    trait='Great Generals are earned 50% faster and give nearby units 15% more [ICON_STRENGTH] Combat Strength.',
    dawn="Commandant Pilsudski, Poland does not yet exist; it will in November. Until then you have the Regency Council in Warsaw, the legion cadres and the certainty that the German occupation is ending and that neither Berlin nor Moscow will draw your borders for you." + NL + "Raise the army, hold Lwow, take Wilno and Minsk, decide how far east the border runs and whether to march with Petliura on Kiev, and when the Red Army turns west in the summer of 1920, hold Warsaw.",
    pedia="Jozef Pilsudski (1867-1935), socialist conspirator, commander of the Polish Legions and prisoner of the Germans at Magdeburg, returned to Warsaw on 10 November 1918 and became head of state of the reborn republic the next day. He fought the Soviets from February 1919, took Kiev in May 1920, lost it in June and won the Battle of Warsaw in August." + NL + "The Peace of Riga of 1921 fixed the border he had fought for. He retired, returned by coup in 1926 and ruled Poland until his death.",
    lines={
        'FIRSTGREETING': ["Pilsudski. Poland is back on the map, and she intends to stay there.", "Welcome to Warsaw. Yesterday it was a German garrison town.", "The Republic of Poland receives you."],
        'GREETING': ["Yes?", "Speak.", "What does Poland owe this visit to?"],
        'GOODBYE': ["Farewell.", "God keep you.", "Until next time."],
        'DECLAREWAR': ["Poland has fought for a hundred and twenty years to exist. One more war is nothing.", "Then it is war.", "So be it."],
        'ATTACKED': ["You attack Poland? Every empire in Europe has tried.", "Another enemy. We have outlasted three partitions.", "Very well. The uhlans will answer.", "A mistake. Poland remembers."],
        'DEFEATED': ["Poland has been erased before. It never lasts.", "Take Warsaw. You will not keep it.", "The republic falls. The nation does not."],
        'WINWAR': ["Poland is secure. The border is where we drew it.", "Victory. Now to build the state."],
        'LOSEWAR': ["A truce. Poland needs time.", "Peace, for now.", "Agreed."],
        'TRADE_YES': ["Agreed.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "Poland cannot afford that.", "Impossible."],
        'TRADEREQUEST': ["A proposal from Warsaw.", "Poland offers this.", "Consider it."],
        'DEMANDTRIBUTE': ["The Republic requires a contribution.", "Pay, and keep the peace.", "You will provide this."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten Poland.", "Careful.", "You would regret it."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "Poland pays nobody."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
    })
CS_EN = {'FINLAND': ('Finland', 'Helsinki'), 'ESTONIA': ('Estonia', 'Reval'), 'LATVIA': ('Latvia', 'Riga'), 'LITHUANIA': ('Lithuania', 'Vilna'), 'GERMANY': ('Germany (Ober Ost)', 'Konigsberg'),
         'ROMANIA': ('Romania', 'Kishinev'), 'GEORGIA': ('Georgia', 'Tiflis'), 'AZERBAIJAN': ('Azerbaijan', 'Baku'), 'ARMENIA': ('Armenia', 'Erivan'), 'OTTOMAN': ('Ottoman Empire', 'Kars'),
         'PERSIA': ('Persia', 'Tabriz'), 'BUKHARA': ('Emirate of Bukhara', 'Bukhara'), 'KHIVA': ('Khanate of Khiva', 'Khiva')}
EXTRA_EN = {'TXT_KEY_RUS1918_SIDE_RED': 'Russian SFSR', 'TXT_KEY_RUS1918_SIDE_SOUTH': 'White South', 'TXT_KEY_RUS1918_SIDE_SIB': 'Siberia', 'TXT_KEY_RUS1918_SIDE_NORTH': 'Northern Region',
            'TXT_KEY_RUS1918_SIDE_UKR': 'Ukrainian State', 'TXT_KEY_RUS1918_SIDE_POL': 'Poland', 'TXT_KEY_RUS1918_SIDE_BARB': 'Insurgents',
            'TXT_KEY_RUS1918_WEEK': 'Week {1_Num}', 'TXT_KEY_RUS1918_WEEK_TT': 'Week {1_Num} of the Civil War, counted from 1 June 1918'}
MOODS = ('_NEUTRAL', '_HAPPY', '_ANGRY')
def emit(lang, FF, CS, EXTRA):
    rows = []
    def rep(tag, text): rows.append(f'    <Replace Tag="{tag}" Text="{html.escape(text, quote=True)}" />')
    for k, f in FF.items():
        c = F[k]['civ']; prefix = F[k]['prefix']; leader_key = F[k]['leader_key']; trait_key = F[k]['trait_key']
        rep(leader_key, f['leader']); rep(leader_key + '_PEDIA', f['pedia'])
        rep(f'TXT_KEY_CIV_{c}_DESC', f['civ_long']); rep(f'TXT_KEY_CIV_{c}_SHORT_DESC', f['civ_short']); rep(f'TXT_KEY_CIV_{c}_ADJECTIVE', f['adj'])
        rep(f'TXT_KEY_CIV5_DAWN_{c}_TEXT', f['dawn']); rep(trait_key + '_SHORT', f['trait_short']); rep(trait_key, f['trait'])
        for key in KEYS(prefix):
            suf = key[len(prefix):]; base = suf; mood = ''
            for m in MOODS:
                if suf.endswith(m): base, mood = suf[:-len(m)], m
            parts = base.rsplit('_', 1)
            if parts[-1].isdigit(): base, n = parts[0], int(parts[1]) - 1
            else: n = {'_NEUTRAL': 0, '_HAPPY': 1, '_ANGRY': 2}.get(mood, 0)
            if base in f['lines']: lines = f['lines'][base]; rep(key, lines[n % len(lines)])
    for key, (state, city) in CS.items():
        rep(f'TXT_KEY_CITYSTATE_RUS1918_{key}', state); rep(f'TXT_KEY_CITY_RUS1918_{key}', city)
    for eid, (t_en, x_en, t_ru, x_ru) in EVENTS.items():
        rep(f'TXT_KEY_RUS1918_EVT_{eid}_TITLE', t_en if lang == 'en' else t_ru); rep(f'TXT_KEY_RUS1918_EVT_{eid}_TEXT', x_en if lang == 'en' else x_ru)
    for k2, v in EXTRA.items(): rep(k2, v)
    # unique units and buildings (text/uniques.py; Russian in ru.py)
    for u in uniques.UNITS + uniques.BUILDINGS:
        t = ('UNIT' if u in uniques.UNITS else 'BUILDING') + '_RUS1918_' + u['key']
        name, help_, strategy, pedia = (u['name'], u['help'], u['strategy'], u['pedia']) if lang == 'en' else RU_UNIQUES[u['key']]
        rep(f'TXT_KEY_{t}', name); rep(f'TXT_KEY_{t}_HELP', help_); rep(f'TXT_KEY_{t}_STRATEGY', strategy); rep(f'TXT_KEY_CIV5_RUS1918_{u["key"]}_TEXT', pedia)
    return rows
if __name__ == '__main__':
    rows_en = emit('en', F, CS_EN, EXTRA_EN); rows_ru = emit('ru', RU, RU_CS, RU_EXTRA)
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n<!-- Russia 1918: leader, civilization, city-state, event and unique unit text (EN + RU). -->\n<GameData>\n  <Language_en_US>\n' + '\n'.join(rows_en) +
           '\n  </Language_en_US>\n  <Language_RU_RU>\n' + '\n'.join(rows_ru) + '\n  </Language_RU_RU>\n</GameData>\n')
    open(OUT, 'w', encoding='utf-8').write(xml)
    print('wrote', OUT, len(rows_en), 'EN +', len(rows_ru), 'RU rows')
    sql_out = os.path.join(HERE, '..', 'ui', 'Russia1918_Uniques.sql')
    open(sql_out, 'w', encoding='utf-8').write(uniques.sql())
    print('wrote', sql_out, len(uniques.UNITS), 'units +', len(uniques.BUILDINGS), 'buildings')
