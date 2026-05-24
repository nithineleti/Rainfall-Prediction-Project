"""
Improved visualization for sparse features like streams
"""
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load feature stack
print("Loading feature stack...")
src = rasterio.open('data/processed/stage3/features_stack.tif')

# Band 7 = stream (0 or 1)
# Band 8 = drainage_density
stream = src.read(7)
drainage_density = src.read(8)
geology = src.read(4)  # Band 4 = geology

src.close()

# ===== STREAM VISUALIZATION =====
print("\nCreating improved stream visualization...")
fig, ax = plt.subplots(figsize=(10, 10))

# Create custom colormap: white for 0, blue for 1
cmap = mcolors.ListedColormap(['white', 'blue'])
bounds = [-0.5, 0.5, 1.5]
norm = mcolors.BoundaryNorm(bounds, cmap.N)

# Clean up stream data (handle float precision issues)
stream_clean = np.where(stream > 0.5, 1, 0)
stream_clean = np.where(np.isnan(stream), np.nan, stream_clean)

im = ax.imshow(stream_clean, cmap=cmap, norm=norm, interpolation='nearest')
ax.set_title(f'Stream Network\n({(stream_clean==1).sum()} stream pixels)', fontsize=14, fontweight='bold')
ax.axis('off')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='white', edgecolor='black', label='No Stream'),
    Patch(facecolor='blue', edgecolor='black', label='Stream')
]
ax.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.savefig('data/processed/stage3/figs/stream.png', dpi=150, bbox_inches='tight')
print(f"Saved: data/processed/stage3/figs/stream.png")
print(f"  Stream pixels: {(stream_clean==1).sum()}")
plt.close()

# ===== DRAINAGE DENSITY VISUALIZATION =====
print("\nCreating improved drainage density visualization...")
fig, ax = plt.subplots(figsize=(10, 10))

# Mask NaN values
dd_masked = np.ma.masked_invalid(drainage_density)

im = ax.imshow(dd_masked, cmap='Blues', interpolation='nearest', vmin=0, vmax=1.1)
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Drainage Density (km/km²)', fontsize=12)
ax.set_title(f'Drainage Density\n(0.0 - {np.nanmax(drainage_density):.2f} km/km²)', 
             fontsize=14, fontweight='bold')
ax.axis('off')

plt.tight_layout()
plt.savefig('data/processed/stage3/figs/drainage_density.png', dpi=150, bbox_inches='tight')
print(f"Saved: data/processed/stage3/figs/drainage_density.png")
print(f"  DD Min: {np.nanmin(drainage_density):.6f}, Max: {np.nanmax(drainage_density):.6f}")
plt.close()

# ===== GEOLOGY VISUALIZATION =====
print("\nCreating geology visualization...")
fig, ax = plt.subplots(figsize=(10, 10))

# Clean geology data
geology_clean = np.where(geology == 0, np.nan, geology)
geology_masked = np.ma.masked_invalid(geology_clean)

unique_geo = np.unique(geology_masked.compressed())
print(f"  Unique geology values: {unique_geo}")

im = ax.imshow(geology_masked, cmap='Set3', interpolation='nearest')
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Geology Class', fontsize=12)
ax.set_title(f'Geology\n({len(unique_geo)} unique class{"es" if len(unique_geo) > 1 else ""})', 
             fontsize=14, fontweight='bold')
ax.axis('off')

if len(unique_geo) == 1:
    ax.text(0.5, 0.95, 'Note: Study area has uniform geology (single class)', 
            transform=ax.transAxes, ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
            fontsize=10)

plt.tight_layout()
plt.savefig('data/processed/stage3/figs/geology.png', dpi=150, bbox_inches='tight')
print(f"Saved: data/processed/stage3/figs/geology.png")
plt.close()

print("\nDone! All visualizations improved.")
print("\nSummary:")
print(f"  Stream pixels: {(stream_clean==1).sum()} / {stream_clean.size} ({100*(stream_clean==1).sum()/stream_clean.size:.3f}%)")
print(f"  Drainage density range: {np.nanmin(drainage_density):.6f} to {np.nanmax(drainage_density):.6f}")
print(f"  Geology classes: {len(unique_geo)}")
