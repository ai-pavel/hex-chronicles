----------------------------------------------------------------
-- China 1928: dated events. One turn = one week from 10 October 1928.
-- Sides: NAN (China donor), GMJ (Zulu), SHX (Russia), FT (Germany), GX (Ethiopia), CCP (Shoshone), BARB (barbarians), and the
-- city-states JAPAN, SOVIET, WEIHAIWEI and GUANGDONG.
-- An event can give or take gold, spawn units in a named city (the first of a list that the side or a side at peace with it holds;
-- with "anywhere" next to the city whoever holds it, for guerrillas and invaders; the capital otherwise), at a named spot of the map,
-- remove units by name or around a city, declare war ("war"), make peace ("peace"), declare friendship ("friends"), hand cities over
-- ("transfer"), rename a city ("rename"), found a city ("found"), act for further sides ("also"), require a city to be held by given
-- sides ("onlyif"), and always shows a popup.
----------------------------------------------------------------
local kSideCiv = { NAN = "CIVILIZATION_CHINA", GMJ = "CIVILIZATION_ZULU", SHX = "CIVILIZATION_RUSSIA", FT = "CIVILIZATION_GERMANY", GX = "CIVILIZATION_ETHIOPIA", CCP = "CIVILIZATION_SHOSHONE" }
local kSideMinor = { JAPAN = "MINOR_CIV_CHN1928_JAPAN", SOVIET = "MINOR_CIV_CHN1928_SOVIET", WEIHAIWEI = "MINOR_CIV_CHN1928_WEIHAIWEI", GUANGDONG = "MINOR_CIV_CHN1928_GUANGDONG" }
-- map plots of the places the events name that are not cities (filled in by gen_china1928.py from longitude and latitude)
local kSpots = {} -- @SPOTS@
local DAYS_PER_TURN = 7

local function DaysFromCivil(y, m, d)
	if m <= 2 then y = y - 1 end
	local era = math.floor(y / 400); local yoe = y - era * 400; local mp = (m + 9) % 12
	local doy = math.floor((153 * mp + 2) / 5) + d - 1
	local doe = yoe * 365 + math.floor(yoe / 4) - math.floor(yoe / 100) + doy
	return era * 146097 + doe - 719468
end
local kStart = DaysFromCivil(1928, 10, 10)
local function Turn(date)
	local y, m, d = date:match("(%d+)-(%d+)-(%d+)")
	return math.floor((DaysFromCivil(tonumber(y), tonumber(m), tonumber(d)) - kStart) / DAYS_PER_TURN)
end

local WHAMPOA = { "PROMOTION_DRILL_1", "PROMOTION_SHOCK_1" }    -- Nanjing's central divisions
local NWARMY = { "PROMOTION_DRILL_1", "PROMOTION_MARCH" }       -- Feng Yuxiang's Northwest Army
local GXARMY = { "PROMOTION_DRILL_1", "PROMOTION_DRILL_2" }     -- the Guangxi divisions
local RED = { "PROMOTION_DRILL_1", "PROMOTION_MARCH" }          -- the Red Army
local KWANTUNG = { "PROMOTION_DRILL_1", "PROMOTION_SHOCK_1" }   -- the Kwantung Army
local ALL_CHINA = { "NAN", "GMJ", "SHX", "FT", "GX", "CCP" }
local kEvents = {
	-- the National Government (Chiang Kai-shek)
	{ date = "1928-10-10", side = "NAN", id = "NAN_CHAIRMAN", gold = 300 },
	{ date = "1929-01-01", side = "NAN", id = "NAN_DISBANDMENT", gold = 400, also = { { side = "GMJ", gold = -150 }, { side = "SHX", gold = -150 }, { side = "GX", gold = -150 } } },
	{ date = "1929-03-26", side = "NAN", id = "NAN_GUANGXI_WAR", war = { "GX" }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Jiujiang", "Anqing", "Nanjing" }, n = 3, promos = WHAMPOA, name = "Central Army" }, { type = "UNIT_ARTILLERY", city = { "Jiujiang", "Anqing", "Nanjing" }, n = 1, name = "Field Battery" } },
		also = { { side = "GX", remove = { near = "Tangshan", radius = 4, n = 6 } } } },
	{ date = "1929-04-05", side = "NAN", id = "NAN_WUHAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Hankou", "Jiujiang", "Nanjing" }, n = 2, name = "Central Army" } }, also = { { side = "GX", gold = -300, remove = { near = "Hankou", radius = 3, n = 2 } } } },
	{ date = "1930-05-11", side = "NAN", id = "NAN_CENTRAL_PLAINS", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Xuzhou", "Bengbu", "Nanjing" }, n = 4, promos = WHAMPOA, name = "Central Army" }, { type = "UNIT_ARTILLERY", city = { "Xuzhou", "Bengbu", "Nanjing" }, n = 2, name = "Field Battery" }, { type = "UNIT_WWI_BOMBER", city = { "Xuzhou", "Nanjing" }, n = 1, name = "Nanjing Air Squadron" } } },
	{ date = "1930-11-04", side = "NAN", id = "NAN_PLAINS_END", gold = 500, peace = { "GMJ", "SHX" }, also = { { side = "GMJ", remove = { names = { "Guominjun", "Big Sword Brigade" }, n = 5 } }, { side = "SHX", gold = -400 } } },
	{ date = "1930-11-05", side = "NAN", id = "NAN_ENCIRCLE_1", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Ji'an", "Nanchang" }, n = 3, name = "Bandit Suppression Division" } } },
	{ date = "1931-04-01", side = "NAN", id = "NAN_ENCIRCLE_2", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Ji'an", "Ganzhou", "Nanchang" }, n = 4, name = "Bandit Suppression Division" }, { type = "UNIT_ARTILLERY", city = { "Ji'an", "Nanchang" }, n = 1, name = "Field Battery" } } },
	{ date = "1931-07-01", side = "NAN", id = "NAN_ENCIRCLE_3", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Nanchang" }, n = 4, promos = WHAMPOA, name = "Central Army" }, { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Ji'an", "Nanchang" }, n = 2, name = "Bandit Suppression Division" } } },
	{ date = "1931-07-28", side = "NAN", id = "NAN_FLOODS", gold = -600, also = { { side = "GX", gold = -200 } } },
	{ date = "1932-01-01", side = "NAN", id = "NAN_REUNION", gold = 300, peace = { "GX" } },
	{ date = "1933-02-01", side = "NAN", id = "NAN_ENCIRCLE_4", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Nanchang" }, n = 4, promos = WHAMPOA, name = "Central Army" } } },
	{ date = "1933-09-25", side = "NAN", id = "NAN_ENCIRCLE_5", gold = 500, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Nanchang" }, n = 5, promos = WHAMPOA, name = "German-trained Division" }, { type = "UNIT_ARTILLERY", city = { "Nanchang" }, n = 2, name = "Field Battery" }, { type = "UNIT_WWI_BOMBER", city = { "Nanchang" }, n = 2, name = "Nanchang Air Squadron" }, { type = "UNIT_WORKER", city = { "Nanchang" }, n = 2, name = "Blockhouse Builders" } } },
	{ date = "1934-02-19", side = "NAN", id = "NAN_NEW_LIFE", gold = 200 },
	{ date = "1935-11-04", side = "NAN", id = "NAN_FABI", gold = 1000 },
	{ date = "1936-07-18", side = "NAN", id = "NAN_CANTON", transfer = { from = "GUANGDONG", all = true } },
	{ date = "1936-12-25", side = "NAN", id = "NAN_XIAN_RELEASE", peace = { "CCP" }, also = { { side = "FT", gold = -500 } } },
	{ date = "1937-07-07", side = "JAPAN", id = "JAPAN_MARCO_POLO", war = ALL_CHINA, units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "FENGTAI", n = 4, promos = KWANTUNG, name = "China Garrison Army" }, { type = "UNIT_ARTILLERY", spot = "FENGTAI", n = 2, name = "Japanese Field Artillery" }, { type = "UNIT_WWI_TANK", spot = "FENGTAI", n = 1, name = "Type 89 Tanks" }, { type = "UNIT_GREAT_WAR_INFANTRY", city = "Dairen", n = 3, promos = KWANTUNG, name = "Kwantung Army" } } },
	-- the Guominjun (Feng Yuxiang)
	{ date = "1929-04-01", side = "GMJ", id = "GMJ_FAMINE", gold = -300, also = { { side = "BARB", units = { { type = "UNIT_RIFLEMAN", city = { "Tianshui", "Pingliang", "Lanzhou" }, n = 2, name = "Famine Bandits" }, { type = "UNIT_RIFLEMAN", city = { "Baoji", "Xi'an" }, n = 1, name = "Famine Bandits" } } } } },
	{ date = "1929-05-22", side = "GMJ", id = "GMJ_HAN_FUJU", remove = { near = "Luoyang", radius = 4, n = 2 }, also = { { side = "NAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Xuzhou", "Nanjing" }, n = 2, name = "Han Fuju's Army" }, { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Bengbu", "Nanjing" }, n = 1, name = "Shi Yousan's Army" } } } } },
	{ date = "1929-10-10", side = "GMJ", id = "GMJ_WAR_1929", war = { "NAN" }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Luoyang", "Xi'an", "Kaifeng" }, n = 3, promos = NWARMY, name = "Guominjun" }, { type = "UNIT_CAVALRY", city = { "Luoyang", "Xi'an" }, n = 1, name = "Northwest Cavalry" } } },
	{ date = "1930-05-11", side = "GMJ", id = "GMJ_CENTRAL_PLAINS", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Kaifeng", "Xi'an" }, n = 4, promos = NWARMY, name = "Guominjun" }, { type = "UNIT_ARTILLERY", city = { "Kaifeng", "Xi'an" }, n = 1, name = "Field Battery" }, { type = "UNIT_CAVALRY", city = { "Kaifeng" }, n = 1, name = "Northwest Cavalry" } } },
	{ date = "1933-05-26", side = "GMJ", id = "GMJ_CHAHAR", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Zhangjiakou", "Datong" }, n = 3, promos = NWARMY, name = "Anti-Japanese Allied Army" }, { type = "UNIT_CAVALRY", city = { "Zhangjiakou", "Datong" }, n = 1, name = "Anti-Japanese Allied Army" } } },
	{ date = "1933-08-05", side = "GMJ", id = "GMJ_CHAHAR_END", remove = { names = { "Anti-Japanese Allied Army" }, n = 4 } },
	-- Shanxi (Yan Xishan)
	{ date = "1930-04-01", side = "SHX", id = "SHX_COALITION", war = { "NAN" }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Shijiazhuang", "Taiyuan" }, n = 3, name = "Shanxi Army" }, { type = "UNIT_ARTILLERY", city = { "Taiyuan" }, n = 1, name = "Taiyuan Mountain Battery" } }, also = { { side = "GX", war = { "NAN" } } } },
	{ date = "1930-09-09", side = "SHX", id = "SHX_BEIPING_GOVT", gold = 400 },
	{ date = "1930-09-18", side = "FT", id = "FT_INTO_THE_PASS", gold = 800, transfer = { from = "SHX", cities = { "Tianjin", "Beiping" } }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Beiping", "Jinzhou" }, n = 3, name = "Northeast Army" } } },
	{ date = "1932-02-29", side = "SHX", id = "SHX_RETURN", gold = 500 },
	{ date = "1933-08-01", side = "SHX", id = "SHX_INDUSTRY", gold = 600 },
	{ date = "1936-02-20", side = "CCP", id = "CCP_EASTERN_EXPEDITION", units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "YELLOW_RIVER_CROSSING", n = 3, promos = RED, name = "Red Army" } }, also = { { side = "NAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Taiyuan", "Linfen", "Luoyang" }, n = 2, name = "Central Army" } } } } },
	{ date = "1936-11-15", side = "BARB", id = "BARB_SUIYUAN", units = { { type = "UNIT_CAVALRY", spot = "SUIYUAN_NORTH", n = 3, name = "Inner Mongolian Army" }, { type = "UNIT_RIFLEMAN", spot = "SUIYUAN_NORTH", n = 2, name = "Grand Han Righteous Army" } } },
	{ date = "1936-11-24", side = "SHX", id = "SHX_BAILINGMIAO", gold = 300, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Guisui", "Baotou", "Datong" }, n = 2, name = "Fu Zuoyi's 35th Army" }, { type = "UNIT_CAVALRY", city = { "Guisui", "Baotou" }, n = 1, name = "Suiyuan Cavalry" } } },
	-- Fengtian (Zhang Xueliang)
	{ date = "1928-12-29", side = "FT", id = "FT_FLAG", gold = 300, friends = { "NAN" } },
	{ date = "1929-01-10", side = "FT", id = "FT_YANG_CHANG", gold = 300 },
	{ date = "1929-07-10", side = "FT", id = "FT_CER" },
	{ date = "1929-10-12", side = "SOVIET", id = "SOVIET_LAHASUSU", war = { "FT" }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "LAHASUSU", n = 2, name = "Special Far Eastern Army" } } },
	{ date = "1929-11-17", side = "SOVIET", id = "SOVIET_MANZHOULI", units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "MANZHOULI_FRONT", n = 3, name = "Special Far Eastern Army" }, { type = "UNIT_WWI_TANK", spot = "MANZHOULI_FRONT", n = 1, name = "MS-1 Tanks" }, { type = "UNIT_CAVALRY", spot = "MANZHOULI_FRONT", n = 1, name = "Buryat-Mongol Cavalry" } } },
	{ date = "1929-12-22", side = "SOVIET", id = "SOVIET_KHABAROVSK", peace = { "FT" }, remove = { names = { "Special Far Eastern Army", "MS-1 Tanks", "Buryat-Mongol Cavalry" }, n = 8 } },
	{ date = "1931-09-18", side = "JAPAN", id = "JAPAN_MUKDEN", war = { "FT" }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "MUKDEN_ZONE", n = 3, promos = KWANTUNG, name = "Kwantung Army" }, { type = "UNIT_ARTILLERY", spot = "MUKDEN_ZONE", n = 1, name = "Japanese Field Artillery" }, { type = "UNIT_GREAT_WAR_INFANTRY", spot = "CHANGCHUN_ZONE", n = 2, promos = KWANTUNG, name = "Kwantung Army" }, { type = "UNIT_GREAT_WAR_INFANTRY", spot = "ANDONG_ZONE", n = 1, promos = KWANTUNG, name = "Kwantung Army" } },
		also = { { side = "FT", gold = -500 } } },
	{ date = "1931-09-21", side = "JAPAN", id = "JAPAN_KOREA_ARMY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Pyongyang", "Seoul" }, n = 3, name = "Korea Army" }, { type = "UNIT_WWI_BOMBER", city = { "Pyongyang", "Seoul" }, n = 1, name = "Japanese Army Air Service" } } },
	{ date = "1931-11-04", side = "FT", id = "FT_NENJIANG", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Qiqihar", "Harbin", "Hailun" }, n = 2, name = "Ma Zhanshan's Heilongjiang Army" }, { type = "UNIT_CAVALRY", city = { "Qiqihar", "Hailun" }, n = 1, name = "Ma Zhanshan's Heilongjiang Army" } } },
	{ date = "1932-01-03", side = "JAPAN", id = "JAPAN_JINZHOU", units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "JINZHOU_FRONT", n = 3, promos = KWANTUNG, name = "Kwantung Army" }, { type = "UNIT_WWI_BOMBER", city = "Dairen", n = 1, name = "Japanese Army Air Service" } } },
	{ date = "1932-01-28", side = "JAPAN", id = "JAPAN_SHANGHAI", war = { "NAN" }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "WUSONG", n = 3, promos = KWANTUNG, name = "Shanghai Expeditionary Army" }, { type = "UNIT_BATTLESHIP", spot = "WUSONG_SEA", n = 1, name = "Third Fleet" }, { type = "UNIT_DESTROYER", spot = "WUSONG_SEA", n = 2, name = "Third Fleet" } },
		also = { { side = "NAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Shanghai", n = 3, promos = { "PROMOTION_DRILL_1", "PROMOTION_COVER_1" }, name = "19th Route Army" }, { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Suzhou", "Shanghai", "Nanjing" }, n = 2, promos = WHAMPOA, name = "Fifth Army" } } } } },
	{ date = "1932-02-05", side = "JAPAN", id = "JAPAN_HARBIN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "HARBIN_FRONT", n = 3, promos = KWANTUNG, name = "Kwantung Army" } } },
	{ date = "1932-03-01", side = "JAPAN", id = "JAPAN_MANCHUKUO", rename = { city = "Changchun", name = "Xinjing", held = { "JAPAN" } }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Changchun", "Xinjing", "Mukden", "Dairen" }, n = 3, name = "Manchukuo Imperial Army" } } },
	{ date = "1932-05-05", side = "JAPAN", id = "JAPAN_SHANGHAI_TRUCE", peace = { "NAN" }, remove = { names = { "Shanghai Expeditionary Army", "Third Fleet" }, n = 6 } },
	{ date = "1933-01-01", side = "JAPAN", id = "JAPAN_SHANHAIGUAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "SHANHAIGUAN_FRONT", n = 3, promos = KWANTUNG, name = "Kwantung Army" }, { type = "UNIT_ARTILLERY", spot = "SHANHAIGUAN_FRONT", n = 1, name = "Japanese Field Artillery" } } },
	{ date = "1933-02-23", side = "JAPAN", id = "JAPAN_REHE", war = { "SHX", "NAN" }, units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "REHE_FRONT", n = 4, promos = KWANTUNG, name = "Kwantung Army" }, { type = "UNIT_WWI_TANK", spot = "REHE_FRONT", n = 1, name = "Kawahara Motorised Unit" }, { type = "UNIT_CAVALRY", spot = "REHE_FRONT", n = 1, name = "Manchukuo Cavalry" } } },
	{ date = "1933-03-11", side = "FT", id = "FT_RESIGNATION", gold = -300 },
	{ date = "1933-05-31", side = "JAPAN", id = "JAPAN_TANGGU", peace = { "FT", "NAN", "SHX", "GMJ" } },
	{ date = "1934-03-01", side = "FT", id = "FT_RETURN", gold = 500, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Hankou", "Kaifeng", "Xi'an", "Beiping" }, n = 3, name = "Northeast Army" } } },
	{ date = "1935-06-10", side = "JAPAN", id = "JAPAN_HE_UMEZU", also = { { side = "NAN", gold = -300 }, { side = "FT", remove = { near = "Beiping", radius = 4, n = 2 } } } },
	{ date = "1935-10-01", side = "FT", id = "FT_NORTHWEST", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Xi'an", "Lanzhou", "Hankou" }, n = 3, name = "Northeast Army" }, { type = "UNIT_GREAT_GENERAL", city = { "Xi'an", "Hankou" }, n = 1, name = "Northwest Bandit Suppression Headquarters" } } },
	{ date = "1935-11-25", side = "JAPAN", id = "JAPAN_EAST_HEBEI" },
	{ date = "1936-12-12", side = "FT", id = "FT_XIAN", peace = { "CCP" } },
	-- Guangxi (Li Zongren)
	{ date = "1929-02-21", side = "GX", id = "GX_HUNAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Yueyang", "Changsha", "Hankou" }, n = 2, promos = GXARMY, name = "Fourth Group Army" } } },
	{ date = "1930-06-04", side = "GX", id = "GX_CHANGSHA", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Guilin", "Nanning" }, n = 3, promos = GXARMY, name = "Guangxi Army" } } },
	{ date = "1931-05-28", side = "GX", id = "GX_CANTON_GOVT", gold = 500 },
	{ date = "1932-06-01", side = "GX", id = "GX_THREE_SELFS", gold = 300, units = { { type = "UNIT_RIFLEMAN", city = { "Guilin", "Nanning" }, n = 2, name = "Guangxi Militia" } } },
	{ date = "1936-06-01", side = "GX", id = "GX_LIANGGUANG", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Guilin", "Nanning" }, n = 3, promos = GXARMY, name = "Guangxi Army" } } },
	-- the Chinese Communists (Mao Zedong, Zhu De)
	{ date = "1928-12-10", side = "CCP", id = "CCP_PENG", units = { { type = "UNIT_RIFLEMAN", city = "Jinggangshan", n = 2, promos = RED, name = "Fifth Red Army" } } },
	{ date = "1929-01-14", side = "CCP", id = "CCP_GANNAN", units = { { type = "UNIT_RIFLEMAN", city = { "Ruijin", "Jinggangshan" }, anywhere = true, n = 2, promos = RED, name = "Fourth Red Army" } } },
	{ date = "1929-03-14", side = "CCP", id = "CCP_CHANGTING", gold = 300, units = { { type = "UNIT_RIFLEMAN", city = { "Ruijin" }, anywhere = true, n = 1, promos = RED, name = "Fourth Red Army" } } },
	{ date = "1929-12-28", side = "CCP", id = "CCP_GUTIAN", units = { { type = "UNIT_GREAT_GENERAL", city = { "Ruijin", "Jinggangshan" }, anywhere = true, n = 1, name = "Front Committee" } } },
	{ date = "1930-07-27", side = "CCP", id = "CCP_CHANGSHA", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Changsha", anywhere = true, n = 2, promos = RED, name = "Third Red Army Group" } } },
	{ date = "1930-12-30", side = "CCP", id = "CCP_LONGGANG", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Ruijin" }, anywhere = true, n = 2, promos = RED, name = "First Red Army Group" }, { type = "UNIT_ARTILLERY", city = { "Ruijin" }, anywhere = true, n = 1, name = "Captured Battery" } } },
	{ date = "1931-11-07", side = "CCP", id = "CCP_SOVIET_REPUBLIC", gold = 500, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Ruijin", "Jinggangshan" }, anywhere = true, n = 2, promos = RED, name = "Red Army" } } },
	{ date = "1931-12-14", side = "CCP", id = "CCP_NINGDU", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Ruijin", anywhere = true, n = 3, name = "Fifth Red Army Group" }, { type = "UNIT_MACHINE_GUN", city = "Ruijin", anywhere = true, n = 1, name = "Fifth Red Army Group" } } },
	{ date = "1934-10-10", side = "CCP", id = "CCP_LONG_MARCH", units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "YUDU", n = 4, promos = RED, name = "Central Red Army" } } },
	{ date = "1934-12-01", side = "CCP", id = "CCP_XIANG_RIVER", remove = { names = { "Central Red Army" }, n = 2 } },
	{ date = "1935-01-15", side = "CCP", id = "CCP_ZUNYI", units = { { type = "UNIT_GREAT_GENERAL", city = "Zunyi", anywhere = true, n = 1, name = "Mao Zedong" } } },
	{ date = "1935-05-29", side = "CCP", id = "CCP_LUDING", units = { { type = "UNIT_RIFLEMAN", spot = "LUDING", n = 1, promos = RED, name = "Luding Vanguard" } } },
	{ date = "1935-10-19", side = "CCP", id = "CCP_SHAANBEI", units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "WUQI", n = 2, promos = RED, name = "Shaanbei Red Army" } } },
	{ date = "1935-11-10", side = "CCP", id = "CCP_WAYAOBAO", found = { spot = "WAYAOBAO", name = "Wayaobao" }, units = { { type = "UNIT_RIFLEMAN", spot = "WAYAOBAO", n = 1, promos = RED, name = "Red Guards" } } },
	{ date = "1936-10-22", side = "CCP", id = "CCP_HUINING", units = { { type = "UNIT_GREAT_WAR_INFANTRY", spot = "HUINING", n = 3, promos = RED, name = "Second Front Army" }, { type = "UNIT_GREAT_WAR_INFANTRY", spot = "HUINING", n = 2, promos = RED, name = "Fourth Front Army" } } },
	-- the colonies
	{ date = "1930-10-01", side = "NAN", id = "NAN_WEIHAIWEI", transfer = { from = "WEIHAIWEI", all = true } },
	-- bandits and rebels
	{ date = "1933-11-22", side = "BARB", id = "BARB_FUJIAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Fuzhou", "Xiamen" }, n = 3, name = "People's Revolutionary Army" }, { type = "UNIT_MACHINE_GUN", city = { "Fuzhou" }, n = 1, name = "People's Revolutionary Army" } },
		also = { { side = "NAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Jian'ou", "Wenzhou", "Nanchang" }, n = 3, promos = WHAMPOA, name = "Central Army" } } } } },
	{ date = "1934-01-13", side = "NAN", id = "NAN_FUZHOU", gold = 200, also = { { side = "BARB", remove = { names = { "People's Revolutionary Army" }, n = 4 } } } },
}
local kRecurring = {
	{ start = "1928-11-07", every = 8, side = "NAN", id = "NAN_LEVY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Nanjing", n = 1, name = "Central Army" } } },
	{ start = "1928-11-14", every = 10, side = "GMJ", id = "GMJ_LEVY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Xi'an", "Kaifeng" }, n = 1, name = "Guominjun" } } },
	{ start = "1928-11-21", every = 10, side = "SHX", id = "SHX_LEVY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Taiyuan", n = 1, name = "Shanxi Army" } } },
	{ start = "1928-11-28", every = 10, side = "FT", id = "FT_LEVY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Mukden", "Beiping", "Xi'an" }, n = 1, name = "Northeast Army" } } },
	{ start = "1928-12-05", every = 10, side = "GX", id = "GX_LEVY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Guilin", "Nanning" }, n = 1, name = "Guangxi Army" } } },
	{ start = "1928-12-12", every = 6, side = "CCP", id = "CCP_LEVY", units = { { type = "UNIT_RIFLEMAN", city = { "Ruijin", "Wayaobao", "Jinggangshan" }, anywhere = true, n = 1, promos = RED, name = "Red Guards" } } },
	{ start = "1932-04-06", stop = "1935-01-01", every = 8, side = "FT", id = "FT_VOLUNTEERS", units = { { type = "UNIT_RIFLEMAN", city = { "Harbin", "Jilin", "Qiqihar" }, anywhere = true, n = 1, name = "Northeast Volunteer Army" } } },
	{ start = "1931-11-11", every = 8, side = "JAPAN", id = "JAPAN_REINFORCE", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Mukden", "Xinjing", "Changchun", "Dairen" }, n = 1, promos = KWANTUNG, name = "Kwantung Army" } } },
	{ start = "1929-01-02", every = 12, side = "BARB", id = "BARB_HENAN", units = { { type = "UNIT_RIFLEMAN", city = { "Nanyang", "Luoyang" }, n = 1, name = "Henan Bandits" } } },
	{ start = "1929-02-06", every = 12, side = "BARB", id = "BARB_SHANDONG", units = { { type = "UNIT_RIFLEMAN", city = { "Jining", "Haizhou" }, n = 1, name = "Red Spears" } } },
	{ start = "1929-03-06", every = 12, side = "BARB", id = "BARB_HONGHUZI", units = { { type = "UNIT_CAVALRY", city = { "Jiamusi", "Hailun", "Harbin" }, n = 1, name = "Honghuzi" } } },
	{ start = "1929-04-03", every = 12, side = "BARB", id = "BARB_SOUTH", units = { { type = "UNIT_RIFLEMAN", city = { "Longyan", "Chenzhou", "Hechi", "Baise" }, n = 1, name = "Hill Bandits" } } },
}

----------------------------------------------------------------
local function FindPlayer(side)
	if side == "BARB" then return Players[GameDefines.MAX_CIV_PLAYERS] end
	local minorType = kSideMinor[side]
	if minorType then
		local info = GameInfo.MinorCivilizations[minorType]
		if not info then return nil end
		for i = GameDefines.MAX_MAJOR_CIVS, GameDefines.MAX_CIV_PLAYERS - 1 do
			local p = Players[i]
			if p and p:IsAlive() and p:IsMinorCiv() and p:GetMinorCivType() == info.ID then return p end
		end
		return nil
	end
	local civType = kSideCiv[side]
	for i = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
		local p = Players[i]
		if p and p:IsAlive() then
			local info = GameInfo.Civilizations[p:GetCivilizationType()]
			if info and info.Type == civType then return p end
		end
	end
	return nil
end
local function FindCity(name)
	for i = 0, GameDefines.MAX_CIV_PLAYERS do
		local p = Players[i]
		if p and p:IsAlive() then
			for city in p:Cities() do
				if city:GetName() == name then return city, p end
			end
		end
	end
	return nil
end
-- a city the side may muster in: its own, or one of a player it is not at war with (allies, city-states)
local function Friendly(pPlayer, pOwner)
	if pOwner == pPlayer then return true end
	return not Teams[pPlayer:GetTeam()]:IsAtWar(pOwner:GetTeam())
end
local function SpotPlot(name)
	local s = kSpots[name]
	return s and Map.GetPlot(s[1], s[2]) or nil
end
local function FindCityPlot(pPlayer, side, spec)
	if spec.spot then
		local plot = SpotPlot(spec.spot)
		if plot then return plot end
	end
	local names = spec.city or {}
	if type(names) ~= "table" then names = { names } end
	for _, name in ipairs(names) do
		local city, pOwner = FindCity(name)
		if city and (side == "BARB" or spec.anywhere or Friendly(pPlayer, pOwner)) then return city:Plot() end
	end
	local cap = pPlayer and pPlayer:GetCapitalCity()
	return cap and cap:Plot() or nil
end
local function Spawn(pPlayer, side, spec)
	local unitInfo = GameInfo.Units[spec.type]; local plot = FindCityPlot(pPlayer, side, spec)
	if not (unitInfo and plot) then return end
	for i = 1, spec.n or 1 do
		local unit = pPlayer:InitUnit(unitInfo.ID, plot:GetX(), plot:GetY())
		if unit then
			pcall(function() unit:JumpToNearestValidPlot() end)
			for _, promo in ipairs(spec.promos or {}) do local p = GameInfo.UnitPromotions[promo]; if p then unit:SetHasPromotion(p.ID, true) end end
			-- no starting experience: promotions come from the spec, a pending promotion would stop the unit every turn
			if spec.name then pcall(function() unit:SetName(spec.name) end) end
		end
	end
end
local function Remove(pPlayer, spec)
	local left = spec.n or 1; local doomed = {}
	local center = nil
	if spec.near then local city = FindCity(spec.near); center = city and city:Plot() end
	if spec.near and not center then return end
	for unit in pPlayer:Units() do
		if left <= 0 then break end
		local hit = false
		if center then
			hit = unit:IsCombatUnit() and Map.PlotDistance(unit:GetX(), unit:GetY(), center:GetX(), center:GetY()) <= (spec.radius or 3)
		else
			local nm = unit:GetNameNoDesc()
			for _, want in ipairs(spec.names) do
				if nm == want then hit = true; break end
			end
		end
		if hit then table.insert(doomed, unit); left = left - 1 end
	end
	for _, unit in ipairs(doomed) do unit:Kill(true, -1) end
end
local function DeclareWar(a, b)
	if not (a and b) or a == b then return end
	local ta = Teams[a:GetTeam()]; local tb = b:GetTeam()
	if ta and not ta:IsAtWar(tb) then ta:DeclareWar(tb) end
end
local function MakePeace(a, b)
	if not (a and b) or a == b then return end
	local ta = Teams[a:GetTeam()]; local tb = b:GetTeam()
	if ta and ta:IsAtWar(tb) then ta:MakePeace(tb) end
end
local function Friends(a, b)
	if a and b and a ~= b and not a:IsMinorCiv() and not b:IsMinorCiv() and not a:IsDoF(b:GetID()) then a:DoForceDoF(b:GetID()) end
end
local function Holds(cond)
	local city, pOwner = FindCity(cond.city)
	if not city then return false end
	for _, side in ipairs(cond.held) do
		if pOwner == FindPlayer(side) then return true end
	end
	return false
end
-- hand cities over without a fight (the Northeast Army entering Beiping, the rendition of Weihaiwei, Canton in 1936)
local function Transfer(pPlayer, spec)
	local pFrom = FindPlayer(spec.from)
	if not pFrom or pFrom == pPlayer then return end
	local list = {}
	if spec.all then
		for city in pFrom:Cities() do table.insert(list, city) end
		table.sort(list, function(a, b) return (a:IsCapital() and 1 or 0) < (b:IsCapital() and 1 or 0) end)   -- the capital last
	else
		for _, name in ipairs(spec.cities or {}) do
			local city, pOwner = FindCity(name)
			if city and pOwner == pFrom then table.insert(list, city) end
		end
	end
	for _, city in ipairs(list) do pcall(function() pPlayer:AcquireCity(city, false, true) end) end
end
local function Rename(spec)
	local city, pOwner = FindCity(spec.city)
	if not city then return end
	for _, side in ipairs(spec.held or {}) do
		if pOwner == FindPlayer(side) then city:SetName(spec.name); return end
	end
end
-- found a city at a spot or the nearest free land around it (the Communist base in northern Shaanxi)
local function Found(pPlayer, spec)
	if FindCity(spec.name) then return end
	local plot = SpotPlot(spec.spot)
	if not plot then return end
	for r = 0, 3 do
		for dx = -r, r do
			for dy = -r, r do
				local p = Map.GetPlot(plot:GetX() + dx, plot:GetY() + dy)
				if p and not p:IsWater() and not p:IsMountain() and not p:IsCity() and Map.PlotDistance(p:GetX(), p:GetY(), plot:GetX(), plot:GetY()) == r then
					local clear = true
					for i = 0, GameDefines.MAX_CIV_PLAYERS do
						local q = Players[i]
						if q and q:IsAlive() then
							for city in q:Cities() do
								if Map.PlotDistance(city:GetX(), city:GetY(), p:GetX(), p:GetY()) < 3 then clear = false; break end
							end
						end
						if not clear then break end
					end
					if clear then
						pPlayer:InitCity(p:GetX(), p:GetY())
						local city = p:GetPlotCity()
						if city then pcall(function() city:SetName(spec.name) end) end
						return
					end
				end
			end
		end
	end
end
local function ApplyTo(side, ev)
	local pPlayer = FindPlayer(side)
	if not pPlayer then return end
	if ev.gold and side ~= "BARB" then pPlayer:ChangeGold(math.max(ev.gold, -pPlayer:GetGold())) end
	-- wars first, so that invaders can stand in the country they invade
	for _, other in ipairs(ev.war or {}) do pcall(DeclareWar, pPlayer, FindPlayer(other)) end
	for _, other in ipairs(ev.peace or {}) do pcall(MakePeace, pPlayer, FindPlayer(other)) end
	for _, other in ipairs(ev.friends or {}) do pcall(Friends, pPlayer, FindPlayer(other)) end
	if ev.transfer then pcall(Transfer, pPlayer, ev.transfer) end
	if ev.found then pcall(Found, pPlayer, ev.found) end
	if ev.rename then pcall(Rename, ev.rename) end
	for _, spec in ipairs(ev.units or {}) do Spawn(pPlayer, side, spec) end
	if ev.remove then Remove(pPlayer, ev.remove) end
end
local function Apply(ev)
	local pSide = FindPlayer(ev.side)
	if ev.side ~= "BARB" and not pSide then return end   -- the side is gone: its events lapse
	if ev.onlyif and not Holds(ev.onlyif) then return end
	ApplyTo(ev.side, ev)
	for _, other in ipairs(ev.also or {}) do pcall(ApplyTo, other.side, other) end
	if ev.quiet and pSide ~= Players[Game.GetActivePlayer()] then return end   -- recurring levies: only their own side is told
	local who = Locale.ConvertTextKey("TXT_KEY_CHN1928_SIDE_" .. ev.side)
	local title = Locale.ConvertTextKey("TXT_KEY_CHN1928_EVT_" .. ev.id .. "_TITLE")
	local text = Locale.ConvertTextKey("TXT_KEY_CHN1928_EVT_" .. ev.id .. "_TEXT")
	local header = string.format("[COLOR_YELLOW]%s[ENDCOLOR][NEWLINE]%s%s[NEWLINE][NEWLINE]", title, who, (ev.date and ev.date ~= "" and (", " .. ev.date) or ""))
	Events.SerialEventGameMessagePopup({ Type = ButtonPopupTypes.BUTTONPOPUP_TEXT, Data1 = 520, Text = header .. text })
end

----------------------------------------------------------------
local function Key(id, turn) return string.format("CHN1928_EVT_%s_%d", id, turn) end
local function AlreadyFired(key) local ok, v = pcall(function() return Modding.OpenSaveData().GetValue(key) end); return ok and v ~= nil end
local function MarkFired(key) pcall(function() Modding.OpenSaveData().SetValue(key, 1) end) end
local function ProcessTurn()
	local turn = Game.GetGameTurn()
	for i, ev in ipairs(kEvents) do
		if Turn(ev.date) == turn and not AlreadyFired(Key(i, turn)) then
			MarkFired(Key(i, turn)); local ok, err = pcall(Apply, ev)
			if not ok then print("China 1928 event failed: " .. tostring(err)) end
		end
	end
	for i, rec in ipairs(kRecurring) do
		local t0 = Turn(rec.start)
		if turn >= t0 and (not rec.stop or turn <= Turn(rec.stop)) and (turn - t0) % rec.every == 0 and not AlreadyFired(Key("R" .. i, turn)) then
			MarkFired(Key("R" .. i, turn)); local ok, err = pcall(Apply, { side = rec.side, id = rec.id, gold = rec.gold, units = rec.units, date = "", quiet = true })
			if not ok then print("China 1928 recurring event failed: " .. tostring(err)) end
		end
	end
end
Events.ActivePlayerTurnStart.Add(function() pcall(ProcessTurn) end)
