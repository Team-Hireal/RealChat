import { useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppProvider, useAppContext } from './context/AppContext';
import { ThemeProvider } from './context/ThemeContext';
import { ACTIONS } from './context/AppReducer';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MainPanel from './components/MainPanel';
import AuthPage from './components/AuthPage';
import useConfig from './hooks/useConfig';
import usePolling from './hooks/usePolling';
import apiService from './services/api';
import soundService from './services/soundService';
import io from 'socket.io-client';
import './App.css';

function AppContent() {
  const { state, dispatch } = useAppContext();
  const { loadConfig } = useConfig();

  // Load initial data
  useEffect(() => {
    loadConfig();

    // Initialize sound service from localStorage
    const savedSoundPref = localStorage.getItem('soundEnabled');
    if (savedSoundPref !== null) {
      soundService.setEnabled(savedSoundPref === 'true');
    }

    // Connect to Socket.IO for real-time updates
    const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5050';
    const socket = io(SOCKET_URL);

    socket.on('connect', () => {
      console.log('Connected to Flask Socket.IO');
      dispatch({ type: ACTIONS.SET_SOCKET_CONNECTED, payload: true });
    });

    socket.on('disconnect', () => {
      dispatch({ type: ACTIONS.SET_SOCKET_CONNECTED, payload: false });
    });

    socket.on('current_chat_update', (data) => {
      dispatch({ type: ACTIONS.SET_CURRENT_CHAT, payload: data });
    });

    socket.on('bridge_message', (data) => {
      soundService.playMessage();
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'info',
          message: `Bridge: ${data.sender} in ${data.chat}: ${data.text.substring(0, 50)}...`,
          timestamp: Date.now()
        }
      });
    });

    socket.on('ai_response', (data) => {
      soundService.playComplete();
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: { type: 'success', message: `AI responded in ${data.chat}`, timestamp: Date.now() }
      });
    });

    socket.on('log', (data) => {
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: { type: data.type || 'info', message: data.message, timestamp: data.timestamp || Date.now() }
      });
    });

    socket.on('message_sent', (data) => {
      soundService.playSuccess();
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'success',
          message: `Message sent to ${data.chat}${data.via ? ` via ${data.via}` : ''}`,
          timestamp: Date.now()
        }
      });
    });

    return () => { socket.disconnect(); };
  }, []);

  // Poll for status
  usePolling(async () => {
    try {
      const statusRes = await apiService.getStatus();
      dispatch({ type: ACTIONS.SET_BOT_STATUS, payload: statusRes.data });
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, 1000, true);

  // Poll for current chat
  usePolling(async () => {
    try {
      const chatRes = await apiService.getCurrentChat();
      if (chatRes.data.success) {
        dispatch({
          type: ACTIONS.SET_CURRENT_CHAT,
          payload: { chat: chatRes.data.chat || 'No active chat', detected: chatRes.data.detected || false }
        });
      }
    } catch (error) {
      console.error('Current chat polling error:', error);
    }
  }, 1000, true);

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <div className="control-layout">
          <Sidebar />
          <MainPanel />
        </div>
      </main>
    </div>
  );
}

function AuthGate() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Loading...</p>
      </div>
    );
  }

  if (!user) return <AuthPage />;

  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AuthGate />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
