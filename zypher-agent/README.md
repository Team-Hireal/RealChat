# Zypher Agent Service for RealChat

Deno-based AI agent service that integrates with the RealChat WeChat automation system.

## Prerequisites

- Deno 2.0+ ([install here](https://deno.land/))
- Anthropic API key configured in `../ai_settings.json` (shared with Flask backend)

## Setup

**No additional configuration needed!**

Zypher Agent automatically reads from `../ai_settings.json`, which is the same configuration file used by the Flask backend. This means:

- ✅ Same API key
- ✅ Same base URL (supports custom endpoints)
- ✅ Same model configuration
- ✅ No duplicate configuration

### Optional: Override Settings

If you want to use different settings for Zypher Agent:

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set your custom values:
```
ANTHROPIC_API_KEY=your_custom_key_here
ANTHROPIC_BASE_URL=https://your-custom-endpoint.com
```

## Running

### Development mode (with auto-reload):
```bash
deno task dev
```

### Production mode:
```bash
deno task start
```

The service will start on port 8000 by default.

## API Endpoints

### POST /api/chat
Process a chat message with the Zypher Agent.

**Request:**
```json
{
  "message": "Hello, how are you?",
  "model": "claude-sonnet-4-20250514",
  "history": [
    { "role": "user", "content": "Previous message" },
    { "role": "assistant", "content": "Previous response" }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": "[Agent] I'm doing well, thanks for asking!",
  "model": "zypher"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "zypher-agent"
}
```

## Integration with RealChat

The Zypher Agent service integrates with the RealChat system:

1. **Flask Backend** (port 5000) - WeChat automation
2. **Zypher Agent** (port 8000) - AI agent processing
3. **Frontend** - Switches between Claude and Zypher

When "Zypher" is selected in the AI Chat dropdown, requests are routed to this service.
