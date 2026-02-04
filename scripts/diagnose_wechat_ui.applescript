tell application "System Events"
    tell process "WeChat"
        if (count of windows) > 0 then
            set mainWindow to window 1
            set allElements to entire contents of mainWindow

            set output to "Total UI elements: " & (count of allElements) & return & return

            -- Count different types of elements
            set staticTextCount to 0
            set textFieldCount to 0
            set textAreaCount to 0
            set buttonCount to 0
            set imageCount to 0
            set groupCount to 0
            set scrollAreaCount to 0

            repeat with elem in allElements
                try
                    set elemRole to role of elem
                    if elemRole is "AXStaticText" then
                        set staticTextCount to staticTextCount + 1
                    else if elemRole is "AXTextField" then
                        set textFieldCount to textFieldCount + 1
                    else if elemRole is "AXTextArea" then
                        set textAreaCount to textAreaCount + 1
                    else if elemRole is "AXButton" then
                        set buttonCount to buttonCount + 1
                    else if elemRole is "AXImage" then
                        set imageCount to imageCount + 1
                    else if elemRole is "AXGroup" then
                        set groupCount to groupCount + 1
                    else if elemRole is "AXScrollArea" then
                        set scrollAreaCount to scrollAreaCount + 1
                    end if
                end try
            end repeat

            set output to output & "Static texts: " & staticTextCount & return
            set output to output & "Text fields: " & textFieldCount & return
            set output to output & "Text areas: " & textAreaCount & return
            set output to output & "Buttons: " & buttonCount & return
            set output to output & "Images: " & imageCount & return
            set output to output & "Groups: " & groupCount & return
            set output to output & "Scroll areas: " & scrollAreaCount & return & return

            -- Get sample static texts
            set output to output & "Sample static texts (first 20):" & return
            set textCount to 0
            repeat with elem in allElements
                try
                    if role of elem is "AXStaticText" then
                        set txt to value of elem
                        if txt is not missing value and txt is not "" then
                            set textCount to textCount + 1
                            set output to output & textCount & ": " & txt & return
                            if textCount >= 20 then exit repeat
                        end if
                    end if
                end try
            end repeat

            return output
        else
            return "No WeChat window found"
        end if
    end tell
end tell
