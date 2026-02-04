#!/usr/bin/env python3
"""
Test script to verify WeChat chat detection
"""

import sys
sys.path.insert(0, '/Users/test/Desktop/Hireal/RealChat')

from services.wechat_service import WeChatService

# Initialize service
wechat = WeChatService()

print("=" * 60)
print("WeChat Chat Detection Test")
print("=" * 60)

# Check if WeChat is running
print(f"\n1. WeChat Running: {wechat.is_wechat_running()}")

# Get window info
window_info = wechat.get_wechat_window_info()
if window_info:
    print(f"\n2. Window Info:")
    print(f"   Title: {window_info.get('title')}")
    print(f"   Size: {window_info.get('width')}x{window_info.get('height')}")
    print(f"   Frontmost: {window_info.get('is_frontmost')}")
else:
    print("\n2. Window Info: Not available")

# Get current chat name
current_chat = wechat.get_current_chat_name()
print(f"\n3. Current Chat: {current_chat or 'Not detected'}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
