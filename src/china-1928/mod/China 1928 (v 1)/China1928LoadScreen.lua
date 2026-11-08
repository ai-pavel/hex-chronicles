----------------------------------------------------------------
-- China 1928 scenario load screen
-- Modelled on Firaxis' scenario load screens (Korea / Civil War):
-- picks the scenario map, locks the civ list to the six sides,
-- lets the player choose a side and a difficulty, and starts the game.
----------------------------------------------------------------
include( "IconSupport" );
include( "UniqueBonuses" );

ksModID = "3b7d9e42-1928-4a6c-8f15-c2e0d4b7a913";
ksMapFile = "China1928.Civ5Map";

-- index = player slot in the scenario map
ktScenario = {
	[0] = { Civ = "CIVILIZATION_CHINA", Name = "National Government", Leader = "Chiang Kai-shek",
		Blurb = "10 October 1928. The Northern Expedition is over, Beijing has become Beiping, and today you take office as Chairman of the National Government in Nanjing. You hold the Yangtze delta, Shanghai's customs and banks, and the best-trained divisions in China. But the country is united only on paper: Feng Yuxiang, Yan Xishan, the Guangxi clique and the young Zhang Xueliang command their own armies and their own provinces.[NEWLINE][NEWLINE]Reduce the armies of the others before they combine against you, root out the Communists in the hills of Jiangxi, and keep the Japanese from finding a pretext." },
	[1] = { Civ = "CIVILIZATION_ZULU", Name = "Guominjun", Leader = "Feng Yuxiang",
		Blurb = "The Christian General's Northwest Army is one of the largest in China and the most disciplined, and it holds Henan, Shaanxi, Gansu and western Shandong. It is also the poorest: the northwest is starving, and Nanjing pays its own divisions first.[NEWLINE][NEWLINE]Hold the Longhai railway and the Yellow River, find allies against Chiang before he finds yours, and keep your generals loyal; Nanjing's silver can buy them." },
	[2] = { Civ = "CIVILIZATION_RUSSIA", Name = "Shanxi", Leader = "Yan Xishan",
		Blurb = "The Model Governor has ruled Shanxi since 1911, and his troops entered Beiping in June. You hold the mountain fortress of Shanxi with its coal and its arsenal, and now the old capital, Tianjin and the Hebei plain as well.[NEWLINE][NEWLINE]Keep what the Northern Expedition gave you, choose your moment against Nanjing with care, and never leave Taiyuan undefended: the passes are your best friends." },
	[3] = { Civ = "CIVILIZATION_GERMANY", Name = "Fengtian", Leader = "Zhang Xueliang",
		Blurb = "In June the Japanese blew up your father's train at Huanggutun. At twenty-seven you inherit the richest provinces of China, the Mukden Arsenal, an air force and a quarter of a million men, between the Kwantung Army in the south and the Soviets on the Chinese Eastern Railway in the north.[NEWLINE][NEWLINE]Decide whether to raise Nanjing's flag over Manchuria, keep the old generals in line, and stay strong enough that Tokyo thinks twice." },
	[4] = { Civ = "CIVILIZATION_ETHIOPIA", Name = "Guangxi", Leader = "Li Zongren",
		Blurb = "The New Guangxi clique of Li Zongren, Bai Chongxi and Huang Shaohong fought from Guangxi to Beiping in the Northern Expedition. Its armies hold Wuhan and Hubei, and Bai's troops are still in eastern Hebei; at home, Guangxi is poor, mountainous and fiercely loyal.[NEWLINE][NEWLINE]Hold Wuhan if you can, guard the road home through Hunan, and remember that your strength is your soldiers and your hills." },
	[5] = { Civ = "CIVILIZATION_SHOSHONE", Name = "Chinese Communists", Leader = "Mao Zedong",
		Blurb = "A year after the Kuomintang turned on its Communist allies, Mao Zedong and Zhu De hold out in the Jinggang mountains on the Hunan-Jiangxi border with a few thousand men, and other bands survive around the Hong Lake, in the Dabie mountains and in northeastern Jiangxi.[NEWLINE][NEWLINE]Survive. Build base areas in the hills, win the villages with land reform, and fight only when you can win. If the bases fall, the army must live on: a side that loses its last city fights on while it has units." },
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
		Controls.Quote:SetText( "China, 10 October 1928. Chiang Kai-shek's National Government at Nanjing, Feng Yuxiang's Guominjun, Yan Xishan's Shanxi, Zhang Xueliang's Fengtian clique, the Guangxi clique and the Communists, with Japan, the Soviet Union, Mongolia, the provincial militarists and the colonies as city-states and bandits in the hills. One turn is one week. Only domination ends the war." );
	end
	Controls.MainStack:CalculateSize();
	Controls.MainStack:ReprocessAnchoring();
	Controls.DoMScrollPanel:CalculateInternalSize();
end

Initialize();
