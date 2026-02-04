tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.5

        if (count of windows) > 0 then
            set mainWindow to window 1
            set allElements to entire contents of mainWindow

            set output to ""

            -- Find the list with many children
            repeat with elem in allElements
                try
                    if role of elem is "AXList" then
                        set childCount to count of UI elements of elem

                        if childCount > 20 and childCount < 100 then
                            set output to output & "List with " & childCount & " items" & return & return

                            -- Examine first item in detail
                            set firstItem to UI element 1 of elem

                            set output to output & "First item details:" & return
                            set output to output & "Role: " & (role of firstItem) & return
                            set output to output & "Role description: " & (role description of firstItem) & return

                            -- Get all properties
                            try
                                set itemProps to properties of firstItem
                                set output to output & "Properties: " & itemProps & return & return
                            end try

                            -- Get actions
                            try
                                set itemActions to actions of firstItem
                                set output to output & "Actions: " & return
                                repeat with act in itemActions
                                    set output to output & "  - " & (description of act) & return
                                end repeat
                            end try

                            -- Get attributes
                            try
                                set itemAttrs to attributes of firstItem
                                set output to output & return & "Attributes (" & (count of itemAttrs) & "):" & return
                                repeat with attr in itemAttrs
                                    try
                                        set attrName to name of attr
                                        set attrValue to value of attr
                                        if attrValue is not missing value then
                                            set output to output & "  " & attrName & ": " & attrValue & return
                                        end if
                                    end try
                                end repeat
                            end try

                            exit repeat
                        end if
                    end if
                end try
            end repeat

            return output
        else
            return "No window found"
        end if
    end tell
end tell
