# 🚀 Watershed-UP Full-Stack Quick Start

## Current Configuration Summary

### ✅ Backend (FastAPI)
- **Location**: `backend/`
- **Main file**: `backend/main.py`
- **Virtual env**: `backend/.venv/`
- **Port**: `8000`
- **Start command**: 
  ```powershell
  cd backend
  .venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
  ```

### ✅ Frontend (React + Vite)
- **Location**: `app-frontend/`
- **Main file**: `app-frontend/src/main.tsx`
- **Dependencies**: `app-frontend/node_modules/`
- **Port**: `5173`
- **Start command**:
  ```powershell
  cd app-frontend
  npm run dev
  ```

### 📁 Key File Paths

#### Backend Files
```
backend/
├── main.py                              # FastAPI app entry point
├── requirements.txt                     # Python dependencies
├── .venv/                               # Python virtual environment
├── routers/
│   ├── tiles.py                         # Tile serving endpoints
│   └── watersheds.py                    # Watershed API endpoints
├── utils/
│   └── raster_tile_utils.py            # Tile rendering utilities
└── data_demo/
    ├── rasters/demo_raster.tif         # Demo raster data ✅
    └── vectors/demo_watersheds.geojson  # Demo vector data ✅
```

#### Frontend Files
```
app-frontend/
├── src/
│   ├── App.tsx                          # Root React component
│   ├── main.tsx                         # Entry point
│   ├── components/
│   │   └── MapView.tsx                  # MapLibre GL map component
│   └── pages/
│       └── Home.tsx                     # Home page
├── vite.config.ts                       # Vite config with API proxy
├── package.json                         # Node.js dependencies
└── node_modules/                        # Dependencies (installed) ✅
```

### 🔌 API Endpoints

#### Backend (http://localhost:8000)
- **Health Check**: `GET /health`
- **API Docs**: `GET /docs` (Swagger UI)
- **Watersheds**: `GET /api/watersheds` (GeoJSON)
- **Demo Tiles**: `GET /tiles/demo/{z}/{x}/{y}.png` (PNG tiles)

#### Frontend (http://localhost:5173)
- **Application**: React SPA
- **API Proxy**: 
  - `/api/*` → `http://localhost:8000/api/*`
  - `/tiles/*` → `http://localhost:8000/tiles/*`

### 🎯 Quick Start Options

#### Option 1: Automated Launcher (Recommended)
```powershell
# Run this from project root
.\run_fullstack.ps1
```
or
```cmd
run_fullstack.bat
```

This will:
1. Check all dependencies
2. Start backend in new window
3. Start frontend in new window
4. Display access URLs

#### Option 2: Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```powershell
cd backend
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path
cd app-frontend
npm run dev
```

#### Option 3: Using activate_all.ps1

**Terminal 1 - Backend:**
```powershell
.\activate_all.ps1
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
.\activate_all.ps1
cd app-frontend
npm run dev
```

### 🧪 Testing the Stack

Once both servers are running, test these URLs:

1. **Backend Health**:
   ```
   http://localhost:8000/health
   ```
   Should return: `{"status":"ok","service":"Watershed-UP backend"}`

2. **API Documentation**:
   ```
   http://localhost:8000/docs
   ```
   Interactive Swagger UI

3. **Watersheds GeoJSON**:
   ```
   http://localhost:8000/api/watersheds
   ```
   Returns GeoJSON from demo_watersheds.geojson

4. **Demo Tile** (example):
   ```
   http://localhost:8000/tiles/demo/10/629/389.png
   ```
   Returns PNG tile image

5. **Frontend Application**:
   ```
   http://localhost:5173
   ```
   React app with MapLibre GL map

### 🔍 Map Component Details

The `MapView.tsx` component:
- **Base layer**: Stamen Terrain tiles (public)
- **Overlay**: Demo raster tiles from backend
- **Center**: Lucknow (80.9462°E, 26.8467°N)
- **Zoom**: 10
- **Features**: Click to show coordinates

### 🛠️ Dependencies Status

#### Backend (Python)
- ✅ fastapi==0.109.0
- ✅ uvicorn[standard]==0.27.0
- ✅ rasterio==1.4.3
- ✅ geopandas==1.0.1
- ✅ mercantile==1.2.1
- ✅ All dependencies installed in `.venv/`

#### Frontend (Node.js)
- ✅ react@18.2.0
- ✅ vite@5.0.0
- ✅ maplibre-gl@2.4.0
- ✅ tailwindcss@3.4.14
- ✅ All 446 packages installed in `node_modules/`

### 🔥 CORS Configuration

Backend CORS is configured to allow all origins:
```python
allow_origins=["*"]  # Accepts requests from any origin
```

For production, change to:
```python
allow_origins=["http://localhost:5173", "https://yourdomain.com"]
```

### 📊 Data Files Verified

- ✅ `backend/data_demo/rasters/demo_raster.tif` exists
- ✅ `backend/data_demo/vectors/demo_watersheds.geojson` exists

### 🚨 Troubleshooting

#### Backend won't start
```powershell
# Reinstall dependencies
cd backend
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

#### Frontend won't start
```powershell
# Reinstall dependencies
cd app-frontend
npm install
```

#### "uvicorn not recognized"
Use full path:
```powershell
cd backend
.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

#### "npm not recognized"
Add Node.js to PATH:
```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path
```

#### Port already in use
Change ports in:
- Backend: Add `--port 8001` to uvicorn command
- Frontend: Change `port: 5173` in `vite.config.ts`
- Update proxy URLs accordingly

### 📝 Next Steps

1. **Test the current setup**: Run both servers and verify all endpoints work
2. **Customize the map**: Edit `MapView.tsx` to change center/zoom
3. **Add features**: Create new API endpoints in `backend/routers/`
4. **Style the UI**: Modify Tailwind classes in React components
5. **Add real data**: Replace demo files with actual watershed data
6. **Deploy**: Configure for production environment

### 💡 Development Workflow

1. Start both servers using `run_fullstack.ps1`
2. Edit backend code → server auto-reloads
3. Edit frontend code → Vite hot-reloads
4. View changes instantly in browser
5. Check API docs at `/docs` for backend changes
6. Use browser DevTools for frontend debugging

---

**Current Status**: ✅ All files verified, all dependencies installed, ready to run!

Run `.\run_fullstack.ps1` to start the full stack now! 🚀
