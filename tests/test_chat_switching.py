#!/usr/bin/env python3
"""
Test Suite: Chat Switching & Command Parsing
Tests the core chat switching capability safely (File Transfer only).

Usage:
    ./venv/bin/python tests/test_chat_switching.py
    ./venv/bin/python tests/test_chat_switching.py --live   # Run live WeChat tests
"""

import sys
import os
import time
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.command_parser import CommandParser, CommandExecutor


# ============================================================================
# Unit Tests: Command Parser (no WeChat needed)
# ============================================================================

def test_command_parser():
    """Test command parsing with various input formats"""
    parser = CommandParser()
    passed = 0
    failed = 0

    test_cases = [
        # Structured commands
        ("help", "help", None),
        ("status", "status", None),
        ("list chats", "list_chats", None),
        ("monitor John", "monitor", ["John"]),
        ("switch to Mom", "switch", ["Mom"]),
        ("stop monitoring", "stop_monitor", None),
        ("check messages", "check_messages", None),
        ("auto-reply", "auto_reply", None),
        ("auto reply on", "auto_reply", None),

        # Natural language - chat switching
        ("help me chat to John", "switch", ["John"]),
        ("talk to Mom", "switch", ["Mom"]),
        ("message David", "switch", ["David"]),
        ("I want to chat to Sarah", "switch", ["Sarah"]),
        ("can you open the chat with Boss", "switch", ["Boss"]),
        ("let's talk to Mike", "switch", ["Mike"]),
        ("go to Work Group", "switch", ["Work Group"]),
        ("switch back to File Transfer", "switch", ["File Transfer"]),
        ("text to Alice please", "switch", ["Alice"]),
        ("help me chat to John please", "switch", ["John"]),

        # Natural language - check messages
        ("check all my messages", "check_messages", None),
        ("any new messages", "check_messages", None),
        ("what needs my response", "check_messages", None),
        ("go through my messages", "check_messages", None),
        ("do i have any unread messages", "check_messages", None),
        ("see if anything needs my reply", "check_messages", None),

        # Natural language - auto reply
        ("handle my messages", "auto_reply", None),
        ("i'm busy", "auto_reply", None),

        # Should NOT match (regular messages)
        ("hello how are you", None, None),
        ("thanks for the info", None, None),
        ("meeting at 3pm", None, None),
    ]

    print("=" * 60)
    print("TEST: Command Parser")
    print("=" * 60)

    for message, expected_cmd, expected_args in test_cases:
        result = parser.parse(message)

        actual_cmd = result['command'] if result else None
        actual_args = result.get('args') if result else None

        # Check command match
        cmd_ok = actual_cmd == expected_cmd
        # Check args match (if expected)
        args_ok = True
        if expected_args is not None and actual_args is not None:
            args_ok = all(
                exp.lower() in act.lower()
                for exp, act in zip(expected_args, actual_args)
            )
        elif expected_args is not None and actual_args is None:
            args_ok = False

        if cmd_ok and args_ok:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"
            print(f"  [{status}] \"{message}\"")
            print(f"         Expected: cmd={expected_cmd}, args={expected_args}")
            print(f"         Got:      cmd={actual_cmd}, args={actual_args}")
            continue

        print(f"  [{status}] \"{message}\" → {actual_cmd}" +
              (f" [{', '.join(actual_args)}]" if actual_args else ""))

    print(f"\nResults: {passed} passed, {failed} failed, {passed + failed} total")
    return failed == 0


# ============================================================================
# Live Tests: WeChat Integration (requires WeChat running)
# ============================================================================

def test_live_wechat_service():
    """Test WeChat service methods (requires WeChat running)"""
    from services.wechat_service import WeChatService

    config = {
        'chat_names': ['File Transfer', '文件传输助手'],
        'scan_method': 'applescript'
    }
    service = WeChatService(config)

    print("\n" + "=" * 60)
    print("TEST: WeChat Service (Live)")
    print("=" * 60)

    # Test 1: Is WeChat running?
    running = service.is_wechat_running()
    print(f"  WeChat running: {running}")
    if not running:
        print("  SKIP: WeChat not running, skipping live tests")
        return True

    # Test 2: Get window info
    window = service.get_wechat_window_info()
    print(f"  Window info: {window}")

    # Test 3: Get current chat
    current = service.get_current_chat_name()
    print(f"  Current chat: {current}")

    # Test 4: Open File Transfer (SAFE)
    print("\n  Opening File Transfer (safe test)...")
    success = service.open_chat("File Transfer")
    print(f"  open_chat('File Transfer'): {success}")
    time.sleep(1)

    # Verify
    after = service.get_current_chat_name()
    print(f"  After switch, current chat: {after}")

    return True


def test_live_command_execution():
    """Test command execution with actual WeChat (File Transfer only)"""
    from services.wechat_service import WeChatService

    config = {
        'chat_names': ['File Transfer', '文件传输助手'],
        'scan_method': 'applescript'
    }
    service = WeChatService(config)

    if not service.is_wechat_running():
        print("  SKIP: WeChat not running")
        return True

    executor = CommandExecutor(service)
    parser = CommandParser()

    print("\n" + "=" * 60)
    print("TEST: Command Execution (Live - File Transfer only)")
    print("=" * 60)

    # Only test with File Transfer for safety
    test_commands = [
        "status",
        "help",
        "switch to File Transfer",  # Safe: switching to File Transfer
        "status",
    ]

    for cmd_text in test_commands:
        print(f"\n  Command: \"{cmd_text}\"")
        parsed = parser.parse(cmd_text)
        if parsed:
            response = executor.execute(parsed)
            # Show first 3 lines of response
            lines = response.strip().split('\n')[:3]
            for line in lines:
                print(f"    {line}")
            if len(response.strip().split('\n')) > 3:
                print(f"    ... ({len(response.strip().split(chr(10)))} lines total)")
        else:
            print(f"    Not recognized as command")
        time.sleep(0.5)

    return True


def test_live_send_to_file_transfer():
    """Test sending a message to File Transfer (safe)"""
    from services.wechat_service import WeChatService

    config = {
        'chat_names': ['File Transfer', '文件传输助手'],
        'scan_method': 'applescript'
    }
    service = WeChatService(config)

    if not service.is_wechat_running():
        print("  SKIP: WeChat not running")
        return True

    print("\n" + "=" * 60)
    print("TEST: Send Message to File Transfer (Safe)")
    print("=" * 60)

    # First make sure we're in File Transfer
    service.open_chat("File Transfer")
    time.sleep(1)

    # Send a test message
    test_msg = f"[Agent] Test message at {time.strftime('%H:%M:%S')}"
    print(f"  Sending: \"{test_msg}\"")
    success = service.send_message(test_msg)
    print(f"  Result: {'SUCCESS' if success else 'FAILED'}")

    return success


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Test chat switching')
    arg_parser.add_argument('--live', action='store_true',
                           help='Run live WeChat tests')
    args = arg_parser.parse_args()

    print("\n🧪 HiChat - Chat Switching Test Suite\n")

    all_passed = True

    # Always run unit tests
    if not test_command_parser():
        all_passed = False

    # Run live tests if requested
    if args.live:
        if not test_live_wechat_service():
            all_passed = False
        if not test_live_command_execution():
            all_passed = False
        if not test_live_send_to_file_transfer():
            all_passed = False
    else:
        print("\n💡 Run with --live to test actual WeChat integration")

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
