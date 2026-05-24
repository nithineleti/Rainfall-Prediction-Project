# src/compare_with_ahp.py
import rasterio
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import pandas as pd

ml_class = "data/processed/stage4/predicted_grp_class.tif"
ahp_class = "data/processed/grp_class_lucknow.tif"   # original AHP class from stage2

with rasterio.open(ml_class) as s:
    ml = s.read(1)
    ml_nod = s.nodata
with rasterio.open(ahp_class) as s:
    ahp = s.read(1)
    ahp_nod = s.nodata

# mask to pixels where BOTH are valid
mask_ml = (ml != ml_nod) & (~np.isnan(ml))
mask_ahp = (ahp != ahp_nod) & (~np.isnan(ahp))
mask = mask_ml & mask_ahp

if mask.sum() == 0:
    print("No overlapping valid pixels between ML and AHP rasters.")
else:
    y_true = ahp[mask].ravel().astype(int)
    y_pred = ml[mask].ravel().astype(int)
    print("Pixels compared:", y_true.size)
    print("Confusion matrix:")
    cm = confusion_matrix(y_true, y_pred, labels=[0,1,2])
    print(cm)
    print("\nClassification report:")
    print(classification_report(y_true, y_pred, labels=[0,1,2]))
    # simple overall agreement
    agree = (y_true == y_pred).sum() / y_true.size
    print(f"\nOverall pixel agreement: {agree:.3f}")
    # save confusion matrix CSV
    pd.DataFrame(cm, index=["AHP_0","AHP_1","AHP_2"], columns=["ML_0","ML_1","ML_2"]).to_csv("data/processed/stage4/confusion_ml_vs_ahp.csv")
    print("Saved confusion matrix CSV to data/processed/stage4/confusion_ml_vs_ahp.csv")
