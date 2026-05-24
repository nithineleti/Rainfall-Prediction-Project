@echo off
REM Frontend Setup and Run Script for Watershed-UP
SETLOCAL EnableDelayedExpansion

echo.
echo =====================================
echo Watershed-UP Frontend Setup
echo =====================================
echo.

REM Add Node.js to PATH
set "PATH=C:\Program Files\nodejs;%PATH%"

REM Check Node.js installation
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js version:
node --version
echo.

echo [OK] npm version:
npm --version
echo.

REM Navigate to frontend directory
cd /d "%~dp0app-frontend"
if errorlevel 1 (
    echo [ERROR] Cannot find app-frontend directory
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM Check if package.json exists
if not exist "package.json" (
    echo [ERROR] package.json not found in %CD%
    pause
    exit /b 1
)

REM Install dependencies
if not exist "node_modules\" (
    echo [INFO] Installing dependencies... (this may take a few minutes)
    echo.
    call npm install
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed successfully!
) else (
    echo [OK] Dependencies already installed (skipping npm install)
)

echo.
echo =====================================
echo Starting Development Server...
echo =====================================
echo.
echo Frontend URL: http://localhost:5173
echo Backend API:  http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start development server
call npm run dev

pause
