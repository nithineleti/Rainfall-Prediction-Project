# src/plot_prediction.py
import rasterio
import matplotlib.pyplot as plt
import numpy as np
import os

score = "data/processed/stage4/predicted_grp_score.tif"
clazz = "data/processed/stage4/predicted_grp_class.tif"
outdir = "data/processed/stage4/figs"
os.makedirs(outdir, exist_ok=True)

def plot(path, outname, cmap=None):
    with rasterio.open(path) as src:
        arr = src.read(1)
        nod = src.nodata
    arr = np.where((arr==nod) | np.isnan(arr), np.nan, arr)
    plt.figure(figsize=(8,6))
    plt.imshow(arr, origin='upper')
    plt.colorbar()
    plt.title(os.path.basename(path))
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(outname, dpi=150)
    plt.close()
    print("Saved:", outname)

plot(score, os.path.join(outdir, "predicted_grp_score.png"))
plot(clazz, os.path.join(outdir, "predicted_grp_class.png"))
