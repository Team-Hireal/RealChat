# How to Start RealChat - Complete Guide

## 🚀 Quick Start (Recommended)

The easiest way to start the project:

```bash
./setup_and_start.sh
```

This interactive script will:
1. ✓ Check Python installation
2. ✓ Check WeChat status
3. ✓ Create/verify .env configuration
4. ✓ Set up virtual environment
5. ✓ Install dependencies
6. ✓ Run validation tests
7. ✓ Start the application

---

## 📋 Prerequisites

Before starting, ensure you have:

### Required
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **WeChat Desktop App** - Must be running
- **Anthropic API Key** - [Get one here](https://console.anthropic.com/)

### Optional (for OCR chat scanning)
- **Tesseract OCR** - `brew install tesseract tesseract-lang`

### Optional (for Docker deployment)
- **Docker** - [Download](https://www.docker.com/get-started)

---

## 🔧 Manual Setup (Step by Step)

If you prefer manual setup:

### Step 1: Clone/Navigate to Project

```bash
cd /Users/test/Desktop/Hireal/RealChat
```

### Step 2: Create Configuration File

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
# Flask Configuration
FLASK_ENV=development
FLASK_PORT=5001
SECRET_KEY=your-secret-key-here

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
```

**Important**: Edit `.env` and replace `your-anthropic-api-key-here` with your actual API key.

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements_consolidated.txt
```

### Step 5: Create Data Directories

```bash
mkdir -p data logs
```

### Step 6: Verify Setup

```bash
python3 test_consolidated.py
```

You should see:
```
✓ Services imported successfully
✓ WeChat service initialized
✓ AI service initialized
✓ WeChat detection working
✓ AI service status working
✓ Flask app imports successfully

Passed: 5/5 tests
```

### Step 7: Start WeChat

Make sure WeChat is running:

```bash
open -a WeChat
```

### Step 8: Start the Application

Choose one of the methods below.

---

## 🎯 Starting Methods

### Method 1: Development Mode (Recommended for Testing)

**Best for**: Local development, testing, debugging

```bash
python3 app_consolidated.py
```

**Features**:
- Auto-reload on code changes
- Debug mode enabled
- Detailed error messages
- Access at: http://localhost:5001

**To stop**: Press `Ctrl+C`

---

### Method 2: Production Mode (Gunicorn)

**Best for**: Production deployment, better performance

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 app_consolidated:app
```

**Features**:
- Production-ready WSGI server
- Better performance
- WebSocket support via eventlet
- Access at: http://localhost:5001

**To stop**: Press `Ctrl+C`

---

### Method 3: Docker (Single Container)

**Best for**: Isolated deployment, easy distribution

#### Option A: Docker Compose (Recommended)

```bash
# Start
docker-compose -f docker-compose.consolidated.yml up -d

# View logs
docker-compose -f docker-compose.consolidated.yml logs -f

# Stop
docker-compose -f docker-compose.consolidated.yml down
```

#### Option B: Docker Run

```bash
# Build image
docker build -f Dockerfile.consolidated -t realchat:latest .

# Run container
docker run -d \
  --name realchat \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  realchat:latest

# View logs
docker logs -f realchat

# Stop
docker stop realchat
docker rm realchat
```

---

### Method 4: Background Process (systemd)

**Best for**: Linux servers, auto-start on boot

Create `/etc/systemd/system/realchat.service`:

```ini
[Unit]
Description=RealChat Flask Application
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/RealChat
Environment="PATH=/path/to/RealChat/venv/bin"
ExecStart=/path/to/RealChat/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 app_consolidated:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable realchat
sudo systemctl start realchat
sudo systemctl status realchat
```

---

## ✅ Verification

After starting, verify the application is running:

### 1. Check Health Endpoint

```bash
curl http://localhost:5001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "wechat": true,
    "ai": true
  }
}
```

### 2. Check Status Endpoint

```bash
curl http://localhost:5001/api/status
```

Expected response:
```json
{
  "agent_running": false,
  "wechat_running": true,
  "ai_status": {
    "provider": "Anthropic Claude",
    "model": "claude-sonnet-4-5-20250929",
    "api_key_configured": true,
    "healthy": true
  },
  "config": {
    "chat_names": ["File Transfer", "文件传输助手"],
    "scan_method": "applescript",
    "ai_model": "claude-sonnet-4-5-20250929"
  }
}
```

### 3. Test Sending a Message

```bash
curl -X POST http://localhost:5001/api/wechat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Test from API"}'
```

### 4. Test AI Response

```bash
curl -X POST http://localhost:5001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

---

## 🎮 Using the Application

### Web Interface

Open in browser: http://localhost:5001

### Start the AI Agent

```bash
curl -X POST http://localhost:5001/api/agent/start
```

Or use the web interface.

### Stop the AI Agent

```bash
curl -X POST http://localhost:5001/api/agent/stop
```

### Scan Available Chats

```bash
curl http://localhost:5001/api/wechat/chats?max=10
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution**: Install dependencies

```bash
pip install -r requirements_consolidated.txt
```

### Issue: "WeChat not running"

**Solution**: Start WeChat

```bash
open -a WeChat
```

### Issue: "Port 5001 already in use"

**Solution**: Kill the process or use a different port

```bash
# Find process
lsof -i :5001

# Kill it
kill -9 <PID>

# Or use different port
FLASK_PORT=5002 python3 app_consolidated.py
```

### Issue: "AI API key not configured"

**Solution**: Edit `.env` file

```bash
nano .env
# Add your API key to AI_API_KEY=
```

### Issue: "Permission denied" when running scripts

**Solution**: Make scripts executable

```bash
chmod +x setup_and_start.sh
chmod +x start_consolidated.sh
```

### Issue: "Import error: flask_socketio"

**Solution**: Install Flask-SocketIO

```bash
pip install flask-socketio python-socketio eventlet
```

### Issue: Docker build fails

**Solution**: Check Docker is running

```bash
docker --version
docker ps
```

---

## 📊 Monitoring

### View Logs

**Development mode**: Logs appear in terminal

**Docker**:
```bash
docker logs -f realchat
```

**Log files**: Check `logs/` directory

### Check Process Status

```bash
# Check if running
ps aux | grep app_consolidated

# Check port
lsof -i :5001

# Check health
curl http://localhost:5001/api/health
```

---

## 🔄 Updating

To update the application:

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements_consolidated.txt --upgrade

# Restart application
# (Stop current process and start again)
```

---

## 🛑 Stopping the Application

### Development Mode
Press `Ctrl+C` in the terminal

### Docker
```bash
docker-compose -f docker-compose.consolidated.yml down
# or
docker stop realchat
```

### systemd
```bash
sudo systemctl stop realchat
```

---

## 📝 Configuration Options

Edit `.env` to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `FLASK_PORT` | Port to run on | 5001 |
| `AI_API_KEY` | Anthropic API key | (required) |
| `AI_MODEL` | Claude model to use | claude-sonnet-4-5-20250929 |
| `WECHAT_CHAT_NAMES` | Default chats to monitor | File Transfer,文件传输助手 |
| `WECHAT_SCAN_METHOD` | Chat scanning method | applescript |
| `AGENT_AUTO_START` | Auto-start agent on launch | false |
| `AGENT_MONITOR_INTERVAL` | Seconds between checks | 3 |

---

## 🎯 Quick Reference

### Start Commands

```bash
# Interactive setup
./setup_and_start.sh

# Development
python3 app_consolidated.py

# Production
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5001 app_consolidated:app

# Docker
docker-compose -f docker-compose.consolidated.yml up -d
```

### API Endpoints

```bash
# Health check
curl http://localhost:5001/api/health

# Get status
curl http://localhost:5001/api/status

# Send message
curl -X POST http://localhost:5001/api/wechat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Start agent
curl -X POST http://localhost:5001/api/agent/start

# Stop agent
curl -X POST http://localhost:5001/api/agent/stop
```

---

## 📚 Additional Resources

- **Architecture**: See `MONOREPO_PLAN.md`
- **API Documentation**: See `README_CONSOLIDATED.md`
- **Testing**: See `TESTING_GUIDE.md`
- **Deployment**: See `CONSOLIDATION_COMPLETE.md`

---

## ✨ Summary

**Easiest way to start**:
```bash
./setup_and_start.sh
```

**Manual start**:
```bash
pip install -r requirements_consolidated.txt
python3 app_consolidated.py
```

**Access**: http://localhost:5001

**Need help?** Check the troubleshooting section above or review the documentation files.

---

**Last Updated**: 2026-02-01
**Version**: 2.0.0 (Consolidated Monorepo)
