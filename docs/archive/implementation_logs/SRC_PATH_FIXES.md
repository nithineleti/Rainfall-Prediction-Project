# Path Fixes Applied to src/ Files

## Date: November 2, 2025

This document tracks all path corrections made to legacy `src/` files to support `run_pipeline.bat`.

## Summary

Updated **10 files** in the `src/` directory to use `path_config.py` instead of hardcoded paths.

---

## Files Fixed

### 1. src/preprocess.py ✅
- **Added:** Python path setup (lines 13-18)
- **Changed:** Uses `RAW_DEM`, `DEM`, `SLOPE`, `HILLSHADE`, `RASTERS_DIR` from path_config
- **Impact:** Correctly processes DEM from `data/raw/lucknow_dem_12.5/` → outputs to `data/rasters/`

### 2. src/preprocess_lulc.py ✅
- **Added:** Python path setup (lines 9-13)
- **Changed:** Uses `DEM`, `RAW_LULC`, `RAW_DISTRICT_SHP`, `LULC` from path_config
- **Impact:** Correctly clips LULC to `data/rasters/lulc_lucknow.tif`

### 3. src/preprocess_rain.py ✅
- **Added:** Python path setup (lines 7-12)
- **Changed:** Uses `DEM`, `RAW_RAINFALL`, `RAW_DISTRICT_SHP`, `RAINFALL` from path_config
- **Impact:** Correctly processes rainfall to `data/rasters/rainfall_lucknow.tif`

### 4. src/preprocess_stage3.py ✅
- **Added:** Python path setup (lines 16-20)
- **Changed:** Uses `DEM`, `RAW_DISTRICT_SHP`, `RAW_GEOLOGY_SHP`, `RAW_NDVI`, `RASTERS_DIR`
- **Impact:** Outputs geology/NDVI to `data/rasters/`

### 5. src/ahp_with_rain.py ✅
- **Added:** Python path setup (lines 6-10)
- **Changed:** 
  - `IN_DIR = "data/processed"` → `IN_DIR = str(RASTERS_DIR)`
  - Uses `SLOPE`, `LULC`, `RAINFALL` from path_config
- **Impact:** Reads inputs from `data/rasters/`, outputs GRP score there

### 6. src/ahp.py ✅
- **Added:** Python path setup (lines 23-27)
- **Changed:**
  - `IN_DIR = "data/processed"` → `IN_DIR = str(RASTERS_DIR)`
  - Uses `SLOPE`, `LULC`, `RAINFALL` from path_config
- **Impact:** Multi-criteria AHP uses correct raster locations

### 7. src/ahp_with_lulc.py ✅
- **Added:** Python path setup (lines 11-15)
- **Changed:**
  - `IN_DIR = "data/processed"` → `IN_DIR = str(RASTERS_DIR)`
  - Uses `SLOPE`, `LULC` from path_config
- **Impact:** Slope + LULC overlay works correctly

### 8. src/derive_drainage.py ✅
- **Added:** Python path setup (lines 18-22)
- **Changed:**
  - `DEM = "data/processed/dem_lucknow.tif"` → `DEM = str(DEM)` from path_config
  - `OUT_DIR = "data/processed/stage3"` → `OUT_DIR = str(RASTERS_DIR)`
- **Impact:** Flow accumulation, streams, drainage density → `data/rasters/`

### 9. src/features_stack.py ✅
- **Added:** Python path setup (lines 13-17)
- **Changed:**
  - All hardcoded paths replaced with path_config imports
  - `OUT_DIR = "data/processed/stage3"` → `OUT_DIR = str(RASTERS_DIR)`
  - `OUT_BANDS = ...features_stack_bands.csv` → `str(TABLES_DIR)/features_bands.csv`
- **Impact:** 
  - Feature stack saved to `data/rasters/features_stack.tif`
  - Band metadata to `data/tables/features_bands.csv`

### 10. src/train_model.py ✅
- **Added:** Python path setup (lines 17-21)
- **Changed:**
  - `DEFAULT_OUT = "data/processed/stage4"` → `DEFAULT_OUT = str(TABLES_DIR)`
  - Added `DEFAULT_FIGURES = str(FIGURES_DIR)`
  - CV results → `data/tables/cv_results.csv`
  - Feature importances → `data/tables/feature_importances.csv`
  - Confusion matrix → `data/figures/confusion_matrix.png`
  - Classification report → `data/figures/classification_report.txt`
- **Impact:** ML outputs organized in new structure

### 11. src/clean_samples.py ✅
- **Added:** Python path setup (lines 5-9)
- **Changed:**
  - `infile = "data/processed/stage4/train_samples.csv"` → uses `TABLES_DIR`
  - `outfile = "data/processed/stage4/train_samples_clean.csv"` → uses `TABLES_DIR`
- **Impact:** Reads/writes samples from `data/tables/`

---

## Pattern Applied

All files follow this consistent pattern:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Then import from path_config
from path_config import DEM, RASTERS_DIR, TABLES_DIR, etc.
```

---

## Path Mapping (Old → New)

| Old Path | New Path | Purpose |
|----------|----------|---------|
| `data/processed/` | `data/rasters/` | All raster files |
| `data/processed/stage3/` | `data/rasters/` | Stage 3 outputs |
| `data/processed/stage4/` (CSV) | `data/tables/` | Training samples, CV results |
| `data/processed/stage4/` (PNG/TXT) | `data/figures/` | Plots, confusion matrices |
| `data/processed/lucknow_dem_clipped.tif` | `data/raw/lucknow_dem_12.5/dem_lucknow_12.5.tif` | DEM source |

---

## Remaining Hardcoded Paths

Some files in `src/` may still have hardcoded paths if they are not called by `run_pipeline.bat`. These include:

- `src/predict_map.py` - May need updating
- `src/compare_with_ahp.py` - May need updating  
- `src/shap_explain.py` - May need updating
- `src/visualize_stage3.py` - May need updating
- Other utility scripts not in main pipeline

**Recommendation:** Use `run_model.bat` instead, which uses the modern `scripts/` folder with all paths already corrected.

---

## Verification

To verify all paths are correct:

```powershell
# Search for any remaining hardcoded paths
Get-ChildItem src/*.py | Select-String -Pattern 'data/processed' | Where-Object { $_.Line -notmatch '#' }
```

---

## Notes

- All fixes maintain backward compatibility with command-line arguments
- The `path_config.py` approach provides a single source of truth for all paths
- Files are now consistent with the modern `scripts/` folder structure
- **12.5m ALOS PALSAR DEM** is now properly integrated (was 30m Copernicus)

---

## Next Steps

If errors occur with other `src/` files:

1. Add Python path setup (5 lines at top)
2. Import required paths from `path_config`
3. Update hardcoded strings to use imported constants
4. Test the script

Or simply use **`run_model.bat`** which uses the fully-corrected `scripts/` folder! ✅
