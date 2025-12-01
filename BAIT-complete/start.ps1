# BAIT Desktop - Start

Write-Host "Starting BAIT Desktop..." -ForegroundColor Cyan

# Start Python backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python api_server.py"

# Wait
Start-Sleep -Seconds 3

# Start Vite
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"

# Wait
Start-Sleep -Seconds 5

# Start Electron
Write-Host "Launching desktop app..." -ForegroundColor Green
electron .
