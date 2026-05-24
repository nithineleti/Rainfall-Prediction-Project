"""
Fix slope calculation by properly handling NoData values (-9999)

The current slope_lucknow.tif has unrealistic values (~89°) because
the DEM contains -9999 NoData values that weren't masked during
gradient calculation. This creates massive elevation changes.

This script:
1. Reads DEM and properly masks NoData (-9999)
2. Recalculates slope in degrees
3. Overwrites slope_lucknow.tif with corrected values
"""
import os
import numpy as np
import rasterio

DEM_FILE = "data/processed/dem_lucknow.tif"
SLOPE_FILE = "data/processed/slope_lucknow.tif"

print("🔧 Fixing slope calculation...")

# Read DEM
with rasterio.open(DEM_FILE) as src:
    arr = src.read(1)
    transform = src.transform
    profile = src.profile.copy()
    nodata = src.nodata
    
print(f"  DEM NoData value: {nodata}")

# Create proper mask (exclude NoData)
if nodata is not None:
    mask = (arr != nodata) & np.isfinite(arr)
else:
    mask = np.isfinite(arr)

# Replace NoData with NaN for gradient calculation
arr_clean = np.where(mask, arr, np.nan)

# Get pixel size in degrees
xres_deg = abs(transform.a)
yres_deg = abs(transform.e)

# Convert to meters (critical fix!)
# At Lucknow (26.8°N):
# - 1° longitude ≈ 111320 * cos(26.8°) ≈ 99,450 m
# - 1° latitude ≈ 111320 m
import math
lat = 26.8  # Lucknow latitude
meters_per_deg_lon = 111320 * math.cos(math.radians(lat))
meters_per_deg_lat = 111320

xres = xres_deg * meters_per_deg_lon  # Convert to meters
yres = yres_deg * meters_per_deg_lat  # Convert to meters

print(f"  Pixel size: {xres_deg:.6f}° × {yres_deg:.6f}° = {xres:.2f}m × {yres:.2f}m")
print(f"  Valid pixels: {mask.sum():,} / {mask.size:,} ({mask.sum()/mask.size*100:.1f}%)")
print(f"  DEM range: {arr_clean[mask].min():.2f} - {arr_clean[mask].max():.2f} m")

# Compute slope using moving window (handles NaN properly)
print("  Computing slope using moving window...")
from scipy.ndimage import generic_filter

def local_slope(window):
    """Calculate slope from 3x3 window (center pixel)"""
    # window is flattened: [TL, T, TR, L, C, R, BL, B, BR]
    if window.size != 9:
        return np.nan
    
    # Reshape to 3x3
    w = window.reshape(3, 3)
    
    # Check if center and neighbors are valid
    if not np.isfinite(w[1, 1]):  # center
        return np.nan
    
    # Use Horn's method (average of gradients)
    # dz/dx = ((TR + 2*R + BR) - (TL + 2*L + BL)) / (8 * xres)
    # dz/dy = ((BL + 2*B + BR) - (TL + 2*T + TR)) / (8 * yres)
    
    # Replace NaN with center value (smooths boundaries)
    w_filled = np.where(np.isfinite(w), w, w[1, 1])
    
    dz_dx = ((w_filled[0, 2] + 2*w_filled[1, 2] + w_filled[2, 2]) - 
             (w_filled[0, 0] + 2*w_filled[1, 0] + w_filled[2, 0])) / (8 * xres)
    
    dz_dy = ((w_filled[2, 0] + 2*w_filled[2, 1] + w_filled[2, 2]) - 
             (w_filled[0, 0] + 2*w_filled[0, 1] + w_filled[0, 2])) / (8 * yres)
    
    # Convert to degrees
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    return np.degrees(slope_rad)

# Apply to entire array
slope_deg = generic_filter(arr_clean, local_slope, size=3, mode='constant', cval=np.nan)

# Ensure mask is applied
slope_deg[~mask] = np.nan

# Statistics
valid_slope = slope_deg[mask]
print(f"\n📊 New Slope Statistics:")
print(f"  Min: {valid_slope.min():.2f}°")
print(f"  Max: {valid_slope.max():.2f}°")
print(f"  Mean: {valid_slope.mean():.2f}°")
print(f"  Median: {np.median(valid_slope):.2f}°")

# Distribution check
print(f"\n📈 Slope Distribution:")
ranges = [(0, 1), (1, 2), (2, 5), (5, 10), (10, 20)]
for low, high in ranges:
    count = np.sum((valid_slope >= low) & (valid_slope < high))
    pct = count / len(valid_slope) * 100
    print(f"  {low}-{high}°: {pct:.1f}%")
extreme = np.sum(valid_slope >= 20)
print(f"  ≥20°: {extreme/len(valid_slope)*100:.1f}%")

# Write corrected slope
profile.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=np.nan)

print(f"\n💾 Writing corrected slope to: {SLOPE_FILE}")
with rasterio.open(SLOPE_FILE, 'w', **profile) as dst:
    dst.write(slope_deg.astype('float32'), 1)

print("✅ Slope calculation fixed!")
print("\n📝 Next steps:")
print("  1. Re-run QGIS characterization: exec(open('qgis_characterize_watersheds.py').read())")
print("  2. Re-extract DBF: python extract_dbf_to_csv.py")
print("  3. Clean output: python clean_qgis_output.py")
print("  4. Prioritize: python src/prioritize_watersheds.py")
