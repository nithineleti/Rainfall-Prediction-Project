import os
import sys
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Add bin/src to path for feature engineering utilities
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.config_utils import load_config
from src.features import add_temporal_features, add_wind_features, add_thermo_features, apply_scaler

from flask_cors import CORS
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Load configuration and models
cfg = load_config("configs/config.yaml")

# Fix for potential missing LightGBM or different XGBoost paths in config
model_clf_path = cfg["paths"]["model_clf"]
model_reg_path = cfg["paths"]["model_reg"]
scaler_clf_path = cfg["paths"]["scaler"]
scaler_reg_path = cfg["paths"]["scaler"].replace(".pkl", "_reg.pkl")

# Load only if files exist
if os.path.exists(model_clf_path):
    clf = joblib.load(model_clf_path)
else:
    clf = None

if os.path.exists(model_reg_path):
    reg = joblib.load(model_reg_path)
else:
    # Try LightGBM ensemble if XGB regressor is not found by exact name
    lgbm_path = model_reg_path.replace("xgb", "lgbm")
    if os.path.exists(lgbm_path):
        reg = joblib.load(lgbm_path)
    else:
        reg = None

scaler_clf = joblib.load(scaler_clf_path) if os.path.exists(scaler_clf_path) else None
scaler_reg = joblib.load(scaler_reg_path) if os.path.exists(scaler_reg_path) else None

@app.route('/predict', methods=['POST'])
def predict():
    """
    Expects JSON input with weather parameters.
    Example: {"t2m": 25, "d2m": 18, "sp": 1013, "u10": 2, "v10": -1, "RH2M": 80, ...}
    """
    try:
        data = request.get_json()
        df = pd.DataFrame([data])
        
        # 1. Feature Engineering (Apply same logic as training)
        df = add_temporal_features(df)
        df = add_wind_features(df)
        df = add_thermo_features(df)
        
        # 2. Select model features
        feat_cols = cfg["features"]["era5"] + cfg["features"]["nasa"] + cfg["features"]["spatial"] + cfg["features"]["engineered"]
        X = df[[c for c in feat_cols if c in df.columns]]
        
        # 3. Stage 1: Classification (Is it going to rain?)
        if clf and scaler_clf:
            X_sc_clf = apply_scaler(X, scaler_clf)
            is_rain = int(clf.predict(X_sc_clf)[0])
            rain_prob = float(clf.predict_proba(X_sc_clf)[0][1])
        else:
            return jsonify({"status": "error", "message": "Classification model not loaded"}), 500
        
        # 4. Stage 2: Regression (How much rain?)
        precip_mm = 0.0
        if is_rain:
            if reg and scaler_reg:
                X_sc_reg = apply_scaler(X, scaler_reg)
                log_precip = reg.predict(X_sc_reg)[0]
                precip_mm = float(np.expm1(log_precip))
            else:
                log.warning("Regression model not loaded, but rain predicted.")
            
        return jsonify({
            "status": "success",
            "prediction": {
                "will_rain": bool(is_rain),
                "probability": round(rain_prob, 2),
                "expected_amount_mm": round(precip_mm, 2)
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model_loaded": True})

if __name__ == '__main__':
    # Default port for development; can be connected to frontend
    app.run(host='0.0.0.0', port=5001, debug=True)
