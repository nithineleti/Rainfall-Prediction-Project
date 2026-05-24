#!/usr/bin/env python3
"""
Recompute composite watershed scores after:
 - filtering out tiny basins (area_km2 < AREA_THRESH)
 - filling NaN mean_dd_zone with median
 - winsorizing and log-transforming stream density
 - recomputing composite normalized scores

Outputs:
 - data/rasters/watershed_summary_filtered.csv
 - data/figures/watershed_correlation_heatmap_filtered.png
 - data/figures/top_basins_rankings_filtered.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RASTERS = PROJECT_ROOT / "data" / "rasters"
DATA_FIGURES = PROJECT_ROOT / "data" / "figures"

IN_CSV = DATA_RASTERS / "watershed_summary.csv"
OUT_CSV = DATA_RASTERS / "watershed_summary_filtered.csv"
OUT_HEAT = DATA_FIGURES / "watershed_correlation_heatmap_filtered.png"
OUT_TOP = DATA_FIGURES / "top_basins_rankings_filtered.png"

DATA_FIGURES.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------
# Parameters (tune as needed)
# -------------------------------------------------------------------
AREA_THRESH = 0.0005   # km² — remove basins smaller than this
WINSOR_PCT = 0.99      # cap at 99th percentile
SEED = 42
np.random.seed(SEED)

# -------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------
df = pd.read_csv(IN_CSV)
print(f"Loaded {len(df)} basins from {IN_CSV}")

# Filter by area
df_filtered = df[df['area_km2'] >= AREA_THRESH].copy()
print(f"After filter area >= {AREA_THRESH:.4f} km²: {len(df_filtered)} basins remain (removed {len(df) - len(df_filtered)})")

# Fill NaN mean_dd_zone
if 'mean_dd_zone' in df_filtered.columns:
    med = df_filtered['mean_dd_zone'].median(skipna=True)
    df_filtered['mean_dd_zone'] = df_filtered['mean_dd_zone'].fillna(med)
    print(f"Filled NaN mean_dd_zone with median: {med:.3f}")

# -------------------------------------------------------------------
# Compute transformed stream density
# -------------------------------------------------------------------
df_filtered['stream_density_km_per_km2'] = df_filtered['stream_length_km'] / df_filtered['area_km2']
cap = df_filtered['stream_density_km_per_km2'].quantile(WINSOR_PCT)
df_filtered['stream_density_capped'] = df_filtered['stream_density_km_per_km2'].clip(upper=cap)
df_filtered['stream_density_log1p'] = np.log1p(df_filtered['stream_density_capped'])
print(f"Winsorized stream_density at {WINSOR_PCT*100:.1f}% -> cap = {cap:.2f}")

# -------------------------------------------------------------------
# Composite scoring
# -------------------------------------------------------------------
metrics = [m for m in ['stream_density_log1p', 'mean_dd_zone', 'mean_slope'] if m in df_filtered.columns]
print("Using metrics for composite:", metrics)

zs = []
for m in metrics:
    vals = df_filtered[m].astype(float)
    mu, sd = np.nanmean(vals), np.nanstd(vals)
    if sd == 0 or np.isnan(sd):
        z = np.zeros_like(vals)
    else:
        z = (vals - mu) / sd
    zs.append(z)

if zs:
    avg_z = np.nanmean(np.vstack(zs), axis=0)
    df_filtered['composite_zscore'] = avg_z
    mn, mx = np.nanmin(avg_z), np.nanmax(avg_z)
    df_filtered['composite_norm'] = (avg_z - mn) / (mx - mn) if mx > mn else 0.0
else:
    df_filtered['composite_zscore'] = np.nan
    df_filtered['composite_norm'] = np.nan

# -------------------------------------------------------------------
# Save updated summary
# -------------------------------------------------------------------
df_filtered.to_csv(OUT_CSV, index=False)
print(f"✅ Saved filtered summary: {OUT_CSV}")

# -------------------------------------------------------------------
# Correlation heatmap
# -------------------------------------------------------------------
corr = df_filtered[['area_km2', 'stream_length_km', 'stream_density_log1p', 'mean_dd_zone', 'mean_slope', 'composite_norm']].corr()
plt.figure(figsize=(7, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdYlBu_r', square=True)
plt.tight_layout()
plt.savefig(OUT_HEAT, dpi=300)
plt.close()
print(f"📊 Saved correlation heatmap: {OUT_HEAT}")

# -------------------------------------------------------------------
# Ranking plot
# -------------------------------------------------------------------
top = df_filtered.sort_values('composite_norm', ascending=False).head(15)
plt.figure(figsize=(8, 6))
plt.barh(top['id'].astype(str), top['composite_norm'], color='mediumslateblue')
plt.gca().invert_yaxis()
plt.xlabel('Composite Score (Normalized)')
plt.title('Top 15 Basins (Filtered & Transformed)')
plt.tight_layout()
plt.savefig(OUT_TOP, dpi=300)
plt.close()
print(f"🏆 Saved ranking plot: {OUT_TOP}")

print("\nDone.")
