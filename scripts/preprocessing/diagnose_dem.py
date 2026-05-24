"""
Quick diagnostic to check DEM data issues
"""
import numpy as np
import rasterio

dem_path = "data/processed/dem_lucknow.tif"

print("=" * 70)
print("DEM DIAGNOSTIC")
print("=" * 70)

with rasterio.open(dem_path) as src:
    print(f"\nFile: {dem_path}")
    print(f"Driver: {src.driver}")
    print(f"Shape: {src.shape}")
    print(f"Dtype: {src.dtypes[0]}")
    print(f"NoData value: {src.nodata}")
    print(f"CRS: {src.crs}")
    print(f"Bounds: {src.bounds}")
    
    # Read data WITHOUT masking
    data_raw = src.read(1)
    print(f"\n--- Raw Data (unmasked) ---")
    print(f"Shape: {data_raw.shape}")
    print(f"Dtype: {data_raw.dtype}")
    print(f"Min: {np.min(data_raw)}")
    print(f"Max: {np.max(data_raw)}")
    print(f"Mean: {np.mean(data_raw)}")
    print(f"Contains NaN: {np.isnan(data_raw).any()}")
    print(f"Contains Inf: {np.isinf(data_raw).any()}")
    print(f"Unique values count: {len(np.unique(data_raw))}")
    
    # Count NoData values
    if src.nodata is not None:
        nodata_count = np.sum(data_raw == src.nodata)
        total_pixels = data_raw.size
        print(f"NoData pixels: {nodata_count} / {total_pixels} ({100*nodata_count/total_pixels:.2f}%)")
    
    # Read data WITH masking
    data_masked = src.read(1, masked=True)
    print(f"\n--- Masked Data ---")
    print(f"Type: {type(data_masked)}")
    print(f"All masked?: {data_masked.mask.all() if hasattr(data_masked, 'mask') else 'N/A'}")
    if hasattr(data_masked, 'mask'):
        masked_count = np.sum(data_masked.mask)
        print(f"Masked pixels: {masked_count} / {data_masked.size} ({100*masked_count/data_masked.size:.2f}%)")
    
    # Try to get stats
    try:
        print(f"Min (masked): {data_masked.min()}")
        print(f"Max (masked): {data_masked.max()}")
        print(f"Mean (masked): {data_masked.mean()}")
    except Exception as e:
        print(f"Error getting stats: {e}")
    
    # Sample some values
    print(f"\n--- Sample Values (first 10x10 corner) ---")
    print(data_raw[:10, :10])

print("\n" + "=" * 70)
