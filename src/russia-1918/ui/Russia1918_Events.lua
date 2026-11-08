----------------------------------------------------------------
-- Russia 1918: dated events. One turn = one week from 1 June 1918.
-- Sides: RED (Russia), SOUTH (Germany donor), SIB (Shoshone), NORTH (England), UKR (Ethiopia), POL (Poland), BARB (barbarians).
-- An event can give gold, spawn units in a named city (own city, or any city with "anycity"), remove units by name,
-- declare war ("war") or force a friendship ("friends"), and always shows a popup.
----------------------------------------------------------------
local kSideCiv = { RED = "CIVILIZATION_RUSSIA", SOUTH = "CIVILIZATION_GERMANY", SIB = "CIVILIZATION_SHOSHONE", NORTH = "CIVILIZATION_ENGLAND", UKR = "CIVILIZATION_ETHIOPIA", POL = "CIVILIZATION_POLAND" }
local DAYS_PER_TURN = 7

local function DaysFromCivil(y, m, d)
	if m <= 2 then y = y - 1 end
	local era = math.floor(y / 400); local yoe = y - era * 400; local mp = (m + 9) % 12
	local doy = math.floor((153 * mp + 2) / 5) + d - 1
	local doe = yoe * 365 + math.floor(yoe / 4) - math.floor(yoe / 100) + doy
	return era * 146097 + doe - 719468
end
local kStart = DaysFromCivil(1918, 6, 1)
local function Turn(date)
	local y, m, d = date:match("(%d+)-(%d+)-(%d+)")
	return math.floor((DaysFromCivil(tonumber(y), tonumber(m), tonumber(d)) - kStart) / DAYS_PER_TURN)
end

local VET = { "PROMOTION_DRILL_1", "PROMOTION_SHOCK_1" }
local kEvents = {
	-- RSFSR
	{ date = "1918-06-12", side = "RED", id = "RED_VSEVOBUCH", gold = 500, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Moscow", n = 3, name = "Red Army Rifle Division", xp = 5 } } },
	{ date = "1918-07-10", side = "RED", id = "RED_LATVIANS", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Moscow", n = 2, promos = { "PROMOTION_DRILL_1" }, name = "Latvian Riflemen", xp = 25 } } },
	{ date = "1918-08-10", side = "RED", id = "RED_SVIYAZHSK", units = { { type = "UNIT_GREAT_GENERAL", city = "Kazan", n = 1, name = "Trotsky's Train" }, { type = "UNIT_ARTILLERY", city = "Kazan", n = 1, name = "Armoured Train", xp = 10 } } },
	{ date = "1918-11-13", side = "RED", id = "RED_BREST", gold = 1000 },
	{ date = "1918-12-24", side = "RED", id = "RED_UKRWAR", war = { "UKR" } },
	{ date = "1919-11-17", side = "RED", id = "RED_KONARMIYA", units = { { type = "UNIT_CAVALRY", city = "Voronezh", n = 4, promos = { "PROMOTION_SHOCK_1", "PROMOTION_MOBILITY" }, name = "First Cavalry Army", xp = 20 } } },
	{ date = "1921-03-21", side = "RED", id = "RED_NEP", gold = 1500 },
	-- White South
	{ date = "1918-06-23", side = "SOUTH", id = "SOUTH_KUBAN", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Novocherkassk", n = 2, promos = VET, name = "Volunteer Regiment", xp = 25 }, { type = "UNIT_CAVALRY", city = "Novocherkassk", n = 2, name = "Don Cossack Regiment", xp = 15 } } },
	{ date = "1918-12-26", side = "SOUTH", id = "SOUTH_AFSR", gold = 1000, units = { { type = "UNIT_GREAT_GENERAL", city = "Novocherkassk", n = 1, name = "Wrangel" } } },
	{ date = "1919-03-25", side = "SOUTH", id = "SOUTH_BRITISH", gold = 1500, units = { { type = "UNIT_WWI_TANK", city = "Ekaterinodar", n = 2, name = "Mark V (British)", xp = 10 }, { type = "UNIT_TRIPLANE", city = "Ekaterinodar", n = 2, name = "RAF 47 Squadron", xp = 10 } } },
	{ date = "1919-07-03", side = "SOUTH", id = "SOUTH_MOSCOW_DIRECTIVE", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Kharkov", n = 3, name = "Volunteer Regiment", xp = 15 }, { type = "UNIT_CAVALRY", city = "Kharkov", n = 2, name = "Kuban Cossack Regiment", xp = 15 } } },
	{ date = "1919-08-10", side = "SOUTH", id = "SOUTH_MAMONTOV", units = { { type = "UNIT_CAVALRY", city = "Novocherkassk", n = 3, promos = { "PROMOTION_MOBILITY" }, name = "Mamontov's Corps", xp = 20 } } },
	{ date = "1920-04-04", side = "SOUTH", id = "SOUTH_WRANGEL", gold = 800, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Sevastopol", n = 2, name = "Russian Army (Wrangel)", xp = 20 } } },
	-- Siberia
	{ date = "1918-06-08", side = "SIB", id = "SIB_KOMUCH", gold = 500, units = { { type = "UNIT_RIFLEMAN", city = "Samara", n = 3, name = "People's Army", xp = 5 } } },
	{ date = "1918-11-18", side = "SIB", id = "SIB_KOLCHAK", gold = 1500, units = { { type = "UNIT_GREAT_GENERAL", city = "Omsk", n = 1, name = "Supreme Ruler's Staff" } } },
	{ date = "1919-01-15", side = "SIB", id = "SIB_ENTENTE", gold = 2000, units = { { type = "UNIT_ARTILLERY", city = "Omsk", n = 2, name = "British-equipped Battery", xp = 10 }, { type = "UNIT_GATLINGGUN", city = "Omsk", n = 2, name = "Machine-gun Company", xp = 10 } } },
	{ date = "1919-03-04", side = "SIB", id = "SIB_SPRING", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Ufa", n = 3, name = "Western Army Regiment", xp = 10 }, { type = "UNIT_CAVALRY", city = "Ufa", n = 2, name = "Orenburg Cossacks", xp = 10 } } },
	{ date = "1919-06-01", side = "SIB", id = "SIB_ENTENTE2", gold = 1500 },
	-- Northern Region / Northwestern Army
	{ date = "1918-08-02", side = "NORTH", id = "NORTH_ARKHANGELSK", gold = 1000, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Arkhangelsk", n = 3, name = "Royal Scots", xp = 20 }, { type = "UNIT_ARTILLERY", city = "Arkhangelsk", n = 1, name = "Royal Artillery Battery", xp = 10 }, { type = "UNIT_DESTROYER", city = "Arkhangelsk", n = 1, name = "Royal Navy Destroyer", xp = 10 } } },
	{ date = "1918-09-04", side = "NORTH", id = "NORTH_US", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Arkhangelsk", n = 2, name = "US 339th Infantry", xp = 10 } } },
	{ date = "1919-05-13", side = "NORTH", id = "NORTH_NWCORPS", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Reval", anycity = true, n = 3, name = "Northern Corps", xp = 15 }, { type = "UNIT_CAVALRY", city = "Reval", anycity = true, n = 1, name = "Northwestern Army Cavalry", xp = 10 }, { type = "UNIT_GREAT_GENERAL", city = "Reval", anycity = true, n = 1, name = "Yudenich's Staff" } } },
	{ date = "1919-09-27", side = "NORTH", id = "NORTH_EVACUATION", gold = -500, remove = { names = { "Royal Scots", "US 339th Infantry" }, n = 5 } },
	{ date = "1919-10-10", side = "NORTH", id = "NORTH_PETROGRAD", gold = 800, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Reval", anycity = true, n = 3, name = "Northwestern Army", xp = 15 }, { type = "UNIT_WWI_TANK", city = "Reval", anycity = true, n = 1, name = "Mark V (Yudenich)", xp = 10 } } },
	-- Ukraine
	{ date = "1918-11-11", side = "UKR", id = "UKR_ARMISTICE", gold = -500, remove = { names = { "German garrison" }, n = 8 }, units = { { type = "UNIT_RIFLEMAN", city = "Vinnitsa", n = 3, name = "Directory Insurgents", xp = 5 } } },
	{ date = "1918-12-14", side = "UKR", id = "UKR_DIRECTORY", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Kiev", n = 2, name = "Sich Riflemen", xp = 15 } } },
	{ date = "1919-01-22", side = "UKR", id = "UKR_ZLUKA", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Tarnopol", n = 2, promos = { "PROMOTION_DRILL_1" }, name = "Galician Army", xp = 20 } } },
	{ date = "1920-04-21", side = "UKR", id = "UKR_WARSAW", gold = 500, friends = { "POL" } },
	-- Poland
	{ date = "1918-11-11", side = "POL", id = "POL_INDEPENDENCE", gold = 1500, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Warsaw", n = 3, name = "Polish Army Regiment", xp = 10 } } },
	{ date = "1919-02-14", side = "POL", id = "POL_WAR", war = { "RED" } },
	{ date = "1919-04-15", side = "POL", id = "POL_HALLER", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Warsaw", n = 4, promos = { "PROMOTION_DRILL_1" }, name = "Blue Army", xp = 25 }, { type = "UNIT_ARTILLERY", city = "Warsaw", n = 2, name = "Field Artillery Battery", xp = 15 }, { type = "UNIT_TRIPLANE", city = "Warsaw", n = 1, name = "Kosciuszko Squadron", xp = 10 } } },
	{ date = "1919-12-01", side = "POL", id = "POL_GREATER_POLAND", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Lodz", n = 2, name = "Greater Poland Army", xp = 15 } } },
	{ date = "1920-04-25", side = "POL", id = "POL_KIEV", gold = 800, units = { { type = "UNIT_CAVALRY", city = "Lwow", n = 2, name = "Uhlan Regiment", xp = 15 }, { type = "UNIT_GREAT_WAR_INFANTRY", city = "Lwow", n = 2, name = "Polish Army Regiment", xp = 15 } } },
	{ date = "1920-08-01", side = "POL", id = "POL_VOLUNTEERS", gold = 1000, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Warsaw", n = 3, name = "Volunteer Army", xp = 10 }, { type = "UNIT_CAVALRY", city = "Warsaw", n = 2, name = "Uhlan Regiment", xp = 10 } } },
	-- barbarians: Grigoriev's mutiny, the Tambov rising
	{ date = "1919-05-10", side = "BARB", id = "BARB_GRIGORIEV", units = { { type = "UNIT_RIFLEMAN", city = "Elisavetgrad", anycity = true, n = 2, promos = { "PROMOTION_SHOCK_1" }, name = "Grigoriev's Men", xp = 15 }, { type = "UNIT_CAVALRY", city = "Elisavetgrad", anycity = true, n = 2, promos = { "PROMOTION_MOBILITY" }, name = "Grigoriev's Cavalry", xp = 15 } } },
	{ date = "1920-08-19", side = "BARB", id = "BARB_TAMBOV", units = { { type = "UNIT_RIFLEMAN", city = "Tambov", anycity = true, n = 3, promos = { "PROMOTION_SHOCK_1" }, name = "Antonov's Partisans", xp = 15 }, { type = "UNIT_CAVALRY", city = "Tambov", anycity = true, n = 1, name = "Antonov's Partisans", xp = 10 } } },
}
local kRecurring = {
	{ start = "1918-09-01", every = 8, side = "RED", id = "RED_MOBILIZATION", units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Moscow", n = 2, name = "Red Army Rifle Division", xp = 5 }, { type = "UNIT_RIFLEMAN", city = "Petrograd", n = 1, name = "Red Guards", xp = 5 } } },
	{ start = "1918-10-01", every = 10, side = "SIB", id = "SIB_VLADIVOSTOK", gold = 400, units = { { type = "UNIT_GREAT_WAR_INFANTRY", city = "Omsk", n = 1, name = "Siberian Army Regiment", xp = 10 } } },
	{ start = "1919-01-01", every = 10, side = "SOUTH", id = "SOUTH_ENTENTE", gold = 600 },
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
local function FindCityPlot(pPlayer, side, name, anycity)
	for i = 0, GameDefines.MAX_CIV_PLAYERS do
		local p = Players[i]
		if p and p:IsAlive() then
			for city in p:Cities() do
				if city:GetName() == name and (side == "BARB" or anycity or p == pPlayer) then return city:Plot() end
			end
		end
	end
	local cap = pPlayer and pPlayer:GetCapitalCity()
	return cap and cap:Plot() or nil
end
local function Spawn(pPlayer, side, spec)
	local unitInfo = GameInfo.Units[spec.type]; local plot = FindCityPlot(pPlayer, side, spec.city, spec.anycity)
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
	local left = spec.n or 1
	for unit in pPlayer:Units() do
		if left <= 0 then break end
		local nm = unit:GetNameNoDesc()
		for _, want in ipairs(spec.names) do
			if nm == want then unit:Kill(true, -1); left = left - 1; break end
		end
	end
end
local function DeclareWar(a, b)
	if not (a and b) then return end
	local ta = Teams[a:GetTeam()]; local tb = b:GetTeam()
	if ta and not ta:IsAtWar(tb) then ta:DeclareWar(tb) end
end
local function MakeFriends(a, b)
	if a and b and not a:IsDoF(b:GetID()) then a:DoForceDoF(b:GetID()) end
end
local function ApplyTo(side, ev)
	local pPlayer = FindPlayer(side)
	if not pPlayer then return end
	if ev.gold then pPlayer:ChangeGold(ev.gold) end
	for _, spec in ipairs(ev.units or {}) do Spawn(pPlayer, side, spec) end
	if ev.remove then Remove(pPlayer, ev.remove) end
	for _, other in ipairs(ev.war or {}) do pcall(DeclareWar, pPlayer, FindPlayer(other)) end
	for _, other in ipairs(ev.friends or {}) do pcall(MakeFriends, pPlayer, FindPlayer(other)) end
end
local function Apply(ev)
	ApplyTo(ev.side, ev)
	if ev.also then ApplyTo(ev.also.side, ev.also) end
	local who = Locale.ConvertTextKey("TXT_KEY_RUS1918_SIDE_" .. ev.side)
	local title = Locale.ConvertTextKey("TXT_KEY_RUS1918_EVT_" .. ev.id .. "_TITLE")
	local text = Locale.ConvertTextKey("TXT_KEY_RUS1918_EVT_" .. ev.id .. "_TEXT")
	local header = string.format("[COLOR_YELLOW]%s[ENDCOLOR][NEWLINE]%s%s[NEWLINE][NEWLINE]", title, who, (ev.date and ev.date ~= "" and (", " .. ev.date) or ""))
	Events.SerialEventGameMessagePopup({ Type = ButtonPopupTypes.BUTTONPOPUP_TEXT, Data1 = 520, Text = header .. text })
end

----------------------------------------------------------------
local function Key(id, turn) return string.format("RUS1918_EVT_%s_%d", id, turn) end
local function AlreadyFired(key) local ok, v = pcall(function() return Modding.OpenSaveData().GetValue(key) end); return ok and v ~= nil end
local function MarkFired(key) pcall(function() Modding.OpenSaveData().SetValue(key, 1) end) end
local function ProcessTurn()
	local turn = Game.GetGameTurn()
	for i, ev in ipairs(kEvents) do
		if Turn(ev.date) == turn and not AlreadyFired(Key(i, turn)) then
			MarkFired(Key(i, turn)); local ok, err = pcall(Apply, ev)
			if not ok then print("Russia 1918 event failed: " .. tostring(err)) end
		end
	end
	for i, rec in ipairs(kRecurring) do
		local t0 = Turn(rec.start)
		if turn >= t0 and (turn - t0) % rec.every == 0 and not AlreadyFired(Key("R" .. i, turn)) then
			MarkFired(Key("R" .. i, turn)); local ok, err = pcall(Apply, { side = rec.side, id = rec.id, gold = rec.gold, units = rec.units, date = "" })
			if not ok then print("Russia 1918 recurring event failed: " .. tostring(err)) end
		end
	end
end
Events.ActivePlayerTurnStart.Add(function() pcall(ProcessTurn) end)
