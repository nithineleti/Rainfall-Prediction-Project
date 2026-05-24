# Troubleshooting Guide

Common issues and their solutions for the Watershed Prioritization platform.

---

## General Debugging Approach

1. **Check logs first** - Most issues show up in logs
2. **Verify environment** - Python/Node versions, dependencies
3. **Test API separately** - Isolate backend from frontend issues
4. **Check file paths** - Ensure data files exist
5. **Validate configuration** - Review `config.yml` and `.env` files

---

## Backend Issues

### Server Won't Start

**Issue**: `uvicorn` fails to start or crashes immediately

**Symptoms**:
```
ERROR: Error loading ASGI app...
ModuleNotFoundError: No module named 'app'
```

**Solutions**:

1. **Check working directory**:
   ```powershell
   # Must be in backend/ directory
   cd backend
   python run.py
   ```

2. **Verify Python environment**:
   ```powershell
   # Check Python version
   python --version  # Should be 3.11+
   
   # Activate virtual environment
   .\.venv\Scripts\Activate.ps1  # PowerShell
   source .venv/bin/activate      # Linux/Mac
   ```

3. **Reinstall dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Check port availability**:
   ```powershell
   # Port 8000 might be in use
   netstat -ano | findstr :8000
   
   # Kill process if needed
   taskkill /PID <PID> /F
   ```

---

### Import Errors

**Issue**: `ModuleNotFoundError` or `ImportError`

**Symptoms**:
```python
ModuleNotFoundError: No module named 'geopandas'
ImportError: cannot import name 'WatershedService'
```

**Solutions**:

1. **Install missing package**:
   ```powershell
   pip install geopandas
   ```

2. **Check PYTHONPATH**:
   ```powershell
   # Add backend to PYTHONPATH
   $env:PYTHONPATH = "G:\PROJECTS\watershed-up\backend"
   ```

3. **Use relative imports**:
   ```python
   # Good
   from app.services.watershed import WatershedService
   
   # Bad (might fail)
   from services.watershed import WatershedService
   ```

---

### CORS Errors

**Issue**: Frontend can't connect to backend

**Symptoms**:
```
Access to fetch at 'http://localhost:8000/api/watersheds' from origin 
'http://localhost:5173' has been blocked by CORS policy
```

**Solutions**:

1. **Check CORS configuration** (`backend/.env`):
   ```env
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

2. **Verify CORS middleware** (`backend/app/main.py`):
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Check frontend API URL** (`app-frontend/.env`):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

---

### Data Loading Errors

**Issue**: Cannot load watershed or prediction data

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/processed/watersheds.gpkg'
```

**Solutions**:

1. **Verify file exists**:
   ```powershell
   ls data/processed/watersheds.gpkg
   ```

2. **Run ML pipeline** to generate data:
   ```powershell
   python run_complete_pipeline.py
   ```

3. **Check file paths in config** (`configs/config.yml`):
   ```yaml
   processed_data_dir: "G:/PROJECTS/watershed-up/data/processed"
   ```

4. **Use absolute paths**:
   ```python
   from pathlib import Path
   
   BASE_DIR = Path(__file__).parent.parent
   DATA_PATH = BASE_DIR / "data" / "processed" / "watersheds.gpkg"
   ```

---

### NumPy Serialization Error

**Issue**: Error when returning NumPy arrays in API

**Symptoms**:
```
TypeError: Object of type int64 is not JSON serializable
```

**Solutions**:

1. **Convert to Python types**:
   ```python
   # Bad
   return {"value": np.int64(10)}
   
   # Good
   return {"value": int(10)}
   ```

2. **Use Pydantic models**:
   ```python
   from pydantic import BaseModel
   
   class Response(BaseModel):
       value: int
       
       class Config:
           arbitrary_types_allowed = True
   ```

3. **Custom JSON encoder**:
   ```python
   import json
   import numpy as np
   
   class NumpyEncoder(json.JSONEncoder):
       def default(self, obj):
           if isinstance(obj, np.integer):
               return int(obj)
           if isinstance(obj, np.floating):
               return float(obj)
           if isinstance(obj, np.ndarray):
               return obj.tolist()
           return super().default(obj)
   ```

---

### Slow API Response

**Issue**: Endpoints take too long to respond

**Symptoms**:
- Requests timeout
- Frontend shows loading spinner indefinitely

**Solutions**:

1. **Add caching**:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_watersheds():
       # Expensive operation
       return load_data()
   ```

2. **Use async operations**:
   ```python
   import asyncio
   
   async def get_watersheds():
       data = await load_data_async()
       return data
   ```

3. **Paginate large datasets**:
   ```python
   def get_watersheds(page: int = 1, page_size: int = 20):
       start = (page - 1) * page_size
       end = start + page_size
       return data[start:end]
   ```

4. **Add database indexes**:
   ```sql
   CREATE INDEX idx_priority ON watersheds(priority_class);
   CREATE INDEX idx_area ON watersheds(area_km2);
   ```

---

## Frontend Issues

### Build Errors

**Issue**: `npm run build` fails

**Symptoms**:
```
ERROR: Cannot find module 'react'
ERROR: Type error: Property 'map' does not exist on type 'never'
```

**Solutions**:

1. **Clear node_modules and reinstall**:
   ```powershell
   rm -r node_modules package-lock.json
   npm install
   ```

2. **Check Node version**:
   ```powershell
   node --version  # Should be 18+
   nvm use 18      # If using nvm
   ```

3. **Fix TypeScript errors**:
   ```typescript
   // Add type annotations
   const [data, setData] = useState<Watershed[]>([]);
   
   // Handle null/undefined
   const watersheds = data?.watersheds || [];
   ```

4. **Check imports**:
   ```typescript
   // Good
   import React from 'react';
   import { useState } from 'react';
   
   // Bad (might fail with some configs)
   import * as React from 'react';
   ```

---

### API Connection Issues

**Issue**: Frontend can't fetch data from backend

**Symptoms**:
```
Error: Network Error
Failed to fetch
```

**Solutions**:

1. **Check backend is running**:
   ```powershell
   # Test backend directly
   curl http://localhost:8000/api/health
   ```

2. **Verify API URL** (`app-frontend/.env`):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **Check browser console** for CORS errors (see CORS section above)

4. **Add error handling**:
   ```typescript
   try {
     const response = await fetch('/api/watersheds');
     const data = await response.json();
   } catch (error) {
     console.error('Failed to fetch:', error);
     // Show user-friendly error message
   }
   ```

---

### Type Errors

**Issue**: TypeScript compilation errors

**Symptoms**:
```
Type 'string | undefined' is not assignable to type 'string'
Property 'name' does not exist on type '{}'
```

**Solutions**:

1. **Add type guards**:
   ```typescript
   if (typeof value === 'string') {
     // value is string here
   }
   
   if (data && 'name' in data) {
     // data has name property
   }
   ```

2. **Use optional chaining**:
   ```typescript
   // Good
   const name = watershed?.name || 'Unknown';
   
   // Bad
   const name = watershed.name;
   ```

3. **Define interfaces**:
   ```typescript
   interface Watershed {
     id: number;
     name: string;
     area_km2: number;
   }
   
   const watershed: Watershed = {...};
   ```

---

### Charts Not Rendering

**Issue**: Recharts or other visualizations don't show

**Symptoms**:
- Empty chart area
- Console error: `Cannot read property 'map' of undefined`

**Solutions**:

1. **Check data format**:
   ```typescript
   // Data must be array
   const data = [
     { name: 'High', value: 15 },
     { name: 'Medium', value: 25 },
   ];
   
   // Not undefined or null
   if (!data) return <div>No data</div>;
   ```

2. **Verify chart dimensions**:
   ```typescript
   <ResponsiveContainer width="100%" height={300}>
     <PieChart>
       {/* Chart content */}
     </PieChart>
   </ResponsiveContainer>
   ```

3. **Check parent container has height**:
   ```css
   .chart-container {
     height: 400px;
     width: 100%;
   }
   ```

---

### Map Not Loading

**Issue**: Leaflet map doesn't render

**Symptoms**:
- Gray box instead of map
- Console error: `Map container not found`

**Solutions**:

1. **Import Leaflet CSS**:
   ```typescript
   import 'leaflet/dist/leaflet.css';
   ```

2. **Set map container height**:
   ```css
   .map-container {
     height: 600px;
     width: 100%;
   }
   ```

3. **Fix marker icons** (Leaflet + Vite issue):
   ```typescript
   import L from 'leaflet';
   import icon from 'leaflet/dist/images/marker-icon.png';
   import iconShadow from 'leaflet/dist/images/marker-shadow.png';
   
   let DefaultIcon = L.icon({
     iconUrl: icon,
     shadowUrl: iconShadow,
   });
   
   L.Marker.prototype.options.icon = DefaultIcon;
   ```

---

## ML Pipeline Issues

### Memory Errors

**Issue**: Pipeline crashes with out-of-memory error

**Symptoms**:
```
MemoryError: Unable to allocate array
Killed (out of memory)
```

**Solutions**:

1. **Process in chunks**:
   ```python
   # Process raster in tiles
   for window in rasterio.windows.Window.from_bounds(...):
       data = src.read(1, window=window)
       process(data)
   ```

2. **Reduce resolution**:
   ```yaml
   # config.yml
   resolution: 90  # Instead of 30
   ```

3. **Close files after use**:
   ```python
   with rasterio.open(path) as src:
       data = src.read(1)
   # File automatically closed
   ```

4. **Use data types efficiently**:
   ```python
   # Bad - Uses 8 bytes per value
   array = np.array(data, dtype=np.float64)
   
   # Good - Uses 4 bytes
   array = np.array(data, dtype=np.float32)
   ```

---

### GDAL Errors

**Issue**: GDAL operations fail

**Symptoms**:
```
ERROR 4: Unable to open ...
CPLE_AppDefined: Too many open files
```

**Solutions**:

1. **Install GDAL properly**:
   ```powershell
   # Conda (recommended)
   conda install -c conda-forge gdal
   
   # Pip (harder on Windows)
   pip install GDAL==3.6.4
   ```

2. **Set GDAL environment variables**:
   ```powershell
   $env:GDAL_DATA = "C:\path\to\gdal\data"
   $env:PROJ_LIB = "C:\path\to\proj"
   ```

3. **Close datasets**:
   ```python
   from osgeo import gdal
   
   ds = gdal.Open(path)
   # Use dataset
   ds = None  # Close it
   ```

---

### NoData/NaN Issues

**Issue**: Rasters contain NoData values causing errors

**Symptoms**:
```
RuntimeWarning: invalid value encountered in multiply
NaN values in feature extraction
```

**Solutions**:

1. **Fill NoData values**:
   ```python
   from scipy.ndimage import distance_transform_edt
   
   # Fill NoData with nearest valid value
   mask = np.isnan(dem)
   indices = distance_transform_edt(mask, return_distances=False, return_indices=True)
   dem_filled = dem[tuple(indices)]
   ```

2. **Use our fix script**:
   ```powershell
   python fix_dem_nodata.py
   ```

3. **Set NoData value**:
   ```python
   import rasterio
   
   with rasterio.open(output_path, 'w', nodata=-9999, **profile) as dst:
       dst.write(data, 1)
   ```

---

### CRS Mismatch

**Issue**: Coordinate reference systems don't match

**Symptoms**:
```
ValueError: CRS mismatch: EPSG:4326 vs EPSG:32644
Geometries don't align visually
```

**Solutions**:

1. **Reproject data**:
   ```python
   import geopandas as gpd
   
   # Reproject to target CRS
   gdf_reprojected = gdf.to_crs("EPSG:32644")
   ```

2. **Use consistent CRS** throughout project:
   ```yaml
   # config.yml
   target_crs: "EPSG:32644"  # UTM Zone 44N
   ```

3. **Check CRS before operations**:
   ```python
   if gdf1.crs != gdf2.crs:
       gdf2 = gdf2.to_crs(gdf1.crs)
   ```

---

### Model Training Fails

**Issue**: XGBoost training crashes or produces poor results

**Symptoms**:
```
XGBoostError: Check failed
ValueError: Input contains NaN
Low accuracy (<50%)
```

**Solutions**:

1. **Check for NaN values**:
   ```python
   assert not X_train.isnull().any().any(), "Training data contains NaN"
   assert not y_train.isnull().any(), "Labels contain NaN"
   ```

2. **Balance classes**:
   ```python
   from imblearn.over_sampling import SMOTE
   
   smote = SMOTE(random_state=42)
   X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
   ```

3. **Adjust hyperparameters**:
   ```python
   params = {
       'max_depth': 6,           # Reduce to prevent overfitting
       'learning_rate': 0.1,     # Slower learning
       'n_estimators': 100,      # More trees
       'scale_pos_weight': 2,    # Handle class imbalance
   }
   ```

4. **Check feature scaling**:
   ```python
   from sklearn.preprocessing import StandardScaler
   
   scaler = StandardScaler()
   X_scaled = scaler.fit_transform(X)
   ```

---

## Environment Issues

### Python Version Conflicts

**Issue**: Code requires Python 3.11+ but different version installed

**Solutions**:

1. **Use conda** to manage Python versions:
   ```powershell
   conda create -n watershed python=3.11
   conda activate watershed
   ```

2. **Use pyenv** (Linux/Mac):
   ```bash
   pyenv install 3.11.0
   pyenv local 3.11.0
   ```

---

### Dependency Conflicts

**Issue**: Package versions incompatible

**Symptoms**:
```
ERROR: Cannot install package-a and package-b because they require different versions of dependency-c
```

**Solutions**:

1. **Use conda** (better at resolving conflicts):
   ```powershell
   conda env create -f environment.yml
   ```

2. **Create fresh environment**:
   ```powershell
   rm -r venv
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Pin specific versions** (`requirements.txt`):
   ```
   geopandas==0.14.0
   rasterio==1.3.9
   ```

---

## Docker Issues

### Container Won't Start

**Issue**: Docker container exits immediately

**Solutions**:

1. **Check logs**:
   ```powershell
   docker logs <container_id>
   ```

2. **Verify Dockerfile**:
   ```dockerfile
   # Ensure CMD is correct
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Check port mapping**:
   ```powershell
   docker run -p 8000:8000 backend-image
   ```

---

### Volume Mount Issues

**Issue**: Data files not accessible in container

**Solutions**:

1. **Use absolute paths**:
   ```powershell
   docker run -v G:\PROJECTS\watershed-up\data:/app/data backend-image
   ```

2. **Check permissions** (Linux):
   ```bash
   chmod -R 755 data/
   ```

---

## Getting Help

If you can't resolve an issue:

1. **Check logs** thoroughly - Most answers are there
2. **Search GitHub Issues** - Someone may have had the same problem
3. **Create detailed issue** with:
   - Error message (full stack trace)
   - Steps to reproduce
   - Environment details (OS, Python/Node version)
   - Relevant code/config files
4. **Ask in Discussions** for general questions

**GitHub Repository**: https://github.com/PAVANKUMARELETI/watershed-prioritization

---

**Last Updated**: November 12, 2025
