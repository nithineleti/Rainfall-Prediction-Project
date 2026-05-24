"""
Visualize enhanced watershed features
"""
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

OUT_DIR = "data/processed/stage3/figs"

def load_raster(filepath):
    src = rasterio.open(filepath)
    data = src.read(1)
    src.close()
    return data

def clean_data(data, percentile_clip=99):
    """Remove outliers and NaN for better visualization"""
    data_clean = data.copy()
    data_clean = np.where(np.isinf(data_clean), np.nan, data_clean)
    
    # Clip extreme outliers
    if percentile_clip:
        valid = data_clean[~np.isnan(data_clean)]
        if len(valid) > 0:
            lower = np.percentile(valid, 100 - percentile_clip)
            upper = np.percentile(valid, percentile_clip)
            data_clean = np.clip(data_clean, lower, upper)
    
    return data_clean

print("Creating enhanced watershed feature visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

# 1. TWI - Topographic Wetness Index
ax = axes[0]
twi = load_raster('data/processed/stage3/twi_lucknow.tif')
twi_clean = clean_data(twi, percentile_clip=95)
im = ax.imshow(twi_clean, cmap='Blues', interpolation='nearest')
ax.set_title('Topographic Wetness Index (TWI)\nHigher = Water Accumulation Zones', 
             fontsize=12, fontweight='bold')
ax.axis('off')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# 2. Aspect
ax = axes[1]
aspect = load_raster('data/processed/stage3/aspect_lucknow.tif')
aspect_clean = np.where(aspect < 0, np.nan, aspect)  # Remove flat areas (-1)
im = ax.imshow(aspect_clean, cmap='twilight', vmin=0, vmax=360, interpolation='nearest')
ax.set_title('Slope Aspect\n(Direction: N=0°, E=90°, S=180°, W=270°)', 
             fontsize=12, fontweight='bold')
ax.axis('off')
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Degrees', rotation=270, labelpad=15)

# 3. Plan Curvature
ax = axes[2]
plan_curv = load_raster('data/processed/stage3/plan_curvature_lucknow.tif')
plan_curv_clean = clean_data(plan_curv, percentile_clip=99.5)
im = ax.imshow(plan_curv_clean, cmap='RdBu_r', interpolation='nearest')
ax.set_title('Plan Curvature\nNegative=Convergent (Valleys), Positive=Divergent (Ridges)', 
             fontsize=12, fontweight='bold')
ax.axis('off')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# 4. Profile Curvature
ax = axes[3]
prof_curv = load_raster('data/processed/stage3/profile_curvature_lucknow.tif')
prof_curv_clean = clean_data(prof_curv, percentile_clip=99.5)
im = ax.imshow(prof_curv_clean, cmap='RdBu_r', interpolation='nearest')
ax.set_title('Profile Curvature\nNegative=Concave (Erosion), Positive=Convex (Deposition)', 
             fontsize=12, fontweight='bold')
ax.axis('off')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# 5. TPI - Topographic Position Index
ax = axes[4]
tpi = load_raster('data/processed/stage3/tpi_lucknow.tif')
tpi_clean = clean_data(tpi, percentile_clip=98)
im = ax.imshow(tpi_clean, cmap='terrain', interpolation='nearest')
ax.set_title('Topographic Position Index (TPI)\nPositive=Ridges (Recharge), Negative=Valleys (Discharge)', 
             fontsize=12, fontweight='bold')
ax.axis('off')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# 6. Distance to Streams
ax = axes[5]
dist_stream = load_raster('data/processed/stage3/distance_to_stream_lucknow.tif')
dist_clean = clean_data(dist_stream, percentile_clip=None)
im = ax.imshow(dist_clean, cmap='YlGnBu_r', interpolation='nearest')
ax.set_title('Distance to Streams\nProximity to Surface Water Network', 
             fontsize=12, fontweight='bold')
ax.axis('off')
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Meters', rotation=270, labelpad=15)

plt.suptitle('Enhanced Watershed Features for Groundwater Prediction', 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.97])

outfile = f'{OUT_DIR}/enhanced_watershed_features.png'
plt.savefig(outfile, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {outfile}")
plt.close()

# Create individual high-quality visualizations
print("\nCreating individual feature visualizations...")

# TWI detailed
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
im = ax.imshow(twi_clean, cmap='Blues', interpolation='nearest')
ax.set_title('Topographic Wetness Index (TWI)\nWater Accumulation Potential', 
             fontsize=14, fontweight='bold', pad=20)
ax.axis('off')
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('TWI Value (Higher = More Water Accumulation)', rotation=270, labelpad=20)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/twi.png', dpi=150, bbox_inches='tight')
print(f"✓ Saved: {OUT_DIR}/twi.png")
plt.close()

# Distance to streams detailed
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
im = ax.imshow(dist_clean, cmap='YlGnBu_r', interpolation='nearest')
ax.set_title('Distance to Stream Network\nGroundwater-Surface Water Interaction Zone', 
             fontsize=14, fontweight='bold', pad=20)
ax.axis('off')
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Distance (meters)', rotation=270, labelpad=20)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/distance_to_stream.png', dpi=150, bbox_inches='tight')
print(f"✓ Saved: {OUT_DIR}/distance_to_stream.png")
plt.close()

print("\n" + "="*70)
print("VISUALIZATION COMPLETE!")
print("="*70)
print("""
Created visualizations showing:
1. TWI - Where water tends to accumulate (recharge zones)
2. Aspect - Directional effects on evapotranspiration
3. Plan Curvature - Flow convergence/divergence patterns
4. Profile Curvature - Flow acceleration/deceleration zones
5. TPI - Ridge/valley classification (recharge/discharge)
6. Distance to Streams - Surface water proximity

These features provide MUCH more spatial detail than uniform geology!
They capture the actual hydrological processes affecting groundwater.
""")
