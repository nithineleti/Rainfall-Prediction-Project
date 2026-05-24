# 🌧️ UP Rainfall Prediction Pipeline (Dual-Stage ML)

An advanced meteorological intelligence system designed to predict rainfall threats and volumes across 75 districts of Uttar Pradesh using specialized Machine Learning models.

## 🚀 System Architecture

This project implements a **Dual-Stage Pipeline**:
1.  **Stage 1: Classification (XGBoost)** - Predicts whether a rainfall event (Threat/No Threat) will occur based on real-time atmospheric conditions.
2.  **Stage 2: Regression (LightGBM)** - If a threat is detected, this model estimates the precise rainfall volume in millimeters.

### Core Technologies
*   **Backend**: FastAPI (Python 3.11) with Uvicorn (4-worker parallel processing).
*   **Frontend**: React 19 + Vite + Tailwind CSS 4.
*   **Intelligence**: Open-Meteo API integration for real-time telemetry.
*   **Physics Engine**: Magnus-Tetens formula for precise Specific Humidity calculation.

## 🛠️ Features

*   **Real-time Dashboard**: Interactive map showing weather telemetry for all 75 districts.
*   **Synchronous Analytics**: Live streaming of atmospheric data (Temperature, Humidity, Pressure, Wind Vectors).
*   **High Performance**: Asynchronous data fetching (Parallelized on both Frontend and Backend).
*   **Meteorological Logic**: Handles complex feature engineering including $u$ and $v$ wind components and temporal periodic encodings.

## 🚦 Getting Started

### Prerequisites
*   Python 3.11+
*   Node.js 18+
*   A virtual environment (`.venv`)

### 1. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn main_api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Frontend Setup
```bash
# Navigate to UI folder
cd up-weather-intelligence-system

# Install and Run
npm install
npx vite --port 5176
```

## 📊 API Endpoints

*   `GET /live-weather`: Fetches real-time RAW telemetry.
*   `POST /predict`: Unified endpoint for the Dual-Stage prediction results.
*   `GET /api/v1/forecast`: Multi-district summarized intelligence.

## 📄 License
MIT License - Developed for Advanced Rainfall Analytics in Uttar Pradesh.
