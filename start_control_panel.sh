#!/bin/bash

# RealChat Control Panel Startup Script
# This script ensures the Flask backend is running and opens the control panel

echo "======================================"
echo "RealChat Control Panel Startup"
echo "======================================"
echo ""

# Check if Flask server is already running
if lsof -i :5001 > /dev/null 2>&1; then
    echo "✓ Flask server is already running on port 5001"
else
    echo "Starting Flask server..."
    cd "$(dirname "$0")"
    python3 app_consolidated.py > /tmp/realchat_flask.log 2>&1 &
    FLASK_PID=$!
    echo "  Flask server started (PID: $FLASK_PID)"
    echo "  Waiting for server to be ready..."
    sleep 3

    # Verify server started
    if lsof -i :5001 > /dev/null 2>&1; then
        echo "  ✓ Server is ready"
    else
        echo "  ✗ Failed to start server"
        echo "  Check logs: tail -f /tmp/realchat_flask.log"
        exit 1
    fi
fi

echo ""
echo "======================================"
echo "✓ RealChat is ready!"
echo "======================================"
echo ""
echo "Control Panel URL:"
echo "  http://localhost:5001"
echo ""
echo "Opening control panel in your browser..."
open http://localhost:5001

echo ""
echo "Server logs: tail -f /tmp/realchat_flask.log"
echo "To stop: pkill -f app_consolidated.py"
