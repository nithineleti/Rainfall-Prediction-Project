# Research Methodology

**Project:** Watershed-UP - Groundwater Potential Zone Mapping Platform  
**Author:** Pavan Kumar Eletti  
**Date:** November 2025

---

## 📋 Overview

This document outlines the research methodology employed in the Watershed-UP platform for mapping groundwater potential zones and prioritizing watersheds for sustainable water resource management in Lucknow, India.

---

## 1. Research Framework

### 1.1 Research Objectives
1. **Primary Objective:** Develop an AI-powered platform for groundwater potential zone mapping
2. **Secondary Objectives:**
   - Integrate multi-source geospatial data (DEM, LULC, rainfall, soil, geology)
   - Engineer relevant hydrological and topographic features
   - Train and validate machine learning models for classification
   - Delineate and characterize watersheds for prioritization
   - Build an interactive web platform for decision support

### 1.2 Study Area
- **Location:** Lucknow District, Uttar Pradesh, India
- **Coordinates:** 26°30'N to 27°10'N, 80°30'E to 81°13'E
- **Area:** ~2,500 km²
- **Climate:** Humid subtropical with distinct monsoon season
- **Geology:** Indo-Gangetic alluvial plain
- **Population:** ~4.6 million (as of 2021 census)

---

## 2. Data Collection & Sources

### 2.1 Remote Sensing Data

| Data Type | Source | Resolution | Year | Purpose |
|-----------|--------|------------|------|---------|
| **DEM** | ALOS PALSAR | 12.5m | 2011 | Terrain analysis, watershed delineation |
| **LULC** | ESRI Land Cover | 10m | 2021 | Land use classification |
| **Rainfall** | CHIRPS | 0.25° (~25km) | 2000-2023 | Precipitation patterns |
| **NDVI** | Landsat 8/9 | 30m | 2020-2023 | Vegetation health |

### 2.2 Ground Truth Data
- **Well Locations:** Field surveys and government records (n=500+)
- **Well Classification:** High, Medium, Low groundwater potential based on:
  - Static water level (depth to water table)
  - Yield (liters per minute)
  - Water quality parameters
  - Seasonal variation

### 2.3 Ancillary Data
- **Soil Texture:** Clay, sand, silt content from soil surveys
- **Geology:** Geological maps from Geological Survey of India (GSI)
- **Administrative Boundaries:** District and block boundaries

---

## 3. Feature Engineering

### 3.1 Topographic Features (6)
Derived from ALOS PALSAR DEM (12.5m):

1. **Slope** - Rate of elevation change (degrees)
   - Formula: `slope = arctan(√(dz/dx)² + (dz/dy)²)`
   - Tool: `gdaldem slope`

2. **Aspect** - Direction of slope (degrees, 0-360°)
   - Formula: `aspect = arctan2(dz/dy, -dz/dx)`
   - Tool: `gdaldem aspect`

3. **Curvature** - Surface convexity/concavity
   - Types: Plan, profile, total curvature
   - Tool: WhiteboxTools `PlanCurvature`

4. **Terrain Ruggedness Index (TRI)**
   - Quantifies topographic heterogeneity
   - Formula: `TRI = √Σ(elev_cell - elev_center)²`
   - Tool: `gdaldem TRI`

5. **Topographic Position Index (TPI)**
   - Relative elevation to surrounding cells
   - Tool: WhiteboxTools `TPI`

6. **Topographic Wetness Index (TWI)**
   - Quantifies water accumulation potential
   - Formula: `TWI = ln(A / tan(β))` where A=upslope area, β=slope
   - Tool: WhiteboxTools `WetnessIndex`

### 3.2 Hydrological Features (4)

7. **Flow Accumulation**
   - Upstream drainage area (number of cells)
   - Method: D8 flow direction algorithm
   - Tool: `pysheds` or WhiteboxTools

8. **Stream Network**
   - Extracted using flow accumulation threshold
   - Threshold: 500 cells (effective area ~19 ha)
   - Tool: `pysheds.grid.extract_river_network`

9. **Drainage Density**
   - Stream length per unit area (km/km²)
   - Calculated per watershed polygon
   - Formula: `DD = ΣL / A` where L=stream length, A=area

10. **Stream Density**
    - Number of stream segments per unit area
    - Formula: `SD = N / A` where N=number of streams, A=area

### 3.3 Land Use/Land Cover Features (3)

11. **Forest Cover %**
    - Percentage of forest area within analysis window
    - Source: ESRI 10m LULC (Class: Trees)

12. **Agriculture %**
    - Percentage of agricultural land
    - Source: ESRI 10m LULC (Class: Crops)

13. **LULC Diversity (Shannon Index)**
    - Quantifies land use heterogeneity
    - Formula: `H = -Σ(p_i × ln(p_i))` where p_i = proportion of class i

### 3.4 Climate Features (4)

14. **Annual Rainfall** - Total yearly precipitation (mm)
15. **Monsoon Rainfall** - June-September (mm)
16. **Winter Rainfall** - December-February (mm)
17. **Pre-Monsoon Rainfall** - March-May (mm)

**Total:** 17 feature bands stacked into multi-band GeoTIFF

---

## 4. Machine Learning Pipeline

### 4.1 Training Data Preparation

**Sampling Strategy:**
- Extract feature values at well locations (point sampling)
- Buffer wells by 30m to account for GPS uncertainty
- Balance classes using SMOTE (Synthetic Minority Over-sampling Technique)
- Train/test split: 80/20 stratified by class

**Data Cleaning:**
- Remove wells with missing data
- Filter outliers (±3 standard deviations)
- Normalize features (StandardScaler or MinMaxScaler)

### 4.2 Model Selection & Training

**Algorithm:** XGBoost (Gradient Boosting Decision Trees)

**Rationale:**
- Handles non-linear relationships
- Robust to outliers and missing data
- Built-in feature importance
- Fast training and prediction

**Hyperparameter Optimization:**
- Method: GridSearchCV with 5-fold cross-validation
- Parameters tuned:
  - `n_estimators`: [50, 100, 200]
  - `max_depth`: [3, 5, 7, 10]
  - `learning_rate`: [0.01, 0.05, 0.1]
  - `subsample`: [0.8, 0.9, 1.0]
  - `colsample_bytree`: [0.8, 0.9, 1.0]

**Training Process:**
```python
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV

model = XGBClassifier(
    objective='multi:softmax',
    num_class=3,  # High, Medium, Low
    random_state=42
)

param_grid = { ... }
grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1_macro')
grid_search.fit(X_train, y_train)
```

### 4.3 Model Evaluation

**Metrics:**
- **Accuracy** - Overall correct predictions
- **Precision** - Correct positive predictions per class
- **Recall** - True positives detected per class
- **F1-Score** - Harmonic mean of precision and recall
- **ROC-AUC** - Area under receiver operating characteristic curve
- **Confusion Matrix** - Detailed classification breakdown

**Validation:**
- 5-fold cross-validation on training set
- Independent test set evaluation
- Spatial cross-validation (leave-one-watershed-out)

### 4.4 Model Interpretation

**SHAP (SHapley Additive exPlanations):**
- Calculate feature contributions for each prediction
- Global feature importance ranking
- Local explanations for individual predictions
- Partial dependence plots for feature effects

---

## 5. Watershed Delineation & Characterization

### 5.1 Watershed Delineation

**Method:** D8 Flow Direction Algorithm

**Steps:**
1. **Pit Filling** - Remove spurious sinks in DEM
   - Tool: `pysheds.grid.fill_pits()`
2. **Flow Direction** - Compute D8 flow direction grid
   - Each cell flows to steepest neighbor (8 directions)
3. **Flow Accumulation** - Count upstream cells
4. **Watershed Delineation** - Trace contributing area to pour points
   - Pour points: stream network endpoints or specified outlets

**Watershed Identification:**
- Minimum area threshold: 1 km²
- Maximum area threshold: 100 km²
- Result: 50+ watersheds identified

### 5.2 Morphometric Analysis

**Watershed Characteristics Computed:**

| Parameter | Formula | Description |
|-----------|---------|-------------|
| **Area (A)** | - | Total watershed area (km²) |
| **Perimeter (P)** | - | Watershed boundary length (km) |
| **Length (L)** | - | Longest dimension (km) |
| **Form Factor (Ff)** | A / L² | Watershed shape (circular vs elongated) |
| **Circularity Ratio (Rc)** | 4πA / P² | Degree of circularity |
| **Elongation Ratio (Re)** | √(A/π) / L | Elongation measure |
| **Relief (R)** | max(elev) - min(elev) | Elevation range (m) |
| **Relief Ratio (Rr)** | R / L | Slope steepness |
| **Drainage Density (DD)** | ΣL_stream / A | Stream length per unit area |
| **Stream Frequency (SF)** | N_streams / A | Stream count per unit area |

### 5.3 Prioritization using AHP

**Analytical Hierarchy Process (AHP):**

**Criteria Weights (Expert-based):**
1. Groundwater Potential (40%)
2. Drainage Density (20%)
3. Relief Ratio (15%)
4. LULC Diversity (15%)
5. Forest Cover % (10%)

**Normalization:**
- Each criterion scaled to 0-1 range
- Higher values = higher priority

**Composite Score:**
```
Priority Score = Σ(weight_i × normalized_value_i)
```

**Classification:**
- **High Priority:** Score > 0.7
- **Medium Priority:** 0.4 ≤ Score ≤ 0.7
- **Low Priority:** Score < 0.4

---

## 6. Web Platform Development

### 6.1 Backend Architecture
- **Framework:** FastAPI (Python)
- **Database:** SQLAlchemy with PostgreSQL/SQLite
- **Geospatial Processing:** GeoPandas, Rasterio, Shapely
- **API Design:** RESTful endpoints with OpenAPI documentation

### 6.2 Frontend Architecture
- **Framework:** React 18 with TypeScript
- **Mapping:** Leaflet.js via react-leaflet
- **Charting:** Recharts for data visualization
- **Styling:** Tailwind CSS for responsive design

### 6.3 Deployment
- **Containerization:** Docker with docker-compose
- **CI/CD:** GitHub Actions for automated testing and linting
- **Hosting:** (To be determined - AWS/Azure/GCP)

---

## 7. Validation & Accuracy Assessment

### 7.1 Model Validation Results

**Test Set Performance (n=100 wells):**
- **Overall Accuracy:** 79.6%
- **High GWP Class:** Precision=82%, Recall=78%
- **Medium GWP Class:** Precision=76%, Recall=80%
- **Low GWP Class:** Precision=78%, Recall=81%
- **Macro F1-Score:** 79.8%
- **ROC-AUC:** 0.85

### 7.2 Spatial Validation
- Predictions validated against independent well data not used in training
- Spatial autocorrelation analysis (Moran's I) to check for clustering

### 7.3 Expert Validation
- Watershed prioritization reviewed by local water resource experts
- Field verification of high-priority watersheds

---

## 8. Limitations & Future Work

### 8.1 Current Limitations
1. **Temporal Coverage:** Single-year LULC and DEM (static analysis)
2. **Ground Truth:** Limited well data (n=500) for large study area
3. **Hydrogeological Data:** Lack of detailed aquifer parameters
4. **Validation:** Limited independent validation dataset
5. **Scale:** 30m resolution may miss local-scale variations

### 8.2 Future Research Directions
1. **Time-Series Analysis:** Integrate multi-year data for temporal trends
2. **Deep Learning:** Explore CNN/LSTM architectures for spatial-temporal modeling
3. **Uncertainty Quantification:** Implement Bayesian approaches for prediction intervals
4. **Multi-Region Extension:** Apply methodology to other districts/states
5. **Real-Time Updates:** Automated data pipelines for continuous monitoring
6. **Groundwater Modeling:** Integration with MODFLOW for aquifer simulation

---

## 9. Ethical Considerations

### 9.1 Data Privacy
- Well location data anonymized to protect landowner privacy
- Aggregated results provided at watershed scale, not individual parcels

### 9.2 Accessibility
- Platform designed for free public access
- Open-source codebase for transparency and reproducibility
- Documentation provided in English and Hindi (planned)

### 9.3 Responsible Use
- Results intended for planning purposes, not regulatory enforcement
- Recommendations should be validated by local authorities before implementation
- Platform does not guarantee groundwater availability, only potential zones

---

## 10. References

### Key Publications
1. Rahmati, O., et al. (2019). "Machine learning approaches for spatial modeling of agricultural droughts in the south-east region of Queensland Australia." *Science of The Total Environment*, 699, 134230.

2. Naghibi, S. A., et al. (2017). "GIS-based groundwater potential mapping using boosted regression tree, classification and regression tree, and random forest machine learning models in Iran." *Environmental Monitoring and Assessment*, 189(1), 44.

3. Tehrany, M. S., et al. (2019). "Evaluating the application of the statistical index method in flood susceptibility mapping and its comparison with frequency ratio and logistic regression methods." *Geomatics, Natural Hazards and Risk*, 10(1), 79-101.

### Data Sources
- **ALOS PALSAR DEM:** JAXA (Japan Aerospace Exploration Agency)
- **ESRI Land Cover:** Esri 2021 Land Cover dataset
- **CHIRPS Rainfall:** Climate Hazards Group, UC Santa Barbara
- **Well Data:** Central Ground Water Board (CGWB), Government of India

### Software & Tools
- **Python Libraries:** scikit-learn, XGBoost, SHAP, GeoPandas, Rasterio, pysheds
- **GIS Tools:** GDAL/OGR, WhiteboxTools
- **Web Frameworks:** FastAPI, React, Leaflet
- **Development:** VS Code, Git, GitHub, Docker

---

## Appendices

### Appendix A: Feature Correlation Matrix
*(See `docs/analysis/ENHANCED_FEATURES_SUMMARY.md`)*

### Appendix B: Hyperparameter Tuning Results
*(See `docs/research/MODEL_TRAINING_RESULTS.md`)*

### Appendix C: Watershed Characterization Tables
*(See `data/tables/watershed_summary.csv`)*

### Appendix D: SHAP Value Analysis
*(See `outputs/shap_summary.png`)*

---

**Document Version:** 1.0.0  
**Last Updated:** November 12, 2025  
**Status:** ✅ Complete
