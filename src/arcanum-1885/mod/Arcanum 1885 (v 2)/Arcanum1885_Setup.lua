----------------------------------------------------------------
-- Arcanum 1885 game-start setup, run once per game from the UI update loop, a moment after the screen is alive.
--
-- 1. Resources. The map leaves resources to the game (the "randomise resources" map flag), and the game's world-builder
--    placement is stingy on a map this size: a handful of deposits of each strategic resource for the whole continent.
--    So, once, with the game's own random generator (every game still differs):
--    a) every strategic deposit already on the map holds twice as much;
--    b) every strategic resource is topped up to a density set by the land area, at least twice the deposits the game
--       placed, spread over the map's sectors in proportion to their land;
--    c) every nation's start gets at least 2 iron, 2 coal and 1 horses within 5 hexes (within 4 where the land allows),
--       every free city at least one strategic deposit within 3 hexes;
--    d) every luxury and bonus resource on the map gets half as many deposits again.
--    New deposits obey the game's own placement rules (Plot:CanHaveResource: Resource_TerrainBooleans, _FeatureBooleans,
--    _FeatureTerrainBooleans, hills / flatland / riverside flags); only a start that has no such plot nearby falls back
--    to the wider rules of the stock map scripts (iron and coal on wooded hills, coal in flat forest or jungle).
--    No plot that holds a resource, a city, an improvement, a natural wonder or a start is touched, except that 1a
--    raises the amount on plots that already hold a strategic resource and no city or improvement.
-- 2. The Smoky Skies scenario opened all five policy branches for every nation at the start (its TurnsRemaining.lua did
--    it); that file is not used here, so the same is done here.
--
-- Run once: only on the first turn, and not again once marked done, either in the save data or by the open branches
-- (a game state of its own, saved with the game), so reloading a save never adds resources twice.
----------------------------------------------------------------
local kBranches = { "POLICY_BRANCH_CULTURE", "POLICY_BRANCH_MILITARY", "POLICY_BRANCH_INDUSTRY", "POLICY_BRANCH_LABOR", "POLICY_BRANCH_COMMERCE" }

-- Strategic resources: land plots per deposit wanted on the map, and the amount of a new deposit (from, to). The amounts
-- span the stock map scripts' small and major deposits; aluminum and uranium are the scenario's Aetherium and Luboric.
local kStrategic = {
	{ type = "RESOURCE_IRON",     landPer =  90, amount = { 3, 6 } },
	{ type = "RESOURCE_COAL",     landPer = 110, amount = { 3, 7 } },
	{ type = "RESOURCE_HORSE",    landPer = 110, amount = { 2, 4 } },
	{ type = "RESOURCE_OIL",      landPer = 160, amount = { 3, 7 } },
	{ type = "RESOURCE_ALUMINUM", landPer = 200, amount = { 3, 8 } },
	{ type = "RESOURCE_URANIUM",  landPer = 200, amount = { 2, 4 } },
}
local kStartNeeds = { { "RESOURCE_IRON", 2 }, { "RESOURCE_COAL", 2 }, { "RESOURCE_HORSE", 1 } }   -- per nation's start
local kFreeCityPicks = { "RESOURCE_IRON", "RESOURCE_COAL", "RESOURCE_HORSE", "RESOURCE_OIL" }        -- one of them if a free city has none
local START_NEAR, START_FAR, FREE_CITY_RADIUS = 4, 5, 3
local STRATEGIC_SPACING = 2      -- no two deposits of one strategic resource within 2 hexes (top-up only)
local EXTRA_PERCENT = 50         -- luxury and bonus deposits added, in percent of those on the map
local SECTOR_COLS, SECTOR_ROWS = 4, 5

local g_W, g_H                   -- map size
local g_deposits = {}            -- resource ID -> list of { x, y }
local g_isStart = {}             -- plot index -> true for the nations' and free cities' start plots
local g_isWonder = {}            -- feature ID -> true for natural wonders
local g_blocked = {}             -- plot index -> true where nothing may be placed (see IsFree)
local g_log = {}                 -- resource ID -> { doubled, topup, starts, cities, extra }
local FOREST, JUNGLE = -2, -2    -- feature IDs, set in PlaceResources

local function Rand(n, why)      -- 0 .. n-1 from the game's synchronised generator
	if n <= 1 then return 0 end
	return Game.Rand(n, "Arcanum 1885 resources: " .. why)
end

local function Shuffle(t)
	for i = #t, 2, -1 do
		local j = Rand(i, "shuffle") + 1
		t[i], t[j] = t[j], t[i]
	end
	return t
end

local function Log(id, key)
	local e = g_log[id]
	if not e then e = { doubled = 0, topup = 0, starts = 0, cities = 0, extra = 0 }; g_log[id] = e end
	e[key] = e[key] + 1
end

local function Index(plot) return plot:GetY() * g_W + plot:GetX() end

-- Deposits of one resource within `radius` hexes of (x, y).
local function CountNear(id, x, y, radius)
	local n = 0
	for _, d in ipairs(g_deposits[id] or {}) do
		if Map.PlotDistance(x, y, d[1], d[2]) <= radius then n = n + 1 end
	end
	return n
end

local function HasResourceAdjacent(plot)
	for dir = 0, DirectionTypes.NUM_DIRECTION_TYPES - 1 do
		local adj = Map.PlotDirection(plot:GetX(), plot:GetY(), dir)
		if adj and adj:GetResourceType() ~= -1 then return true end
	end
	return false
end

local function NextToMountain(plot)
	for dir = 0, DirectionTypes.NUM_DIRECTION_TYPES - 1 do
		local adj = Map.PlotDirection(plot:GetX(), plot:GetY(), dir)
		if adj and adj:IsMountain() then return true end
	end
	return false
end

-- A plot the setup may put a new resource on: empty, no city, improvement, natural wonder, start or lake. Everything but
-- the resource stays put while the setup runs, so it is looked up once per plot.
local function IsFree(plot)
	local i = Index(plot)
	local blocked = g_blocked[i]
	if blocked == nil then
		blocked = g_isStart[i] == true or plot:IsCity() or plot:GetImprovementType() ~= -1
			or g_isWonder[plot:GetFeatureType()] == true or plot:IsLake()
		g_blocked[i] = blocked
	end
	return not blocked and plot:GetResourceType() == -1
end

-- The game's own rule; strategic resources only on land.
local function IsLegal(plot, id, landOnly)
	if not IsFree(plot) then return false end
	if landOnly and plot:IsWater() then return false end
	return plot:CanHaveResource(id, false)
end

-- The wider rules of the stock map scripts (AssignStartingPlots), used only when a start has no legal plot left nearby.
local function IsStockLegal(plot, typeName)
	if not IsFree(plot) or plot:IsWater() or plot:IsMountain() then return false end
	local f = plot:GetFeatureType()
	local open = (f == -1)
	local wooded = (f == FOREST or f == JUNGLE)
	if typeName == "RESOURCE_IRON" then
		return plot:IsHills() and (open or wooded)
	elseif typeName == "RESOURCE_COAL" then
		return (plot:IsHills() and (open or wooded)) or (plot:IsFlatlands() and wooded)
	elseif typeName == "RESOURCE_HORSE" then
		local t = GameInfo.Terrains[plot:GetTerrainType()]
		return plot:IsFlatlands() and open and t ~= nil
			and (t.Type == "TERRAIN_GRASS" or t.Type == "TERRAIN_PLAINS" or t.Type == "TERRAIN_TUNDRA")
	end
	return false
end

local function Place(plot, id, amount, key)
	plot:SetResourceType(id, amount)
	if plot:GetResourceType() ~= id then return false end
	table.insert(g_deposits[id], { plot:GetX(), plot:GetY() })
	Log(id, key)
	return true
end

local function NewAmount(spec)
	return spec.amount[1] + Rand(spec.amount[2] - spec.amount[1] + 1, "amount " .. spec.type)
end

-- Sets the amount on a plot that keeps its resource.
local function SetAmount(plot, id, n)
	pcall(function() plot:SetNumResource(n) end)
	if plot:GetNumResource() ~= n then
		plot:SetResourceType(-1)
		plot:SetResourceType(id, n)
	end
end

-- Plots within `radius` of (x, y), not the centre, as a list of { plot, distance }.
local function PlotsAround(x, y, radius)
	local out = {}
	for dy = -radius, radius do
		for dx = -radius, radius do
			local plot = Map.GetPlotXY(x, y, dx, dy)
			if plot then
				local d = Map.PlotDistance(x, y, plot:GetX(), plot:GetY())
				if d >= 1 and d <= radius then table.insert(out, { plot, d }) end
			end
		end
	end
	return out
end

-- A random plot for `spec` around (x, y): the game's rules within `near` hexes first, then within `far`, then the stock
-- map scripts' wider rules the same way.
local function PickAround(spec, x, y, near, far)
	local around = PlotsAround(x, y, far)
	local passes = {
		{ near, function(p) return IsLegal(p, spec.id, true) end },
		{ far,  function(p) return IsLegal(p, spec.id, true) end },
		{ near, function(p) return IsStockLegal(p, spec.type) end },
		{ far,  function(p) return IsStockLegal(p, spec.type) end },
	}
	for _, pass in ipairs(passes) do
		local found = {}
		for _, e in ipairs(around) do
			if e[2] <= pass[1] and pass[2](e[1]) then table.insert(found, e[1]) end
		end
		if #found > 0 then return found[Rand(#found, "pick " .. spec.type) + 1] end
	end
	return nil
end

local function StartPlotOf(pPlayer)
	local plot = pPlayer:GetStartingPlot()
	if plot then return plot end
	for unit in pPlayer:Units() do return unit:GetPlot() end
	return nil
end

local function PlaceResources()
	g_W, g_H = Map.GetGridSize()
	local byType = {}
	for _, spec in ipairs(kStrategic) do
		local row = GameInfo.Resources[spec.type]
		if row then spec.id = row.ID; byType[spec.type] = spec end
	end
	for row in GameInfo.Resources() do g_deposits[row.ID] = {} end
	for row in GameInfo.Features() do
		if row.NaturalWonder == true or row.NaturalWonder == 1 then g_isWonder[row.ID] = true end
	end
	if GameInfo.Features.FEATURE_FOREST then FOREST = GameInfo.Features.FEATURE_FOREST.ID end
	if GameInfo.Features.FEATURE_JUNGLE then JUNGLE = GameInfo.Features.FEATURE_JUNGLE.ID end

	-- The nations' starts and the free cities.
	local majors, cities = {}, {}
	for iPlayer = 0, GameDefines.MAX_CIV_PLAYERS - 1 do
		local pPlayer = Players[iPlayer]
		if pPlayer and pPlayer:IsAlive() then
			if pPlayer:IsMinorCiv() then
				local city = pPlayer:GetCapitalCity()
				if not city then for c in pPlayer:Cities() do city = c; break end end
				if city then table.insert(cities, city:Plot()) end
			elseif iPlayer < GameDefines.MAX_MAJOR_CIVS then
				local plot = StartPlotOf(pPlayer)
				if plot then table.insert(majors, plot); g_isStart[Index(plot)] = true end
			end
		end
	end
	for _, plot in ipairs(cities) do g_isStart[Index(plot)] = true end

	-- Survey: deposits by type, land per sector.
	local sectorW, sectorH = g_W / SECTOR_COLS, g_H / SECTOR_ROWS
	local function SectorOf(x, y)
		return math.min(SECTOR_COLS - 1, math.floor(x / sectorW)) + math.min(SECTOR_ROWS - 1, math.floor(y / sectorH)) * SECTOR_COLS + 1
	end
	local nSectors = SECTOR_COLS * SECTOR_ROWS
	local sectorLand, land = {}, 0
	for s = 1, nSectors do sectorLand[s] = 0 end
	local all = {}
	for i = 0, Map.GetNumPlots() - 1 do
		local plot = Map.GetPlotByIndex(i)
		local r = plot:GetResourceType()
		if r ~= -1 and g_deposits[r] then table.insert(g_deposits[r], { plot:GetX(), plot:GetY() }) end
		if not plot:IsWater() and not plot:IsMountain() then
			land = land + 1
			local s = SectorOf(plot:GetX(), plot:GetY())
			sectorLand[s] = sectorLand[s] + 1
		end
		table.insert(all, plot)
	end
	local stockCount = {}
	for id, list in pairs(g_deposits) do stockCount[id] = #list end

	-- a) Twice the amount in every strategic deposit (not on cities or improved plots, whose amount the owner already counts).
	for _, plot in ipairs(all) do
		local r = plot:GetResourceType()
		for _, spec in ipairs(kStrategic) do
			if spec.id == r and not plot:IsCity() and plot:GetImprovementType() == -1 then
				local n = plot:GetNumResource()
				if n > 0 then SetAmount(plot, r, n * 2); Log(r, "doubled") end
			end
		end
	end

	-- b) Top up every strategic resource, sector by sector in proportion to the land.
	local sectorJitter = {}
	for s = 1, nSectors do sectorJitter[s] = Rand(1000, "sector order") / 100000 end
	for _, spec in ipairs(kStrategic) do
		if spec.id then
			local id = spec.id
			local target = math.max(2 * stockCount[id], math.floor(land / spec.landPer))
			local toAdd = target - #g_deposits[id]
			-- Candidates per sector, shuffled; for iron and aluminum the hills and the plots next to mountains first.
			local cand, count = {}, {}
			for s = 1, nSectors do cand[s] = { pos = 1 }; count[s] = 0 end
			local preferred, other = {}, {}
			for _, plot in ipairs(all) do
				if IsLegal(plot, id, true) then
					local prefer = (spec.type == "RESOURCE_IRON" or spec.type == "RESOURCE_ALUMINUM") and (plot:IsHills() or NextToMountain(plot))
					table.insert(prefer and preferred or other, plot)
				end
			end
			for _, list in ipairs({ Shuffle(preferred), Shuffle(other) }) do
				for _, plot in ipairs(list) do table.insert(cand[SectorOf(plot:GetX(), plot:GetY())], plot) end
			end
			for _, d in ipairs(g_deposits[id]) do
				local s = SectorOf(d[1], d[2]); count[s] = count[s] + 1
			end
			local added = 0
			while added < toAdd do
				-- the sector furthest below its share of the target that still has a candidate
				local best, bestGap = nil, nil
				for s = 1, nSectors do
					if cand[s].pos <= #cand[s] then
						local gap = target * sectorLand[s] / land - count[s] + sectorJitter[s]
						if not bestGap or gap > bestGap then best, bestGap = s, gap end
					end
				end
				if not best then break end
				local list = cand[best]
				local placed = false
				while list.pos <= #list and not placed do
					local plot = list[list.pos]; list.pos = list.pos + 1
					if IsLegal(plot, id, true) and CountNear(id, plot:GetX(), plot:GetY(), STRATEGIC_SPACING) == 0 then
						placed = Place(plot, id, NewAmount(spec), "topup")
					end
				end
				if placed then added = added + 1; count[best] = count[best] + 1 end
			end
		end
	end

	-- c) Every nation's start: 2 iron, 2 coal, 1 horses within 5 hexes; every free city: one strategic within 3.
	for _, start in ipairs(majors) do
		local x, y = start:GetX(), start:GetY()
		for _, need in ipairs(kStartNeeds) do
			local spec = byType[need[1]]
			if spec and spec.id then
				local have = CountNear(spec.id, x, y, START_FAR)
				while have < need[2] do
					local plot = PickAround(spec, x, y, START_NEAR, START_FAR)
					if not plot or not Place(plot, spec.id, math.max(spec.amount[1] + 1, NewAmount(spec)), "starts") then
						print("Arcanum 1885: no plot for " .. spec.type .. " near the start at " .. x .. "," .. y)
						break
					end
					have = have + 1
				end
			end
		end
	end
	for _, home in ipairs(cities) do
		local x, y = home:GetX(), home:GetY()
		local have = 0
		for _, spec in ipairs(kStrategic) do
			if spec.id then have = have + CountNear(spec.id, x, y, FREE_CITY_RADIUS) end
		end
		if have == 0 then
			local picks = {}
			for _, t in ipairs(kFreeCityPicks) do if byType[t] and byType[t].id then table.insert(picks, byType[t]) end end
			for _, spec in ipairs(Shuffle(picks)) do
				local plot = PickAround(spec, x, y, FREE_CITY_RADIUS, FREE_CITY_RADIUS)
				if plot and Place(plot, spec.id, NewAmount(spec), "cities") then break end
			end
		end
	end

	-- d) Half as many again of every luxury and bonus resource on the map, one plot apart from any other resource.
	local free = {}
	for _, plot in ipairs(all) do
		if IsFree(plot) and not plot:IsMountain() then table.insert(free, plot) end
	end
	Shuffle(free)
	for row in GameInfo.Resources() do
		local luxury = (row.ResourceClassType == "RESOURCECLASS_LUXURY")
		local bonus = (row.ResourceClassType == "RESOURCECLASS_BONUS")
		local n = stockCount[row.ID] or 0
		if (luxury or bonus) and n > 0 and not row.OnlyMinorCivs and row.CivilizationType == nil then
			local want = math.floor(n * EXTRA_PERCENT / 100)
			if (n * EXTRA_PERCENT) % 100 ~= 0 and Rand(2, "round " .. row.Type) == 1 then want = want + 1 end
			if luxury and want < 1 then want = 1 end
			local added = 0
			local start = Rand(#free, "start " .. row.Type) + 1    -- each resource walks the shuffled list from its own place
			for k = 0, #free - 1 do
				if added >= want then break end
				local plot = free[(start + k - 1) % #free + 1]
				if IsLegal(plot, row.ID, false) and not HasResourceAdjacent(plot)
						and CountNear(row.ID, plot:GetX(), plot:GetY(), 2) == 0 then
					if Place(plot, row.ID, 1, "extra") then added = added + 1 end
				end
			end
		end
	end

	-- Summary for Lua.log.
	print("Arcanum 1885 resources: " .. land .. " land plots, " .. #majors .. " starts, " .. #cities .. " free cities")
	for row in GameInfo.Resources() do
		local e = g_log[row.ID]
		if e then
			print(string.format("  %-20s on map %3d -> %3d   doubled %3d  top-up %3d  at starts %2d  at free cities %2d  extra %3d",
				row.Type, stockCount[row.ID], #g_deposits[row.ID], e.doubled, e.topup, e.starts, e.cities, e.extra))
		end
	end
end

local function UnlockBranches()
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
		local pPlayer = Players[iPlayer]
		if pPlayer and pPlayer:IsAlive() and not pPlayer:IsMinorCiv() then
			for _, name in ipairs(kBranches) do
				local branch = GameInfo.PolicyBranchTypes[name]
				if branch and not pPlayer:IsPolicyBranchUnlocked(branch.ID) then
					pPlayer:SetPolicyBranchUnlocked(branch.ID, true)
				end
			end
		end
	end
	print("Arcanum 1885: policy branches opened")
end

-- Done before: marked in the save data, or every nation already has the five branches open (nothing else opens them on
-- the first turn, and the branches are saved with the game even if the save data is not).
local function SetupDone()
	local ok, v = pcall(function() return Modding.OpenSaveData().GetValue("ARC1885_SETUP_DONE") end)
	if ok and v ~= nil then return true end
	local nations, open = 0, 0
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
		local pPlayer = Players[iPlayer]
		if pPlayer and pPlayer:IsAlive() and not pPlayer:IsMinorCiv() then
			nations = nations + 1
			local all = true
			for _, name in ipairs(kBranches) do
				local branch = GameInfo.PolicyBranchTypes[name]
				if branch and not pPlayer:IsPolicyBranchUnlocked(branch.ID) then all = false end
			end
			if all then open = open + 1 end
		end
	end
	return nations > 0 and open == nations
end
local function MarkSetupDone() pcall(function() Modding.OpenSaveData().SetValue("ARC1885_SETUP_DONE", 1) end) end

local g_elapsed = 0
local g_pending = true
ContextPtr:SetUpdate(function(dt)
	if not g_pending then return end
	g_elapsed = g_elapsed + (dt or 0)
	if g_elapsed < 2.0 then return end
	g_pending = false
	if Game.GetElapsedGameTurns() > 0 then return end
	if SetupDone() then print("Arcanum 1885: setup already done in this game"); return end
	MarkSetupDone()
	local ok, err = pcall(PlaceResources)
	if not ok then print("Arcanum 1885 resources failed: " .. tostring(err)) end
	ok, err = pcall(UnlockBranches)
	if not ok then print("Arcanum 1885 setup failed: " .. tostring(err)) end
end)
