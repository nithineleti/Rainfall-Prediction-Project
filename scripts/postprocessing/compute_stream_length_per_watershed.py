#!/usr/bin/env python3
"""
Compute accurate stream length (km) within each watershed polygon.

Inputs:
 - data/rasters/watersheds.gpkg (layer=watersheds)
 - data/rasters/stream_polygons.shp or stream_skeleton_pts.shp
Outputs:
 - data/rasters/watersheds_stats_enhanced.csv (adds stream_length_km)
 - updates watersheds.gpkg with same attribute
"""
import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE = Path("data/rasters")
WGPKG = BASE / "watersheds.gpkg"
STREAMS = BASE / "stream_polygons.shp"   # or change to stream_skeleton_pts.shp
OUT_CSV = BASE / "watersheds_stats_enhanced.csv"
OUT_GPKG = WGPKG

print("Loading data...")
watersheds = gpd.read_file(WGPKG, layer="watersheds")
streams = gpd.read_file(STREAMS)

if watersheds.crs != streams.crs:
    streams = streams.to_crs(watersheds.crs)

watersheds["stream_length_km"] = 0.0

for i, basin in watersheds.iterrows():
    geom = basin.geometry
    inter = streams[streams.intersects(geom)]
    if inter.empty:
        continue
    inter["geom_clip"] = inter.geometry.intersection(geom)
    inter = inter.set_geometry("geom_clip")
    # length measured in CRS units (meters for EPSG:32644)
    total_len_km = inter.length.sum() / 1000.0
    watersheds.at[i, "stream_length_km"] = total_len_km
    print(f"[{i+1}/{len(watersheds)}] Basin {basin['id']}: {total_len_km:.3f} km")

watersheds.to_file(OUT_GPKG, layer="watersheds", driver="GPKG")
watersheds.drop(columns="geometry").to_csv(OUT_CSV, index=False)
print(f"✅ Updated {OUT_GPKG} and wrote {OUT_CSV}")
