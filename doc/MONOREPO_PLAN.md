# Flask Monorepo Consolidation Plan

## Overview

Consolidate all RealChat services into a single Flask application for easier deployment as a monorepo.

## Current Architecture (Multi-Service)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Flask Web App  │────▶│ Agent Orchestrator│────▶│  WeChat Bridge  │
│   (Port 5001)   │     │   (Port 8082)     │     │  (Ports 8080/81)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                        │                         │
        │                        │                         │
        ▼                        ▼                         ▼
   Python/Flask           Node.js/Express          Node.js/Wechaty
```

**Issues:**
- 3 separate services to deploy
- Node.js + Python dependencies
- Complex inter-service communication
- Multiple ports to manage

## Proposed Architecture (Flask Monorepo)

```
┌────────────────────────────────────────────────────────────┐
│                    Flask Application                        │
│                      (Port 5001)                           │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Web Routes  │  │ Agent Manager│  │ WeChat Connector│ │
│  │  (API/UI)    │  │ (AI Provider)│  │  (AppleScript)  │ │
│  └──────────────┘  └──────────────┘  └─────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Background Workers (Threading)                │ │
│  │  - Message Monitor                                    │ │
│  │  - AI Response Generator                              │ │
│  │  - Chat Scanner (OCR)                                 │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    Anthropic Claude API
```

**Benefits:**
- ✓ Single Python application
- ✓ One deployment unit
- ✓ Shared dependencies
- ✓ Simpler configuration
- ✓ Easier to debug and maintain

## Implementation Options

### Option 1: Pure Python (Recommended)

**Approach**: Replace Node.js services with Python equivalents

**Components:**
1. **Flask Web Server** - Already exists (`app.py`)
2. **Agent Manager** - Python module for AI integration
3. **WeChat Connector** - AppleScript + OCR (already in Python)
4. **Background Workers** - Python threading/asyncio

**Pros:**
- Single language (Python)
- No Node.js dependency
- Easier deployment
- Better integration

**Cons:**
- No Wechaty (Node.js library)
- Limited to AppleScript/OCR for WeChat

### Option 2: Hybrid with Subprocess Management

**Approach**: Flask manages Node.js services as subprocesses

**Components:**
1. **Flask Web Server** - Main application
2. **Node.js Services** - Run as subprocesses
3. **Process Manager** - Python subprocess management

**Pros:**
- Keep existing Node.js code
- Gradual migration possible

**Cons:**
- Still requires Node.js
- More complex deployment
- Process management overhead

### Option 3: Python-Wechaty (Future)

**Approach**: Use python-wechaty library

**Components:**
1. **Flask Web Server**
2. **Python-Wechaty** - Python port of Wechaty
3. **Agent Manager**

**Pros:**
- Pure Python
- Full WeChat API access

**Cons:**
- python-wechaty less mature
- May have compatibility issues

## Recommended: Option 1 (Pure Python)

This is the most practical for your use case since you're primarily using AppleScript automation anyway.

## Directory Structure

```
RealChat/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env                        # Configuration
├── Dockerfile                  # Single container
├── README.md
│
├── core/                       # Core modules
│   ├── __init__.py
│   ├── storage.py             # Unified storage
│   ├── config.py              # Configuration management
│   └── logger.py              # Logging utilities
│
├── services/                   # Business logic
│   ├── __init__.py
│   ├── wechat_service.py      # WeChat automation
│   ├── ai_service.py          # AI provider integration
│   ├── agent_service.py       # Agent orchestration
│   └── message_service.py     # Message handling
│
├── modules/                    # Feature modules
│   ├── __init__.py
│   ├── agent_manager.py       # Agent lifecycle
│   ├── message_analyzer.py    # Message analysis
│   ├── privacy_controller.py  # Privacy management
│   ├── moments_browser.py     # Moments browsing
│   └── relationship_analyzer.py
│
├── api/                        # API routes
│   ├── __init__.py
│   ├── chat_routes.py         # Chat endpoints
│   ├── agent_routes.py        # Agent endpoints
│   ├── config_routes.py       # Config endpoints
│   └── status_routes.py       # Status endpoints
│
├── workers/                    # Background workers
│   ├── __init__.py
│   ├── message_monitor.py     # Monitor messages
│   ├── ai_responder.py        # Generate responses
│   └── chat_scanner.py        # Scan chats
│
├── scripts/                    # Automation scripts
│   ├── scan_chats_ocr.py
│   ├── send_message.applescript
│   └── read_message.applescript
│
├── frontend/                   # React frontend
│   ├── dist/                  # Built files
│   └── src/
│
├── tests/                      # Test suite
│   ├── test_services.py
│   ├── test_api.py
│   └── test_workers.py
│
└── docs/                       # Documentation
    ├── API.md
    ├── DEPLOYMENT.md
    └── ARCHITECTURE.md
```

## Implementation Steps

### Phase 1: Core Consolidation
1. ✓ Create unified Flask app structure
2. ✓ Consolidate configuration management
3. ✓ Implement service layer
4. ✓ Add background workers

### Phase 2: Feature Migration
1. ✓ Migrate AI provider logic to Python
2. ✓ Integrate WeChat automation (AppleScript/OCR)
3. ✓ Add message monitoring
4. ✓ Implement agent orchestration

### Phase 3: API & Frontend
1. ✓ Create RESTful API endpoints
2. ✓ Add WebSocket support (Flask-SocketIO)
3. ✓ Integrate React frontend
4. ✓ Add real-time updates

### Phase 4: Deployment
1. ✓ Create single Dockerfile
2. ✓ Update deployment scripts
3. ✓ Add health checks
4. ✓ Configure logging

## Key Features to Preserve

### 1. AI Integration
- Anthropic Claude API (direct)
- Configurable model selection
- Custom API endpoints

### 2. WeChat Automation
- AppleScript-based messaging
- OCR chat scanning
- Message monitoring

### 3. Agent Management
- Multiple agent types
- Privacy controls
- Message analysis

### 4. Web Interface
- React frontend
- Real-time updates
- Configuration management

## Configuration (.env)

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_PORT=5001
SECRET_KEY=your-secret-key

# AI Provider
AI_API_KEY=your-anthropic-key
AI_BASE_URL=https://api.anthropic.com
AI_MODEL=claude-sonnet-4-5-20250929
AI_MAX_TOKENS=1024

# WeChat Configuration
WECHAT_CHAT_NAMES=File Transfer,文件传输助手
WECHAT_SCAN_METHOD=ocr  # ocr, applescript, manual

# Agent Configuration
AGENT_AUTO_START=false
AGENT_MONITOR_INTERVAL=3

# Storage
STORAGE_PATH=./data
LOG_LEVEL=INFO
```

## Deployment

### Single Container Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    tesseract-ocr \\
    tesseract-ocr-chi-sim \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5001

# Run application
CMD ["python", "app.py"]
```

### Docker Compose (Simplified)

```yaml
version: '3.8'

services:
  realchat:
    build: .
    container_name: realchat
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - AI_API_KEY=${AI_API_KEY}
      - AI_BASE_URL=${AI_BASE_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

### Direct Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## Migration Strategy

### Step 1: Create New Structure (Non-Breaking)
- Create new `services/` directory
- Implement service layer
- Keep existing code working

### Step 2: Gradual Migration
- Move AI logic to `ai_service.py`
- Move WeChat logic to `wechat_service.py`
- Update `app.py` to use services

### Step 3: Remove Old Services
- Deprecate Node.js services
- Remove `agent-orchestrator/`
- Remove `wechat-bridge/`
- Update docker-compose.yml

### Step 4: Testing & Validation
- Run test suite
- Verify all features work
- Performance testing

## Comparison

| Aspect | Current (Multi-Service) | Proposed (Monorepo) |
|--------|------------------------|---------------------|
| **Languages** | Python + Node.js | Python only |
| **Services** | 3 separate | 1 unified |
| **Ports** | 5001, 8080, 8081, 8082 | 5001 only |
| **Deployment** | Docker Compose | Single container |
| **Dependencies** | npm + pip | pip only |
| **Complexity** | High | Low |
| **Maintenance** | Complex | Simple |
| **Debugging** | Multi-service | Single app |

## Next Steps

1. **Review this plan** - Confirm approach
2. **Create new structure** - Set up directories
3. **Implement services** - Build service layer
4. **Migrate features** - Move functionality
5. **Test thoroughly** - Ensure everything works
6. **Deploy** - Single container deployment

## Questions to Consider

1. **Do you need Wechaty?** If not, pure Python is best
2. **What's your deployment target?** (Docker, VPS, cloud)
3. **Do you need real-time features?** (WebSocket support)
4. **What's your priority?** (Speed vs features)

## Recommendation

**Go with Option 1 (Pure Python)** because:
- You're already using AppleScript for WeChat
- Simpler deployment and maintenance
- Single language ecosystem
- Easier to debug and extend
- No Node.js dependency

Would you like me to implement this consolidated Flask monorepo?
