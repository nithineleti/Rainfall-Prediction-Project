#!/usr/bin/env python3
"""
scripts/preprocessing/02_fix_slope.py

Robust slope recalculation for watershed modelling.

- Adds project root to sys.path so import path_config works.
- Handles NoData values correctly using global median fallback.
- Windowed Horn kernel slope calculation, NoData-safe, optional sink-fill.
- Automatically deletes temporary filled DEMs created by --sink-fill.
"""
from __future__ import annotations

from pathlib import Path
import sys
import platform
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import warnings
from typing import Tuple, Optional, Dict
import numpy as np
import rasterio
from rasterio.windows import Window
from scipy import ndimage

# Try import path_config if available
try:
    import path_config as pc  # type: ignore
except Exception:
    pc = None

# Horn kernels (3x3) base (unnormalized for meter scaling later)
_K_HORN_DX = np.array([[-1, 0, 1],
                       [-2, 0, 2],
                       [-1, 0, 1]], dtype=float) / 8.0
_K_HORN_DY = np.array([[-1, -2, -1],
                       [0, 0, 0],
                       [1, 2, 1]], dtype=float) / 8.0


def geographic_spacing_in_meters(lat_center_deg: float) -> Tuple[float, float]:
    meters_per_degree_lat = (
        111132.954
        - 559.822 * np.cos(2 * np.radians(lat_center_deg))
        + 1.175 * np.cos(4 * np.radians(lat_center_deg))
    )
    meters_per_degree_lon = (np.pi / 180) * 6378137.0 * np.cos(np.radians(lat_center_deg))
    return meters_per_degree_lon, meters_per_degree_lat


def fill_for_convolution(arr: np.ndarray, fallback: float) -> np.ndarray:
    """
    Fill NaNs with local mean (3x3) and fallback to provided 'fallback' value
    if a local mean cannot be computed (e.g., all-NaN windows).
    """
    if not np.isfinite(arr).any():
        return np.full_like(arr, fallback, dtype=arr.dtype)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        arr_f = ndimage.generic_filter(arr, np.nanmean, size=3, mode="nearest")

    if np.isnan(arr_f).any():
        arr_f = np.where(np.isfinite(arr_f), arr_f, fallback)

    return arr_f


def slope_windowed(
    dem_path: str,
    slope_out: str,
    slope_pct_out: str,
    aspect_out: Optional[str] = None,
    method: str = "horn",
    sink_fill: bool = False,
    block_size: int = 1024,
) -> Dict[str, int]:
    """
    Compute slope (deg) & slope % windowed; write outputs.
    Returns diagnostics dict: {'total_windows': int, 'all_nan_windows': int}
    """
    dem_to_use = dem_path
    temp_filled_path = None

    # Optional sink-fill using richdem
    if sink_fill:
        try:
            import richdem as rd  # type: ignore
        except Exception:
            print("⚠️  richdem not installed — skipping sink-fill.")
            sink_fill = False
        else:
            print("🕳️ Performing sink-fill with richdem (may take time)...")
            with rasterio.open(dem_path) as src:
                arr = src.read(1).astype("float32")
                nodata = src.nodata
                mask = (arr != nodata) if nodata is not None else np.isfinite(arr)
                arr = np.where(mask, arr, np.nan)
                prof = src.profile.copy()
                prof.update(dtype=rasterio.float32, nodata=np.nan)

            rd_arr = rd.rdarray(arr, no_data=np.nan)
            filled = rd.FillDepressions(rd_arr, in_place=False)
            temp_filled_path = Path(dem_path).with_suffix(".filled.tif")
            with rasterio.open(temp_filled_path, "w", **prof) as dst:
                dst.write(np.where(np.isfinite(filled), filled, np.nan).astype("float32"), 1)
            dem_to_use = str(temp_filled_path)
            print(f"✅ Sink-fill output: {dem_to_use}")

    # Read metadata and compute pixel sizes; compute a global median fallback
    with rasterio.open(dem_to_use) as src:
        profile = src.profile.copy()
        nodata = src.nodata
        crs = src.crs
        transform = src.transform
        width, height = src.width, src.height

        xres = float(transform.a)
        yres = abs(float(transform.e))
        if crs and crs.is_geographic:
            lat_center = float(transform.f + (height / 2.0) * transform.e)
            m_per_lon, m_per_lat = geographic_spacing_in_meters(lat_center)
            cell_x_m = abs(xres) * m_per_lon
            cell_y_m = abs(yres) * m_per_lat
            print(f"🌍 CRS geographic. Converting degrees→meters at lat {lat_center:.6f}")
        else:
            cell_x_m = abs(xres)
            cell_y_m = abs(yres)
        print(f"📏 Pixel size (m): {cell_x_m:.3f} × {cell_y_m:.3f}")

        # Compute global median fallback
        full_arr = src.read(1, masked=True)
        finite_vals = full_arr.compressed() if hasattr(full_arr, "compressed") else full_arr[np.isfinite(full_arr)]
        global_median = float(np.nanmedian(finite_vals)) if len(finite_vals) > 0 else 0.0
        print(f"[info] Global fallback median for NaN-windows: {global_median:.3f}")

    out_profile = profile.copy()
    out_profile.update(dtype=rasterio.float32, count=1, compress="lzw", nodata=np.nan)

    all_nan_window_count = 0
    total_windows = 0

    with rasterio.open(dem_to_use) as src, \
        rasterio.open(slope_out, "w", **out_profile) as slope_dst, \
        rasterio.open(slope_pct_out, "w", **out_profile) as slope_pct_dst, \
        (rasterio.open(aspect_out, "w", **out_profile) if aspect_out else DummyCtx()) as aspect_dst:

        bs = max(128, min(block_size, max(src.width, src.height)))
        overlap = 1  # kernel radius for 3x3

        for y0 in range(0, src.height, bs):
            h = min(bs, src.height - y0)
            for x0 in range(0, src.width, bs):
                total_windows += 1
                w = min(bs, src.width - x0)
                win = Window(
                    max(0, x0 - overlap),
                    max(0, y0 - overlap),
                    w + (overlap if x0 > 0 else 0) + (overlap if (x0 + w) < src.width else 0),
                    h + (overlap if y0 > 0 else 0) + (overlap if (y0 + h) < src.height else 0),
                )
                arr = src.read(1, window=win).astype("float32")

                if nodata is not None:
                    mask = (arr != nodata) & np.isfinite(arr)
                else:
                    mask = np.isfinite(arr)
                arr_nan = np.where(mask, arr, np.nan)

                if not np.isfinite(arr_nan).any():
                    all_nan_window_count += 1
                    arr_filled = np.full_like(arr_nan, global_median, dtype=arr_nan.dtype)
                else:
                    arr_filled = fill_for_convolution(arr_nan, global_median)

                if method == "horn":
                    dx = ndimage.convolve(arr_filled, _K_HORN_DX / cell_x_m, mode="nearest")
                    dy = ndimage.convolve(arr_filled, _K_HORN_DY / cell_y_m, mode="nearest")
                else:
                    dy, dx = np.gradient(arr_filled, cell_y_m, cell_x_m, edge_order=2)

                slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
                slope_deg = np.degrees(slope_rad)
                slope_pct = np.tan(slope_rad) * 100.0

                aspect = np.arctan2(dy, -dx)
                aspect = np.where(aspect < 0, 2 * np.pi + aspect, aspect)
                aspect_deg = np.degrees(aspect)

                # Apply mask
                slope_deg[~np.isfinite(arr_nan)] = np.nan
                slope_pct[~np.isfinite(arr_nan)] = np.nan
                aspect_deg[~np.isfinite(arr_nan)] = np.nan

                # Crop overlaps
                sx = 0 if x0 == 0 else overlap
                sy = 0 if y0 == 0 else overlap
                ex, ey = sx + w, sy + h
                write_win = Window(x0, y0, w, h)

                slope_dst.write(slope_deg[sy:ey, sx:ex].astype("float32"), 1, window=write_win)
                slope_pct_dst.write(slope_pct[sy:ey, sx:ex].astype("float32"), 1, window=write_win)
                if aspect_out:
                    aspect_dst.write(aspect_deg[sy:ey, sx:ex].astype("float32"), 1, window=write_win)

    # Auto-delete temporary filled DEM
    if temp_filled_path and temp_filled_path.exists():
        temp_filled_path.unlink()
        print(f"🧹 Deleted temporary file: {temp_filled_path}")

    print("✅ Done writing slope, slope percent, and aspect (if requested).")
    print(f"[info] Total windows processed: {total_windows}, all-NaN windows: {all_nan_window_count}")
    return {"total_windows": total_windows, "all_nan_windows": all_nan_window_count}


class DummyCtx:
    def __enter__(self): return None
    def __exit__(self, exc_type, exc, tb): return False


def summary_stats(path: str) -> dict:
    with rasterio.open(path) as src:
        arr = src.read(1, masked=True)
        valid = arr.compressed() if hasattr(arr, "compressed") else arr[np.isfinite(arr)]
        if len(valid) == 0:
            return {}
        return {
            "min": float(np.nanmin(valid)),
            "max": float(np.nanmax(valid)),
            "mean": float(np.nanmean(valid)),
            "median": float(np.nanmedian(valid)),
            "count_valid": int(np.isfinite(valid).sum()),
        }


def cli():
    print("🐍 Python executable:", sys.executable)
    print("🔢 Python version:", platform.python_version())
    print("📂 Project root:", PROJECT_ROOT)

    p = argparse.ArgumentParser(description="Recompute slope robustly")
    p.add_argument("--dem", help="Input DEM (override path_config.RAW_DEM)")
    p.add_argument("--slope-out", help="Slope degrees output (override path_config.SLOPE)")
    p.add_argument("--slope-pct-out", help="Slope percent output")
    p.add_argument("--aspect-out", help="Aspect output (optional)")
    p.add_argument("--method", choices=("horn", "gradient"), default="horn")
    p.add_argument("--sink-fill", action="store_true", help="Use richdem to fill sinks before slope")
    p.add_argument("--block", type=int, default=1024, help="Block size for windowed processing")
    args = p.parse_args()

    def get_pc(name):
        return getattr(pc, name) if pc and hasattr(pc, name) else None

    dem = args.dem or get_pc("RAW_DEM")
    slope_out = args.slope_out or get_pc("SLOPE")
    slope_pct_out = args.slope_pct_out or (
        str(Path(slope_out).with_name(Path(slope_out).stem + "_pct.tif")) if slope_out else None
    )
    aspect_out = args.aspect_out or (get_pc("ASPECT") if pc and hasattr(pc, "ASPECT") else None)

    if dem is None or slope_out is None or slope_pct_out is None:
        sys.exit("❌ ERROR: Provide --dem and --slope-out or set path_config.RAW_DEM/SLOPE")

    dem = str(Path(dem).resolve())
    slope_out = str(Path(slope_out).resolve())
    slope_pct_out = str(Path(slope_pct_out).resolve())
    aspect_out = str(Path(aspect_out).resolve()) if aspect_out else None

    print(f"\nDEM: {dem}")
    print(f"Slope (deg): {slope_out}")
    print(f"Slope (pct): {slope_pct_out}")
    if aspect_out:
        print(f"Aspect: {aspect_out}")

    diagnostics = slope_windowed(
        dem, slope_out, slope_pct_out, aspect_out, method=args.method, sink_fill=args.sink_fill, block_size=args.block
    )

    print("\n📊 Summary:")
    outputs = [pth for pth in (slope_out, slope_pct_out, aspect_out) if pth]
    for pth in outputs:
        stats = summary_stats(pth)
        if not stats:
            print(f"  {pth}: no valid data")
        else:
            print(f"  {pth}: min={stats['min']:.3f}, max={stats['max']:.3f}, mean={stats['mean']:.3f}, "
                  f"median={stats['median']:.3f}, valid={stats['count_valid']}")

    print(f"\n✅ Diagnostics: total_windows={diagnostics['total_windows']}, all_nan_windows={diagnostics['all_nan_windows']}")


if __name__ == "__main__":
    cli()
