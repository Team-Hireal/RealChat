tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.5

        if (count of windows) > 0 then
            set mainWindow to window 1
            set allElements to entire contents of mainWindow

            set output to "Looking for chat list and messages..." & return & return

            -- Count all UI element types to understand the structure better
            set elementTypes to {}
            repeat with elem in allElements
                try
                    set elemRole to role of elem
                    set elemDesc to role description of elem

                    -- Look for interesting element types
                    if elemRole is not in {"AXStaticText", "AXButton", "AXImage", "AXGroup"} then
                        set output to output & "Found: " & elemRole & " (" & elemDesc & ")" & return

                        -- Try to get its value
                        try
                            set elemValue to value of elem
                            if elemValue is not missing value and elemValue is not "" then
                                set output to output & "  Value: " & elemValue & return
                            end if
                        end try

                        -- Try to get its children
                        try
                            set childCount to count of UI elements of elem
                            set output to output & "  Children: " & childCount & return
                        end try

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
