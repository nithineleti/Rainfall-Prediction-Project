# Watershed-UP Code Documentation Index

## Overview

This directory contains **detailed technical documentation** for every Python script in the Watershed-UP project. Each document explains:
- **What we have done** (implementation details)
- **Why we did it** (scientific rationale and design decisions)
- **How it works** (algorithms, parameters, mathematics)
- **Usage examples** (command-line execution)
- **Integration** (dependencies and data flow)

---

## Documentation Organization

### **Stage 1: DEM Processing** 
| File | Documentation | Purpose |
|------|--------------|---------|
| `src/preprocess.py` | [01_preprocess_py.md](01_preprocess_py.md) | DEM clipping, slope, hillshade |
| `src/mosaic_and_clip_dem.py` | [03_mosaic_and_clip_dem_py.md](03_mosaic_and_clip_dem_py.md) | Mosaic ALOS tiles, clip to boundary |
| `src/check_data.py` | [04_check_data_py.md](04_check_data_py.md) | Validate DEM and data quality |

### **Stage 2: Multi-Criteria Integration**
| File | Documentation | Purpose |
|------|--------------|---------|
| `src/preprocess_lulc.py` | [05_preprocess_lulc_py.md](05_preprocess_lulc_py.md) | Process ESA WorldCover LULC |
| `src/preprocess_rain.py` | [06_preprocess_rain_py.md](06_preprocess_rain_py.md) | Process CHIRPS rainfall data |
| `src/ahp.py` | [07_ahp_py.md](07_ahp_py.md) | AHP with slope only |
| `src/ahp_with_lulc.py` | [08_ahp_with_lulc_py.md](08_ahp_with_lulc_py.md) | AHP with slope + LULC |
| `src/ahp_with_rain.py` | [09_ahp_with_rain_py.md](09_ahp_with_rain_py.md) | AHP with slope + LULC + rainfall |

### **Stage 3: Advanced Features**
| File | Documentation | Purpose |
|------|--------------|---------|
| `src/preprocess_stage3.py` | [10_preprocess_stage3_py.md](10_preprocess_stage3_py.md) | Process geology, NDVI layers |
| `src/derive_drainage.py` | [11_derive_drainage_py.md](11_derive_drainage_py.md) | Flow accumulation, stream network, drainage density |
| `src/features_stack.py` | [12_features_stack_py.md](12_features_stack_py.md) | Combine all layers into 9-band raster |
| `src/visualize_stage3.py` | [13_visualize_stage3_py.md](13_visualize_stage3_py.md) | Generate stage 3 figures |

### **Stage 4: Machine Learning**
| File | Documentation | Purpose |
|------|--------------|---------|
| `src/sample_wells.py` | [14_sample_wells_py.md](14_sample_wells_py.md) | Extract features at well locations |
| `src/clean_samples.py` | [15_clean_samples_py.md](15_clean_samples_py.md) | Remove NaNs, impute, validate training data |
| `src/train_model.py` | [02_train_model_py.md](02_train_model_py.md) | **Train Random Forest with spatial CV** |
| `src/predict_map.py` | [16_predict_map_py.md](16_predict_map_py.md) | Generate pixel-wise predictions |
| `src/compare_with_ahp.py` | [17_compare_with_ahp_py.md](17_compare_with_ahp_py.md) | ML vs AHP agreement analysis |
| `src/shap_explain.py` | [18_shap_explain_py.md](18_shap_explain_py.md) | SHAP values for model interpretability |

### **Visualization & Analysis**
| File | Documentation | Purpose |
|------|--------------|---------|
| `src/visualize.py` | [19_visualize_py.md](19_visualize_py.md) | General visualization utilities |
| `src/plot_prediction.py` | [20_plot_prediction_py.md](20_plot_prediction_py.md) | Plot ML predictions |
| `src/plot_predicted_class.py` | [21_plot_predicted_class_py.md](21_plot_predicted_class_py.md) | Plot classified GRPZ |
| `src/inspect_samples.py` | [22_inspect_samples_py.md](22_inspect_samples_py.md) | Inspect training data quality |
| `src/inspect_stack.py` | [23_inspect_stack_py.md](23_inspect_stack_py.md) | Inspect feature stack |

### **Utility Scripts**
| File | Documentation | Purpose |
|------|--------------|---------|
| `src/check_raster.py` | [24_check_raster_py.md](24_check_raster_py.md) | Validate raster metadata, CRS |
| `src/check_lulc.py` | [25_check_lulc_py.md](25_check_lulc_py.md) | Validate LULC classes |
| `src/download_lulc.py` | [26_download_lulc_py.md](26_download_lulc_py.md) | Download ESA WorldCover |
| `scripts/prepare_wells.py` | [27_prepare_wells_py.md](27_prepare_wells_py.md) | Prepare well data from CGWB |
| `scripts/quality_check_stage5.py` | [28_quality_check_stage5_py.md](28_quality_check_stage5_py.md) | Stage 5 comparison figures |

---

## Streamlit Visualization Platform

### **Main Application**
| File | Documentation | Purpose |
|------|--------------|---------|
| `app/main.py` | [30_app_main_py.md](30_app_main_py.md) | Entry point, navigation, sidebar |

### **Application Pages**
| File | Documentation | Purpose |
|------|--------------|---------|
| `app/pages/home.py` | [31_page_home_py.md](31_page_home_py.md) | Project overview, legend, data checker |
| `app/pages/interactive_map.py` | [32_page_interactive_map_py.md](32_page_interactive_map_py.md) | Folium maps with ML/AHP toggle |
| `app/pages/data_layers.py` | [33_page_data_layers_py.md](33_page_data_layers_py.md) | Explore all 9+ layers |
| `app/pages/model_insights.py` | [34_page_model_insights_py.md](34_page_model_insights_py.md) | Feature importance, CV results |
| `app/pages/statistical_analysis.py` | [35_page_statistical_analysis_py.md](35_page_statistical_analysis_py.md) | Correlations, distributions |
| `app/pages/well_validation.py` | [36_page_well_validation_py.md](36_page_well_validation_py.md) | CGWB well validation |
| `app/pages/export_download.py` | [37_page_export_download_py.md](37_page_export_download_py.md) | Download GeoTIFF, Shapefile, CSV |

---

## Quick Reference

### **Complete Pipeline Execution Order**

```bash
# Stage 1: DEM Processing
python src/mosaic_and_clip_dem.py       # Mosaic ALOS tiles
python src/preprocess.py                 # Slope, hillshade
python src/check_data.py                 # Validate outputs

# Stage 2: Multi-Criteria AHP
python src/preprocess_lulc.py            # LULC alignment
python src/preprocess_rain.py            # Rainfall alignment
python src/ahp_with_rain.py              # Final AHP (slope+LULC+rain)

# Stage 3: Advanced Features
python src/preprocess_stage3.py          # Geology, NDVI
python src/derive_drainage.py            # Flow, streams, drainage density
python src/features_stack.py             # Combine to 9-band raster
python src/visualize_stage3.py           # Correlation plots

# Stage 4: Machine Learning
python src/sample_wells.py               # Extract training samples
python src/clean_samples.py              # Clean NaNs
python src/train_model.py                # Train RF (5-fold spatial CV)
python src/predict_map.py                # Predict entire raster
python src/compare_with_ahp.py           # ML vs AHP confusion matrix
python src/shap_explain.py               # SHAP interpretability

# Stage 5: Quality Check
python scripts/quality_check_stage5.py   # Compare old vs new DEM

# Launch Platform
streamlit run app/main.py                # Interactive visualization
```

### **Most Important Files to Understand**

**If you're learning the methodology:**
1. [01_preprocess_py.md](01_preprocess_py.md) - Foundation: How we process terrain
2. [09_ahp_with_rain_py.md](09_ahp_with_rain_py.md) - Expert-driven approach
3. [02_train_model_py.md](02_train_model_py.md) - Machine learning core
4. [11_derive_drainage_py.md](11_derive_drainage_py.md) - Hydrological features
5. [12_features_stack_py.md](12_features_stack_py.md) - Data integration

**If you're using the platform:**
1. [30_app_main_py.md](30_app_main_py.md) - How the app works
2. [32_page_interactive_map_py.md](32_page_interactive_map_py.md) - Map functionality
3. [34_page_model_insights_py.md](34_page_model_insights_py.md) - Understanding results

**If you're extending to new areas:**
1. [03_mosaic_and_clip_dem_py.md](03_mosaic_and_clip_dem_py.md) - DEM preparation
2. [14_sample_wells_py.md](14_sample_wells_py.md) - Training data creation
3. [16_predict_map_py.md](16_predict_map_py.md) - Generating predictions

---

## Key Concepts Explained

### **1. Spatial Cross-Validation**
- **Why needed:** Standard random CV invalid for spatial data due to autocorrelation
- **Our approach:** K-Means clustering of well coordinates → 5 geographic folds
- **Impact:** Realistic accuracy (95.7%); random CV would overestimate by ~20%
- **Documented in:** [02_train_model_py.md](02_train_model_py.md)

### **2. Analytic Hierarchy Process (AHP)**
- **What:** Multi-criteria decision analysis using weighted linear combination
- **Weights:** Slope (50%), LULC (30%), Rainfall (20%) from literature
- **Purpose:** Expert-driven baseline for comparison with ML
- **Documented in:** [07-09_ahp_*.md](07_ahp_py.md)

### **3. Feature Engineering**
- **9 features total:** slope, LULC, rain, geology, NDVI, flow_acc, stream, drainage_density, grp_score
- **Multi-source integration:** DEM (ALOS), LULC (ESA), Rain (CHIRPS), Wells (CGWB)
- **Alignment:** All resampled to 12.5m grid, EPSG:4326
- **Documented in:** [12_features_stack_py.md](12_features_stack_py.md)

### **4. D8 Flow Algorithm**
- **Purpose:** Compute water flow direction from DEM
- **Method:** Each cell flows to steepest downslope neighbor (8 directions)
- **Outputs:** Flow accumulation, stream network, drainage density
- **Documented in:** [11_derive_drainage_py.md](11_derive_drainage_py.md)

### **5. SHAP Interpretability**
- **What:** SHapley Additive exPlanations - game-theoretic feature attribution
- **Purpose:** Explain individual predictions (which features drove this classification?)
- **Usage:** Builds trust with stakeholders, validates model logic
- **Documented in:** [18_shap_explain_py.md](18_shap_explain_py.md)

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    RAW DATA SOURCES                         │
├─────────────────────────────────────────────────────────────┤
│ • ALOS PALSAR DEM (12.5m)      → Stage 1                   │
│ • ESA WorldCover LULC (10m)    → Stage 2                   │
│ • CHIRPS Rainfall (5.5km)      → Stage 2                   │
│ • Geology Shapefile            → Stage 3                   │
│ • MODIS NDVI (250m)            → Stage 3                   │
│ • CGWB Well Data (2000 wells)  → Stage 4                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  STAGE 1: DEM PROCESSING                    │
├─────────────────────────────────────────────────────────────┤
│ mosaic_and_clip_dem.py  → lucknow_dem_clipped.tif          │
│ preprocess.py           → dem, slope, hillshade             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              STAGE 2: MULTI-CRITERIA AHP                    │
├─────────────────────────────────────────────────────────────┤
│ preprocess_lulc.py      → lulc_lucknow.tif                 │
│ preprocess_rain.py      → rain_mean_lucknow.tif            │
│ ahp_with_rain.py        → grp_score, grp_class             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│           STAGE 3: ADVANCED FEATURES                        │
├─────────────────────────────────────────────────────────────┤
│ preprocess_stage3.py    → geology, ndvi                    │
│ derive_drainage.py      → flow_acc, stream, drain_density  │
│ features_stack.py       → features_stack.tif (9 bands)     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│            STAGE 4: MACHINE LEARNING                        │
├─────────────────────────────────────────────────────────────┤
│ sample_wells.py         → train_samples.csv                │
│ clean_samples.py        → train_samples_clean.csv          │
│ train_model.py          → rf_baseline.pkl (95.7% acc)      │
│ predict_map.py          → predicted_grp_class.tif          │
│ shap_explain.py         → SHAP summary plot                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│         VISUALIZATION PLATFORM (Streamlit)                  │
├─────────────────────────────────────────────────────────────┤
│ app/main.py             → Navigation, sidebar              │
│ pages/interactive_map   → Folium mapping                   │
│ pages/model_insights    → Feature importance, CV           │
│ pages/export_download   → GeoTIFF, Shapefile, CSV          │
└─────────────────────────────────────────────────────────────┘
```

---

## Documentation Standards

Each documentation file follows this structure:

1. **Overview** - File purpose, dependencies, outputs
2. **What We Have Done** - Detailed implementation walkthrough
3. **Why We Did It** - Scientific rationale, design decisions
4. **Technical Details** - Algorithms, mathematics, parameters
5. **Input/Output Specs** - Data formats, file paths
6. **Usage Examples** - Command-line execution
7. **Error Handling** - Common issues and fixes
8. **Integration** - Upstream/downstream dependencies
9. **Future Improvements** - Planned enhancements
10. **References** - Academic citations, software docs

---

## Version History

| Date | Author | Changes |
|------|--------|---------|
| Oct 27, 2025 | Pavan Kumar Eletti | Initial documentation creation |

---

## Contact & Support

**Questions about code?** Refer to individual documentation files  
**Questions about methodology?** See thesis chapters in `docs/thesis_progress_stage*.tex`  
**Questions about platform?** See `docs/VISUALIZATION_PLATFORM_GUIDE.md`  

**Project Status:** Complete (Stage 5 finished Oct 25, 2025)  
**Platform Status:** Functional (fixing NumPy/Folium dependencies)

---

## Next Steps for Users

### **For Developers:**
1. Start with this index to understand project structure
2. Read 01-05 (preprocessing) to understand data flow
3. Read 02 (train_model) to understand ML methodology
4. Explore app documentation for platform architecture

### **For Researchers:**
1. Focus on methodology files: 02, 09, 11, 12, 18
2. Review SHAP and feature importance explanations
3. Understand spatial CV rationale
4. Compare AHP vs ML approaches

### **For Stakeholders:**
1. Read app documentation (30-37) for platform usage
2. Understand interactive_map and model_insights pages
3. Learn how to download and use outputs
4. Review validation methodology in well_validation docs

---

**Total Scripts Documented:** 37 files  
**Total Documentation Pages:** ~300 pages (when complete)  
**Average Detail Level:** 5,000-10,000 words per file  
**Completion Status:** 2/37 complete, 35 in progress

---

**Last Updated:** October 27, 2025  
**Next Review:** Before thesis final submission
