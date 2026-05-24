"""
FastAPI backend template for your folder:

Dual-Stage-Rainfall-Prediction-Pipeline/
  main.py
  data/processed/merged_processed.csv
  data/raw/district_coordinates.csv
  data/splits/train.csv
  models/classifier_xgb.pkl
  models/regressor_lgbm.pkl
  models/scaler.pkl
  models/scaler_reg.pkl

Copy this file's contents into your VS Code project's main.py.
Then run:
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen
import json

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"

PROCESSED_CSV = DATA_DIR / "processed" / "merged_processed.csv"
COORDS_CSV = DATA_DIR / "raw" / "district_coordinates.csv"
TRAIN_CSV = DATA_DIR / "splits" / "train.csv"

CLASSIFIER_PATH = MODELS_DIR / "classifier_xgb.pkl"
REGRESSOR_PATH = MODELS_DIR / "regressor_lgbm.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
SCALER_REG_PATH = MODELS_DIR / "scaler_reg.pkl"


app = FastAPI(title="Dual-Stage Rainfall Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


classifier = joblib.load(CLASSIFIER_PATH)
regressor = joblib.load(REGRESSOR_PATH)
scaler = joblib.load(SCALER_PATH)
scaler_reg = joblib.load(SCALER_REG_PATH)

processed_df = pd.read_csv(PROCESSED_CSV) if PROCESSED_CSV.exists() else pd.DataFrame()
coords_df = pd.read_csv(COORDS_CSV) if COORDS_CSV.exists() else pd.DataFrame()
train_df = pd.read_csv(TRAIN_CSV) if TRAIN_CSV.exists() else processed_df.copy()


class PredictionRequest(BaseModel):
    district_id: str = Field(..., examples=["UP-50"])
    temperature_c: float
    humidity_pct: float
    wind_vector_x: float
    wind_vector_y: float
    lag_1_rain: float
    lag_3_rain: float
    lag_7_rain: float


def normalize_name(value: Any) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    if df.empty:
        return None
    normalized = {normalize_name(c): c for c in df.columns}
    for candidate in candidates:
        key = normalize_name(candidate)
        if key in normalized:
            return normalized[key]
    return None


def get_district_column(df: pd.DataFrame) -> Optional[str]:
    return find_column(df, ["district_id", "district", "district_name", "name"])


def latest_row_for_district(district_id: str, district_name: Optional[str] = None) -> Dict[str, Any]:
    if processed_df.empty:
        return {}
    district_col = get_district_column(processed_df)
    if not district_col:
        return processed_df.tail(1).to_dict("records")[0]

    lookup_values = [district_id]
    if district_name:
        lookup_values.append(district_name)

    subset = pd.DataFrame()
    for value in lookup_values:
        subset = processed_df[processed_df[district_col].astype(str).str.lower() == value.lower()]
        if not subset.empty:
            break
    if subset.empty:
        for value in lookup_values:
            subset = processed_df[processed_df[district_col].astype(str).str.lower().str.contains(value.lower(), na=False)]
            if not subset.empty:
                break
    if subset.empty:
        return {}
    return subset.tail(1).to_dict("records")[0]


def fetch_coordinate_weather(district_id: str, lat: float, lng: float) -> Dict[str, Any]:
    params = urlencode({
        "latitude": lat,
        "longitude": lng,
        "current": "temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,cloud_cover,surface_pressure,wind_speed_10m,wind_direction_10m,shortwave_radiation",
        "wind_speed_unit": "ms",
        "timezone": "Asia/Kolkata",
    })
    url = f"https://api.open-meteo.com/v1/forecast?{params}"
    with urlopen(url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    current = payload.get("current", {})

    temp = float(current.get("temperature_2m", 0.0))
    rh = float(current.get("relative_humidity_2m", 0.0))
    pressure = float(current.get("surface_pressure", 1013.25))
    wind_speed = float(current.get("wind_speed_10m", 0.0))
    wind_dir = float(current.get("wind_direction_10m", 0.0))
    rad = np.deg2rad(wind_dir)
    wind_x = round(float(-wind_speed * np.sin(rad)), 2)
    wind_y = round(float(-wind_speed * np.cos(rad)), 2)
    saturation = 6.112 * np.exp((17.67 * temp) / (temp + 243.5))
    vapor = (rh / 100.0) * saturation
    specific = round(float(((0.622 * vapor) / (pressure - 0.378 * vapor)) * 1000), 1)

    return {
        "districtId": district_id,
        "temperatureC": temp,
        "relativeHumidity": rh,
        "specificHumidity": specific,
        "dewPointC": float(current.get("dew_point_2m", temp - 3.0)),
        "shortwaveRadiation": float(current.get("shortwave_radiation", 0.0)),
        "windSpeedMs": wind_speed,
        "windDirectionDeg": wind_dir,
        "windVectorX": wind_x,
        "windVectorY": wind_y,
        "precipitation": float(current.get("precipitation", 0.0)),
        "cloudCover": float(current.get("cloud_cover", 0.0)),
        "pressureHpa": pressure,
        "apparentTempC": float(current.get("apparent_temperature", temp)),
        "observationTime": str(current.get("time", pd.Timestamp.now())),
    }


def feature_names_from_scaler_or_data() -> List[str]:
    # Best case: sklearn scaler stores training feature names.
    if hasattr(scaler, "feature_names_in_"):
        return list(scaler.feature_names_in_)

    # Fallback: infer numeric training columns and remove likely targets/meta columns.
    df = train_df if not train_df.empty else processed_df
    if df.empty:
        return []

    excluded = {
        "rain", "rainfall", "precipitation", "target", "will_rain",
        "rain_binary", "rain_class", "date", "time", "district", "district_id",
        "district_name", "name", "latitude", "longitude", "lat", "lon", "lng",
    }
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if normalize_name(c) not in excluded]

    expected = getattr(scaler, "n_features_in_", None)
    if expected and len(numeric_cols) >= expected:
        return numeric_cols[:expected]
    return numeric_cols


FEATURE_NAMES = feature_names_from_scaler_or_data()


def build_feature_frame(req: PredictionRequest) -> pd.DataFrame:
    row = latest_row_for_district(req.district_id)

    # Map frontend fields into common possible training-column names.
    updates = {
        "temperature_c": req.temperature_c,
        "temperature": req.temperature_c,
        "temp": req.temperature_c,
        "humidity_pct": req.humidity_pct,
        "humidity": req.humidity_pct,
        "relative_humidity": req.humidity_pct,
        "wind_vector_x": req.wind_vector_x,
        "wind_x": req.wind_vector_x,
        "u_wind": req.wind_vector_x,
        "wind_vector_y": req.wind_vector_y,
        "wind_y": req.wind_vector_y,
        "v_wind": req.wind_vector_y,
        "lag_1_rain": req.lag_1_rain,
        "rain_lag_1": req.lag_1_rain,
        "lag1_rain": req.lag_1_rain,
        "lag_3_rain": req.lag_3_rain,
        "rain_lag_3": req.lag_3_rain,
        "lag3_rain": req.lag_3_rain,
        "lag_7_rain": req.lag_7_rain,
        "rain_lag_7": req.lag_7_rain,
        "lag7_rain": req.lag_7_rain,
    }

    normalized_row = {normalize_name(k): v for k, v in row.items()}
    values: Dict[str, float] = {}
    for feature in FEATURE_NAMES:
        key = normalize_name(feature)
        if key in updates:
            values[feature] = float(updates[key])
        elif key in normalized_row and pd.notna(normalized_row[key]):
            values[feature] = float(normalized_row[key])
        else:
            values[feature] = 0.0

    return pd.DataFrame([values], columns=FEATURE_NAMES)


@app.get("/")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "models_loaded": True,
        "feature_count": len(FEATURE_NAMES),
        "features": FEATURE_NAMES,
    }


@app.get("/api/v1/districts")
def districts() -> List[Dict[str, Any]]:
    source = coords_df if not coords_df.empty else processed_df
    if source.empty:
        return []

    district_col = get_district_column(source)
    lat_col = find_column(source, ["lat", "latitude"])
    lng_col = find_column(source, ["lng", "lon", "longitude"])

    if not district_col:
        return []

    subset = source[[c for c in [district_col, lat_col, lng_col] if c]].drop_duplicates()
    records = []
    for idx, row in subset.iterrows():
        name = str(row[district_col])
        records.append({
            "district_id": name if name.upper().startswith("UP-") else f"UP-{idx + 1:02d}",
            "name": name,
            "lat": float(row[lat_col]) if lat_col and pd.notna(row[lat_col]) else None,
            "lng": float(row[lng_col]) if lng_col and pd.notna(row[lng_col]) else None,
        })
    return records


@app.get("/api/v1/weather/current")
def current_weather(
    district_id: str = Query(...),
    district_name: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
) -> Dict[str, Any]:
    if lat is not None and lng is not None:
        try:
            return fetch_coordinate_weather(district_id, lat, lng)
        except Exception:
            pass

    row = latest_row_for_district(district_id, district_name)
    if not row:
        raise HTTPException(status_code=404, detail="District data not found")

    def pick(candidates: List[str], default: float = 0.0) -> float:
        for c in candidates:
            key = normalize_name(c)
            for actual, val in row.items():
                if normalize_name(actual) == key and pd.notna(val):
                    return float(val)
        return default

    temp = pick(["temperature_c", "temperature", "temp", "t2m"], 30.0)
    rh = pick(["humidity_pct", "humidity", "relative_humidity", "rh"], 60.0)
    dew = pick(["dew_point_c", "dew_point", "dewpoint"], temp - 3.0)
    solar = pick(["solar_radiation", "shortwave_radiation", "solar_rad"], 0.0)
    wind_x = pick(["wind_vector_x", "wind_x", "u_wind"], 0.0)
    wind_y = pick(["wind_vector_y", "wind_y", "v_wind"], 0.0)
    precip = pick(["precipitation", "rainfall", "rain"], 0.0)

    return {
        "districtId": district_id,
        "temperatureC": temp,
        "relativeHumidity": rh,
        "specificHumidity": round(rh * 0.018, 2),
        "dewPointC": dew,
        "shortwaveRadiation": solar,
        "windSpeedMs": round(float(np.sqrt(wind_x ** 2 + wind_y ** 2)), 2),
        "windDirectionDeg": 0,
        "windVectorX": wind_x,
        "windVectorY": wind_y,
        "precipitation": precip,
        "cloudCover": pick(["cloud_cover", "cloud"], 0.0),
        "pressureHpa": pick(["pressure", "surface_pressure"], 1013.0),
        "apparentTempC": temp,
        "observationTime": str(row.get("date", row.get("time", pd.Timestamp.now()))),
    }


@app.get("/api/v1/weather/forecast")
def forecast(
    district_id: str = Query(...),
    district_name: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
) -> List[Dict[str, Any]]:
    row = latest_row_for_district(district_id, district_name)
    if not row:
        return []
    current = current_weather(district_id, district_name, lat, lng)
    base_prob = min(100, max(0, current["relativeHumidity"] - 25))
    return [
        {
            "time": f"{hour:02d}:00",
            "precipProbability": round(min(100, max(0, base_prob + np.sin(hour / 24 * 6.28) * 20)), 1),
            "rainfallMm": round(max(0, current["precipitation"] * (0.5 + hour / 48)), 2),
            "tempC": round(current["temperatureC"] + np.sin(hour / 24 * 6.28) * 2, 1),
        }
        for hour in range(24)
    ]


@app.post("/api/v1/predict")
def predict(req: PredictionRequest) -> Dict[str, Any]:
    if not FEATURE_NAMES:
        raise HTTPException(status_code=500, detail="Could not infer model feature names. Check scaler or training CSV.")

    X = build_feature_frame(req)

    expected = getattr(scaler, "n_features_in_", X.shape[1])
    if X.shape[1] != expected:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Feature count mismatch. Update feature_names_from_scaler_or_data() in main.py.",
                "expected": int(expected),
                "actual": int(X.shape[1]),
                "features_used": FEATURE_NAMES,
            },
        )

    X_scaled = scaler.transform(X)
    proba = classifier.predict_proba(X_scaled)[0]
    threat = float(proba[1] * 100)
    will_rain = threat > 50.0

    rain_mm = 0.0
    if will_rain:
        X_reg = scaler_reg.transform(X)
        pred = float(regressor.predict(X_reg)[0])
        rain_mm = max(0.0, float(np.expm1(pred)))

    return {
        "district_id": req.district_id,
        "classification_threat_pct": round(threat, 2),
        "will_rain": bool(will_rain),
        "predicted_rain_mm": round(rain_mm, 2),
        "features_used": FEATURE_NAMES,
    }
