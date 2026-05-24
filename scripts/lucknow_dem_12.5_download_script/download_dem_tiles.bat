@echo off
REM Download ALOS PALSAR 12.5m DEM tiles for Lucknow

echo ========================================
echo Downloading ALOS PALSAR DEM tiles (12.5m)
echo ========================================
echo.
echo This will download 10 DEM tiles (~500MB each)
echo Total size: ~5 GB
echo Download location: data\raw\alos_dem_tiles
echo.
pause

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Change to download directory
cd data\raw\alos_dem_tiles

REM Run download script
python ..\..\..\scripts\lucknow_dem_12.5_download_script\download-all-2025-11-01_18-12-34.py

echo.
echo ========================================
echo Download complete!
echo ========================================
echo.
echo Next step: Run mosaic and clip script
echo Command: python scripts\lucknow_dem_12.5_download_script\mosaic_and_clip_dem.py
echo.
pause
