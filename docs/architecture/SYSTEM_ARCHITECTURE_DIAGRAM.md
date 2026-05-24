# Watershed-UP System Architecture Diagram

**Visual representation of the complete system architecture**

---

## 🏗️ High-Level System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    WATERSHED-UP SYSTEM                                │
│          Groundwater Potential Zone Mapping Platform                  │
└──────────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                  │
        ┌───────▼────────┐              ┌────────▼────────┐
        │  DATA LAYER    │              │  APPLICATION    │
        │                │              │     LAYER       │
        └───────┬────────┘              └────────┬────────┘
                │                                  │
    ┌───────────┼──────────┐            ┌─────────┼─────────┐
    │           │          │            │         │         │
┌───▼───┐   ┌──▼──┐   ┌───▼───┐   ┌────▼───┐ ┌──▼──┐  ┌───▼────┐
│ Raw   │   │Proc │   │Output │   │ ML     │ │ Web │  │ Export │
│ Data  │   │Data │   │  Data │   │ Model  │ │ App │  │ Tools  │
└───────┘   └─────┘   └───────┘   └────────┘ └─────┘  └────────┘
```

---

## 📊 Data Flow Architecture

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         INPUT DATA SOURCES                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
         │              │              │              │
    ┌────▼────┐    ┌───▼────┐    ┌────▼────┐   ┌────▼────┐
    │ ALOS    │    │ CHIRPS │    │ ESA     │   │  USGS   │
    │ PALSAR  │    │ Rainfall│   │WorldCover│  │ Landsat │
    │ DEM     │    │         │    │ LULC    │   │  NDVI   │
    │ 12.5m   │    │ 5km     │    │ 10m     │   │  30m    │
    └────┬────┘    └───┬────┘    └────┬────┘   └────┬────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                            │
         ┏━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━┓
         ┃    PREPROCESSING PIPELINE         ┃
         ┃   (scripts/preprocessing/)        ┃
         ┗━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━┛
                            │
              ┌─────────────┼─────────────┐
              │             │             │
         ┌────▼────┐   ┌────▼────┐  ┌────▼────┐
         │ DEM     │   │ Slope   │  │ Drainage│
         │Processing│  │ Terrain │  │ Network │
         └────┬────┘   └────┬────┘  └────┬────┘
              │             │             │
              └─────────────┴─────────────┘
                            │
         ┏━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━┓
         ┃   FEATURE ENGINEERING             ┃
         ┃   (src/features_stack.py)         ┃
         ┗━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━┛
                            │
                   ┌────────▼─────────┐
                   │  17-Band Feature │
                   │      Stack       │
                   │  (5802 x 5220)   │
                   └────────┬─────────┘
                            │
         ┏━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━┓
         ┃   MACHINE LEARNING PIPELINE       ┃
         ┃   (scripts/ml/)                   ┃
         ┗━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━┛
                            │
              ┌─────────────┼─────────────┐
              │             │             │
         ┌────▼────┐   ┌────▼────┐  ┌────▼────┐
         │ Sample  │   │ Train   │  │ Predict │
         │ Extract │   │ RF Model│  │   Map   │
         └────┬────┘   └────┬────┘  └────┬────┘
              │             │             │
              └─────────────┴─────────────┘
                            │
         ┏━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━┓
         ┃   WATERSHED ANALYSIS              ┃
         ┃   (scripts/watershed/)            ┃
         ┗━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━┛
                            │
                   ┌────────▼─────────┐
                   │   Priority       │
                   │   Watersheds     │
                   └────────┬─────────┘
                            │
         ┏━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━┓
         ┃   VISUALIZATION & OUTPUTS         ┃
         ┃   (app/, outputs/)                ┃
         ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                            │
              ┌─────────────┼─────────────┐
              │             │             │
         ┌────▼────┐   ┌────▼────┐  ┌────▼────┐
         │Streamlit│   │ Reports │  │Shapefiles│
         │Web App  │   │  PDFs   │  │  QGIS   │
         └─────────┘   └─────────┘  └─────────┘
```

---

## 🔄 Processing Pipeline Detailed Flow

```
START
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 1: RAW DATA INGESTION                             │
├─────────────────────────────────────────────────────────┤
│ • ALOS PALSAR DEM tiles (10 files, ~5GB)               │
│ • CHIRPS rainfall (monthly → mean annual)               │
│ • ESA WorldCover LULC                                   │
│ • USGS Landsat NDVI                                     │
│ • Soil texture (clay, sand, silt)                       │
│ • District boundary shapefile                           │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 2: DEM PREPROCESSING                              │
│ Script: scripts/preprocessing/01_process_dem.py         │
├─────────────────────────────────────────────────────────┤
│ Input:  data/raw/lucknow_dem_12.5/dem_lucknow_12.5.tif │
│ Output: data/rasters/dem_lucknow.tif                   │
│                                                          │
│ Operations:                                              │
│  1. Load DEM mosaic                                     │
│  2. Clip to district boundary                           │
│  3. Reproject to UTM 44N (EPSG:32644)                  │
│  4. Handle NoData values                                │
│  5. Validate output (shape: 5802 x 5220)               │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 3: TERRAIN ANALYSIS                               │
│ Script: scripts/preprocessing/02_calculate_slope.py     │
├─────────────────────────────────────────────────────────┤
│ Input:  dem_lucknow.tif                                 │
│ Outputs:                                                 │
│  • slope_lucknow.tif (degrees, 0-90°)                  │
│  • aspect_lucknow.tif (degrees, 0-360°)                │
│  • hillshade_lucknow.tif (visualization)               │
│                                                          │
│ Method: GDAL DEMProcessing                              │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 4: HYDROLOGICAL ANALYSIS                          │
│ Script: scripts/preprocessing/03_calculate_drainage.py  │
├─────────────────────────────────────────────────────────┤
│ Input:  dem_lucknow.tif                                 │
│ Outputs:                                                 │
│  • flow_acc_lucknow.tif (D8 algorithm)                 │
│  • stream_network_lucknow.tif (threshold: 1000)        │
│  • drainage_density_lucknow.tif (kernel: 1000m)        │
│  • distance_to_stream_lucknow.tif (Euclidean)          │
│                                                          │
│ Method: WhiteboxTools                                   │
│  - BreachDepressions                                    │
│  - D8FlowAccumulation                                   │
│  - ExtractStreams                                       │
│  - EuclideanDistance                                    │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 5: ENHANCED WATERSHED FEATURES                    │
│ Script: src/enhance_watershed_features.py               │
├─────────────────────────────────────────────────────────┤
│ Input:  dem_lucknow.tif                                 │
│ Outputs:                                                 │
│  • twi_lucknow.tif (Topographic Wetness Index)         │
│  • plan_curvature_lucknow.tif (convergence)            │
│  • profile_curvature_lucknow.tif (acceleration)        │
│  • tpi_lucknow.tif (Topographic Position Index)        │
│                                                          │
│ Method: WhiteboxTools                                   │
│  - WetnessIndex                                         │
│  - PlanCurvature                                        │
│  - ProfileCurvature                                     │
│  - TopographicPositionIndex                             │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 6: FEATURE STACK CREATION                         │
│ Script: src/features_stack.py                           │
├─────────────────────────────────────────────────────────┤
│ Inputs: 17 individual rasters                           │
│ Output: features_stack.tif (17 bands)                   │
│                                                          │
│ Band Order:                                              │
│  1. slope           2. lulc           3. rain           │
│  4. ndvi            5. flow_acc       6. stream         │
│  7. drainage_density 8. twi           9. aspect         │
│  10. plan_curv      11. prof_curv     12. tpi           │
│  13. dist_stream    14. soil_clay     15. soil_sand     │
│  16. soil_silt      17. grp_score                       │
│                                                          │
│ Operations:                                              │
│  - Reproject all to match DEM CRS                       │
│  - Resample to 12.5m resolution                         │
│  - Stack into single multi-band raster                  │
│  - Generate band mapping CSV                            │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 7: TRAINING SAMPLE EXTRACTION                     │
│ Script: src/sample_wells.py                             │
├─────────────────────────────────────────────────────────┤
│ Input:  features_stack.tif                              │
│ Output: train_samples.csv (2000 samples)                │
│                                                          │
│ Method:                                                  │
│  - Use grp_score (band 17) as validity mask            │
│  - Stratified random sampling                           │
│  - Extract all 17 feature values per sample            │
│  - Include x, y coordinates                             │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 8: DATA CLEANING                                  │
│ Script: src/clean_samples.py                            │
├─────────────────────────────────────────────────────────┤
│ Input:  train_samples.csv                               │
│ Output: train_samples_clean.csv                         │
│                                                          │
│ Operations:                                              │
│  - Remove grp_score column (prevent data leakage)      │
│  - Impute missing values (median strategy)             │
│  - Remove rows with missing labels                      │
│  - Validate feature count (16 features)                │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 9: MODEL TRAINING                                 │
│ Script: src/train_model.py                              │
├─────────────────────────────────────────────────────────┤
│ Input:  train_samples_clean.csv                         │
│ Outputs:                                                 │
│  • rf_baseline.pkl (trained model)                     │
│  • cv_results.csv (5-fold performance)                 │
│  • feature_importances.csv                             │
│  • confusion_matrix.png                                 │
│  • classification_report.txt                            │
│                                                          │
│ Algorithm: RandomForestClassifier                       │
│  - n_estimators: 200                                    │
│  - max_depth: None                                      │
│  - min_samples_split: 5                                 │
│                                                          │
│ Cross-Validation: 5-fold Spatial GroupKFold            │
│  - Group by spatial clusters (KMeans on x,y)           │
│  - Prevents spatial autocorrelation bias               │
│                                                          │
│ Performance:                                             │
│  - Accuracy: 79.6%                                      │
│  - Balanced Accuracy: 74.8%                             │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 10: PREDICTION GENERATION                         │
│ Script: src/predict_map.py                              │
├─────────────────────────────────────────────────────────┤
│ Inputs:                                                  │
│  • features_stack.tif                                   │
│  • rf_baseline.pkl                                      │
│  • train_samples_clean.csv (for feature names)         │
│                                                          │
│ Outputs:                                                 │
│  • predicted_grp_score.tif (continuous 0-1)            │
│  • predicted_grp_class.tif (categorical 1-5)           │
│                                                          │
│ Process:                                                 │
│  1. Load 17-band stack                                  │
│  2. Use band 17 as validity mask                        │
│  3. Extract 16 features for valid pixels               │
│  4. Predict on 16,694,057 pixels                       │
│  5. Write predictions back to raster                    │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 11: WATERSHED DELINEATION                         │
│ Script: src/delineate_watersheds.py                     │
├─────────────────────────────────────────────────────────┤
│ Inputs:                                                  │
│  • flow_acc_lucknow.tif                                │
│  • stream_network_lucknow.tif                          │
│                                                          │
│ Output: watersheds_grid.shp                             │
│                                                          │
│ Method:                                                  │
│  - Create pour points grid                              │
│  - Extract watersheds using D8 pointer                 │
│  - Vectorize watershed boundaries                       │
│  - Calculate area, perimeter                            │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 12: WATERSHED CHARACTERIZATION                    │
│ Script: src/characterize_watersheds.py                  │
├─────────────────────────────────────────────────────────┤
│ Input:  watersheds_grid.shp + all feature rasters       │
│ Output: watersheds_characterized.shp                    │
│                                                          │
│ Zonal Statistics per Watershed:                         │
│  • Mean slope, TWI, drainage density                   │
│  • Dominant LULC class                                  │
│  • Soil composition (% clay/sand/silt)                 │
│  • Stream density                                       │
│  • Mean predicted GRP score                             │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 13: WATERSHED PRIORITIZATION                      │
│ Script: src/prioritize_watersheds.py                    │
├─────────────────────────────────────────────────────────┤
│ Input:  watersheds_characterized.shp                    │
│ Output: watersheds_prioritized.shp                      │
│                                                          │
│ Multi-Criteria Scoring:                                 │
│  - GRP score (40% weight)                               │
│  - Slope suitability (20%)                              │
│  - LULC suitability (20%)                               │
│  - Drainage potential (20%)                             │
│                                                          │
│ Priority Classes:                                        │
│  1. Very High (top 25%)                                 │
│  2. High (25-50%)                                       │
│  3. Moderate (50-75%)                                   │
│  4. Low (bottom 25%)                                    │
│                                                          │
│ Outputs:                                                 │
│  • Ranked watershed shapefile                           │
│  • Intervention recommendations                         │
│  • Action plan Excel file                               │
└─────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ STAGE 14: VISUALIZATION & REPORTING                     │
│ App: app/main.py (Streamlit)                            │
├─────────────────────────────────────────────────────────┤
│ Features:                                                │
│  • Interactive map viewer                               │
│  • Layer comparison tools                               │
│  • Model performance dashboard                          │
│  • Watershed priority map                               │
│  • Export to PDF/Excel/Shapefile                        │
│                                                          │
│ Access: http://localhost:8501                           │
└─────────────────────────────────────────────────────────┘
  │
  ▼
END
```

---

## 🏛️ Component Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     WATERSHED-UP COMPONENTS                     │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 1. DATA LAYER                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Raw Data   │  │  Processed   │  │   Outputs    │         │
│  │              │  │    Data      │  │              │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • DEM tiles  │  │ • Rasters    │  │ • Predictions│         │
│  │ • LULC       │  │ • Vectors    │  │ • Reports    │         │
│  │ • Rainfall   │  │ • Tables     │  │ • Figures    │         │
│  │ • NDVI       │  │ • Features   │  │ • Shapefiles │         │
│  │ • Soil       │  │              │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 2. PROCESSING LAYER                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Preprocessing │  │   Feature    │  │   Machine    │         │
│  │   Pipeline   │  │ Engineering  │  │   Learning   │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • DEM        │  │ • Stack      │  │ • Sampling   │         │
│  │ • Slope      │  │   creation   │  │ • Training   │         │
│  │ • Drainage   │  │ • Band       │  │ • Prediction │         │
│  │ • Enhanced   │  │   mapping    │  │ • Validation │         │
│  │   features   │  │ • Resampling │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 3. ANALYSIS LAYER                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Watershed   │  │    Model     │  │   Spatial    │         │
│  │   Analysis   │  │ Explainability│  │   Analysis   │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • Delineate  │  │ • SHAP       │  │ • Zonal      │         │
│  │ • Characterize│ │ • Feature    │  │   statistics │         │
│  │ • Prioritize │  │   importance │  │ • Clustering │         │
│  │ • Rank       │  │ • CV metrics │  │ • Buffers    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 4. PRESENTATION LAYER                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Streamlit  │  │   Reports    │  │   Export     │         │
│  │   Web App    │  │              │  │    Tools     │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • Dashboard  │  │ • PDF        │  │ • Shapefile  │         │
│  │ • Map viewer │  │ • Excel      │  │ • GeoTIFF    │         │
│  │ • Charts     │  │ • Markdown   │  │ • CSV        │         │
│  │ • Interactive│  │ • Text       │  │ • JSON       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 5. CONFIGURATION LAYER                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ path_config  │  │  config.yml  │  │ Environment  │         │
│  │     .py      │  │              │  │              │         │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤         │
│  │ • All paths  │  │ • Settings   │  │ • .venv      │         │
│  │ • Directories│  │ • Parameters │  │ • conda env  │         │
│  │ • Centralized│  │ • Thresholds │  │ • Dependencies│        │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Module Interaction Diagram

```
   path_config.py (Central Hub)
         │
         ├──────────────────────┬──────────────────────┬─────────
         │                      │                      │
         ▼                      ▼                      ▼
   Preprocessing          Feature Stack          ML Pipeline
         │                      │                      │
         │                      │                      │
    ┌────▼────┐           ┌────▼────┐          ┌─────▼─────┐
    │01_process│          │features  │          │sample     │
    │_dem.py   │          │_stack.py │          │_wells.py  │
    └────┬────┘           └────┬────┘          └─────┬─────┘
         │                      │                      │
    ┌────▼────┐                │                 ┌────▼────┐
    │02_calculate│              │                │clean    │
    │_slope.py  │               │                │_samples.py│
    └────┬────┘                │                └────┬────┘
         │                      │                     │
    ┌────▼────┐                │                ┌────▼────┐
    │03_calculate│              │               │train    │
    │_drainage.py│              │               │_model.py│
    └────┬────┘                │               └────┬────┘
         │                      │                    │
         └──────────────────────┼────────────────────┘
                                │
                           ┌────▼────┐
                           │predict  │
                           │_map.py  │
                           └────┬────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
   Watershed              Visualization          Reports
   Analysis                    │                      │
         │                     │                      │
    ┌────▼────┐          ┌─────▼─────┐         ┌─────▼─────┐
    │delineate│          │app/main.py│         │generate   │
    │_watersheds│        │(Streamlit)│         │_reports.py│
    └────┬────┘          └───────────┘         └───────────┘
         │
    ┌────▼────┐
    │characterize│
    │_watersheds│
    └────┬────┘
         │
    ┌────▼────┐
    │prioritize│
    │_watersheds│
    └─────────┘
```

---

## 💾 Data Storage Architecture

```
data/
│
├── raw/                    [~5 GB, not in git]
│   └── Static input files
│       • Downloaded once
│       • Never modified
│
├── rasters/               [~4 GB, not in git]
│   └── Processed rasters
│       • Generated from raw
│       • Reproducible
│       • 12.5m resolution
│
├── vectors/               [~50 MB, not in git]
│   └── Shapefiles
│       • Watershed boundaries
│       • Characterized attributes
│
├── tables/                [~10 MB, some in git]
│   └── CSV files
│       • Training samples
│       • Model metrics
│       • Feature mappings
│
└── figures/               [~20 MB, some in git]
    └── Visualizations
        • Plots
        • Maps
        • Charts
```

---

## 🎯 Execution Entry Points

```
┌──────────────────────────────────────────────────────┐
│              EXECUTION ENTRY POINTS                   │
└──────────────────────────────────────────────────────┘

1. COMPLETE PIPELINE
   ┌─────────────────────────────────────┐
   │ run_pipeline.bat                    │
   │ run_pipeline.ps1                    │
   │ run_complete_pipeline.py            │
   └─────────────────────────────────────┘
        │
        ├─► All stages sequentially
        └─► ~30-45 minutes

2. INDIVIDUAL MODULES
   ┌─────────────────────────────────────┐
   │ python scripts/preprocessing/...    │
   │ python src/features_stack.py        │
   │ python src/train_model.py           │
   └─────────────────────────────────────┘
        │
        ├─► Targeted execution
        └─► Minutes per script

3. INTERACTIVE APP
   ┌─────────────────────────────────────┐
   │ streamlit run app/main.py           │
   │ launch_streamlit.bat                │
   └─────────────────────────────────────┘
        │
        ├─► Web interface
        └─► http://localhost:8501

4. JUPYTER NOTEBOOKS
   ┌─────────────────────────────────────┐
   │ jupyter notebook                    │
   │ notebooks/01_pilot_demo.ipynb       │
   └─────────────────────────────────────┘
        │
        ├─► Exploratory analysis
        └─► Interactive development
```

---

**Last Updated:** November 6, 2025  
**Version:** 5.0 (ALOS PALSAR + Soil Features)
