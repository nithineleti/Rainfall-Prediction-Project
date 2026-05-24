# src/shap_explain.py
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import joblib, pandas as pd, numpy as np
import shap
import matplotlib.pyplot as plt
from path_config import MODELS_DIR, TABLES_DIR, FIGURES_DIR

MODEL = os.path.join(str(MODELS_DIR), "rf_baseline.pkl")
SAMPLES = os.path.join(str(TABLES_DIR), "train_samples_clean.csv")
OUT = str(FIGURES_DIR)
os.makedirs(OUT, exist_ok=True)

clf = joblib.load(MODEL)
df = pd.read_csv(SAMPLES)
# Exclude grp_score to avoid data leakage (it was used to create synthetic labels)
feat_cols = [c for c in df.columns if c not in ('id','x','y','label','label_type','grp_score')]
X = df[feat_cols].values

# Use interventional feature perturbation to avoid additivity errors with new DEM features
explainer = shap.TreeExplainer(clf, feature_perturbation='interventional')
shap_vals = explainer.shap_values(X, check_additivity=False)  # list for multi-class

# summary plot (for class 1 by default)
shap.summary_plot(shap_vals, X, feature_names=feat_cols, show=False)
plt.savefig(os.path.join(OUT,"shap_summary.png"), bbox_inches='tight', dpi=150)
plt.close()
print("Saved SHAP summary:", os.path.join(OUT,"shap_summary.png"))
