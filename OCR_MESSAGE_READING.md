# OCR-Based Message Reading System

## Overview

Since WeChat doesn't expose message content through the accessibility API, we've implemented an **OCR-based message reading system** using macOS's built-in Vision framework.

## Architecture

### Components

1. **WeChatOCR** (`services/wechat_ocr.py`)
   - Captures screenshots of message area
   - Extracts text using Vision framework OCR
   - Parses text into structured messages
   - Filters out agent's own messages

2. **NewMessageDetector** (`services/message_detector.py`)
   - Monitors chat sidebar for changes
   - Detects new message indicators
   - Triggers OCR only when needed (efficiency)

3. **Integration** (`services/wechat_service.py`)
   - Combines OCR and detection
   - Provides unified API

## How It Works

### 1. Message Reading Flow

```
1. Capture screenshot of message area (right side of WeChat window)
2. Run Vision OCR on screenshot
3. Parse OCR text into messages (text + timestamp)
4. Filter out agent's own messages
5. Return structured message list
```

### 2. New Message Detection Flow

```
1. Monitor chat sidebar UI elements
2. Detect changes (new items, updated previews)
3. When change detected → trigger OCR
4. Extract only NEW messages (not in previous scan)
5. Add to agent context
```

### 3. Efficiency Strategy

**Problem:** OCR is computationally expensive (~1-2 seconds per scan)

**Solution:** Smart triggering
- Monitor sidebar continuously (fast, <100ms)
- Only run OCR when sidebar changes
- Cache previous messages to detect new ones
- Filter out agent's own messages

## API Endpoints

### 1. Read All Messages (OCR)
```bash
GET /api/wechat/read?ocr=true
```

**Response:**
```json
{
    "success": true,
    "method": "ocr",
    "messages": [
        {
            "timestamp": "Tuesday 22:33",
            "text": "8a50a72daf9b4c6bbf0fc0f9374cb45e",
            "is_agent": false
        },
        {
            "timestamp": "Tuesday 23:18",
            "text": "Hello!",
            "is_agent": false
        }
    ],
    "count": 2
}
```

### 2. Get New Messages Only
```bash
GET /api/wechat/messages/new
```

Returns only messages since last check.

### 3. Check for New Messages
```bash
GET /api/wechat/messages/check
```

**Response:**
```json
{
    "success": true,
    "has_new_message": true
}
```

Fast check without running OCR.

## Usage Examples

### Example 1: Read Messages with OCR

```bash
curl -s "http://localhost:5001/api/wechat/read?ocr=true" | python3 -m json.tool
```

### Example 2: Monitor for New Messages

```python
import requests
import time

while True:
    # Check if there's a new message (fast)
    check = requests.get('http://localhost:5001/api/wechat/messages/check')

    if check.json()['has_new_message']:
        # Run OCR to get new messages
        messages = requests.get('http://localhost:5001/api/wechat/messages/new')

        for msg in messages.json()['messages']:
            print(f"[{msg['timestamp']}] {msg['text']}")

    time.sleep(2)  # Check every 2 seconds
```

### Example 3: Agent Integration

```python
# When agent sends a message
wechat_service.send_message("Hello!", "Chat Name")
wechat_service.mark_message_as_sent("Hello!")  # Filter it out from OCR

# Later, check for replies
new_messages = wechat_service.get_new_messages_ocr()
for msg in new_messages:
    # Process user's reply
    agent_respond(msg['text'])
```

## Message Structure

Each message contains:

```python
{
    'timestamp': str,      # e.g., "Tuesday 22:33", "Yesterday 14:20"
    'text': str,          # Message content
    'is_agent': bool      # True if sent by agent (filtered out)
}
```

## OCR Accuracy

### What Works Well:
- ✅ English text
- ✅ Chinese text (Vision framework supports it)
- ✅ Short messages
- ✅ Clear fonts

### Limitations:
- ⚠️ Emojis (may be skipped or misread)
- ⚠️ Images (not extracted)
- ⚠️ Files/attachments (not detected)
- ⚠️ Very long messages (may be truncated)

## Performance

### Timing:
- **Screenshot capture:** ~100ms
- **Vision OCR:** ~1-2 seconds
- **Parsing:** <10ms
- **Total:** ~1.5-2 seconds per scan

### Optimization:
- Only run OCR when sidebar changes
- Cache previous messages
- Filter duplicates
- Rate limiting (configurable)

## Configuration

### Screenshot Area Calculation:
```python
# Message area (right side of window)
msg_x = window_x + (window_width * 0.3)  # After sidebar
msg_y = window_y + 80                     # Below title bar
msg_w = (window_width * 0.7) - 20        # Right side
msg_h = window_height - 180               # Exclude input area
```

### OCR Settings:
```swift
request.recognitionLevel = .accurate  // High accuracy
request.usesLanguageCorrection = true // Auto-correct
```

## Troubleshooting

### Issue: No text extracted
**Causes:**
1. WeChat window off-screen
2. Chat not open
3. No messages visible

**Solution:**
```bash
# Move window on-screen
osascript -e 'tell application "System Events" to tell process "WeChat" to set position of window 1 to {100, 100}'

# Open a chat
curl -X POST http://localhost:5001/api/wechat/open-chat \
  -H "Content-Type: application/json" \
  -d '{"chat_name": "File Transfer"}'
```

### Issue: OCR too slow
**Solution:** Reduce check frequency
```python
# Check every 5 seconds instead of 2
time.sleep(5)
```

### Issue: Agent's messages appearing in results
**Solution:** Mark messages as sent
```python
wechat_service.mark_message_as_sent("Your message text")
```

### Issue: Duplicate messages
**Solution:** Use `get_new_messages_ocr()` instead of `read_messages_ocr()`

## Integration with Agent

### Recommended Workflow:

1. **Agent sends message**
   ```python
   wechat_service.send_message(text, chat_name)
   wechat_service.mark_message_as_sent(text)
   ```

2. **Monitor for replies**
   ```python
   while waiting_for_reply:
       if wechat_service.has_new_message():
           new_msgs = wechat_service.get_new_messages_ocr()
           if new_msgs:
               # Process reply
               break
       time.sleep(2)
   ```

3. **Add to context**
   ```python
   for msg in new_messages:
       context.append({
           'role': 'user',
           'content': msg['text'],
           'timestamp': msg['timestamp']
       })
   ```

## Future Improvements

### Possible Enhancements:
1. **Image recognition** - Detect when images are sent
2. **File detection** - Identify file attachments
3. **Sender identification** - Distinguish between different senders
4. **Message threading** - Group related messages
5. **Emoji support** - Better emoji recognition
6. **Real-time streaming** - WebSocket updates

### Alternative Approaches:
1. **WeChat database** - Read from local SQLite database
2. **Network interception** - Capture WeChat protocol
3. **WeChat API** - If official API becomes available

## Testing

### Test Script:
```bash
#!/bin/bash

echo "Testing OCR Message Reading"
echo "==========================="
echo ""

# 1. Open File Transfer chat
echo "1. Opening File Transfer chat..."
curl -X POST http://localhost:5001/api/wechat/open-chat \
  -H "Content-Type: application/json" \
  -d '{"chat_name": "File"}' -s | python3 -m json.tool

sleep 2

# 2. Read messages with OCR
echo ""
echo "2. Reading messages with OCR..."
curl -s "http://localhost:5001/api/wechat/read?ocr=true" | python3 -m json.tool

# 3. Check for new messages
echo ""
echo "3. Checking for new messages..."
curl -s "http://localhost:5001/api/wechat/messages/check" | python3 -m json.tool
```

## Summary

**Advantages:**
- ✅ Works when accessibility API fails
- ✅ Extracts actual message content
- ✅ Supports multiple languages
- ✅ No external dependencies (uses macOS Vision)
- ✅ Smart triggering for efficiency

**Limitations:**
- ⚠️ Slower than API access (~2 seconds)
- ⚠️ Requires chat to be visible
- ⚠️ May miss emojis/images
- ⚠️ Needs window on-screen

**Best Use Case:**
- Agent monitoring conversations
- Reading user replies
- Building conversation context
- Automated responses

**The OCR system enables the agent to read and respond to messages autonomously!** 🎉
