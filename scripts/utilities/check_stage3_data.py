import rasterio
import numpy as np
import os
from datetime import datetime

files = [
    'stream_network_lucknow.tif',
    'drainage_density_lucknow.tif', 
    'geology_lucknow.tif',
    'flow_acc_lucknow.tif'
]

base = 'data/processed/stage3'

print("=" * 60)
print("Stage 3 Raster Data Check")
print("=" * 60)

for f in files:
    path = os.path.join(base, f)
    if not os.path.exists(path):
        print(f"\n{f}: FILE NOT FOUND")
        continue
        
    src = rasterio.open(path)
    data = src.read(1)
    
    # Get valid data (non-NaN)
    if np.isnan(data).any():
        valid = data[~np.isnan(data)]
    else:
        valid = data.flatten()
    
    # Get modification time
    mod_time = datetime.fromtimestamp(os.path.getmtime(path))
    
    print(f"\n{f}:")
    print(f"  Shape: {data.shape}")
    print(f"  Total pixels: {data.size}")
    print(f"  Valid pixels: {len(valid)}")
    print(f"  Unique values: {len(np.unique(valid))}")
    
    unique_vals = np.unique(valid)
    if len(unique_vals) <= 10:
        print(f"  Values: {unique_vals}")
    else:
        print(f"  Values (first 10): {unique_vals[:10]}")
        print(f"  Values (last 10): {unique_vals[-10:]}")
    
    print(f"  Min: {valid.min():.6f}, Max: {valid.max():.6f}")
    print(f"  Mean: {valid.mean():.6f}")
    print(f"  Modified: {mod_time}")
    
    src.close()

print("\n" + "=" * 60)
