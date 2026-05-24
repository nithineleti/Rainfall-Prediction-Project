# Quick Reference: File Locations

## 📁 Where to Find Everything

### Input Data

| What You Need | Where to Find It |
|---------------|------------------|
| **Digital Elevation Model** | `data/rasters/dem_lucknow.tif` |
| **Slope (CORRECTED!)** | `data/rasters/slope_lucknow.tif` |
| **Land Use/Land Cover** | `data/rasters/lulc_lucknow.tif` |
| **Rainfall** | `data/rasters/rainfall_lucknow.tif` |
| **NDVI** | `data/rasters/ndvi_lucknow.tif` |
| **Well Data** | `data/raw/GW_2018_20_with_xy.csv` |

### Derived Features

| Feature | Location |
|---------|----------|
| **Flow Accumulation** | `data/rasters/flow_acc_lucknow.tif` |
| **Stream Network** | `data/rasters/stream_network_lucknow.tif` |
| **Drainage Density** | `data/rasters/drainage_density_lucknow.tif` |
| **TWI** | `data/rasters/twi_lucknow.tif` |
| **Aspect** | `data/rasters/aspect_lucknow.tif` |
| **Curvatures** | `data/rasters/plan_curvature_lucknow.tif`, `profile_curvature_lucknow.tif` |
| **TPI** | `data/rasters/tpi_lucknow.tif` |
| **Distance to Stream** | `data/rasters/distance_to_stream_lucknow.tif` |

### ML Data

| Item | Location |
|------|----------|
| **Feature Stack (14 bands)** | `data/rasters/features_stack.tif` |
| **Band Names** | `data/rasters/features_stack_bands.csv` |
| **Training Samples** | `data/tables/train_samples.csv` |
| **Trained Model** | `models/rf_baseline.pkl` |
| **Feature Importance** | `data/tables/feature_importances.csv` |
| **CV Results** | `data/tables/cv_results.csv` |

### Watershed Data

| Item | Location |
|------|----------|
| **Watershed Grid** | `data/vectors/watersheds_grid.shp` |
| **Characterized Watersheds** | `data/vectors/watersheds_characterized.shp` |
| **Prioritized Watersheds** | `data/vectors/watersheds_prioritized.shp` |
| **Watershed Table** | `data/tables/watersheds_characterized.csv` |
| **Priority Table** | `data/tables/watersheds_prioritized.csv` |

### Reports & Outputs

| Output | Location |
|--------|----------|
| **Executive Summary** | `outputs/reports/Executive_Summary.pdf` |
| **Action Plans** | `outputs/reports/Watershed_Action_Plans.xlsx` |
| **Priority Summary** | `outputs/reports/priority_summary.txt` |
| **ML Predictions** | `outputs/predictions/predicted_grp_score.tif` |
| **Classification Map** | `outputs/predictions/predicted_class.tif` |

---

## 🔧 Scripts to Run

### Preprocessing Workflow

```bash
# Step 1: Process DEM
python scripts/preprocessing/01_process_dem.py

# Step 2: Calculate slope (WITH CORRECTION!)
python scripts/preprocessing/02_calculate_slope.py

# Step 3: Calculate drainage features
python scripts/preprocessing/03_calculate_drainage.py

# Step 4: Create feature stack (14 bands)
python scripts/preprocessing/04_create_feature_stack.py
```

### Watershed Workflow

```bash
# Step 1: Delineate watersheds
python scripts/watershed/delineate_watersheds.py

# Step 2: Characterize with QGIS (run in QGIS Python)
python scripts/qgis/characterize_watersheds.py

# Step 3: Prioritize watersheds
python scripts/watershed/prioritize_watersheds.py

# Step 4: Generate reports
python scripts/watershed/generate_reports.py
```

### ML Workflow

```bash
# Step 1: Prepare samples from wells
python scripts/ml/prepare_samples.py

# Step 2: Train Random Forest model
python scripts/ml/train_model.py

# Step 3: Generate predictions
python scripts/ml/predict_map.py
```

### Analysis Scripts

```bash
# Basic AHP
python scripts/analysis/ahp_basic.py

# AHP with rainfall
python scripts/analysis/ahp_with_rainfall.py

# AHP with LULC
python scripts/analysis/ahp_with_lulc.py
```

### Utilities

```bash
# Diagnose slope values
python scripts/utilities/diagnose_slope.py

# Extract DBF to CSV
python scripts/utilities/extract_dbf_to_csv.py

# Clean QGIS output
python scripts/utilities/clean_qgis_output.py

# Verify QGIS output
python scripts/utilities/verify_qgis_output.py
```

---

## 💻 Dashboard

### Launch Dashboard
```bash
streamlit run app/main.py
```

**URL:** http://localhost:8501

### Dashboard Pages
1. **Home** - Overview and metrics
2. **Watershed Management** - Priority maps and plans
3. **Data Layers** - Feature information (safe, no crashes!)
4. **Model Insights** - Feature importance and SHAP
5. **Statistical Analysis** - Spatial statistics
6. **Well Validation** - Ground truth comparison
7. **Export** - Download reports

---

## 📦 Import Paths in Code

### Using Centralized Paths

```python
# Import path configuration
from path_config import (
    DEM, SLOPE, LULC, RAINFALL, NDVI,
    FEATURES_STACK, FEATURES_BANDS_CSV,
    WATERSHEDS_CSV, WATERSHEDS_PRIORITY_CSV,
    TRAIN_SAMPLES_CSV, FEATURE_IMPORTANCE_CSV,
    EXECUTIVE_SUMMARY_PDF, ACTION_PLANS_XLSX,
    RF_MODEL, ML_PREDICTION
)

# Use in your scripts
dem = rasterio.open(DEM)
df = pd.read_csv(WATERSHEDS_CSV)
```

### Path Categories Available

```python
from path_config import (
    # Directories
    RASTERS_DIR, VECTORS_DIR, TABLES_DIR, 
    REPORTS_DIR, PREDICTIONS_DIR,
    
    # Input Rasters
    DEM, SLOPE, LULC, RAINFALL, NDVI,
    
    # Derived Rasters
    FLOW_ACC, STREAM_NETWORK, DRAINAGE_DENSITY,
    TWI, ASPECT, PLAN_CURVATURE, PROFILE_CURVATURE,
    TPI, DIST_TO_STREAM,
    
    # Feature Stack
    FEATURES_STACK, FEATURES_BANDS_CSV,
    
    # Vectors
    WATERSHEDS_GRID, WATERSHEDS_CHARACTERIZED,
    WATERSHEDS_PRIORITIZED,
    
    # Tables
    WATERSHEDS_CSV, WATERSHEDS_PRIORITY_CSV,
    TRAIN_SAMPLES_CSV, FEATURE_IMPORTANCE_CSV,
    
    # Reports
    EXECUTIVE_SUMMARY_PDF, ACTION_PLANS_XLSX,
    
    # ML
    ML_PREDICTION, RF_MODEL
)
```

---

## 🔍 Quick Searches

### Find All Rasters
```bash
ls data/rasters/*.tif
```

### Find All Shapefiles
```bash
ls data/vectors/*.shp
```

### Find All CSV Files
```bash
ls data/tables/*.csv
```

### Find All Reports
```bash
ls outputs/reports/*
```

### Find All Scripts
```bash
ls scripts/*/*.py
```

---

## 📋 Common Tasks

### View Feature Stack Bands
```bash
cat data/rasters/features_stack_bands.csv
```

### Check Slope Statistics
```bash
python scripts/utilities/diagnose_slope.py
```

### View Watershed Priorities
```bash
cat outputs/reports/priority_summary.txt
```

### Check Model Performance
```bash
cat data/tables/cv_results.csv
```

### View Feature Importance
```bash
cat data/tables/feature_importances.csv
```

---

## ⚠️ Important Notes

### Corrected Slope
The slope raster has been CORRECTED for degree-to-meter conversion:
- **Old (WRONG):** 89.72° mean (nearly vertical!)
- **New (CORRECT):** 1.46° mean (realistic for flat terrain)

Always use: `data/rasters/slope_lucknow.tif`

### Dashboard Compatibility
Use the **safe** version of Data Layers page (no rasterio crashes):
- File: `app/pages/data_layers_safe.py`
- Configured in: `app/main.py`

### QGIS Scripts
QGIS automation scripts must run in QGIS Python environment:
```bash
# From OSGeo4W Shell or QGIS Python Console
python scripts/qgis/characterize_watersheds.py
```

---

## 📞 Getting Help

1. **Check path config:** `python path_config.py`
2. **View structure:** See `REORGANIZATION_VISUAL_SUMMARY.md`
3. **Read checklist:** See `POST_REORGANIZATION_CHECKLIST.md`
4. **Review summary:** See `REORGANIZATION_SUMMARY.md`
5. **Old docs:** Look in `docs/archive/`

---

**Everything you need is now organized and easy to find!** 🎯
