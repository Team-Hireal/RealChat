#!/bin/bash
# RealChat - Quick Start Script (Consolidated Monorepo)

set -e

echo "======================================================================"
echo "RealChat - Consolidated Flask Monorepo"
echo "======================================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
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
    echo "✓ Created .env file. Please edit it with your API key."
    echo ""
fi

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.9+"; exit 1; }
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements_consolidated.txt
echo "✓ Dependencies installed"
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data logs
echo "✓ Data directories created"
echo ""

# Check if WeChat is running
echo "Checking WeChat status..."
if pgrep -x "WeChat" > /dev/null; then
    echo "✓ WeChat is running"
else
    echo "⚠️  WeChat is not running. Please start WeChat."
fi
echo ""

# Display configuration
echo "======================================================================"
echo "Configuration"
echo "======================================================================"
echo "Flask Port: ${FLASK_PORT:-5001}"
echo "AI Model: ${AI_MODEL:-claude-sonnet-4-5-20250929}"
echo "WeChat Scan Method: ${WECHAT_SCAN_METHOD:-applescript}"
echo "Agent Auto Start: ${AGENT_AUTO_START:-false}"
echo ""

# Ask user what to do
echo "======================================================================"
echo "What would you like to do?"
echo "======================================================================"
echo "1) Start Flask app (development mode)"
echo "2) Start Flask app (production mode with gunicorn)"
echo "3) Run tests"
echo "4) Build Docker image"
echo "5) Start with Docker Compose"
echo "6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "Starting Flask app in development mode..."
        echo "Access at: http://localhost:5001"
        echo "Press Ctrl+C to stop"
        echo ""
        python3 app_consolidated.py
        ;;
    2)
        echo ""
        echo "Starting Flask app with gunicorn..."
        echo "Access at: http://localhost:5001"
        echo "Press Ctrl+C to stop"
        echo ""
        gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 app_consolidated:app
        ;;
    3)
        echo ""
        echo "Running tests..."
        pytest tests/ -v
        ;;
    4)
        echo ""
        echo "Building Docker image..."
        docker build -f Dockerfile.consolidated -t realchat:latest .
        echo "✓ Docker image built: realchat:latest"
        ;;
    5)
        echo ""
        echo "Starting with Docker Compose..."
        docker-compose -f docker-compose.consolidated.yml up -d
        echo "✓ RealChat started"
        echo "Access at: http://localhost:5001"
        echo ""
        echo "To view logs: docker-compose -f docker-compose.consolidated.yml logs -f"
        echo "To stop: docker-compose -f docker-compose.consolidated.yml down"
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
