# 🌧️ Rainfall Prediction System (Dual-Stage ML)

An advanced meteorological intelligence system designed to predict rainfall threats and volumes across 75 districts of Uttar Pradesh using specialized Machine Learning models.

## 🔗 Live Deployment
**Web Application**: [http://16.171.254.60:5176](http://16.171.254.60:5176)  
**API Status**: [http://16.171.254.60/ping](http://16.171.254.60/ping)

## 🚀 System Architecture

This project implements a **Dual-Stage Pipeline**:
1.  **Stage 1: Classification (XGBoost)** - Predicts whether a rainfall event (Threat/No Threat) will occur based on real-time atmospheric conditions.
2.  **Stage 2: Regression (LightGBM)** - If a threat is detected, this model estimates the precise rainfall volume in millimeters.

### Core Technologies
*   **Backend**: FastAPI (Python) - Hosted on AWS EC2 (Port 80).
*   **Frontend**: React 19 + Vite + Tailwind CSS - Hosted on Port 5176.
*   **Intelligence**: Open-Meteo API integration for real-time telemetry.
*   **Models**: XGBoost (Classification) & LightGBM (Regression).

## 🛠️ Features

*   **Real-time Dashboard**: Interactive map showing weather telemetry for all 75 districts.
*   **Synchronous Analytics**: Live streaming of atmospheric data (Temperature, Humidity, Pressure, Wind Vectors).
*   **High Performance**: Asynchronous data fetching using `httpx` and `Promise.all`.
*   **Production Ready**: Automated deployment on AWS with persistent background sessions.

## 🚦 Getting Started (Local Development)

### Prerequisites
*   Python 3.11+
*   Node.js 18+
*   A virtual environment (`.venv`)

### 1. Backend Setup
```bash
pip install -r requirements.txt
python3 -m uvicorn main_api:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd up-weather-intelligence-system
npm install
npm run dev
```

## 📊 Deployment
The system is currently deployed on **AWS EC2 (Ubuntu 26.04)**:
*   **Backend**: Running as a root service on Port 80 for public accessibility.
*   **Processes**: Managed via `screen` for 24/7 uptime.

## 📄 License
MIT License - Developed for Advanced Rainfall Analytics.
