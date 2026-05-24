# src/visualize.py
import matplotlib.pyplot as plt
import rasterio
import numpy as np
import os

PROC = "data/processed"
DEM = os.path.join(PROC, "dem_lucknow.tif")
HILL = os.path.join(PROC, "hillshade_lucknow.tif")
SLOPE = os.path.join(PROC, "slope_lucknow.tif")
GRP_CLASS = os.path.join(PROC, "grp_class_lucknow.tif")
OUT_DIR = "data/processed/figs"
os.makedirs(OUT_DIR, exist_ok=True)

def plot_raster(path, ax, title, cmap='viridis', vmin=None, vmax=None):
    with rasterio.open(path) as src:
        arr = src.read(1)
        # mask nodata
        arr = np.where(arr==src.nodata, np.nan, arr)
        im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(title)
        ax.axis('off')
        return im

fig, axes = plt.subplots(1,3, figsize=(18,6))
im1 = plot_raster(DEM, axes[0], "DEM (clipped)")
im2 = plot_raster(HILL, axes[1], "Hillshade", cmap='gray')
im3 = plot_raster(GRP_CLASS, axes[2], "GRP class (0 low,1 mod,2 high)", cmap='tab10', vmin=0, vmax=2)
fig.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)
fig.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)
fig.colorbar(im3, ax=axes[2], fraction=0.046, pad=0.04)
plt.tight_layout()
outpng = os.path.join(OUT_DIR, "pilot_maps.png")
plt.savefig(outpng, dpi=200)
print("Saved figure to", outpng)
plt.show()
