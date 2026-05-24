# Watershed-UP Project Architecture

**Project:** Groundwater Potential Zone Mapping using AI/ML  
**Author:** Pavan Kumar Eletti  
**Last Updated:** November 6, 2025

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Core Components](#core-components)
4. [Data Flow Pipeline](#data-flow-pipeline)
5. [Module Dependencies](#module-dependencies)
6. [Configuration Management](#configuration-management)
7. [Execution Workflows](#execution-workflows)

---

## 🎯 Project Overview

**Watershed-UP** is an end-to-end geospatial ML pipeline for mapping groundwater recharge potential zones. The system integrates:
- **Remote Sensing Data**: DEM (ALOS PALSAR 12.5m), LULC, NDVI, Rainfall
- **Hydrological Analysis**: Drainage networks, flow accumulation, watershed delineation
- **Machine Learning**: Random Forest classifier with 17 features
- **Visualization**: Interactive Streamlit web application

**Key Metrics:**
- Resolution: 12.5m pixels (30.3M pixels total)
- Model Accuracy: 79.6% (5-fold cross-validation)
- Feature Stack: 17 bands including soil texture
- Coverage: Lucknow District, Uttar Pradesh

---

## 📁 Directory Structure

```
watershed-up/
│
├── 📂 app/                          # Streamlit web application
│   ├── main.py                      # Main dashboard entry point
│   ├── pages/                       # Multi-page app modules
│   │   ├── data_layers.py          # Raster layer viewer
│   │   ├── predictions.py          # ML prediction viewer
│   │   └── watersheds.py           # Watershed analysis
│   └── requirements_app.txt         # App-specific dependencies
│
├── 📂 backend/                      # Flask API backend (optional)
│   ├── app/                         # API endpoints
│   ├── run.py                       # API server
│   └── requirements.txt             # Backend dependencies
│
├── 📂 configs/                      # Configuration files
│   └── config.yml                   # Project-wide settings
│
├── 📂 data/                         # Data storage (excluded from git)
│   ├── raw/                         # Original input data
│   │   ├── lucknow_dem_12.5/       # ALOS PALSAR DEM tiles
│   │   ├── lucknow_lulc/           # Land use/land cover
│   │   ├── lucknow_chirps/         # Rainfall data
│   │   ├── lucknow_ndvi/           # Vegetation index
│   │   ├── lucknow_soil/           # Soil texture (clay, sand, silt)
│   │   ├── lucknow_wells/          # Well location data
│   │   ├── lucknow_shp/            # District boundary
│   │   └── lucknow_geology/        # Geological data
│   │
│   ├── rasters/                     # Processed raster outputs
│   │   ├── dem_lucknow.tif         # Clipped & projected DEM
│   │   ├── slope_lucknow.tif       # Slope (degrees)
│   │   ├── flow_acc_lucknow.tif    # Flow accumulation
│   │   ├── stream_network_lucknow.tif
│   │   ├── drainage_density_lucknow.tif
│   │   ├── twi_lucknow.tif         # Topographic Wetness Index
│   │   ├── aspect_lucknow.tif      # Aspect (degrees)
│   │   ├── plan_curvature_lucknow.tif
│   │   ├── profile_curvature_lucknow.tif
│   │   ├── tpi_lucknow.tif         # Topographic Position Index
│   │   ├── distance_to_stream_lucknow.tif
│   │   └── features_stack.tif      # 17-band ML feature stack
│   │
│   ├── vectors/                     # Vector outputs
│   │   ├── watersheds_grid.shp     # Delineated watersheds
│   │   ├── watersheds_characterized.shp
│   │   └── watersheds_prioritized.shp
│   │
│   ├── tables/                      # CSV outputs
│   │   ├── train_samples.csv       # Raw training samples
│   │   ├── train_samples_clean.csv # Cleaned samples
│   │   ├── cv_results.csv          # Cross-validation results
│   │   ├── feature_importances.csv # Feature importance scores
│   │   ├── features_bands.csv      # Feature stack band mapping
│   │   ├── watersheds_characterized.csv
│   │   └── watersheds_prioritized.csv
│   │
│   └── figures/                     # Visualization outputs
│       ├── confusion_matrix.png
│       ├── 01_dem_comparison.png
│       ├── 02_slope_comparison.png
│       └── ...
│
├── 📂 docs/                         # Documentation
│   ├── ARCHITECTURE_OVERVIEW.md
│   ├── ENHANCED_WATERSHED_FEATURES.md
│   ├── MODEL_TRAINING_RESULTS.md
│   ├── STAGE5_COMPLETE.md
│   └── ...
│
├── 📂 models/                       # Trained ML models (excluded from git)
│   └── rf_baseline.pkl              # Random Forest classifier
│
├── 📂 notebooks/                    # Jupyter notebooks (exploration)
│   └── 01_pilot_demo.ipynb
│
├── 📂 outputs/                      # Final outputs (excluded from git)
│   ├── predictions/
│   │   ├── predicted_grp_score.tif  # Continuous predictions
│   │   └── predicted_grp_class.tif  # Classified zones
│   └── reports/
│       ├── Executive_Summary.pdf
│       └── Watershed_Action_Plans.xlsx
│
├── 📂 scripts/                      # Organized processing scripts
│   ├── preprocessing/               # Data preprocessing
│   │   ├── 01_process_dem.py       # DEM clipping & projection
│   │   ├── 02_calculate_slope.py   # Slope calculation
│   │   ├── 03_calculate_drainage.py # Drainage analysis
│   │   └── 04_create_feature_stack.py
│   │
│   ├── ml/                          # Machine learning
│   │   ├── 01_prepare_samples.py   # Sample extraction
│   │   ├── 03_train_model.py       # Model training
│   │   ├── 04_predict_map.py       # Prediction generation
│   │   └── 06_analyze_enhanced_model.py
│   │
│   ├── watershed/                   # Watershed analysis
│   │   ├── delineate_watersheds.py
│   │   ├── characterize_watersheds.py
│   │   └── prioritize_watersheds.py
│   │
│   ├── postprocessing/              # Output refinement
│   │   └── recompute_scores_filter_and_transform.py
│   │
│   ├── visualization/               # Plotting scripts
│   │   └── visualize_and_enhance_watersheds.py
│   │
│   ├── analysis/                    # AHP and comparison
│   │   ├── ahp_basic.py
│   │   └── compare_ml_vs_ahp.py
│   │
│   ├── utilities/                   # Helper scripts
│   │   └── verify_paths.py
│   │
│   └── maintenance/                 # Project maintenance
│       └── cleanup_project.ps1
│
├── 📂 src/                          # Legacy source code (being migrated)
│   ├── features_stack.py           # Feature stack creation
│   ├── train_model.py              # Model training
│   ├── predict_map.py              # Prediction generation
│   ├── sample_wells.py             # Sample extraction
│   ├── clean_samples.py            # Data cleaning
│   ├── derive_drainage.py          # Drainage derivation
│   ├── shap_explain.py             # SHAP explainability
│   ├── delineate_watersheds.py     # Watershed delineation
│   ├── characterize_watersheds.py  # Watershed metrics
│   ├── prioritize_watersheds.py    # Priority ranking
│   └── ...
│
├── 📂 tests/                        # Unit tests
│   ├── backend/
│   └── ml/
│
├── 📄 path_config.py               # **CENTRAL PATH CONFIGURATION**
├── 📄 run_pipeline.bat             # Windows batch execution
├── 📄 run_pipeline.ps1             # PowerShell execution
├── 📄 run_complete_pipeline.py     # Python orchestrator
├── 📄 requirements.txt             # Python dependencies
├── 📄 environment.yml              # Conda environment
├── 📄 .gitignore                   # Git exclusions
└── 📄 README.md                    # Project documentation
```

---

## 🔧 Core Components

### 1. **Path Configuration (`path_config.py`)**
**Purpose:** Centralized path management for all data, models, and outputs.

**Key Paths:**
```python
# Base directories
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Critical paths
DEM = RASTERS_DIR / "dem_lucknow.tif"
FEATURES_STACK = RASTERS_DIR / "features_stack.tif"
TRAIN_SAMPLES_CSV = TABLES_DIR / "train_samples_clean.csv"
```

**Usage:** All scripts import paths from this single source:
```python
from path_config import DEM, SLOPE, FEATURES_STACK
```

---

### 2. **Preprocessing Pipeline**

#### **Stage 1: DEM Processing**
**Script:** `scripts/preprocessing/01_process_dem.py`
- Input: `data/raw/lucknow_dem_12.5/dem_lucknow_12.5.tif`
- Output: `data/rasters/dem_lucknow.tif`
- Operations: Clipping, reprojection (EPSG:32644), NoData handling

#### **Stage 2: Terrain Analysis**
**Script:** `scripts/preprocessing/02_calculate_slope.py`
- Input: DEM
- Output: Slope, Aspect, Hillshade
- Method: GDAL DEMProcessing

#### **Stage 3: Hydrological Analysis**
**Script:** `scripts/preprocessing/03_calculate_drainage.py`
- Input: DEM
- Outputs:
  - Flow Accumulation (`flow_acc_lucknow.tif`)
  - Stream Network (`stream_network_lucknow.tif`)
  - Drainage Density (`drainage_density_lucknow.tif`)
  - Distance to Stream (`distance_to_stream_lucknow.tif`)
- Method: WhiteboxTools

#### **Stage 4: Enhanced Watershed Features**
**Script:** `src/enhance_watershed_features.py`
- Outputs:
  - TWI (Topographic Wetness Index)
  - Plan Curvature (flow convergence)
  - Profile Curvature (flow acceleration)
  - TPI (Topographic Position Index)
- Method: WhiteboxTools terrain analysis

#### **Stage 5: Feature Stack Creation**
**Script:** `src/features_stack.py`
- Inputs: 17 individual rasters
- Output: `data/rasters/features_stack.tif` (17 bands)
- Bands:
  1. slope
  2. lulc (land use/cover)
  3. rain (precipitation)
  4. ndvi (vegetation)
  5. flow_acc
  6. stream (binary)
  7. drainage_density
  8. twi
  9. aspect
  10. plan_curv
  11. prof_curv
  12. tpi
  13. dist_stream
  14. **soil_clay** ← NEW
  15. **soil_sand** ← NEW
  16. **soil_silt** ← NEW
  17. grp_score (validity mask)

---

### 3. **Machine Learning Pipeline**

#### **Sample Generation**
**Script:** `src/sample_wells.py`
- Input: `features_stack.tif`, well locations
- Output: `data/tables/train_samples.csv` (2,000 samples)
- Method: Stratified random sampling

#### **Data Cleaning**
**Script:** `src/clean_samples.py`
- Input: `train_samples.csv`
- Output: `train_samples_clean.csv`
- Operations:
  - Remove `grp_score` column (prevent data leakage)
  - Impute missing values (median)
  - Remove invalid rows

#### **Model Training**
**Script:** `src/train_model.py`
- Algorithm: Random Forest Classifier
- Cross-Validation: 5-fold spatial GroupKFold
- Outputs:
  - `models/rf_baseline.pkl`
  - `data/tables/cv_results.csv`
  - `data/tables/feature_importances.csv`
  - `data/figures/confusion_matrix.png`

**Hyperparameters:**
```python
RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=5,
    random_state=42
)
```

#### **Prediction Generation**
**Script:** `src/predict_map.py`
- Input: `features_stack.tif`, `rf_baseline.pkl`
- Outputs:
  - `outputs/predictions/predicted_grp_score.tif` (continuous)
  - `outputs/predictions/predicted_grp_class.tif` (classified)

#### **Model Explainability**
**Script:** `src/shap_explain.py`
- Method: SHAP (SHapley Additive exPlanations)
- Output: Feature contribution analysis

---

### 4. **Watershed Analysis**

#### **Delineation**
**Script:** `src/delineate_watersheds.py`
- Input: Flow accumulation, stream network
- Output: `data/vectors/watersheds_grid.shp`
- Method: Pour point-based watershed extraction

#### **Characterization**
**Script:** `src/characterize_watersheds.py`
- Inputs: Watersheds, all feature rasters
- Output: `data/vectors/watersheds_characterized.shp`
- Metrics:
  - Mean slope, TWI, drainage density
  - Dominant LULC class
  - Soil composition
  - Stream density

#### **Prioritization**
**Script:** `src/prioritize_watersheds.py`
- Input: `watersheds_characterized.shp`
- Output: `watersheds_prioritized.shp`
- Ranking: Multi-criteria scoring
- Categories: Very High, High, Moderate, Low

---

### 5. **Visualization Platform**

#### **Streamlit App**
**Entry Point:** `app/main.py`

**Pages:**
1. **Home Dashboard** (`main.py`)
   - Project overview
   - Key metrics
   - Quick navigation

2. **Data Layers** (`pages/data_layers.py`)
   - Interactive raster viewer
   - Layer comparison tools
   - Statistics display

3. **ML Predictions** (`pages/predictions.py`)
   - Prediction map viewer
   - Model performance metrics
   - Feature importance charts

4. **Watershed Analysis** (`pages/watersheds.py`)
   - Priority watershed map
   - Intervention recommendations
   - Export tools

**Launch:**
```bash
streamlit run app/main.py
```

---

## 🔄 Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAW DATA INPUTS                              │
├─────────────────────────────────────────────────────────────────┤
│ • ALOS PALSAR DEM (12.5m)    • LULC (WorldCover)               │
│ • CHIRPS Rainfall            • NDVI (Landsat/Sentinel)         │
│ • Soil Texture (clay/sand/silt) • Well Locations               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  PREPROCESSING STAGE                             │
├─────────────────────────────────────────────────────────────────┤
│ 01_process_dem.py        → dem_lucknow.tif                     │
│ 02_calculate_slope.py    → slope, aspect, hillshade            │
│ 03_calculate_drainage.py → flow_acc, streams, drainage_density │
│ enhance_watershed_features.py → TWI, curvatures, TPI           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│               FEATURE STACK CREATION                             │
├─────────────────────────────────────────────────────────────────┤
│ features_stack.py        → features_stack.tif (17 bands)       │
│                          → features_bands.csv                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                 MACHINE LEARNING STAGE                           │
├─────────────────────────────────────────────────────────────────┤
│ sample_wells.py          → train_samples.csv                   │
│ clean_samples.py         → train_samples_clean.csv             │
│ train_model.py           → rf_baseline.pkl + metrics           │
│ predict_map.py           → predicted_grp_score.tif             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              WATERSHED ANALYSIS STAGE                            │
├─────────────────────────────────────────────────────────────────┤
│ delineate_watersheds.py     → watersheds_grid.shp              │
│ characterize_watersheds.py  → watersheds_characterized.shp     │
│ prioritize_watersheds.py    → watersheds_prioritized.shp       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   VISUALIZATION & OUTPUTS                        │
├─────────────────────────────────────────────────────────────────┤
│ • Streamlit Web App (app/main.py)                              │
│ • PDF Reports (outputs/reports/)                               │
│ • Excel Action Plans                                            │
│ • QGIS-ready Shapefiles                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Module Dependencies

### **Core Libraries**
```python
# Geospatial Processing
rasterio          # Raster I/O
rioxarray         # Raster analysis with xarray
geopandas         # Vector data handling
shapely           # Geometric operations
whitebox          # Hydrological analysis

# Machine Learning
scikit-learn      # Random Forest, metrics
numpy             # Numerical computing
pandas            # Tabular data

# Visualization
matplotlib        # Static plots
plotly            # Interactive charts
streamlit         # Web application

# Utilities
pyyaml            # Configuration files
tqdm              # Progress bars
joblib            # Model serialization
```

### **Environment Setup**
```bash
# Conda environment
conda env create -f environment.yml
conda activate watershed-up

# Or pip installation
pip install -r requirements.txt
```

---

## ⚙️ Configuration Management

### **Path Configuration**
**File:** `path_config.py`
- Single source of truth for all file paths
- Automatically creates missing directories
- OS-agnostic (uses `pathlib.Path`)

### **Project Configuration**
**File:** `configs/config.yml`
```yaml
project:
  name: "Watershed-UP"
  study_area: "Lucknow District"
  crs: "EPSG:32644"  # UTM Zone 44N

processing:
  dem_resolution: 12.5  # meters
  stream_threshold: 1000  # flow accumulation cells
  
ml_model:
  algorithm: "RandomForest"
  n_estimators: 200
  cv_folds: 5
  
watershed:
  min_area: 1.0  # km²
  priority_classes: ["Very High", "High", "Moderate", "Low"]
```

---

## 🚀 Execution Workflows

### **Option 1: Complete Pipeline (Automated)**
```bash
# Windows Batch
run_pipeline.bat

# PowerShell
.\run_pipeline.ps1

# Python
python run_complete_pipeline.py
```

**Pipeline Stages:**
1. DEM processing
2. Slope calculation
3. Drainage analysis
4. Enhanced features
5. Feature stack creation
6. Sample generation
7. Model training
8. Prediction generation

---

### **Option 2: Individual Scripts**

#### **Preprocessing Only**
```bash
python scripts/preprocessing/01_process_dem.py
python scripts/preprocessing/02_calculate_slope.py
python scripts/preprocessing/03_calculate_drainage.py
python src/enhance_watershed_features.py
```

#### **ML Training Only**
```bash
python src/features_stack.py
python src/sample_wells.py
python src/clean_samples.py
python src/train_model.py --in data/tables/train_samples_clean.csv
```

#### **Prediction Only**
```bash
python src/predict_map.py \
  --stack data/rasters/features_stack.tif \
  --model models/rf_baseline.pkl \
  --train_csv data/tables/train_samples_clean.csv \
  --bands_csv data/tables/features_bands.csv
```

#### **Watershed Analysis**
```bash
python src/delineate_watersheds.py
python src/characterize_watersheds.py
python src/prioritize_watersheds.py
```

---

### **Option 3: Interactive Dashboard**
```bash
# Launch Streamlit app
streamlit run app/main.py

# Or use convenience scripts
launch_streamlit.bat      # Windows
./launch_streamlit.ps1    # PowerShell
```

---

## 📊 Feature Engineering Details

### **17-Band Feature Stack**

| Band | Feature | Type | Importance | Description |
|------|---------|------|------------|-------------|
| 1 | slope | Continuous | 7.9% | Terrain steepness (degrees) |
| 2 | lulc | Categorical | 16.1% | Land use/land cover classes |
| 3 | rain | Continuous | 21.8% | Mean annual rainfall (mm) |
| 4 | ndvi | Continuous | 12.3% | Vegetation health index |
| 5 | flow_acc | Continuous | 1.3% | Flow accumulation (log scale) |
| 6 | stream | Binary | 0.0% | Stream network (1=stream) |
| 7 | drainage_density | Continuous | 0.2% | Stream density (km/km²) |
| 8 | twi | Continuous | 4.1% | Topographic Wetness Index |
| 9 | aspect | Continuous | 4.0% | Slope direction (degrees) |
| 10 | plan_curv | Continuous | 3.6% | Flow convergence/divergence |
| 11 | prof_curv | Continuous | 3.7% | Flow acceleration |
| 12 | tpi | Continuous | 3.8% | Ridge/valley position |
| 13 | dist_stream | Continuous | 3.4% | Distance to nearest stream (m) |
| 14 | **soil_clay** | Continuous | **5.8%** | Clay content (%) |
| 15 | **soil_sand** | Continuous | **5.9%** | Sand content (%) |
| 16 | **soil_silt** | Continuous | **6.1%** | Silt content (%) |
| 17 | grp_score | Continuous | - | Validity mask (excluded from training) |

**Total Soil Contribution: 17.8%** (ranked 5-7 in importance)

---

## 🔐 Security & Best Practices

### **Git Configuration**
**File:** `.gitignore`
```
# Large files excluded from version control
.venv/
data/
models/*.pkl
outputs/
*.zip
*.tif
```

### **Data Backup**
- Raw data: Store in `data/raw/` (not versioned)
- Processed outputs: Regenerable from raw data
- Models: Save with timestamps for versioning

### **Code Quality**
- Centralized paths (`path_config.py`)
- Modular scripts (single responsibility)
- Comprehensive error handling
- Progress bars for long operations
- Logging for debugging

---

## 📈 Performance Metrics

### **Model Performance**
- **Accuracy:** 79.6% (5-fold CV)
- **Balanced Accuracy:** 74.8%
- **Training Time:** ~2-3 minutes (2,000 samples)
- **Prediction Time:** ~5-10 minutes (30.3M pixels)

### **Computational Resources**
- **DEM Processing:** 12.5m resolution (30.3M pixels)
- **Feature Stack Size:** ~3.8 GB (17 bands × 5,802 × 5,220 pixels)
- **Memory Requirements:** 16 GB RAM recommended
- **Processing Time:** ~30-45 minutes (full pipeline)

### **Data Volumes**
- Raw DEM: ~5 GB (10 ALOS tiles)
- Feature Stack: ~3.8 GB
- Predictions: ~500 MB
- Total Storage: ~10-15 GB

---

## 🔄 Version History

### **Stage 5 (Current - Nov 2025)**
- ✅ ALOS PALSAR DEM upgrade (12.5m resolution)
- ✅ Soil texture features integrated (clay, sand, silt)
- ✅ 17-band feature stack
- ✅ Enhanced watershed features (TWI, curvatures, TPI)
- ✅ Streamlit visualization platform

### **Stage 4 (Oct 2025)**
- ✅ Random Forest ML model
- ✅ 14-band feature stack
- ✅ Cross-validation framework
- ✅ Feature importance analysis

### **Stage 3 (Sep 2025)**
- ✅ Drainage network analysis
- ✅ NDVI integration
- ✅ Geology preprocessing
- ✅ 9-band feature stack

### **Stage 1-2 (Aug 2025)**
- ✅ DEM processing pipeline
- ✅ LULC and rainfall integration
- ✅ AHP-based GRP mapping

---

## 🛠️ Troubleshooting

### **Common Issues**

1. **Missing paths error**
   - Solution: All scripts use `path_config.py` - check paths are correct

2. **DEM NoData values**
   - Solution: Run `scripts/preprocessing/01_process_dem.py` with proper masking

3. **Feature stack band mismatch**
   - Solution: Regenerate feature stack after adding new layers

4. **Memory errors**
   - Solution: Process in chunks or reduce raster resolution

5. **Model performance drop**
   - Solution: Check for data leakage (grp_score excluded from training)

---

## 📚 Additional Resources

### **Documentation Files**
- `README.md` - Project overview and quick start
- `docs/ENHANCED_WATERSHED_FEATURES.md` - Feature engineering details
- `docs/MODEL_TRAINING_RESULTS.md` - ML performance analysis
- `docs/STAGE5_COMPLETE.md` - Latest milestone summary

### **Scripts Documentation**
- Each script includes docstrings with:
  - Purpose and inputs/outputs
  - Usage examples
  - Parameter descriptions

### **External References**
- WhiteboxTools: https://www.whiteboxgeo.com/
- ALOS PALSAR: https://asf.alaska.edu/data-sets/sar-data-sets/alos-palsar/
- CHIRPS Rainfall: https://www.chc.ucsb.edu/data/chirps

---

## 👤 Contact & Contribution

**Author:** Pavan Kumar Eleti  
**Project:** Groundwater Potential Zone Mapping  
**Repository:** https://github.com/PAVANKUMARELETI/watershed-up

**For questions or contributions:**
- Open an issue on GitHub
- Submit a pull request
- Contact: msd23013@iiitl.ac.in

---

**Last Updated:** November 6, 2025  
**Version:** 5.0 (ALOS PALSAR + Soil Features)
