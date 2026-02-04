tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.5

        if (count of windows) > 0 then
            set mainWindow to window 1
            set allElements to entire contents of mainWindow

            set output to "Searching for lists..." & return & return

            -- Find all lists
            set listCount to 0
            repeat with elem in allElements
                try
                    if role of elem is "AXList" then
                        set listCount to listCount + 1
                        set childCount to count of UI elements of elem

                        set output to output & "List " & listCount & " - Children: " & childCount & return

                        -- If this list has many children (likely messages), examine them
                        if childCount > 20 and childCount < 100 then
                            set output to output & "Examining first 10 items:" & return

                            set itemNum to 0
                            repeat with child in (UI elements of elem)
                                set itemNum to itemNum + 1
                                if itemNum > 10 then exit repeat

                                try
                                    set childRole to role of child
                                    set childValue to value of child
                                    set childDesc to description of child

                                    set output to output & "  Item " & itemNum & ":" & return
                                    set output to output & "    Role: " & childRole & return

                                    if childValue is not missing value and childValue is not "" then
                                        set output to output & "    Value: " & childValue & return
                                    end if

                                    if childDesc is not missing value and childDesc is not "" then
                                        set output to output & "    Description: " & childDesc & return
                                    end if

                                    -- Try to get static texts within this item
                                    try
                                        set staticTexts to static texts of child
                                        if (count of staticTexts) > 0 then
                                            set output to output & "    Static texts: "
                                            repeat with staticTextElem in staticTexts
                                                try
                                                    set stValue to value of staticTextElem
                                                    if stValue is not missing value and stValue is not "" then
                                                        set output to output & stValue & " | "
                                                    end if
                                                end try
                                            end repeat
                                            set output to output & return
                                        end if
                                    end try

                                    set output to output & return
                                end try
                            end repeat
                        end if

                        set output to output & return
                    end if
                end try
            end repeat

            return output
        else
            return "No window found"
        end if
    end tell
end tell
