#!/usr/bin/env python3
"""
Test script to explore WeChat's accessibility hierarchy
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


def get_attribute_names(element):
    """Get all attribute names for an element"""
    try:
        error_code, names = AXUIElementCopyAttributeNames(element, None)
        if error_code == kAXErrorSuccess:
            return names
        return []
    except Exception as e:
        return []


def explore_element(element, depth=0, max_depth=5):
    """Recursively explore accessibility element hierarchy"""
    if depth > max_depth:
        return

    indent = "  " * depth

    # Get basic info
    role = get_attribute_value(element, "AXRole")
    title = get_attribute_value(element, "AXTitle")
    value = get_attribute_value(element, "AXValue")
    description = get_attribute_value(element, "AXDescription")

    # Print element info
    print(f"{indent}Role: {role}")
    if title:
        print(f"{indent}  Title: {title}")
    if value:
        print(f"{indent}  Value: {value}")
    if description:
        print(f"{indent}  Description: {description}")

    # Get children
    children = get_attribute_value(element, "AXChildren")
    if children:
        print(f"{indent}  Children: {len(children)}")
        for i, child in enumerate(children):
            if i < 10:  # Limit to first 10 children per level
                print(f"{indent}  --- Child {i} ---")
                explore_element(child, depth + 1, max_depth)


def main():
    pid = get_wechat_pid()
    if not pid:
        print("WeChat is not running")
        return

    print(f"Found WeChat with PID: {pid}")

    # Create accessibility element for WeChat
    app_element = AXUIElementCreateApplication(pid)

    print("\n=== WeChat Accessibility Hierarchy ===\n")
    explore_element(app_element, max_depth=3)


if __name__ == "__main__":
    main()
