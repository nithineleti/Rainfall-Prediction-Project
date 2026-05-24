# Batch File Guide - Which One to Use?

## ✅ CURRENT/ACTIVE Batch Files (Use These!)

### 1. **run_model.bat** ⭐ PRIMARY
**Location:** `G:\PROJECTS\watershed-up\run_model.bat`

**What it does:**
- Complete ML pipeline execution
- Uses NEW reorganized `scripts/` folder
- All paths corrected to use `path_config.py`

**Steps executed:**
1. Activate `.venv` environment
2. Process DEM (slope & hillshade) - 12.5m resolution
3. Create feature stack (14 bands)
4. Generate training samples (5,000)
5. Validate samples
6. Train Random Forest model
7. Generate predictions
8. Analyze model performance
9. Print summary

**Usage:**
```cmd
run_model.bat
```

**Duration:** ~5-10 minutes (with 12.5m DEM)

**Output Files:**
- Models: `models/rf_baseline.pkl`
- Samples: `data/tables/train_samples.csv`
- Results: `data/tables/cv_results.csv`, `feature_importances.csv`
- Predictions: `outputs/predictions/predicted_grp_*.tif`
- Figures: `data/figures/enhanced_model_results.png`

---

### 2. **setup_12.5m_dem.bat** (One-time use)
**Location:** `G:\PROJECTS\watershed-up\setup_12.5m_dem.bat`

**What it does:**
- Downloads ALOS PALSAR 12.5m DEM tiles
- Extracts ZIP files
- Mosaics tiles
- Clips to Lucknow boundary

**Usage:** (Already completed!)
```cmd
setup_12.5m_dem.bat
```

**Status:** ✅ Already run - 12.5m DEM ready at `data/raw/lucknow_dem_12.5/dem_lucknow_12.5.tif`

---

## ❌ DEPRECATED Batch Files (Do NOT use!)

### ❌ run_pipeline.bat (OLD)
**Why deprecated:**
- Uses old `src/` folder structure
- Hardcoded paths (not using `path_config.py`)
- Missing path imports in scripts
- References conda environment (deleted)
- Runs outdated workflow

**Error when run:**
```
ModuleNotFoundError: No module named 'path_config'
```

**Replacement:** Use `run_model.bat` instead

---

## 📁 Folder Structure Reference

### ✅ NEW Structure (Active)
```
scripts/
  ├── preprocessing/     # DEM, feature stack creation
  ├── ml/               # ML training, prediction, analysis
  ├── analysis/         # AHP, statistics
  └── visualization/    # Plotting scripts
```

### ❌ OLD Structure (Deprecated)
```
src/
  ├── preprocess.py
  ├── train_model.py
  ├── predict_map.py
  └── ... (30+ files with hardcoded paths)
```

---

## 🎯 Quick Start Guide

### To retrain the model:
```cmd
run_model.bat
```

### To launch the dashboard:
```cmd
streamlit run app/main.py
```

### To generate predictions only:
```cmd
.venv\Scripts\activate
python scripts\ml\04_predict_map.py --stack data\rasters\features_stack.tif --model models\rf_baseline.pkl
```

### To analyze model:
```cmd
.venv\Scripts\activate
python scripts\ml\06_analyze_enhanced_model.py
```

---

## ✅ Current Status

**DEM:**
- ✅ 12.5m ALOS PALSAR (30.3M pixels)
- ✅ Processed: slope, hillshade

**Features:**
- ✅ 14-band stack at 12.5m resolution
- ✅ Stream feature fixed (no more NaN)

**Model:**
- ✅ Trained: Random Forest (75.9% accuracy)
- ✅ Features: 13 inputs
- ✅ Predictions: 9.1M pixels

**Path Structure:**
- ✅ All scripts use `path_config.py`
- ✅ Files migrated to new locations
- ✅ No hardcoded paths

---

## 🚀 Next Steps

1. **Use `run_model.bat` for all ML pipeline operations** ✅
2. **Ignore/delete `run_pipeline.bat`** (outdated)
3. **Launch dashboard:** `streamlit run app/main.py`
4. **Commit changes to Git** (optional)

---

## 📝 Notes

- The `src/` folder is kept for backward compatibility but should NOT be used
- All active development uses `scripts/` folder
- All paths centralized in `path_config.py`
- Old `data/processed/stage3/` and `data/processed/stage4/` folders can be deleted (files already migrated)
