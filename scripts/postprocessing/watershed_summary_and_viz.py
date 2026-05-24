#!/usr/bin/env python3
"""
scripts/postprocessing/watershed_summary_and_viz.py

Consolidate watershed attributes, compute derived metrics, and create summary visualizations.

Outputs:
 - data/rasters/watershed_summary.csv
 - data/rasters/watershed_correlation_heatmap.png
 - data/rasters/top_basins_rankings.png
"""
from pathlib import Path
import sys
import math
import numpy as np
import pandas as pd

try:
    import geopandas as gpd
except Exception:
    gpd = None

import matplotlib.pyplot as plt

BASE = Path("data/rasters")
WGPKG = BASE / "watersheds.gpkg"
WGPKG_LAYER = "watersheds"
CSV_ENH = BASE / "watersheds_stats_enhanced.csv"    # may exist
CSV_DD = BASE / "watersheds_stats_dd.csv"          # produced previously
CSV_OLD = BASE / "watersheds_stats.csv"            # original simple CSV
OUT_MASTER = BASE / "watershed_summary.csv"
OUT_HEAT = BASE / "watershed_correlation_heatmap.png"
OUT_TOP = BASE / "top_basins_rankings.png"

def read_existing():
    dfs = []
    # prefer geopackage attributes (ensures geometry-derived columns present)
    if WGPKG.exists() and gpd is not None:
        try:
            g = gpd.read_file(WGPKG, layer=WGPKG_LAYER)
            df_g = g.drop(columns='geometry').copy()
            dfs.append(("gpkg", df_g))
            print(f"Loaded {len(df_g)} records from {WGPKG}")
        except Exception as e:
            print("Warning: failed to read geopackage:", e)

    # add other CSVs if present; give them lower precedence (merge on 'id' or 'pour_flat')
    for p in (CSV_ENH, CSV_DD, CSV_OLD):
        if p.exists():
            try:
                df = pd.read_csv(p)
                dfs.append((p.name, df))
                print(f"Loaded {len(df)} rows from {p.name}")
            except Exception as e:
                print(f"Warning: failed reading {p}: {e}")

    if not dfs:
        sys.exit("No input data found. Please run previous steps to create watersheds outputs.")

    # merge all on 'id' if available, else on 'pour_flat', else attempt index-based merge
    # Start with gpkg if exists
    base_name, base_df = dfs[0]
    merged = base_df.copy()
    for name, df in dfs[1:]:
        # find join key
        if 'id' in merged.columns and 'id' in df.columns:
            merged = merged.merge(df.drop(columns=[c for c in df.columns if c in merged.columns and c!='id']),
                                  on='id', how='left', suffixes=('', '_'+name))
        elif 'pour_flat' in merged.columns and 'pour_flat' in df.columns:
            merged = merged.merge(df.drop(columns=[c for c in df.columns if c in merged.columns and c!='pour_flat']),
                                  on='pour_flat', how='left', suffixes=('', '_'+name))
        else:
            # fallback: concatenate columns by position (risky), align by index
            # ensure same length; if not, skip
            if len(df) == len(merged):
                # add columns with name prefix to avoid collisions
                cols = {c: f"{name}_{c}" for c in df.columns if c not in merged.columns}
                df_ren = df.rename(columns=cols)
                merged = pd.concat([merged.reset_index(drop=True), df_ren.reset_index(drop=True)], axis=1)
            else:
                print(f"Skipping {name}: cannot merge (no common key and length mismatch).")

    # ensure numeric types for key columns
    return merged

def compute_derived(df):
    d = df.copy()
    # canonicalize column names we may have
    # possible fields: area_km2, stream_length_km, mean_slope, mean_dd_zone, mean_flowacc, n_pixels
    # ensure they exist (create NaN if missing)
    for col in ['area_km2', 'stream_length_km', 'mean_slope', 'mean_dd_zone', 'mean_flowacc', 'n_pixels']:
        if col not in d.columns:
            d[col] = np.nan

    # derived: stream_density_km_per_km2
    # avoid division by zero
    d['stream_density_km_per_km2'] = d.apply(lambda r: (r['stream_length_km'] / r['area_km2']) if pd.notna(r['stream_length_km']) and pd.notna(r['area_km2']) and r['area_km2']>0 else np.nan, axis=1)

    # relief_density_ratio = mean_slope / stream_density (avoid zero/NaN)
    def safe_div(a,b):
        try:
            if pd.isna(a) or pd.isna(b) or b == 0:
                return np.nan
            return a / b
        except Exception:
            return np.nan

    d['relief_density_ratio'] = d.apply(lambda r: safe_div(r['mean_slope'], r['stream_density_km_per_km2']), axis=1)

    # percentiles & ranks for important metrics
    rank_cols = ['area_km2','stream_length_km','stream_density_km_per_km2','mean_dd_zone','mean_slope']
    for c in rank_cols:
        if c in d.columns:
            d[f'{c}_pct_rank'] = d[c].rank(pct=True)
        else:
            d[f'{c}_pct_rank'] = np.nan

    # composite score — simple weighted z-score (example)
    metrics = []
    for c in ['stream_density_km_per_km2','mean_dd_zone','mean_slope']:
        if c in d.columns:
            metrics.append(c)
    if metrics:
        zscores = []
        for c in metrics:
            vals = d[c].astype(float)
            m = np.nanmean(vals)
            s = np.nanstd(vals)
            if s == 0 or np.isnan(s):
                z = np.zeros_like(vals)
            else:
                z = (vals - m) / s
            zscores.append(z)
        # average zscore
        avg_z = np.nanmean(np.vstack(zscores), axis=0)
        d['composite_zscore'] = avg_z
        # normalized 0-1
        mn, mx = np.nanmin(avg_z), np.nanmax(avg_z)
        if not np.isnan(mn) and not np.isnan(mx) and mx>mn:
            d['composite_norm'] = (avg_z - mn) / (mx - mn)
        else:
            d['composite_norm'] = np.nan
    else:
        d['composite_zscore'] = np.nan
        d['composite_norm'] = np.nan

    return d

def make_heatmap(df, out_png):
    # correlation heatmap for numeric columns
    num = df.select_dtypes(include=[np.number]).copy()
    if num.shape[1] < 2:
        print("Not enough numeric columns to make heatmap.")
        return
    corr = num.corr()
    plt.figure(figsize=(8,8))
    try:
        import seaborn as sns
        sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdYlBu_r', square=True, cbar_kws={'shrink':0.6})
    except Exception:
        plt.imshow(corr, cmap='RdYlBu_r', vmin=-1, vmax=1)
        plt.colorbar()
        plt.title('Correlation matrix')
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()
    print("Saved correlation heatmap to", out_png)

def make_rank_plots(df, out_png, top_n=10):
    # two subplots: top by stream_density and top by mean_dd_zone
    df2 = df.copy()
    # ensure numeric
    for c in ['stream_density_km_per_km2','mean_dd_zone']:
        if c not in df2.columns:
            df2[c] = np.nan
    top1 = df2.sort_values('stream_density_km_per_km2', ascending=False).head(top_n)
    top2 = df2.sort_values('mean_dd_zone', ascending=False).head(top_n)

    fig, axes = plt.subplots(1,2, figsize=(14,6))
    axes[0].barh(top1['id'].astype(str), top1['stream_density_km_per_km2'], color='steelblue')
    axes[0].invert_yaxis()
    axes[0].set_title(f"Top {top_n} basins by stream density (km/km^2)")
    axes[0].set_xlabel('stream_density_km_per_km2')

    axes[1].barh(top2['id'].astype(str), top2['mean_dd_zone'], color='darkorange')
    axes[1].invert_yaxis()
    axes[1].set_title(f"Top {top_n} basins by mean drainage density")
    axes[1].set_xlabel('mean_dd_zone (km/km^2)')

    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()
    print("Saved ranking plots to", out_png)

def main():
    merged = read_existing()
    df = compute_derived(merged)
    # save master CSV
    df.to_csv(OUT_MASTER, index=False)
    print("Wrote master summary:", OUT_MASTER)
    # visualizations
    make_heatmap(df, OUT_HEAT)
    make_rank_plots(df, OUT_TOP, top_n=10)

    # print short ranked table
    print("\nTop 10 basins by composite_norm:")
    if 'composite_norm' in df.columns:
        print(df[['id','area_km2','stream_length_km','stream_density_km_per_km2','mean_dd_zone','composite_norm']].sort_values('composite_norm', ascending=False).head(10).to_string(index=False))
    print("\nDone.")

if __name__ == "__main__":
    main()
