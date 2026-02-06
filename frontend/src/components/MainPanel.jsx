import { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { ACTIONS } from '../context/AppReducer';
import ChatBox from './ChatBox';
import './MainPanel.css';

const MainPanel = () => {
  const { state, dispatch } = useAppContext();
  const [hasLogged, setHasLogged] = useState(false);

  useEffect(() => {
    if (!hasLogged) {
      addLog('Control panel loaded', 'info');
      setHasLogged(true);
    }
  }, [hasLogged]);

  const addLog = (message, type = 'info') => {
    dispatch({
      type: ACTIONS.ADD_LOG,
      payload: {
        type: type,
        message: message,
        timestamp: Date.now()
      }
    });
  };

  const clearLogs = () => {
    dispatch({ type: ACTIONS.CLEAR_LOGS });
    addLog('Logs cleared', 'info');
  };

  return (
    <div className="main-panel">
      {/* AI ChatBox */}
      <div className="section chatbox-section">
        <ChatBox />
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
          {!state.logs || state.logs.length === 0 ? (
            <div className="log-entry log-info">
              <span className="log-time">{new Date().toLocaleTimeString()}</span>
              No logs yet
            </div>
          ) : (
            state.logs.map((log, index) => (
              <div key={index} className={`log-entry log-${log.type}`}>
                <span className="log-time">
                  {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()}
                </span>
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
