import React, { useEffect, useRef } from 'react';
import { useAppContext } from '../context/AppContext';
import './ActivityLogs.css';

const ActivityLogs = () => {
  const { state } = useAppContext();
  const { logs } = state;
  const logsEndRef = useRef(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Auto-scroll disabled to allow users to review older logs
  // useEffect(() => {
  //   scrollToBottom();
  // }, [logs]);

  const getLogClass = (level) => {
    switch (level) {
      case 'success':
        return 'log-success';
      case 'error':
        return 'log-error';
      case 'warning':
        return 'log-warning';
      case 'info':
      default:
        return 'log-info';
    }
  };

  return (
    <div className="activity-logs">
      <h2>Activity Logs</h2>
      <div className="logs-container">
        {logs.length === 0 ? (
          <div className="empty-state">No logs yet. Start the bot to see activity.</div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className={`log-entry ${getLogClass(log.level)}`}>
              <span className="log-timestamp">{log.timestamp}</span>
              <span className="log-message">{log.message}</span>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
};

export default ActivityLogs;
