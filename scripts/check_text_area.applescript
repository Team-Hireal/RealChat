tell application "System Events"
    tell process "WeChat"
        if (count of windows) > 0 then
            set mainWindow to window 1
            set allElements to entire contents of mainWindow

            set output to "Looking for text areas..." & return & return

            repeat with elem in allElements
                try
                    if role of elem is "AXTextArea" then
                        set output to output & "Found text area!" & return
                        set output to output & "Value: " & (value of elem) & return
                        set output to output & "Description: " & (description of elem) & return
                        try
                            set output to output & "Help: " & (help of elem) & return
                        end try
                        try
                            set output to output & "Role description: " & (role description of elem) & return
                        end try
                        try
                            set output to output & "Subrole: " & (subrole of elem) & return
                        end try
                        set output to output & return
                    end if
                end try
            end repeat

            return output
        else
            return "No WeChat window found"
        end if
    end tell
end tell
