#!/usr/bin/env python3
# src/clean_samples.py
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from path_config import TABLES_DIR

infile = os.path.join(str(TABLES_DIR), "train_samples.csv")
outfile = os.path.join(str(TABLES_DIR), "train_samples_clean.csv")
if len(sys.argv) > 1:
    infile = sys.argv[1]
if len(sys.argv) > 2:
    outfile = sys.argv[2]

if not os.path.exists(infile):
    print("Input not found:", infile); sys.exit(1)

df = pd.read_csv(infile)
print("Loaded:", infile, "shape:", df.shape)

# 1) Drop columns that are all-NaN
allnan_cols = [c for c in df.columns if df[c].isna().all()]
if allnan_cols:
    print("Dropping columns with all NaN:", allnan_cols)
    df = df.drop(columns=allnan_cols)
else:
    print("No all-NaN columns found.")

# 2) Identify label column (prefer 'label')
if 'label' not in df.columns:
    labels = [c for c in df.columns if c.lower() in ('target','class','y','label')]
    if labels:
        label_col = labels[0]
        print("Using label column:", label_col)
        df = df.rename(columns={label_col: 'label'})
    else:
        print("No label column found. Exiting.")
        sys.exit(1)
else:
    label_col = 'label'

# 3) Drop rows with missing labels
n_before = len(df)
df = df[df['label'].notna()].copy()
n_after = len(df)
print(f"Dropped {n_before-n_after} rows with missing label. Remaining rows: {n_after}")

if n_after == 0:
    print("No rows remain after dropping missing labels. Exiting.")
    sys.exit(1)

# 4) Identify feature columns (exclude id,x,y,label,label_type)
exclude = {'id','x','y','label','label_type'}
feat_cols = [c for c in df.columns if c not in exclude]
print("Feature columns detected (count):", len(feat_cols))

# 5) Ensure feature columns are numeric; coerce if needed
for c in feat_cols:
    if not np.issubdtype(df[c].dtype, np.number):
        print("Coercing to numeric:", c)
        df[c] = pd.to_numeric(df[c], errors='coerce')

# 6) Drop any columns that became entirely NaN after coercion
drop_after = [c for c in feat_cols if df[c].isna().all()]
if drop_after:
    print("Dropping features that are now all NaN after coercion:", drop_after)
    df = df.drop(columns=drop_after)
    feat_cols = [c for c in feat_cols if c not in drop_after]

# 7) Impute remaining NaNs in feature columns with median
nan_counts = df[feat_cols].isna().sum().sum()
print("Total NaN values in feature matrix before impute:", nan_counts)
for c in feat_cols:
    if df[c].isna().any():
        med = df[c].median(skipna=True)
        if np.isfinite(med):
            df[c] = df[c].fillna(med)
        else:
            # if median is NaN (all values NaN), drop column
            print("Dropping column with non-finite median:", c)
            df = df.drop(columns=[c])
            feat_cols.remove(c)

# 8) Final checks
print("Final shape:", df.shape)
print("Final NaN counts (should be 0):")
print(df.isna().sum().sort_values(ascending=False).head(10).to_string())

# 9) Save cleaned CSV
os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)
df.to_csv(outfile, index=False)
print("Wrote cleaned CSV ->", outfile)
