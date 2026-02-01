import React from 'react';
import { useAppContext } from '../context/AppContext';
import './StatusBadge.css';

const StatusBadge = () => {
  const { state } = useAppContext();
  const { running } = state.botStatus;

  return (
    <div className={`status-badge ${running ? 'running' : 'stopped'}`}>
      <span className="status-dot"></span>
      <span className="status-text">{running ? 'Running' : 'Stopped'}</span>
    </div>
  );
};

export default StatusBadge;
