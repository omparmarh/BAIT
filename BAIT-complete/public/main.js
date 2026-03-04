const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow;
let backendProcess;

// Cross-platform Python path
const venvPython = process.platform === 'win32'
  ? path.join(__dirname, '../venv/Scripts/python.exe')
  : path.join(__dirname, '../venv/bin/python3');

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    title: 'BAIT - AI Assistant'
  });

  mainWindow.loadURL('http://localhost:5173');
  // mainWindow.webContents.openDevTools(); // uncomment for debugging
}

function isBackendRunning(callback) {
  // Check if port 8000 is already serving before spawning a new process
  http.get('http://127.0.0.1:8000/', (res) => {
    callback(true);
  }).on('error', () => {
    callback(false);
  });
}

function startBackend() {
  isBackendRunning((running) => {
    if (running) {
      console.log('Backend already running on port 8000, skipping spawn.');
      return;
    }

    const pythonScript = path.join(__dirname, '../api_server.py');
    console.log(`Starting backend: ${venvPython} ${pythonScript}`);

    backendProcess = spawn(venvPython, [pythonScript], {
      cwd: path.join(__dirname, '..'),
      stdio: ['ignore', 'pipe', 'pipe']
    });

    backendProcess.stdout.on('data', (data) => console.log('Backend:', data.toString()));
    backendProcess.stderr.on('data', (data) => console.error('Backend:', data.toString()));

    backendProcess.on('error', (err) => {
      console.error('Failed to start backend:', err.message);
    });

    backendProcess.on('exit', (code) => {
      console.log(`Backend exited with code ${code}`);
    });
  });
}

app.on('ready', () => {
  startBackend();
  setTimeout(createWindow, 3000);
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  app.quit();
});
