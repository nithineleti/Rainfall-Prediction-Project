#!/usr/bin/env python3
"""
scripts/postprocessing/stream_skeletonize_and_length.py

Inputs:
 - stream raster: data/rasters/stream_network_lucknow.tif (binary: 0/1)

Outputs:
 - data/rasters/stream_skeleton_pts.shp  (point per skeleton pixel, attribute: seg_id)
 - data/rasters/stream_segments_lengths.csv (seg_id, pixel_count, length_km)
 - optional: data/rasters/stream_polygons.shp (vectorized full stream raster polygons for QA)

Requirements:
    pip install rasterio numpy scipy scikit-image geopandas shapely fiona
"""
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import shapes
from scipy import ndimage
from skimage.morphology import skeletonize
from skimage.measure import label
import geopandas as gpd
from shapely.geometry import Point, shape
from scipy.ndimage import binary_closing
import math
import csv

# configure paths (update if needed)
BASE = Path("data/rasters")
STREAM_RASTER = BASE / "stream_network_lucknow.tif"
SKELETON_POINTS_SHP = BASE / "stream_skeleton_pts.shp"
SEGMENTS_CSV = BASE / "stream_segments_lengths.csv"
STREAM_POLY_SHP = BASE / "stream_polygons.shp"  # optional QA

def pixel_length_km(profile, shape):
    t = profile["transform"]
    xres = t.a
    yres = -t.e
    crs = profile.get("crs", None)
    rows, cols = shape
    if crs and getattr(crs, "is_geographic", False):
        top_left_x, top_left_y = t * (0, 0)
        center_lat = top_left_y - (rows / 2.0) * (-t.e)
        meters_per_deg = 111320.0
        lon_scale = math.cos(math.radians(center_lat))
        px_m = abs(xres) * meters_per_deg * lon_scale
        py_m = abs(yres) * meters_per_deg
    else:
        px_m = abs(xres)
        py_m = abs(yres)
    return (px_m + py_m) / 2.0 / 1000.0  # km

def main():
    if not STREAM_RASTER.exists():
        raise SystemExit(f"Stream raster not found: {STREAM_RASTER}")

    with rasterio.open(STREAM_RASTER) as src:
        arr = src.read(1, masked=True).filled(0).astype(np.uint8)
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs
        shape_arr = arr.shape
        px_km = pixel_length_km(profile, shape_arr)
    print("Loaded stream raster:", STREAM_RASTER)
    print("Pixel length (approx km):", px_km)

    # Ensure binary
    bin_stream = (arr == 1).astype(np.uint8)

    # Optional small morphological clean (remove singletons): uncomment if needed
    bin_stream = binary_closing(bin_stream, structure=np.ones((3,3)), iterations=1)

    # Skeletonize (requires boolean array)
    print("Skeletonizing stream raster (single-pixel centerlines)...")
    skel_bool = skeletonize(bin_stream.astype(bool))
    skel = skel_bool.astype(np.uint8)

    # Label connected components on skeleton
    labeled = label(skel, connectivity=2)  # 1..N, 0 is background
    n_segments = int(labeled.max())
    print("Found skeleton segments:", n_segments)

    # Build CSV summary: count pixels per segment -> length_km = count * px_km
    seg_ids, counts = np.unique(labeled[labeled > 0], return_counts=True)
    rows = []
    for seg_id, count in zip(seg_ids, counts):
        length_km = count * px_km
        rows.append((int(seg_id), int(count), float(length_km)))

    # Write CSV
    SEGMENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(SEGMENTS_CSV, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["seg_id", "pixel_count", "length_km"])
        for r in rows:
            writer.writerow(r)
    print("Wrote segment length CSV:", SEGMENTS_CSV)

    # Create point shapefile of skeleton pixels with seg_id attribute (easy to inspect in QGIS)
    pts = []
    seg_attr = []
    it = np.nditer(labeled, flags=['multi_index'])
    for val in it:
        seg = int(val)
        if seg > 0:
            r, c = it.multi_index
            # center coordinates of pixel
            x, y = rasterio.transform.xy(transform, r, c, offset='center')
            pts.append(Point(x, y))
            seg_attr.append(seg)
    if pts:
        gdf = gpd.GeoDataFrame({"seg_id": seg_attr}, geometry=pts, crs=crs)
        gdf.to_file(SKELETON_POINTS_SHP)
        print("Wrote skeleton points shapefile:", SKELETON_POINTS_SHP)
    else:
        print("No skeleton points found; nothing to write.")

    # Optional: Vectorize full stream raster to polygons for QA (small polygons)
    print("Vectorizing full stream raster to polygons (QA)...")
    shapes_iter = shapes(bin_stream.astype(np.uint8), mask=bin_stream.astype(bool), transform=transform)
    geoms = []
    vals = []
    for geom, val in shapes_iter:
        if int(val) == 1:
            geoms.append(shape(geom))
            vals.append(1)
    if geoms:
        gdfp = gpd.GeoDataFrame({"value": vals}, geometry=geoms, crs=crs)
        gdfp.to_file(STREAM_POLY_SHP)
        print("Wrote stream polygons (QA):", STREAM_POLY_SHP)
    else:
        print("No shapes found during vectorization.")

    print("Done.")

if __name__ == "__main__":
    main()
