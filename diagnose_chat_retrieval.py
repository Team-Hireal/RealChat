#!/usr/bin/env python3
"""
Diagnostic Script: Chat Name vs Content Retrieval
Helps understand what the agent can actually retrieve from WeChat
"""

import subprocess
import json
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

print("=" * 70)
print("WeChat Chat Retrieval Diagnostic")
print("=" * 70)
print()

# Test 1: What does the accessibility API return?
log("Test 1: Checking what accessibility API returns from chat list...")
print()

script = '''
tell application "WeChat" to activate
delay 1

tell application "System Events"
    tell process "WeChat"
        -- Try to get the chat list
        try
            set chatList to UI elements of window 1
            set chatListInfo to {}

            repeat with elem in chatList
                try
                    set elemClass to class of elem as string
                    set elemName to name of elem as string
                    set elemValue to value of elem as string
                    set elemDesc to description of elem as string

                    set end of chatListInfo to {elemClass:elemClass, elemName:elemName, elemValue:elemValue, elemDesc:elemDesc}
                on error errMsg
                    -- Skip elements that error
                end try
            end repeat

            return chatListInfo as string
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
end tell
'''

try:
    result = subprocess.run(['osascript', '-e', script],
                          capture_output=True, text=True, timeout=15)
    print("Accessibility API Output:")
    print("-" * 70)
    print(result.stdout)
    print()
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test 2: What does the current scan_chats script return?
log("Test 2: Testing current scan_chats AppleScript...")
print()

scan_script = '''
tell application "WeChat\" to activate
delay 1

tell application "System Events"
    tell process "WeChat"
        try
            -- Get the main window
            set mainWindow to window 1

            -- Try to get chat list (left sidebar)
            set chatElements to UI elements of mainWindow

            set chatNames to {}
            repeat with elem in chatElements
                try
                    set elemName to name of elem
                    if elemName is not missing value and elemName is not "" then
                        set end of chatNames to elemName
                    end if
                on error
                    -- Skip
                end try
            end repeat

            return chatNames
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
end tell
'''

try:
    result = subprocess.run(['osascript', '-e', scan_script],
                          capture_output=True, text=True, timeout=15)
    print("Current scan_chats Output:")
    print("-" * 70)
    output = result.stdout.strip()
    if output:
        # Try to parse as list
        items = output.split(', ')
        print(f"Found {len(items)} items:")
        for i, item in enumerate(items[:10], 1):  # Show first 10
            print(f"  {i}. {item}")
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more")
    else:
        print("(empty)")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test 3: Can we get the selected chat name?
log("Test 3: Checking if we can get the currently selected chat name...")
print()

selected_chat_script = '''
tell application "WeChat" to activate
delay 1

tell application "System Events"
    tell process "WeChat"
        try
            -- Try to get the title of the main window or selected chat
            set windowTitle to name of window 1
            return "Window title: " & windowTitle
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
end tell
'''

try:
    result = subprocess.run(['osascript', '-e', selected_chat_script],
                          capture_output=True, text=True, timeout=10)
    print("Selected Chat Detection:")
    print("-" * 70)
    print(result.stdout)
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test 4: Can we read message content?
log("Test 4: Checking if we can read message content from current chat...")
print()

read_content_script = '''
tell application "WeChat" to activate
delay 1

tell application "System Events"
    tell process "WeChat"
        try
            -- Select all and copy (this gets the chat content)
            keystroke "a" using {command down}
            delay 0.3
            keystroke "c" using {command down}
            delay 0.3
            return the clipboard
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
end tell
'''

try:
    result = subprocess.run(['osascript', '-e', read_content_script],
                          capture_output=True, text=True, timeout=10)
    content = result.stdout.strip()
    print("Message Content Retrieval:")
    print("-" * 70)
    if content:
        lines = content.split('\n')
        print(f"Retrieved {len(lines)} lines of content")
        print("First 5 lines:")
        for i, line in enumerate(lines[:5], 1):
            print(f"  {i}. {line[:80]}{'...' if len(line) > 80 else ''}")
        print()
        print("Last 5 lines:")
        for i, line in enumerate(lines[-5:], 1):
            print(f"  {i}. {line[:80]}{'...' if len(line) > 80 else ''}")
    else:
        print("(empty)")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Summary
print("=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)
print()
print("Key Findings:")
print("1. Accessibility API: Check what UI elements are exposed above")
print("2. Chat Names: Check if actual chat names appear in the output")
print("3. Message Content: Check if message content can be retrieved")
print()
print("Expected Issue:")
print("- Chat names are NOT exposed through accessibility API")
print("- Only message content and UI element descriptions are available")
print("- This is why the agent cannot find chats by name reliably")
print()
print("Recommended Solutions:")
print("1. Use OCR-based scanning (scripts/scan_chats_ocr.py)")
print("2. Use manual chat name entry")
print("3. Switch to WeChat Web mode for better API access")
print()
