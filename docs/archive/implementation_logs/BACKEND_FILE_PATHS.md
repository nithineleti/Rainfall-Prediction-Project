# Backend File Path Organization

## Summary
All backend routers now use **absolute paths** to prevent path resolution issues. The project has files at two different root locations:
- **PROJECT_ROOT**: `G:\PROJECTS\watershed-up` (main project root)
- **BACKEND_ROOT**: `G:\PROJECTS\watershed-up\backend` (backend-specific files)

## File Locations

### Raster Files (at PROJECT_ROOT)
Located in: `G:\PROJECTS\watershed-up\`

| File Path | Size | Purpose |
|-----------|------|---------|
| `outputs/predictions/predicted_grp_score.tif` | 28.25 MB | ML prediction scores |
| `outputs/predictions/predicted_grp_class.tif` | 2.98 MB | ML prediction classes |
| `data/rasters/ndvi_mean_lucknow.tif` | 17.23 MB | NDVI vegetation index |
| `data/rasters/rain_mean_lucknow.tif` | 15.83 MB | Rainfall data |
| `data/rasters/lulc_lucknow.tif` | 57.8 MB | Land use/land cover |
| `data/rasters/slope_lucknow.tif` | 57.7 MB | Terrain slope |
| `data/rasters/drainage_density_lucknow.tif` | 19.25 MB | Drainage density |
| `data/rasters/dem_lucknow.tif` | 57.8 MB | Digital elevation model |
| `data/rasters/twi_lucknow.tif` | 6.21 MB | Topographic wetness index |

### CSV Files (at PROJECT_ROOT)
Located in: `G:\PROJECTS\watershed-up\data\tables\`

| File | Size | Purpose |
|------|------|---------|
| `feature_importances.csv` | 0.15 KB | ML feature importance rankings |
| `cv_results.csv` | 0.29 KB | Cross-validation results |
| `watersheds_characterized.csv` | 30 KB | Watershed attributes and statistics |

### Vector Files (at BACKEND_ROOT)
Located in: `G:\PROJECTS\watershed-up\backend\data_demo\vectors\`

| File | Size | Purpose |
|------|------|---------|
| `real_watersheds.geojson` | 0.35 MB | Watershed polygon geometries (144 watersheds) |

## Router Configuration

### 1. layers.py (Tile Server)
```python
# Get project root (watershed-up directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent
# __file__ = .../backend/routers/layers.py
# .parent = .../backend/routers/
# .parent.parent = .../backend/
# .parent.parent.parent = .../watershed-up/ ← PROJECT_ROOT
```

**Uses PROJECT_ROOT for:**
- All 9 raster tile layers (predictions + environmental + terrain data)

### 2. statistics.py (Statistics API)
```python
# Get project root (watershed-up directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent
```

**Uses PROJECT_ROOT for:**
- `feature_importances.csv`
- `cv_results.csv`
- `watersheds_characterized.csv`

### 3. watersheds.py (Watershed GeoJSON API)
```python
# Get backend directory
BACKEND_ROOT = Path(__file__).parent.parent
# Get project root for CSV files
PROJECT_ROOT = BACKEND_ROOT.parent
```

**Uses BACKEND_ROOT for:**
- `data_demo/vectors/real_watersheds.geojson` (GeoJSON in backend folder)

**Uses PROJECT_ROOT for:**
- `data/tables/watersheds_characterized.csv` (CSV at project root)

### 4. tiles.py (Legacy Tile Endpoint)
```python
# Get project root (watershed-up directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent
```

**Uses PROJECT_ROOT for:**
- `outputs/predictions/predicted_grp_score.tif`

## API Endpoints

### Tile Endpoints (layers.py)
```
GET /layers/grp_score/{z}/{x}/{y}.png           - ML prediction scores
GET /layers/grp_class/{z}/{x}/{y}.png           - ML prediction classes
GET /layers/ndvi/{z}/{x}/{y}.png                - NDVI vegetation
GET /layers/rainfall/{z}/{x}/{y}.png            - Rainfall data
GET /layers/lulc/{z}/{x}/{y}.png                - Land use/cover
GET /layers/slope/{z}/{x}/{y}.png               - Terrain slope
GET /layers/drainage_density/{z}/{x}/{y}.png    - Drainage density
GET /layers/elevation/{z}/{x}/{y}.png           - Elevation (DEM)
GET /layers/twi/{z}/{x}/{y}.png                 - Topographic wetness
```

### Statistics Endpoints (statistics.py)
```
GET /api/statistics/feature-importance          - Feature rankings
GET /api/statistics/cv-results                  - Model performance
```

### Watershed Endpoints (watersheds.py)
```
GET /api/watersheds                             - All watershed polygons
GET /api/watersheds/{watershed_id}              - Single watershed detail
```

## Backend Server
- **File**: `backend/simple_main.py`
- **Port**: 8000
- **Current PID**: 23088
- **Status**: ✅ Running successfully
- **CORS**: Enabled for http://localhost:5173

## Frontend
- **Directory**: `app-frontend/`
- **Port**: 5173
- **Status**: ✅ Running (Vite dev server)
- **Backend**: Connected to http://localhost:8000

## Path Resolution Pattern

**Why absolute paths?**
Relative paths like `"../outputs/data.tif"` are resolved from the **current working directory** (where Python is executed), not from where the Python file is located. This causes issues when:
- Running from different directories
- Running in Docker containers
- Using different execution methods

**Solution:**
Use `Path(__file__)` to get the absolute path to the current Python file, then navigate from there:

```python
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "outputs" / "data.tif"
# Always resolves correctly regardless of execution directory
```

## Verification
Run `verify_paths.ps1` to check all file paths:
```powershell
& "G:\PROJECTS\watershed-up\verify_paths.ps1"
```

Expected output: `OK All required files exist!`

## Status: ✅ ALL PATHS VERIFIED AND WORKING
- Backend: Running on port 8000 (PID 23088)
- Frontend: Running on port 5173
- All 13 files verified and accessible
- No 404 errors expected
