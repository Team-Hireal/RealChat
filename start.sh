#!/bin/bash

echo "============================================"
echo "🚀 RealChat - Complete Startup Guide"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "   Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
else
    echo -e "${GREEN}✅ Docker is installed${NC}"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "   Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
else
    echo -e "${GREEN}✅ Docker Compose is installed${NC}"
fi

echo ""
echo "============================================"
echo "⚙️  Configuration Setup"
echo "============================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    cp .env.example .env
fi

# Check if API key is configured
source .env
if [ -z "$AI_API_KEY" ] || [ "$AI_API_KEY" = "your_api_key_here" ]; then
    echo -e "${RED}❌ API key not configured${NC}"
    echo ""
    echo "Please edit .env and add your Anthropic API key:"
    echo ""
    echo -e "${BLUE}nano .env${NC}"
    echo ""
    echo "Set the following:"
    echo -e "${YELLOW}AI_API_KEY=sk-ant-xxxxx${NC}"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    echo ""
    read -p "Press Enter after you've configured .env, or Ctrl+C to exit..."

    # Re-check after user edits
    source .env
    if [ -z "$AI_API_KEY" ] || [ "$AI_API_KEY" = "your_api_key_here" ]; then
        echo -e "${RED}❌ API key still not configured. Exiting.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ API key configured${NC}"
echo ""

echo "============================================"
echo "🏗️  Building and Starting Services"
echo "============================================"
echo ""

# Ask which services to start
echo "Which services do you want to start?"
echo ""
echo "  1) Full Stack (WeChat Bridge + AI Agent + Web App) - Recommended"
echo "  2) Web App Only (Classic mode - Desktop WeChat)"
echo "  3) AI Agent Stack (WeChat Bridge + AI Agent)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}🚀 Starting full stack...${NC}"
        docker-compose up -d --build
        SERVICES="all"
        ;;
    2)
        echo ""
        echo -e "${BLUE}🚀 Starting web app only...${NC}"
        docker-compose up -d --build web-app
        SERVICES="web-app"
        ;;
    3)
        echo ""
        echo -e "${BLUE}🚀 Starting AI agent stack...${NC}"
        docker-compose up -d --build wechat-bridge agent-orchestrator
        SERVICES="ai-stack"
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "============================================"
echo "✅ Services Started!"
echo "============================================"
echo ""

# Check service status
echo "📊 Service Status:"
echo ""

if [ "$SERVICES" = "all" ] || [ "$SERVICES" = "ai-stack" ]; then
    # Check WeChat Bridge
    if curl -s http://localhost:8081/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ WeChat Bridge: Running${NC}"
        echo "   http://localhost:8081/status"
    else
        echo -e "${RED}❌ WeChat Bridge: Not responding${NC}"
    fi

    # Check Agent Orchestrator
    if curl -s http://localhost:8082/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Agent Orchestrator: Running${NC}"
        echo "   http://localhost:8082/health"
    else
        echo -e "${RED}❌ Agent Orchestrator: Not responding${NC}"
    fi
fi

if [ "$SERVICES" = "all" ] || [ "$SERVICES" = "web-app" ]; then
    # Check Web App
    if curl -s http://localhost:5001 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Web Application: Running${NC}"
        echo "   http://localhost:5001"
    else
        echo -e "${RED}❌ Web Application: Not responding${NC}"
    fi
fi

echo ""
echo "============================================"
echo "📱 Next Steps"
echo "============================================"
echo ""

if [ "$SERVICES" = "all" ] || [ "$SERVICES" = "ai-stack" ]; then
    echo "1️⃣  Login to WeChat (Mobile):"
    echo "   - Watch logs for QR code:"
    echo -e "     ${BLUE}docker-compose logs -f wechat-bridge${NC}"
    echo "   - Open WeChat on your phone"
    echo "   - Go to: Settings → WeChat Web"
    echo "   - Scan the QR code"
    echo ""
fi

echo "2️⃣  Access Web Interface:"
echo -e "   ${GREEN}http://localhost:5001${NC}"
echo ""

echo "3️⃣  Configure AI Settings:"
echo "   - Click the ⚙️ Settings button (top-right)"
echo "   - Verify your API key"
echo "   - Choose AI provider"
echo "   - Save configuration"
echo ""

if [ "$SERVICES" = "all" ] || [ "$SERVICES" = "ai-stack" ]; then
    echo "4️⃣  Start Chatting:"
    echo "   - Send a message to any WeChat contact"
    echo "   - AI will respond automatically!"
    echo ""
fi

echo "============================================"
echo "🛠️  Useful Commands"
echo "============================================"
echo ""
echo "View logs:"
echo -e "  ${BLUE}docker-compose logs -f${NC}"
echo ""
echo "Stop services:"
echo -e "  ${BLUE}docker-compose down${NC}"
echo ""
echo "Restart services:"
echo -e "  ${BLUE}docker-compose restart${NC}"
echo ""
echo "Check status:"
echo -e "  ${BLUE}docker-compose ps${NC}"
echo ""

echo "============================================"
echo "📚 Documentation"
echo "============================================"
echo ""
echo "Setup Guide:          SETUP_GUIDE.md"
echo "Settings Guide:       SETTINGS_UPDATE.md"
echo "Architecture:         ARCHITECTURE_DIAGRAM.md"
echo "Implementation:       IMPLEMENTATION_SUMMARY.md"
echo ""

echo "============================================"
echo "🎉 RealChat is Ready!"
echo "============================================"
echo ""

# Ask if user wants to view logs
read -p "View logs now? [y/N]: " view_logs
if [ "$view_logs" = "y" ] || [ "$view_logs" = "Y" ]; then
    docker-compose logs -f
fi
