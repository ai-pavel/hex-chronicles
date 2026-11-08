#!/usr/bin/env python3
"""Generate Spain1936_Text.xml: Language_en_US + Language_RU_RU overrides for the six sides, the six city-states, the events and the calendar."""
import os, html, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ru import RU, RU_CS, RU_EXTRA, RU_UNIQUES
import uniques
from events_text import EVENTS
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
DIALOG_KEYS = [l.strip() for l in open(os.path.join(XMLDIR, 'LEADER_DIALOG_KEYS.txt')) if l.strip()]
KEYS = lambda prefix: [k for k in DIALOG_KEYS if k.startswith(prefix)]
OUT = os.path.join(HERE, '..', 'ui', 'Spain1936_Text.xml')
NL = '[NEWLINE][NEWLINE]'
F = {}
F['REP'] = dict(prefix='TXT_KEY_LEADER_CATHERINE_', leader_key='TXT_KEY_LEADER_CATHERINE', civ='RUSSIA', trait_key='TXT_KEY_TRAIT_STRATEGIC_RICHES',
    leader='Manuel Azana', civ_long='Spanish Republic', civ_short='Spanish Republic', adj='Republican', trait_short='Arsenals of the Republic',
    trait='Strategic resources provide +1 [ICON_PRODUCTION] Production, and Horse and Iron provide double quantity. The Republic keeps the capital, the arsenals and most of the industry.',
    dawn="President Azana, the rising of the generals has failed in Madrid, Barcelona, Valencia, Bilbao and the mining valleys of Asturias. The Republic keeps the capital, the gold reserve of the Bank of Spain, most of the fleet and the air force, and the industrial cities. It has lost its army: the officers have rebelled or are suspected, and the defence of the Republic lies with the militias of the parties and the unions." + NL + "Hold the passes of the Guadarrama and the roads from the south, turn the militias into an army, and keep the Generalitat, the Basques and the anarchists fighting one war rather than four. Paris and London will not sell you arms; Moscow will, at a price.",
    pedia="Manuel Azana Diaz (1880-1940), writer and leader of Republican Left, was the most prominent politician of the Second Republic: minister of war and prime minister from 1931 to 1933, prime minister again after the Popular Front victory of February 1936, and President of the Republic from May 1936." + NL + "He spent the war in Madrid, Valencia, Barcelona and Montserrat, pleading for a negotiated peace, and resigned in exile in France on 27 February 1939. He died at Montauban in November 1940.",
    lines={
        'FIRSTGREETING': ["Manuel Azana, President of the Spanish Republic. The Republic is the lawful government of Spain, whatever the generals say.", "Welcome to Madrid. You find the Republic in arms, which was not its wish.", "The Republic receives you. Peace, pity and pardon are not yet on the agenda, but they will be."],
        'GREETING': ["Yes?", "What brings you to Madrid?", "The Republic is listening."],
        'GOODBYE': ["Good day.", "Until the next time.", "Farewell."],
        'DECLAREWAR': ["Then you join the rebels. The Republic will defend itself.", "So be it. Spain has had enough of generals deciding for her.", "Very well. History will judge which of us broke the peace."],
        'ATTACKED': ["You attack the lawful government of Spain? The League of Nations will hear of it, for what that is worth.", "Another enemy. The Republic has no shortage of them.", "Madrid has held before. It will hold again.", "You chose your side. We will remember it."],
        'DEFEATED': ["The Republic falls. The idea of a free Spain does not.", "Take the cities. You will not take the memory.", "I asked for peace, pity and pardon. I hope you will grant them."],
        'WINWAR': ["The rising is over. Now Spain must learn to live together again.", "The Republic stands. Let there be no reprisals."],
        'LOSEWAR': ["A truce. Spain needs it more than either of us.", "Peace, then. Let the guns be silent.", "Agreed."],
        'TRADE_YES': ["Agreed. The Republic pays its debts.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "The Republic cannot accept that.", "Unacceptable."],
        'TRADEREQUEST': ["A proposal from the Republic.", "Consider this, in good faith.", "Business, nothing more."],
        'DEMANDTRIBUTE': ["The Republic requires a contribution to its defence.", "Pay, and we will forget your neutrality.", "You will provide this."],
        'LETSHEARIT': ["Go on.", "Speak.", "I am listening."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Out of the question.", "Refused."],
        'WARBLUFF': ["Threats do not move the Republic.", "Do not test us.", "Careful."],
        'TRIBUTE_YES': ["Take it. It is cheaper than a war.", "Very well."], 'TRIBUTE_NO': ["The Republic pays nobody.", "No."],
        'TRADE_NEEDMORE': ["Not enough.", "You can do better than that.", "Add something."],
    })
F['NAT'] = dict(prefix='TXT_KEY_LEADER_SHAKA_', leader_key='TXT_KEY_LEADER_SHAKA', civ='ZULU', trait_key='TXT_KEY_TRAIT_BUFFALO_HORNS',
    leader='Francisco Franco', civ_long='Nationalist Spain', civ_short='Nationalists', adj='Nationalist', trait_short='Army of Africa',
    trait='Melee units cost 50% less maintenance. All units require 25% less experience to earn their next promotion. The Legion and the Regulares are the veterans of the Rif.',
    dawn="General Franco, the rising has half failed. You command the Army of Africa, the only battle-hardened troops in Spain, but they are in Morocco, and the Republican fleet holds the Strait. In Seville, Cadiz and Cordoba a few thousand soldiers hold Andalusia for you; Mola holds the north, and between your two armies lies the whole of Republican Extremadura and New Castile." + NL + "Bring the Army of Africa across by air and by sea, march north to join Mola, relieve the Alcazar of Toledo and take Madrid before the Republic can build an army. Germany and Italy are willing to help; make sure the help comes to you.",
    pedia="Francisco Franco Bahamonde (1892-1975), the youngest general in Europe in 1926, made his career in the colonial war in Morocco and commanded the Spanish Legion. In 1936 he was military commander of the Canary Islands; he flew to Tetuan on 19 July to take command of the Army of Africa." + NL + "Named Generalisimo and head of state by the other rebel generals in September 1936, he led the Nationalists to victory in April 1939 and ruled Spain as a dictator until his death in November 1975.",
    lines={
        'FIRSTGREETING': ["General Franco, commander of the Army of Africa.", "You find Spain at war. The army has risen to save her, as it sees it.", "The Nationalist command receives you."],
        'GREETING': ["Yes?", "Be brief.", "What is it?"],
        'GOODBYE': ["Good day.", "That will be all.", "Until the next time."],
        'DECLAREWAR': ["Then you will share the fate of the Reds.", "So be it. The army does not negotiate with its enemies.", "War, then."],
        'ATTACKED': ["You attack the Nationalist army? You will regret it.", "Another enemy. We have dealt with worse in Africa.", "Very well. The Legion will answer.", "We will remember this."],
        'DEFEATED': ["The army is beaten. It will not be the last word.", "Take the cities. You will not hold them.", "I was mistaken in you."],
        'WINWAR': ["The war is over. Our troops have reached their last objectives.", "Victory. Now order."],
        'LOSEWAR': ["A truce. For now.", "Agreed. The army needs to regroup.", "Very well."],
        'TRADE_YES': ["Agreed.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "Unacceptable.", "Impossible."],
        'TRADEREQUEST': ["A proposal from the Nationalist command.", "Consider this.", "An offer."],
        'DEMANDTRIBUTE': ["The army needs supplies. You will provide them.", "Pay, and remain neutral.", "A contribution to the cause."],
        'LETSHEARIT': ["Go on.", "Speak.", "I am listening."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten the army.", "Careful.", "You would regret it."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["The army pays nobody.", "No."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
    })
F['NORTH'] = dict(prefix='TXT_KEY_LEADER_BISMARCK_', leader_key='TXT_KEY_LEADER_BISMARCK', civ='GERMANY', trait_key='TXT_KEY_TRAIT_CONVERTS_LAND_BARBARIANS',
    leader='Emilio Mola', civ_long='Army of the North', civ_short='Army of the North', adj='Nationalist', trait_short='The Director',
    trait='When a land unit defeats a barbarian unit inside an encampment, there is a 67% chance it earns 25 [ICON_GOLD] Gold and the barbarians join your side. Land unit maintenance reduced by 25%.',
    dawn="General Mola, you planned the rising as its Director, and in the north it has succeeded: Old Castile and Leon, Galicia, Navarre, Alava, the Rioja and western Aragon are yours, and the Carlist requetes of Navarre have answered in their thousands. But Madrid did not fall, your columns are stopped in the passes of the Guadarrama, and ammunition is short." + NL + "Hold the passes and the Aragon front, close the French border at Irun to cut the Basques and Asturians off from France, and then turn on Bilbao, Santander and Asturias one at a time. Franco is coming up from the south; whether you meet him as an equal is up to you.",
    pedia="Emilio Mola Vidal (1887-1937), born in Cuba and a veteran of the Moroccan wars, was the last director-general of security of the monarchy. Sent to command at Pamplona in 1936, he became the 'Director' who planned the military rising of July 1936." + NL + "He commanded the Army of the North through the Basque campaign and was killed when his aircraft crashed near Alcocero, Burgos, on 3 June 1937.",
    lines={
        'FIRSTGREETING': ["General Mola, Army of the North.", "Welcome to Burgos. The Junta de Defensa sits here, for now.", "The Army of the North receives you."],
        'GREETING': ["Yes?", "Speak, I have a front to run.", "What is it?"],
        'GOODBYE': ["Good day.", "Until next time.", "Farewell."],
        'DECLAREWAR': ["Then it is war.", "You side with the Republic. You will share its fate.", "So be it."],
        'ATTACKED': ["You attack the Army of the North? You will regret it.", "One more front. We have enough already.", "Very well. Navarre will answer.", "A mistake. We will remember it."],
        'DEFEATED': ["The army is beaten. The cause is not.", "Take Burgos. You will not keep it.", "So it ends."],
        'WINWAR': ["The north is ours. Now the rest.", "Victory."],
        'LOSEWAR': ["A truce. We accept.", "Peace, for now.", "Very well."],
        'TRADE_YES': ["Agreed.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "We cannot.", "Impossible."],
        'TRADEREQUEST': ["A proposal from Burgos.", "Consider this.", "An offer."],
        'DEMANDTRIBUTE': ["The army needs supplies. You will provide them.", "Pay, and stay out of this.", "A contribution."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten us.", "Careful.", "You would regret it."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "The army pays nobody."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
    })
F['CAT'] = dict(prefix='TXT_KEY_LEADER_POCATELLO_', leader_key='TXT_KEY_LEADER_POCATELLO', civ='SHOSHONE', trait_key='TXT_KEY_TRAIT_GREAT_EXPANSE',
    leader='Lluis Companys', civ_long='Generalitat of Catalonia', civ_short='Catalonia', adj='Catalan', trait_short='Visca Catalunya',
    trait='Units receive a combat bonus when fighting within their own territory. Founded cities start with additional territory.',
    dawn="President Companys, in Barcelona the rising was crushed in two days by the Assault Guards, the Guardia Civil and the workers of the CNT, and General Goded is a prisoner. The Generalitat governs; the Central Committee of Antifascist Militias rules the streets, and the columns are already on the road to Zaragoza and Huesca." + NL + "Turn the factories of Barcelona into a war industry, take back Mallorca if you can, and hold Catalonia together between the government in Madrid, the anarchist committees and the Aragon front. Catalonia's autonomy has never been so complete, nor so fragile.",
    pedia="Lluis Companys i Jover (1882-1940), a labour lawyer and leader of the Republican Left of Catalonia, became President of the Generalitat in 1934. Imprisoned after proclaiming a Catalan State within a federal republic in October 1934, he was freed by the Popular Front victory of 1936." + NL + "He led Catalonia through the war and crossed into France in February 1939. Arrested by the Gestapo in 1940 and handed over to Franco, he was tried by court-martial and executed at Montjuic on 15 October 1940.",
    lines={
        'FIRSTGREETING': ["Lluis Companys, President of the Generalitat of Catalonia.", "Welcome to Barcelona. Catalonia has stayed loyal to the Republic and to itself.", "The Generalitat receives you."],
        'GREETING': ["Yes?", "Speak.", "What brings you to Barcelona?"],
        'GOODBYE': ["Farewell.", "Adeu.", "Until next time."],
        'DECLAREWAR': ["Then Catalonia will defend itself.", "So be it.", "You will find Barcelona harder than you think."],
        'ATTACKED': ["You attack Catalonia? Every army that tried has regretted it.", "Another enemy. We have enough of them already.", "Very well. The militias will answer.", "A mistake. Catalonia remembers."],
        'DEFEATED': ["Catalonia falls. It has risen before.", "Take Barcelona. You will not take the Catalans.", "We go into exile, as so many before us."],
        'WINWAR': ["Catalonia is safe. Now we rebuild.", "Victory. Visca Catalunya."],
        'LOSEWAR': ["A truce. Catalonia needs it.", "Peace, for now.", "Agreed."],
        'TRADE_YES': ["Agreed.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "Catalonia cannot afford that.", "Impossible."],
        'TRADEREQUEST': ["A proposal from the Generalitat.", "Catalonia offers this.", "Consider it."],
        'DEMANDTRIBUTE': ["The Generalitat requires a contribution.", "Pay, and keep the peace.", "You will provide this."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten Catalonia.", "Careful.", "You would regret it."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "Catalonia pays nobody."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
    })
F['EUZ'] = dict(prefix='TXT_KEY_LEADER_SELASSIE_', leader_key='TXT_KEY_LEADER_SELASSIE', civ='ETHIOPIA', trait_key='TXT_KEY_TRAIT_BONUS_AGAINST_TECH',
    leader='Jose Antonio Aguirre', civ_long='Basque Country (Euzkadi)', civ_short='Basque Country', adj='Basque', trait_short='Gudariak',
    trait='+20% [ICON_STRENGTH] Combat Strength against civilizations that have more cities than you.',
    dawn="Jose Antonio, Biscay and Gipuzkoa have stayed with the Republic; Alava and Navarre have gone with Mola. Your party, Catholic and conservative, has chosen the Republic that promised the Basques their statute, and the Cortes will grant it within weeks. The north is cut off from the rest of the Republic, and Irun, the gate to France, is already under attack." + NL + "Raise an army of Basque battalions, build the Iron Ring around Bilbao, keep the mines of Somorrostro and the shipyards of the Nervion working, and protect your people. Help can only come by sea.",
    pedia="Jose Antonio Aguirre y Lecube (1904-1960), lawyer, footballer for Athletic Bilbao and leader of the Basque Nationalist Party, was elected the first lehendakari (president) of the Basque Government and took the oath under the oak of Guernica on 7 October 1936." + NL + "After the fall of Bilbao in June 1937 his government went into exile, first in Barcelona and then in France; caught in Belgium by the German invasion of 1940, he escaped across Nazi Germany under a false identity to the Americas. He led the Basque government in exile until his death in Paris in 1960.",
    lines={
        'FIRSTGREETING': ["Jose Antonio Aguirre, lehendakari of the Basque Government.", "Welcome to Bilbao. Euzkadi stands with the Republic and with its own freedom.", "The Basque Government receives you."],
        'GREETING': ["Yes?", "Speak.", "What brings you to Euzkadi?"],
        'GOODBYE': ["Agur.", "Farewell.", "Until next time."],
        'DECLAREWAR': ["Then the Basques will defend their land.", "So be it.", "You will find our mountains hard going."],
        'ATTACKED': ["You attack Euzkadi? Our people have defended these valleys for a thousand years.", "Another enemy. We are used to it.", "Very well. The gudaris will answer.", "A mistake."],
        'DEFEATED': ["Euzkadi falls. The Basques remain.", "Take Bilbao. You will not take our language or our faith.", "We go into exile. We will come back."],
        'WINWAR': ["Euzkadi is free. Now we rebuild.", "Victory. Now peace."],
        'LOSEWAR': ["A truce. Our people need it.", "Peace, for now.", "Agreed."],
        'TRADE_YES': ["Agreed. Basque iron for your bread.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "Euzkadi cannot afford that.", "Impossible."],
        'TRADEREQUEST': ["A proposal from Bilbao.", "Euzkadi offers this.", "Consider it."],
        'DEMANDTRIBUTE': ["The Basque Government requires a contribution.", "Pay, and keep the peace.", "You will provide this."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Very well."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Do not threaten Euzkadi.", "Careful.", "You would regret it."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "Euzkadi pays nobody."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
    })
F['CNT'] = dict(prefix='TXT_KEY_LEADER_MONTEZUMA_', leader_key='TXT_KEY_LEADER_MONTEZUMA', civ='AZTEC', trait_key='TXT_KEY_TRAIT_CULTURE_FROM_KILLS', dawn_key='TXT_KEY_CIV5_DAWN_AZTECS_TEXT',
    leader='Buenaventura Durruti', civ_long='CNT-FAI and the Council of Aragon', civ_short='CNT-FAI', adj='Confederal', trait_short='The Revolution',
    trait='Gains [ICON_CULTURE] Culture for the empire from each enemy unit killed.',
    dawn="Comrade Durruti, the workers of the CNT have beaten the army in the streets of Barcelona, and the arsenals are open. A few days later the columns set out for Aragon in requisitioned lorries: yours for Zaragoza, the Ascaso column for Huesca, the Ortiz column for Caspe. Behind the front the villages burn the property registers and collectivise the land." + NL + "Take Zaragoza if you can, hold the Aragon front, and keep the revolution alive while the Republic and the Generalitat rebuild a state around you. The Republic needs your columns and distrusts your committees; the war and the revolution will have to be won together, or neither will be.",
    pedia="Jose Buenaventura Durruti Dumange (1896-1936), a railway mechanic from Leon, was the best-known militant of the anarchist movement: a member of the Solidarios group in the 1920s, years of exile in the Americas and Europe, prison under the Republic. In July 1936 he fought in the streets of Barcelona and led the column that bore his name to the gates of Zaragoza." + NL + "In November 1936 he brought part of his column to the defence of Madrid, where he was mortally wounded on 19 November in the University City; he died the next day. Hundreds of thousands attended his funeral in Barcelona.",
    lines={
        'FIRSTGREETING': ["Durruti. I speak for nobody but my comrades, and they speak for themselves.", "Welcome to the Aragon front. Here nobody salutes and everybody fights.", "The CNT-FAI receives you. Keep it short; there is a war and a revolution to win."],
        'GREETING': ["Comrade?", "What is it?", "Speak."],
        'GOODBYE': ["Salud.", "Until the next time.", "Back to the front."],
        'DECLAREWAR': ["Then you will meet the columns.", "So be it. We were never afraid of a fight.", "War, then."],
        'ATTACKED': ["You attack the workers in arms? Come and try.", "Another enemy. The revolution has plenty.", "Very well. The column will answer.", "We will not forget this."],
        'DEFEATED': ["You can kill us. You cannot kill the idea.", "Take the villages. The land will remember who worked it.", "The column is broken. The movement is not."],
        'WINWAR': ["The revolution holds. Now we build.", "Victory, comrades."],
        'LOSEWAR': ["A truce. The comrades need rest.", "Peace, for now.", "Agreed."],
        'TRADE_YES': ["Agreed.", "Yes.", "Done."],
        'TRADE_NO': ["No.", "Not with us.", "Impossible."],
        'TRADEREQUEST': ["A proposal from the committee.", "Consider this.", "An offer, between equals."],
        'DEMANDTRIBUTE': ["The front needs arms. You will provide them.", "A contribution to the revolution.", "Pay."],
        'LETSHEARIT': ["Go on.", "I am listening.", "Speak."],
        'AGREE_SHORT': ["Agreed.", "Yes.", "Fine."],
        'DISAGREE_SHORT': ["No.", "Never.", "Refused."],
        'WARBLUFF': ["Threats? We have heard them all.", "Careful.", "You would regret it."],
        'TRIBUTE_YES': ["Take it.", "Very well."], 'TRIBUTE_NO': ["No.", "The revolution pays nobody."],
        'TRADE_NEEDMORE': ["Not enough.", "Add something.", "More."],
    })
CS_EN = {'PORTUGAL': ('Portugal', 'Lisbon'), 'GIBRALTAR': ('Gibraltar (British)', 'Gibraltar'), 'TANGIER': ('Tangier International Zone', 'Tangier'), 'ANDORRA': ('Andorra', 'Andorra la Vella'),
         'FRANCE': ('France', 'Perpignan'), 'NAFRICA': ('French North Africa', 'Oran')}
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
EXTRA_EN = {'TXT_KEY_ESP1936_SIDE_REP': 'Spanish Republic', 'TXT_KEY_ESP1936_SIDE_NAT': 'Nationalists', 'TXT_KEY_ESP1936_SIDE_NORTH': 'Army of the North', 'TXT_KEY_ESP1936_SIDE_CAT': 'Catalonia',
            'TXT_KEY_ESP1936_SIDE_EUZ': 'Basque Country', 'TXT_KEY_ESP1936_SIDE_CNT': 'CNT-FAI', 'TXT_KEY_ESP1936_SIDE_BARB': 'Fugitives and insurgents',
            'TXT_KEY_ESP1936_WEEK': 'Week {1_Num}', 'TXT_KEY_ESP1936_WEEK_TT': 'Week {1_Num} of the Civil War, counted from 25 July 1936'}
EXTRA_EN.update({f'TXT_KEY_ESP1936_MONTH_{i + 1}': m for i, m in enumerate(MONTHS_EN)})
MOODS = ('_NEUTRAL', '_HAPPY', '_ANGRY')
def emit(lang, FF, CS, EXTRA):
    rows = []
    def rep(tag, text): rows.append(f'    <Replace Tag="{tag}" Text="{html.escape(text, quote=True)}" />')
    for k, f in FF.items():
        c = F[k]['civ']; prefix = F[k]['prefix']; leader_key = F[k]['leader_key']; trait_key = F[k]['trait_key']
        rep(leader_key, f['leader']); rep(leader_key + '_PEDIA', f['pedia'])
        rep(f'TXT_KEY_CIV_{c}_DESC', f['civ_long']); rep(f'TXT_KEY_CIV_{c}_SHORT_DESC', f['civ_short']); rep(f'TXT_KEY_CIV_{c}_ADJECTIVE', f['adj'])
        rep(F[k].get('dawn_key', f'TXT_KEY_CIV5_DAWN_{c}_TEXT'), f['dawn']); rep(trait_key + '_SHORT', f['trait_short']); rep(trait_key, f['trait'])
        for key in KEYS(prefix):
            suf = key[len(prefix):]; base = suf; mood = ''
            for m in MOODS:
                if suf.endswith(m): base, mood = suf[:-len(m)], m
            parts = base.rsplit('_', 1)
            if parts[-1].isdigit(): base, n = parts[0], int(parts[1]) - 1
            else: n = {'_NEUTRAL': 0, '_HAPPY': 1, '_ANGRY': 2}.get(mood, 0)
            if base in f['lines']: lines = f['lines'][base]; rep(key, lines[n % len(lines)])
    for key, (state, city) in CS.items():
        rep(f'TXT_KEY_CITYSTATE_ESP1936_{key}', state); rep(f'TXT_KEY_CITY_ESP1936_{key}', city)
    for eid, (t_en, x_en, t_ru, x_ru) in EVENTS.items():
        rep(f'TXT_KEY_ESP1936_EVT_{eid}_TITLE', t_en if lang == 'en' else t_ru); rep(f'TXT_KEY_ESP1936_EVT_{eid}_TEXT', x_en if lang == 'en' else x_ru)
    for k2, v in EXTRA.items(): rep(k2, v)
    # unique units and buildings (text/uniques.py; Russian in ru.py)
    for u in uniques.UNITS + uniques.BUILDINGS:
        t = ('UNIT' if u in uniques.UNITS else 'BUILDING') + '_ESP1936_' + u['key']
        name, help_, strategy, pedia = (u['name'], u['help'], u['strategy'], u['pedia']) if lang == 'en' else RU_UNIQUES[u['key']]
        rep(f'TXT_KEY_{t}', name); rep(f'TXT_KEY_{t}_HELP', help_); rep(f'TXT_KEY_{t}_STRATEGY', strategy); rep(f'TXT_KEY_CIV5_ESP1936_{u["key"]}_TEXT', pedia)
    return rows
if __name__ == '__main__':
    rows_en = emit('en', F, CS_EN, EXTRA_EN); rows_ru = emit('ru', RU, RU_CS, RU_EXTRA)
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n<!-- Spain 1936: leader, civilization, city-state and event text (EN + RU). -->\n<GameData>\n  <Language_en_US>\n' + '\n'.join(rows_en) +
           '\n  </Language_en_US>\n  <Language_RU_RU>\n' + '\n'.join(rows_ru) + '\n  </Language_RU_RU>\n</GameData>\n')
    open(OUT, 'w', encoding='utf-8').write(xml)
    print('wrote', OUT, len(rows_en), 'EN +', len(rows_ru), 'RU rows')
    sql_out = os.path.join(HERE, '..', 'ui', 'Spain1936_Uniques.sql')
    open(sql_out, 'w', encoding='utf-8').write(uniques.sql())
    print('wrote', sql_out, len(uniques.UNITS), 'units +', len(uniques.BUILDINGS), 'buildings')
