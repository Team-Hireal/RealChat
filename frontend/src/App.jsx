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
import './App.css';

function AppContent() {
  const { state, dispatch } = useAppContext();
  const { loadConfig } = useConfig();

  // Load initial data
  useEffect(() => {
    loadConfig();
  }, []);

  // Poll for status
  usePolling(async () => {
    try {
      const statusRes = await apiService.getStatus();
      dispatch({ type: ACTIONS.SET_BOT_STATUS, payload: statusRes.data });
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, 2000, true);

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
