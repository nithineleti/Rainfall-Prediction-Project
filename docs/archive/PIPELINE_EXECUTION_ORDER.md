# Complete Pipeline Execution Order - Watershed-UP

## 🎯 Full Pipeline Execution (Stages 1-5)

Run these commands in order from the project root directory (`G:\PROJECTS\watershed-up`):

---

## ✅ **STAGE 1: DEM Processing**

### 1.1 Mosaic and Clip DEM (if needed)
```powershell
python src/mosaic_and_clip_dem.py
```
**Output:** `data/processed/lucknow_dem_clipped.tif`  
**Time:** ~2 minutes  
**Skip if:** DEM already clipped

### 1.2 DEM Preprocessing (Slope, Hillshade)
```powershell
python src/preprocess.py
```
**Outputs:** 
- `data/processed/dem_lucknow.tif`
- `data/processed/slope_lucknow.tif`
- `data/processed/hillshade_lucknow.tif`

**Time:** ~2 minutes

---

## ✅ **STAGE 2: Multi-Criteria AHP**

### 2.1 Preprocess LULC
```powershell
python src/preprocess_lulc.py
```
**Output:** `data/processed/lulc_lucknow.tif`  
**Time:** ~1 minute

### 2.2 Preprocess Rainfall
```powershell
python src/preprocess_rain.py
```
**Output:** `data/processed/rain_mean_lucknow.tif`  
**Time:** ~1 minute

### 2.3 AHP Analysis (Final - with Slope + LULC + Rain)
```powershell
python src/ahp_with_rain.py
```
**Outputs:**
- `data/processed/grp_score_lucknow.tif` (continuous 0-1)
- `data/processed/grp_class_lucknow.tif` (classified 0/1/2)
- `data/processed/grp_class_lucknow.shp` (vector)

**Time:** ~2 minutes

**Note:** You can also run intermediate AHP versions:
- `python src/ahp.py` (slope only)
- `python src/ahp_with_lulc.py` (slope + LULC)

---

## ✅ **STAGE 3: Advanced Features**

### 3.1 Preprocess Geology and NDVI
```powershell
python src/preprocess_stage3.py
```
**Outputs:**
- `data/processed/stage3/geology_lucknow.tif`
- `data/processed/stage3/ndvi_mean_lucknow.tif`

**Time:** ~2 minutes

### 3.2 Derive Drainage Features
```powershell
python src/derive_drainage.py
```
**Outputs:**
- `data/processed/stage3/flow_acc_lucknow.tif`
- `data/processed/stage3/stream_network_lucknow.tif`
- `data/processed/stage3/drainage_density_lucknow.tif`

**Time:** ~2 minutes

### 3.3 Create Feature Stack (9-band raster)
```powershell
python src/features_stack.py
```
**Outputs:**
- `data/processed/stage3/features_stack.tif` (9 bands)
- `data/processed/stage3/features_stack_bands.csv`
- `data/processed/stage3/features_corr.csv`
- `data/processed/stage3/features_summary.csv`

**Time:** ~2 minutes

### 3.4 Visualize Stage 3 (Optional - Correlation Plots)
```powershell
python src/visualize_stage3.py
```
**Outputs:**
- Correlation heatmap
- Feature distribution plots

**Time:** ~1 minute

---

## ✅ **STAGE 4: Machine Learning**

### 4.1 Sample Wells (Extract Training Data)
```powershell
python src/sample_wells.py
```
**Output:** `data/processed/stage4/train_samples.csv`  
**Time:** ~30 seconds

### 4.2 Clean Training Samples
```powershell
python src/clean_samples.py
```
**Output:** `data/processed/stage4/train_samples_clean.csv`  
**Time:** ~10 seconds

### 4.3 Train Random Forest Model
```powershell
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir models --cv_k 5
```
**Outputs:**
- `models/rf_baseline.pkl` (trained model)
- `data/processed/stage4/cv_results.csv`
- `data/processed/stage4/feature_importances.csv`
- `data/processed/stage4/confusion_matrix.png`
- `data/processed/stage4/classification_report.txt`

**Time:** ~2-5 minutes  
**Expected Accuracy:** 95.7% (5-fold spatial CV)

### 4.4 Generate Predictions
```powershell
python src/predict_map.py --stack data/processed/stage3/features_stack.tif --model models/rf_baseline.pkl --out_dir data/processed/stage4
```
**Outputs:**
- `data/processed/stage4/predicted_grp_score.tif`
- `data/processed/stage4/predicted_grp_class.tif`

**Time:** ~3-5 minutes

### 4.5 Compare ML vs AHP
```powershell
python src/compare_with_ahp.py
```
**Outputs:**
- Confusion matrix (ML vs AHP)
- Agreement statistics

**Time:** ~30 seconds

### 4.6 SHAP Interpretability Analysis
```powershell
python src/shap_explain.py
```
**Outputs:**
- `data/processed/stage4/figs_shap/shap_summary.png`
- SHAP value explanations

**Time:** ~2-3 minutes

---

## ✅ **STAGE 5: Quality Check (Optional)**

### 5.1 Quality Check Stage 5
```powershell
python scripts/quality_check_stage5.py
```
**Outputs:**
- 6 comparison figures (old DEM vs new DEM)
- Performance improvement metrics

**Time:** ~2 minutes

---

## ✅ **LAUNCH VISUALIZATION PLATFORM**

### Final Step: Run Streamlit App
```powershell
conda activate watershed-up
$env:PYTHONNOUSERSITE=1
streamlit run app/main.py
```

**Access:** http://localhost:8501  
**Features:**
- Interactive map (ML/AHP toggle)
- Data layer explorer
- Model insights
- Statistical analysis
- Well validation
- Export/download

---

## 📋 **Quick Reference: Complete Pipeline**

### **Copy-Paste All Commands (Sequential Execution)**

```powershell
# Activate environment
conda activate watershed-up

# STAGE 1: DEM Processing
python src/preprocess.py

# STAGE 2: Multi-Criteria AHP
python src/preprocess_lulc.py
python src/preprocess_rain.py
python src/ahp_with_rain.py

# STAGE 3: Advanced Features
python src/preprocess_stage3.py
python src/derive_drainage.py
python src/features_stack.py
python src/visualize_stage3.py

# STAGE 4: Machine Learning
python src/sample_wells.py
python src/clean_samples.py
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir models --cv_k 5
python src/predict_map.py --stack data/processed/stage3/features_stack.tif --model models/rf_baseline.pkl --out_dir data/processed/stage4
python src/compare_with_ahp.py
python src/shap_explain.py

# STAGE 5: Quality Check (Optional)
python scripts/quality_check_stage5.py

# LAUNCH PLATFORM
$env:PYTHONNOUSERSITE=1
streamlit run app/main.py
```

**Total Time:** ~25-35 minutes for complete pipeline

---

## ⚡ **Fast Pipeline (Skip Optional Steps)**

```powershell
conda activate watershed-up

# Core pipeline only
python src/preprocess.py
python src/preprocess_lulc.py
python src/preprocess_rain.py
python src/ahp_with_rain.py
python src/preprocess_stage3.py
python src/derive_drainage.py
python src/features_stack.py
python src/sample_wells.py
python src/clean_samples.py
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv --out_dir models --cv_k 5
python src/predict_map.py --stack data/processed/stage3/features_stack.tif --model models/rf_baseline.pkl --out_dir data/processed/stage4

# Launch platform
$env:PYTHONNOUSERSITE=1
streamlit run app/main.py
```

**Time:** ~20 minutes (skips visualization, comparison, SHAP, quality check)

---

## 🔍 **Verification Checklist**

After each stage, verify outputs exist:

### **Stage 1 Outputs:**
- [ ] `data/processed/dem_lucknow.tif`
- [ ] `data/processed/slope_lucknow.tif`
- [ ] `data/processed/hillshade_lucknow.tif`

### **Stage 2 Outputs:**
- [ ] `data/processed/lulc_lucknow.tif`
- [ ] `data/processed/rain_mean_lucknow.tif`
- [ ] `data/processed/grp_score_lucknow.tif`
- [ ] `data/processed/grp_class_lucknow.shp`

### **Stage 3 Outputs:**
- [ ] `data/processed/stage3/geology_lucknow.tif`
- [ ] `data/processed/stage3/ndvi_mean_lucknow.tif`
- [ ] `data/processed/stage3/flow_acc_lucknow.tif`
- [ ] `data/processed/stage3/stream_network_lucknow.tif`
- [ ] `data/processed/stage3/drainage_density_lucknow.tif`
- [ ] `data/processed/stage3/features_stack.tif`

### **Stage 4 Outputs:**
- [ ] `data/processed/stage4/train_samples_clean.csv`
- [ ] `models/rf_baseline.pkl`
- [ ] `data/processed/stage4/predicted_grp_class.tif`
- [ ] `data/processed/stage4/cv_results.csv`

---

## 🛠️ **Troubleshooting**

### **Error: "DLL load failed" when loading model in Streamlit**
- **Symptom:** "Error loading model: DLL load failed while importing lib: The specified procedure could not be found"
- **Cause:** PyArrow 15+ has Windows DLL compatibility issues with scikit-learn
- **Solution:** 
  ```powershell
  conda activate watershed-up
  pip uninstall pyarrow -y
  pip install "pyarrow<15.0"
  streamlit run app/main.py
  ```

### **Error: "File not found"**
- **Cause:** Skipped a previous step
- **Solution:** Run pipeline in order from beginning

### **Error: "No module named..."**
- **Cause:** Missing dependencies
- **Solution:** 
  ```powershell
  conda activate watershed-up
  pip install -r requirements.txt
  ```

### **Error: "NaN values in training data"**
- **Cause:** `clean_samples.py` not run
- **Solution:** Run `python src/clean_samples.py` before training

### **Streamlit won't start**
- **Solution:**
  ```powershell
  conda activate watershed-up
  pip install "numpy<2.0"
  conda install -c conda-forge folium streamlit-folium
  pip install "pyarrow<15.0"
  $env:PYTHONNOUSERSITE=1
  streamlit run app/main.py
  ```

---

## 📊 **Expected Results**

After complete pipeline:
- **Model Accuracy:** 95.7% (±0.3%)
- **Balanced Accuracy:** 93.4%
- **Processing Time:** 25-35 minutes
- **Total Files Generated:** 25+ rasters, 10+ CSVs, 1 model, 1 shapefile
- **Platform:** Fully functional with 7 interactive pages

---

## 🎓 **Pipeline Dependencies**

```
DEM → slope → AHP
      ↓
LULC → AHP → grp_score
      ↓         ↓
Rain → AHP      ↓
                ↓
Geology ────────┼─→ features_stack → sample_wells → train_model → predict_map
NDVI ───────────┤                         ↓              ↓
Flow_acc ───────┤                         ↓              ↓
Stream ─────────┤                    clean_samples   rf_baseline.pkl
Drainage ───────┘                         ↓              ↓
                                          └──────────────┘
                                                 ↓
                                          Streamlit App
```

---

## 📝 **Notes**

1. **Environment:** Always activate `conda activate watershed-up` first
2. **NumPy:** Use version <2.0 for compatibility
3. **Working Directory:** Run all commands from project root
4. **Interruption:** Pipeline is idempotent - can resume from any stage
5. **Debugging:** Check console output for errors after each step

---

**Created:** October 27, 2025  
**Last Updated:** October 27, 2025  
**Pipeline Version:** Stage 5 (ALOS DEM)  
**Total Scripts:** 16 core + 4 optional = 20 files
