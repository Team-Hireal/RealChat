import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';
import express from 'express';
import WebSocket from 'ws';
import dotenv from 'dotenv';

dotenv.config();

class AgentOrchestrator {
  constructor(config = {}) {
    this.config = {
      port: config.port || 8082,
      wechatBridgeWs: config.wechatBridgeWs || 'ws://localhost:8080',
      ...config
    };

    this.providers = {
      zypher: null,
      openclaw: null,
      anthropic: null
    };

    this.activeProvider = process.env.DEFAULT_AI_PROVIDER || 'anthropic';
    this.conversations = new Map(); // contactId -> conversation history
    this.wechatWs = null;
    this.httpServer = null;
  }

  async initialize() {
    console.log('🤖 Initializing Agent Orchestrator...');

    // Get unified API configuration
    const apiKey = process.env.AI_API_KEY || process.env.ANTHROPIC_API_KEY;
    const baseURL = process.env.AI_BASE_URL || 'https://api.anthropic.com';
    const model = process.env.AI_MODEL || 'claude-3-5-sonnet-20241022';
    const maxTokens = parseInt(process.env.AI_MAX_TOKENS || '1024');

    if (!apiKey) {
      console.error('❌ No API key configured. Set AI_API_KEY in .env');
      throw new Error('API key required');
    }

    // Initialize Anthropic (always available with unified key)
    this.providers.anthropic = new Anthropic({
      apiKey: apiKey,
      baseURL: baseURL
    });
    console.log(`✅ Anthropic provider initialized (baseURL: ${baseURL})`);

    // Store config for later use
    this.config.apiKey = apiKey;
    this.config.baseURL = baseURL;
    this.config.model = model;
    this.config.maxTokens = maxTokens;

    // Initialize Zypher (if configured)
    if (process.env.ZYPHER_ENABLED === 'true') {
      try {
        // Note: Zypher might not be a real package yet, this is conceptual
        const { ZypherAgent, AnthropicModelProvider } = await import('@zypher/agent');
        const provider = new AnthropicModelProvider({
          apiKey: apiKey,
          baseURL: baseURL
        });
        this.providers.zypher = new ZypherAgent(provider);
        await this.providers.zypher.init();
        console.log('✅ Zypher provider initialized');
      } catch (error) {
        console.warn('⚠️  Zypher provider not available:', error.message);
      }
    }

    // Initialize OpenClaw connection (if configured)
    if (process.env.OPENCLAW_ENABLED === 'true' && process.env.OPENCLAW_ENDPOINT) {
      this.providers.openclaw = {
        endpoint: process.env.OPENCLAW_ENDPOINT,
        apiKey: apiKey  // Use unified API key
      };
      console.log(`✅ OpenClaw provider configured: ${this.providers.openclaw.endpoint}`);
    }

    // Connect to WeChat bridge
    await this.connectToWeChatBridge();

    // Start HTTP server
    this.startHttpServer();

    console.log(`✅ Agent Orchestrator initialized with provider: ${this.activeProvider}`);
  }

  async connectToWeChatBridge() {
    return new Promise((resolve, reject) => {
      console.log(`🔌 Connecting to WeChat Bridge at ${this.config.wechatBridgeWs}...`);

      this.wechatWs = new WebSocket(this.config.wechatBridgeWs);

      this.wechatWs.on('open', () => {
        console.log('✅ Connected to WeChat Bridge');
        resolve();
      });

      this.wechatWs.on('message', async (data) => {
        try {
          const message = JSON.parse(data.toString());
          await this.handleWeChatMessage(message);
        } catch (error) {
          console.error('Error handling WeChat message:', error);
        }
      });

      this.wechatWs.on('error', (error) => {
        console.error('WeChat Bridge connection error:', error);
        reject(error);
      });

      this.wechatWs.on('close', () => {
        console.log('❌ Disconnected from WeChat Bridge');
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.connectToWeChatBridge(), 5000);
      });
    });
  }

  async handleWeChatMessage(message) {
    if (message.type === 'message') {
      const { data } = message;
      console.log(`📨 Processing message from ${data.from.name}: ${data.text.substring(0, 50)}...`);

      try {
        // Process with AI
        const response = await this.processMessage(data.text, {
          from: data.from,
          room: data.room,
          conversationHistory: this.getConversationHistory(data.from.id)
        });

        // Update conversation history
        this.addToConversationHistory(data.from.id, 'user', data.text);
        this.addToConversationHistory(data.from.id, 'assistant', response.text);

        // Send response back to WeChat
        this.sendToWeChat({
          type: 'send_message',
          data: {
            contactId: data.from.id,
            roomId: data.room?.id,
            text: response.text
          }
        });

        console.log(`✅ Response sent via ${response.provider}`);
      } catch (error) {
        console.error('Error processing message:', error);

        // Send error message to user
        this.sendToWeChat({
          type: 'send_message',
          data: {
            contactId: data.from.id,
            text: '抱歉，我遇到了一些问题。请稍后再试。(Sorry, I encountered an issue. Please try again later.)'
          }
        });
      }
    }
  }

  async processMessage(message, context = {}) {
    const provider = this.activeProvider;

    console.log(`🤖 Processing with provider: ${provider}`);

    switch (provider) {
      case 'zypher':
        return await this.processWithZypher(message, context);
      case 'openclaw':
        return await this.processWithOpenClaw(message, context);
      case 'anthropic':
        return await this.processWithAnthropic(message, context);
      default:
        throw new Error(`Unknown provider: ${provider}`);
    }
  }

  async processWithZypher(message, context) {
    if (!this.providers.zypher) {
      throw new Error('Zypher provider not initialized');
    }

    const agent = this.providers.zypher;

    // Build task description with context
    const taskDescription = `
You are a helpful WeChat assistant. Respond to this message in a friendly and concise way.

From: ${context.from?.name || 'Unknown'}
${context.room ? `In group: ${context.room.topic}` : ''}

Message: ${message}

${context.conversationHistory && context.conversationHistory.length > 0 ? `
Previous conversation:
${context.conversationHistory.slice(-5).map(m =>
  `${m.role === 'user' ? context.from.name : 'You'}: ${m.content}`
).join('\n')}
` : ''}

Provide a helpful, friendly response in the same language as the user's message.
Keep your response concise (1-3 sentences).
    `.trim();

    const result = await agent.runTask(taskDescription);

    return {
      text: result.output || result.text || result,
      provider: 'zypher',
      metadata: result.metadata || {}
    };
  }

  async processWithOpenClaw(message, context) {
    if (!this.providers.openclaw) {
      throw new Error('OpenClaw provider not configured');
    }

    const config = this.providers.openclaw;

    // Send to local OpenClaw instance
    const response = await axios.post(`${config.endpoint}/api/chat`, {
      message: message,
      context: {
        from: context.from,
        room: context.room,
        history: context.conversationHistory?.slice(-10) || []
      }
    }, {
      headers: {
        'Authorization': config.apiKey ? `Bearer ${config.apiKey}` : undefined,
        'Content-Type': 'application/json'
      },
      timeout: 30000 // 30 second timeout
    });

    return {
      text: response.data.response || response.data.text || response.data.message,
      provider: 'openclaw',
      metadata: response.data.metadata || {}
    };
  }

  async processWithAnthropic(message, context) {
    if (!this.providers.anthropic) {
      throw new Error('Anthropic provider not initialized');
    }

    const client = this.providers.anthropic;

    // Build messages array
    const messages = [];

    // Add conversation history (last 10 messages)
    if (context.conversationHistory && context.conversationHistory.length > 0) {
      messages.push(...context.conversationHistory.slice(-10));
    }

    // Add current message
    messages.push({
      role: 'user',
      content: message
    });

    // Build system prompt
    const systemPrompt = `You are a helpful WeChat assistant chatting with ${context.from?.name || 'a user'}${context.room ? ` in the group "${context.room.topic}"` : ''}.

Guidelines:
- Be friendly, warm, and conversational
- Keep responses concise (1-3 sentences typically)
- Match the language of the user's message (Chinese or English)
- Be helpful and provide value
- Use emojis sparingly and naturally
- If you don't know something, admit it honestly

Remember: You're having a casual WeChat conversation, not writing an essay.`;

    const response = await client.messages.create({
      model: this.config.model || 'claude-3-5-sonnet-20241022',
      max_tokens: this.config.maxTokens || 1024,
      system: systemPrompt,
      messages: messages
    });

    return {
      text: response.content[0].text,
      provider: 'anthropic',
      metadata: {
        model: response.model,
        usage: response.usage,
        stopReason: response.stop_reason
      }
    };
  }

  getConversationHistory(contactId) {
    return this.conversations.get(contactId) || [];
  }

  addToConversationHistory(contactId, role, content) {
    if (!this.conversations.has(contactId)) {
      this.conversations.set(contactId, []);
    }

    const history = this.conversations.get(contactId);
    history.push({ role, content });

    // Keep only last 20 messages
    if (history.length > 20) {
      this.conversations.set(contactId, history.slice(-20));
    }
  }

  clearConversationHistory(contactId) {
    this.conversations.delete(contactId);
  }

  sendToWeChat(message) {
    if (this.wechatWs && this.wechatWs.readyState === WebSocket.OPEN) {
      this.wechatWs.send(JSON.stringify(message));
    } else {
      console.error('Cannot send to WeChat: connection not open');
    }
  }

  setActiveProvider(provider) {
    if (!['zypher', 'openclaw', 'anthropic'].includes(provider)) {
      throw new Error(`Invalid provider: ${provider}`);
    }

    if (!this.providers[provider]) {
      throw new Error(`Provider ${provider} not initialized`);
    }

    this.activeProvider = provider;
    console.log(`✅ Active provider changed to: ${provider}`);
  }

  getProviderStatus() {
    return {
      active: this.activeProvider,
      config: {
        apiKey: this.config.apiKey ? '***' + this.config.apiKey.slice(-4) : 'not set',
        baseURL: this.config.baseURL,
        model: this.config.model,
        maxTokens: this.config.maxTokens
      },
      providers: {
        zypher: {
          enabled: !!this.providers.zypher,
          active: this.activeProvider === 'zypher'
        },
        openclaw: {
          enabled: !!this.providers.openclaw,
          active: this.activeProvider === 'openclaw',
          endpoint: this.providers.openclaw?.endpoint
        },
        anthropic: {
          enabled: !!this.providers.anthropic,
          active: this.activeProvider === 'anthropic'
        }
      }
    };
  }

  async updateConfig(newConfig) {
    // Update configuration
    if (newConfig.apiKey) {
      this.config.apiKey = newConfig.apiKey;
    }
    if (newConfig.baseURL) {
      this.config.baseURL = newConfig.baseURL;
    }
    if (newConfig.model) {
      this.config.model = newConfig.model;
    }
    if (newConfig.maxTokens) {
      this.config.maxTokens = parseInt(newConfig.maxTokens);
    }

    // Reinitialize Anthropic provider with new config
    if (newConfig.apiKey || newConfig.baseURL) {
      this.providers.anthropic = new Anthropic({
        apiKey: this.config.apiKey,
        baseURL: this.config.baseURL
      });
      console.log('✅ Anthropic provider reinitialized with new config');
    }

    // Update OpenClaw endpoint if provided
    if (newConfig.openclawEndpoint && this.providers.openclaw) {
      this.providers.openclaw.endpoint = newConfig.openclawEndpoint;
      console.log(`✅ OpenClaw endpoint updated: ${newConfig.openclawEndpoint}`);
    }

    return this.getProviderStatus();
  }

  startHttpServer() {
    const app = express();
    app.use(express.json());

    // Health check
    app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        provider: this.activeProvider,
        conversations: this.conversations.size
      });
    });

    // Get provider status
    app.get('/api/provider', (req, res) => {
      res.json(this.getProviderStatus());
    });

    // Set active provider
    app.post('/api/provider', (req, res) => {
      try {
        const { provider } = req.body;
        this.setActiveProvider(provider);
        res.json({ success: true, provider: this.activeProvider });
      } catch (error) {
        res.status(400).json({ success: false, error: error.message });
      }
    });

    // Update configuration
    app.post('/api/config', async (req, res) => {
      try {
        const newConfig = req.body;
        const status = await this.updateConfig(newConfig);
        res.json({ success: true, config: status });
      } catch (error) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // Get current configuration
    app.get('/api/config', (req, res) => {
      res.json({
        success: true,
        config: {
          apiKey: this.config.apiKey ? '***' + this.config.apiKey.slice(-4) : 'not set',
          baseURL: this.config.baseURL,
          model: this.config.model,
          maxTokens: this.config.maxTokens,
          activeProvider: this.activeProvider,
          openclawEndpoint: this.providers.openclaw?.endpoint
        }
      });
    });

    // Manual message processing (for testing)
    app.post('/api/process', async (req, res) => {
      try {
        const { message, context } = req.body;
        const response = await this.processMessage(message, context || {});
        res.json({ success: true, response });
      } catch (error) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // Clear conversation history
    app.delete('/api/conversation/:contactId', (req, res) => {
      const { contactId } = req.params;
      this.clearConversationHistory(contactId);
      res.json({ success: true });
    });

    // Get conversation history
    app.get('/api/conversation/:contactId', (req, res) => {
      const { contactId } = req.params;
      const history = this.getConversationHistory(contactId);
      res.json({ success: true, history });
    });

    this.httpServer = app.listen(this.config.port, () => {
      console.log(`🌐 HTTP server listening on port ${this.config.port}`);
    });
  }

  async stop() {
    console.log('🛑 Stopping Agent Orchestrator...');

    if (this.wechatWs) {
      this.wechatWs.close();
    }

    if (this.httpServer) {
      this.httpServer.close();
    }

    console.log('✅ Agent Orchestrator stopped');
  }
}

// Start the orchestrator if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const orchestrator = new AgentOrchestrator({
    port: parseInt(process.env.PORT || '8082'),
    wechatBridgeWs: process.env.WECHAT_BRIDGE_WS || 'ws://localhost:8080'
  });

  orchestrator.initialize().catch(error => {
    console.error('Failed to initialize orchestrator:', error);
    process.exit(1);
  });

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    await orchestrator.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
    await orchestrator.stop();
    process.exit(0);
  });
}

export default AgentOrchestrator;
