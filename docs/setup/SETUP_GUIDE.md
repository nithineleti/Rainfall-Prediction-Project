# ========================================
# WATERSHED-UP PROJECT SETUP GUIDE
# Python Virtual Environment (venv)
# ========================================

## Quick Start

### 1. Prerequisites
- Python 3.11 (recommended) or Python 3.10
- Git (for cloning repository)

### 2. Clone Repository
```powershell
git clone <your-repo-url>
cd watershed-up
```

### 3. Create Virtual Environment
```powershell
# Using Python 3.11 (recommended)
py -3.11 -m venv .venv

# OR using Python 3.10
py -3.10 -m venv .venv

# OR if you only have one Python version
python -m venv .venv
```

### 4. Activate Environment
```powershell
# PowerShell
.venv\Scripts\activate

# CMD
.venv\Scripts\activate.bat
```

### 5. Install Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all packages
pip install -r requirements.txt
```

### 6. Verify Installation
```powershell
python -c "import geopandas; import rasterio; import streamlit; print('✓ All packages OK!')"
```

### 7. Launch Streamlit Dashboard
```powershell
streamlit run app/main.py
```

## Project Structure

```
watershed-up/
├── .venv/                      # Virtual environment (created locally, not in git)
├── app/                        # Streamlit dashboard
├── data/                       # Data files (organize as needed)
│   ├── rasters/               # GeoTIFF files
│   ├── vectors/               # Shapefiles
│   ├── tables/                # CSV files
│   └── figures/               # Output plots
├── scripts/                    # Processing scripts
│   ├── preprocessing/         # Data preparation
│   ├── ml/                    # Machine learning
│   ├── watershed/             # Watershed analysis
│   └── visualization/         # Plotting
├── models/                     # Trained ML models
├── tests/                      # Unit tests
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Environment Management

### Activate
```powershell
.venv\Scripts\activate
```

### Deactivate
```powershell
deactivate
```

### Update Dependencies
```powershell
# After installing new packages
pip freeze > requirements.txt
```

### Recreate Environment
```powershell
# Remove old environment
Remove-Item -Recurse -Force .venv

# Create new
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Team Setup Instructions

When your team pulls the repository, they should:

1. **Check Python version:**
   ```powershell
   python --version
   # Should be 3.10.x or 3.11.x
   ```

2. **Create virtual environment:**
   ```powershell
   py -3.11 -m venv .venv
   ```

3. **Activate environment:**
   ```powershell
   .venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Run tests (optional):**
   ```powershell
   python -m pytest tests/
   ```

6. **Launch application:**
   ```powershell
   streamlit run app/main.py
   ```

## Common Issues

### Issue: "python not found"
**Solution:** Install Python 3.10 or 3.11 from [python.org](https://www.python.org/downloads/)

### Issue: "No module named 'rasterio'"
**Solution:**
```powershell
pip install rasterio
```

### Issue: GDAL/Rasterio errors on Windows
**Solution:**
Windows wheels are automatically installed from PyPI. If issues persist:
1. Download precompiled wheels from: https://www.lfd.uci.edu/~gohlke/pythonlibs/
2. Install manually: `pip install GDAL-*.whl`

### Issue: NumPy version conflicts
**Solution:**
```powershell
pip install "numpy<2.0" --force-reinstall
```

## Git Ignore

Make sure `.venv/` is in `.gitignore`:
```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ipynb_checkpoints/
```

## CI/CD Setup

Example GitHub Actions workflow:
```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          python -m venv .venv
          .venv\Scripts\activate
          pip install -r requirements.txt
          pytest tests/
```

## Migration from Conda

If you previously used conda:
1. ✅ Conda environment removed
2. ✅ Python 3.11 venv created
3. ✅ All packages installed
4. ✅ requirements.txt generated
5. ✅ Batch files updated

## Package Versions (Current)

- Python: 3.11.9
- NumPy: 1.26.4 (< 2.0 for compatibility)
- Pandas: 2.3.3
- GeoPandas: 1.1.1
- Rasterio: 1.4.3
- Streamlit: 1.51.0
- Scikit-learn: 1.7.2
- SHAP: 0.49.1

## Support

For issues or questions:
1. Check this guide
2. Review error messages
3. Search GitHub issues
4. Contact team lead
