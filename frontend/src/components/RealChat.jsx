import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import './RealChat.css';

const RealChat = () => {
  // State management
  const [agentRunning, setAgentRunning] = useState(false);
  const [wechatRunning, setWechatRunning] = useState(false);
  const [selectedChat, setSelectedChat] = useState('');
  const [chats, setChats] = useState([]);
  const [logs, setLogs] = useState([]);
  const [testMessage, setTestMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [windowInfo, setWindowInfo] = useState(null);

  // Refs
  const socketRef = useRef(null);
  const logsEndRef = useRef(null);

  // Auto-scroll logs
  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5050';
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5050';

// Initialize socket connection
  useEffect(() => {
    socketRef.current = io(SOCKET_URL);

    socketRef.current.on('connect', () => {
      addLog('Connected to server', 'success');
    });

    socketRef.current.on('status', (data) => {
      setAgentRunning(data.agent_running);
      setWechatRunning(data.wechat_running);
    });

    socketRef.current.on('agent_status', (data) => {
      addLog(`Agent ${data.status}`, 'info');
      setAgentRunning(data.status === 'started');
    });

    socketRef.current.on('new_message', (data) => {
      addLog(`📨 New message in ${data.chat}: ${data.message.substring(0, 50)}...`, 'message');
    });

    socketRef.current.on('ai_response', (data) => {
      addLog(`🤖 AI response: ${data.response.substring(0, 50)}...`, 'ai');
    });

    socketRef.current.on('message_sent', (data) => {
      addLog(`✓ Message sent to ${data.chat}`, 'success');
    });

    socketRef.current.on('command_executed', (data) => {
      addLog(`⚡ Command executed: ${data.command}`, 'command');
    });

    socketRef.current.on('chat_switched', (data) => {
      addLog(`🔄 Switched to monitoring: ${data.chat}`, 'info');
      setSelectedChat(data.chat);
    });

    socketRef.current.on('error', (data) => {
      addLog(`❌ Error: ${data.error}`, 'error');
    });

    // Fetch initial status
    fetchStatus();
    fetchWindowInfo();

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  // Helper functions
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { message, type, timestamp }]);
  };

  const apiCall = async (endpoint, method = 'GET', body = null) => {
    try {
      const token = localStorage.getItem('access_token');
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      };
      if (body) options.body = JSON.stringify(body);

      const response = await fetch(`${API_BASE}${endpoint}`, options);
      const data = await response.json();
      return data;
    } catch (error) {
      addLog(`API Error: ${error.message}`, 'error');
      return { success: false, error: error.message };
    }
  };

  // API functions
  const fetchStatus = async () => {
    const data = await apiCall('/api/status');
    if (data) {
      setAgentRunning(data.agent_running);
      setWechatRunning(data.wechat_running);
    }
  };

  const fetchWindowInfo = async () => {
    const data = await apiCall('/api/wechat/window');
    if (data.success) {
      setWindowInfo(data.window);
    }
  };

  const fetchChats = async () => {
    setLoading(true);
    addLog('Scanning chats...', 'info');
    const data = await apiCall('/api/wechat/chats?structured=true&max=20');
    if (data.success) {
      setChats(data.chats);
      addLog(`Found ${data.chats.length} chats`, 'success');
    }
    setLoading(false);
  };

  const startAgent = async (chatName = null) => {
    setLoading(true);
    const body = chatName ? { chat_name: chatName } : {};
    const data = await apiCall('/api/agent/start', 'POST', body);
    if (data.success) {
      addLog(data.message, 'success');
      setAgentRunning(true);
    }
    setLoading(false);
  };

  const stopAgent = async () => {
    setLoading(true);
    const data = await apiCall('/api/agent/stop', 'POST');
    if (data.success) {
      addLog(data.message, 'success');
      setAgentRunning(false);
    }
    setLoading(false);
  };

  const sendTestMessage = async () => {
    if (!testMessage.trim()) {
      addLog('Please enter a message', 'error');
      return;
    }

    setLoading(true);
    const data = await apiCall('/api/wechat/send', 'POST', {
      message: testMessage,
      chat_name: selectedChat || 'File Transfer'
    });

    if (data.success) {
      addLog(`Message sent: ${testMessage}`, 'success');
      setTestMessage('');
    }
    setLoading(false);
  };

  const readMessages = async () => {
    setLoading(true);
    const chatName = selectedChat || 'File Transfer';
    addLog(`Reading messages from ${chatName}...`, 'info');

    const data = await apiCall(`/api/wechat/read?structured=true&chat_name=${encodeURIComponent(chatName)}`);

    if (data.success && data.data) {
      addLog(`Read ${data.data.message_count} messages from ${chatName}`, 'success');
      if (data.data.latest_message) {
        addLog(`Latest: ${data.data.latest_message.substring(0, 100)}`, 'message');
      }
    }
    setLoading(false);
  };

  // Render
  return (
    <div className="realchat-container">
      {/* Header */}
      <header className="header">
        <div className="logo">
          <span className="logo-icon">🤖</span>
          <h1>RealChat</h1>
        </div>
        <div className="status-indicators">
          <div className={`status-badge ${wechatRunning ? 'online' : 'offline'}`}>
            WeChat: {wechatRunning ? 'Online' : 'Offline'}
          </div>
          <div className={`status-badge ${agentRunning ? 'online' : 'offline'}`}>
            Agent: {agentRunning ? 'Running' : 'Stopped'}
          </div>
        </div>
      </header>

      <div className="main-content">
        {/* Sidebar */}
        <aside className="sidebar">
          <section className="section">
            <h2 className="section-title">Agent Control</h2>
            <div className="button-group">
              <button
                className="btn btn-primary"
                onClick={() => startAgent()}
                disabled={agentRunning || loading}
              >
                {agentRunning ? '✓ Running' : 'Start Agent'}
              </button>
              <button
                className="btn btn-danger"
                onClick={stopAgent}
                disabled={!agentRunning || loading}
              >
                Stop Agent
              </button>
            </div>
          </section>

          <section className="section">
            <h2 className="section-title">WeChat Window</h2>
            {windowInfo && (
              <div className="info-card">
                <div className="info-item">
                  <span className="info-label">Title:</span>
                  <span className="info-value">{windowInfo.title || 'WeChat'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Size:</span>
                  <span className="info-value">{windowInfo.width}x{windowInfo.height}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Active:</span>
                  <span className={`status-dot ${windowInfo.is_frontmost ? 'active' : 'inactive'}`}></span>
                </div>
              </div>
            )}
            <button className="btn btn-secondary" onClick={fetchWindowInfo}>
              Refresh
            </button>
          </section>

          <section className="section">
            <h2 className="section-title">Chats</h2>
            <button className="btn btn-secondary" onClick={fetchChats} disabled={loading}>
              {loading ? 'Scanning...' : 'Scan Chats'}
            </button>
            <div className="chat-list">
              {chats.length > 0 ? (
                chats.map((chat, idx) => (
                  <div
                    key={idx}
                    className={`chat-item ${selectedChat === chat.name ? 'selected' : ''}`}
                    onClick={() => setSelectedChat(chat.name)}
                  >
                    <span className="chat-icon">{chat.type === 'group' ? '👥' : '👤'}</span>
                    <span className="chat-name">{chat.name}</span>
                  </div>
                ))
              ) : (
                <p className="empty-state">No chats found</p>
              )}
            </div>
          </section>
        </aside>

        {/* Main Panel */}
        <main className="main-panel">
          <section className="section">
            <h2 className="section-title">Test Message</h2>
            <div className="input-group">
              <input
                type="text"
                className="input"
                placeholder="Enter test message..."
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendTestMessage()}
              />
              <button className="btn btn-primary" onClick={sendTestMessage} disabled={loading}>
                Send
              </button>
            </div>
            <div className="chat-info">
              Target: <strong>{selectedChat || 'File Transfer'}</strong>
            </div>
          </section>

          <section className="section">
            <h2 className="section-title">Quick Actions</h2>
            <div className="button-group">
              <button className="btn btn-secondary" onClick={readMessages} disabled={loading}>
                Read Messages
              </button>
              <button className="btn btn-secondary" onClick={fetchStatus} disabled={loading}>
                Refresh Status
              </button>
            </div>
          </section>

          <section className="section logs-section">
            <h2 className="section-title">Activity Log</h2>
            <div className="logs-container">
              {logs.map((log, idx) => (
                <div key={idx} className={`log-entry log-${log.type}`}>
                  <span className="log-time">{log.timestamp}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => setLogs([])}>
              Clear Logs
            </button>
          </section>
        </main>
      </div>
    </div>
  );
};

export default RealChat;
