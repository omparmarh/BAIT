const { app, BrowserWindow } = require('electron');
const path = require('path');
const spawn = require('child_process').spawn;

let mainWindow;
let backendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    title: 'BAIT - AI Assistant'
  });

  mainWindow.loadURL('http://localhost:5173');
  mainWindow.webContents.openDevTools();
}

function startBackend() {
  const pythonScript = path.join(__dirname, '../api_server.py');
  const venvPython = path.join(__dirname, '../venv/Scripts/python.exe');
  
  backendProcess = spawn(venvPython, [pythonScript]);
  backendProcess.stdout.on('data', (data) => console.log('Backend:', data.toString()));
  backendProcess.stderr.on('data', (data) => console.error('Backend Error:', data.toString()));
}

app.on('ready', () => {
  startBackend();
  setTimeout(createWindow, 3000);
});

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill();
  app.quit();
});
