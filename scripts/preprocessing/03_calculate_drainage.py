#!/usr/bin/env python3
"""
scripts/preprocessing/03_calculate_drainage.py

Compute D8 flow directions, flow accumulation, stream network and drainage density.

Improvements over previous version:
 - Vectorized D8 flow-direction using numpy stacks (fast)
 - Efficient flow-accumulation using flattened indices + topological queue
 - Proper CRS-aware pixel length and area calculation (projects degrees->meters)
 - CLI options: thresholds in cells or km2, optional vectorization to shapefile
 - Cleaner logging and diagnostics

Outputs (by default, from path_config):
 - flow_acc_lucknow.tif      (float32)   : upstream cell count (or area units)
 - stream_network_lucknow.tif(int8)     : binary stream network (1 = stream)
 - drainage_density_lucknow.tif(float32): local drainage density (km per km^2)
 - optional: stream_network_lucknow.shp (if --vectorize)

Usage:
    python scripts/preprocessing/03_calculate_drainage.py [--dem DEM] [--stream-threshold 20] [--threshold-units cells|km2] [--vectorize]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import math
import time
import warnings
from collections import deque
from typing import Tuple, Optional

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.features import shapes
import rasterio.features
from scipy import ndimage

# Add project root to path so path_config can be imported (if running from scripts dir)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
try:
    import path_config as pc  # type: ignore
except Exception:
    pc = None

# Default neighbor ordering for D8 (E, NE, N, NW, W, SW, S, SE)
_NBR_OFFSETS = np.array([
    (0, 1),   # E
    (-1, 1),  # NE
    (-1, 0),  # N
    (-1, -1), # NW
    (0, -1),  # W
    (1, -1),  # SW
    (1, 0),   # S
    (1, 1),   # SE
], dtype=int)

# diagonal distances relative to pixel (used if you want weighted length)
_NBR_DIST = np.array([1.0, math.sqrt(2), 1.0, math.sqrt(2), 1.0, math.sqrt(2), 1.0, math.sqrt(2)], dtype=float)


def compute_d8_flowdir_vectorized(dem: np.ndarray, valid_mask: np.ndarray) -> np.ndarray:
    """
    Vectorized D8 flow direction:
    - dem: 2D float array (np.nan for nodata)
    - valid_mask: bool array True where dem is valid
    Returns:
      flowdir: int8 array with values 0..7 for neighbor index, -1 for sink/nodata
    """
    rows, cols = dem.shape
    # pad dem with nan
    pad = 1
    dpad = np.pad(dem, pad_width=pad, mode='constant', constant_values=np.nan)
    # build neighbor stacks: shape (8, rows, cols)
    neighs = np.empty((8, rows, cols), dtype=float)
    # center (not used directly here)
    center = dpad[pad:pad + rows, pad:pad + cols]

    # fill neighbor arrays with shifts
    # map same ordering as _NBR_OFFSETS
    shifts = [
        (0, 1), (-1, 1), (-1, 0), (-1, -1),
        (0, -1), (1, -1), (1, 0), (1, 1)
    ]
    for k, (dr, dc) in enumerate(shifts):
        neighs[k] = dpad[pad + dr: pad + dr + rows, pad + dc: pad + dc + cols]

    # compute elevation drops: center - neighbor (positive = downhill)
    diffs = center[np.newaxis, :, :] - neighs  # shape (8, rows, cols)

    # For masked/invalid neighbors, set diffs to -inf so they are never chosen
    diffs_masked = np.where(np.isfinite(diffs), diffs, -np.inf)

    # best neighbor index (argmax) and its drop value
    best_idx = np.argmax(diffs_masked, axis=0)         # shape (rows, cols)
    best_val = np.take_along_axis(diffs_masked, best_idx[np.newaxis, :, :], axis=0)[0]

    # create flowdir array; where center is NaN or best_val <= 0 set -1 (sink/nodata)
    flowdir = -np.ones_like(best_idx, dtype=np.int8)
    valid_center = np.isfinite(center)
    downhill = best_val > 0.0
    # only assign where center valid and there exists a downhill neighbor
    mask_assign = valid_center & downhill
    flowdir[mask_assign] = best_idx[mask_assign].astype(np.int8)

    # respect original valid_mask: set flowdir = -1 where not valid
    flowdir[~valid_mask] = -1

    return flowdir


def compute_flow_accumulation_topo(flowdir: np.ndarray) -> np.ndarray:
    """
    Compute flow accumulation (# upstream cells including self) using topological approach.

    Algorithm:
    - flatten grid to 1D indices
    - compute destination index for each cell (or -1)
    - compute indegree using bincount
    - initialize queue with indeg==0 (sources)
    - pop sources, add their accumulation to their destination, decrement indegree of destination, enqueue when 0

    Returns float32 array of upstream cell counts (nan for sink/nodata).
    """
    rows, cols = flowdir.shape
    n = rows * cols
    flat_idx = np.arange(n, dtype=np.int32).reshape(rows, cols)

    # compute destination indices: for each cell with d>=0, dest = flat_idx[r+dr, c+dc]
    dest_idx = -np.ones(n, dtype=np.int32)
    mask_valid = (flowdir >= 0)
    # compute r,c arrays
    r_coords, c_coords = np.divmod(np.arange(n), cols)
    # easier vectorized: iterate over 8 directions and set dest where flowdir==k
    for k, (dr, dc) in enumerate(_NBR_OFFSETS):
        sel = (flowdir == k)
        if not sel.any():
            continue
        rr = r_coords[sel.flat]
        cc = c_coords[sel.flat]
        dest_r = rr + dr
        dest_c = cc + dc
        in_bounds = (dest_r >= 0) & (dest_r < rows) & (dest_c >= 0) & (dest_c < cols)
        valid_src_flat = np.flatnonzero(sel)
        # Only set destinations for those that remain in bounds; others keep -1
        dest_flat = np.full(valid_src_flat.shape, -1, dtype=np.int32)
        if in_bounds.any():
            valid_idx = np.flatnonzero(in_bounds)
            dest_positions = (dest_r[in_bounds] * cols + dest_c[in_bounds]).astype(np.int32)
            dest_flat[valid_idx] = dest_positions
        dest_idx[valid_src_flat] = dest_flat

    # indegree: number of incoming links for each destination
    # dest_idx contains -1 for sinks; filter valid
    valid_dest_mask = dest_idx >= 0
    if valid_dest_mask.any():
        indeg = np.bincount(dest_idx[valid_dest_mask], minlength=n).astype(np.int32)
    else:
        indeg = np.zeros(n, dtype=np.int32)

    # initialize accumulation: 1 per valid cell (self)
    acc = np.zeros(n, dtype=np.float64)
    src_valid_cells = (flowdir.flatten() >= 0)
    acc[src_valid_cells] = 1.0

    # initial queue: indices with indeg == 0 and valid cells
    q = deque(np.flatnonzero((indeg == 0) & src_valid_cells))

    processed = 0
    while q:
        i = q.popleft()
        processed += 1
        d = dest_idx[i]
        if d >= 0:
            acc[d] += acc[i]
            indeg[d] -= 1
            if indeg[d] == 0:
                # only enqueue if destination is a valid cell (it should be)
                if src_valid_cells[d]:
                    q.append(d)

    # reshape
    acc_grid = acc.reshape((rows, cols))
    # mark NaN for flowdir < 0 (sinks/nodata)
    acc_grid = np.where(flowdir >= 0, acc_grid.astype(np.float32), np.nan)
    return acc_grid


def raster_pixel_length_km(profile: rasterio.profiles.Profile, shape: Tuple[int, int]) -> float:
    """
    Compute approximate pixel length (average of x/y) in km using profile.transform and CRS.
    If CRS is geographic, convert degrees->meters using center latitude.
    """
    transform = profile['transform']
    width, height = shape[1], shape[0]
    xres = transform.a
    yres = -transform.e
    crs = profile.get('crs', None)

    if crs and getattr(crs, "is_geographic", False):
        # approximate using center latitude
        top_left_x, top_left_y = transform * (0, 0)
        center_lat = top_left_y - (height / 2.0) * yres
        meters_per_deg = 111320.0
        lon_scale = math.cos(math.radians(center_lat))
        px_m = abs(xres) * meters_per_deg * lon_scale
        py_m = abs(yres) * meters_per_deg
    else:
        # projected units assumed meters
        px_m = abs(xres)
        py_m = abs(yres)

    return float((px_m + py_m) / 2.0 / 1000.0)  # km


def vectorize_streams(stream_raster: np.ndarray, transform, crs, out_shp: Path) -> None:
    """Vectorize binary stream raster to a shapefile (lines approximated as polygons' boundaries)."""
    try:
        import geopandas as gpd
        from shapely.geometry import shape
    except Exception:
        print("⚠️  geopandas/shapely not installed; skipping vectorization.")
        return

    # generate shapes for stream pixels (value 1)
    mask = np.isfinite(stream_raster) & (stream_raster == 1)
    if not mask.any():
        print("No stream pixels to vectorize.")
        return

    results = []
    for geom, value in shapes(stream_raster.astype(np.uint8), mask=mask, transform=transform):
        if int(value) == 1:
            results.append(shape(geom))

    if not results:
        print("No shapes extracted.")
        return

    gdf = gpd.GeoDataFrame({"geometry": results}, crs=crs)
    # optionally dissolve into a single multilinestring/polygon boundary
    gdf.to_file(out_shp, driver="ESRI Shapefile")
    print(f"Wrote vector streams to {out_shp}")


def main():
    p = argparse.ArgumentParser(description="Compute flowdir, flowacc, stream network and drainage density")
    p.add_argument("--dem", help="Input DEM (override path_config.RAW_DEM)")
    p.add_argument("--flowacc-out", help="Flow accumulation output (override path_config.FLOW_ACC)")
    p.add_argument("--stream-out", help="Stream network output (override path_config.STREAM_NETWORK)")
    p.add_argument("--dd-out", help="Drainage density output (override path_config.DRAINAGE_DENSITY)")
    p.add_argument("--stream-threshold", type=float, default=20.0, help="Threshold for stream extraction (cells or km2 based on --threshold-units)")
    p.add_argument("--threshold-units", choices=("cells", "km2"), default="cells", help="Interpret stream-threshold as upstream cell count or upstream area (km^2)")
    p.add_argument("--window-size", type=int, default=31, help="Window size for drainage density (odd number)")
    p.add_argument("--vectorize", action="store_true", help="Export stream network as shapefile (requires geopandas)")
    args = p.parse_args()

    # resolve paths with path_config fallback
    dem_path = args.dem or (pc.RAW_DEM if pc and hasattr(pc, "RAW_DEM") else None)
    flowacc_path = args.flowacc_out or (pc.FLOW_ACC if pc and hasattr(pc, "FLOW_ACC") else "data/rasters/flow_acc.tif")
    stream_path = args.stream_out or (pc.STREAM_NETWORK if pc and hasattr(pc, "STREAM_NETWORK") else "data/rasters/stream_network.tif")
    dd_path = args.dd_out or (pc.DRAINAGE_DENSITY if pc and hasattr(pc, "DRAINAGE_DENSITY") else "data/rasters/drainage_density.tif")

    if dem_path is None:
        sys.exit("ERROR: Provide --dem or set path_config.RAW_DEM")

    dem_path = str(Path(dem_path).resolve())
    flowacc_path = str(Path(flowacc_path).resolve())
    stream_path = str(Path(stream_path).resolve())
    dd_path = str(Path(dd_path).resolve())

    print("DEM:", dem_path)
    print("Flow accumulation out:", flowacc_path)
    print("Stream out:", stream_path)
    print("Drainage density out:", dd_path)
    start_time = time.time()

    with rasterio.open(dem_path) as src:
        dem = src.read(1, masked=True).astype(float)
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs
        nodata = src.nodata
        shape = dem.shape
        print("DEM shape:", shape, "CRS:", crs)

        # prepare dem array with np.nan for invalid
        dem_arr = dem.filled(np.nan) if hasattr(dem, "filled") else dem
        valid_mask = np.isfinite(dem_arr)

        # pixel length in km (average)
        px_len_km = raster_pixel_length_km(profile, shape)
        print(f"Approx pixel length: {px_len_km:.6f} km (avg of x/y). Pixel area ~ {px_len_km**2:.6f} km^2")

    # compute D8 flow directions (vectorized)
    print("Computing D8 flow directions ...")
    t0 = time.time()
    flowdir = compute_d8_flowdir_vectorized(dem_arr, valid_mask)
    print(f"Flowdir done in {time.time()-t0:.2f}s")

    # compute flow accumulation (topological)
    print("Computing flow accumulation ...")
    t0 = time.time()
    flowacc = compute_flow_accumulation_topo(flowdir)
    print(f"Flow accumulation done in {time.time()-t0:.2f}s")

    # write flow accumulation (counts of upstream cells)
    profile_out = profile.copy()
    profile_out.update(dtype=rasterio.float32, count=1, compress="lzw", nodata=np.nan)
    with rasterio.open(flowacc_path, "w", **profile_out) as dst:
        dst.write(np.where(np.isfinite(flowacc), flowacc.astype(np.float32), np.nan), 1)
    print("Wrote flow accumulation to:", flowacc_path)

    # write flowdir (int8) file
    flowdir_out = str(Path(flowacc_path).with_name("flow_dir.tif"))
    pdir = profile.copy()
    pdir.update(dtype=rasterio.int8, count=1, nodata=-1)
    with rasterio.open(flowdir_out, "w", **pdir) as dst:
        dst.write(flowdir.astype(np.int8), 1)
    print("Wrote flow directions to:", flowdir_out)

    # decide stream extraction threshold logic
    if args.threshold_units == "cells":
        threshold_cells = int(args.stream_threshold)
        print(f"Using threshold: {threshold_cells} upstream cells")
    else:
        # threshold in km^2: convert to cells by dividing by pixel area
        cell_area_km2 = px_len_km * px_len_km
        threshold_cells = int(math.ceil(float(args.stream_threshold) / cell_area_km2))
        print(f"Using threshold: {args.stream_threshold} km^2 ≈ {threshold_cells} upstream cells (pixel area {cell_area_km2:.6f} km^2)")

    # extract stream network: accumulation >= threshold_cells
    stream = np.zeros_like(flowacc, dtype=np.int8)
    stream[np.where(flowacc >= threshold_cells)] = 1

    # morphological connect and thin
    print("Performing morphological connectivity (dilate/erode) to improve network)")
    struct = np.array([[0, 1, 0],
                       [1, 1, 1],
                       [0, 1, 0]], dtype=np.bool_)
    stream_conn = ndimage.binary_dilation(stream, structure=struct, iterations=2)
    stream_conn = ndimage.binary_erosion(stream_conn, structure=struct, iterations=1)
    stream = stream_conn.astype(np.int8)
    print("Stream pixels:", int(np.sum(stream)))

    # write stream raster
    with rasterio.open(stream_path, "w", **profile_out) as dst:
        dst.write(stream.astype(np.int8), 1)
    print("Wrote stream network raster to:", stream_path)

    # optional vectorize
    if args.vectorize:
        shp_path = str(Path(stream_path).with_suffix(".shp"))
        print("Vectorizing stream raster to:", shp_path)
        vectorize_streams(stream, transform, crs, Path(shp_path))

    # compute drainage density: local window stream length (km) / window area (km^2)
    win = max(3, (args.window_size // 2) * 2 + 1)  # ensure odd >=3
    print("Computing drainage density with window size:", win)
    kernel = np.ones((win, win), dtype=np.int32)
    stream_count = ndimage.convolve(stream.astype(np.int32), kernel, mode='constant', cval=0)
    stream_length_km = stream_count * px_len_km  # approximate: each stream pixel ~ px_len_km length
    window_area_km2 = (win * px_len_km) * (win * px_len_km)
    dd = stream_length_km / window_area_km2
    dd = np.where(np.isfinite(flowacc), dd, np.nan)

    with rasterio.open(dd_path, "w", **profile_out) as dst:
        dst.write(dd.astype(np.float32), 1)
    print("Wrote drainage density raster to:", dd_path)

    elapsed = time.time() - start_time
    print(f"\nDone. Elapsed time: {elapsed:.1f}s")
    # print some summary stats
    print("Flowacc stats: min/max/mean (valid):", np.nanmin(flowacc), np.nanmax(flowacc), np.nanmean(flowacc))
    print("Drainage density stats (km/km^2) valid: min/max/mean:", np.nanmin(dd), np.nanmax(dd), np.nanmean(dd))


if __name__ == "__main__":
    main()
