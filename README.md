# RealChat - AI-Powered WeChat Automation

Intelligent WeChat automation with **AI agent integration** supporting mobile WeChat, multiple AI providers, and both web and terminal interfaces.

## 🎯 What It Does

This bot helps you:
- **AI-powered responses** - Intelligent, context-aware replies using Claude AI
- **Mobile WeChat support** - Works with your phone's WeChat app (NEW!)
- **Multiple AI providers** - Choose between Anthropic API, Zypher Agents, or local OpenClaw (NEW!)
- **Catch up on unreplied messages** - Never miss important contacts
- **Send personalized introductions** - Smart templating system
- **Safe & Non-destructive** - No messages are ever deleted

## ✨ Key Features

### AI Agent Integration (NEW!)
- **🤖 Three AI Provider Options:**
  - **Anthropic API** - Direct Claude integration (simple & reliable)
  - **Zypher Agents** - Advanced agent framework with tool use
  - **OpenClaw Local** - Connect your local Clawdbot instance
- **📱 Mobile WeChat Support** - Works with native mobile app via Wechaty
- **💬 Intelligent Conversations** - Context-aware, natural responses
- **🔄 Real-time Processing** - Instant AI responses to incoming messages

### Core Features
- **Safe & Non-destructive** - Does NOT delete any messages
- **Smart Detection** - Identifies which messages haven't been replied to
- **Template System** - Use placeholders for personalized messages
- **Web Interface** - Modern, user-friendly web UI
- **Terminal Interface** - Classic command-line interface
- **Dry Run Mode** - Test without sending real messages
- **Contact Tracking** - Remembers who you've already replied to

---

## 🚀 Quick Start (AI Agent Mode - NEW!)

### Option A: Docker (Recommended - Easiest!)

**1. Install Docker:**
- Download from https://docs.docker.com/get-docker/

**2. Quick start:**
```bash
./quick-start.sh
```

**3. Configure your AI provider:**
```bash
# Edit .env and add your API key
nano .env

# Set at minimum:
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**4. Scan QR code with mobile WeChat:**
- Watch the logs for QR code URL
- Open WeChat on your phone → Settings → WeChat Web
- Scan the QR code

**5. Start chatting!**
- Send a message to yourself or any contact
- The AI will respond automatically

**📚 Full documentation:** See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions

---

## 🚀 Getting Started (Classic Mode - Desktop WeChat)

### Step 1: Prerequisites

**System Requirements:**
- macOS (required for AppleScript automation)
- Python 3.x installed
- WeChat for macOS (desktop version)

**Install Python dependencies:**
```bash
pip3 install -r requirements.txt
```

**Grant Accessibility Permissions:**
1. Open **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Click the lock icon to make changes
3. Add and enable **Terminal** (or iTerm2, or your terminal app)
4. Add and enable **Script Editor**

**WeChat Setup:**
1. Install WeChat for macOS (desktop version)
2. Log in to your account
3. Make sure WeChat is open and the main window is visible (not minimized)

### Step 2: Choose Your Interface

#### Option A: Web Interface (Recommended - Easiest!)

**Start the web server:**
```bash
./start-web.sh
```

**Open your browser:**
```
http://localhost:5000
```

**Configure and run:**
1. Fill in the configuration form:
   - Chat name (e.g., "宝宝们" or contact name)
   - Your name and title
   - Introduction template (use {{NAME}} and {{TITLE}})
   - Default reply message
   - Reply mode (Smart mode recommended)
   - Dry run: Yes (for testing)
2. Click "Save Configuration"
3. Click "Start Bot" to test
4. Review the logs
5. If everything looks good, change Dry Run to "No" and start again

#### Option B: Terminal Interface (Classic)

**First time setup:**
```bash
./get-started.sh
```

**Run the bot:**
```bash
./run.sh
```

### Step 3: Test First!

**Always test with Dry Run mode first:**
- Dry Run shows what WOULD be sent without actually sending
- Review the logs to make sure messages look correct
- Once satisfied, disable Dry Run and run for real

### Step 4: Troubleshooting

**If you see "WeChat window not found":**
```bash
./troubleshoot.sh
```

This will help diagnose:
- Whether WeChat is running
- Whether the window is visible
- Whether accessibility permissions are working

---

## 📖 Detailed Usage

### Configuration Options

**Chat Name:**
- For 1-on-1 chats: Use the contact's display name
- For group chats: Use the group name
- Must match exactly (case-sensitive)

**Your Name & Title:**
- Used in introduction template
- Example: Name="John", Title="Product Manager at TechCorp"

**Introduction Template:**
- Sent to new contacts you haven't replied to
- Use `{{NAME}}` and `{{TITLE}}` as placeholders
- Example: "Hi! I'm {{NAME}}, {{TITLE}}. Great meeting you!"

**Default Reply:**
- Sent to contacts you've already introduced yourself to
- Example: "Thanks for your message! I'll get back to you soon."

**Reply Modes:**
- **Mode A (Introduction only)**: Send intro to everyone
- **Mode B (Default only)**: Send default reply to everyone
- **Mode C (Smart mode)**: Intro to new contacts, default to known contacts ✅ Recommended
- **Dry Run:**
- Test mode that shows what would be sent without actually sending
- Always recommended for first-time use

### Example Scenarios

**Scenario 1: Met 20 people at a networking event**

1. Add them all on WeChat
2. Open web interface: `./start-web.sh`
3. Configure:
   - Chat: "Conference Contacts" (or go one-by-one)
   - Your Name: "John Doe"
   - Your Title: "Product Manager at TechCorp"
   - Template: "Hi! I'm {{NAME}}, {{TITLE}}. Great meeting you at the conference!"
   - Mode: Smart mode
   - Dry Run: Yes
4. Click "Start Bot" to test
5. Review logs, then disable Dry Run and run for real

**Scenario 2: Quick catch-up with existing contacts**

1. Configure with default reply: "Thanks for reaching out! I'll respond soon."
2. Set mode to "Default reply only"
3. Run the bot to send quick acknowledgments

### How It Works

1. **UI Automation**: Uses AppleScript to interact with WeChat's interface
2. **Message Detection**: Scans message history to find unreplied messages
3. **Smart Reply**: Determines which template to use based on mode and history
4. **Contact Tracking**: Saves contact names to avoid duplicate introductions

---

## 🔧 Configuration Files

**Config file:** `~/.wechat_autoreply_config`
- Stores your settings (chat name, templates, mode, etc.)

**Tracking file:** `~/.wechat_autoreply_tracking`
- Stores contacts you've already replied to

**Useful commands:**

Reset tracking (treat everyone as new):
```bash
rm ~/.wechat_autoreply_tracking
```

View who you've replied to:
```bash
cat ~/.wechat_autoreply_tracking
```

Reconfigure settings:
```bash
./config.sh
```

---

## 🐛 Common Issues & Solutions

### "WeChat window not found"
**Solution:**
- Make sure WeChat is running and logged in
- The main window must be visible (not minimized)
- Run `./troubleshoot.sh` to diagnose

### "Could not find or switch to chat"
**Solution:**
- Check the chat name is exactly correct (case-sensitive)
- Make sure the chat appears in your WeChat sidebar
- Try opening the chat manually first

### "splitter group 1 not found"
**Solution:**
- WeChat's UI structure may have changed
- Make sure WeChat is fully loaded
- Try restarting WeChat
- Run `./diagnose_ui.applescript` to inspect UI structure

### Messages not being detected
**Solution:**
- The bot scans the last 20 messages
- Make sure you're in a 1-on-1 chat or small group
- Check that messages are actually unreplied

### Script permissions error
**Solution:**
- Grant Accessibility permissions in System Preferences
- Restart Terminal after granting permissions
- Make sure both Terminal and Script Editor are enabled

---

## ⚠️ Important Notes

- **macOS only**: This script uses AppleScript which only works on macOS
- **Desktop WeChat required**: Must use WeChat for macOS (not web version)
- **UI must be visible**: WeChat window must be open and not minimized
- **Chinese WeChat**: Script looks for "我" to identify your messages
- **One chat at a time**: Reconfigure for different chats
- **Safe operation**: No messages are ever deleted

---

## 📁 Project Structure

```
wemac/
├── app.py                      # Flask web server
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── style.css              # Styling
│   └── app.js                 # Frontend logic
├── wemac_autoreply.applescript # Core bot logic
├── mouseclick.py              # Mouse automation helper
├── start-web.sh               # Start web interface
├── get-started.sh             # Terminal setup wizard
├── config.sh                  # Configuration script
├── run.sh                     # Run the bot
├── troubleshoot.sh            # Diagnostic tool
├── diagnose_ui.applescript    # UI inspector
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── WEB_GUIDE.md              # Web interface guide
└── STRUCTURE.md              # Project overview
```

---

## 🤝 Contributing

This project was cleaned up and enhanced with a web interface. The original script was a Chinese WeChat RPA bot that deleted messages. The new version:
- ✅ Does NOT delete any messages
- ✅ Has a modern web interface
- ✅ Includes safety features (dry run, tracking)
- ✅ Better error handling and diagnostics

---

## 📄 License

Use at your own risk. This tool interacts with WeChat's UI which may change with updates.

---

## 🔗 Additional Resources

- **Web Interface Guide**: See `WEB_GUIDE.md` for detailed web UI documentation
- **Project Structure**: See `STRUCTURE.md` for file organization
- **Troubleshooting**: Run `./troubleshoot.sh` for diagnostics

---

**Made with ❤️ using AppleScript, Python Flask, and modern web technologies**
