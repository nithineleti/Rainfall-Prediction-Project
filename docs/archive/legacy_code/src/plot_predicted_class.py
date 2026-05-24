# src/plot_predicted_class.py
import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

IN_CLASS = "data/processed/stage4/predicted_grp_class.tif"
IN_SCORE = "data/processed/stage4/predicted_grp_score.tif"
OUT_DIR = "data/processed/stage4/figs"
os.makedirs(OUT_DIR, exist_ok=True)

# color map for classes 0,1,2
cmap = ListedColormap(["#2b83ba", "#ffffbf", "#d7191c"])  # blue, yellow, red

def plot_class(inpath, outpng):
    with rasterio.open(inpath) as src:
        arr = src.read(1)
        nod = src.nodata
    mask = (arr == nod) | np.isnan(arr)
    disp = np.where(mask, np.nan, arr)
    plt.figure(figsize=(8,6))
    im = plt.imshow(disp, origin='upper', cmap=cmap, vmin=0, vmax=2)
    plt.title("Predicted GRP Class")
    cbar = plt.colorbar(im, ticks=[0,1,2])
    cbar.ax.set_yticklabels(['Low (0)','Moderate (1)','High (2)'])
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(outpng, dpi=200)
    plt.close()
    print("Saved:", outpng)

def plot_score(inpath, outpng):
    with rasterio.open(inpath) as src:
        arr = src.read(1)
        nod = src.nodata
    mask = np.isnan(arr) if nod is None else ((arr == nod) | np.isnan(arr))
    disp = np.where(mask, np.nan, arr)
    plt.figure(figsize=(8,6))
    im = plt.imshow(disp, origin='upper')
    plt.title("Predicted GRP Score")
    plt.colorbar(im)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(outpng, dpi=200)
    plt.close()
    print("Saved:", outpng)

plot_class(IN_CLASS, os.path.join(OUT_DIR, "predicted_grp_class_colored.png"))
plot_score(IN_SCORE, os.path.join(OUT_DIR, "predicted_grp_score.png"))
