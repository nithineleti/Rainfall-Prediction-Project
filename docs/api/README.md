# API Overview

Welcome to the **Watershed Prioritization API** documentation. This API provides programmatic access to groundwater potential analysis, watershed data, and ML predictions.

---

## Quick Start

### 1. Start the Backend Server

```bash
cd backend
python run.py
```

Server will start at: `http://localhost:8000`

### 2. Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# List watersheds
curl http://localhost:8000/api/watersheds

# Make a prediction
curl -X POST http://localhost:8000/api/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{"longitude": 80.1234, "latitude": 13.4567}'
```

### 3. Interactive Documentation

Visit `http://localhost:8000/docs` for **Swagger UI** with interactive testing.

---

## API Endpoints

### Health & Status

- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed system status

### Watersheds

- `GET /api/watersheds` - List watersheds (paginated)
- `GET /api/watersheds/{id}` - Get watershed details
- `GET /api/watersheds/{id}/geometry` - Get watershed boundary (GeoJSON)

### Predictions

- `POST /api/predictions/predict` - Predict for a single point
- `POST /api/predictions/batch` - Batch predictions
- `GET /api/predictions/map` - Get prediction raster image

### Analytics

- `GET /api/analytics/summary` - Overall statistics
- `GET /api/analytics/priority-distribution` - Priority distribution data
- `GET /api/analytics/feature-importance` - SHAP feature importance
- `GET /api/analytics/model-performance` - Model metrics

---

## Authentication

**Current**: No authentication required  
**Future**: JWT token-based authentication

**Planned Headers**:
```http
Authorization: Bearer <token>
```

---

## Response Format

All responses are JSON-formatted.

**Success Response**:
```json
{
  "field1": "value1",
  "field2": "value2",
  ...
}
```

**Error Response**:
```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

---

## Pagination

Lists are paginated with the following parameters:

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | - | Page number (1-indexed) |
| `page_size` | integer | 20 | 100 | Items per page |

**Response**:
```json
{
  "total": 520,
  "page": 1,
  "page_size": 20,
  "total_pages": 26,
  "items": [...]
}
```

---

## Rate Limiting

**Current**: No limits  
**Future**: 100 requests/minute per IP

---

## CORS

**Allowed Origins** (Development):
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative frontend)

**Production**: Configure via environment variable `CORS_ORIGINS`

---

## Examples

### Python

```python
import requests

# List high-priority watersheds
response = requests.get(
    "http://localhost:8000/api/watersheds",
    params={"priority": "high", "page_size": 50}
)
watersheds = response.json()

# Make prediction
prediction = requests.post(
    "http://localhost:8000/api/predictions/predict",
    json={"longitude": 80.1234, "latitude": 13.4567}
).json()

print(f"Prediction: {prediction['prediction']}")
print(f"Probability: {prediction['probability']:.2%}")
```

### JavaScript

```javascript
// List watersheds
const response = await fetch('http://localhost:8000/api/watersheds?priority=high');
const data = await response.json();

// Make prediction
const prediction = await fetch('http://localhost:8000/api/predictions/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ longitude: 80.1234, latitude: 13.4567 })
}).then(res => res.json());

console.log(`Prediction: ${prediction.prediction}`);
```

### cURL

```bash
# Get watersheds
curl "http://localhost:8000/api/watersheds?priority=high&page=1&page_size=20"

# Predict
curl -X POST "http://localhost:8000/api/predictions/predict" \
  -H "Content-Type: application/json" \
  -d '{"longitude": 80.1234, "latitude": 13.4567}'

# Get analytics
curl "http://localhost:8000/api/analytics/summary"
```

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Success |
| `400` | Bad Request | Invalid parameters |
| `404` | Not Found | Resource not found |
| `422` | Validation Error | Invalid request body |
| `500` | Server Error | Internal error |

---

## Documentation

- **Endpoints**: See [ENDPOINTS.md](./ENDPOINTS.md) for detailed endpoint documentation
- **Schemas**: See [SCHEMAS.md](./SCHEMAS.md) for request/response schemas
- **Interactive**: Visit `/docs` for Swagger UI
- **OpenAPI**: Download spec from `/openapi.json`

---

## Support

- **Issues**: Report bugs on GitHub
- **Questions**: Open a discussion on GitHub
- **Documentation**: Check `/docs` folder

---

## Version History

**v2.0.0** (2025-11-12): Current version
- FastAPI backend
- Watershed endpoints
- Prediction endpoints
- Analytics endpoints

**v1.0.0** (2025-10-15): Initial release
- Basic Streamlit API
- Limited functionality

---

**Last Updated**: November 12, 2025  
**API Version**: 2.0.0
