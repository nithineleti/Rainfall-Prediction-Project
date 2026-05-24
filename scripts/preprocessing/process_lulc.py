"""
src/preprocess_lulc.py (fixed for nodata handling)

Clips the manually-downloaded LULC GeoTIFF to the district boundary,
reprojects/resamples to match the DEM grid, replaces NaN nodata with 0,
and writes an integer raster data type (int16).
"""
import os
import rioxarray as rxr
import geopandas as gpd
import numpy as np
from path_config import DEM, RAW_LULC, RAW_DISTRICT_SHP, LULC

DEM_FILE = str(DEM)
LULC_RAW = str(RAW_LULC)
BOUNDARY = str(RAW_DISTRICT_SHP)
OUT = str(LULC)

os.makedirs(os.path.dirname(OUT), exist_ok=True)

print("Loading DEM and LULC...")
dem = rxr.open_rasterio(DEM_FILE, masked=True)
lulc = rxr.open_rasterio(LULC_RAW, masked=True)   # DataArray with integer classes, but nodata might be NaN
shp = gpd.read_file(BOUNDARY)

# ensure CRS consistent for clipping
if shp.crs != lulc.rio.crs:
    shp = shp.to_crs(lulc.rio.crs)

print("Clipping LULC to district boundary (this can take a moment)...")
lulc_clip = lulc.rio.clip(shp.geometry, shp.crs, drop=True, invert=False)

print("Reprojecting/resampling LULC to match DEM grid...")
# reproject_match uses nearest-neighbor by default for categorical data
lulc_match = lulc_clip.rio.reproject_match(dem, resampling=1)  # 1 => nearest

# Replace any NaN (float) with an integer nodata code (0) and cast to int16
print("Replacing NaN nodata with integer 0 and casting to int16...")
# If the DataArray has multiple bands, select first; typically LULC is single-band
arr = lulc_match.squeeze()
arr_filled = arr.fillna(0).astype('int16')

# Create a new DataArray with same coords / attrs, but integer dtype
arr_filled.rio.write_nodata(0, inplace=True)

print("Writing:", OUT)
arr_filled.rio.to_raster(OUT)
print("Done. Wrote", OUT)
