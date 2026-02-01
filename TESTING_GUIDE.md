# WeChat Message Testing Guide

## Overview
This guide will help you test the message sending functionality in WeChat using the File Transfer chat as a safe testing environment.

## Prerequisites
1. WeChat desktop app must be installed and running
2. You must be logged into WeChat
3. The web interface must be running at http://localhost:5001

## Testing Steps

### Step 1: Open WeChat and Navigate to File Transfer
1. Open the WeChat desktop application
2. Click on "File Transfer" (文件传输助手) in your chat list
   - This is a personal chat where you can safely test messages
   - Any messages sent here will only be visible to you

### Step 2: Test Message Sending
1. Open your browser and go to http://localhost:5001
2. In the Configuration section, you'll see two buttons:
   - **Scan Chats**: Scans available chats in WeChat
   - **Send Test Message**: Sends a test message to the currently open chat

3. With File Transfer open in WeChat, click **"Send Test Message"**
   - The button will show "Sending..." while processing
   - You should see a success message: "✓ Test message sent! Now scan chats to verify."
   - Check WeChat - you should see the test message appear in File Transfer

### Step 3: Verify Message Appears in Scan
1. Click the **"Scan Chats"** button
2. The scan will show all available chats
3. Look for File Transfer in the list
4. The scan should show the test message you just sent

## Troubleshooting

### "WeChat window not found" Error
- Make sure WeChat is running and not minimized
- Make sure you're logged in
- Try clicking the WeChat icon in the dock to bring it to the front

### Message Not Sending
- Ensure you have a chat open in WeChat (File Transfer recommended)
- Check that the input field is accessible
- Verify accessibility permissions are granted:
  - System Preferences → Security & Privacy → Privacy → Accessibility
  - Make sure Terminal or your browser has accessibility permissions

### Message Not Appearing in Scan
- Wait a few seconds after sending before scanning
- Make sure you're scanning the correct chat
- Try refreshing the WeChat window

## What's Happening Behind the Scenes

When you click "Send Test Message":
1. The web interface calls the `/api/send-test-message` endpoint
2. The backend runs `send_test_message.applescript`
3. The AppleScript:
   - Activates WeChat
   - Finds the input area (scroll area 2)
   - Clicks in the input field
   - Pastes the test message from clipboard
   - Presses Enter to send
   - Clears the clipboard

When you click "Scan Chats":
1. The web interface calls the `/api/scan-chats` endpoint
2. The backend runs `scan_chats.applescript`
3. The AppleScript reads the chat list from WeChat's accessibility API
4. Returns a JSON array of available chats

## Next Steps

Once message sending is working:
1. Test with other chats (not just File Transfer)
2. Test the auto-reply functionality
3. Configure your intro template and default reply
4. Test in dry run mode first before going live

## Files Involved

- `send_test_message.applescript` - Sends test messages
- `scan_chats.applescript` - Scans available chats
- `app.py` - Backend API endpoints
- `frontend/src/components/ConfigurationForm.jsx` - UI component
