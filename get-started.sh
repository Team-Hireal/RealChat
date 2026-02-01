#!/bin/bash

# Getting Started with WeChat Auto-Reply Bot
# This script will guide you through the setup process

clear

cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           WeChat Auto-Reply Bot - Getting Started           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Welcome! This guide will help you set up the WeChat auto-reply bot
in just a few steps.

═══════════════════════════════════════════════════════════════

📋 WHAT YOU NEED
═══════════════════════════════════════════════════════════════

 1. ✓ macOS (you have this)
 2. ? WeChat desktop app installed
 3. ? WeChat logged in  
 4. ? Python 3 with pynput library
 5. ? Accessibility permissions granted

Let's check your setup...

EOF

echo -n "Checking Python 3... "
if command -v python3 &> /dev/null; then
    echo "✓ Found: $(python3 --version)"
else
    echo "✗ Not found"
    echo ""
    echo "Please install Python 3: https://www.python.org/downloads/"
    exit 1
fi

echo -n "Checking pynput library... "
if python3 -c "import pynput" 2>/dev/null; then
    echo "✓ Installed"
else
    echo "✗ Not installed"
    echo ""
    read -p "Would you like to install pynput now? (y/n): " install_pynput
    if [[ "$install_pynput" =~ ^[Yy]$ ]]; then
        echo "Installing pynput..."
        pip3 install pynput
        if [ $? -eq 0 ]; then
            echo "✓ pynput installed successfully"
        else
            echo "✗ Failed to install pynput. Please install manually: pip3 install pynput"
            exit 1
        fi
    else
        echo "Please install pynput manually: pip3 install pynput"
        exit 1
    fi
fi

echo -n "Checking WeChat... "
if pgrep -x "WeChat" > /dev/null; then
    echo "✓ Running"
else
    echo "✗ Not running"
    echo ""
    echo "Please start WeChat and log in before continuing."
    read -p "Press Enter when WeChat is running and logged in..."
fi

cat << 'EOF'

═══════════════════════════════════════════════════════════════

🔐 ACCESSIBILITY PERMISSIONS
═══════════════════════════════════════════════════════════════

The bot needs accessibility permissions to control WeChat.

Steps:
 1. Open System Preferences
 2. Go to Security & Privacy → Privacy → Accessibility
 3. Click the lock to make changes
 4. Add and enable: Terminal (or your terminal app)
 5. Add and enable: Script Editor

EOF

read -p "Have you granted accessibility permissions? (y/n): " has_permissions
if [[ ! "$has_permissions" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please grant permissions and run this script again."
    exit 0
fi

cat << 'EOF'

═══════════════════════════════════════════════════════════════

🎯 USE CASE SELECTION
═══════════════════════════════════════════════════════════════

What's your main use case?

 a) After networking event - introduce myself to new contacts
 b) Catch up on messages - send default reply to everyone
 c) Mixed - smart mode (intro to new, default to known)

EOF

read -p "Select (a/b/c): " use_case

case "$use_case" in
    a)
        echo ""
        echo "Great! You'll send introductions to contacts."
        echo "We'll configure mode A (Introduction mode)."
        ;;
    b)
        echo ""
        echo "Great! You'll send a default reply to all unreplied messages."
        echo "We'll configure mode B (Default reply mode)."
        ;;
    c)
        echo ""
        echo "Great! Smart mode will send intros to new contacts and"
        echo "default replies to known contacts."
        echo "We'll configure mode C (Smart mode)."
        ;;
    *)
        echo ""
        echo "Invalid selection. Please run the script again."
        exit 1
        ;;
esac

cat << 'EOF'

═══════════════════════════════════════════════════════════════

📝 CONFIGURATION
═══════════════════════════════════════════════════════════════

Next, we'll run the configuration wizard.
You'll be asked for:
 - Chat name (the person/group to reply to)
 - Your name and title
 - Message templates
 - Reply mode
 - Dry run mode (recommended: yes for first time)

EOF

read -p "Ready to configure? Press Enter to continue..."

# Run config.sh
./config.sh

if [ $? -ne 0 ]; then
    echo ""
    echo "Configuration failed. Please check the errors above."
    exit 1
fi

cat << 'EOF'

═══════════════════════════════════════════════════════════════

🎉 SETUP COMPLETE!
═══════════════════════════════════════════════════════════════

You're all set! Here's what to do next:

Step 1: Test with Dry Run
──────────────────────────
  ./run.sh
  
  This will show you what messages WOULD be sent
  without actually sending them. Review the output!

Step 2: Run for Real  
──────────────────────
  If everything looks good:
  
  ./config.sh  # Change dry run to "no"
  ./run.sh     # Actually send messages

═══════════════════════════════════════════════════════════════

📚 HELPFUL COMMANDS
═══════════════════════════════════════════════════════════════

See examples:           ./demo.sh
View configuration:     cat ~/.wechat_autoreply_config
View tracking:          cat ~/.wechat_autoreply_tracking
Reset tracking:         rm ~/.wechat_autoreply_tracking
Reconfigure:            ./config.sh
Quick reference:        cat QUICKSTART.md
Full documentation:     cat README.md

═══════════════════════════════════════════════════════════════

💡 TIPS
═══════════════════════════════════════════════════════════════

 ✓ Always test with dry run first
 ✓ Check the chat name is exact (case-sensitive)
 ✓ Keep WeChat open and logged in
 ✓ Review QUICKSTART.md for quick reference
 ✓ Check ARCHITECTURE.txt to understand how it works

═══════════════════════════════════════════════════════════════

Ready to test? Run: ./run.sh

EOF
