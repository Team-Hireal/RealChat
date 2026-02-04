import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api';

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
  getBackendConfig: () => api.get('/backend/config'),
  updateBackendConfig: (config) => api.post('/backend/config', config),

  // Agent control
  startAgent: (chatName) => api.post('/agent/start', { chat_name: chatName }),
  stopAgent: () => api.post('/agent/stop'),
  switchChat: (chat) => api.post('/agent/switch-chat', { chat }),

  // Status and monitoring
  getStatus: () => api.get('/status'),
  getBackendStatus: () => api.get('/backend/status'),
  getLogs: () => api.get('/logs'),
  getTracking: () => api.get('/tracking'),

  // WeChat operations
  scanChats: (maxChats = 10) => api.get(`/wechat/chats?max_chats=${maxChats}`),
  searchChat: (query) => api.get(`/wechat/chats/search?q=${encodeURIComponent(query)}`),
  getCurrentChat: () => api.get('/wechat/current-chat'),
  getWindowInfo: () => api.get('/wechat/window'),
  sendMessage: (chat, message) => api.post('/wechat/send', { chat_name: chat, message }),
  readMessages: (chat) => api.get(`/wechat/read?chat_name=${encodeURIComponent(chat)}&structured=true`),
  getHistory: (chat) => api.get(`/wechat/history?chat=${chat}`),

  // WeChat Bridge operations
  getBridgeStatus: () => api.get('/bridge/status'),
  sendViaBridge: (chat, message) => api.post('/bridge/send', { chat_name: chat, message }),

  // AI operations
  chatWithAI: (message, context) => api.post('/ai/chat', { message, context }),
  analyzeMessage: (message) => api.post('/ai/analyze', { message }),

  // Testing
  sendTestMessage: (message) => api.post('/send-test-message', { message }),
};

export default apiService;
