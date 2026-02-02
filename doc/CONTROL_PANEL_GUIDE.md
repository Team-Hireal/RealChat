# RealChat Control Panel - Quick Start Guide

## ✅ Setup Complete!

### What's Running:
- **Flask Server**: http://localhost:5001
- **Control Panel**: file:///Users/test/Desktop/Hireal/RealChat/control_panel.html

### Changes Made:

#### 1. Search Fixed to Use "File" Only ✅
- Search now uses "File" instead of "File Transfer"
- More reliable matching
- Test passed: Found "File Transfer" chat successfully

#### 2. Real-Time Control Panel Created ✅
**Features:**
- 🎛️ Real-time monitoring with WebSocket
- 📊 Live status indicators (WeChat & Agent)
- 💬 Send messages directly
- 📥 Read messages on demand
- 🪟 Window information display
- 📝 Activity log with color coding
- ⚡ Quick action buttons
- 🔄 Auto-refresh every 5 seconds

## How to Use:

### Start the System:
```bash
# Start Flask server
python3 app_consolidated.py

# Open control panel
open control_panel.html
```

### Using the Control Panel:

1. **Check Status**
   - Top right shows WeChat and Agent status
   - Green = Online/Running
   - Red = Offline/Stopped

2. **Start Agent**
   - Click "▶️ Start Agent" button
   - Agent will begin monitoring File Transfer

3. **Send Messages**
   - Type in the message box
   - Press Enter or click "Send 📤"
   - Message goes to the chat specified in "Target Chat"

4. **Read Messages**
   - Click "📥 Read Messages"
   - Latest messages appear in activity log

5. **Quick Messages**
   - Use quick action buttons for common messages
   - "👋 Hello", "🧪 Test", "📊 Status"

6. **Monitor Activity**
   - All actions appear in the activity log
   - Color coded by type:
     - Green = Success
     - Red = Error
     - Blue = Info
     - Purple = Messages
     - Yellow = Warnings

### API Endpoints Available:

```bash
# Send message
curl -X POST http://localhost:5001/api/wechat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "chat_name": "File Transfer"}'

# Read messages
curl "http://localhost:5001/api/wechat/read?chat_name=File%20Transfer&structured=true"

# Search chats (using "File")
curl "http://localhost:5001/api/wechat/chats/search?q=File"

# Get window info
curl http://localhost:5001/api/wechat/window

# Start agent
curl -X POST http://localhost:5001/api/agent/start \
  -H "Content-Type: application/json" \
  -d '{"chat_name": "File Transfer"}'

# Stop agent
curl -X POST http://localhost:5001/api/agent/stop
```

### Test Scripts:

```bash
# Test "File" search
python3 test_file_search.py

# Test all bridge APIs
python3 test_wechat_bridge.py
```

## Files Created:

1. **control_panel.html** - Real-time web control panel
2. **test_file_search.py** - Test script for "File" search
3. **test_wechat_bridge.py** - Comprehensive API test

## Tips:

- **Search Term**: Use "File" instead of "File Transfer" for better results
- **Target Chat**: Change in the sidebar to monitor different chats
- **Activity Log**: Scroll to see full history, click "Clear Logs" to reset
- **Auto-Refresh**: Status updates automatically every 5 seconds
- **WebSocket**: Real-time updates when agent detects new messages

## Troubleshooting:

**Control panel not connecting?**
- Make sure Flask server is running on port 5001
- Check browser console for errors

**Messages not sending?**
- Verify WeChat is running (check status badge)
- Ensure WeChat window is accessible
- Check activity log for error messages

**Agent not responding?**
- Click "Stop Agent" then "Start Agent" to restart
- Check that target chat is correct
- Verify WeChat is the active window

## Next Steps:

1. Open control_panel.html in your browser
2. Click "Start Agent" to begin monitoring
3. Send a test message using the message box
4. Watch the activity log for real-time updates

Enjoy your RealChat control panel! 🎉
