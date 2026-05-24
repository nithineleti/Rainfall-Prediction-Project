# Path Verification Script for Watershed-UP Backend
# This script verifies all file paths used by the backend

Write-Host "=== WATERSHED-UP BACKEND PATH VERIFICATION ===" -ForegroundColor Cyan
Write-Host ""

# Define expected paths based on router configurations
$paths = @{
    "Raster Files (at PROJECT_ROOT)" = @(
        "outputs\predictions\predicted_grp_score.tif",
        "outputs\predictions\predicted_grp_class.tif",
        "data\rasters\ndvi_mean_lucknow.tif",
        "data\rasters\rain_mean_lucknow.tif",
        "data\rasters\lulc_lucknow.tif",
        "data\rasters\slope_lucknow.tif",
        "data\rasters\drainage_density_lucknow.tif",
        "data\rasters\dem_lucknow.tif",
        "data\rasters\twi_lucknow.tif"
    )
    "CSV Files (at PROJECT_ROOT)" = @(
        "data\tables\feature_importances.csv",
        "data\tables\cv_results.csv",
        "data\tables\watersheds_characterized.csv"
    )
    "Vector Files (at BACKEND_ROOT)" = @(
        "backend\data_demo\vectors\real_watersheds.geojson"
    )
}

$projectRoot = "G:\PROJECTS\watershed-up"
$allExist = $true

foreach ($category in $paths.Keys) {
    Write-Host "$category" -ForegroundColor Yellow
    Write-Host ("=" * 60)
    
    foreach ($relativePath in $paths[$category]) {
        $fullPath = Join-Path $projectRoot $relativePath
        $exists = Test-Path $fullPath
        
        if ($exists) {
            Write-Host "  OK " -ForegroundColor Green -NoNewline
            $fileSize = (Get-Item $fullPath).Length / 1MB
            $fileSizeStr = [Math]::Round($fileSize, 2)
            Write-Host "$relativePath ($fileSizeStr MB)"
        } else {
            Write-Host "  MISSING " -ForegroundColor Red -NoNewline
            Write-Host "$relativePath [NOT FOUND]"
            $allExist = $false
        }
    }
    Write-Host ""
}

# Summary
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
if ($allExist) {
    Write-Host "OK All required files exist!" -ForegroundColor Green
} else {
    Write-Host "MISSING Some files are missing!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Router Configuration:" -ForegroundColor Yellow
Write-Host "  - layers.py:      PROJECT_ROOT = Path(__file__).parent.parent.parent"
Write-Host "  - statistics.py:  PROJECT_ROOT = Path(__file__).parent.parent.parent"
Write-Host "  - watersheds.py:  BACKEND_ROOT = Path(__file__).parent.parent"
Write-Host "                    PROJECT_ROOT = BACKEND_ROOT.parent"
Write-Host "  - tiles.py:       PROJECT_ROOT = Path(__file__).parent.parent.parent"
Write-Host ""
Write-Host "Expected Resolutions:" -ForegroundColor Yellow
Write-Host "  - PROJECT_ROOT → G:\PROJECTS\watershed-up"
Write-Host "  - BACKEND_ROOT → G:\PROJECTS\watershed-up\backend"
