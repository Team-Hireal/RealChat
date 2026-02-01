-- =============================================================================
-- WeChat Auto-Reply Bot
-- Purpose: Automatically reply to unreplied messages with templates
-- Safe: Does NOT delete any messages
-- =============================================================================

-- Configuration variables (passed from shell script)
property chatWindowName : ""
property yourName : ""
property yourTitle : ""
property introTemplate : ""
property defaultReply : ""
property replyMode : ""
property dryRun : true

-- Python interpreter path
property pythonBin : "python3"

-- Working directory
property workingDir : ""

-- Tracking file to remember who we've replied to
property trackingFile : ""

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

on leftClick(p)
	set x to the first item of p
	set y to the (last item of p) - 3
	do shell script pythonBin & space & workingDir & "mouseclick.py" & space & (x as text) & space & (y as text) & space & "1"
end leftClick

on replace(s, old, new)
	set AppleScript's text item delimiters to the old
	set parts to every text item of s
	set AppleScript's text item delimiters to the new
	set replaced to the parts as string
	set AppleScript's text item delimiters to ""
	return replaced
end replace

on removeHeader(s)
	-- Remove "Name: " prefix from message
	-- Handles both Chinese and English formats: "Name: message" or "Name：message" (Chinese colon)
	
	-- Try English colon first
	set AppleScript's text item delimiters to ":"
	set parts to text items of s
	if (count of parts) > 1 then
		set newText to (items 2 through (count of parts) of parts) as string
		set AppleScript's text item delimiters to ""
		return newText
	end if
	
	-- Try Chinese colon (：)
	set AppleScript's text item delimiters to "："
	set parts to text items of s
	if (count of parts) > 1 then
		set newText to (items 2 through (count of parts) of parts) as string
		set AppleScript's text item delimiters to ""
		return newText
	end if
	
	-- No colon found, return as-is
	set AppleScript's text item delimiters to ""
	return s
end removeHeader

on fillTemplate(template, nameValue, titleValue)
	set result to template
	set result to my replace(result, "{{NAME}}", nameValue)
	set result to my replace(result, "{{TITLE}}", titleValue)
	return result
end fillTemplate

on hasRepliedTo(contactName)
	-- Check if we've already replied to this contact
	try
		set trackingData to do shell script "cat " & quoted form of trackingFile
		if trackingData contains contactName then
			return true
		end if
	on error
		-- File doesn't exist or is empty
		return false
	end try
	return false
end hasRepliedTo

on markAsReplied(contactName)
	-- Mark this contact as replied to
	try
		do shell script "echo " & quoted form of contactName & " >> " & quoted form of trackingFile
	on error errMsg
		log "Error saving to tracking file: " & errMsg
	end try
end markAsReplied

on sendReply(msg)
	if (length of msg) > 0 then
		set the clipboard to "" -- clear clipboard
		delay 0.3
		set the clipboard to msg
		-- Verify clipboard set correctly
		repeat 3 times
			if (the clipboard as text) is equal to msg then
				exit repeat
			end if
			set the clipboard to msg
			delay 0.2
		end repeat
	end if
	
	tell application "WeChat" to activate
	delay 1.0
	
	tell application "System Events"
		tell process "WeChat"
			if not (window 1 exists) then
				return false
			end if
			try
				tell window 1
					if exists splitter group 1 then
						tell splitter group 1
							if exists splitter group 1 then
								tell splitter group 1
									if exists scroll area 2 then
										-- Click in the input area
										my leftClick(position of scroll area 2)
										delay 0.3
										-- Paste the message
										keystroke "v" using command down
										delay 0.5
										
										if not dryRun then
											-- Send the message
											key code 36 -- Enter
											delay 1.5
										else
											log "DRY RUN: Would send message (not actually sending)"
											-- Clear the input
											keystroke "a" using command down
											delay 0.2
											key code 51 -- Delete
										end if
										
										set the clipboard to "" -- clear clipboard
										return true
									end if
								end tell
							end if
						end tell
					end if
				end tell
			on error errMsg
				log "Error sending reply: " & errMsg
				return false
			end try
		end tell
	end tell
	return false
end sendReply

on switchToChat(targetName)
	log "Searching for chat: '" & targetName & "'"
	
	tell application "System Events"
		tell process "WeChat"
			if not (window 1 exists) then
				log "ERROR: WeChat window does not exist"
				return false
			end if
			try
				tell window 1
					if not (exists splitter group 1) then
						log "ERROR: splitter group 1 not found"
						return false
					end if
					
					tell splitter group 1
						if not (exists scroll area 1) then
							log "ERROR: scroll area 1 not found (chat list)"
							return false
						end if
						
						tell scroll area 1
							if not (exists table 1) then
								log "ERROR: table 1 not found (chat list table)"
								return false
							end if
							
							tell table 1
								set chatCount to count rows
								log "Found " & chatCount & " chat(s) in list"
								
								if chatCount = 0 then
									log "ERROR: No chats found in list"
									return false
								end if
								
								-- First pass: collect all chat names for debugging
								set foundChats to {}
								set chatIndex to 0
								
								repeat with chat in rows
									set chatIndex to chatIndex + 1
									try
										if exists first row of UI element 1 of chat then
											set chatName to name of first row of UI element 1 of chat
											set end of foundChats to chatName
											
											-- Try multiple matching strategies for Chinese/English support
											set exactMatch to (chatName = targetName)
											set startsWithMatch to (chatName starts with targetName)
											set containsMatch to (chatName contains targetName)
											
											-- Also try reverse matching (target contains chat name)
											set reverseMatch to (targetName contains chatName)
											
											if exactMatch or startsWithMatch or containsMatch or reverseMatch then
												log "✓ Match found! Chat name: '" & chatName & "' (index: " & chatIndex & ")"
												log "  Exact match: " & exactMatch & ", Starts with: " & startsWithMatch & ", Contains: " & containsMatch
												
												-- Click on the chat
												try
													my leftClick(position of chat)
													delay 1.0 -- Increased delay for chat switching
													log "✓ Successfully clicked on chat: '" & chatName & "'"
													return true
												on error clickErr
													log "ERROR: Failed to click chat: " & clickErr
													return false
												end try
											end if
										end if
									on error errMsg
										log "WARNING: Error reading chat " & chatIndex & ": " & errMsg
									end try
								end repeat
								
								-- If we get here, no match was found
								log "ERROR: Chat '" & targetName & "' not found in chat list"
								log ""
								log "Available chats (first 10):"
								set displayCount to chatCount
								if displayCount > 10 then
									set displayCount to 10
								end if
								repeat with i from 1 to displayCount
									try
										log "  " & i & ". '" & item i of foundChats & "'"
									on error
										log "  " & i & ". (could not read name)"
									end try
								end repeat
								if chatCount > 10 then
									log "  ... and " & (chatCount - 10) & " more"
								end if
								
								return false
							end tell
						end tell
					end tell
				end tell
			on error errMsg
				log "ERROR: Exception while switching chat: " & errMsg
				return false
			end try
		end tell
	end tell
	return false
end switchToChat

on getUnrepliedMessages()
	-- Returns a list of {sender, message} for messages we haven't replied to
	set unrepliedMessages to {}
	
	tell application "System Events"
		tell process "WeChat"
			if not (window 1 exists) then
				log "WeChat window not found."
				return unrepliedMessages
			end if
			
			try
				tell window 1
					if not (exists splitter group 1) then
						log "splitter group 1 not found."
						return unrepliedMessages
					end if
					
					tell splitter group 1
						if not (exists splitter group 1) then
							log "Nested splitter group 1 not found."
							return unrepliedMessages
						end if
						
						tell splitter group 1
							if not (exists scroll area 1) then
								log "scroll area 1 not found - cannot access messages."
								return unrepliedMessages
							end if
							
							tell scroll area 1
								if not (exists table 1) then
									log "table 1 not found - no messages."
									return unrepliedMessages
								end if
								
								tell table 1
									set messageCount to count rows
									log "Found " & messageCount & " message rows."
									
									if messageCount = 0 then
										return unrepliedMessages
									end if
									
									-- Get the last few messages and check for replies
									set checkStart to messageCount - 20
									if checkStart < 1 then
										set checkStart to 1
									end if
									
									set lastSender to ""
									set needsReply to false
									
									-- Scan messages backwards
									repeat with i from messageCount to checkStart by -1
										set message to item i of rows
										set messageElement to UI element 1 of UI element 1 of message
										set messageContent to name of messageElement
										
										-- Check if this is our message
										-- Chinese WeChat: messages start with "我" (me)
										-- English WeChat: messages might start with "You:" or your name
										set isMyMessage to false
										
										if messageContent starts with "我" then
											set isMyMessage to true
										else if messageContent starts with "You:" then
											set isMyMessage to true
										else if messageContent starts with "You " then
											set isMyMessage to true
										end if
										
										if isMyMessage then
											-- We replied to the last sender
											set needsReply to false
										else
											-- This is from someone else
											set sender to my removeHeader(messageContent)
											
											-- If we haven't seen this sender yet in this scan
											if sender ≠ lastSender then
												if lastSender ≠ "" and needsReply then
													-- Previous sender needs reply
													set end of unrepliedMessages to {contactName:lastSender, needsIntro:(not my hasRepliedTo(lastSender))}
												end if
												set lastSender to sender
												set needsReply to true
											end if
										end if
									end repeat
									
									-- Check the last sender
									if lastSender ≠ "" and needsReply then
										set end of unrepliedMessages to {contactName:lastSender, needsIntro:(not my hasRepliedTo(lastSender))}
									end if
									
								end tell
							end tell
						end tell
					end tell
				end tell
			on error errMsg
				log "Error getting unreplied messages: " & errMsg
			end try
		end tell
	end tell
	
	return unrepliedMessages
end getUnrepliedMessages

-- =============================================================================
-- MAIN SCRIPT
-- =============================================================================

on run argv
	-- Parse arguments passed from shell script
	if (count of argv) ≥ 7 then
		set chatWindowName to item 1 of argv
		set yourName to item 2 of argv
		set yourTitle to item 3 of argv
		set introTemplate to item 4 of argv
		set defaultReply to item 5 of argv
		set replyMode to item 6 of argv
		set dryRunStr to item 7 of argv
		
		if dryRunStr is "yes" then
			set dryRun to true
		else
			set dryRun to false
		end if
		
		if (count of argv) ≥ 8 then
			set workingDir to item 8 of argv
		end if
		
		if (count of argv) ≥ 9 then
			set trackingFile to item 9 of argv
		end if
	else
		log "ERROR: Insufficient arguments provided."
		return
	end if
	
	log "============================================"
	log "WeChat Auto-Reply Bot Starting"
	log "Chat: " & chatWindowName
	log "Mode: " & replyMode
	log "Dry Run: " & dryRun
	log "============================================"
	
	-- Check if WeChat application exists
	try
		tell application "System Events"
			if not (exists application process "WeChat") then
				log "ERROR: WeChat application is not running."
				log "Please start WeChat and log in, then try again."
				return
			end if
		end tell
	on error errMsg
		log "ERROR: Could not check if WeChat is running: " & errMsg
		log "Please make sure WeChat is installed and running."
		return
	end try
	
	log "WeChat process found. Activating..."
	
	-- Activate WeChat with better error handling
	try
		tell application "WeChat" to activate
		delay 1.0 -- Increased delay for activation
	on error errMsg
		log "ERROR: Could not activate WeChat: " & errMsg
		log "Please make sure WeChat is installed and you have granted accessibility permissions."
		return
	end try
	
	log "Waiting for WeChat window to appear..."
	
	-- Wait for WeChat window with more time and better checking
	tell application "System Events"
		set counter to 0
		set maxWait to 10 -- Increased from 4 to 10 seconds
		set windowFound to false
		
		repeat until (counter ≥ maxWait) or windowFound
			set counter to counter + 1
			try
				if exists process "WeChat" then
					if exists window 1 of process "WeChat" then
						set windowFound to true
						log "WeChat window found after " & counter & " second(s)."
						exit repeat
					end if
				end if
			on error
				-- Continue waiting
			end try
			delay 1
		end repeat
		
		if not windowFound then
			log "ERROR: WeChat window not found after waiting " & maxWait & " seconds."
			log ""
			log "Troubleshooting steps:"
			log "  1. Make sure WeChat is running and logged in"
			log "  2. Check if WeChat window is minimized (try clicking it)"
			log "  3. Make sure WeChat is not showing a login screen"
			log "  4. Grant Accessibility permissions in System Preferences"
			log "  5. Try restarting WeChat"
			return
		end if
		
		-- Additional verification that window is accessible
		try
			set windowCount to count of windows of process "WeChat"
			log "Found " & windowCount & " WeChat window(s)."
		on error errMsg
			log "WARNING: Could not verify window count: " & errMsg
		end try
	end tell
	
	-- Switch to target chat
	log "Switching to chat: " & chatWindowName
	if not my switchToChat(chatWindowName) then
		log "ERROR: Could not find or switch to chat: " & chatWindowName
		log "Make sure the chat exists in your recent chats list."
		return
	end if
	
	log "Successfully switched to chat."
	delay 1.0
	
	-- Get unreplied messages
	log "Scanning for unreplied messages..."
	set unrepliedList to my getUnrepliedMessages()
	
	if (count of unrepliedList) = 0 then
		log "No unreplied messages found. All caught up!"
		return
	end if
	
	log "Found " & (count of unrepliedList) & " contact(s) needing replies."
	log ""
	
	-- Process each unreplied message
	repeat with msgInfo in unrepliedList
		set contactName to contactName of msgInfo
		set needsIntro to needsIntro of msgInfo
		
		log "Processing: " & contactName
		
		-- Determine which message to send
		set messageToSend to ""
		
		if replyMode is "a" then
			-- Always send introduction
			set messageToSend to my fillTemplate(introTemplate, yourName, yourTitle)
			log "  → Sending introduction"
		else if replyMode is "b" then
			-- Always send default reply
			set messageToSend to defaultReply
			log "  → Sending default reply"
		else if replyMode is "c" then
			-- Smart mode
			if needsIntro then
				set messageToSend to my fillTemplate(introTemplate, yourName, yourTitle)
				log "  → Sending introduction (new contact)"
			else
				set messageToSend to defaultReply
				log "  → Sending default reply (known contact)"
			end if
		end if
		
		-- Send the reply
		if my sendReply(messageToSend) then
			if not dryRun then
				log "  ✓ Reply sent"
				my markAsReplied(contactName)
			else
				log "  ✓ DRY RUN: Would send reply"
			end if
		else
			log "  ✗ Failed to send reply"
		end if
		
		delay 1.0
	end repeat
	
	log ""
	log "============================================"
	log "Auto-reply process complete!"
	log "Processed " & (count of unrepliedList) & " contact(s)."
	log "============================================"
	
end run
