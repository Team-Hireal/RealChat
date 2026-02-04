tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.3

        set output to "Menu bars: " & (count of menu bars) & return & return

        if (count of menu bars) > 0 then
            set menuBar to menu bar 1

            set output to output & "Menus:" & return
            repeat with m in (menu bar items of menuBar)
                try
                    set menuTitle to title of m
                    set output to output & "- " & menuTitle & return

                    -- Get menu items for each menu
                    try
                        set menuItems to menu items of menu 1 of m
                        repeat with mi in menuItems
                            try
                                set itemTitle to title of mi
                                if itemTitle is not "" then
                                    set output to output & "  - " & itemTitle & return
                                end if
                            end try
                        end repeat
                    end try
                end try
            end repeat
        end if

        return output
    end tell
end tell
