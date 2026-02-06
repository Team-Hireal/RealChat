# ✅ Zypher Agent - Unified Configuration

## Summary

Zypher Agent now uses the **same configuration** as your Flask backend!

### Configuration Source

**File:** `/Users/test/Desktop/Hireal/RealChat/ai_settings.json`

```json
{
  "api_key": "sk-xpXNVYRC6LM7xMaxeXyOKnGwD8JHhrVE62fWewJ9J0XYwbhR",
  "base_url": "https://hone.vvvv.ee",
  "model": "claude-sonnet-4-5-20250929"
}
```

### What This Means

✅ **Single source of truth** - Update API settings in one place
✅ **Same API endpoint** - Both Claude and Zypher use `https://hone.vvvv.ee`
✅ **Same API key** - No duplicate configuration needed
✅ **Same model** - Consistent AI model across services

### How It Works

1. **Zypher Agent starts** → Reads `../ai_settings.json`
2. **Loads configuration** → API key, base URL, model
3. **Initializes Anthropic provider** → Uses your custom endpoint
4. **Ready to process requests** → Same backend as Claude

### Testing

Verify the configuration is loaded correctly:

```bash
cd zypher-agent
deno run --allow-read test_config.ts
```

Expected output:
```
✅ Successfully loaded ai_settings.json
   API Key: SET (hidden)
   Base URL: https://hone.vvvv.ee
   Model: claude-sonnet-4-5-20250929
```

### Starting Zypher Agent

**No additional setup needed!** Just run:

```bash
cd zypher-agent
deno task start
```

Or use the integrated startup script:

```bash
./start_with_zypher.sh
```

### Updating Configuration

To change API settings for **both** Claude and Zypher:

1. Update `ai_settings.json` in the root directory
2. Restart both services

**OR** use the frontend AI Settings panel - changes apply to both!

### Architecture

```
┌─────────────────────────────────┐
│      ai_settings.json           │
│  (Single Configuration Source)  │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      │             │
┌─────▼─────┐ ┌────▼─────┐
│   Flask   │ │  Zypher  │
│  Backend  │ │  Agent   │
│  (Claude) │ │ (Zypher) │
└───────────┘ └──────────┘
```

### Benefits

1. **Simplified Management** - One configuration file
2. **Consistency** - Same settings everywhere
3. **Custom Endpoints** - Works with your `hone.vvvv.ee` endpoint
4. **Easy Updates** - Change once, applies everywhere

### Optional Override

If you need different settings for Zypher (rare):

```bash
cd zypher-agent
cp .env.example .env
# Edit .env with custom values
```

But for most cases, the shared configuration is perfect!

## Quick Start

```bash
# 1. Verify configuration
cd zypher-agent
deno run --allow-read test_config.ts

# 2. Start Zypher Agent
deno task start

# 3. In another terminal, start Flask
cd ..
source venv/bin/activate
python app_consolidated.py

# 4. In another terminal, start Frontend
cd frontend
npm run dev

# 5. Open http://localhost:5175 and select "Zypher" in AI Chat!
```

## Troubleshooting

**Issue:** Zypher can't find ai_settings.json

**Solution:** Make sure you're running from the `zypher-agent/` directory, or the file exists at `../ai_settings.json`

**Issue:** Different API key needed for Zypher

**Solution:** Create `.env` file in `zypher-agent/` with custom settings

## Next Steps

- [x] Unified configuration ✅
- [ ] Test Zypher responses in WeChat
- [ ] Compare Claude vs Zypher performance
- [ ] Add MCP tools for enhanced capabilities
