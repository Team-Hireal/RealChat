tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.5

        if (count of windows) > 0 then
            set mainWindow to window 1

            -- Try to right-click in the message area
            -- First, let's try to find any clickable element in the main group
            try
                if (count of groups of mainWindow) > 0 then
                    set mainGroup to group 1 of mainWindow

                    -- Try to right-click on the group
                    tell mainGroup
                        perform action "AXShowMenu"
                    end tell

                    delay 0.5

                    -- Check if a menu appeared
                    if (count of menus of mainWindow) > 0 then
                        set contextMenu to menu 1 of mainWindow
                        set menuItems to menu items of contextMenu

                        set output to "Context menu items:" & return
                        repeat with mi in menuItems
                            try
                                set itemTitle to title of mi
                                if itemTitle is not "" then
                                    set output to output & "- " & itemTitle & return
                                end if
                            end try
                        end repeat

                        -- Close the menu
                        key code 53 -- Escape

                        return output
                    else
                        return "No context menu appeared"
                    end if
                end if
            on error errMsg
                return "Error: " & errMsg
            end try
        else
            return "No window found"
        end if
    end tell
end tell
