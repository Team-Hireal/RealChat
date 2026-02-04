tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.5

        -- Store original clipboard
        set originalClipboard to the clipboard
        set copiedMessages to {}

        try
            -- Click somewhere in the window to ensure focus
            if (count of windows) > 0 then
                set mainWindow to window 1

                -- Try to focus on the message area by clicking on a group
                try
                    if (count of groups of mainWindow) > 0 then
                        click group 1 of mainWindow
                        delay 0.3
                    end if
                end try

                -- Try different keyboard combinations to select and copy messages
                -- Approach 1: Try to select text with Shift+Up Arrow and copy
                repeat 5 times
                    -- Select current line/message
                    keystroke (ASCII character 28) using {shift down} -- Right arrow with shift
                    keystroke (ASCII character 28) using {shift down}
                    keystroke (ASCII character 28) using {shift down}
                    delay 0.1

                    -- Try to extend selection
                    key code 126 using {shift down, command down} -- Shift+Cmd+Up to select to beginning
                    delay 0.1

                    -- Copy
                    keystroke "c" using command down
                    delay 0.2

                    -- Check clipboard
                    set clipContent to the clipboard
                    if clipContent is not equal to originalClipboard and clipContent is not "" then
                        -- Check if this message is already in our list
                        set isDuplicate to false
                        repeat with existingMsg in copiedMessages
                            if existingMsg is clipContent then
                                set isDuplicate to true
                                exit repeat
                            end if
                        end repeat

                        if not isDuplicate then
                            set end of copiedMessages to clipContent
                        end if
                    end if

                    -- Move to next message area
                    key code 125 -- Down arrow
                    delay 0.2
                end repeat

                -- Restore clipboard
                set the clipboard to originalClipboard

                -- Return results
                if (count of copiedMessages) > 0 then
                    set output to "{\"success\": true, \"messages\": ["
                    repeat with i from 1 to count of copiedMessages
                        set msg to item i of copiedMessages
                        set msg to my replaceText(msg, "\\", "\\\\")
                        set msg to my replaceText(msg, "\"", "\\\"")
                        set msg to my replaceText(msg, return, "\\n")
                        set output to output & "\"" & msg & "\""
                        if i < (count of copiedMessages) then
                            set output to output & ", "
                        end if
                    end repeat
                    set output to output & "], \"count\": " & (count of copiedMessages) & "}"
                    return output
                else
                    return "{\"success\": false, \"error\": \"No messages copied\", \"clipboard\": \"" & (the clipboard) & "\"}"
                end if
            else
                return "{\"success\": false, \"error\": \"No window found\"}"
            end if

        on error errMsg
            try
                set the clipboard to originalClipboard
            end try
            return "{\"success\": false, \"error\": \"" & errMsg & "\"}"
        end try
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
