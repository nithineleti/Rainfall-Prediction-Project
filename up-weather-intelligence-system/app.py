# 🚀 COMPLETE INTEGRATION GUIDE
# Connect your VS Code backend with the React dashboard
# Match this guide EXACTLY with your file structure

## ============================================================
## PHASE 1: Create app.py in your project root
## ============================================================
## 
## Create a NEW file called `app.py` at the ROOT of your project
## (same level as `package.json`, `data/`, `models/`, `src/`)
##
## Copy the COMPLETE code from the code block below into `app.py`.
##
## IMPORTANT NOTES about YOUR specific project:
##   - Model files: models/classifier_xgb.pkl + models/regressor_lgbm.pkl
##   - Scalers: models/scaler.pkl + models/scaler_reg.pkl
##   - SQLite DB: data/weather_db.sqlite
##   - Features pipeline: src/features.py (your existing file)
##   - CORS: ENABLED for localhost:5173 (Vite dev server)
##
## ============================================================
## APP.PY CODE — COPY EVERYTHING BELOW THIS LINE
## ============================================================

"""
UP Rainfall Prediction — FastAPI Backend Server
Loads YOUR trained models from models/ directory
Serves predictions to React dashboard via REST API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sqlite3
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime

# ============================================================
# Initialize FastAPI App
# ============================================================
app = FastAPI(
    title="UP Rainfall Prediction API",
    description="End-to-end predictive weather intelligence for Uttar Pradesh",
    version="2.0.0"
)

# ============================================================
# CRITICAL: CORS Middleware — MUST be present for frontend!
# This allows your React dev server (Vite) to make requests
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev server
        "http://localhost:3000",    # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",                         # Allow all (for testing)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Paths — adjust if your file structure differs
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "weather_db.sqlite")

# ============================================================
# Load YOUR Pre-Trained Models & Scalers
# ============================================================
try:
    print("🔄 Loading pre-trained models...")
    
    # Classifier: XGBoost for Rain/No-Rain classification
    classifier_path = os.path.join(MODELS_DIR, "classifier_xgb.pkl")
    classifier = joblib.load(classifier_path)
    print(f"  ✅ Loaded classifier from {classifier_path}")
    
    # Regressor: LightGBM for rainfall volume estimation
    regressor_path = os.path.join(MODELS_DIR, "regressor_lgbm.pkl")
    regressor = joblib.load(regressor_path)
    print(f"  ✅ Loaded regressor from {regressor_path}")
    
    # Scalers — CRITICAL for proper predictions!
    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    scaler = joblib.load(scaler_path)
    print(f"  ✅ Loaded scaler from {scaler_path}")
    
    scaler_reg_path = os.path.join(MODELS_DIR, "scaler_reg.pkl")
    scaler_reg = joblib.load(scaler_reg_path)
    print(f"  ✅ Loaded regressor scaler from {scaler_reg_path}")
    
    print("✅ All models and scalers loaded successfully!")
    
except FileNotFoundError as e:
    print(f"❌ Model file not found: {e}")
    print("   Check that models/ directory contains:")
    print("   - classifier_xgb.pkl")
    print("   - regressor_lgbm.pkl")
    print("   - scaler.pkl")
    print("   - scaler_reg.pkl")
    classifier = None
    regressor = None
    scaler = None
    scaler_reg = None
except Exception as e:
    print(f"❌ Error loading models: {e}")
    classifier = None
    regressor = None
    scaler = None
    scaler_reg = None

# ============================================================
# Load your existing features.py module for feature engineering
# ============================================================
try:
    sys_path = os.path.join(BASE_DIR, "src")
    if sys_path not in __import__('sys').path:
        __import__('sys').path.insert(0, sys_path)
    from features import compute_features  # Adjust if your function name differs
    FEATURES_AVAILABLE = True
    print("✅ Loaded features.py for feature engineering")
except ImportError:
    FEATURES_AVAILABLE = False
    print("⚠️  features.py not found — using direct feature mapping")

# ============================================================
# Pydantic Request Model
# ============================================================
class WeatherInferenceRequest(BaseModel):
    district_id: str = Field(..., description="District code like UP-01 to UP-75")
    temperature_c: float = Field(..., ge=-10, le=55, description="Current temperature in °C")
    humidity_pct: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    wind_vector_x: float = Field(..., description="U-component of wind vector (m/s)")
    wind_vector_y: float = Field(..., description="V-component of wind vector (m/s)")
    lag_1_rain: float = Field(..., description="Rainfall 1 day ago (mm)")
    lag_3_rain: float = Field(..., description="Rainfall 3 days ago (mm)")
    lag_7_rain: float = Field(..., description="Rainfall 7 days ago (mm)")

class PredictionResponse(BaseModel):
    district_id: str
    classification_threat_pct: float
    will_rain: bool
    predicted_rain_mm: float
    model_source: str = "your_trained_models"
    timestamp: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# ============================================================
# Helper: Get historical features from SQLite
# ============================================================
def get_district_historical_features(district_id: str) -> Optional[Dict[str, float]]:
    """Fetch baseline features from your SQLite database."""
    try:
        if not os.path.exists(DB_PATH):
            return None
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Try common table names — adjust based on your schema
        for table in ["district_features", "features", "weather_data"]:
            try:
                cursor.execute(f"SELECT * FROM {table} WHERE district_id = ? LIMIT 1", (district_id,))
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    conn.close()
                    return result
            except sqlite3.OperationalError:
                continue
        conn.close()
        return None
    except Exception as e:
        print(f"DB query error: {e}")
        return None

# ============================================================
# Helper: Build feature array for model prediction
# ============================================================
def build_features(req: WeatherInferenceRequest, historical: Optional[Dict] = None) -> np.ndarray:
    """
    Build the feature array expected by YOUR trained models.
    
    IMPORTANT: The feature order MUST match what your models were trained on.
    Adjust the column order below based on your training notebooks:
    03_classification.ipynb and 04_regression.ipynb
    """
    features = {
        "temperature": req.temperature_c,
        "humidity": req.humidity_pct,
        "wind_x": req.wind_vector_x,
        "wind_y": req.wind_vector_y,
        "lag_1_rain": req.lag_1_rain,
        "lag_3_rain": req.lag_3_rain,
        "lag_7_rain": req.lag_7_rain,
    }
    
    # Add historical features if available
    if historical:
        for key, val in historical.items():
            if key not in features and isinstance(val, (int, float)):
                features[key] = val
    
    # Add solar radiation and dew point if available in historical data
    if historical:
        features.setdefault("solar_radiation", historical.get("solar_radiation", 20.0))
        features.setdefault("dew_point_spread", historical.get("dew_point_spread", 3.0))
    
    # 🔄 FEATURE ORDER — MATCH YOUR TRAINING DATA!
    # Change this order to match the columns your models were trained on.
    # Check your 03_classification.ipynb and 04_regression.ipynb to find the exact order.
    feature_order = [
        "temperature", "humidity", "wind_x", "wind_y",
        "lag_1_rain", "lag_3_rain", "lag_7_rain",
        "solar_radiation", "dew_point_spread"
    ]
    
    feature_array = np.array([[features.get(col, 0.0) for col in feature_order]])
    return feature_array

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint — used by frontend to verify connection."""
    return {
        "status": "healthy",
        "service": "UP Rainfall Prediction API",
        "version": "2.0.0",
        "models_loaded": classifier is not None and regressor is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/districts", tags=["Districts"])
async def get_all_districts():
    """
    Returns all 75 UP districts.
    Used by frontend for connection verification and district list.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try to get districts from your database
        # Adjust table/column names based on your actual schema
        cursor.execute("SELECT * FROM district_features")
        rows = cursor.fetchall()
        
        if not rows:
            # Fallback: return district IDs from JSON files
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            
        conn.close()
        return [dict(r) for r in rows]
        
    except sqlite3.OperationalError as e:
        # Fallback: return basic district list
        districts = []
        for i in range(1, 76):
            districts.append({
                "district_id": f"UP-{i:02d}",
                "name": f"District_{i}",
            })
        return districts

@app.post("/api/v1/predict", response_model=PredictionResponse, tags=["Prediction"])
async def run_predictive_inference(req: WeatherInferenceRequest):
    """
    MAIN PREDICTION ENDPOINT — Used by React dashboard.
    
    1. Receives live weather values from the frontend
    2. Fetches historical lags from SQLite
    3. Applies YOUR scalers
    4. Runs YOUR XGBoost classifier
    5. If rain predicted, runs YOUR LightGBM regressor
    6. Returns threat probability and rainfall volume
    
    Request body matches Pydantic schema above.
    """
    if classifier is None or regressor is None:
        raise HTTPException(
            status_code=500,
            detail="Models not loaded. Check server startup logs for errors."
        )
    
    try:
        # Step 1: Fetch historical features from your SQLite DB
        historical = get_district_historical_features(req.district_id)
        
        # Step 2: Build feature array (must match your training data order!)
        raw_features = build_features(req, historical)
        
        # Step 3: Apply scaling (CRITICAL — your models expect scaled features!)
        scaled_features = scaler.transform(raw_features)
        
        # Step 4: XGBoost Classification — Will it rain?
        proba = classifier.predict_proba(scaled_features)[0]
        # Assuming class 1 = rain, class 0 = no rain
        threat_pct = float(proba[1] * 100)  # Probability of rain
        will_rain = threat_pct > 50.0
        
        # Step 5: LightGBM Regression — How much rain?
        rain_mm = 0.0
        if will_rain:
            # Scale features for regressor (might need different scaler)
            scaled_features_reg = scaler_reg.transform(raw_features)
            log_pred = regressor.predict(scaled_features_reg)[0]
            # Inverse log-transform: exp(y) - 1
            rain_mm = float(np.expm1(log_pred))
        
        return PredictionResponse(
            district_id=req.district_id,
            classification_threat_pct=round(threat_pct, 2),
            will_rain=will_rain,
            predicted_rain_mm=round(rain_mm, 2),
            model_source="your_trained_models",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )

@app.post("/api/v1/predict/bulk", tags=["Prediction"])
async def bulk_predict(requests: List[WeatherInferenceRequest]):
    """Predict for multiple districts at once."""
    results = []
    for req in requests:
        try:
            historical = get_district_historical_features(req.district_id)
            raw_features = build_features(req, historical)
            scaled_features = scaler.transform(raw_features)
            
            proba = classifier.predict_proba(scaled_features)[0]
            threat_pct = float(proba[1] * 100)
            will_rain = threat_pct > 50.0
            
            rain_mm = 0.0
            if will_rain:
                scaled_features_reg = scaler_reg.transform(raw_features)
                log_pred = regressor.predict(scaled_features_reg)[0]
                rain_mm = float(np.expm1(log_pred))
            
            results.append({
                "district_id": req.district_id,
                "threat_pct": round(threat_pct, 2),
                "will_rain": will_rain,
                "rain_mm": round(rain_mm, 2),
            })
        except Exception as e:
            results.append({
                "district_id": req.district_id,
                "error": str(e)
            })
    return results

# ============================================================
# Startup message
# ============================================================
@app.on_event("startup")
async def startup_message():
    print("\n" + "=" * 60)
    print("🌧️ UP Rainfall Prediction API — Server Started!")
    print("=" * 60)
    print(f" Base URL: http://localhost:8000")
    print(f"📊 Docs: http://localhost:8000/docs")
    print(f"🔍 Health: http://localhost:8000/")
    print(f"📡 Predict: POST http://localhost:8000/api/v1/predict")
    print(f"🗄️  SQLite: {DB_PATH}")
    print(f"🤖 Classifier: models/classifier_xgb.pkl")
    print(f"🤖 Regressor: models/regressor_lgbm.pkl")
    print("=" * 60 + "\n")
