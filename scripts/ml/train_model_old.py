#!/usr/bin/env python3
"""
src/train_model.py

Train a baseline RandomForest classifier with spatial block CV.

Outputs:
 - models/rf_baseline.pkl           (trained model on all data)
 - data/processed/stage4/cv_results.csv
 - data/processed/stage4/feature_importances.csv
 - data/processed/stage4/confusion_matrix.png
 - data/processed/stage4/classification_report.txt

Usage:
    python src/train_model.py --in data/processed/stage4/train_samples.csv --out_dir models --cv_k 5
"""
import os
import argparse
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (confusion_matrix, classification_report,
                             accuracy_score, balanced_accuracy_score)
from sklearn.cluster import KMeans
import joblib
import matplotlib.pyplot as plt

DEFAULT_OUT = "data/processed/stage4"
DEFAULT_MODEL_DIR = "models"
os.makedirs(DEFAULT_OUT, exist_ok=True)
os.makedirs(DEFAULT_MODEL_DIR, exist_ok=True)


def make_spatial_groups(coords_df, n_groups=5, random_state=42):
    """
    Create spatial groups using KMeans on coordinates.

    coords_df: DataFrame with columns ['x','y'] (or similar)
    returns: array of group ids (length = len(coords_df))
    """
    coords = coords_df[['x', 'y']].values
    if len(coords) < n_groups:
        # fallback: less samples than groups -> assign all zeros
        return np.zeros(len(coords), dtype=int)
    kmeans = KMeans(n_clusters=n_groups, random_state=random_state)
    groups = kmeans.fit_predict(coords)
    return groups


def safe_feature_columns(df, ignore_cols=None):
    if ignore_cols is None:
        ignore_cols = {'id', 'x', 'y', 'label', 'label_type', 'grp_score'}
    feat_cols = [c for c in df.columns if c not in ignore_cols]
    return feat_cols


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="infile", required=True, help="Input CSV with samples")
    p.add_argument("--out_dir", default=DEFAULT_MODEL_DIR, help="Directory to save models")
    p.add_argument("--cv_k", type=int, default=5, help="Number of spatial folds (GroupKFold)")
    p.add_argument("--n_estimators", type=int, default=200)
    p.add_argument("--random_state", type=int, default=42)
    p.add_argument("--target_col", default="label", help="Name of target column in CSV")
    args = p.parse_args()

    df = pd.read_csv(args.infile)
    if args.target_col not in df.columns:
        raise ValueError(f"Target column '{args.target_col}' not found in {args.infile}")

    # select feature columns
    feat_cols = safe_feature_columns(df)
    X = df[feat_cols].values
    y = df[args.target_col].values

    # drop rows with NaNs in features or labels
    mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
    if mask.sum() == 0:
        raise RuntimeError("No valid rows found after removing NaNs. Check input CSV.")
    X = X[mask]
    y = y[mask]
    coords = df[['x', 'y']].values[mask]

    # spatial grouping via KMeans
    groups = make_spatial_groups(pd.DataFrame(coords, columns=['x', 'y']), n_groups=args.cv_k, random_state=args.random_state)

    # GroupKFold
    gkf = GroupKFold(n_splits=args.cv_k)

    clf = RandomForestClassifier(n_estimators=args.n_estimators, n_jobs=-1, random_state=args.random_state)

    # Perform group CV and collect fold metrics + predictions
    fold = 0
    records = []
    y_pred_all = np.empty_like(y)
    y_pred_all[:] = -999
    for train_idx, test_idx in gkf.split(X, y, groups):
        fold += 1
        Xtr, ytr = X[train_idx], y[train_idx]
        Xte, yte = X[test_idx], y[test_idx]
        clf.fit(Xtr, ytr)
        yhat = clf.predict(Xte)
        y_pred_all[test_idx] = yhat
        acc = accuracy_score(yte, yhat)
        bal = balanced_accuracy_score(yte, yhat)
        print(f"Fold {fold}: train={len(train_idx)} test={len(test_idx)} acc={acc:.3f} bal_acc={bal:.3f}")
        records.append({
            "fold": fold,
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "accuracy": acc,
            "balanced_accuracy": bal
        })

    recdf = pd.DataFrame(records)
    recdf.to_csv(os.path.join(DEFAULT_OUT, "cv_results.csv"), index=False)
    print("Saved CV results:", os.path.join(DEFAULT_OUT, "cv_results.csv"))

    # Train final model on all data
    clf.fit(X, y)
    model_path = os.path.join(args.out_dir, "rf_baseline.pkl")
    joblib.dump(clf, model_path)
    print("Saved final model:", model_path)

    # Feature importances
    fi = clf.feature_importances_
    fi_df = pd.DataFrame({"feature": feat_cols, "importance": fi})
    fi_df = fi_df.sort_values("importance", ascending=False)
    fi_df.to_csv(os.path.join(DEFAULT_OUT, "feature_importances.csv"), index=False)
    print("Saved feature importances:", os.path.join(DEFAULT_OUT, "feature_importances.csv"))

    # Confusion matrix (aggregated from CV predictions)
    valid_mask_pred = (y_pred_all != -999)
    if valid_mask_pred.sum() == 0:
        print("Warning: No CV predictions collected; skipping confusion matrix.")
    else:
        cm = confusion_matrix(y[valid_mask_pred], y_pred_all[valid_mask_pred])
        plt.figure(figsize=(5, 5))
        plt.imshow(cm, interpolation="nearest", cmap="Blues")
        plt.title("Confusion matrix (CV aggregated)")
        plt.colorbar()
        plt.xlabel("Predicted")
        plt.ylabel("True")
        for (i, j), v in np.ndenumerate(cm):
            plt.text(j, i, int(v), ha="center", va="center", color="black")
        plt.tight_layout()
        cm_path = os.path.join(DEFAULT_OUT, "confusion_matrix.png")
        plt.savefig(cm_path, dpi=150)
        print("Saved confusion matrix:", cm_path)

    # classification report
    if valid_mask_pred.sum() > 0:
        report = classification_report(y[valid_mask_pred], y_pred_all[valid_mask_pred])
        with open(os.path.join(DEFAULT_OUT, "classification_report.txt"), "w") as fh:
            fh.write(report)
        print("Saved classification report:", os.path.join(DEFAULT_OUT, "classification_report.txt"))

    # Save CV summary (print)
    print("\nCV summary:")
    print(recdf)
    print("\nDone.")

if __name__ == "__main__":
    main()
