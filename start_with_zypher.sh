#!/bin/bash

# RealChat Integrated Startup Script
# Starts Flask backend and Zypher Agent service

echo "🚀 Starting RealChat services..."

# Check if Deno is installed
if ! command -v deno &> /dev/null; then
    echo "❌ Deno is not installed. Please install Deno 2.0+ from https://deno.land/"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Python virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate Python virtual environment
source venv/bin/activate

# Zypher Agent will automatically read from ai_settings.json
# No need to configure separate .env file
echo "📝 Zypher Agent will use settings from ai_settings.json"

# Start Zypher Agent in background
echo "🤖 Starting Zypher Agent service (port 8000)..."
cd zypher-agent
deno task start &
ZYPHER_PID=$!
cd ..

# Wait for Zypher Agent to start
sleep 3

# Start Flask backend
echo "🐍 Starting Flask backend (port 5000)..."
python app_consolidated.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 2

echo ""
echo "✅ RealChat services started successfully!"
echo ""
echo "📊 Service Status:"
echo "  - Flask Backend: http://localhost:5000 (PID: $FLASK_PID)"
echo "  - Zypher Agent: http://localhost:8000 (PID: $ZYPHER_PID)"
echo "  - Frontend: http://localhost:5175 (start separately with: cd frontend && npm run dev)"
echo ""
echo "🛑 To stop services:"
echo "  kill $FLASK_PID $ZYPHER_PID"
echo ""
echo "📝 Logs:"
echo "  - Flask: Check terminal output"
echo "  - Zypher: Check terminal output"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $FLASK_PID $ZYPHER_PID 2>/dev/null; exit 0" INT TERM

# Keep script running
wait
