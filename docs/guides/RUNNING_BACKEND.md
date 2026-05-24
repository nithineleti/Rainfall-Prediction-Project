# Running the Backend

This guide explains how to set up, run, and develop the FastAPI backend server.

---

## Prerequisites

- **Python**: 3.11 or higher
- **pip**: Latest version
- **Virtual Environment**: Recommended (venv or conda)
- **Git**: For version control

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PAVANKUMARELETI/watershed-up.git
cd watershed-up
```

### 2. Create Virtual Environment

**Using venv (Windows)**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Using venv (Linux/Mac)**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Using conda**:
```bash
conda create -n watershed-backend python=3.11
conda activate watershed-backend
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Dependencies include**:
- FastAPI 0.104+
- Uvicorn (ASGI server)
- Pydantic v2
- GeoPandas, Rasterio, Shapely
- XGBoost, scikit-learn
- NumPy, Pandas

### 4. Verify Installation

```bash
python -c "import fastapi; import geopandas; import xgboost; print('All dependencies installed!')"
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Data Paths
DATA_DIR=../data
MODELS_DIR=../models
PROCESSED_DIR=../data/processed

# Model Files
MODEL_PATH=../models/xgboost_model.json
FEATURE_STACK_PATH=../data/processed/feature_stack.tif
WATERSHED_PATH=../data/processed/prioritized_watersheds.gpkg

# API Settings
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
MAX_PAGE_SIZE=100
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### CORS Configuration

Update CORS origins in `backend/app/main.py` if needed:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Running the Server

### Development Mode

**Using run.py** (Recommended):
```bash
cd backend
python run.py
```

**Using uvicorn directly**:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Mode

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Using Gunicorn** (Linux/Mac):
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

---

## Testing the API

### Health Check

```bash
# Check if server is running
curl http://localhost:8000/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-11-12T10:30:00Z"
}
```

### Interactive Documentation

Open your browser and visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints interactively from Swagger UI.

### Test Endpoints

**List Watersheds**:
```bash
curl http://localhost:8000/api/watersheds?page=1&page_size=5
```

**Get Watershed Detail**:
```bash
curl http://localhost:8000/api/watersheds/1
```

**Make Prediction**:
```bash
curl -X POST http://localhost:8000/api/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{"longitude": 80.1234, "latitude": 13.4567}'
```

**Get Analytics**:
```bash
curl http://localhost:8000/api/analytics/summary
```

---

## Development Workflow

### Project Structure

```
backend/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration
│   ├── routers/             # API endpoints
│   │   ├── watersheds.py
│   │   ├── predictions.py
│   │   ├── analytics.py
│   │   └── health.py
│   ├── services/            # Business logic
│   │   ├── watershed_service.py
│   │   ├── prediction_service.py
│   │   └── analytics_service.py
│   ├── models/              # Pydantic schemas
│   │   └── schemas.py
│   └── utils/               # Utilities
│       ├── spatial.py
│       └── logger.py
├── tests/                   # Unit tests
├── Dockerfile               # Docker configuration
├── requirements.txt         # Dependencies
└── run.py                   # Dev server launcher
```

### Adding a New Endpoint

**1. Create route in `routers/`**:

```python
# backend/app/routers/new_feature.py
from fastapi import APIRouter, Depends
from app.services.new_feature_service import NewFeatureService

router = APIRouter()

@router.get("/new-endpoint")
async def get_new_feature(service: NewFeatureService = Depends()):
    """Get new feature data."""
    return await service.get_data()
```

**2. Create service in `services/`**:

```python
# backend/app/services/new_feature_service.py
class NewFeatureService:
    def __init__(self):
        # Initialize
        pass
    
    async def get_data(self):
        # Business logic
        return {"data": "example"}
```

**3. Register router in `main.py`**:

```python
from app.routers import new_feature

app.include_router(
    new_feature.router,
    prefix="/api/new-feature",
    tags=["new-feature"]
)
```

### Code Style

Follow **PEP 8** and use **Black** formatter:

```bash
# Format code
black app/

# Check style
flake8 app/

# Type checking
mypy app/
```

### Adding Type Hints

Always add type hints to functions:

```python
from typing import List, Optional

async def get_watersheds(
    page: int,
    page_size: int,
    priority: Optional[str] = None
) -> dict:
    """Get watersheds with type hints."""
    pass
```

---

## Debugging

### Enable Debug Logging

**In `run.py`**:
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"  # Enable debug logs
    )
```

**In code**:
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Using Python Debugger

**Set breakpoint**:
```python
import pdb; pdb.set_trace()
```

**Or use VS Code debugger**:

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "cwd": "${workspaceFolder}/backend",
      "jinja": true
    }
  ]
}
```

### Common Issues

**1. Module Import Errors**
```bash
# Ensure you're in the backend directory
cd backend
python run.py

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/backend"
```

**2. CORS Errors**
- Check `CORS_ORIGINS` in configuration
- Ensure frontend URL is included
- Check browser console for exact error

**3. Port Already in Use**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

**4. Database/File Not Found**
- Check `.env` file paths
- Verify data files exist in `data/processed/`
- Run ML pipeline if files are missing

---

## Hot Reload

FastAPI with `--reload` automatically reloads when code changes:

1. Edit a file (e.g., `app/routers/watersheds.py`)
2. Save the file
3. Server automatically restarts
4. Test changes immediately

**Files watched**:
- All `.py` files in `app/`
- Changes in `requirements.txt` require manual restart

---

## Running Tests

### Unit Tests

```bash
cd backend
pytest tests/ -v
```

### Test with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.

### Test Specific File

```bash
pytest tests/test_watershed_service.py -v
```

### Test Specific Function

```bash
pytest tests/test_watershed_service.py::test_get_watersheds -v
```

---

## Performance Monitoring

### Request Timing

Add middleware to log request duration:

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Memory Profiling

```bash
pip install memory-profiler

# Add @profile decorator
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Your code
    pass
```

---

## Docker Deployment

### Build Image

```bash
cd backend
docker build -t watershed-backend .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/../data:/app/data \
  -v $(pwd)/../models:/app/models \
  --name watershed-backend \
  watershed-backend
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - DATA_DIR=/app/data
      - MODELS_DIR=/app/models
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## Environment Management

### Requirements Files

**`requirements.txt`** - Production dependencies:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
geopandas==0.14.0
xgboost==2.0.1
```

**`requirements-dev.txt`** - Development dependencies:
```txt
-r requirements.txt
pytest==7.4.3
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.0
```

Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

### Updating Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade fastapi

# Freeze current versions
pip freeze > requirements.txt
```

---

## Logging

### Log Configuration

```python
# backend/app/utils/logger.py
import logging
from pathlib import Path

def setup_logger(name: str, log_file: Path, level=logging.INFO):
    """Setup logger with file and console handlers."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### Using Logger

```python
from app.utils.logger import setup_logger
from pathlib import Path

logger = setup_logger(__name__, Path("logs/app.log"))

logger.info("Server started")
logger.error("Error occurred", exc_info=True)
```

---

## API Versioning

### URL-based Versioning

```python
# v1 router
router_v1 = APIRouter(prefix="/api/v1")

@router_v1.get("/watersheds")
async def get_watersheds_v1():
    # Version 1 implementation
    pass

# v2 router
router_v2 = APIRouter(prefix="/api/v2")

@router_v2.get("/watersheds")
async def get_watersheds_v2():
    # Version 2 implementation
    pass

# Register both
app.include_router(router_v1)
app.include_router(router_v2)
```

---

## Security Best Practices

### 1. Input Validation

Always validate inputs with Pydantic:

```python
from pydantic import BaseModel, Field, validator

class PredictionRequest(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Invalid longitude')
        return v
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/predictions/predict")
@limiter.limit("10/minute")
async def predict():
    pass
```

### 3. API Keys (Future)

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "your-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

---

## Troubleshooting

### Server Won't Start

**Check Python version**:
```bash
python --version  # Should be 3.11+
```

**Check port availability**:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

### Import Errors

**Verify installation**:
```bash
pip list | grep fastapi
pip list | grep geopandas
```

**Reinstall dependencies**:
```bash
pip install --force-reinstall -r requirements.txt
```

### Data Loading Errors

**Check file paths**:
```python
from pathlib import Path

data_dir = Path("../data/processed")
print(f"Data directory exists: {data_dir.exists()}")
print(f"Files: {list(data_dir.glob('*.gpkg'))}")
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Project Architecture](../architecture/BACKEND.md)
- [API Reference](../api/ENDPOINTS.md)

---

**Last Updated**: November 12, 2025  
**Version**: 2.0.0
