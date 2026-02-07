import { useEffect } from 'react';
import { AppProvider, useAppContext } from './context/AppContext';
import { ThemeProvider } from './context/ThemeContext';
import { ACTIONS } from './context/AppReducer';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MainPanel from './components/MainPanel';
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

    // Connect to Socket.IO for real-time updates
    const socket = io('http://localhost:5001');

    socket.on('connect', () => {
      console.log('✅ Connected to Flask Socket.IO');
      dispatch({ type: ACTIONS.SET_SOCKET_CONNECTED, payload: true });
    });

    socket.on('disconnect', () => {
      console.log('❌ Disconnected from Flask Socket.IO');
      dispatch({ type: ACTIONS.SET_SOCKET_CONNECTED, payload: false });
    });

    // Listen for current chat updates
    socket.on('current_chat_update', (data) => {
      console.log('📱 Current chat update:', data);
      dispatch({
        type: ACTIONS.SET_CURRENT_CHAT,
        payload: data
      });
    });

    socket.on('bridge_message', (data) => {
      console.log('📨 Bridge message:', data);

      // Play notification sound for new message
      soundService.playMessage();

      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'info',
          message: `📨 Bridge: ${data.sender} in ${data.chat}: ${data.text.substring(0, 50)}...`,
          timestamp: Date.now()
        }
      });
    });

    socket.on('ai_response', (data) => {
      console.log('🤖 AI response:', data);

      // Play completion sound when AI finishes responding
      soundService.playComplete();

      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'success',
          message: `🤖 AI responded in ${data.chat}`,
          timestamp: Date.now()
        }
      });
    });

    socket.on('log', (data) => {
      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: data.type || 'info',
          message: data.message,
          timestamp: data.timestamp || Date.now()
        }
      });
    });

    socket.on('message_sent', (data) => {
      // Play success sound when message is sent
      soundService.playSuccess();

      dispatch({
        type: ACTIONS.ADD_LOG,
        payload: {
          type: 'success',
          message: `✅ Message sent to ${data.chat}${data.via ? ` via ${data.via}` : ''}`,
          timestamp: Date.now()
        }
      });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Poll for status - Every 1 second for consistent responsiveness
  usePolling(async () => {
    try {
      const statusRes = await apiService.getStatus();
      dispatch({ type: ACTIONS.SET_BOT_STATUS, payload: statusRes.data });
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, 1000, true);

  // Poll for current chat - Every 1 second for consistent responsiveness
  usePolling(async () => {
    try {
      const chatRes = await apiService.getCurrentChat();
      if (chatRes.data.success) {
        dispatch({
          type: ACTIONS.SET_CURRENT_CHAT,
          payload: {
            chat: chatRes.data.chat || 'No active chat',
            detected: chatRes.data.detected || false
          }
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

function App() {
  return (
    <ThemeProvider>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </ThemeProvider>
  );
}

export default App;
