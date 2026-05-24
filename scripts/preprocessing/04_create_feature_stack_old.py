"""
src/features_stack.py

Stack available Stage-3 rasters into a single multi-band GeoTIFF for ML.

Output:
 - data/processed/stage3/features_stack.tif
 - data/processed/stage3/features_stack_bands.csv

Usage:
    python src/features_stack.py
"""
import os
import numpy as np
import rioxarray as rxr
import rasterio
import pandas as pd

# expected inputs (paths)
DEM = "data/processed/dem_lucknow.tif"
LULC = "data/processed/lulc_lucknow.tif"
SLOPE = "data/processed/slope_lucknow.tif"
RAIN = "data/processed/rain_mean_lucknow.tif"
GEOLOGY = "data/processed/stage3/geology_lucknow.tif"
NDVI = "data/processed/stage3/ndvi_mean_lucknow.tif"
FLOWACC = "data/processed/stage3/flow_acc_lucknow.tif"
STREAM = "data/processed/stage3/stream_network_lucknow.tif"
DRAINAGE = "data/processed/stage3/drainage_density_lucknow.tif"
GRP_SCORE = "data/processed/grp_score_lucknow.tif"  # optional (AHP result)

# Enhanced watershed features
TWI = "data/processed/stage3/twi_lucknow.tif"
ASPECT = "data/processed/stage3/aspect_lucknow.tif"
PLAN_CURV = "data/processed/stage3/plan_curvature_lucknow.tif"
PROF_CURV = "data/processed/stage3/profile_curvature_lucknow.tif"
TPI = "data/processed/stage3/tpi_lucknow.tif"
DIST_STREAM = "data/processed/stage3/distance_to_stream_lucknow.tif"

OUT_DIR = "data/processed/stage3"
OUT_STACK = os.path.join(OUT_DIR, "features_stack.tif")
OUT_BANDS = os.path.join(OUT_DIR, "features_stack_bands.csv")

os.makedirs(OUT_DIR, exist_ok=True)

# list of candidate layers in desired stacking order (name, path, type)
# type = 'cat' for categorical (nearest), 'cont' for continuous (bilinear)
CANDIDATES = [
    ("slope", SLOPE, "cont"),
    ("lulc", LULC, "cat"),
    ("rain", RAIN, "cont"),
    # ("geology", GEOLOGY, "cat"),  # REMOVED: uniform geology (no variance)
    ("ndvi", NDVI, "cont"),
    ("flow_acc", FLOWACC, "cont"),
    ("stream", STREAM, "cat"),
    ("drainage_density", DRAINAGE, "cont"),
    ("twi", TWI, "cont"),              # NEW: Water accumulation potential
    ("aspect", ASPECT, "cont"),        # NEW: Slope direction
    ("plan_curv", PLAN_CURV, "cont"),  # NEW: Flow convergence/divergence
    ("prof_curv", PROF_CURV, "cont"),  # NEW: Flow acceleration
    ("tpi", TPI, "cont"),              # NEW: Ridge/valley classification
    ("dist_stream", DIST_STREAM, "cont"),  # NEW: Proximity to streams
    ("grp_score", GRP_SCORE, "cont")
]

def open_dem_profile():
    if not os.path.exists(DEM):
        raise FileNotFoundError("DEM not found; run Stage-1 preprocessing first: {}".format(DEM))
    with rasterio.open(DEM) as src:
        prof = src.profile.copy()
    return prof

def load_and_match(path, dem_da, reclass_cat=False, resampling=1):
    """
    Load raster with rioxarray, reproject_match to dem_da.
    resampling: 1 -> nearest, 2 -> bilinear
    reclass_cat: if True, convert 0 nodata -> np.nan and keep integer codes
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
        # treat zero or nan as nodata, convert to nan, keep integer codes as floats
        arr = np.where((arr == 0) | (~np.isfinite(arr)), np.nan, arr)
    else:
        arr = np.where(np.isfinite(arr), arr, np.nan)
    return arr

def main():
    print("Stacking available features into:", OUT_STACK)
    # open DEM as rioxarray DataArray for reproject_match target
    dem_da = rxr.open_rasterio(DEM, masked=True)
    if dem_da.rio.count > 1:
        dem_da = dem_da.isel(band=0)

    # collect arrays and band names
    bands = []
    names = []
    for name, path, typ in CANDIDATES:
        if os.path.exists(path):
            print("Loading:", name, "from", path)
            resample = 1 if typ == "cat" else 2
            arr = load_and_match(path, dem_da, reclass_cat=(typ=="cat"), resampling=resample)
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
