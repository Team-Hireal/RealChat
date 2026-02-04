#!/usr/bin/env python3
"""
Detailed WeChat UI inspection script
"""

import subprocess

print("=" * 60)
print("WeChat UI Element Inspection")
print("=" * 60)

# Script to get all static text elements
script = '''
tell application "System Events"
    tell process "WeChat"
        if (count of windows) = 0 then
            return "No windows"
        end if

        set mainWindow to window 1
        set winTitle to name of mainWindow

        set output to "Window Title: " & winTitle & return & return

        -- Get all static text elements
        try
            set staticTexts to static texts of mainWindow
            set output to output & "Static Text Elements (" & (count of staticTexts) & "):" & return
            repeat with i from 1 to (count of staticTexts)
                set textValue to value of item i of staticTexts
                if textValue is not "" then
                    set output to output & "  [" & i & "] " & textValue & return
                end if
            end repeat
        on error errMsg
            set output to output & "Error getting static texts: " & errMsg & return
        end try

        return output
    end tell
end tell
'''

try:
    result = subprocess.run(['osascript', '-e', script],
                          capture_output=True, text=True, timeout=10)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
except Exception as e:
    print(f"Error: {e}")

print("=" * 60)
