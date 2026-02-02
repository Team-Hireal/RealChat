# RealChat Messaging Behavior

## 📱 Message Flow

### Startup Behavior
When you start the agent, it sends **ONE message** to File Transfer:

```
🤖 RealChat Agent Ready

📱 Mode: Command mode

Type 'help' for commands.
```

This is the **only automatic message** sent at startup.

---

## 💬 Where Messages Are Sent

### 1. File Transfer (Command Chat)
**Purpose**: Control center for the agent

**Messages sent here:**
- ✅ Startup message (one time only)
- ✅ Command responses (when you send commands)
- ✅ Status updates (when you ask for status)
- ✅ Chat lists (when you ask for available chats)

**Example:**
```
You: help
Agent: 🤖 RealChat Agent Commands:
       [shows command list]

You: status
Agent: 📊 Agent Status:
       ✅ Active
       📱 Monitoring: John Doe

You: list chats
Agent: 📱 Available Chats (5):
       • John Doe
       • Work Group
       ...
```

### 2. Monitored Chat (Target Chat)
**Purpose**: Where the AI interacts with other users

**Messages sent here:**
- ✅ AI responses to messages in that chat
- ❌ NO command responses
- ❌ NO status updates

**Example:**
```
John Doe: Hey, what's the weather today?
Agent: I can help you with that! [AI response]

John Doe: Thanks!
Agent: You're welcome! [AI response]
```

---

## 🔄 Message Routing

```
┌─────────────────────────────────────────┐
│         File Transfer (Control)          │
│  - Startup message (1x only)            │
│  - Command responses                     │
│  - Status updates                        │
└─────────────────────────────────────────┘
                    ↕
            [Agent Core]
                    ↕
┌─────────────────────────────────────────┐
│      Monitored Chat (if selected)       │
│  - AI responses to messages              │
│  - Conversations with users              │
└─────────────────────────────────────────┘
```

---

## 📋 Message Count

### At Startup
- **File Transfer**: 1 message (startup notification)
- **Monitored Chat**: 0 messages (waits for user input)

### During Operation
- **File Transfer**: Only when you send commands
- **Monitored Chat**: Only when responding to messages

---

## 🎯 Key Points

1. **One startup message only** - Sent to File Transfer when agent starts
2. **Commands go to File Transfer** - All control messages stay in File Transfer
3. **AI responses go to target chat** - Conversations happen in the monitored chat
4. **No spam** - Agent only responds when needed
5. **Clear separation** - Control (File Transfer) vs Conversation (Target Chat)

---

## 💡 Examples

### Example 1: Command Mode Only
```
[Start Agent]
File Transfer: "🤖 RealChat Agent Ready..."  ← ONE MESSAGE

[You send command]
You → File Transfer: "help"
Agent → File Transfer: [command response]

[You send another command]
You → File Transfer: "status"
Agent → File Transfer: [status response]
```

### Example 2: Monitoring a Chat
```
[Start Agent]
File Transfer: "🤖 RealChat Agent Ready..."  ← ONE MESSAGE

[You send command]
You → File Transfer: "monitor John Doe"
Agent → File Transfer: "✅ Now monitoring: John Doe"

[John sends message]
John → John Doe Chat: "Hello!"
Agent → John Doe Chat: "Hi! How can I help?"  ← Response in target chat

[You check status]
You → File Transfer: "status"
Agent → File Transfer: "📊 Agent Status: Monitoring John Doe"
```

### Example 3: Switching Chats
```
[Currently monitoring John Doe]

[You send command]
You → File Transfer: "switch to Work Group"
Agent → File Transfer: "🔄 Switched to Work Group"

[Work Group member sends message]
Member → Work Group: "What's the deadline?"
Agent → Work Group: [AI response]  ← Response in new target chat

[File Transfer stays clean]
File Transfer: Only shows your commands and responses
```

---

## ✅ Summary

**File Transfer receives:**
- 1 startup message
- Command responses only

**Monitored chat receives:**
- AI responses to messages
- Nothing else

**Result:**
- Clean, organized messaging
- No spam or unnecessary messages
- Clear separation of control and conversation

---

**Updated**: 2026-02-01
**Behavior**: One startup message to File Transfer only
