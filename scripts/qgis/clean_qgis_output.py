# -*- coding: utf-8 -*-
"""
Clean and rename QGIS output columns
DBF format has 10-character field name limit, so QGIS truncated them
"""
import pandas as pd
import sys

# Set UTF-8 encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("Cleaning QGIS output...")

# Read the messy CSV
df = pd.read_csv("data/processed/stage4/watersheds_characterized.csv")

print(f"Original: {len(df)} rows, {len(df.columns)} columns")

# The real data is in the later columns (QGIS ran zonal stats multiple times)
# Based on output: gwp_mean_4, slope_me_4, elev_mea_4, etc. are the latest/correct ones

# Create clean DataFrame with properly named columns
clean_df = pd.DataFrame()

# Basic info (from original shapefile)
clean_df['watershed_id'] = df['watershed_']
clean_df['area_km2'] = df['area_km2']
clean_df['centroid_lon'] = df['centroid_l']
clean_df['centroid_lat'] = df['centroid_1']

# Real extracted data (latest iteration - suffix _6, _2 - CORRECTED SLOPE!)
clean_df['gwp_mean'] = df['gwp_mean_6']  # Latest GWP stats
clean_df['gwp_std'] = df['gwp_stde_2']    # GWP standard deviation
clean_df['slope_mean'] = df['slope_me_6']  # Latest slope mean (CORRECTED!)
clean_df['slope_max'] = df['slope_ma_6']    # Latest slope max (CORRECTED!)
clean_df['elev_mean'] = df['elev_mea_6']   # Latest elevation mean
clean_df['elev_min'] = df['elev_min_6']     # Latest elevation min
clean_df['elev_max'] = df['elev_max_6']     # Latest elevation max
clean_df['drain_dens'] = df['drain_me_2']   # Drainage density
clean_df['rainfall'] = df['rain_mea_2']     # Rainfall mean

# LULC percentages (these were assigned in script, not extracted)
clean_df['forest'] = df['forest']
clean_df['cropland'] = df['cropland']
clean_df['urban'] = df['urban']
clean_df['water'] = df['water']
clean_df['other'] = df['other']

# Calculate derived fields
clean_df['elev_range'] = clean_df['elev_max'] - clean_df['elev_min']

# Stream length (km) = drainage density (km/km²) × area (km²)
clean_df['stream_km'] = clean_df['drain_dens'] * clean_df['area_km2']

# Population proxy (urban + cropland weighted)
clean_df['population_score'] = (clean_df['urban'] * 3 + clean_df['cropland']) / 4

print(f"\nCleaned: {len(clean_df)} rows, {len(clean_df.columns)} columns")
print(f"\nColumns: {list(clean_df.columns)}")

# Save cleaned CSV
output_file = "data/processed/stage4/watersheds_characterized.csv"
clean_df.to_csv(output_file, index=False)
print(f"\n✓ Saved clean CSV: {output_file}")

# Show statistics
print("\n📊 Data Statistics:")
print(f"\n  GWP: mean={clean_df['gwp_mean'].mean():.3f}, std={clean_df['gwp_mean'].std():.3f}")
print(f"  Slope: mean={clean_df['slope_mean'].mean():.2f}°, max={clean_df['slope_max'].max():.2f}°")
print(f"  Elevation: mean={clean_df['elev_mean'].mean():.1f}m, range=[{clean_df['elev_min'].min():.1f}, {clean_df['elev_max'].max():.1f}]")
print(f"  Rainfall: mean={clean_df['rainfall'].mean():.1f} mm/year")
print(f"  Drainage: mean={clean_df['drain_dens'].mean():.3f} km/km²")

print(f"\n  LULC Percentages:")
print(f"    Forest: {clean_df['forest'].mean():.1f}%")
print(f"    Cropland: {clean_df['cropland'].mean():.1f}%")
print(f"    Urban: {clean_df['urban'].mean():.1f}%")
print(f"    Water: {clean_df['water'].mean():.1f}%")
print(f"    Other: {clean_df['other'].mean():.1f}%")

# Show first few rows
print("\nFirst 3 rows:")
print(clean_df.head(3))

print("\n✅ Ready for prioritization!")
print("   Next: python src/prioritize_watersheds.py")
