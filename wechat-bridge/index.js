import { WechatyBuilder, ScanStatus, log } from 'wechaty';
import { FileBox } from 'file-box';
import { WebSocketServer, WebSocket } from 'ws';
import express from 'express';
import dotenv from 'dotenv';

dotenv.config();

class WeChatBridge {
  constructor(config = {}) {
    this.config = {
      port: config.port || 8080,
      httpPort: config.httpPort || 8081,
      puppetType: config.puppetType || 'wechat',
      flaskUrl: config.flaskUrl || 'http://localhost:5001',
      ...config
    };

    this.bot = null;
    this.wsServer = null;
    this.httpServer = null;
    this.clients = new Set();
    this.isLoggedIn = false;
    this.currentUser = null;
    this.messageCache = new Map(); // Cache messages for response routing
  }

  async start() {
    console.log('🚀 Starting WeChat Bridge...');

    // Initialize Wechaty bot
    this.bot = WechatyBuilder.build({
      name: 'realchat-bot',
      puppetOptions: {
        uos: true  // Enable UOS (iPad) protocol for better stability
      }
    });

    // Set up event handlers
    this.bot
      .on('scan', this.onScan.bind(this))
      .on('login', this.onLogin.bind(this))
      .on('message', this.onMessage.bind(this))
      .on('logout', this.onLogout.bind(this))
      .on('error', this.onError.bind(this));

    // Start WebSocket server
    this.startWebSocketServer();

    // Start HTTP server for health checks
    this.startHttpServer();

    // Start the bot
    try {
      await this.bot.start();
      console.log('✅ WeChat Bridge started successfully');
    } catch (error) {
      console.error('❌ Failed to start WeChat Bridge:', error);
      throw error;
    }
  }

  startWebSocketServer() {
    this.wsServer = new WebSocketServer({ port: this.config.port });

    this.wsServer.on('connection', (ws) => {
      console.log('📱 Web client connected');
      this.clients.add(ws);

      // Send current status
      ws.send(JSON.stringify({
        type: 'status',
        data: {
          isLoggedIn: this.isLoggedIn,
          user: this.currentUser
        }
      }));

      ws.on('message', async (data) => {
        try {
          const message = JSON.parse(data.toString());
          await this.handleWebAppMessage(ws, message);
        } catch (error) {
          console.error('Error handling web app message:', error);
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
      });

      ws.on('close', () => {
        this.clients.delete(ws);
        console.log('📱 Web client disconnected');
      });

      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        this.clients.delete(ws);
      });
    });

    console.log(`🔌 WebSocket server listening on port ${this.config.port}`);
  }

  startHttpServer() {
    const app = express();
    app.use(express.json());

    app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        isLoggedIn: this.isLoggedIn,
        user: this.currentUser
      });
    });

    app.get('/status', (req, res) => {
      res.json({
        isLoggedIn: this.isLoggedIn,
        user: this.currentUser,
        clients: this.clients.size
      });
    });

    // Endpoint for Flask to send messages via bridge
    app.post('/send', async (req, res) => {
      try {
        const { contactId, roomId, contactName, roomName, text } = req.body;

        if (!this.isLoggedIn) {
          return res.status(400).json({ success: false, error: 'Not logged in to WeChat' });
        }

        // Send message
        if (roomName) {
          const room = await this.bot.Room.find({ topic: roomName });
          if (room) {
            await room.say(text);
            console.log(`✅ Message sent to room: ${roomName}`);
            res.json({ success: true, room: roomName });
          } else {
            res.status(404).json({ success: false, error: `Room not found: ${roomName}` });
          }
        } else if (contactName) {
          const contact = await this.bot.Contact.find({ name: contactName });
          if (contact) {
            await contact.say(text);
            console.log(`✅ Message sent to contact: ${contactName}`);
            res.json({ success: true, contact: contactName });
          } else {
            res.status(404).json({ success: false, error: `Contact not found: ${contactName}` });
          }
        } else if (roomId) {
          const room = await this.bot.Room.find({ id: roomId });
          if (room) {
            await room.say(text);
            res.json({ success: true, roomId });
          } else {
            res.status(404).json({ success: false, error: `Room not found: ${roomId}` });
          }
        } else if (contactId) {
          const contact = await this.bot.Contact.find({ id: contactId });
          if (contact) {
            await contact.say(text);
            res.json({ success: true, contactId });
          } else {
            res.status(404).json({ success: false, error: `Contact not found: ${contactId}` });
          }
        } else {
          res.status(400).json({ success: false, error: 'Either contactId, roomId, contactName, or roomName must be provided' });
        }
      } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({ success: false, error: error.message });
      }
    });

    this.httpServer = app.listen(this.config.httpPort, () => {
      console.log(`🌐 HTTP server listening on port ${this.config.httpPort}`);
    });
  }

  onScan(qrcode, status) {
    if (status === ScanStatus.Waiting || status === ScanStatus.Timeout) {
      const qrcodeImageUrl = `https://wechaty.js.org/qrcode/${encodeURIComponent(qrcode)}`;

      console.log('📱 Scan QR Code to login:');
      console.log(qrcodeImageUrl);

      this.broadcast({
        type: 'qrcode',
        data: {
          qrcode: qrcode,
          url: qrcodeImageUrl,
          status: status
        }
      });
    } else {
      console.log(`Scan status: ${status}`);
    }
  }

  async onLogin(user) {
    this.isLoggedIn = true;
    this.currentUser = {
      id: user.id,
      name: user.name()
    };

    console.log(`✅ User ${user.name()} logged in`);

    this.broadcast({
      type: 'login',
      data: {
        user: this.currentUser
      }
    });
  }

  async onMessage(message) {
    try {
      // Ignore messages from self
      if (message.self()) return;

      const contact = message.talker();
      const text = message.text();
      const room = message.room();
      const messageType = message.type();

      // Only process text messages for now
      if (messageType !== this.bot.Message.Type.Text) {
        console.log(`Ignoring non-text message type: ${messageType}`);
        return;
      }

      // Prepare message data
      const messageData = {
        id: message.id,
        text: text,
        from: {
          id: contact.id,
          name: contact.name(),
          alias: await contact.alias() || contact.name()
        },
        room: room ? {
          id: room.id,
          topic: await room.topic()
        } : null,
        timestamp: message.date().getTime(),
        messageType: messageType
      };

      console.log(`📨 Message from ${contact.name()}: ${text.substring(0, 50)}...`);

      // Cache message for response routing
      this.messageCache.set(message.id, message);

      // Forward to Flask backend for AI processing
      try {
        const response = await fetch(`${this.config.flaskUrl}/api/bridge/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(messageData)
        });

        if (response.ok) {
          const result = await response.json();
          console.log(`✅ Message forwarded to Flask: ${result.success ? 'success' : 'failed'}`);

          // If Flask returns a response, send it back
          if (result.response) {
            await message.say(result.response);
            console.log(`🤖 AI response sent: ${result.response.substring(0, 50)}...`);
          }
        } else {
          console.error(`❌ Flask returned error: ${response.status}`);
        }
      } catch (error) {
        console.error('❌ Error forwarding to Flask:', error.message);
      }

      // Also broadcast to WebSocket clients
      this.broadcast({
        type: 'message',
        data: messageData
      });
    } catch (error) {
      console.error('Error processing message:', error);
    }
  }

  onLogout(user) {
    this.isLoggedIn = false;
    this.currentUser = null;

    console.log(`👋 User ${user.name()} logged out`);

    this.broadcast({
      type: 'logout',
      data: {}
    });
  }

  onError(error) {
    console.error('❌ Bot error:', error);

    this.broadcast({
      type: 'error',
      data: {
        message: error.message
      }
    });
  }

  async handleWebAppMessage(ws, message) {
    console.log(`📥 Received from web app: ${message.type}`);

    switch (message.type) {
      case 'send_message':
        await this.sendMessage(message.data);
        break;

      case 'get_contacts':
        await this.getContacts(ws);
        break;

      case 'get_rooms':
        await this.getRooms(ws);
        break;

      case 'get_contact':
        await this.getContact(ws, message.data.contactId);
        break;

      default:
        console.log(`Unknown message type: ${message.type}`);
    }
  }

  async sendMessage(data) {
    const { contactId, roomId, text } = data;

    if (!this.isLoggedIn) {
      throw new Error('Not logged in to WeChat');
    }

    try {
      if (roomId) {
        // Send to room
        const room = await this.bot.Room.find({ id: roomId });
        if (room) {
          await room.say(text);
          console.log(`✅ Message sent to room: ${await room.topic()}`);

          this.broadcast({
            type: 'message_sent',
            data: {
              success: true,
              roomId,
              text
            }
          });
        } else {
          throw new Error(`Room not found: ${roomId}`);
        }
      } else if (contactId) {
        // Send to contact
        const contact = await this.bot.Contact.find({ id: contactId });
        if (contact) {
          await contact.say(text);
          console.log(`✅ Message sent to contact: ${contact.name()}`);

          this.broadcast({
            type: 'message_sent',
            data: {
              success: true,
              contactId,
              text
            }
          });
        } else {
          throw new Error(`Contact not found: ${contactId}`);
        }
      } else {
        throw new Error('Either contactId or roomId must be provided');
      }
    } catch (error) {
      console.error('Error sending message:', error);

      this.broadcast({
        type: 'message_sent',
        data: {
          success: false,
          error: error.message
        }
      });

      throw error;
    }
  }

  async getContacts(ws) {
    if (!this.isLoggedIn) {
      ws.send(JSON.stringify({
        type: 'contacts',
        data: { contacts: [], error: 'Not logged in' }
      }));
      return;
    }

    try {
      const contacts = await this.bot.Contact.findAll();
      const contactList = await Promise.all(
        contacts
          .filter(c => !c.self())
          .slice(0, 100)  // Limit to first 100 contacts
          .map(async (c) => ({
            id: c.id,
            name: c.name(),
            alias: await c.alias() || c.name()
          }))
      );

      ws.send(JSON.stringify({
        type: 'contacts',
        data: { contacts: contactList }
      }));

      console.log(`📋 Sent ${contactList.length} contacts`);
    } catch (error) {
      console.error('Error getting contacts:', error);
      ws.send(JSON.stringify({
        type: 'contacts',
        data: { contacts: [], error: error.message }
      }));
    }
  }

  async getRooms(ws) {
    if (!this.isLoggedIn) {
      ws.send(JSON.stringify({
        type: 'rooms',
        data: { rooms: [], error: 'Not logged in' }
      }));
      return;
    }

    try {
      const rooms = await this.bot.Room.findAll();
      const roomList = await Promise.all(
        rooms.slice(0, 50).map(async (r) => ({
          id: r.id,
          topic: await r.topic()
        }))
      );

      ws.send(JSON.stringify({
        type: 'rooms',
        data: { rooms: roomList }
      }));

      console.log(`📋 Sent ${roomList.length} rooms`);
    } catch (error) {
      console.error('Error getting rooms:', error);
      ws.send(JSON.stringify({
        type: 'rooms',
        data: { rooms: [], error: error.message }
      }));
    }
  }

  async getContact(ws, contactId) {
    if (!this.isLoggedIn) {
      ws.send(JSON.stringify({
        type: 'contact',
        data: { contact: null, error: 'Not logged in' }
      }));
      return;
    }

    try {
      const contact = await this.bot.Contact.find({ id: contactId });
      if (contact) {
        const contactData = {
          id: contact.id,
          name: contact.name(),
          alias: await contact.alias() || contact.name()
        };

        ws.send(JSON.stringify({
          type: 'contact',
          data: { contact: contactData }
        }));
      } else {
        ws.send(JSON.stringify({
          type: 'contact',
          data: { contact: null, error: 'Contact not found' }
        }));
      }
    } catch (error) {
      console.error('Error getting contact:', error);
      ws.send(JSON.stringify({
        type: 'contact',
        data: { contact: null, error: error.message }
      }));
    }
  }

  broadcast(message) {
    const data = JSON.stringify(message);
    let sentCount = 0;

    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data);
        sentCount++;
      }
    });

    if (sentCount > 0) {
      console.log(`📤 Broadcast to ${sentCount} client(s): ${message.type}`);
    }
  }

  async stop() {
    console.log('🛑 Stopping WeChat Bridge...');

    if (this.bot) {
      await this.bot.stop();
    }

    if (this.wsServer) {
      this.wsServer.close();
    }

    if (this.httpServer) {
      this.httpServer.close();
    }

    console.log('✅ WeChat Bridge stopped');
  }
}

// Start the bridge if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const bridge = new WeChatBridge({
    port: parseInt(process.env.WS_PORT || '8080'),
    httpPort: parseInt(process.env.HTTP_PORT || '8081')
  });

  bridge.start().catch(error => {
    console.error('Failed to start bridge:', error);
    process.exit(1);
  });

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    await bridge.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
    await bridge.stop();
    process.exit(0);
  });
}

export default WeChatBridge;
