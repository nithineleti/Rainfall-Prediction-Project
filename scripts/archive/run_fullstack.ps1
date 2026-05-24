#!/usr/bin/env pwsh
# =========================================
# Watershed-UP Full-Stack Startup Script
# =========================================
# Runs both backend (FastAPI) and frontend (React + Vite)

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Watershed-UP Full-Stack Launcher" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

# Check if backend venv exists
if (-Not (Test-Path "backend\.venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Backend virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: cd backend; python -m venv .venv; .venv\Scripts\activate; pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Check if frontend node_modules exists
if (-Not (Test-Path "app-frontend\node_modules")) {
    Write-Host "[ERROR] Frontend dependencies not installed!" -ForegroundColor Red
    Write-Host "Please run: cd app-frontend; npm install" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/4] Starting Backend Server (FastAPI)..." -ForegroundColor Green
Write-Host "      URL: http://localhost:8000" -ForegroundColor Gray
Write-Host "      Docs: http://localhost:8000/docs`n" -ForegroundColor Gray

# Start backend in new PowerShell window
$backendScript = @"
cd '$PSScriptRoot\backend'
Write-Host 'Backend starting...' -ForegroundColor Cyan
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Start-Sleep -Seconds 3

Write-Host "[2/4] Starting Frontend Server (Vite + React)..." -ForegroundColor Green
Write-Host "      URL: http://localhost:5173`n" -ForegroundColor Gray

# Add Node.js to PATH and start frontend in new window
$frontendScript = @"
`$env:Path = 'C:\Program Files\nodejs;' + `$env:Path
cd '$PSScriptRoot\app-frontend'
Write-Host 'Frontend starting...' -ForegroundColor Cyan
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Start-Sleep -Seconds 2

Write-Host "`n[3/4] Servers Starting..." -ForegroundColor Green
Write-Host "      Please wait for both servers to initialize...`n" -ForegroundColor Gray

Start-Sleep -Seconds 3

Write-Host "[4/4] Ready!" -ForegroundColor Green
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Full-Stack Environment Running" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

Write-Host "Access your application:" -ForegroundColor White
Write-Host "  Frontend:   " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:5173" -ForegroundColor Yellow
Write-Host "  Backend:    " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000" -ForegroundColor Yellow
Write-Host "  API Docs:   " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  Health:     " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000/health" -ForegroundColor Yellow

Write-Host "`nEndpoints available:" -ForegroundColor White
Write-Host "  GET  /api/watersheds          - Watershed GeoJSON" -ForegroundColor Gray
Write-Host "  GET  /tiles/demo/{z}/{x}/{y}  - Demo raster tiles`n" -ForegroundColor Gray

Write-Host "Press Ctrl+C to stop this script." -ForegroundColor Cyan
Write-Host "(Backend and Frontend will continue running in separate windows)`n" -ForegroundColor Cyan

# Keep script running
while ($true) {
    Start-Sleep -Seconds 10
}
