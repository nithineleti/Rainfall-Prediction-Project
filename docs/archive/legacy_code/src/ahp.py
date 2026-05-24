"""
src/ahp.py

Usage:
    python src/ahp.py

What it does:
- Reads processed rasters from data/rasters/
    - REQUIRED: slope_lucknow.tif
    - OPTIONAL: soil_perm_lucknow.tif, lulc_lucknow.tif, rainfall_lucknow.tif
- Normalizes each layer to 0-1 with interpretation that HIGHER = better for recharge
- Applies default weights (if optional layers missing, weights are rebalanced)
- Produces:
    - data/rasters/grp_score_lucknow.tif  (continuous score 0-1)
    - data/rasters/grp_class_lucknow.tif  (0=Low,1=Moderate,2=High)
    - data/rasters/grp_class_lucknow.shp  (polygonized shapefile)
Notes:
- Default weights (initial): slope:0.30, soil:0.25, lulc:0.20, rain:0.25
- You can change weights in the WEIGHTS dict below.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import rasterio
import rasterio.features
import rasterio.mask
import geopandas as gpd
from rasterio.enums import Resampling
from shapely.geometry import shape
from path_config import SLOPE, LULC, RAINFALL, RASTERS_DIR

IN_DIR = str(RASTERS_DIR)
OUT_DIR = IN_DIR

SLOPE = str(SLOPE)
SOIL = os.path.join(IN_DIR, "soil_perm_lucknow.tif")          # optional
LULC = str(LULC)
RAIN = str(RAINFALL)   # optional

GRP_SCORE = os.path.join(OUT_DIR, "grp_score_lucknow.tif")
GRP_CLASS = os.path.join(OUT_DIR, "grp_class_lucknow.tif")
GRP_SHP = os.path.join(OUT_DIR, "grp_class_lucknow.shp")

# Default weights (sum not required; will be normalized)
WEIGHTS = {
    "slope": 0.30,
    "soil": 0.25,
    "lulc": 0.20,
    "rain": 0.25
}

def read_raster(path):
    if not os.path.exists(path):
        return None, None
    src = rasterio.open(path)
    arr = src.read(1).astype('float32')
    profile = src.profile
    src.close()
    return arr, profile

def minmax_norm(arr, higher_is_better=True):
    # arr: numpy array, may contain nan
    a = np.array(arr, dtype=float)
    a_mask = np.isfinite(a)
    if not a_mask.any():
        return None
    amin = np.nanmin(a[a_mask])
    amax = np.nanmax(a[a_mask])
    if amax - amin == 0:
        norm = np.zeros_like(a)
    else:
        norm = (a - amin) / (amax - amin)
    # if higher_is_better False (e.g., slope where lower slope => better), invert
    if not higher_is_better:
        norm = 1.0 - norm
    # keep nan as nan
    norm[~a_mask] = np.nan
    return norm

def write_raster(path, data, profile):
    profile2 = profile.copy()
    profile2.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)
    with rasterio.open(path, 'w', **profile2) as dst:
        dst.write(data.astype('float32'), 1)

def classify_score(score):
    # score: 2D array with 0-1 continuous values
    # classify into 3 classes using quantiles
    mask = np.isfinite(score)
    out = np.full(score.shape, -9999, dtype=np.int16)
    if not mask.any():
        return out
    vals = score[mask]
    q1 = np.quantile(vals, 1/3)
    q2 = np.quantile(vals, 2/3)
    out[(score <= q1) & mask] = 0   # Low
    out[(score > q1) & (score <= q2) & mask] = 1  # Moderate
    out[(score > q2) & mask] = 2   # High
    out[~mask] = -9999
    return out

def polygonize(raster_path, shp_path):
    with rasterio.open(raster_path) as src:
        image = src.read(1)
        mask = image != -9999
        transform = src.transform
        meta = src.meta
        shapes = rasterio.features.shapes(image, mask=mask, transform=transform)
        records = []
        geoms = []
        vals = []
        for geom, val in shapes:
            geoms.append(shape(geom))
            vals.append(int(val))
        gdf = gpd.GeoDataFrame({'class': vals}, geometry=geoms, crs=meta.get('crs'))
        # remove nodata polygons if any
        gdf = gdf[gdf['class'] != -9999]
        gdf.to_file(shp_path)
        print("Wrote polygon shapefile:", shp_path)

def main():
    # Read slope (required)
    slope_arr, profile = read_raster(SLOPE)
    if slope_arr is None:
        raise FileNotFoundError("Slope raster not found. Run src/preprocess.py first.")
    print("Loaded slope:", SLOPE)
    layers = {}
    layers['slope'] = (minmax_norm(slope_arr, higher_is_better=False))  # lower slope -> better

    # Read optional layers; try to resample if resolution differs
    for name, path in [('soil', SOIL), ('lulc', LULC), ('rain', RAIN)]:
        arr, prof = read_raster(path)
        if arr is None:
            print(f"Optional layer '{name}' not found at {path} — skipping.")
            continue
        # If profile transform differs from slope profile, resample arr to slope grid
        if prof['transform'] != profile['transform'] or prof['width'] != profile['width'] or prof['height'] != profile['height']:
            print(f"Resampling {name} to slope grid...")
            # simple resample using rasterio
            data_resampled = np.empty((profile['height'], profile['width']), dtype='float32')
            with rasterio.open(path) as src:
                rasterio.warp.reproject(
                    source=rasterio.band(src, 1),
                    destination=data_resampled,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=profile['transform'],
                    dst_crs=profile['crs'],
                    resampling=Resampling.nearest
                )
            arr = data_resampled
        # normalize; decision for higher_is_better depends on type:
        hib = True
        if name == 'soil':
            # assume soil_perm raster encoded so higher = more permeable -> higher is better
            hib = True
        if name == 'lulc':
            # for lulc we might have categorical classes; simple normalization works if classes are numeric
            hib = True
        if name == 'rain':
            hib = True
        layers[name] = minmax_norm(arr, higher_is_better=hib)
        print(f"Loaded and normalized {name}")

    # Determine which layers we have and normalize weights
    present = list(layers.keys())
    print("Present layers:", present)
    weights_present = {k: WEIGHTS.get(k, 0.0) for k in present}
    total_w = sum(weights_present.values())
    if total_w == 0:
        # if somehow all zeros, distribute equally
        weights_present = {k: 1.0 for k in present}
        total_w = sum(weights_present.values())
    # normalized weights
    weights_present = {k: float(v)/total_w for k,v in weights_present.items()}
    print("Using weights:", weights_present)

    # stack and compute score
    first = True
    score = None
    for k, w in weights_present.items():
        arr = layers[k]
        if score is None:
            score = np.zeros_like(arr, dtype=float)
        # handle NaNs
        valid_mask = np.isfinite(arr)
        # accumulate weighted score but preserve NaNs
        arr_f = np.where(valid_mask, arr, 0.0)
        score = score + w * arr_f

    # set score to nan where all inputs were nan
    mask_any = np.zeros_like(score, dtype=bool)
    for v in layers.values():
        mask_any = mask_any | np.isfinite(v)
    score[~mask_any] = np.nan
    # clip score to 0-1
    score = np.clip(score, 0, 1)

    # write continuous score raster
    write_raster(GRP_SCORE, score, profile)
    print("Wrote GRP score raster:", GRP_SCORE)

    # classify
    cls = classify_score(score)
    # write class raster (use nodata int code -9999)
    profile_cls = profile.copy()
    profile_cls.update(dtype=rasterio.int16, count=1, compress='lzw', nodata=-9999)
    with rasterio.open(GRP_CLASS, 'w', **profile_cls) as dst:
        dst.write(cls.astype(rasterio.int16), 1)
    print("Wrote classified GRP raster:", GRP_CLASS)

    # polygonize
    polygonize(GRP_CLASS, GRP_SHP)

if __name__ == "__main__":
    main()
