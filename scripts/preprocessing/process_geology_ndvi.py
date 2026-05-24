"""
src/preprocess_stage3.py

Preprocess Stage-3 inputs:
 - Clip & rasterize geology shapefile to DEM grid
 - Clip & reproject NDVI raster to DEM grid and normalize (0-1)
Outputs:
 - data/processed/stage3/geology_lucknow.tif  (int16, nodata=0)
 - data/processed/stage3/geology_legend.csv   (mapping text -> code)  [if text labels exist]
 - data/processed/stage3/ndvi_mean_lucknow.tif (float32, nodata=np.nan)

Usage:
    python src/preprocess_stage3.py
"""
import os
import sys
import numpy as np
import pyproj  # ensure PROJ DLLs load before geopandas on Windows
import fiona  # ensure GDAL/Fiona stack initialized first
import geopandas as gpd
import rioxarray as rxr
import rasterio
from rasterio.features import rasterize
from shapely.geometry import mapping
import pandas as pd
from path_config import DEM, RAW_DISTRICT_SHP, RAW_GEOLOGY_SHP, RAW_NDVI, RASTERS_DIR

# ---------- Config / paths ----------
DEM_FILE = str(DEM)
DISTRICT_SHP = str(RAW_DISTRICT_SHP)
GEOLOGY_SHP = str(RAW_GEOLOGY_SHP)
NDVI_RAW = str(RAW_NDVI)

OUT_DIR = "data/processed/stage3"  # Keep old location for now
GEOLOGY_OUT = os.path.join(OUT_DIR, "geology_lucknow.tif")
GEOLOGY_LEGEND = os.path.join(OUT_DIR, "geology_legend.csv")
NDVI_OUT = str(RASTERS_DIR / "ndvi_lucknow.tif")  # Use new rasters location

os.makedirs(OUT_DIR, exist_ok=True)


def load_dem_profile():
    if not os.path.exists(DEM_FILE):
        raise FileNotFoundError(f"DEM not found: {DEM_FILE}. Run Stage-1 preprocessing first.")
    src = rasterio.open(DEM_FILE)
    prof = src.profile.copy()
    transform = src.transform
    width = src.width
    height = src.height
    crs = src.crs
    src.close()
    return prof, transform, width, height, crs


def clip_geology_and_rasterize():
    print("Processing geology shapefile...")
    if not os.path.exists(GEOLOGY_SHP):
        raise FileNotFoundError(f"Geology shapefile not found at {GEOLOGY_SHP}")

    # load district polygon
    district = gpd.read_file(DISTRICT_SHP)
    if district.empty:
        raise ValueError("District shapefile appears empty.")
    # load geology
    geo = gpd.read_file(GEOLOGY_SHP)
    if geo.empty:
        raise ValueError("Geology shapefile is empty.")

    prof, transform, width, height, dem_crs = load_dem_profile()

    # Reproject geology to DEM CRS if needed
    if geo.crs != dem_crs:
        print("Reprojecting geology to DEM CRS:", dem_crs)
        geo = geo.to_crs(dem_crs)

    # Clip geology to district extent
    # Ensure district in same CRS as geology
    if district.crs != geo.crs:
        district = district.to_crs(geo.crs)

    # Use overlay intersection to clip (safe)
    try:
        geo_clip = gpd.overlay(geo, district, how='intersection')
    except Exception:
        # fallback: simple spatial filter
        geo_clip = geo[geo.intersects(district.unary_union)]

    if geo_clip.empty:
        print("Warning: clipped geology is empty. Check CRS / geometry. Writing empty raster.")
        # Write an empty raster with nodata zeros
        empty = np.zeros((height, width), dtype=np.int16)
        profile = prof.copy()
        profile.update(dtype=rasterio.int16, count=1, compress='lzw', nodata=0)
        with rasterio.open(GEOLOGY_OUT, 'w', **profile) as dst:
            dst.write(empty, 1)
        return

    # Determine attribute to use for rasterization:
    attrs = [c for c in geo_clip.columns if c.lower() not in ("geometry",)]
    numeric_field = None
    text_field = None
    for c in attrs:
        if pd.api.types.is_integer_dtype(geo_clip[c]) or pd.api.types.is_float_dtype(geo_clip[c]):
            numeric_field = c
            break
        if pd.api.types.is_object_dtype(geo_clip[c]) and text_field is None:
            text_field = c

    if numeric_field:
        print("Rasterizing using numeric attribute:", numeric_field)
        shapes = ((mapping(geom), int(val)) for geom, val in zip(geo_clip.geometry, geo_clip[numeric_field]))
        legend = None
    else:
        # factorize text field into integer codes
        if text_field is None:
            print("No suitable attribute found; using feature index as codes")
            geo_clip["_code"] = range(1, len(geo_clip) + 1)
            shapes = ((mapping(geom), int(val)) for geom, val in zip(geo_clip.geometry, geo_clip["_code"]))
            legend = pd.DataFrame({"code": geo_clip["_code"], "label": geo_clip.index.astype(str)})
        else:
            print("Rasterizing using text attribute (factorized):", text_field)
            codes, uniques = pd.factorize(geo_clip[text_field])
            codes = codes + 1
            geo_clip["_code"] = codes
            shapes = ((mapping(geom), int(val)) for geom, val in zip(geo_clip.geometry, geo_clip["_code"]))
            legend = pd.DataFrame({"code": list(range(1, len(uniques) + 1)), "label": list(uniques)})

    # Rasterize: fill outside as 0 (nodata)
    out_shape = (height, width)
    print("Rasterizing geology to DEM grid (width x height):", width, "x", height)
    rasterized = rasterize(
        shapes,
        out_shape=out_shape,
        transform=transform,
        fill=0,
        dtype=np.int16,
        all_touched=False
    )

    # Write to file
    profile = prof.copy()
    profile.update(dtype=rasterio.int16, count=1, compress='lzw', nodata=0)
    with rasterio.open(GEOLOGY_OUT, 'w', **profile) as dst:
        dst.write(rasterized.astype(rasterio.int16), 1)

    print("Wrote geology raster:", GEOLOGY_OUT)
    # write legend if available
    if legend is not None:
        legend.to_csv(GEOLOGY_LEGEND, index=False)
        print("Wrote geology legend:", GEOLOGY_LEGEND)
    else:
        print("No legend written (numeric codes used directly in shapefile).")


def process_ndvi():
    print("Processing NDVI raster...")
    if not os.path.exists(NDVI_RAW):
        raise FileNotFoundError(f"NDVI raster not found: {NDVI_RAW}")

    prof, transform, width, height, dem_crs = load_dem_profile()

    # Open NDVI using rioxarray for clip + reproject_match convenience
    ndvi = rxr.open_rasterio(NDVI_RAW, masked=True)
    # If NDVI has multiple bands, take the first
    if hasattr(ndvi, 'rio') and ndvi.rio.count > 1:
        ndvi = ndvi.isel(band=0)

    # Ensure geometry for clipping
    district = gpd.read_file(DISTRICT_SHP)
    if district.crs != ndvi.rio.crs:
        district = district.to_crs(ndvi.rio.crs)

    # Clip to district
    try:
        ndvi_clip = ndvi.rio.clip(district.geometry, district.crs, drop=True, invert=False)
    except Exception as e:
        print("NDVI clipping warning:", e)
        ndvi_clip = ndvi

    # Reproject / resample to DEM grid (bilinear interpolation appropriate for continuous NDVI)
    dem = rxr.open_rasterio(DEM, masked=True)
    ndvi_matched = ndvi_clip.rio.reproject_match(dem, resampling=2)  # 2 -> bilinear

    # Convert to numpy and normalize to 0-1
    arr = np.array(ndvi_matched.squeeze(), dtype=float)
    mask = np.isfinite(arr)
    if mask.any():
        amin = np.nanmin(arr[mask])
        amax = np.nanmax(arr[mask])
        if amax - amin == 0:
            norm = np.zeros_like(arr)
        else:
            norm = (arr - amin) / (amax - amin)
    else:
        norm = arr  # all NaN
    # keep NaNs where invalid
    norm[~mask] = np.nan

    # get DEM profile with rasterio (safe)
    with rasterio.open(DEM) as dsrc:
        prof2 = dsrc.profile.copy()

    prof2.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)

    with rasterio.open(NDVI_OUT, 'w', **prof2) as dst:
        dst.write(norm.astype('float32'), 1)

    print("Wrote normalized NDVI to:", NDVI_OUT)


def main():
    try:
        clip_geology_and_rasterize()
    except Exception as e:
        print("Error processing geology:", e)
        raise

    try:
        process_ndvi()
    except Exception as e:
        print("Error processing NDVI:", e)
        raise

    print("Stage-3 preprocessing completed. Outputs in", OUT_DIR)


if __name__ == "__main__":
    main()
