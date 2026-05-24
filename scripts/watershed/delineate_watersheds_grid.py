#!/usr/bin/env python
"""
src/delineate_watersheds_grid.py

Create planning units (micro-watersheds) using regular grid approach.

For flat alluvial terrain like Lucknow where traditional watershed delineation
doesn't work well, this creates uniform planning units that still incorporate
hydrological characteristics.

Outputs (data/processed/stage4/):
 - watersheds_lucknow.tif (raster)               : Watershed ID for each pixel  
 - watershed_boundaries_lucknow.shp (vector)     : Polygon boundaries
 - watershed_centroids_lucknow.shp (vector)      : Management unit centers

Usage:
    python src/delineate_watersheds_grid.py

Parameters:
    GRID_SIZE_KM = 1.5  # Size of each watershed planning unit (1.5 x 1.5 km)
"""
import os
import numpy as np
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape, Point
import warnings
warnings.filterwarnings('ignore')

# Paths
DEM_FILE = "data/processed/dem_lucknow.tif"
OUT_DIR = "data/processed/stage4"
os.makedirs(OUT_DIR, exist_ok=True)

# Outputs
OUT_WATERSHEDS_RASTER = os.path.join(OUT_DIR, "watersheds_lucknow.tif")
OUT_WATERSHEDS_VECTOR = os.path.join(OUT_DIR, "watershed_boundaries_lucknow.shp")
OUT_CENTROIDS = os.path.join(OUT_DIR, "watershed_centroids_lucknow.shp")

# Parameters
GRID_SIZE_KM = 1.5  # Size of each planning unit (km)
PIXEL_SIZE_M = 12.5  # ALOS PALSAR resolution


def create_grid_watersheds(dem_shape, grid_size_km, pixel_size_m):
    """
    Create regular grid of watershed planning units
    
    For flat terrain, uniform grid provides consistent management units
    while still allowing integration of hydrological data.
    
    Parameters:
    -----------
    dem_shape : tuple
        (rows, cols) of DEM raster
    grid_size_km : float
        Size of each grid cell in kilometers
    pixel_size_m : float
        DEM pixel size in meters
    
    Returns:
    --------
    watersheds : ndarray (int32)
        Grid ID for each pixel
    """
    rows, cols = dem_shape
    
    # Convert grid size to pixels
    grid_pixels = int((grid_size_km * 1000) / pixel_size_m)
    
    print(f"\nGrid parameters:")
    print(f"  Grid size: {grid_size_km} km = {grid_pixels} pixels")
    print(f"  Grid area: {grid_size_km**2:.2f} km²")
    
    # Create grid
    watersheds = np.zeros((rows, cols), dtype=np.int32)
    
    watershed_id = 1
    for r_start in range(0, rows, grid_pixels):
        for c_start in range(0, cols, grid_pixels):
            r_end = min(r_start + grid_pixels, rows)
            c_end = min(c_start + grid_pixels, cols)
            
            watersheds[r_start:r_end, c_start:c_end] = watershed_id
            watershed_id += 1
    
    n_watersheds = watershed_id - 1
    print(f"  Created {n_watersheds} grid cells")
    
    # Calculate statistics
    pixel_area_km2 = (pixel_size_m / 1000) ** 2
    
    areas = []
    for ws_id in range(1, watershed_id):
        area = (watersheds == ws_id).sum() * pixel_area_km2
        areas.append(area)
    
    areas = np.array(areas)
    
    print(f"\nWatershed statistics:")
    print(f"  Count: {len(areas)}")
    print(f"  Area range: {areas.min():.2f} - {areas.max():.2f} km²")
    print(f"  Mean area: {areas.mean():.2f} km²")
    print(f"  Total coverage: {areas.sum():.2f} km²")
    
    return watersheds


def vectorize_grid(watersheds, transform, crs, pixel_size_m):
    """
    Convert grid to vector polygons
    
    Parameters:
    -----------
    watersheds : ndarray
        Grid ID raster
    transform : Affine
        Raster geotransform
    crs : CRS
        Coordinate reference system
    pixel_size_m : float
        Pixel size in meters
    
    Returns:
    --------
    gdf : GeoDataFrame
        Grid polygons with attributes
    """
    print("\nVectorizing grid to polygons...")
    
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
    
    # Area
    pixel_area_m2 = pixel_size_m ** 2
    gdf['area_km2'] = 0.0
    
    for idx, row in gdf.iterrows():
        ws_id = row['watershed_id']
        pixel_count = (watersheds == ws_id).sum()
        gdf.loc[idx, 'area_km2'] = pixel_count * pixel_area_m2 / 1e6
    
    # Perimeter (approximate)
    deg_to_m = 105000
    gdf['perimeter_m'] = gdf.geometry.length * deg_to_m
    
    # Compactness
    gdf['compactness'] = (4 * np.pi * gdf['area_km2'] * 1e6) / (gdf['perimeter_m'] ** 2)
    
    # Centroid
    centroids = gdf.geometry.centroid
    gdf['centroid_lon'] = centroids.x
    gdf['centroid_lat'] = centroids.y
    
    # Sort by ID
    gdf = gdf.sort_values('watershed_id').reset_index(drop=True)
    
    return gdf


def save_centroids(gdf, output_path):
    """
    Save watershed centroids as point shapefile (for management unit centers)
    """
    print("\nCreating centroids shapefile...")
    
    centroid_gdf = gpd.GeoDataFrame({
        'watershed_id': gdf['watershed_id'],
        'geometry': [Point(lon, lat) for lon, lat in zip(gdf['centroid_lon'], gdf['centroid_lat'])]
    }, crs=gdf.crs)
    
    centroid_gdf.to_file(output_path)
    print(f"✓ Saved {len(centroid_gdf)} centroids to: {output_path}")


def main():
    print("="*70)
    print("GRID-BASED WATERSHED PLANNING UNITS FOR LUCKNOW DISTRICT")
    print("="*70)
    print(f"\nApproach: Regular grid (suitable for flat alluvial terrain)")
    print(f"Grid size: {GRID_SIZE_KM} km × {GRID_SIZE_KM} km")
    print(f"Purpose: Administrative planning units with hydrological data")
    
    # Load DEM for extent and georeferencing
    print(f"\nLoading DEM from: {DEM_FILE}")
    with rasterio.open(DEM_FILE) as src:
        dem_shape = src.shape
        transform = src.transform
        crs = src.crs
        profile = src.profile
    
    print(f"  DEM shape: {dem_shape}")
    print(f"  CRS: {crs}")
    
    # Create grid
    print("\n" + "="*70)
    print("CREATING GRID-BASED PLANNING UNITS")
    print("="*70)
    
    watersheds = create_grid_watersheds(dem_shape, GRID_SIZE_KM, PIXEL_SIZE_M)
    
    # Save raster
    print(f"\nSaving watershed raster...")
    profile_out = profile.copy()
    profile_out.update(dtype='int32', nodata=0, compress='lzw')
    
    with rasterio.open(OUT_WATERSHEDS_RASTER, 'w', **profile_out) as dst:
        dst.write(watersheds, 1)
    
    print(f"✓ Saved: {OUT_WATERSHEDS_RASTER}")
    
    # Vectorize
    gdf = vectorize_grid(watersheds, transform, crs, PIXEL_SIZE_M)
    
    # Save shapefile
    print(f"\nSaving watershed boundaries...")
    gdf.to_file(OUT_WATERSHEDS_VECTOR)
    print(f"✓ Saved: {OUT_WATERSHEDS_VECTOR}")
    
    # Save CSV
    csv_path = OUT_WATERSHEDS_VECTOR.replace('.shp', '.csv')
    gdf.drop('geometry', axis=1).to_csv(csv_path, index=False)
    print(f"✓ Saved: {csv_path}")
    
    # Save centroids
    save_centroids(gdf, OUT_CENTROIDS)
    
    # Summary
    print("\n" + "="*70)
    print("GRID CREATION COMPLETE!")
    print("="*70)
    
    print(f"\nOutputs:")
    print(f"  1. Watershed raster: {OUT_WATERSHEDS_RASTER}")
    print(f"  2. Watershed polygons: {OUT_WATERSHEDS_VECTOR}")
    print(f"  3. Watershed centroids: {OUT_CENTROIDS}")
    
    print(f"\nStatistics:")
    print(f"  Total planning units: {len(gdf)}")
    print(f"  Unit size range: {gdf['area_km2'].min():.2f} - {gdf['area_km2'].max():.2f} km²")
    print(f"  Mean unit size: {gdf['area_km2'].mean():.2f} km²")
    print(f"  Total coverage: {gdf['area_km2'].sum():.2f} km²")
    print(f"  Grid compactness: {gdf['compactness'].mean():.3f} (1.0 = square)")
    
    print(f"\n✓ Planning units ready for characterization!")
    print(f"\nNote: These are administrative planning units, not hydrological watersheds.")
    print(f"      They incorporate drainage patterns through zonal statistics.")
    print(f"\nNext step: python src/characterize_watersheds.py")


if __name__ == "__main__":
    main()
