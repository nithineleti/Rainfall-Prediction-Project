# Combined Environment Setup for Watershed-UP
# Activates Python venv AND adds Node.js to PATH

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Watershed-UP Environment Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Activate Python virtual environment
$venvPath = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "[1/2] Activating Python virtual environment..." -ForegroundColor Yellow
    & $venvPath
    Write-Host "[OK] Python venv activated" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python venv not found at: $venvPath" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Add Node.js to PATH
$nodePath = "C:\Program Files\nodejs"
if (Test-Path $nodePath) {
    Write-Host "[2/2] Adding Node.js to PATH..." -ForegroundColor Yellow
    $env:Path = "$nodePath;" + $env:Path
    Write-Host "[OK] Node.js added to PATH" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Node.js not found at: $nodePath" -ForegroundColor Yellow
    Write-Host "Frontend development may not work" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Environment Ready!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verify installations
Write-Host "Installed versions:" -ForegroundColor White
Write-Host "  Python: " -NoNewline -ForegroundColor Gray
python --version

Write-Host "  Node.js: " -NoNewline -ForegroundColor Gray
try {
    node --version
} catch {
    Write-Host "Not available" -ForegroundColor Red
}

Write-Host "  npm: " -NoNewline -ForegroundColor Gray
try {
    npm --version
} catch {
    Write-Host "Not available" -ForegroundColor Red
}

Write-Host ""
Write-Host "You can now run:" -ForegroundColor Cyan
Write-Host "  - Python scripts (backend, ML pipeline)" -ForegroundColor White
Write-Host "  - npm commands (frontend development)" -ForegroundColor White
Write-Host ""
