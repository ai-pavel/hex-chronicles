----------------------------------------------------------------
-- China 1928 turn-1 setup.
--  * buildings: the stock buildings the map places become each side's own of the same class
--  * production: every city gets a unit of 1928 in its queue (each side its own unique of the class)
--  * unit names: the stock type stays, the unit carries its historical designation
--  * unit names: barbarians are bandits and rebels
--  * stance: the human player's units start fortified
--  * calendar: one turn = one week from 10 October 1928, drawn over the top panel
----------------------------------------------------------------
local kQueues = {
	CIVILIZATION_CHINA    = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_MACHINE_GUN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
	CIVILIZATION_ZULU     = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_LANCER", "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
	CIVILIZATION_RUSSIA   = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_MACHINE_GUN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
	CIVILIZATION_GERMANY  = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WWI_BOMBER", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
	CIVILIZATION_ETHIOPIA = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_MACHINE_GUN", "UNIT_WORKER" },
	CIVILIZATION_SHOSHONE = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
}
local kFallback = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_MACHINE_GUN", "UNIT_WORKER" }
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
	print("China 1928: initial production queued")
end

----------------------------------------------------------------
local kUnitNames = {
	CIVILIZATION_CHINA = { UNIT_GREAT_WAR_INFANTRY = "Central Army", UNIT_RIFLEMAN = "Provincial Division", UNIT_CAVALRY = "Cavalry Brigade", UNIT_LANCER = "Cavalry Brigade",
		UNIT_ARTILLERY = "Field Battery", UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_TRIPLANE = "Nanjing Air Squadron", UNIT_WWI_BOMBER = "Nanjing Air Squadron",
		UNIT_WWI_TANK = "Armoured Car Company", UNIT_IRONCLAD = "River Gunboat", UNIT_DESTROYER = "Cruiser Squadron", UNIT_WORKER = "Labour Corps", UNIT_CARAVAN = "Supply Column", UNIT_CARGO_SHIP = "Coastal Steamer" },
	CIVILIZATION_ZULU = { UNIT_GREAT_WAR_INFANTRY = "Guominjun", UNIT_RIFLEMAN = "Provincial Division", UNIT_CAVALRY = "Northwest Cavalry", UNIT_LANCER = "Northwest Cavalry",
		UNIT_ARTILLERY = "Field Battery", UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_TRIPLANE = "Guominjun Air Squadron", UNIT_WWI_BOMBER = "Guominjun Air Squadron",
		UNIT_WWI_TANK = "Armoured Car Company", UNIT_WORKER = "Road Builders", UNIT_CARAVAN = "Camel Train", UNIT_CARGO_SHIP = "Coastal Steamer" },
	CIVILIZATION_RUSSIA = { UNIT_GREAT_WAR_INFANTRY = "Shanxi Army", UNIT_RIFLEMAN = "Provincial Militia", UNIT_RUSSIAN_COSSACK = "Shanxi Cavalry", UNIT_CAVALRY = "Shanxi Cavalry", UNIT_LANCER = "Shanxi Cavalry",
		UNIT_ARTILLERY = "Taiyuan Mountain Battery", UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_TRIPLANE = "Shanxi Air Squadron", UNIT_WWI_BOMBER = "Shanxi Air Squadron",
		UNIT_WWI_TANK = "Armoured Car Company", UNIT_WORKER = "Railway Workers", UNIT_CARAVAN = "Supply Column", UNIT_CARGO_SHIP = "Coastal Steamer" },
	CIVILIZATION_GERMANY = { UNIT_GREAT_WAR_INFANTRY = "Northeast Army", UNIT_RIFLEMAN = "Provincial Division", UNIT_CAVALRY = "Northeast Cavalry", UNIT_LANCER = "Northeast Cavalry",
		UNIT_ARTILLERY = "Field Battery", UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_TRIPLANE = "Northeast Air Corps", UNIT_WWI_BOMBER = "Northeast Air Corps",
		UNIT_WWI_TANK = "Renault FT Company", UNIT_IRONCLAD = "Northeast Navy Gunboat", UNIT_DESTROYER = "Northeast Navy Cruiser", UNIT_WORKER = "Railway Workers", UNIT_CARAVAN = "Supply Column", UNIT_CARGO_SHIP = "Coastal Steamer" },
	CIVILIZATION_ETHIOPIA = { UNIT_GREAT_WAR_INFANTRY = "Fourth Group Army", UNIT_RIFLEMAN = "Guangxi Militia", UNIT_ETHIOPIAN_MEHAL_SEFARI = "Guangxi Militia", UNIT_CAVALRY = "Cavalry Squadron", UNIT_LANCER = "Cavalry Squadron",
		UNIT_ARTILLERY = "Field Battery", UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_TRIPLANE = "Guangxi Air Squadron", UNIT_WWI_BOMBER = "Guangxi Air Squadron",
		UNIT_WWI_TANK = "Armoured Car Company", UNIT_IRONCLAD = "River Gunboat", UNIT_WORKER = "Labour Corps", UNIT_CARAVAN = "Supply Column", UNIT_CARGO_SHIP = "Coastal Steamer" },
	CIVILIZATION_SHOSHONE = { UNIT_GREAT_WAR_INFANTRY = "Red Army", UNIT_RIFLEMAN = "Red Guards", UNIT_SHOSHONE_COMANCHE_RIDERS = "Red Cavalry", UNIT_CAVALRY = "Red Cavalry", UNIT_LANCER = "Red Cavalry",
		UNIT_ARTILLERY = "Captured Battery", UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_WORKER = "Peasant Volunteers", UNIT_CARAVAN = "Porters" },
	CIVILIZATION_BARBARIAN = { UNIT_GREAT_WAR_INFANTRY = "Rebel Army", UNIT_RIFLEMAN = "Bandits", UNIT_CAVALRY = "Mounted Bandits", UNIT_LANCER = "Mounted Bandits", UNIT_MACHINE_GUN = "Rebel Army" },
}
-- special cases picked by promotion: Nanjing's Whampoa divisions (Drill I + Shock I), Feng's Northwest Army (Drill I + March), Yan's garrisons (Cover I),
-- the Guangxi divisions (Drill I + Drill II), the Red Army (Drill I + March); stock units only, a unique keeps the name of its class
local function Has(unit, promo) local p = GameInfo.UnitPromotions[promo]; return p and unit:IsHasPromotion(p.ID) end
local function SpecialName(civType, unit, ut)
	if GameInfo.Units[unit:GetUnitType()].Type ~= ut.Type then return nil end
	local drill, shock, cover, march = Has(unit, "PROMOTION_DRILL_1"), Has(unit, "PROMOTION_SHOCK_1"), Has(unit, "PROMOTION_COVER_1"), Has(unit, "PROMOTION_MARCH")
	if civType == "CIVILIZATION_CHINA" then
		if ut.Type == "UNIT_GREAT_WAR_INFANTRY" and drill and shock then return "Central Army (Whampoa)" end
	elseif civType == "CIVILIZATION_ZULU" then
		if ut.Type == "UNIT_GREAT_WAR_INFANTRY" and drill and march then return "Northwest Army" end
	elseif civType == "CIVILIZATION_RUSSIA" then
		if ut.Type == "UNIT_GREAT_WAR_INFANTRY" and cover then return "Shanxi Garrison" end
	elseif civType == "CIVILIZATION_ETHIOPIA" then
		if ut.Type == "UNIT_GREAT_WAR_INFANTRY" and drill and Has(unit, "PROMOTION_DRILL_2") then return "Seventh Army" end
	elseif civType == "CIVILIZATION_SHOSHONE" then
		if ut.Type == "UNIT_RIFLEMAN" and drill and march then return "Red Army Guerrillas" end
	end
	return nil
end
local function NameUnit(pPlayer, unit)
	if not unit or unit:IsDead() or unit:HasName() then return end
	local civ = GameInfo.Civilizations[pPlayer:GetCivilizationType()]
	local map = civ and kUnitNames[civ.Type]
	if not map then return end
	local ut = BaseUnit(GameInfo.Units[unit:GetUnitType()])
	if not ut then return end
	local name = SpecialName(civ.Type, unit, ut) or map[ut.Type]
	if name then unit:SetName(name) end
end
local function NameAllUnits()
	for _, iPlayer in ipairs((function() local t = {}; for i = 0, GameDefines.MAX_MAJOR_CIVS - 1 do table.insert(t, i) end; table.insert(t, GameDefines.MAX_CIV_PLAYERS); return t end)()) do
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
	print("China 1928: units set to defensive stance")
end
local function SetupDiplomacy()
	-- October 1928: the five armies are nominally one National Revolutionary Army, at peace with open borders; nobody is anybody's friend
	print("China 1928: diplomacy as in the map")
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
	local y, m, d = 1928, 10, 10
	local n = turn * 7
	while n > 0 do
		local left = DaysInMonth(y, m) - d
		if n <= left then d = d + n; n = 0
		else n = n - left - 1; d = 1; m = m + 1; if m > 12 then m = 1; y = y + 1 end end
	end
	return string.format("%d %s %d", d, Locale.ConvertTextKey("TXT_KEY_CHN1928_MONTH_" .. m), y)
end
local function ApplyCalendar(force)
	local turn = Game.GetGameTurn()
	local dateLabel = ContextPtr:LookUpControl("/InGame/TopPanel/CurrentDate")
	local turnLabel = ContextPtr:LookUpControl("/InGame/TopPanel/CurrentTurn")
	local dateText = DateForTurn(turn)
	local weekText = Locale.ConvertTextKey("TXT_KEY_CHN1928_WEEK", turn + 1)
	if dateLabel and (force or dateLabel:GetText() ~= dateText) then dateLabel:SetText(dateText); dateLabel:SetToolTipString(Locale.ConvertTextKey("TXT_KEY_CHN1928_WEEK_TT", turn + 1)) end
	if turnLabel and (force or turnLabel:GetText() ~= weekText) then turnLabel:SetText(weekText) end
end
Events.ActivePlayerTurnStart.Add(function() pcall(ApplyCalendar, true) end)
Events.SerialEventGameDataDirty.Add(function() pcall(ApplyCalendar, false) end)

----------------------------------------------------------------
-- The map places stock Barracks, Armories, Military Academies, Workshops, Factories and Castles, classes the sides now replace
-- with their own (text/uniques.py). Swap each for the owner's building of the class, as the game does when a city changes hands,
-- so that no city can add its side's unique on top of the stock building.
local function CivBuilding(civType, class)
	for row in GameInfo.Civilization_BuildingClassOverrides{ CivilizationType = civType, BuildingClassType = class } do
		if row.BuildingType then return GameInfo.Buildings[row.BuildingType] end
		return nil
	end
	local bc = GameInfo.BuildingClasses[class]
	return bc and GameInfo.Buildings[bc.DefaultBuilding]
end
local function SetupBuildings()
	local n = 0
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
		local pPlayer = Players[iPlayer]
		if pPlayer and pPlayer:IsAlive() and not pPlayer:IsMinorCiv() then
			local civType = CivOf(pPlayer)
			for city in pPlayer:Cities() do
				for b in GameInfo.Buildings() do
					if city:GetNumRealBuilding(b.ID) > 0 then
						local want = CivBuilding(civType, b.BuildingClass)
						if want and want.ID ~= b.ID then
							city:SetNumRealBuilding(b.ID, 0)
							city:SetNumRealBuilding(want.ID, 1)
							n = n + 1
						end
					end
				end
			end
		end
	end
	print("China 1928: " .. n .. " buildings swapped for their owners' own")
end

----------------------------------------------------------------
local function SetupDone()
	local ok, v = pcall(function() return Modding.OpenSaveData().GetValue("CHN1928_SETUP_DONE") end)
	return ok and v ~= nil
end
local function MarkSetupDone() pcall(function() Modding.OpenSaveData().SetValue("CHN1928_SETUP_DONE", 1) end) end
local function RunSetup()
	print("China 1928: running turn-1 setup")
	for _, step in ipairs({ { "buildings", SetupBuildings }, { "production", SetupProduction }, { "names", NameAllUnits }, { "diplomacy", SetupDiplomacy }, { "stance", SetupStance } }) do
		local ok, err = pcall(step[2])
		if not ok then print("China 1928 " .. step[1] .. " setup failed: " .. tostring(err)) end
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
