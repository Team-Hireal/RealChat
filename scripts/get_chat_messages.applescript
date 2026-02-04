#!/usr/bin/osascript
-- Get recent messages from the currently active WeChat chat

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

on run argv
    -- Get max messages parameter (default 10)
    set maxMessages to 10
    if (count of argv) > 0 then
        try
            set maxMessages to item 1 of argv as integer
        end try
    end if

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

                -- Get the main window
                tell window 1
                    set messagesList to {}
                    set messageCount to 0
                    set skipLabels to {"WeChat", "微信", "Chats", "Contacts", "Favorites", "File Transfer", "文件传输助手", "Search", "Messages", "Moments", "Settings", ""}

                    -- Try to find message elements in the chat area
                    try
                        set allElements to entire contents

                        -- Look for text elements that appear to be messages
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

                                        -- Skip message count indicators
                                        if not shouldSkip then
                                            if textValue contains "new message" or textValue contains "unread message" or textValue contains "条新消息" or textValue contains "条未读" then
                                                set shouldSkip to true
                                            end if
                                        end if

                                        -- Only include text longer than 3 characters
                                        if not shouldSkip and length of textValue > 3 then
                                            -- Add to messages list
                                            set end of messagesList to textValue
                                            set messageCount to messageCount + 1

                                            -- Stop if we have enough messages
                                            if messageCount >= maxMessages then
                                                exit repeat
                                            end if
                                        end if
                                    end if
                                end if
                            end try
                        end repeat
                    end try

                    -- Build JSON response
                    set jsonMessages to "["
                    set firstMessage to true
                    repeat with msg in messagesList
                        if not firstMessage then
                            set jsonMessages to jsonMessages & ","
                        end if
                        set escapedMsg to my escapeJSON(msg)
                        set jsonMessages to jsonMessages & "\"" & escapedMsg & "\""
                        set firstMessage to false
                    end repeat
                    set jsonMessages to jsonMessages & "]"

                    return "{\"success\": true, \"messages\": " & jsonMessages & ", \"count\": " & messageCount & "}"
                end tell
            end tell
        end tell
    on error errMsg
        set escapedError to my escapeJSON(errMsg)
        return "{\"success\": false, \"error\": \"" & escapedError & "\"}"
    end try
end run
