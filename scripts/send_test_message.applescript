-- =============================================================================
-- WeChat Message Sender
-- Purpose: Send a message to the currently open WeChat chat
-- =============================================================================

on run argv
	-- Get message from arguments or use default
	set testMessage to "Test message - " & (current date) as string
	if (count of argv) ≥ 1 then
		set testMessage to item 1 of argv
	end if

	log "Sending message: " & testMessage

	-- Activate WeChat
	tell application "WeChat" to activate
	delay 0.5

	tell application "System Events"
		tell process "WeChat"
			if not (window 1 exists) then
				log "ERROR: WeChat window not found"
				return "{\"success\": false, \"error\": \"WeChat window not found\"}"
			end if

			try
				-- Navigate to the text input area
				tell window 1
					tell group 1
						tell splitter group 1
							tell splitter group 1
								-- Clear any existing text
								set value of text area 1 to ""
								delay 0.2

								-- Type the message
								set value of text area 1 to testMessage
								delay 0.3

								-- Focus the text area
								set focused of text area 1 to true
								delay 0.2

								-- Send the message (Enter key)
								keystroke return
								delay 0.5

								log "✓ Message sent successfully"
								return "{\"success\": true, \"message\": \"Message sent\"}"
							end tell
						end tell
					end tell
				end tell
			on error errMsg
				log "ERROR: " & errMsg
				return "{\"success\": false, \"error\": \"" & errMsg & "\"}"
			end try
		end tell
	end tell
end run
