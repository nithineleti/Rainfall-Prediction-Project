#!/usr/bin/env python3
"""
scripts/postprocessing/compute_dd_per_watershed.py

Compute mean drainage density (dd) per watershed polygon and update watersheds GeoPackage + CSV.

Inputs (expected):
 - data/rasters/watersheds.gpkg  (layer 'watersheds')
 - data/rasters/drainage_density_lucknow.tif

Outputs:
 - updates data/rasters/watersheds.gpkg layer 'watersheds' adding/overwriting column 'mean_dd_zone'
 - writes CSV: data/rasters/watersheds_stats_dd.csv (watershed attributes including new field)
"""
from pathlib import Path
import sys
import math

import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import mapping

BASE = Path("data/rasters")
WATERS_GPKG = BASE / "watersheds.gpkg"
WATERS_LAYER = "watersheds"
DD_TIF = BASE / "drainage_density_lucknow.tif"
OUT_CSV = BASE / "watersheds_stats_dd.csv"

if not WATERS_GPKG.exists():
    sys.exit(f"Watersheds GeoPackage not found: {WATERS_GPKG}")
if not DD_TIF.exists():
    sys.exit(f"Drainage density raster not found: {DD_TIF}")

print("Loading watersheds...")
gdf = gpd.read_file(WATERS_GPKG, layer=WATERS_LAYER)
if gdf.empty:
    sys.exit("No features in watersheds layer.")

print("Opening drainage density raster:", DD_TIF)
with rasterio.open(DD_TIF) as src:
    dd_crs = src.crs
    dd_transform = src.transform
    dd_nodata = src.nodata
    dd_dtype = src.dtypes[0]
    print("Raster CRS:", dd_crs, "nodata:", dd_nodata)

    # Reproject watersheds to raster CRS if needed
    if gdf.crs is None:
        raise RuntimeError("Watersheds layer has no CRS.")
    if gdf.crs != dd_crs:
        print(f"Reprojecting watersheds from {gdf.crs} -> {dd_crs}")
        gdf = gdf.to_crs(dd_crs)

    # Prepare output field
    mean_dd_list = []
    idxs = []
    print("Computing zonal mean drainage density for each watershed (this may take a few seconds)...")
    for i, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            mean_dd_list.append(float("nan"))
            idxs.append(i)
            continue
        try:
            # mask returns (data, transform) with data shape (bands, h, w)
            out_image, out_transform = mask(src, [mapping(geom)], crop=True, all_touched=False, filled=False)
            # out_image is masked array if filled=False; if not, convert using nodata
            arr = out_image[0]  # single band
            # handle masked arrays and nodata
            if np.ma.is_masked(arr):
                valid = ~arr.mask
                data = arr.data[valid]
            else:
                if dd_nodata is not None:
                    valid = (arr != dd_nodata) & np.isfinite(arr)
                    data = arr[valid]
                else:
                    valid = np.isfinite(arr)
                    data = arr[valid]
            if data.size == 0:
                mean_val = float("nan")
            else:
                mean_val = float(np.nanmean(data))
            mean_dd_list.append(mean_val)
            idxs.append(i)
        except Exception as e:
            print(f"  Warning: failed mask for feature index {i}: {e}")
            mean_dd_list.append(float("nan"))
            idxs.append(i)

# attach results to gdf
gdf = gdf.copy()
gdf["mean_dd_zone"] = np.nan
for i, v in zip(idxs, mean_dd_list):
    gdf.at[i, "mean_dd_zone"] = v

# write updated GeoPackage (overwrite layer)
print("Writing updated GeoPackage (overwriting layer)...")
# geopandas to_file will replace the layer if exists on most Fiona/GPKG installs,
# but some Fiona versions require deleting first. We'll attempt to overwrite.
try:
    gdf.to_file(WATERS_GPKG, layer=WATERS_LAYER, driver="GPKG")
except Exception as e:
    print("Overwrite failed; attempting to remove layer then write. Error:", e)
    # Attempt best-effort deletion by writing to a temp file and replacing
    tmp = WATERS_GPKG.with_suffix(".tmp.gpkg")
    gdf.to_file(tmp, layer=WATERS_LAYER, driver="GPKG")
    tmp.replace(WATERS_GPKG)
    print("Replaced geopackage with new version.")

# Save CSV summary
print("Writing CSV:", OUT_CSV)
# drop geometry for CSV
df_out = gdf.drop(columns="geometry").copy()
# Ensure numeric columns serialized well
df_out.to_csv(OUT_CSV, index=False)
print("Done. Added 'mean_dd_zone' to watersheds and wrote CSV.")

# Quick stats
valid_vals = df_out["mean_dd_zone"].dropna().values
if valid_vals.size:
    print("mean_dd_zone stats -> min: {:.6f}, max: {:.6f}, mean: {:.6f}".format(valid_vals.min(), valid_vals.max(), valid_vals.mean()))
else:
    print("No valid mean_dd_zone values computed.")
