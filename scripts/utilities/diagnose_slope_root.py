"""
Diagnose slope raster values to understand the 89° anomaly.
"""
import rasterio
import numpy as np

# Read slope raster
print("Reading slope raster...")
with rasterio.open('data/processed/slope_lucknow.tif') as src:
    slope_data = src.read(1)
    
    # Filter valid data
    valid = slope_data[~np.isnan(slope_data)]
    
    print(f"\n📊 Slope Raster Statistics:")
    print(f"  Min: {valid.min():.2f}")
    print(f"  Max: {valid.max():.2f}")
    print(f"  Mean: {valid.mean():.2f}")
    print(f"  Median: {np.median(valid):.2f}")
    print(f"  Std Dev: {valid.std():.2f}")
    
    # Check percentiles
    print(f"\n📈 Percentiles:")
    print(f"  10th: {np.percentile(valid, 10):.2f}")
    print(f"  25th: {np.percentile(valid, 25):.2f}")
    print(f"  50th: {np.percentile(valid, 50):.2f}")
    print(f"  75th: {np.percentile(valid, 75):.2f}")
    print(f"  90th: {np.percentile(valid, 90):.2f}")
    
    # Histogram
    print(f"\n📊 Value Distribution:")
    ranges = [(0, 1), (1, 5), (5, 10), (10, 30), (30, 60), (60, 90)]
    for low, high in ranges:
        count = np.sum((valid >= low) & (valid < high))
        pct = count / len(valid) * 100
        print(f"  {low}-{high}°: {count:,} pixels ({pct:.1f}%)")
    
    # Check if values > 85°
    extreme = np.sum(valid > 85)
    print(f"\n⚠️  Values > 85°: {extreme:,} pixels ({extreme/len(valid)*100:.1f}%)")
    
    print(f"\n💡 Diagnosis:")
    if valid.mean() > 45:
        print("  ⚠️  ISSUE: Mean slope > 45° is unrealistic for flat terrain!")
        print("  Possible causes:")
        print("    - Slope calculated in percent, not degrees")
        print("    - Incorrect unit conversion")
        print("    - Raster interpretation error")
    else:
        print("  ✅ Slope values look reasonable")
