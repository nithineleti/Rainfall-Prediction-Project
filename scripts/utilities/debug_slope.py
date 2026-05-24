"""
Debug slope calculation to understand why slopes are ~90°
"""
import numpy as np
import rasterio

DEM_FILE = "data/processed/dem_lucknow.tif"

print("Reading DEM...")
with rasterio.open(DEM_FILE) as src:
    arr = src.read(1)
    transform = src.transform
    nodata = src.nodata

# Mask NoData
mask = (arr != nodata) & np.isfinite(arr)
arr_clean = np.where(mask, arr, np.nan)

# Get pixel size in degrees
xres_deg = abs(transform.a)
yres_deg = abs(transform.e)

# Convert to meters (approx at 26°N latitude)
# At Lucknow (26.8°N): 1° longitude ≈ 111320 * cos(26.8°) ≈ 99,450 m
# 1° latitude ≈ 111320 m
import math
lat = 26.8
meters_per_deg_lon = 111320 * math.cos(math.radians(lat))
meters_per_deg_lat = 111320

xres_m = xres_deg * meters_per_deg_lon
yres_m = yres_deg * meters_per_deg_lat

print(f"\n📏 Resolution:")
print(f"  Degrees: {xres_deg:.6f}° × {yres_deg:.6f}°")
print(f"  Meters: {xres_m:.2f}m × {yres_m:.2f}m")

# Take a small sample where we have valid data
print(f"\n🔍 Sampling valid area...")
# Find first valid region (10x10 pixels)
valid_rows, valid_cols = np.where(mask)
if len(valid_rows) == 0:
    print("No valid data!")
    exit(1)

# Take middle region
mid_idx = len(valid_rows) // 2
center_r = valid_rows[mid_idx]
center_c = valid_cols[mid_idx]

# Extract 10x10 window
r_start = max(0, center_r - 5)
r_end = min(arr.shape[0], center_r + 5)
c_start = max(0, center_c - 5)
c_end = min(arr.shape[1], center_c + 5)

window = arr_clean[r_start:r_end, c_start:c_end]
print(f"\nWindow location: rows {r_start}-{r_end}, cols {c_start}-{c_end}")
print(f"Window elevation stats:")
print(f"  Min: {np.nanmin(window):.2f}m")
print(f"  Max: {np.nanmax(window):.2f}m")
print(f"  Range: {np.nanmax(window) - np.nanmin(window):.2f}m")
print(f"  Mean: {np.nanmean(window):.2f}m")

# Manual gradient calculation for center pixel
if window.shape[0] >= 3 and window.shape[1] >= 3:
    # Get 3x3 around center
    win3x3 = window[window.shape[0]//2-1:window.shape[0]//2+2, 
                    window.shape[1]//2-1:window.shape[1]//2+2]
    
    if win3x3.shape == (3, 3):
        print(f"\n3×3 window (elevations in m):")
        for i in range(3):
            print(f"  {win3x3[i,0]:6.2f}  {win3x3[i,1]:6.2f}  {win3x3[i,2]:6.2f}")
        
        # Horn's method
        dz_dx = ((win3x3[0, 2] + 2*win3x3[1, 2] + win3x3[2, 2]) - 
                 (win3x3[0, 0] + 2*win3x3[1, 0] + win3x3[2, 0])) / 8.0
        dz_dy = ((win3x3[2, 0] + 2*win3x3[2, 1] + win3x3[2, 2]) - 
                 (win3x3[0, 0] + 2*win3x3[0, 1] + win3x3[0, 2])) / 8.0
        
        print(f"\n📐 Gradient (in DEM units per pixel):")
        print(f"  dz/dx: {dz_dx:.4f} m/pixel")
        print(f"  dz/dy: {dz_dy:.4f} m/pixel")
        
        # Convert to slope
        # WRONG WAY (using degree units):
        slope_wrong_rad = np.arctan(np.sqrt((dz_dx/xres_deg)**2 + (dz_dy/yres_deg)**2))
        slope_wrong_deg = np.degrees(slope_wrong_rad)
        
        # RIGHT WAY (using meter units):
        slope_right_rad = np.arctan(np.sqrt((dz_dx/xres_m)**2 + (dz_dy/yres_m)**2))
        slope_right_deg = np.degrees(slope_right_rad)
        
        print(f"\n🎯 Slope calculation:")
        print(f"  If using degree units (WRONG): {slope_wrong_deg:.2f}°")
        print(f"  If using meter units (RIGHT): {slope_right_deg:.2f}°")
        
        print(f"\n💡 Diagnosis:")
        if slope_wrong_deg > 45:
            print("  ⚠️  The preprocess.py script is dividing by pixel size in DEGREES,")
            print("      not METERS! This creates huge slopes.")
            print(f"      Fix: Convert pixel size to meters first.")
            print(f"      xres_deg ({xres_deg:.6f}°) should be converted to")
            print(f"      xres_m ({xres_m:.2f}m) before calculating gradient.")
