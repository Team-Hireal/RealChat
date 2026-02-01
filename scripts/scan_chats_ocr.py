#!/usr/bin/env python3
"""
WeChat Chat Scanner with OCR
Uses AppleScript to control WeChat and OCR to read chat names from screenshots
"""

import subprocess
import time
import json
from pathlib import Path
import sys

try:
    from PIL import Image
    import pytesseract
    import pyautogui
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    print("Install with: pip install pytesseract pillow pyautogui")
    sys.exit(1)

def open_wechat_window():
    """Open WeChat window using dock click or menu"""
    # First try to activate WeChat
    script1 = '''
    tell application "WeChat"
        activate
        delay 1
    end tell

    tell application "System Events"
        tell process "WeChat"
            return count of windows
        end tell
    end tell
    '''

    result = subprocess.run(['osascript', '-e', script1], capture_output=True, text=True)
    window_count = result.stdout.strip()

    if window_count != "0":
        return "success"

    # If no windows, try clicking dock icon
    script2 = '''
    tell application "System Events"
        tell process "Dock"
            try
                set wechatIcon to first UI element of list 1 whose name is "WeChat"
                click wechatIcon
                delay 3
                return "success"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
    end tell
    '''

    result = subprocess.run(['osascript', '-e', script2], capture_output=True, text=True)
    return result.stdout.strip()

def get_wechat_window_bounds():
    """Get the bounds of the main WeChat window (largest window)"""
    script = '''
    tell application "System Events"
        tell process "WeChat"
            if (count of windows) = 0 then
                return "no_window"
            end if

            -- Find the largest window (main window)
            set largestWindow to window 1
            set largestSize to 0

            repeat with win in windows
                set winSize to size of win
                set w to item 1 of winSize
                set h to item 2 of winSize
                set totalSize to w * h

                if totalSize > largestSize then
                    set largestSize to totalSize
                    set largestWindow to win
                end if
            end repeat

            -- Get bounds of largest window
            tell largestWindow
                set winPosition to position
                set winSize to size
                set x to item 1 of winPosition
                set y to item 2 of winPosition
                set w to item 1 of winSize
                set h to item 2 of winSize
                return (x as string) & "," & (y as string) & "," & (w as string) & "," & (h as string)
            end tell
        end tell
    end tell
    '''

    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    output = result.stdout.strip()

    if output == "no_window":
        return None

    try:
        # Remove spaces and split
        output = output.replace(' ', '')
        parts = output.split(',')
        x, y, w, h = map(int, parts)
        return {'x': x, 'y': y, 'width': w, 'height': h}
    except Exception as e:
        print(f"Error parsing window bounds: {e}")
        print(f"Raw output: {output}")
        return None

def get_chat_list_region(window_bounds):
    """Estimate the chat list region within the WeChat window"""
    # WeChat's chat list is typically on the left side
    # Approximate dimensions based on typical WeChat layout
    chat_list_width = int(window_bounds['width'] * 0.3)  # Left 30% of window
    chat_list_height = window_bounds['height'] - 100  # Full height minus header

    return {
        'x': window_bounds['x'] + 10,  # Small offset from left edge
        'y': window_bounds['y'] + 80,  # Below header
        'width': chat_list_width,
        'height': chat_list_height
    }

def capture_chat_list_screenshot(region):
    """Capture screenshot of the chat list region"""
    try:
        # Use macOS native screencapture command
        screenshot_path = Path('/tmp/wechat_chat_list.png')

        # Calculate the region in the format: x,y,width,height
        x = region['x']
        y = region['y']
        w = region['width']
        h = region['height']

        # Use screencapture with -R flag for region
        cmd = ['screencapture', '-x', '-R', f"{x},{y},{w},{h}", str(screenshot_path)]
        result = subprocess.run(cmd, capture_output=True)

        if result.returncode != 0:
            print(f"screencapture error: {result.stderr.decode()}")
            return None, None

        # Load the image
        image = Image.open(screenshot_path)

        return image, screenshot_path
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def extract_chat_names_from_image(image, lang='chi_sim+eng'):
    """Extract chat names from screenshot using OCR"""
    try:
        # Configure tesseract for better Chinese character recognition
        custom_config = r'--oem 3 --psm 6'

        # Perform OCR
        text = pytesseract.image_to_string(image, lang=lang, config=custom_config)

        # Split into lines and clean up
        lines = text.split('\n')
        chat_names = []

        for line in lines:
            line = line.strip()
            # Filter out empty lines and very short lines (likely noise)
            if len(line) > 1 and not line.isdigit():
                # Remove common OCR artifacts
                line = line.replace('|', '').replace('_', '').strip()
                if line:
                    chat_names.append(line)

        return chat_names
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return []

def scan_wechat_chats(max_chats=10, lang='chi_sim+eng'):
    """Main function to scan WeChat chats using OCR"""
    print("WeChat Chat Scanner (OCR Method)")
    print("=" * 60)

    # Step 1: Open WeChat window
    print("1. Opening WeChat window...")
    result = open_wechat_window()
    if "error" in result.lower():
        return {"error": f"Could not open WeChat: {result}"}

    time.sleep(2)  # Wait for window to fully open

    # Step 2: Get window bounds
    print("2. Getting WeChat window bounds...")
    window_bounds = get_wechat_window_bounds()
    if not window_bounds:
        return {"error": "Could not find WeChat window"}

    print(f"   Window: {window_bounds['width']}x{window_bounds['height']} at ({window_bounds['x']}, {window_bounds['y']})")

    # Step 3: Calculate chat list region
    print("3. Calculating chat list region...")
    chat_region = get_chat_list_region(window_bounds)
    print(f"   Chat list region: {chat_region['width']}x{chat_region['height']} at ({chat_region['x']}, {chat_region['y']})")

    # Step 4: Capture screenshot
    print("4. Capturing screenshot...")
    screenshot, screenshot_path = capture_chat_list_screenshot(chat_region)
    if not screenshot:
        return {"error": "Could not capture screenshot"}

    print(f"   Screenshot saved to: {screenshot_path}")

    # Step 5: Perform OCR
    print("5. Performing OCR to extract chat names...")
    chat_names = extract_chat_names_from_image(screenshot, lang=lang)

    if not chat_names:
        return {
            "error": "No chat names found. Check screenshot at /tmp/wechat_chat_list.png",
            "suggestion": "Make sure WeChat is showing the chat list and try again"
        }

    # Limit to max_chats
    chat_names = chat_names[:max_chats]

    print(f"   Found {len(chat_names)} chat names")

    return {"chats": chat_names}

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Scan WeChat chats using OCR')
    parser.add_argument('max_chats', type=int, nargs='?', default=10,
                        help='Maximum number of chats to return (default: 10)')
    parser.add_argument('--lang', default='chi_sim+eng',
                        help='Tesseract language (default: chi_sim+eng for Chinese+English)')
    parser.add_argument('--json', action='store_true',
                        help='Output in JSON format')

    args = parser.parse_args()

    result = scan_wechat_chats(max_chats=args.max_chats, lang=args.lang)

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("\n" + "=" * 60)
        print("Results:")
        print("=" * 60)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            if "suggestion" in result:
                print(f"💡 Suggestion: {result['suggestion']}")
        else:
            print(f"✓ Found {len(result['chats'])} chats:")
            for i, chat in enumerate(result['chats'], 1):
                print(f"  {i}. {chat}")

if __name__ == '__main__':
    main()
