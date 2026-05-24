# How to Run the Watershed Groundwater Potential Model - End to End

This guide walks you through running the complete ML pipeline from raw data to predictions.

## Quick Start (Automated)

### Option 1: Run Complete Pipeline (Recommended)
```bash
# Activate environment
conda activate watershed-up

# Run automated pipeline (all 7 stages)
python run_complete_pipeline.py
```

### Option 2: Manual Step-by-Step (for debugging/customization)
See "Manual Execution" section below.

---

## Prerequisites

### 1. Activate Conda Environment
```bash
conda activate watershed-up
```

### 2. Verify Required Files Exist
```bash
# Check raw data files
dir data\raw\DEM\*.tif
dir data\raw\lulc\*.tif
dir data\raw\rainfall\*.tif

# Check AHP output (grp_score baseline)
dir data\processed\stage2\grp_score.tif
```

---

## Automated Pipeline Execution

### Run Complete Pipeline
```bash
python run_complete_pipeline.py
```

**What it does:**
1. ✅ **Enhanced Watershed Features** - Derives TWI, TPI, dist_stream, curvatures, aspect
2. ✅ **Feature Stack** - Combines all 13 features into single multi-band raster
3. ✅ **Training Samples** - Generates 2,000 synthetic samples from stack
4. ✅ **Data Cleaning** - Removes NaN, imputes missing values
5. ✅ **Model Training** - Trains Random Forest with 5-fold spatial CV
6. ✅ **Predictions** - Generates probability and classification maps
7. ✅ **Visualizations** - Creates impact analysis figures

**Expected Output:**
```
========================================
STAGE 1: Enhanced Watershed Features
========================================
✓ All 6 enhanced features already exist
...
========================================
PIPELINE COMPLETE!
========================================
Total time: ~15-20 minutes
```

**Output Files:**
- Model: `data/processed/stage4/rf_baseline.pkl`
- Predictions: `data/processed/stage4/predicted_grp_*.tif`
- Figures: `data/processed/stage4/figs/*.png`

---

## Manual Execution (Step-by-Step)

### Stage 1: Generate Enhanced Watershed Features

**Purpose:** Derive hydrologically-relevant features from DEM

```bash
python src/enhance_watershed_features.py
```

**Generates:**
- `data/processed/stage3/twi.tif` - Topographic Wetness Index
- `data/processed/stage3/tpi.tif` - Topographic Position Index
- `data/processed/stage3/dist_stream.tif` - Distance to stream
- `data/processed/stage3/plan_curv.tif` - Plan curvature
- `data/processed/stage3/prof_curv.tif` - Profile curvature
- `data/processed/stage3/aspect.tif` - Aspect

**Time:** ~5 minutes

---

### Stage 2: Create Feature Stack

**Purpose:** Combine all features into single multi-band raster

```bash
python src/features_stack.py
```

**Input Features:**
1. slope (from DEM)
2. lulc (land use)
3. rain (rainfall)
4. ndvi (vegetation index)
5. flow_acc (flow accumulation)
6. stream (stream network)
7. drainage_density
8. twi (enhanced)
9. aspect (enhanced)
10. plan_curv (enhanced)
11. prof_curv (enhanced)
12. tpi (enhanced)
13. dist_stream (enhanced)
14. grp_score (AHP baseline - **NOT used as feature, only for sampling**)

**Generates:**
- `data/processed/stage3/features_stack.tif` - 14-band stack
- `data/processed/stage3/features_stack_bands.csv` - Band mapping

**Time:** ~2 minutes

---

### Stage 3: Generate Training Samples

**Purpose:** Extract pixel values from feature stack for training

```bash
python src/sample_wells.py --stack data/processed/stage3/features_stack.tif --n 2000 --mode synthetic
```

**Parameters:**
- `--stack`: Path to feature stack
- `--n`: Number of samples (default: 2000)
- `--mode`: Sampling mode
  - `synthetic`: Random sampling across grp_score classes
  - `wells`: Use real well data (if available)

**Generates:**
- `data/processed/stage4/train_samples.csv` - 2,000 samples with all features

**Time:** ~1 minute

---

### Stage 4: Clean Training Data

**Purpose:** Handle missing values, remove outliers

```bash
python src/clean_samples.py
```

**What it does:**
- Removes rows with missing labels
- Imputes missing feature values (median strategy)
- Removes all-NaN columns

**Generates:**
- `data/processed/stage4/train_samples_clean.csv` - Clean dataset

**Time:** <1 minute

---

### Stage 5: Train Model

**Purpose:** Train Random Forest classifier with spatial cross-validation

```bash
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir data/processed/stage4 --cv_k 5 --n_estimators 200
```

**Parameters:**
- `--in`: Clean training samples CSV
- `--out_dir`: Output directory for model and results
- `--cv_k`: Number of cross-validation folds (default: 5)
- `--n_estimators`: Number of trees in forest (default: 200)

**Model Details:**
- **Algorithm:** Random Forest Classifier
- **Features:** 13 (grp_score excluded to prevent leakage)
- **Cross-Validation:** Spatial GroupKFold (KMeans clustering)
- **Performance:** ~89% accuracy, ~87% balanced accuracy

**Generates:**
- `data/processed/stage4/rf_baseline.pkl` - Trained model
- `data/processed/stage4/cv_results.csv` - Cross-validation scores
- `data/processed/stage4/feature_importances.csv` - Feature contributions

**Time:** ~3 minutes

**Expected Output:**
```
Fold 1: train=1526 test=474 acc=0.882 bal_acc=0.866
Fold 2: train=1575 test=425 acc=0.847 bal_acc=0.845
Fold 3: train=1606 test=394 acc=0.934 bal_acc=0.854
Fold 4: train=1640 test=360 acc=0.906 bal_acc=0.879
Fold 5: train=1653 test=347 acc=0.905 bal_acc=0.896
Saved final model: data/processed/stage4\rf_baseline.pkl
```

---

### Stage 6: Generate Predictions

**Purpose:** Apply trained model to entire study area

```bash
python src/predict_map.py --stack data/processed/stage3/features_stack.tif --model data/processed/stage4/rf_baseline.pkl --out_dir data/processed/stage4 --bands_csv data/processed/stage3/features_stack_bands.csv
```

**Parameters:**
- `--stack`: Feature stack raster
- `--model`: Trained model pickle file
- `--out_dir`: Output directory
- `--bands_csv`: Band name mapping

**Generates:**
- `data/processed/stage4/predicted_grp_score.tif` - Probability map (0-1)
- `data/processed/stage4/predicted_grp_class.tif` - Classification (1-5)

**Coverage:** 2,073,600 pixels (1440×1440)

**Time:** ~2 minutes

---

### Stage 7: Create Visualizations

**Purpose:** Generate impact analysis figures

```bash
python visualize_prediction_results.py
```

**Generates:**
- `data/processed/stage4/figs/enhanced_features_impact.png`
  - 9-panel visualization
  - Prediction maps
  - Feature importance bar chart
  - Key watershed features
  - Statistics summary

- `data/processed/stage4/figs/before_after_comparison.png`
  - Side-by-side: AHP vs ML predictions
  - Difference map
  - Histogram comparison

**Time:** ~1 minute

---

## Test Backend API (Optional)

### Start FastAPI Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access:**
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Run API Tests
```bash
python test_api.py
```

**Tests:**
1. Health check
2. Authentication (demo/demo123)
3. ML model endpoints
4. Job queue
5. AHP engine

---

## Understanding the Output

### Model Performance (Corrected - No Data Leakage)
```
Accuracy: 89.49%
Balanced Accuracy: 86.80%
Features: 13 (grp_score properly excluded)
```

### Feature Importance Breakdown
```
Top Features:
  rain:            27.15%  - Rainfall
  lulc:            26.75%  - Land use/cover
  ndvi:            11.03%  - Vegetation index
  slope:            6.46%  - Terrain slope

Enhanced Watershed Features (26.08% total):
  tpi:              4.84%  - Topographic Position Index
  twi:              4.78%  - Topographic Wetness Index
  dist_stream:      4.41%  - Distance to stream
  plan_curv:        4.22%  - Plan curvature
  prof_curv:        4.07%  - Profile curvature
  aspect:           3.77%  - Aspect
```

### Prediction Classes
```
Class 1: Very Low Potential
Class 2: Low Potential
Class 3: Moderate Potential
Class 4: High Potential
Class 5: Very High Potential
```

---

## Troubleshooting

### Issue: "Module not found" errors
**Solution:**
```bash
# Ensure you're in the watershed-up environment
conda activate watershed-up

# Reinstall dependencies if needed
pip install -r requirements.txt
```

### Issue: "File not found" errors
**Solution:**
```bash
# Check you're in the project root
cd G:\PROJECTS\watershed-up

# Verify data files exist
dir data\processed\stage3\*.tif
```

### Issue: Model accuracy seems too high (>95%)
**Solution:**
This was the data leakage bug! Check that `grp_score` is NOT in feature importances:
```bash
python -c "import pandas as pd; fi = pd.read_csv('data/processed/stage4/feature_importances.csv'); print(fi); assert 'grp_score' not in fi['feature'].values, 'Data leakage detected!'"
```

### Issue: Out of memory during prediction
**Solution:**
Reduce chunk size in `predict_map.py` (currently processes all pixels at once)

---

## File Locations Reference

### Input Data
- DEM: `data/raw/DEM/*.tif`
- LULC: `data/raw/lulc/*.tif`
- Rainfall: `data/raw/rainfall/*.tif`
- AHP Output: `data/processed/stage2/grp_score.tif`

### Intermediate Files
- Enhanced Features: `data/processed/stage3/twi.tif`, `tpi.tif`, etc.
- Feature Stack: `data/processed/stage3/features_stack.tif`
- Training Samples: `data/processed/stage4/train_samples_clean.csv`

### Output Files
- Model: `data/processed/stage4/rf_baseline.pkl`
- CV Results: `data/processed/stage4/cv_results.csv`
- Feature Importances: `data/processed/stage4/feature_importances.csv`
- Predictions: `data/processed/stage4/predicted_grp_*.tif`
- Figures: `data/processed/stage4/figs/*.png`

---

## Performance Metrics

### Training Time (typical)
- Enhanced Features: ~5 minutes
- Feature Stack: ~2 minutes
- Sampling: ~1 minute
- Cleaning: <1 minute
- Training: ~3 minutes
- Prediction: ~2 minutes
- Visualization: ~1 minute
**Total: ~15 minutes**

### Hardware Requirements
- RAM: 8GB minimum, 16GB recommended
- Storage: ~5GB for all data and outputs
- CPU: Multi-core recommended (parallel processing in Random Forest)

---

## Next Steps

### For Thesis
1. Review `DATA_LEAKAGE_FIX.md` - explains the bug fix
2. Use figures in `data/processed/stage4/figs/` for presentation
3. Report **89.49% accuracy** (corrected, not the leaked 95.63%)
4. Emphasize **26.08% watershed feature contribution**

### For Production Deployment
1. Start Docker stack: `docker-compose up -d`
2. Access API at http://localhost:8000
3. Use Streamlit app: `streamlit run app/main.py`

### For Further Development
1. Add more training samples from real well data
2. Tune hyperparameters (n_estimators, max_depth, etc.)
3. Experiment with other models (XGBoost, Neural Networks)
4. Add uncertainty quantification

---

## Quick Commands Summary

```bash
# Complete automated run
conda activate watershed-up
python run_complete_pipeline.py

# Manual run (all stages)
python src/enhance_watershed_features.py
python src/features_stack.py
python src/sample_wells.py --stack data/processed/stage3/features_stack.tif --n 2000 --mode synthetic
python src/clean_samples.py
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir data/processed/stage4 --cv_k 5 --n_estimators 200
python src/predict_map.py --stack data/processed/stage3/features_stack.tif --model data/processed/stage4/rf_baseline.pkl --out_dir data/processed/stage4 --bands_csv data/processed/stage3/features_stack_bands.csv
python visualize_prediction_results.py

# Test backend API
cd backend
uvicorn app.main:app --reload
# In another terminal:
python test_api.py
```

---

## Support

**For Issues:**
- Check `DATA_LEAKAGE_FIX.md` for known issues
- Review `PIPELINE_WORKING_SOLUTION.md` for troubleshooting
- Verify environment: `conda list` should show all required packages

**Documentation:**
- Architecture: `docs/ARCHITECTURE_OVERVIEW.md`
- API Guide: `docs/api/`
- Thesis Progress: `docs/thesis_progress_stage5.tex`
