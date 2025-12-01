# BAIT Desktop - Complete Setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BAIT Desktop Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Install Python dependencies
Write-Host "`n[1/3] Installing Python packages..." -ForegroundColor Yellow
if (Test-Path "venv/Scripts/Activate.ps1") {
    .\venv\Scripts\Activate.ps1
} else {
    python -m venv venv
    .\venv\Scripts\Activate.ps1
}
pip install -r requirements.txt

# Install Node dependencies
Write-Host "[2/3] Installing Node packages..." -ForegroundColor Yellow
npm install

# Create public/main.js if missing
Write-Host "[3/3] Setting up Electron..." -ForegroundColor Yellow
if (-not (Test-Path "public")) {
    New-Item -ItemType Directory -Path "public"
}

$mainJs = @"
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
"@

Set-Content -Path "public/main.js" -Value $mainJs

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   ✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nRun: .\start.ps1" -ForegroundColor Cyan
