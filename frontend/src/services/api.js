import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
export const apiService = {
  // Configuration
  getConfig: () => api.get('/config'),
  updateConfig: (config) => api.post('/config', config),

  // Bot control
  startBot: () => api.post('/start'),
  stopBot: () => api.post('/stop'),

  // Status and monitoring
  getStatus: () => api.get('/status'),
  getLogs: () => api.get('/logs'),
  getTracking: () => api.get('/tracking'),

  // WeChat scanning
  scanChats: (maxChats = 10) => api.get(`/scan-chats?max_chats=${maxChats}`),
  checkAccessibility: () => api.get('/check-accessibility'),

  // Testing
  sendTestMessage: (message) => api.post('/send-test-message', { message }),
};

export default apiService;
