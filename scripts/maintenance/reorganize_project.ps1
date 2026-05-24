# Project Reorganization Script
# Consolidates scattered files into clean structure

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "WATERSHED PROJECT REORGANIZATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Create new directory structure
Write-Host "[1/8] Creating new directory structure..." -ForegroundColor Yellow

$newDirs = @(
    "data/rasters",
    "data/vectors",
    "data/tables",
    "data/figures",
    "outputs/reports",
    "outputs/predictions",
    "scripts/preprocessing",
    "scripts/analysis",
    "scripts/watershed",
    "scripts/ml",
    "scripts/utilities",
    "scripts/qgis",
    "docs/archive",
    "docs/methodology",
    "docs/results",
    "docs/guides"
)

foreach ($dir in $newDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    }
}

# Move rasters from stage3/stage4 to data/rasters/
Write-Host "`n[2/8] Consolidating raster files..." -ForegroundColor Yellow

$rasterMoves = @{
    # Stage 3 rasters
    "data/processed/stage3/flow_acc_lucknow.tif" = "data/rasters/flow_acc_lucknow.tif"
    "data/processed/stage3/stream_network_lucknow.tif" = "data/rasters/stream_network_lucknow.tif"
    "data/processed/stage3/drainage_density_lucknow.tif" = "data/rasters/drainage_density_lucknow.tif"
    "data/processed/stage3/twi_lucknow.tif" = "data/rasters/twi_lucknow.tif"
    "data/processed/stage3/aspect_lucknow.tif" = "data/rasters/aspect_lucknow.tif"
    "data/processed/stage3/plan_curvature_lucknow.tif" = "data/rasters/plan_curvature_lucknow.tif"
    "data/processed/stage3/profile_curvature_lucknow.tif" = "data/rasters/profile_curvature_lucknow.tif"
    "data/processed/stage3/tpi_lucknow.tif" = "data/rasters/tpi_lucknow.tif"
    "data/processed/stage3/distance_to_stream_lucknow.tif" = "data/rasters/distance_to_stream_lucknow.tif"
    "data/processed/stage3/ndvi_mean_lucknow.tif" = "data/rasters/ndvi_lucknow.tif"
    "data/processed/stage3/features_stack.tif" = "data/rasters/features_stack.tif"
    "data/processed/stage3/features_stack_bands.csv" = "data/rasters/features_stack_bands.csv"
    
    # Root rasters
    "data/processed/dem_lucknow.tif" = "data/rasters/dem_lucknow.tif"
    "data/processed/slope_lucknow.tif" = "data/rasters/slope_lucknow.tif"
    "data/processed/hillshade_lucknow.tif" = "data/rasters/hillshade_lucknow.tif"
    "data/processed/lulc_lucknow.tif" = "data/rasters/lulc_lucknow.tif"
    "data/processed/rain_mean_lucknow.tif" = "data/rasters/rainfall_lucknow.tif"
    "data/processed/ndvi_lucknow.tif" = "data/rasters/ndvi_lucknow.tif"
    "data/processed/grp_score_lucknow.tif" = "data/rasters/gwp_ahp_lucknow.tif"
    "data/processed/grp_class_lucknow.tif" = "data/rasters/gwp_ahp_class_lucknow.tif"
}

foreach ($src in $rasterMoves.Keys) {
    $dst = $rasterMoves[$src]
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  ✓ Copied: $(Split-Path $dst -Leaf)" -ForegroundColor Green
    }
}

# Copy auxiliary files (.aux.xml)
Get-ChildItem "data/processed/*.tif.aux.xml" | ForEach-Object {
    $newName = $_.Name -replace "rain_mean", "rainfall" -replace "grp_score", "gwp_ahp" -replace "grp_class", "gwp_ahp_class"
    Copy-Item $_.FullName "data/rasters/$newName" -Force
}

# Move ML predictions
if (Test-Path "data/processed/predicted_grp_score.tif") {
    Copy-Item -Recurse "data/processed/predicted_grp_score.tif/*" "outputs/predictions/" -Force
    Write-Host "  ✓ Moved ML predictions" -ForegroundColor Green
}

# Move vector files
Write-Host "`n[3/8] Consolidating vector files..." -ForegroundColor Yellow

$vectorMoves = @{
    "data/processed/stage4/watersheds_grid.shp" = "data/vectors/watersheds_grid.shp"
    "data/processed/stage4/watersheds_characterized.shp" = "data/vectors/watersheds_characterized.shp"
    "data/processed/stage4/watersheds_prioritized.shp" = "data/vectors/watersheds_prioritized.shp"
}

foreach ($src in $vectorMoves.Keys) {
    $dst = $vectorMoves[$src]
    if (Test-Path $src) {
        # Copy shapefile and all associated files (.dbf, .shx, .prj, etc.)
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($src)
        $srcDir = Split-Path $src
        $dstDir = Split-Path $dst
        
        Get-ChildItem "$srcDir/$baseName.*" | ForEach-Object {
            $newPath = Join-Path $dstDir $_.Name
            Copy-Item $_.FullName $newPath -Force
        }
        Write-Host "  ✓ Copied: $(Split-Path $dst -Leaf)" -ForegroundColor Green
    }
}

# Move CSV/table files
Write-Host "`n[4/8] Consolidating table files..." -ForegroundColor Yellow

$tableMoves = @{
    "data/processed/stage4/watersheds_characterized.csv" = "data/tables/watersheds_characterized.csv"
    "data/processed/stage4/watersheds_prioritized.csv" = "data/tables/watersheds_prioritized.csv"
    "data/processed/stage4/train_samples.csv" = "data/tables/train_samples.csv"
    "data/processed/stage4/feature_importances.csv" = "data/tables/feature_importances.csv"
    "data/processed/stage4/cv_results.csv" = "data/tables/cv_results.csv"
    "data/processed/stage4/priority_summary.txt" = "outputs/reports/priority_summary.txt"
}

foreach ($src in $tableMoves.Keys) {
    $dst = $tableMoves[$src]
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  ✓ Copied: $(Split-Path $dst -Leaf)" -ForegroundColor Green
    }
}

# Move reports
Write-Host "`n[5/8] Moving reports..." -ForegroundColor Yellow

if (Test-Path "data/processed/stage4/Executive_Summary.pdf") {
    Copy-Item "data/processed/stage4/Executive_Summary.pdf" "outputs/reports/" -Force
    Write-Host "  ✓ Moved: Executive_Summary.pdf" -ForegroundColor Green
}

if (Test-Path "data/processed/stage4/Watershed_Action_Plans.xlsx") {
    Copy-Item "data/processed/stage4/Watershed_Action_Plans.xlsx" "outputs/reports/" -Force
    Write-Host "  ✓ Moved: Watershed_Action_Plans.xlsx" -ForegroundColor Green
}

# Move figures
Write-Host "`n[6/8] Moving figures..." -ForegroundColor Yellow

if (Test-Path "data/processed/figs") {
    Copy-Item -Recurse "data/processed/figs/*" "data/figures/" -Force
    Write-Host "  ✓ Moved visualization figures" -ForegroundColor Green
}

if (Test-Path "data/processed/stage4/ml_training_summary.png") {
    Copy-Item "data/processed/stage4/ml_training_summary.png" "data/figures/" -Force
}

# Organize scripts
Write-Host "`n[7/8] Organizing Python scripts..." -ForegroundColor Yellow

# Preprocessing scripts
$preprocessingScripts = @{
    "src/preprocess.py" = "scripts/preprocessing/01_process_dem.py"
    "fix_slope_calculation.py" = "scripts/preprocessing/02_calculate_slope.py"
    "src/derive_drainage.py" = "scripts/preprocessing/03_calculate_drainage.py"
    "src/features_stack.py" = "scripts/preprocessing/04_create_feature_stack.py"
}

foreach ($src in $preprocessingScripts.Keys) {
    $dst = $preprocessingScripts[$src]
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  ✓ Moved: $(Split-Path $dst -Leaf)" -ForegroundColor Green
    }
}

# Analysis scripts
$analysisScripts = @{
    "src/ahp.py" = "scripts/analysis/ahp_basic.py"
    "src/ahp_with_rain.py" = "scripts/analysis/ahp_with_rainfall.py"
    "src/ahp_with_lulc.py" = "scripts/analysis/ahp_with_lulc.py"
}

foreach ($src in $analysisScripts.Keys) {
    $dst = $analysisScripts[$src]
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
    }
}

# Watershed scripts
$watershedScripts = @{
    "src/delineate_watersheds.py" = "scripts/watershed/delineate_watersheds.py"
    "src/characterize_watersheds.py" = "scripts/watershed/characterize_watersheds.py"
    "src/prioritize_watersheds.py" = "scripts/watershed/prioritize_watersheds.py"
    "src/generate_watershed_reports.py" = "scripts/watershed/generate_reports.py"
}

foreach ($src in $watershedScripts.Keys) {
    $dst = $watershedScripts[$src]
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
    }
}

# ML scripts
$mlScripts = @{
    "src/sample_wells.py" = "scripts/ml/prepare_samples.py"
    "src/train_model.py" = "scripts/ml/train_model.py"
    "src/predict_map.py" = "scripts/ml/predict_map.py"
}

foreach ($src in $mlScripts.Keys) {
    $dst = $mlScripts[$src]
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
    }
}

# QGIS scripts
$qgisScripts = @{
    "qgis_characterize_watersheds.py" = "scripts/qgis/characterize_watersheds.py"
}

foreach ($src in $qgisScripts.Keys) {
    $dst = $qgisScripts[$src]
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
    }
}

# Utility scripts
$utilityScripts = @{
    "extract_dbf_to_csv.py" = "scripts/utilities/extract_dbf_to_csv.py"
    "clean_qgis_output.py" = "scripts/utilities/clean_qgis_output.py"
    "verify_qgis_output.py" = "scripts/utilities/verify_qgis_output.py"
    "diagnose_slope.py" = "scripts/utilities/diagnose_slope.py"
    "debug_slope.py" = "scripts/utilities/debug_slope.py"
    "check_slope_stats.py" = "scripts/utilities/check_slope_stats.py"
}

foreach ($src in $utilityScripts.Keys) {
    $dst = $utilityScripts[$src]
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
    }
}

# Move documentation
Write-Host "`n[8/8] Organizing documentation..." -ForegroundColor Yellow

$docs = Get-ChildItem "*.md" | Where-Object { $_.Name -ne "README.md" }
foreach ($doc in $docs) {
    Copy-Item $doc.FullName "docs/archive/" -Force
}
Write-Host "  ✓ Moved $($docs.Count) markdown files to docs/archive/" -ForegroundColor Green

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "REORGANIZATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "✅ New Structure Created:" -ForegroundColor Green
Write-Host "  data/rasters/      - All raster files"
Write-Host "  data/vectors/      - Shapefiles"
Write-Host "  data/tables/       - CSV files"
Write-Host "  data/figures/      - Visualizations"
Write-Host "  outputs/reports/   - PDF & Excel reports"
Write-Host "  outputs/predictions/ - ML predictions"
Write-Host "  scripts/          - Organized Python scripts"
Write-Host "  docs/archive/     - Documentation"

Write-Host "`n📌 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review new structure"
Write-Host "  2. Update import paths in Python scripts"
Write-Host "  3. Test Streamlit dashboard"
Write-Host "  4. Clean up old stage folders (optional)"

Write-Host "`n⚠️  Note: Original files preserved for safety" -ForegroundColor Yellow
Write-Host "  After testing, you can delete:" -ForegroundColor Yellow
Write-Host "  - data/processed/stage3/"
Write-Host "  - data/processed/stage4/"
Write-Host "  - data/processed/stage5_quality_check/"
Write-Host "`n"
