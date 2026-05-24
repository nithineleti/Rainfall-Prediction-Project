@echo off
REM Complete workflow: Download, mosaic, clip ALOS PALSAR 12.5m DEM

echo ========================================
echo ALOS PALSAR 12.5m DEM Setup
echo ========================================
echo.
echo This script will:
echo   1. Download 10 DEM tiles from ASF (~5 GB)
echo   2. Extract all ZIP files
echo   3. Mosaic tiles into single raster
echo   4. Clip to Lucknow district boundary
echo   5. Save final DEM to data\raw\lucknow_dem_12.5\
echo.
echo Total time: ~30-60 minutes (depends on download speed)
echo.
pause

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM ========================================
REM Step 1: Download DEM tiles
REM ========================================
echo.
echo ========================================
echo [1/4] Downloading DEM tiles...
echo ========================================
cd data\raw\alos_dem_tiles
python ..\..\..\.scripts\lucknow_dem_12.5_download_script\download-all-2025-11-01_18-12-34.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Download failed!
    pause
    exit /b 1
)
cd ..\..\..

REM ========================================
REM Step 2: Extract ZIP files
REM ========================================
echo.
echo ========================================
echo [2/4] Extracting ZIP files...
echo ========================================
cd data\raw\alos_dem_tiles
for %%f in (*.zip) do (
    echo Extracting %%f...
    powershell -Command "Expand-Archive -Path '%%f' -DestinationPath '.' -Force"
)
cd ..\..\..

REM ========================================
REM Step 3: Mosaic and clip DEM
REM ========================================
echo.
echo ========================================
echo [3/4] Mosaicking and clipping DEM...
echo ========================================
python scripts\lucknow_dem_12.5_download_script\mosaic_and_clip_dem.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Mosaic/clip failed!
    pause
    exit /b 1
)

REM ========================================
REM Step 4: Verify output
REM ========================================
echo.
echo ========================================
echo [4/4] Verifying output...
echo ========================================
python -c "import rasterio; src = rasterio.open('data/raw/lucknow_dem_12.5/dem_lucknow_12.5.tif'); print(f'Resolution: {src.res[0]:.10f} degrees (~{111320 * abs(src.res[0]):.2f}m)'); print(f'Shape: {src.shape}'); print(f'Bounds: {src.bounds}'); print(f'CRS: {src.crs}')"

echo.
echo ========================================
echo SUCCESS! 12.5m DEM ready
echo ========================================
echo.
echo Output: data\raw\lucknow_dem_12.5\dem_lucknow_12.5.tif
echo.
echo Next step: Rerun the ML pipeline
echo Command: run_model.bat
echo.
pause
