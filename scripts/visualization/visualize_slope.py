"""
Generate slope visualization PNG images
Shows corrected slope distribution and maps
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from matplotlib.colors import LinearSegmentedColormap

# Paths
SLOPE_FILE = "data/rasters/slope_lucknow.tif"
OUTPUT_DIR = "data/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📊 Generating slope visualization images...")

# Read slope raster
with rasterio.open(SLOPE_FILE) as src:
    slope_data = src.read(1)
    
    # Filter valid data
    valid_slope = slope_data[~np.isnan(slope_data)]
    
    print(f"\n✅ Slope Statistics (CORRECTED):")
    print(f"  Min: {valid_slope.min():.2f}°")
    print(f"  Max: {valid_slope.max():.2f}°")
    print(f"  Mean: {valid_slope.mean():.2f}°")
    print(f"  Median: {np.median(valid_slope):.2f}°")
    print(f"  Std Dev: {valid_slope.std():.2f}°")

# Create figure with 3 subplots
fig = plt.figure(figsize=(18, 6))

# ========================================
# 1. Slope Distribution Histogram
# ========================================
ax1 = plt.subplot(1, 3, 1)
plt.hist(valid_slope, bins=100, color='steelblue', edgecolor='black', alpha=0.7)
plt.axvline(valid_slope.mean(), color='red', linestyle='--', linewidth=2, 
            label=f'Mean: {valid_slope.mean():.2f}°')
plt.axvline(np.median(valid_slope), color='orange', linestyle='--', linewidth=2,
            label=f'Median: {np.median(valid_slope):.2f}°')
plt.xlabel('Slope (degrees)', fontsize=12, fontweight='bold')
plt.ylabel('Frequency', fontsize=12, fontweight='bold')
plt.title('Slope Distribution (CORRECTED)\nRealistic 1-2° for Flat Terrain!', 
          fontsize=14, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

# Add statistics text box
stats_text = f"""Statistics:
Min: {valid_slope.min():.2f}°
Max: {valid_slope.max():.2f}°
Mean: {valid_slope.mean():.2f}°
Median: {np.median(valid_slope):.2f}°

0-1°: {np.sum((valid_slope >= 0) & (valid_slope < 1)) / len(valid_slope) * 100:.1f}%
1-2°: {np.sum((valid_slope >= 1) & (valid_slope < 2)) / len(valid_slope) * 100:.1f}%
2-5°: {np.sum((valid_slope >= 2) & (valid_slope < 5)) / len(valid_slope) * 100:.1f}%
>5°: {np.sum(valid_slope >= 5) / len(valid_slope) * 100:.1f}%"""

plt.text(0.98, 0.97, stats_text, transform=ax1.transAxes,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
         fontsize=9, family='monospace')

# ========================================
# 2. Slope Map (Classified)
# ========================================
ax2 = plt.subplot(1, 3, 2)

# Create classified slope map
slope_classified = np.full_like(slope_data, np.nan)
slope_classified[~np.isnan(slope_data)] = 0  # Default

# Classify
slope_classified[(slope_data >= 0) & (slope_data < 1)] = 1   # Very Gentle
slope_classified[(slope_data >= 1) & (slope_data < 2)] = 2   # Gentle
slope_classified[(slope_data >= 2) & (slope_data < 5)] = 3   # Moderate
slope_classified[(slope_data >= 5) & (slope_data < 10)] = 4  # Steep
slope_classified[slope_data >= 10] = 5                       # Very Steep

# Custom colormap (green → yellow → red)
colors = ['#006400', '#90EE90', '#FFFF00', '#FFA500', '#FF0000']
cmap = LinearSegmentedColormap.from_list('slope', colors, N=5)

im2 = plt.imshow(slope_classified, cmap=cmap, vmin=1, vmax=5)
plt.colorbar(im2, ax=ax2, ticks=[1, 2, 3, 4, 5], 
             label='Slope Class',
             format=plt.FuncFormatter(lambda x, p: 
                   ['', 'Very Gentle\n(0-1°)', 'Gentle\n(1-2°)', 
                    'Moderate\n(2-5°)', 'Steep\n(5-10°)', 'Very Steep\n(>10°)'][int(x)]))
plt.title('Slope Classification Map\nLucknow District', fontsize=14, fontweight='bold')
plt.xlabel('Easting', fontsize=12)
plt.ylabel('Northing', fontsize=12)

# ========================================
# 3. Slope Map (Continuous)
# ========================================
ax3 = plt.subplot(1, 3, 3)

# Continuous slope map with terrain colormap
im3 = plt.imshow(slope_data, cmap='terrain', vmin=0, vmax=10)
cbar = plt.colorbar(im3, ax=ax3, label='Slope (degrees)')
plt.title('Continuous Slope Map\nCorrected Values (0-21°)', fontsize=14, fontweight='bold')
plt.xlabel('Easting', fontsize=12)
plt.ylabel('Northing', fontsize=12)

# Add annotation
plt.text(0.02, 0.98, 'CORRECTED!\nRealistic slope values\nfor flat Indo-Gangetic Plain', 
         transform=ax3.transAxes,
         verticalalignment='top', horizontalalignment='left',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9),
         fontsize=10, fontweight='bold')

# ========================================
# Save figure
# ========================================
plt.tight_layout()
output_file = os.path.join(OUTPUT_DIR, 'slope_corrected_visualization.png')
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✅ Saved: {output_file}")

plt.close()

# ========================================
# Create comparison figure (before/after concept)
# ========================================
fig2, axes = plt.subplots(1, 2, figsize=(14, 6))

# "Before" (simulated - just for visualization)
ax_before = axes[0]
ax_before.text(0.5, 0.5, 'BEFORE FIX\n\n❌ Mean: 89.72°\n❌ Nearly vertical!\n❌ Unrealistic', 
               transform=ax_before.transAxes,
               verticalalignment='center', horizontalalignment='center',
               fontsize=20, fontweight='bold', color='red',
               bbox=dict(boxstyle='round', facecolor='mistyrose', alpha=0.9))
ax_before.set_xlim(0, 1)
ax_before.set_ylim(0, 1)
ax_before.set_title('Slope Calculation ERROR', fontsize=16, fontweight='bold')
ax_before.axis('off')

# "After" (actual corrected values)
ax_after = axes[1]
ax_after.text(0.5, 0.5, f'AFTER FIX\n\n✅ Mean: {valid_slope.mean():.2f}°\n✅ Gentle slope\n✅ Realistic!', 
              transform=ax_after.transAxes,
              verticalalignment='center', horizontalalignment='center',
              fontsize=20, fontweight='bold', color='darkgreen',
              bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))
ax_after.set_xlim(0, 1)
ax_after.set_ylim(0, 1)
ax_after.set_title('Slope Calculation CORRECTED', fontsize=16, fontweight='bold')
ax_after.axis('off')

plt.suptitle('Slope Fix: Degree-to-Meter Conversion Applied', 
             fontsize=18, fontweight='bold', y=1.02)

output_file2 = os.path.join(OUTPUT_DIR, 'slope_before_after_fix.png')
plt.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Saved: {output_file2}")

plt.close()

# ========================================
# Create detailed distribution chart
# ========================================
fig3, ax = plt.subplots(figsize=(12, 8))

# Prepare distribution data
ranges = [
    ('0-1°\n(Very Flat)', 0, 1, 'darkgreen'),
    ('1-2°\n(Flat)', 1, 2, 'green'),
    ('2-5°\n(Gentle)', 2, 5, 'yellowgreen'),
    ('5-10°\n(Moderate)', 5, 10, 'orange'),
    ('10-20°\n(Steep)', 10, 20, 'orangered'),
    ('>20°\n(Very Steep)', 20, 100, 'red')
]

labels = []
values = []
colors_list = []

for label, low, high, color in ranges:
    count = np.sum((valid_slope >= low) & (valid_slope < high))
    pct = count / len(valid_slope) * 100
    labels.append(label)
    values.append(pct)
    colors_list.append(color)

# Create bar chart
bars = plt.bar(range(len(labels)), values, color=colors_list, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, values)):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.1f}%',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.xlabel('Slope Range', fontsize=14, fontweight='bold')
plt.ylabel('Percentage of Area (%)', fontsize=14, fontweight='bold')
plt.title('Slope Distribution by Class - Lucknow District\n(CORRECTED - Realistic Values)', 
          fontsize=16, fontweight='bold')
plt.xticks(range(len(labels)), labels, fontsize=11)
plt.grid(axis='y', alpha=0.3)
plt.ylim(0, max(values) * 1.2)

# Add summary box
summary_text = f"""✅ CORRECTED SLOPE
    
Mean: {valid_slope.mean():.2f}°
Median: {np.median(valid_slope):.2f}°
Std: {valid_slope.std():.2f}°

Flat terrain dominates
(0-2°: {np.sum((valid_slope >= 0) & (valid_slope < 2)) / len(valid_slope) * 100:.1f}%)

Appropriate for:
→ Percolation tanks
→ Farm ponds
→ Flat area interventions"""

plt.text(0.98, 0.97, summary_text, transform=ax.transAxes,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9),
         fontsize=11, family='monospace', fontweight='bold')

output_file3 = os.path.join(OUTPUT_DIR, 'slope_distribution_chart.png')
plt.savefig(output_file3, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Saved: {output_file3}")

plt.close()

print(f"\n🎨 All slope visualizations saved to: {OUTPUT_DIR}/")
print(f"\n📁 Generated files:")
print(f"  1. slope_corrected_visualization.png (3-panel: histogram + maps)")
print(f"  2. slope_before_after_fix.png (before/after comparison)")
print(f"  3. slope_distribution_chart.png (detailed distribution)")
print(f"\n✅ DONE! Open {OUTPUT_DIR}/ to view images.")
