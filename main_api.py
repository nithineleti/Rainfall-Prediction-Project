import os
import sys
import logging
import joblib
import pandas as pd
import numpy as np
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root and src to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.config_utils import load_config
from src.features import add_temporal_features, add_wind_features, add_thermo_features, apply_scaler

app = FastAPI(title="UP Weather Intelligence API")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration and models
cfg = load_config("configs/config.yaml")
MODELS_DIR = PROJECT_ROOT / "models"

try:
    clf = joblib.load(MODELS_DIR / "classifier_xgb.pkl")
    reg = joblib.load(MODELS_DIR / "regressor_lgbm.pkl")
    scaler_clf = joblib.load(MODELS_DIR / "scaler.pkl")
    scaler_reg = joblib.load(MODELS_DIR / "scaler_reg.pkl")
    print("✅ Models and scalers loaded successfully.")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    clf = reg = scaler_clf = scaler_reg = None

# District coordinates mapping
try:
    coords_df = pd.read_csv(PROJECT_ROOT / "data/raw/district_coordinates.csv")
    DISTRICT_COORDS = {row['district'].lower(): (row['latitude'], row['longitude']) for _, row in coords_df.iterrows()}
except Exception:
    DISTRICT_COORDS = {}

class WeatherData(BaseModel):
    temperature_2m: float
    relative_humidity_2m: float
    dew_point_2m: float
    shortwave_radiation: float
    wind_speed_10m: float
    wind_direction_10m: float
    surface_pressure: float
    cloud_cover: float
    precipitation: float

@app.get("/")
async def root():
    return {"message": "API is online"}

@app.get("/ping")
async def ping():
    return {"status": "online", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/weather/current")
async def get_weather_current_alias(district_id: str, lat: float = None, lng: float = None):
    return await get_live_weather(district_id, lat, lng)

class PredictRequest(BaseModel):
    district_id: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_vector_x: Optional[float] = None
    wind_vector_y: Optional[float] = None
    lag_1_rain: Optional[float] = None
    lag_3_rain: Optional[float] = None
    lag_7_rain: Optional[float] = None

@app.post("/api/v1/predict")
async def predict_alias(request: PredictRequest):
    # Support both formats: with lat/lng or with weather features
    lat = request.lat or 26.8467
    lng = request.lng or 80.9462
    return await predict(request.district_id, lat, lng)

def calculate_specific_humidity(t2m, rh2m, sp_pa):
    """
    Calculate specific humidity (g/kg) given temperature, RH, and surface pressure.
    """
    # Magnu-Tetens approximation for saturation vapor pressure
    es = 6.112 * np.exp((17.67 * t2m) / (t2m + 243.5))
    # Actual vapor pressure
    e = (rh2m / 100.0) * es
    # Mixing ratio
    w = 0.622 * e / (sp_pa / 100.0 - e)
    # Specific humidity
    q = w / (1 + w)
    return round(float(q * 1000), 2)  # Convert to g/kg

@app.get("/live-weather")
async def get_live_weather(district_id: str, lat: float = None, lng: float = None):
    # If lat/lng not provided, try to look up from district_id
    if lat is None or lng is None:
        coords = DISTRICT_COORDS.get(district_id.lower())
        if coords:
            lat, lng = coords
        else:
            # Default to Lucknow if not found
            lat, lng = 26.8467, 80.9462
            
    # Fetch live data from Open-Meteo using async httpx
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,cloud_cover,surface_pressure,wind_speed_10m,wind_direction_10m,shortwave_radiation,dew_point_2m&timezone=auto"
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise Exception(f"Open-Meteo API returned error {response.status_code}")
        
            data = response.json()
            current = data.get("current", {})
            
            # Extract variables
            t2m = float(current.get("temperature_2m") or 0)
            rh = float(current.get("relative_humidity_2m") or 0)
            sp_hpa = float(current.get("surface_pressure") or 1013.25)
            
            # Calculate specific humidity accurately
            q_gkg = calculate_specific_humidity(t2m, rh, sp_hpa * 100)
            
            # Calculate wind vectors (Meteorology convention)
            ws = float(current.get("wind_speed_10m", 0) or 0)
            wd = float(current.get("wind_direction_10m", 0) or 0)
            # In meteorology: u is from West (positive X), v is from South (positive Y)
            # Note: Open-Meteo wind direction is "coming from"
            u = -ws * np.sin(np.radians(wd))
            v = -ws * np.cos(np.radians(wd))
            
            return {
                "districtId": district_id,
                "temperatureC": t2m,
                "relativeHumidity": rh,
                "specificHumidity": q_gkg,
                "dewPointC": float(current.get("dew_point_2m") or 0),
                "shortwaveRadiation": float(current.get("shortwave_radiation") or 0),
                "windSpeedMs": ws / 3.6 if ws else 0,
                "windDirectionDeg": float(wd or 0),
                "windVectorX": float(u),
                "windVectorY": float(v),
                "precipitation": float(current.get("precipitation") or 0),
                "cloudCover": float(current.get("cloud_cover") or 0),
                "pressureHpa": float(current.get("surface_pressure") or 1013.25),
                "apparentTempC": float(current.get("apparent_temperature") or 0),
                "observationTime": str(current.get("time", datetime.now().isoformat()))
            }
    except Exception as e:
        print(f"Weather API error: {e}")
        # Return fallback data instead of error
        return {
            "districtId": district_id,
            "temperatureC": 25.0,
            "relativeHumidity": 60,
            "specificHumidity": 11.0,
            "dewPointC": 15.0,
            "shortwaveRadiation": 150.0,
            "windSpeedMs": 2.5,
            "windDirectionDeg": 180,
            "windVectorX": 0.0,
            "windVectorY": -2.5,
            "precipitation": 0.0,
            "cloudCover": 30,
            "pressureHpa": 1013.25,
            "apparentTempC": 24.0,
            "observationTime": datetime.now().isoformat()
        }

@app.get("/api/v1/weather/forecast")
async def get_weather_forecast_alias(district_id: str, lat: float = None, lng: float = None):
    # Fetch forecast data from Open-Meteo
    if lat is None or lng is None:
        coords = DISTRICT_COORDS.get(district_id.lower())
        if coords:
            lat, lng = coords
        else:
            lat, lng = 26.8467, 80.9462

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=precipitation_probability,precipitation,temperature_2m&timezone=auto"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            data = response.json()
            hourly = data.get("hourly", {})
            times = hourly.get("time", [])[:24]
            probs = hourly.get("precipitation_probability", [])[:24]
            precips = hourly.get("precipitation", [])[:24]
            temps = hourly.get("temperature_2m", [])[:24]

            forecast = []
            for i in range(len(times)):
                forecast.append({
                    "time": times[i],
                    "precipProbability": probs[i],
                    "rainfallMm": precips[i],
                    "tempC": temps[i]
                })
            return forecast
    except Exception as e:
        return []

@app.get("/api/v1/districts")
async def get_districts():
    # Return list of districts from the coordinates file
    try:
        districts = []
        for district, coords in DISTRICT_COORDS.items():
            districts.append({
                "id": district.upper(),
                "name": district.capitalize(),
                "lat": coords[0],
                "lng": coords[1]
            })
        return districts
    except Exception:
        return []

@app.get("/predict")
async def predict(district_id: str, lat: float, lng: float):
    """
    Get rainfall prediction for a district using live weather data.
    
    Features are engineered from Open-Meteo API response to match the training data format
    used by the dual-stage (classification + regression) ML models.
    """
    try:
        # 1. Get live weather data from Open-Meteo
        live_data = await get_live_weather(district_id, lat, lng)
        
        # 2. Extract and convert weather variables to match training feature names
        t2m = live_data.get('temperatureC', 20)           # Temperature 2m (°C)
        d2m = live_data.get('dewPointC', 10)              # Dewpoint 2m (°C)
        rh2m = live_data.get('relativeHumidity', 60)      # Relative humidity 2m (%)
        wind_speed = live_data.get('windSpeed', 3)        # Wind speed (m/s)
        wind_direction = live_data.get('windDirection', 180)  # Wind direction (°)
        precipitation = live_data.get('precipitation', 0)  # Current precipitation (mm)
        pressure = live_data.get('pressureHPa', 1013)     # Surface pressure (hPa)
        
        # 3. Compute wind components (u10, v10) from speed and direction
        # Wind direction in meteorology: 0°=N, 90°=E, 180°=S, 270°=W
        wind_dir_rad = np.radians(wind_direction)
        u10 = wind_speed * np.sin(wind_dir_rad)          # East-West component
        v10 = wind_speed * np.cos(wind_dir_rad)          # North-South component
        
        # 4. Generate temporal features
        now = datetime.now()
        month = now.month
        day_of_year = now.timetuple().tm_yday
        
        # Circular encoding for month (handles 12→1 continuity)
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        
        # Season encoding based on Indian monsoon calendar
        if month in [12, 1, 2]:
            season_encoded = 0       # Winter
        elif month in [3, 4, 5]:
            season_encoded = 1       # Spring/Pre-monsoon
        elif month in [6, 7, 8, 9]:
            season_encoded = 3       # Monsoon (peak rainfall season)
        else:  # Oct, Nov
            season_encoded = 4       # Post-monsoon
        
        # 5. Compute wind speed and direction features
        wind_speed_10m = np.sqrt(u10**2 + v10**2)
        
        # Wind direction circular encoding
        wind_dir_sin = np.sin(wind_dir_rad)
        wind_dir_cos = np.cos(wind_dir_rad)
        
        # WD10M (from NASA) and WD50M - assume same direction (rough simplification)
        wd10m_sin = wind_dir_sin
        wd10m_cos = wind_dir_cos
        wd50m_sin = wind_dir_sin
        wd50m_cos = wind_dir_cos
        
        # 6. Compute thermodynamic features
        tdd = max(t2m - d2m, 0.1)  # Temperature-Dewpoint Depression (prevents div by zero)
        humidity_stress = rh2m / max(tdd, 0.1)  # Humidity stress index
        
        # 7. Precipitation lag features (critical for monsoon patterns)
        # Since we only have current reading, use it as proxy for recent history
        # These are typically computed from time-series data, but we approximate here
        precip_lag_1d = precipitation
        precip_lag_3d = precipitation * 0.5  # Decay model: older precip ~50% of current
        precip_lag_7d = precipitation * 0.3  # 7-day old precip ~30%
        precip_roll_7d = precipitation * 0.5  # 7-day rolling average (50% current + history)
        precip_roll_30d = precipitation * 0.3  # 30-day rolling average (heavier on history)
        
        # 8. Wind speed at 50m (estimate using power law: v = u(z/z₀)^α where α≈0.2)
        ws50m = wind_speed * ((50/10) ** 0.2)
        
        # 9. Rain streak (consecutive rainy days indicator for persistence)
        rain_streak = 1 if precipitation > 0.1 else 0
        
        # 10. Build comprehensive feature DataFrame matching config.yaml specification
        input_df = pd.DataFrame([{
            # ERA5 features (atmospheric reanalysis)
            't2m': t2m,
            'd2m': d2m,
            'u10': u10,
            'v10': v10,
            'sp': pressure * 100,  # Convert hPa to Pa for ERA5 compatibility
            
            # NASA POWER features (satellite/reanalysis)
            'RH2M': rh2m,
            'WS10M': wind_speed,
            'WS50M': ws50m,
            'WD10M': wind_direction,
            'WD50M': wind_direction,
            
            # Spatial features
            'latitude': lat,
            'longitude': lng,
            
            # Engineered features (computed from raw data)
            'month_sin': month_sin,
            'month_cos': month_cos,
            'season_encoded': season_encoded,
            'wind_speed_10m': wind_speed_10m,
            'wind_dir_sin': wind_dir_sin,
            'wind_dir_cos': wind_dir_cos,
            'wd10m_sin': wd10m_sin,
            'wd10m_cos': wd10m_cos,
            'wd50m_sin': wd50m_sin,
            'wd50m_cos': wd50m_cos,
            'tdd': tdd,
            'humidity_stress': humidity_stress,
            'precip_lag_1d': precip_lag_1d,
            'precip_lag_3d': precip_lag_3d,
            'precip_lag_7d': precip_lag_7d,
            'precip_roll_7d': precip_roll_7d,
            'precip_roll_30d': precip_roll_30d,
            'day_of_year': day_of_year,
            'rain_streak': rain_streak,
        }])
        
        # Reorder columns to match exactly what the scaler was trained with
        feature_order = [
            't2m', 'd2m', 'sp', 'u10', 'v10', 'RH2M', 'WS10M', 'WS50M', 
            'latitude', 'longitude', 'month_sin', 'month_cos', 'season_encoded', 
            'wind_speed_10m', 'wind_dir_sin', 'wind_dir_cos', 'wd10m_sin', 'wd10m_cos', 
            'wd50m_sin', 'wd50m_cos', 'tdd', 'humidity_stress', 'precip_lag_1d', 
            'precip_lag_3d', 'precip_lag_7d', 'precip_roll_7d', 'precip_roll_30d', 
            'day_of_year', 'rain_streak'
        ]
        
        # Ensure all required columns exist (even if 0) and are in the correct order
        for col in feature_order:
            if col not in input_df.columns:
                input_df[col] = 0.0
                
        input_df = input_df[feature_order]
        
        threat_pct = 0.0
        rainfall_mm = 0.0
        error_msg = None
        
        # 11. Classification stage (rain vs no-rain threat percentage)
        if clf is not None and scaler_clf is not None:
            try:
                scaled_input = scaler_clf.transform(input_df)
                threat_proba = clf.predict_proba(scaled_input)
                # Get probability of rain class (index 1 = rain, index 0 = no-rain)
                threat_pct = float(threat_proba[0][1] * 100) if threat_proba.shape[1] > 1 else 0.0
            except Exception as e:
                print(f"❌ Classifier error: {str(e)}")
                error_msg = f"Classifier error: {str(e)}"
                threat_pct = 0.0
        
        # 12. Regression stage (rainfall amount in mm)
        if reg is not None and scaler_reg is not None:
            try:
                scaled_input = scaler_reg.transform(input_df)
                rainfall_pred = reg.predict(scaled_input)
                rainfall_mm = max(float(rainfall_pred[0]), 0) if rainfall_pred[0] is not None else 0.0
            except Exception as e:
                print(f"❌ Regressor error: {str(e)}")
                if not error_msg:
                    error_msg = f"Regressor error: {str(e)}"
                rainfall_mm = 0.0
        
        return {
            "district_id": district_id,
            "latitude": lat,
            "longitude": lng,
            "threat_pct": round(threat_pct, 2),
            "rainfall_mm": round(rainfall_mm, 2),
            "will_rain": threat_pct > 50,
            "weather": live_data,
            "error": error_msg
        }
    
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        return {
            "district_id": district_id,
            "threat_pct": 0,
            "rainfall_mm": 0,
            "will_rain": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
