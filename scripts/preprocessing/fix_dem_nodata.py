"""
Fix DEM files by replacing NaN values with a proper NoData value
"""
import numpy as np
import rasterio
import os

def fix_dem_nodata(input_path, output_path=None, nodata_value=-9999):
    """
    Replace NaN values in DEM with a proper NoData value
    
    Args:
        input_path: Path to input DEM file
        output_path: Path to output file (if None, creates _fixed.tif)
        nodata_value: Value to use for NoData (default: -9999)
    """
    if output_path is None:
        # Write to a new file with _fixed suffix
        output_path = input_path.replace('.tif', '_fixed.tif')
    
    with rasterio.open(input_path) as src:
        data = src.read(1)
        profile = src.profile.copy()
        
        print(f"\nProcessing: {input_path}")
        print(f"  Original shape: {data.shape}")
        print(f"  Original dtype: {data.dtype}")
        print(f"  Original NoData: {src.nodata}")
        
        # Count NaN values
        nan_count = np.isnan(data).sum()
        total_pixels = data.size
        print(f"  NaN pixels: {nan_count} / {total_pixels} ({100*nan_count/total_pixels:.2f}%)")
        
        # Replace NaN with NoData value
        data_fixed = np.where(np.isnan(data), nodata_value, data)
        
        # Update profile
        profile.update(
            nodata=nodata_value,
            compress='lzw'
        )
        
        # Write fixed file
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(data_fixed, 1)
        
        print(f"✓ Fixed DEM saved to: {output_path}")
        print(f"  New NoData value: {nodata_value}")
        
        # Verify
        with rasterio.open(output_path) as check:
            check_data = check.read(1, masked=True)
            valid_data = check_data.compressed()
            if len(valid_data) > 0:
                print(f"  Valid data range: {valid_data.min():.2f} to {valid_data.max():.2f}")
                print(f"  Valid data mean: {valid_data.mean():.2f}")
            else:
                print("  WARNING: No valid data found!")


if __name__ == "__main__":
    print("=" * 70)
    print("FIX DEM NODATA VALUES")
    print("=" * 70)
    
    # Fix main DEM
    fix_dem_nodata("data/processed/dem_lucknow.tif")
    
    # Fix slope (likely has the same issue)
    if os.path.exists("data/processed/slope_lucknow.tif"):
        print()
        fix_dem_nodata("data/processed/slope_lucknow.tif")
    
    print("\n" + "=" * 70)
    print("DEM FILES FIXED!")
    print("=" * 70)
    print("\nFixed files have been created with '_fixed.tif' extension.")
    print("\nTo use these files, rename them to replace the originals:")
    print("  1. Delete or rename the original files")
    print("  2. Rename _fixed.tif files to remove the _fixed suffix")
