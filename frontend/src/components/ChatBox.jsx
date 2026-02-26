import { useState, useRef, useEffect, useCallback } from 'react';
import { useAppContext } from '../context/AppContext';
import { ACTIONS } from '../context/AppReducer';
import io from 'socket.io-client';
import './ChatBox.css';

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5050';
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5050';

const ChatBox = () => {
  const { state, dispatch } = useAppContext();
  const { chatSessions, activeChat, mode } = state;
  const isDev = mode === 'developer';
  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
  };
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('zypher');
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);
  const processingRef = useRef(false);
  const selectedModelRef = useRef('zypher');
  const activeChatRef = useRef(null);

  const messages = activeChat ? (chatSessions[activeChat] || []) : [];

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);
  useEffect(() => { selectedModelRef.current = selectedModel; }, [selectedModel]);
  useEffect(() => { activeChatRef.current = activeChat; }, [activeChat]);

  const processWeChatMessage = useCallback(async (messageText, chatName) => {
    const currentModel = selectedModelRef.current;
    setIsLoading(true);
    try {
      // Read current session messages at call time via a ref-based approach
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          message: messageText,
          model: currentModel,
          history: [], // Backend has context from OCR; history sent separately if needed
          send_to_wechat: true
        })
      });
      const data = await response.json();
      const msg = data.success
        ? { role: 'assistant', content: data.response, model: data.model || currentModel, timestamp: new Date().toLocaleTimeString() }
        : { role: 'error', content: `Error: ${data.error || 'Failed to get AI response'}`, timestamp: new Date().toLocaleTimeString() };
      dispatch({ type: ACTIONS.ADD_MESSAGE_TO_SESSION, payload: { chatName, message: msg } });
    } catch (error) {
      dispatch({ type: ACTIONS.ADD_MESSAGE_TO_SESSION, payload: { chatName, message: { role: 'error', content: `Error: ${error.message}`, timestamp: new Date().toLocaleTimeString() } } });
    } finally {
      setIsLoading(false);
      processingRef.current = false;
    }
  }, [dispatch]);

  useEffect(() => {
    if (socketRef.current?.connected) return;

    socketRef.current = io(SOCKET_URL, { reconnection: false, forceNew: true });

    socketRef.current.on('connect', () => console.log('[ChatBox] Socket connected'));

    socketRef.current.on('current_chat_update', (data) => {
      if (data.detected && data.chat) {
        dispatch({ type: ACTIONS.ENSURE_CHAT_SESSION, payload: data.chat });
        dispatch({ type: ACTIONS.SET_ACTIVE_CHAT, payload: data.chat });
      }
    });

    socketRef.current.on('load_context', (data) => {
      const chatName = data.chat_name || activeChatRef.current || 'Unknown';
      dispatch({ type: ACTIONS.SET_ACTIVE_CHAT, payload: chatName });
      dispatch({
        type: ACTIONS.REPLACE_SESSION_MESSAGES,
        payload: {
          chatName,
          messages: [
            { role: 'user', content: data.context, timestamp: new Date().toLocaleTimeString(), source: 'wechat_context' },
            { role: 'assistant', content: `Loaded ${data.message_count} messages from WeChat as context.`, model: 'system', timestamp: new Date().toLocaleTimeString() }
          ]
        }
      });
    });

    socketRef.current.on('wechat_message', (data) => {
      if (processingRef.current) return;
      processingRef.current = true;

      const chatName = data.chat_name || activeChatRef.current || 'Unknown';
      dispatch({ type: ACTIONS.ENSURE_CHAT_SESSION, payload: chatName });
      dispatch({ type: ACTIONS.SET_ACTIVE_CHAT, payload: chatName });
      dispatch({
        type: ACTIONS.ADD_MESSAGE_TO_SESSION,
        payload: { chatName, message: { role: 'user', content: data.text, timestamp: data.timestamp, source: 'wechat' } }
      });

      setTimeout(() => processWeChatMessage(data.text, chatName), 100);
    });

    return () => {
      socketRef.current?.off('wechat_message');
      socketRef.current?.off('load_context');
      socketRef.current?.off('current_chat_update');
    };
  }, [dispatch, processWeChatMessage]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading || !activeChat) return;
    const userMessage = { role: 'user', content: input, timestamp: new Date().toLocaleTimeString() };
    dispatch({ type: ACTIONS.ADD_MESSAGE_TO_SESSION, payload: { chatName: activeChat, message: userMessage } });
    const msgText = input;
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ message: msgText, model: selectedModel, history: [...messages, userMessage] })
      });
      const data = await response.json();
      const msg = data.success
        ? { role: 'assistant', content: data.response, model: selectedModel, timestamp: new Date().toLocaleTimeString() }
        : { role: 'error', content: `Error: ${data.error}`, timestamp: new Date().toLocaleTimeString() };
      dispatch({ type: ACTIONS.ADD_MESSAGE_TO_SESSION, payload: { chatName: activeChat, message: msg } });
    } catch (error) {
      dispatch({ type: ACTIONS.ADD_MESSAGE_TO_SESSION, payload: { chatName: activeChat, message: { role: 'error', content: `Failed to connect: ${error.message}`, timestamp: new Date().toLocaleTimeString() } } });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const clearChat = () => {
    if (!activeChat) return;
    dispatch({ type: ACTIONS.REPLACE_SESSION_MESSAGES, payload: { chatName: activeChat, messages: [] } });
  };

  const chatNames = Object.keys(chatSessions);

  return (
    <div className="chatbox-container">
      <div className="chatbox-header">
        <h3 className="chatbox-title">AI Chat</h3>
        <div className="chatbox-controls">
          {isDev && (
            <select className="model-selector" value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
              <option value="zypher">Zypher</option>
              <option value="openclaw">OpenClaw</option>
            </select>
          )}
          <button className="clear-chat-btn" onClick={clearChat}>🗑️ Clear</button>
        </div>
      </div>

      {chatNames.length > 0 && (
        <div className="chat-tabs">
          {chatNames.map(name => (
            <button key={name} className={`chat-tab ${name === activeChat ? 'chat-tab-active' : ''}`}
              onClick={() => dispatch({ type: ACTIONS.SET_ACTIVE_CHAT, payload: name })}>
              {name}
            </button>
          ))}
        </div>
      )}

      <div className="chatbox-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>{activeChat ? `No messages in ${activeChat}` : 'Select a chat to begin'}</p>
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
            <div className="message-header"><span className="message-role">🤖 {selectedModel}</span></div>
            <div className="message-content typing-indicator"><span></span><span></span><span></span></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chatbox-input-container">
        <textarea className="chatbox-input" value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={handleKeyPress}
          placeholder={activeChat ? `Message ${activeChat}...` : 'Select a chat...'} rows="3" disabled={isLoading} />
        <button className="chatbox-send-btn" onClick={sendMessage} disabled={isLoading || !input.trim()}>
          {isLoading ? '⏳' : '📤'} Send
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
