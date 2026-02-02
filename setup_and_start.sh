#!/bin/bash
# RealChat - Complete Setup and Start Guide
# This script will guide you through the entire setup process

set -e

echo "======================================================================"
echo "RealChat - Complete Setup and Start Guide"
echo "======================================================================"
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi
echo ""

# Step 2: Check WeChat
echo "Step 2: Checking WeChat..."
if pgrep -x "WeChat" > /dev/null; then
    echo "✓ WeChat is running"
else
    echo "⚠️  WeChat is not running"
    echo "   Please start WeChat before running the agent"
    read -p "   Start WeChat now? (y/n): " start_wechat
    if [ "$start_wechat" = "y" ]; then
        open -a WeChat
        echo "   Waiting for WeChat to start..."
        sleep 3
    fi
fi
echo ""

# Step 3: Check/Create .env file
echo "Step 3: Checking configuration..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=development
FLASK_PORT=5001
SECRET_KEY=dev-secret-key-change-in-production

# AI Provider (Anthropic Claude)
AI_API_KEY=your-anthropic-api-key-here
AI_BASE_URL=https://api.anthropic.com
AI_MODEL=claude-sonnet-4-5-20250929
AI_MAX_TOKENS=1024

# WeChat Configuration
WECHAT_CHAT_NAMES=File Transfer,文件传输助手
WECHAT_SCAN_METHOD=applescript

# Agent Configuration
AGENT_AUTO_START=false
AGENT_MONITOR_INTERVAL=3

# Storage
STORAGE_PATH=./data
LOG_LEVEL=INFO
EOF
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your Anthropic API key"
    echo "   Current API key: $(grep AI_API_KEY .env | cut -d'=' -f2)"
    echo ""
    read -p "   Do you want to edit .env now? (y/n): " edit_env
    if [ "$edit_env" = "y" ]; then
        ${EDITOR:-nano} .env
    else
        echo "   Remember to edit .env before starting the agent!"
    fi
else
    echo "✓ .env file exists"
    API_KEY=$(grep AI_API_KEY .env | cut -d'=' -f2)
    if [ "$API_KEY" = "your-anthropic-api-key-here" ] || [ -z "$API_KEY" ]; then
        echo "⚠️  API key not configured in .env"
        read -p "   Edit .env now? (y/n): " edit_env
        if [ "$edit_env" = "y" ]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo "✓ API key configured"
    fi
fi
echo ""

# Step 4: Create virtual environment
echo "Step 4: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi
echo ""

# Step 5: Activate virtual environment and install dependencies
echo "Step 5: Installing dependencies..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Check if dependencies are installed
if python3 -c "import flask" 2>/dev/null; then
    echo "✓ Dependencies already installed"
else
    echo "Installing Python packages..."
    pip install -r requirements_consolidated.txt -q
    echo "✓ Dependencies installed"
fi
echo ""

# Step 6: Create data directories
echo "Step 6: Creating data directories..."
mkdir -p data logs
echo "✓ Data directories ready"
echo ""

# Step 7: Run validation test
echo "Step 7: Running validation tests..."
python3 test_consolidated.py
TEST_RESULT=$?
echo ""

if [ $TEST_RESULT -ne 0 ]; then
    echo "⚠️  Some tests failed. Please check the errors above."
    read -p "Continue anyway? (y/n): " continue_anyway
    if [ "$continue_anyway" != "y" ]; then
        exit 1
    fi
fi

# Step 8: Display configuration
echo "======================================================================"
echo "Configuration Summary"
echo "======================================================================"
echo "Flask Port: $(grep FLASK_PORT .env | cut -d'=' -f2)"
echo "AI Model: $(grep AI_MODEL .env | cut -d'=' -f2)"
echo "WeChat Scan Method: $(grep WECHAT_SCAN_METHOD .env | cut -d'=' -f2)"
echo "Agent Auto Start: $(grep AGENT_AUTO_START .env | cut -d'=' -f2)"
echo ""

# Step 9: Choose how to start
echo "======================================================================"
echo "How would you like to start RealChat?"
echo "======================================================================"
echo "1) Development mode (Flask debug, auto-reload)"
echo "2) Production mode (Gunicorn)"
echo "3) Docker (single container)"
echo "4) Just setup, don't start"
echo "5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "======================================================================"
        echo "Starting RealChat in Development Mode"
        echo "======================================================================"
        echo ""
        echo "Access the application at: http://localhost:5001"
        echo ""
        echo "API Endpoints:"
        echo "  - Health: http://localhost:5001/api/health"
        echo "  - Status: http://localhost:5001/api/status"
        echo "  - Chats:  http://localhost:5001/api/wechat/chats"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        python3 app_consolidated.py
        ;;
    2)
        echo ""
        echo "======================================================================"
        echo "Starting RealChat in Production Mode"
        echo "======================================================================"
        echo ""
        echo "Access the application at: http://localhost:5001"
        echo "Press Ctrl+C to stop"
        echo ""
        gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 app_consolidated:app
        ;;
    3)
        echo ""
        echo "======================================================================"
        echo "Starting RealChat with Docker"
        echo "======================================================================"
        echo ""

        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not found. Please install Docker first."
            echo "   Visit: https://www.docker.com/get-started"
            exit 1
        fi

        echo "Building Docker image..."
        docker build -f Dockerfile.consolidated -t realchat:latest .

        echo ""
        echo "Starting container..."
        docker run -d \
            --name realchat \
            -p 5001:5001 \
            --env-file .env \
            -v $(pwd)/data:/app/data \
            -v $(pwd)/logs:/app/logs \
            realchat:latest

        echo ""
        echo "✓ RealChat started in Docker"
        echo ""
        echo "Access at: http://localhost:5001"
        echo ""
        echo "Useful commands:"
        echo "  View logs:    docker logs -f realchat"
        echo "  Stop:         docker stop realchat"
        echo "  Remove:       docker rm realchat"
        echo "  Restart:      docker restart realchat"
        ;;
    4)
        echo ""
        echo "✓ Setup complete! You can start the application later with:"
        echo ""
        echo "  Development:  python3 app_consolidated.py"
        echo "  Production:   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 app_consolidated:app"
        echo "  Docker:       docker-compose -f docker-compose.consolidated.yml up -d"
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
