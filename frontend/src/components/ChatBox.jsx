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
  const processingRef = useRef(false); // Flag to prevent duplicate processing
  const selectedModelRef = useRef('claude'); // Store current model in ref for socket listeners

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Sync selectedModel to ref so socket listeners always have the latest value
  useEffect(() => {
    selectedModelRef.current = selectedModel;
    console.log(`[ChatBox] Model selection changed to: ${selectedModel}`);
  }, [selectedModel]);

  // Set up Socket.IO connection for WeChat messages
  useEffect(() => {
    // Prevent multiple socket connections - reuse existing socket if available
    if (!socketRef.current || !socketRef.current.connected) {
      console.log('[ChatBox] Creating NEW socket connection');
      socketRef.current = io('http://localhost:5001', {
        reconnection: false,  // Disable auto-reconnection to prevent duplicates
        forceNew: true  // Force new connection (close old ones)
      });

      socketRef.current.on('connect', () => {
        console.log('[ChatBox] Socket connected - ID:', socketRef.current.id);
      });

      // Listen for context load event (from Test OCR button)
      socketRef.current.on('load_context', (data) => {
        console.log('[ChatBox] Loading context:', data);

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
        console.log('[ChatBox] Received WeChat message:', data);

        // Prevent duplicate processing
        if (processingRef.current) {
          console.warn('[ChatBox] Already processing, SKIPPING duplicate');
          return;
        }

        processingRef.current = true;

        // Add WeChat message as user message
        const wechatMessage = {
          role: 'user',
          content: data.text,
          timestamp: data.timestamp,
          source: 'wechat'
        };

        setMessages(prev => [...prev, wechatMessage]);

        // Process message after a small delay to ensure state is updated
        setTimeout(() => {
          setMessages(currentMessages => {
            processWeChatMessage(data.text, [...currentMessages]);
            return currentMessages;
          });
        }, 100);
      });
    } else {
      console.log('[ChatBox] Reusing existing socket connection - ID:', socketRef.current.id);
    }

    return () => {
      console.log('[ChatBox] Cleanup - removing listeners');
      socketRef.current?.off('wechat_message');
      socketRef.current?.off('load_context');
      // Don't disconnect - keep connection alive for reuse
    };
  }, []); // Empty dependency array - only set up listener once

  const processWeChatMessage = async (messageText, currentMessages) => {
    // Use ref to get the current model selection (fixes closure issue in socket listeners)
    const currentModel = selectedModelRef.current;
    console.log(`[processWeChatMessage] Starting processing for: ${messageText} with model: ${currentModel}`);
    setIsLoading(true);

    try {
      console.log(`[processWeChatMessage] Sending to /api/chat with model: ${currentModel}`);
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText,
          model: currentModel,  // Use ref value instead of state
          history: currentMessages,
          send_to_wechat: false  // Don't send from backend, we'll send from frontend
        })
      });

      const data = await response.json();
      console.log('[processWeChatMessage] Received AI response:', data.response);

      if (data.success) {
        const aiMessage = {
          role: 'assistant',
          content: data.response,
          model: data.model || selectedModel,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, aiMessage]);

        // Send AI response to WeChat - simplified for testing
        try {
          // Get current chat from backend
          const chatResponse = await fetch('http://localhost:5001/api/wechat/current-chat');
          const chatData = await chatResponse.json();

          if (chatData.success && chatData.chat) {
            const currentChat = chatData.chat;
            console.log(`[processWeChatMessage] Sending AI response to WeChat chat: ${currentChat}`);
            console.log(`[processWeChatMessage] Message to send: "${data.response}"`);

            // Send message directly to WeChat without any filtering
            const sendResponse = await fetch('http://localhost:5001/api/wechat/send', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                chat_name: currentChat,
                message: data.response
              })
            });

            const sendData = await sendResponse.json();

            if (sendData.success) {
              console.log('[processWeChatMessage] ✅ AI response sent to WeChat successfully');
            } else {
              console.warn('[processWeChatMessage] ⚠️ Failed to send AI response to WeChat:', sendData.error);
            }
          }
        } catch (sendError) {
          console.error('[processWeChatMessage] Error sending AI response to WeChat:', sendError);
        }
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
      processingRef.current = false; // Reset processing flag
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