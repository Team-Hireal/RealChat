# Quick Start: WeChat Web Mode

## Why Use WeChat Web Mode?

WeChat Web mode is the **recommended** approach because:
- ✅ More reliable than desktop automation
- ✅ Can actually list and access chats
- ✅ Already fully implemented in the codebase
- ✅ No accessibility API limitations
- ✅ Works consistently across WeChat versions

## Setup (One-Time)

1. **Start the Backend** (if not already running):
   ```bash
   cd /Users/test/Desktop/Hireal/RealChat/wemac
   python app.py
   ```

2. **Start the Frontend** (if not already running):
   ```bash
   cd /Users/test/Desktop/Hireal/RealChat/wemac/frontend
   npm run dev
   ```

## Using WeChat Web

### Method 1: Via API (Command Line)

1. **Start WeChat Web Browser:**
   ```bash
   curl -X POST http://localhost:5001/api/web/start
   ```
   - A Chrome browser window will open
   - You'll see the WeChat Web QR code

2. **Scan QR Code:**
   - Open WeChat on your phone
   - Go to "Me" → "Settings" → "WeChat Web"
   - Scan the QR code on your computer screen
   - Confirm login on your phone

3. **Check Login Status:**
   ```bash
   curl http://localhost:5001/api/web/status
   ```
   - Should return: `{"logged_in": true, "status": "ready"}`

4. **Send a Test Message:**
   ```bash
   curl -X POST http://localhost:5001/api/web/send \
     -H "Content-Type: application/json" \
     -d '{"chat_name": "Friend Name", "message": "Hello from automation!"}'
   ```

### Method 2: Via Web Interface

1. **Open the Web Interface:**
   ```
   http://localhost:5173
   ```

2. **Configure Settings:**
   - Go to Configuration section
   - Enter your name and title
   - Set your intro template or default reply
   - Choose reply mode (Custom or Intro Template)

3. **Start the Bot:**
   - Click "Start Bot" button
   - The bot will begin monitoring for new messages
   - It will auto-reply based on your configuration

## Configuration Options

### Reply Modes

**Custom Reply Mode (`-m c`):**
- Sends the same message to everyone
- Use for simple, consistent responses
- Example: "Thanks for your message! I'll get back to you soon."

**Intro Template Mode (`-m i`):**
- Personalizes messages with name and title
- Use placeholders: `{{NAME}}` and `{{TITLE}}`
- Example: "Hi! I'm {{NAME}}, {{TITLE}} at Company. How can I help?"

### Dry Run Mode

**Enabled (`-d yes`):**
- Bot logs what it would do but doesn't send messages
- Safe for testing
- See what messages would be sent

**Disabled (`-d no`):**
- Bot actually sends messages
- Use after testing in dry run mode

## Troubleshooting

### Browser Doesn't Open
```bash
# Check if Chrome/Chromium is installed
which google-chrome chromium-browser chromium

# Install Chrome if needed (macOS)
brew install --cask google-chrome
```

### QR Code Doesn't Appear
- Wait 5-10 seconds for page to load
- Check browser console for errors
- Try refreshing the page

### Login Fails
- Make sure you're scanning with the correct WeChat account
- Check that WeChat Web is enabled in your WeChat settings
- Try logging out and scanning again

### Can't Send Messages
```bash
# Check status first
curl http://localhost:5001/api/web/status

# If not logged in, restart
curl -X POST http://localhost:5001/api/web/start
```

## API Reference

### Start WeChat Web
```bash
POST /api/web/start
Response: {"status": "started", "message": "Browser opened"}
```

### Check Status
```bash
GET /api/web/status
Response: {"logged_in": true/false, "status": "ready"/"not_ready"}
```

### Send Message
```bash
POST /api/web/send
Body: {
  "chat_name": "Contact Name",
  "message": "Your message here"
}
Response: {"success": true/false, "message": "..."}
```

### Get Configuration
```bash
GET /api/config
Response: {
  "chat_name": "...",
  "user_name": "...",
  "user_title": "...",
  "intro_template": "...",
  "default_reply": "...",
  "reply_mode": "c"/"i",
  "dry_run": "yes"/"no"
}
```

### Update Configuration
```bash
POST /api/config
Body: {
  "chat_name": "Group Chat",
  "user_name": "John Doe",
  "user_title": "Product Manager",
  "reply_mode": "i",
  "dry_run": "yes"
}
Response: {"success": true}
```

## Example Workflow

```bash
# 1. Start WeChat Web
curl -X POST http://localhost:5001/api/web/start

# 2. Scan QR code with phone (wait for login)

# 3. Verify login
curl http://localhost:5001/api/web/status

# 4. Configure bot
curl -X POST http://localhost:5001/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "chat_name": "Work Group",
    "user_name": "Jane Smith",
    "user_title": "Senior Developer",
    "intro_template": "Hi! I'\''m {{NAME}}, {{TITLE}}. How can I help?",
    "reply_mode": "i",
    "dry_run": "yes"
  }'

# 5. Start bot (dry run mode for testing)
curl -X POST http://localhost:5001/api/start

# 6. Check logs
curl http://localhost:5001/api/logs

# 7. If everything looks good, disable dry run
curl -X POST http://localhost:5001/api/config \
  -H "Content-Type: application/json" \
  -d '{"dry_run": "no"}'

# 8. Restart bot in live mode
curl -X POST http://localhost:5001/api/stop
curl -X POST http://localhost:5001/api/start
```

## Tips

1. **Always test in dry run mode first** to see what messages would be sent
2. **Monitor the logs** to see bot activity: `curl http://localhost:5001/api/logs`
3. **Use specific chat names** - the bot works best with exact chat names
4. **Keep the browser window open** - closing it will disconnect WeChat Web
5. **Check tracking** to see who you've replied to: `curl http://localhost:5001/api/tracking`

## Next Steps

- Customize your intro template with your information
- Test in dry run mode with a test chat
- Monitor logs to ensure it's working as expected
- Switch to live mode when ready
- Set up monitoring to track responses

---

**Need Help?**
- Check `WECHAT_INTEGRATION_FINAL.md` for detailed technical information
- Run `python test_integration.py` for diagnostics
- Review logs at `http://localhost:5001/api/logs`
