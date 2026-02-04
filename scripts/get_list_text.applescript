tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.5

        if (count of windows) > 0 then
            set mainWindow to window 1
            set allElements to entire contents of mainWindow

            set output to ""

            -- Find the list with ~40 children (likely messages)
            repeat with elem in allElements
                try
                    if role of elem is "AXList" then
                        set childCount to count of UI elements of elem

                        if childCount > 20 and childCount < 100 then
                            set output to output & "Found message list with " & childCount & " items" & return & return

                            -- Get first 10 items and their text
                            set itemNum to 0
                            repeat with child in (UI elements of elem)
                                set itemNum to itemNum + 1
                                if itemNum > 10 then exit repeat

                                try
                                    -- Try different ways to get text
                                    set itemText to ""

                                    -- Method 1: Direct value
                                    try
                                        set itemText to value of child
                                    end try

                                    -- Method 2: Title
                                    if itemText is "" or itemText is missing value then
                                        try
                                            set itemText to title of child
                                        end try
                                    end if

                                    -- Method 3: Name
                                    if itemText is "" or itemText is missing value then
                                        try
                                            set itemText to name of child
                                        end try
                                    end if

                                    -- Method 4: Get entire contents and look for text
                                    if itemText is "" or itemText is missing value then
                                        try
                                            set childElements to entire contents of child
                                            repeat with ce in childElements
                                                try
                                                    set ceValue to value of ce
                                                    if ceValue is not missing value and ceValue is not "" and (length of ceValue) > 0 then
                                                        set itemText to itemText & ceValue & " "
                                                    end if
                                                end try
                                            end repeat
                                        end try
                                    end if

                                    set output to output & itemNum & ": " & itemText & return
                                end try
                            end repeat

                            exit repeat
                        end if
                    end if
                end try
            end repeat

            if output is "" then
                set output to "No suitable list found"
            end if

            return output
        else
            return "No window found"
        end if
    end tell
end tell
