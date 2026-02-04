tell application "System Events"
    tell process "WeChat"
        if (count of windows) > 0 then
            set mainWindow to window 1
            set allElements to entire contents of mainWindow

            set output to "Searching for message-like elements..." & return & return

            -- Look for elements that might be messages
            -- Messages might be in groups, have specific roles, or contain text

            set messageCount to 0
            repeat with elem in allElements
                try
                    set elemRole to role of elem
                    set elemValue to value of elem

                    -- Look for groups or elements with text content
                    if elemRole is "AXGroup" and elemValue is not missing value and elemValue is not "" then
                        set messageCount to messageCount + 1
                        set output to output & "Group " & messageCount & ": " & elemValue & return

                        if messageCount >= 10 then exit repeat
                    end if
                end try
            end repeat

            if messageCount is 0 then
                set output to output & "No message-like groups found." & return & return

                -- Try looking for any element with substantial text content
                set textCount to 0
                repeat with elem in allElements
                    try
                        set elemValue to value of elem
                        if elemValue is not missing value and (length of elemValue) > 10 then
                            set textCount to textCount + 1
                            set output to output & "Text " & textCount & " (" & (role of elem) & "): " & elemValue & return

                            if textCount >= 10 then exit repeat
                        end if
                    end try
                end repeat
            end if

            return output
        else
            return "No window found"
        end if
    end tell
end tell
