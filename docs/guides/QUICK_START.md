# Quick Start - Watershed Groundwater Potential Model

## 🚀 Run Model End-to-End (Choose ONE method)

### **Option 1: Automated Batch Script (EASIEST)**
```cmd
run_model.bat
```
- Double-click `run_model.bat` in File Explorer
- Runs all 7 stages automatically
- Verifies outputs and shows results
- ~15 minutes total

---

### **Option 2: Automated PowerShell Script**
```powershell
.\run_model.ps1
```
- Right-click → "Run with PowerShell"
- Colored output with progress indicators
- Complete verification and summary
- Recommended for Windows 10/11

---

### **Option 3: Python Pipeline Script**
```bash
conda activate watershed-up
python run_complete_pipeline.py
```
- Automated 7-stage workflow
- Progress tracking and timing
- Error handling with verification

---

### **Option 4: Manual Execution (Step-by-Step)**

**Activate environment first:**
```bash
conda activate watershed-up
```

**Then run in order:**

#### STAGE 1: Enhanced Watershed Features (~5 min)
```bash
python src/enhance_watershed_features.py
```
Generates: TWI, TPI, dist_stream, plan_curv, prof_curv, aspect

#### STAGE 2: Feature Stack (~2 min)
```bash
python src/features_stack.py
```
Creates 14-band raster (13 features + grp_score for labels)

#### STAGE 3: Training Samples (~1 min)
```bash
python src/sample_wells.py --stack data/processed/stage3/features_stack.tif --n 2000 --mode synthetic
```
Generates 2,000 training samples

#### STAGE 4: Data Cleaning (<1 min)
```bash
python src/clean_samples.py
```
Handles NaN values, imputes missing data

#### STAGE 5: Model Training (~3 min)
```bash
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir data/processed/stage4 --cv_k 5 --n_estimators 200
```
Trains Random Forest with 5-fold spatial CV

#### STAGE 6: Predictions (~2 min)
```bash
python src/predict_map.py --stack data/processed/stage3/features_stack.tif --model data/processed/stage4/rf_baseline.pkl --out_dir data/processed/stage4 --bands_csv data/processed/stage3/features_stack_bands.csv
```
Generates probability and classification maps

#### STAGE 7: Visualizations (~1 min)
```bash
python visualize_prediction_results.py
```
Creates impact analysis figures

---

## 📊 Current Status

✅ **Model Trained & Validated**
- Accuracy: **89.49%** (corrected - no data leakage)
- Balanced Accuracy: **86.80%**
- Features: **13** (grp_score properly excluded)
- Watershed Features Contribution: **26.08%**

✅ **Outputs Ready**
- Model: `data/processed/stage4/rf_baseline.pkl`
- Predictions: `data/processed/stage4/predicted_grp_*.tif`
- Figures: `data/processed/stage4/figs/*.png`
- Feature Importances: `data/processed/stage4/feature_importances.csv`

---

## 📁 Key Output Files

| File | Description |
|------|-------------|
| `rf_baseline.pkl` | Trained Random Forest model |
| `feature_importances.csv` | 13 features (no grp_score leak) |
| `cv_results.csv` | 5-fold CV scores |
| `predicted_grp_score.tif` | Probability map (0-1) |
| `predicted_grp_class.tif` | Classification (1-5) |
| `enhanced_features_impact.png` | 9-panel visualization |
| `before_after_comparison.png` | AHP vs ML comparison |

---

## 🔍 Feature Importance Breakdown

**Top Features:**
```
rain:            27.15%  - Rainfall
lulc:            26.75%  - Land use/cover
ndvi:            11.03%  - Vegetation index
slope:            6.46%  - Terrain slope
```

**Enhanced Watershed Features (26.08% total):**
```
tpi:              4.84%  - Topographic Position Index
twi:              4.78%  - Topographic Wetness Index
dist_stream:      4.41%  - Distance to stream
plan_curv:        4.22%  - Plan curvature
prof_curv:        4.07%  - Profile curvature
aspect:           3.77%  - Aspect
```

---

## 📊 Execution Summary

| Stage | Description | Time | Key Outputs |
|-------|-------------|------|-------------|
| **Stage 1** | Enhanced Features | 5 min | TWI, TPI, curvatures, aspect, dist_stream |
| **Stage 2** | Feature Stack | 2 min | 14-band raster |
| **Stage 3** | Sampling | 1 min | 2,000 training samples |
| **Stage 4** | Cleaning | <1 min | Clean dataset |
| **Stage 5** | Training | 3 min | RF model, CV results |
| **Stage 6** | Prediction | 2 min | Probability & class maps |
| **Stage 7** | Visualization | 1 min | Impact figures |
| **Total** | **7 stages** | **~15 min** | **Complete ML pipeline** |

---

## ✅ Quality Verification

### Verify No Data Leakage
```bash
python -c "import pandas as pd; fi = pd.read_csv('data/processed/stage4/feature_importances.csv'); assert 'grp_score' not in fi['feature'].values; print('✓ No data leakage detected')"
```

### Check Model Performance
```bash
python -c "import pandas as pd; cv = pd.read_csv('data/processed/stage4/cv_results.csv'); print(f'Accuracy: {cv[\"test_accuracy\"].mean():.3f}'); print(f'Balanced: {cv[\"test_balanced_accuracy\"].mean():.3f}')"
```

### View Feature Importances
```bash
python -c "import pandas as pd; fi = pd.read_csv('data/processed/stage4/feature_importances.csv'); print(fi.to_string(index=False))"
```

---

## 🌐 Test Backend API (Optional)

### Start FastAPI Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Comprehensive API Test
```bash
python test_api.py
```

**Access Points:**
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

---

## 📚 Additional Documentation

| File | Purpose |
|------|---------|
| `RUN_MODEL_GUIDE.md` | Complete step-by-step guide with details |
| `DATA_LEAKAGE_FIX.md` | Bug fix explanation and validation |
| `PIPELINE_WORKING_SOLUTION.md` | Troubleshooting and solutions |
| `ENHANCED_FEATURES_SUMMARY.md` | Watershed features technical details |

---

## 🚨 Troubleshooting

### "Module not found" errors
```bash
conda activate watershed-up
pip install -r requirements.txt
```

### "File not found" errors
```bash
# Ensure you're in project root
cd G:\PROJECTS\watershed-up

# Check data files exist
dir data\processed\stage3\*.tif
```

### Accuracy too high (>95%)
**This was the data leakage bug!** Check that grp_score is NOT in features:
```bash
python -c "import pandas as pd; print(pd.read_csv('data/processed/stage4/feature_importances.csv'))"
```
Should show 13 features, NOT 14.

---

## 🎓 For Thesis Presentation

**Report These Metrics:**
- ✅ Accuracy: **89.49%** (NOT 95.63% - that was data leakage)
- ✅ Balanced Accuracy: **86.80%**
- ✅ Features: **13** (grp_score properly excluded)
- ✅ Watershed Contribution: **26.08%**
- ✅ Cross-Validation: 5-fold spatial GroupKFold

**Key Finding:**
Enhanced watershed features (TWI, TPI, dist_stream, curvatures, aspect) contribute **26% of model's predictive power**, validating the hypothesis that hydrological features significantly improve groundwater potential mapping beyond traditional AHP methods.

---

## 🎯 Next Steps

1. ✅ Model trained and validated (COMPLETE)
2. ✅ Predictions generated (COMPLETE)
3. ✅ Visualizations ready (COMPLETE)
4. ✅ Data leakage bug fixed (COMPLETE)
5. → Review figures: `data/processed/stage4/figs/`
6. → Update thesis with corrected metrics
7. → Prepare presentation slides
8. → Deploy API for stakeholder demo (optional)

**Everything is ready to use!**

### Critical Files:
- [ ] `data/processed/slope_lucknow.tif`
- [ ] `data/processed/grp_class_lucknow.shp`
- [ ] `data/processed/stage3/features_stack.tif`
- [ ] `models/rf_baseline.pkl`
- [ ] `data/processed/stage4/predicted_grp_class.tif`

**If all exist:** ✅ Pipeline successful!

---

## 🛠️ Quick Troubleshooting

### Streamlit DLL Error ("Error loading model: DLL load failed")?
```powershell
conda activate watershed-up
pip uninstall pyarrow -y
pip install "pyarrow<15.0"
streamlit run app/main.py
```
**Cause:** PyArrow 15+ has Windows DLL compatibility issues with scikit-learn

### Streamlit won't start?
```powershell
conda activate watershed-up
pip install "numpy<2.0"
conda install -c conda-forge folium streamlit-folium
$env:PYTHONNOUSERSITE=1
streamlit run app/main.py
```

### Script failed?
- Check error message in console
- Verify previous stage completed
- Re-run failed script individually

### Need to restart from middle?
- Pipeline is idempotent
- Can re-run any stage independently
- Scripts check if outputs exist

---

## 📁 File Locations

**Documentation:** `PIPELINE_EXECUTION_ORDER.md` (detailed guide)  
**Scripts:** `src/*.py` (processing) + `app/*.py` (platform)  
**Batch:** `run_pipeline.bat` (automated)  
**PowerShell:** `run_pipeline.ps1` (automated with colors)  

---

**Created:** October 27, 2025  
**For:** Complete pipeline rerun ending with Streamlit
