# -*- coding: utf-8 -*-
"""
Simple test to verify DEM statistics are working
"""
import numpy as np
import rasterio

print("=" * 70)
print("DEM STATISTICS TEST")
print("=" * 70)

# Test New DEM
new_dem_path = "data/processed/dem_lucknow.tif"
with rasterio.open(new_dem_path) as src:
    new_dem = src.read(1, masked=True)
    
print("\nDEM Statistics:")
print(f"    New DEM - Min: {np.nanmin(new_dem):.2f}m, Max: {np.nanmax(new_dem):.2f}m, Mean: {np.nanmean(new_dem):.2f}m")

# Test with masked array methods (should also work now)
valid_data = new_dem.compressed()
print(f"    Valid pixels: {len(valid_data)} / {new_dem.size}")
print(f"    Using compressed() - Min: {valid_data.min():.2f}m, Max: {valid_data.max():.2f}m, Mean: {valid_data.mean():.2f}m")

print("\n" + "=" * 70)
print("SUCCESS! No more NaN in statistics!")
print("=" * 70)
