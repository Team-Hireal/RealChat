#!/bin/bash

echo "============================================"
echo "🚀 RealChat AI Agent - Quick Start"
echo "============================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   nano .env"
    echo ""
    echo "   At minimum, you need to set:"
    echo "   - ANTHROPIC_API_KEY=your_key_here"
    echo ""
    read -p "Press Enter after you've configured .env, or Ctrl+C to exit..."
fi

# Check if ANTHROPIC_API_KEY is set
source .env
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo "❌ ANTHROPIC_API_KEY is not set in .env"
    echo "   Please edit .env and add your Anthropic API key"
    echo "   Get one from: https://console.anthropic.com/"
    exit 1
fi

echo "✅ Configuration looks good!"
echo ""

# Ask which mode to run
echo "Choose deployment mode:"
echo "  1) Full stack (WeChat Bridge + AI Agent + Web App)"
echo "  2) AI Agent only (connect to existing WeChat Bridge)"
echo "  3) WeChat Bridge only"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting full stack..."
        docker-compose up -d
        ;;
    2)
        echo ""
        echo "🚀 Starting AI Agent only..."
        docker-compose up -d agent-orchestrator
        ;;
    3)
        echo ""
        echo "🚀 Starting WeChat Bridge only..."
        docker-compose up -d wechat-bridge
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "============================================"
echo "✅ Services Started!"
echo "============================================"
echo ""
echo "📱 Next steps:"
echo ""
echo "1. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "2. Check status:"
echo "   curl http://localhost:8081/status  # WeChat Bridge"
echo "   curl http://localhost:8082/health  # AI Agent"
echo ""
echo "3. Login to WeChat:"
echo "   - Watch the logs for QR code URL"
echo "   - Scan with your mobile WeChat app"
echo ""
echo "4. Access web interface:"
echo "   http://localhost:5001"
echo ""
echo "5. Stop services:"
echo "   docker-compose down"
echo ""
echo "============================================"
echo ""

# Ask if user wants to view logs
read -p "View logs now? [y/N]: " view_logs
if [ "$view_logs" = "y" ] || [ "$view_logs" = "Y" ]; then
    docker-compose logs -f
fi
