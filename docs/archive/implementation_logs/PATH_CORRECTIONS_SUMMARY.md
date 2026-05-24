# File Path Corrections Applied

## Summary
Updated all ML and visualization scripts to use centralized path_config.py instead of hardcoded paths.

## Changes Made

### 1. ML Scripts Updated:
- **scripts/ml/01_prepare_samples.py** ✅
  - Changed: `OUT_DIR_DEFAULT = "data/processed/stage4"` → `str(TABLES_DIR)`
  - Now saves to: `data/tables/train_samples.csv`

- **scripts/ml/03_train_model.py** ✅  
  - Changed: `DEFAULT_OUT = "data/processed/stage4"` → `OUTPUT_TABLES` and `OUTPUT_FIGURES`
  - CV results: `data/tables/cv_results.csv`
  - Feature importances: `data/tables/feature_importances.csv`
  - Confusion matrix: `data/figures/confusion_matrix.png`
  - Classification report: `data/figures/classification_report.txt`

- **scripts/ml/04_predict_map.py** ✅
  - Changed: `default="data/processed/stage4"` → `default=str(PREDICTIONS_DIR)`
  - Now uses: `TRAIN_SAMPLES_CSV`, `FEATURES_BANDS_CSV`
  - Predictions save to: `outputs/predictions/predicted_grp_*.tif`

- **scripts/ml/06_analyze_enhanced_model.py** ✅
  - Now reads from: `FEATURE_IMPORTANCE_CSV`, `CV_RESULTS_CSV`
  - Saves figures to: `FIGURES_DIR/enhanced_model_results.png`

- **scripts/ml/08_print_ml_summary.py** ✅
  - Updated to use: `FEATURE_IMPORTANCE_CSV`, `CV_RESULTS_CSV`, `TRAIN_SAMPLES_CSV`

- **scripts/ml/09_final_summary.py** ✅
  - Updated paths in output messages to use `PREDICTIONS_DIR` and `FIGURES_DIR`

### 2. Path Structure (from path_config.py):

**OLD Structure:**
```
data/processed/
  ├── stage3/  (features_stack.tif, rasters, figs/)
  └── stage4/  (train_samples.csv, cv_results.csv, predictions/)
```

**NEW Structure:**
```
data/
  ├── rasters/         # All feature rasters + stack
  ├── tables/          # CSV files (samples, CV results, importances)
  ├── figures/         # PNG plots, confusion matrix
  └── raw/             # Original input data

outputs/
  ├── predictions/     # ML prediction TIFFs
  └── reports/         # PDF/XLSX reports

models/
  └── rf_baseline.pkl  # Trained models
```

### 3. Files Still Using Old Paths (TO FIX):

visualization scripts still reference:
- `data/processed/stage3/` for rasters (should use `data/rasters/`)
- `data/processed/stage4/` for predictions (should use `outputs/predictions/`)

### 4. Next Steps:

1. ✅ Move existing files from old locations to new:
   ```powershell
   # Move CSVs
   Move-Item data/processed/stage4/*.csv data/tables/
   
   # Move figures  
   Move-Item data/processed/stage4/figs/*.png data/figures/
   
   # Move predictions
   Move-Item data/processed/stage4/predicted_*.tif outputs/predictions/
   
   # Clean up old folders
   Remove-Item -Recurse data/processed/stage3
   Remove-Item -Recurse data/processed/stage4
   ```

2. Update visualization scripts
3. Test complete pipeline with new paths
4. Update run_model.bat to ensure all outputs go to correct locations

## Benefits:
- ✅ Single source of truth (path_config.py)
- ✅ Easier to maintain and update
- ✅ Clearer separation of data types
- ✅ Better organization for Git
- ✅ Follows best practices for data science projects
