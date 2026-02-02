# RealChat User Workflow Guide

## Overview

RealChat now supports a flexible workflow where you can control the agent through WeChat File Transfer chat using natural language commands. The agent defaults to "command mode" and you can dynamically switch between monitoring different chats.

---

## 🚀 Quick Start

### Method 1: Command Mode (Recommended)

1. **Open the web interface**: http://localhost:5001
2. **Click "Start Agent"** (no need to select a chat)
3. **Open WeChat** and go to "File Transfer" chat
4. **Send commands** to control the agent

### Method 2: Direct Monitoring

1. **Open the web interface**: http://localhost:5001
2. **Click "Scan Chats"** to discover available chats
3. **Select a chat** from the dropdown
4. **Click "Start Agent"** to monitor that specific chat

---

## 📱 Command Mode (File Transfer)

When the agent starts without a selected chat, it enters **Command Mode** where it listens for commands in the File Transfer chat.

### Available Commands

#### 📊 Status & Information
```
status
```
Check current agent status and which chat is being monitored.

```
list chats
```
Show all available WeChat chats that can be monitored.

```
help
```
Display all available commands with examples.

#### 🎯 Chat Control
```
monitor <chat name>
```
Start monitoring a specific chat. The agent will respond to messages in that chat.

**Examples:**
- `monitor John Doe`
- `monitor Work Group`
- `monitor 张三` (Chinese names supported)

```
switch to <chat name>
```
Switch from current chat to a different chat.

**Examples:**
- `switch to Family Group`
- `switch to Boss`

```
stop monitoring
```
Stop monitoring the current chat and return to command mode.

---

## 🔄 Workflow Examples

### Example 1: Monitor a Friend's Chat

1. Start agent (command mode)
2. In File Transfer, send: `list chats`
3. Agent responds with available chats
4. Send: `monitor John Doe`
5. Agent confirms and starts monitoring
6. Now John Doe can chat with the AI agent
7. You can check status anytime: `status`

### Example 2: Switch Between Chats

1. Currently monitoring "Work Group"
2. In File Transfer, send: `switch to Family Group`
3. Agent stops monitoring Work Group
4. Agent starts monitoring Family Group
5. Family members can now chat with AI

### Example 3: Stop and Resume

1. Currently monitoring a chat
2. In File Transfer, send: `stop monitoring`
3. Agent returns to command mode
4. Later, send: `monitor <chat name>` to resume

---

## 🎯 Use Cases

### Use Case 1: Auto-Reply While Busy

**Scenario**: You're in a meeting and want the AI to handle messages.

**Steps**:
1. Start agent in command mode
2. Send: `monitor Boss`
3. AI responds to your boss's messages
4. After meeting, send: `stop monitoring`

### Use Case 2: Group Chat Assistant

**Scenario**: You want AI to help answer questions in a work group.

**Steps**:
1. Start agent
2. Send: `monitor Work Group`
3. Anyone in the group can ask questions
4. AI responds automatically
5. You can check what's happening: `status`

### Use Case 3: Multiple Chat Management

**Scenario**: You need to monitor different chats throughout the day.

**Steps**:
1. Morning: `monitor Client A`
2. Afternoon: `switch to Client B`
3. Evening: `switch to Family Group`
4. Night: `stop monitoring`

---

## 🖥️ Web Interface Features

### Sidebar Controls

**System Status**
- WeChat: Shows if WeChat is running
- AI Service: Shows if AI is healthy
- Agent: Shows if agent is running

**Chat Selection**
- Dropdown to select target chat
- "Scan Chats" button to discover chats
- Shows currently monitored chat

**Agent Control**
- "Start Agent" - Begin monitoring (command mode or selected chat)
- "Stop Agent" - Stop the agent
- "Refresh Status" - Update system status

### Main Area

**Messages**
- Real-time display of messages and AI responses
- Shows which chat each message is from
- System notifications for command execution

**Input**
- Send messages directly to WeChat
- Useful for testing

---

## 🔧 Advanced Features

### Dynamic Chat Switching

The agent can switch between chats without restarting:
- Send commands to File Transfer anytime
- Agent continues monitoring current chat
- Commands are processed immediately
- Switching is seamless

### Multi-User Support

When monitoring a group chat:
- All members can interact with the AI
- AI responds to everyone
- You maintain control via File Transfer commands

### Status Monitoring

Check agent status from:
- Web interface (real-time updates)
- File Transfer chat (`status` command)
- Activity logs in web interface

---

## 📋 Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show all commands | `help` |
| `status` | Check agent status | `status` |
| `list chats` | Show available chats | `list chats` |
| `monitor <name>` | Start monitoring chat | `monitor John` |
| `switch to <name>` | Switch to different chat | `switch to Work` |
| `stop monitoring` | Stop monitoring | `stop monitoring` |

---

## 🎨 User Interface

### Command Mode Indicator

When in command mode, you'll see:
```
📱 Mode: Command mode (File Transfer)
```

### Monitoring Indicator

When monitoring a chat, you'll see:
```
📱 Monitoring: John Doe
```

### Real-Time Updates

The web interface shows:
- ✅ Command executed successfully
- 🔄 Chat switched
- 📨 New message received
- 🤖 AI response sent

---

## 🔐 Privacy & Control

### You're Always in Control

- Agent only monitors chats you specify
- Stop monitoring anytime with `stop monitoring`
- Check status anytime with `status`
- All actions logged in web interface

### Default Behavior

- **Default**: Command mode (File Transfer)
- **No auto-monitoring**: Agent waits for your command
- **Explicit control**: You choose which chats to monitor

---

## 🐛 Troubleshooting

### Agent Not Responding to Commands

1. Check agent is running (web interface)
2. Make sure you're in File Transfer chat
3. Try `help` command to verify connection

### Can't Find Chat

1. Use `list chats` to see available chats
2. Make sure WeChat is open
3. Try partial name matching (e.g., "John" for "John Doe")

### Agent Not Monitoring

1. Check status with `status` command
2. Verify chat name is correct
3. Try `monitor <chat>` again

---

## 💡 Tips & Best Practices

1. **Start with command mode**: Don't select a chat initially, just start the agent
2. **Use File Transfer as control center**: All commands go through File Transfer
3. **Check status regularly**: Use `status` to see what's being monitored
4. **Partial names work**: "John" will match "John Doe"
5. **Stop when done**: Use `stop monitoring` to return to command mode

---

## 🎯 Summary

**Default Workflow:**
1. Start Agent → Command Mode (File Transfer)
2. Send Commands → Control agent behavior
3. Monitor Chats → AI responds automatically
4. Switch/Stop → Dynamic control anytime

**Key Benefits:**
- ✅ No need to select chat before starting
- ✅ Control agent through WeChat itself
- ✅ Switch between chats dynamically
- ✅ Always know what's being monitored
- ✅ Stop/resume anytime

---

## 📞 Support

For issues or questions:
- Check web interface logs
- Review this guide
- Verify WeChat is running
- Ensure AI service is healthy

**Status Check**: http://localhost:5001/api/status

---

**Version**: 2.0.0
**Last Updated**: 2026-02-01
**Mode**: Command-First Workflow
