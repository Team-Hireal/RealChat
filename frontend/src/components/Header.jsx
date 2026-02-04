import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { useTheme } from '../context/ThemeContext';
import apiService from '../services/api';
import './Header.css';

const Header = () => {
  const { state } = useAppContext();
  const { theme, toggleTheme } = useTheme();
  const [backendRunning, setBackendRunning] = useState(false);
  const [wechatOnline, setWechatOnline] = useState(false);
  const [agentRunning, setAgentRunning] = useState(false);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await apiService.getStatus();
        if (response.data) {
          setBackendRunning(true);
          setWechatOnline(response.data.wechat_running || false);
          setAgentRunning(response.data.agent_running || false);
        }
      } catch (error) {
        setBackendRunning(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="header">
      <div className="logo">
        <span className="logo-icon">🤖</span>
        <h1>RealChat Control Panel</h1>
      </div>
      <div className="status-badges">
        <div className={`badge ${backendRunning ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          <span>Backend: {backendRunning ? 'Running' : 'Stopped'}</span>
        </div>
        <div className={`badge ${wechatOnline ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          <span>WeChat: {wechatOnline ? 'Online' : 'Offline'}</span>
        </div>
        <div className={`badge ${agentRunning ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          <span>Agent: {agentRunning ? 'Running' : 'Stopped'}</span>
        </div>
        <button
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label="Toggle theme"
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
      </div>
    </header>
  );
};

export default Header;
