#!/usr/bin/env python3
"""
scripts/visualize_and_enhance_watersheds.py

1) Compute accurate stream length per watershed and update watersheds GeoPackage + CSV.
2) Produce a PNG map (hillshade / watersheds colored by area_km2 / streams overlay).

Run from project root (VS Code terminal):
    python scripts/visualize_and_enhance_watersheds.py

Assumptions:
 - watersheds.gpkg layer 'watersheds' exists (created earlier)
 - stream_polygons.shp or stream_skeleton_pts.shp exists in data/rasters/
 - hillshade_lucknow.tif exists in data/rasters/ (used as basemap)
 - CRS is projected (EPSG:32644) for correct distance units; if geographic, script will reproject to EPSG:32644
"""
from pathlib import Path
import sys
import math
import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import mapping
from shapely.ops import unary_union

BASE = Path("data/rasters")
WATERSHEDS_GPKG = BASE / "watersheds.gpkg"
WATERSHEDS_LAYER = "watersheds"
STREAM_POLY = BASE / "stream_polygons.shp"
STREAM_SKELETON = BASE / "stream_skeleton_pts.shp"
HILLSHADE = BASE / "hillshade_lucknow.tif"
OUT_CSV = BASE / "watersheds_stats_enhanced.csv"
OUT_PNG = BASE / "watersheds_map_vscode.png"

TARGET_CRS = "EPSG:32644"  # UTM / Projected CRS for length calculations — change if your project uses another

def load_watersheds():
    if not WATERSHEDS_GPKG.exists():
        raise FileNotFoundError(f"{WATERSHEDS_GPKG} not found. Run watershed delineation first.")
    g = gpd.read_file(WATERSHEDS_GPKG, layer=WATERSHEDS_LAYER)
    return g

def load_streams():
    # prefer polygonized streams if available, else use skeleton points to create short segments (fallback)
    if STREAM_POLY.exists():
        s = gpd.read_file(STREAM_POLY)
        return s
    if STREAM_SKELETON.exists():
        s = gpd.read_file(STREAM_SKELETON)
        # convert points to small buffered lines/polygons (approx) to enable intersection lengths;
        # here we simply buffer points by half-pixel and take boundaries to get line-ish features.
        print("Converting skeleton points to short line segments via buffering (approx).")
        px = 0.0125  # km length approx used earlier; but in projected meters we use 12.5 m
        # We'll buffer by 6 m (0.006 km) in projected CRS later; return points for now and handle after reprojection
        return s
    raise FileNotFoundError("No stream vector found (stream_polygons.shp or stream_skeleton_pts.shp)")

def ensure_projected(gdf, target_crs=TARGET_CRS):
    if gdf.crs is None:
        raise RuntimeError("Input GeoDataFrame has no CRS.")
    if gdf.crs.to_string() != target_crs:
        print(f"Reprojecting from {gdf.crs} -> {target_crs}")
        return gdf.to_crs(target_crs)
    return gdf

def compute_stream_length_per_watershed(watersheds_gdf, streams_gdf):
    # Ensure both in projected CRS for meter-length units
    watersheds = ensure_projected(watersheds_gdf, TARGET_CRS)
    streams = ensure_projected(streams_gdf, TARGET_CRS)

    # If streams are polygons, convert to line (boundary); if points, buffer small then boundary
    geom_types = set(streams.geom_type.unique())
    if geom_types & {"Polygon", "MultiPolygon"}:
        print("Converting stream polygons -> line boundaries for length computation.")
        streams_lines = streams.copy()
        streams_lines['geometry'] = streams_lines.geometry.boundary
    elif geom_types & {"Point", "MultiPoint"}:
        print("Stream source is points: buffering points slightly and taking boundary to create short segments.")
        # buffer by e.g., 6 m to approximate pixel length (DEM pixel ~12.5 m)
        streams_lines = streams.copy()
        streams_lines['geometry'] = streams_lines.geometry.buffer(6).boundary
    else:
        # Lines already
        streams_lines = streams.copy()

    # Clip by each watershed and compute length
    watersheds['stream_length_km'] = 0.0
    for idx, basin in watersheds.iterrows():
        poly = basin.geometry
        if poly is None or poly.is_empty:
            continue
        # quick spatial index select
        candidate = streams_lines[streams_lines.intersects(poly)]
        if candidate.empty:
            watersheds.at[idx, 'stream_length_km'] = 0.0
            continue
        # clip and sum lengths
        clipped = candidate.copy()
        clipped['geometry'] = clipped.geometry.intersection(poly)
        # remove empties
        clipped = clipped[~clipped.is_empty & clipped.geometry.notnull()]
        if clipped.empty:
            watersheds.at[idx, 'stream_length_km'] = 0.0
            continue
        # length in meters (projected CRS), sum and convert to km
        total_m = clipped.length.sum()
        watersheds.at[idx, 'stream_length_km'] = float(total_m / 1000.0)
    return watersheds

def save_results(watersheds_gdf):
    # update gpkg (overwrite layer) and write CSV
    print("Saving updated GeoPackage and CSV ...")
    # write to new layer name 'watersheds' replacing existing
    watersheds_gdf.to_file(WATERSHEDS_GPKG, layer=WATERSHEDS_LAYER, driver="GPKG")
    # drop geometry for CSV
    df = watersheds_gdf.drop(columns='geometry').copy()
    df.to_csv(OUT_CSV, index=False)
    print("Wrote:", WATERSHEDS_GPKG, "and", OUT_CSV)

def plot_map(watersheds_gdf, streams_gdf, hillshade_tif, out_png):
    # Reproject everything to the same CRS for plotting
    watersheds = ensure_projected(watersheds_gdf, TARGET_CRS)
    streams = ensure_projected(streams_gdf, TARGET_CRS)

    # Read hillshade raster (if exists) and reproject isn't necessary if already in TARGET_CRS
    if not hillshade_tif.exists():
        print("Hillshade not found; plotting without base raster.")
        raster = None
    else:
        raster = rasterio.open(hillshade_tif)
        # If raster CRS differs, warn (we assume it matches TARGET_CRS else image will be misaligned)
        if raster.crs is None:
            print("Warning: hillshade raster has no CRS.")
        elif raster.crs.to_string() != TARGET_CRS:
            print(f"Hillshade CRS {raster.crs} != {TARGET_CRS}. Attempting to proceed (may misalign).")

        # read full raster (beware memory, but your raster is manageable)
        arr = raster.read(1)
        arr = np.where(arr==raster.nodata, np.nan, arr)
        # compute extent
        left, bottom, right, top = raster.bounds.left, raster.bounds.bottom, raster.bounds.right, raster.bounds.top
        extent = (left, right, bottom, top)

    # Prepare plot
    fig, ax = plt.subplots(figsize=(12, 12), dpi=150)
    if raster is not None:
        # hillshade: show as gray
        im = ax.imshow(arr, cmap='gray', extent=extent, origin='upper')
    else:
        ax.set_facecolor('lightgray')

    # watershed choropleth by area_km2
    vmin = watersheds['area_km2'].min() if 'area_km2' in watersheds.columns else watersheds['n_pixels'].min()
    vmax = watersheds['area_km2'].max() if 'area_km2' in watersheds.columns else watersheds['n_pixels'].max()
    watersheds.plot(column='area_km2', ax=ax, cmap='OrRd', alpha=0.45, edgecolor='k', linewidth=0.4, vmin=vmin, vmax=vmax)

    # plot streams as blue lines
    # convert polygon streams to boundary if necessary
    geom_types = set(streams.geom_type.unique())
    if geom_types & {"Polygon", "MultiPolygon"}:
        lines = streams.copy()
        lines['geometry'] = lines.geometry.boundary
    elif geom_types & {"Point", "MultiPoint"}:
        lines = streams.copy()
        lines['geometry'] = lines.geometry.buffer(6).boundary
    else:
        lines = streams

    lines.plot(ax=ax, color='deepskyblue', linewidth=0.6, alpha=0.9)

    # extent: zoom to watersheds total bounds
    total_bounds = watersheds.total_bounds  # minx, miny, maxx, maxy
    pad_x = (total_bounds[2] - total_bounds[0]) * 0.03
    pad_y = (total_bounds[3] - total_bounds[1]) * 0.03
    ax.set_xlim(total_bounds[0] - pad_x, total_bounds[2] + pad_x)
    ax.set_ylim(total_bounds[1] - pad_y, total_bounds[3] + pad_y)

    # add colorbar for area
    sm = plt.cm.ScalarMappable(cmap='OrRd', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.01)
    cbar.set_label('area_km2')

    # add north arrow (simple)
    x0 = total_bounds[2] - pad_x*2
    y0 = total_bounds[3] - pad_y*2
    ax.annotate('N', xy=(x0, y0+pad_y*0.6), fontsize=12, ha='center')
    ax.arrow(x0, y0, 0, pad_y*0.5, head_width=pad_x*0.5, head_length=pad_y*0.25, fc='k', ec='k')

    # add scale bar (approx)
    # get axis width in data units
    xspan = ax.get_xlim()[1] - ax.get_xlim()[0]
    # choose scale bar length ~ 5% of xspan, round to nice number (m)
    desired = xspan * 0.05
    # round desired to nearest 100/500/1000 m
    def nice_round(m):
        if m <= 100: return 100
        if m <= 500: return 500
        if m <= 1000: return 1000
        if m <= 5000: return 5000
        if m <= 10000: return 10000
        return 20000
    sb_len = nice_round(desired)
    # position
    sx = ax.get_xlim()[0] + pad_x
    sy = ax.get_ylim()[0] + pad_y*0.5
    ax.hlines(sy, sx, sx + sb_len, colors='k', linewidth=3)
    ax.vlines([sx, sx+sb_len], sy - pad_y*0.05, sy + pad_y*0.05, colors='k', linewidth=3)
    ax.text(sx + sb_len/2, sy - pad_y*0.12, f"{int(sb_len)} m", ha='center', va='top', fontsize=10)

    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("Saved map image:", out_png)

def main():
    print("Loading data...")
    watersheds = load_watersheds()
    streams = load_streams()
    # If streams came as points and watersheds in projected CRS, we will reproj later

    # Reproject to target CRS for accurate lengths
    if watersheds.crs is None:
        raise RuntimeError("Watersheds layer has no CRS; cannot reliably compute lengths.")
    if watersheds.crs.to_string() != TARGET_CRS:
        print(f"Reprojecting watersheds {watersheds.crs} -> {TARGET_CRS}")
        watersheds = watersheds.to_crs(TARGET_CRS)
    if streams.crs is None:
        raise RuntimeError("Streams layer has no CRS; cannot compute lengths.")
    if streams.crs.to_string() != TARGET_CRS:
        print(f"Reprojecting streams {streams.crs} -> {TARGET_CRS}")
        streams = streams.to_crs(TARGET_CRS)

    print("Computing stream lengths per watershed ...")
    watersheds_enh = compute_stream_length_per_watershed(watersheds, streams)
    print("Done computing lengths. Sample:")
    print(watersheds_enh[['id', 'area_km2', 'stream_length_km']].sort_values('area_km2', ascending=False).head())

    # Save results
    save_results(watersheds_enh)

    # Plot and export PNG
    print("Rendering map image ...")
    plot_map(watersheds_enh, streams, HILLSHADE, OUT_PNG)
    print("All done.")

if __name__ == "__main__":
    main()
