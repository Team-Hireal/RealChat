#!/usr/bin/env python3
"""
New message detector for WeChat
Monitors chat sidebar for changes to trigger OCR
"""
import subprocess
import time
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class NewMessageDetector:
    """Detects new messages by monitoring WeChat chat sidebar"""

    def __init__(self):
        self.last_chat_state = {}
        self.last_check_time = 0

    def get_chat_sidebar_info(self) -> Optional[Dict]:
        """
        Get information from chat sidebar (unread counts, last messages)

        Returns:
            Dict with chat information or None
        """
        try:
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    if (count of windows) = 0 then
                        return "no_window"
                    end if

                    set mainWindow to window 1

                    -- Get all UI elements
                    set allElements to entire contents of mainWindow

                    -- Look for chat list items (usually in left sidebar)
                    set chatInfo to {}

                    repeat with elem in allElements
                        try
                            set elemRole to role of elem
                            set elemValue to value of elem

                            -- Look for text elements that might be chat names or message previews
                            if elemRole is "AXStaticText" and elemValue is not missing value then
                                if elemValue is not "" and (length of elemValue) > 0 then
                                    set end of chatInfo to elemValue
                                end if
                            end if
                        end try
                    end repeat

                    -- Return as comma-separated list
                    set AppleScript's text item delimiters to "|"
                    return chatInfo as text
                end tell
            end tell
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=10)
            output = result.stdout.strip()

            if output == "no_window" or not output:
                return None

            # Parse chat info
            chat_items = output.split('|')

            return {
                'items': chat_items,
                'count': len(chat_items),
                'hash': hash(output),  # Quick way to detect changes
                'timestamp': time.time()
            }

        except Exception as e:
            logger.error(f"Error getting chat sidebar info: {e}")
            return None

    def has_new_message(self, current_chat: str = None) -> bool:
        """
        Check if there's a new message by comparing sidebar state

        Args:
            current_chat: Name of currently open chat (to filter out)

        Returns:
            bool: True if new message detected
        """
        try:
            current_state = self.get_chat_sidebar_info()

            if not current_state:
                return False

            # First check - initialize state
            if not self.last_chat_state:
                self.last_chat_state = current_state
                return False

            # Compare hash to detect any changes
            if current_state['hash'] != self.last_chat_state['hash']:
                logger.info("Chat sidebar changed - possible new message")

                # Update state
                old_state = self.last_chat_state
                self.last_chat_state = current_state

                # Check if item count increased (new chat or message)
                if current_state['count'] > old_state['count']:
                    logger.info(f"New items detected: {current_state['count']} vs {old_state['count']}")
                    return True

                # Check if any items changed (message preview updated)
                old_items = set(old_state['items'])
                new_items = set(current_state['items'])

                if new_items != old_items:
                    logger.info("Chat items changed - new message likely")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking for new messages: {e}")
            return False

    def get_unread_indicator(self) -> Optional[int]:
        """
        Try to get unread message count from WeChat

        Returns:
            Number of unread messages or None
        """
        try:
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    if (count of windows) = 0 then
                        return "0"
                    end if

                    -- Try to find unread badge/indicator
                    -- This is app-specific and may need adjustment
                    set mainWindow to window 1
                    set allElements to entire contents of mainWindow

                    -- Look for elements that might contain unread count
                    repeat with elem in allElements
                        try
                            set elemValue to value of elem
                            if elemValue is not missing value then
                                -- Check if it's a number (unread count)
                                try
                                    set numValue to elemValue as number
                                    if numValue > 0 and numValue < 1000 then
                                        return elemValue as text
                                    end if
                                end try
                            end if
                        end try
                    end repeat

                    return "0"
                end tell
            end tell
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=5)
            output = result.stdout.strip()

            try:
                return int(output)
            except:
                return None

        except Exception as e:
            logger.error(f"Error getting unread indicator: {e}")
            return None

    def should_trigger_ocr(self, check_interval: float = 2.0) -> bool:
        """
        Determine if OCR should be triggered

        Args:
            check_interval: Minimum seconds between checks

        Returns:
            bool: True if OCR should run
        """
        current_time = time.time()

        # Rate limiting
        if current_time - self.last_check_time < check_interval:
            return False

        self.last_check_time = current_time

        # Check for new messages
        return self.has_new_message()
