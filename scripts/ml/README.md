# Machine Learning Pipeline - Execution Order

This folder contains the ML pipeline scripts for groundwater potential prediction.

## 📋 Execution Order

### **Step 1: Prepare Training Samples**
**File:** `01_prepare_samples.py`

**Purpose:** Generate training samples from feature stack
- Extracts features at random or well locations
- Creates synthetic labels from AHP scores
- Generates spatial samples to avoid bias

**Usage:**
```bash
python scripts/ml/01_prepare_samples.py --stack data/rasters/features_stack.tif \
    --out data/tables/train_samples.csv --n 5000 --mode synthetic
```

**Outputs:**
- `data/tables/train_samples.csv` - Training samples with features and labels

---

### **Step 2: Check Sample Quality**
**File:** `02_check_samples.py`

**Purpose:** Validate training samples
- Check for missing values
- Verify feature distributions
- Detect outliers
- Ensure spatial balance

**Usage:**
```bash
python scripts/ml/02_check_samples.py
```

**Outputs:**
- Console report on sample quality
- Statistics on each feature

---

### **Step 3: Train ML Model**
**File:** `03_train_model.py`

**Purpose:** Train Random Forest classifier
- Uses spatial cross-validation (prevents data leakage)
- 5-fold GroupKFold based on spatial clustering
- Saves trained model and metrics

**Usage:**
```bash
python scripts/ml/03_train_model.py --in data/tables/train_samples.csv \
    --out_dir models --cv_k 5 --n_estimators 200
```

**Outputs:**
- `models/rf_baseline.pkl` - Trained model
- `data/processed/stage4/cv_results.csv` - Cross-validation metrics
- `data/processed/stage4/feature_importances.csv` - Feature rankings
- `data/processed/stage4/confusion_matrix.png` - Model performance

---

### **Step 4: Generate Predictions**
**File:** `04_predict_map.py`

**Purpose:** Apply trained model to entire study area
- Loads feature stack
- Predicts groundwater potential class for each pixel
- Generates probability maps

**Usage:**
```bash
python scripts/ml/04_predict_map.py
```

**Outputs:**
- `data/rasters/gwp_prediction.tif` - Predicted classes (0=Low, 1=Moderate, 2=High)
- `data/rasters/gwp_probability_*.tif` - Probability maps for each class

---

### **Step 5: SHAP Analysis**
**File:** `05_shap_explain.py`

**Purpose:** Explain model predictions using SHAP values
- Calculates feature contributions
- Generates waterfall plots
- Creates summary plots

**Usage:**
```bash
python scripts/ml/05_shap_explain.py
```

**Outputs:**
- `data/figures/shap_summary.png` - Feature importance plot
- `data/figures/shap_waterfall_*.png` - Individual prediction explanations

---

### **Step 6: Enhanced Model Analysis**
**File:** `06_analyze_enhanced_model.py`

**Purpose:** Analyze model with enhanced features
- Compare importance of 14 features
- Assess impact of new terrain features
- Generate detailed reports

**Usage:**
```bash
python scripts/ml/06_analyze_enhanced_model.py
```

**Outputs:**
- Feature importance comparisons
- Performance metrics
- Visualization plots

---

### **Step 7: Summarize Training**
**File:** `07_summarize_ml_training.py`

**Purpose:** Generate comprehensive training summary
- Aggregate all metrics
- Compare fold performances
- Statistical analysis

**Usage:**
```bash
python scripts/ml/07_summarize_ml_training.py
```

**Outputs:**
- Training summary report
- Performance statistics

---

### **Step 8: Print Summary**
**File:** `08_print_ml_summary.py`

**Purpose:** Display final ML pipeline summary
- Print all results to console
- Show key metrics and file locations

**Usage:**
```bash
python scripts/ml/08_print_ml_summary.py
```

**Outputs:**
- Console summary of entire ML pipeline

---

## 🚀 Quick Run (All Steps)

### Full Pipeline
```bash
# Activate environment
conda activate watershed-up

# Run all steps in order
python scripts/ml/01_prepare_samples.py --stack data/rasters/features_stack.tif --out data/tables/train_samples.csv --n 5000
python scripts/ml/02_check_samples.py
python scripts/ml/03_train_model.py --in data/tables/train_samples.csv --out_dir models
python scripts/ml/04_predict_map.py
python scripts/ml/05_shap_explain.py
python scripts/ml/06_analyze_enhanced_model.py
python scripts/ml/07_summarize_ml_training.py
python scripts/ml/08_print_ml_summary.py
```

### Essential Steps Only
```bash
# Minimum for predictions
python scripts/ml/01_prepare_samples.py --stack data/rasters/features_stack.tif --out data/tables/train_samples.csv --n 5000
python scripts/ml/03_train_model.py --in data/tables/train_samples.csv --out_dir models
python scripts/ml/04_predict_map.py
```

---

## 📁 Old Versions (Backup)

These files are kept for reference but not part of the active pipeline:
- `prepare_samples_old.py` - Legacy sample preparation
- `train_model_old.py` - Old training script
- `predict_map_old.py` - Previous prediction method

**Do not use these files** - they are kept only for version history.

---

## ⚙️ Configuration

All ML parameters can be adjusted in `config.yml`:

```yaml
machine_learning:
  sampling:
    n_samples: 5000
    random_seed: 42
  
  training:
    n_estimators: 200
    cv_folds: 5
    random_state: 42
    n_jobs: -1
```

**To change parameters:**
1. Edit `config.yml`
2. Re-run scripts (no code changes needed!)

---

## 📊 Expected Outputs

After running the full pipeline, you should have:

### Model Files
- ✅ `models/rf_baseline.pkl` (~50 MB)

### Data Files
- ✅ `data/tables/train_samples.csv` (~2 MB for 5,000 samples)
- ✅ `data/rasters/gwp_prediction.tif` (~10 MB)

### Results Files
- ✅ `data/processed/stage4/cv_results.csv`
- ✅ `data/processed/stage4/feature_importances.csv`
- ✅ `data/processed/stage4/confusion_matrix.png`

### Analysis Files
- ✅ `data/figures/shap_summary.png`
- ✅ Various summary reports

---

## 🧪 Testing

Verify each step completed successfully:

```bash
# Check if outputs exist
python -c "import os; files = ['data/tables/train_samples.csv', 'models/rf_baseline.pkl', 'data/rasters/gwp_prediction.tif']; [print(f'✓ {f}' if os.path.exists(f) else f'✗ {f}') for f in files]"
```

---

## 🔍 Troubleshooting

### Error: "No module named 'sklearn'"
```bash
conda activate watershed-up
conda install scikit-learn
```

### Error: "No such file: train_samples.csv"
```bash
# Run step 1 first
python scripts/ml/01_prepare_samples.py --stack data/rasters/features_stack.tif --out data/tables/train_samples.csv --n 5000
```

### Error: "No such file: features_stack.tif"
```bash
# Run preprocessing first
python scripts/preprocessing/04_create_feature_stack.py
```

---

## 📈 Performance Metrics

**Expected Results (5,000 samples, 5-fold CV):**
- Accuracy: ~75-85%
- Balanced Accuracy: ~73-83%
- Training Time: ~2-5 minutes
- Prediction Time: ~30 seconds

**Top Features (typical):**
1. Flow accumulation (~15%)
2. Drainage density (~12%)
3. TWI (~10%)
4. Slope (~7%)
5. Rainfall (~7%)

---

## 📝 Notes

- **Spatial CV is critical** - Prevents data leakage from nearby samples
- **Sample size matters** - More samples = better model (but slower training)
- **Feature engineering** - The 14 features were carefully selected
- **Class imbalance** - Handled through balanced Random Forest

---

## 🎯 Next Steps

After completing the ML pipeline:
1. ✅ Validate predictions with field data (if available)
2. ✅ Use predictions in watershed prioritization
3. ✅ Visualize results in Streamlit dashboard
4. ✅ Generate official reports

---

**Last Updated:** November 1, 2025  
**Status:** Production Ready ✅
