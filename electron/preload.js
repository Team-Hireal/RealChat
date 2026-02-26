const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  restartBackend: () => ipcRenderer.invoke('restart-backend'),

  // Event listeners
  onBackendStatus: (callback) => {
    ipcRenderer.on('backend-status', (event, data) => callback(data));
  },

  // Platform info
  platform: process.platform
});

// Log that preload script loaded
console.log('Preload script loaded');
