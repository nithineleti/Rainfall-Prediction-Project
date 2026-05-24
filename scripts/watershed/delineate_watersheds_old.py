#!/usr/bin/env python
"""
src/delineate_watersheds.py

Delineate micro-watersheds from DEM using D8 flow routing and flow accumulation.

Outputs (data/processed/stage4/):
 - watersheds_lucknow.tif (raster)        : Watershed ID for each pixel
 - watershed_boundaries_lucknow.shp (vector) : Polygon boundaries with attributes
 - pour_points_lucknow.shp (vector)          : Watershed outlet points

Usage:
    python src/delineate_watersheds.py

Parameters:
    MIN_AREA_KM2 = 0.5   # Minimum watershed area
    MAX_AREA_KM2 = 5.0   # Maximum watershed area (micro-watershed range)
    
Notes:
 - Uses flow accumulation peaks as pour points (watershed outlets)
 - Traces upstream contributing area for each pour point
 - Filters by size to get micro-watersheds
 - Vectorizes to GeoPackage/Shapefile for GIS compatibility
"""
import os
import numpy as np
import rasterio
from rasterio.features import shapes
from scipy.ndimage import maximum_filter, label
from collections import deque
import geopandas as gpd
from shapely.geometry import shape, Point
import warnings
warnings.filterwarnings('ignore')

# Paths
FLOW_DIR_FILE = "data/processed/stage3/flow_dir_lucknow.tif"
FLOW_ACC_FILE = "data/processed/stage3/flow_acc_lucknow.tif"
OUT_DIR = "data/processed/stage4"
os.makedirs(OUT_DIR, exist_ok=True)

# Outputs
OUT_WATERSHEDS_RASTER = os.path.join(OUT_DIR, "watersheds_lucknow.tif")
OUT_WATERSHEDS_VECTOR = os.path.join(OUT_DIR, "watershed_boundaries_lucknow.shp")
OUT_POUR_POINTS = os.path.join(OUT_DIR, "pour_points_lucknow.shp")

# Parameters
MIN_AREA_KM2 = 0.05  # Minimum watershed area (km²) - adjusted for small study area
MAX_AREA_KM2 = 2.0   # Maximum watershed area (km²) - micro-watershed definition
PIXEL_SIZE_M = 12.5  # ALOS PALSAR DEM resolution
PEAK_WINDOW = 10     # Window size for local maxima detection (avoid too many tiny watersheds)

# D8 neighbor offsets (matches derive_drainage.py)
# [E, NE, N, NW, W, SW, S, SE]
NBRS = [(0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1)]
REVERSE_NBRS = [(0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1)]


def trace_upstream(flow_dir, outlet_row, outlet_col):
    """
    Trace all cells that drain to the outlet point
    
    Uses breadth-first search with reverse flow direction
    to find the contributing watershed area.
    
    Parameters:
    -----------
    flow_dir : ndarray (int8)
        D8 flow direction array (0-7 = direction index, -1 = sink/nodata)
    outlet_row, outlet_col : int
        Coordinates of watershed outlet (pour point)
    
    Returns:
    --------
    contributing : ndarray (bool)
        True for cells that drain to this outlet
    """
    rows, cols = flow_dir.shape
    contributing = np.zeros_like(flow_dir, dtype=bool)
    
    # BFS queue
    queue = deque([(outlet_row, outlet_col)])
    contributing[outlet_row, outlet_col] = True
    
    while queue:
        r, c = queue.popleft()
        
        # Check all neighbors that flow INTO this cell
        for i, (dr, dc) in enumerate(NBRS):
            nr, nc = r + dr, c + dc
            
            # Bounds check
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            
            # Skip if already visited
            if contributing[nr, nc]:
                continue
            
            # If neighbor's flow direction points to current cell, add to watershed
            if flow_dir[nr, nc] == i:
                contributing[nr, nc] = True
                queue.append((nr, nc))
    
    return contributing


def find_pour_points(flow_acc, min_pixels, max_pixels, peak_window=20):
    """
    Identify watershed pour points using flow accumulation peaks
    
    Pour points are local maxima in flow accumulation where
    multiple streams converge (high drainage area).
    
    If no peaks found (flat terrain), falls back to grid-based approach.
    
    Parameters:
    -----------
    flow_acc : ndarray
        Flow accumulation (upstream cell count)
    min_pixels : int
        Minimum accumulation threshold
    max_pixels : int
        Maximum accumulation (avoid whole-district outlet)
    peak_window : int
        Size of window for local maximum detection
    
    Returns:
    --------
    pour_points : list of (row, col) tuples
        Coordinates of identified pour points
    """
    # Find local maxima
    local_max = maximum_filter(flow_acc, size=peak_window)
    is_peak = (flow_acc == local_max) & (flow_acc >= min_pixels) & (flow_acc <= max_pixels)
    
    # Get coordinates
    pour_points = np.argwhere(is_peak)
    
    # Fallback: If no pour points found (flat terrain or small area)
    # Use grid-based approach: create regular grid of watershed outlets
    if len(pour_points) == 0:
        print("  ⚠ No pour points found using flow accumulation peaks")
        print("  → Using grid-based watershed delineation (for flat terrain)")
        
        rows, cols = flow_acc.shape
        
        # Create grid of pour points (e.g., every 200 pixels ≈ 2.5 km)
        grid_spacing = 100  # pixels (1.25 km spacing)
        
        pour_points_list = []
        for r in range(grid_spacing//2, rows, grid_spacing):
            for c in range(grid_spacing//2, cols, grid_spacing):
                # Use cells with highest flow accumulation in local window
                r_start = max(0, r - grid_spacing//2)
                r_end = min(rows, r + grid_spacing//2)
                c_start = max(0, c - grid_spacing//2)
                c_end = min(cols, c + grid_spacing//2)
                
                window = flow_acc[r_start:r_end, c_start:c_end]
                if window.size > 0:
                    local_argmax = np.unravel_index(window.argmax(), window.shape)
                    pour_r = r_start + local_argmax[0]
                    pour_c = c_start + local_argmax[1]
                    pour_points_list.append([pour_r, pour_c])
        
        pour_points = np.array(pour_points_list)
        print(f"  → Generated {len(pour_points)} grid-based pour points")
    
    return pour_points


def delineate_watersheds(flow_dir, flow_acc, min_area_km2, max_area_km2, pixel_size_m):
    """
    Delineate micro-watersheds from flow direction and accumulation
    
    Algorithm:
    1. Convert area thresholds to pixel counts
    2. Find pour points (flow accumulation peaks)
    3. Trace upstream contributing area for each pour point
    4. Assign unique watershed ID to each contributing area
    5. Filter by size constraints
    6. Renumber consecutively
    
    Parameters:
    -----------
    flow_dir : ndarray
        D8 flow direction array
    flow_acc : ndarray
        Flow accumulation array
    min_area_km2, max_area_km2 : float
        Size constraints for micro-watersheds
    pixel_size_m : float
        DEM resolution in meters
    
    Returns:
    --------
    watersheds : ndarray (int32)
        Watershed ID for each pixel (0 = no watershed)
    pour_points : ndarray
        Coordinates of pour points (N x 2)
    """
    print("\n" + "="*70)
    print("WATERSHED DELINEATION ALGORITHM")
    print("="*70)
    
    # Convert area to pixels
    pixel_area_km2 = (pixel_size_m / 1000) ** 2
    min_pixels = int(min_area_km2 / pixel_area_km2)
    max_pixels = int(max_area_km2 / pixel_area_km2)
    
    print(f"\nArea constraints:")
    print(f"  Min area: {min_area_km2} km² = {min_pixels} pixels")
    print(f"  Max area: {max_area_km2} km² = {max_pixels} pixels")
    print(f"  Pixel size: {pixel_size_m}m → {pixel_area_km2*1e6:.0f} m² per pixel")
    
    # Find pour points
    print(f"\nFinding pour points (local flow accumulation peaks)...")
    pour_points = find_pour_points(flow_acc, min_pixels, max_pixels, PEAK_WINDOW)
    print(f"  Identified {len(pour_points)} candidate pour points")
    
    # Initialize watershed raster
    watersheds = np.zeros_like(flow_acc, dtype=np.int32)
    valid_pour_points = []
    
    # Trace watershed for each pour point
    print(f"\nTracing watersheds upstream from pour points...")
    watershed_id = 1
    
    for row, col in pour_points:
        # Skip if already assigned to another watershed
        if watersheds[row, col] > 0:
            continue
        
        # Trace contributing area
        contributing = trace_upstream(flow_dir, row, col)
        ws_size = contributing.sum()
        
        # Check size constraints
        if ws_size < min_pixels or ws_size > max_pixels:
            continue
        
        # Assign watershed ID
        watersheds[contributing] = watershed_id
        valid_pour_points.append([row, col])
        
        if watershed_id % 50 == 0:
            print(f"  Processed {watershed_id} watersheds...")
        
        watershed_id += 1
    
    valid_pour_points = np.array(valid_pour_points)
    
    print(f"\n✓ Delineated {watershed_id - 1} watersheds")
    
    # Calculate area statistics
    if watershed_id > 1:
        areas_km2 = []
        for ws_id in range(1, watershed_id):
            ws_area = (watersheds == ws_id).sum() * pixel_area_km2
            areas_km2.append(ws_area)
        
        areas_km2 = np.array(areas_km2)
        
        print(f"\nWatershed statistics:")
        print(f"  Count: {len(areas_km2)}")
        print(f"  Area range: {areas_km2.min():.2f} - {areas_km2.max():.2f} km²")
        print(f"  Mean area: {areas_km2.mean():.2f} km²")
        print(f"  Median area: {np.median(areas_km2):.2f} km²")
        print(f"  Total coverage: {areas_km2.sum():.2f} km²")
    else:
        print(f"\n⚠ No watersheds found! Try adjusting MIN_AREA_KM2/MAX_AREA_KM2 parameters.")
    
    return watersheds, valid_pour_points


def vectorize_watersheds(watersheds, transform, crs, pixel_size_m):
    """
    Convert watershed raster to vector polygons
    
    Extracts polygon features and calculates geometric attributes:
    - Area (km²)
    - Perimeter (m)
    - Compactness ratio (1 = circle, <1 = elongated)
    - Centroid coordinates
    
    Parameters:
    -----------
    watersheds : ndarray
        Watershed ID raster
    transform : Affine
        Raster geotransform
    crs : CRS
        Coordinate reference system
    pixel_size_m : float
        Pixel size in meters (for area calculation)
    
    Returns:
    --------
    gdf : GeoDataFrame
        Watershed polygons with attributes
    """
    print("\nVectorizing watersheds to polygons...")
    
    # Extract polygon shapes
    mask = watersheds > 0
    geoms = []
    values = []
    
    for geom, value in shapes(watersheds.astype(np.int32), mask=mask, transform=transform):
        geoms.append(shape(geom))
        values.append(int(value))
    
    print(f"  Extracted {len(geoms)} polygons")
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'watershed_id': values,
        'geometry': geoms
    }, crs=crs)
    
    # Calculate attributes
    print("  Calculating geometric attributes...")
    
    # Area in km² (using pixel count for accuracy)
    pixel_area_m2 = pixel_size_m ** 2
    gdf['area_km2'] = 0.0
    
    for idx, row in gdf.iterrows():
        ws_id = row['watershed_id']
        pixel_count = (watersheds == ws_id).sum()
        gdf.loc[idx, 'area_km2'] = pixel_count * pixel_area_m2 / 1e6
    
    # Perimeter (assuming equal lat/lon degrees at Lucknow ~27°N)
    # 1 degree ≈ 111 km latitude, ≈ 99 km longitude
    deg_to_m = 105000  # Approximate average
    gdf['perimeter_m'] = gdf.geometry.length * deg_to_m
    
    # Compactness ratio: 4π*Area / Perimeter²
    # Perfect circle = 1.0, elongated shapes < 1.0
    gdf['compactness'] = (4 * np.pi * gdf['area_km2'] * 1e6) / (gdf['perimeter_m'] ** 2)
    
    # Centroid coordinates
    centroids = gdf.geometry.centroid
    gdf['centroid_lon'] = centroids.x
    gdf['centroid_lat'] = centroids.y
    
    # Sort by watershed ID
    gdf = gdf.sort_values('watershed_id').reset_index(drop=True)
    
    return gdf


def save_pour_points(pour_points, transform, crs, output_path):
    """
    Save pour point locations as point shapefile
    
    Parameters:
    -----------
    pour_points : ndarray
        Pour point coordinates (N x 2 array of row, col)
    transform : Affine
        Raster geotransform
    crs : CRS
        Coordinate reference system
    output_path : str
        Output shapefile path
    """
    print("\nCreating pour points shapefile...")
    
    geoms = []
    for row, col in pour_points:
        # Convert pixel coordinates to geographic
        lon, lat = transform * (col, row)
        geoms.append(Point(lon, lat))
    
    gdf = gpd.GeoDataFrame({
        'point_id': range(1, len(geoms) + 1),
        'geometry': geoms
    }, crs=crs)
    
    gdf.to_file(output_path)
    print(f"✓ Saved {len(gdf)} pour points to: {output_path}")


def main():
    print("="*70)
    print("MICRO-WATERSHED DELINEATION FOR LUCKNOW DISTRICT")
    print("="*70)
    print(f"\nParameters:")
    print(f"  Size range: {MIN_AREA_KM2} - {MAX_AREA_KM2} km² (micro-watershed)")
    print(f"  DEM resolution: {PIXEL_SIZE_M}m (ALOS PALSAR)")
    
    # Check if flow direction exists
    if not os.path.exists(FLOW_DIR_FILE):
        print(f"\n❌ Flow direction file not found: {FLOW_DIR_FILE}")
        print("\nPlease run derive_drainage.py first!")
        print("  Command: python src/derive_drainage.py")
        return
    
    # Load flow direction
    print(f"\nLoading flow direction from: {FLOW_DIR_FILE}")
    with rasterio.open(FLOW_DIR_FILE) as src:
        flow_dir = src.read(1)
        transform = src.transform
        crs = src.crs
        profile = src.profile
    
    print(f"  Shape: {flow_dir.shape}")
    print(f"  CRS: {crs}")
    
    # Load flow accumulation
    print(f"\nLoading flow accumulation from: {FLOW_ACC_FILE}")
    with rasterio.open(FLOW_ACC_FILE) as src:
        flow_acc = src.read(1)
    
    # Handle NaN values
    flow_acc = np.nan_to_num(flow_acc, nan=0.0)
    
    print(f"  Flow accumulation range: {flow_acc.min():.0f} - {flow_acc.max():.0f} cells")
    
    # Delineate watersheds
    watersheds, pour_points = delineate_watersheds(
        flow_dir, flow_acc,
        min_area_km2=MIN_AREA_KM2,
        max_area_km2=MAX_AREA_KM2,
        pixel_size_m=PIXEL_SIZE_M
    )
    
    # Save watershed raster
    print(f"\nSaving watershed raster...")
    profile_out = profile.copy()
    profile_out.update(dtype='int32', nodata=0, compress='lzw')
    
    with rasterio.open(OUT_WATERSHEDS_RASTER, 'w', **profile_out) as dst:
        dst.write(watersheds, 1)
    
    print(f"✓ Saved: {OUT_WATERSHEDS_RASTER}")
    
    # Vectorize to shapefile
    gdf = vectorize_watersheds(watersheds, transform, crs, PIXEL_SIZE_M)
    
    # Save shapefile
    print(f"\nSaving watershed boundaries...")
    gdf.to_file(OUT_WATERSHEDS_VECTOR)
    print(f"✓ Saved: {OUT_WATERSHEDS_VECTOR}")
    
    # Save CSV for easy inspection
    csv_path = OUT_WATERSHEDS_VECTOR.replace('.shp', '.csv')
    gdf.drop('geometry', axis=1).to_csv(csv_path, index=False)
    print(f"✓ Saved: {csv_path}")
    
    # Save pour points
    save_pour_points(pour_points, transform, crs, OUT_POUR_POINTS)
    
    # Summary
    print("\n" + "="*70)
    print("DELINEATION COMPLETE!")
    print("="*70)
    
    print(f"\nOutputs:")
    print(f"  1. Watershed raster: {OUT_WATERSHEDS_RASTER}")
    print(f"  2. Watershed polygons: {OUT_WATERSHEDS_VECTOR}")
    print(f"  3. Pour points: {OUT_POUR_POINTS}")
    
    print(f"\nStatistics:")
    print(f"  Total watersheds: {len(gdf)}")
    print(f"  Size range: {gdf['area_km2'].min():.2f} - {gdf['area_km2'].max():.2f} km²")
    print(f"  Mean size: {gdf['area_km2'].mean():.2f} km²")
    print(f"  Total coverage: {gdf['area_km2'].sum():.2f} km²")
    print(f"  Compactness: {gdf['compactness'].mean():.3f} (1.0 = circular)")
    
    print(f"\n✓ Micro-watersheds ready for characterization!")
    print(f"\nNext step: python src/characterize_watersheds.py")


if __name__ == "__main__":
    main()
