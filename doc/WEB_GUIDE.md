# Web Interface Guide

## Starting the Web Interface

```bash
./start-web.sh
```

Open your browser to: **http://localhost:5000**

## Interface Overview

### 1. Control Panel
- **Start Bot** - Begin auto-replying to messages
- **Stop Bot** - Stop the bot
- **Refresh Status** - Update status and logs

### 2. Configuration
- **Chat Name** - The WeChat contact/group to reply to
- **Your Name** - Used in introduction template
- **Your Title** - Your role/position
- **Introduction Template** - Message for new contacts (use {{NAME}} and {{TITLE}})
- **Default Reply** - Message for known contacts
- **Reply Mode**:
  - Introduction only - Send intro to all
  - Default reply only - Send default to all
  - Smart mode - Intro to new, default to known (recommended)
- **Dry Run** - Test mode (doesn't send messages)

### 3. Activity Logs
Real-time logs showing what the bot is doing:
- Blue = Info
- Green = Success
- Red = Error
- Yellow = Warning

### 4. Replied Contacts
List of contacts you've already replied to (tracked automatically)

## Workflow

1. **Configure** - Fill in your settings and save
2. **Test** - Enable "Dry Run" and click "Start Bot"
3. **Review** - Check the logs to see what would be sent
4. **Run** - Disable "Dry Run" and start again to send real messages

## Troubleshooting

If the bot can't find WeChat window:
```bash
./troubleshoot.sh
```

Make sure:
- WeChat is open and logged in
- The chat window is visible (not minimized)
- Accessibility permissions are granted

## Advantages Over Terminal

✅ **Visual feedback** - See status at a glance
✅ **Easy configuration** - Forms instead of prompts
✅ **Real-time logs** - Watch the bot work
✅ **No command line** - Just click buttons
✅ **Better UX** - Modern, intuitive interface

## Technical Details

- **Backend**: Python Flask (lightweight web server)
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks)
- **Port**: 5000 (localhost only)
- **Security**: Only accessible from your computer
- **Automation**: Same AppleScript as terminal version
