"""
scripts/preprocessing/04_create_feature_stack.py

Stack available rasters into a single multi-band GeoTIFF for ML.

Output:
 - data/rasters/features_stack.tif
 - data/tables/features_stack_bands.csv

Usage:
    python scripts/preprocessing/04_create_feature_stack.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import rioxarray as rxr
import rasterio
import pandas as pd
from path_config import (
    DEM, LULC, SLOPE, RAINFALL, NDVI, 
    FLOW_ACC, STREAM_NETWORK, DRAINAGE_DENSITY,
    TWI, ASPECT, PLAN_CURVATURE, PROFILE_CURVATURE, TPI, DIST_TO_STREAM,
    GWP_AHP, RASTERS_DIR, TABLES_DIR, FEATURES_STACK, FEATURES_BANDS_CSV
)

OUT_DIR = str(RASTERS_DIR)
OUT_STACK = str(FEATURES_STACK)
OUT_BANDS = str(FEATURES_BANDS_CSV)

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(str(TABLES_DIR), exist_ok=True)

# list of candidate layers in desired stacking order (name, path, type)
# type = 'cat' for categorical (nearest), 'cont' for continuous (bilinear)
CANDIDATES = [
    ("slope", str(SLOPE), "cont"),
    ("lulc", str(LULC), "cat"),
    ("rain", str(RAINFALL), "cont"),
    ("ndvi", str(NDVI), "cont"),
    ("flow_acc", str(FLOW_ACC), "cont"),
    ("stream", str(STREAM_NETWORK), "cat"),
    ("drainage_density", str(DRAINAGE_DENSITY), "cont"),
    ("twi", str(TWI), "cont"),              # NEW: Water accumulation potential
    ("aspect", str(ASPECT), "cont"),        # NEW: Slope direction
    ("plan_curv", str(PLAN_CURVATURE), "cont"),  # NEW: Flow convergence/divergence
    ("prof_curv", str(PROFILE_CURVATURE), "cont"),  # NEW: Flow acceleration
    ("tpi", str(TPI), "cont"),              # NEW: Ridge/valley classification
    ("dist_stream", str(DIST_TO_STREAM), "cont"),  # NEW: Proximity to streams
    ("grp_score", str(GWP_AHP), "cont")
]

def open_dem_profile():
    if not os.path.exists(str(DEM)):
        raise FileNotFoundError("DEM not found; run Stage-1 preprocessing first: {}".format(DEM))
    with rasterio.open(str(DEM)) as src:
        prof = src.profile.copy()
    return prof

def load_and_match(path, dem_da, reclass_cat=False, resampling=1, feat_name=None):
    """
    Load raster with rioxarray, reproject_match to dem_da.
    resampling: 1 -> nearest, 2 -> bilinear
    reclass_cat: if True, convert 0 nodata -> np.nan and keep integer codes
    feat_name: feature name (used to handle special cases like stream)
    """
    da = rxr.open_rasterio(path, masked=True)
    # If multi-band, take first
    if da.rio.count > 1:
        da = da.isel(band=0)
    # reproject / resample to match dem
    try:
        matched = da.rio.reproject_match(dem_da, resampling=resampling)
    except Exception as e:
        print(f"Warning: reproject_match failed for {path} with error: {e}. Trying to proceed with .rio.reproject.")
        matched = da
    arr = np.array(matched.squeeze(), dtype=float)
    # handle nodata: rioxarray masked arrays may have np.nan already
    if reclass_cat:
        # Special handling for binary features like stream where 0 is a valid value
        if feat_name == "stream":
            # For stream: 0 = non-stream (valid), 1 = stream (valid), only convert NaN
            arr = np.where(np.isfinite(arr), arr, np.nan)
        else:
            # For other categorical: treat zero or nan as nodata, convert to nan, keep integer codes as floats
            arr = np.where((arr == 0) | (~np.isfinite(arr)), np.nan, arr)
    else:
        arr = np.where(np.isfinite(arr), arr, np.nan)
    return arr

def main():
    print("Stacking available features into:", OUT_STACK)
    # open DEM as rioxarray DataArray for reproject_match target
    dem_da = rxr.open_rasterio(str(DEM), masked=True)
    if dem_da.rio.count > 1:
        dem_da = dem_da.isel(band=0)

    # collect arrays and band names
    bands = []
    names = []
    for name, path, typ in CANDIDATES:
        if os.path.exists(path):
            print("Loading:", name, "from", path)
            resample = 1 if typ == "cat" else 2
            arr = load_and_match(path, dem_da, reclass_cat=(typ=="cat"), resampling=resample, feat_name=name)
            bands.append(arr)
            names.append(name)
        else:
            print("Skipping (not found):", name)

    if not bands:
        raise SystemExit("No input rasters found to stack. Place files in data/processed and try again.")

    # stack -> shape (bands, rows, cols)
    stack = np.stack(bands, axis=0).astype(np.float32)
    nband, rows, cols = stack.shape
    print("Stack shape (bands,rows,cols):", stack.shape)

    # write using rasterio with DEM profile
    prof = open_dem_profile()
    prof.update(count=nband, dtype=rasterio.float32, compress='lzw', nodata=np.nan)

    with rasterio.open(OUT_STACK, 'w', **prof) as dst:
        for i in range(nband):
            dst.write(stack[i,:,:], i+1)

    # write bandnames CSV
    df = pd.DataFrame({"band_index": list(range(1, len(names)+1)), "band_name": names})
    df.to_csv(OUT_BANDS, index=False)
    print("Wrote stack:", OUT_STACK)
    print("Wrote band list:", OUT_BANDS)
    print("Done. Bands:", names)

if __name__ == "__main__":
    main()
