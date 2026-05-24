# 🔌 CONNECT FRONTEND TO YOUR VS CODE BACKEND
# Tailored for YOUR exact file structure

## ============================================================
## YOUR FILE STRUCTURE (confirmed from screenshots):
## ============================================================
## 
## rainfall_prediction_project/
## ├── .venv/                      ← Your Python virtual environment
## ├── configs/config.yaml         ← Your project config
## ├── data/
## │   ├── processed/              ← Processed data
## │   ├── raw/                    ← CSV files
## │   ├── splits/                 ← Train/test splits
## │   ├── india_districts.json
## │   ├── up_districts.json
## │   └── weather_db.sqlite       ← YOUR SQLite database
## ├── models/
## │   ├── classifier_xgb.pkl      ← YOUR XGBoost classifier
## │   ├── regressor_lgbm.pkl      ← YOUR LightGBM regressor
## │   ├── regressor_xgb.pkl
## │   ├── scaler.pkl              ← YOUR scaler (IMPORTANT!)
## │   └── scaler_reg.pkl          ← YOUR regressor scaler
## ├── src/
## │   ├── features.py             ← YOUR feature engineering
## │   ├── preprocess.py
## │   ├── train_classifier.py
## │   ├── train_regressor.py
## │   ├── evaluate.py
## │   └── visualize.py
## ├── notebooks/
## │   ├── 01_eda.ipynb
## │   ├── 02_preprocessing.ipynb
## │   ├── 03_classification.ipynb
## │   ├── 04_regression.ipynb
## │   └── 05_visualizations.ipynb
## ├── outputs/                    ← Plots, reports, metrics
## ├── app.py                      ← CREATE THIS FILE (provided)
## ├── requirements.txt
## └── (frontend dashboard folder) ← The React app I built

## ============================================================
## STEP-BY-STEP CONNECTION PROCESS
## ============================================================

---

## STEP 1: Create app.py in Your Project Root

**Location:** Place `app.py` at the ROOT of your `rainfall_prediction_project/` folder
(same level as `data/`, `models/`, `src/`, `notebooks/`)

The complete `app.py` code was provided in the previous message.
**Copy the entire code block and save it as `app.py`**.

### What this app.py does:
- ✅ Loads YOUR `models/classifier_xgb.pkl`
- ✅ Loads YOUR `models/regressor_lgbm.pkl`
- ✅ Loads YOUR `models/scaler.pkl` and `models/scaler_reg.pkl`
- ✅ Reads from YOUR `data/weather_db.sqlite`
- ✅ Imports YOUR `src/features.py` if available
- ✅ Enables CORS for React frontend
- ✅ Exposes `GET /api/v1/districts` and `POST /api/v1/predict`

---

## STEP 2: Verify Your SQLite Database Schema

**IMPORTANT:** The `app.py` queries your SQLite database for district features.
You need to verify the table/column names match.

### Check your SQLite schema:
Open a Python terminal in VS Code and run:

```python
import sqlite3
conn = sqlite3.connect("data/weather_db.sqlite")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

# For each table, list columns
for table in tables:
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f"\nTable '{table[0]}' columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

conn.close()
```

### Adjust app.py if needed:
If your table name is NOT `district_features`, find this section in `app.py`
and change the table name:

```python
# In app.py, search for these lines and update:
cursor.execute("SELECT * FROM YOUR_TABLE_NAME WHERE district_id = ? LIMIT 1", (district_id,))
```

---

## STEP 3: Verify Feature Order (CRITICAL!)

Your models were trained with a specific feature order. The `app.py` MUST
use the EXACT same order when making predictions.

### Check your training notebooks:
Open `notebooks/03_classification.ipynb` and `notebooks/04_regression.ipynb`

Look for where you define `X` (features) and check the column order:

```python
# Example of what you might see:
feature_columns = [
    "temperature", "humidity", "wind_x", "wind_y",
    "lag_1_rain", "lag_3_rain", "lag_7_rain",
    "solar_radiation", "dew_point_spread"
]
```

### Update app.py feature order:
In `app.py`, find the `build_features()` function and update the `feature_order` list
to match YOUR training data exactly:

```python
# CHANGE THIS to match your notebook's feature columns:
feature_order = [
    "temperature", "humidity", "wind_x", "wind_y",
    "lag_1_rain", "lag_3_rain", "lag_7_rain",
    "solar_radiation", "dew_point_spread"
]
```

---

## STEP 4: Install Backend Dependencies

Activate your virtual environment and install FastAPI dependencies:

```bash
# Windows (cmd):
.venv\Scripts\activate

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# macOS/Linux:
source .venv/bin/activate

# Install dependencies:
pip install fastapi "uvicorn[standard]" pydantic joblib numpy pandas requests
```

### Verify installation:
```bash
pip list | findstr fastapi    # Windows
pip list | grep fastapi       # macOS/Linux
```

---

## STEP 5: Start Your FastAPI Backend

In your VS Code terminal (with virtual environment activated):

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Expected Output:
```
INFO:     Will watch for changes in these directories: ['...rainfall_prediction_project']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🔄 Loading pre-trained models...
  ✅ Loaded classifier from models/classifier_xgb.pkl
  ✅ Loaded regressor from models/regressor_lgbm.pkl
  ✅ Loaded scaler from models/scaler.pkl
  ✅ Loaded regressor scaler from models/scaler_reg.pkl
✅ All models and scalers loaded successfully!
✅ Loaded features.py for feature engineering

============================================================
️ UP Rainfall Prediction API — Server Started!
============================================================
📍 Base URL: http://localhost:8000
📊 Docs: http://localhost:8000/docs
 Health: http://localhost:8000/
📡 Predict: POST http://localhost:8000/api/v1/predict
️  SQLite: data/weather_db.sqlite
 Classifier: models/classifier_xgb.pkl
 Regressor: models/regressor_lgbm.pkl
============================================================
```

### If you see errors:
| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install fastapi` |
| `FileNotFoundError: models/classifier_xgb.pkl` | Check the model file exists in `models/` |
| `sqlite3.OperationalError: no such table` | Check Step 2 — update table name in `app.py` |
| `ValueError: shape mismatch` | Check Step 3 — feature order doesn't match training data |

---

## STEP 6: Test Your Backend

Open a browser to `http://localhost:8000/docs` — you should see the Swagger UI.

### Test the health endpoint:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "service": "UP Rainfall Prediction API",
  "version": "2.0.0",
  "models_loaded": true,
  "timestamp": "2024-..."
}
```

### Test the prediction endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "district_id": "UP-50",
    "temperature_c": 32.5,
    "humidity_pct": 78.0,
    "wind_vector_x": -1.6,
    "wind_vector_y": 2.8,
    "lag_1_rain": 15.0,
    "lag_3_rain": 35.0,
    "lag_7_rain": 78.0
  }'
```

Expected response:
```json
{
  "district_id": "UP-50",
  "classification_threat_pct": 63.42,
  "will_rain": true,
  "predicted_rain_mm": 23.8,
  "model_source": "your_trained_models",
  "timestamp": "2024-..."
}
```

---

## STEP 7: Install Frontend Dependencies

The React dashboard I built is in a separate folder. Inside that folder:

```bash
cd rainfall-analytics-pro
npm install
```

---

## STEP 8: Start the Frontend Dashboard

In a NEW terminal (keep VS Code terminal running):

```bash
cd rainfall-analytics-pro
npm run dev
```

Expected output:
```
VITE v7.3.2  ready in 500 ms

➜  Local:   http://localhost:5173/
```

---

## STEP 9: Verify Connection in Dashboard

1. Open browser to `http://localhost:5173`

2. Look at the top panel **"Live Telemetry & FastAPI Hub"**

3. Check these indicators:
   - ✅ Green badge: **"Backend ONLINE"**
   - ✅ Red badge: **"LIVE STREAM"**
   - ✅ Real-time temperature, humidity, dew point values
   - ✅ Click **"Test & Re-Predict"** → see green prediction box

4. If you see **"Backend OFFLINE"**:
   - Check VS Code terminal — is Uvicorn running?
   - In dashboard, verify URL is `http://localhost:8000`
   - Open browser console (F12) for CORS errors

---

## 🔧 COMMON ISSUES & FIXES

### Issue 1: "Backend OFFLINE" — CORS Error
**Symptom:** Browser console shows `CORS policy` error

**Fix:** Verify `app.py` has CORS middleware (it does — see Step 1):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: Prediction Returns Wrong Values
**Symptom:** Predictions are 0 or unrealistic numbers

**Fix 1:** Verify feature order in `app.py` matches your notebooks:
- Open `notebooks/03_classification.ipynb`
- Find where `X` is defined
- Copy the column order to `app.py`

**Fix 2:** Verify scalers are loaded:
- Check startup logs for `✅ Loaded scaler` messages
- If scalers aren't found, check `models/scaler.pkl` exists

**Fix 3:** Test with known values:
```python
# In VS Code terminal:
python -c "
import joblib, numpy as np
model = joblib.load('models/classifier_xgb.pkl')
scaler = joblib.load('models/scaler.pkl')
# Use sample from your training data
test = np.array([[32.5, 78, -1.6, 2.8, 15, 35, 78, 20, 3]])
scaled = scaler.transform(test)
print('Prediction:', model.predict_proba(scaled))
"
```

### Issue 3: "Models not loaded" Error
**Symptom:** API returns 500 with "Models not loaded"

**Fix:** Check these:
1. `models/classifier_xgb.pkl` exists in the correct location
2. `models/regressor_lgbm.pkl` exists
3. Python package versions match training (check `requirements.txt`)
4. Virtual environment is activated

### Issue 4: SQLite Table Not Found
**Symptom:** API returns 500 with "no such table"

**Fix:** Run Step 2 to check your actual table names, then update `app.py`:
```python
# Change this line to match your table:
cursor.execute("SELECT * FROM YOUR_ACTUAL_TABLE_NAME WHERE district_id = ? LIMIT 1", (district_id,))
```

### Issue 5: Shape Mismatch in Model Prediction
**Symptom:** Error about feature dimensions

**Fix:** Count the features your model expects:
```python
# Check how many features your model expects:
import joblib
model = joblib.load('models/classifier_xgb.pkl')
print('Model n_features:', model.n_features_in_)
```

Then ensure `feature_order` in `app.py` has the same number of features.

---

## 📋 QUICK REFERENCE: File Locations

| File | Location | Purpose |
|------|----------|---------|
| `app.py` | Project root | FastAPI server (create this) |
| `classifier_xgb.pkl` | `models/` | Your trained classifier |
| `regressor_lgbm.pkl` | `models/` | Your trained regressor |
| `scaler.pkl` | `models/` | Feature scaler |
| `scaler_reg.pkl` | `models/` | Regressor scaler |
| `weather_db.sqlite` | `data/` | Your SQLite database |
| `features.py` | `src/` | Your feature engineering |
| Frontend | `rainfall-analytics-pro/` | React dashboard |

---

## ✅ SUCCESS CHECKLIST

- [ ] `app.py` created in project root
- [ ] CORS middleware added (included in app.py)
- [ ] Models load successfully (check startup logs)
- [ ] Scalers load successfully
- [ ] SQLite table name matches (check Step 2)
- [ ] Feature order matches training data (check Step 3)
- [ ] `GET /` returns healthy status
- [ ] `POST /api/v1/predict` returns predictions
- [ ] Frontend shows "Backend ONLINE"
- [ ] Live weather values display in dashboard
- [ ] Predictions match your model's expected output

---

## 🎯 FINAL STEP: Integration

Once everything works:

1. **Keep your VS Code terminal running** (uvicorn on port 8000)
2. **Keep your frontend terminal running** (Vite on port 5173)
3. **Open `http://localhost:5173` in browser**
4. **Select a district** → see live weather + YOUR model's prediction
5. **Click different districts** → watch predictions update in real-time

---

## 📞 Still Having Issues?

1. Check browser console (F12 → Console) for errors
2. Check VS Code terminal for server errors
3. Visit `http://localhost:8000/docs` to test API manually
4. Run the test script: `python test_backend.py`
