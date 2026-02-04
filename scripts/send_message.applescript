#!/usr/bin/osascript
-- Send a message to a WeChat chat
-- Usage: osascript send_message.applescript "Chat Name" "Message"

on run argv
    if (count of argv) < 2 then
        return "{\"success\": false, \"error\": \"Usage: send_message.applescript <chat_name> <message>\"}"
    end if

    set chatName to item 1 of argv
    set messageText to item 2 of argv

    try
        tell application "System Events"
            if not (exists process "WeChat") then
                return "{\"success\": false, \"error\": \"WeChat is not running\"}"
            end if

            tell process "WeChat"
                set frontmost to true
                delay 0.5

                -- Try to use keyboard shortcut to open search (Cmd+F)
                keystroke "f" using command down
                delay 0.3

                -- Type the chat name
                keystroke chatName
                delay 0.5

                -- Press Enter to select first result
                key code 36 -- Enter
                delay 0.5

                -- Type the message
                keystroke messageText
                delay 0.2

                -- Send the message (Enter)
                key code 36 -- Enter
                delay 0.3

                return "{\"success\": true, \"message\": \"Message sent\"}"
            end tell
        end tell
    on error errMsg
        return "{\"success\": false, \"error\": \"" & errMsg & "\"}"
    end try
end run
