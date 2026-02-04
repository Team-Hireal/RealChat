tell application "System Events"
    tell process "WeChat"
        -- Activate WeChat
        set frontmost to true
        delay 0.5

        -- Store original clipboard
        set originalClipboard to the clipboard

        if (count of windows) > 0 then
            set mainWindow to window 1

            -- Try to find a group or scroll area that might contain messages
            set allElements to entire contents of mainWindow

            -- Look for the text area (input field) and try to find elements near it
            -- that might be the message display area
            set output to ""

            -- First, let's try a simple approach: just use keyboard shortcuts
            -- Assuming the message area is already focused or can be focused

            -- Try clicking somewhere in the window first
            try
                -- Get the first group (main content area)
                if (count of groups of mainWindow) > 0 then
                    set mainGroup to group 1 of mainWindow
                    click mainGroup
                    delay 0.2
                end if
            end try

            -- Now try to select all and copy
            keystroke "a" using command down
            delay 0.3

            keystroke "c" using command down
            delay 0.3

            -- Get clipboard
            set newClipboard to the clipboard

            -- Check if we got anything different
            if newClipboard is not equal to originalClipboard then
                set output to newClipboard
            else
                set output to "No new content copied"
            end if

            -- Restore original clipboard
            set the clipboard to originalClipboard

            -- Press Escape to deselect
            key code 53
            delay 0.2

            return output
        else
            return "No window found"
        end if
    end tell
end tell
