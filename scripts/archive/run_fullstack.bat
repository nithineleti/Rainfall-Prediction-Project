@echo off
REM =========================================
REM Watershed-UP Full-Stack Startup Script
REM =========================================

echo.
echo =========================================
echo Watershed-UP Full-Stack Launcher
echo =========================================
echo.

REM Check backend venv
if not exist "backend\.venv\Scripts\python.exe" (
    echo [ERROR] Backend virtual environment not found!
    echo Please run: cd backend ^&^& python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check frontend node_modules
if not exist "app-frontend\node_modules" (
    echo [ERROR] Frontend dependencies not installed!
    echo Please run: cd app-frontend ^&^& npm install
    pause
    exit /b 1
)

echo [1/2] Starting Backend Server (FastAPI)...
echo       URL: http://localhost:8000
echo       Docs: http://localhost:8000/docs
echo.

REM Start backend in new window
start "Watershed-UP Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server (Vite + React)...
echo       URL: http://localhost:5173
echo.

REM Start frontend in new window
set "PATH=C:\Program Files\nodejs;%PATH%"
start "Watershed-UP Frontend" cmd /k "cd /d %~dp0app-frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo =========================================
echo Full-Stack Environment Starting
echo =========================================
echo.
echo Access your application:
echo   Frontend:   http://localhost:5173
echo   Backend:    http://localhost:8000
echo   API Docs:   http://localhost:8000/docs
echo   Health:     http://localhost:8000/health
echo.
echo Endpoints:
echo   GET  /api/watersheds          - Watershed GeoJSON
echo   GET  /tiles/demo/{z}/{x}/{y}  - Demo raster tiles
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
