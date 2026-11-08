----------------------------------------------------------------
-- Russia 1918 turn-1 setup.
--  * production: every city gets a 1918-era unit in its queue, the side's own unique where it has one of that class
--  * unit names: the stock type stays, the unit carries its historical designation
--  * diplomacy: the three White governments are friends; everybody else dislikes the Reds
--  * stance: the human player's units start fortified
--  * calendar: one turn = one week from 1 June 1918, drawn over the top panel
----------------------------------------------------------------
local kQueues = {
	CIVILIZATION_RUSSIA   = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_RIFLEMAN", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_LANCER", "UNIT_GATLINGGUN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
	CIVILIZATION_GERMANY  = { "UNIT_LANCER", "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_LANCER", "UNIT_GREAT_WAR_INFANTRY", "UNIT_GATLINGGUN" },
	CIVILIZATION_SHOSHONE = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_RIFLEMAN", "UNIT_LANCER", "UNIT_ARTILLERY", "UNIT_RIFLEMAN", "UNIT_GATLINGGUN" },
	CIVILIZATION_ENGLAND  = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_RIFLEMAN", "UNIT_GATLINGGUN", "UNIT_GREAT_WAR_INFANTRY" },
	CIVILIZATION_ETHIOPIA = { "UNIT_RIFLEMAN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_LANCER", "UNIT_ARTILLERY", "UNIT_RIFLEMAN", "UNIT_GATLINGGUN" },
	CIVILIZATION_POLAND   = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_LANCER", "UNIT_RIFLEMAN", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_GATLINGGUN" },
}
local kFallback = { "UNIT_RIFLEMAN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_WORKER" }
local function CivOf(pPlayer)
	local civ = GameInfo.Civilizations[pPlayer:GetCivilizationType()]
	return civ and civ.Type or ""
end
local function FindPlayer(civType)
	for i = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
		local p = Players[i]
		if p and p:IsEverAlive() and CivOf(p) == civType then return p end
	end
	return nil
end

----------------------------------------------------------------
-- the queues name stock types; a side builds its own unique unit of the same class instead (text/uniques.py)
local function CivUnit(civType, unitType)
	local unit = GameInfo.Units[unitType]
	if not unit then return nil end
	for row in GameInfo.Civilization_UnitClassOverrides{ CivilizationType = civType, UnitClassType = unit.Class } do
		if row.UnitType then return GameInfo.Units[row.UnitType] end
		return nil
	end
	return unit
end
-- a unique unit is named like the stock unit of its class
local function BaseUnit(unit)
	local class = unit and GameInfo.UnitClasses[unit.Class]
	return class and GameInfo.Units[class.DefaultUnit] or unit
end
local function QueueFor(city, list, n)
	local civType = CivOf(Players[city:GetOwner()])
	for k = 0, #list - 1 do
		local unit = CivUnit(civType, list[(n + k) % #list + 1])
		if unit and city:CanTrain(unit.ID) then
			city:PushOrder(OrderTypes.ORDER_TRAIN, unit.ID, -1, false, false, false)
			return true
		end
	end
	return false
end
local function SetupProduction()
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
		local pPlayer = Players[iPlayer]
		if pPlayer and pPlayer:IsAlive() and not pPlayer:IsMinorCiv() then
			local list = kQueues[CivOf(pPlayer)] or kFallback
			local n = 0
			for city in pPlayer:Cities() do
				if city:GetOrderQueueLength() == 0 then
					if not QueueFor(city, list, n) then QueueFor(city, kFallback, n) end
					n = n + 1
				end
			end
		end
	end
	print("Russia 1918: initial production queued")
end

----------------------------------------------------------------
local kUnitNames = {
	CIVILIZATION_RUSSIA = { UNIT_GREAT_WAR_INFANTRY = "Red Army Rifle Division", UNIT_RIFLEMAN = "Red Guards", UNIT_CAVALRY = "Red Cavalry", UNIT_LANCER = "Red Cavalry", UNIT_ARTILLERY = "Armoured Train",
		UNIT_GATLINGGUN = "Maxim Company", UNIT_TRIPLANE = "Nieuport Squadron", UNIT_WWI_BOMBER = "Ilya Muromets", UNIT_WWI_TANK = "Captured Tank", UNIT_BATTLESHIP = "Baltic Fleet Dreadnought",
		UNIT_DESTROYER = "Novik-class Destroyer", UNIT_SUBMARINE = "Bars-class Submarine", UNIT_IRONCLAD = "Volga Flotilla Gunboat", UNIT_WORKER = "Labour Army", UNIT_CARAVAN = "Grain Train" },
	CIVILIZATION_GERMANY = { UNIT_GREAT_WAR_INFANTRY = "Volunteer Regiment", UNIT_RIFLEMAN = "Don Plastuns", UNIT_CAVALRY = "Don Cossack Regiment", UNIT_LANCER = "Kuban Cossack Regiment", UNIT_ARTILLERY = "Armoured Train",
		UNIT_GATLINGGUN = "Machine-gun Company", UNIT_WWI_TANK = "Mark V (British)", UNIT_TRIPLANE = "RAF 47 Squadron", UNIT_IRONCLAD = "Azov Flotilla Gunboat", UNIT_WORKER = "Labour Company", UNIT_CARAVAN = "Grain Train" },
	CIVILIZATION_SHOSHONE = { UNIT_GREAT_WAR_INFANTRY = "Siberian Army Regiment", UNIT_RIFLEMAN = "Siberian Rifles", UNIT_CAVALRY = "Orenburg Cossacks", UNIT_LANCER = "Siberian Cossacks", UNIT_ARTILLERY = "Armoured Train",
		UNIT_GATLINGGUN = "Machine-gun Company", UNIT_WWI_TANK = "Mark V (British)", UNIT_WORKER = "Labour Company", UNIT_CARAVAN = "Trans-Siberian Supply Train" },
	CIVILIZATION_ENGLAND = { UNIT_GREAT_WAR_INFANTRY = "Royal Scots", UNIT_RIFLEMAN = "Slavo-British Legion", UNIT_CAVALRY = "Northwestern Army Cavalry", UNIT_LANCER = "Northwestern Army Cavalry", UNIT_ARTILLERY = "Royal Artillery Battery",
		UNIT_GATLINGGUN = "Vickers Section", UNIT_WWI_TANK = "Mark V (Yudenich)", UNIT_DESTROYER = "Royal Navy Destroyer", UNIT_IRONCLAD = "River Monitor", UNIT_WORKER = "Labour Company", UNIT_CARAVAN = "Allied Supply Convoy" },
	CIVILIZATION_ETHIOPIA = { UNIT_GREAT_WAR_INFANTRY = "Serdiuk Division", UNIT_RIFLEMAN = "Haidamaks", UNIT_CAVALRY = "Zaporozhian Cavalry", UNIT_LANCER = "Zaporozhian Cavalry", UNIT_ARTILLERY = "Armoured Train",
		UNIT_GATLINGGUN = "Machine-gun Company", UNIT_IRONCLAD = "Black Sea Gunboat", UNIT_WORKER = "Labour Company", UNIT_CARAVAN = "Grain Train" },
	CIVILIZATION_POLAND = { UNIT_GREAT_WAR_INFANTRY = "Legion Infantry", UNIT_RIFLEMAN = "POW Militia", UNIT_CAVALRY = "Uhlan Regiment", UNIT_LANCER = "Uhlan Regiment", UNIT_ARTILLERY = "Field Artillery Battery",
		UNIT_GATLINGGUN = "Machine-gun Company", UNIT_TRIPLANE = "Kosciuszko Squadron", UNIT_WWI_TANK = "Renault FT", UNIT_WORKER = "Labour Company", UNIT_CARAVAN = "Supply Train" },
}
-- special cases picked by promotion: German garrisons in Ukraine (Cover I) and the Czechoslovak Legion in Siberia (Drill I + Shock I)
local function SpecialName(civType, unit, ut)
	if ut.Type ~= "UNIT_GREAT_WAR_INFANTRY" then return nil end
	local cover = GameInfo.UnitPromotions["PROMOTION_COVER_1"]; local shock = GameInfo.UnitPromotions["PROMOTION_SHOCK_1"]; local drill = GameInfo.UnitPromotions["PROMOTION_DRILL_1"]
	if civType == "CIVILIZATION_ETHIOPIA" and cover and unit:IsHasPromotion(cover.ID) then return "German garrison" end
	if civType == "CIVILIZATION_SHOSHONE" and shock and drill and unit:IsHasPromotion(shock.ID) and unit:IsHasPromotion(drill.ID) then return "Czechoslovak Legion" end
	if civType == "CIVILIZATION_GERMANY" and shock and drill and unit:IsHasPromotion(shock.ID) and unit:IsHasPromotion(drill.ID) then return "Kornilov Shock Regiment" end
	return nil
end
local function NameUnit(pPlayer, unit)
	if not unit or unit:IsDead() or unit:HasName() then return end
	local civ = GameInfo.Civilizations[pPlayer:GetCivilizationType()]
	local map = civ and kUnitNames[civ.Type]
	if not map then return end
	local own = GameInfo.Units[unit:GetUnitType()]
	local ut = BaseUnit(own)
	if not ut then return end
	-- the special names go to stock units only: a Serdiuk Division has Cover I but is no German garrison (the armistice event removes those by name)
	local name = (own.Type == ut.Type and SpecialName(civ.Type, unit, ut)) or map[ut.Type]
	if name then unit:SetName(name) end
end
local function NameAllUnits()
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
		local pPlayer = Players[iPlayer]
		if pPlayer and pPlayer:IsAlive() then
			for unit in pPlayer:Units() do pcall(NameUnit, pPlayer, unit) end
		end
	end
end
Events.SerialEventUnitCreated.Add(function(playerID, unitID)
	local pPlayer = Players[playerID]
	if pPlayer then pcall(NameUnit, pPlayer, pPlayer:GetUnitByID(unitID)) end
end)

----------------------------------------------------------------
local function Friends(a, b)
	if a and b and not a:IsDoF(b:GetID()) then a:DoForceDoF(b:GetID()) end
end
local function Hostile(a, b)
	if a and b then
		if not a:IsDenouncedPlayer(b:GetID()) then a:DoForceDenounce(b:GetID()) end
		if not b:IsDenouncedPlayer(a:GetID()) then b:DoForceDenounce(a:GetID()) end
	end
end
local function SetupStance()
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
		local pPlayer = Players[iPlayer]
		if pPlayer and pPlayer:IsAlive() and pPlayer:IsHuman() then
			for unit in pPlayer:Units() do
				if not unit:IsTrade() then
					local plot = unit:GetPlot()
					if unit:GetDomainType() == DomainTypes.DOMAIN_AIR and unit:CanAirPatrol(plot) then
						unit:PushMission(MissionTypes.MISSION_AIRPATROL)
					elseif unit:IsCombatUnit() and unit:CanFortify(plot) then
						unit:PushMission(MissionTypes.MISSION_FORTIFY)
					else
						unit:PushMission(MissionTypes.MISSION_SLEEP)
					end
				end
			end
		end
	end
	print("Russia 1918: units set to defensive stance")
end
local function SetupDiplomacy()
	local red = FindPlayer("CIVILIZATION_RUSSIA"); local south = FindPlayer("CIVILIZATION_GERMANY"); local sib = FindPlayer("CIVILIZATION_SHOSHONE")
	local north = FindPlayer("CIVILIZATION_ENGLAND"); local ukr = FindPlayer("CIVILIZATION_ETHIOPIA"); local pol = FindPlayer("CIVILIZATION_POLAND")
	Friends(south, sib); Friends(south, north); Friends(sib, north)
	Hostile(red, ukr); Hostile(red, pol)
	print("Russia 1918: diplomacy applied")
end

----------------------------------------------------------------
local kMonthNames = { "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" }
local function DaysInMonth(y, m)
	if m == 2 then
		if (y % 4 == 0 and y % 100 ~= 0) or y % 400 == 0 then return 29 else return 28 end
	end
	if m == 4 or m == 6 or m == 9 or m == 11 then return 30 end
	return 31
end
local function DateForTurn(turn)
	local y, m, d = 1918, 6, 1
	local n = turn * 7
	while n > 0 do
		local left = DaysInMonth(y, m) - d
		if n <= left then d = d + n; n = 0
		else n = n - left - 1; d = 1; m = m + 1; if m > 12 then m = 1; y = y + 1 end end
	end
	return string.format("%d %s %d", d, kMonthNames[m], y)
end
local function ApplyCalendar(force)
	local turn = Game.GetGameTurn()
	local dateLabel = ContextPtr:LookUpControl("/InGame/TopPanel/CurrentDate")
	local turnLabel = ContextPtr:LookUpControl("/InGame/TopPanel/CurrentTurn")
	local dateText = DateForTurn(turn)
	local weekText = Locale.ConvertTextKey("TXT_KEY_RUS1918_WEEK", turn + 1)
	if dateLabel and (force or dateLabel:GetText() ~= dateText) then dateLabel:SetText(dateText); dateLabel:SetToolTipString(Locale.ConvertTextKey("TXT_KEY_RUS1918_WEEK_TT", turn + 1)) end
	if turnLabel and (force or turnLabel:GetText() ~= weekText) then turnLabel:SetText(weekText) end
end
Events.ActivePlayerTurnStart.Add(function() pcall(ApplyCalendar, true) end)
Events.SerialEventGameDataDirty.Add(function() pcall(ApplyCalendar, false) end)

----------------------------------------------------------------
local function SetupDone()
	local ok, v = pcall(function() return Modding.OpenSaveData().GetValue("RUS1918_SETUP_DONE") end)
	return ok and v ~= nil
end
local function MarkSetupDone() pcall(function() Modding.OpenSaveData().SetValue("RUS1918_SETUP_DONE", 1) end) end
local function RunSetup()
	print("Russia 1918: running turn-1 setup")
	for name, fn in pairs({ production = SetupProduction, names = NameAllUnits, diplomacy = SetupDiplomacy, stance = SetupStance }) do
		local ok, err = pcall(fn)
		if not ok then print("Russia 1918 " .. name .. " setup failed: " .. tostring(err)) end
	end
	MarkSetupDone()
end
local g_elapsed = 0
local g_setupPending = true
local g_calTick = 0
ContextPtr:SetUpdate(function(dt)
	g_calTick = g_calTick + (dt or 0)
	if g_calTick > 0.5 then g_calTick = 0; pcall(ApplyCalendar, false) end
	if not g_setupPending then return end
	g_elapsed = g_elapsed + (dt or 0)
	if g_elapsed < 2.0 then return end
	g_setupPending = false
	if Game.GetElapsedGameTurns() > 0 or SetupDone() then return end
	RunSetup()
end)
