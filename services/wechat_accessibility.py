#!/usr/bin/env python3
"""
WeChat Accessibility Service - Extract messages using macOS Accessibility API
Much more reliable than OCR approach
"""
from Cocoa import NSWorkspace
from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    kAXErrorSuccess,
)
from typing import List, Dict, Optional
import time


class WeChatAccessibilityService:
    def __init__(self):
        self.last_message_count = 0
        self.seen_messages = set()

    def get_wechat_pid(self) -> Optional[int]:
        """Get WeChat process ID"""
        workspace = NSWorkspace.sharedWorkspace()
        apps = workspace.runningApplications()

        for app in apps:
            if app.localizedName() == "WeChat":
                return app.processIdentifier()
        return None

    def get_attribute_value(self, element, attribute):
        """Safely get an attribute value from an accessibility element"""
        try:
            error_code, value = AXUIElementCopyAttributeValue(element, attribute, None)
            if error_code == kAXErrorSuccess:
                return value
            return None
        except Exception:
            return None

    def find_message_list(self, element, depth=0, max_depth=10):
        """Recursively find the message list element"""
        if depth > max_depth:
            return None

        role = self.get_attribute_value(element, "AXRole")
        title = self.get_attribute_value(element, "AXTitle")

        # Look for AXList with title "Messages"
        if role == "AXList" and title == "Messages":
            return element

        # Search children
        children = self.get_attribute_value(element, "AXChildren")
        if children:
            for child in children:
                result = self.find_message_list(child, depth + 1, max_depth)
                if result:
                    return result

        return None

    def extract_message_text(self, element) -> Optional[str]:
        """Extract text from a message element"""
        # Try AXTitle first (most reliable)
        title = self.get_attribute_value(element, "AXTitle")
        if title and isinstance(title, str):
            return title.strip()

        # Fallback to AXValue
        value = self.get_attribute_value(element, "AXValue")
        if value and isinstance(value, str):
            return value.strip()

        return None

    def get_messages(self) -> List[Dict]:
        """
        Get all messages from the current WeChat chat
        Returns list of message dictionaries with text and metadata
        """
        pid = self.get_wechat_pid()
        if not pid:
            return []

        # Create accessibility element for WeChat
        app_element = AXUIElementCreateApplication(pid)

        # Find the message list
        message_list = self.find_message_list(app_element)
        if not message_list:
            return []

        # Get all message elements
        children = self.get_attribute_value(message_list, "AXChildren")
        if not children:
            return []

        messages = []
        for i, child in enumerate(children):
            text = self.extract_message_text(child)
            if text:
                # Get position for ordering (use index as fallback)
                y_pos = i

                messages.append({
                    "index": i,
                    "text": text,
                    "y_position": y_pos,
                    "is_agent": text.startswith("[Agent]")
                })

        return messages

    def get_new_messages(self) -> List[Dict]:
        """
        Get only new messages that haven't been seen before
        Filters out agent messages and duplicates
        """
        all_messages = self.get_messages()

        new_messages = []
        for msg in all_messages:
            # Skip agent messages
            if msg["is_agent"]:
                continue

            # Check if we've seen this message before
            msg_signature = f"{msg['text']}_{msg['index']}"
            if msg_signature not in self.seen_messages:
                self.seen_messages.add(msg_signature)
                new_messages.append(msg)

        return new_messages

    def get_latest_user_message(self) -> Optional[str]:
        """
        Get the most recent user message (non-agent)
        Returns None if no new messages
        """
        all_messages = self.get_messages()

        # Filter out agent messages and sort by index (higher = more recent)
        user_messages = [m for m in all_messages if not m["is_agent"]]

        if not user_messages:
            return None

        # Sort by index (higher = more recent)
        user_messages.sort(key=lambda x: x["index"], reverse=True)

        latest = user_messages[0]

        # Check if we've already processed this message
        # Use ONLY text as signature (index can change as messages are added/removed)
        msg_signature = latest['text']
        if msg_signature in self.seen_messages:
            return None

        self.seen_messages.add(msg_signature)

        # Keep seen_messages size manageable (last 100 messages)
        if len(self.seen_messages) > 100:
            # Convert to list, keep last 50, convert back to set
            seen_list = list(self.seen_messages)
            self.seen_messages = set(seen_list[-50:])

        return latest["text"]


# Test the service
if __name__ == "__main__":
    service = WeChatAccessibilityService()

    print("Testing WeChat Accessibility Service")
    print("=" * 60)

    # Get all messages
    messages = service.get_messages()
    print(f"\nTotal messages: {len(messages)}")

    # Show last 5 messages
    print("\nLast 5 messages:")
    for msg in messages[-5:]:
        prefix = "[AGENT]" if msg["is_agent"] else "[USER] "
        print(f"{prefix} {msg['text']}")

    # Test new message detection
    print("\n" + "=" * 60)
    print("Testing new message detection...")
    print("Send a message in WeChat now!")

    for i in range(10):
        time.sleep(2)
        new_msg = service.get_latest_user_message()
        if new_msg:
            print(f"\n✅ New message detected: {new_msg}")
            break
        print(f"  Checking... ({i+1}/10)")
    else:
        print("\n  No new messages detected")
