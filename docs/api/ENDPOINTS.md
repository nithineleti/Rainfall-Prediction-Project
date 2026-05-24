# API Documentation

## Overview

The Watershed Prioritization API is a RESTful service built with **FastAPI** that provides programmatic access to groundwater potential analysis, watershed data, and ML predictions.

**Base URL**: `http://localhost:8000` (Development)  
**API Version**: v2.0  
**Authentication**: None (future: JWT tokens)

---

## Table of Contents

1. [Health Check](#health-check)
2. [Watersheds](#watersheds)
3. [Predictions](#predictions)
4. [Analytics](#analytics)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)

---

## Health Check

### Check API Status

Check if the API is running and healthy.

**Endpoint**: `GET /api/health`

**Response** (`200 OK`):
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Example**:
```bash
curl http://localhost:8000/api/health
```

---

### Detailed Health Check

Get detailed system status including model availability and data readiness.

**Endpoint**: `GET /api/health/detailed`

**Response** (`200 OK`):
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-11-12T10:30:00Z",
  "components": {
    "model": {
      "status": "ready",
      "path": "/path/to/xgboost_model.json",
      "loaded_at": "2025-11-12T09:00:00Z"
    },
    "feature_stack": {
      "status": "ready",
      "bands": 17,
      "resolution": "30m"
    },
    "watersheds": {
      "status": "ready",
      "count": 520,
      "path": "/path/to/prioritized_watersheds.gpkg"
    }
  }
}
```

---

## Watersheds

### List Watersheds

Get a paginated list of watersheds with optional filtering.

**Endpoint**: `GET /api/watersheds`

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (starting from 1) |
| `page_size` | integer | No | 20 | Items per page (max: 100) |
| `priority` | string | No | - | Filter by priority: `high`, `medium`, `low` |
| `min_area` | float | No | - | Minimum area in km² |
| `max_area` | float | No | - | Maximum area in km² |
| `sort_by` | string | No | `priority_score` | Sort field |
| `sort_order` | string | No | `desc` | Sort order: `asc`, `desc` |

**Response** (`200 OK`):
```json
{
  "total": 520,
  "page": 1,
  "page_size": 20,
  "total_pages": 26,
  "watersheds": [
    {
      "watershed_id": 1,
      "area_km2": 45.3,
      "perimeter_km": 32.1,
      "priority_class": "High",
      "priority_score": 0.85,
      "mean_elevation": 234.5,
      "mean_slope": 12.3,
      "drainage_density": 2.45,
      "lulc_forest_pct": 45.2,
      "lulc_agriculture_pct": 32.1,
      "mean_rainfall": 1200.5,
      "gw_potential_mean": 0.78
    },
    // ... more watersheds
  ]
}
```

**Example**:
```bash
# Get first page with default settings
curl "http://localhost:8000/api/watersheds"

# Get high priority watersheds
curl "http://localhost:8000/api/watersheds?priority=high&page_size=50"

# Get large watersheds sorted by area
curl "http://localhost:8000/api/watersheds?min_area=50&sort_by=area_km2&sort_order=desc"
```

**Python Example**:
```python
import requests

response = requests.get(
    "http://localhost:8000/api/watersheds",
    params={"priority": "high", "page": 1, "page_size": 20}
)

data = response.json()
print(f"Total high-priority watersheds: {data['total']}")

for watershed in data['watersheds']:
    print(f"ID: {watershed['watershed_id']}, Score: {watershed['priority_score']}")
```

---

### Get Watershed Detail

Get detailed information for a specific watershed.

**Endpoint**: `GET /api/watersheds/{watershed_id}`

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `watershed_id` | integer | Yes | Unique watershed identifier |

**Response** (`200 OK`):
```json
{
  "watershed_id": 1,
  "basic_info": {
    "area_km2": 45.3,
    "perimeter_km": 32.1,
    "elongation_ratio": 0.78,
    "compactness_coeff": 1.23,
    "form_factor": 0.65
  },
  "priority": {
    "class": "High",
    "score": 0.85,
    "rank": 12,
    "percentile": 98
  },
  "terrain": {
    "mean_elevation": 234.5,
    "elevation_range": 180.3,
    "mean_slope": 12.3,
    "mean_aspect": 145.2,
    "relief_ratio": 0.056
  },
  "drainage": {
    "drainage_density": 2.45,
    "stream_frequency": 3.2,
    "bifurcation_ratio": 4.1
  },
  "land_cover": {
    "forest_pct": 45.2,
    "agriculture_pct": 32.1,
    "builtup_pct": 5.3,
    "water_pct": 2.1,
    "diversity_index": 1.82
  },
  "climate": {
    "mean_rainfall": 1200.5,
    "rainfall_cv": 0.23
  },
  "groundwater": {
    "mean_potential": 0.78,
    "high_potential_pct": 65.3,
    "recommendation": "High priority for development"
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[80.123, 13.456], [80.125, 13.458], ...]]
  }
}
```

**Error Response** (`404 Not Found`):
```json
{
  "detail": "Watershed 999 not found",
  "status_code": 404,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Example**:
```bash
curl "http://localhost:8000/api/watersheds/1"
```

---

### Get Watershed Geometry

Get the boundary geometry of a watershed as GeoJSON.

**Endpoint**: `GET /api/watersheds/{watershed_id}/geometry`

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `watershed_id` | integer | Yes | Unique watershed identifier |

**Response** (`200 OK`):
```json
{
  "type": "Feature",
  "properties": {
    "watershed_id": 1,
    "priority_class": "High",
    "area_km2": 45.3
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [80.12345, 13.45678],
        [80.12456, 13.45789],
        [80.12567, 13.45678],
        [80.12345, 13.45678]
      ]
    ]
  }
}
```

**Example**:
```bash
curl "http://localhost:8000/api/watersheds/1/geometry" > watershed_1.geojson
```

**Python Example**:
```python
import requests
import geopandas as gpd

response = requests.get("http://localhost:8000/api/watersheds/1/geometry")
geojson = response.json()

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame.from_features([geojson])
gdf.plot()
```

---

## Predictions

### Predict for Point

Predict groundwater potential for a specific geographic location.

**Endpoint**: `POST /api/predictions/predict`

**Request Body**:
```json
{
  "longitude": 80.1234,
  "latitude": 13.4567
}
```

**Request Body Schema**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `longitude` | float | Yes | -180 to 180 | Longitude in decimal degrees |
| `latitude` | float | Yes | -90 to 90 | Latitude in decimal degrees |

**Response** (`200 OK`):
```json
{
  "longitude": 80.1234,
  "latitude": 13.4567,
  "prediction": "High",
  "probability": 0.78,
  "confidence": "High",
  "features": {
    "elevation": 234.5,
    "slope": 12.3,
    "aspect": 145.2,
    "curvature": -0.002,
    "tri": 45.3,
    "twi": 8.9,
    "flow_accumulation": 1234.5,
    "drainage_density": 2.45,
    "lulc_forest_pct": 45.2,
    "lulc_agriculture_pct": 32.1,
    "lulc_builtup_pct": 5.3,
    "lulc_water_pct": 2.1,
    "lulc_diversity": 1.82,
    "annual_rainfall": 1200.5,
    "rainfall_cv": 0.23,
    "geology_lithology": 3,
    "distance_to_streams": 450.2
  },
  "recommendation": "Suitable for groundwater development",
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Confidence Levels**:
- `High`: Probability > 0.7 or < 0.3
- `Medium`: Probability 0.4-0.7 or 0.3-0.6
- `Low`: Probability 0.45-0.55

**Error Response** (`400 Bad Request`):
```json
{
  "detail": [
    {
      "loc": ["body", "longitude"],
      "msg": "ensure this value is less than or equal to 180",
      "type": "value_error.number.not_le"
    }
  ],
  "status_code": 400,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/predictions/predict" \
  -H "Content-Type: application/json" \
  -d '{"longitude": 80.1234, "latitude": 13.4567}'
```

**Python Example**:
```python
import requests

data = {"longitude": 80.1234, "latitude": 13.4567}
response = requests.post(
    "http://localhost:8000/api/predictions/predict",
    json=data
)

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Probability: {result['probability']:.2%}")
print(f"Recommendation: {result['recommendation']}")
```

---

### Batch Predictions

Predict groundwater potential for multiple locations.

**Endpoint**: `POST /api/predictions/batch`

**Request Body**:
```json
{
  "points": [
    {"longitude": 80.1234, "latitude": 13.4567},
    {"longitude": 80.2345, "latitude": 13.5678},
    {"longitude": 80.3456, "latitude": 13.6789}
  ]
}
```

**Request Constraints**:
- Maximum points per request: 100

**Response** (`200 OK`):
```json
{
  "total": 3,
  "predictions": [
    {
      "longitude": 80.1234,
      "latitude": 13.4567,
      "prediction": "High",
      "probability": 0.78
    },
    {
      "longitude": 80.2345,
      "latitude": 13.5678,
      "prediction": "Low",
      "probability": 0.32
    },
    {
      "longitude": 80.3456,
      "latitude": 13.6789,
      "prediction": "High",
      "probability": 0.85
    }
  ],
  "summary": {
    "high_count": 2,
    "low_count": 1,
    "mean_probability": 0.65
  },
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/predictions/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "points": [
      {"longitude": 80.1234, "latitude": 13.4567},
      {"longitude": 80.2345, "latitude": 13.5678}
    ]
  }'
```

---

### Get Prediction Map

Get the prediction probability raster as an image.

**Endpoint**: `GET /api/predictions/map`

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `format` | string | No | `png` | Output format: `png`, `jpeg`, `tiff` |
| `colormap` | string | No | `RdYlGn` | Matplotlib colormap name |
| `width` | integer | No | 800 | Image width in pixels |
| `height` | integer | No | 600 | Image height in pixels |

**Response** (`200 OK`):
- Content-Type: `image/png` (or appropriate MIME type)
- Binary image data

**Example**:
```bash
# Download as PNG
curl "http://localhost:8000/api/predictions/map?format=png" -o prediction_map.png

# Download as GeoTIFF
curl "http://localhost:8000/api/predictions/map?format=tiff" -o prediction_map.tif
```

**Python Example**:
```python
import requests
from PIL import Image
from io import BytesIO

response = requests.get(
    "http://localhost:8000/api/predictions/map",
    params={"format": "png", "colormap": "RdYlGn"}
)

image = Image.open(BytesIO(response.content))
image.show()
```

---

## Analytics

### Get Summary Statistics

Get overall statistics for the watershed dataset.

**Endpoint**: `GET /api/analytics/summary`

**Response** (`200 OK`):
```json
{
  "total_watersheds": 520,
  "total_area_km2": 12345.67,
  "priority_distribution": {
    "high": {
      "count": 145,
      "percentage": 27.88,
      "total_area_km2": 4532.1
    },
    "medium": {
      "count": 234,
      "percentage": 45.0,
      "total_area_km2": 5678.9
    },
    "low": {
      "count": 141,
      "percentage": 27.12,
      "total_area_km2": 2134.67
    }
  },
  "terrain": {
    "mean_elevation": 345.6,
    "mean_slope": 15.2,
    "elevation_range": [50.0, 1200.0]
  },
  "land_cover": {
    "mean_forest_pct": 38.5,
    "mean_agriculture_pct": 42.3,
    "mean_builtup_pct": 8.9
  },
  "groundwater": {
    "mean_potential": 0.62,
    "high_potential_area_km2": 6789.45,
    "high_potential_pct": 55.0
  },
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Example**:
```bash
curl "http://localhost:8000/api/analytics/summary"
```

---

### Get Priority Distribution

Get data for priority distribution chart.

**Endpoint**: `GET /api/analytics/priority-distribution`

**Response** (`200 OK`):
```json
{
  "chart_data": [
    {
      "priority": "High",
      "count": 145,
      "percentage": 27.88,
      "color": "#2e7d32"
    },
    {
      "priority": "Medium",
      "count": 234,
      "percentage": 45.0,
      "color": "#ed6c02"
    },
    {
      "priority": "Low",
      "count": 141,
      "percentage": 27.12,
      "color": "#d32f2f"
    }
  ],
  "total": 520,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Example**:
```bash
curl "http://localhost:8000/api/analytics/priority-distribution"
```

---

### Get Feature Importance

Get SHAP feature importance values.

**Endpoint**: `GET /api/analytics/feature-importance`

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `top_n` | integer | No | 10 | Number of top features to return |

**Response** (`200 OK`):
```json
{
  "features": [
    {
      "name": "Topographic Wetness Index (TWI)",
      "importance": 0.245,
      "rank": 1
    },
    {
      "name": "Flow Accumulation",
      "importance": 0.189,
      "rank": 2
    },
    {
      "name": "Drainage Density",
      "importance": 0.156,
      "rank": 3
    },
    {
      "name": "Annual Rainfall",
      "importance": 0.134,
      "rank": 4
    },
    {
      "name": "Elevation",
      "importance": 0.098,
      "rank": 5
    },
    {
      "name": "LULC - Agriculture %",
      "importance": 0.076,
      "rank": 6
    },
    {
      "name": "Slope",
      "importance": 0.054,
      "rank": 7
    },
    {
      "name": "Distance to Streams",
      "importance": 0.048,
      "rank": 8
    },
    {
      "name": "LULC - Forest %",
      "importance": 0.032,
      "rank": 9
    },
    {
      "name": "Geology - Lithology",
      "importance": 0.025,
      "rank": 10
    }
  ],
  "total_features": 17,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Example**:
```bash
# Get top 5 features
curl "http://localhost:8000/api/analytics/feature-importance?top_n=5"
```

---

### Get Model Performance

Get model performance metrics.

**Endpoint**: `GET /api/analytics/model-performance`

**Response** (`200 OK`):
```json
{
  "metrics": {
    "accuracy": 0.796,
    "precision": 0.82,
    "recall": 0.76,
    "f1_score": 0.79,
    "roc_auc": 0.85
  },
  "confusion_matrix": {
    "true_negatives": 420,
    "false_positives": 80,
    "false_negatives": 90,
    "true_positives": 310
  },
  "classification_report": {
    "Low": {
      "precision": 0.84,
      "recall": 0.82,
      "f1-score": 0.83,
      "support": 500
    },
    "High": {
      "precision": 0.82,
      "recall": 0.76,
      "f1-score": 0.79,
      "support": 400
    }
  },
  "model_info": {
    "algorithm": "XGBoost",
    "version": "2.0.1",
    "features": 17,
    "training_samples": 2700,
    "test_samples": 900,
    "trained_at": "2025-10-15T14:30:00Z"
  },
  "timestamp": "2025-11-12T10:30:00Z"
}
```

**Example**:
```bash
curl "http://localhost:8000/api/analytics/model-performance"
```

---

## Error Handling

### Error Response Format

All errors return JSON with the following structure:

```json
{
  "detail": "Error message or array of validation errors",
  "status_code": 400,
  "timestamp": "2025-11-12T10:30:00Z",
  "path": "/api/predictions/predict"
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200` | OK | Successful GET request |
| `201` | Created | Successful POST (created resource) |
| `400` | Bad Request | Invalid input, validation error |
| `404` | Not Found | Resource doesn't exist |
| `422` | Unprocessable Entity | Pydantic validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected server error |

### Common Errors

#### Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["body", "longitude"],
      "msg": "ensure this value is less than or equal to 180",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 180}
    }
  ],
  "status_code": 422,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

#### Not Found Error (404)

```json
{
  "detail": "Watershed 999 not found",
  "status_code": 404,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

#### Server Error (500)

```json
{
  "detail": "Internal server error",
  "status_code": 500,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

---

## Rate Limiting

**Current**: No rate limiting  
**Future**: 100 requests per minute per IP

**Rate Limit Headers** (future):
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699876800
```

---

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Client Libraries

### Python

```python
import requests

class WatershedAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_watersheds(self, page=1, page_size=20, priority=None):
        params = {"page": page, "page_size": page_size}
        if priority:
            params["priority"] = priority
        
        response = requests.get(f"{self.base_url}/api/watersheds", params=params)
        response.raise_for_status()
        return response.json()
    
    def predict(self, longitude, latitude):
        data = {"longitude": longitude, "latitude": latitude}
        response = requests.post(
            f"{self.base_url}/api/predictions/predict",
            json=data
        )
        response.raise_for_status()
        return response.json()

# Usage
api = WatershedAPI()
watersheds = api.get_watersheds(priority="high")
prediction = api.predict(80.1234, 13.4567)
```

### JavaScript

```javascript
class WatershedAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async getWatersheds(page = 1, pageSize = 20, priority = null) {
    const params = new URLSearchParams({ page, page_size: pageSize });
    if (priority) params.append('priority', priority);

    const response = await fetch(`${this.baseURL}/api/watersheds?${params}`);
    if (!response.ok) throw new Error('API request failed');
    return response.json();
  }

  async predict(longitude, latitude) {
    const response = await fetch(`${this.baseURL}/api/predictions/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ longitude, latitude }),
    });

    if (!response.ok) throw new Error('Prediction failed');
    return response.json();
  }
}

// Usage
const api = new WatershedAPI();
const watersheds = await api.getWatersheds(1, 20, 'high');
const prediction = await api.predict(80.1234, 13.4567);
```

---

**Last Updated**: November 12, 2025  
**API Version**: 2.0.0
