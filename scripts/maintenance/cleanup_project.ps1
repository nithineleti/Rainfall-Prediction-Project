################################################################################
# Watershed Project Cleanup Script
# Removes debug files, test files, unused data, and Python cache
# 
# Estimated space savings: ~900-1100 MB
# Run: .\cleanup_project.ps1
################################################################################

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Watershed Project Cleanup Utility" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Track space saved
$totalSize = 0

function Get-FolderSize {
    param([string]$path)
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        return $size
    }
    return 0
}

function Remove-ItemSafe {
    param(
        [string]$path,
        [string]$description
    )
    
    if (Test-Path $path) {
        $size = 0
        if (Test-Path $path -PathType Container) {
            $size = Get-FolderSize $path
        } else {
            $size = (Get-Item $path).Length
        }
        
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        
        if (-not (Test-Path $path)) {
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "[DELETED] $description ($sizeMB MB)" -ForegroundColor Green
            return $size
        } else {
            Write-Host "[FAILED] Could not delete: $description" -ForegroundColor Red
            return 0
        }
    } else {
        Write-Host "[SKIP] Not found: $description" -ForegroundColor Yellow
        return 0
    }
}

Write-Host "1. Removing debug and test files..." -ForegroundColor Cyan
$totalSize += Remove-ItemSafe "debug_stage3.py" "Debug script (debug_stage3.py)"
$totalSize += Remove-ItemSafe "debug_stage3_verbose.py" "Debug script (debug_stage3_verbose.py)"
$totalSize += Remove-ItemSafe "test_imports.py" "Test script (test_imports.py)"
$totalSize += Remove-ItemSafe "test_geopandas_minimal.py" "Test script (test_geopandas_minimal.py)"
$totalSize += Remove-ItemSafe "test_stage3_check.bat" "Test batch file (test_stage3_check.bat)"
$totalSize += Remove-ItemSafe "run_stage3.py" "Standalone Stage 3 script"
$totalSize += Remove-ItemSafe "streamlit_log.txt" "Streamlit log file"

Write-Host ""
Write-Host "2. Removing obsolete scripts..." -ForegroundColor Cyan
$totalSize += Remove-ItemSafe "run_pipeline_skip_stage3.bat" "Workaround script (skip_stage3.bat)"
$totalSize += Remove-ItemSafe "run_pipeline_skip_stage3.ps1" "Workaround script (skip_stage3.ps1)"
$totalSize += Remove-ItemSafe "check_environment.ps1" "Environment check script"
$totalSize += Remove-ItemSafe "launch_platform.bat" "Duplicate launcher"

Write-Host ""
Write-Host "3. Removing Python cache files..." -ForegroundColor Cyan
$totalSize += Remove-ItemSafe "src\__pycache__" "src/__pycache__"
$totalSize += Remove-ItemSafe "app\__pycache__" "app/__pycache__"
$totalSize += Remove-ItemSafe "app\pages\__pycache__" "app/pages/__pycache__"

Write-Host ""
Write-Host "4. Removing unused source files..." -ForegroundColor Cyan
$totalSize += Remove-ItemSafe "src\download_data.sh" "Shell download script"
$totalSize += Remove-ItemSafe "src\download_lulc.py" "LULC download script"
$totalSize += Remove-ItemSafe "src\check_data.py" "Data check script"
$totalSize += Remove-ItemSafe "src\check_lulc.py" "LULC check script"
$totalSize += Remove-ItemSafe "src\check_raster.py" "Raster check script"
$totalSize += Remove-ItemSafe "src\inspect_samples.py" "Sample inspection script"
$totalSize += Remove-ItemSafe "src\inspect_stack.py" "Stack inspection script"

Write-Host ""
Write-Host "5. Removing intermediate processed files..." -ForegroundColor Cyan
$totalSize += Remove-ItemSafe "data\processed\mosaic_dem.tif" "Mosaic DEM (intermediate)"
$totalSize += Remove-ItemSafe "data\processed\lucknow_dem_clipped.tif" "Clipped DEM (intermediate)"
$totalSize += Remove-ItemSafe "data\processed\hillshade_lucknow.tif" "Hillshade (visualization only)"

Write-Host ""
Write-Host "6. Removing redundant documentation..." -ForegroundColor Cyan
$totalSize += Remove-ItemSafe "TROUBLESHOOTING.md" "Old troubleshooting doc"
$totalSize += Remove-ItemSafe "STREAMLIT_LAUNCH.md" "Redundant Streamlit doc"

Write-Host ""
Write-Host "7. Removing temporary download script..." -ForegroundColor Cyan
$totalSize += Remove-ItemSafe "data\raw\download-all-2025-10-25_10-15-04.py" "Temporary download script"

Write-Host ""
Write-Host "8. Removing ALOS PALSAR data (LARGEST - not used in pipeline)..." -ForegroundColor Cyan
Write-Host "   Note: We use Copernicus DEM instead of ALOS PALSAR" -ForegroundColor Yellow

# ALOS PALSAR ZIP files
$totalSize += Remove-ItemSafe "data\raw\AP_07405_FBD_F0520_RT1.zip" "ALOS PALSAR ZIP 1"
$totalSize += Remove-ItemSafe "data\raw\AP_07405_FBD_F0530_RT1.zip" "ALOS PALSAR ZIP 2"
$totalSize += Remove-ItemSafe "data\raw\AP_08324_FBD_F0510_RT1.zip" "ALOS PALSAR ZIP 3"
$totalSize += Remove-ItemSafe "data\raw\AP_08324_FBD_F0520_RT1.zip" "ALOS PALSAR ZIP 4"
$totalSize += Remove-ItemSafe "data\raw\AP_08324_FBD_F0530_RT1.zip" "ALOS PALSAR ZIP 5"
$totalSize += Remove-ItemSafe "data\raw\AP_08572_FBD_F0520_RT1.zip" "ALOS PALSAR ZIP 6"
$totalSize += Remove-ItemSafe "data\raw\AP_11788_FBS_F3070_RT1.zip" "ALOS PALSAR ZIP 7"
$totalSize += Remove-ItemSafe "data\raw\AP_11788_FBS_F3080_RT1.zip" "ALOS PALSAR ZIP 8"
$totalSize += Remove-ItemSafe "data\raw\AP_12350_FBD_F0520_RT1.zip" "ALOS PALSAR ZIP 9"
$totalSize += Remove-ItemSafe "data\raw\AP_12350_FBD_F0530_RT1.zip" "ALOS PALSAR ZIP 10"

# ALOS PALSAR extracted folders
$totalSize += Remove-ItemSafe "data\raw\AP_07405_FBD_F0520_RT1" "ALOS PALSAR Folder 1"
$totalSize += Remove-ItemSafe "data\raw\AP_07405_FBD_F0530_RT1" "ALOS PALSAR Folder 2"
$totalSize += Remove-ItemSafe "data\raw\AP_08324_FBD_F0510_RT1" "ALOS PALSAR Folder 3"
$totalSize += Remove-ItemSafe "data\raw\AP_08324_FBD_F0520_RT1" "ALOS PALSAR Folder 4"
$totalSize += Remove-ItemSafe "data\raw\AP_08324_FBD_F0530_RT1" "ALOS PALSAR Folder 5"
$totalSize += Remove-ItemSafe "data\raw\AP_08572_FBD_F0520_RT1" "ALOS PALSAR Folder 6"
$totalSize += Remove-ItemSafe "data\raw\AP_11788_FBS_F3070_RT1" "ALOS PALSAR Folder 7"
$totalSize += Remove-ItemSafe "data\raw\AP_11788_FBS_F3080_RT1" "ALOS PALSAR Folder 8"
$totalSize += Remove-ItemSafe "data\raw\AP_12350_FBD_F0520_RT1" "ALOS PALSAR Folder 9"
$totalSize += Remove-ItemSafe "data\raw\AP_12350_FBD_F0530_RT1" "ALOS PALSAR Folder 10"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$totalMB = [math]::Round($totalSize / 1MB, 2)
$totalGB = [math]::Round($totalSize / 1GB, 2)

Write-Host "Total space freed: $totalMB MB ($totalGB GB)" -ForegroundColor Green
Write-Host ""
Write-Host "Project is now clean and thesis-ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Essential files retained:" -ForegroundColor Cyan
Write-Host "  - All source scripts (src/)" -ForegroundColor White
Write-Host "  - Streamlit app (app/)" -ForegroundColor White
Write-Host "  - Pipeline automation (run_pipeline.*)" -ForegroundColor White
Write-Host "  - Essential raw data (DEM, LULC, rainfall, wells)" -ForegroundColor White
Write-Host "  - All processed outputs (stage3, stage4, stage5)" -ForegroundColor White
Write-Host "  - Trained model (models/rf_baseline.pkl)" -ForegroundColor White
Write-Host "  - Documentation (docs/, README.md)" -ForegroundColor White
Write-Host ""
Write-Host "Run 'run_pipeline.bat' to regenerate any intermediate files if needed." -ForegroundColor Yellow
Write-Host ""
