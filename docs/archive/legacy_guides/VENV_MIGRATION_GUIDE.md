# ========================================
# WATERSHED-UP: CONDA TO VENV MIGRATION GUIDE
# ========================================

## Current Status
- Using: conda environment 'watershed-up'
- Python: 3.10.19
- Key packages: geopandas, rasterio, streamlit

## Migration Steps

### 1. Remove Conda Environment

```powershell
# Deactivate current environment
conda deactivate

# Remove watershed-up environment
conda env remove -n watershed-up -y

# Verify removal
conda env list
```

### 2. Install Python (if not already installed)

**Option A: Python.org (Recommended)**
- Download: https://www.python.org/downloads/
- Version: Python 3.10.11 or 3.11.x
- ✅ Check "Add Python to PATH"
- Install for all users

**Option B: Microsoft Store**
- Search "Python 3.10" or "Python 3.11"
- Install from Microsoft Store

**Verify installation:**
```powershell
python --version
# Should show: Python 3.10.x or 3.11.x
```

### 3. Create Virtual Environment

```powershell
# Navigate to project directory
cd G:\PROJECTS\watershed-up

# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel
```

### 4. Install GDAL/Geospatial Libraries (Windows)

**⚠️ CRITICAL: Install GDAL FIRST on Windows**

**Method 1: Precompiled Wheels (EASIEST)**

1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/

2. Download wheels for your Python version:
   - Search for: `GDAL`
   - Download: `GDAL-3.4.3-cp310-cp310-win_amd64.whl` (for Python 3.10)
   - Search for: `rasterio`
   - Download: `rasterio-1.3.9-cp310-cp310-win_amd64.whl`
   - Search for: `Fiona`
   - Download: `Fiona-1.9.5-cp310-cp310-win_amd64.whl`

3. Install in order:
   ```powershell
   pip install GDAL-3.4.3-cp310-cp310-win_amd64.whl
   pip install rasterio-1.3.9-cp310-cp310-win_amd64.whl
   pip install Fiona-1.9.5-cp310-cp310-win_amd64.whl
   ```

**Method 2: OSGeo4W (Alternative)**

1. Download OSGeo4W: https://trac.osgeo.org/osgeo4w/
2. Install with GDAL, PROJ, GEOS
3. Add to PATH: `C:\OSGeo4W64\bin`

### 5. Install All Dependencies

```powershell
# Install from requirements file
pip install -r requirements_venv.txt
```

### 6. Verify Installation

```powershell
# Test imports
python -c "import geopandas; print('GeoPandas OK')"
python -c "import rasterio; print('Rasterio OK')"
python -c "import streamlit; print('Streamlit OK')"
python -c "import sklearn; print('Scikit-learn OK')"
python -c "import shap; print('SHAP OK')"

# Check versions
pip list | findstr "geopandas rasterio streamlit numpy pandas"
```

### 7. Update Scripts (if needed)

All scripts should work without changes. The activation command changes:

**Old (conda):**
```powershell
conda activate watershed-up
```

**New (venv):**
```powershell
.venv\Scripts\activate
```

### 8. Update Batch Files

**Files to update:**
- `run_model.bat`
- `run_pipeline.bat`
- `launch_streamlit.bat`

**Change:**
```batch
# Old
call conda activate watershed-up

# New
call .venv\Scripts\activate.bat
```

## Quick Setup (Automated)

Run the setup script:
```powershell
.\setup_venv.bat
```

This will:
1. Remove conda environment
2. Create .venv
3. Upgrade pip
4. Guide you through GDAL installation
5. Install all dependencies

## Troubleshooting

### Issue: "Python not found"
**Solution:** Install Python 3.10/3.11 and add to PATH

### Issue: "GDAL wheel not compatible"
**Solution:** Match wheel to Python version:
- `cp310` = Python 3.10
- `cp311` = Python 3.11
- `win_amd64` = 64-bit Windows

### Issue: "ImportError: DLL load failed"
**Solution:** 
1. Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Reinstall GDAL wheel

### Issue: "numpy version conflict"
**Solution:**
```powershell
pip install "numpy>=1.24.0,<2.0.0" --force-reinstall
```

## Advantages of venv over conda

✅ **Faster**: No environment solver overhead
✅ **Lighter**: Smaller disk footprint
✅ **Standard**: Native Python, no extra tools
✅ **Portable**: Works with standard pip/PyPI
✅ **Compatible**: Better IDE integration

## Environment Activation

**Activate:**
```powershell
.venv\Scripts\activate
```

**Deactivate:**
```powershell
deactivate
```

**Verify active:**
```powershell
where python
# Should show: G:\PROJECTS\watershed-up\.venv\Scripts\python.exe
```

## File Structure After Migration

```
watershed-up/
├── .venv/                      # Virtual environment (NEW)
│   ├── Scripts/
│   │   ├── activate.bat
│   │   ├── python.exe
│   │   └── pip.exe
│   └── Lib/
├── requirements_venv.txt       # Dependencies (NEW)
├── setup_venv.bat             # Setup script (NEW)
├── environment.yml            # OLD - can delete
└── ml/conda_env.yml           # OLD - can delete
```

## Next Steps After Migration

1. ✅ Activate new environment: `.venv\Scripts\activate`
2. ✅ Test scripts: `python scripts/ml/01_prepare_samples.py --help`
3. ✅ Launch Streamlit: `streamlit run app/main.py`
4. ✅ Run ML pipeline: Check all scripts work
5. ✅ Delete old conda files: `environment.yml`, `ml/conda_env.yml`

## Rollback (if needed)

If migration fails:
```powershell
# Recreate conda environment
conda env create -f environment.yml
conda activate watershed-up
```
