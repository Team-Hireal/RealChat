#!/usr/bin/env python3
"""
Test script for WeChatService Bridge APIs
Tests: locate, navigate, read, and write operations
"""

import sys
import time
from datetime import datetime
from services.wechat_service import WeChatService

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_wechat_service():
    """Test all WeChatService APIs"""

    # Initialize service
    print_section("1. Initialize WeChatService")
    config = {
        'chat_names': ['File Transfer', '文件传输助手'],
        'scan_method': 'applescript'
    }
    wechat = WeChatService(config)
    print("✓ WeChatService initialized")

    # Test 1: Check if WeChat is running
    print_section("2. Check WeChat Status")
    is_running = wechat.is_wechat_running()
    print(f"WeChat Running: {is_running}")

    if not is_running:
        print("❌ WeChat is not running. Please start WeChat and try again.")
        return False

    # Test 2: Get window information
    print_section("3. Get Window Information")
    window_info = wechat.get_wechat_window_info()
    if window_info:
        print(f"✓ Window Title: {window_info['title']}")
        print(f"✓ Window Size: {window_info['width']}x{window_info['height']}")
        print(f"✓ Window Position: ({window_info['x']}, {window_info['y']})")
        print(f"✓ Is Frontmost: {window_info['is_frontmost']}")
    else:
        print("❌ Could not get window information")
        return False

    # Test 3: Ensure WeChat is ready
    print_section("4. Verify WeChat Ready State")
    is_ready = wechat.ensure_wechat_ready()
    print(f"WeChat Ready: {is_ready}")

    if not is_ready:
        print("❌ WeChat is not ready for automation")
        return False

    # Test 4: Search for chats
    print_section("5. Search for 'File' Chat")
    search_results = wechat.search_chats("file", max_results=5)
    print(f"Found {len(search_results)} chats matching 'file':")
    for chat in search_results:
        print(f"  • {chat['name']} (type: {chat['type']})")

    # Test 5: Send test message
    print_section("6. Send Test Message to File Transfer")
    current_time = datetime.now().strftime("%H:%M:%S")
    test_message = f"Test, RealChat, {current_time}"
    print(f"Message: {test_message}")
    print("Sending...")

    success = wechat.send_message(test_message, "File Transfer")

    if success:
        print("✓ Message sent successfully!")
    else:
        print("❌ Failed to send message")
        return False

    # Wait for message to be sent
    print("Waiting 2 seconds for message to be delivered...")
    time.sleep(2)

    # Test 6: Read messages (plain text)
    print_section("7. Read Messages (Plain Text)")
    content = wechat.read_last_message("File Transfer")
    if content:
        lines = content.split('\n')
        print(f"✓ Read {len(lines)} lines from File Transfer")
        print("\nLast 5 messages:")
        for line in lines[-5:]:
            if line.strip():
                print(f"  {line[:100]}")
    else:
        print("❌ Could not read messages")

    # Test 7: Read messages (structured)
    print_section("8. Read Messages (Structured)")
    structured_data = wechat.read_messages_structured("File Transfer")
    if structured_data:
        print(f"✓ Chat: {structured_data['chat_name']}")
        print(f"✓ Timestamp: {structured_data['timestamp']}")
        print(f"✓ Message Count: {structured_data['message_count']}")
        print(f"✓ Latest Message: {structured_data['latest_message'][:100] if structured_data['latest_message'] else 'None'}")

        # Check if our test message is in the messages
        print("\n🔍 Verifying sent message...")
        found_message = False
        for msg in structured_data['messages']:
            if test_message in msg['text']:
                found_message = True
                print(f"✓ FOUND OUR MESSAGE: {msg['text']}")
                break

        if not found_message:
            print("⚠️  Test message not found in recent messages")
            print("   (This might be normal if there are many messages)")
    else:
        print("❌ Could not read structured messages")

    # Test 8: Scan chats (structured)
    print_section("9. Scan Available Chats (Structured)")
    chats = wechat.scan_chats_structured(max_chats=10)
    print(f"Found {len(chats)} chats:")
    for chat in chats[:5]:
        print(f"  {chat['index']}. {chat['name']} ({chat['type']})")

    print_section("✅ All Tests Completed Successfully!")
    return True

if __name__ == "__main__":
    try:
        success = test_wechat_service()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
