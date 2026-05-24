"""
AHP overlay: slope + LULC

Outputs:
 - data/processed/grp_score_lucknow.tif (0-1)
 - data/processed/grp_class_lucknow.tif (0 low,1 med,2 high)
 - data/processed/grp_class_lucknow.shp
Usage:
    python src/ahp_with_lulc.py
"""
import os
import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import shape
import rasterio.features
from rasterio.enums import Resampling

IN_DIR = "data/processed"
SLOPE_TIF = os.path.join(IN_DIR, "slope_lucknow.tif")
LULC_TIF = os.path.join(IN_DIR, "lulc_lucknow.tif")
GRP_SCORE = os.path.join(IN_DIR, "grp_score_lucknow.tif")
GRP_CLASS = os.path.join(IN_DIR, "grp_class_lucknow.tif")
GRP_SHP = os.path.join(IN_DIR, "grp_class_lucknow.shp")

# weights (you can tune)
WEIGHT_SLOPE = 0.6
WEIGHT_LULC = 0.4

def read_raster(path):
    if not os.path.exists(path):
        return None, None
    with rasterio.open(path) as src:
        arr = src.read(1).astype('float32')
        profile = src.profile
    return arr, profile

def minmax_norm(arr):
    a = np.array(arr, dtype=float)
    mask = np.isfinite(a)
    if not mask.any():
        return None
    amin = np.nanmin(a[mask])
    amax = np.nanmax(a[mask])
    if amax - amin == 0:
        return np.zeros_like(a)
    norm = (a - amin) / (amax - amin)
    norm[~mask] = np.nan
    return norm

def classify_score(score):
    mask = np.isfinite(score)
    out = np.full(score.shape, -9999, dtype=np.int16)
    if not mask.any():
        return out
    vals = score[mask]
    q1 = np.quantile(vals, 1/3)
    q2 = np.quantile(vals, 2/3)
    out[(score <= q1) & mask] = 0
    out[(score > q1) & (score <= q2) & mask] = 1
    out[(score > q2) & mask] = 2
    out[~mask] = -9999
    return out

# LULC mapping based on ESA WorldCover classes (v100 codes)
# These are example recharge suitability weights (0-1). Adjust with expert feedback.
LULC_MAP = {
    10: 0.6,   # Tree cover
    20: 0.5,   # Shrubland
    30: 0.6,   # Grassland
    40: 0.8,   # Cropland
    50: 0.2,   # Built-up
    60: 0.7,   # Bare / sparse vegetation
    70: 0.1,   # Snow & ice (unlikely here)
    80: 0.1,   # Permanent water (assign low for recharge mapping)
    90: 0.1,   # Urban / sealed
    95: 0.2    # Wetland / water (lower)
}

def polygonize(raster_path, shp_path):
    with rasterio.open(raster_path) as src:
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
        gdf = gpd.GeoDataFrame({'class': vals}, geometry=geoms, crs=src.crs)
        gdf.to_file(shp_path)
        print("Wrote polygon shapefile:", shp_path)

def main():
    slope, prof_s = read_raster(SLOPE_TIF)
    if slope is None:
        raise FileNotFoundError("Slope raster not found.")
    print("Loaded slope")

    # normalize slope (lower slope -> higher recharge)
    slope_norm = minmax_norm(slope)
    slope_norm = 1.0 - slope_norm  # invert: low slope higher score

    # read LULC
    lulc, prof_l = read_raster(LULC_TIF)
    if lulc is None:
        print("LULC raster not found. Run preprocess_lulc.py first.")
        return
    print("Loaded LULC")
    # if shape differs, resample LULC to slope grid (nearest)
    if (prof_l['transform'] != prof_s['transform']) or (prof_l['width'] != prof_s['width']) or (prof_l['height'] != prof_s['height']):
        print("Resampling LULC to slope grid...")
        data_resampled = np.empty((prof_s['height'], prof_s['width']), dtype='float32')
        with rasterio.open(LULC_TIF) as src:
            rasterio.warp.reproject(
                source=rasterio.band(src, 1),
                destination=data_resampled,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=prof_s['transform'],
                dst_crs=prof_s['crs'],
                resampling=Resampling.nearest
            )
        lulc = data_resampled

    # after reading or resampling lulc into numpy array `lulc`:
    # treat 0 as nodata (WorldCover uses positive codes for classes)
    # convert any 0 values to np.nan so mapping keeps them unmapped
    lulc = np.array(lulc, dtype=float)
    lulc[lulc == 0] = np.nan


    # map lulc classes to weights
    lulc_weight = np.full(lulc.shape, np.nan, dtype=float)
    for code, wt in LULC_MAP.items():
        lulc_weight[lulc == code] = wt
    # If any lulc cells unmapped, set nan
    print("Mapped LULC classes to weights.")

    # combine weights
    total_w = WEIGHT_SLOPE + WEIGHT_LULC
    score = np.zeros_like(slope_norm, dtype=float)
    # handle nan masks
    valid = np.isfinite(slope_norm) | np.isfinite(lulc_weight)
    slope_f = np.where(np.isfinite(slope_norm), slope_norm, 0.0)
    lulc_f = np.where(np.isfinite(lulc_weight), lulc_weight, 0.0)
    score = (WEIGHT_SLOPE*slope_f + WEIGHT_LULC*lulc_f) / total_w
    score[~valid] = np.nan
    score = np.clip(score, 0, 1)

    # write continuous score
    prof_out = prof_s.copy()
    prof_out.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)
    with rasterio.open(GRP_SCORE, 'w', **prof_out) as dst:
        dst.write(score.astype('float32'), 1)
    print("Wrote", GRP_SCORE)

    # classify and write class raster
    cls = classify_score(score)
    prof_cls = prof_s.copy()
    prof_cls.update(dtype=rasterio.int16, count=1, compress='lzw', nodata=-9999)
    with rasterio.open(GRP_CLASS, 'w', **prof_cls) as dst:
        dst.write(cls.astype(rasterio.int16), 1)
    print("Wrote", GRP_CLASS)

    # polygonize
    polygonize(GRP_CLASS, GRP_SHP)

if __name__ == "__main__":
    main()
