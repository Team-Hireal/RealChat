#!/bin/bash

# WeChat Auto-Reply Configuration Script
# This script helps you set up the auto-reply bot interactively

CONFIG_FILE="$HOME/.wechat_autoreply_config"

echo "============================================"
echo "WeChat Auto-Reply Bot - Configuration"
echo "============================================"
echo ""

# Load existing config if available
if [ -f "$CONFIG_FILE" ]; then
    echo "Found existing configuration. Press Enter to keep current values."
    echo ""
    source "$CONFIG_FILE"
fi

# Chat Window Name
echo "1. Chat Window Name"
echo "   This is the name of the WeChat chat/contact you want to auto-reply to."
echo "   (For group chats, use the group name. For individuals, use their display name)"
if [ -n "$CHAT_WINDOW_NAME" ]; then
    echo "   Current: $CHAT_WINDOW_NAME"
fi
read -p "   Enter chat name: " input
if [ -n "$input" ]; then
    CHAT_WINDOW_NAME="$input"
fi
echo ""

# Your Name (for template)
echo "2. Your Name"
echo "   This will be used in the self-introduction template."
if [ -n "$YOUR_NAME" ]; then
    echo "   Current: $YOUR_NAME"
fi
read -p "   Enter your name: " input
if [ -n "$input" ]; then
    YOUR_NAME="$input"
fi
echo ""

# Your Title/Role (for template)
echo "3. Your Title/Role (optional)"
echo "   Example: 'Software Engineer at ABC Company' or 'Product Manager'"
if [ -n "$YOUR_TITLE" ]; then
    echo "   Current: $YOUR_TITLE"
fi
read -p "   Enter your title: " input
if [ -n "$input" ]; then
    YOUR_TITLE="$input"
fi
echo ""

# Self-Introduction Template
echo "4. Self-Introduction Template"
echo "   This message will be sent as your introduction to new contacts."
echo "   Use {{NAME}} and {{TITLE}} as placeholders."
if [ -n "$INTRO_TEMPLATE" ]; then
    echo "   Current: $INTRO_TEMPLATE"
fi
read -p "   Enter template (or press Enter for default): " input
if [ -n "$input" ]; then
    INTRO_TEMPLATE="$input"
else
    if [ -z "$INTRO_TEMPLATE" ]; then
        INTRO_TEMPLATE="Hi! I'm {{NAME}}, {{TITLE}}. It was great meeting you! Let's stay in touch."
    fi
fi
echo ""

# Default Reply Message
echo "5. Default Reply Message"
echo "   This message will be sent to contacts you've already introduced yourself to."
if [ -n "$DEFAULT_REPLY" ]; then
    echo "   Current: $DEFAULT_REPLY"
fi
read -p "   Enter default reply (or press Enter for default): " input
if [ -n "$input" ]; then
    DEFAULT_REPLY="$input"
else
    if [ -z "$DEFAULT_REPLY" ]; then
        DEFAULT_REPLY="Thanks for your message! I'll get back to you soon."
    fi
fi
echo ""

# Reply Mode
echo "6. Reply Mode"
echo "   a) Introduction mode - Send self-introduction to all unreplied messages"
echo "   b) Default reply mode - Send default reply to all unreplied messages"
echo "   c) Smart mode - Send introduction to new contacts, default reply to known contacts"
if [ -n "$REPLY_MODE" ]; then
    echo "   Current: $REPLY_MODE"
fi
read -p "   Enter mode (a/b/c): " input
if [ -n "$input" ]; then
    REPLY_MODE="$input"
fi
echo ""

# Dry Run
echo "7. Dry Run Mode"
echo "   In dry run mode, the script will show what it would do without actually sending messages."
echo "   Recommended to test first!"
if [ -n "$DRY_RUN" ]; then
    echo "   Current: $DRY_RUN"
fi
read -p "   Enable dry run? (yes/no) [yes]: " input
if [ -n "$input" ]; then
    DRY_RUN="$input"
else
    if [ -z "$DRY_RUN" ]; then
        DRY_RUN="yes"
    fi
fi
echo ""

# Save configuration
cat > "$CONFIG_FILE" << EOF
# WeChat Auto-Reply Configuration
# Generated on $(date)

CHAT_WINDOW_NAME="$CHAT_WINDOW_NAME"
YOUR_NAME="$YOUR_NAME"
YOUR_TITLE="$YOUR_TITLE"
INTRO_TEMPLATE="$INTRO_TEMPLATE"
DEFAULT_REPLY="$DEFAULT_REPLY"
REPLY_MODE="$REPLY_MODE"
DRY_RUN="$DRY_RUN"
EOF

echo "============================================"
echo "Configuration saved to: $CONFIG_FILE"
echo "============================================"
echo ""
echo "Summary:"
echo "  Chat: $CHAT_WINDOW_NAME"
echo "  Your Name: $YOUR_NAME"
echo "  Title: $YOUR_TITLE"
echo "  Reply Mode: $REPLY_MODE"
echo "  Dry Run: $DRY_RUN"
echo ""
echo "To start the bot, run: ./run.sh"
echo "To reconfigure, run: ./config.sh"
echo ""
