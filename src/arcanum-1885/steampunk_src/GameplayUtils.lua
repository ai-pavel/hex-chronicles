--------------------------------------------------------------
-- GameplayUtils.lua --
-- Scenario: Empires of the Smoky Skies (XP)
-- Author: Anton Strenger
-- DateCreated: 1/11/2012
--
-- Contains constants and helper functions 
-- used in gameplay and UI scripting.
--------------------------------------------------------------
-- Hungarian Notation Addendum --
-- k		: Global constant
-- t		: Lua table
--------------------------------------------------------------

-----------------------------
-- Constants --
-----------------------------
kiTokensNeededForVictory = 3;
function GetTokensNeededForVictory() return kiTokensNeededForVictory; end

kiCultureFromFirstCity = 115; -- Just enough for 3 policies
function GetCultureFromFirstCity() return kiCultureFromFirstCity; end

kiCultureFromLastTech = 200;
function GetCultureFromLastTech() return kiCultureFromLastTech; end

kiTurnsMustHoldForVictory = 5;
function GetTurnsMustHoldForVictory() return kiTurnsMustHoldForVictory; end

ktTokens =
{
	--[[
	Type	: (string) Name of the token. IMPORTANT: Used as key for saved data, so changing this will cause problems with older saves!
	{
		Name		: (string) Category name
		Title		: (string) Honorary title given to the player that owns the token
		Help		: (string) Text describing what is measured to determine ownership
		UnlockTurn	: (int) Must reach this turn before token is available
		UnlockTech	: (int) Some player must discover this tech before token is available
		DefaultValue: (int) Value that a player starts with
	}
	--]]
	Military = {
		Name = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_MILITARY"),
		Title = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_MILITARY_TITLE"),
		Help = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_MILITARY_HELP"),
		UnlockTurn = 0,
		UnlockTech = GameInfo.Technologies["TECH_LANDSHIPS"].ID,
		DefaultValue = 0,
	},
	Labor = {
		Name = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_LABOR"),
		Title = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_LABOR_TITLE"),
		Help = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_LABOR_HELP"),
		UnlockTurn = 0,
		UnlockTech = GameInfo.Technologies["TECH_NOBLESSE_OBLIGE"].ID,
		DefaultValue = 0,
	},
	Industry = {
		Name = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_INDUSTRY"),
		Title = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_INDUSTRY_TITLE"),
		Help = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_INDUSTRY_HELP"),
		UnlockTurn = 0,
		UnlockTech = GameInfo.Technologies["TECH_AUTOMATA"].ID,
		DefaultValue = 0,
	},
	Culture = {
		Name = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_CULTURE"),
		Title = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_CULTURE_TITLE"),
		Help = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_CULTURE_HELP"),
		UnlockTurn = 0,
		UnlockTech = GameInfo.Technologies["TECH_TECHNOCRACY"].ID,
		DefaultValue = 0,
	},
	Commerce = {
		Name = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_COMMERCE"),
		Title = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_COMMERCE_TITLE"),
		Help = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_COMMERCE_HELP"),
		UnlockTurn = 0,
		UnlockTech = GameInfo.Technologies["TECH_PERPETUAL_MOTION"].ID,
		DefaultValue = 0,
	},
}
function GetTokensTable() return ktTokens; end

ktUnitTiers =
{
	Airship =
	{
		{
			Tech = GameInfo.Technologies["TECH_AIRSHIPS"].ID,
			UnitClass = GameInfo.UnitClasses["UNITCLASS_AIRSHIP"].ID,
		},
		{
			Tech = GameInfo.Technologies["TECH_SKY_FORTRESS"].ID,
			UnitClass = GameInfo.UnitClasses["UNITCLASS_SKY_FORTRESS"].ID,
		},
	},
	Landship = 
	{
		{
			Tech = GameInfo.Technologies["TECH_STEAM_POWER"].ID,
			UnitClass = GameInfo.UnitClasses["UNITCLASS_LAND_IRONCLAD"].ID,
		},
		{
			Tech = GameInfo.Technologies["TECH_LANDSHIPS"].ID,
			UnitClass = GameInfo.UnitClasses["UNITCLASS_LANDSHIP"].ID,
		},
		{
			Tech = GameInfo.Technologies["TECH_LAND_LEVIATHAN"].ID,
			UnitClass = GameInfo.UnitClasses["UNITCLASS_LAND_LEVIATHAN"].ID,
		},
	}
}
function GetUnitTiersTable() return ktUnitTiers; end

ktWonderPoints = 
{
	-- National Wonders
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_ANALYTICAL_ENGINE"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_BILTMORE_HOUSE"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_INVENTORS_HALL"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_CARNEGIE_HALL"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_SUBTERRANEAN_COLONY"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_PERPETUAL_MOTION_ENGINE"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_INTELLIGENCE_AGENCY"].ID,
		Value = 1,
	},
	-- World Wonders
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_BIG_BEN"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_BRANDENBURG_GATE"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_LOUVRE"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_STATUE_OF_LIBERTY"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_EIFFEL_TOWER"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_PENTAGON"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_NEUSCHWANSTEIN"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_CRISTO_REDENTOR"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_SYDNEY_OPERA_HOUSE"].ID,
		Value = 1,
	},
	{
		BuildingClass = GameInfo.BuildingClasses["BUILDINGCLASS_CN_TOWER"].ID,
		Value = 1,
	},
}
function GetWonderPointsTable() return ktWonderPoints; end

-----------------------------
-- Gameplay Functions --
-----------------------------
function IsTechResearchedByAnyone(iTech)
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		if (Players[iPlayer] ~= nil and Players[iPlayer]:IsAlive()) then
			local iTeam = Players[iPlayer]:GetTeam();
			if (Teams[iTeam] ~= nil) then
				if (Teams[iTeam]:IsHasTech(iTech)) then
					return true;
				end
			end
		end
	end
	
	return false;
end

-- Can this token be owned by a player? (Unlocks at same time for all players)
function IsTokenUnlocked(sToken, iTurn)
	-- Game turn
	if (iTurn >= ktTokens[sToken].UnlockTurn) then
		-- Tech research
		if (ktTokens[sToken].UnlockTech ~= nil and IsTechResearchedByAnyone(ktTokens[sToken].UnlockTech)) then
			return true;
		end
	end

	return false;
end

-- How many tokens are unlocked?
function GetNumTokensUnlocked(iTurn)
	local iTokens = 0;
	for s,t in pairs(ktTokens) do
		if (IsTokenUnlocked(s, iTurn)) then
			iTokens = iTokens + 1;
		end
	end
	
	return iTokens;
end

function IsVictoryPossible(iTurn)
	return (GetNumTokensUnlocked(iTurn) >= GetTokensNeededForVictory());
end

-- What is the highest production city for this player?
function GetMostProductiveCityForPlayer(iPlayer)
	local iValue = ktTokens.Industry.DefaultValue;
	local iCityID = nil;
	local pPlayer = Players[iPlayer];
	
	-- What is this player's most productive city?
	if (pPlayer ~= nil) then
		for pCity in pPlayer:Cities() do
			if (pCity ~= nil) then
				local iProd = pCity:GetCurrentProductionDifference(false, false);
				if (iProd >= iValue) then
					iValue = iProd;
					iCityID = pCity:GetID();
				end
			end
		end
	else
		print("Scripting error - pPlayer is nil when looking for most productive city");
	end
	
	return iCityID;
end

-----------------------------
-- Utility Functions --
-----------------------------
-- Make a deep copy of a Lua table
-- From http://snippets.luacode.org/snippets/Deep_copy_of_a_Lua_Table_2
function deepcopy(t)
	if type(t) ~= 'table' then return t end
	local mt = getmetatable(t)
	local res = {}
	for k,v in pairs(t) do
		if type(v) == 'table' then
			v = deepcopy(v)
		end
		res[k] = v
	end
	setmetatable(res,mt)
	return res
end