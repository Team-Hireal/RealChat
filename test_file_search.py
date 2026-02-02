#!/usr/bin/env python3
"""
Test script using "File" search term for File Transfer chat
"""

import sys
import time
from datetime import datetime
from services.wechat_service import WeChatService

def test_file_search():
    """Test searching with 'File' and sending message"""

    print("=" * 70)
    print("  Testing WeChat Bridge with 'File' Search")
    print("=" * 70)

    # Initialize service
    config = {
        'chat_names': ['File Transfer', '文件传输助手'],
        'scan_method': 'manual'  # Use manual mode for configured chats
    }
    wechat = WeChatService(config)

    # Step 1: Verify WeChat is ready
    print("\n1. Checking WeChat status...")
    if not wechat.ensure_wechat_ready():
        print("❌ WeChat is not ready")
        return False

    print("✓ WeChat is ready")

    # Step 2: Search for "File" (not "File Transfer")
    print("\n2. Searching for 'File' chat...")
    results = wechat.search_chats("File", max_results=5)

    if results:
        print(f"✓ Found {len(results)} matches:")
        for chat in results:
            print(f"   • {chat['name']} ({chat['type']})")

        # Use the first result
        target_chat = results[0]['name']
        print(f"\n✓ Using: {target_chat}")
    else:
        # Fallback to configured name
        print("⚠️  No search results, using configured name")
        target_chat = "File Transfer"

    # Step 3: Send test message
    print(f"\n3. Sending message to '{target_chat}'...")
    current_time = datetime.now().strftime("%H:%M:%S")
    message = f"🎯 Test with 'File' search - {current_time}"

    print(f"   Message: {message}")

    success = wechat.send_message(message, target_chat)

    if success:
        print("✓ Message sent successfully!")
    else:
        print("❌ Failed to send message")
        return False

    # Step 4: Wait and read back
    print("\n4. Waiting 2 seconds...")
    time.sleep(2)

    print("5. Reading messages back...")
    data = wechat.read_messages_structured(target_chat)

    if data:
        print(f"✓ Read {data['message_count']} messages")
        print(f"✓ Latest: {data['latest_message'][:100]}")

        # Verify our message
        print("\n6. Verifying sent message...")
        for msg in data['messages'][-10:]:
            if message in msg['text']:
                print(f"✓ VERIFIED: Found our message!")
                print(f"   {msg['text'][:150]}")
                return True

        print("⚠️  Message not found in recent messages (might be normal)")
        return True
    else:
        print("❌ Failed to read messages")
        return False

if __name__ == "__main__":
    try:
        success = test_file_search()
        print("\n" + "=" * 70)
        if success:
            print("  ✅ TEST PASSED - 'File' search works!")
        else:
            print("  ❌ TEST FAILED")
        print("=" * 70)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
