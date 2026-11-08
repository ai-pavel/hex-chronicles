----------------------------------------------------------------
-- Spain 1936 scenario load screen
-- Modelled on Firaxis' scenario load screens (Korea / Civil War):
-- picks the scenario map, locks the civ list to the six sides,
-- lets the player choose a side and a difficulty, and starts the game.
----------------------------------------------------------------
include( "IconSupport" );
include( "UniqueBonuses" );

ksModID = "8c4f2a61-1936-4e0b-9d57-3a7e1b5c9f24";
ksMapFile = "Spain1936.Civ5Map";

-- index = player slot in the scenario map
ktScenario = {
	[0] = { Civ = "CIVILIZATION_RUSSIA", Name = "Spanish Republic", Leader = "Manuel Azana",
		Blurb = "25 July 1936. The rising of 17-18 July has failed in Madrid, Barcelona, Valencia and the industrial north, and the Republic keeps the capital, the gold reserve, most of the fleet and the air force. But the army has dissolved, and the streets belong to the militias of the parties and the unions.[NEWLINE][NEWLINE]Hold the Guadarrama passes and the road from the south, turn the militias into an army, and make the anarchists, the Catalans and the Basques fight one war together. Help will come from Moscow; it will not come from Paris or London." },
	[1] = { Civ = "CIVILIZATION_ZULU", Name = "Nationalists", Leader = "Francisco Franco",
		Blurb = "The best troops in Spain, the Legion and the Moroccan Regulares, are on the wrong side of the Strait, and the Republican fleet is between them and Andalusia. Queipo de Llano holds Seville, Cadiz and Cordoba with a handful of soldiers; German and Italian transports are on their way.[NEWLINE][NEWLINE]Bring the Army of Africa across, march north through Extremadura to join Mola, relieve the Alcazar of Toledo and take Madrid before the Republic has an army." },
	[2] = { Civ = "CIVILIZATION_GERMANY", Name = "Army of the North", Leader = "Emilio Mola",
		Blurb = "The Director of the conspiracy holds Old Castile, Leon, Galicia, Navarre and western Aragon, with the requetes of Navarre as his best troops. His columns are stopped in the Guadarrama passes, short of ammunition, sixty kilometres from Madrid.[NEWLINE][NEWLINE]Hold the Aragon front against the Catalan columns, take San Sebastian and the border at Irun to cut the north off from France, and then turn on Bilbao, Santander and Asturias." },
	[3] = { Civ = "CIVILIZATION_SHOSHONE", Name = "Catalonia", Leader = "Lluis Companys",
		Blurb = "In Barcelona the rising was crushed in two days by the Assault Guards, the Guardia Civil and the workers of the CNT. The Generalitat governs, but the Central Committee of Antifascist Militias rules the streets, and the columns are already marching on Zaragoza and Huesca.[NEWLINE][NEWLINE]Build a war industry out of the factories of Barcelona, take Mallorca back if you can, and keep Catalonia in one piece between Valencia, the anarchists and the front." },
	[4] = { Civ = "CIVILIZATION_ETHIOPIA", Name = "Basque Country", Leader = "Jose Antonio Aguirre",
		Blurb = "Biscay and Gipuzkoa have stayed with the Republic; Alava and Navarre have gone with Mola. The Basque Nationalists, Catholic and conservative, have sided with the Republic that promised them their statute.[NEWLINE][NEWLINE]Hold San Sebastian and the border at Irun as long as you can, build an army of Basque battalions and the Iron Ring around Bilbao, and keep the iron mines and the shipyards working. The north is cut off from the rest of the Republic." },
	[5] = { Civ = "CIVILIZATION_AZTEC", Name = "CNT-FAI", Leader = "Buenaventura Durruti",
		Blurb = "The columns of the anarchist unions left Barcelona for Aragon a few days after the rising: the Durruti column for Zaragoza, the Ascaso and Ortiz columns for Huesca and Caspe. Behind them the villages collectivise their land.[NEWLINE][NEWLINE]Take Zaragoza if you can, hold the Aragon front, and keep the revolution alive while the Republic and the Generalitat rebuild a state around you. Your allies need you, and fear you." },
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
	PreGame.SetGameSpeed(GameInfo.GameSpeeds["GAMESPEED_QUICK"].ID);

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
				controlTable.Description:SetText( entry.Name );

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
				controlTable.Title:SetText( string.format("%s - %s (%s)", entry.Leader, entry.Name, Locale.ConvertTextKey(trait.ShortDescription)) );
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
		Controls.Title:SetText( string.format("%s - %s (%s)", entry.Leader, entry.Name, Locale.ConvertTextKey(trait.ShortDescription)) );
		PopulateUniqueBonuses( Controls, civ, leader );
		Controls.Quote:SetText( entry.Blurb );
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
		Controls.Quote:SetText( "Spain, 25 July 1936, one week after the rising. The Republic, Catalonia, the Basque Country and the anarchist columns against Franco's Army of Africa and Mola's Army of the North, with Portugal, Gibraltar, Tangier, Andorra, France and French North Africa as city-states and fugitives in the sierras. One turn is one week. Only domination ends the war." );
	end
	Controls.MainStack:CalculateSize();
	Controls.MainStack:ReprocessAnchoring();
	Controls.DoMScrollPanel:CalculateInternalSize();
end

Initialize();
