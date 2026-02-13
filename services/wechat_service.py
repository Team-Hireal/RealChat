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
        self.chat_cache = []  # Cache for scanned chats
        self.chat_cache_time = 0  # Timestamp of last scan

        # Initialize OCR and message detector
        self.ocr_reader = None
        self.message_detector = None
        self.accessibility_service = None  # NEW: Accessibility API service
        self._init_ocr_components()
        self._init_accessibility()  # NEW: Initialize Accessibility API

    def _init_accessibility(self):
        """Initialize Accessibility API service (better than OCR)"""
        try:
            from services.wechat_accessibility import WeChatAccessibilityService
            self.accessibility_service = WeChatAccessibilityService()
            logger.info("✅ Accessibility API initialized (100% accurate, no OCR errors)")
        except Exception as e:
            logger.warning(f"Could not initialize Accessibility API: {e}")

    def arrange_windows_side_by_side(self):
        """
        Arrange WeChat (right half) and browser (left half) on the current display.
        Uses pure AppleScript to avoid Cocoa/AppleScript coordinate system mismatches.
        """
        try:
            # Single AppleScript that gets screen size and positions both windows
            # Uses Finder desktop bounds (already in AppleScript coordinates)
            script = '''
            -- Get screen dimensions from Finder desktop
            tell application "Finder"
                set _b to bounds of window of desktop
                set screenW to item 3 of _b
                set screenH to item 4 of _b
            end tell

            -- Menu bar height (standard macOS)
            set menuBarH to 25
            set halfW to (screenW / 2) as integer
            set availH to screenH - menuBarH

            -- Position WeChat on the RIGHT half (starts at center, extends to right edge)
            tell application "System Events"
                tell process "WeChat"
                    if (count of windows) > 0 then
                        set position of window 1 to {halfW, menuBarH}
                        set size of window 1 to {halfW, availH}
                    end if
                end tell
            end tell

            -- Position browser on the LEFT half
            set browserFound to false

            if application "Google Chrome" is running then
                tell application "System Events"
                    tell process "Google Chrome"
                        if (count of windows) > 0 then
                            set position of window 1 to {0, menuBarH}
                            set size of window 1 to {halfW, availH}
                            set browserFound to true
                        end if
                    end tell
                end tell
            end if

            if not browserFound and application "Safari" is running then
                tell application "System Events"
                    tell process "Safari"
                        if (count of windows) > 0 then
                            set position of window 1 to {0, menuBarH}
                            set size of window 1 to {halfW, availH}
                            set browserFound to true
                        end if
                    end tell
                end tell
            end if

            if not browserFound and application "Arc" is running then
                tell application "System Events"
                    tell process "Arc"
                        if (count of windows) > 0 then
                            set position of window 1 to {0, menuBarH}
                            set size of window 1 to {halfW, availH}
                        end if
                    end tell
                end tell
            end if

            return "OK:" & screenW & "x" & screenH
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                logger.info(f"Windows arranged side-by-side: {result.stdout.strip()}")
            else:
                logger.error(f"AppleScript error: {result.stderr.strip()}")

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Error arranging windows: {e}")
            return False

    def _init_ocr_components(self):
        """Initialize OCR and message detection components"""
        try:
            from services.wechat_ocr import WeChatOCR
            from services.message_detector import NewMessageDetector

            self.ocr_reader = WeChatOCR()
            self.message_detector = NewMessageDetector()
            logger.info("OCR components initialized")
        except Exception as e:
            logger.warning(f"Could not initialize OCR components: {e}")

    def read_messages_ocr(self) -> List[Dict]:
        """
        Read messages using OCR (DEPRECATED - use read_messages_accessibility instead)

        Returns:
            List of message dictionaries
        """
        if not self.ocr_reader:
            logger.error("OCR reader not initialized")
            return []

        try:
            messages = self.ocr_reader.read_messages()
            logger.info(f"OCR read {len(messages)} messages")
            return messages
        except Exception as e:
            logger.error(f"Error reading messages with OCR: {e}")
            return []

    def read_messages_accessibility(self) -> List[Dict]:
        """
        Read messages using Accessibility API (RECOMMENDED - 100% accurate)

        Returns:
            List of message dictionaries with only NEW user messages
        """
        if not self.accessibility_service:
            logger.warning("Accessibility API not available, falling back to OCR")
            return self.read_messages_ocr()

        try:
            # Get the latest user message (automatically filters agent messages)
            latest_message = self.accessibility_service.get_latest_user_message()

            if latest_message:
                logger.info(f"✅ Accessibility API detected new message: {latest_message[:50]}...")
                return [{
                    'timestamp': 'Now',
                    'text': latest_message,
                    'is_agent': False
                }]
            else:
                return []

        except Exception as e:
            logger.error(f"Error reading messages with Accessibility API: {e}")
            logger.warning("Falling back to OCR")
            return self.read_messages_ocr()

    def get_new_messages_ocr(self) -> List[Dict]:
        """
        Get only new messages since last check using OCR

        Returns:
            List of new message dictionaries
        """
        if not self.ocr_reader:
            logger.error("OCR reader not initialized")
            return []

        try:
            new_messages = self.ocr_reader.get_new_messages()
            logger.info(f"Found {len(new_messages)} new messages")
            return new_messages
        except Exception as e:
            logger.error(f"Error getting new messages: {e}")
            return []

    def has_new_message(self) -> bool:
        """
        Check if there's a new message by monitoring sidebar

        Returns:
            bool: True if new message detected
        """
        if not self.message_detector:
            return False

        try:
            return self.message_detector.has_new_message()
        except Exception as e:
            logger.error(f"Error checking for new messages: {e}")
            return False

    def mark_message_as_sent(self, text: str):
        """Mark a message as sent by agent (to filter it out from OCR)"""
        if self.ocr_reader:
            self.ocr_reader.mark_as_agent_message(text)

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

    def is_wechat_frontmost(self) -> bool:
        """Check if WeChat is the frontmost (active) application"""
        try:
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                return frontApp is "WeChat"
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=5)
            return result.stdout.strip() == 'true'
        except Exception as e:
            logger.error(f"Error checking if WeChat is frontmost: {e}")
            return False

    def get_cursor_position(self) -> Optional[Dict]:
        """Get current cursor position using Quartz (faster and more reliable)"""
        try:
            from Quartz import CGEventGetLocation, CGEventCreate

            # Get cursor position using Quartz
            event = CGEventCreate(None)
            cursor_pos = CGEventGetLocation(event)

            return {
                'x': int(cursor_pos.x),
                'y': int(cursor_pos.y)
            }
        except ImportError:
            # Fallback to AppleScript if Quartz not available
            logger.warning("Quartz not available, falling back to AppleScript")
            try:
                script = '''
                use framework "Foundation"
                use framework "AppKit"

                set mouseLocation to current application's NSEvent's mouseLocation()
                set x to (x of mouseLocation) as integer
                set y to (y of mouseLocation) as integer

                return (x as string) & "," & (y as string)
                '''
                result = subprocess.run(['osascript', '-e', script],
                                      capture_output=True, text=True, timeout=5)
                output = result.stdout.strip()
                if output and ',' in output:
                    x, y = map(int, output.split(','))
                    return {'x': x, 'y': y}
            except Exception as e:
                logger.error(f"Error getting cursor position via AppleScript: {e}")
                return None
        except Exception as e:
            logger.error(f"Error getting cursor position: {e}")
            return None

    def get_window_under_cursor(self) -> Optional[Dict]:
        """Get the window and process under the cursor using Quartz"""
        try:
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            from Quartz import CGEventGetLocation, CGEventCreate

            # Get cursor position using Quartz
            event = CGEventCreate(None)
            cursor_pos = CGEventGetLocation(event)
            cursor_x = int(cursor_pos.x)
            cursor_y = int(cursor_pos.y)

            # Get all on-screen windows
            window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)

            # Find window under cursor (check from front to back)
            for window in window_list:
                bounds = window.get('kCGWindowBounds', {})
                x = bounds.get('X', 0)
                y = bounds.get('Y', 0)
                w = bounds.get('Width', 0)
                h = bounds.get('Height', 0)

                # Check if cursor is within this window
                if x <= cursor_x <= x + w and y <= cursor_y <= y + h:
                    owner = window.get('kCGWindowOwnerName', 'Unknown')
                    window_id = window.get('kCGWindowNumber', 0)
                    window_name = window.get('kCGWindowName', '')
                    layer = window.get('kCGWindowLayer', 0)

                    # Only report windows at layer 0 (normal application windows)
                    if layer == 0:
                        return {
                            'process_name': owner,
                            'window_name': window_name or owner,
                            'window_id': window_id,
                            'cursor_x': cursor_x,
                            'cursor_y': cursor_y,
                            'layer': layer
                        }

            # No window found at layer 0
            return {
                'process_name': 'Unknown',
                'window_name': 'Unknown',
                'window_id': 0,
                'cursor_x': cursor_x,
                'cursor_y': cursor_y,
                'layer': -1
            }

        except ImportError:
            logger.warning("Quartz not available, falling back to AppleScript")
            # Fallback to cursor position only
            cursor = self.get_cursor_position()
            if cursor:
                return {
                    'process_name': 'Unknown',
                    'window_name': 'Unknown',
                    'window_id': 0,
                    'cursor_x': cursor['x'],
                    'cursor_y': cursor['y'],
                    'layer': -1
                }
            return None
        except Exception as e:
            logger.error(f"Error getting window under cursor: {e}")
            return None

    def is_cursor_in_wechat_window(self) -> bool:
        """Check if cursor is within WeChat window bounds"""
        try:
            # Get window bounds
            window_info = self.get_wechat_window_info()
            if not window_info:
                return False

            # Get cursor position
            cursor = self.get_cursor_position()
            if not cursor:
                return False

            # Check if cursor is within window bounds
            x, y = cursor['x'], cursor['y']
            wx, wy = window_info['x'], window_info['y']
            ww, wh = window_info['width'], window_info['height']

            in_bounds = (wx <= x <= wx + ww) and (wy <= y <= wy + wh)

            if not in_bounds:
                logger.debug(f"Cursor ({x}, {y}) outside WeChat window ({wx}, {wy}, {ww}x{wh})")

            return in_bounds
        except Exception as e:
            logger.error(f"Error checking cursor in window: {e}")
            return False

    def verify_wechat_active_and_focused(self) -> bool:
        """
        Comprehensive verification that WeChat is active and cursor is in window

        Returns:
            bool: True if WeChat is frontmost AND cursor is in WeChat window
        """
        # First check if WeChat is frontmost
        if not self.is_wechat_frontmost():
            logger.debug("WeChat is not frontmost")
            return False

        # Get window under cursor
        window_info = self.get_window_under_cursor()
        if not window_info:
            logger.debug("Could not detect window under cursor")
            return False

        # Check if cursor is over WeChat
        if window_info['process_name'] != 'WeChat':
            logger.debug(f"Cursor is over {window_info['process_name']}, not WeChat")
            return False

        logger.debug(f"Cursor is over WeChat window: {window_info['window_name']}")
        return True

    def get_wechat_window_info(self) -> Optional[Dict]:
        """Get WeChat window information including title and bounds"""
        try:
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    if (count of windows) = 0 then
                        return "no_window"
                    end if

                    set mainWindow to window 1
                    set winTitle to name of mainWindow
                    set winPosition to position of mainWindow
                    set winSize to size of mainWindow
                    set x to item 1 of winPosition
                    set y to item 2 of winPosition
                    set w to item 1 of winSize
                    set h to item 2 of winSize

                    return winTitle & "|" & (x as string) & "," & (y as string) & "," & (w as string) & "," & (h as string)
                end tell
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=5)
            output = result.stdout.strip()

            if output == "no_window":
                return None

            parts = output.split('|')
            if len(parts) != 2:
                return None

            title = parts[0]
            bounds_str = parts[1].replace(' ', '')
            x, y, w, h = map(int, bounds_str.split(','))

            return {
                'title': title,
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'is_frontmost': self.is_wechat_frontmost()
            }
        except Exception as e:
            logger.error(f"Error getting WeChat window info: {e}")
            return None

    def get_current_chat_name(self) -> Optional[str]:
        """
        Get the current chat name from WeChat window title
        Optimized for high-frequency scanning (10 Hz)

        Returns:
            str: Current chat name or None if not detected
        """
        try:
            # Fast method: Only check window title (no UI element parsing)
            # This is instant and works when a chat is actually open
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    if (count of windows) = 0 then
                        return "no_window"
                    end if

                    set mainWindow to window 1
                    set winTitle to name of mainWindow

                    -- Return the window title
                    return winTitle
                end tell
            end tell
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=1)
            output = result.stdout.strip()

            if output == "no_window" or output == "":
                return None

            # Filter out common non-chat titles
            non_chat_titles = ['WeChat', '微信', 'Chats', '聊天', 'WeChat (Window)', 'Contacts', '通讯录']
            if output in non_chat_titles:
                return None

            # Log successful detection
            logger.info(f"✅ DETECTED: '{output}'")
            return output

        except Exception as e:
            logger.error(f"Error getting current chat name: {e}")
            return None

    def ensure_wechat_ready(self) -> bool:
        """Ensure WeChat is running and ready for automation"""
        if not self.is_wechat_running():
            logger.error("WeChat is not running")
            return False

        window_info = self.get_wechat_window_info()
        if not window_info:
            logger.error("WeChat window not found")
            return False

        logger.info(f"WeChat window: {window_info['title']} ({window_info['width']}x{window_info['height']})")
        return True

    def open_chat(self, chat_name: str) -> bool:
        """
        Open a chat by name (changes window title)

        Args:
            chat_name: Name of the chat to open

        Returns:
            bool: True if chat was opened successfully
        """
        try:
            logger.info(f"Opening chat: {chat_name}")

            script = f'''
            tell application "WeChat"
                activate
            end tell
            delay 0.3

            tell application "System Events"
                tell process "WeChat"
                    -- Open search (Cmd+F)
                    keystroke "f" using {{command down}}
                    delay 0.2

                    -- Clear search field
                    keystroke "a" using {{command down}}
                    delay 0.05
                    key code 51  -- Delete
                    delay 0.1

                    -- Type chat name
                    keystroke "{chat_name}"
                    delay 0.3

                    -- Press Down arrow to select first result
                    key code 125  -- Down arrow
                    delay 0.1

                    -- Press Enter TWICE to open the chat
                    key code 36  -- Enter (selects chat)
                    delay 0.2
                    key code 36  -- Enter (opens chat)
                    delay 0.3

                    -- Close search (ESC)
                    key code 53  -- ESC
                    delay 0.1

                    return "SUCCESS"
                end tell
            end tell
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True,
                                  timeout=10, check=True)

            # Wait a moment for window title to update
            time.sleep(0.5)

            # Verify the chat is open by checking window title
            current_chat = self.get_current_chat_name()
            if current_chat and chat_name.lower() in current_chat.lower():
                logger.info(f"✅ Chat opened successfully: {current_chat}")
                return True
            else:
                logger.warning(f"⚠️ Chat may not be open. Window title: {current_chat}")
                return False

        except Exception as e:
            logger.error(f"Error opening chat: {e}")
            return False

    def send_message(self, text: str, chat_name: str = None) -> bool:
        """
        Send message to WeChat chat (simplified - assumes chat is already open)

        Args:
            text: Message content
            chat_name: Target chat name (not used in simplified version)

        Returns:
            bool: Success status
        """
        # Verify WeChat is ready (running and has window)
        if not self.ensure_wechat_ready():
            logger.error("WeChat is not ready for automation")
            return False

        logger.info(f"Sending message directly (assuming chat is already open)")

        # Write message to temp file
        temp_file = '/tmp/wechat_msg.txt'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(text)

        # Use clipboard method to preserve emojis and special characters
        script = f'''
        set msg to do shell script "cat {temp_file}"

        -- Copy message to clipboard
        set the clipboard to msg

        tell application "WeChat"
            activate
        end tell
        delay 0.2

        tell application "System Events"
            tell process "WeChat"
                -- Paste message from clipboard (preserves emojis)
                keystroke "v" using {{command down}}
                delay 0.15

                -- Send message (Enter)
                key code 36
                delay 0.1

                return "SUCCESS"
            end tell
        end tell
        '''

        try:
            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True,
                                  timeout=10, check=True)
            logger.info(f"✅ Message sent successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
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
            delay 0.2
            tell application "System Events"
                tell process "WeChat"
                    keystroke "f" using {{command down}}
                    delay 0.15
                    keystroke "a" using {{command down}}
                    delay 0.05
                    key code 51
                    delay 0.1
                    keystroke "{chat}"
                    delay 0.3
                    key code 125  -- Down arrow
                    delay 0.15
                    key code 36  -- Enter
                    delay 0.3
                    key code 53  -- ESC
                    delay 0.15
                    keystroke "a" using {{command down}}
                    delay 0.1
                    keystroke "c" using {{command down}}
                    delay 0.15
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

    def read_messages_structured(self, chat_name: str = None) -> Optional[Dict]:
        """
        Read messages from WeChat chat and return structured data

        Args:
            chat_name: Target chat name (defaults to File Transfer)

        Returns:
            Dict with structured message data or None
        """
        import time as time_module

        # Verify WeChat is ready
        if not self.ensure_wechat_ready():
            logger.error("WeChat is not ready for automation")
            return None

        # Read raw content
        content = self.read_last_message(chat_name)

        if not content:
            return None

        # Parse content into structured format
        lines = [l.strip() for l in content.split('\n') if l.strip()]

        # Build structured response
        structured_data = {
            'chat_name': chat_name or self.chat_names[0],
            'timestamp': time_module.time(),
            'raw_content': content,
            'message_count': len(lines),
            'messages': []
        }

        # Parse individual messages
        # Format: Each line is a message (simple parsing for now)
        for i, line in enumerate(lines):
            message_data = {
                'index': i,
                'text': line,
                'length': len(line)
            }
            structured_data['messages'].append(message_data)

        # Get the latest message
        if lines:
            structured_data['latest_message'] = lines[-1]
        else:
            structured_data['latest_message'] = None

        logger.info(f"Structured data: {structured_data['message_count']} messages from {structured_data['chat_name']}")

        return structured_data

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
        import time as time_module

        # Use cache if recent (within 30 seconds)
        if self.chat_cache and (time_module.time() - self.chat_cache_time) < 30:
            logger.info(f"Using cached chat list ({len(self.chat_cache)} chats)")
            return self.chat_cache[:max_chats]

        chats = []

        if self.scan_method == 'ocr':
            chats = self.scan_chats_ocr(max_chats)
        elif self.scan_method == 'applescript':
            chats = self.scan_chats_applescript(max_chats)
        else:
            # Manual mode - return configured chats
            chats = self.chat_names

        # Update cache
        if chats:
            self.chat_cache = chats
            self.chat_cache_time = time_module.time()
            logger.info(f"Updated chat cache with {len(chats)} chats")

        return chats

    def scan_chats_structured(self, max_chats: int = 10) -> List[Dict]:
        """
        Scan chats and return structured data

        Returns:
            List of chat dictionaries with metadata
        """
        import time as time_module

        chat_names = self.scan_chats(max_chats)

        structured_chats = []
        for i, chat_name in enumerate(chat_names):
            chat_data = {
                'index': i,
                'name': chat_name,
                'display_name': chat_name,
                'type': 'contact' if not any(kw in chat_name.lower() for kw in ['group', '群', 'team']) else 'group',
                'last_scan': time_module.time()
            }
            structured_chats.append(chat_data)

        logger.info(f"Structured {len(structured_chats)} chats")
        return structured_chats

    def search_chats(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for chats by name

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of matching chat dictionaries
        """
        try:
            # Get all available chats
            all_chats = self.scan_chats_structured(max_chats=20)

            # Filter chats by query (case-insensitive)
            query_lower = query.lower()
            matching_chats = [
                chat for chat in all_chats
                if query_lower in chat['name'].lower()
            ]

            # Limit results
            results = matching_chats[:max_results]

            logger.info(f"Search for '{query}' found {len(matching_chats)} matches, returning {len(results)}")
            return results

        except Exception as e:
            logger.error(f"Error searching chats: {e}")
            return []

    def scan_conversation_history(self, chat_name: str = None, max_messages: int = 50) -> Optional[Dict]:
        """
        Scan and analyze conversation history from a chat

        Args:
            chat_name: Target chat name (defaults to File Transfer)
            max_messages: Maximum number of messages to analyze

        Returns:
            Dict with conversation history analysis
        """
        logger.info(f"Scanning conversation history for {chat_name or 'File Transfer'}...")

        # Read messages using structured method
        data = self.read_messages_structured(chat_name)

        if not data:
            logger.warning("Could not read conversation history")
            return None

        # Analyze the conversation
        messages = data.get('messages', [])
        total_messages = len(messages)

        # Get recent messages
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

        # Try to identify message patterns
        user_messages = []
        bot_messages = []

        for msg in recent_messages:
            text = msg['text']
            # Identify bot messages (contain RealChat or 🤖)
            if 'RealChat' in text or '🤖' in text:
                bot_messages.append(msg)
            else:
                user_messages.append(msg)

        analysis = {
            'chat_name': data['chat_name'],
            'total_messages': total_messages,
            'scanned_messages': len(recent_messages),
            'user_messages': len(user_messages),
            'bot_messages': len(bot_messages),
            'latest_message': data.get('latest_message'),
            'messages': recent_messages,
            'can_read_history': True,
            'timestamp': data.get('timestamp')
        }

        logger.info(f"History scan complete: {total_messages} total, {len(user_messages)} user, {len(bot_messages)} bot")

        return analysis
        """
        Search for chats matching a query

        Args:
            query: Search query (case-insensitive)
            max_results: Maximum number of results

        Returns:
            List of matching chat dictionaries
        """
        all_chats = self.scan_chats_structured(max_chats=50)

        # If scan returned no results, fall back to configured chat names
        if not all_chats:
            logger.info("Scan returned no results, using configured chat names")
            all_chats = []
            for i, chat_name in enumerate(self.chat_names):
                chat_data = {
                    'index': i,
                    'name': chat_name,
                    'display_name': chat_name,
                    'type': 'contact',
                    'last_scan': time.time()
                }
                all_chats.append(chat_data)

        query_lower = query.lower()
        matches = []

        for chat in all_chats:
            if query_lower in chat['name'].lower():
                matches.append(chat)

            if len(matches) >= max_results:
                break

        logger.info(f"Found {len(matches)} chats matching '{query}'")
        return matches

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
