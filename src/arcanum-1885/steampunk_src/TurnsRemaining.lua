--------------------------------------------------------------
-- TurnsRemaining.lua
-- Scenario: Empires of the Smoky Skies (XP)
-- Author: Anton Strenger
-- DateCreated: 1/5/2012
--
-- Updates gameplay data, and handles gameplay events.
--------------------------------------------------------------
-- Terms --
-- Token	: A victory category (ex. Labor, Industry) which 
--			is controlled by a player in order to win
--------------------------------------------------------------
-- Hungarian Notation Addendum --
-- g		: Global variable
-- k		: Global constant
-- t		: Lua table
-- c		: UI control
--------------------------------------------------------------

include( "GameplayUtils" );

-----------------------------
-- Globals --
-----------------------------
-- Constants --
ktTokens = GetTokensTable();
ktUnitTiers = GetUnitTiersTable();
ktTokenUpdateFns = 
{
	Military = function(iPlayer) UpdateMilitary(iPlayer); end,
	Culture = function(iPlayer) UpdateCulture(iPlayer); end,
	Industry = function(iPlayer) UpdateIndustry(iPlayer); end,
	Commerce = function(iPlayer) UpdateCommerce(iPlayer); end,
	Labor = function(iPlayer) UpdateLabor(iPlayer); end,
}

-- Variables --
gbScenarioDone = false;
gbUpdated = false; -- Flag for UI updating
gtTokenLeaderValues = {}; -- Keeps track of the highest current value in each category
gtTokensUnlocked = {}; -- Helps to keep track of whether a token has been unlocked before or not

gtPlayerStatus = {}; -- Keeps track of each player's status in each of the victory categories
gtMostAdvancedUnitTier = {}; -- [sUnitType] = (int) tier (1, 2, ..)

giPlayerAboutToWin = -1;
giTurnsControlHeld = 0;

gbLogSaveData = false;

-- Connection to the Modding save data.  Keep one global connection, rather than opening/closing, to speed up access
g_SaveData = Modding.OpenSaveData();
g_Properties = nil;
-------------------------------------------------------------- 
-- Access the modding database entries through a locally cached table
function GetPersistentProperty(name)
	if(g_Properties == nil) then
		g_Properties = {};
	end
	
	if(g_Properties[name] == nil) then
		g_Properties[name] = g_SaveData.GetValue(name);
	end
	
	return g_Properties[name];
end
--------------------------------------------------------------
-- Access the modding database entries through a locally cached table
function SetPersistentProperty(name, value)
	if(g_Properties == nil) then
		g_Properties = {};
	end
	
	if (g_Properties[name] ~= value) then
		g_SaveData.SetValue(name, value);
		g_Properties[name] = value;
	end
end

-----------------------------
-- Update Loop --
-----------------------------
ContextPtr:SetUpdate(function()
	if (gbScenarioDone) then
		ContextPtr:ClearUpdate();
	end
	
	if (not gbUpdated) then
		local iActivePlayer = Game.GetActivePlayer();
		local strStatus = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_TURNS_REMAINING", GetNumTokensOwned(iActivePlayer), GetNumTokensUnlocked(Game.GetGameTurn() - 1)); --antonjs: consider: keep var for last turn updated
		if (giPlayerAboutToWin == iActivePlayer) then
			strStatus = "[COLOR_POSITIVE_TEXT]" .. strStatus .. "[ENDCOLOR]";
		elseif (giPlayerAboutToWin ~= -1) then
			strStatus = "[COLOR_WARNING_TEXT]" .. strStatus .. "[ENDCOLOR]";
		end
		Controls.QuickStatusLabel:SetText(strStatus);
		gbUpdated = true;
	end
	
	Controls.Grid:DoAutoSize();
end);

function OnGameCoreUpdateBegin()
	local iLeaderTokens = 0;
	local iLeader = -1;
	local iLeaderTeam = -1;
	
	-- Get token leader
	for iPlayerLoop = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		local iTokensOwned = GetNumTokensOwned(iPlayerLoop);
		if (iTokensOwned > iLeaderTokens) then --antonjs: todo: address case of a tie
			iLeaderTokens = iTokensOwned;
			iLeader = iPlayerLoop;
			iLeaderTeam = Players[iPlayerLoop]:GetTeam();
		end
	end
	
	-- Check for victory
	if (iLeaderTokens >= GetTokensNeededForVictory()) then
		if (iLeader ~= -1 and iLeader == giPlayerAboutToWin) then
			if (giTurnsControlHeld >= GetTurnsMustHoldForVictory()) then
				local gameState = Game.GetGameState();
				if (gameState == GameplayGameStateTypes.GAMESTATE_ON) then
					Game.SetVictoryValid(GameInfo.Victories["VICTORY_TIME"].ID, true);
					Game.SetWinner(iLeaderTeam, GameInfo.Victories["VICTORY_TIME"].ID);
					gbScenarioDone = true;
				elseif (gameState == GameplayGameStateTypes.GAMESTATE_EXTENDED) then
					Game.SetGameState(GameplayGameStateTypes.GAMESTATE_OVER);
					gbScenarioDone = true;
				end
			end
		end
	end
	
	if (gbScenarioDone) then
		GameEvents.GameCoreUpdateBegin.Remove(OnGameCoreUpdateBegin);
		DoEndgameAchievements();
	end
end
GameEvents.GameCoreUpdateBegin.Add( OnGameCoreUpdateBegin );

-----------------------------
-- Gameplay Data --
-----------------------------
function GetNumTokensOwned(iPlayer)
	local iTokensOwned = 0;
	for s,t in pairs(ktTokens) do
		CheckHasPlayerData(iPlayer, s);
		if (gtPlayerStatus[iPlayer][s].Owned) then
			iTokensOwned = iTokensOwned + 1;
		end
	end
	
	return iTokensOwned;
end

-- The most advanced unit tier goes up as soon as any player builds (not just researches) a more advanced unit.
-- Once the tier goes up, it does not go back down; the world (and the League) has raised its standards.
function UpdateMostAdvancedUnits()
	local bSomethingChanged = false;

	-- For each unit type (ex. landship, airship)
	for sType,tTiers in pairs(ktUnitTiers) do
		local iUnitTier = gtMostAdvancedUnitTier[sType];
		-- For each tier
		for iTier,t in ipairs(tTiers) do
			if (iTier > iUnitTier) then
				-- Check to see if any players have a more advanced unit than our current most advanced
				for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
					local pPlayer = Players[iPlayer];
					if (pPlayer ~= nil and pPlayer:IsAlive()) then
						if (pPlayer:GetUnitClassCount(t.UnitClass) > 0) then
							iUnitTier = iTier;
							break;
						end
					end
				end
			end
		end
		
		if (iUnitTier > gtMostAdvancedUnitTier[sType]) then
			bSomethingChanged = true;
			gtMostAdvancedUnitTier[sType] = iUnitTier;
		end
	end
	
	if (bSomethingChanged) then
		SaveSteampunkData();
	
		local tCopy = deepcopy(gtMostAdvancedUnitTier);
		LuaEvents.ScenarioUnitTiersChanged(tCopy);
	end
end

-- UpdateMostAdvancedUnits should be called before this update
function UpdateMilitary(iPlayer)
	CheckHasPlayerData(iPlayer, "Military");
	local pPlayer = Players[iPlayer];
	if (pPlayer and pPlayer:IsAlive()) then
		local iAirshipUnitClass = ktUnitTiers["Airship"][gtMostAdvancedUnitTier["Airship"]].UnitClass;
		local iLandshipUnitClass = ktUnitTiers["Landship"][gtMostAdvancedUnitTier["Landship"]].UnitClass;
		local iValue = pPlayer:GetUnitClassCount(iAirshipUnitClass) + pPlayer:GetUnitClassCount(iLandshipUnitClass);
		
		gtPlayerStatus[iPlayer].Military.Value = iValue;
		if (iValue >= gtTokenLeaderValues.Military) then
			gtTokenLeaderValues.Military = iValue;
		end
	else
		gtPlayerStatus[iPlayer].Military.Value = ktTokens.Military.DefaultValue;
	end
end

function UpdateCulture(iPlayer)
	CheckHasPlayerData(iPlayer, "Culture");
	local pPlayer = Players[iPlayer];
	if (pPlayer and pPlayer:IsAlive()) then
		local iValue = Players[iPlayer]:GetNumPolicies();
		gtPlayerStatus[iPlayer].Culture.Value = iValue;
		if (iValue >= gtTokenLeaderValues.Culture) then
			gtTokenLeaderValues.Culture = iValue;
		end
	else
		gtPlayerStatus[iPlayer].Culture.Value = ktTokens.Culture.DefaultValue;
	end
end

function UpdateIndustry(iPlayer)
	CheckHasPlayerData(iPlayer, "Industry");
	local pPlayer = Players[iPlayer];
	if (pPlayer and pPlayer:IsAlive()) then
		local iValue = ktTokens.Industry.DefaultValue;
		local iCityID = GetMostProductiveCityForPlayer(iPlayer);
		local pPlayer = Players[iPlayer];
		if (iCityID ~= nil) then
			if (pPlayer ~= nil) then
				local pCity = pPlayer:GetCityByID(iCityID);
				if (pCity ~= nil) then
					iValue = pCity:GetRawProductionDifference(true, false);
				else
					print("Scripting error - pCity is nil when updating Industry for Player " .. iPlayer);
				end
			else
				print("Scripting error - pPlayer is nil when updating Industry for Player " .. iPlayer);
			end
		end
		
		gtPlayerStatus[iPlayer].Industry.Value = iValue;
		if (iValue >= gtTokenLeaderValues.Industry) then
			gtTokenLeaderValues.Industry = iValue;
		end
	else
		gtPlayerStatus[iPlayer].Industry.Value = ktTokens.Industry.DefaultValue;
	end
end

function UpdateCommerce(iPlayer)
	CheckHasPlayerData(iPlayer, "Commerce");
	local pPlayer = Players[iPlayer];
	if (pPlayer and pPlayer:IsAlive()) then
		local iValue = Players[iPlayer]:GetLifetimeGrossGold();
		gtPlayerStatus[iPlayer].Commerce.Value = iValue;
		if (iValue >= gtTokenLeaderValues.Commerce) then
			gtTokenLeaderValues.Commerce = iValue;
		end
	else
		gtPlayerStatus[iPlayer].Commerce.Value = ktTokens.Commerce.DefaultValue;
	end
end

function UpdateLabor(iPlayer)
	CheckHasPlayerData(iPlayer, "Labor");
	local pPlayer = Players[iPlayer];
	if (pPlayer and pPlayer:IsAlive()) then
		local iValue = ktTokens.Labor.DefaultValue;
		for i, t in pairs(GetWonderPointsTable()) do
			if (Players[iPlayer]:GetBuildingClassCount(t.BuildingClass) > 0) then
				iValue = iValue + t.Value;
			end
		end
		gtPlayerStatus[iPlayer].Labor.Value = iValue;
		if (iValue >= gtTokenLeaderValues.Labor) then
			gtTokenLeaderValues.Labor = iValue;
		end
	else
		gtPlayerStatus[iPlayer].Labor.Value = ktTokens.Labor.DefaultValue;
	end
end

function UpdateTokenOwnership(sToken)
	local iGameTurn = Game.GetGameTurn();
	
	-- If this token is just now available, there are extra considerations
	local bFirstTime = CheckTokenJustUnlocked(sToken);
	
	if (IsTokenUnlocked(sToken, iGameTurn)) then
		-- Who is the old owner?
		local iOldOwner = -1;
		for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
			CheckHasPlayerData(iPlayer, sToken);
			if (gtPlayerStatus[iPlayer][sToken].Owned) then
				iOldOwner = iPlayer;
				break;
			end
		end
		
		-- Calculations for new owner
		local iLeaderValue = gtTokenLeaderValues[sToken];
		local iNumLeaders = 0;
		for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
			-- Must be alive!
			local pPlayer = Players[iPlayer];
			if (pPlayer and pPlayer:IsAlive()) then
				local iPlayerValue = gtPlayerStatus[iPlayer][sToken].Value;
				
				-- Are we in the lead?
				if (iPlayerValue == iLeaderValue) then
					gtPlayerStatus[iPlayer][sToken].Owned = true;
					if (bFirstTime) then
						gtPlayerStatus[iPlayer][sToken].OwnedWholeGame = true;
					end
					iNumLeaders = iNumLeaders + 1;
				else
					gtPlayerStatus[iPlayer][sToken].Owned = false;
					if (gtPlayerStatus[iPlayer][sToken].OwnedWholeGame) then
						gtPlayerStatus[iPlayer][sToken].OwnedWholeGame = false;
					end
				end
			else
				gtPlayerStatus[iPlayer][sToken].Owned = false;
				if (gtPlayerStatus[iPlayer][sToken].OwnedWholeGame) then
					gtPlayerStatus[iPlayer][sToken].OwnedWholeGame = false;
				end
			end
		end
		
		-- In a tie, nobody gets the token
		if (iNumLeaders > 1) then
			for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
				gtPlayerStatus[iPlayer][sToken].Owned = false;
				if (gtPlayerStatus[iPlayer][sToken].OwnedWholeGame) then
					gtPlayerStatus[iPlayer][sToken].OwnedWholeGame = false;
				end
			end
		elseif (iNumLeaders <= 0) then
			print("Scripting ERROR: A token is unlocked, but not owned by any player!");
		end
		
		-- Who is the new owner?
		local iNewOwner = -1;
		for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
			CheckHasPlayerData(iPlayer, sToken);
			if (gtPlayerStatus[iPlayer][sToken].Owned) then
				iNewOwner = iPlayer;
				break;
			end
		end
		
		-- If there is a new owner, send a notification
		if (iNewOwner ~= iOldOwner and iNewOwner ~= -1) then
			local pNewOwner = Players[iNewOwner];
			local pActivePlayer = Players[Game.GetActivePlayer()];
			if (pNewOwner ~= nil and pActivePlayer ~= nil) then
				local sTitle = ktTokens[sToken].Title;
				local sMessage = Locale.ConvertTextKey("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_NOTIF_TT", pNewOwner:GetCivilizationShortDescriptionKey(), sTitle);
				local sSummary = Locale.ConvertTextKey("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_NOTIF_SUMMARY", pNewOwner:GetCivilizationShortDescriptionKey(), sTitle);
				pActivePlayer:AddNotification(NotificationTypes.NOTIFICATION_GENERIC, sMessage, sSummary, -1, -1, iNewOwner);
			end
		end
	end
end

function UpdatePlayerStatus()
	-- Determine player values and highest values
	ResetLeaderValues(); -- Wipe these clean and recalculate; the leader value might be less than it was last turn (ex. unit tier change)
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		for s, t in pairs(ktTokens) do
			CheckHasPlayerData(iPlayer, s);
			if (ktTokenUpdateFns[s] ~= nil) then
				ktTokenUpdateFns[s](iPlayer);
			else
				print("Scripting error - invalid update function for Victory Token: " .. s);
			end
		end
	end
	
	-- Determine ownership based on above values
	for s,t in pairs(ktTokens) do
		UpdateTokenOwnership(s);
	end
	
	-- Is someone now in a position to win?
	local iMostTokens = 0;
	local iMostTokensPlayer = -1;
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		local iTokens = GetNumTokensOwned(iPlayer);
		if (iTokens > iMostTokens) then
			iMostTokens = iTokens;
			iMostTokensPlayer = iPlayer;
		end
	end
	-- Yes - someone is about to win
	if (iMostTokens >= GetTokensNeededForVictory()) then
		-- Someone new!
		if (iMostTokensPlayer ~= giPlayerAboutToWin) then
			giPlayerAboutToWin = iMostTokensPlayer;
			giTurnsControlHeld = 0;
		-- Same guy, getting closer
		else
			giTurnsControlHeld = giTurnsControlHeld + 1;
		end
	-- No - nobody has enough tokens
	else
		giPlayerAboutToWin = -1;
		giTurnsControlHeld = 0;
	end
	
	SaveSteampunkData();
	
	local tCopy = deepcopy(gtPlayerStatus);
	LuaEvents.ScenarioPlayerStatusChanged(tCopy, Game.GetGameTurn(), Game.GetGameTurnYear(), giPlayerAboutToWin, giTurnsControlHeld);
end

function ResetUnitTiers()
	local kiDefaultTier = 1;
	gtMostAdvancedUnitTier = {};
	for s,t in pairs(ktUnitTiers) do
		gtMostAdvancedUnitTier[s] = kiDefaultTier;
	end
	
	SaveSteampunkData();
	
	local tCopy = deepcopy(gtMostAdvancedUnitTier);
	LuaEvents.ScenarioUnitTiersChanged(tCopy);
end

function ResetLeaderValues()
	gtTokenLeaderValues = {};
	for s, t in pairs(ktTokens) do
		gtTokenLeaderValues[s] = t.DefaultValue;
	end
end

function ResetPlayerStatus()
	gtPlayerStatus = {};

	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		for s, t in pairs(ktTokens) do
			CheckHasPlayerData(iPlayer, s);
		end
	end
	
	SaveSteampunkData();
	
	local tCopy = deepcopy(gtPlayerStatus);
	LuaEvents.ScenarioPlayerStatusChanged(tCopy, Game.GetGameTurn(), Game.GetGameTurnYear(), -1, 0);
end

-- Ensures that data table has allotted space for this player and token, creating space if needed
function CheckHasPlayerData(iPlayer, sToken)
	local bHadPlayerData = true;
	
	if (ktTokens[sToken] == nil) then
		print("Scripting error - invalid Victory Token key: " .. sToken);
		return false;
	end
	if (gtPlayerStatus == nil) then
		gtPlayerStatus = {};
	end
	if (gtPlayerStatus[iPlayer] == nil) then
		gtPlayerStatus[iPlayer] = {};
	end
	if (gtPlayerStatus[iPlayer][sToken] == nil) then
		gtPlayerStatus[iPlayer][sToken] = {
			Owned = false,
			OwnedWholeGame = false,
			Value = ktTokens[sToken].DefaultValue,
		};
		bHadPlayerData = false;
	end
	
	return bHadPlayerData;
end

-- Check if a token is now unlocked for the first time
function CheckTokenJustUnlocked(sToken)
	if (IsTokenUnlocked(sToken, Game.GetGameTurn() - 1)) then
		if (not gtTokensUnlocked[sToken]) then
			gtTokensUnlocked[sToken] = true;
			return true;
		end
	end
	
	return false;
end

-----------------------------
-- Game Event Handlers --
-----------------------------
GameEvents.PlayerDoTurn.Add(function(iPlayer)
	local iTurn = Game.GetGameTurn();
	
	-- Update on Barbarian player's turn (after all major civs take their turn) so that we are fair to all players
	if (iPlayer == 63) then
		UpdateMostAdvancedUnits();
		UpdatePlayerStatus();
	end

	return false;
end);

GameEvents.PlayerCityFounded.Add(function(iPlayer, iCityX, iCityY)
	local kCultureBonus = GetCultureFromFirstCity();
	
	-- If this is player's first city, grant them the starting Culture amount
	local pPlayer = Players[iPlayer];
	if (pPlayer ~= nil) then
		if (not pPlayer:IsMinorCiv() and pPlayer:GetNumCities() == 1) then
			pPlayer:ChangeJONSCulture(kCultureBonus);
		end
	end
end);

GameEvents.TeamTechResearched.Add(function(iTeam, iTech, iChange)
	local kCultureBonus = GetCultureFromLastTech();
	
	if (iTech == GameInfo.Technologies["TECH_THE_GRAND_IDEA"].ID) then
		for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
			if (Players[iPlayer] ~= nil) then
				if (Players[iPlayer]:GetTeam() == iTeam) then
					Players[iPlayer]:ChangeJONSCulture(kCultureBonus);
				end
			end
		end
	end
end);

-- Medium negative modifier when other player has exactly 2 Titles
GameEvents.GetScenarioDiploModifier1.Add(function(ePlayer1, ePlayer2)

	if (GetNumTokensOwned(ePlayer2) == 2) then
		return 20;
	end
	
	return 0;
end)

-- Large negative modifier when other player has more than 2 Titles (about to win)
GameEvents.GetScenarioDiploModifier2.Add(function(ePlayer1, ePlayer2)

	if (GetNumTokensOwned(ePlayer2) > 2) then
		return 70;
	end
	
	return 0;
end)

function CanAdoptPolicyBranch (iPlayerID, iPolicyBranch)
	return false;
end
GameEvents.PlayerCanAdoptPolicyBranch.Add(CanAdoptPolicyBranch);

function ReceivePlayerStatusChanged(tPlayerStatus, iTurn, iYear, iPlayerAboutToWin, iTurnsControlHeld)
	gbUpdated = false;
end
LuaEvents.ScenarioPlayerStatusChanged.Add( ReceivePlayerStatusChanged );

function ReceiveUnitTiersChanged(tUnitTiers)
	-- No changes needed
end
LuaEvents.ScenarioUnitTiersChanged.Add( ReceiveUnitTiersChanged );

-----------------------------
-- Achievements --
-----------------------------
function DoEndgameAchievements()
	for iPlayerLoop = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		for sToken,t in pairs(ktTokens) do
			CheckHasPlayerData(iPlayerLoop, sToken);
			if (gtPlayerStatus[iPlayerLoop][sToken].OwnedWholeGame) then
				if (gtPlayerStatus[iPlayerLoop][sToken].Owned) then
					UI.UnlockAchievement("ACHIEVEMENT_XP1_44");
				else
					print("Scripting ERROR: Player " .. iPlayerLoop .. " owned " .. sToken .. " the whole game, but does not own it now. Um, what?");
				end
			end
		end
	end
end

-----------------------------
-- UI Handlers --
-----------------------------
function OnBriefingButton()
    UI.AddPopup( { Type = ButtonPopupTypes.BUTTONPOPUP_TEXT,
                   Data1 = 800,
                   Option1 = true,
                   Text = "TXT_KEY_STEAMPUNK_SCENARIO_CIV5_DAWN_TEXT" } );
end
Controls.BriefingButton:RegisterCallback( Mouse.eLClick, OnBriefingButton );

function OnVictoryStatusButton()
	UIManager:QueuePopup(Controls.VictoryStatus, PopupPriority.eUtmost);
end
Controls.VictoryStatusButton:RegisterCallback(Mouse.eLClick, OnVictoryStatusButton)

function OnEnterCityScreen()
    ContextPtr:SetHide( true );
end
Events.SerialEventEnterCityScreen.Add( OnEnterCityScreen );

function OnExitCityScreen()
	if (Game:GetGameState() ~= GameplayGameStateTypes.GAMESTATE_EXTENDED) then 
    		ContextPtr:SetHide( false );
	end
end
Events.SerialEventExitCityScreen.Add( OnExitCityScreen );

-----------------------------
-- Saved Data --
-----------------------------
function SaveSteampunkData()
	
	-- giPlayerAboutToWin
	local key = "PlayerAboutToWin";
	local value = giPlayerAboutToWin;
	SetPersistentProperty(key, value);
	if (gbLogSaveData) then
		print("=====DEBUG===== Saving data. [KEY] " .. key .. " | [VALUE] " .. value);
	end
	
	-- giTurnsControlHeld
	key = "TurnsControlHeld";
	value = giTurnsControlHeld;
	SetPersistentProperty(key, value);
	if (gbLogSaveData) then
		print("=====DEBUG===== Saving data. [KEY] " .. key .. " | [VALUE] " .. value);
	end	
	
	-- gtMostAdvancedUnitTier
	for sType,i in pairs(gtMostAdvancedUnitTier) do
		local sKey = string.format("Latest_Tier_%s", sType);
		local iValue = gtMostAdvancedUnitTier[sType];
		SetPersistentProperty(sKey, iValue);
		if (gbLogSaveData) then
			print("=====DEBUG===== Saving data. [KEY] " .. sKey .. " | [VALUE] " .. iValue);
		end
	end
	
	-- gtTokensUnlocked
	for s,b in pairs(gtTokensUnlocked) do
		local sKey = string.format("Token_%s_Unlocked", s);
		local iValue = 0;
		if (gtTokensUnlocked[s]) then
			iValue = 1;
		end
		SetPersistentProperty(sKey, iValue);
		if (gbLogSaveData) then
			print("=====DEBUG===== Saving data. [KEY] " .. sKey .. " | [VALUE] " .. iValue);
		end
	end
	
	-- gtPlayerStatus
	for iPlayer,tTokensData in ipairs(gtPlayerStatus) do
		for sToken,tTokenData in pairs(tTokensData) do
			CheckHasPlayerData(iPlayer, sToken);
			local sKeyTemplate = string.format("Player%i_%s_", iPlayer, sToken);
			
			-- Owned
			local sKey = sKeyTemplate .. "Owned";
			local iValue = 0;
			if (gtPlayerStatus[iPlayer][sToken].Owned) then
				iValue = 1;
			end
			SetPersistentProperty(sKey, iValue);
			
			-- OwnedWholeGame
			sKey = sKeyTemplate .. "OwnedWholeGame";
			iValue = 0;
			if (gtPlayerStatus[iPlayer][sToken].OwnedWholeGame) then
				iValue = 1;
			end
			SetPersistentProperty(sKey, iValue);
			if (Players[iPlayer]:IsAlive() and gbLogSaveData) then
				print("=====DEBUG===== Saving data. [KEY] " .. sKey .. " | [VALUE] " .. iValue);
			end
			
			-- Value
			sKey = sKeyTemplate .. "Value";
			iValue = gtPlayerStatus[iPlayer][sToken].Value;
			SetPersistentProperty(sKey, iValue);
		end
	end
end

function LoadSteampunkData()
	
	-- giPlayerAboutToWin
	local key = "PlayerAboutToWin";
	local value = GetPersistentProperty(key);
	if (value ~= nil) then
		giPlayerAboutToWin = value;
		if (gbLogSaveData) then
			print("=====DEBUG===== Loading data. [KEY] " .. key .. " | [VALUE] " .. value);
		end
	end
	
	-- giTurnsControlHeld
	key = "TurnsControlHeld";
	value = GetPersistentProperty(key);
	if (value ~= nil) then
		giTurnsControlHeld = value;
		if (gbLogSaveData) then
			print("=====DEBUG===== Loading data. [KEY] " .. key .. " | [VALUE] " .. value);
		end
	end	
	
	-- gtMostAdvancedUnitTier
	for sType,tTiers in pairs(ktUnitTiers) do
		local sKey = string.format("Latest_Tier_%s", sType);
		local iValue = GetPersistentProperty(sKey);
		
		-- Workaround for older saves. If no tier data found, assume tier 1, and will update soon anyways
		if (iValue == nil) then
			iValue = 1;
			if (gbLogSaveData) then
				print("=====DEBUG===== Loading data. [KEY] " .. sKey .. " NOT FOUND, initializing to Tier 1");
			end
		end
		
		if (iValue ~= nil) then
			gtMostAdvancedUnitTier[sType] = iValue;
			if (gbLogSaveData) then
				print("=====DEBUG===== Loading data. [KEY] " .. sKey .. " | [VALUE] " .. iValue);
			end
		end
	end
	
	-- gtTokensUnlocked
	for s,t in pairs(ktTokens) do
		local sKey = string.format("Token_%s_Unlocked", s);
		local iValue = GetPersistentProperty(sKey);
		if (iValue ~= nil) then
			if (iValue == 1) then
				gtTokensUnlocked[s] = true;
			else
				gtTokensUnlocked[s] = false;
			end
			if (gbLogSaveData) then
				print("=====DEBUG===== Loading data. [KEY] " .. sKey .. " | [VALUE] " .. iValue);
			end
		end
	end
	
	-- gtPlayerStatus
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		for sToken,t in pairs(ktTokens) do
			CheckHasPlayerData(iPlayer, sToken);
			local sKeyTemplate = string.format("Player%i_%s_", iPlayer, sToken);
			
			-- Owned
			local sKey = sKeyTemplate .. "Owned";
			local iValue = GetPersistentProperty(sKey);
			if (iValue ~= nil) then
				if (iValue == 1) then
					gtPlayerStatus[iPlayer][sToken].Owned = true;
				else
					gtPlayerStatus[iPlayer][sToken].Owned = false;
				end
			end
			
			-- OwnedWholeGame
			sKey = sKeyTemplate .. "OwnedWholeGame";
			iValue = GetPersistentProperty(sKey);
			if (iValue ~= nil) then
				if (iValue == 1) then
					gtPlayerStatus[iPlayer][sToken].OwnedWholeGame = true;
				else
					gtPlayerStatus[iPlayer][sToken].OwnedWholeGame = false;
				end
				
				if (Players[iPlayer]:IsAlive() and gbLogSaveData) then
					print("=====DEBUG===== Loading data. [KEY] " .. sKey .. " | [VALUE] " .. iValue);
				end
			end
			
			-- Value
			sKey = sKeyTemplate .. "Value";
			iValue = GetPersistentProperty(sKey);
			if (iValue ~= nil) then
				gtPlayerStatus[iPlayer][sToken].Value = iValue;
			end
		end
	end
	
	local tPlayerStatusCopy = deepcopy(gtPlayerStatus);
	LuaEvents.ScenarioPlayerStatusChanged(tPlayerStatusCopy, Game.GetGameTurn() - 1, Game.GetGameTurnYear() - 1, giPlayerAboutToWin, giTurnsControlHeld); --antonjs: todo: save and load the turn and year
	
	local tUnitTiersCopy = deepcopy(gtMostAdvancedUnitTier);
	LuaEvents.ScenarioUnitTiersChanged(tUnitTiersCopy);
end

-----------------------------
-- Initialization --
-----------------------------
function InitUnitTiers()
	ResetUnitTiers();
end

function InitLeaderValues()
	ResetLeaderValues();
end

function InitPlayerStatus()
	ResetPlayerStatus();
end

function InitPlayerPolicies()
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		local pPlayer = Players[iPlayer];
		if (pPlayer ~= nil) then
			if (pPlayer:IsAlive()) then
				pPlayer:SetPolicyBranchUnlocked(GameInfo.PolicyBranchTypes["POLICY_BRANCH_LABOR"].ID, true);
				pPlayer:SetPolicyBranchUnlocked(GameInfo.PolicyBranchTypes["POLICY_BRANCH_CULTURE"].ID, true);
				pPlayer:SetPolicyBranchUnlocked(GameInfo.PolicyBranchTypes["POLICY_BRANCH_INDUSTRY"].ID, true);
				pPlayer:SetPolicyBranchUnlocked(GameInfo.PolicyBranchTypes["POLICY_BRANCH_COMMERCE"].ID, true);
				pPlayer:SetPolicyBranchUnlocked(GameInfo.PolicyBranchTypes["POLICY_BRANCH_MILITARY"].ID, true);
			end
		end
	end
end

function DoStartingUnits()
	-- Note: settlers and workers handled in the Eras game info in XML
	local tStartingUnits = {};
	local iNumScouts = 2;
	local iNumLandIronclads = 2;
	for i = 1, iNumScouts, 1 do
		table.insert(tStartingUnits, GameInfoTypes["UNIT_SCOUT"]);
	end
	for i = 1, iNumLandIronclads, 1 do
		table.insert(tStartingUnits, GameInfoTypes["UNIT_LAND_IRONCLAD"]);
	end
	
	for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
		local pPlayer = Players[iPlayer];
		if (pPlayer ~= nil) then
			if (pPlayer:IsAlive()) then
				local pPlot = pPlayer:GetStartingPlot();
				if (pPlot ~= nil) then
					for i, eUnitType in pairs(tStartingUnits) do
						local pUnit = pPlayer:InitUnit(eUnitType, pPlot:GetX(), pPlot:GetY());
						pUnit:JumpToNearestValidPlot();
					end
				end
			end
		end
	end
end

function Initialize()
	local iValue = GetPersistentProperty("Initialized");

	if (iValue == nil) then
		print("Script init: New game, initializing player data");
		
		Game.SetVictoryValid(GameInfo.Victories["VICTORY_TIME"].ID, false);
		Game.SetVictoryValid(GameInfo.Victories["VICTORY_SPACE_RACE"].ID, false);
		Game.SetVictoryValid(GameInfo.Victories["VICTORY_DOMINATION"].ID, false);
		Game.SetVictoryValid(GameInfo.Victories["VICTORY_CULTURAL"].ID, false);
		Game.SetVictoryValid(GameInfo.Victories["VICTORY_DIPLOMATIC"].ID, false);
		
		for s,t in pairs(ktTokens) do
			gtTokensUnlocked[s] = false;
		end
		InitUnitTiers();
		InitLeaderValues();
		InitPlayerStatus();
		InitPlayerPolicies();
		
		DoStartingUnits();
		
		SetPersistentProperty("Initialized", 1);
	elseif (iValue == 1) then
		print("Script init: Load game, loading player data");
		LoadSteampunkData();
	else
		print("Script ERROR: unexpected case in script init");
	end
end

-- Initialize
Initialize();