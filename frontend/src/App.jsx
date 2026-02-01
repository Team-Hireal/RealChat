import { useEffect } from 'react';
import { AppProvider, useAppContext } from './context/AppContext';
import { ThemeProvider } from './context/ThemeContext';
import { ACTIONS } from './context/AppReducer';
import Header from './components/Header';
import ControlPanel from './components/ControlPanel';
import ConfigurationForm from './components/ConfigurationForm';
import ActivityLogs from './components/ActivityLogs';
import ContactTracking from './components/ContactTracking';
import useConfig from './hooks/useConfig';
import usePolling from './hooks/usePolling';
import apiService from './services/api';
import './App.css';

function AppContent() {
  const { state, dispatch } = useAppContext();
  const { loadConfig } = useConfig();

  // Load initial data
  useEffect(() => {
    loadConfig();
  }, []);

  // Poll for status and logs when bot is running
  usePolling(async () => {
    try {
      const [statusRes, logsRes, trackingRes] = await Promise.all([
        apiService.getStatus(),
        apiService.getLogs(),
        apiService.getTracking(),
      ]);

      dispatch({ type: ACTIONS.SET_BOT_STATUS, payload: statusRes.data });
      dispatch({ type: ACTIONS.SET_LOGS, payload: logsRes.data });
      dispatch({ type: ACTIONS.SET_TRACKING, payload: trackingRes.data });
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, 2000, true); // Poll every 2 seconds

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <div className="content-grid">
          <ConfigurationForm />
          <div className="logs-section">
            <ActivityLogs />
            <ContactTracking />
          </div>
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
