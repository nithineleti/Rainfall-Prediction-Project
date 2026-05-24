# Frontend Setup and Run Script for Watershed-UP
# PowerShell version

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Watershed-UP Frontend Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Add Node.js to PATH for current session
$env:Path = "C:\Program Files\nodejs;" + $env:Path

# Check Node.js installation
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "[OK] npm version: $npmVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERROR] npm not found!" -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
$frontendPath = Join-Path $PSScriptRoot "app-frontend"
if (Test-Path $frontendPath) {
    Set-Location $frontendPath
    Write-Host "Current directory: $PWD" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "[ERROR] app-frontend directory not found!" -ForegroundColor Red
    exit 1
}

# Check package.json
if (-not (Test-Path "package.json")) {
    Write-Host "[ERROR] package.json not found" -ForegroundColor Red
    exit 1
}

# Install dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "[INFO] Installing dependencies... (this may take a few minutes)" -ForegroundColor Yellow
    Write-Host ""
    
    npm install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        Write-Host "Please check your internet connection and try again" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[OK] Dependencies already installed (skipping npm install)" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Starting Development Server..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend URL: http://localhost:5173" -ForegroundColor Green
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start development server
npm run dev
