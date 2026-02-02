#!/bin/bash
# Quick Start Script for RealChat Consolidated

echo "🚀 Starting RealChat Consolidated Flask App..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python3 -c "import flask_socketio" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements_consolidated.txt -q
fi

# Check if WeChat is running
if ! pgrep -x "WeChat" > /dev/null; then
    echo "⚠️  WeChat is not running. Starting WeChat..."
    open -a WeChat
    sleep 2
fi

# Start the application
echo ""
echo "✅ Starting Flask application on http://localhost:5001"
echo ""
echo "API Endpoints:"
echo "  - Health: http://localhost:5001/api/health"
echo "  - Status: http://localhost:5001/api/status"
echo "  - Send Message: POST http://localhost:5001/api/wechat/send"
echo "  - Start Agent: POST http://localhost:5001/api/agent/start"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 app_consolidated.py
