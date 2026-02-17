import React, { useState, useEffect, useCallback } from 'react';
import { useAppContext } from '../context/AppContext';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import apiService from '../services/api';
import './Header.css';

const SERVICES = [
  { key: 'backend',  label: 'Backend',  port: 5001 },
  { key: 'frontend', label: 'Frontend', port: 5173 },
  { key: 'zypher',   label: 'Zypher',   port: 8000 },
  { key: 'bridge',   label: 'Bridge',   port: 8080 },
];

const Header = () => {
  const { state } = useAppContext();
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const [serviceStatus, setServiceStatus] = useState({});
  const [restarting, setRestarting] = useState({});

  const checkServices = useCallback(async () => {
    try {
      const res = await apiService.getServicesStatus();
      if (res.data) setServiceStatus(res.data);
    } catch {
      // Backend itself is down
      setServiceStatus(prev => ({ ...prev, backend: false }));
    }
  }, []);

  useEffect(() => {
    checkServices();
    const interval = setInterval(checkServices, 3000);
    return () => clearInterval(interval);
  }, [checkServices]);

  const handleRestart = async (serviceName) => {
    setRestarting(prev => ({ ...prev, [serviceName]: true }));
    try {
      await apiService.restartService(serviceName);
    } catch {
      // Backend may have restarted itself
    }
    // Poll until service comes back (or timeout)
    setTimeout(() => {
      checkServices();
      setRestarting(prev => ({ ...prev, [serviceName]: false }));
    }, serviceName === 'backend' ? 4000 : 2000);
  };

  return (
    <header className="header">
      <div className="logo">
        <img src="/realchat-icon.svg" alt="RealChat" className="logo-icon" />
        <h1>RealChat</h1>
      </div>

      <div className="service-controls">
        {SERVICES.map(svc => {
          const alive = serviceStatus[svc.key];
          const spinning = restarting[svc.key];
          return (
            <div key={svc.key} className="service-chip">
              <span className={`svc-dot ${alive ? 'on' : 'off'}`} />
              <span className="svc-label">{svc.label}</span>
              <button
                className={`svc-restart${spinning ? ' spinning' : ''}`}
                onClick={() => handleRestart(svc.key)}
                disabled={spinning}
                title={`Restart ${svc.label}`}
                aria-label={`Restart ${svc.label}`}
              >
                &#x21bb;
              </button>
            </div>
          );
        })}
      </div>

      <button
        className="theme-toggle"
        onClick={toggleTheme}
        aria-label="Toggle theme"
      >
        {theme === 'light' ? '\u{1F319}' : '\u{2600}\u{FE0F}'}
      </button>

      {user && (
        <button className="logout-btn" onClick={logout} title={user.email}>
          Sign Out
        </button>
      )}
    </header>
  );
};

export default Header;