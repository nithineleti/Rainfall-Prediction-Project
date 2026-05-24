# GRPZ Visualization Platform - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GRPZ Visualization Platform                   │
│                     (Streamlit Web Application)                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Main Application                         │
│                         (app/main.py)                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Navigation sidebar                                     │  │
│  │  • Custom CSS styling                                     │  │
│  │  │  • Page routing                                         │  │
│  │  • Configuration management                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Home Page   │     │ Interactive  │     │ Data Layers  │
│   (🏠)       │     │   Map (🗺️)   │     │    (📊)      │
└──────────────┘     └──────────────┘     └──────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Model     │     │ Statistical  │     │     Well     │
│  Insights    │     │   Analysis   │     │ Validation   │
│    (🤖)      │     │    (📈)      │     │    (🔍)      │
└──────────────┘     └──────────────┘     └──────────────┘
        │
        ▼
┌──────────────┐
│   Export &   │
│   Download   │
│    (📥)      │
└──────────────┘
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Sources                             │
├─────────────────────────────────────────────────────────────────┤
│  • DEM (Elevation)              • LULC (Land Use)               │
│  • Rainfall Data                • NDVI (Vegetation)             │
│  • Geology Maps                 • Well Data (CGWB)              │
│  • Flow Accumulation            • Drainage Density              │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Pipeline                           │
├─────────────────────────────────────────────────────────────────┤
│  1. Preprocessing (src/preprocess*.py)                          │
│  2. Feature Engineering (src/derive_drainage.py)                │
│  3. Feature Stacking (src/features_stack.py)                    │
│  4. Model Training (src/train_model.py)                         │
│  5. Prediction (src/predict_map.py)                             │
│  6. AHP Analysis (src/ahp.py)                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Processed Outputs                           │
├─────────────────────────────────────────────────────────────────┤
│  • Prediction Maps (GeoTIFF)   • Training Data (CSV)           │
│  • Feature Importance           • Validation Metrics            │
│  • Trained Model (.pkl)         • Statistical Reports           │
│  • Comparison Results           • Correlation Matrices          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              Visualization Platform (Streamlit)                  │
├─────────────────────────────────────────────────────────────────┤
│  • Interactive Maps             • Statistical Analysis          │
│  • Data Exploration             • Model Insights                │
│  • Validation Tools             • Export Functions              │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        End Users                                 │
├─────────────────────────────────────────────────────────────────┤
│  • Water Resource Planners      • Policy Makers                │
│  • Researchers                   • GIS Analysts                 │
│  • Stakeholders                  • Decision Makers              │
└─────────────────────────────────────────────────────────────────┘
```

## Page Navigation Flow

```
                    ┌─────────────┐
                    │    Home     │
                    │   (🏠)      │
                    │             │
                    │  • Overview │
                    │  • Legend   │
                    │  • Status   │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │Interactive │  │   Data     │  │   Model    │
    │    Map     │  │  Layers    │  │  Insights  │
    │   (🗺️)     │  │   (📊)     │  │   (🤖)     │
    │            │  │            │  │            │
    │• ML/AHP    │  │• DEM       │  │• Feature   │
    │• Wells     │  │• Slope     │  │  Importance│
    │• Boundary  │  │• LULC      │  │• CV Results│
    │• Stats     │  │• Rainfall  │  │• Confusion │
    └────────────┘  │• NDVI      │  │  Matrix    │
           │        │• Geology   │  └────────────┘
           │        │• Drainage  │         │
           │        └────────────┘         │
           │               │               │
           │               ▼               │
           │        ┌────────────┐         │
           │        │Statistical │         │
           │        │  Analysis  │         │
           │        │   (📈)     │         │
           │        │            │         │
           │        │• Class     │         │
           │        │  Distribution       │
           │        │• Correlations       │
           │        │• Spatial   │         │
           │        │  Patterns  │         │
           │        └────────────┘         │
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
                    ┌────────────┐
                    │    Well    │
                    │ Validation │
                    │   (🔍)     │
                    │            │
                    │• Trends    │
                    │• Cross-tab │
                    │• Metrics   │
                    └──────┬─────┘
                           │
                           ▼
                    ┌────────────┐
                    │  Export &  │
                    │  Download  │
                    │   (📥)     │
                    │            │
                    │• GeoTIFF   │
                    │• Shapefile │
                    │• CSV       │
                    │• Model     │
                    │• Packages  │
                    └────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Web UI)                           │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit 1.28+        │  HTML/CSS (embedded)                  │
│  Folium + Leaflet.js    │  Custom JavaScript (via Streamlit)    │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Visualization Libraries                       │
├─────────────────────────────────────────────────────────────────┤
│  Matplotlib 3.x         │  Seaborn (statistical plots)          │
│  Folium (maps)          │  Streamlit-Folium (integration)       │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Geospatial Processing                          │
├─────────────────────────────────────────────────────────────────┤
│  Rasterio               │  GeoPandas                            │
│  Rioxarray              │  Shapely                              │
│  GDAL/OGR               │  Pyproj                               │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data & Analytics                              │
├─────────────────────────────────────────────────────────────────┤
│  NumPy                  │  Pandas                               │
│  SciPy                  │  Scikit-learn                         │
│  SHAP                   │  Joblib                               │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Options

```
┌─────────────────────────────────────────────────────────────────┐
│                     Local Development                            │
│  • Run on local machine                                         │
│  • Access via localhost:8501                                    │
│  • Ideal for testing and development                            │
│                                                                  │
│  Command: streamlit run app/main.py                             │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Local Network                                │
│  • Deploy on organization server                                │
│  • Access via internal IP                                       │
│  • Suitable for organization-wide use                           │
│                                                                  │
│  Command: streamlit run app/main.py --server.address 0.0.0.0   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Deployment                              │
│  • Streamlit Cloud (free tier available)                       │
│  • AWS, Azure, GCP                                              │
│  • Docker containers                                            │
│  • Accessible globally via URL                                  │
│                                                                  │
│  Options:                                                        │
│  - Streamlit Share (easiest, free)                             │
│  - Docker + Cloud VM                                            │
│  - Kubernetes cluster                                           │
└─────────────────────────────────────────────────────────────────┘
```

## User Workflow

```
┌─────────────┐
│   Access    │
│  Platform   │◄──── Web Browser (Chrome, Firefox, Edge)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Explore   │
│    Maps     │──────► Toggle ML/AHP predictions
└──────┬──────┘       View well locations
       │              Adjust opacity
       ▼
┌─────────────┐
│  Examine    │
│    Data     │──────► View input features
└──────┬──────┘       Check statistics
       │              Compare layers
       ▼
┌─────────────┐
│  Validate   │
│   Results   │──────► Check model performance
└──────┬──────┘       Review feature importance
       │              Compare with wells
       ▼
┌─────────────┐
│   Export    │
│    Data     │──────► Download GeoTIFF
└──────┬──────┘       Export shapefiles
       │              Get CSV data
       ▼
┌─────────────┐
│   Further   │
│  Analysis   │──────► Use in QGIS/ArcGIS
└─────────────┘       Statistical analysis
                      Report generation
```

## File Organization

```
watershed-up/
│
├── app/                          ← Web Application
│   ├── main.py                  ← Entry point
│   ├── launch_app.py            ← Launcher
│   ├── README.md                ← App docs
│   └── pages/                   ← Page modules
│       ├── home.py
│       ├── interactive_map.py
│       ├── data_layers.py
│       ├── model_insights.py
│       ├── statistical_analysis.py
│       ├── well_validation.py
│       └── export_download.py
│
├── .streamlit/                   ← Configuration
│   └── config.toml              ← Theme & settings
│
├── data/                         ← Data files
│   ├── raw/                     ← Original data
│   │   ├── wells_cgwb.csv
│   │   └── lucknow_shp/
│   └── processed/               ← Processed data
│       ├── *.tif                ← Rasters
│       ├── stage3/              ← Features
│       └── stage4/              ← ML outputs
│
├── models/                       ← Trained models
│   └── rf_baseline.pkl
│
├── src/                          ← Processing scripts
│   ├── preprocess.py
│   ├── train_model.py
│   ├── predict_map.py
│   └── ...
│
├── docs/                         ← Documentation
│   ├── VISUALIZATION_PLATFORM_GUIDE.md
│   ├── DEMO_SCRIPT.md
│   ├── PLATFORM_SUMMARY.md
│   └── LAUNCH_CHECKLIST.md
│
└── requirements.txt              ← Dependencies
```

## Key Features by Page

```
🏠 Home
├── Project overview
├── GRPZ classification legend
├── Data availability status
└── Getting started guide

🗺️ Interactive Map
├── Folium-based mapping
├── ML vs AHP toggle
├── Well overlay (rise/fall)
├── Opacity controls
└── Real-time statistics

📊 Data Layers
├── 9+ feature visualizations
├── Statistical summaries
├── Multi-layer comparison
├── Correlation analysis
└── Metadata viewer

🤖 Model Insights
├── Feature importance
├── Cross-validation results
├── Confusion matrix
├── SHAP analysis
└── ML vs AHP comparison

📈 Statistical Analysis
├── Class distributions
├── Feature statistics
├── Correlation heatmaps
├── Spatial patterns
└── Export capabilities

🔍 Well Validation
├── Well trend analysis
├── Prediction validation
├── Cross-tabulation
├── Performance metrics
└── Export validated data

📥 Export & Download
├── GeoTIFF downloads
├── Shapefile packages
├── CSV data
├── Model files
└── Complete packages
```

---

This architecture enables:
- **Modularity**: Easy to maintain and extend
- **Scalability**: Can handle additional districts/regions
- **Usability**: Intuitive for non-technical users
- **Transparency**: All methods and data visible
- **Flexibility**: Multiple deployment options
- **Reproducibility**: Complete pipeline documentation
