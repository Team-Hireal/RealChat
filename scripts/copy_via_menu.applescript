tell application "System Events"
    tell process "WeChat"
        set frontmost to true
        delay 0.5

        -- Store original clipboard
        set originalClipboard to the clipboard

        try
            -- Click on File menu -> Select All
            click menu item "Select All" of menu "File" of menu bar 1
            delay 0.3

            -- Click on Edit menu -> Copy
            click menu item "Copy" of menu "Edit" of menu bar 1
            delay 0.3

            -- Get clipboard content
            set newClipboard to the clipboard

            -- Restore original clipboard
            set the clipboard to originalClipboard

            -- Return the result
            if newClipboard is not equal to originalClipboard then
                return newClipboard
            else
                return "No content copied"
            end if
        on error errMsg
            return "Error: " & errMsg
        end try
    end tell
end tell
