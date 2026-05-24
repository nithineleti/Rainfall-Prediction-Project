# Running the ML Pipeline

This guide explains how to execute the complete machine learning pipeline for groundwater potential assessment and watershed prioritization.

---

## Prerequisites

- **Python**: 3.11 or higher
- **Conda**: Recommended for managing geospatial dependencies
- **GDAL**: Geospatial Data Abstraction Library
- **Data**: DEM, LULC, rainfall, geology, well data

**System Requirements**:
- RAM: 16GB minimum, 32GB recommended
- Storage: 50GB free space
- CPU: Multi-core processor recommended

---

## Installation

### Option 1: Using Conda (Recommended)

```bash
# Create conda environment
conda env create -f ml/conda_env.yml

# Activate environment
conda activate watershed-ml

# Verify installation
python -c "import geopandas, rasterio, xgboost; print('Success!')"
```

### Option 2: Using venv

```bash
# Create virtual environment
python -m venv .venv-ml
source .venv-ml/bin/activate  # Linux/Mac
# or
.venv-ml\Scripts\Activate.ps1  # Windows

# Install GDAL first (system-specific)
# Windows: Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
pip install GDAL-3.4.3-cp311-cp311-win_amd64.whl

# Install other dependencies
pip install -r requirements.txt
```

---

## Data Preparation

### 1. Download Required Data

**Create data directory structure**:
```bash
mkdir -p data/raw/{srtm,copernicus,imd,gsi,cgwb}
mkdir -p data/processed
```

**Download datasets**:

**DEM (SRTM 30m)**:
- Source: https://earthexplorer.usgs.gov/
- Format: GeoTIFF
- Coverage: Study area extent + buffer
- Place in: `data/raw/srtm/`

**Land Use/Land Cover (Copernicus)**:
- Source: https://land.copernicus.eu/global/
- Format: GeoTIFF
- Year: Latest available
- Place in: `data/raw/copernicus/land_cover.tif`

**Rainfall (IMD/CHIRPS)**:
- Source: IMD or CHIRPS
- Format: NetCDF or GeoTIFF
- Period: Annual mean
- Place in: `data/raw/imd/rainfall_annual.tif`

**Geology (GSI)**:
- Source: Geological Survey of India
- Format: Shapefile
- Place in: `data/raw/gsi/geology.shp`

**Well Data (CGWB)**:
- Source: Central Ground Water Board
- Format: CSV or Shapefile
- Required fields: ID, longitude, latitude, yield, depth
- Place in: `data/raw/cgwb/wells.csv`

### 2. Verify Data

```bash
python scripts/verify_data.py
```

**Expected output**:
```
✓ DEM files found: 4 tiles
✓ LULC file exists
✓ Rainfall file exists
✓ Geology file exists
✓ Well data found: 2,500 records
All data files present!
```

---

## Pipeline Execution

### Complete Pipeline (Automated)

Run the entire pipeline with one command:

```bash
python run_complete_pipeline.py
```

**This executes all stages**:
1. Data preprocessing
2. Feature engineering
3. Feature stack creation
4. Sample extraction
5. Model training
6. Model evaluation
7. Spatial prediction
8. Watershed delineation
9. Watershed characterization
10. Watershed prioritization

**Estimated time**: 1.5-2 hours (depending on study area size)

---

## Step-by-Step Execution

### Stage 1: Data Preprocessing

#### 1.1 DEM Processing

```bash
python src/mosaic_and_clip_dem.py
```

**What it does**:
- Mosaics multiple DEM tiles
- Clips to study area boundary
- Reprojects to UTM (EPSG:32644)
- Fills NoData values
- Saves: `data/processed/dem_processed.tif`

**Configuration** (`configs/config.yml`):
```yaml
preprocessing:
  dem:
    input_dir: data/raw/srtm
    output: data/processed/dem_processed.tif
    target_crs: EPSG:32644
    resolution: 30
    fill_nodata: true
```

#### 1.2 LULC Processing

```bash
python src/preprocess_lulc.py
```

**What it does**:
- Clips LULC to study area
- Reprojects to match DEM
- Resamples to 30m resolution
- Saves: `data/processed/lulc_processed.tif`

#### 1.3 Rainfall Processing

```bash
python src/preprocess_rain.py
```

**What it does**:
- Extracts annual rainfall
- Clips and reprojects
- Resamples to 30m
- Saves: `data/processed/rainfall_processed.tif`

---

### Stage 2: Feature Engineering

#### 2.1 Terrain Features

```bash
python src/derive_terrain_features.py
```

**Generates**:
- Slope (degrees)
- Aspect (degrees)
- Curvature
- Terrain Ruggedness Index (TRI)
- Topographic Wetness Index (TWI)

**Output**: `data/processed/terrain_features.tif` (5 bands)

#### 2.2 Drainage Features

```bash
python src/derive_drainage.py
```

**Generates**:
- Flow direction (D8)
- Flow accumulation
- Stream network
- Drainage density
- Distance to streams

**Output**: `data/processed/drainage_features.tif` (3 bands)

#### 2.3 LULC Features

```bash
python src/extract_lulc_features.py
```

**Generates**:
- Forest percentage
- Agriculture percentage
- Built-up percentage
- Water percentage
- Land cover diversity

**Output**: `data/processed/lulc_features.tif` (5 bands)

---

### Stage 3: Feature Stack Creation

```bash
python src/features_stack.py
```

**Combines all features**:
- 17 bands total
- Aligned pixels
- Same resolution (30m)
- Same CRS (EPSG:32644)

**Output**: `data/processed/feature_stack.tif` (17 bands)

**Verify feature stack**:
```bash
python -c "
import rasterio
with rasterio.open('data/processed/feature_stack.tif') as src:
    print(f'Bands: {src.count}')
    print(f'Shape: {src.shape}')
    print(f'CRS: {src.crs}')
    print(f'Band names: {src.descriptions}')
"
```

---

### Stage 4: Sample Extraction

```bash
python src/prepare_samples.py
```

**What it does**:
- Loads well data
- Classifies wells: High-yield (>500 L/day), Low-yield (<200 L/day)
- Extracts feature values at well locations
- Splits: 70% train, 30% test
- Handles class imbalance

**Output**:
- `data/processed/train_samples.csv`
- `data/processed/test_samples.csv`

**Sample distribution**:
```
Training samples: 1,890
  - High yield: 850 (45%)
  - Low yield: 1,040 (55%)

Test samples: 810
  - High yield: 365 (45%)
  - Low yield: 445 (55%)
```

---

### Stage 5: Model Training

```bash
python src/train_model.py
```

**Training process**:
1. Load training samples
2. Grid search for hyperparameters (5-fold CV)
3. Train best model
4. Save model

**Hyperparameter search**:
```python
{
    'max_depth': [3, 5, 7, 9],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'n_estimators': [100, 200, 300, 500],
    'min_child_weight': [1, 3, 5],
    'gamma': [0, 0.1, 0.2],
    'subsample': [0.8, 0.9, 1.0],
    'colsample_bytree': [0.8, 0.9, 1.0],
}
```

**Best hyperparameters** (from training):
```python
{
    'max_depth': 5,
    'learning_rate': 0.1,
    'n_estimators': 300,
    'min_child_weight': 3,
    'gamma': 0.1,
    'subsample': 0.9,
    'colsample_bytree': 0.9
}
```

**Output**: `models/xgboost_model.json`

**Training time**: ~20 minutes (with grid search)

---

### Stage 6: Model Evaluation

```bash
python src/evaluate_model.py
```

**Generates**:
- Classification metrics
- Confusion matrix
- ROC-AUC curve
- Feature importance (SHAP)
- Evaluation report (HTML/PDF)

**Output**: `data/outputs/model_evaluation.html`

**Expected metrics**:
```
Accuracy:  79.6%
Precision: 82.0%
Recall:    76.0%
F1-Score:  79.0%
ROC-AUC:   85.0%
```

**Confusion matrix**:
```
                Predicted
              Low    High
Actual  Low   420     80
        High   90    310
```

---

### Stage 7: Spatial Prediction

```bash
python src/predict_map.py
```

**What it does**:
- Loads trained model
- Loads feature stack
- Predicts for every pixel
- Generates probability raster
- Classifies: High (>0.5), Low (≤0.5)

**Output**:
- `data/processed/prediction_map.tif` (probabilities)
- `data/processed/prediction_classes.tif` (binary)

**Memory optimization**:
- Processes in chunks (10,000 pixels at a time)
- Monitors memory usage
- Uses float32 to save space

**Prediction time**: ~10 minutes

---

### Stage 8: Watershed Delineation

```bash
python src/delineate_watersheds.py
```

**Process**:
1. Fill sinks in DEM
2. Calculate flow direction (D8)
3. Calculate flow accumulation
4. Extract streams (threshold: 1,000 cells)
5. Identify pour points
6. Delineate watershed boundaries

**Output**:
- `data/processed/watersheds.gpkg` (polygons)
- `data/processed/streams.gpkg` (lines)

**Parameters**:
```yaml
watershed:
  min_area_km2: 5
  flow_threshold: 1000
  pour_point_distance: 500
```

**Result**: ~520 watersheds delineated

---

### Stage 9: Watershed Characterization

```bash
python src/characterize_watersheds.py
```

**Extracts features for each watershed**:

**Morphometric**:
- Area, perimeter, elongation ratio
- Compactness coefficient, form factor

**Terrain**:
- Mean elevation, elevation range
- Mean slope, relief ratio

**Drainage**:
- Drainage density
- Stream frequency, bifurcation ratio

**LULC**:
- Forest, agriculture, built-up percentages
- Land cover diversity

**Climate**:
- Mean rainfall, rainfall variability

**Groundwater**:
- Mean prediction probability
- High-potential area percentage

**Output**: `data/processed/characterized_watersheds.gpkg`

---

### Stage 10: Watershed Prioritization

```bash
python src/prioritize_watersheds.py
```

**Multi-criteria scoring** (AHP weights):
```python
{
    'gw_potential_mean': 0.35,      # 35%
    'drainage_density': 0.15,       # 15%
    'forest_cover_pct': 0.12,       # 12%
    'mean_rainfall': 0.10,          # 10%
    'relief_ratio': 0.08,           # 8%
    'agriculture_pct': 0.08,        # 8%
    'mean_slope': 0.07,             # 7%
    'area_km2': 0.05                # 5%
}
```

**Priority classes**:
- High: Score > 0.7 (145 watersheds, 28%)
- Medium: Score 0.4-0.7 (234 watersheds, 45%)
- Low: Score < 0.4 (141 watersheds, 27%)

**Output**: `data/processed/prioritized_watersheds.gpkg`

---

## Visualization

### Generate Charts

```bash
python src/visualize_results.py
```

**Creates**:
- Priority distribution pie chart
- Feature importance bar chart
- Model performance metrics
- Spatial distribution maps

**Output**: `data/outputs/visualizations/`

### Interactive Plots (Jupyter)

```bash
jupyter notebook ml/notebooks/04_watershed_analysis.ipynb
```

---

## Configuration

### Edit Pipeline Config

**File**: `configs/config.yml`

```yaml
# Spatial parameters
spatial:
  crs: EPSG:32644
  resolution: 30
  nodata: -9999

# Model parameters
model:
  algorithm: xgboost
  n_estimators: 300
  max_depth: 5
  learning_rate: 0.1
  test_size: 0.3
  random_state: 42

# Watershed parameters
watershed:
  min_area_km2: 5
  flow_threshold: 1000

# Prioritization weights
prioritization:
  gw_potential_mean: 0.35
  drainage_density: 0.15
  forest_cover_pct: 0.12
  # ... more weights
```

---

## Monitoring Progress

### Check Logs

```bash
tail -f logs/pipeline.log
```

### Progress Indicators

Each script outputs progress:

```
[1/5] Loading DEM tiles... ████████████████████ 100%
[2/5] Mosaicing... ████████████████████ 100%
[3/5] Clipping to study area... ████████████████████ 100%
[4/5] Reprojecting... ████████████████████ 100%
[5/5] Filling NoData... ████████████████████ 100%
✓ DEM processing complete!
```

---

## Troubleshooting

### Memory Errors

**Error**: `MemoryError: Unable to allocate array`

**Solution**:
```python
# In predict_map.py, reduce chunk size
chunk_size = 5000  # Instead of 10000
```

### GDAL Errors

**Error**: `ERROR 4: Unable to open file`

**Solution**:
```bash
# Check file exists
ls -lh data/raw/srtm/

# Verify GDAL can read it
gdalinfo data/raw/srtm/tile1.tif
```

### NoData Issues

**Error**: `Invalid values in feature stack`

**Solution**:
```python
# Fill NoData before processing
features[np.isnan(features)] = 0
features[np.isinf(features)] = 0
```

### CRS Mismatch

**Error**: `CRS mismatch between rasters`

**Solution**:
```bash
# Reproject all to same CRS
gdalwarp -t_srs EPSG:32644 input.tif output.tif
```

---

## Performance Optimization

### Parallel Processing

```python
from multiprocessing import Pool

with Pool(processes=8) as pool:
    results = pool.map(process_watershed, watershed_ids)
```

### GPU Acceleration

```python
# XGBoost with GPU
model = XGBClassifier(
    tree_method='gpu_hist',
    gpu_id=0,
    predictor='gpu_predictor'
)
```

### Chunked Processing

```python
def process_large_raster(src_path, chunk_size=1000):
    with rasterio.open(src_path) as src:
        for row in range(0, src.height, chunk_size):
            window = Window(0, row, src.width, min(chunk_size, src.height - row))
            chunk = src.read(window=window)
            # Process chunk
            yield process(chunk)
```

---

## Output Files

**After complete pipeline execution**:

```
data/processed/
├── dem_processed.tif              # Processed DEM
├── lulc_processed.tif             # Processed LULC
├── rainfall_processed.tif         # Processed rainfall
├── terrain_features.tif           # Terrain features (5 bands)
├── drainage_features.tif          # Drainage features (3 bands)
├── lulc_features.tif              # LULC features (5 bands)
├── feature_stack.tif              # Complete feature stack (17 bands)
├── train_samples.csv              # Training data
├── test_samples.csv               # Test data
├── prediction_map.tif             # Prediction probabilities
├── prediction_classes.tif         # Binary predictions
├── watersheds.gpkg                # Watershed boundaries
├── streams.gpkg                   # Stream network
├── characterized_watersheds.gpkg  # Watersheds with features
└── prioritized_watersheds.gpkg    # Final prioritized watersheds

models/
└── xgboost_model.json             # Trained XGBoost model

data/outputs/
├── model_evaluation.html          # Evaluation report
└── visualizations/                # Charts and maps
    ├── priority_distribution.png
    ├── feature_importance.png
    ├── roc_curve.png
    └── prediction_map.png
```

---

## Updating the Model

### Retrain with New Data

```bash
# Add new well data to wells.csv
# Re-run from sample extraction
python src/prepare_samples.py
python src/train_model.py
python src/evaluate_model.py
python src/predict_map.py
```

### Adjust Hyperparameters

Edit `configs/config.yml`:

```yaml
model:
  n_estimators: 500      # Increase trees
  max_depth: 7           # Deeper trees
  learning_rate: 0.05    # Lower learning rate
```

Then retrain:
```bash
python src/train_model.py
```

---

## Best Practices

1. **Always backup data** before running pipeline
2. **Check intermediate outputs** after each stage
3. **Monitor memory usage** for large study areas
4. **Version control your config** files
5. **Document any modifications** to the pipeline
6. **Validate results** against ground truth

---

## Additional Resources

- [ML Pipeline Architecture](../architecture/ML_PIPELINE.md)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [GDAL Documentation](https://gdal.org/)
- [GeoPandas Documentation](https://geopandas.org/)

---

**Last Updated**: November 12, 2025  
**Version**: 2.0.0
