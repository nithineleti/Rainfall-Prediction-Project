import os
os.environ['GDAL_DATA'] = r'C:\Users\PAVAN\anaconda3\envs\watershed-up\Library\share\gdal'

import geopandas as gpd
from rasterstats import zonal_stats

print("Starting watershed characterization test...")

# Load watersheds
ws_file = "data/processed/stage4/watershed_boundaries_lucknow.shp"
print(f"Loading: {ws_file}")

if not os.path.exists(ws_file):
    print(f"ERROR: File not found: {ws_file}")
else:
    gdf = gpd.read_file(ws_file)
    print(f"Loaded {len(gdf)} watersheds")
    print(f"Columns: {list(gdf.columns)}")
    
    # Test zonal stats on AHP scores
    ahp_file = "data/processed/grp_score_lucknow.tif"
    if os.path.exists(ahp_file):
        print(f"\nTesting zonal stats on: {ahp_file}")
        stats = zonal_stats(gdf.geometry, ahp_file, stats=['mean', 'std'], nodata=-9999)
        print(f"First 3 results: {stats[:3]}")
        print("SUCCESS!")
    else:
        print(f"AHP file not found: {ahp_file}")

print("\nTest complete!")
