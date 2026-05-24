"""
src/ahp_with_rain.py
Combines slope, LULC, and mean annual rainfall into GRP score.
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import rasterio
from rasterio.enums import Resampling
import geopandas as gpd
import rasterio.features
from shapely.geometry import shape
from path_config import SLOPE, LULC, RAINFALL, RASTERS_DIR

IN_DIR = str(RASTERS_DIR)
SLOPE = str(SLOPE)
LULC = str(LULC)
RAIN = str(RAINFALL)

OUT_SCORE = os.path.join(IN_DIR, "grp_score_lucknow.tif")
OUT_CLASS = os.path.join(IN_DIR, "grp_class_lucknow.tif")
OUT_SHP = os.path.join(IN_DIR, "grp_class_lucknow.shp")

# weights (example): tune these with domain expert
W_SLOPE = 0.5
W_LULC = 0.3
W_RAIN = 0.2

def read_arr(path):
    if not os.path.exists(path):
        return None, None
    with rasterio.open(path) as src:
        arr = src.read(1).astype('float32')
        prof = src.profile
    return arr, prof

def norm(arr, higher_is_better=True):
    a = np.array(arr, dtype=float)
    mask = np.isfinite(a)
    if not mask.any():
        return a
    amin = np.nanmin(a[mask])
    amax = np.nanmax(a[mask])
    if amax - amin == 0:
        n = np.zeros_like(a)
    else:
        n = (a - amin) / (amax - amin)
    if not higher_is_better:
        n = 1.0 - n
    n[~mask] = np.nan
    return n

# read slope
slope, prof = read_arr(SLOPE)
if slope is None:
    raise SystemExit("Slope missing")
slope_n = norm(slope, higher_is_better=False)  # low slope better

# read lulc and map to weight (assumes lulc nodata are nan)
lulc_arr, p_l = read_arr(LULC)
if lulc_arr is None:
    print("LULC missing, running without it")
    lulc_n = None
else:
    # mapping - choose consistent mapping as earlier
    LMAP = {10:0.6,20:0.5,30:0.6,40:0.8,50:0.1,60:0.7,80:0.2,90:0.1,95:0.2}
    lulc_w = np.full(lulc_arr.shape, np.nan, dtype=float)
    # treat 0 as nodata if present
    lulc_arr = np.where(lulc_arr==0, np.nan, lulc_arr)
    for code, wt in LMAP.items():
        lulc_w[lulc_arr==code] = wt
    # normalize lulc weights to 0-1 (they already 0-1) but ensure finite
    lulc_n = np.array(lulc_w, dtype=float)
    lulc_n[~np.isfinite(lulc_n)] = np.nan

# read rainfall
rain, p_r = read_arr(RAIN)
if rain is None:
    print("Rain missing, running without it")
    rain_n = None
else:
    rain_n = norm(rain, higher_is_better=True)

# Decide present layers and normalize weights
layers = {'slope':slope_n}
if lulc_n is not None:
    layers['lulc'] = lulc_n
if rain_n is not None:
    layers['rain'] = rain_n

present = list(layers.keys())
weights = {'slope':W_SLOPE, 'lulc':W_LULC, 'rain':W_RAIN}
# normalize to present
w_pres = {k:weights.get(k,0.0) for k in present}
s = sum(w_pres.values())
if s==0:
    w_pres = {k:1.0/len(present) for k in present}
else:
    w_pres = {k:v/s for k,v in w_pres.items()}

print("Present layers:", present, "weights:", w_pres)

# combine
score = np.zeros_like(slope_n, dtype=float)
mask_any = np.zeros_like(score, dtype=bool)
for k,w in w_pres.items():
    arr = layers[k]
    valid = np.isfinite(arr)
    mask_any = mask_any | valid
    arr_f = np.where(valid, arr, 0.0)
    score += w * arr_f

score[~mask_any] = np.nan
score = np.clip(score, 0, 1)

# write score
prof_out = prof.copy()
prof_out.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)
with rasterio.open(OUT_SCORE, 'w', **prof_out) as dst:
    dst.write(score.astype('float32'), 1)
print("Wrote", OUT_SCORE)

# classify
mask = np.isfinite(score)
cls = np.full(score.shape, -9999, dtype='int16')
if mask.any():
    q1 = np.nanquantile(score[mask], 1/3)
    q2 = np.nanquantile(score[mask], 2/3)
    cls[(score <= q1) & mask] = 0
    cls[(score > q1) & (score <= q2) & mask] = 1
    cls[(score > q2) & mask] = 2

prof_cls = prof.copy()
prof_cls.update(dtype=rasterio.int16, count=1, compress='lzw', nodata=-9999)
with rasterio.open(OUT_CLASS, 'w', **prof_cls) as dst:
    dst.write(cls.astype('int16'), 1)
print("Wrote", OUT_CLASS)

# optional polygonize for shapefile (same as previous)
with rasterio.open(OUT_CLASS) as src:
    image = src.read(1)
    mask = image != -9999
    transform = src.transform
    shapes = rasterio.features.shapes(image, mask=mask, transform=transform)
    geoms = []
    vals = []
    for geom, val in shapes:
        if int(val) == -9999:
            continue
        geoms.append(shape(geom))
        vals.append(int(val))
    import geopandas as gpd
    gdf = gpd.GeoDataFrame({'class': vals}, geometry=geoms, crs=src.crs)
    gdf.to_file(OUT_SHP)
    print("Wrote", OUT_SHP)
