# 🚀 Quick Start Guide

**Get Watershed-UP running in 10 minutes!**

---

## Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **8GB RAM minimum** (16GB recommended for ML tasks)

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/PAVANKUMARELETI/watershed-up.git
cd watershed-up
```

---

## 2️⃣ Backend Setup (FastAPI)

### Install Python Dependencies

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Start Backend Server

```powershell
# From backend/ directory
python simple_main.py

# Server runs on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

---

## 3️⃣ Frontend Setup (React + Vite)

### Install Node Dependencies

```powershell
# Navigate to frontend (from project root)
cd app-frontend

# Install dependencies
npm install
```

### Start Frontend Dev Server

```powershell
# From app-frontend/ directory
npm run dev

# Frontend runs on http://localhost:5173
```

---

## 4️⃣ Access the Application

Open your browser and navigate to:
- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs

### What You'll See:

1. **Map View Tab**: Interactive map with watershed boundaries
   - Click any watershed to view details
   - Toggle layers (Groundwater Potential, NDVI, Elevation, etc.)
   
2. **Analytics Tab**: Data visualizations
   - Cross-validation performance charts
   - Watershed distribution statistics
   - Feature importance rankings

---

## 5️⃣ (Optional) Run ML Pipeline

If you want to retrain models or process new data:

```powershell
# From project root
cd ml/src

# Run complete pipeline
python run_pipeline.py

# Or run individual steps:
python preprocessing/preprocess.py
python models/train.py
python models/predict.py
```

---

## 🔧 Troubleshooting

### Backend won't start?

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```powershell
cd backend
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend won't start?

**Issue**: `npm ERR! missing: vite`

**Solution**:
```powershell
cd app-frontend
npm install
```

### Port already in use?

**Backend (port 8000)**:
```powershell
# Find process
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

**Frontend (port 5173)**:
```powershell
# Find process
netstat -ano | findstr :5173

# Kill process
taskkill /PID <PID> /F
```

### CORS errors in browser?

Make sure backend CORS settings include frontend port:
- Check `backend/simple_main.py`
- Verify `allow_origins` includes `http://localhost:5173`

---

## 📚 Next Steps

- [Environment Setup Details](ENVIRONMENT_SETUP.md) - Detailed configuration guide
- [Architecture Overview](../architecture/PROJECT_ARCHITECTURE.md) - System design
- [API Documentation](../api/ENDPOINTS.md) - API reference
- [Running ML Pipeline](../guides/RUNNING_ML_PIPELINE.md) - ML workflow details

---

## 🆘 Need Help?

- **Issues**: [GitHub Issues](https://github.com/PAVANKUMARELETI/watershed-up/issues)
- **Discussions**: [GitHub Discussions](https://github.com/PAVANKUMARELETI/watershed-up/discussions)
- **Email**: pavankumareletti@example.com

---

**Estimated Setup Time**: 10-15 minutes  
**Difficulty**: Beginner-friendly  
**Last Updated**: November 12, 2025
