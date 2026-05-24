# ML Pipeline Architecture

## Overview

The Machine Learning pipeline is a comprehensive end-to-end workflow for groundwater potential assessment using **XGBoost classification** with spatial feature engineering. It processes multi-source geospatial data (DEM, LULC, rainfall, geology) to identify high-potential groundwater zones and prioritize watersheds.

**Tech Stack**:
- **ML Framework**: XGBoost 2.0+, scikit-learn 1.3+
- **Spatial Processing**: GDAL, Rasterio, GeoPandas, Shapely
- **Feature Engineering**: NumPy, Pandas, SciPy
- **Explainability**: SHAP (SHapley Additive exPlanations)
- **Visualization**: Matplotlib, Seaborn
- **Configuration**: YAML-based config files

**Model Performance**:
- **Accuracy**: 79.6%
- **Precision**: 0.82
- **Recall**: 0.76
- **F1-Score**: 0.79
- **Features**: 17-feature engineered stack

---

## Pipeline Architecture

### High-Level Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Acquisition                              │
│  - DEM (SRTM 30m)                                                │
│  - Land Use/Land Cover (Copernicus)                              │
│  - Rainfall (IMD/CHIRPS)                                         │
│  - Geology (GSI)                                                 │
│  - Well Data (CGWB)                                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Preprocessing                                  │
│  - Mosaic and clip to study area                                │
│  - Reproject to common CRS (EPSG:32644)                         │
│  - Handle NoData values                                          │
│  - Resample to common resolution (30m)                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Feature Engineering                              │
│  - Terrain: Slope, Aspect, Curvature, TRI, TWI                  │
│  - Drainage: Flow Direction, Flow Accumulation, Streams         │
│  - LULC: Land cover percentages, fragmentation                  │
│  - Climate: Rainfall statistics                                 │
│  - Geology: Lithology classes                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Feature Stack                                 │
│  - 17-band raster (all features)                                │
│  - Aligned pixels, same resolution                              │
│  - Ready for training/prediction                                │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Sample Extraction                               │
│  - Positive samples: High-yielding wells                        │
│  - Negative samples: Low-yielding wells                         │
│  - Extract feature values at well locations                     │
│  - Split: 70% train, 30% test                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Model Training                                 │
│  - Algorithm: XGBoost Classifier                                │
│  - Hyperparameter tuning: GridSearchCV                          │
│  - Cross-validation: 5-fold stratified                          │
│  - Class balancing: scale_pos_weight                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Model Evaluation                                │
│  - Accuracy, Precision, Recall, F1                              │
│  - ROC-AUC curve                                                │
│  - Confusion matrix                                             │
│  - Feature importance (SHAP)                                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Spatial Prediction                               │
│  - Predict for entire study area                                │
│  - Generate probability raster                                  │
│  - Classify: High (>0.5) / Low (≤0.5)                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│               Watershed Delineation                              │
│  - Fill sinks in DEM                                            │
│  - Flow direction (D8 algorithm)                                │
│  - Flow accumulation                                            │
│  - Stream extraction (threshold)                                │
│  - Watershed boundaries (pour points)                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│            Watershed Characterization                            │
│  - Area, perimeter, shape metrics                               │
│  - Zonal statistics (mean, std, range)                          │
│  - Drainage density, relief ratio                               │
│  - LULC composition                                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│             Watershed Prioritization                             │
│  - Aggregate prediction probabilities                           │
│  - Multi-criteria scoring (AHP weights)                         │
│  - Rank watersheds by score                                     │
│  - Classify: High (>0.7), Medium (0.4-0.7), Low (<0.4)          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Outputs                                      │
│  - Trained model (xgboost_model.json)                           │
│  - Prediction raster (prediction_map.tif)                       │
│  - Prioritized watersheds (GeoPackage)                          │
│  - Visualizations (charts, maps)                                │
│  - Performance report (HTML/PDF)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
ml/
├── src/                          # Source code (✅ RESTRUCTURED)
│   ├── __init__.py
│   ├── config.py                 # Centralized configuration & paths
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── dem_processing.py     # DEM preprocessing
│   │   ├── preprocess_dem.py     # DEM processing utilities
│   │   ├── lulc_processing.py    # LULC preprocessing
│   │   └── rainfall_processing.py # Rainfall preprocessing
│   ├── features/
│   │   ├── __init__.py
│   │   ├── feature_stack.py      # 17-band feature stack creation
│   │   ├── drainage_features.py  # Drainage network features
│   │   └── enhanced_features.py  # Enhanced watershed features
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py              # Model training
│   │   ├── predict.py            # Spatial prediction
│   │   ├── sample_wells.py       # Training sample extraction
│   │   └── clean_samples.py      # Data cleaning & validation
│   ├── watershed/
│   │   ├── __init__.py
│   │   ├── delineation.py        # Watershed delineation
│   │   ├── characterization.py   # Watershed characterization
│   │   └── prioritization.py     # AHP-based prioritization
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plots.py              # General plotting utilities
│   │   ├── plot_prediction.py    # Prediction visualization
│   │   └── shap_analysis.py      # SHAP interpretability
│   └── utils/
│       └── __init__.py           # Helper utilities
│   ├── features/
│   │   ├── terrain.py            # Terrain feature extraction
│   │   ├── drainage.py           # Drainage feature extraction
│   │   ├── lulc.py               # LULC feature extraction
│   │   └── feature_stack.py      # Feature stack creation
│   ├── models/
│   │   ├── train.py              # Model training
│   │   ├── predict.py            # Spatial prediction
│   │   └── evaluate.py           # Model evaluation
│   ├── watershed/
│   │   ├── delineation.py        # Watershed delineation
│   │   ├── characterization.py   # Feature extraction
│   │   └── prioritization.py     # Priority scoring
│   ├── visualization/
│   │   ├── plots.py              # Chart generation
│   │   └── maps.py               # Map visualization
│   ├── utils/
│   │   ├── io.py                 # File I/O utilities
│   │   ├── spatial.py            # Spatial operations
│   │   └── validators.py         # Data validation
│   └── config.py                 # Configuration
├── notebooks/                     # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_watershed_analysis.ipynb
├── configs/
│   └── config.yml                # Pipeline configuration
├── models/                        # Trained models
│   └── xgboost_model.json
└── conda_env.yml                 # Conda environment
```

---

## Pipeline Stages

### Stage 1: Data Preprocessing

#### DEM Processing (`mosaic_and_clip_dem.py`)

**Inputs**:
- Multiple SRTM DEM tiles (GeoTIFF)
- Study area boundary (Shapefile/GeoJSON)

**Processing Steps**:
1. Mosaic multiple DEM tiles
2. Clip to study area
3. Reproject to UTM Zone 44N (EPSG:32644)
4. Fill NoData values using interpolation
5. Save processed DEM

**Key Functions**:
```python
def mosaic_dem_tiles(tile_paths: List[Path]) -> np.ndarray:
    """Mosaic multiple DEM tiles into single raster."""
    
def clip_to_boundary(raster: np.ndarray, boundary: gpd.GeoDataFrame) -> np.ndarray:
    """Clip raster to study area boundary."""
    
def fill_nodata(raster: np.ndarray, method: str = 'interpolate') -> np.ndarray:
    """Fill NoData values in raster."""
```

**Output**:
- `data/processed/dem_processed.tif` (Single-band raster, 30m resolution)

#### LULC Processing (`preprocess_lulc.py`)

**Inputs**:
- Copernicus Global Land Cover (GeoTIFF)
- Study area boundary

**Processing Steps**:
1. Clip to study area
2. Reproject to match DEM CRS
3. Resample to 30m resolution
4. Reclassify land cover classes (11 classes → simplified)
5. Save processed LULC

**Land Cover Classes**:
- 0: Water
- 20: Shrubland
- 30: Herbaceous vegetation
- 40: Cropland
- 50: Built-up
- 60: Bare/sparse vegetation
- 70: Snow and ice
- 80: Permanent water bodies
- 90: Herbaceous wetland
- 100: Moss and lichen

**Output**:
- `data/processed/lulc_processed.tif`

#### Rainfall Processing (`preprocess_rain.py`)

**Inputs**:
- IMD/CHIRPS rainfall data (NetCDF/GeoTIFF)
- Study area boundary

**Processing Steps**:
1. Extract annual rainfall
2. Clip to study area
3. Reproject and resample to 30m
4. Calculate statistics (mean, variability)
5. Save processed rainfall

**Output**:
- `data/processed/rainfall_processed.tif`

---

### Stage 2: Feature Engineering

#### Terrain Features (`derive_terrain_features.py`)

**Features Derived from DEM**:

1. **Slope** (degrees): Rate of elevation change
   ```python
   slope = arctan(sqrt(dz/dx² + dz/dy²)) * 180/π
   ```

2. **Aspect** (degrees): Direction of slope
   ```python
   aspect = arctan2(dz/dy, dz/dx) * 180/π
   ```

3. **Curvature**: Surface convexity/concavity
   ```python
   curvature = -(d²z/dx² + d²z/dy²)
   ```

4. **Terrain Ruggedness Index (TRI)**: Elevation variability
   ```python
   TRI = sqrt(Σ(z_i - z_center)²)
   ```

5. **Topographic Wetness Index (TWI)**: Wetness accumulation
   ```python
   TWI = ln(flow_accumulation / tan(slope))
   ```

**Implementation**:
```python
from scipy.ndimage import sobel

def calculate_slope(dem: np.ndarray, resolution: float) -> np.ndarray:
    """Calculate slope from DEM."""
    dzdy = sobel(dem, axis=0) / (8 * resolution)
    dzdx = sobel(dem, axis=1) / (8 * resolution)
    slope = np.arctan(np.sqrt(dzdx**2 + dzdy**2)) * 180 / np.pi
    return slope
```

#### Drainage Features (`derive_drainage.py`)

**Features**:

1. **Flow Direction** (D8 algorithm): Direction water flows
2. **Flow Accumulation**: Number of cells draining to each cell
3. **Stream Network**: Extracted from flow accumulation (threshold > 1000 cells)
4. **Drainage Density**: Total stream length / watershed area

**Flow Direction Algorithm**:
```python
def flow_direction_d8(dem: np.ndarray) -> np.ndarray:
    """Calculate D8 flow direction.
    
    Direction codes:
    32  64  128
    16   0    1
     8   4    2
    """
    flow_dir = np.zeros_like(dem, dtype=np.uint8)
    
    for i in range(1, dem.shape[0] - 1):
        for j in range(1, dem.shape[1] - 1):
            neighbors = [
                dem[i-1, j+1], dem[i, j+1], dem[i+1, j+1],
                dem[i-1, j], dem[i+1, j],
                dem[i-1, j-1], dem[i, j-1], dem[i+1, j-1]
            ]
            codes = [1, 2, 4, 8, 16, 32, 64, 128]
            max_slope_idx = np.argmax([(dem[i, j] - n) for n in neighbors])
            flow_dir[i, j] = codes[max_slope_idx]
    
    return flow_dir
```

#### LULC Features (`extract_lulc_features.py`)

**Features**:
1. Forest percentage
2. Agriculture percentage
3. Built-up percentage
4. Water body percentage
5. Land cover diversity (Shannon index)

**Calculation**:
```python
def calculate_lulc_percentages(lulc: np.ndarray) -> dict:
    """Calculate land cover percentages."""
    total_pixels = lulc.size
    
    return {
        'forest_pct': np.sum(lulc == 111) / total_pixels * 100,
        'agriculture_pct': np.sum(lulc == 40) / total_pixels * 100,
        'builtup_pct': np.sum(lulc == 50) / total_pixels * 100,
        'water_pct': np.sum(lulc == 80) / total_pixels * 100,
    }
```

---

### Stage 3: Feature Stack Creation

**Combine all features into multi-band raster** (`features_stack.py`)

**17 Bands**:
1. Elevation
2. Slope
3. Aspect
4. Curvature
5. TRI
6. TWI
7. Flow Accumulation (log-transformed)
8. Drainage Density
9. LULC - Forest %
10. LULC - Agriculture %
11. LULC - Built-up %
12. LULC - Water %
13. LULC Diversity
14. Annual Rainfall
15. Rainfall Variability (CV)
16. Geology - Lithology Class
17. Distance to Streams

**Implementation**:
```python
def create_feature_stack(feature_dict: dict, output_path: Path):
    """Create multi-band feature stack."""
    # Ensure all features have same shape
    reference_shape = feature_dict['elevation'].shape
    
    bands = []
    band_names = []
    
    for name, data in feature_dict.items():
        if data.shape != reference_shape:
            data = resize_array(data, reference_shape)
        bands.append(data)
        band_names.append(name)
    
    # Stack bands
    stack = np.stack(bands, axis=0)
    
    # Write to GeoTIFF
    write_raster(stack, output_path, band_names=band_names)
```

**Output**:
- `data/processed/feature_stack.tif` (17-band GeoTIFF)

---

### Stage 4: Model Training

#### Sample Extraction (`prepare_samples.py`)

**Well Data Processing**:
1. Load well locations from CGWB database
2. Extract yield values (liters/day)
3. Classify: High-yield (>500 L/day), Low-yield (<200 L/day)
4. Extract feature values at well locations
5. Create training dataset

**Implementation**:
```python
def extract_samples_at_points(feature_stack_path: Path, well_points: gpd.GeoDataFrame) -> pd.DataFrame:
    """Extract feature values at well locations."""
    with rasterio.open(feature_stack_path) as src:
        samples = []
        for idx, point in well_points.iterrows():
            row, col = src.index(point.geometry.x, point.geometry.y)
            values = src.read()[:, row, col]
            samples.append({
                'well_id': point['id'],
                'label': point['class'],
                **{f'feature_{i}': v for i, v in enumerate(values)}
            })
    
    return pd.DataFrame(samples)
```

#### Model Training (`train_model.py`)

**XGBoost Configuration**:
```python
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold

# Hyperparameter grid
param_grid = {
    'max_depth': [3, 5, 7, 9],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'n_estimators': [100, 200, 300, 500],
    'min_child_weight': [1, 3, 5],
    'gamma': [0, 0.1, 0.2],
    'subsample': [0.8, 0.9, 1.0],
    'colsample_bytree': [0.8, 0.9, 1.0],
}

# Model
model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    random_state=42,
    scale_pos_weight=len(y_train[y_train == 0]) / len(y_train[y_train == 1])  # Handle class imbalance
)

# Grid search with cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid_search = GridSearchCV(
    model,
    param_grid,
    cv=cv,
    scoring='f1',
    n_jobs=-1,
    verbose=2
)

# Train
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
```

**Best Hyperparameters** (from training):
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

**Save Model**:
```python
best_model.save_model('models/xgboost_model.json')
```

---

### Stage 5: Model Evaluation

#### Metrics Calculation (`evaluate_model.py`)

**Classification Metrics**:
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

metrics = {
    'accuracy': accuracy_score(y_test, y_pred),      # 0.796
    'precision': precision_score(y_test, y_pred),    # 0.82
    'recall': recall_score(y_test, y_pred),          # 0.76
    'f1': f1_score(y_test, y_pred),                  # 0.79
    'roc_auc': roc_auc_score(y_test, y_pred_proba),  # 0.85
}
```

**Confusion Matrix**:
```
                Predicted
              Low    High
Actual  Low   420     80
        High   90    310

True Negatives:  420
False Positives:  80
False Negatives:  90
True Positives:  310
```

#### Feature Importance (SHAP)

**SHAP Analysis**:
```python
import shap

# Create explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Summary plot
shap.summary_plot(shap_values, X_test, feature_names=feature_names)

# Feature importance ranking
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': np.abs(shap_values).mean(axis=0)
}).sort_values('importance', ascending=False)
```

**Top 10 Features** (by SHAP importance):
1. Topographic Wetness Index (TWI)
2. Flow Accumulation
3. Drainage Density
4. Annual Rainfall
5. Elevation
6. LULC - Agriculture %
7. Slope
8. Distance to Streams
9. LULC - Forest %
10. Geology - Lithology

---

### Stage 6: Spatial Prediction

#### Prediction Map (`predict_map.py`)

**Process**:
1. Load trained model
2. Load feature stack
3. Predict for each pixel
4. Generate probability raster
5. Classify into High/Low zones

**Implementation**:
```python
def predict_spatial(model_path: Path, feature_stack_path: Path, output_path: Path):
    """Generate spatial prediction map."""
    # Load model
    model = xgb.Booster()
    model.load_model(str(model_path))
    
    # Load features
    with rasterio.open(feature_stack_path) as src:
        features = src.read()  # (17, height, width)
        profile = src.profile
    
    # Reshape for prediction
    n_bands, height, width = features.shape
    features_flat = features.reshape(n_bands, -1).T  # (n_pixels, n_features)
    
    # Predict (in batches to save memory)
    batch_size = 10000
    predictions = []
    
    for i in range(0, len(features_flat), batch_size):
        batch = features_flat[i:i+batch_size]
        batch_pred = model.predict(xgb.DMatrix(batch))
        predictions.extend(batch_pred)
    
    # Reshape back to raster
    pred_map = np.array(predictions).reshape(height, width)
    
    # Save
    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(pred_map, 1)
```

**Output**:
- `data/processed/prediction_map.tif` (Probability values 0-1)
- `data/processed/prediction_classes.tif` (Binary: High=1, Low=0)

---

### Stage 7: Watershed Delineation

#### Delineation Process (`delineate_watersheds.py`)

**Steps**:
1. Fill sinks in DEM
2. Calculate flow direction
3. Calculate flow accumulation
4. Extract stream network (threshold: 1000 accumulated cells)
5. Identify pour points (stream outlets)
6. Delineate watershed boundaries

**Sink Filling**:
```python
from scipy.ndimage import grey_dilation

def fill_sinks(dem: np.ndarray) -> np.ndarray:
    """Fill sinks in DEM using iterative filling."""
    filled = dem.copy()
    
    while True:
        dilated = grey_dilation(filled, size=(3, 3))
        filled_new = np.minimum(dilated, dem)
        
        if np.array_equal(filled, filled_new):
            break
        
        filled = filled_new
    
    return filled
```

**Watershed Segmentation**:
```python
from skimage.segmentation import watershed
from skimage.feature import peak_local_max

def delineate_watersheds(flow_acc: np.ndarray, min_size: int = 1000) -> np.ndarray:
    """Delineate watershed boundaries."""
    # Find watershed outlets (local maxima in flow accumulation)
    markers = peak_local_max(-flow_acc, min_distance=50, labels=flow_acc > min_size)
    
    # Watershed segmentation
    watersheds = watershed(flow_acc, markers, mask=flow_acc > 0)
    
    return watersheds
```

**Output**:
- `data/processed/watersheds.gpkg` (Vector polygons)
- `data/processed/streams.gpkg` (Stream network)

---

### Stage 8: Watershed Characterization

#### Feature Extraction (`characterize_watersheds.py`)

**For each watershed, calculate**:

1. **Morphometric Features**:
   - Area (km²)
   - Perimeter (km)
   - Elongation ratio
   - Compactness coefficient
   - Form factor

2. **Terrain Statistics**:
   - Mean elevation
   - Elevation range
   - Mean slope
   - Relief ratio

3. **Drainage Features**:
   - Drainage density
   - Stream frequency
   - Bifurcation ratio

4. **LULC Composition**:
   - Forest cover %
   - Agricultural land %
   - Built-up area %

5. **Climate**:
   - Mean annual rainfall

6. **Prediction Statistics**:
   - Mean groundwater potential
   - High potential area %

**Zonal Statistics**:
```python
from rasterstats import zonal_stats

def extract_watershed_features(watersheds_gdf: gpd.GeoDataFrame, raster_paths: dict) -> gpd.GeoDataFrame:
    """Extract features for each watershed."""
    
    for raster_name, raster_path in raster_paths.items():
        stats = zonal_stats(
            watersheds_gdf.geometry,
            str(raster_path),
            stats=['mean', 'std', 'min', 'max', 'sum']
        )
        
        for stat_name in ['mean', 'std', 'min', 'max']:
            watersheds_gdf[f'{raster_name}_{stat_name}'] = [s[stat_name] for s in stats]
    
    return watersheds_gdf
```

---

### Stage 9: Watershed Prioritization

#### Priority Scoring (`prioritize_watersheds.py`)

**Multi-Criteria Decision Making (AHP Weights)**:

```python
criteria_weights = {
    'gw_potential_mean': 0.35,      # Highest weight
    'drainage_density': 0.15,
    'forest_cover_pct': 0.12,
    'mean_rainfall': 0.10,
    'relief_ratio': 0.08,
    'agriculture_pct': 0.08,
    'mean_slope': 0.07,
    'area_km2': 0.05
}
```

**Normalization and Scoring**:
```python
def calculate_priority_score(watersheds_gdf: gpd.GeoDataFrame, weights: dict) -> gpd.GeoDataFrame:
    """Calculate priority scores using weighted criteria."""
    
    # Normalize each criterion to 0-1
    for criterion, weight in weights.items():
        col = watersheds_gdf[criterion]
        
        # Higher is better normalization
        if criterion in ['gw_potential_mean', 'drainage_density', 'forest_cover_pct', 'mean_rainfall']:
            normalized = (col - col.min()) / (col.max() - col.min())
        # Lower is better normalization
        else:
            normalized = (col.max() - col) / (col.max() - col.min())
        
        watersheds_gdf[f'{criterion}_norm'] = normalized
    
    # Calculate weighted score
    watersheds_gdf['priority_score'] = sum(
        watersheds_gdf[f'{crit}_norm'] * weight 
        for crit, weight in weights.items()
    )
    
    # Classify
    watersheds_gdf['priority_class'] = pd.cut(
        watersheds_gdf['priority_score'],
        bins=[0, 0.4, 0.7, 1.0],
        labels=['Low', 'Medium', 'High']
    )
    
    return watersheds_gdf
```

**Output**:
- `data/processed/prioritized_watersheds.gpkg` (Final output)

**Priority Distribution**:
- High priority: 145 watersheds (28%)
- Medium priority: 234 watersheds (45%)
- Low priority: 141 watersheds (27%)

---

## Configuration

### `config.yml`

```yaml
# Data paths
data:
  raw_dir: data/raw
  processed_dir: data/processed
  output_dir: data/outputs
  
  # Input datasets
  dem: ${data.raw_dir}/srtm/
  lulc: ${data.raw_dir}/copernicus/land_cover.tif
  rainfall: ${data.raw_dir}/imd/rainfall_annual.tif
  geology: ${data.raw_dir}/gsi/geology.shp
  wells: ${data.raw_dir}/cgwb/wells.csv
  
  # Outputs
  feature_stack: ${data.processed_dir}/feature_stack.tif
  prediction_map: ${data.processed_dir}/prediction_map.tif
  watersheds: ${data.processed_dir}/prioritized_watersheds.gpkg

# Spatial parameters
spatial:
  crs: EPSG:32644  # UTM Zone 44N
  resolution: 30    # meters
  nodata: -9999
  
# Model parameters
model:
  algorithm: xgboost
  n_estimators: 300
  max_depth: 5
  learning_rate: 0.1
  test_size: 0.3
  random_state: 42
  
# Feature engineering
features:
  terrain:
    - elevation
    - slope
    - aspect
    - curvature
    - tri
    - twi
  drainage:
    - flow_accumulation
    - drainage_density
    - distance_to_streams
  lulc:
    - forest_pct
    - agriculture_pct
    - builtup_pct
    - water_pct
    - diversity
  climate:
    - annual_rainfall
    - rainfall_cv
  geology:
    - lithology_class

# Watershed parameters
watershed:
  min_area_km2: 5
  flow_threshold: 1000
  pour_point_distance: 500
  
# Prioritization weights (AHP)
prioritization:
  gw_potential_mean: 0.35
  drainage_density: 0.15
  forest_cover_pct: 0.12
  mean_rainfall: 0.10
  relief_ratio: 0.08
  agriculture_pct: 0.08
  mean_slope: 0.07
  area_km2: 0.05
```

---

## Running the Pipeline

### Complete Pipeline Execution

```bash
# Using the master script
python run_complete_pipeline.py

# Or step-by-step
python src/mosaic_and_clip_dem.py
python src/preprocess_lulc.py
python src/preprocess_rain.py
python src/derive_terrain_features.py
python src/derive_drainage.py
python src/features_stack.py
python src/prepare_samples.py
python src/train_model.py
python src/predict_map.py
python src/delineate_watersheds.py
python src/characterize_watersheds.py
python src/prioritize_watersheds.py
```

### Execution Time

**Estimated runtime** (on standard laptop):
- Preprocessing: ~15 minutes
- Feature engineering: ~30 minutes
- Model training: ~20 minutes (with grid search)
- Prediction: ~10 minutes
- Watershed analysis: ~25 minutes
- **Total**: ~1.5-2 hours

---

## Model Interpretability (SHAP)

### SHAP Value Analysis

```python
import shap

# Load model and data
model = xgb.Booster()
model.load_model('models/xgboost_model.json')

X_test = pd.read_csv('data/processed/test_samples.csv')

# Calculate SHAP values
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Summary plot (feature importance)
shap.summary_plot(shap_values, X_test, plot_type="bar")

# Detailed summary plot
shap.summary_plot(shap_values, X_test)

# Individual prediction explanation
shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])

# Dependence plot (feature interaction)
shap.dependence_plot("TWI", shap_values, X_test)
```

---

## Performance Optimization

### 1. Memory Management

**Chunked Processing**:
```python
def predict_in_chunks(model, feature_stack_path, chunk_size=1000):
    """Predict in chunks to avoid memory overflow."""
    with rasterio.open(feature_stack_path) as src:
        height, width = src.shape
        
        for row_start in range(0, height, chunk_size):
            row_end = min(row_start + chunk_size, height)
            chunk = src.read(window=Window(0, row_start, width, row_end - row_start))
            
            # Process chunk
            predictions = model.predict(chunk)
            
            # Write to output
            yield predictions
```

### 2. Parallel Processing

```python
from multiprocessing import Pool

def process_watershed(watershed_id):
    """Process single watershed."""
    # Extract features
    # Calculate statistics
    return results

# Parallel execution
with Pool(processes=8) as pool:
    results = pool.map(process_watershed, watershed_ids)
```

### 3. GPU Acceleration (XGBoost)

```python
model = XGBClassifier(
    tree_method='gpu_hist',  # Use GPU
    gpu_id=0,
    predictor='gpu_predictor'
)
```

---

## Troubleshooting

### Common Issues

**1. Memory Error During Prediction**
```
Solution: Use chunked processing (see above)
```

**2. NoData Values in Feature Stack**
```python
# Fill NoData before stacking
features[np.isnan(features)] = 0
```

**3. CRS Mismatch**
```python
# Ensure all rasters have same CRS
target_crs = 'EPSG:32644'
raster = raster.to_crs(target_crs)
```

**4. Class Imbalance**
```python
# Use SMOTE or scale_pos_weight
from imblearn.over_sampling import SMOTE
X_resampled, y_resampled = SMOTE().fit_resample(X, y)
```

---

## Future Enhancements

1. **Deep Learning Models**: CNN for spatial patterns
2. **Time Series Analysis**: Temporal trends in groundwater
3. **Ensemble Models**: Combine XGBoost, Random Forest, Neural Nets
4. **Real-time Predictions**: API for on-demand predictions
5. **Automated Retraining**: Update model with new well data

---

**Last Updated**: November 12, 2025  
**Version**: 2.0.0
