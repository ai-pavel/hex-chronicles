----------------------------------------------------------------
-- Spain 1936: dated events. One turn = one week from 25 July 1936.
-- Sides: REP (Russia donor), NAT (Zulu), NORTH (Germany), CAT (Shoshone), EUZ (Ethiopia), CNT (Aztec), BARB (barbarians).
-- An event can give or take gold, spawn units in a named city (the first of a list that the side or a side at peace with it
-- holds; the capital otherwise; barbarians take any city), remove units by name, declare war ("war"), make peace ("peace"),
-- act for a second side ("also"), require a city to be held by given sides ("onlyif"), and always shows a popup.
----------------------------------------------------------------
local kSideCiv = { REP = "CIVILIZATION_RUSSIA", NAT = "CIVILIZATION_ZULU", NORTH = "CIVILIZATION_GERMANY", CAT = "CIVILIZATION_SHOSHONE", EUZ = "CIVILIZATION_ETHIOPIA", CNT = "CIVILIZATION_AZTEC" }
local DAYS_PER_TURN = 7

local function DaysFromCivil(y, m, d)
	if m <= 2 then y = y - 1 end
	local era = math.floor(y / 400); local yoe = y - era * 400; local mp = (m + 9) % 12
	local doy = math.floor((153 * mp + 2) / 5) + d - 1
	local doe = yoe * 365 + math.floor(yoe / 4) - math.floor(yoe / 100) + doy
	return era * 146097 + doe - 719468
end
local kStart = DaysFromCivil(1936, 7, 25)
local function Turn(date)
	local y, m, d = date:match("(%d+)-(%d+)-(%d+)")
	return math.floor((DaysFromCivil(tonumber(y), tonumber(m), tonumber(d)) - kStart) / DAYS_PER_TURN)
end

local LEGION = { "PROMOTION_DRILL_1", "PROMOTION_SHOCK_1" }      -- the Spanish Legion
local REGULARES = { "PROMOTION_SHOCK_1" }                         -- Moroccan Regulares, Navarrese requetes
local GUARD = { "PROMOTION_DRILL_1", "PROMOTION_COVER_1" }        -- Assault Guards
local COLUMN = { "PROMOTION_SHOCK_1", "PROMOTION_MARCH" }         -- the confederal columns
local IB = { "PROMOTION_DRILL_1", "PROMOTION_SHOCK_1" }           -- International Brigades
local kEvents = {
	-- the Nationalists of the South (Franco)
	{ date = "1936-08-01", side = "NAT", id = "NAT_AIRLIFT", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Seville", n = 2, promos = LEGION, name = "Spanish Legion" }, { type = "UNIT_RIFLEMAN", city = "Seville", n = 1, promos = REGULARES, name = "Regulares" }, { type = "UNIT_WWI_BOMBER", city = "Seville", n = 1, name = "Ju 52" } } },
	{ date = "1936-08-05", side = "NAT", id = "NAT_CONVOY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Cadiz", n = 1, promos = LEGION, name = "Spanish Legion" }, { type = "UNIT_RIFLEMAN", city = "Cadiz", n = 2, promos = REGULARES, name = "Regulares" }, { type = "UNIT_ARTILLERY", city = "Cadiz", n = 1, name = "Field Battery" } } },
	{ date = "1936-09-27", side = "NAT", id = "NAT_ALCAZAR", gold = 300, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Toledo", "Talavera" }, n = 2, promos = LEGION, name = "Spanish Legion" }, { type = "UNIT_RIFLEMAN", city = { "Toledo", "Talavera" }, n = 1, promos = REGULARES, name = "Regulares" } } },
	{ date = "1936-10-01", side = "NAT", id = "NAT_GENERALISIMO", gold = 1000, units = { { type = "UNIT_GREAT_GENERAL", city = "Seville", n = 1, name = "Franco's Headquarters" } }, also = { side = "NORTH", gold = 500 } },
	{ date = "1936-11-07", side = "NAT", id = "NAT_CONDOR", units = { { type = "UNIT_WWI_BOMBER", city = "Seville", n = 2, name = "Ju 52 (Condor Legion)" }, { type = "UNIT_TRIPLANE", city = "Seville", n = 2, name = "He 51 (Condor Legion)" }, { type = "UNIT_WWI_TANK", city = "Seville", n = 1, name = "Panzer I (Condor Legion)" }, { type = "UNIT_ANTI_AIRCRAFT_GUN", city = "Seville", n = 1, name = "88 mm Flak (Condor Legion)" } } },
	{ date = "1936-12-23", side = "NAT", id = "NAT_CTV", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Cadiz", n = 3, name = "Italian Blackshirts" }, { type = "UNIT_WWI_TANK", city = "Cadiz", n = 1, name = "CV-33 Tankettes" }, { type = "UNIT_TRIPLANE", city = "Cadiz", n = 1, name = "CR.32 (Aviazione Legionaria)" } } },
	{ date = "1937-03-08", side = "NAT", id = "NAT_GUADALAJARA", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Siguenza", "Soria", "Calatayud" }, n = 3, name = "CTV Division" }, { type = "UNIT_WWI_TANK", city = { "Siguenza", "Soria", "Calatayud" }, n = 1, name = "CV-33 Tankettes" } } },
	{ date = "1937-04-19", side = "NAT", id = "NAT_UNIFICATION", gold = 500, units = { { type = "UNIT_RIFLEMAN", city = "Seville", n = 2, name = "Falange Militia" } }, also = { side = "NORTH", units = { { type = "UNIT_RIFLEMAN", city = "Pamplona", n = 2, promos = REGULARES, name = "Requetes" } } } },
	{ date = "1937-12-29", side = "NAT", id = "NAT_TERUEL", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Calamocha", "Calatayud", "Zaragoza" }, n = 3, name = "Army of Castile" }, { type = "UNIT_ARTILLERY", city = { "Calamocha", "Calatayud", "Zaragoza" }, n = 2, name = "Field Battery" } } },
	{ date = "1938-03-07", side = "NAT", id = "NAT_ARAGON", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Zaragoza", "Belchite", "Calatayud" }, n = 4, name = "Moroccan Army Corps" }, { type = "UNIT_WWI_TANK", city = { "Zaragoza", "Calatayud" }, n = 2, name = "Panzer I" }, { type = "UNIT_WWI_BOMBER", city = { "Zaragoza", "Seville" }, n = 1, name = "SM.79 (Aviazione Legionaria)" } } },
	{ date = "1938-12-23", side = "NAT", id = "NAT_CATALONIA", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Lerida", "Fraga", "Zaragoza" }, n = 4, name = "Army of the North" }, { type = "UNIT_ARTILLERY", city = { "Lerida", "Fraga", "Zaragoza" }, n = 2, name = "Field Battery" }, { type = "UNIT_WWI_TANK", city = { "Lerida", "Fraga", "Zaragoza" }, n = 1, name = "Panzer I" } } },
	-- Mola's Army of the North
	{ date = "1936-08-01", side = "NORTH", id = "NORTH_REQUETES", units = { { type = "UNIT_RIFLEMAN", city = "Pamplona", n = 2, promos = REGULARES, name = "Requetes" } } },
	{ date = "1936-09-29", side = "NORTH", id = "NORTH_CANARIAS", units = { { type = "UNIT_BATTLESHIP", city = "El Ferrol", n = 1, name = "Canarias (heavy cruiser)" } } },
	{ date = "1937-03-31", side = "NORTH", id = "NORTH_BISCAY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Vitoria", "Burgos" }, n = 3, name = "Navarrese Brigade" }, { type = "UNIT_ARTILLERY", city = { "Vitoria", "Burgos" }, n = 2, name = "Field Battery" }, { type = "UNIT_WWI_BOMBER", city = { "Vitoria", "Burgos" }, n = 2, name = "Ju 52 (Condor Legion)" }, { type = "UNIT_TRIPLANE", city = { "Vitoria", "Burgos" }, n = 1, name = "He 51 (Condor Legion)" } } },
	{ date = "1937-06-03", side = "NORTH", id = "NORTH_MOLA" },
	{ date = "1937-08-14", side = "NORTH", id = "NORTH_SANTANDER", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Reinosa", "Burgos" }, n = 3, name = "Navarrese Brigade" } }, also = { side = "NAT", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Reinosa", "Burgos" }, n = 2, name = "CTV Division" } } } },
	{ date = "1937-09-01", side = "NORTH", id = "NORTH_ASTURIAS", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Leon", "Oviedo", "Santander" }, n = 3, name = "Navarrese Brigade" }, { type = "UNIT_ARTILLERY", city = { "Leon", "Oviedo" }, n = 1, name = "Field Battery" } } },
	-- the Republic
	{ date = "1936-08-08", side = "REP", id = "REP_NONINTERVENTION", gold = -300 },
	{ date = "1936-09-04", side = "REP", id = "REP_LARGO", gold = 800 },
	{ date = "1936-10-12", side = "REP", id = "REP_SOVIET", units = { { type = "UNIT_WWI_TANK", city = "Cartagena", n = 2, name = "T-26" }, { type = "UNIT_TRIPLANE", city = "Cartagena", n = 2, name = "I-15 Chato" }, { type = "UNIT_WWI_BOMBER", city = "Cartagena", n = 1, name = "SB Katiuska" } } },
	{ date = "1936-10-18", side = "REP", id = "REP_POPULAR_ARMY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Madrid", n = 3, name = "Mixed Brigade" } } },
	{ date = "1936-11-07", side = "REP", id = "REP_MADRID", gold = 500, units = { { type = "UNIT_GREAT_GENERAL", city = "Madrid", n = 1, name = "Junta de Defensa" }, { type = "UNIT_GREAT_WAR_INFANTRY", city = "Madrid", n = 2, name = "Fifth Regiment" }, { type = "UNIT_MACHINE_GUN", city = "Madrid", n = 1, name = "Machine-gun Company" } } },
	{ date = "1936-11-08", side = "REP", id = "REP_BRIGADES", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Madrid", "Albacete" }, n = 2, promos = IB, name = "International Brigade" } } },
	{ date = "1937-02-06", side = "REP", id = "REP_JARAMA", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Madrid", "Albacete" }, n = 2, promos = IB, name = "International Brigade" }, { type = "UNIT_WWI_TANK", city = "Madrid", n = 1, name = "T-26" }, { type = "UNIT_ARTILLERY", city = "Madrid", n = 1, name = "Field Battery" } } },
	{ date = "1937-03-08", side = "REP", id = "REP_GUADALAJARA", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Guadalajara", "Madrid" }, n = 1, promos = IB, name = "International Brigade" }, { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Guadalajara", "Madrid" }, n = 2, name = "11th Division (Lister)" }, { type = "UNIT_TRIPLANE", city = { "Guadalajara", "Madrid" }, n = 1, name = "I-15 Chato" } } },
	{ date = "1937-05-17", side = "REP", id = "REP_NEGRIN", gold = 800 },
	{ date = "1937-07-06", side = "REP", id = "REP_BRUNETE", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Madrid", n = 3, name = "Mixed Brigade" }, { type = "UNIT_WWI_TANK", city = "Madrid", n = 2, name = "T-26" }, { type = "UNIT_ARTILLERY", city = "Madrid", n = 1, name = "Field Battery" } } },
	{ date = "1937-08-10", side = "REP", id = "REP_ARAGON", gold = 300, also = { side = "CNT", gold = -300 } },
	{ date = "1937-08-24", side = "REP", id = "REP_BELCHITE", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Caspe", "Lerida" }, n = 3, name = "Army of the East" }, { type = "UNIT_WWI_TANK", city = { "Caspe", "Lerida" }, n = 1, name = "BT-5" } } },
	{ date = "1937-10-31", side = "REP", id = "REP_BARCELONA", gold = 500 },
	{ date = "1937-12-15", side = "REP", id = "REP_TERUEL", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Mora de Rubielos", "Castellon", "Valencia" }, n = 4, name = "Army of the Levante" }, { type = "UNIT_ARTILLERY", city = { "Mora de Rubielos", "Castellon", "Valencia" }, n = 2, name = "Field Battery" }, { type = "UNIT_WWI_TANK", city = { "Mora de Rubielos", "Valencia" }, n = 1, name = "T-26" } } },
	{ date = "1938-07-25", side = "REP", id = "REP_EBRO", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Gandesa", "Tortosa", "Tarragona", "Barcelona" }, n = 4, name = "Army of the Ebro" }, { type = "UNIT_ARTILLERY", city = { "Gandesa", "Tortosa", "Tarragona", "Barcelona" }, n = 2, name = "Field Battery" }, { type = "UNIT_MACHINE_GUN", city = { "Gandesa", "Tortosa", "Tarragona", "Barcelona" }, n = 1, name = "Machine-gun Company" } } },
	{ date = "1938-10-28", side = "REP", id = "REP_FAREWELL", remove = { names = { "International Brigade" }, n = 12 } },
	{ date = "1939-03-05", side = "REP", id = "REP_CASADO", gold = -500, also = { side = "BARB", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Madrid", n = 2, name = "Units loyal to Negrin" } } } },
	-- Catalonia
	{ date = "1936-08-07", side = "CAT", id = "CAT_INDUSTRY", gold = 500, units = { { type = "UNIT_ARTILLERY", city = "Barcelona", n = 1, name = "Field Battery" }, { type = "UNIT_MACHINE_GUN", city = "Barcelona", n = 1, name = "Machine-gun Company" } } },
	{ date = "1936-08-16", side = "CAT", id = "CAT_MALLORCA", units = { { type = "UNIT_RIFLEMAN", city = { "Mahon", "Barcelona" }, n = 2, name = "Bayo's Expedition" }, { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Mahon", "Barcelona" }, n = 1, name = "Bayo's Expedition" } } },
	{ date = "1937-05-03", side = "CAT", id = "CAT_MAYDAYS", war = { "CNT" }, also = { side = "REP", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = { "Barcelona", "Tarragona" }, n = 2, promos = GUARD, name = "Assault Guards" } } } },
	{ date = "1937-05-08", side = "CAT", id = "CAT_MAYDAYS_END", gold = -300, peace = { "CNT" }, also = { side = "REP", gold = 300 } },
	{ date = "1939-01-28", side = "CAT", id = "CAT_RETIRADA" },
	-- the Basque Country
	{ date = "1936-10-07", side = "EUZ", id = "EUZ_AGUIRRE", gold = 600, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Bilbao", n = 3, name = "Euzko Gudarostea" } } },
	{ date = "1937-04-26", side = "EUZ", id = "EUZ_GUERNICA" },
	{ date = "1937-05-21", side = "EUZ", id = "EUZ_HABANA" },
	{ date = "1937-08-24", side = "EUZ", id = "EUZ_SANTONA", onlyif = { city = "Bilbao", held = { "NAT", "NORTH" } }, remove = { names = { "Euzko Gudarostea", "Gudari Battalion" }, n = 4 } },
	-- the CNT-FAI
	{ date = "1936-10-06", side = "CNT", id = "CNT_COUNCIL", gold = 400, units = { { type = "UNIT_RIFLEMAN", city = "Caspe", n = 2, promos = COLUMN, name = "Confederal Column" } } },
	{ date = "1936-11-04", side = "CNT", id = "CNT_MINISTERS", gold = 300 },
	{ date = "1936-11-15", side = "CNT", id = "CNT_DURRUTI_MADRID", units = { { type = "UNIT_RIFLEMAN", city = { "Madrid", "Caspe" }, n = 3, promos = COLUMN, name = "Durruti Column" } } },
	{ date = "1936-11-20", side = "CNT", id = "CNT_DURRUTI" },
	-- fugitives and holdouts
	{ date = "1937-10-21", side = "BARB", id = "BARB_ASTURIAS", units = { { type = "UNIT_RIFLEMAN", city = { "Oviedo", "Gijon", "Leon" }, n = 3, name = "Fugitives (fuxidos)" } } },
}
local kRecurring = {
	{ start = "1936-08-15", stop = "1936-10-10", every = 2, side = "NAT", id = "NAT_AIRBRIDGE", units = { { type = "UNIT_RIFLEMAN", city = "Seville", n = 1, promos = REGULARES, name = "Regulares" } } },
	{ start = "1936-09-05", every = 6, side = "NAT", id = "NAT_MOROCCO", units = { { type = "UNIT_RIFLEMAN", city = { "Tetuan", "Ceuta", "Melilla" }, n = 1, promos = REGULARES, name = "Regulares" } } },
	{ start = "1937-01-02", every = 8, side = "NAT", id = "NAT_CREDIT", gold = 400 },
	{ start = "1936-10-03", every = 8, side = "REP", id = "REP_QUINTAS", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Madrid", n = 1, name = "Mixed Brigade" }, { type = "UNIT_GREAT_WAR_INFANTRY", city = "Valencia", n = 1, name = "Mixed Brigade" } } },
	{ start = "1936-10-10", every = 8, side = "NORTH", id = "NORTH_QUINTAS", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Burgos", n = 1, name = "Army of the North" } } },
	{ start = "1936-09-12", every = 10, side = "CAT", id = "CAT_LEVY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Barcelona", n = 1, name = "Catalan Army" } } },
}

----------------------------------------------------------------
local function FindPlayer(side)
	if side == "BARB" then return Players[GameDefines.MAX_CIV_PLAYERS] end
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
local function FindCityPlot(pPlayer, side, names)
	if type(names) ~= "table" then names = { names } end
	for _, name in ipairs(names) do
		local city, pOwner = FindCity(name)
		if city and (side == "BARB" or Friendly(pPlayer, pOwner)) then return city:Plot() end
	end
	local cap = pPlayer and pPlayer:GetCapitalCity()
	return cap and cap:Plot() or nil
end
local function Spawn(pPlayer, side, spec)
	local unitInfo = GameInfo.Units[spec.type]; local plot = FindCityPlot(pPlayer, side, spec.city)
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
	for unit in pPlayer:Units() do
		if left <= 0 then break end
		local nm = unit:GetNameNoDesc()
		for _, want in ipairs(spec.names) do
			if nm == want then table.insert(doomed, unit); left = left - 1; break end
		end
	end
	for _, unit in ipairs(doomed) do unit:Kill(true, -1) end
end
local function DeclareWar(a, b)
	if not (a and b) then return end
	local ta = Teams[a:GetTeam()]; local tb = b:GetTeam()
	if ta and not ta:IsAtWar(tb) then ta:DeclareWar(tb) end
end
local function MakePeace(a, b)
	if not (a and b) then return end
	local ta = Teams[a:GetTeam()]; local tb = b:GetTeam()
	if ta and ta:IsAtWar(tb) then ta:MakePeace(tb) end
end
local function Holds(cond)
	local city, pOwner = FindCity(cond.city)
	if not city then return false end
	for _, side in ipairs(cond.held) do
		if pOwner == FindPlayer(side) then return true end
	end
	return false
end
local function ApplyTo(side, ev)
	local pPlayer = FindPlayer(side)
	if not pPlayer then return end
	if ev.gold and side ~= "BARB" then pPlayer:ChangeGold(math.max(ev.gold, -pPlayer:GetGold())) end
	for _, spec in ipairs(ev.units or {}) do Spawn(pPlayer, side, spec) end
	if ev.remove then Remove(pPlayer, ev.remove) end
	for _, other in ipairs(ev.war or {}) do pcall(DeclareWar, pPlayer, FindPlayer(other)) end
	for _, other in ipairs(ev.peace or {}) do pcall(MakePeace, pPlayer, FindPlayer(other)) end
end
local function Apply(ev)
	local pSide = FindPlayer(ev.side)
	if ev.side ~= "BARB" and not pSide then return end   -- the side is gone: its events lapse
	if ev.onlyif and not Holds(ev.onlyif) then return end
	ApplyTo(ev.side, ev)
	if ev.also then ApplyTo(ev.also.side, ev.also) end
	if ev.quiet and pSide ~= Players[Game.GetActivePlayer()] then return end   -- recurring levies: only their own side is told
	local who = Locale.ConvertTextKey("TXT_KEY_ESP1936_SIDE_" .. ev.side)
	local title = Locale.ConvertTextKey("TXT_KEY_ESP1936_EVT_" .. ev.id .. "_TITLE")
	local text = Locale.ConvertTextKey("TXT_KEY_ESP1936_EVT_" .. ev.id .. "_TEXT")
	local header = string.format("[COLOR_YELLOW]%s[ENDCOLOR][NEWLINE]%s%s[NEWLINE][NEWLINE]", title, who, (ev.date and ev.date ~= "" and (", " .. ev.date) or ""))
	Events.SerialEventGameMessagePopup({ Type = ButtonPopupTypes.BUTTONPOPUP_TEXT, Data1 = 520, Text = header .. text })
end

----------------------------------------------------------------
local function Key(id, turn) return string.format("ESP1936_EVT_%s_%d", id, turn) end
local function AlreadyFired(key) local ok, v = pcall(function() return Modding.OpenSaveData().GetValue(key) end); return ok and v ~= nil end
local function MarkFired(key) pcall(function() Modding.OpenSaveData().SetValue(key, 1) end) end
local function ProcessTurn()
	local turn = Game.GetGameTurn()
	for i, ev in ipairs(kEvents) do
		if Turn(ev.date) == turn and not AlreadyFired(Key(i, turn)) then
			MarkFired(Key(i, turn)); local ok, err = pcall(Apply, ev)
			if not ok then print("Spain 1936 event failed: " .. tostring(err)) end
		end
	end
	for i, rec in ipairs(kRecurring) do
		local t0 = Turn(rec.start)
		if turn >= t0 and (not rec.stop or turn <= Turn(rec.stop)) and (turn - t0) % rec.every == 0 and not AlreadyFired(Key("R" .. i, turn)) then
			MarkFired(Key("R" .. i, turn)); local ok, err = pcall(Apply, { side = rec.side, id = rec.id, gold = rec.gold, units = rec.units, date = "", quiet = true })
			if not ok then print("Spain 1936 recurring event failed: " .. tostring(err)) end
		end
	end
end
Events.ActivePlayerTurnStart.Add(function() pcall(ProcessTurn) end)
