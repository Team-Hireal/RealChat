import { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { ACTIONS } from '../context/AppReducer';
import apiService from '../services/api';
import AISettings from './AISettings';
import './Sidebar.css';

const Sidebar = () => {
  const { dispatch } = useAppContext();
  const [agentRunning, setAgentRunning] = useState(false);
  const [chatName, setChatName] = useState('File');
  const [windowInfo, setWindowInfo] = useState(null);
  const [backendConfig, setBackendConfig] = useState({
    ai_model: 'claude-sonnet-4-5-20250929',
    scan_method: 'applescript',
    ai_max_tokens: 1024,
    auto_detect_messages: false
  });
  const [automation, setAutomation] = useState({
    auto_reply: false,
    auto_forward: false,
    command_mode: true
  });

  useEffect(() => {
    loadBackendConfig();
    refreshWindow();
    const interval = setInterval(refreshWindow, 1000);
    return () => clearInterval(interval);
  }, []);

  const loadBackendConfig = async () => {
    try {
      const response = await apiService.getBackendConfig();
      if (response.data.success && response.data.config) {
        setBackendConfig(response.data.config);
      }
    } catch (error) {
      console.error('Failed to load backend config:', error);
    }
  };

  const updateBackendConfig = async (updates) => {
    try {
      const newConfig = { ...backendConfig, ...updates };
      await apiService.updateBackendConfig(newConfig);
      setBackendConfig(newConfig);
    } catch (error) {
      console.error('Failed to update backend config:', error);
    }
  };

  const refreshWindow = async () => {
    try {
      const response = await apiService.getWindowInfo();
      if (response.data.success) {
        setWindowInfo(response.data);
      }
    } catch (error) {
      console.error('Failed to refresh window:', error);
    }
  };

  const startAgent = async () => {
    try {
      await apiService.startAgent(chatName);
      setAgentRunning(true);
    } catch (error) {
      console.error('Failed to start agent:', error);
    }
  };

  const stopAgent = async () => {
    try {
      await apiService.stopAgent();
      setAgentRunning(false);
    } catch (error) {
      console.error('Failed to stop agent:', error);
    }
  };

  const searchChat = async () => {
    try {
      const response = await apiService.searchChat(chatName);
      if (response.data.success && response.data.results.length > 0) {
        console.log('Found chats:', response.data.results);
      }
    } catch (error) {
      console.error('Failed to search chat:', error);
    }
  };

  const readMessages = async () => {
    try {
      await apiService.readMessages(chatName);
    } catch (error) {
      console.error('Failed to read messages:', error);
    }
  };

  const testOCR = async () => {
    try {
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'info',
          message: '🔍 Starting OCR message reading...',
          timestamp: Date.now()
        }
      });

      const response = await apiService.readMessagesOCR();

      if (response.data.success) {
        const messages = response.data.messages;

        dispatch({
          type: ACTIONS.ADD_LOG,
          payload: {
            type: 'success',
            message: `✅ OCR extracted ${messages.length} messages`,
            timestamp: Date.now()
          }
        });

        // Display each message in the activity log
        messages.forEach((msg, index) => {
          const timestamp = msg.timestamp || 'Unknown time';
          const sender = msg.sender || 'Unknown sender';
          const text = msg.text || '';

          dispatch({
            type: ACTIONS.ADD_LOG,
            payload: {
              type: 'info',
              message: `📝 [${timestamp}] ${sender}: ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}`,
              timestamp: Date.now()
            }
          });
        });

        console.log('Full OCR results:', messages);
      } else {
        dispatch({
          type: ACTIONS.ADD_LOG,
          payload: {
            type: 'error',
            message: `❌ OCR failed: ${response.data.error || 'Unknown error'}`,
            timestamp: Date.now()
          }
        });
      }
    } catch (error) {
      console.error('Failed to run OCR:', error);
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'error',
          message: `❌ OCR error: ${error.message}`,
          timestamp: Date.now()
        }
      });
    }
  };

  const openChatTest = async () => {
    try {
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'info',
          message: `📂 Opening chat: ${chatName}`,
          timestamp: Date.now()
        }
      });

      const response = await apiService.openChat(chatName);

      if (response.data.success) {
        dispatch({
          type: ACTIONS.ADD_LOG,
          payload: {
            type: 'success',
            message: `✅ Chat opened: ${response.data.chat}`,
            timestamp: Date.now()
          }
        });
      } else {
        dispatch({
          type: ACTIONS.ADD_LOG,
          payload: {
            type: 'error',
            message: '❌ Failed to open chat',
            timestamp: Date.now()
          }
        });
      }
    } catch (error) {
      console.error('Failed to open chat:', error);
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'error',
          message: `❌ Error opening chat: ${error.message}`,
          timestamp: Date.now()
        }
      });
    }
  };

  return (
    <div className="sidebar">
      {/* AI Settings */}
      <AISettings />

      {/* Agent Control */}
      <div className="section">
        <h3 className="section-title">Agent Control</h3>
        <button
          className="btn btn-primary"
          onClick={startAgent}
          disabled={agentRunning}
        >
          ▶️ Start Agent
        </button>
        <button
          className="btn btn-danger"
          onClick={stopAgent}
          disabled={!agentRunning}
        >
          ⏹️ Stop Agent
        </button>
      </div>

      {/* Target Chat */}
      <div className="section">
        <h3 className="section-title">Target Chat</h3>
        <div className="input-group">
          <input
            type="text"
            className="input"
            value={chatName}
            onChange={(e) => setChatName(e.target.value)}
            placeholder="Enter chat name..."
          />
          <small className="input-hint">
            💡 Use "File" to find "File Transfer"
          </small>
        </div>
        <button className="btn btn-secondary" onClick={searchChat}>
          🔍 Search Chat
        </button>
      </div>

      {/* WeChat Window */}
      <div className="section">
        <h3 className="section-title">WeChat Window</h3>
        <div className="info-card">
          {windowInfo && windowInfo.window ? (
            <>
              <div className="info-item">
                <span className="info-label">Title:</span>
                <span className="info-value">{windowInfo.window.title || 'WeChat'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Size:</span>
                <span className="info-value">
                  {windowInfo.window.width}x{windowInfo.window.height}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Active:</span>
                <span className="info-value">
                  {windowInfo.window.is_frontmost ? '✓ Yes' : '✗ No'}
                </span>
              </div>
              {windowInfo.cursor && (
                <div className="info-item">
                  <span className="info-label">Cursor Pos:</span>
                  <span className="info-value cursor-pos">
                    ({windowInfo.cursor.x}, {windowInfo.cursor.y})
                  </span>
                </div>
              )}
              {windowInfo.window_under_cursor && (
                <div className="info-item">
                  <span className="info-label">Window Under:</span>
                  <span className={`info-value ${windowInfo.window_under_cursor.process_name === 'WeChat' ? 'success' : 'error'}`}>
                    {windowInfo.window_under_cursor.process_name}
                  </span>
                </div>
              )}
              <div className="info-item">
                <span className="info-label">Cursor:</span>
                <span className="info-value">
                  {windowInfo.cursor_in_window ? '✓ In Window' : '✗ Outside'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Focus:</span>
                <span className={`info-value ${windowInfo.is_focused ? 'success' : 'error'}`}>
                  {windowInfo.is_focused ? '✓ Focused' : '✗ Not Focused'}
                </span>
              </div>
            </>
          ) : (
            <div className="info-item">
              <span className="info-label">Status:</span>
              <span className="info-value">Loading...</span>
            </div>
          )}
        </div>
        <button className="btn btn-secondary" onClick={refreshWindow}>
          🔄 Refresh
        </button>
      </div>

      {/* Quick Actions */}
      <div className="section">
        <h3 className="section-title">Quick Actions</h3>
        <button className="btn btn-secondary" onClick={openChatTest}>
          📂 Open Chat
        </button>
        <button className="btn btn-secondary" onClick={readMessages}>
          📥 Read Messages
        </button>
        <button className="btn btn-primary" onClick={testOCR}>
          🔍 Test OCR Reading
        </button>
      </div>

      {/* Backend Configuration */}
      <div className="section">
        <h3 className="section-title">Backend Configuration</h3>
        <div className="input-group">
          <label className="input-label">AI Model</label>
          <select
            className="input"
            value={backendConfig.ai_model}
            onChange={(e) => updateBackendConfig({ ai_model: e.target.value })}
          >
            <option value="claude-sonnet-4-5-20250929">Claude Sonnet 4.5</option>
            <option value="claude-opus-4-5-20251101">Claude Opus 4.5</option>
            <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
            <option value="claude-3-opus-20240229">Claude 3 Opus</option>
          </select>
        </div>
        <div className="input-group">
          <label className="input-label">Scan Method</label>
          <select
            className="input"
            value={backendConfig.scan_method}
            onChange={(e) => updateBackendConfig({ scan_method: e.target.value })}
          >
            <option value="applescript">AppleScript</option>
            <option value="ocr">OCR</option>
            <option value="manual">Manual</option>
          </select>
        </div>
        <div className="input-group">
          <label className="input-label">Max Tokens</label>
          <input
            type="number"
            className="input"
            value={backendConfig.ai_max_tokens}
            onChange={(e) => updateBackendConfig({ ai_max_tokens: parseInt(e.target.value) })}
            min="256"
            max="8192"
            step="256"
          />
        </div>
        <div className="toggle-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={backendConfig.auto_detect_messages || false}
              onChange={(e) => updateBackendConfig({ auto_detect_messages: e.target.checked })}
            />
            <span className="toggle-text">Auto-Detect New Messages</span>
          </label>
          <small className="input-hint">
            💡 Automatically run OCR when new messages arrive
          </small>
        </div>
      </div>

      {/* Automation */}
      <div className="section">
        <h3 className="section-title">Automation</h3>
        <div className="toggle-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={automation.auto_reply}
              onChange={(e) => setAutomation({...automation, auto_reply: e.target.checked})}
            />
            <span className="toggle-text">Auto Reply</span>
          </label>
        </div>
        <div className="toggle-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={automation.auto_forward}
              onChange={(e) => setAutomation({...automation, auto_forward: e.target.checked})}
            />
            <span className="toggle-text">Auto Forward</span>
          </label>
        </div>
        <div className="toggle-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={automation.command_mode}
              onChange={(e) => setAutomation({...automation, command_mode: e.target.checked})}
            />
            <span className="toggle-text">Command Mode</span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
