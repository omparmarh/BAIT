# BAIT Desktop App - Simple Start (All in one terminal)

Write-Host "Starting BAIT..." -ForegroundColor Cyan

# Activate Python venv
.\venv\Scripts\Activate.ps1

# Start backend in background
Write-Host "Starting backend..." -ForegroundColor Yellow
Start-Process -NoNewWindow python -ArgumentList "api_server.py"

# Wait 3 seconds
Start-Sleep -Seconds 3

# Start Vite in background
Write-Host "Starting frontend..." -ForegroundColor Yellow
Start-Job -ScriptBlock { Set-Location $using:PWD; npm run dev }

# Wait 5 seconds for Vite
Start-Sleep -Seconds 5

# Launch Electron
Write-Host "Launching desktop app..." -ForegroundColor Green
electron .
