#!/usr/bin/env python3
"""
src/predict_map.py

Robust predictor that maps a trained sklearn model across a feature stack GeoTIFF.

Behavior:
 - Tries to detect the feature column names used during training by reading:
     1) data/processed/stage4/train_samples_clean_nogrp.csv (preferred)
     2) features_stack_bands.csv (fallback)
 - Selects only the bands required by the model (by matching names).
 - Supports models with predict_proba and predict.
 - Writes:
     - predicted_grp_score.tif (float32, nodata=nan)
     - predicted_grp_class.tif (int8, nodata=-1)

Usage:
    python src/predict_map.py --stack data/processed/stage3/features_stack.tif \
        --model models/rf_baseline.pkl --out_dir data/processed/stage4
"""

import os
import sys
import joblib
import numpy as np
import rasterio
import argparse
import pandas as pd

DEFAULT_TRAIN_CSV = "data/processed/stage4/train_samples_clean_nogrp.csv"
DEFAULT_BANDCSV = "data/processed/stage3/features_stack_bands.csv"

def read_band_names_from_stack_csv(stack_csv):
    """Read band names CSV; accept either column 'band_name' or first column."""
    if not os.path.exists(stack_csv):
        return None
    try:
        df = pd.read_csv(stack_csv)
        if 'band_name' in df.columns:
            return df['band_name'].astype(str).tolist()
        else:
            # assume first column contains names
            return df.iloc[:, 0].astype(str).tolist()
    except Exception:
        return None

def read_feature_names_from_train_csv(train_csv):
    """Read feature column names used for training (exclude id,x,y,label,label_type)."""
    if not os.path.exists(train_csv):
        return None
    try:
        df = pd.read_csv(train_csv, nrows=2)
        exclude = {'id','x','y','label','label_type'}
        feat_cols = [c for c in df.columns if c not in exclude]
        # ensure deterministic order
        return feat_cols
    except Exception:
        return None

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stack", required=True, help="Path to features_stack.tif")
    p.add_argument("--model", required=True, help="Path to trained model .pkl")
    p.add_argument("--out_dir", default="data/processed/stage4", help="Output directory")
    p.add_argument("--train_csv", default=DEFAULT_TRAIN_CSV, help="Optional: training CSV to read feature names from")
    p.add_argument("--bands_csv", default=DEFAULT_BANDCSV, help="Optional: companion CSV with band names")
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    model = joblib.load(args.model)
    print(f"Loaded model: {args.model}")

    # Attempt to detect feature column names from training CSV first
    feat_names = None
    if args.train_csv and os.path.exists(args.train_csv):
        print("Trying to read feature names from training CSV:", args.train_csv)
        feat_names = read_feature_names_from_train_csv(args.train_csv)
        if feat_names:
            print("Detected feature names from train CSV:", feat_names)
    if feat_names is None:
        # fallback: try features_stack_bands.csv
        print("Trying to read band names from:", args.bands_csv)
        stack_band_names = read_band_names_from_stack_csv(args.bands_csv)
        if stack_band_names:
            print("Read band names from CSV. Example:", stack_band_names[:10])
            # as a fallback, use all band names
            feat_names = stack_band_names
        else:
            print("No band-name CSV found. Will attempt to use all bands from stack (order may mismatch).")
            feat_names = None  # handled later

    # Open stack and read
    with rasterio.open(args.stack) as src:
        profile = src.profile
        data = src.read().astype("float32")  # (bands, rows, cols)
        rows, cols = src.height, src.width
        n_bands = src.count
        print(f"Stack info: {cols}x{rows} pixels, {n_bands} bands, CRS={src.crs}")

        # read band names as fallback if not provided above and embedded
        if feat_names is None:
            # will use indices (all bands)
            stack_band_names = read_band_names_from_stack_csv(args.bands_csv) or [f"band_{i+1}" for i in range(n_bands)]
            feat_names = stack_band_names
            print("Using fallback band names:", feat_names[:10])

        # if feat_names length differs from stack bands, we'll try to match
        if len(feat_names) != n_bands:
            print(f"Feature-name count ({len(feat_names)}) != stack band count ({n_bands}).")
            # still proceed: assume the stack band names file aligns and we can map by name
        # Build a mapping: band_name -> band_index (0-based)
        stack_names = read_band_names_from_stack_csv(args.bands_csv)
        if stack_names and len(stack_names) == n_bands:
            bandname_to_idx = {name: i for i, name in enumerate(stack_names)}
            print("Mapping available from features_stack_bands.csv")
        else:
            # fallback: name by index band_1,...band_n
            bandname_to_idx = {f"band_{i+1}": i for i in range(n_bands)}
            # also include indices as string keys
            for i in range(n_bands):
                bandname_to_idx[str(i+1)] = i

        # Determine required band indices (in order) matching feat_names
        required_idx = []
        missing = []
        for fname in feat_names:
            # try exact match
            if fname in bandname_to_idx:
                required_idx.append(bandname_to_idx[fname])
            else:
                # try case-insensitive match
                matched = None
                for k in bandname_to_idx:
                    if k.lower() == str(fname).lower():
                        matched = bandname_to_idx[k]; break
                if matched is not None:
                    required_idx.append(matched)
                else:
                    missing.append(fname)

        if missing:
            print("Warning: could not map these requested feature names to stack bands:", missing)
            print("Proceeding by using all stack bands instead.")
            required_idx = list(range(n_bands))

        # Now build a data array using only required indices (preserve order)
        req_data = data[required_idx, :, :]  # shape (req_bands, rows, cols)
        req_bands = req_data.shape[0]
        print(f"Using {req_bands} bands for prediction (indices):", required_idx)

        # determine validity mask: prefer grp_score if present in feat_names, else any-finite
        grp_idx = None
        for i, nm in enumerate(feat_names):
            if isinstance(nm, str) and 'grp' in nm.lower() and 'score' in nm.lower():
                # map to corresponding required_idx position
                if i < len(required_idx):
                    grp_idx = i
                break
        if grp_idx is not None and 0 <= grp_idx < req_bands:
            mask = np.isfinite(req_data[grp_idx])
            print(f"Using feature '{feat_names[grp_idx]}' (req band index {grp_idx}) as validity mask")
        else:
            mask = np.any(np.isfinite(req_data), axis=0)
            print("Using ANY-finite-band mask (np.any).")

        n_valid = int(np.count_nonzero(mask))
        print(f"Valid pixels: {n_valid} / {rows*cols} ({100.0 * n_valid/(rows*cols):.2f}%)")

        if n_valid == 0:
            # print per-band finite counts for debug
            finite_counts = [int(np.count_nonzero(np.isfinite(req_data[i]))) for i in range(req_bands)]
            print("Per-band finite counts (selected bands):", finite_counts)
            raise RuntimeError("No valid pixels in selected stack bands. Abort.")

        # Flatten and select valid pixels
        flat = np.moveaxis(req_data, 0, -1).reshape(-1, req_bands)  # (rows*cols, req_bands)
        valid_idx_flat = np.where(mask.reshape(-1))[0]
        X_valid = flat[valid_idx_flat]

    # Now ensure the model accepts this number of features
    expected_n_features = None
    try:
        # for sklearn RandomForestClassifier
        expected_n_features = model.n_features_in_
    except Exception:
        expected_n_features = None

    if expected_n_features is not None and expected_n_features != X_valid.shape[1]:
        print(f"Model expects {expected_n_features} features but X has {X_valid.shape[1]}.")
        # Try to trim or pad X_valid:
        if X_valid.shape[1] > expected_n_features:
            print("Trimming X_valid to the first", expected_n_features, "columns.")
            X_valid = X_valid[:, :expected_n_features]
        else:
            # pad with zeros
            pad_cols = expected_n_features - X_valid.shape[1]
            print("Padding X_valid with", pad_cols, "zero-columns.")
            X_valid = np.hstack([X_valid, np.zeros((X_valid.shape[0], pad_cols), dtype=X_valid.dtype)])

    print("Running predictions on", X_valid.shape[0], "pixels with", X_valid.shape[1], "features each.")

    # Predict with model
    if hasattr(model, "predict_proba"):
        try:
            probs = model.predict_proba(X_valid)
            # If multiclass, take max probability as "score"
            if probs.ndim == 2:
                scores = probs.max(axis=1).astype("float32")
            else:
                scores = probs[:, 1].astype("float32")
        except Exception:
            # fallback to predict numeric
            scores = model.predict(X_valid).astype("float32")
    else:
        scores = model.predict(X_valid).astype("float32")

    preds = model.predict(X_valid).astype("int8")

    # Reconstruct rasters
    score_raster = np.full((rows * cols,), np.nan, dtype="float32")
    class_raster = np.full((rows * cols,), -1, dtype="int8")
    score_raster[valid_idx_flat] = scores
    class_raster[valid_idx_flat] = preds
    score_raster = score_raster.reshape((rows, cols))
    class_raster = class_raster.reshape((rows, cols))

    # Write outputs
    out_score = os.path.join(args.out_dir, "predicted_grp_score.tif")
    out_class = os.path.join(args.out_dir, "predicted_grp_class.tif")

    # score profile
    profile_score = {
        "driver": "GTiff",
        "height": rows,
        "width": cols,
        "count": 1,
        "dtype": "float32",
        "crs": None,
        "transform": None,
        "nodata": np.nan
    }
    # better to copy profile from stack
    with rasterio.open(args.stack) as src:
        profile_score = src.profile.copy()
        profile_score.update(dtype="float32", count=1, nodata=np.nan)

    with rasterio.open(out_score, "w", **profile_score) as dst:
        dst.write(score_raster.astype("float32"), 1)

    profile_class = profile_score.copy()
    profile_class.update(dtype="int8", nodata=-1)
    with rasterio.open(out_class, "w", **profile_class) as dst:
        dst.write(class_raster.astype("int8"), 1)

    print("Wrote:", out_score)
    print("Wrote:", out_class)
    print("Done.")

if __name__ == "__main__":
    main()
