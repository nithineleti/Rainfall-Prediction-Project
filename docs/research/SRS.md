# Software Requirements Specification (SRS)
## Watershed-UP: AI/ML-Based Groundwater Recharge Potential Zonation System

**Document Version:** 1.0  
**Date:** October 27, 2025  
**Project:** Watershed-UP  
**Author:** Pavan Kumar Eleti  
**Project Guide:** Dr. Deepak Kumar Singh  
**Institution:** IIIT Lucknow

---

## Document Control

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | Oct 27, 2025 | Pavan Kumar Eleti | Initial SRS document |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features and Requirements](#3-system-features-and-requirements)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Data Requirements](#6-data-requirements)
7. [System Architecture](#7-system-architecture)
8. [Appendices](#8-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document describes the functional and non-functional requirements for the **Watershed-UP** system - an AI/ML-based groundwater recharge potential zonation platform. The system integrates remote sensing, GIS, and machine learning to delineate groundwater potential zones (GRPZ) for water resource planning and management.

**Intended Audience:**
- Software developers and maintainers
- Water resource planners and decision-makers
- Research supervisors and thesis evaluators
- Stakeholders in groundwater management
- Future researchers extending the system

### 1.2 Project Scope

**Project Name:** Watershed-UP (Groundwater Recharge Potential Zonation System)

**Objectives:**
- Automate geospatial preprocessing of multi-source remote sensing data
- Generate groundwater potential zone maps using ML and AHP methods
- Provide interactive visualization platform for stakeholders
- Enable validation against field well data
- Support evidence-based water resource planning

**Benefits:**
- Reduces manual GIS processing time from weeks to hours
- Provides 95.7% accurate ML-based predictions
- Enables local-scale (12.5m resolution) planning
- Offers transparent, interpretable results via SHAP analysis
- Supports reproducible scientific research

**Study Area:** Lucknow District, Uttar Pradesh, India (pilot implementation)  
**Scalability:** Methodology designed for extension to entire Uttar Pradesh state

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| **GRPZ** | Groundwater Recharge Potential Zone - areas with varying capacity for aquifer recharge |
| **AHP** | Analytic Hierarchy Process - multi-criteria decision analysis method |
| **DEM** | Digital Elevation Model - raster representing terrain elevation |
| **LULC** | Land Use/Land Cover - classification of surface features |
| **NDVI** | Normalized Difference Vegetation Index - vegetation density indicator |
| **ML** | Machine Learning - AI-based pattern recognition and prediction |
| **RF** | Random Forest - ensemble machine learning algorithm |
| **SHAP** | SHapley Additive exPlanations - model interpretability method |
| **CGWB** | Central Ground Water Board - Indian government agency |
| **CHIRPS** | Climate Hazards Group InfraRed Precipitation with Station data |
| **ESA** | European Space Agency |
| **ALOS** | Advanced Land Observing Satellite (JAXA) |
| **CV** | Cross-Validation - model evaluation technique |
| **GIS** | Geographic Information System |
| **RS** | Remote Sensing |

### 1.4 References

**Data Sources:**
1. ALOS PALSAR DEM - Alaska Satellite Facility, JAXA
2. ESA WorldCover 2021 - European Space Agency
3. CHIRPS Rainfall Data - UC Santa Barbara Climate Hazards Center
4. CGWB Well Data - Central Ground Water Board, India
5. Geological Survey of India - Lithological maps

**Software & Libraries:**
1. Python 3.11 - Programming language
2. Rasterio - Geospatial raster processing
3. GeoPandas - Vector data operations
4. Scikit-learn - Machine learning
5. Streamlit - Web application framework
6. Folium - Interactive mapping

**Academic References:**
1. Analytical Hierarchy Process (Saaty, 1980)
2. Random Forest (Breiman, 2001)
3. SHAP values (Lundberg & Lee, 2017)

### 1.5 Document Overview

This SRS is organized into 8 main sections:
- **Section 2:** Overall system description and context
- **Section 3:** Detailed functional requirements
- **Section 4:** Interface requirements (UI, API, hardware)
- **Section 5:** Non-functional requirements (performance, security)
- **Section 6:** Data requirements and formats
- **Section 7:** System architecture and design
- **Section 8:** Appendices with supplementary information

---

## 2. Overall Description

### 2.1 Product Perspective

Watershed-UP is a **standalone geospatial analysis and visualization system** consisting of:

1. **Processing Pipeline** - Python scripts for automated data preprocessing
2. **ML Model Training** - Random Forest classifier for GRPZ prediction
3. **Visualization Platform** - Streamlit web application for interactive exploration
4. **Export Tools** - Data download and format conversion utilities

**System Context:**
- Operates on local workstation or server environment
- Inputs: Remote sensing data (DEM, LULC, rainfall, etc.)
- Outputs: GRPZ maps (raster/vector), trained models, validation metrics
- Interfaces: Web browser (visualization), GIS software (data integration)

**System Boundaries:**
- **In Scope:** Data preprocessing, model training, prediction, visualization
- **Out of Scope:** Real-time satellite data acquisition, field survey automation

### 2.2 Product Functions

**Core Functions:**

1. **Geospatial Data Preprocessing**
   - Clip rasters to study area boundary
   - Reproject/resample to common grid
   - Compute terrain derivatives (slope, hillshade, flow accumulation)
   - Extract drainage networks
   - Calculate drainage density

2. **Multi-Criteria Analysis (AHP)**
   - Apply expert-defined weights to thematic layers
   - Generate composite GRPZ scores
   - Classify zones into Poor/Moderate/High potential

3. **Machine Learning Modeling**
   - Sample training data from well locations
   - Train Random Forest classifier
   - Perform spatial cross-validation
   - Generate pixel-level predictions
   - Compute feature importance

4. **Model Interpretation**
   - SHAP analysis for feature contributions
   - Confusion matrices (ML vs AHP, ML vs wells)
   - Classification reports and metrics

5. **Interactive Visualization**
   - Web-based map interface
   - Toggle between ML/AHP predictions
   - Layer-by-layer data exploration
   - Well validation cross-tabulation
   - Statistical dashboards

6. **Data Export**
   - GeoTIFF rasters for GIS integration
   - Shapefiles for vector analysis
   - CSV tables for statistical software
   - Trained models (pickle format)

### 2.3 User Classes and Characteristics

| User Class | Technical Expertise | Primary Use Cases |
|------------|---------------------|-------------------|
| **Water Resource Planners** | Medium (GIS proficient) | Identify priority recharge zones, plan conservation projects |
| **Policy Makers** | Low (non-technical) | Understand spatial patterns, make informed decisions |
| **GIS Analysts** | High (technical) | Integrate GRPZ data into larger systems, custom analysis |
| **Researchers** | High (Python/ML) | Reproduce methodology, extend to new areas, modify models |
| **Field Engineers** | Medium (domain experts) | Validate predictions, plan groundwater structures |

### 2.4 Operating Environment

**Hardware Requirements:**
- **Minimum:** 8 GB RAM, 50 GB storage, dual-core processor
- **Recommended:** 16 GB RAM, 100 GB SSD, quad-core processor
- **Server Deployment:** 32 GB RAM, multi-core processor (for concurrent users)

**Software Environment:**
- **OS:** Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python:** 3.9 - 3.11
- **Web Browser:** Chrome 90+, Firefox 88+, Edge 90+ (for visualization platform)
- **Optional:** QGIS 3.x, ArcGIS Pro (for GIS integration)

**Network Requirements:**
- Local installation: No internet required after setup
- Web deployment: HTTPS server with minimum 10 Mbps bandwidth
- Data download: Internet connection for initial data acquisition

### 2.5 Design and Implementation Constraints

**Technical Constraints:**
1. **Python 3.11 Compatibility:** All libraries must support Python 3.11
2. **NumPy Version:** Must use NumPy <2.0 due to package compatibility
3. **Coordinate System:** EPSG:4326 (WGS84) for consistency
4. **Raster Resolution:** 12.5m (determined by ALOS DEM)
5. **Memory Limitations:** Process 1440×1440 pixel grids efficiently

**Data Constraints:**
1. **DEM Coverage:** Must cover entire study area
2. **Temporal Alignment:** All datasets from similar time period (±2 years)
3. **Well Data Quality:** Minimum 500 wells for ML training
4. **Spatial Accuracy:** Positional accuracy within ±30m

**Regulatory Constraints:**
1. **Data Licensing:** Respect open data licenses (CC-BY, public domain)
2. **Privacy:** No personally identifiable information in well data
3. **Publication:** Acknowledge data providers as per license terms

**Development Constraints:**
1. **Open Source:** Use only open-source libraries (no proprietary GIS)
2. **Reproducibility:** Document all processing steps
3. **Version Control:** Maintain Git repository for code changes

### 2.6 Assumptions and Dependencies

**Assumptions:**
1. Users have basic understanding of groundwater concepts
2. Input data is of acceptable quality (no major gaps/errors)
3. Study area has sufficient well data for validation
4. Computational resources are adequate for processing
5. Web browser supports JavaScript and modern HTML5

**Dependencies:**

**External Data Dependencies:**
- ALOS PALSAR DEM availability
- ESA WorldCover LULC updates
- CHIRPS rainfall data continuity
- CGWB well data access

**Software Dependencies:**
```
Core Processing:
- Python 3.11
- NumPy <2.0
- Pandas 2.x
- Rasterio 1.3+
- GeoPandas 0.14+
- Scikit-learn 1.3+

Visualization:
- Streamlit 1.28+
- Folium 0.15+
- Matplotlib 3.7+
- Seaborn 0.12+

Optional:
- SHAP 0.43+ (for interpretability)
- Richdem (for advanced drainage)
```

---

## 3. System Features and Requirements

### 3.1 Data Preprocessing Module

**Priority:** High (Critical)  
**Description:** Automates ingestion, clipping, reprojection, and preprocessing of multi-source geospatial data

#### 3.1.1 DEM Processing (REQ-DP-001)

**Functional Requirements:**

**FR-DP-001.1:** System shall load ALOS PALSAR DEM in GeoTIFF format  
**FR-DP-001.2:** System shall clip DEM to district boundary shapefile  
**FR-DP-001.3:** System shall compute slope in degrees using gradient method  
**FR-DP-001.4:** System shall generate hillshade with azimuth=315°, altitude=45°  
**FR-DP-001.5:** System shall save outputs at 12.5m resolution  
**FR-DP-001.6:** System shall maintain EPSG:4326 coordinate system  

**Input:** 
- DEM raster (GeoTIFF)
- District boundary (Shapefile)

**Output:**
- `dem_lucknow.tif` (clipped DEM)
- `slope_lucknow.tif` (slope in degrees)
- `hillshade_lucknow.tif` (shaded relief)

**Processing Time:** <2 minutes for 1440×1440 grid

#### 3.1.2 LULC Processing (REQ-DP-002)

**Functional Requirements:**

**FR-DP-002.1:** System shall load ESA WorldCover LULC raster  
**FR-DP-002.2:** System shall clip LULC to district boundary  
**FR-DP-002.3:** System shall resample to DEM grid using nearest-neighbor  
**FR-DP-002.4:** System shall preserve LULC class codes (10-95)  
**FR-DP-002.5:** System shall handle NoData values appropriately  

**Input:** ESA WorldCover GeoTIFF  
**Output:** `lulc_lucknow.tif` (aligned to DEM grid)  
**Processing Time:** <1 minute

#### 3.1.3 Rainfall Processing (REQ-DP-003)

**Functional Requirements:**

**FR-DP-003.1:** System shall load CHIRPS mean annual rainfall raster  
**FR-DP-003.2:** System shall clip to district boundary  
**FR-DP-003.3:** System shall resample to DEM grid using bilinear interpolation  
**FR-DP-003.4:** System shall output rainfall in mm/year  

**Input:** CHIRPS rainfall GeoTIFF  
**Output:** `rain_mean_lucknow.tif`  
**Processing Time:** <1 minute

#### 3.1.4 Hydrological Features (REQ-DP-004)

**Functional Requirements:**

**FR-DP-004.1:** System shall compute D8 flow directions from DEM  
**FR-DP-004.2:** System shall calculate flow accumulation  
**FR-DP-004.3:** System shall extract stream network (threshold=1000 cells)  
**FR-DP-004.4:** System shall compute drainage density (kernel size=31×31)  
**FR-DP-004.5:** System shall handle sinks and flat areas  

**Input:** DEM  
**Outputs:**
- `flow_acc_lucknow.tif`
- `stream_network_lucknow.tif`
- `drainage_density_lucknow.tif`

**Processing Time:** <5 minutes

#### 3.1.5 Geology and NDVI (REQ-DP-005)

**Functional Requirements:**

**FR-DP-005.1:** System shall rasterize geology shapefile to DEM grid  
**FR-DP-005.2:** System shall normalize NDVI values to 0-1 range  
**FR-DP-005.3:** System shall align all layers to common extent  

**Inputs:**
- Geology shapefile
- NDVI raster

**Outputs:**
- `geology_lucknow.tif`
- `ndvi_mean_lucknow.tif`

#### 3.1.6 Feature Stack Creation (REQ-DP-006)

**Functional Requirements:**

**FR-DP-006.1:** System shall combine all layers into 9-band stack  
**FR-DP-006.2:** Band order shall be: slope, LULC, rain, geology, NDVI, flow_acc, stream, drainage_density, grp_score  
**FR-DP-006.3:** System shall verify spatial alignment of all bands  
**FR-DP-006.4:** System shall generate metadata CSV listing band names  
**FR-DP-006.5:** System shall compute correlation matrix  

**Output:**
- `features_stack.tif` (9-band raster)
- `features_stack_bands.csv` (band names)
- `features_corr.csv` (correlation matrix)
- `features_summary.csv` (statistics)

**Processing Time:** <2 minutes

### 3.2 AHP Analysis Module

**Priority:** High (Critical)  
**Description:** Implements Analytic Hierarchy Process for expert-driven GRPZ mapping

#### 3.2.1 Weight Assignment (REQ-AHP-001)

**Functional Requirements:**

**FR-AHP-001.1:** System shall accept user-defined weights for layers  
**FR-AHP-001.2:** Default weights shall be: Slope(0.5), LULC(0.3), Rain(0.2)  
**FR-AHP-001.3:** System shall validate weights sum to 1.0  
**FR-AHP-001.4:** System shall support custom weight configurations  

#### 3.2.2 Score Calculation (REQ-AHP-002)

**Functional Requirements:**

**FR-AHP-002.1:** System shall normalize each layer to 0-1 range  
**FR-AHP-002.2:** System shall apply weighted linear combination  
**FR-AHP-002.3:** System shall handle NoData pixels  
**FR-AHP-002.4:** System shall output continuous scores (0-1)  

**Formula:** `GRP_score = w₁×slope_norm + w₂×LULC_norm + w₃×rain_norm`

#### 3.2.3 Classification (REQ-AHP-003)

**Functional Requirements:**

**FR-AHP-003.1:** System shall classify scores into 3 classes:
- Poor (0): score < 0.33
- Moderate (1): 0.33 ≤ score < 0.67
- High (2): score ≥ 0.67

**FR-AHP-003.2:** System shall generate class raster  
**FR-AHP-003.3:** System shall export as shapefile  

**Outputs:**
- `grp_score_lucknow.tif` (continuous)
- `grp_class_lucknow.tif` (classified)
- `grp_class_lucknow.shp` (vector)

### 3.3 Machine Learning Module

**Priority:** High (Critical)  
**Description:** Random Forest-based supervised classification for GRPZ prediction

#### 3.3.1 Training Data Preparation (REQ-ML-001)

**Functional Requirements:**

**FR-ML-001.1:** System shall sample features at well coordinates  
**FR-ML-001.2:** System shall extract all 9 feature values per well  
**FR-ML-001.3:** System shall remove samples with NaN values  
**FR-ML-001.4:** System shall impute remaining NaNs with mean/median  
**FR-ML-001.5:** System shall create labels from AHP scores  
**FR-ML-001.6:** System shall export cleaned training dataset  

**Input:** 
- Feature stack
- Well locations (CSV with lat/lon)

**Output:**
- `train_samples.csv` (raw samples)
- `train_samples_clean.csv` (processed)

**Minimum Sample Size:** 500 wells  
**Recommended:** 2000+ wells

#### 3.3.2 Model Training (REQ-ML-002)

**Functional Requirements:**

**FR-ML-002.1:** System shall implement Random Forest classifier  
**FR-ML-002.2:** Default hyperparameters:
- n_estimators = 200
- max_depth = None (unlimited)
- min_samples_split = 2
- random_state = 42

**FR-ML-002.3:** System shall perform k-fold spatial cross-validation (k=5)  
**FR-ML-002.4:** System shall compute accuracy, balanced accuracy, precision, recall, F1  
**FR-ML-002.5:** System shall save trained model as pickle file  
**FR-ML-002.6:** System shall generate confusion matrix  
**FR-ML-002.7:** System shall export feature importances  

**Outputs:**
- `rf_baseline.pkl` (trained model)
- `cv_results.csv` (cross-validation metrics)
- `feature_importances.csv`
- `confusion_matrix.png`
- `classification_report.txt`

**Performance Target:** Mean CV accuracy ≥ 85%

#### 3.3.3 Prediction Generation (REQ-ML-003)

**Functional Requirements:**

**FR-ML-003.1:** System shall load trained model  
**FR-ML-003.2:** System shall predict on entire feature stack  
**FR-ML-003.3:** System shall output class predictions (0/1/2)  
**FR-ML-003.4:** System shall output probability scores  
**FR-ML-003.5:** System shall handle NoData pixels  

**Outputs:**
- `predicted_grp_class.tif` (classification)
- `predicted_grp_score.tif` (probabilities)

**Processing Time:** <5 minutes for 1440×1440 grid

#### 3.3.4 Model Interpretation (REQ-ML-004)

**Functional Requirements:**

**FR-ML-004.1:** System shall compute SHAP values for feature explanations  
**FR-ML-004.2:** System shall generate SHAP summary plot  
**FR-ML-004.3:** System shall compare ML vs AHP predictions  
**FR-ML-004.4:** System shall compute pixel-wise agreement  

**Outputs:**
- `shap_summary.png`
- `confusion_ml_vs_ahp.csv`

### 3.4 Visualization Platform

**Priority:** High (Critical)  
**Description:** Interactive web-based dashboard for stakeholder engagement

#### 3.4.1 Home Page (REQ-VIZ-001)

**Functional Requirements:**

**FR-VIZ-001.1:** System shall display project overview  
**FR-VIZ-001.2:** System shall show GRPZ classification legend  
**FR-VIZ-001.3:** System shall check data file availability  
**FR-VIZ-001.4:** System shall provide navigation to other pages  

#### 3.4.2 Interactive Map (REQ-VIZ-002)

**Functional Requirements:**

**FR-VIZ-002.1:** System shall render Folium-based interactive map  
**FR-VIZ-002.2:** System shall allow toggle between ML and AHP predictions  
**FR-VIZ-002.3:** System shall overlay well locations  
**FR-VIZ-002.4:** System shall display district boundaries  
**FR-VIZ-002.5:** System shall support multiple basemaps (OSM, satellite, CartoDB)  
**FR-VIZ-002.6:** System shall show layer statistics (class distribution)  
**FR-VIZ-002.7:** System shall allow opacity adjustment  

**User Interactions:**
- Pan, zoom, click features
- Toggle layers on/off
- Change basemap
- Adjust transparency

#### 3.4.3 Data Layers Explorer (REQ-VIZ-003)

**Functional Requirements:**

**FR-VIZ-003.1:** System shall visualize all 9+ individual layers  
**FR-VIZ-003.2:** System shall compute and display statistics (min/max/mean/std)  
**FR-VIZ-003.3:** System shall generate histograms  
**FR-VIZ-003.4:** System shall support side-by-side layer comparison (up to 4)  
**FR-VIZ-003.5:** System shall display correlation heatmap  

**Available Layers:**
- DEM, Slope, Hillshade
- LULC, Rainfall, NDVI
- Geology, Flow Accumulation
- Drainage Density, Stream Network

#### 3.4.4 Model Insights (REQ-VIZ-004)

**Functional Requirements:**

**FR-VIZ-004.1:** System shall display feature importance chart  
**FR-VIZ-004.2:** System shall show CV performance metrics  
**FR-VIZ-004.3:** System shall render confusion matrix  
**FR-VIZ-004.4:** System shall display SHAP summary plot  
**FR-VIZ-004.5:** System shall compare ML vs AHP agreement  

#### 3.4.5 Statistical Analysis (REQ-VIZ-005)

**Functional Requirements:**

**FR-VIZ-005.1:** System shall show training data statistics  
**FR-VIZ-005.2:** System shall display class distributions  
**FR-VIZ-005.3:** System shall render correlation matrices  
**FR-VIZ-005.4:** System shall export statistics as CSV  

#### 3.4.6 Well Validation (REQ-VIZ-006)

**Functional Requirements:**

**FR-VIZ-006.1:** System shall load CGWB well data  
**FR-VIZ-006.2:** System shall extract predicted GRPZ class at well locations  
**FR-VIZ-006.3:** System shall create cross-tabulation (wells × predictions)  
**FR-VIZ-006.4:** System shall compute validation metrics  
**FR-VIZ-006.5:** System shall visualize well performance by predicted class  

#### 3.4.7 Export & Download (REQ-VIZ-007)

**Functional Requirements:**

**FR-VIZ-007.1:** System shall provide download links for:
- GeoTIFF rasters (all layers)
- Shapefiles (GRPZ classifications)
- CSV files (well data, statistics, metrics)
- Pickle files (trained models)

**FR-VIZ-007.2:** System shall create complete data packages  
**FR-VIZ-007.3:** System shall display metadata and usage guidelines  

### 3.5 Validation and Quality Assurance

**Priority:** Medium (Important)  
**Description:** Tools for comparing results and ensuring data quality

#### 3.5.1 Quality Check Script (REQ-QA-001)

**Functional Requirements:**

**FR-QA-001.1:** System shall generate comparison figures (old vs new DEM)  
**FR-QA-001.2:** System shall compute performance improvements  
**FR-QA-001.3:** System shall validate spatial alignment  
**FR-QA-001.4:** System shall check for NaN values  
**FR-QA-001.5:** System shall verify CRS consistency  

**Outputs:**
- 6 comparison PNG figures
- Quality metrics summary
- Data integrity report

---

## 4. External Interface Requirements

### 4.1 User Interface Requirements

#### 4.1.1 Web Interface (Streamlit Platform)

**Layout Requirements:**
- Responsive design (minimum width: 1024px recommended)
- Sidebar navigation with page icons
- Main content area with scrolling
- Multi-column layouts for comparisons

**Visual Design:**
- Color scheme: Blue (#1f77b4) primary, Green/Yellow/Red for GRPZ classes
- Font: Sans-serif, minimum 11pt for body text
- Contrast ratio: WCAG AA compliant (4.5:1 minimum)

**Interactive Elements:**
- Buttons: Clear labels, hover effects
- Dropdowns: Sorted options, searchable if >10 items
- Sliders: Value labels, snap to increments
- Maps: Pan, zoom, click, tooltip on hover

**Error Handling:**
- File not found: Display friendly message with path
- Invalid data: Show error details and suggested fix
- Processing errors: Log to console, notify user

#### 4.1.2 Command-Line Interface

**Script Execution:**
```bash
# Standard pattern
python src/script_name.py [--arg1 value] [--arg2 value]

# Example
python src/train_model.py --in data/processed/stage4/train_samples_clean.csv \
                          --out_dir models --cv_k 5
```

**Requirements:**
- Help text available via `--help` flag
- Progress indicators for long-running tasks
- Clear error messages with exit codes
- Output paths printed upon completion

### 4.2 Hardware Interfaces

**Not Applicable** - System operates entirely in software, no direct hardware control

### 4.3 Software Interfaces

#### 4.3.1 Input Data Formats

| Data Type | Format | Specification |
|-----------|--------|---------------|
| DEM | GeoTIFF | Single-band, Float32, EPSG:4326 |
| LULC | GeoTIFF | Single-band, UInt8, class codes 10-95 |
| Rainfall | GeoTIFF | Single-band, Float32, mm/year |
| Geology | Shapefile | Polygon, attribute table with class codes |
| Wells | CSV | Columns: id, lat, lon, [optional: water_level, trend] |
| District Boundary | Shapefile | Polygon, EPSG:4326 |

#### 4.3.2 Output Data Formats

| Product | Format | Specification |
|---------|--------|---------------|
| Processed Rasters | GeoTIFF | EPSG:4326, LZW compression, tiled |
| GRPZ Classification | Shapefile | Polygon, attributes: class, score, area |
| Trained Model | Pickle | Scikit-learn RandomForestClassifier object |
| Statistics | CSV | UTF-8, comma-delimited, header row |
| Figures | PNG | 300 DPI, RGB color |

#### 4.3.3 External Libraries

**Core Processing:**
```python
rasterio >= 1.3.0        # Raster I/O
geopandas >= 0.14.0      # Vector operations
numpy < 2.0              # Numerical computing
pandas >= 2.0            # Data manipulation
scikit-learn >= 1.3.0    # Machine learning
```

**Visualization:**
```python
streamlit >= 1.28.0      # Web framework
folium >= 0.15.0         # Interactive maps
matplotlib >= 3.7.0      # Plotting
seaborn >= 0.12.0        # Statistical viz
```

**Optional:**
```python
shap >= 0.43.0           # Model interpretability
richdem                  # Advanced hydrology
```

### 4.4 Communication Interfaces

#### 4.4.1 Web Server (Streamlit)

**Protocol:** HTTP/HTTPS  
**Port:** 8501 (default, configurable)  
**Endpoints:** Auto-generated by Streamlit framework  

**Configuration:**
```toml
# .streamlit/config.toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

#### 4.4.2 File System

**Read Operations:**
- Input data from `data/raw/`
- Processed data from `data/processed/`
- Models from `models/`
- Configuration from `configs/`

**Write Operations:**
- Processed outputs to `data/processed/`
- Models to `models/`
- Figures to `data/processed/figs/` or `data/processed/stage*/figs/`
- Logs to `logs/` (optional)

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

#### 5.1.1 Processing Speed

| Operation | Maximum Time | Target |
|-----------|--------------|--------|
| DEM clipping | 2 minutes | 1 minute |
| Slope calculation | 2 minutes | 1 minute |
| Flow accumulation | 10 minutes | 5 minutes |
| Feature stack creation | 3 minutes | 2 minutes |
| Model training (2000 samples, 5-fold CV) | 10 minutes | 5 minutes |
| Prediction (1440×1440 grid) | 10 minutes | 5 minutes |
| Full pipeline (Stages 1-4) | 2 hours | 1 hour |

#### 5.1.2 Memory Usage

- **Maximum RAM:** 8 GB for processing, 4 GB for visualization
- **Disk Space:** 10 GB for data, 5 GB for backups
- **Temp Files:** Auto-cleanup after processing

#### 5.1.3 Web Platform Response Time

| Action | Maximum Response Time |
|--------|----------------------|
| Page load | 5 seconds |
| Map rendering | 3 seconds |
| Layer toggle | 1 second |
| Statistics computation | 5 seconds |
| File download initiation | 2 seconds |

### 5.2 Safety Requirements

**Data Integrity:**
- All write operations shall use atomic file writes
- Backup original data before overwriting
- Verify checksums for critical data files

**Error Recovery:**
- System shall continue processing after non-critical errors
- Failed processing stages shall not corrupt previous outputs
- User shall be notified of any data quality issues

### 5.3 Security Requirements

**Data Privacy:**
- Well location coordinates may be public domain or restricted
- No personally identifiable information (PII) in datasets
- Optional: Implement authentication for web platform deployment

**Access Control:**
- Local deployment: Filesystem permissions control access
- Web deployment: Role-based access (view/download/admin)

**Code Security:**
- No hardcoded credentials
- Sanitize user inputs to prevent injection
- Use secure pickle loading (`pickle.load` only from trusted sources)

### 5.4 Software Quality Attributes

#### 5.4.1 Reliability

- **Uptime:** 99% for local use, 95% for web deployment
- **Mean Time Between Failures (MTBF):** >100 hours of continuous processing
- **Error Rate:** <1% of processing runs fail due to software bugs

#### 5.4.2 Maintainability

- **Code Documentation:** Docstrings for all functions
- **Commenting:** Inline comments for complex logic
- **Modularity:** Functions <100 lines, modules <1000 lines
- **Version Control:** Git with meaningful commit messages

#### 5.4.3 Portability

- **OS Support:** Windows, Linux, macOS
- **Python Version:** 3.9 - 3.11
- **Deployment:** Conda environment, Docker container (future)

#### 5.4.4 Usability

- **Learning Curve:** Non-technical users can explore platform within 15 minutes
- **Documentation:** User guide, API docs, video tutorials
- **Error Messages:** Clear, actionable, non-technical language

#### 5.4.5 Scalability

- **Horizontal:** Multiple study areas processed in parallel
- **Vertical:** Larger grids (up to 5000×5000 pixels) with adequate RAM
- **Data Volume:** Handle datasets up to 50 GB total size

#### 5.4.6 Reproducibility

- **Version Tracking:** All code, data, and results versioned
- **Documentation:** Complete processing logs
- **Environment:** Exact package versions specified
- **Random Seeds:** Fixed for stochastic processes (random_state=42)

---

## 6. Data Requirements

### 6.1 Input Data Specifications

#### 6.1.1 Digital Elevation Model (DEM)

**Source:** ALOS PALSAR World 3D - 30m (AW3D30)  
**Provider:** Alaska Satellite Facility, JAXA  
**Format:** GeoTIFF  
**Resolution:** 12.5m (original), resampled from 30m tiles  
**Coverage:** Global  
**Vertical Accuracy:** ±5m (RMSE)  
**Coordinate System:** EPSG:4326 (WGS84)  
**Data Type:** Float32  
**NoData Value:** -9999 or NaN  
**Update Frequency:** Static (2006-2011 acquisition)  

**Acquisition:**
```
Download from: https://asf.alaska.edu/
Tiles required: AP_07405, AP_08324, AP_08572, AP_11788, AP_12350
Processing: Mosaic → Clip to Lucknow boundary
```

#### 6.1.2 Land Use/Land Cover (LULC)

**Source:** ESA WorldCover 2021  
**Provider:** European Space Agency  
**Format:** GeoTIFF  
**Resolution:** 10m (original)  
**Classes:** 11 categories (Tree cover, Cropland, Built-up, etc.)  
**Coordinate System:** EPSG:4326  
**Data Type:** UInt8  
**NoData Value:** 0  
**Accuracy:** >75% globally  
**Update Frequency:** Annual  

**Class Codes:**
- 10: Tree cover
- 20: Shrubland
- 30: Grassland
- 40: Cropland
- 50: Built-up
- 60: Bare/sparse vegetation
- 70: Snow and ice
- 80: Permanent water bodies
- 90: Herbaceous wetland
- 95: Mangroves
- 100: Moss and lichen

#### 6.1.3 Rainfall Data

**Source:** CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)  
**Provider:** UC Santa Barbara Climate Hazards Center  
**Format:** NetCDF or GeoTIFF  
**Resolution:** 0.05° (~5.5 km)  
**Temporal Coverage:** 1981-present  
**Temporal Resolution:** Daily, aggregated to mean annual  
**Coordinate System:** EPSG:4326  
**Data Type:** Float32  
**Units:** mm/year  
**Accuracy:** ±10% in monsoon-dominated regions  

**Processing:**
```
1. Download daily data for 2010-2020
2. Compute mean annual rainfall
3. Resample to DEM grid (bilinear)
```

#### 6.1.4 Geological Data

**Source:** Geological Survey of India (GSI)  
**Format:** Shapefile (vector polygons)  
**Attributes:** Lithology, formation name, age  
**Coordinate System:** EPSG:4326  
**Scale:** 1:50,000 or better  
**Coverage:** Lucknow district and surroundings  

**Lithological Classes:**
- Alluvium
- Sandstone
- Shale
- Limestone
- Granite
- Others

#### 6.1.5 NDVI (Normalized Difference Vegetation Index)

**Source:** MODIS or Landsat  
**Provider:** NASA  
**Format:** GeoTIFF  
**Resolution:** 250m (MODIS) or 30m (Landsat)  
**Temporal Coverage:** 2015-2020 average  
**Data Type:** Float32  
**Value Range:** -1 to +1  
**Processing:** Compute mean NDVI, normalize to 0-1  

#### 6.1.6 Well Data (CGWB)

**Source:** Central Ground Water Board, India  
**Format:** CSV  
**Required Fields:**
- `id`: Unique well identifier
- `lat`: Latitude (decimal degrees)
- `lon`: Longitude (decimal degrees)

**Optional Fields:**
- `water_level`: Depth to water table (m)
- `trend`: Rising/Stable/Declining
- `year`: Observation year

**Data Quality Requirements:**
- Positional accuracy: ±100m
- Temporal alignment: 2015-2020
- Minimum sample size: 500 wells (preferably 2000+)
- Spatial distribution: Representative of entire district

#### 6.1.7 District Boundary

**Source:** Survey of India or state GIS portal  
**Format:** Shapefile (polygon)  
**Coordinate System:** EPSG:4326  
**Attributes:** District name, state, area  
**Topology:** Single polygon, no gaps/overlaps  

### 6.2 Output Data Products

#### 6.2.1 Processed Rasters

**Standard Specifications:**
- **CRS:** EPSG:4326
- **Resolution:** 12.5m (~0.000278°)
- **Grid Size:** 1440 × 1440 pixels (Lucknow)
- **Format:** GeoTIFF with LZW compression
- **Tiling:** 256×256 pixel tiles
- **Metadata:** GDAL-compliant tags

**Products:**
1. `dem_lucknow.tif` - Digital elevation (meters)
2. `slope_lucknow.tif` - Slope (degrees, 0-90)
3. `hillshade_lucknow.tif` - Shaded relief (0-255)
4. `lulc_lucknow.tif` - Land use classes (10-100)
5. `rain_mean_lucknow.tif` - Rainfall (mm/year)
6. `geology_lucknow.tif` - Lithology codes
7. `ndvi_mean_lucknow.tif` - Vegetation index (0-1)
8. `flow_acc_lucknow.tif` - Flow accumulation (cells)
9. `stream_network_lucknow.tif` - Binary streams (0/1)
10. `drainage_density_lucknow.tif` - Density (km/km²)
11. `grp_score_lucknow.tif` - AHP scores (0-1)
12. `grp_class_lucknow.tif` - AHP classes (0/1/2)
13. `predicted_grp_score.tif` - ML probabilities (0-1)
14. `predicted_grp_class.tif` - ML classes (0/1/2)

#### 6.2.2 Vector Outputs

**Shapefile Specifications:**
- **Geometry:** Polygon
- **CRS:** EPSG:4326
- **Files:** .shp, .shx, .dbf, .prj

**Products:**
1. `grp_class_lucknow.shp`
   - **Attributes:** class (0/1/2), score (0-1), area_km2

#### 6.2.3 Tabular Data

**CSV Specifications:**
- **Encoding:** UTF-8
- **Delimiter:** Comma
- **Header:** First row
- **Missing Values:** Empty string or "NaN"

**Products:**
1. `train_samples.csv` - Raw training data
2. `train_samples_clean.csv` - Processed training data
3. `cv_results.csv` - Cross-validation metrics
4. `feature_importances.csv` - Feature rankings
5. `features_summary.csv` - Layer statistics
6. `features_corr.csv` - Correlation matrix
7. `confusion_ml_vs_ahp.csv` - Agreement matrix

#### 6.2.4 Machine Learning Models

**Pickle Format:**
- **Library:** scikit-learn 1.3+
- **Object:** RandomForestClassifier
- **Compatibility:** Python 3.9-3.11
- **Security Warning:** Only load trusted models

**Products:**
1. `rf_baseline.pkl` - Trained Random Forest

#### 6.2.5 Visualizations

**PNG Specifications:**
- **Resolution:** 300 DPI
- **Color:** RGB
- **Dimensions:** Variable (typically 1600×1200 or 2400×1800)

**Products:**
- Confusion matrices
- Feature importance charts
- Correlation heatmaps
- SHAP summary plots
- Map figures

### 6.3 Data Storage and Organization

**Directory Structure:**
```
watershed-up/
├── data/
│   ├── raw/                    # Original downloaded data
│   │   ├── dem_copernicus_glo30.tif (archived)
│   │   ├── lucknow_dem_clipped.tif (ALOS)
│   │   ├── lucknow_Water_Level_WDC.csv
│   │   ├── wells_cgwb.csv
│   │   ├── lucknow_shp/       # District boundary
│   │   ├── AP_*/              # ALOS tiles
│   │   └── stage3/            # Geology, NDVI
│   │
│   └── processed/              # Processing outputs
│       ├── dem_lucknow.tif
│       ├── slope_lucknow.tif
│       ├── lulc_lucknow.tif
│       ├── grp_*.tif
│       ├── stage3/            # Advanced features
│       │   ├── geology_lucknow.tif
│       │   ├── ndvi_mean_lucknow.tif
│       │   ├── flow_acc_lucknow.tif
│       │   ├── drainage_density_lucknow.tif
│       │   ├── features_stack.tif
│       │   ├── features_*.csv
│       │   └── figs/
│       │
│       ├── stage4/            # ML outputs
│       │   ├── train_samples*.csv
│       │   ├── predicted_grp_*.tif
│       │   ├── cv_results.csv
│       │   ├── feature_importances.csv
│       │   ├── confusion_matrix.png
│       │   └── figs_shap/
│       │
│       └── stage5_quality_check/  # Comparison figures
│
├── models/
│   └── rf_baseline.pkl
│
├── backups/
│   └── stage4_copernicus_20251025/  # Old DEM results
│
├── src/                        # Processing scripts
├── app/                        # Visualization platform
├── configs/                    # Configuration files
├── docs/                       # Documentation
└── notebooks/                  # Jupyter demos
```

### 6.4 Data Quality Standards

**Acceptance Criteria:**
1. **Spatial Alignment:** All rasters must share identical extent, resolution, CRS
2. **Completeness:** NoData pixels <20% of total area
3. **Consistency:** Value ranges within expected bounds (e.g., slope 0-90°)
4. **Accuracy:** Positional accuracy ±30m RMSE
5. **Temporal Coherence:** Data from within 5-year window

**Quality Checks:**
- Automated CRS verification
- Extent/resolution consistency check
- NaN value inventory
- Statistical outlier detection
- Visual inspection of outputs

---

## 7. System Architecture

### 7.1 System Overview

**Architecture Pattern:** Modular Pipeline with Web Frontend

**Components:**
1. **Data Preprocessing Layer** - Batch processing scripts
2. **Analysis Layer** - AHP and ML modules
3. **Presentation Layer** - Streamlit web application
4. **Storage Layer** - Filesystem-based data management

**Data Flow:**
```
Raw Data → Preprocessing → Feature Engineering → Modeling → Visualization
                                                              ↓
                                                        Export/Download
```

### 7.2 Component Architecture

#### 7.2.1 Processing Scripts (`src/`)

**Module Organization:**

```
src/
├── preprocess.py              # Stage 1: DEM processing
├── preprocess_lulc.py         # Stage 2: LULC
├── preprocess_rain.py         # Stage 2: Rainfall
├── ahp.py                     # AHP: Slope only
├── ahp_with_lulc.py           # AHP: Slope + LULC
├── ahp_with_rain.py           # AHP: Slope + LULC + Rain
├── preprocess_stage3.py       # Stage 3: Geology + NDVI
├── derive_drainage.py         # Stage 3: Hydrology
├── features_stack.py          # Stage 3: Feature combination
├── visualize_stage3.py        # Stage 3: Plots
├── sample_wells.py            # Stage 4: Training data
├── clean_samples.py           # Stage 4: Data cleaning
├── train_model.py             # Stage 4: ML training
├── predict_map.py             # Stage 4: ML prediction
├── compare_with_ahp.py        # Stage 4: Comparison
├── shap_explain.py            # Stage 4: Interpretability
├── check_data.py              # Utility: Data validation
├── mosaic_and_clip_dem.py     # Utility: DEM mosaicking
└── quality_check_stage5.py    # Utility: Quality comparison
```

**Design Principles:**
- **Single Responsibility:** Each script performs one well-defined task
- **Idempotency:** Can re-run without side effects
- **Logging:** Print progress to stdout
- **Error Handling:** Graceful failures with informative messages

#### 7.2.2 Visualization Platform (`app/`)

**Architecture:** Multi-Page Streamlit Application

```
app/
├── main.py                    # Entry point, routing
├── README.md                  # Platform documentation
└── pages/
    ├── __init__.py
    ├── home.py                # Overview and legend
    ├── interactive_map.py     # Folium mapping
    ├── data_layers.py         # Layer explorer
    ├── model_insights.py      # ML performance
    ├── statistical_analysis.py # Statistics
    ├── well_validation.py     # Well-based validation
    └── export_download.py     # Data download
```

**Framework:** Streamlit 1.28+  
**State Management:** Session state for user selections  
**Caching:** `@st.cache_data` for heavy computations  

#### 7.2.3 Configuration (`configs/`)

**config.yml** (Optional - for future parameterization):
```yaml
study_area:
  name: "Lucknow District"
  boundary: "data/raw/lucknow_shp/lucknow.shp"

dem:
  source: "data/processed/lucknow_dem_clipped.tif"
  resolution: 12.5  # meters

ahp:
  weights:
    slope: 0.5
    lulc: 0.3
    rain: 0.2

ml:
  algorithm: "RandomForest"
  n_estimators: 200
  cv_folds: 5
  random_state: 42
```

#### 7.2.4 Documentation (`docs/`)

**Content:**
- `SRS.md` - This document
- `VISUALIZATION_PLATFORM_GUIDE.md` - User guide
- `PLATFORM_SUMMARY.md` - Executive summary
- `DEMO_SCRIPT.md` - Presentation script
- `STAGE*_*.md` - Stage-specific documentation
- `thesis_progress_stage*.tex` - LaTeX thesis chapters

### 7.3 Deployment Architecture

#### 7.3.1 Local Deployment (Current)

**Environment:** Conda virtual environment  
**Installation:**
```bash
conda env create -f environment.yml
conda activate watershed-up
streamlit run app/main.py
```

**Access:** `http://localhost:8501`

#### 7.3.2 Server Deployment (Future)

**Options:**
1. **Streamlit Cloud:**
   - Pros: Free, managed, automatic updates from Git
   - Cons: Limited resources, public access

2. **Docker Container:**
   - Dockerfile for reproducibility
   - Deploy to AWS/Azure/GCP
   - Scalable with Kubernetes

3. **On-Premise Server:**
   - Internal university/department server
   - Controlled access via VPN
   - Integration with existing systems

**Recommended Stack for Production:**
- Nginx reverse proxy
- HTTPS with SSL certificate
- Authentication layer (OAuth2)
- Rate limiting and caching
- Backup and disaster recovery

### 7.4 Technology Stack Summary

**Programming Languages:**
- Python 3.11 (primary)
- HTML/CSS/JavaScript (Streamlit-generated)

**Core Frameworks:**
- Streamlit 1.28+ (web framework)
- Scikit-learn 1.3+ (machine learning)
- Rasterio 1.3+ (geospatial raster)
- GeoPandas 0.14+ (geospatial vector)

**Key Libraries:**
- NumPy <2.0 (numerical)
- Pandas 2.x (data manipulation)
- Matplotlib 3.7+ (plotting)
- Seaborn 0.12+ (statistical viz)
- Folium 0.15+ (interactive maps)
- SHAP 0.43+ (interpretability)

**Development Tools:**
- Git (version control)
- Conda (environment management)
- VS Code (IDE)
- Jupyter (exploratory analysis)

**Data Formats:**
- GeoTIFF (rasters)
- Shapefile (vectors)
- CSV (tables)
- Pickle (models)
- PNG (figures)

---

## 8. Appendices

### 8.1 Appendix A: Glossary of Terms

| Term | Definition |
|------|------------|
| **Aquifer** | Underground layer of water-bearing rock/sediment |
| **Recharge** | Process of water infiltrating to replenish groundwater |
| **Potential Zone** | Area with favorable conditions for groundwater recharge |
| **DEM** | Digital representation of terrain elevation |
| **Slope** | Rate of change in elevation, indicator of runoff vs. infiltration |
| **Flow Accumulation** | Count of upslope cells draining through each cell |
| **Drainage Density** | Total stream length per unit area |
| **LULC** | Classification of land surface (forest, urban, cropland, etc.) |
| **NDVI** | Satellite-derived vegetation index (greenness) |
| **AHP** | Multi-criteria decision method using weighted linear combination |
| **Random Forest** | Ensemble learning method using multiple decision trees |
| **Cross-Validation** | Model evaluation by splitting data into training/test sets |
| **Feature Importance** | Measure of each variable's contribution to predictions |
| **SHAP** | Method to explain individual predictions |
| **Confusion Matrix** | Table comparing predicted vs. actual classes |

### 8.2 Appendix B: Acronyms

- **AI:** Artificial Intelligence
- **AHP:** Analytic Hierarchy Process
- **ALOS:** Advanced Land Observing Satellite
- **API:** Application Programming Interface
- **CGWB:** Central Ground Water Board
- **CHIRPS:** Climate Hazards Group InfraRed Precipitation with Station data
- **CRS:** Coordinate Reference System
- **CSV:** Comma-Separated Values
- **CV:** Cross-Validation
- **DEM:** Digital Elevation Model
- **ESA:** European Space Agency
- **GIS:** Geographic Information System
- **GRPZ:** Groundwater Recharge Potential Zone
- **GSI:** Geological Survey of India
- **JAXA:** Japan Aerospace Exploration Agency
- **LULC:** Land Use/Land Cover
- **ML:** Machine Learning
- **MODIS:** Moderate Resolution Imaging Spectroradiometer
- **NDVI:** Normalized Difference Vegetation Index
- **PNG:** Portable Network Graphics
- **RF:** Random Forest
- **RMSE:** Root Mean Square Error
- **RS:** Remote Sensing
- **SHAP:** SHapley Additive exPlanations
- **SRS:** Software Requirements Specification
- **TIF/TIFF:** Tagged Image File Format
- **UI:** User Interface
- **WGS84:** World Geodetic System 1984 (EPSG:4326)

### 8.3 Appendix C: Sample Workflows

#### C.1 Complete Processing Workflow (Stages 1-5)

```bash
# Activate environment
conda activate watershed-up

# Stage 1: DEM Processing
python src/preprocess.py

# Stage 2: Multi-Criteria Integration
python src/preprocess_lulc.py
python src/preprocess_rain.py
python src/ahp_with_rain.py

# Stage 3: Advanced Features
python src/preprocess_stage3.py
python src/derive_drainage.py
python src/features_stack.py
python src/visualize_stage3.py

# Stage 4: Machine Learning
python src/sample_wells.py \
    --stack data/processed/stage3/features_stack.tif \
    --wells data/raw/wells_cgwb.csv \
    --out data/processed/stage4/train_samples.csv

python src/clean_samples.py

python src/train_model.py \
    --in data/processed/stage4/train_samples_clean.csv \
    --out_dir models \
    --cv_k 5

python src/predict_map.py \
    --stack data/processed/stage3/features_stack.tif \
    --model models/rf_baseline.pkl \
    --out_dir data/processed/stage4

python src/compare_with_ahp.py
python src/shap_explain.py

# Stage 5: Quality Check
python scripts/quality_check_stage5.py

# Launch Platform
streamlit run app/main.py
```

#### C.2 Quick Start for New Study Area

1. **Prepare Data:**
   - Download DEM covering study area
   - Acquire district boundary shapefile
   - Collect well data CSV

2. **Configure:**
   - Update file paths in scripts
   - Set study area boundary

3. **Run Pipeline:**
   - Execute Stages 1-4 in sequence
   - Launch visualization platform

4. **Validate:**
   - Visual inspection in platform
   - Compare with known field conditions
   - Iterate on weights/parameters

### 8.4 Appendix D: System Requirements Summary

**Minimum System:**
- CPU: Dual-core 2.0 GHz
- RAM: 8 GB
- Storage: 50 GB
- OS: Windows 10 / Ubuntu 20.04 / macOS 11
- Python: 3.9
- Browser: Chrome 90+

**Recommended System:**
- CPU: Quad-core 3.0 GHz
- RAM: 16 GB
- Storage: 100 GB SSD
- OS: Latest stable
- Python: 3.11
- Browser: Latest Chrome/Firefox

**Server Deployment:**
- CPU: 8+ cores
- RAM: 32 GB
- Storage: 200 GB SSD (RAID)
- Network: 100 Mbps, static IP
- Backup: Daily incremental

### 8.5 Appendix E: Testing Requirements

#### E.1 Unit Testing

**Scope:** Individual functions in processing scripts

**Test Cases:**
- DEM clipping produces correct extent
- Slope values are in range [0, 90]
- Feature stack has correct number of bands
- Model achieves >85% CV accuracy on test data

**Framework:** pytest (future implementation)

#### E.2 Integration Testing

**Scope:** End-to-end pipeline execution

**Test Cases:**
- Stage 1-4 pipeline completes without errors
- All expected output files are generated
- Output file formats are valid (GeoTIFF, Shapefile, CSV)
- Spatial alignment is maintained

#### E.3 User Acceptance Testing

**Scope:** Visualization platform usability

**Test Participants:**
- Water resource planners (3-5)
- GIS analysts (2-3)
- Non-technical stakeholders (5-10)

**Test Scenarios:**
- Navigate to interactive map and toggle layers
- Download GRPZ classification shapefile
- Find feature importance chart
- Validate predictions against well data

**Success Criteria:**
- 90% of tasks completed without assistance
- Average task completion time <5 minutes
- User satisfaction rating ≥4/5

### 8.6 Appendix F: Maintenance and Support

**Maintenance Schedule:**
- **Weekly:** Monitor for new LULC/rainfall data releases
- **Monthly:** Review user feedback, update documentation
- **Quarterly:** Software dependency updates
- **Annually:** Model retraining with new well data

**Support Channels:**
- GitHub Issues: Bug reports, feature requests
- Email: Technical questions, collaboration
- Documentation: User guide, FAQs, video tutorials

**Update Process:**
1. Develop fix/feature in development branch
2. Test on sample dataset
3. Update documentation
4. Merge to main branch
5. Deploy to production
6. Notify users of changes

### 8.7 Appendix G: Future Enhancements

**Planned Features (Priority 1):**
1. Multi-temporal analysis (seasonal groundwater dynamics)
2. Uncertainty quantification for predictions
3. Ensemble modeling (RF + XGBoost + SVM)
4. Real-time data integration APIs

**Planned Features (Priority 2):**
5. 3D terrain visualization
6. Scenario modeling (climate change, land use change)
7. Automated report generation (PDF)
8. Mobile-responsive design

**Planned Features (Priority 3):**
9. User authentication and roles
10. Cloud deployment (AWS/Azure)
11. Multi-language support (Hindi, English)
12. Integration with state water department systems

---

## Document Approval

**Prepared By:**  
Pavan Kumar Eleti    
IIITL  
Date: October 27, 2025



---

**End of Software Requirements Specification**

*This document is subject to updates as the project evolves. Version control is maintained via Git repository.*
