const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const log = require('electron-log');

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';
log.info('RealChat starting...');

let mainWindow = null;
let backendProcess = null;

const isDev = !app.isPackaged;

function createWindow() {
  log.info('Creating main window...');

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'build', 'icon.png'),
    show: false
  });

  // Load the app
  if (isDev) {
    // In development, load from Vite dev server
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    // In production, load from built files
    // __dirname is in app.asar, so go up to find dist
    const distPath = path.join(__dirname, '..', 'dist', 'index.html');
    mainWindow.loadFile(distPath);
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    log.info('Main window shown');
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

function startBackend() {
  if (backendProcess) {
    log.warn('Backend already running');
    return;
  }

  log.info('Starting Python backend...');

  // Find the python executable from venv
  let pythonPath;
  let backendPath;
  let workingDir;

  if (isDev) {
    pythonPath = './venv/bin/python3';
    backendPath = path.join(__dirname, '..', 'app_consolidated.py');
    workingDir = path.join(__dirname, '..');
  } else {
    // In production, venv is packaged with the app
    pythonPath = path.join(process.resourcesPath, 'app', 'venv', 'bin', 'python3');
    backendPath = path.join(process.resourcesPath, 'app', 'app_consolidated.py');
    workingDir = path.join(process.resourcesPath, 'app');
  }

  backendProcess = spawn(pythonPath, [backendPath], {
    cwd: workingDir,
    env: { ...process.env, FLASK_ENV: 'production' },
    stdio: ['ignore', 'pipe', 'pipe']
  });

  backendProcess.stdout.on('data', (data) => {
    log.info(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    log.error(`Backend Error: ${data}`);
  });

  backendProcess.on('close', (code) => {
    log.info(`Backend process exited with code ${code}`);
    backendProcess = null;
  });

  backendProcess.on('error', (err) => {
    log.error('Failed to start backend:', err);
    backendProcess = null;
  });
}

function stopBackend() {
  if (backendProcess) {
    log.info('Stopping backend...');
    backendProcess.kill();
    backendProcess = null;
  }
}

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-platform', () => {
  return process.platform;
});

ipcMain.handle('restart-backend', () => {
  stopBackend();
  setTimeout(startBackend, 1000);
  return { success: true };
});

// App lifecycle
app.whenReady().then(() => {
  log.info('App ready');
  createWindow();

  if (!isDev) {
    startBackend();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  log.info('App quitting...');
  stopBackend();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  log.error('Uncaught exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  log.error('Unhandled rejection at:', promise, 'reason:', reason);
});
