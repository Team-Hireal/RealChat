# Zypher Agent Integration Guide

This guide explains how to set up and use the Zypher Agent with RealChat.

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (port 5175)    │
└────────┬────────┘
         │
         ├──────────────┬──────────────┐
         │              │              │
    ┌────▼────┐    ┌────▼────┐   ┌────▼────┐
    │  Flask  │    │ Zypher  │   │ WeChat  │
    │  (5000) │    │ (8000)  │   │ Bridge  │
    └────┬────┘    └─────────┘   └─────────┘
         │
    ┌────▼────┐
    │ WeChat  │
    │   App   │
    └─────────┘
```

## Setup Instructions

### 1. Install Deno

If you haven't installed Deno yet:

```bash
# macOS/Linux
curl -fsSL https://deno.land/install.sh | sh

# Or with Homebrew
brew install deno
```

### 2. Configure Zypher Agent

```bash
cd zypher-agent
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 3. Install Dependencies

Deno will automatically install dependencies when you run the service.

### 4. Start Services

#### Option A: Start All Services Together
```bash
./start_with_zypher.sh
```

#### Option B: Start Services Individually

**Terminal 1 - Zypher Agent:**
```bash
cd zypher-agent
deno task start
```

**Terminal 2 - Flask Backend:**
```bash
source venv/bin/activate
python app_consolidated.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Verify Services

Check that all services are running:

```bash
# Check Zypher Agent
curl http://localhost:8000/health

# Check Flask Backend
curl http://localhost:5000/api/health

# Check Frontend
open http://localhost:5175
```

## Using Zypher Agent

### In the Frontend

1. Open the control panel at `http://localhost:5175`
2. Go to the **AI Chat** section
3. Click the dropdown that says "Claude"
4. Select **"Zypher"**
5. Start chatting!

### How It Works

1. **User sends message in WeChat** → OCR detects it
2. **Message appears in ChatBox** → Routed to selected AI (Claude or Zypher)
3. **Zypher Agent processes** → Uses advanced reasoning and planning
4. **Response sent to WeChat** → With `[Agent]` prefix
5. **OCR filters agent messages** → Prevents infinite loops

### Differences: Claude vs Zypher

| Feature | Claude | Zypher |
|---------|--------|--------|
| **Type** | Direct API call | Agent framework |
| **Reasoning** | Single-turn | Multi-step planning |
| **Tools** | None | Can use MCP tools |
| **Speed** | Fast | Slightly slower |
| **Use Case** | Quick responses | Complex tasks |

## Troubleshooting

### Zypher Agent Not Starting

**Error:** `Zypher Agent service is not running`

**Solution:**
```bash
cd zypher-agent
deno task start
```

Check logs for errors. Common issues:
- Missing `ANTHROPIC_API_KEY` in `.env`
- Port 8000 already in use
- Deno not installed

### Connection Refused

**Error:** `Failed to connect to Zypher Agent`

**Check:**
1. Is Zypher Agent running? `curl http://localhost:8000/health`
2. Is the port correct? Check `ZYPHER_PORT` in `.env`
3. Firewall blocking connections?

### API Key Issues

**Error:** `Environment variable ANTHROPIC_API_KEY is not set`

**Solution:**
1. Copy `.env.example` to `.env` in `zypher-agent/`
2. Add your API key: `ANTHROPIC_API_KEY=sk-ant-xxxxx`
3. Restart Zypher Agent

## Advanced Configuration

### Custom Port

Edit `zypher-agent/.env`:
```
ZYPHER_PORT=9000
```

Update Flask backend `.env`:
```
ZYPHER_URL=http://localhost:9000
```

### Adding MCP Tools

To give Zypher web crawling capabilities:

1. Get a Firecrawl API key from https://firecrawl.dev
2. Add to `zypher-agent/.env`:
```
FIRECRAWL_API_KEY=fc-xxxxx
```
3. Uncomment the MCP registration code in `main.ts`

### Custom Models

Edit the model in `zypher-agent/main.ts`:
```typescript
const modelName = model || "claude-opus-4-20250514";  // Use Opus instead
```

## Development

### Watch Mode

For development with auto-reload:
```bash
cd zypher-agent
deno task dev
```

### Logs

Zypher Agent logs to console. To save logs:
```bash
deno task start > zypher.log 2>&1
```

### Testing

Test the Zypher endpoint directly:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "claude-sonnet-4-20250514"
  }'
```

## Next Steps

- [ ] Add more MCP tools for enhanced capabilities
- [ ] Implement conversation memory
- [ ] Add support for file uploads
- [ ] Create custom tools for WeChat-specific actions

## Support

If you encounter issues:
1. Check the logs in all three terminals
2. Verify all services are running
3. Check API keys are configured
4. Review the troubleshooting section above
