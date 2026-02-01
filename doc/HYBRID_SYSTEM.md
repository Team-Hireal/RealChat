# WeChat Automation - Hybrid System

## Overview

This system supports **two methods** for automating WeChat:

1. **Desktop App Automation** (AppleScript + Accessibility API)
2. **WeChat Web Automation** (Selenium + Browser Control)

## Method 1: Desktop App Automation

### How It Works
- Uses AppleScript to control the native WeChat desktop app
- Requires macOS Accessibility permissions
- Directly interacts with the WeChat UI elements

### Pros
- Full access to all WeChat features
- Works with native desktop app
- No QR code scanning needed (if already logged in)

### Cons
- Requires Accessibility permissions
- Can be fragile if WeChat UI changes
- macOS only

### Setup Steps
1. Grant Accessibility permissions:
   - Open System Preferences → Privacy & Security → Accessibility
   - Add and enable: Terminal, iTerm, or your code editor
   - Restart the application after granting permissions

2. Run diagnostic tool:
   ```bash
   ./check_accessibility.sh
   ```

3. If successful, you can use the desktop automation method

## Method 2: WeChat Web Automation

### How It Works
- Opens WeChat Web (web.wechat.com) in Chrome browser
- Uses Selenium to control the browser
- Interacts with web interface elements

### Pros
- No accessibility permissions needed
- More reliable (web UI is more stable)
- Cross-platform (works on macOS, Windows, Linux)
- Can be controlled from web interface

### Cons
- Requires QR code scanning to log in
- Some features may be limited vs desktop app
- Requires Chrome browser

### Setup Steps
1. Install dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Start WeChat Web browser from the web interface:
   - Click "Start WeChat Web" button
   - Scan QR code with your phone
   - Wait for login confirmation

3. Once logged in, you can send messages via the web interface

## API Endpoints

### Method Selection
- `GET /api/method` - Get current automation method
- `POST /api/method` - Set method (desktop or web)

### WeChat Web Control
- `POST /api/web/start` - Start WeChat Web browser
- `GET /api/web/status` - Check login status
- `POST /api/web/send` - Send message via web

### Accessibility Check
- `GET /api/check-accessibility` - Check if permissions are granted

## Usage from Web Interface

### Desktop Method
1. Ensure WeChat desktop app is running
2. Grant accessibility permissions
3. Click "Start Bot" in web interface
4. Bot will use AppleScript to control desktop app

### Web Method
1. Click "Switch to Web Method" in settings
2. Click "Start WeChat Web Browser"
3. Scan QR code when browser opens
4. Wait for login confirmation
5. Click "Start Bot" to begin automation

## Hybrid Approach

The system can automatically fall back:
1. Try desktop method first
2. If accessibility fails, suggest web method
3. User can manually switch between methods

## Troubleshooting

### Desktop Method Issues
- **"WeChat window not found"**: Run `./check_accessibility.sh`
- **Permissions denied**: Grant accessibility permissions in System Preferences
- **WeChat not responding**: Restart WeChat app

### Web Method Issues
- **Browser won't start**: Install Chrome and check Selenium installation
- **QR code timeout**: Scan faster or increase timeout
- **Can't find chat**: Check chat name spelling (case-sensitive)

## Files

- `wechat_web.py` - WeChat Web automation module
- `check_accessibility.sh` - Diagnostic tool for desktop method
- `app.py` - Flask backend with both methods
- `wemac_autoreply.applescript` - Desktop automation script
