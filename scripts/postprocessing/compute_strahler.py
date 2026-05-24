#!/usr/bin/env python3
"""
scripts/postprocessing/compute_strahler.py

Compute Strahler order for skeleton segments.

Inputs (assumed produced earlier):
 - data/rasters/stream_skeleton_pts.shp  (points with seg_id)
 - data/rasters/flow_dir.tif            (int8, 0..7 neighbor index, -1 for sink/nodata)
 - data/rasters/stream_segments_lengths.csv (seg_id, pixel_count, length_km) [optional]

Outputs:
 - data/rasters/stream_segments_strahler.csv (seg_id, pixel_count, length_km, strahler)
 - data/rasters/stream_segments_strahler.shp (points with seg_id + strahler)
"""
from pathlib import Path
import rasterio
import numpy as np
import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Point

BASE = Path("data/rasters")
SKEL_PTS = BASE / "stream_skeleton_pts.shp"
FLOWDIR = BASE / "flow_dir.tif"
SEG_CSV = BASE / "stream_segments_lengths.csv"
OUT_CSV = BASE / "stream_segments_strahler.csv"
OUT_SHP = BASE / "stream_segments_strahler.shp"

if not SKEL_PTS.exists():
    raise SystemExit(f"Skeleton points not found: {SKEL_PTS}")
if not FLOWDIR.exists():
    raise SystemExit(f"Flow direction raster not found: {FLOWDIR}")

print("Loading skeleton points...")
gdf = gpd.read_file(SKEL_PTS)
if "seg_id" not in gdf.columns:
    raise SystemExit("Expected 'seg_id' attribute in skeleton points shapefile.")

# read flowdir raster as array
with rasterio.open(FLOWDIR) as src:
    fd = src.read(1)  # int values
    transform = src.transform
    nodata = src.nodata
    crs = src.crs

# helper: map geometry point -> pixel row/col
def xy_to_rc(x, y, transform):
    inv = ~transform
    col, row = inv * (x, y)
    return int(round(row)), int(round(col))

# Build a mapping: for each skeleton point (pixel), find downstream pixel using flowdir,
# then map that downstream pixel to a seg_id (if any). We'll use a dictionary keyed by pixel rc.
print("Indexing skeleton points by pixel coordinates...")
pix_to_seg = {}        # (r,c) -> seg_id
seg_pixel_counts = {}  # seg_id -> count (fallback if CSV not present)
coords = []
for idx, row in gdf.iterrows():
    seg = int(row["seg_id"])
    geom = row.geometry
    x, y = geom.x, geom.y
    r, c = xy_to_rc(x, y, transform)
    pix_to_seg[(r, c)] = seg
    seg_pixel_counts[seg] = seg_pixel_counts.get(seg, 0) + 1
    coords.append(((r, c), seg))

print(f"Indexed {len(coords)} skeleton pixels across {len(set(pix_to_seg.values()))} segments.")

# If CSV exists, load pixel_count & length_km for final table
seg_df = {}
if SEG_CSV.exists():
    print("Loading existing segments CSV for length info...")
    dfseg = pd.read_csv(SEG_CSV)
    for _, r in dfseg.iterrows():
        seg_df[int(r["seg_id"])] = {"pixel_count": int(r["pixel_count"]), "length_km": float(r["length_km"])}
else:
    # fallback to computed counts
    for seg, cnt in seg_pixel_counts.items():
        seg_df[seg] = {"pixel_count": int(cnt), "length_km": float(cnt)}  # length placeholder (pixels) — not ideal

# neighbor offset lookup matches flowdir index convention used earlier: [E, NE, N, NW, W, SW, S, SE]
nbr_offsets = [
    (0, 1), (-1, 1), (-1, 0), (-1, -1),
    (0, -1), (1, -1), (1, 0), (1, 1)
]

# build directed edges between segments: seg -> downstream_seg (if downstream pixel belongs to some seg)
print("Building inter-segment graph edges using flow direction...")
edges = []  # list of (src_seg, dst_seg)
missed = 0
for (r, c), seg in coords:
    # check bounds
    if r < 0 or r >= fd.shape[0] or c < 0 or c >= fd.shape[1]:
        continue
    d = int(fd[r, c])
    if d < 0:
        # sink or nodata
        missed += 1
        continue
    dr, dc = nbr_offsets[d]
    rr = r + dr
    cc = c + dc
    if (rr, cc) in pix_to_seg:
        downstream_seg = pix_to_seg[(rr, cc)]
        if downstream_seg != seg:
            edges.append((seg, downstream_seg))
    else:
        # downstream pixel not skeleton (maybe smoothing or gap). Check small neighborhood for nearest skeleton pixel
        found = False
        for drn in (-1, 0, 1):
            for dcn in (-1, 0, 1):
                nbr = (rr + drn, cc + dcn)
                if nbr in pix_to_seg:
                    downstream_seg = pix_to_seg[nbr]
                    if downstream_seg != seg:
                        edges.append((seg, downstream_seg))
                    found = True
                    break
            if found:
                break
        if not found:
            missed += 1

print(f"Built {len(edges)} inter-segment edge records; missed {missed} skeleton pixels with no downstream seg.")

# Create directed graph and collapse parallel edges
G = nx.DiGraph()
G.add_nodes_from(list(seg_df.keys()))
G.add_edges_from(edges)

# Remove self-loops (if any)
G.remove_edges_from(nx.selfloop_edges(G))

print("Graph: nodes=", G.number_of_nodes(), "edges=", G.number_of_edges())

# Now compute Strahler order.
# We want to compute Strahler order at segment-level where edges point downstream (u->v means u flows to v).
# For Strahler we need upstream lists: find nodes with no incoming edges (sources).
from collections import deque, defaultdict

# Build upstream adjacency: for each node v, list of upstream nodes that flow into v
upstreams = defaultdict(list)
for u, v in G.edges():
    upstreams[v].append(u)

# nodes with no upstreams are sources
all_nodes = set(G.nodes())
strahler = {n: None for n in all_nodes}

# compute topological order on the reversed graph (process sources to sinks)
# We'll compute iteratively using indegree concept on reversed edges
rev_indeg = {n: len(upstreams.get(n, [])) for n in all_nodes}
queue = deque([n for n, deg in rev_indeg.items() if deg == 0])

# For nodes with no upstream, assign order 1
for n in list(queue):
    strahler[n] = 1

print("Computing Strahler orders...")
processed = 0
while queue:
    node = queue.popleft()
    processed += 1
    # propagate to downstreams (successors in G)
    for down in G.successors(node):
        # when considering 'down', collect orders of its upstreams if all are assigned
        up_nodes = upstreams.get(down, [])
        if any(strahler.get(u) is None for u in up_nodes):
            # not ready yet
            continue
        # all upstreams assigned -> compute order
        orders = [strahler[u] for u in up_nodes]
        if len(orders) == 0:
            ord_val = 1
        else:
            max_o = max(orders)
            if orders.count(max_o) >= 2:
                ord_val = max_o + 1
            else:
                ord_val = max_o
        # assign if not assigned yet
        if strahler.get(down) is None:
            strahler[down] = ord_val
        else:
            # if assigned, use max (shouldn't normally happen)
            strahler[down] = max(strahler[down], ord_val)

        # decrease reverse indegree and enqueue if ready
        rev_indeg[down] -= 1
        if rev_indeg[down] == 0:
            queue.append(down)

# Any remaining unassigned nodes -> assign 1 (isolated or sinks)
for n in all_nodes:
    if strahler[n] is None:
        strahler[n] = 1

print("Strahler assignment done. Processed nodes:", processed)

# Build output table
out_rows = []
for seg, meta in seg_df.items():
    pcount = meta.get("pixel_count", 0)
    length_km = meta.get("length_km", 0.0)
    s = int(strahler.get(seg, 1))
    out_rows.append({"seg_id": int(seg), "pixel_count": int(pcount), "length_km": float(length_km), "strahler": s})

df_out = pd.DataFrame(out_rows)
df_out.to_csv(OUT_CSV, index=False)
print("Wrote Strahler CSV:", OUT_CSV)

# Join strahler back to skeleton points (so every point has seg_id + strahler)
gdf_out = gdf.copy()
gdf_out["strahler"] = gdf_out["seg_id"].map(lambda x: int(strahler.get(int(x), 1)))
gdf_out.to_file(OUT_SHP)
print("Wrote skeleton points with Strahler to:", OUT_SHP)

print("Done.")
