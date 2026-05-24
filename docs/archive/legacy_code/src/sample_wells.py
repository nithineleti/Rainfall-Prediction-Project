#!/usr/bin/env python3
"""
src/sample_wells.py

Create training samples for Stage-4.
- If --wells CSV is provided, sample features at those coords.
- Otherwise generate synthetic random samples within stack bounds.
- Optionally create synthetic labels using existing grp_score (AHP) + noise.

Outputs:
 - data/tables/train_samples.csv
Columns: id, x, y, band_1, band_2, ..., band_N, label, label_type

Usage (synthetic):
    python src/sample_wells.py --stack data/rasters/features_stack.tif \
        --out data/tables/train_samples.csv --n 2000 --mode synthetic

Usage (sample existing wells CSV):
    python src/sample_wells.py --stack ... --wells data/raw/wells.csv --out ...
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import numpy as np
# Import rasterio before pandas to avoid GDAL/Pandas DLL conflicts on Windows
import rasterio
from rasterio.sample import sample_gen
import pandas as pd
from path_config import TABLES_DIR, FEATURES_STACK

OUT_DIR_DEFAULT = str(TABLES_DIR)
DEFAULT_STACK = str(FEATURES_STACK)
os.makedirs(OUT_DIR_DEFAULT, exist_ok=True)


def sample_stack_at_coords(stack_path, coords):
    """Return NxB numpy array of sampled values for coords (list of (x,y))."""
    with rasterio.open(stack_path) as src:
        vals = list(sample_gen(src, coords))
        arr = np.vstack([v for v in vals])
        return arr


def random_points_within_valid(stack_path, n, seed=42, max_tries=200000):
    """
    Generate n random points within raster bounds where stack has valid values.

    Strategy:
    - Try to detect a 'grp_score' band from companion CSV (features_stack_bands.csv).
      If present, use its finite mask as the valid area.
    - Otherwise, accept pixels where ANY band is finite.
    - If valid pixels count < n, sample with replacement (warn).
    """
    rng = np.random.RandomState(seed)
    with rasterio.open(stack_path) as src:
        transform = src.transform
        rows = src.height
        cols = src.width

        # read whole stack into memory (bands, rows, cols)
        data = src.read().astype(float)

    # try to find grp_score band via companion CSV or fallback names
    grp_band_idx = None
    csvpath = os.path.join(os.path.dirname(stack_path), "features_stack_bands.csv")
    if os.path.exists(csvpath):
        try:
            df = pd.read_csv(csvpath)
            # Accept either column named 'band_name' or first column listing names
            if 'band_name' in df.columns:
                names = df['band_name'].astype(str).tolist()
            else:
                names = df.iloc[:, 0].astype(str).tolist()
            for i, nme in enumerate(names):
                nlow = nme.lower()
                if 'grp' in nlow and 'score' in nlow:
                    grp_band_idx = i
                    break
        except Exception:
            grp_band_idx = None

    # If no CSV, attempt to detect by scanning for a band with values in 0..1 or typical grp_score range
    if grp_band_idx is None:
        # simple heuristic: look for band with values mostly between 0 and 1 and non-zero finite fraction
        for i in range(data.shape[0]):
            arr = data[i]
            finite = np.isfinite(arr)
            cnt = np.count_nonzero(finite)
            if cnt == 0:
                continue
            mn = np.nanmin(np.where(finite, arr, np.nan))
            mx = np.nanmax(np.where(finite, arr, np.nan))
            # grp_score in your pipeline was roughly 0..1 - use heuristic
            if 0.0 <= mn <= 1.0 and 0.0 <= mx <= 1.5:
                grp_band_idx = i
                break

    if grp_band_idx is not None:
        grp_arr = data[grp_band_idx]
        valid_mask = np.isfinite(grp_arr)
        # inform
        print(f"-> Using detected grp_score band index {grp_band_idx+1} as valid-mask (finite pixels).")
    else:
        # fallback: any finite band
        valid_mask = np.any(np.isfinite(data), axis=0)
        print("-> No grp_score band detected. Using ANY finite-band pixels as valid-mask.")

    valid_idx = np.argwhere(valid_mask)
    total_valid = valid_idx.shape[0]
    if total_valid == 0:
        raise RuntimeError("No valid pixels found in stack (even with fallback). Check features_stack or band generation.")
    if total_valid < n:
        print(f"Warning: only {total_valid} valid pixels available but requested n={n}. Sampling with replacement.")
        chosen_idx = rng.choice(total_valid, size=n, replace=True)
    else:
        chosen_idx = rng.choice(total_valid, size=n, replace=False)

    chosen = valid_idx[chosen_idx]
    points = []
    for r, c in chosen:
        x, y = transform * (c + 0.5, r + 0.5)
        points.append((x, y))
    return points


def load_band_names(stack_path):
    """Load band names from features_bands.csv in TABLES_DIR."""
    band_names = None
    # First try TABLES_DIR (new location)
    from path_config import TABLES_DIR
    csvpath = os.path.join(str(TABLES_DIR), "features_bands.csv")
    if not os.path.exists(csvpath):
        # Fallback: try same directory as stack (old location)
        csvpath = os.path.join(os.path.dirname(stack_path), "features_stack_bands.csv")
    
    if os.path.exists(csvpath):
        try:
            df = pd.read_csv(csvpath)
            if 'band_name' in df.columns:
                band_names = df['band_name'].astype(str).tolist()
            else:
                # assume first column has names
                band_names = df.iloc[:, 0].astype(str).tolist()
        except Exception:
            band_names = None
    return band_names


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stack", default=DEFAULT_STACK, help="Path to features_stack.tif")
    p.add_argument("--wells", default=None, help="Optional CSV with lon,lat (columns x,y or lon,lat)")
    p.add_argument("--out", default=os.path.join(OUT_DIR_DEFAULT, "train_samples.csv"))
    p.add_argument("--n", type=int, default=2000, help="Number of synthetic points if no wells provided")
    p.add_argument("--mode", choices=["synthetic", "use_wells"], default="synthetic")
    p.add_argument("--label-source", choices=["grp_score", "quantile", "manual"], default="grp_score",
                   help="How to make synthetic labels (if mode synthetic). grp_score uses AHP grp_score band.")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    stack_path = args.stack
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    band_names = load_band_names(stack_path)
    if band_names is None:
        with rasterio.open(stack_path) as src:
            band_names = [f"band_{i}" for i in range(1, src.count + 1)]

    # try to find grp_score band index (0-based)
    grp_score_band_index = None
    for i, name in enumerate(band_names):
        nlow = name.lower()
        if 'grp' in nlow and 'score' in nlow:
            grp_score_band_index = i
            break

    if args.mode == "use_wells" and args.wells:
        df_w = pd.read_csv(args.wells)
        # try to find lon/lat columns
        if "lon" in df_w.columns and "lat" in df_w.columns:
            coords = list(zip(df_w['lon'].values, df_w['lat'].values))
        elif "x" in df_w.columns and "y" in df_w.columns:
            coords = list(zip(df_w['x'].values, df_w['y'].values))
        else:
            raise ValueError("Wells CSV must contain 'lon,lat' or 'x,y' columns.")
        samples = sample_stack_at_coords(stack_path, coords)
        out_df = pd.DataFrame(samples, columns=band_names)
        out_df['x'] = [c[0] for c in coords]
        out_df['y'] = [c[1] for c in coords]
        if 'label' in df_w.columns:
            out_df['label'] = df_w['label'].values
            out_df['label_type'] = 'observed'
        else:
            out_df['label'] = np.nan
            out_df['label_type'] = 'unknown'
        out_df.index.name = 'id'
        out_df.reset_index(inplace=True)

    else:
        pts = random_points_within_valid(stack_path, args.n, seed=args.seed)
        samples = sample_stack_at_coords(stack_path, pts)
        out_df = pd.DataFrame(samples, columns=band_names)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        out_df['x'] = xs; out_df['y'] = ys

        # create synthetic labels
        if args.label_source == "grp_score" and grp_score_band_index is not None:
            gs = out_df[band_names[grp_score_band_index]].values
            thr_low = np.nanpercentile(gs, 33)
            thr_high = np.nanpercentile(gs, 66)
            labels = np.full_like(gs, 1, dtype=int)
            labels[np.isnan(gs)] = 1  # if any nan, put as moderate
            labels[gs <= thr_low] = 0
            labels[gs >= thr_high] = 2
            rng = np.random.RandomState(args.seed)
            flip = rng.rand(len(labels)) < 0.05
            labels[flip] = rng.randint(0, 3, flip.sum())
            out_df['label'] = labels
            out_df['label_type'] = 'synthetic_grp_score'

        elif args.label_source == "quantile":
            vals = out_df[band_names[0]].values
            thr1 = np.nanpercentile(vals, 33); thr2 = np.nanpercentile(vals, 66)
            labels = np.where(vals <= thr1, 0, np.where(vals >= thr2, 2, 1))
            out_df['label'] = labels
            out_df['label_type'] = 'synthetic_quantile'
        else:
            out_df['label'] = np.nan
            out_df['label_type'] = 'unknown'

        out_df.index.name = 'id'
        out_df.reset_index(inplace=True)

    out_df.to_csv(args.out, index=False)
    print(f"Wrote samples -> {args.out}. n={len(out_df)}. Label type: {out_df['label_type'].unique()}")


if __name__ == "__main__":
    main()
