#!/bin/bash

# WeChat Auto-Reply Bot Runner
# This script runs the auto-reply bot with your configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPLESCRIPT_PATH="$SCRIPT_DIR/wemac_autoreply_fixed.applescript"
CONFIG_FILE="$HOME/.wechat_autoreply_config"
TRACKING_FILE="$HOME/.wechat_autoreply_tracking"

# Check if configuration exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "============================================"
    echo "No configuration found!"
    echo "============================================"
    echo ""
    echo "Please run ./config.sh first to set up your auto-reply settings."
    echo ""
    exit 1
fi

# Load configuration
source "$CONFIG_FILE"

# Validate required fields
if [ -z "$CHAT_WINDOW_NAME" ]; then
    echo "ERROR: CHAT_WINDOW_NAME not configured."
    echo "Please run ./config.sh to configure the bot."
    exit 1
fi

if [ -z "$YOUR_NAME" ]; then
    echo "ERROR: YOUR_NAME not configured."
    echo "Please run ./config.sh to configure the bot."
    exit 1
fi

# Show current configuration
echo "============================================"
echo "WeChat Auto-Reply Bot"
echo "============================================"
echo ""
echo "Configuration:"
echo "  Chat: $CHAT_WINDOW_NAME"
echo "  Your Name: $YOUR_NAME"
echo "  Your Title: $YOUR_TITLE"
echo "  Reply Mode: $REPLY_MODE"
echo "  Dry Run: $DRY_RUN"
echo ""

if [ "$DRY_RUN" = "yes" ]; then
    echo "⚠️  DRY RUN MODE ENABLED"
    echo "   The bot will show what it would do without actually sending messages."
    echo "   Run ./config.sh and set dry run to 'no' to send real messages."
    echo ""
fi

echo "Press Ctrl+C to stop"
echo "============================================"
echo ""

# Check if WeChat is running (try multiple possible process names)
WECHAT_RUNNING=false

# Try English name first
if pgrep -x "WeChat" > /dev/null; then
    WECHAT_RUNNING=true
    echo "✓ WeChat process found (English name)"
fi

# Try Chinese name (微信)
if ! $WECHAT_RUNNING && pgrep -f "微信" > /dev/null 2>&1; then
    WECHAT_RUNNING=true
    echo "✓ WeChat process found (Chinese name)"
fi

# Try case-insensitive search
if ! $WECHAT_RUNNING && pgrep -i "wechat" > /dev/null; then
    WECHAT_RUNNING=true
    echo "✓ WeChat process found (case-insensitive)"
fi

if [ "$WECHAT_RUNNING" = false ]; then
    echo ""
    echo "ERROR: WeChat is not running."
    echo ""
    echo "Please:"
    echo "  1. Start WeChat application"
    echo "  2. Log in to your account"
    echo "  3. Make sure WeChat window is visible (not minimized)"
    echo "  4. Run this script again"
    echo ""
    exit 1
fi

# Run the auto-reply script
osascript "$APPLESCRIPT_PATH" \
    "$CHAT_WINDOW_NAME" \
    "$YOUR_NAME" \
    "$YOUR_TITLE" \
    "$INTRO_TEMPLATE" \
    "$DEFAULT_REPLY" \
    "$REPLY_MODE" \
    "$DRY_RUN" \
    "$SCRIPT_DIR" \
    "$TRACKING_FILE"

echo ""
echo "============================================"
echo "Auto-reply bot finished."
echo ""
echo "To reply to more chats:"
echo "  - Run ./config.sh to change the target chat"
echo "  - Run ./run.sh again"
echo ""
echo "To see who you've replied to:"
echo "  cat ~/.wechat_autoreply_tracking"
echo "============================================"
