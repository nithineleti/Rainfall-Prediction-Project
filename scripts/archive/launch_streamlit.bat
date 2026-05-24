@echo off
REM Launch Streamlit Platform with UTF-8 encoding support
REM Fixes emoji/Unicode character display issues on Windows

echo.
echo ========================================
echo Launching GRPZ Streamlit Platform
echo ========================================
echo.
echo Platform will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate .venv environment
    echo Please run: py -3.11 -m venv .venv
    pause
    exit /b 1
)

REM Set UTF-8 encoding for Python I/O
set PYTHONIOENCODING=utf-8

REM Launch Streamlit
streamlit run app\main.py

pause
