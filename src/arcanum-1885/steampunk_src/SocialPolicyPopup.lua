--------------------------------------------------------------
-- SocialPolicyPopup.lua
-- Scenario: Empires of the Smoky Skies (XP)
-- Author: Anton Strenger
-- DateCreated: 3/22/2012
--
-- Overrides base game social policy screen for scenario.
--------------------------------------------------------------

include( "IconSupport" );
include( "InstanceManager" );
include( "TutorialPopupScreen" );

local m_PopupInfo = nil;

local g_LaborPipeManager = InstanceManager:new( "ConnectorPipe", "ConnectorImage", Controls.LaborPanel );
local g_CulturePipeManager = InstanceManager:new( "ConnectorPipe", "ConnectorImage", Controls.CulturePanel );
local g_IndustryPipeManager = InstanceManager:new( "ConnectorPipe", "ConnectorImage", Controls.IndustryPanel );
local g_CommercePipeManager = InstanceManager:new( "ConnectorPipe", "ConnectorImage", Controls.CommercePanel );
local g_MilitaryPipeManager = InstanceManager:new( "ConnectorPipe", "ConnectorImage", Controls.MilitaryPanel );

local g_LaborInstanceManager = InstanceManager:new( "PolicyButton", "PolicyIcon", Controls.LaborPanel );
local g_CultureInstanceManager = InstanceManager:new( "PolicyButton", "PolicyIcon", Controls.CulturePanel );
local g_IndustryInstanceManager = InstanceManager:new( "PolicyButton", "PolicyIcon", Controls.IndustryPanel );
local g_CommerceInstanceManager = InstanceManager:new( "PolicyButton", "PolicyIcon", Controls.CommercePanel );
local g_MilitaryInstanceManager = InstanceManager:new( "PolicyButton", "PolicyIcon", Controls.MilitaryPanel );

include( "FLuaVector" );

local fullColor = {x = 1, y = 1, z = 1, w = 1};
local fadeColor = {x = 1, y = 1, z = 1, w = 0};
local fadeColorRV = {x = 1, y = 1, z = 1, w = 0.2};
local pinkColor = {x = 2, y = 0, z = 2, w = 1};
local lockTexture = "48Lock.dds";
local checkTexture = "48Checked.dds";

local hTexture = "Connect_H.dds";
local vTexture = "Connect_V.dds";

local topRightTexture =		"Connect_JonCurve_TopRight.dds"
local topLeftTexture =		"Connect_JonCurve_TopLeft.dds"
local bottomRightTexture =	"Connect_JonCurve_BottomRight.dds"
local bottomLeftTexture =	"Connect_JonCurve_BottomLeft.dds"

local policyIcons = {};

local g_PolicyXOffset = 28;
local g_PolicyYOffset = 68;

local g_PolicyPipeXOffset = 28;
local g_PolicyPipeYOffset = 68;

local m_gPolicyID;
local m_gAdoptingPolicy;

-------------------------------------------------
-- On Policy Selected
-------------------------------------------------
function PolicySelected( policyIndex )
    
    print("Clicked on Policy: " .. tostring(policyIndex));
    
	if policyIndex == -1 then
		return;
	end
    local player = Players[Game.GetActivePlayer()];   
    if player == nil then
		return;
    end
    
    local bHasPolicy = player:HasPolicy(policyIndex);
    local bCanAdoptPolicy = player:CanAdoptPolicy(policyIndex);
    
    print("bHasPolicy: " .. tostring(bHasPolicy));
    print("bCanAdoptPolicy: " .. tostring(bCanAdoptPolicy));
    print("Policy Blocked: " .. tostring(player:IsPolicyBlocked(policyIndex)));
    
    local bPolicyBlocked = false;
    
    -- If we can get this, OR we already have it, see if we can unblock it first
    if (bHasPolicy or bCanAdoptPolicy) then
    
		-- Policy blocked off right now? If so, try to activate
		if (player:IsPolicyBlocked(policyIndex)) then
			
			bPolicyBlocked = true;
			
			local strPolicyBranch = GameInfo.Policies[policyIndex].PolicyBranchType;
			local iPolicyBranch = GameInfoTypes[strPolicyBranch];
			
			print("Policy Branch: " .. tostring(iPolicyBranch));
			
			local popupInfo = {
				Type = ButtonPopupTypes.BUTTONPOPUP_CONFIRM_POLICY_BRANCH_SWITCH,
				Data1 = iPolicyBranch;
			}
			Events.SerialEventGameMessagePopup(popupInfo);
			
		end
    end
    
    -- Can adopt Policy right now - don't try this if we're going to unblock the Policy instead
    if (bCanAdoptPolicy and not bPolicyBlocked) then
		m_gPolicyID = policyIndex;
		m_gAdoptingPolicy = true;
		Controls.PolicyConfirm:SetHide(false);
		Controls.BGBlock:SetHide(true);	
	end
	
end

-------------------------------------------------
-- On Policy Branch Selected
-------------------------------------------------
function PolicyBranchSelected( policyBranchIndex )
    
	if policyBranchIndex == -1 then
		return;
	end
    local player = Players[Game.GetActivePlayer()];   
    if player == nil then
		return;
    end
    
    local bHasPolicyBranch = player:IsPolicyBranchUnlocked(policyBranchIndex);
    local bCanAdoptPolicyBranch = player:CanUnlockPolicyBranch(policyBranchIndex);
        
    local bUnblockingPolicyBranch = false;
    
    -- If we can get this, OR we already have it, see if we can unblock it first
    if (bHasPolicyBranch or bCanAdoptPolicyBranch) then
    
		-- Policy Branch blocked off right now? If so, try to activate
		if (player:IsPolicyBranchBlocked(policyBranchIndex)) then
			
			bUnblockingPolicyBranch = true;
			
			local popupInfo = {
				Type = ButtonPopupTypes.BUTTONPOPUP_CONFIRM_POLICY_BRANCH_SWITCH,
				Data1 = policyBranchIndex;
			}
			Events.SerialEventGameMessagePopup(popupInfo);
		end
    end
    
    -- Can adopt Policy Branch right now - don't try this if we're going to unblock the Policy Branch instead
    if (bCanAdoptPolicyBranch and not bUnblockingPolicyBranch) then
		m_gPolicyID = policyBranchIndex;
		m_gAdoptingPolicy = false;
		Controls.PolicyConfirm:SetHide(false);
		Controls.BGBlock:SetHide(true);
	end
end

-------------------------------------------------
-------------------------------------------------
function OnPopupMessage(popupInfo)
	
	local popupType = popupInfo.Type;
	if popupType ~= ButtonPopupTypes.BUTTONPOPUP_CHOOSEPOLICY then
		return;
	end
	
	m_PopupInfo = popupInfo;

	UpdateDisplay();
	
	if( m_PopupInfo.Data1 == 1 ) then
    	if( ContextPtr:IsHidden() == false ) then
    	    OnClose();
    	else
        	UIManager:QueuePopup( ContextPtr, PopupPriority.eUtmost );
    	end
	else
    	UIManager:QueuePopup( ContextPtr, PopupPriority.SocialPolicy );
	end
end
Events.SerialEventGameMessagePopup.Add( OnPopupMessage );

-------------------------------------------------
-------------------------------------------------
function UpdateDisplay()

    local player = Players[Game.GetActivePlayer()];
    local pTeam = Teams[player:GetTeam()];
    
    if player == nil then
		return;
    end
    
    Controls.AnarchyBlock:SetHide( not player:IsAnarchy() );

    local bShowAll = OptionsManager.GetPolicyInfo();
    
    local szText = Locale.ConvertTextKey("TXT_KEY_NEXT_POLICY_COST_LABEL", player:GetNextPolicyCost());
    Controls.NextCost:SetText(szText);
    
    szText = Locale.ConvertTextKey("TXT_KEY_CURRENT_CULTURE_LABEL", player:GetJONSCulture());
    Controls.CurrentCultureLabel:SetText(szText);
    
    szText = Locale.ConvertTextKey("TXT_KEY_CULTURE_PER_TURN_LABEL", player:GetTotalJONSCulturePerTurn());
    Controls.CulturePerTurnLabel:SetText(szText);
    
    local iTurns;
    local iCultureNeeded = player:GetNextPolicyCost() - player:GetJONSCulture();
    if (iCultureNeeded <= 0) then
		iTurns = 0;
    else
		if (player:GetTotalJONSCulturePerTurn() == 0) then
			iTurns = "?";
		else
			iTurns = iCultureNeeded / player:GetTotalJONSCulturePerTurn();
			iTurns = iTurns + 1;
			iTurns = math.floor(iTurns);
		end
    end
    szText = Locale.ConvertTextKey("TXT_KEY_NEXT_POLICY_TURN_LABEL", iTurns);
    Controls.NextPolicyTurnLabel:SetText(szText);
    
    -- Player Title
    local iDominantBranch = player:GetDominantPolicyBranchForTitle();
    Controls.PlayerTitleLabel:SetHide(true);
    
    -- Free Policies
    local iNumFreePolicies = player:GetNumFreePolicies();
    if (iNumFreePolicies > 0) then
	    szText = Locale.ConvertTextKey("TXT_KEY_FREE_POLICIES_LABEL", iNumFreePolicies);
	    Controls.FreePoliciesLabel:SetText( szText );
	    Controls.FreePoliciesLabel:SetHide( false );
	else
	    Controls.FreePoliciesLabel:SetHide( true );
    end
    
	Controls.InfoStack:ReprocessAnchoring();

	local justLooking = true;
	if player:GetJONSCulture() >= player:GetNextPolicyCost() then
		justLooking = false;
	end
	
	-- Adjust Policy Branches
	local i = 0;
	local numUnlockedBranches = player:GetNumPolicyBranchesUnlocked();
--	if numUnlockedBranches > 0 then
		local policyBranchInfo = GameInfo.PolicyBranchTypes[i];
		while policyBranchInfo ~= nil do
			local numString = tostring( i );
			
			local backName = "BranchBack"..numString;
			local ImageMaskName = "ImageMask"..numString;
						
			local thisBack = Controls[backName];
			local thisImageMask = Controls[ImageMaskName];
			
			
			if(thisImageMask == nil) then
				print(ImageMaskName);
			end
			
			local strToolTip = Locale.ConvertTextKey(policyBranchInfo.Help);
			
			-- Branch is not yet unlocked
			if not player:IsPolicyBranchUnlocked( i ) then
				
				-- Cannot adopt this branch right now
				if (not player:CanUnlockPolicyBranch(i)) then
					
					strToolTip = strToolTip .. "[NEWLINE][NEWLINE]" .. Locale.ConvertTextKey("TXT_KEY_POLICY_BRANCH_CANNOT_UNLOCK");
					
					thisLock:SetHide( false );
				-- Can adopt this branch right now
				else
					strToolTip = strToolTip .. "[NEWLINE][NEWLINE]" .. Locale.ConvertTextKey("TXT_KEY_POLICY_BRANCH_UNLOCK_SPEND", player:GetNextPolicyCost());
				end
				
				thisBack:SetColor( fadeColor );
				thisImageMask:SetHide(true);
				
			-- Branch is unlocked, but blocked by another branch
			elseif (player:IsPolicyBranchBlocked(i)) then
				thisBack:SetColor( fadeColor );
				strToolTip = strToolTip .. "[NEWLINE][NEWLINE]" .. Locale.ConvertTextKey("TXT_KEY_POLICY_BRANCH_BLOCKED");
				
			-- Branch is unlocked already
			else
				thisBack:SetColor( fullColor );				
				thisImageMask:SetHide(false);
			end
					
			i = i + 1;
			policyBranchInfo = GameInfo.PolicyBranchTypes[i];
		end
	
	-- Adjust Policy buttons
	i = 0;
	local policyInfo = GameInfo.Policies[i];
	while policyInfo ~= nil do
		
		local iBranch = policyInfo.PolicyBranchType;
		
		-- If this is nil it means the Policy is a freebie handed out with the Branch, so don't display it
		if (iBranch ~= nil) then
			
			local thisPolicyIcon = policyIcons[i];
			
			-- Tooltip
			local strTooltip = Locale.ConvertTextKey( policyInfo.Help );
			
			-- Player already has Policy
			if player:HasPolicy( i ) then
				thisPolicyIcon.MouseOverContainer:SetHide( true );
				thisPolicyIcon.PolicyIcon:SetDisabled( true );
				thisPolicyIcon.PolicyImage:SetColor( fullColor );
				IconHookup( policyInfo.PortraitIndex, 64, policyInfo.IconAtlasAchieved, thisPolicyIcon.PolicyImage );
				
			-- Can adopt the Policy right now
			elseif player:CanAdoptPolicy( i ) then
				thisPolicyIcon.MouseOverContainer:SetHide( false );
				thisPolicyIcon.PolicyIcon:SetDisabled( false );
				if justLooking then
					thisPolicyIcon.PolicyImage:SetColor( fullColor );
				else
					thisPolicyIcon.PolicyIcon:SetVoid1( i ); -- indicates policy to be chosen
					thisPolicyIcon.PolicyImage:SetColor( fullColor );
				end
				IconHookup( policyInfo.PortraitIndex, 64, policyInfo.IconAtlas, thisPolicyIcon.PolicyImage );
				
			-- Policy is locked
			else
				thisPolicyIcon.MouseOverContainer:SetHide( true );
				thisPolicyIcon.PolicyIcon:SetDisabled( true );
				thisPolicyIcon.PolicyImage:SetColor( fadeColorRV );
				IconHookup( policyInfo.PortraitIndex, 64, policyInfo.IconAtlas, thisPolicyIcon.PolicyImage );
				-- Tooltip
				strTooltip = strTooltip .. "[NEWLINE][NEWLINE]" .. Locale.ConvertTextKey("TXT_KEY_POLICY_CANNOT_UNLOCK");
			end
			
			-- Policy is Blocked
			if player:IsPolicyBlocked(i) then
				thisPolicyIcon.PolicyImage:SetColor( fadeColorRV );
				IconHookup( policyInfo.PortraitIndex, 64, policyInfo.IconAtlas, thisPolicyIcon.PolicyImage );
				
				-- Update tooltip if we have this Policy
				if player:HasPolicy( i ) then
					strTooltip = strTooltip .. "[NEWLINE][NEWLINE]" .. Locale.ConvertTextKey("TXT_KEY_POLICY_BRANCH_BLOCKED");
				end
			end
				
			thisPolicyIcon.PolicyIcon:SetToolTipString( strTooltip );
		end
		
		i = i + 1;
		policyInfo = GameInfo.Policies[i];
	end
end
Events.EventPoliciesDirty.Add( UpdateDisplay );

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
function OnClose()
    UIManager:DequeuePopup( ContextPtr );
end
Controls.CloseButton:RegisterCallback( Mouse.eLClick, OnClose );

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
function InputHandler( uiMsg, wParam, lParam )
    ----------------------------------------------------------------        
    -- Key Down Processing
    ----------------------------------------------------------------        
    if uiMsg == KeyEvents.KeyDown then
        if wParam == Keys.VK_ESCAPE or wParam == Keys.VK_RETURN then
			if(Controls.PolicyConfirm:IsHidden())then
	            OnClose();
	        else
				Controls.PolicyConfirm:SetHide(true);
            	Controls.BGBlock:SetHide(false);
			end
			return true;
        end
    end
end
ContextPtr:SetInputHandler( InputHandler );

function GetPipe(branchType)
	local controlTable = nil;
	
	-- decide which panel it goes on
	if branchType == "POLICY_BRANCH_LABOR" then
		controlTable = g_LaborPipeManager:GetInstance();
	elseif branchType == "POLICY_BRANCH_CULTURE" then
		controlTable = g_CulturePipeManager:GetInstance();
	elseif branchType == "POLICY_BRANCH_INDUSTRY" then
		controlTable = g_IndustryPipeManager:GetInstance();
	elseif branchType == "POLICY_BRANCH_COMMERCE" then
		controlTable = g_CommercePipeManager:GetInstance();
	elseif branchType == "POLICY_BRANCH_MILITARY" then
		controlTable = g_MilitaryPipeManager:GetInstance();
	end

	return controlTable;
end

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
function Init()

	-- add the pipes
	local policyPipes = {};
	for row in GameInfo.Policies() do
		policyPipes[row.Type] = 
		{
			upConnectionLeft = false;
			upConnectionRight = false;
			upConnectionCenter = false;
			upConnectionType = 0;
			downConnectionLeft = false;
			downConnectionRight = false;
			downConnectionCenter = false;
			downConnectionType = 0;
			yOffset = 0;
			policyType = row.Type;
		};
	end
	
	local cnxCenter = 1
	local cnxLeft = 2
	local cnxRight = 4

	-- Figure out which top and bottom adapters we need
	for row in GameInfo.Policy_PrereqPolicies() do
		local prereq = GameInfo.Policies[row.PrereqPolicy];
		local policy = GameInfo.Policies[row.PolicyType];
		if policy and prereq then
			if policy.GridX < prereq.GridX then
				policyPipes[policy.Type].upConnectionRight = true;
				policyPipes[prereq.Type].downConnectionLeft = true;
			elseif policy.GridX > prereq.GridX then
				policyPipes[policy.Type].upConnectionLeft = true;
				policyPipes[prereq.Type].downConnectionRight = true;
			else -- policy.GridX == prereq.GridX
				policyPipes[policy.Type].upConnectionCenter = true;
				policyPipes[prereq.Type].downConnectionCenter = true;
			end
			local yOffset = (policy.GridY - prereq.GridY) - 1;
			if yOffset > policyPipes[prereq.Type].yOffset then
				policyPipes[prereq.Type].yOffset = yOffset;
			end
		end
	end

	for pipeIndex, thisPipe in pairs(policyPipes) do
		if thisPipe.upConnectionLeft then
			thisPipe.upConnectionType = thisPipe.upConnectionType + cnxLeft;
		end 
		if thisPipe.upConnectionRight then
			thisPipe.upConnectionType = thisPipe.upConnectionType + cnxRight;
		end 
		if thisPipe.upConnectionCenter then
			thisPipe.upConnectionType = thisPipe.upConnectionType + cnxCenter;
		end 
		if thisPipe.downConnectionLeft then
			thisPipe.downConnectionType = thisPipe.downConnectionType + cnxLeft;
		end 
		if thisPipe.downConnectionRight then
			thisPipe.downConnectionType = thisPipe.downConnectionType + cnxRight;
		end 
		if thisPipe.downConnectionCenter then
			thisPipe.downConnectionType = thisPipe.downConnectionType + cnxCenter;
		end 
	end

	-- three passes down, up, connection
	-- connection
	for row in GameInfo.Policy_PrereqPolicies() do
		local prereq = GameInfo.Policies[row.PrereqPolicy];
		local policy = GameInfo.Policies[row.PolicyType];
		if policy and prereq then
		
			local thisPipe = policyPipes[row.PrereqPolicy];
		
			if policy.GridY - prereq.GridY > 1 or policy.GridY - prereq.GridY < -1 then
				local xOffset = (prereq.GridX-1)*g_PolicyPipeXOffset + 30;
				local pipe = GetPipe(policy.PolicyBranchType);
				pipe.ConnectorImage:SetOffsetVal( xOffset, (prereq.GridY-1)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(vTexture);
				local size = { x = 19; y = g_PolicyPipeYOffset*(policy.GridY - prereq.GridY - 1); };
				pipe.ConnectorImage:SetSize(size);
			end
			
			if policy.GridX - prereq.GridX == 1 then
				local xOffset = (prereq.GridX-1)*g_PolicyPipeXOffset + 30;
				local pipe = GetPipe(policy.PolicyBranchType);
				pipe.ConnectorImage:SetOffsetVal( xOffset + 16, (prereq.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(hTexture);
				local size = { x = 19; y = 19; };
				pipe.ConnectorImage:SetSize(size);
			end
			if policy.GridX - prereq.GridX == 2 then
				local xOffset = (prereq.GridX-1)*g_PolicyPipeXOffset + 30;
				local pipe = GetPipe(policy.PolicyBranchType);
				pipe.ConnectorImage:SetOffsetVal( xOffset + 16, (prereq.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(hTexture);
				local size = { x = 40; y = 19; };
				pipe.ConnectorImage:SetSize(size);
			end
			if policy.GridX - prereq.GridX == -2 then
				local xOffset = (policy.GridX-1)*g_PolicyPipeXOffset + 30;
				local pipe = GetPipe(policy.PolicyBranchType);
				pipe.ConnectorImage:SetOffsetVal( xOffset + 16, (prereq.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(hTexture);
				local size = { x = 40; y = 19; };
				pipe.ConnectorImage:SetSize(size);
			end
			if policy.GridX - prereq.GridX == -1 then
				local xOffset = (policy.GridX-1)*g_PolicyPipeXOffset + 30;
				local pipe = GetPipe(policy.PolicyBranchType);
				pipe.ConnectorImage:SetOffsetVal( xOffset + 16, (prereq.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(hTexture);
				local size = { x = 20; y = 19; };
				pipe.ConnectorImage:SetSize(size);
			end
			
		end
	end
	
	-- Down	
	for pipeIndex, thisPipe in pairs(policyPipes) do
		local policy = GameInfo.Policies[thisPipe.policyType];
		local xOffset = (policy.GridX-1)*g_PolicyPipeXOffset + 30;
		if thisPipe.downConnectionType >= 1 then
			
			local startPipe = GetPipe(policy.PolicyBranchType);
			startPipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset + 48 );
			startPipe.ConnectorImage:SetTexture(vTexture);
			
			local pipe = GetPipe(policy.PolicyBranchType);			
			if thisPipe.downConnectionType == 1 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(vTexture);
			elseif thisPipe.downConnectionType == 2 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(bottomRightTexture);
			elseif thisPipe.downConnectionType == 3 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(vTexture);
				pipe = GetPipe(policy.PolicyBranchType);			
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(bottomRightTexture);
			elseif thisPipe.downConnectionType == 4 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(bottomLeftTexture);
			elseif thisPipe.downConnectionType == 5 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(vTexture);
				pipe = GetPipe(policy.PolicyBranchType);			
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(bottomLeftTexture);
			elseif thisPipe.downConnectionType == 6 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(bottomRightTexture);
				pipe = GetPipe(policy.PolicyBranchType);		
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(bottomLeftTexture);
			else
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(vTexture);
				pipe = GetPipe(policy.PolicyBranchType);		
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(bottomRightTexture);
				pipe = GetPipe(policy.PolicyBranchType);
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1 + thisPipe.yOffset)*g_PolicyPipeYOffset + 58 );
				pipe.ConnectorImage:SetTexture(bottomLeftTexture);
			end
		end
	end

	-- Up
	for pipeIndex, thisPipe in pairs(policyPipes) do
		local policy = GameInfo.Policies[thisPipe.policyType];
		local xOffset = (policy.GridX-1)*g_PolicyPipeXOffset + 30;
		
		if thisPipe.upConnectionType >= 1 then
			
			local startPipe = GetPipe(policy.PolicyBranchType);
			startPipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset + 0 );
			startPipe.ConnectorImage:SetTexture(vTexture);
			
			local pipe = GetPipe(policy.PolicyBranchType);			
			if thisPipe.upConnectionType == 1 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(vTexture);
			elseif thisPipe.upConnectionType == 2 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(topRightTexture);
			elseif thisPipe.upConnectionType == 3 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(vTexture);
				pipe = GetPipe(policy.PolicyBranchType);			
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(topRightTexture);
			elseif thisPipe.upConnectionType == 4 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(topLeftTexture);
			elseif thisPipe.upConnectionType == 5 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(vTexture);
				pipe = GetPipe(policy.PolicyBranchType);			
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(topLeftTexture);
			elseif thisPipe.upConnectionType == 6 then
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(topRightTexture);
				pipe = GetPipe(policy.PolicyBranchType);		
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(topLeftTexture);
			else
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(vTexture);
				pipe = GetPipe(policy.PolicyBranchType);		
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(topRightTexture);
				pipe = GetPipe(policy.PolicyBranchType);
				pipe.ConnectorImage:SetOffsetVal( xOffset, (policy.GridY-1)*g_PolicyPipeYOffset - 10 );
				pipe.ConnectorImage:SetTexture(topLeftTexture);
			end
		end
	end

	-- Add Policy buttons
	i = 0;
	policyInfo = GameInfo.Policies[i];
	while policyInfo ~= nil do
		
		local iBranch = policyInfo.PolicyBranchType;
		
		-- If this is nil it means the Policy is a freebie handed out with the Branch, so don't display it
		if (iBranch ~= nil) then
			
			local controlTable = nil;
			print("Policy Branch: " .. iBranch);
			
			-- decide which panel it goes on
			if iBranch == "POLICY_BRANCH_LABOR" then
				controlTable = g_LaborInstanceManager:GetInstance();
			elseif iBranch == "POLICY_BRANCH_CULTURE" then
				controlTable = g_CultureInstanceManager:GetInstance();
			elseif iBranch == "POLICY_BRANCH_INDUSTRY" then
				controlTable = g_IndustryInstanceManager:GetInstance();
			elseif iBranch == "POLICY_BRANCH_COMMERCE" then
				controlTable = g_CommerceInstanceManager:GetInstance();
			elseif iBranch == "POLICY_BRANCH_MILITARY" then
				controlTable = g_MilitaryInstanceManager:GetInstance();
			end
			
			IconHookup( policyInfo.PortraitIndex, 64, policyInfo.IconAtlas, controlTable.PolicyImage );

			-- this math should match Russ's mocked up layout
			controlTable.PolicyIcon:SetOffsetVal((policyInfo.GridX-1)*g_PolicyXOffset+16,(policyInfo.GridY-1)*g_PolicyYOffset+12);
			controlTable.PolicyIcon:SetVoid1( i ); -- indicates which policy
			controlTable.PolicyIcon:RegisterCallback( Mouse.eLClick, PolicySelected );
			
			-- store this away for later
			policyIcons[i] = controlTable;
		end
		
		i = i + 1;
		policyInfo = GameInfo.Policies[i];
	end
	
end

function OnYes( )
	Controls.PolicyConfirm:SetHide(true);
	Controls.BGBlock:SetHide(false);
	
	Network.SendUpdatePolicies(m_gPolicyID, m_gAdoptingPolicy, true);
	Events.AudioPlay2DSound("AS2D_INTERFACE_POLICY");		
end
Controls.Yes:RegisterCallback( Mouse.eLClick, OnYes );

function OnNo( )
	Controls.PolicyConfirm:SetHide(true);
	Controls.BGBlock:SetHide(false);
end
Controls.No:RegisterCallback( Mouse.eLClick, OnNo );


-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
function ShowHideHandler( bIsHide, bInitState )
    if( not bInitState ) then
        if( not bIsHide ) then
        	UI.incTurnTimerSemaphore();
        	--OpenAdvisorPopup(ButtonPopupTypes.BUTTONPOPUP_CHOOSEPOLICY);
        	Events.SerialEventGameMessagePopupShown(m_PopupInfo);
        else
            UI.decTurnTimerSemaphore();
            --CloseAdvisorPopup(ButtonPopupTypes.BUTTONPOPUP_CHOOSEPOLICY);
            Events.SerialEventGameMessagePopupProcessed.CallImmediate(ButtonPopupTypes.BUTTONPOPUP_CHOOSEPOLICY, 0);
        end
    end
end
ContextPtr:SetShowHideHandler( ShowHideHandler );

Init();