#!/usr/bin/env python3
"""
Test script to extract messages from WeChat using accessibility API
"""
import Quartz
from Cocoa import NSWorkspace
from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeNames,
    AXUIElementCopyAttributeValue,
    kAXErrorSuccess,
)
import sys


def get_wechat_pid():
    """Get WeChat process ID"""
    workspace = NSWorkspace.sharedWorkspace()
    apps = workspace.runningApplications()

    for app in apps:
        if app.localizedName() == "WeChat":
            return app.processIdentifier()
    return None


def get_attribute_value(element, attribute):
    """Safely get an attribute value from an accessibility element"""
    try:
        error_code, value = AXUIElementCopyAttributeValue(element, attribute, None)
        if error_code == kAXErrorSuccess:
            return value
        return None
    except Exception as e:
        return None


def get_all_attributes(element):
    """Get all attributes and their values for an element"""
    try:
        error_code, names = AXUIElementCopyAttributeNames(element, None)
        if error_code != kAXErrorSuccess:
            return {}

        attributes = {}
        for name in names:
            value = get_attribute_value(element, name)
            if value is not None and name not in ['AXChildren', 'AXParent', 'AXWindow', 'AXTopLevelUIElement']:
                attributes[name] = value
        return attributes
    except Exception as e:
        return {}


def find_message_list(element, depth=0, max_depth=10):
    """Recursively find the message list element"""
    if depth > max_depth:
        return None

    role = get_attribute_value(element, "AXRole")
    title = get_attribute_value(element, "AXTitle")

    # Look for AXList with title "Messages"
    if role == "AXList" and title == "Messages":
        return element

    # Search children
    children = get_attribute_value(element, "AXChildren")
    if children:
        for child in children:
            result = find_message_list(child, depth + 1, max_depth)
            if result:
                return result

    return None


def explore_message_element(element, depth=0):
    """Recursively explore a message element to extract all text"""
    role = get_attribute_value(element, "AXRole")
    value = get_attribute_value(element, "AXValue")
    title = get_attribute_value(element, "AXTitle")
    description = get_attribute_value(element, "AXDescription")

    texts = []

    # Collect text from this element
    if value and isinstance(value, str):
        texts.append(value)
    if title and isinstance(title, str) and title != value:
        texts.append(title)
    if description and isinstance(description, str) and description not in [value, title]:
        texts.append(description)

    # Recursively get text from children
    children = get_attribute_value(element, "AXChildren")
    if children:
        for child in children:
            child_texts = explore_message_element(child, depth + 1)
            texts.extend(child_texts)

    return texts


def extract_messages(message_list):
    """Extract all messages from the message list"""
    children = get_attribute_value(message_list, "AXChildren")
    if not children:
        return []

    messages = []
    for i, child in enumerate(children):
        # Get all attributes
        attrs = get_all_attributes(child)

        # Get role
        role = get_attribute_value(child, "AXRole")

        # Extract all text from this message element
        texts = explore_message_element(child)

        message_info = {
            "index": i,
            "role": role,
            "attributes": attrs,
            "texts": texts,
            "combined_text": " ".join(texts) if texts else ""
        }

        messages.append(message_info)

    return messages


def main():
    pid = get_wechat_pid()
    if not pid:
        print("WeChat is not running")
        return

    print(f"Found WeChat with PID: {pid}\n")

    # Create accessibility element for WeChat
    app_element = AXUIElementCreateApplication(pid)

    # Find the message list
    print("Searching for message list...")
    message_list = find_message_list(app_element)

    if not message_list:
        print("Could not find message list")
        return

    print("Found message list!\n")

    # Extract messages
    messages = extract_messages(message_list)

    print(f"Found {len(messages)} message elements\n")
    print("=" * 80)

    # Print last 10 messages
    for msg in messages[-10:]:
        print(f"\nMessage {msg['index']}:")
        print(f"  Role: {msg['role']}")
        print(f"  Combined Text: {msg['combined_text']}")
        if msg['attributes']:
            print(f"  Attributes: {list(msg['attributes'].keys())}")

    print("\n" + "=" * 80)
    print("\nLast 5 messages (detailed):")
    for msg in messages[-5:]:
        print(f"\n--- Message {msg['index']} ---")
        print(f"Role: {msg['role']}")
        print(f"All texts found: {msg['texts']}")
        print(f"Attributes: {msg['attributes']}")


if __name__ == "__main__":
    main()
