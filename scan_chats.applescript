-- =============================================================================
-- WeChat Chat Scanner
-- Purpose: Scan and list available chats from WeChat
-- Returns: JSON array of chat names
-- Note: WeChat desktop's accessibility API has limitations
-- =============================================================================

on run argv
	set maxChats to 10
	if (count of argv) ≥ 1 then
		try
			set maxChats to item 1 of argv as integer
		end try
	end if

	tell application "System Events"
		if not (exists application process "WeChat") then
			return "{\"error\": \"WeChat is not running. Please start WeChat first.\"}"
		end if
	end tell

	-- Open WeChat window via dock click
	tell application "System Events"
		tell process "Dock"
			try
				set wechatIcon to first UI element of list 1 whose name is "WeChat"
				click wechatIcon
				delay 3
			on error
				return "{\"error\": \"Could not find WeChat in dock\"}"
			end try
		end tell

		tell process "WeChat"
			if (count of windows) = 0 then
				return "{\"error\": \"WeChat window did not open. Please click the WeChat icon in the dock manually.\"}"
			end if

			try
				tell window 1
					tell UI element 1
						tell UI element 9
							tell UI element 1
								-- Access the chat list (AXList at position 7)
								set chatList to UI element 7

								-- Get element count
								set elemCount to count of UI elements of chatList

								if elemCount = 0 then
									return "{\"error\": \"No chats found in the list. Make sure you're on the Messages view.\"}"
								end if

								-- Try to extract chat names from entire contents
								set allContents to entire contents of chatList
								set chatNames to {}

								repeat with elem in allContents
									try
										-- Try multiple ways to get the name
										set elemName to missing value

										try
											set elemName to name of elem
										end try

										if elemName is missing value or elemName is "" then
											try
												set elemName to value of elem
											end try
										end if

										if elemName is missing value or elemName is "" then
											try
												set elemName to title of elem
											end try
										end if

										if elemName is missing value or elemName is "" then
											try
												set elemName to description of elem
											end try
										end if

										-- If we found a valid name, add it
										if elemName is not missing value and elemName is not "" and elemName is not "Messages" then
											if chatNames does not contain elemName then
												set end of chatNames to elemName
												if (count of chatNames) ≥ maxChats then exit repeat
											end if
										end if
									end try
								end repeat

								-- Build JSON response
								if (count of chatNames) > 0 then
									set output to "{\"chats\": ["
									set firstItem to true
									repeat with chatName in chatNames
										if not firstItem then
											set output to output & ", "
										end if
										-- Escape quotes in chat names
										set escapedName to my replaceText(chatName, "\"", "\\\"")
										set output to output & "\"" & escapedName & "\""
										set firstItem to false
									end repeat
									set output to output & "]}"
									return output
								else
									return "{\"error\": \"WeChat desktop accessibility API does not expose chat names. Please use WeChat Web mode instead.\", \"suggestion\": \"Switch to WeChat Web automation in the settings.\"}"
								end if
							end tell
						end tell
					end tell
				end tell
			on error errMsg
				return "{\"error\": \"Could not access chat list: " & errMsg & "\", \"suggestion\": \"Try using WeChat Web mode instead.\"}"
			end try
		end tell
	end tell
end run

-- Helper function to replace text
on replaceText(theText, oldString, newString)
	set AppleScript's text item delimiters to oldString
	set textItems to text items of theText
	set AppleScript's text item delimiters to newString
	set theText to textItems as string
	set AppleScript's text item delimiters to ""
	return theText
end replaceText
