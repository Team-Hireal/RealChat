import { useState, useRef, useEffect } from 'react';
import io from 'socket.io-client';
import './ChatBox.css';

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('claude');
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Set up Socket.IO connection for WeChat messages
  useEffect(() => {
    socketRef.current = io('http://localhost:5001');

    socketRef.current.on('connect', () => {
      console.log('ChatBox connected to Socket.IO');
    });

    // Listen for context load event (from Test OCR button)
    socketRef.current.on('load_context', (data) => {
      console.log('Loading context:', data);

      // Add context as ONE user message
      const contextMessage = {
        role: 'user',
        content: data.context,
        timestamp: new Date().toLocaleTimeString(),
        source: 'wechat_context'
      };

      setMessages([contextMessage]);

      // Add system message
      const systemMessage = {
        role: 'assistant',
        content: `Loaded ${data.message_count} messages from WeChat as context. I'm ready to respond to new messages.`,
        model: 'system',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, systemMessage]);
    });

    // Listen for WeChat messages
    socketRef.current.on('wechat_message', (data) => {
      console.log('Received WeChat message:', data);

      // Add WeChat message as user message
      const wechatMessage = {
        role: 'user',
        content: data.text,
        timestamp: data.timestamp,
        source: 'wechat'
      };

      setMessages(prev => [...prev, wechatMessage]);

      // Automatically send to AI for processing
      processWeChatMessage(data.text, [...messages, wechatMessage]);
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, [messages]);

  const processWeChatMessage = async (messageText, currentMessages) => {
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText,
          model: selectedModel,
          history: currentMessages
        })
      });

      const data = await response.json();

      if (data.success) {
        const aiMessage = {
          role: 'assistant',
          content: data.response,
          model: data.model || selectedModel,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, aiMessage]);

        // Send AI response back to WeChat with [Agent] prefix
        await sendToWeChat(data.response);
      } else {
        const errorMessage = {
          role: 'error',
          content: `Error: ${data.error || 'Failed to get AI response'}`,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error processing WeChat message:', error);
      const errorMessage = {
        role: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendToWeChat = async (message) => {
    try {
      // Claude now adds [Agent] prefix automatically via system prompt
      const response = await fetch('http://localhost:5001/api/wechat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,  // Send as-is, Claude already added [Agent]
          mark_as_agent: true  // Mark this as agent message for OCR filtering
        })
      });

      const data = await response.json();

      if (data.success) {
        console.log('✅ Message sent to WeChat:', message.substring(0, 50));
      } else {
        console.error('❌ Failed to send to WeChat:', data.error);
      }
    } catch (error) {
      console.error('Error sending to WeChat:', error);
    }
  };

  const loadInitialContext = async () => {
    try {
      // Fetch current messages from WeChat via OCR
      const response = await fetch('http://localhost:5001/api/wechat/read?ocr=true');
      const data = await response.json();

      if (data.success && data.messages && data.messages.length > 0) {
        // Combine all messages into one text block
        const contextText = data.messages
          .filter(msg => msg.text && msg.text.trim())  // Only non-empty messages
          .map(msg => `[${msg.timestamp}] ${msg.text}`)
          .join('\n');

        if (contextText) {
          // Add as ONE user message with all context
          const contextMessage = {
            role: 'user',
            content: `Here are the current messages from WeChat:\n\n${contextText}`,
            timestamp: new Date().toLocaleTimeString(),
            source: 'wechat_context'
          };

          setMessages([contextMessage]);

          // Add a system message indicating context was loaded
          const systemMessage = {
            role: 'assistant',
            content: `Loaded ${data.messages.filter(msg => msg.text && msg.text.trim()).length} messages from WeChat as context. I'm ready to respond to new messages.`,
            model: 'system',
            timestamp: new Date().toLocaleTimeString()
          };
          setMessages(prev => [...prev, systemMessage]);
        }
      }
    } catch (error) {
      console.error('Error loading initial context:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          model: selectedModel,
          history: messages
        })
      });

      const data = await response.json();

      if (data.success) {
        const aiMessage = {
          role: 'assistant',
          content: data.response,
          model: selectedModel,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          role: 'error',
          content: `Error: ${data.error}`,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: `Failed to connect: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-header">
        <h3 className="chatbox-title">AI Chat</h3>
        <div className="chatbox-controls">
          <select
            className="model-selector"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="claude">Claude</option>
            <option value="zypher">Zypher</option>
          </select>
          <button className="clear-chat-btn" onClick={loadInitialContext}>
            📥 Load Context
          </button>
          <button className="clear-chat-btn" onClick={clearChat}>
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="chatbox-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>👋 Start a conversation with {selectedModel === 'claude' ? 'Claude' : 'Zypher'}</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message message-${msg.role}`}>
              <div className="message-header">
                <span className="message-role">
                  {msg.role === 'user' ? '👤 You' : msg.role === 'assistant' ? `🤖 ${msg.model || 'AI'}` : '⚠️ Error'}
                </span>
                <span className="message-time">{msg.timestamp}</span>
              </div>
              <div className="message-content">{msg.content}</div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message message-assistant">
            <div className="message-header">
              <span className="message-role">🤖 {selectedModel}</span>
            </div>
            <div className="message-content typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chatbox-input-container">
        <textarea
          className="chatbox-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={`Ask ${selectedModel === 'claude' ? 'Claude' : 'Zypher'} anything...`}
          rows="3"
          disabled={isLoading}
        />
        <button
          className="chatbox-send-btn"
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? '⏳' : '📤'} Send
        </button>
      </div>
    </div>
  );
};

export default ChatBox;