#!/usr/bin/osascript
-- Get the currently active chat name from WeChat

on escapeJSON(theText)
    set theText to my replaceText(theText, "\\", "\\\\")
    set theText to my replaceText(theText, "\"", "\\\"")
    set theText to my replaceText(theText, return, "\\n")
    set theText to my replaceText(theText, linefeed, "\\n")
    set theText to my replaceText(theText, tab, "\\t")
    return theText
end escapeJSON

on replaceText(theText, searchString, replacementString)
    set AppleScript's text item delimiters to searchString
    set theTextItems to every text item of theText
    set AppleScript's text item delimiters to replacementString
    set theText to theTextItems as string
    set AppleScript's text item delimiters to ""
    return theText
end replaceText

on run
    try
        tell application "System Events"
            -- Check if WeChat is running
            if not (exists process "WeChat") then
                return "{\"success\": false, \"error\": \"WeChat is not running\"}"
            end if

            tell process "WeChat"
                -- Check if WeChat has any windows
                if (count of windows) = 0 then
                    return "{\"success\": false, \"error\": \"No WeChat windows open\"}"
                end if

                -- Get the main window (usually window 1)
                tell window 1
                    -- Try to find chat name in UI elements using entire contents
                    try
                        set allElements to entire contents
                        set skipLabels to {"WeChat", "微信", "Chats", "Contacts", "Favorites", "Official Accounts", "Mini Programs", "Me", "Search", ""}

                        repeat with elem in allElements
                            try
                                if role of elem is "AXStaticText" then
                                    set textValue to value of elem
                                    if textValue is not missing value and textValue is not "" then
                                        -- Check if this text should be skipped
                                        set shouldSkip to false
                                        repeat with skipLabel in skipLabels
                                            if textValue is skipLabel then
                                                set shouldSkip to true
                                                exit repeat
                                            end if
                                        end repeat

                                        -- Skip message count indicators (e.g., "3 new messages", "1 unread message")
                                        if not shouldSkip then
                                            if textValue contains "new message" or textValue contains "unread message" or textValue contains "条新消息" or textValue contains "条未读" then
                                                set shouldSkip to true
                                            end if
                                        end if

                                        -- Skip very short text (likely UI labels)
                                        if not shouldSkip and length of textValue > 1 then
                                            -- Found a potential chat name
                                            set escapedText to my escapeJSON(textValue)
                                            return "{\"success\": true, \"chat\": \"" & escapedText & "\", \"detected\": true}"
                                        end if
                                    end if
                                end if
                            end try
                        end repeat
                    end try

                    -- No chat detected
                    return "{\"success\": true, \"chat\": \"No active chat\", \"detected\": false}"
                end tell
            end tell
        end tell
    on error errMsg
        set escapedError to my escapeJSON(errMsg)
        return "{\"success\": false, \"error\": \"" & escapedError & "\"}"
    end try
end run
