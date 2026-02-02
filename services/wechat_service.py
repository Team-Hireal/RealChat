"""
WeChat Service
Handles all WeChat automation (AppleScript, OCR, messaging)
Consolidates functionality from agent.py and scripts/
"""

import subprocess
import time
from pathlib import Path
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class WeChatService:
    """Unified WeChat automation service"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.chat_names = self.config.get('chat_names', ['File Transfer', '文件传输助手'])
        self.scan_method = self.config.get('scan_method', 'applescript')  # applescript, ocr, manual

    def is_wechat_running(self) -> bool:
        """Check if WeChat is running"""
        try:
            script = '''
            tell application "System Events"
                return (name of processes) contains "WeChat"
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=5)
            return result.stdout.strip() == 'true'
        except Exception as e:
            logger.error(f"Error checking WeChat status: {e}")
            return False

    def send_message(self, text: str, chat_name: str = None) -> bool:
        """
        Send message to WeChat chat

        Args:
            text: Message content
            chat_name: Target chat name (defaults to File Transfer)

        Returns:
            bool: Success status
        """
        # Use provided chat name or default to first configured chat
        target_chats = [chat_name] if chat_name else self.chat_names

        # Write message to temp file
        temp_file = '/tmp/wechat_msg.txt'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(text)

        # Try each chat name
        for chat in target_chats:
            script = f'''
            set msg to do shell script "cat {temp_file}"

            tell application "WeChat"
                activate
            end tell
            delay 0.8

            tell application "System Events"
                tell process "WeChat"
                    -- Open search
                    keystroke "f" using {{command down}}
                    delay 0.4

                    -- Clear search
                    keystroke "a" using {{command down}}
                    delay 0.1
                    key code 51  -- Delete
                    delay 0.3

                    -- Type chat name
                    keystroke "{chat}"
                    delay 1.0

                    -- Select first result
                    key code 125  -- Down arrow
                    delay 0.3

                    -- Open chat
                    key code 36  -- Enter
                    delay 0.8

                    -- Close search
                    key code 53  -- ESC
                    delay 0.3

                    -- Type message
                    keystroke msg
                    delay 0.4

                    -- Send
                    key code 36  -- Enter
                    delay 0.3

                    return "SUCCESS"
                end tell
            end tell
            '''

            try:
                result = subprocess.run(['osascript', '-e', script],
                                      capture_output=True, text=True,
                                      timeout=20, check=True)
                logger.info(f"Message sent to {chat}")
                return True
            except Exception as e:
                logger.warning(f"Failed to send to {chat}: {e}")
                continue

        logger.error("Failed to send message to any configured chat")
        return False

    def read_last_message(self, chat_name: str = None) -> Optional[str]:
        """
        Read last message from WeChat chat

        Args:
            chat_name: Target chat name (defaults to File Transfer)

        Returns:
            str: Message content or None
        """
        target_chats = [chat_name] if chat_name else self.chat_names

        for chat in target_chats:
            script = f'''
            tell application "WeChat" to activate
            delay 0.5
            tell application "System Events"
                tell process "WeChat"
                    keystroke "f" using {{command down}}
                    delay 0.3
                    keystroke "a" using {{command down}}
                    delay 0.1
                    key code 51
                    delay 0.2
                    keystroke "{chat}"
                    delay 0.7
                    key code 125  -- Down arrow
                    delay 0.3
                    key code 36  -- Enter
                    delay 0.5
                    key code 53  -- ESC
                    delay 0.3
                    keystroke "a" using {{command down}}
                    delay 0.2
                    keystroke "c" using {{command down}}
                    delay 0.3
                end tell
            end tell
            return the clipboard
            '''

            try:
                result = subprocess.run(['osascript', '-e', script],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    content = result.stdout.strip()
                    logger.info(f"Read {len(content)} chars from {chat}")
                    return content
            except Exception as e:
                logger.warning(f"Failed to read from {chat}: {e}")
                continue

        return None

    def scan_chats_applescript(self, max_chats: int = 10) -> List[str]:
        """
        Scan chats using AppleScript (limited by accessibility API)

        Returns:
            List of chat names (may be empty due to API limitations)
        """
        script = '''
        tell application "WeChat" to activate
        delay 0.5
        tell application "System Events"
            tell process "WeChat"
                set chatElements to UI elements of window 1
                set chatNames to {}
                repeat with elem in chatElements
                    try
                        set elemName to name of elem
                        if elemName is not missing value and elemName is not "" then
                            set end of chatNames to elemName
                        end if
                    end try
                end repeat
                return chatNames
            end tell
        end tell
        '''

        try:
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=15)
            output = result.stdout.strip()
            if output:
                chats = [c.strip() for c in output.split(',')]
                return chats[:max_chats]
        except Exception as e:
            logger.error(f"AppleScript scan failed: {e}")

        return []

    def scan_chats_ocr(self, max_chats: int = 10) -> List[str]:
        """
        Scan chats using OCR (more reliable but requires dependencies)

        Returns:
            List of chat names extracted via OCR
        """
        try:
            # Import OCR dependencies
            from PIL import Image
            import pytesseract

            # Get WeChat window bounds
            bounds = self._get_window_bounds()
            if not bounds:
                logger.error("Could not get WeChat window bounds")
                return []

            # Calculate chat list region
            region = self._get_chat_list_region(bounds)

            # Capture screenshot
            screenshot_path = '/tmp/wechat_chat_list.png'
            self._capture_screenshot(region, screenshot_path)

            # Perform OCR
            image = Image.open(screenshot_path)
            text = pytesseract.image_to_string(image, lang='chi_sim+eng',
                                              config='--oem 3 --psm 6')

            # Extract chat names
            lines = text.split('\n')
            chat_names = []
            for line in lines:
                line = line.strip()
                if len(line) > 1 and not line.isdigit():
                    line = line.replace('|', '').replace('_', '').strip()
                    if line:
                        chat_names.append(line)

            return chat_names[:max_chats]

        except ImportError:
            logger.error("OCR dependencies not installed (pytesseract, PIL)")
            return []
        except Exception as e:
            logger.error(f"OCR scan failed: {e}")
            return []

    def scan_chats(self, max_chats: int = 10) -> List[str]:
        """
        Scan chats using configured method

        Returns:
            List of chat names
        """
        if self.scan_method == 'ocr':
            return self.scan_chats_ocr(max_chats)
        elif self.scan_method == 'applescript':
            return self.scan_chats_applescript(max_chats)
        else:
            # Manual mode - return configured chats
            return self.chat_names

    def _get_window_bounds(self) -> Optional[Dict]:
        """Get WeChat window bounds"""
        script = '''
        tell application "System Events"
            tell process "WeChat"
                if (count of windows) = 0 then
                    return "no_window"
                end if

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

        try:
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=5)
            output = result.stdout.strip()
            if output == "no_window":
                return None

            parts = output.replace(' ', '').split(',')
            x, y, w, h = map(int, parts)
            return {'x': x, 'y': y, 'width': w, 'height': h}
        except Exception as e:
            logger.error(f"Error getting window bounds: {e}")
            return None

    def _get_chat_list_region(self, window_bounds: Dict) -> Dict:
        """Calculate chat list region within window"""
        chat_list_width = int(window_bounds['width'] * 0.3)
        chat_list_height = window_bounds['height'] - 100

        return {
            'x': window_bounds['x'] + 10,
            'y': window_bounds['y'] + 80,
            'width': chat_list_width,
            'height': chat_list_height
        }

    def _capture_screenshot(self, region: Dict, output_path: str):
        """Capture screenshot of region"""
        x = region['x']
        y = region['y']
        w = region['width']
        h = region['height']

        cmd = ['screencapture', '-x', '-R', f"{x},{y},{w},{h}", output_path]
        subprocess.run(cmd, capture_output=True, timeout=10)
