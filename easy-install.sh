#!/bin/bash

# RealChat Easy Installer
# One-command setup for local deployment

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo ""
echo -e "${PURPLE}╔════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                        ║${NC}"
echo -e "${PURPLE}║        RealChat Easy Installer        ║${NC}"
echo -e "${PURPLE}║                                        ║${NC}"
echo -e "${PURPLE}╔════════════════════════════════════════╗${NC}"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ Error: RealChat requires macOS for WeChat automation${NC}"
    echo "   WeChat desktop automation uses AppleScript (macOS only)"
    exit 1
fi

echo -e "${BLUE}📋 Checking prerequisites...${NC}"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION} installed${NC}"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js ${NODE_VERSION} installed${NC}"
else
    echo -e "${RED}❌ Node.js not found${NC}"
    echo "   Install from: https://nodejs.org/"
    exit 1
fi

# Check WeChat
if pgrep -x "WeChat" > /dev/null; then
    echo -e "${GREEN}✅ WeChat is running${NC}"
else
    echo -e "${YELLOW}⚠️  WeChat is not running${NC}"
    echo "   Please start WeChat before using RealChat"
fi

echo ""
echo -e "${BLUE}📦 Installing dependencies...${NC}"
echo ""

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -q flask flask-cors flask-socketio requests pynput pyautogui 2>&1 | grep -v "already satisfied" || true
echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Install Node.js dependencies for agent orchestrator
if [ -d "agent-orchestrator" ]; then
    echo "Installing Agent Orchestrator dependencies..."
    cd agent-orchestrator
    npm install --silent 2>&1 | grep -v "npm WARN" || true
    cd ..
    echo -e "${GREEN}✅ Agent Orchestrator dependencies installed${NC}"
fi

# Install Node.js dependencies for WeChat bridge
if [ -d "wechat-bridge" ]; then
    echo "Installing WeChat Bridge dependencies..."
    cd wechat-bridge
    npm install --silent 2>&1 | grep -v "npm WARN" || true
    cd ..
    echo -e "${GREEN}✅ WeChat Bridge dependencies installed${NC}"
fi

# Install React frontend dependencies
if [ -d "frontend" ]; then
    echo "Installing Frontend dependencies..."
    cd frontend
    npm install --silent 2>&1 | grep -v "npm WARN" || true
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
fi

echo ""
echo -e "${BLUE}⚙️  Configuring RealChat...${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your API key:${NC}"
    echo "   nano .env"
    echo "   Set: AI_API_KEY=your_key_here"
    echo ""
    read -p "Press Enter after configuring .env, or Ctrl+C to exit..."
fi

# Verify API key is set
source .env
if [ -z "$AI_API_KEY" ] || [ "$AI_API_KEY" = "your_api_key_here" ]; then
    echo -e "${RED}❌ API key not configured${NC}"
    echo "   Please edit .env and set AI_API_KEY"
    exit 1
fi

echo -e "${GREEN}✅ Configuration complete${NC}"

echo ""
echo -e "${BLUE}🔐 Checking permissions...${NC}"
echo ""

# Check accessibility permissions
echo "Checking accessibility permissions..."
if ! osascript -e 'tell application "System Events" to get name of processes' &> /dev/null; then
    echo -e "${YELLOW}⚠️  Accessibility permissions needed${NC}"
    echo ""
    echo "Please grant accessibility permissions:"
    echo "1. Open System Preferences → Security & Privacy → Privacy → Accessibility"
    echo "2. Click the lock to make changes"
    echo "3. Add Terminal (or your terminal app)"
    echo "4. Enable the checkbox"
    echo ""
    read -p "Press Enter after granting permissions..."
fi

echo -e "${GREEN}✅ Permissions configured${NC}"

echo ""
echo -e "${BLUE}🚀 Creating launch scripts...${NC}"
echo ""

# Create start script
cat > start-realchat.sh << 'EOF'
#!/bin/bash

echo "Starting RealChat..."

# Start Flask backend
echo "Starting Flask backend..."
python3 app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Start Agent Orchestrator (if exists)
if [ -d "agent-orchestrator" ]; then
    echo "Starting Agent Orchestrator..."
    cd agent-orchestrator
    npm start &
    AGENT_PID=$!
    cd ..
fi

# Start WeChat Bridge (if exists)
if [ -d "wechat-bridge" ]; then
    echo "Starting WeChat Bridge..."
    cd wechat-bridge
    npm start &
    BRIDGE_PID=$!
    cd ..
fi

echo ""
echo "✅ RealChat is running!"
echo ""
echo "Web Interface: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $FLASK_PID $AGENT_PID $BRIDGE_PID 2>/dev/null; exit" INT
wait
EOF

chmod +x start-realchat.sh

# Create stop script
cat > stop-realchat.sh << 'EOF'
#!/bin/bash

echo "Stopping RealChat..."

# Kill Flask
pkill -f "python3 app.py"

# Kill Node.js services
pkill -f "agent-orchestrator"
pkill -f "wechat-bridge"

echo "✅ RealChat stopped"
EOF

chmod +x stop-realchat.sh

echo -e "${GREEN}✅ Launch scripts created${NC}"

echo ""
echo -e "${PURPLE}╔════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                        ║${NC}"
echo -e "${PURPLE}║     Installation Complete! 🎉         ║${NC}"
echo -e "${PURPLE}║                                        ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ RealChat is ready to use!${NC}"
echo ""
echo -e "${BLUE}📚 Quick Start:${NC}"
echo ""
echo "  1. Start RealChat:"
echo -e "     ${YELLOW}./start-realchat.sh${NC}"
echo ""
echo "  2. Open web interface:"
echo -e "     ${YELLOW}http://localhost:5001${NC}"
echo ""
echo "  3. Stop RealChat:"
echo -e "     ${YELLOW}./stop-realchat.sh${NC}"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo "  - Setup Guide: SETUP_GUIDE.md"
echo "  - Architecture: COMPLETE_ARCHITECTURE.md"
echo "  - Quick Start: QUICKSTART.md"
echo ""
echo -e "${BLUE}🔧 Configuration:${NC}"
echo "  - Edit .env to change settings"
echo "  - Click ⚙️ Settings in web interface"
echo ""
echo -e "${GREEN}Ready to start? Run: ./start-realchat.sh${NC}"
echo ""
