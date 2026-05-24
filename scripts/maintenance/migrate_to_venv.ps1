# ========================================
# MIGRATE FROM CONDA TO PYTHON VENV
# Watershed-UP Project
# ========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " CONDA TO VENV MIGRATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Deactivate conda
Write-Host "[1/7] Deactivating conda environment..." -ForegroundColor Yellow
conda deactivate 2>$null
Write-Host "   ✓ Done`n" -ForegroundColor Green

# Step 2: Remove conda environment
Write-Host "[2/7] Removing conda environment 'watershed-up'..." -ForegroundColor Yellow
$removeEnv = Read-Host "   Remove conda environment? (y/n)"
if ($removeEnv -eq 'y') {
    conda env remove -n watershed-up -y
    Write-Host "   ✓ Conda environment removed`n" -ForegroundColor Green
} else {
    Write-Host "   ⊘ Skipped (keeping conda env for rollback)`n" -ForegroundColor Yellow
}

# Step 3: Check Python
Write-Host "[3/7] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Python not found!" -ForegroundColor Red
    Write-Host "`nPlease install Python 3.10 or 3.11:" -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/`n" -ForegroundColor Yellow
    exit 1
}
Write-Host "   ✓ Found: $pythonVersion`n" -ForegroundColor Green

# Step 4: Create virtual environment
Write-Host "[4/7] Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "   ! .venv folder exists" -ForegroundColor Yellow
    $removeVenv = Read-Host "   Remove existing .venv? (y/n)"
    if ($removeVenv -eq 'y') {
        Remove-Item -Path ".venv" -Recurse -Force
        Write-Host "   ✓ Removed old .venv" -ForegroundColor Green
    }
}

python -m venv .venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Virtual environment created: .venv`n" -ForegroundColor Green
} else {
    Write-Host "   ✗ Failed to create virtual environment`n" -ForegroundColor Red
    exit 1
}

# Step 5: Activate and upgrade pip
Write-Host "[5/7] Activating environment and upgrading pip..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel --quiet
Write-Host "   ✓ Pip upgraded`n" -ForegroundColor Green

# Step 6: GDAL Installation Guide
Write-Host "[6/7] GDAL/Geospatial Libraries Installation..." -ForegroundColor Yellow
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " IMPORTANT: WINDOWS GDAL INSTALLATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "GDAL must be installed BEFORE other packages on Windows.`n" -ForegroundColor Yellow

Write-Host "Option 1 - Precompiled Wheels (RECOMMENDED):" -ForegroundColor Green
Write-Host "  1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/" -ForegroundColor White
Write-Host "  2. Download wheels matching your Python version:" -ForegroundColor White
Write-Host "     - GDAL-3.4.3-cp310-cp310-win_amd64.whl (for Python 3.10)" -ForegroundColor Gray
Write-Host "     - rasterio-1.3.9-cp310-cp310-win_amd64.whl" -ForegroundColor Gray
Write-Host "     - Fiona-1.9.5-cp310-cp310-win_amd64.whl" -ForegroundColor Gray
Write-Host "  3. Install in order:" -ForegroundColor White
Write-Host "     pip install GDAL-*.whl" -ForegroundColor Gray
Write-Host "     pip install rasterio-*.whl" -ForegroundColor Gray
Write-Host "     pip install Fiona-*.whl`n" -ForegroundColor Gray

Write-Host "Option 2 - Try pip (may fail on Windows):" -ForegroundColor Yellow
Write-Host "  pip install GDAL rasterio Fiona`n" -ForegroundColor Gray

$gdalChoice = Read-Host "Have you installed GDAL wheels? (y/n/skip)"

if ($gdalChoice -eq 'y') {
    Write-Host "   ✓ GDAL ready, proceeding with installation`n" -ForegroundColor Green
} elseif ($gdalChoice -eq 'skip') {
    Write-Host "   ⊘ Skipping GDAL check (installation may fail)`n" -ForegroundColor Yellow
} else {
    Write-Host "`n   ⊘ Please install GDAL wheels first, then run:" -ForegroundColor Yellow
    Write-Host "      pip install -r requirements_venv.txt`n" -ForegroundColor Cyan
    exit 0
}

# Step 7: Install dependencies
Write-Host "[7/7] Installing all dependencies..." -ForegroundColor Yellow
Write-Host "   This may take several minutes...`n" -ForegroundColor Gray

$installDeps = Read-Host "Install from requirements_venv.txt? (y/n)"
if ($installDeps -eq 'y') {
    pip install -r requirements_venv.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n   ✓ All dependencies installed!`n" -ForegroundColor Green
    } else {
        Write-Host "`n   ✗ Installation failed. Check errors above.`n" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   ⊘ Skipped. Run manually: pip install -r requirements_venv.txt`n" -ForegroundColor Yellow
}

# Verification
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " VERIFYING INSTALLATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Testing key imports..." -ForegroundColor Yellow

$imports = @(
    @{name="NumPy"; cmd="import numpy; print(numpy.__version__)"},
    @{name="Pandas"; cmd="import pandas; print(pandas.__version__)"},
    @{name="GeoPandas"; cmd="import geopandas; print(geopandas.__version__)"},
    @{name="Rasterio"; cmd="import rasterio; print(rasterio.__version__)"},
    @{name="Streamlit"; cmd="import streamlit; print(streamlit.__version__)"},
    @{name="Scikit-learn"; cmd="import sklearn; print(sklearn.__version__)"},
    @{name="SHAP"; cmd="import shap; print(shap.__version__)"}
)

$allGood = $true
foreach ($import in $imports) {
    try {
        $result = python -c $import.cmd 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ $($import.name): $result" -ForegroundColor Green
        } else {
            Write-Host "   ✗ $($import.name): Failed" -ForegroundColor Red
            $allGood = $false
        }
    } catch {
        Write-Host "   ✗ $($import.name): Error" -ForegroundColor Red
        $allGood = $false
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host " ✅ MIGRATION COMPLETE!" -ForegroundColor Green
} else {
    Write-Host " ⚠️  MIGRATION PARTIALLY COMPLETE" -ForegroundColor Yellow
}
Write-Host "========================================`n" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Activate environment: .venv\Scripts\activate" -ForegroundColor White
    Write-Host "  2. Test scripts: python scripts/ml/01_prepare_samples.py --help" -ForegroundColor White
    Write-Host "  3. Launch Streamlit: streamlit run app/main.py" -ForegroundColor White
    Write-Host "`nTo deactivate: deactivate`n" -ForegroundColor Gray
} else {
    Write-Host "Some packages failed to import. Check errors above." -ForegroundColor Red
    Write-Host "You may need to install GDAL wheels manually.`n" -ForegroundColor Yellow
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
