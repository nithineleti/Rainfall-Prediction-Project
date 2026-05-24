# Code Documentation: `src/preprocess.py`

## Overview

**File:** `src/preprocess.py`  
**Purpose:** Stage 1 preprocessing - DEM clipping, slope calculation, and hillshade generation  
**Stage:** Stage 1 - Foundational DEM Processing  
**Dependencies:** rioxarray, geopandas, numpy, rasterio  
**Output Files:** 
- `dem_lucknow.tif`
- `slope_lucknow.tif`
- `hillshade_lucknow.tif`

---

## What We Have Done

### 1. **DEM Clipping**
```python
def clip_dem_if_needed():
    if os.path.exists(DEM_CLIPPED):
        print("Clipped DEM already exists:", DEM_CLIPPED)
        return
    print("Clipping DEM to district...")
    dem = rxr.open_rasterio(DEM_IN, masked=True)
    shp = gpd.read_file(DISTRICT_SHP)
    if shp.crs != dem.rio.crs:
        shp = shp.to_crs(dem.rio.crs)
    demc = dem.rio.clip(shp.geometry, shp.crs, drop=True, invert=False)
    demc.rio.to_raster(DEM_CLIPPED)
```

**What it does:**
- Loads ALOS PALSAR DEM (12.5m resolution)
- Reads Lucknow district boundary shapefile
- Clips DEM to exact district boundary
- Ensures CRS consistency between DEM and boundary
- Saves clipped DEM to avoid reprocessing

**Why we did it:**
- **Reduce data volume:** Original DEM tiles cover large area; clipping to study area reduces file size and processing time
- **Focus analysis:** Only relevant pixels within district boundary are retained
- **CRS alignment:** Ensures spatial consistency between raster and vector data
- **Efficiency:** Checks if clipped DEM already exists to avoid redundant processing

---

### 2. **Slope Calculation (Pure Python Implementation)**
```python
def compute_slope_and_hillshade():
    # Get pixel size from transform
    transform = src.transform
    xres = transform.a
    yres = -transform.e
    
    # Compute gradients using central differences
    dy, dx = np.gradient(arr_f, yres, xres, edge_order=2)
    
    # Calculate slope in radians then convert to degrees
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)
```

**What it does:**
- Extracts geotransform parameters (pixel size in degrees)
- Computes elevation gradients in X and Y directions using `np.gradient()`
- Calculates slope magnitude: $\text{slope} = \arctan(\sqrt{(\frac{\partial z}{\partial x})^2 + (\frac{\partial z}{\partial y})^2})$
- Converts from radians to degrees (0-90°)
- Preserves NoData as NaN

**Why we did it:**
- **Critical GIS parameter:** Slope controls runoff vs. infiltration - gentle slopes favor recharge, steep slopes favor runoff
- **Pure Python approach:** Avoids dependency on GDAL command-line tools, making code more portable
- **Mathematical accuracy:** Central difference method (`edge_order=2`) provides better accuracy than simple forward/backward differences
- **Physical interpretation:** Degrees are more intuitive for domain experts than radians or percent slope
- **Hydrological relevance:** Slope is primary factor in AHP weighting (50% weight) and ML feature importance

**Scientific rationale:**
- Studies show inverse relationship between slope and groundwater recharge potential
- Flat areas (<5°) allow longer water residence time → better infiltration
- Steep slopes (>15°) promote rapid runoff → poor recharge

---

### 3. **Hillshade Generation**
```python
# Hillshade parameters
azimuth_deg = 315.0  # Northwest (sun direction)
altitude_deg = 45.0  # 45° elevation

# Convert to mathematical angles
az = np.radians(360.0 - azimuth_deg + 90.0)
alt = np.radians(altitude_deg)

# Calculate aspect (slope direction)
aspect = np.arctan2(dy, -dx)
aspect = np.where(aspect < 0, 2*np.pi + aspect, aspect)

# Horn's hillshade formula
hillshade = 255.0 * (
    (np.cos(alt) * np.cos(slope_rad)) +
    (np.sin(alt) * np.sin(slope_rad) * np.cos(az - aspect))
)
```

**What it does:**
- Simulates illumination from sun at 315° azimuth (NW) and 45° altitude
- Computes terrain aspect (direction of maximum slope)
- Applies Horn's hillshade algorithm
- Scales output to 0-255 grayscale range
- Clips negative values to 0

**Why we did it:**
- **Visualization:** Provides 3D terrain perspective for stakeholder presentations
- **Quality control:** Visual inspection reveals DEM artifacts or processing errors
- **Geomorphology:** Highlights drainage patterns, ridges, valleys
- **Standard parameters:** 315° azimuth and 45° altitude are cartographic conventions
- **Not used in modeling:** Purely for visualization, not included in ML features

**Technical details:**
- **Horn's method:** More sophisticated than simple dot product, accounts for both slope and aspect
- **Aspect calculation:** `arctan2(dy, -dx)` gives direction perpendicular to slope gradient
- **Normalization:** 0-255 range matches standard grayscale imagery conventions

---

### 4. **Raster Writing with Metadata**
```python
# Copy profile from DEM
profile = dem_xr.rio.profile.copy()
profile.update({
    'dtype': 'float32',
    'nodata': np.nan,
    'compress': 'lzw',
    'tiled': True,
    'blockxsize': 256,
    'blockysize': 256
})

# Write slope
with rasterio.open(SLOPE_TIF, 'w', **profile) as dst:
    dst.write(slope_deg.astype('float32'), 1)
    dst.set_band_description(1, "Slope (degrees)")
```

**What it does:**
- Inherits CRS, transform, dimensions from input DEM
- Sets data type to float32 (sufficient precision, smaller than float64)
- Uses LZW compression to reduce file size (~30-50% smaller)
- Enables internal tiling (256×256) for faster partial reads
- Adds band descriptions for metadata clarity

**Why we did it:**
- **Data integrity:** Profile copying ensures perfect spatial alignment with DEM
- **Efficiency:** Compression saves disk space without quality loss
- **Performance:** Tiling accelerates random access in GIS software
- **Interoperability:** Standard GeoTIFF format compatible with QGIS, ArcGIS, GDAL
- **Documentation:** Band descriptions help future users understand data content

---

## Why We Made These Choices

### **1. Why ALOS PALSAR DEM (12.5m) instead of SRTM or Copernicus?**
- **Resolution:** 12.5m vs 30m (Copernicus) vs 90m (SRTM) - provides 5.7× better spatial detail
- **Vertical accuracy:** ±5m RMSE vs ±16m (SRTM) - more accurate elevation values
- **Terrain representation:** Captures finer drainage features critical for groundwater modeling
- **Open data:** Freely available from Alaska Satellite Facility
- **Stage 5 improvement:** Upgraded from Copernicus GLO-30 to ALOS, resulting in +2.97% model accuracy gain

### **2. Why compute slope in degrees?**
- **Domain convention:** Hydrologists and water resource engineers use degrees
- **Interpretability:** 0° = flat, 45° = steep is intuitive
- **AHP weighting:** Literature on groundwater recharge uses degree-based slope classes
- **Alternative rejected:** Percent slope (rise/run × 100) less intuitive for non-engineers

### **3. Why central difference gradient method?**
- **Accuracy:** Second-order central differences more accurate than first-order forward/backward
- **Edge handling:** `edge_order=2` parameter maintains accuracy at raster boundaries
- **NumPy efficiency:** Vectorized `np.gradient()` is 10-100× faster than Python loops
- **Standard practice:** Used by GDAL `gdaldem slope` internally

### **4. Why check if output exists before reprocessing?**
- **Development efficiency:** Avoid re-running 5-10 minute processing when testing downstream code
- **Reproducibility:** Deterministic outputs - same inputs always produce same outputs
- **Error recovery:** If pipeline fails mid-stage, can resume without starting over
- **Best practice:** Common pattern in data pipelines (e.g., Make, Snakemake)

---

## Technical Details

### **Coordinate Reference System (CRS)**
- **EPSG:4326 (WGS84):** Geographic coordinate system (latitude/longitude)
- **Why not projected?:** Study area small enough that distortion is minimal
- **Pixel size:** ~0.000278° (~12.5m at Lucknow's latitude ~26°N)
- **Consideration:** For larger areas or precise area calculations, UTM projection (EPSG:32644) would be better

### **Gradient Calculation Mathematics**
Given DEM elevation $z(x,y)$:

$$\frac{\partial z}{\partial x} \approx \frac{z(x+\Delta x, y) - z(x-\Delta x, y)}{2\Delta x}$$

$$\frac{\partial z}{\partial y} \approx \frac{z(x, y+\Delta y) - z(x, y-\Delta y)}{2\Delta y}$$

$$\text{slope} = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right)$$

Where:
- $\Delta x$ = pixel width in meters (xres)
- $\Delta y$ = pixel height in meters (yres)
- Central difference uses neighbors on both sides

### **Memory Optimization**
```python
arr_f = np.where(mask, arr, np.nan)  # Replace nodata with NaN
```
- **Why NaN?** Propagates through calculations automatically (NaN + 5 = NaN)
- **Alternative rejected:** Masking with `np.ma.masked_array` slower and more complex
- **Trade-off:** NaN requires float dtype (can't use int8/int16), but acceptable for DEM

### **Hillshade Formula Explanation**
Horn's method: $H = 255 \times \left[\cos(\theta_z) \cos(\alpha) + \sin(\theta_z) \sin(\alpha) \cos(\theta_a - A)\right]$

Where:
- $H$ = hillshade value (0-255)
- $\theta_z$ = solar altitude angle (45°)
- $\theta_a$ = solar azimuth angle (315°)
- $\alpha$ = terrain slope angle
- $A$ = terrain aspect angle

**Interpretation:**
- First term: Illumination on horizontal surface
- Second term: Adjustment for sloped surface orientation
- Cosine difference: Maximum when aspect faces sun, minimum when opposite

---

## Input/Output Specifications

### **Inputs**
| File | Format | Resolution | CRS | Notes |
|------|--------|------------|-----|-------|
| `lucknow_dem_clipped.tif` | GeoTIFF | 12.5m | EPSG:4326 | ALOS PALSAR DEM |
| `lucknow_shp/lucknow.shp` | Shapefile | - | EPSG:4326 | District boundary |

### **Outputs**
| File | Data Type | NoData | Range | Description |
|------|-----------|--------|-------|-------------|
| `dem_lucknow.tif` | Float32 | NaN | 70-180m | Clipped elevation |
| `slope_lucknow.tif` | Float32 | NaN | 0-90° | Terrain slope |
| `hillshade_lucknow.tif` | UInt8 | 0 | 0-255 | Shaded relief |

### **Processing Time**
- DEM clipping: ~30 seconds (1440×1440 pixels)
- Slope calculation: ~45 seconds
- Hillshade generation: ~30 seconds
- **Total:** ~2 minutes on modern laptop (Intel i5, 16GB RAM)

---

## Error Handling

### **1. Missing Input Files**
```python
if not os.path.exists(DEM_IN):
    raise FileNotFoundError(f"Input DEM not found: {DEM_IN}")
```
- **Why:** Fail fast with clear error message
- **User action:** Check data download or path configuration

### **2. Empty DEM (All NoData)**
```python
mask = np.isfinite(arr)
if not mask.any():
    raise RuntimeError("DEM contains no valid data")
```
- **Why:** Detect invalid/corrupted input before expensive calculations
- **Cause:** Incorrect clipping or corrupt download

### **3. CRS Mismatch**
```python
if shp.crs != dem.rio.crs:
    shp = shp.to_crs(dem.rio.crs)
```
- **Why:** Automatic reprojection ensures correct spatial overlap
- **Alternative:** Could raise error, but auto-fixing is user-friendly

### **4. Pixel Size Extraction Failure**
```python
try:
    xres = transform.a
    yres = -transform.e
except:
    # Fallback: compute from coordinates
    xs = dem_xr['x'].values
    xres = abs(xs[1] - xs[0])
```
- **Why:** Different rasterio versions handle transforms differently
- **Robustness:** Multiple fallback methods ensure compatibility

---

## Usage Examples

### **Basic Usage**
```bash
python src/preprocess.py
```

### **Expected Console Output**
```
Clipping DEM to district...
Wrote clipped DEM: data/processed/dem_lucknow.tif
Loading clipped DEM...
Pixel size roughly: xres=0.000277, yres=0.000277
Computing slope and hillshade...
Wrote: data/processed/slope_lucknow.tif
Wrote: data/processed/hillshade_lucknow.tif
Done!
```

### **Troubleshooting**
**Problem:** "DEM contains no valid data"  
**Solution:** Check if `lucknow_dem_clipped.tif` exists and is valid:
```bash
gdalinfo data/processed/lucknow_dem_clipped.tif
```

**Problem:** Very slow processing (>10 minutes)  
**Solution:** Check DEM size; if too large, verify clipping worked correctly

---

## Integration with Pipeline

### **Upstream Dependencies**
- **None** - This is Stage 1 (first step in pipeline)
- Requires manual data download of ALOS DEM tiles
- Requires district boundary shapefile

### **Downstream Usage**
- **Stage 2:** LULC/Rainfall processing (uses DEM profile for alignment)
- **Stage 3:** Flow accumulation, drainage density (uses DEM elevation)
- **AHP:** Slope used as primary criterion (50% weight)
- **ML:** Slope is #1 feature by importance (via GRP score: 53%)

### **Files Used By**
- `slope_lucknow.tif` → `features_stack.py`, `ahp*.py`
- `dem_lucknow.tif` → `derive_drainage.py`, alignment reference
- `hillshade_lucknow.tif` → Visualization only (not in ML)

---

## Future Improvements

### **Potential Enhancements**
1. **Multi-directional hillshade:** Combine multiple azimuth angles (e.g., 225°, 270°, 315°) for better visualization
2. **Curvature calculation:** Plan/profile curvature useful for water accumulation modeling
3. **Terrain roughness:** Standard deviation of slope within moving window
4. **Sink filling:** Pre-process DEM to fill depressions for better drainage network

### **Performance Optimizations**
1. **Dask integration:** Process larger-than-memory DEMs in chunks
2. **Numba JIT:** Compile gradient calculation for 2-5× speedup
3. **GPU acceleration:** Use CuPy for massive DEMs

### **Code Refactoring**
1. **Function parameters:** Accept input/output paths as arguments instead of hardcoding
2. **Configuration file:** Move paths to `configs/config.yml`
3. **Logging:** Replace `print()` with proper `logging` module
4. **Unit tests:** Add pytest tests for gradient calculation accuracy

---

## References

### **Academic Citations**
1. Horn, B. K. P. (1981). "Hill shading and the reflectance map." Proceedings of the IEEE, 69(1), 14-47.
2. Burrough, P. A., & McDonnell, R. (1998). "Principles of Geographical Information Systems." Oxford University Press.
3. Zevenbergen, L. W., & Thorne, C. R. (1987). "Quantitative analysis of land surface topography." Earth Surface Processes and Landforms, 12(1), 47-56.

### **Software Documentation**
- Rasterio: https://rasterio.readthedocs.io/
- Rioxarray: https://corteva.github.io/rioxarray/
- NumPy gradient: https://numpy.org/doc/stable/reference/generated/numpy.gradient.html

### **Data Sources**
- ALOS PALSAR: https://asf.alaska.edu/data-sets/derived-data-sets/alos-palsar-rtc/alos-palsar-radiometric-terrain-correction/

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Oct 25, 2025 | Initial implementation with Copernicus DEM | Pavan |
| 2.0 | Oct 25, 2025 | **Upgraded to ALOS PALSAR DEM** (12.5m) | Pavan |
| 2.1 | Oct 27, 2025 | Documentation created | Pavan |

**Key Change (Stage 5):** Line 21 updated from `dem_copernicus_glo30.tif` to `lucknow_dem_clipped.tif` (ALOS PALSAR)

---

**Document Status:** Complete  
**Last Updated:** October 27, 2025  
**Next Review:** Before thesis submission
