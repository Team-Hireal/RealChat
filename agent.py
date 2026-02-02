#!/usr/bin/env python3
"""
RealChat Backend - Simple AI Chat Agent
Monitors WeChat and responds with AI
"""

import os
import time
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
AI_API_KEY = os.getenv('AI_API_KEY')
AI_BASE_URL = os.getenv('AI_BASE_URL')
AI_MODEL = os.getenv('AI_MODEL', 'claude-sonnet-4-5-20250929')
# Try both English and Chinese names for File Transfer chat
CHAT_NAMES = ["File Transfer", "文件传输助手"]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def send_message(text):
    """Send message to WeChat File Transfer Assistant with verification"""
    # Write to temp file
    with open('/tmp/msg.txt', 'w') as f:
        f.write(text)

    # Try both chat names
    for chat_name in CHAT_NAMES:
        script = f'''
        set msg to do shell script "cat /tmp/msg.txt"

        tell application "WeChat"
            activate
        end tell
        delay 0.8

        tell application "System Events"
            tell process "WeChat"
                -- Step 1: Open search (Cmd+F)
                keystroke "f" using {{command down}}
                delay 0.4

                -- Step 2: Clear any existing search
                keystroke "a" using {{command down}}
                delay 0.1
                key code 51  -- Delete
                delay 0.3

                -- Step 3: Type the chat name
                keystroke "{chat_name}"
                delay 1.0

                -- Step 4: Press Down arrow to select first result
                key code 125  -- Down arrow
                delay 0.3

                -- Step 5: Press Enter to open the chat
                key code 36  -- Enter
                delay 0.8

                -- Step 6: Close search (ESC)
                key code 53  -- ESC
                delay 0.3

                -- Step 7: Type the message
                keystroke msg
                delay 0.4

                -- Step 8: Send with Enter
                key code 36  -- Enter
                delay 0.3

                return "SUCCESS"
            end tell
        end tell
        '''

        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=20, check=True)
            return True
        except Exception as e:
            # Try next chat name
            continue

    log(f"Send error: Failed with all chat names")
    return False

def get_ai_response(user_msg):
    """Get AI response"""
    try:
        resp = requests.post(
            f"{AI_BASE_URL}/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": AI_API_KEY,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": AI_MODEL,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": f"You are a friendly AI assistant. User said: {user_msg}. Respond briefly and conversationally."}]
            },
            timeout=30
        )
        return resp.json()['content'][0]['text']
    except Exception as e:
        log(f"AI error: {e}")
        return None

def read_last_message():
    """Read last message from WeChat"""
    # Try both chat names
    for chat_name in CHAT_NAMES:
        script = f'''
        tell application "WeChat" to activate
        delay 0.5
        tell application "System Events"
            tell process "WeChat"
                keystroke "f" using {{command down}}
                delay 0.3
                keystroke "a" using {{command down}}
                delay 0.1
                key code 51
                delay 0.2
                keystroke "{chat_name}"
                delay 0.7
                key code 125  -- Down arrow
                delay 0.3
                key code 36  -- Enter
                delay 0.5
                key code 53  -- ESC
                delay 0.3
                keystroke "a" using {{command down}}
                delay 0.2
                keystroke "c" using {{command down}}
                delay 0.3
            end tell
        end tell
        return the clipboard
        '''

        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            continue
    return None

def main():
    log("🤖 RealChat AI Agent Starting...")
    log(f"📱 Monitoring: {CHAT_NAMES[0]} / {CHAT_NAMES[1]}")

    # Send startup message
    log("📤 Sending startup message...")
    if send_message("RealChat AI is active! Reply to chat with me."):
        log("✅ Startup message sent!")
    else:
        log("❌ Failed to send startup message")
        return

    last_msg = "RealChat AI is active! Reply to chat with me."

    log("👀 Monitoring for messages...")

    while True:
        try:
            # Read messages
            full_text = read_last_message()

            if full_text:
                # Get last line
                lines = [l.strip() for l in full_text.split('\n') if l.strip()]
                if lines:
                    latest = lines[-1]

                    # Check if new and not from us
                    if latest != last_msg and "RealChat" not in latest:
                        log(f"📨 New: {latest[:50]}...")

                        # Get AI response
                        log("🤔 Thinking...")
                        ai_resp = get_ai_response(latest)

                        if ai_resp:
                            log(f"💬 AI: {ai_resp[:50]}...")

                            # Send
                            if send_message(ai_resp):
                                log("✅ Sent!")
                                last_msg = ai_resp
                            else:
                                log("❌ Send failed")

            time.sleep(3)

        except KeyboardInterrupt:
            log("👋 Stopping...")
            break
        except Exception as e:
            log(f"❌ Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
