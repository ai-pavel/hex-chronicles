--------------------------------------------------------------
-- VictoryStatus.lua --
-- Scenario: Empires of the Smoky Skies (XP)
-- Author: Anton Strenger
-- DateCreated: 1/5/2012
--
-- Handles a custom popup screen for the scenario, which
-- gives the player information about progress towards
-- the victory tokens needed to win.
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
include( "IconSupport" );

-----------------------------
-- Globals --
-----------------------------
-- Constants --
ktTokens = GetTokensTable();
ktUnitTiers = GetUnitTiersTable();
ktTokenDisplayOrder = --antonjs: todo: make this less hacky?
{
	"Military",
	"Labor",
	"Industry",
	"Culture",
	"Commerce",
}

-- Variables --
gbUpdated = false; -- Flag for UI updating
gtTokenUI = {}; -- Accessor for UI elements in status screen
gtPlayerStatus = {}; -- via TurnsRemaining.lua
gtMostAdvancedUnitTier = {}; -- via TurnsRemaining.lua

giPlayerAboutToWin = -1; -- via TurnsRemaining.lua
giTurnsControlHeld = 0; -- via TurnsRemaining.lua

giTurnUpdated = 0;
giYearUpdated = 1799;

-----------------------------
-- Game Event Handlers --
-----------------------------
function ReceivePlayerStatusChanged(tPlayerStatus, iTurn, iYear, iPlayerAboutToWin, iTurnsControlHeld)
	gbUpdated = false;
	gtPlayerStatus = tPlayerStatus;
	giTurnUpdated = iTurn;
	giYearUpdated = iYear;
	giPlayerAboutToWin = iPlayerAboutToWin;
	giTurnsControlHeld = iTurnsControlHeld;
end
LuaEvents.ScenarioPlayerStatusChanged.Add( ReceivePlayerStatusChanged );

function ReceiveUnitTiersChanged(tUnitTiers)
	gtMostAdvancedUnitTier = tUnitTiers;
end
LuaEvents.ScenarioUnitTiersChanged.Add( ReceiveUnitTiersChanged );

-----------------------------
-- UI Handlers --
-----------------------------
ContextPtr:SetUpdate(function()
	if (not gbUpdated) then
		local iActivePlayer = Game:GetActivePlayer();

		local iTokensNeededForVictory = GetTokensNeededForVictory();
		local sHelpText = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_HELP", iTokensNeededForVictory, GetTurnsMustHoldForVictory());
		sHelpText = sHelpText .. "[NEWLINE][NEWLINE]";
		if (not IsVictoryPossible(giYearUpdated)) then
			sHelpText = sHelpText .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_LOCKED") .. "  ";
		elseif (giPlayerAboutToWin ~= -1) then
			local iTurnsUntilWin = GetTurnsMustHoldForVictory() - giTurnsControlHeld;
			if (iTurnsUntilWin < 0) then
				iTurnsUntilWin = 0;
			end
			local sCivAboutToWinKey = Players[giPlayerAboutToWin]:GetCivilizationShortDescriptionKey();
			local sCountdownText = Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_COUNTDOWN", iTurnsUntilWin, sCivAboutToWinKey) .. "  ";
			if (giPlayerAboutToWin == iActivePlayer) then
				sCountdownText = "[COLOR_POSITIVE_TEXT]" .. sCountdownText .. "[ENDCOLOR]";
			else
				sCountdownText = "[COLOR_WARNING_TEXT]" .. sCountdownText .. "[ENDCOLOR]";
			end
			sHelpText = sHelpText .. sCountdownText;
		end
		sHelpText = sHelpText .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_POSSIBLE", giYearUpdated); --antonjs: todo: separate line, general UI stuff
		Controls.HelpLabel:SetText(sHelpText);

		for s,t in pairs(ktTokens) do
			local bUnlocked = IsTokenUnlocked(s, giTurnUpdated);
			
			gtTokenUI[s].TitleLabel:SetText(t.Title .. "  ");
			gtTokenUI[s].PortraitFrame:SetHide(true);
			
			local sLabelText = "[ICON_LOCKED]  ";
			if (bUnlocked) then
				sLabelText = "[ICON_BULLET]  ";
			end
			sLabelText = sLabelText .. t.Help .. "[NEWLINE]      ";
			local iNumInList = 0;
			for iPlayer = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
				if (Players[iPlayer]:IsAlive()) then
					if (iNumInList ~= 0) then
						sLabelText = sLabelText .. ", ";
					end
					iNumInList = iNumInList + 1;
					
					local sCivDesc = Locale.Lookup(Players[iPlayer]:GetCivilizationShortDescriptionKey());
					if (iPlayer == iActivePlayer) then
						sCivDesc = Locale.Lookup("TXT_KEY_YOU");
					end
					sCivDesc = sCivDesc .. ": " .. gtPlayerStatus[iPlayer][s].Value;
					if (gtPlayerStatus[iPlayer][s].Owned) then
						sCivDesc = "[COLOR_POSITIVE_TEXT]" .. sCivDesc .. "[ENDCOLOR]";
						local pPlayer = Players[iPlayer];
						if (pPlayer ~= nil) then
							local tLeader = GameInfo.Leaders[pPlayer:GetLeaderType()];
							IconHookup( tLeader.PortraitIndex, 64, tLeader.IconAtlas, gtTokenUI[s].Portrait );
							gtTokenUI[s].PortraitFrame:SetHide(false);
						else
							print("SCRIPTING ERROR: Got nil when looking for player that owns a Title");
						end
						
					end
					sLabelText = sLabelText .. sCivDesc;
				end
			end
			local sLabelTT = GetTokenTooltip(s, iActivePlayer);
			gtTokenUI[s].TokenLabel:SetText(sLabelText);
			gtTokenUI[s].TokenLabel:SetToolTipString(sLabelTT);
		end
		
		gbUpdated = true;
	end
end);

function GetTokenTooltip(sToken, iForPlayer)
	local s = "";
	
	-- Unlock info
	if (not IsTokenUnlocked(sToken, giTurnUpdated)) then
		local iUnlockTech = ktTokens[sToken].UnlockTech;
		if (not IsTechResearchedByAnyone(iUnlockTech)) then
			s = s .. "[COLOR_WARNING_TEXT]" .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_TECH_UNLOCK", GameInfo.Technologies[iUnlockTech].Description) .. "[ENDCOLOR]";
			s = s .. "[NEWLINE][NEWLINE]";
		end
		--[[ antonjs: Disabled, since not in use
		local iUnlockTurn = ktTokens[sToken].UnlockTurn;
		if (iUnlockTurn > giTurnUpdated and iUnlockTurn > 0) then
			s = s .. "[COLOR_WARNING_TEXT]" .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_TURN_UNLOCK", iUnlockTurn) .. "[ENDCOLOR]";
			s = s .. "[NEWLINE][NEWLINE]";
		end
		--]]
	end
	
	-- Token info
	if (sToken == "Military") then
		local iLandshipClass = ktUnitTiers["Landship"][gtMostAdvancedUnitTier["Landship"]].UnitClass;
		local iAirshipClass = ktUnitTiers["Airship"][gtMostAdvancedUnitTier["Airship"]].UnitClass;
		s = s .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_MILITARY_TT", GameInfo.UnitClasses[iLandshipClass].Description, GameInfo.UnitClasses[iAirshipClass].Description);
	elseif (sToken == "Culture") then
		s = s .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_CULTURE_TT");
	elseif (sToken == "Industry") then
		local iYourBestCityID = GetMostProductiveCityForPlayer(iForPlayer);
		local sYourBestCity = Locale.Lookup("TXT_KEY_MISC_UNKNOWN");
		local pForPlayer = Players[iForPlayer];
		if (pForPlayer ~= nil) then
			local pYourBestCity = pForPlayer:GetCityByID(iYourBestCityID);
			if (pYourBestCity ~= nil) then
				sYourBestCity = pYourBestCity:GetName();
			end
		end
		
		local iWorldBestProd = -1;
		local sWorldBestCity = Locale.Lookup("TXT_KEY_MISC_UNKNOWN");
		local bTieForLead = false;
		
		for iPlayerLoop = 0, GameDefines.MAX_MAJOR_CIVS - 1, 1 do
			if (Players[iPlayerLoop]:IsAlive()) then
				local iBestCityID = GetMostProductiveCityForPlayer(iPlayerLoop);
				local pCity = Players[iPlayerLoop]:GetCityByID(iBestCityID);
				if (pCity ~= nil) then
					local iProd = pCity:GetCurrentProductionDifference(false, false);
					if (iProd > iWorldBestProd) then
						bTieForLead = false; -- This city is strictly better than the ones we've seen
						iWorldBestProd = iProd;
						sWorldBestCity = pCity:GetName();
					elseif (iProd == iWorldBestProd) then
						bTieForLead = true; -- This city is tied with one we've seen, so don't show any city name in the tooltip
						sWorldBestCity = Locale.Lookup("TXT_KEY_MISC_UNKNOWN");
					end	
				end
			end
		end
		
		s = s .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_INDUSTRY_TT", sWorldBestCity, sYourBestCity);
	elseif (sToken == "Commerce") then
		s = s .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_COMMERCE_TT");
	elseif (sToken == "Labor") then
		s = s .. Locale.Lookup("TXT_KEY_STEAMPUNK_SCENARIO_VICTORY_CATEGORY_LABOR_TT");
	else
		print("Scripting error: Attempting to get tooltip for an unknown victory token (" .. sToken .. ")");
	end
	
	return s;
end

function OnClose()
    UIManager:DequeuePopup(ContextPtr);
end
Controls.CloseStatusButton:RegisterCallback(Mouse.eLClick, OnClose);

ContextPtr:SetInputHandler(function(uiMsg, wParam, lParam)
    if(uiMsg == KeyEvents.KeyDown) then
		if (wParam == Keys.VK_ESCAPE or wParam == Keys.VK_RETURN) then
			OnClose();
			return true;
		end
    end
end);

-----------------------------
-- Initialization --
-----------------------------
function BuildLayout()
	local iActivePlayer = Game:GetActivePlayer();
	CivIconHookup(iActivePlayer, 64, Controls.CivIcon, Controls.CivIconBG, Controls.CivIconShadow, false, true);
	for i,s in ipairs(ktTokenDisplayOrder) do
		local t = ktTokens[s];
		gtTokenUI[s] = BuildTokenInstance(Controls.TokenStack, t);
	end
end

function BuildTokenInstance(cStack, tToken)
	local t = {};
	ContextPtr:BuildInstanceForControl("TokenInstance", t, cStack);
	t.TokenLabel:LocalizeAndSetText("[ICON_BULLET]" .. tToken.Title .. " (" .. tToken.Name .. ")");
	return t;
end

-- Initialize
BuildLayout();