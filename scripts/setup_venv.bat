@echo off
REM ========================================
REM SETUP PYTHON VIRTUAL ENVIRONMENT
REM For Watershed-UP Project
REM ========================================

echo.
echo ========================================
echo WATERSHED-UP ENVIRONMENT SETUP
echo ========================================
echo.

REM Step 1: Deactivate conda if active
echo [1/6] Checking for active conda environment...
call conda deactivate 2>nul
echo    Done

REM Step 2: Remove old conda environment
echo.
echo [2/6] Removing old conda environment 'watershed-up'...
call conda env remove -n watershed-up -y 2>nul
echo    Done

REM Step 3: Check Python version
echo.
echo [3/6] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo    ERROR: Python not found in PATH!
    echo    Please install Python 3.10 or 3.11 from python.org
    pause
    exit /b 1
)

REM Step 4: Create virtual environment
echo.
echo [4/6] Creating Python virtual environment...
if exist .venv (
    echo    Removing existing .venv folder...
    rmdir /s /q .venv
)
python -m venv .venv
echo    Virtual environment created: .venv

REM Step 5: Activate and upgrade pip
echo.
echo [5/6] Activating environment and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
echo    Pip upgraded

REM Step 6: Install dependencies
echo.
echo [6/6] Installing dependencies...
echo.
echo ========================================
echo IMPORTANT WINDOWS INSTALLATION NOTES:
echo ========================================
echo.
echo For GDAL/Rasterio/Fiona on Windows:
echo.
echo Option 1 - Use precompiled wheels (RECOMMENDED):
echo   1. Download wheels from: https://www.lfd.uci.edu/~gohlke/pythonlibs/
echo   2. Download: GDAL, rasterio, Fiona (match your Python version)
echo   3. Install in order:
echo      pip install GDAL-*.whl
echo      pip install rasterio-*.whl
echo      pip install Fiona-*.whl
echo   4. Then run: pip install -r requirements_venv.txt
echo.
echo Option 2 - Use OSGeo4W (Alternative):
echo   1. Install OSGeo4W from: https://trac.osgeo.org/osgeo4w/
echo   2. Then run: pip install -r requirements_venv.txt
echo.
echo ========================================
echo.

set /p choice="Install dependencies now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Installing packages...
    pip install -r requirements_venv.txt
    echo.
    echo ========================================
    echo INSTALLATION COMPLETE!
    echo ========================================
) else (
    echo.
    echo Skipping automatic installation.
    echo Run manually: pip install -r requirements_venv.txt
)

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo To activate environment:
echo    .venv\Scripts\activate
echo.
echo To deactivate:
echo    deactivate
echo.
echo To verify installation:
echo    python -c "import geopandas, rasterio, streamlit; print('All good!')"
echo.
pause
