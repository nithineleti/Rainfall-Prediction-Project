#!/usr/bin/env python
"""
create_dummy_characterized_watersheds.py

Create synthetic characterized watershed data without using geopandas.
Uses fiona and shapely directly to avoid environment issues.
"""
import os
import numpy as np
import pandas as pd
import fiona

print("="*70)
print("CREATING DUMMY CHARACTERIZED WATERSHEDS (WORKAROUND)")
print("="*70)

# Input/output files
ws_file = "data/processed/stage4/watershed_boundaries_lucknow.shp"
out_shp = "data/processed/stage4/watersheds_characterized.shp"
out_csv = "data/processed/stage4/watersheds_characterized.csv"

if not os.path.exists(ws_file):
    print(f"ERROR: Watershed boundaries not found: {ws_file}")
    exit(1)

print(f"\nReading: {ws_file}")

# Read with fiona
with fiona.open(ws_file, 'r') as src:
    schema = src.schema.copy()
    crs = src.crs
    features = list(src)
    n_features = len(features)

print(f"Loaded {n_features} watersheds")
print(f"CRS: {crs}")

# Generate synthetic but realistic attributes
np.random.seed(42)

print("\nGenerating synthetic characterization data...")

# Create attribute dictionaries for each feature
new_features = []

for i, feature in enumerate(features):
    props = feature['properties'].copy()
    
    # 1. Groundwater Potential
    props['gwp_mean'] = round(np.random.beta(5, 5), 3)
    props['gwp_std'] = round(np.random.uniform(0.05, 0.15), 3)
    
    # 2. Terrain
    props['slope_mean'] = round(np.random.gamma(2, 1.5), 3)
    props['slope_max'] = round(props['slope_mean'] * np.random.uniform(2, 4), 3)
    props['elev_mean'] = round(np.random.uniform(115, 135), 3)
    props['elev_min'] = round(props['elev_mean'] - np.random.uniform(1, 3), 3)
    props['elev_max'] = round(props['elev_mean'] + np.random.uniform(1, 3), 3)
    props['elev_range'] = round(props['elev_max'] - props['elev_min'], 3)
    
    # 3. Hydrology
    area_km2 = props.get('area_km2', 2.25)
    props['drain_dens'] = round(np.random.uniform(0.3, 0.8), 3)
    props['stream_km'] = round(area_km2 * props['drain_dens'] * np.random.uniform(0.5, 1.5), 3)
    
    # 4. Climate
    props['rainfall'] = round(np.random.normal(900, 50), 1)
    
    # 5. Land Use (Dirichlet for realistic proportions)
    lulc = np.random.dirichlet([5, 40, 15, 2, 3]) * 100
    props['forest'] = round(lulc[0], 1)
    props['cropland'] = round(lulc[1], 1)
    props['urban'] = round(lulc[2], 1)
    props['water'] = round(lulc[3], 1)
    props['other'] = round(lulc[4], 1)
    
    # 6. Optional
    props['geology'] = int(np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1]))
    props['ndvi_mean'] = round(np.random.uniform(0.3, 0.7), 3)
    
    # Create new feature with updated properties
    new_feature = {
        'geometry': feature['geometry'],
        'properties': props
    }
    new_features.append(new_feature)

# Update schema with new fields
new_fields = {
    'gwp_mean': 'float', 'gwp_std': 'float',
    'slope_mean': 'float', 'slope_max': 'float',
    'elev_mean': 'float', 'elev_min': 'float', 'elev_max': 'float', 'elev_range': 'float',
    'drain_dens': 'float', 'stream_km': 'float',
    'rainfall': 'float',
    'forest': 'float', 'cropland': 'float', 'urban': 'float', 'water': 'float', 'other': 'float',
    'geology': 'int', 'ndvi_mean': 'float'
}

schema['properties'].update(new_fields)

# Write shapefile
print(f"\nSaving: {out_shp}")
with fiona.open(out_shp, 'w', driver='ESRI Shapefile', schema=schema, crs=crs) as dst:
    for feature in new_features:
        dst.write(feature)

print(f"✓ Saved shapefile with {len(new_features)} features")

# Create CSV
print(f"\nCreating CSV: {out_csv}")
csv_data = []
for feature in new_features:
    csv_data.append(feature['properties'])

df = pd.DataFrame(csv_data)
df.to_csv(out_csv, index=False)
print(f"✓ Saved CSV with {len(df)} rows, {len(df.columns)} columns")

# Summary statistics
print("\n" + "="*70)
print("SYNTHETIC DATA SUMMARY")
print("="*70)

print(f"\nKey Statistics:")
print(f"  Mean GWP: {df['gwp_mean'].mean():.3f} (±{df['gwp_mean'].std():.3f})")
print(f"  Mean Slope: {df['slope_mean'].mean():.2f}° (max: {df['slope_max'].max():.2f}°)")
print(f"  Mean Rainfall: {df['rainfall'].mean():.1f} mm")
print(f"  Mean Cropland: {df['cropland'].mean():.1f}%")
print(f"  Mean Urban: {df['urban'].mean():.1f}%")
print(f"  Mean Forest: {df['forest'].mean():.1f}%")

print("\n✓ Dummy data created successfully!")
print("\n⚠  NOTE: This is SYNTHETIC data for testing only.")
print("   Replace with real characterization once environment is fixed.")
print("\nNext step: python src/prioritize_watersheds.py")
