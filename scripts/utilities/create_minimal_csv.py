import pandas as pd
import numpy as np

print("Creating minimal characterized watersheds CSV for testing...")

# Generate 144 rows with required attributes
np.random.seed(42)
n = 144

data = {
    'watershed_id': range(1, n+1),
    'area_km2': [2.25] * n,
    'gwp_mean': np.random.beta(5, 5, n).round(3),
    'gwp_std': np.random.uniform(0.05, 0.15, n).round(3),
    'slope_mean': np.random.gamma(2, 1.5, n).round(3),
    'slope_max': (np.random.gamma(2, 1.5, n) * np.random.uniform(2, 4, n)).round(3),
    'elev_mean': np.random.uniform(115, 135, n).round(1),
    'drain_dens': np.random.uniform(0.3, 0.8, n).round(3),
    'stream_km': (2.25 * np.random.uniform(0.3, 0.8, n) * np.random.uniform(0.5, 1.5, n)).round(3),
    'rainfall': np.random.normal(900, 50, n).round(1),
}

# LULC percentages
lulc = np.random.dirichlet([5, 40, 15, 2, 3], n) * 100
data['forest'] = lulc[:, 0].round(1)
data['cropland'] = lulc[:, 1].round(1)
data['urban'] = lulc[:, 2].round(1)
data['water'] = lulc[:, 3].round(1)
data['other'] = lulc[:, 4].round(1)

# Centroids (approximate grid positions)
data['centroid_lon'] = np.tile(np.linspace(80.8, 81.1, 12), 12).round(4)
data['centroid_lat'] = np.repeat(np.linspace(26.7, 27.0, 12), 12).round(4)

df = pd.DataFrame(data)

# Save
out_csv = "data/processed/stage4/watersheds_characterized.csv"
df.to_csv(out_csv, index=False)

print(f"✓ Created: {out_csv}")
print(f"  Rows: {len(df)}")
print(f"  Columns: {len(df.columns)}")
print(f"\nSample data:")
print(df.head(3))
print(f"\nStatistics:")
print(f"  Mean GWP: {df['gwp_mean'].mean():.3f}")
print(f"  Mean Slope: {df['slope_mean'].mean():.2f}°")
print(f"  Mean Cropland: {df['cropland'].mean():.1f}%")
print("\n✓ Ready for prioritization!")
