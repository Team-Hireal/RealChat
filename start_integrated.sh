#!/bin/bash

echo "🚀 Starting RealChat with WeChat Bridge Integration"
echo "===================================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Install WeChat Bridge dependencies
echo "📦 Installing WeChat Bridge dependencies..."
cd wechat-bridge
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Start WeChat Bridge in background
echo "🌉 Starting WeChat Bridge..."
cd wechat-bridge
node index.js > ../logs/bridge.log 2>&1 &
BRIDGE_PID=$!
cd ..
echo "✅ WeChat Bridge started (PID: $BRIDGE_PID)"
echo "   Logs: logs/bridge.log"
echo "   WebSocket: ws://localhost:8080"
echo "   HTTP: http://localhost:8081"
echo ""

# Wait for bridge to start
sleep 3

# Start Flask backend
echo "🐍 Starting Flask backend..."
source venv/bin/activate
python3 app_consolidated.py > logs/flask.log 2>&1 &
FLASK_PID=$!
echo "✅ Flask backend started (PID: $FLASK_PID)"
echo "   Logs: logs/flask.log"
echo "   API: http://localhost:5001"
echo ""

# Wait for Flask to start
sleep 3

# Start React frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm run dev > ../logs/react.log 2>&1 &
REACT_PID=$!
cd ..
echo "✅ React frontend started (PID: $REACT_PID)"
echo "   Logs: logs/react.log"
echo "   URL: http://localhost:5173"
echo ""

echo "===================================================="
echo "✅ All services started successfully!"
echo ""
echo "📱 WeChat Bridge: http://localhost:8081/status"
echo "🐍 Flask Backend: http://localhost:5001/api/status"
echo "⚛️  React Frontend: http://localhost:5173"
echo ""
echo "📋 Process IDs:"
echo "   Bridge: $BRIDGE_PID"
echo "   Flask: $FLASK_PID"
echo "   React: $REACT_PID"
echo ""
echo "To stop all services:"
echo "   kill $BRIDGE_PID $FLASK_PID $REACT_PID"
echo ""
echo "Press Ctrl+C to stop all services..."

# Trap Ctrl+C and cleanup
trap "echo ''; echo '🛑 Stopping all services...'; kill $BRIDGE_PID $FLASK_PID $REACT_PID 2>/dev/null; echo '✅ All services stopped'; exit 0" INT TERM

# Wait for any process to exit
wait
