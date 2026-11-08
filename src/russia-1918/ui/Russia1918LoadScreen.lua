----------------------------------------------------------------
-- Russia 1918 scenario load screen
-- Modelled on Firaxis' scenario load screens (Korea / Civil War):
-- picks the scenario map, locks the civ list to the five factions,
-- lets the player choose a side and a difficulty, and starts the game.
----------------------------------------------------------------
include( "IconSupport" );
include( "UniqueBonuses" );

ksModID = "5e2a9d1c-1918-4c7b-8a3f-9d4b6e0c2f17";
ksMapFile = "Russia1918.Civ5Map";

-- index = player slot in the scenario map
ktScenario = {
	[0] = { Civ = "CIVILIZATION_RUSSIA", Name = "Russian SFSR", Leader = "Vladimir Lenin",
		Blurb = "1 June 1918. The revolution holds Moscow, Petrograd and the heart of the country, and nothing else is certain: the Czechoslovak Legion has seized the Trans-Siberian, the Don has risen, the Germans sit in Kiev and the Allies are landing in the north.[NEWLINE][NEWLINE]You have the railways, the factories and the manpower of central Russia. Hold the Volga, build the Red Army from the Red Guards, and strike the Whites one front at a time before they can join hands." },
	[1] = { Civ = "CIVILIZATION_GERMANY", Name = "White South", Leader = "Anton Denikin",
		Blurb = "The Volunteer Army is nine thousand officers and cadets in the Don steppe; Krasnov's Cossacks hold Novocherkassk and Rostov. Kuban is Red, Tsaritsyn is Red, and between you and Siberia lies the whole Volga.[NEWLINE][NEWLINE]Take Ekaterinodar and the Kuban, win the Cossacks, open the Black Sea ports to British tanks, and march on Moscow before the Reds learn to fight." },
	[2] = { Civ = "CIVILIZATION_SHOSHONE", Name = "Siberia", Leader = "Alexander Kolchak",
		Blurb = "From Samara to Irkutsk the Czechoslovak Legion has thrown out the Soviets along the Trans-Siberian in a fortnight. Komuch sits in Samara, the Siberian Government in Omsk, the Orenburg and Ural Cossacks guard the steppe.[NEWLINE][NEWLINE]Your land is endless and empty, your army is a railway and a few regiments. Take the Volga crossings, link up with the Don, and bring the Supreme Ruler to Moscow." },
	[3] = { Civ = "CIVILIZATION_ENGLAND", Name = "Northern Region", Leader = "Nikolai Yudenich",
		Blurb = "Murmansk and Arkhangelsk, British battalions, American infantry and a few thousand Russians of the Slavo-British Legion, with the Royal Navy behind you and the taiga in front.[NEWLINE][NEWLINE]Push down the Dvina and the Murmansk railway towards Vologda and Petrograd, and when the Baltic states break free, raise the Northwestern Army on the Estonian border for the drive on the old capital." },
	[4] = { Civ = "CIVILIZATION_ETHIOPIA", Name = "Ukrainian State", Leader = "Pavlo Skoropadsky",
		Blurb = "The Hetman rules in Kiev under German bayonets: the richest provinces of the old empire, Odessa, Kharkov, the Donbass and Crimea, and an army that exists mostly on paper. In November the Germans will go home.[NEWLINE][NEWLINE]Build a Ukrainian army before the Reds come back, decide between the Whites and the Poles, and keep the state alive through the winter of 1919." },
	[5] = { Civ = "CIVILIZATION_POLAND", Name = "Poland", Leader = "Jozef Pilsudski",
		Blurb = "Poland does not yet exist; it will in November. Until then you have the Regency Council, the legion cadres and the certainty that the German occupation is ending.[NEWLINE][NEWLINE]Raise the army, hold Lwow, take Wilno and Minsk, decide how far east the border runs, and when the Red Army turns west in 1920, hold Warsaw." },
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
		Controls.Quote:SetText( "Russia, 1 June 1918. Reds against three White fronts, a Ukraine under German occupation and a Poland about to be born, with the border states as city-states and Makhno, the Greens and the Basmachi loose in the countryside. One turn is one week. Only domination ends the war." );
	end
	Controls.MainStack:CalculateSize();
	Controls.MainStack:ReprocessAnchoring();
	Controls.DoMScrollPanel:CalculateInternalSize();
end

Initialize();
