#!/usr/bin/env python3
"""
Send a test message ONLY to File Transfer chat
"""
import subprocess
import sys

def send_to_file_transfer(message):
    """Send message specifically to File Transfer chat"""

    # Write message to temp file
    with open('/tmp/test_msg.txt', 'w') as f:
        f.write(message)

    script = '''
    set msg to do shell script "cat /tmp/test_msg.txt"

    tell application "WeChat"
        activate
    end tell
    delay 0.8

    tell application "System Events"
        tell process "WeChat"
            -- Open search (Cmd+F)
            keystroke "f" using {command down}
            delay 0.4

            -- Clear any existing search
            keystroke "a" using {command down}
            delay 0.1
            key code 51  -- Delete
            delay 0.3

            -- Type "File Transfer" exactly
            keystroke "File Transfer"
            delay 1.0

            -- Press Down arrow to select first result
            key code 125  -- Down arrow
            delay 0.3

            -- Press Enter to open the chat
            key code 36  -- Enter
            delay 0.8

            -- Close search (ESC)
            key code 53  -- ESC
            delay 0.3

            -- Type the message
            keystroke msg
            delay 0.4

            -- Send with Enter
            key code 36  -- Enter
            delay 0.3

            return "SUCCESS"
        end tell
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=20,
            check=True
        )
        print(f"✅ Message sent successfully to File Transfer chat!")
        print(f"📨 Message: \"{message}\"")
        return True
    except subprocess.TimeoutExpired:
        print("❌ Error: Command timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.output}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Test message
    test_message = "Hello! This is a test message from RealChat. Please reply to verify the agent is working."

    print("🎯 Sending test message to File Transfer chat...")
    print(f"📝 Message: \"{test_message}\"")
    print("-" * 60)

    success = send_to_file_transfer(test_message)

    if success:
        print("-" * 60)
        print("✅ Done! Message sent to File Transfer chat only.")
        print("💡 The agent should detect and respond within 3-6 seconds.")
        print("📊 Monitor agent activity: tail -f /tmp/agent.log")
        sys.exit(0)
    else:
        print("-" * 60)
        print("❌ Failed to send message.")
        sys.exit(1)
