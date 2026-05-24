import rasterio
import numpy as np

with rasterio.open('data/rasters/stream_network_lucknow.tif') as src:
    arr = src.read(1)
    
print('Stream raster stats:')
print(f'  Shape: {arr.shape}')
print(f'  Min: {np.nanmin(arr)}')
print(f'  Max: {np.nanmax(arr)}')
print(f'  Unique values: {np.unique(arr[~np.isnan(arr)])}')
print(f'  NaN count: {np.isnan(arr).sum()} ({100*np.isnan(arr).sum()/arr.size:.2f}%)')
print(f'  Valid pixels: {(~np.isnan(arr)).sum()} ({100*(~np.isnan(arr)).sum()/arr.size:.2f}%)')
print(f'  Stream pixels (value=1): {(arr == 1).sum()}')
print(f'  Non-stream pixels (value=0): {(arr == 0).sum()}')

print('\nInterpretation:')
print('  Stream raster is binary: 1=stream, 0=non-stream')
print('  NaN values indicate the raster has no-data regions')
print('  Most samples fall in non-stream areas (value=0) which get replaced with NaN during sample extraction')
