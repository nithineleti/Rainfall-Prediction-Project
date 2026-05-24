#!/usr/bin/env python3
"""
scripts/preprocessing/01_process_dem.py

DEM preprocessing (clipping, slope, hillshade) that uses your project's path_config.py.

Features:
 - Adds project root to sys.path so imports like `import path_config` work.
 - Uses path_config constants by default: RAW_DEM, RAW_DISTRICT_SHP, RASTERS_DIR, DEM, SLOPE, HILLSHADE
 - CLI overrides available: --dem, --shp, --outdir, --slope-out, --hill-out
 - Two gradient methods: 'horn' (default) and 'gradient' (numpy)
 - Robust NaN handling with suppressed runtime warnings and median fallback
 - Preserves CRS/transform, writes float32 outputs with LZW compression
"""
from __future__ import annotations

# --- make project root importable so `import path_config` works regardless of CWD ---
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
# ------------------------------------------------------------------------------

import argparse
import os
import warnings
from typing import Tuple

import numpy as np
import rasterio
import rioxarray as rxr
import geopandas as gpd
from scipy import ndimage

# Try to import path_config (your centralized path file)
try:
    import path_config as pc  # type: ignore
except Exception:
    pc = None  # We'll require CLI overrides in this case

# ---------- Utility functions ----------

def ensure_dirs_from_pc():
    """Call path_config.ensure_dirs() if provided; otherwise create RASTERS_DIR if present."""
    if pc is None:
        return
    try:
        if hasattr(pc, "ensure_dirs"):
            pc.ensure_dirs()
        else:
            if getattr(pc, "RASTERS_DIR", None):
                Path(pc.RASTERS_DIR).mkdir(parents=True, exist_ok=True)
    except Exception:
        # non-fatal: continue without raising
        pass

def geographic_spacing_in_meters(lat_center_deg: float) -> Tuple[float, float]:
    """Return approximate meters per degree at given latitude: (meters_per_deg_lon, meters_per_deg_lat)"""
    meters_per_degree_lat = 111132.954 - 559.822 * np.cos(2*np.radians(lat_center_deg)) + 1.175 * np.cos(4*np.radians(lat_center_deg))
    meters_per_degree_lon = (np.pi/180) * 6378137.0 * np.cos(np.radians(lat_center_deg))
    return meters_per_degree_lon, meters_per_degree_lat

def _fill_local_mean(arr: np.ndarray) -> np.ndarray:
    """
    Fill small NoData holes with local mean (3x3). Suppresses RuntimeWarning for empty windows.
    Any remaining NaNs are replaced with global median (or 0 if that is not finite).
    """
    nan_mask = ~np.isfinite(arr)
    arr_filled = arr.copy()
    if nan_mask.any():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            arr_filled = ndimage.generic_filter(arr_filled, np.nanmean, size=3, mode='nearest')
        if np.isnan(arr_filled).any():
            med = np.nanmedian(arr)
            if not np.isfinite(med):
                med = 0.0
            arr_filled = np.where(np.isfinite(arr_filled), arr_filled, med)
    return arr_filled

def compute_gradients_horn(arr: np.ndarray, cellsize_x: float, cellsize_y: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Horn (3x3) finite-difference kernel for dz/dx (east) and dz/dy (north).
    arr: 2D array with np.nan for NoData.
    cellsize_*: spacing in meters.
    """
    nan_mask = ~np.isfinite(arr)
    arr_filled = arr.copy()
    if nan_mask.any():
        arr_filled = _fill_local_mean(arr_filled)

    k_dx = np.array([[-1, 0, 1],
                     [-2, 0, 2],
                     [-1, 0, 1]], dtype=float) / (8.0 * cellsize_x)
    k_dy = np.array([[-1, -2, -1],
                     [ 0,  0,  0],
                     [ 1,  2,  1]], dtype=float) / (8.0 * cellsize_y)

    dx = ndimage.convolve(arr_filled, k_dx, mode='nearest')
    dy = ndimage.convolve(arr_filled, k_dy, mode='nearest')

    dx[nan_mask] = np.nan
    dy[nan_mask] = np.nan
    return dx, dy

def compute_gradients_np_gradient(arr: np.ndarray, cellsize_x: float, cellsize_y: float) -> Tuple[np.ndarray, np.ndarray]:
    """Use numpy.gradient with local fill and median fallback for NaNs."""
    nan_mask = ~np.isfinite(arr)
    arr_filled = arr.copy()
    if nan_mask.any():
        arr_filled = _fill_local_mean(arr_filled)

    dy, dx = np.gradient(arr_filled, cellsize_y, cellsize_x, edge_order=2)
    dx[nan_mask] = np.nan
    dy[nan_mask] = np.nan
    return dx, dy

# ---------- Core processing ----------

def clip_dem_if_needed(dem_in: str, shp_path: str, dem_out: str) -> str:
    """Clip DEM to district geometry if dem_out doesn't exist. Returns path to clipped DEM."""
    if os.path.exists(dem_out):
        print(f"[clip] clipped DEM already exists: {dem_out}")
        return dem_out

    print(f"[clip] clipping DEM {dem_in} to shapefile {shp_path} -> {dem_out}")
    dem = rxr.open_rasterio(dem_in, masked=True)
    shp = gpd.read_file(shp_path)
    # reproject shp if needed
    if shp.crs != dem.rio.crs:
        shp = shp.to_crs(dem.rio.crs)
    demc = dem.rio.clip(shp.geometry, shp.crs, drop=True, invert=False)
    demc.rio.to_raster(dem_out)
    print(f"[clip] wrote clipped DEM: {dem_out}")
    return dem_out

def compute_slope_and_hillshade(dem_path: str, slope_out: str, hill_out: str,
                                method: str = "horn", azimuth: float = 315.0, altitude: float = 45.0) -> None:
    """Compute slope (degrees) and hillshade (0-255) and write them."""
    print(f"[slope] loading DEM: {dem_path}")
    with rasterio.open(dem_path) as src:
        profile = src.profile.copy()
        nodata = src.nodata
        crs = src.crs
        transform = src.transform
        width = src.width
        height = src.height

        arr = src.read(1).astype('float32')
        if nodata is not None:
            mask = arr == nodata
            arr = np.where(mask, np.nan, arr)
        else:
            mask = ~np.isfinite(arr)
            arr[mask] = np.nan

        xres = float(transform.a)
        yres = abs(float(transform.e))

        if crs and crs.is_geographic:
            # approximate center latitude for converting degrees -> meters
            yoff = transform.f
            e = transform.e
            y_center = yoff + (height / 2.0) * e
            lat_center = float(y_center)
            meters_per_lon, meters_per_lat = geographic_spacing_in_meters(lat_center)
            cellsize_x_m = abs(xres) * meters_per_lon
            cellsize_y_m = abs(yres) * meters_per_lat
            print(f"[slope] CRS geographic. approx meters/deg @ lat {lat_center:.6f}: lon={meters_per_lon:.1f}, lat={meters_per_lat:.1f}")
        else:
            cellsize_x_m = abs(xres)
            cellsize_y_m = abs(yres)

        print(f"[slope] pixel size (m): x={cellsize_x_m:.3f}, y={cellsize_y_m:.3f}")

        if method == "horn":
            dx, dy = compute_gradients_horn(arr, cellsize_x_m, cellsize_y_m)
        else:
            dx, dy = compute_gradients_np_gradient(arr, cellsize_x_m, cellsize_y_m)

        # slope and aspect
        slope_rad = np.arctan(np.sqrt(dx ** 2 + dy ** 2))
        slope_deg = np.degrees(slope_rad)

        aspect = np.arctan2(dy, -dx)
        aspect = np.where(aspect < 0, 2 * np.pi + aspect, aspect)

        # hillshade (0-255)
        az_rad = np.radians(360.0 - azimuth + 90.0)
        alt_rad = np.radians(altitude)
        hs = (np.sin(alt_rad) * np.sin(slope_rad)) + (np.cos(alt_rad) * np.cos(slope_rad) * np.cos(az_rad - aspect))
        hillshade = np.clip(hs, 0.0, 1.0) * 255.0

        valid_mask = np.isfinite(arr)
        slope_out_arr = np.where(valid_mask, slope_deg.astype('float32'), np.nan)
        hill_out_arr = np.where(valid_mask, hillshade.astype('float32'), np.nan)

        out_profile = profile.copy()
        out_profile.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)

    print(f"[slope] writing slope -> {slope_out}")
    with rasterio.open(slope_out, 'w', **out_profile) as dst:
        dst.write(slope_out_arr.astype('float32'), 1)

    print(f"[slope] writing hillshade -> {hill_out}")
    with rasterio.open(hill_out, 'w', **out_profile) as dst:
        dst.write(hill_out_arr.astype('float32'), 1)

    print(f"[slope] finished. slope: {slope_out}, hillshade: {hill_out}")

# ---------- CLI / main ----------

def main():
    parser = argparse.ArgumentParser(description="Clip DEM and compute slope/hillshade using project path_config")
    parser.add_argument("--dem", help="Raw DEM path (override path_config.RAW_DEM)")
    parser.add_argument("--shp", help="District shapefile path (override path_config.RAW_DISTRICT_SHP)")
    parser.add_argument("--outdir", help="Output rasters directory (override path_config.RASTERS_DIR)")
    parser.add_argument("--slope-out", help="Slope output path (override path_config.SLOPE)")
    parser.add_argument("--hill-out", help="Hillshade output path (override path_config.HILLSHADE)")
    parser.add_argument("--method", choices=("horn", "gradient"), default="horn", help="Gradient method (horn|gradient)")
    parser.add_argument("--azimuth", type=float, default=315.0, help="Sun azimuth for hillshade (deg)")
    parser.add_argument("--altitude", type=float, default=45.0, help="Sun altitude for hillshade (deg)")
    parser.add_argument("--no-clip", action="store_true", help="Skip clipping step (assume DEM already cropped)")
    args = parser.parse_args()

    # Ensure path_config directories exist where possible
    ensure_dirs_from_pc()

    # helper to fetch attributes from pc
    def get_pc_attr(name: str):
        return getattr(pc, name) if pc and hasattr(pc, name) else None

    dem_arg = args.dem or get_pc_attr("RAW_DEM")
    shp_arg = args.shp or get_pc_attr("RAW_DISTRICT_SHP")
    outdir_arg = args.outdir or get_pc_attr("RASTERS_DIR")
    slope_out_arg = args.slope_out or get_pc_attr("SLOPE")
    hill_out_arg = args.hill_out or get_pc_attr("HILLSHADE")
    dem_clipped_target = get_pc_attr("DEM")  # optional explicit clipped target file

    if dem_arg is None:
        sys.exit("ERROR: DEM not provided. Pass --dem or set path_config.RAW_DEM.")
    if shp_arg is None and not args.no_clip:
        sys.exit("ERROR: Shapefile not provided. Pass --shp or set path_config.RAW_DISTRICT_SHP.")
    if outdir_arg is None:
        sys.exit("ERROR: Outdir not provided. Pass --outdir or set path_config.RASTERS_DIR.")
    if slope_out_arg is None:
        sys.exit("ERROR: Slope output not provided. Pass --slope-out or set path_config.SLOPE.")
    if hill_out_arg is None:
        sys.exit("ERROR: Hill output not provided. Pass --hill-out or set path_config.HILLSHADE.")

    dem_path = str(Path(dem_arg).expanduser().resolve())
    shp_path = str(Path(shp_arg).expanduser().resolve()) if shp_arg else None
    outdir = Path(outdir_arg).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    slope_out = str(Path(slope_out_arg).expanduser().resolve())
    hill_out = str(Path(hill_out_arg).expanduser().resolve())

    if dem_clipped_target:
        dem_clipped = str(Path(dem_clipped_target).expanduser().resolve())
    else:
        dem_stem = Path(dem_path).stem
        dem_clipped = str(outdir / f"{dem_stem}_clipped.tif")

    # Validate critical files
    if not Path(dem_path).exists():
        sys.exit(f"ERROR: DEM file not found: {dem_path}")
    if (not args.no_clip) and (not Path(shp_path).exists()):
        sys.exit(f"ERROR: Shapefile not found: {shp_path}. Ensure .shp/.shx/.dbf present together.")

    # Clip (unless skipped)
    dem_input = dem_path
    if not args.no_clip:
        dem_input = clip_dem_if_needed(dem_path, shp_path, dem_clipped)
    else:
        # ensure dem_clipped exists (copy if not)
        if dem_input != dem_clipped:
            if not Path(dem_clipped).exists():
                print(f"[cli] copying DEM (no clip) to {dem_clipped}")
                with rasterio.open(dem_input) as src:
                    profile = src.profile.copy()
                    data = src.read(1)
                    profile.update(driver="GTiff")
                    with rasterio.open(dem_clipped, "w", **profile) as dst:
                        dst.write(data, 1)
            dem_input = dem_clipped

    compute_slope_and_hillshade(dem_input, slope_out, hill_out,
                                method=args.method, azimuth=args.azimuth, altitude=args.altitude)

if __name__ == "__main__":
    main()
