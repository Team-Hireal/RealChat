import React from 'react';
import { useAppContext } from '../context/AppContext';
import { useTheme } from '../context/ThemeContext';
import useBotControl from '../hooks/useBotControl';
import StatusBadge from './StatusBadge';
import './Header.css';

const Header = () => {
  const { state } = useAppContext();
  const { theme, toggleTheme } = useTheme();
  const { startBot, stopBot, refreshStatus, isStarting, isStopping } = useBotControl();
  const { running } = state.botStatus;

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-title">WeChat Auto-Reply Bot</h1>
          <StatusBadge />
        </div>
        <div className="header-controls">
          <button
            className="btn btn-primary btn-sm"
            onClick={startBot}
            disabled={running || isStarting}
          >
            {isStarting ? 'Starting...' : 'Start Bot'}
          </button>
          <button
            className="btn btn-danger btn-sm"
            onClick={stopBot}
            disabled={!running || isStopping}
          >
            {isStopping ? 'Stopping...' : 'Stop Bot'}
          </button>
          <button
            className="btn btn-secondary btn-sm"
            onClick={refreshStatus}
          >
            Refresh
          </button>
          <button
            className="btn btn-theme btn-sm"
            onClick={toggleTheme}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
