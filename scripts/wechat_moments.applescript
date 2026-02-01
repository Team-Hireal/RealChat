(*
WeChat Moments Browser
Automates browsing of WeChat Moments (similar to Facebook feed)

Features:
- Browse contact's moments from their profile
- Browse general moments feed
- Extract moment text content
- Extract image information
- Get likes and comments count

Requirements:
- macOS with WeChat desktop app installed
- Accessibility permissions enabled
- WeChat must be running

Usage:
    osascript wechat_moments.applescript browse_contact "Contact Name" 10
    osascript wechat_moments.applescript browse_feed 20

Note: This is a complex automation that may be fragile due to WeChat UI changes.
Rate limiting is recommended to avoid detection.
*)

on run argv
    if (count of argv) < 1 then
        return "Error: Missing command. Usage: browse_contact|browse_feed [args]"
    end if

    set command to item 1 of argv

    if command is "browse_contact" then
        if (count of argv) < 3 then
            return "Error: Missing arguments. Usage: browse_contact <contactName> <limit>"
        end if
        set contactName to item 2 of argv
        set momentLimit to item 3 of argv as integer
        return browseContactMoments(contactName, momentLimit)

    else if command is "browse_feed" then
        if (count of argv) < 2 then
            return "Error: Missing limit argument. Usage: browse_feed <limit>"
        end if
        set momentLimit to item 2 of argv as integer
        return browseFeedMoments(momentLimit)

    else
        return "Error: Unknown command: " & command
    end if
end run

(*
Browse moments from a specific contact's profile
*)
on browseContactMoments(contactName, momentLimit)
    tell application "WeChat"
        activate
        delay 0.5
    end tell

    tell application "System Events"
        tell process "WeChat"
            try
                -- Step 1: Find and open the contact's chat
                set chatFound to openChat(contactName)
                if not chatFound then
                    return "Error: Contact not found: " & contactName
                end if

                delay 0.5

                -- Step 2: Open contact profile
                -- Usually accessible via clicking contact name at top or right-click menu
                try
                    -- Try clicking the contact name/avatar at the top of chat window
                    click static text 1 of group 1 of splitter group 1 of window 1
                    delay 1
                on error
                    return "Error: Could not open contact profile"
                end try

                -- Step 3: Navigate to Moments section
                -- Look for "Moments" or "朋友圈" button/link
                try
                    set profileWindow to window 1
                    set momentsButton to missing value

                    -- Search for Moments button
                    set allButtons to buttons of profileWindow
                    repeat with btn in allButtons
                        set btnTitle to title of btn
                        if btnTitle contains "Moments" or btnTitle contains "朋友圈" then
                            set momentsButton to btn
                            exit repeat
                        end if
                    end repeat

                    if momentsButton is not missing value then
                        click momentsButton
                        delay 1.5
                    else
                        return "Error: Moments button not found in profile"
                    end if
                on error errMsg
                    return "Error: Could not navigate to Moments: " & errMsg
                end try

                -- Step 4: Extract moments data
                set momentsData to extractMomentsFromView(momentLimit)

                -- Step 5: Close profile and return to chat list
                key code 53 -- ESC
                delay 0.3

                -- Return JSON formatted data
                return formatMomentsJSON(momentsData)

            on error errMsg
                return "Error: Failed to browse contact moments: " & errMsg
            end try
        end tell
    end tell
end browseContactMoments

(*
Browse general moments feed
*)
on browseFeedMoments(momentLimit)
    tell application "WeChat"
        activate
        delay 0.5
    end tell

    tell application "System Events"
        tell process "WeChat"
            try
                -- Step 1: Navigate to Moments tab
                -- Look for Moments icon/button in main window
                try
                    set mainWindow to window 1

                    -- Look for Moments tab (usually at the bottom or side)
                    set momentsTab to missing value
                    set allButtons to buttons of mainWindow

                    repeat with btn in allButtons
                        set btnTitle to title of btn
                        if btnTitle contains "Moments" or btnTitle contains "朋友圈" or btnTitle contains "Discover" then
                            set momentsTab to btn
                            exit repeat
                        end if
                    end repeat

                    if momentsTab is not missing value then
                        click momentsTab
                        delay 2
                    else
                        return "Error: Moments tab not found"
                    end if
                on error errMsg
                    return "Error: Could not navigate to Moments feed: " & errMsg
                end try

                -- Step 2: Extract moments from feed
                set momentsData to extractMomentsFromView(momentLimit)

                -- Step 3: Return to main chat view
                key code 53 -- ESC
                delay 0.3

                -- Return JSON formatted data
                return formatMomentsJSON(momentsData)

            on error errMsg
                return "Error: Failed to browse feed moments: " & errMsg
            end try
        end tell
    end tell
end browseFeedMoments

(*
Extract moments data from current view
*)
on extractMomentsFromView(momentLimit)
    set momentsData to {}

    tell application "System Events"
        tell process "WeChat"
            try
                -- Find the moments scroll area
                set momentsView to first scroll area of window 1

                -- Scroll to top first
                set value of vertical scroll bar 1 of momentsView to 0
                delay 0.5

                -- Extract moments by scrolling and reading
                set momentCount to 0
                set scrollPosition to 0
                set maxScrollAttempts to 20

                repeat while momentCount < momentLimit and scrollPosition < maxScrollAttempts
                    -- Get visible UI elements
                    set visibleElements to UI elements of momentsView

                    -- Look for moment containers (usually groups or text areas)
                    repeat with elem in visibleElements
                        if momentCount >= momentLimit then
                            exit repeat
                        end if

                        try
                            set elemRole to role of elem

                            -- Moments are typically in groups or text areas
                            if elemRole is "AXGroup" or elemRole is "AXTextArea" then
                                set momentData to extractSingleMoment(elem)

                                if momentData is not missing value then
                                    set end of momentsData to momentData
                                    set momentCount to momentCount + 1
                                end if
                            end if
                        end try
                    end repeat

                    -- Scroll down for more moments
                    if momentCount < momentLimit then
                        set scrollPosition to scrollPosition + 1
                        key code 125 -- Down arrow
                        key code 125
                        key code 125
                        delay 0.5
                    end if
                end repeat

            on error errMsg
                -- Return what we have so far
                return momentsData
            end try
        end tell
    end tell

    return momentsData
end extractMomentsFromView

(*
Extract data from a single moment element
*)
on extractSingleMoment(momentElement)
    tell application "System Events"
        tell process "WeChat"
            try
                set momentData to {momentText:"", imageCount:0, likes:0, comments:0}

                -- Extract text content
                try
                    set textElements to static texts of momentElement
                    set allText to ""

                    repeat with txtElem in textElements
                        set txtValue to value of txtElem
                        if txtValue is not missing value and txtValue is not "" then
                            set allText to allText & txtValue & " "
                        end if
                    end repeat

                    set momentText of momentData to allText
                end try

                -- Count images (look for image elements)
                try
                    set imageElements to images of momentElement
                    set imageCount of momentData to count of imageElements
                end try

                -- Extract likes/comments (usually shown as numbers)
                -- This is highly dependent on WeChat UI structure
                try
                    set allTexts to value of static texts of momentElement
                    repeat with txt in allTexts
                        -- Look for patterns like "10 likes" or "5 comments"
                        if txt contains "like" or txt contains "赞" then
                            try
                                set likes of momentData to txt as integer
                            end try
                        end if
                        if txt contains "comment" or txt contains "评论" then
                            try
                                set comments of momentData to txt as integer
                            end try
                        end if
                    end repeat
                end try

                return momentData

            on error
                return missing value
            end try
        end tell
    end tell
end extractSingleMoment

(*
Format moments data as JSON
*)
on formatMomentsJSON(momentsData)
    set jsonOutput to "{\"success\": true, \"moments\": ["

    set momentIndex to 0
    repeat with momentData in momentsData
        set momentIndex to momentIndex + 1

        set momentText to momentText of momentData
        set imageCount to imageCount of momentData
        set likes to likes of momentData
        set comments to comments of momentData

        -- Escape quotes in text
        set momentText to my replaceText(momentText, "\"", "\\\"")
        set momentText to my replaceText(momentText, return, " ")
        set momentText to my replaceText(momentText, linefeed, " ")

        set momentJSON to "{" & ¬
            "\"id\": \"moment_" & momentIndex & "\", " & ¬
            "\"content\": \"" & momentText & "\", " & ¬
            "\"images\": " & imageCount & ", " & ¬
            "\"likes\": " & likes & ", " & ¬
            "\"comments\": " & comments & ", " & ¬
            "\"timestamp\": \"" & (current date) as string & "\"" & ¬
            "}"

        set jsonOutput to jsonOutput & momentJSON

        if momentIndex < (count of momentsData) then
            set jsonOutput to jsonOutput & ", "
        end if
    end repeat

    set jsonOutput to jsonOutput & "]}"

    return jsonOutput
end formatMomentsJSON

(*
Helper: Open a chat by name
*)
on openChat(chatName)
    tell application "System Events"
        tell process "WeChat"
            try
                set chatList to first table of first scroll area of first splitter group of first window

                repeat with aRow in rows of chatList
                    try
                        set rowText to value of static text 1 of UI element 1 of aRow
                        if rowText contains chatName then
                            select aRow
                            delay 0.3
                            return true
                        end if
                    end try
                end repeat

                return false
            on error
                return false
            end try
        end tell
    end tell
end openChat

(*
Helper: Replace text
*)
on replaceText(theText, searchString, replacementString)
    set AppleScript's text item delimiters to searchString
    set textItems to text items of theText
    set AppleScript's text item delimiters to replacementString
    set theText to textItems as string
    set AppleScript's text item delimiters to ""
    return theText
end replaceText