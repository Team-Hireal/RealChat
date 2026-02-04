tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.5

        -- Store original clipboard
        set originalClipboard to the clipboard
        set copiedMessages to {}

        if (count of windows) > 0 then
            set mainWindow to window 1

            try
                -- Try to click in the message area (center-right of window)
                set windowPos to position of mainWindow
                set windowSize to size of mainWindow

                -- Calculate position in message area
                set msgX to (item 1 of windowPos) + ((item 1 of windowSize) * 0.65)
                set msgY to (item 2 of windowPos) + ((item 2 of windowSize) * 0.3)

                -- Try to select messages by triple-clicking (selects paragraph/message)
                repeat 5 times
                    -- Triple click to select a message
                    tell mainWindow
                        set position of mouse to {msgX, msgY}
                        delay 0.1
                    end tell

                    -- Simulate triple click using keystroke
                    click at {msgX, msgY}
                    delay 0.05
                    click at {msgX, msgY}
                    delay 0.05
                    click at {msgX, msgY}
                    delay 0.2

                    -- Copy selected text
                    keystroke "c" using command down
                    delay 0.2

                    -- Get clipboard content
                    set clipContent to the clipboard

                    -- Check if we got new content
                    if clipContent is not equal to originalClipboard and clipContent is not "" then
                        set end of copiedMessages to clipContent
                    end if

                    -- Move down to next message (arrow down)
                    key code 125 -- Down arrow
                    delay 0.2

                    -- Move down a bit more for next message
                    set msgY to msgY + 60
                end repeat

                -- Restore clipboard
                set the clipboard to originalClipboard

                -- Return results as JSON
                if (count of copiedMessages) > 0 then
                    set output to "{\"success\": true, \"messages\": ["
                    repeat with i from 1 to count of copiedMessages
                        set msg to item i of copiedMessages
                        -- Escape quotes in message
                        set msg to my replaceText(msg, "\\", "\\\\")
                        set msg to my replaceText(msg, "\"", "\\\"")
                        set output to output & "\"" & msg & "\""
                        if i < (count of copiedMessages) then
                            set output to output & ", "
                        end if
                    end repeat
                    set output to output & "], \"count\": " & (count of copiedMessages) & "}"
                    return output
                else
                    return "{\"success\": false, \"error\": \"No messages copied\"}"
                end if

            on error errMsg
                set the clipboard to originalClipboard
                return "{\"success\": false, \"error\": \"" & errMsg & "\"}"
            end try
        else
            return "{\"success\": false, \"error\": \"No window found\"}"
        end if
    end tell
end tell

on replaceText(theText, searchString, replacementString)
    set AppleScript's text item delimiters to searchString
    set theTextItems to every text item of theText
    set AppleScript's text item delimiters to replacementString
    set theText to theTextItems as string
    set AppleScript's text item delimiters to ""
    return theText
end replaceText
