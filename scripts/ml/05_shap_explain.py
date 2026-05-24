# src/shap_explain.py
import joblib, pandas as pd, numpy as np, os
import shap
import matplotlib.pyplot as plt
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Generate SHAP explanations")
parser.add_argument('--model', default='models/rf_baseline.pkl', help='Path to trained model')
parser.add_argument('--samples', default='data/tables/train_samples.csv', help='Path to training samples')
parser.add_argument('--out', default='data/figures/shap_summary.png', help='Output path for SHAP plot')
parser.add_argument('--n_samples', type=int, default=500, help='Number of samples to use for SHAP')
args = parser.parse_args()

MODEL = args.model
SAMPLES = args.samples
OUT_FILE = args.out
os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)

clf = joblib.load(MODEL)
df = pd.read_csv(SAMPLES)

# Sample subset if requested
if args.n_samples < len(df):
    df = df.sample(n=args.n_samples, random_state=42)

feat_cols = [c for c in df.columns if c not in ('id','x','y','label','label_type')]
X = df[feat_cols].values

# Use interventional feature perturbation to avoid additivity errors with new DEM features
explainer = shap.TreeExplainer(clf, feature_perturbation='interventional')
shap_vals = explainer.shap_values(X, check_additivity=False)  # list for multi-class

# summary plot (for class 1 by default)
shap.summary_plot(shap_vals, X, feature_names=feat_cols, show=False)
plt.savefig(OUT_FILE, bbox_inches='tight', dpi=150)
plt.close()
print(f"Saved SHAP summary: {OUT_FILE}")
