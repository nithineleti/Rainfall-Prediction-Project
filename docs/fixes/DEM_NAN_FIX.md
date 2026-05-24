# DEM NaN Issue - Fixed!

## Problem
Your DEM statistics were showing `nanm` (NaN) values:
```
DEM Statistics:
    New DEM - Min: nanm, Max: nanm, Mean: nanm
    Old DEM - Min: nanm, Max: nanm, Mean: nanm
```

## Root Cause
The DEM file (`data/processed/dem_lucknow.tif`) contained:
- **20.48% NaN pixels** (424,768 out of 2,073,600 total pixels)
- **No NoData value defined** in the file metadata
- When NumPy's `min()`, `max()`, or `mean()` functions encounter even a single NaN, they return NaN

## Investigation Results
Running diagnostic on the original file showed:
```
Original DEM:
  Shape: (1440, 1440)
  NoData value: None  ← Problem!
  NaN pixels: 424768 / 2073600 (20.48%)
  
Raw data stats (including NaN):
  Min: nan
  Max: nan
  Mean: nan
```

## Solution Applied

### 1. Fixed the DEM Files
Created `fix_dem_nodata.py` to:
- Replace all NaN values with proper NoData value (-9999)
- Set the NoData metadata in the file
- Applied to both `dem_lucknow.tif` and `slope_lucknow.tif`

**Results:**
```
Fixed DEM:
  NoData value: -9999.0  ✓
  Valid data range: 99.0 to 142.16 meters
  Valid data mean: 118.79 meters
  No NaN values remaining ✓
```

### 2. Updated Quality Check Script
Modified `scripts/quality_check_stage5.py` to:
- Use `np.nanmin()`, `np.nanmax()`, `np.nanmean()` instead of `.min()`, `.max()`, `.mean()`
- These functions properly ignore NaN/NoData values
- Added UTF-8 encoding support for Windows

## Verification
✓ DEM files now have proper NoData values set
✓ Statistics calculate correctly: Min: 99.00m, Max: 142.16m, Mean: 118.79m
✓ 79.52% of pixels contain valid elevation data
✓ No more NaN in output

## Files Modified
1. `data/processed/dem_lucknow.tif` - Fixed (backup: `dem_lucknow_original.tif`)
2. `data/processed/slope_lucknow.tif` - Fixed (backup: `slope_lucknow_original.tif`)
3. `scripts/quality_check_stage5.py` - Updated statistics calculations

## Created Files
- `fix_dem_nodata.py` - Utility to fix NaN values in raster files
- `diagnose_dem.py` - Diagnostic tool for raster data issues
- `test_dem_stats.py` - Simple test for DEM statistics

## Why Did This Happen?
The NaN values likely came from the DEM source data or processing pipeline where:
- Areas outside the valid data extent contained NaN
- Reprojection or resampling introduced NaN values
- The NoData value wasn't properly propagated through processing steps

## Prevention
When processing raster data in the future:
1. Always set explicit NoData values in output files
2. Use `np.nan*` functions when calculating statistics
3. Use `masked=True` when reading with rasterio
4. Check for NaN values after processing steps
