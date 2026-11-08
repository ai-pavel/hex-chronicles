----------------------------------------------------------------
-- Hawaii 1778 scenario load screen
-- Modelled on Firaxis' scenario load screens: picks the scenario map,
-- locks the civ list to the five chiefdoms, lets the player
-- choose a chiefdom and a difficulty, and starts the game.
----------------------------------------------------------------
include( "IconSupport" );
include( "UniqueBonuses" );

ksModID = "e7b3d1a5-1778-4c2e-9f40-8a6b2c5d7e91";
ksMapFile = "Hawaii1778.Civ5Map";

-- index = player slot in the scenario map; names and blurbs come from the mod's text file (EN + RU)
ktScenario = {
	[0] = { Civ = "CIVILIZATION_POLYNESIA", Key = "KONA" },
	[1] = { Civ = "CIVILIZATION_JAPAN", Key = "HILO" },
	[2] = { Civ = "CIVILIZATION_ZULU", Key = "MAUI" },
	[3] = { Civ = "CIVILIZATION_CARTHAGE", Key = "OAHU" },
	[4] = { Civ = "CIVILIZATION_ETHIOPIA", Key = "KAUAI" },
}

g_CurrentPlayerIndex = nil; -- nil = random

----------------------------------------------------------------
function OnBack()
	if(not Controls.SelectCivScrollPanel:IsHidden()) then
		ToggleCivSelection();
	else
		UIManager:DequeuePopup( ContextPtr );
	end
end
Controls.BackButton:RegisterCallback(Mouse.eLClick, OnBack);

ContextPtr:SetInputHandler( function(uiMsg, wParam, lParam)
	if uiMsg == KeyEvents.KeyDown then
		if wParam == Keys.VK_ESCAPE or wParam == Keys.VK_RETURN then
			OnBack();
		end
	end
	return true;
end);

----------------------------------------------------------------
Controls.StartButton:RegisterCallback(Mouse.eLClick, function()
	PreGame.Reset();

	local iModVersion = Modding.GetActivatedModVersion(ksModID);
	local scenarioMap = Modding.GetEvaluatedFilePath(ksModID, iModVersion, ksMapFile);

	PreGame.SetMapScript(scenarioMap.EvaluatedPath);
	PreGame.SetLoadWBScenario(true);
	UI.ResetScenarioPlayerSlots(true);
	PreGame.SetOverrideScenarioHandicap(true);
	PreGame.SetHandicap(0, g_CurrentDifficulty);
	PreGame.SetGameSpeed(GameInfo.GameSpeeds["GAMESPEED_QUICK"].ID); -- Quick for play testing, Standard is the intended pace
	PreGame.SetEra(GameInfo.Eras["ERA_ANCIENT"].ID);

	local playerIndex = g_CurrentPlayerIndex;
	if(playerIndex == nil) then
		playerIndex = math.random(0, table.count(ktScenario) - 1);
	end
	UI.MoveScenarioPlayerToSlot( playerIndex, 0 );

	Events.SerialEventStartGame();
	UIManager:SetUICursor( 1 );
end);

----------------------------------------------------------------
function DifficultySelected(button, difficulty)
	g_CurrentDifficulty = difficulty;
	g_CurrentDifficultyButton.SelectionAnim:SetHide(true);
	button.SelectionAnim:SetHide(false);
	g_CurrentDifficultyButton = button;
end

function LeaderOf(civ)
	return GameInfo.Leaders[GameInfo.Civilization_Leaders( "CivilizationType = '" .. civ.Type .. "'" )().LeaderheadType];
end
function TraitOf(leader)
	return GameInfo.Traits[GameInfo.Leader_Traits("LeaderType ='" .. leader.Type .. "'")().TraitType];
end
function TitleOf(civ, leader, trait)
	return string.format("%s - %s (%s)", Locale.ConvertTextKey(leader.Description), Locale.ConvertTextKey(civ.ShortDescription), Locale.ConvertTextKey(trait.ShortDescription));
end

function Initialize()
	local defaultDifficulty = GameInfo.HandicapInfos["HANDICAP_PRINCE"] or GameInfo.HandicapInfos()();
	g_CurrentDifficulty = defaultDifficulty.ID;

	for info in GameInfo.HandicapInfos("Type <> 'HANDICAP_AI_DEFAULT'") do
		local controlTable = {};
		ContextPtr:BuildInstanceForControl( "ItemInstance", controlTable, Controls.DifficultyStack );
		if(info.ID == g_CurrentDifficulty) then
			g_CurrentDifficultyButton = controlTable;
			controlTable.SelectionAnim:SetHide(false);
		end
		IconHookup( info.PortraitIndex, 64, info.IconAtlas, controlTable.Icon );
		controlTable.Help:LocalizeAndSetText(info.Help);
		controlTable.Name:LocalizeAndSetText(info.Description);
		controlTable.Button:SetToolTipString(Locale.ConvertTextKey( info.Help ) );
		controlTable.Button:RegisterCallback(Mouse.eLClick, function() DifficultySelected(controlTable, info.ID); end);
	end

	Controls.CivilizationButton:RegisterCallback(Mouse.eLClick, function() ToggleCivSelection() end);
	Controls.DifficultyStack:CalculateSize();
	Controls.DifficultyStack:ReprocessAnchoring();
	Controls.DifficultyScrollPanel:CalculateInternalSize();

	BuildCivSelectList();
	SetPlayerIndex(g_CurrentPlayerIndex);
end

function ToggleCivSelection()
	if(not Controls.SelectCivScrollPanel:IsHidden()) then
		Controls.SelectCivScrollPanel:SetHide(true);
		Controls.DifficultySelectionBox:SetHide(false);
		Controls.DoMBox:SetHide(false);
		Controls.StartButton:SetHide(false);
	else
		BuildCivSelectList();
		Controls.SelectCivScrollPanel:SetHide(false);
		Controls.DifficultySelectionBox:SetHide(true);
		Controls.DoMBox:SetHide(true);
		Controls.StartButton:SetHide(true);
	end
end

function BuildCivSelectList()
	Controls.SelectCivStack:DestroyAllChildren();

	if(g_CurrentPlayerIndex ~= nil) then
		local controlTable = {};
		ContextPtr:BuildInstanceForControl( "SelectCivInstance", controlTable, Controls.SelectCivStack );
		controlTable.Button:SetVoid1( -1 );
		controlTable.Button:RegisterCallback( Mouse.eLClick, function() SetPlayerIndex(nil); ToggleCivSelection(); end );
		controlTable.Title:LocalizeAndSetText("TXT_KEY_RANDOM_LEADER");
		controlTable.Description:LocalizeAndSetText("TXT_KEY_RANDOM_LEADER_HELP");
		IconHookup( 22, 128, "LEADER_ATLAS", controlTable.Portrait );
		if(questionOffset ~= nil) then
			controlTable.Icon:SetTexture( questionTextureSheet );
			controlTable.Icon:SetTextureOffset( questionOffset );
			controlTable.IconShadow:SetTexture( questionTextureSheet );
			controlTable.IconShadow:SetTextureOffset( questionOffset );
		end
		controlTable.BonusDescription:SetText( "" );
		for buttonNum = 1, 2 do
			controlTable["B"..buttonNum]:SetTexture( questionTextureSheet );
			controlTable["B"..buttonNum]:SetTextureOffset( questionOffset );
			controlTable["B"..buttonNum]:SetToolTipString( unknownString );
			controlTable["B"..buttonNum]:SetHide(false);
			controlTable["BF"..buttonNum]:SetHide(false);
		end
	end

	for playerIndex, entry in pairs(ktScenario) do
		if(playerIndex ~= g_CurrentPlayerIndex) then
			local civ = GameInfo.Civilizations[entry.Civ];
			if(civ ~= nil) then
				local leader = LeaderOf(civ);
				local trait = TraitOf(leader);
				local colorSet = GameInfo.PlayerColors[civ.DefaultPlayerColor];
				local primaryColor = GameInfo.Colors[colorSet.PrimaryColor];
				local secondaryColor = GameInfo.Colors[colorSet.SecondaryColor];

				local controlTable = {};
				ContextPtr:BuildInstanceForControl( "SelectCivInstance", controlTable, Controls.SelectCivStack );
				controlTable.Button:SetVoid1( civ.ID );
				controlTable.Button:RegisterCallback( Mouse.eLClick, function() SetPlayerIndex(playerIndex); ToggleCivSelection(); end);
				controlTable.Description:LocalizeAndSetText( civ.ShortDescription );

				IconHookup( leader.PortraitIndex, 128, leader.IconAtlas, controlTable.Portrait );
				local textureOffset, textureAtlas = IconLookup( civ.PortraitIndex, 64, civ.IconAtlas );
				if textureOffset ~= nil then
					controlTable.Icon:SetTexture( textureAtlas );
					controlTable.Icon:SetTextureOffset( textureOffset );
					controlTable.IconShadow:SetTexture( textureAtlas );
					controlTable.IconShadow:SetTextureOffset( textureOffset );
				end
				controlTable.Icon:SetColor( Vector4( primaryColor.Red, primaryColor.Green, primaryColor.Blue, primaryColor.Alpha ) );
				controlTable.TeamColor:SetColor( Vector4( secondaryColor.Red, secondaryColor.Green, secondaryColor.Blue, secondaryColor.Alpha ) );
				controlTable.BonusDescription:SetText( Locale.ConvertTextKey( trait.Description ) );
				controlTable.Title:SetText( TitleOf(civ, leader, trait) );
				PopulateUniqueBonuses( controlTable, civ, leader );
			end
		end
	end

	Controls.SelectCivStack:CalculateSize();
	Controls.SelectCivStack:ReprocessAnchoring();
	Controls.SelectCivScrollPanel:CalculateInternalSize();
end

function SetPlayerIndex(playerIndex)
	g_CurrentPlayerIndex = playerIndex;
	if(playerIndex ~= nil) then
		local entry = ktScenario[playerIndex];
		local civ = GameInfo.Civilizations[entry.Civ];
		local leader = LeaderOf(civ);
		local trait = TraitOf(leader);
		IconHookup( leader.PortraitIndex, 128, leader.IconAtlas, Controls.Portrait );
		IconHookup( civ.PortraitIndex, 64, civ.IconAtlas, Controls.IconShadow );
		Controls.BonusDescription:LocalizeAndSetText(trait.Description);
		Controls.Title:SetText( TitleOf(civ, leader, trait) );
		PopulateUniqueBonuses( Controls, civ, leader );
		Controls.Quote:LocalizeAndSetText( "TXT_KEY_HI1778_BLURB_" .. entry.Key );
	else
		Controls.Title:LocalizeAndSetText("TXT_KEY_RANDOM_LEADER");
		IconHookup( 22, 128, "LEADER_ATLAS", Controls.Portrait );
		if(questionOffset ~= nil) then
			Controls.IconShadow:SetTexture( questionTextureSheet );
			Controls.IconShadow:SetTextureOffset( questionOffset );
		end
		Controls.BonusDescription:SetText( "" );
		for buttonNum = 1, 2 do
			Controls["B"..buttonNum]:SetTexture( questionTextureSheet );
			Controls["B"..buttonNum]:SetTextureOffset( questionOffset );
			Controls["B"..buttonNum]:SetToolTipString( unknownString );
			Controls["B"..buttonNum]:SetHide(false);
			Controls["BF"..buttonNum]:SetHide(false);
		end
		Controls.Quote:LocalizeAndSetText( "TXT_KEY_HI1778_INTRO" );
	end
	Controls.MainStack:CalculateSize();
	Controls.MainStack:ReprocessAnchoring();
	Controls.DoMScrollPanel:CalculateInternalSize();
end

Initialize();
