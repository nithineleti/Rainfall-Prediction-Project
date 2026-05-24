"""
ALOS PALSAR DEM Processing Script
Mosaic multiple DEM tiles from different folders and clip to Lucknow district
"""

import os
import glob
from pathlib import Path
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
import geopandas as gpd
import numpy as np

# ============================================
# CONFIGURATION - Update these paths
# ============================================

# Path to folder containing all extracted DEM folders
DEM_BASE_DIR = r"G:\PROJECTS\watershed-up\data\raw\alos_dem_tiles"

# Path to Lucknow district shapefile
SHAPEFILE_PATH = r"G:\PROJECTS\watershed-up\data\raw\lucknow_shp\lucknow.shp"

# Output paths
MOSAIC_OUTPUT = r"G:\PROJECTS\watershed-up\data\raw\alos_dem_tiles\mosaic_dem_12.5.tif"
CLIPPED_OUTPUT = r"G:\PROJECTS\watershed-up\data\raw\lucknow_dem_12.5\dem_lucknow_12.5.tif"

# ============================================
# STEP 1: Find all DEM files recursively
# ============================================

print("="*60)
print("ALOS PALSAR DEM PROCESSING")
print("="*60)
print("\nStep 1: Locating DEM files...")

# Search for all .dem.tif files in subdirectories
dem_files = []

# Pattern 1: Look for files ending with _dem.tif
pattern1 = os.path.join(DEM_BASE_DIR, "**", "*_dem.tif")
dem_files.extend(glob.glob(pattern1, recursive=True))

# Pattern 2: Look for files with .dem.tif anywhere in name
if not dem_files:
    pattern2 = os.path.join(DEM_BASE_DIR, "**", "*.dem.tif")
    dem_files.extend(glob.glob(pattern2, recursive=True))

# Pattern 3: Look for any .tif with 'dem' in the name
if not dem_files:
    all_tifs = glob.glob(os.path.join(DEM_BASE_DIR, "**", "*.tif"), recursive=True)
    dem_files = [f for f in all_tifs if 'dem' in os.path.basename(f).lower()]

# Remove duplicates
dem_files = list(set(dem_files))

if not dem_files:
    print("ERROR: No DEM files found!")
    print(f"Searched in: {DEM_BASE_DIR}")
    print("\nPlease check:")
    print("1. DEM_BASE_DIR path is correct")
    print("2. Files are unzipped")
    print("3. .dem.tif files exist in subfolders")
    exit(1)

print(f"\nFound {len(dem_files)} DEM files:")
for i, f in enumerate(dem_files, 1):
    rel_path = os.path.relpath(f, DEM_BASE_DIR)
    print(f"  {i}. {rel_path}")

# ============================================
# STEP 2: Mosaic DEM tiles
# ============================================

print("\n" + "="*60)
print("Step 2: Mosaicking DEM tiles...")
print("="*60)

# Open all raster files
src_files = []
for fp in dem_files:
    try:
        src = rasterio.open(fp)
        src_files.append(src)
        print(f"  ✓ Opened: {os.path.basename(fp)}")
    except Exception as e:
        print(f"  ✗ Warning: Could not open {os.path.basename(fp)}: {e}")

if not src_files:
    print("\nERROR: No valid raster files could be opened!")
    exit(1)

print(f"\nMerging {len(src_files)} rasters...")

# Merge rasters
mosaic, out_transform = merge(src_files)

# Get metadata from first file
out_meta = src_files[0].meta.copy()

# Update metadata for mosaic
out_meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": out_transform,
    "compress": "lzw",  # Add compression to save space
    "tiled": True,
    "blockxsize": 256,
    "blockysize": 256
})

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(MOSAIC_OUTPUT), exist_ok=True)

# Save mosaic
print(f"\nSaving mosaic to: {MOSAIC_OUTPUT}")
with rasterio.open(MOSAIC_OUTPUT, "w", **out_meta) as dest:
    dest.write(mosaic)

print("✓ Mosaic saved successfully!")

# Close all source files
for src in src_files:
    src.close()

# ============================================
# STEP 3: Load shapefile and reproject if needed
# ============================================

print("\n" + "="*60)
print("Step 3: Loading and preparing shapefile...")
print("="*60)

if not os.path.exists(SHAPEFILE_PATH):
    print(f"\nERROR: Shapefile not found at: {SHAPEFILE_PATH}")
    print("\nPlease update SHAPEFILE_PATH in the script.")
    print("Current setting:", SHAPEFILE_PATH)
    exit(1)

# Load shapefile
gdf = gpd.read_file(SHAPEFILE_PATH)
print(f"✓ Loaded shapefile")
print(f"  Shapefile CRS: {gdf.crs}")
print(f"  Number of features: {len(gdf)}")

# Open mosaic to check CRS
with rasterio.open(MOSAIC_OUTPUT) as src:
    mosaic_crs = src.crs
    print(f"  Mosaic CRS: {mosaic_crs}")
    
    # Reproject shapefile to match raster if needed
    if gdf.crs != mosaic_crs:
        print("\n  Reprojecting shapefile to match raster CRS...")
        gdf = gdf.to_crs(mosaic_crs)
        print("  ✓ Reprojection complete")
    else:
        print("  ✓ CRS already matches")

# ============================================
# STEP 4: Clip mosaic to shapefile boundary
# ============================================

print("\n" + "="*60)
print("Step 4: Clipping DEM to district boundary...")
print("="*60)

with rasterio.open(MOSAIC_OUTPUT) as src:
    # Clip raster with shapefile geometry
    print("  Performing clip operation...")
    out_image, out_transform = mask(
        src, 
        gdf.geometry, 
        crop=True,
        nodata=src.nodata if src.nodata is not None else -9999,
        all_touched=False
    )
    
    # Update metadata
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform,
        "compress": "lzw",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256
    })

# Save clipped raster
print(f"\n  Saving clipped DEM to: {CLIPPED_OUTPUT}")
with rasterio.open(CLIPPED_OUTPUT, "w", **out_meta) as dest:
    dest.write(out_image)

print("  ✓ Clipped DEM saved successfully!")

# ============================================
# STEP 5: Summary statistics and info
# ============================================

print("\n" + "="*60)
print("PROCESSING COMPLETE!")
print("="*60)

with rasterio.open(CLIPPED_OUTPUT) as src:
    data = src.read(1, masked=True)
    
    print(f"\n📁 Output File Information:")
    print(f"  File: {CLIPPED_OUTPUT}")
    print(f"  Size: {os.path.getsize(CLIPPED_OUTPUT) / (1024*1024):.2f} MB")
    print(f"\n📐 Raster Properties:")
    print(f"  Dimensions: {src.width} x {src.height} pixels")
    print(f"  Resolution: {src.res[0]:.2f} x {src.res[1]:.2f} meters")
    print(f"  CRS: {src.crs}")
    print(f"  Bounds:")
    print(f"    - West:  {src.bounds.left:.6f}")
    print(f"    - South: {src.bounds.bottom:.6f}")
    print(f"    - East:  {src.bounds.right:.6f}")
    print(f"    - North: {src.bounds.top:.6f}")
    
    print(f"\n📊 Elevation Statistics:")
    print(f"  Minimum: {np.min(data):.2f} m")
    print(f"  Maximum: {np.max(data):.2f} m")
    print(f"  Mean:    {np.mean(data):.2f} m")
    print(f"  Median:  {np.median(data):.2f} m")
    print(f"  Std Dev: {np.std(data):.2f} m")

print("\n" + "="*60)
print("✓ DEM is ready for hydrology analysis and AI/ML modeling!")
print("="*60)
print("\nNext steps:")
print("  1. Extract slope, aspect, curvature from DEM")
print("  2. Compute flow accumulation and drainage density")
print("  3. Combine with LULC, rainfall, and other feature layers")
print("  4. Use for groundwater recharge zone prediction")
