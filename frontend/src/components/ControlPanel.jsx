import React from 'react';
import { useAppContext } from '../context/AppContext';
import useBotControl from '../hooks/useBotControl';
import './ControlPanel.css';

const ControlPanel = () => {
  const { state } = useAppContext();
  const { startBot, stopBot, refreshStatus, isStarting, isStopping } = useBotControl();
  const { running } = state.botStatus;

  return (
    <div className="control-panel">
      <div className="button-group">
        <button
          className="btn btn-primary"
          onClick={startBot}
          disabled={running || isStarting}
        >
          {isStarting ? 'Starting...' : 'Start Bot'}
        </button>
        <button
          className="btn btn-danger"
          onClick={stopBot}
          disabled={!running || isStopping}
        >
          {isStopping ? 'Stopping...' : 'Stop Bot'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={refreshStatus}
        >
          Refresh Status
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;
