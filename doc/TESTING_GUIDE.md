# Agent Chat Finding Testing Guide

## Overview

This guide helps you test and debug the WeChat agent's chat finding functionality.

## Backend Architecture

### Services
1. **Flask Web App** (`app.py`) - Port 5001
2. **Agent Orchestrator** (`agent-orchestrator/index.js`) - Port 8082
3. **WeChat Bridge** (`wechat-bridge/index.js`) - Ports 8080/8081
4. **Simple Agent** (`agent.py`) - Standalone Python script

### AI Provider
**Anthropic Claude API (Direct)** - NOT Zypher or Cloudbot
- Model: `claude-sonnet-4-5-20250929` or `claude-3-5-sonnet-20241022`
- Configuration: `.env` file
- API Endpoint: `https://api.anthropic.com/v1/messages`

## The Chat Finding Issue

### Problem
The agent can send messages but cannot reliably find chats because:
- WeChat's macOS desktop app doesn't expose chat names through accessibility API
- AppleScript returns MESSAGE CONTENT instead of CHAT NAMES
- The simple `agent.py` is hardcoded to only work with "File Transfer" / "文件传输助手"

### What Works
✅ Sending messages to known chats (File Transfer Assistant)
✅ Reading message content from current chat
✅ AI response generation

### What Doesn't Work
❌ Scanning/listing all available chats by name
❌ Finding a specific chat by name (except File Transfer)
❌ Retrieving chat names through accessibility API

## Testing Scripts

### 1. Diagnostic Script (Recommended First)
```bash
python3 diagnose_chat_retrieval.py
```

**Purpose**: Understand what the agent can actually retrieve from WeChat
**Output**: Shows what accessibility API returns vs what we need

### 2. Comprehensive Test Suite
```bash
python3 test_agent_chat_finding.py
```

**Tests**:
- ✓ WeChat running check
- ✓ AppleScript chat scanning
- ✓ OCR-based chat scanning
- ✓ Send message to File Transfer
- ✓ Read messages from File Transfer
- ✓ AI response generation
- ✓ Find specific chat by name (interactive)

**Output**: `test_agent_results.json`

### 3. OCR-Based Chat Scanner
```bash
python3 scripts/scan_chats_ocr.py 10 --json
```

**Requirements**:
```bash
pip install pytesseract pillow pyautogui
brew install tesseract tesseract-lang  # For Chinese support
```

**Purpose**: Extract chat names using screenshot + OCR

### 4. Module Tests
```bash
python3 tests/test_realchat_modules.py
```

**Tests**: Agent Manager, Privacy Controller, Storage, Message Analyzer, etc.
**Output**: `test_results.json`

## Solutions

### Solution 1: OCR-Based Scanning (Recommended)
**Pros**: Can extract visible chat names, works with desktop app
**Cons**: Requires visible WeChat window, depends on OCR accuracy

**Implementation**: Already available in `scripts/scan_chats_ocr.py`

### Solution 2: Manual Chat Name Entry
**Pros**: Most reliable, works immediately
**Cons**: Requires user to know exact chat name

**Implementation**: Already working in `agent.py` for File Transfer

### Solution 3: WeChat Web Mode
**Pros**: Proper DOM structure, reliable automation
**Cons**: Requires web login, different from desktop app

**Implementation**: Partial support in `scripts/wechat_web.py`

## Quick Test Commands

### Test if agent can send messages:
```bash
python3 -c "from agent import send_message; send_message('Test from CLI')"
```

### Test if agent can read messages:
```bash
python3 -c "from agent import read_last_message; print(read_last_message())"
```

### Test AI response:
```bash
python3 -c "from agent import get_ai_response; print(get_ai_response('Hello'))"
```

### Run the simple agent:
```bash
python3 agent.py
```

## Environment Setup

### Required Environment Variables (.env)
```bash
AI_API_KEY=your_anthropic_api_key
AI_BASE_URL=https://api.anthropic.com
AI_MODEL=claude-sonnet-4-5-20250929
AI_MAX_TOKENS=1024
DEFAULT_AI_PROVIDER=anthropic
```

### Check Configuration
```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', 'SET' if os.getenv('AI_API_KEY') else 'NOT SET')"
```

## Troubleshooting

### Issue: "No chats found"
**Cause**: Accessibility API limitation
**Solution**: Use OCR-based scanning or manual entry

### Issue: "Failed to send message"
**Cause**: Chat name not found or WeChat not active
**Solution**: Ensure WeChat is running and chat name is exact

### Issue: "AI response failed"
**Cause**: API key not set or invalid
**Solution**: Check `.env` file and API key validity

### Issue: OCR not working
**Cause**: Missing dependencies
**Solution**:
```bash
pip install pytesseract pillow pyautogui
brew install tesseract tesseract-lang
```

## Next Steps

1. **Run diagnostic**: `python3 diagnose_chat_retrieval.py`
2. **Run tests**: `python3 test_agent_chat_finding.py`
3. **Review results**: Check `test_agent_results.json`
4. **Choose solution**: OCR, manual entry, or web mode
5. **Implement**: Modify `agent.py` to use chosen solution

## Files Reference

- `agent.py` - Simple agent (File Transfer only)
- `app.py` - Flask web server
- `agent-orchestrator/index.js` - AI provider management
- `wechat-bridge/index.js` - Wechaty integration
- `scripts/scan_chats_ocr.py` - OCR-based scanner
- `tests/test_realchat_modules.py` - Module tests
- `wechat_chat_scanning_issue.txt` - Issue documentation

## Contact

For issues or questions, refer to the main README or check the issue tracker.
