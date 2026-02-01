# 🎨 RealChat System Architecture Diagram

## 📱 User Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER EXPERIENCE                             │
└─────────────────────────────────────────────────────────────────────┘

1. User opens mobile WeChat app
2. Scans QR code from RealChat logs
3. Sends message to any contact
4. AI processes and responds automatically
5. Conversation continues naturally


┌─────────────────────────────────────────────────────────────────────┐
│                      SYSTEM ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│                      📱 Mobile WeChat App                        │
│                     (User's Phone)                               │
│                                                                  │
│  • Send/receive messages                                        │
│  • Scan QR code for login                                       │
│  • Normal WeChat usage                                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↕
                    WeChat Protocol (HTTPS)
                              ↕
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│              🌉 WeChat Bridge Service (Wechaty)                  │
│                    Port 8080 (WS) | 8081 (HTTP)                 │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • QR Code Generation                                  │    │
│  │  • Login Management                                    │    │
│  │  • Message Routing                                     │    │
│  │  • Contact/Room Management                             │    │
│  │  • WebSocket Server                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Technology: Node.js + Wechaty + WebSocket                      │
│  Container: realchat-wechat-bridge                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↕
                    WebSocket Connection
                              ↕
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│           🤖 Agent Orchestrator (Multi-Provider)                 │
│                        Port 8082 (HTTP)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Core Functions:                                       │    │
│  │  • Receive messages from WeChat Bridge                 │    │
│  │  • Route to selected AI provider                       │    │
│  │  • Manage conversation history                         │    │
│  │  • Send responses back to WeChat                       │    │
│  │  • Provider switching (runtime)                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Technology: Node.js + Express + WebSocket Client               │
│  Container: realchat-agent-orchestrator                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↕
                    Provider Selection
                              ↕
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │
│  🔵 Option 1 │      │  🟢 Option 2 │      │  🟣 Option 3 │
│              │      │              │      │              │
│  Anthropic   │      │    Zypher    │      │   OpenClaw   │
│     API      │      │    Agents    │      │    Local     │
│   (Direct)   │      │  (Advanced)  │      │  (Connect)   │
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
       ↓                     ↓                     ↓
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ • Simple     │      │ • Tool use   │      │ • Full       │
│ • Reliable   │      │ • Multi-step │      │   control    │
│ • Fast       │      │ • Advanced   │      │ • File       │
│ • $0.003/msg │      │ • $0.003/msg │      │   access     │
│              │      │              │      │ • Free       │
└──────────────┘      └──────────────┘      └──────────────┘
       ↓                     ↓                     ↓
       └─────────────────────┴─────────────────────┘
                              ↓
                    Claude API (Anthropic)
                    https://api.anthropic.com


┌─────────────────────────────────────────────────────────────────────┐
│                      DATA FLOW EXAMPLE                              │
└─────────────────────────────────────────────────────────────────────┘

1. User sends: "What's the weather today?"
   ↓
2. Mobile WeChat → WeChat Bridge
   ↓
3. WeChat Bridge → Agent Orchestrator (via WebSocket)
   {
     type: "message",
     from: { id: "user123", name: "John" },
     text: "What's the weather today?"
   }
   ↓
4. Agent Orchestrator → Selected AI Provider
   - Adds conversation history
   - Builds context
   - Sends to AI
   ↓
5. AI Provider → Response
   "I don't have access to real-time weather data, but I can help you
    find weather information. You can check weather.com or your local
    weather app for today's forecast."
   ↓
6. Agent Orchestrator → WeChat Bridge
   {
     type: "send_message",
     contactId: "user123",
     text: "I don't have access to..."
   }
   ↓
7. WeChat Bridge → Mobile WeChat
   ↓
8. User receives AI response!


┌─────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT OPTIONS                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Option A: Local Development (Your Mac)                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Docker Compose                                          │  │
│  │  ├── wechat-bridge (container)                           │  │
│  │  ├── agent-orchestrator (container)                      │  │
│  │  └── web-app (container)                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Access: localhost:5001                                         │
│  Cost: Free (except API usage)                                  │
│  Best for: Development, testing, personal use                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Option B: VPS Deployment (DigitalOcean, AWS, etc.)            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Ubuntu Server 22.04                                     │  │
│  │  ├── Docker + Docker Compose                             │  │
│  │  ├── Nginx (reverse proxy)                               │  │
│  │  ├── SSL Certificate (Let's Encrypt)                     │  │
│  │  └── RealChat Services                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Access: https://your-domain.com                                │
│  Cost: $12-20/month + API usage                                 │
│  Best for: Production, remote access, multiple users            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Option C: Hybrid (Local OpenClaw + Cloud Services)            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Your Mac:                                               │  │
│  │  └── OpenClaw/Clawdbot (local)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                    ↕                                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  VPS:                                                    │  │
│  │  ├── WeChat Bridge                                       │  │
│  │  └── Agent Orchestrator (connects to local OpenClaw)     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Access: https://your-domain.com                                │
│  Cost: $12-20/month (no API costs)                              │
│  Best for: Power users, full control, custom tools              │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION MATRIX                             │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────┐
│   Feature    │  Anthropic   │    Zypher    │   OpenClaw   │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Setup Time   │  5 minutes   │  1-2 hours   │  2-4 hours   │
│ Complexity   │  ⭐ Easy      │  ⭐⭐ Medium  │  ⭐⭐⭐ Hard   │
│ Cost/Message │  $0.003      │  $0.003      │  Free        │
│ Response     │  ⭐⭐⭐⭐⭐     │  ⭐⭐⭐⭐⭐     │  ⭐⭐⭐⭐⭐     │
│ Quality      │              │              │              │
│ Tool Use     │  ❌ No       │  ✅ Yes      │  ✅ Yes      │
│ File Access  │  ❌ No       │  ⚠️ Limited  │  ✅ Full     │
│ Custom Tools │  ❌ No       │  ⚠️ Limited  │  ✅ Full     │
│ Reliability  │  ⭐⭐⭐⭐⭐     │  ⭐⭐⭐⭐      │  ⭐⭐⭐⭐      │
│ Best For     │  Quick start │  Advanced    │  Power users │
└──────────────┴──────────────┴──────────────┴──────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                                  │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Layer 1: Network Security                                       │
│  • Docker network isolation                                      │
│  • Firewall rules (UFW)                                          │
│  • SSL/TLS encryption (HTTPS)                                    │
│  • Rate limiting                                                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 2: Authentication                                         │
│  • API key validation                                            │
│  • WeChat login (QR code)                                        │
│  • JWT tokens (optional)                                         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 3: Data Protection                                        │
│  • Conversation history encryption                               │
│  • API key encryption in .env                                    │
│  • No message logging (privacy)                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 4: Application Security                                  │
│  • Input validation                                              │
│  • XSS protection                                                │
│  • SQL injection prevention                                      │
│  • CORS configuration                                            │
└──────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                    MONITORING & LOGGING                             │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Real-time Monitoring                                            │
│                                                                  │
│  • docker-compose logs -f                                        │
│  • http://localhost:8081/status (WeChat Bridge)                 │
│  • http://localhost:8082/health (Agent Orchestrator)            │
│  • http://localhost:8082/api/provider (Provider status)         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Metrics to Track                                                │
│                                                                  │
│  • Messages processed per day                                    │
│  • Average response time                                         │
│  • API costs (Anthropic usage)                                   │
│  • Error rate                                                    │
│  • Active conversations                                          │
└──────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                    QUICK REFERENCE                                  │
└─────────────────────────────────────────────────────────────────────┘

Start Services:
  docker-compose up -d

Stop Services:
  docker-compose down

View Logs:
  docker-compose logs -f [service-name]

Restart Service:
  docker-compose restart [service-name]

Check Status:
  curl http://localhost:8081/status
  curl http://localhost:8082/health

Switch Provider:
  curl -X POST http://localhost:8082/api/provider \
    -H "Content-Type: application/json" \
    -d '{"provider": "anthropic"}'

Update Configuration:
  1. Edit .env
  2. docker-compose restart

Backup Data:
  docker-compose exec wechat-bridge tar czf /backup.tar.gz /root/.wechaty

Restore Data:
  docker-compose exec wechat-bridge tar xzf /backup.tar.gz -C /


┌─────────────────────────────────────────────────────────────────────┐
│                    TROUBLESHOOTING FLOWCHART                        │
└─────────────────────────────────────────────────────────────────────┘

Problem: AI not responding
  ↓
Check: Is WeChat logged in?
  ├─ No → Scan QR code again
  └─ Yes ↓
Check: Is Agent Orchestrator running?
  ├─ No → docker-compose up -d agent-orchestrator
  └─ Yes ↓
Check: Is API key valid?
  ├─ No → Update .env and restart
  └─ Yes ↓
Check: Provider status
  └─ curl http://localhost:8082/api/provider

Problem: WeChat won't login
  ↓
Check: Is bridge running?
  ├─ No → docker-compose up -d wechat-bridge
  └─ Yes ↓
Check: QR code visible in logs?
  ├─ No → Restart bridge
  └─ Yes ↓
Try: Scan with mobile WeChat
  └─ Settings → WeChat Web → Scan

Problem: High API costs
  ↓
Solution 1: Reduce max tokens
  └─ ANTHROPIC_MAX_TOKENS=512
Solution 2: Limit conversation history
  └─ Keep only last 10 messages
Solution 3: Switch to OpenClaw
  └─ No API costs!


┌─────────────────────────────────────────────────────────────────────┐
│                    SUCCESS CHECKLIST                                │
└─────────────────────────────────────────────────────────────────────┘

✅ Docker installed and running
✅ .env configured with API key
✅ Services started (docker-compose up -d)
✅ WeChat Bridge shows "logged in" in logs
✅ Agent Orchestrator health check passes
✅ Test message sent and AI responded
✅ Provider switching works
✅ Documentation reviewed

🎉 You're ready to use RealChat!
```

## 📚 Additional Resources

- **Setup Guide**: `SETUP_GUIDE.md`
- **Architecture Details**: `MOBILE_WECHAT_ARCHITECTURE.md`
- **Integration Plan**: `AI_AGENT_INTEGRATION_PLAN.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`

## 🚀 Get Started

```bash
cd /Users/test/Desktop/Hireal/RealChat
./quick-start.sh
```

**Happy chatting with AI on WeChat!** 🎉
