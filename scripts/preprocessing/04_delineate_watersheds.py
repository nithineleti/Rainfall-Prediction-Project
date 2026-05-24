#!/usr/bin/env python3
"""
scripts/preprocessing/04_delineate_watersheds.py

Delineate upstream watersheds for pour points and compute per-watershed stats.

Outputs:
 - data/rasters/watersheds.gpkg (layer 'watersheds') with attributes:
     id, area_km2, n_pixels, total_stream_length_km, mean_flowacc, mean_slope, mean_dd
 - data/rasters/watersheds_stats.csv (same attributes as CSV)

Usage examples:
  # use top 50 stream accumulation peaks as pour points
  python scripts/preprocessing/04_delineate_watersheds.py --n-pours 50 --vectorize

  # use accumulation threshold (cells) to pick pour points
  python scripts/preprocessing/04_delineate_watersheds.py --threshold-cells 100 --vectorize

  # provide your own pour points shapefile
  python scripts/preprocessing/04_delineate_watersheds.py --pour-shp data/points/outlets.shp --vectorize

Notes:
 - Requires: rasterio, numpy, geopandas, shapely, scipy
 - Works with your flow_dir where values 0..7 indicate D8 neighbour index (same indexing as previous scripts),
   and flow_acc as upstream cell counts.
 - Memory: keeps a few full-size arrays in memory; should be fine for ~30M cells on a machine with several GB RAM.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import time
import math
from collections import deque, defaultdict

import numpy as np
import rasterio
from rasterio.features import shapes
from rasterio.transform import Affine
import geopandas as gpd
from shapely.geometry import shape, mapping
from scipy import ndimage

# default paths (use your path_config if available)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
try:
    import path_config as pc  # type: ignore
except Exception:
    pc = None

DEFAULT_DEM = str(pc.RAW_DEM) if pc and hasattr(pc, "RAW_DEM") else "data/raw/lucknow_dem_12.5/dem_lucknow_12.5.tif"
DEFAULT_FLOWDIR = str(Path("data/rasters/flow_dir.tif"))
DEFAULT_FLOWACC = str(Path("data/rasters/flow_acc_lucknow.tif"))
DEFAULT_STREAM = str(Path("data/rasters/stream_network_lucknow.tif"))
DEFAULT_SLOPE = str(Path("data/rasters/slope_lucknow.tif"))
DEFAULT_DD = str(Path("data/rasters/drainage_density_lucknow.tif"))
OUT_GPKG = str(Path("data/rasters/watersheds.gpkg"))
OUT_CSV = str(Path("data/rasters/watersheds_stats.csv"))

# neighbor offsets consistent with your D8 convention (E, NE, N, NW, W, SW, S, SE)
_NBR_OFFSETS = [(0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1)]

def raster_pixel_area_km2(profile, shape):
    """Approx pixel area in km^2 (average of x/y), handling geographic CRS by lat scaling."""
    transform = profile["transform"]
    xres = transform.a
    yres = -transform.e
    crs = profile.get("crs", None)
    rows, cols = shape
    if crs and getattr(crs, "is_geographic", False):
        top_left_x, top_left_y = transform * (0, 0)
        center_lat = top_left_y - (rows / 2.0) * (-transform.e)
        meters_per_deg = 111320.0
        lon_scale = math.cos(math.radians(center_lat))
        px_m = abs(xres) * meters_per_deg * lon_scale
        py_m = abs(yres) * meters_per_deg
    else:
        px_m = abs(xres)
        py_m = abs(yres)
    return ((px_m + py_m) / 2.0 / 1000.0) ** 2  # km^2

def read_arrays(flowdir_path, flowacc_path, stream_path=None, slope_path=None, dd_path=None):
    with rasterio.open(flowdir_path) as src_fd:
        fd = src_fd.read(1).astype(np.int8)
        fd_profile = src_fd.profile.copy()
    with rasterio.open(flowacc_path) as src_fa:
        fa = src_fa.read(1).astype(np.float32)
        fa_profile = src_fa.profile.copy()
    # Use profile from flowacc for transform/crs/pixel size (they should match)
    profile = fa_profile
    stream = None
    if stream_path:
        try:
            with rasterio.open(stream_path) as s:
                stream = s.read(1).astype(np.uint8)
        except Exception:
            stream = None
    slope = None
    if slope_path:
        try:
            with rasterio.open(slope_path) as s:
                slope = s.read(1).astype(np.float32)
        except Exception:
            slope = None
    dd = None
    if dd_path:
        try:
            with rasterio.open(dd_path) as s:
                dd = s.read(1).astype(np.float32)
        except Exception:
            dd = None

    return fd, fa, stream, slope, dd, profile

def make_dest_index(flowdir):
    """Return flat dest_idx array of length n where dest_idx[i] is flat index of downstream cell or -1."""
    rows, cols = flowdir.shape
    n = rows * cols
    flat_idx = np.arange(n, dtype=np.int32).reshape(rows, cols)
    dest_idx = -np.ones(n, dtype=np.int32)
    for d, (dr, dc) in enumerate(_NBR_OFFSETS):
        sel = (flowdir == d)
        if not sel.any():
            continue
        # source flat positions
        src_flat = np.flatnonzero(sel)
        rs, cs = np.divmod(src_flat, cols)
        rr = rs + dr
        cc = cs + dc
        in_bounds = (rr >= 0) & (rr < rows) & (cc >= 0) & (cc < cols)
        valid_src = src_flat[in_bounds]
        dest_flats = (rr[in_bounds] * cols + cc[in_bounds]).astype(np.int32)
        dest_idx[valid_src] = dest_flats
    return dest_idx

def build_reverse_index(dest_idx):
    """Return adjacency list: for each flat index j, a list of flat indices that flow into j."""
    n = dest_idx.size
    rev = [[] for _ in range(n)]
    valid = dest_idx >= 0
    srcs = np.flatnonzero(valid)
    dests = dest_idx[valid]
    for s, d in zip(srcs, dests):
        rev[d].append(int(s))
    return rev

def pick_pour_points_from_stream(flowacc, stream, n_pours=None, threshold_cells=None):
    """Return list of flat indices to use as pour points based on stream network & flowacc."""
    if stream is None:
        # fallback: use highest flowacc cells across full raster
        flat = np.argsort(np.nan_to_num(flowacc, nan=-1).ravel())[::-1]
        chosen = []
        i = 0
        while len(chosen) < (n_pours or 1) and i < flat.size:
            idx = int(flat[i])
            if np.isfinite(flowacc.ravel()[idx]) and flowacc.ravel()[idx] > 0:
                chosen.append(idx)
            i += 1
        return chosen

    # stream exists: consider stream pixels only
    stream_mask = (stream == 1)
    flat_idx = np.flatnonzero(stream_mask)
    if threshold_cells is not None:
        # choose local maxima on stream where flowacc >= threshold
        sel = flat_idx[np.where(flowacc.ravel()[flat_idx] >= threshold_cells)[0]]
        # choose peaks (simple: pick those with flowacc >= neighbors on stream)
        # but simpler: return all sel (they are pour points). To avoid many, we will return unique peaks.
        return sel.tolist()

    if n_pours is not None:
        # pick top-n stream pixels by flowacc
        vals = flowacc.ravel()[flat_idx]
        order = np.argsort(vals)[::-1]
        chosen = flat_idx[order][:n_pours]
        return chosen.tolist()

    # default: return top 20 stream pixels
    vals = flowacc.ravel()[flat_idx]
    order = np.argsort(vals)[::-1]
    chosen = flat_idx[order][:20]
    return chosen.tolist()

def delineate_upstream(dest_idx, reverse_index, pour_flat):
    """Return boolean mask (flat) of cells that drain to pour_flat (including it)."""
    n = dest_idx.size
    mask = np.zeros(n, dtype=np.bool_)
    q = deque([int(pour_flat)])
    mask[int(pour_flat)] = True
    while q:
        v = q.popleft()
        for u in reverse_index[v]:
            if not mask[u]:
                mask[u] = True
                q.append(u)
    return mask

def vectorize_mask_to_polygons(mask_flat, transform, crs, out_layer_name=None):
    """Convert boolean mask (flat) to polygon geometries (list of shapely geometries)."""
    # mask_flat is 1D; need to reshape to (rows, cols) externally
    # This function will be called with the 2D mask arr
    raise NotImplementedError("Use rasterio.features.shapes outside this helper.")

def main():
    p = argparse.ArgumentParser(description="Delineate watersheds for pour points and compute stats")
    p.add_argument("--flowdir", default=DEFAULT_FLOWDIR)
    p.add_argument("--flowacc", default=DEFAULT_FLOWACC)
    p.add_argument("--stream", default=DEFAULT_STREAM, help="Binary stream raster (1=stream). Optional.")
    p.add_argument("--slope", default=DEFAULT_SLOPE, help="Slope raster (degrees), optional.")
    p.add_argument("--dd", default=DEFAULT_DD, help="Drainage density raster, optional.")
    p.add_argument("--dem", default=DEFAULT_DEM, help="DEM (optional, used only to report CRS / debug).")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--n-pours", type=int, help="Pick top-N stream accumulation pixels as pour points")
    group.add_argument("--threshold-cells", type=float, help="Pick all stream pixels with accumulation >= threshold (cells)")
    p.add_argument("--pour-shp", help="Optional shapefile/geojson of pour points (will override n-pours/threshold if given)")
    p.add_argument("--vectorize", action="store_true", help="Write watersheds to GeoPackage (default true)")
    p.add_argument("--out-gpkg", default=OUT_GPKG)
    p.add_argument("--out-csv", default=OUT_CSV)
    args = p.parse_args()

    start = time.time()
    fd_path = str(Path(args.flowdir).resolve())
    fa_path = str(Path(args.flowacc).resolve())
    stream_path = str(Path(args.stream).resolve()) if args.stream else None
    slope_path = str(Path(args.slope).resolve()) if args.slope else None
    dd_path = str(Path(args.dd).resolve()) if args.dd else None

    print("Reading rasters...")
    fd, fa, stream, slope, dd, profile = read_arrays(fd_path, fa_path, stream_path, slope_path, dd_path)
    rows, cols = fa.shape
    n = rows * cols
    print("Shape:", fa.shape, "n cells:", n)
    px_area_km2 = raster_pixel_area_km2(profile, fa.shape)
    px_len_km = math.sqrt(px_area_km2)  # approx pixel length in km (avg)
    print(f"Pixel area ~ {px_area_km2:.6f} km^2; pixel length ~ {px_len_km:.6f} km")

    # Determine pour points
    pour_flats = []
    if args.pour_shp:
        print("Loading pour points from:", args.pour_shp)
        g = gpd.read_file(args.pour_shp)
        # map geometries to flat indices using profile.transform
        inv_transform = ~profile["transform"]
        for geom in g.geometry:
            x, y = geom.x, geom.y
            colf, rowf = inv_transform * (x, y)
            r = int(round(rowf)); c = int(round(colf))
            if 0 <= r < rows and 0 <= c < cols:
                pour_flats.append(r * cols + c)
    else:
        print("Selecting pour points from stream / flowacc ...")
        pour_flats = pick_pour_points_from_stream(fa, stream, n_pours=args.n_pours, threshold_cells=args.threshold_cells)
    if len(pour_flats) == 0:
        print("No pour points identified. Aborting.")
        return

    print("Selected pour points (flat indices):", pour_flats[:20], " (total:", len(pour_flats), ")")

    # Build dest index and reverse adjacency
    print("Building downstream index and reverse adjacency ...")
    dest_idx = make_dest_index(fd)
    reverse_idx = build_reverse_index(dest_idx)
    print("Reverse adjacency built.")

    # loop pour points, delineate upstream basin for each
    out_rows = []
    geoms = []
    layer_crs = profile.get("crs", None)
    gpkg = Path(args.out_gpkg)
    gpkg.parent.mkdir(parents=True, exist_ok=True)
    for i, pf in enumerate(pour_flats, start=1):
        print(f"[{i}/{len(pour_flats)}] Delineating basin for pour flat {pf} ...")
        mask_flat = delineate_upstream(dest_idx, reverse_idx, pf)  # boolean 1D array
        # convert to 2D mask
        mask2 = mask_flat.reshape((rows, cols))
        n_cells = int(np.count_nonzero(mask2))
        area_km2 = n_cells * px_area_km2
        # compute sums inside basin
        fa_vals = fa[mask2]
        mean_fa = float(np.nanmean(fa_vals)) if fa_vals.size else float('nan')
        total_stream_km = 0.0
        if stream is not None:
            stream_count = int(np.count_nonzero(stream & mask2))
            total_stream_km = float(stream_count * px_len_km)
        mean_slope = float(np.nanmean(slope[mask2])) if (slope is not None and mask2.any()) else float('nan')
        mean_dd = float(np.nanmean(dd[mask2])) if (dd is not None and mask2.any()) else float('nan')

        out_rows.append({
            "id": i,
            "pour_flat": int(pf),
            "n_pixels": n_cells,
            "area_km2": area_km2,
            "total_stream_km": total_stream_km,
            "mean_flowacc": mean_fa,
            "mean_slope": mean_slope,
            "mean_dd": mean_dd
        })

        # vectorize mask to polygon(s)
        shapes_gen = shapes(mask2.astype('uint8'), mask=mask2, transform=profile["transform"])
        polys = []
        for geom, val in shapes_gen:
            if int(val) == 1:
                polys.append(shape(geom))
        if polys:
            # dissolve polygons into single geometry
            # use unary_union via shapely
            from shapely.ops import unary_union
            poly = unary_union(polys)
            geoms.append((poly, out_rows[-1]))  # store geometry + attributes
        else:
            geoms.append((None, out_rows[-1]))

    # write outputs: GeoPackage & CSV
    import pandas as pd
    df = pd.DataFrame(out_rows)
    df.to_csv(args.out_csv, index=False)
    print("Wrote CSV:", args.out_csv)

    # write geopackage layer (if requested) -- FIXED: pass Shapely geometries (not mapping dicts)
    if args.vectorize:
        import geopandas as gpd
        from shapely.geometry import mapping as shapely_mapping, shape as shapely_shape
        rec_geoms = []
        rec_props = []
        for geom, attrs in geoms:
            if geom is None:
                continue
            # geom is already a Shapely geometry (we created it with unary_union earlier)
            if not hasattr(geom, "geom_type"):
                # if it's a geojson-like geometry dict, convert
                try:
                    geom = shapely_shape(geom)
                except Exception:
                    continue
            rec_geoms.append(geom)
            # ensure properties are simple types (int/float/str)
            props = {k: (int(v) if isinstance(v, (np.integer,)) else float(v) if isinstance(v, (np.floating,)) else v) for k, v in attrs.items()}
            rec_props.append(props)

        if rec_geoms:
            gdf = gpd.GeoDataFrame(rec_props, geometry=rec_geoms, crs=layer_crs)
            # ensure id field is int
            if "id" in gdf.columns:
                gdf["id"] = gdf["id"].astype(int)
            # write gpkg (layer name 'watersheds')
            gdf.to_file(args.out_gpkg, layer="watersheds", driver="GPKG")
            print("Wrote GeoPackage:", args.out_gpkg)
        else:
            print("No watershed polygons to write (all basins empty?)")


    elapsed = time.time() - start
    print(f"Done. elapsed {elapsed:.1f}s. Processed {len(pour_flats)} basins.")
    print("Tip: inspect watersheds.gpkg in QGIS, style by area_km2 or total_stream_km.")

if __name__ == "__main__":
    main()
