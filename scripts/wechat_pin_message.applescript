(*
WeChat Message Pinning Controller
Automates pinning and unpinning of WeChat chats based on message importance

Features:
- Pin chat by name
- Unpin chat by name
- Get list of pinned chats
- Detect read status of messages
- Auto-unpin when messages are read

Requirements:
- macOS with WeChat desktop app installed
- Accessibility permissions enabled
- WeChat must be running

Usage:
    osascript wechat_pin_message.applescript pin "Contact Name"
    osascript wechat_pin_message.applescript unpin "Contact Name"
    osascript wechat_pin_message.applescript list
    osascript wechat_pin_message.applescript check_read "Contact Name"
*)

on run argv
    if (count of argv) < 1 then
        return "Error: Missing command. Usage: pin|unpin|list|check_read [chatName]"
    end if

    set command to item 1 of argv

    if command is "pin" then
        if (count of argv) < 2 then
            return "Error: Missing chat name for pin command"
        end if
        set chatName to item 2 of argv
        return pinChat(chatName)

    else if command is "unpin" then
        if (count of argv) < 2 then
            return "Error: Missing chat name for unpin command"
        end if
        set chatName to item 2 of argv
        return unpinChat(chatName)

    else if command is "list" then
        return listPinnedChats()

    else if command is "check_read" then
        if (count of argv) < 2 then
            return "Error: Missing chat name for check_read command"
        end if
        set chatName to item 2 of argv
        return checkReadStatus(chatName)

    else
        return "Error: Unknown command: " & command
    end if
end run

(*
Pin a chat by name
*)
on pinChat(chatName)
    tell application "WeChat"
        activate
        delay 0.5
    end tell

    tell application "System Events"
        tell process "WeChat"
            try
                -- Find the chat in the list
                set chatFound to false
                set chatRow to missing value

                -- Try to find the chat list
                set chatList to first table of first scroll area of first splitter group of first window

                -- Search for the chat
                repeat with aRow in rows of chatList
                    try
                        set rowText to value of static text 1 of UI element 1 of aRow
                        if rowText contains chatName then
                            set chatFound to true
                            set chatRow to aRow
                            exit repeat
                        end if
                    end try
                end repeat

                if not chatFound then
                    return "Error: Chat not found: " & chatName
                end if

                -- Right-click on the chat
                perform action "AXShowMenu" of chatRow
                delay 0.3

                -- Look for "Pin" menu item
                set menuItems to menu items of menu 1 of chatRow
                repeat with menuItem in menuItems
                    set menuTitle to title of menuItem
                    if menuTitle contains "Pin" or menuTitle contains "置顶" then
                        click menuItem
                        delay 0.2
                        return "Success: Pinned chat: " & chatName
                    end if
                end repeat

                -- If we get here, pin option not found (might already be pinned)
                key code 53 -- ESC to close menu
                return "Info: Chat may already be pinned: " & chatName

            on error errMsg
                return "Error: Failed to pin chat: " & errMsg
            end try
        end tell
    end tell
end pinChat

(*
Unpin a chat by name
*)
on unpinChat(chatName)
    tell application "WeChat"
        activate
        delay 0.5
    end tell

    tell application "System Events"
        tell process "WeChat"
            try
                -- Find the chat in the list (pinned chats are at the top)
                set chatFound to false
                set chatRow to missing value

                set chatList to first table of first scroll area of first splitter group of first window

                -- Search for the chat
                repeat with aRow in rows of chatList
                    try
                        set rowText to value of static text 1 of UI element 1 of aRow
                        if rowText contains chatName then
                            set chatFound to true
                            set chatRow to aRow
                            exit repeat
                        end if
                    end try
                end repeat

                if not chatFound then
                    return "Error: Chat not found: " & chatName
                end if

                -- Right-click on the chat
                perform action "AXShowMenu" of chatRow
                delay 0.3

                -- Look for "Unpin" menu item
                set menuItems to menu items of menu 1 of chatRow
                repeat with menuItem in menuItems
                    set menuTitle to title of menuItem
                    if menuTitle contains "Unpin" or menuTitle contains "取消置顶" then
                        click menuItem
                        delay 0.2
                        return "Success: Unpinned chat: " & chatName
                    end if
                end repeat

                -- If we get here, unpin option not found (might not be pinned)
                key code 53 -- ESC to close menu
                return "Info: Chat may not be pinned: " & chatName

            on error errMsg
                return "Error: Failed to unpin chat: " & errMsg
            end try
        end tell
    end tell
end unpinChat

(*
List all pinned chats
*)
on listPinnedChats()
    tell application "WeChat"
        activate
        delay 0.5
    end tell

    tell application "System Events"
        tell process "WeChat"
            try
                set pinnedChats to {}
                set chatList to first table of first scroll area of first splitter group of first window

                -- Pinned chats are typically at the top and may have a visual indicator
                -- We'll check the first 20 chats for pinned status
                set rowCount to count of rows of chatList
                set maxCheck to 20
                if rowCount < maxCheck then
                    set maxCheck to rowCount
                end if

                repeat with i from 1 to maxCheck
                    try
                        set aRow to row i of chatList

                        -- Try to detect if chat is pinned
                        -- Method 1: Check for pin indicator (varies by WeChat version)
                        -- Method 2: Right-click and check menu (more reliable but slower)

                        -- For now, we'll use a heuristic: pinned chats are at the top
                        -- and separated by a divider line
                        set rowText to value of static text 1 of UI element 1 of aRow

                        -- Check if this is a divider (end of pinned section)
                        if rowText is "" or rowText is missing value then
                            exit repeat
                        end if

                        -- Add to pinned list
                        set end of pinnedChats to rowText

                    end try
                end repeat

                if (count of pinnedChats) is 0 then
                    return "Info: No pinned chats found"
                else
                    set AppleScript's text item delimiters to ", "
                    set pinnedList to pinnedChats as string
                    set AppleScript's text item delimiters to ""
                    return "Pinned chats: " & pinnedList
                end if

            on error errMsg
                return "Error: Failed to list pinned chats: " & errMsg
            end try
        end tell
    end tell
end listPinnedChats

(*
Check if messages in a chat have been read
Returns: "read" or "unread"
*)
on checkReadStatus(chatName)
    tell application "WeChat"
        activate
        delay 0.5
    end tell

    tell application "System Events"
        tell process "WeChat"
            try
                set chatFound to false
                set hasUnreadBadge to false

                set chatList to first table of first scroll area of first splitter group of first window

                -- Search for the chat
                repeat with aRow in rows of chatList
                    try
                        set rowText to value of static text 1 of UI element 1 of aRow
                        if rowText contains chatName then
                            set chatFound to true

                            -- Check for unread badge (red dot or number)
                            -- The badge is typically a UI element with a specific role
                            try
                                set uiElements to UI elements of UI element 1 of aRow
                                repeat with elem in uiElements
                                    try
                                        set elemRole to role of elem
                                        set elemValue to value of elem

                                        -- Check if this is an unread indicator
                                        if elemRole is "AXStaticText" and elemValue is not missing value then
                                            -- Check if it's a number (unread count)
                                            try
                                                set unreadCount to elemValue as integer
                                                if unreadCount > 0 then
                                                    set hasUnreadBadge to true
                                                    exit repeat
                                                end if
                                            end try
                                        end if
                                    end try
                                end repeat
                            end try

                            exit repeat
                        end if
                    end try
                end repeat

                if not chatFound then
                    return "Error: Chat not found: " & chatName
                end if

                if hasUnreadBadge then
                    return "unread"
                else
                    return "read"
                end if

            on error errMsg
                return "Error: Failed to check read status: " & errMsg
            end try
        end tell
    end tell
end checkReadStatus

(*
Helper function to find chat row by name
*)
on findChatRow(chatName)
    tell application "System Events"
        tell process "WeChat"
            try
                set chatList to first table of first scroll area of first splitter group of first window

                repeat with aRow in rows of chatList
                    try
                        set rowText to value of static text 1 of UI element 1 of aRow
                        if rowText contains chatName then
                            return aRow
                        end if
                    end try
                end repeat

                return missing value
            on error
                return missing value
            end try
        end tell
    end tell
end findChatRow
