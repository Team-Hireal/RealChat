import { useState, useEffect } from 'react';
import apiService from '../services/api';
import './MainPanel.css';

const MainPanel = () => {
  const [message, setMessage] = useState('');
  const [chatName, setChatName] = useState('File');
  const [logs, setLogs] = useState([]);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    addLog('Control panel loaded', 'info');
  }, []);

  const addLog = (message, type = 'info') => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time, message, type }]);
  };

  const sendMessage = async () => {
    if (isSending || !message.trim()) return;

    setIsSending(true);
    try {
      let targetChat = chatName || 'File';

      if (targetChat.toLowerCase() === 'file') {
        const searchResponse = await apiService.searchChat('File');
        if (searchResponse.data.success && searchResponse.data.results.length > 0) {
          targetChat = searchResponse.data.results[0].name;
          addLog(`Using chat: ${targetChat}`, 'info');
        }
      }

      addLog(`Sending: ${message}`, 'info');
      const response = await apiService.sendMessage(targetChat, message);

      if (response.data.success) {
        addLog('Message sent successfully', 'success');
        setMessage('');
      } else {
        addLog(`Failed to send: ${response.data.error}`, 'error');
      }
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
    } finally {
      setIsSending(false);
    }
  };

  const sendQuickMessage = async (quickMsg) => {
    setMessage(quickMsg);
    setTimeout(() => sendMessage(), 100);
  };

  const clearLogs = () => {
    setLogs([]);
    addLog('Logs cleared', 'info');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="main-panel">
      {/* Send Message */}
      <div className="section">
        <h3 className="section-title">Send Message</h3>
        <div className="message-box">
          <input
            type="text"
            className="message-input"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
          />
          <button
            className="send-btn"
            onClick={sendMessage}
            disabled={isSending || !message.trim()}
          >
            Send 📤
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button className="action-btn" onClick={() => sendQuickMessage('Hello!')}>
          👋 Hello
        </button>
        <button className="action-btn" onClick={() => sendQuickMessage('Test message')}>
          🧪 Test
        </button>
        <button className="action-btn" onClick={() => sendQuickMessage('Status check')}>
          📊 Status
        </button>
      </div>

      {/* Activity Log */}
      <div className="section">
        <div className="log-header">
          <h3 className="section-title">Activity Log</h3>
          <button className="clear-btn" onClick={clearLogs}>
            🗑️ Clear Logs
          </button>
        </div>
        <div className="logs-container">
          {logs.length === 0 ? (
            <div className="log-entry log-info">
              <span className="log-time">{new Date().toLocaleTimeString()}</span>
              No logs yet
            </div>
          ) : (
            logs.map((log, index) => (
              <div key={index} className={`log-entry log-${log.type}`}>
                <span className="log-time">{log.time}</span>
                {log.message}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default MainPanel;
