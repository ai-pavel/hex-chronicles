----------------------------------------------------------------
-- Spain 1936 turn-1 setup.
--  * buildings: the stock buildings the map places become each side's own of the same class
--  * production: every city gets a 1936-era unit in its queue
--  * unit names: the stock type stays, the unit carries its historical designation
--  * diplomacy: the four Republican sides are friends, so are the two Nationalist armies
--  * stance: the human player's units start fortified
--  * calendar: one turn = one week from 25 July 1936, drawn over the top panel
----------------------------------------------------------------
local kQueues = {
	CIVILIZATION_RUSSIA   = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_MACHINE_GUN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_ANTI_AIRCRAFT_GUN", "UNIT_WORKER" },
	CIVILIZATION_ZULU     = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_MACHINE_GUN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
	CIVILIZATION_GERMANY  = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_MACHINE_GUN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
	CIVILIZATION_SHOSHONE = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_MACHINE_GUN", "UNIT_ARTILLERY", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
	CIVILIZATION_ETHIOPIA = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_MACHINE_GUN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_ARTILLERY" },
	CIVILIZATION_AZTEC    = { "UNIT_GREAT_WAR_INFANTRY", "UNIT_MACHINE_GUN", "UNIT_GREAT_WAR_INFANTRY", "UNIT_WORKER" },
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
	print("Spain 1936: initial production queued")
end

----------------------------------------------------------------
local kUnitNames = {
	CIVILIZATION_RUSSIA = { UNIT_GREAT_WAR_INFANTRY = "Mixed Brigade", UNIT_RIFLEMAN = "Popular Militia", UNIT_RUSSIAN_COSSACK = "Cavalry Squadron", UNIT_CAVALRY = "Cavalry Squadron",
		UNIT_ARTILLERY = "Field Battery", UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_ANTI_AIRCRAFT_GUN = "Anti-aircraft Battery", UNIT_TRIPLANE = "Nieuport-Delage 52",
		UNIT_WWI_BOMBER = "Breguet XIX", UNIT_WWI_TANK = "Renault FT", UNIT_BATTLESHIP = "Jaime I", UNIT_DESTROYER = "Churruca-class Destroyer", UNIT_SUBMARINE = "C-class Submarine",
		UNIT_WORKER = "Fortification Workers", UNIT_CARAVAN = "Supply Lorries", UNIT_CARGO_SHIP = "Supply Ship" },
	CIVILIZATION_ZULU = { UNIT_GREAT_WAR_INFANTRY = "Army of Africa", UNIT_RIFLEMAN = "Falange Militia", UNIT_CAVALRY = "Regulares Cavalry", UNIT_ARTILLERY = "Field Battery",
		UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_ANTI_AIRCRAFT_GUN = "Anti-aircraft Battery", UNIT_TRIPLANE = "Nationalist Fighter Squadron", UNIT_WWI_BOMBER = "Ju 52",
		UNIT_WWI_TANK = "Panzer I", UNIT_IRONCLAD = "Gunboat", UNIT_DESTROYER = "Destroyer", UNIT_WORKER = "Labour Battalion", UNIT_CARAVAN = "Supply Column", UNIT_CARGO_SHIP = "Supply Ship" },
	CIVILIZATION_GERMANY = { UNIT_GREAT_WAR_INFANTRY = "Army of the North", UNIT_RIFLEMAN = "Requetes", UNIT_CAVALRY = "Cavalry Regiment", UNIT_ARTILLERY = "Field Battery",
		UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_ANTI_AIRCRAFT_GUN = "Anti-aircraft Battery", UNIT_TRIPLANE = "He 51", UNIT_WWI_BOMBER = "Ju 52", UNIT_WWI_TANK = "Panzer I",
		UNIT_BATTLESHIP = "Espana", UNIT_DESTROYER = "Velasco-class Destroyer", UNIT_WORKER = "Labour Battalion", UNIT_CARAVAN = "Supply Column", UNIT_CARGO_SHIP = "Supply Ship" },
	CIVILIZATION_SHOSHONE = { UNIT_GREAT_WAR_INFANTRY = "Catalan Army", UNIT_RIFLEMAN = "Militia Column", UNIT_SHOSHONE_COMANCHE_RIDERS = "Cavalry Squadron", UNIT_CAVALRY = "Cavalry Squadron",
		UNIT_ARTILLERY = "Field Battery", UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_ANTI_AIRCRAFT_GUN = "Anti-aircraft Battery", UNIT_TRIPLANE = "Generalitat Air Squadron",
		UNIT_WWI_BOMBER = "Breguet XIX", UNIT_WWI_TANK = "Armoured Car", UNIT_DESTROYER = "Destroyer", UNIT_WORKER = "Fortification Workers", UNIT_CARAVAN = "Supply Lorries", UNIT_CARGO_SHIP = "Supply Ship" },
	CIVILIZATION_ETHIOPIA = { UNIT_GREAT_WAR_INFANTRY = "Euzko Gudarostea", UNIT_RIFLEMAN = "Gudari Battalion", UNIT_ETHIOPIAN_MEHAL_SEFARI = "Gudari Battalion", UNIT_ARTILLERY = "Field Battery",
		UNIT_MACHINE_GUN = "Machine-gun Company", UNIT_ANTI_AIRCRAFT_GUN = "Anti-aircraft Battery", UNIT_TRIPLANE = "Basque Air Squadron", UNIT_WWI_TANK = "Armoured Car",
		UNIT_IRONCLAD = "Armed Trawler", UNIT_DESTROYER = "Destroyer", UNIT_WORKER = "Iron Ring Workers", UNIT_CARAVAN = "Supply Lorries", UNIT_CARGO_SHIP = "Supply Ship" },
	CIVILIZATION_AZTEC = { UNIT_GREAT_WAR_INFANTRY = "Confederal Division", UNIT_RIFLEMAN = "Confederal Column", UNIT_ARTILLERY = "Field Battery", UNIT_MACHINE_GUN = "Machine-gun Section",
		UNIT_ANTI_AIRCRAFT_GUN = "Anti-aircraft Battery", UNIT_WWI_TANK = "Tiznao Armoured Lorry", UNIT_TRIPLANE = "Militia Air Squadron", UNIT_WORKER = "Collective Workers", UNIT_CARAVAN = "Supply Lorries" },
}
-- special cases picked by promotion: the Spanish Legion (Drill I + Shock I), the Regulares and the requetes (Shock I), the Assault Guards
-- and the besieged garrisons (Drill I + Cover I), the confederal columns (Shock I + March)
local function Has(unit, promo) local p = GameInfo.UnitPromotions[promo]; return p and unit:IsHasPromotion(p.ID) end
local function SpecialName(civType, unit, ut)
	local drill, shock, cover, march = Has(unit, "PROMOTION_DRILL_1"), Has(unit, "PROMOTION_SHOCK_1"), Has(unit, "PROMOTION_COVER_1"), Has(unit, "PROMOTION_MARCH")
	if civType == "CIVILIZATION_ZULU" then
		if ut.Type == "UNIT_GREAT_WAR_INFANTRY" and drill and shock then return "Spanish Legion" end
		if ut.Type == "UNIT_GREAT_WAR_INFANTRY" and drill and cover then return "Alcazar Garrison" end
		if shock and (ut.Type == "UNIT_RIFLEMAN" or ut.Type == "UNIT_GREAT_WAR_INFANTRY" or ut.Type == "UNIT_CAVALRY") then return "Regulares" end
	elseif civType == "CIVILIZATION_GERMANY" then
		if ut.Type == "UNIT_GREAT_WAR_INFANTRY" and drill and cover then return "Oviedo Garrison" end
		if ut.Type == "UNIT_RIFLEMAN" and shock then return "Requetes" end
	elseif civType == "CIVILIZATION_RUSSIA" or civType == "CIVILIZATION_SHOSHONE" then
		if ut.Type == "UNIT_GREAT_WAR_INFANTRY" and drill and cover then return "Assault Guards" end
		if ut.Type == "UNIT_RIFLEMAN" and shock and civType == "CIVILIZATION_RUSSIA" then return "Asturian Miners" end
	elseif civType == "CIVILIZATION_AZTEC" then
		if ut.Type == "UNIT_RIFLEMAN" and shock and march then return "Confederal Column" end
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
	print("Spain 1936: units set to defensive stance")
end
local function SetupDiplomacy()
	local rep = FindPlayer("CIVILIZATION_RUSSIA"); local nat = FindPlayer("CIVILIZATION_ZULU"); local north = FindPlayer("CIVILIZATION_GERMANY")
	local cat = FindPlayer("CIVILIZATION_SHOSHONE"); local euz = FindPlayer("CIVILIZATION_ETHIOPIA"); local cnt = FindPlayer("CIVILIZATION_AZTEC")
	Friends(nat, north)
	-- the Republic and the Generalitat, the Republic and the Basques, the Generalitat and the Basques; the anarchists are allies of necessity
	Friends(rep, cat); Friends(rep, euz); Friends(cat, euz)
	print("Spain 1936: diplomacy applied")
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
	local y, m, d = 1936, 7, 25
	local n = turn * 7
	while n > 0 do
		local left = DaysInMonth(y, m) - d
		if n <= left then d = d + n; n = 0
		else n = n - left - 1; d = 1; m = m + 1; if m > 12 then m = 1; y = y + 1 end end
	end
	return string.format("%d %s %d", d, Locale.ConvertTextKey("TXT_KEY_ESP1936_MONTH_" .. m), y)
end
local function ApplyCalendar(force)
	local turn = Game.GetGameTurn()
	local dateLabel = ContextPtr:LookUpControl("/InGame/TopPanel/CurrentDate")
	local turnLabel = ContextPtr:LookUpControl("/InGame/TopPanel/CurrentTurn")
	local dateText = DateForTurn(turn)
	local weekText = Locale.ConvertTextKey("TXT_KEY_ESP1936_WEEK", turn + 1)
	if dateLabel and (force or dateLabel:GetText() ~= dateText) then dateLabel:SetText(dateText); dateLabel:SetToolTipString(Locale.ConvertTextKey("TXT_KEY_ESP1936_WEEK_TT", turn + 1)) end
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
	print("Spain 1936: " .. n .. " buildings swapped for their owners' own")
end

----------------------------------------------------------------
local function SetupDone()
	local ok, v = pcall(function() return Modding.OpenSaveData().GetValue("ESP1936_SETUP_DONE") end)
	return ok and v ~= nil
end
local function MarkSetupDone() pcall(function() Modding.OpenSaveData().SetValue("ESP1936_SETUP_DONE", 1) end) end
local function RunSetup()
	print("Spain 1936: running turn-1 setup")
	for _, step in ipairs({ { "buildings", SetupBuildings }, { "production", SetupProduction }, { "names", NameAllUnits }, { "diplomacy", SetupDiplomacy }, { "stance", SetupStance } }) do
		local ok, err = pcall(step[2])
		if not ok then print("Spain 1936 " .. step[1] .. " setup failed: " .. tostring(err)) end
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
