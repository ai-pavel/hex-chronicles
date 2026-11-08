#!/usr/bin/env python3
"""Generate China1928_Text.xml (Language_en_US + Language_RU_RU overrides for the six sides, the thirteen city-states, the events, the calendar and the
unique units and buildings) and China1928_Uniques.sql (text/uniques.py)."""
import os, html, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ru import RU, RU_CS, RU_EXTRA, RU_UNIQUES
import uniques
from events_text import EVENTS
XMLDIR = os.environ.get('HEX_XML', os.path.join(HERE, '..', '..', '..', 'data', 'xml'))   # tools/extract_game_xml.py
DIALOG_KEYS = [l.strip() for l in open(os.path.join(XMLDIR, 'LEADER_DIALOG_KEYS.txt')) if l.strip()]
KEYS = lambda prefix: [k for k in DIALOG_KEYS if k.startswith(prefix)]
OUT = os.path.join(HERE, '..', 'ui', 'China1928_Text.xml')
NL = '[NEWLINE][NEWLINE]'
F = {}
def lines(first, greet, bye, war, attacked, defeated, win, lose, yes, no, req, demand, hear, agree, disagree, bluff, tyes, tno, more):
    return {'FIRSTGREETING': first, 'GREETING': greet, 'GOODBYE': bye, 'DECLAREWAR': war, 'ATTACKED': attacked, 'DEFEATED': defeated, 'WINWAR': win, 'LOSEWAR': lose,
            'TRADE_YES': yes, 'TRADE_NO': no, 'TRADEREQUEST': req, 'DEMANDTRIBUTE': demand, 'LETSHEARIT': hear, 'AGREE_SHORT': agree, 'DISAGREE_SHORT': disagree,
            'WARBLUFF': bluff, 'TRIBUTE_YES': tyes, 'TRIBUTE_NO': tno, 'TRADE_NEEDMORE': more}
F['NAN'] = dict(prefix='TXT_KEY_LEADER_WUZETIAN_', leader_key='TXT_KEY_LEADER_WU_ZETIAN', civ='CHINA', trait_key='TXT_KEY_TRAIT_ART_OF_WAR',
    leader='Chiang Kai-shek', civ_long='National Government of the Republic of China', civ_short='National Government', adj='Nationalist', trait_short='Sons of Whampoa',
    trait='Great Generals are earned 50% faster, and their combat bonus is 15% stronger. The officers of the Whampoa academy command the Central Army.',
    dawn="Chairman Chiang, the Northern Expedition is over. Beijing has fallen and been renamed Beiping, the Beiyang government is gone, and today, 10 October 1928, you take office as Chairman of the National Government in Nanjing. You hold the Yangtze delta, Shanghai with its customs, its banks and its arsenal, and the best-trained divisions in the country." + NL + "But China is united only on paper. Feng Yuxiang, Yan Xishan and the Guangxi clique, your allies of yesterday, keep their own armies and their own provinces; the Young Marshal in Mukden still flies the old flag; the Communists hold out in the hills of Jiangxi; and the Japanese watch from Dairen and Jinan. Reduce the armies, build a state, and choose your wars carefully.",
    pedia="Chiang Kai-shek (Jiang Jieshi, 1887-1975), trained as an officer in Japan, became commandant of the Whampoa Military Academy in 1924 and led the Northern Expedition of 1926-1928, breaking with the Communists in Shanghai in April 1927. Chairman of the National Government from October 1928, he fought the Central Plains War against Feng Yuxiang and Yan Xishan in 1930 and five campaigns against the Jiangxi Soviet from 1930 to 1934." + NL + "Detained by Zhang Xueliang at Xi'an in December 1936, he agreed to a united front against Japan and led China through the war of 1937-1945. Defeated in the civil war, he withdrew to Taiwan in 1949 and ruled there until his death in April 1975.",
    lines=lines(["Chiang Kai-shek, Chairman of the National Government. China has one government now, and it sits in Nanjing.", "Welcome to Nanjing. The revolution has been won; now the nation must be built.", "The National Government receives you. Speak plainly."],
        ["Yes?", "What brings you to Nanjing?", "The Chairman is listening."], ["Good day.", "Until the next time.", "We shall speak again."],
        ["Then you have chosen rebellion. The government will put it down.", "So be it. China will have one army, not twenty.", "You leave me no choice."],
        ["You attack the lawful government of China? You will regret it.", "Another warlord who thinks himself a king.", "Very well. The Central Army will answer.", "We will remember this."],
        ["Nanjing falls, but China does not.", "Take the cities. The nation will outlast you.", "I underestimated you. It will not happen twice."],
        ["The rebellion is over. Now the reconstruction.", "Order is restored."], ["A truce. China needs it.", "Peace, for now.", "Agreed."],
        ["Agreed.", "Yes.", "Done."], ["No.", "The government cannot accept that.", "Unacceptable."], ["A proposal from Nanjing.", "Consider this carefully.", "An offer."],
        ["The government requires a contribution to the national defence.", "Pay, and remain loyal.", "You will provide this."], ["Go on.", "Speak.", "I am listening."],
        ["Agreed.", "Yes.", "Very well."], ["No.", "Out of the question.", "Refused."], ["Do not threaten the government.", "Careful.", "You would regret it."],
        ["Take it. It is cheaper than a war.", "Very well."], ["The government pays nobody.", "No."], ["Not enough.", "You can do better.", "Add something."]))
F['GMJ'] = dict(prefix='TXT_KEY_LEADER_SHAKA_', leader_key='TXT_KEY_LEADER_SHAKA', civ='ZULU', trait_key='TXT_KEY_TRAIT_BUFFALO_HORNS',
    leader='Feng Yuxiang', civ_long='Guominjun (Northwest Army)', civ_short='Guominjun', adj='Guominjun', trait_short='The Christian General\'s Army',
    trait='Melee units cost 50% less maintenance. All units require 25% less experience to earn their next promotion. Feng Yuxiang\'s soldiers are drilled, frugal and hard-marching.',
    dawn="Marshal Feng, your Second Group Army marched from Shaanxi into Henan and up the Beijing-Hankou railway in the Northern Expedition, and it is one of the largest and best-drilled armies in China. You hold Henan, Shaanxi and Gansu, the Longhai railway and western Shandong; the government in Nanjing has made you its Minister of War." + NL + "But your provinces are the poorest in China, and the great famine is spreading across the northwest. Nanjing pays its own divisions first and talks of disbanding yours. Keep your army fed and your generals loyal, find allies against Chiang before he finds allies among your officers, and hold the Yellow River.",
    pedia="Feng Yuxiang (1882-1948) rose through the Beiyang army and was baptised a Methodist; the 'Christian General' forbade his troops opium, gambling and drink and drilled them hard. In October 1924 he seized Beijing in a coup, expelled the last emperor from the Forbidden City and named his army the Guominjun; in 1926 he joined the Kuomintang and its Northern Expedition." + NL + "Defeated by Chiang Kai-shek in the Central Plains War of 1930, he led the Chahar People's Anti-Japanese Allied Army in 1933 and later held high but powerless posts in Nanjing. He died in a fire aboard a Soviet ship on the Black Sea in September 1948.",
    lines=lines(["Feng Yuxiang. My soldiers do not drink, do not gamble and do not loot. Can you say as much?", "Welcome to Kaifeng. You will find no banquet here; we eat what the soldiers eat.", "The Guominjun receives you."],
        ["Yes?", "Speak, brother.", "What is it?"], ["Go in peace.", "Until next time.", "Farewell."],
        ["Then you will meet my army. It has never been afraid of a long march.", "So be it.", "War, then. God will judge."],
        ["You attack the Guominjun? We have fought worse than you.", "Another enemy. The northwest is used to hard times.", "Very well. The big swords will answer.", "We will remember this."],
        ["The army is broken. The men will find another.", "Take Kaifeng. The people will not love you for it.", "I have been betrayed before."],
        ["Victory. Now the soldiers can plant trees.", "The war is over."], ["A truce. My men need bread more than glory.", "Peace, then.", "Agreed."],
        ["Agreed.", "Yes.", "Done."], ["No.", "We cannot spare it.", "Impossible."], ["A proposal from the Guominjun.", "Consider this.", "An offer."],
        ["The army is hungry. You will help feed it.", "Pay, and we will stay friends.", "A contribution."], ["Go on.", "I am listening.", "Speak."],
        ["Agreed.", "Yes.", "Good."], ["No.", "Never.", "Refused."], ["Do not threaten us.", "Careful, brother.", "You would regret it."],
        ["Take it.", "Very well."], ["No.", "The Guominjun pays nobody."], ["Not enough.", "Add something.", "More."]))
F['SHX'] = dict(prefix='TXT_KEY_LEADER_CATHERINE_', leader_key='TXT_KEY_LEADER_CATHERINE', civ='RUSSIA', trait_key='TXT_KEY_TRAIT_STRATEGIC_RICHES',
    leader='Yan Xishan', civ_long='Shanxi and Hebei (Third Group Army)', civ_short='Shanxi', adj='Shanxi', trait_short='The Model Province',
    trait='Strategic resources provide +1 [ICON_PRODUCTION] Production, and Horse and Iron provide double quantity. Shanxi sits on coal and iron and builds its own arms.',
    dawn="Governor Yan, you have ruled Shanxi since the revolution of 1911, and you have made it the Model Province: roads, schools, village government, an arsenal at Taiyuan, and above all peace behind the passes while the rest of China burned. In June your Third Group Army entered Beijing; now you hold Beiping and Tianjin, the Hebei plain, Chahar and Suiyuan as well." + NL + "Nanjing wants your armies reduced and your revenues shared. Feng Yuxiang is a neighbour and a rival; the Young Marshal is watching Beiping from beyond the Great Wall. Hold what you have, choose your moment, and never leave Taiyuan unguarded.",
    pedia="Yan Xishan (1883-1960), trained at the Japanese military academy and a member of Sun Yat-sen's Tongmenghui, led the Shanxi rising of 1911 and governed the province for almost four decades. His reforms earned Shanxi the name of Model Province, and his army took Beijing for the Kuomintang in June 1928." + NL + "In 1930 he led the coalition against Chiang Kai-shek in the Central Plains War and, defeated, spent a year in exile in Dalian. Back in power in 1932, he industrialised Shanxi, fought the Japanese from 1937 and held Taiyuan until April 1949. He was Premier of the Republic of China in 1949-1950 and died in Taiwan in 1960.",
    lines=lines(["Yan Xishan, Governor of Shanxi. Shanxi asks nothing of anyone, and gives nothing away.", "Welcome to Taiyuan. You came through the passes; you have seen why we are left in peace.", "The Governor receives you."],
        ["Yes?", "Be brief, please.", "What is it?"], ["Good day.", "Until the next time.", "Farewell."],
        ["Then Shanxi will defend itself, as it always has.", "So be it. The passes are ready.", "War, then."],
        ["You attack Shanxi? Many have tried.", "One more enemy at the passes.", "Very well. Taiyuan will answer.", "A mistake. We will remember it."],
        ["Shanxi falls. I will be back.", "Take Taiyuan. You will find it hard to govern.", "So it ends, for now."],
        ["The province is safe. Now we build.", "Victory."], ["A truce. Shanxi prefers peace.", "Peace, for now.", "Agreed."],
        ["Agreed. A fair bargain.", "Yes.", "Done."], ["No.", "Shanxi cannot afford that.", "Impossible."], ["A proposal from Taiyuan.", "Consider this.", "An offer."],
        ["Shanxi requires a contribution.", "Pay, and keep the peace.", "You will provide this."], ["Go on.", "I am listening.", "Speak."],
        ["Agreed.", "Yes.", "Very well."], ["No.", "Never.", "Refused."], ["Do not threaten Shanxi.", "Careful.", "You would regret it."],
        ["Take it.", "Very well."], ["No.", "Shanxi pays nobody."], ["Not enough.", "Add something.", "More."]))
F['FT'] = dict(prefix='TXT_KEY_LEADER_BISMARCK_', leader_key='TXT_KEY_LEADER_BISMARCK', civ='GERMANY', trait_key='TXT_KEY_TRAIT_CONVERTS_LAND_BARBARIANS',
    leader='Zhang Xueliang', civ_long='Fengtian Clique (the Three Eastern Provinces)', civ_short='Fengtian', adj='Fengtian', trait_short='The Old Marshal\'s Legacy',
    trait='When a land unit defeats a barbarian unit inside an encampment, there is a 67% chance it earns 25 [ICON_GOLD] Gold and the barbarians join your side. Land unit maintenance reduced by 25%. Zhang Zuolin began as a bandit chief; his army never stopped recruiting them.',
    dawn="Young Marshal, on 4 June the Japanese blew up your father's train at Huanggutun outside Mukden. At twenty-seven you inherit the three provinces of Manchuria and Rehe: the richest land in China, the Mukden Arsenal, an air force, a navy and a quarter of a million men." + NL + "The Kwantung Army sits in Dairen and along the South Manchuria Railway, the Soviets run the Chinese Eastern Railway through Harbin, and your father's old generals doubt you. Decide whether to raise the flag of Nanjing over the Northeast, master your own house, and stay strong enough that Tokyo thinks twice.",
    pedia="Zhang Xueliang (1901-2001), the 'Young Marshal', son of the Fengtian warlord Zhang Zuolin, took over Manchuria after his father's murder by Kwantung Army officers in June 1928. On 29 December 1928 he raised the Nationalist flag over the Northeast, and in 1930 his intervention decided the Central Plains War for Chiang Kai-shek." + NL + "After the Mukden incident of September 1931 he withdrew his army south of the Great Wall without a fight, and lost Manchuria and then Rehe. In December 1936 at Xi'an he and Yang Hucheng detained Chiang to force a united front against Japan. He spent the following fifty years under arrest, in China and on Taiwan, and died in Honolulu in 2001, aged 100.",
    lines=lines(["Zhang Xueliang. My father built the Northeast; I mean to keep it.", "Welcome to Mukden. You are lucky; the Japanese never come here without an army.", "The Northeast receives you."],
        ["Yes?", "What is it?", "Speak."], ["Good day.", "Until the next time.", "Farewell."],
        ["Then you will meet the Northeast Army.", "So be it. We have aircraft and you do not.", "War, then."],
        ["You attack the Northeast? You choose your enemies badly.", "Another enemy. We have the Japanese already.", "Very well. Mukden will answer.", "We will remember this."],
        ["The Northeast is lost. I will carry that for the rest of my life.", "Take Mukden. Then see who comes for it next.", "I trusted the wrong men."],
        ["Victory. The Northeast stands.", "It is over."], ["A truce. We need it.", "Peace, for now.", "Agreed."],
        ["Agreed.", "Yes.", "Done."], ["No.", "The Northeast cannot accept that.", "Impossible."], ["A proposal from Mukden.", "Consider this.", "An offer."],
        ["The Northeast Army requires a contribution.", "Pay, and stay out of this.", "You will provide this."], ["Go on.", "I am listening.", "Speak."],
        ["Agreed.", "Yes.", "Fine."], ["No.", "Never.", "Refused."], ["Do not threaten us.", "Careful.", "You would regret it."],
        ["Take it.", "Very well."], ["No.", "The Northeast pays nobody."], ["Not enough.", "Add something.", "More."]))
F['GX'] = dict(prefix='TXT_KEY_LEADER_SELASSIE_', leader_key='TXT_KEY_LEADER_SELASSIE', civ='ETHIOPIA', trait_key='TXT_KEY_TRAIT_BONUS_AGAINST_TECH',
    leader='Li Zongren', civ_long='New Guangxi Clique (Fourth Group Army)', civ_short='Guangxi', adj='Guangxi', trait_short='Fewer and Better',
    trait='+20% [ICON_STRENGTH] Combat Strength against civilizations that have more cities than you. Guangxi\'s small, hard armies have beaten bigger ones before.',
    dawn="General Li, the Guangxi clique of Li Zongren, Bai Chongxi and Huang Shaohong took a poor, mountainous province and made its army one of the best in China. Your Seventh Army fought from Hunan to the Yangtze; your Fourth Group Army now holds Wuhan and Hubei through the Wuhan Political Council, and Bai Chongxi's troops stand in eastern Hebei after the march on Beijing." + NL + "Your provinces lie far apart, and the road between them runs through Hunan. Nanjing distrusts you, and you distrust Nanjing. Hold Wuhan if you can, keep the road home open, and remember that Guangxi's strength is its soldiers and its hills.",
    pedia="Li Zongren (1891-1969), with Bai Chongxi and Huang Shaohong the leader of the New Guangxi clique, unified Guangxi by 1925 and commanded the Seventh Army and then the Fourth Group Army in the Northern Expedition. Defeated by Chiang Kai-shek in 1929, he returned to Guangxi and with Bai and Huang Xuchu made it a model province in the 1930s." + NL + "In the war against Japan he won the battle of Taierzhuang in 1938. Elected Vice President in 1948, he was acting President of the Republic of China in 1949, went into exile in the United States, and returned to the People's Republic in 1965, where he died in 1969.",
    lines=lines(["Li Zongren. Guangxi is small, but it has never lost a war it chose to fight.", "Welcome. You have come a long way to see us.", "The Guangxi command receives you."],
        ["Yes?", "Speak.", "What brings you here?"], ["Farewell.", "Until next time.", "Go safely."],
        ["Then you will meet the men of Guangxi.", "So be it.", "You will find our hills hard going."],
        ["You attack Guangxi? Bigger armies have tried.", "Another enemy. We are used to it.", "Very well. The Seventh Army will answer.", "A mistake."],
        ["Guangxi falls. It will rise again.", "Take the cities. You cannot take the hills.", "We go into exile. We will come back."],
        ["Victory. Now home to Guangxi.", "It is over."], ["A truce. Our people need it.", "Peace, for now.", "Agreed."],
        ["Agreed.", "Yes.", "Done."], ["No.", "Guangxi cannot afford that.", "Impossible."], ["A proposal from Guangxi.", "Consider this.", "An offer."],
        ["Guangxi requires a contribution.", "Pay, and keep the peace.", "You will provide this."], ["Go on.", "I am listening.", "Speak."],
        ["Agreed.", "Yes.", "Very well."], ["No.", "Never.", "Refused."], ["Do not threaten Guangxi.", "Careful.", "You would regret it."],
        ["Take it.", "Very well."], ["No.", "Guangxi pays nobody."], ["Not enough.", "Add something.", "More."]))
F['CCP'] = dict(prefix='TXT_KEY_LEADER_POCATELLO_', leader_key='TXT_KEY_LEADER_POCATELLO', civ='SHOSHONE', trait_key='TXT_KEY_TRAIT_GREAT_EXPANSE',
    leader='Mao Zedong', civ_long='Chinese Communist Party and the Red Army', civ_short='Chinese Communists', adj='Communist', trait_short='Base Areas',
    trait='Land units receive +15% [ICON_STRENGTH] Combat Strength in friendly territory, and move through forest in friendly territory as along a road. The Red Army fights best in its own hills.',
    dawn="Comrade Mao, a year after the Kuomintang turned on its Communist allies in Shanghai and Wuhan, the uprisings of 1927 have failed one after another. You and Zhu De hold out in the Jinggang mountains on the Hunan-Jiangxi border with a few thousand men, short of rifles, salt and cloth; other bands survive around the Hong Lake, in the Dabie mountains and in northeastern Jiangxi." + NL + "Survive first. Build base areas in the hills where the warlords' armies meet, win the villages over with land reform, and fight only when you can win. If the bases fall, the army must live on: as long as the Red Army has units in the field, the Communists are not beaten.",
    pedia="Mao Zedong (1893-1976), the son of a Hunan farmer, was a founding member of the Chinese Communist Party in 1921 and an organiser of the peasant movement in Hunan. After the failure of the Autumn Harvest Uprising in September 1927 he led the survivors into the Jinggang mountains, where Zhu De joined him in 1928; their Fourth Red Army moved to southern Jiangxi in 1929, and in November 1931 Mao became chairman of the Chinese Soviet Republic at Ruijin." + NL + "Pushed aside by the party leadership in 1932, he regained command during the Long March at the Zunyi conference of January 1935 and led the Red Army to northern Shaanxi. He proclaimed the People's Republic of China in 1949 and ruled it until his death in 1976.",
    lines=lines(["Mao Zedong. We have little, but the peasants are with us.", "Welcome to the mountains. Mind the path; the enemy uses the roads.", "The Front Committee receives you."],
        ["Comrade?", "What is it?", "Speak."], ["Until the next time.", "Go well.", "Back to work."],
        ["Then the Red Army will fight you as it fights all the others.", "So be it. A single spark can start a prairie fire.", "War, then."],
        ["You attack the Red Army? You will find nobody where you strike.", "Another enemy. We have many.", "Very well. The masses will answer.", "We will not forget this."],
        ["The bases are lost. The army marches on.", "Take the towns. The countryside is ours.", "We retreat. Retreat is not defeat."],
        ["Victory. The land goes to those who till it.", "It is over, for now."], ["A truce. The army needs rest.", "Peace, for now.", "Agreed."],
        ["Agreed.", "Yes.", "Done."], ["No.", "Not with us.", "Impossible."], ["A proposal from the base area.", "Consider this.", "An offer."],
        ["The Red Army needs supplies. You will provide them.", "A contribution to the revolution.", "Pay."], ["Go on.", "I am listening.", "Speak."],
        ["Agreed.", "Yes.", "Good."], ["No.", "Never.", "Refused."], ["Threats? We are used to them.", "Careful.", "You would regret it."],
        ["Take it.", "Very well."], ["No.", "The revolution pays nobody."], ["Not enough.", "Add something.", "More."]))
CS_EN = {'JAPAN': ('Japan', 'Dairen'), 'SOVIET': ('Soviet Union', 'Vladivostok'), 'MONGOLIA': ('Mongolian People\'s Republic', 'Ulan Bator'),
         'SICHUAN': ('Sichuan (Liu Wenhui)', 'Chengdu'), 'CHONGQING': ('Chongqing (Liu Xiang)', 'Chongqing'), 'YUNNAN': ('Yunnan (Long Yun)', 'Kunming'),
         'GUIZHOU': ('Guizhou (Zhou Xicheng)', 'Guiyang'), 'GUANGDONG': ('Guangdong', 'Canton'), 'QINGHAI': ('Qinghai (Ma clique)', 'Xining'),
         'HONGKONG': ('Hong Kong (British)', 'Hong Kong'), 'MACAU': ('Macau (Portuguese)', 'Macau'), 'WEIHAIWEI': ('Weihaiwei (British)', 'Weihaiwei'),
         'INDOCHINA': ('French Indochina', 'Hanoi')}
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
EXTRA_EN = {'TXT_KEY_CHN1928_SIDE_NAN': 'National Government', 'TXT_KEY_CHN1928_SIDE_GMJ': 'Guominjun', 'TXT_KEY_CHN1928_SIDE_SHX': 'Shanxi', 'TXT_KEY_CHN1928_SIDE_FT': 'Fengtian',
            'TXT_KEY_CHN1928_SIDE_GX': 'Guangxi', 'TXT_KEY_CHN1928_SIDE_CCP': 'Chinese Communists', 'TXT_KEY_CHN1928_SIDE_BARB': 'Bandits and rebels',
            'TXT_KEY_CHN1928_SIDE_JAPAN': 'Japan', 'TXT_KEY_CHN1928_SIDE_SOVIET': 'Soviet Union', 'TXT_KEY_CHN1928_SIDE_WEIHAIWEI': 'Weihaiwei', 'TXT_KEY_CHN1928_SIDE_GUANGDONG': 'Guangdong',
            'TXT_KEY_CHN1928_WEEK': 'Week {1_Num}', 'TXT_KEY_CHN1928_WEEK_TT': 'Week {1_Num} of the scenario, counted from 10 October 1928'}
EXTRA_EN.update({f'TXT_KEY_CHN1928_MONTH_{i + 1}': m for i, m in enumerate(MONTHS_EN)})
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
        rep(f'TXT_KEY_CITYSTATE_CHN1928_{key}', state); rep(f'TXT_KEY_CITY_CHN1928_{key}', city)
    for eid, (t_en, x_en, t_ru, x_ru) in EVENTS.items():
        rep(f'TXT_KEY_CHN1928_EVT_{eid}_TITLE', t_en if lang == 'en' else t_ru); rep(f'TXT_KEY_CHN1928_EVT_{eid}_TEXT', x_en if lang == 'en' else x_ru)
    for k2, v in EXTRA.items(): rep(k2, v)
    # unique units and buildings (text/uniques.py; Russian in ru.py)
    for u in uniques.UNITS + uniques.BUILDINGS:
        t = ('UNIT' if u in uniques.UNITS else 'BUILDING') + '_CHN1928_' + u['key']
        name, help_, strategy, pedia = (u['name'], u['help'], u['strategy'], u['pedia']) if lang == 'en' else RU_UNIQUES[u['key']]
        rep(f'TXT_KEY_{t}', name); rep(f'TXT_KEY_{t}_HELP', help_); rep(f'TXT_KEY_{t}_STRATEGY', strategy); rep(f'TXT_KEY_CIV5_CHN1928_{u["key"]}_TEXT', pedia)
    return rows
if __name__ == '__main__':
    rows_en = emit('en', F, CS_EN, EXTRA_EN); rows_ru = emit('ru', RU, RU_CS, RU_EXTRA)
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n<!-- China 1928: leader, civilization, city-state and event text (EN + RU). -->\n<GameData>\n  <Language_en_US>\n' + '\n'.join(rows_en) +
           '\n  </Language_en_US>\n  <Language_RU_RU>\n' + '\n'.join(rows_ru) + '\n  </Language_RU_RU>\n</GameData>\n')
    open(OUT, 'w', encoding='utf-8').write(xml)
    print('wrote', OUT, len(rows_en), 'EN +', len(rows_ru), 'RU rows')
    sql_out = os.path.join(HERE, '..', 'ui', 'China1928_Uniques.sql')
    open(sql_out, 'w', encoding='utf-8').write(uniques.sql())
    print('wrote', sql_out, len(uniques.UNITS), 'units +', len(uniques.BUILDINGS), 'buildings')
