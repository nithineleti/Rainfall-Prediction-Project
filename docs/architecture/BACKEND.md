# Backend Architecture

## Overview

The backend is built with **FastAPI** (Python 3.11+) and follows a clean, layered architecture pattern. It serves as the API layer between the React frontend and the ML pipeline, providing RESTful endpoints for watershed analysis, predictions, and data visualization.

**Tech Stack**:
- **Framework**: FastAPI 0.104+
- **ASGI Server**: Uvicorn
- **Validation**: Pydantic v2
- **Spatial Libraries**: GeoPandas, Shapely, Rasterio
- **ML Integration**: XGBoost, scikit-learn
- **Configuration**: YAML-based config files

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── watersheds.py       # Watershed endpoints
│   │   ├── predictions.py      # ML prediction endpoints
│   │   ├── analytics.py        # Analytics & statistics
│   │   └── health.py           # Health check endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── watershed_service.py    # Watershed business logic
│   │   ├── prediction_service.py   # Prediction logic
│   │   └── analytics_service.py    # Analytics calculations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic models
│   │   └── responses.py        # Response models
│   └── utils/
│       ├── __init__.py
│       ├── spatial.py          # Spatial data utilities
│       ├── logger.py           # Logging configuration
│       └── errors.py           # Error handlers
├── Dockerfile
├── requirements.txt
└── run.py                      # Development server launcher
```

---

## Core Components

### 1. Application Entry Point (`main.py`)

The main FastAPI application with CORS configuration and router registration.

**Key Features**:
- CORS middleware for frontend communication
- Router registration for all endpoints
- Global exception handlers
- Lifespan events for startup/shutdown
- API versioning support

**Example Structure**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import watersheds, predictions, analytics, health

app = FastAPI(
    title="Watershed Prioritization API",
    version="2.0.0",
    description="API for groundwater potential watershed analysis"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router registration
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(watersheds.router, prefix="/api/watersheds", tags=["watersheds"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
```

### 2. Configuration Management (`config.py`)

Centralized configuration using Pydantic settings and environment variables.

**Configuration Categories**:
- **Paths**: Data directories, model paths, output locations
- **ML Settings**: Model parameters, feature lists, thresholds
- **API Settings**: CORS origins, rate limits, pagination
- **Database**: (Future) Database connection settings

**Example**:
```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    
    # ML Settings
    MODEL_PATH: Path = MODELS_DIR / "xgboost_model.json"
    FEATURE_STACK_PATH: Path = DATA_DIR / "processed" / "feature_stack.tif"
    
    # API Settings
    CORS_ORIGINS: list = ["http://localhost:5173"]
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 3. Routers (API Endpoints)

#### `watersheds.py` - Watershed Management

**Endpoints**:
- `GET /api/watersheds` - List all watersheds with pagination
- `GET /api/watersheds/{id}` - Get watershed details
- `GET /api/watersheds/{id}/geometry` - Get watershed boundary GeoJSON
- `POST /api/watersheds/delineate` - Delineate new watershed from pour point

**Example Router**:
```python
from fastapi import APIRouter, Depends, Query
from app.services.watershed_service import WatershedService
from app.models.schemas import WatershedList, WatershedDetail

router = APIRouter()

@router.get("/", response_model=WatershedList)
async def list_watersheds(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    priority: str = Query(None, regex="^(high|medium|low)$"),
    service: WatershedService = Depends()
):
    """List watersheds with pagination and filtering."""
    return await service.get_watersheds(
        page=page,
        page_size=page_size,
        priority_filter=priority
    )
```

#### `predictions.py` - ML Predictions

**Endpoints**:
- `POST /api/predictions/predict` - Run prediction for coordinates
- `GET /api/predictions/map` - Get prediction raster as image
- `POST /api/predictions/batch` - Batch predictions for multiple points

#### `analytics.py` - Analytics & Statistics

**Endpoints**:
- `GET /api/analytics/summary` - Overall statistics
- `GET /api/analytics/priority-distribution` - Priority class distribution
- `GET /api/analytics/feature-importance` - SHAP feature importance
- `GET /api/analytics/trends` - Temporal trends (if applicable)

#### `health.py` - Health Checks

**Endpoints**:
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed system status

### 4. Services (Business Logic)

Services contain the core business logic, separated from HTTP concerns.

#### `watershed_service.py`

**Responsibilities**:
- Load watershed data from GeoPackage/Shapefile
- Filter and paginate watersheds
- Calculate watershed statistics
- Delineate new watersheds using DEM
- Cache frequently accessed data

**Key Methods**:
```python
class WatershedService:
    def __init__(self):
        self.data_path = settings.DATA_DIR / "processed" / "prioritized_watersheds.gpkg"
        self._cache = {}
    
    async def get_watersheds(self, page: int, page_size: int, priority_filter: str = None):
        """Get paginated list of watersheds."""
        gdf = self._load_watersheds()
        
        if priority_filter:
            gdf = gdf[gdf['priority_class'] == priority_filter]
        
        total = len(gdf)
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "watersheds": gdf.iloc[start:end].to_dict('records')
        }
    
    async def get_watershed_detail(self, watershed_id: int):
        """Get detailed information for a watershed."""
        gdf = self._load_watersheds()
        watershed = gdf[gdf['watershed_id'] == watershed_id].iloc[0]
        
        return {
            "id": watershed_id,
            "area_km2": watershed['area_km2'],
            "priority_class": watershed['priority_class'],
            "priority_score": watershed['priority_score'],
            "features": self._extract_features(watershed),
            "geometry": watershed.geometry.__geo_interface__
        }
```

#### `prediction_service.py`

**Responsibilities**:
- Load trained ML model
- Load feature stack (multi-band raster)
- Extract features for given coordinates
- Run predictions using XGBoost model
- Return probability and class predictions

**Key Methods**:
```python
class PredictionService:
    def __init__(self):
        self.model = self._load_model()
        self.feature_stack = self._load_feature_stack()
    
    async def predict_point(self, lon: float, lat: float):
        """Predict groundwater potential for a point."""
        # Extract features from raster stack
        features = self._extract_features_at_point(lon, lat)
        
        # Run prediction
        prob = self.model.predict_proba([features])[0][1]
        prediction = "High" if prob > 0.5 else "Low"
        
        return {
            "longitude": lon,
            "latitude": lat,
            "probability": float(prob),
            "prediction": prediction,
            "features": dict(zip(self.feature_names, features))
        }
```

#### `analytics_service.py`

**Responsibilities**:
- Calculate summary statistics
- Generate distribution charts data
- Compute feature importance (SHAP values)
- Aggregate metrics for dashboard

### 5. Models (Pydantic Schemas)

Pydantic models for request/response validation and serialization.

#### `schemas.py`

**Example Models**:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class WatershedBase(BaseModel):
    watershed_id: int
    area_km2: float
    priority_class: str
    priority_score: float

class WatershedDetail(WatershedBase):
    perimeter_km: float
    mean_elevation: float
    mean_slope: float
    drainage_density: float
    lulc_forest_pct: float
    lulc_agriculture_pct: float
    mean_rainfall: float
    # ... more features

class WatershedList(BaseModel):
    total: int
    page: int
    page_size: int
    watersheds: List[WatershedBase]

class PredictionRequest(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)

class PredictionResponse(BaseModel):
    longitude: float
    latitude: float
    probability: float = Field(..., ge=0, le=1)
    prediction: str
    features: dict
```

### 6. Utilities

#### `spatial.py` - Spatial Operations

**Functions**:
- `extract_raster_value(raster_path, lon, lat)` - Extract value from raster
- `buffer_point(lon, lat, distance)` - Create buffer around point
- `reproject_geometry(geom, from_crs, to_crs)` - Reproject geometries
- `calculate_area(geometry)` - Calculate area in km²

#### `logger.py` - Logging Configuration

**Setup**:
```python
import logging
from pathlib import Path

def setup_logger(name: str, log_file: Path, level=logging.INFO):
    """Configure logger with file and console handlers."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
```

#### `errors.py` - Custom Exception Handlers

**Custom Exceptions**:
```python
from fastapi import HTTPException, status

class WatershedNotFoundError(HTTPException):
    def __init__(self, watershed_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Watershed {watershed_id} not found"
        )

class PredictionError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {message}"
        )
```

---

## Data Flow

### 1. Watershed List Request Flow

```
Client Request → Router → Service → Data Layer → Response
```

**Detailed Steps**:
1. Client sends `GET /api/watersheds?page=1&page_size=20`
2. Router validates query parameters
3. Service loads watershed GeoPackage
4. Service filters and paginates data
5. Service converts to JSON-serializable format
6. Router returns Pydantic model response
7. FastAPI serializes to JSON

### 2. Prediction Request Flow

```
Client → Router → Service → ML Model → Feature Extraction → Prediction → Response
```

**Detailed Steps**:
1. Client sends `POST /api/predictions/predict` with coordinates
2. Router validates request body (Pydantic model)
3. Service loads feature stack raster
4. Service extracts features at coordinates
5. Service loads XGBoost model
6. Service runs prediction
7. Service formats response with probability + class
8. Router returns prediction response

### 3. Analytics Request Flow

```
Client → Router → Service → Data Aggregation → Chart Data → Response
```

---

## API Versioning

The API uses URL path versioning:

```
/api/v1/watersheds  → Version 1 (legacy)
/api/v2/watersheds  → Version 2 (current)
/api/watersheds     → Latest version (v2)
```

**Version Management**:
- New features added to latest version
- Breaking changes require new version
- Old versions maintained for 6 months after deprecation notice

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST (created resource) |
| 400 | Bad Request | Invalid input, validation error |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Pydantic validation error |
| 500 | Internal Server Error | Unexpected server error |

### Error Response Format

```json
{
  "detail": "Watershed 999 not found",
  "status_code": 404,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

### Global Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## Performance Optimization

### 1. Caching Strategy

**In-Memory Cache**:
- Watershed data cached on first load
- Feature stack loaded once at startup
- ML model loaded once at startup
- Cache invalidation on data update

**Implementation**:
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_watersheds():
    """Load watersheds with caching."""
    return gpd.read_file(settings.WATERSHED_PATH)
```

### 2. Async Operations

**Where Used**:
- All database queries (when DB added)
- File I/O operations
- External API calls

**Benefits**:
- Non-blocking I/O
- Better concurrency
- Improved throughput

### 3. Response Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 4. Pagination

**Default Settings**:
- Default page size: 20
- Max page size: 100
- Offset-based pagination

---

## Security

### 1. CORS Configuration

**Current**: Allow localhost (development)
**Production**: Restrict to specific domains

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # From .env
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### 2. Input Validation

**Pydantic Models**: Automatic validation
**Query Parameters**: Type checking and constraints
**File Uploads**: Size limits and type validation

### 3. Rate Limiting

**(Future Implementation)**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/predictions/predict")
@limiter.limit("10/minute")
async def predict(...):
    ...
```

---

## Testing Strategy

### 1. Unit Tests

**Coverage**:
- Services: Business logic testing
- Utilities: Helper function testing
- Models: Pydantic validation testing

**Example**:
```python
def test_watershed_service_get_watersheds():
    service = WatershedService()
    result = service.get_watersheds(page=1, page_size=10)
    assert result['total'] > 0
    assert len(result['watersheds']) <= 10
```

### 2. Integration Tests

**Coverage**:
- Router + Service integration
- End-to-end API calls
- Database operations (when added)

**Example**:
```python
from fastapi.testclient import TestClient

def test_list_watersheds_endpoint():
    client = TestClient(app)
    response = client.get("/api/watersheds?page=1&page_size=5")
    assert response.status_code == 200
    assert len(response.json()['watersheds']) <= 5
```

### 3. Load Tests

**Tools**: Locust, Apache Bench
**Metrics**: Requests/sec, latency, error rate

---

## Deployment

### Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Using run.py
python backend/run.py
```

### Production Server

```bash
# Using gunicorn + uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Monitoring & Logging

### 1. Application Logs

**Levels**:
- DEBUG: Development debugging
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical failures

**Log Files**:
- `logs/app.log` - Application logs
- `logs/access.log` - Access logs
- `logs/error.log` - Error logs

### 2. Metrics

**(Future Implementation)**:
- Request count
- Response time
- Error rate
- Cache hit rate

**Tools**: Prometheus + Grafana

---

## Configuration Files

### `requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3
geopandas==0.14.0
shapely==2.0.2
rasterio==1.3.9
xgboost==2.0.1
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.1.3
python-multipart==0.0.6
```

### `.env` (Example)

```env
# Paths
DATA_DIR=/path/to/data
MODELS_DIR=/path/to/models

# API Settings
CORS_ORIGINS=["http://localhost:5173"]
MAX_PAGE_SIZE=100

# Logging
LOG_LEVEL=INFO
```

---

## Best Practices

### 1. Code Organization

✅ **Do**:
- Keep routers thin (delegate to services)
- Put business logic in services
- Use dependency injection
- Follow single responsibility principle

❌ **Don't**:
- Put business logic in routers
- Access data directly from routers
- Mix concerns (HTTP + business logic)

### 2. Error Handling

✅ **Do**:
- Use custom exceptions
- Log all errors
- Return informative error messages
- Use appropriate HTTP status codes

❌ **Don't**:
- Return generic errors
- Expose internal details
- Ignore exceptions

### 3. Performance

✅ **Do**:
- Cache frequently accessed data
- Use async operations
- Paginate large results
- Compress responses

❌ **Don't**:
- Load all data into memory
- Block on I/O operations
- Return unlimited results

---

## Troubleshooting

### Common Issues

**1. CORS Errors**
```
Solution: Check CORS_ORIGINS in .env matches frontend URL
```

**2. Module Import Errors**
```
Solution: Ensure PYTHONPATH includes backend directory
```

**3. Pydantic Validation Errors**
```
Solution: Check request body matches schema definition
```

**4. Numpy JSON Serialization**
```python
# Convert numpy types to Python native types
response_data = json.loads(
    json.dumps(data, default=lambda x: x.item() if isinstance(x, np.generic) else x)
)
```

---

## Future Enhancements

### Planned Features

1. **Database Integration**
   - PostgreSQL + PostGIS for spatial data
   - SQLAlchemy ORM
   - Alembic migrations

2. **Authentication**
   - JWT tokens
   - OAuth2 integration
   - Role-based access control

3. **WebSocket Support**
   - Real-time updates
   - Progress notifications for long-running tasks

4. **Background Tasks**
   - Celery for async processing
   - Redis for task queue

5. **API Documentation**
   - Interactive Swagger UI (built-in)
   - ReDoc (built-in)
   - Custom API documentation

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [GeoPandas Documentation](https://geopandas.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

**Last Updated**: November 12, 2025  
**Version**: 2.0.0
