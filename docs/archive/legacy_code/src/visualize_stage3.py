"""
src/visualize_stage3.py

Visualize and summarize Stage-3 stacked raster layers.

Outputs:
 - data/figures/<layer>.png
 - data/tables/features_summary.csv
 - data/tables/features_corr.csv  (continuous bands only)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
# Import rasterio before pandas/matplotlib to avoid DLL conflicts on Windows
import rasterio
import pandas as pd
import matplotlib.pyplot as plt
from path_config import FEATURES_STACK, TABLES_DIR, FIGURES_DIR

# Paths
STACK_PATH = str(FEATURES_STACK)
BANDS_CSV = os.path.join(str(TABLES_DIR), "features_bands.csv")
OUT_DIR = str(FIGURES_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

SUMMARY_CSV = os.path.join(str(TABLES_DIR), "features_summary.csv")
CORR_CSV = os.path.join(str(TABLES_DIR), "features_corr.csv")

def main():
    if not os.path.exists(STACK_PATH):
        raise FileNotFoundError(f"Feature stack not found: {STACK_PATH}")
    if not os.path.exists(BANDS_CSV):
        raise FileNotFoundError(f"Band list not found: {BANDS_CSV}")

    bands_df = pd.read_csv(BANDS_CSV)
    band_names = bands_df["band_name"].tolist()

    with rasterio.open(STACK_PATH) as src:
        arrs = []
        stats = []

        for i, name in enumerate(band_names, start=1):
            band = src.read(i, masked=True).astype(float)
            arr = np.where(np.isfinite(band), band, np.nan)

            # Compute summary stats
            valid = arr[np.isfinite(arr)]
            summary = {
                "band": i,
                "name": name,
                "min": np.nanmin(valid) if valid.size else np.nan,
                "max": np.nanmax(valid) if valid.size else np.nan,
                "mean": np.nanmean(valid) if valid.size else np.nan,
                "std": np.nanstd(valid) if valid.size else np.nan,
                "nan_fraction": np.isnan(arr).sum() / arr.size
            }
            stats.append(summary)
            arrs.append(arr)

            # Plot
            plt.figure(figsize=(6, 5))
            im = plt.imshow(arr, cmap="viridis", interpolation="nearest")
            plt.colorbar(im, label=name)
            plt.title(f"{name} (band {i})")
            plt.axis("off")
            plt.tight_layout()
            out_path = os.path.join(OUT_DIR, f"{name}.png")
            plt.savefig(out_path, dpi=150)
            plt.close()
            print(f"Saved {out_path}")

    # Save summary
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv(SUMMARY_CSV, index=False)
    print(f"\nSaved summary stats: {SUMMARY_CSV}")

    # Compute correlation among continuous layers only
    cont_names = [n for n in band_names if n not in ["lulc", "geology", "stream"]]
    cont_idx = [band_names.index(n) for n in cont_names]
    stacked = np.stack([arrs[i] for i in cont_idx], axis=0)
    flat = stacked.reshape(len(cont_names), -1)
    mask = np.isfinite(flat).all(axis=0)
    corr = np.corrcoef(flat[:, mask])

    corr_df = pd.DataFrame(corr, columns=cont_names, index=cont_names)
    corr_df.to_csv(CORR_CSV)
    print(f"Saved correlation matrix: {CORR_CSV}")

if __name__ == "__main__":
    main()
