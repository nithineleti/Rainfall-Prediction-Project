# API Schemas

This document describes all request and response schemas used in the Watershed Prioritization API.

---

## Table of Contents

1. [Common Types](#common-types)
2. [Watershed Schemas](#watershed-schemas)
3. [Prediction Schemas](#prediction-schemas)
4. [Analytics Schemas](#analytics-schemas)
5. [Error Schemas](#error-schemas)

---

## Common Types

### Coordinate

Geographic coordinate in decimal degrees.

**TypeScript**:
```typescript
interface Coordinate {
  longitude: number;  // -180 to 180
  latitude: number;   // -90 to 90
}
```

**Python (Pydantic)**:
```python
from pydantic import BaseModel, Field

class Coordinate(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
```

---

### PriorityClass

Priority classification enum.

**Values**: `"High"`, `"Medium"`, `"Low"`

**TypeScript**:
```typescript
type PriorityClass = "High" | "Medium" | "Low";
```

**Python**:
```python
from enum import Enum

class PriorityClass(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
```

---

### PaginationParams

Common pagination parameters.

**TypeScript**:
```typescript
interface PaginationParams {
  page?: number;      // Default: 1, Min: 1
  page_size?: number; // Default: 20, Min: 1, Max: 100
}
```

**Python**:
```python
from pydantic import Field

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
```

---

### PaginatedResponse

Generic paginated response wrapper.

**TypeScript**:
```typescript
interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: T[];
}
```

**Python**:
```python
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[T]
```

---

## Watershed Schemas

### WatershedBase

Basic watershed information.

**TypeScript**:
```typescript
interface WatershedBase {
  watershed_id: number;
  area_km2: number;
  perimeter_km: number;
  priority_class: PriorityClass;
  priority_score: number;  // 0-1
  mean_elevation: number;
  mean_slope: number;
  drainage_density: number;
  lulc_forest_pct: number;
  lulc_agriculture_pct: number;
  mean_rainfall: number;
  gw_potential_mean: number; // 0-1
}
```

**Python**:
```python
class WatershedBase(BaseModel):
    watershed_id: int
    area_km2: float = Field(..., gt=0)
    perimeter_km: float = Field(..., gt=0)
    priority_class: PriorityClass
    priority_score: float = Field(..., ge=0, le=1)
    mean_elevation: float
    mean_slope: float = Field(..., ge=0, le=90)
    drainage_density: float = Field(..., ge=0)
    lulc_forest_pct: float = Field(..., ge=0, le=100)
    lulc_agriculture_pct: float = Field(..., ge=0, le=100)
    mean_rainfall: float = Field(..., ge=0)
    gw_potential_mean: float = Field(..., ge=0, le=1)
```

---

### WatershedDetail

Detailed watershed information.

**TypeScript**:
```typescript
interface WatershedDetail extends WatershedBase {
  basic_info: {
    elongation_ratio: number;
    compactness_coeff: number;
    form_factor: number;
  };
  priority: {
    class: PriorityClass;
    score: number;
    rank: number;
    percentile: number;
  };
  terrain: {
    mean_elevation: number;
    elevation_range: number;
    mean_slope: number;
    mean_aspect: number;
    relief_ratio: number;
  };
  drainage: {
    drainage_density: number;
    stream_frequency: number;
    bifurcation_ratio: number;
  };
  land_cover: {
    forest_pct: number;
    agriculture_pct: number;
    builtup_pct: number;
    water_pct: number;
    diversity_index: number;
  };
  climate: {
    mean_rainfall: number;
    rainfall_cv: number;
  };
  groundwater: {
    mean_potential: number;
    high_potential_pct: number;
    recommendation: string;
  };
  geometry?: GeoJSONGeometry;
}
```

**Python**:
```python
class BasicInfo(BaseModel):
    elongation_ratio: float
    compactness_coeff: float
    form_factor: float

class PriorityInfo(BaseModel):
    class_: PriorityClass = Field(..., alias='class')
    score: float = Field(..., ge=0, le=1)
    rank: int = Field(..., ge=1)
    percentile: float = Field(..., ge=0, le=100)

class TerrainInfo(BaseModel):
    mean_elevation: float
    elevation_range: float
    mean_slope: float = Field(..., ge=0, le=90)
    mean_aspect: float = Field(..., ge=0, le=360)
    relief_ratio: float

class DrainageInfo(BaseModel):
    drainage_density: float
    stream_frequency: float
    bifurcation_ratio: float

class LandCoverInfo(BaseModel):
    forest_pct: float = Field(..., ge=0, le=100)
    agriculture_pct: float = Field(..., ge=0, le=100)
    builtup_pct: float = Field(..., ge=0, le=100)
    water_pct: float = Field(..., ge=0, le=100)
    diversity_index: float

class ClimateInfo(BaseModel):
    mean_rainfall: float
    rainfall_cv: float

class GroundwaterInfo(BaseModel):
    mean_potential: float = Field(..., ge=0, le=1)
    high_potential_pct: float = Field(..., ge=0, le=100)
    recommendation: str

class WatershedDetail(WatershedBase):
    basic_info: BasicInfo
    priority: PriorityInfo
    terrain: TerrainInfo
    drainage: DrainageInfo
    land_cover: LandCoverInfo
    climate: ClimateInfo
    groundwater: GroundwaterInfo
    geometry: Optional[dict] = None  # GeoJSON geometry
```

---

### WatershedListResponse

Paginated list of watersheds.

**TypeScript**:
```typescript
interface WatershedListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  watersheds: WatershedBase[];
}
```

**Python**:
```python
class WatershedListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    watersheds: List[WatershedBase]
```

---

### WatershedGeometry

Watershed boundary as GeoJSON Feature.

**TypeScript**:
```typescript
interface WatershedGeometry {
  type: "Feature";
  properties: {
    watershed_id: number;
    priority_class: PriorityClass;
    area_km2: number;
  };
  geometry: {
    type: "Polygon" | "MultiPolygon";
    coordinates: number[][][] | number[][][][];
  };
}
```

**Python**:
```python
from geojson_pydantic import Feature, Polygon, MultiPolygon

class WatershedProperties(BaseModel):
    watershed_id: int
    priority_class: PriorityClass
    area_km2: float

class WatershedGeometry(Feature):
    properties: WatershedProperties
    geometry: Union[Polygon, MultiPolygon]
```

---

## Prediction Schemas

### PredictionRequest

Request for single-point prediction.

**TypeScript**:
```typescript
interface PredictionRequest {
  longitude: number;  // -180 to 180
  latitude: number;   // -90 to 90
}
```

**Python**:
```python
class PredictionRequest(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    
    class Config:
        json_schema_extra = {
            "example": {
                "longitude": 80.1234,
                "latitude": 13.4567
            }
        }
```

---

### PredictionResponse

Response from single-point prediction.

**TypeScript**:
```typescript
interface PredictionResponse {
  longitude: number;
  latitude: number;
  prediction: "High" | "Low";
  probability: number;       // 0-1
  confidence: "High" | "Medium" | "Low";
  features: {
    elevation: number;
    slope: number;
    aspect: number;
    curvature: number;
    tri: number;
    twi: number;
    flow_accumulation: number;
    drainage_density: number;
    lulc_forest_pct: number;
    lulc_agriculture_pct: number;
    lulc_builtup_pct: number;
    lulc_water_pct: number;
    lulc_diversity: number;
    annual_rainfall: number;
    rainfall_cv: number;
    geology_lithology: number;
    distance_to_streams: number;
  };
  recommendation: string;
  timestamp: string;         // ISO 8601 format
}
```

**Python**:
```python
from datetime import datetime

class FeatureValues(BaseModel):
    elevation: float
    slope: float
    aspect: float
    curvature: float
    tri: float
    twi: float
    flow_accumulation: float
    drainage_density: float
    lulc_forest_pct: float
    lulc_agriculture_pct: float
    lulc_builtup_pct: float
    lulc_water_pct: float
    lulc_diversity: float
    annual_rainfall: float
    rainfall_cv: float
    geology_lithology: int
    distance_to_streams: float

class PredictionResponse(BaseModel):
    longitude: float
    latitude: float
    prediction: Literal["High", "Low"]
    probability: float = Field(..., ge=0, le=1)
    confidence: Literal["High", "Medium", "Low"]
    features: FeatureValues
    recommendation: str
    timestamp: datetime
```

---

### BatchPredictionRequest

Request for batch predictions.

**TypeScript**:
```typescript
interface BatchPredictionRequest {
  points: Coordinate[];  // Max 100 points
}
```

**Python**:
```python
class BatchPredictionRequest(BaseModel):
    points: List[Coordinate] = Field(..., max_length=100)
    
    @validator('points')
    def validate_points(cls, v):
        if len(v) == 0:
            raise ValueError('At least one point is required')
        return v
```

---

### BatchPredictionResponse

Response from batch predictions.

**TypeScript**:
```typescript
interface BatchPredictionResponse {
  total: number;
  predictions: {
    longitude: number;
    latitude: number;
    prediction: "High" | "Low";
    probability: number;
  }[];
  summary: {
    high_count: number;
    low_count: number;
    mean_probability: number;
  };
  timestamp: string;
}
```

**Python**:
```python
class BatchPredictionItem(BaseModel):
    longitude: float
    latitude: float
    prediction: Literal["High", "Low"]
    probability: float = Field(..., ge=0, le=1)

class BatchSummary(BaseModel):
    high_count: int
    low_count: int
    mean_probability: float

class BatchPredictionResponse(BaseModel):
    total: int
    predictions: List[BatchPredictionItem]
    summary: BatchSummary
    timestamp: datetime
```

---

## Analytics Schemas

### SummaryStatistics

Overall watershed statistics.

**TypeScript**:
```typescript
interface SummaryStatistics {
  total_watersheds: number;
  total_area_km2: number;
  priority_distribution: {
    [key in PriorityClass]: {
      count: number;
      percentage: number;
      total_area_km2: number;
    };
  };
  terrain: {
    mean_elevation: number;
    mean_slope: number;
    elevation_range: [number, number];
  };
  land_cover: {
    mean_forest_pct: number;
    mean_agriculture_pct: number;
    mean_builtup_pct: number;
  };
  groundwater: {
    mean_potential: number;
    high_potential_area_km2: number;
    high_potential_pct: number;
  };
  timestamp: string;
}
```

**Python**:
```python
class PriorityStats(BaseModel):
    count: int
    percentage: float
    total_area_km2: float

class TerrainStats(BaseModel):
    mean_elevation: float
    mean_slope: float
    elevation_range: Tuple[float, float]

class LandCoverStats(BaseModel):
    mean_forest_pct: float
    mean_agriculture_pct: float
    mean_builtup_pct: float

class GroundwaterStats(BaseModel):
    mean_potential: float
    high_potential_area_km2: float
    high_potential_pct: float

class SummaryStatistics(BaseModel):
    total_watersheds: int
    total_area_km2: float
    priority_distribution: Dict[PriorityClass, PriorityStats]
    terrain: TerrainStats
    land_cover: LandCoverStats
    groundwater: GroundwaterStats
    timestamp: datetime
```

---

### PriorityDistribution

Priority distribution chart data.

**TypeScript**:
```typescript
interface PriorityDistribution {
  chart_data: {
    priority: PriorityClass;
    count: number;
    percentage: number;
    color: string;
  }[];
  total: number;
  timestamp: string;
}
```

**Python**:
```python
class PriorityChartData(BaseModel):
    priority: PriorityClass
    count: int
    percentage: float
    color: str  # Hex color

class PriorityDistribution(BaseModel):
    chart_data: List[PriorityChartData]
    total: int
    timestamp: datetime
```

---

### FeatureImportance

SHAP feature importance data.

**TypeScript**:
```typescript
interface FeatureImportance {
  features: {
    name: string;
    importance: number;
    rank: number;
  }[];
  total_features: number;
  timestamp: string;
}
```

**Python**:
```python
class FeatureImportanceItem(BaseModel):
    name: str
    importance: float = Field(..., ge=0, le=1)
    rank: int = Field(..., ge=1)

class FeatureImportance(BaseModel):
    features: List[FeatureImportanceItem]
    total_features: int
    timestamp: datetime
```

---

### ModelPerformance

Model performance metrics.

**TypeScript**:
```typescript
interface ModelPerformance {
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
  };
  confusion_matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
  };
  classification_report: {
    [className: string]: {
      precision: number;
      recall: number;
      "f1-score": number;
      support: number;
    };
  };
  model_info: {
    algorithm: string;
    version: string;
    features: number;
    training_samples: number;
    test_samples: number;
    trained_at: string;
  };
  timestamp: string;
}
```

**Python**:
```python
class Metrics(BaseModel):
    accuracy: float = Field(..., ge=0, le=1)
    precision: float = Field(..., ge=0, le=1)
    recall: float = Field(..., ge=0, le=1)
    f1_score: float = Field(..., ge=0, le=1)
    roc_auc: float = Field(..., ge=0, le=1)

class ConfusionMatrix(BaseModel):
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int

class ClassificationMetrics(BaseModel):
    precision: float
    recall: float
    f1_score: float = Field(..., alias='f1-score')
    support: int

class ModelInfo(BaseModel):
    algorithm: str
    version: str
    features: int
    training_samples: int
    test_samples: int
    trained_at: datetime

class ModelPerformance(BaseModel):
    metrics: Metrics
    confusion_matrix: ConfusionMatrix
    classification_report: Dict[str, ClassificationMetrics]
    model_info: ModelInfo
    timestamp: datetime
```

---

## Error Schemas

### ValidationError

Pydantic validation error (422).

**TypeScript**:
```typescript
interface ValidationError {
  detail: {
    loc: (string | number)[];
    msg: string;
    type: string;
    ctx?: Record<string, any>;
  }[];
  status_code: 422;
  timestamp: string;
}
```

**Python**:
```python
class ValidationErrorDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str
    ctx: Optional[Dict[str, Any]] = None

class ValidationError(BaseModel):
    detail: List[ValidationErrorDetail]
    status_code: int = 422
    timestamp: datetime
```

---

### HTTPError

General HTTP error response.

**TypeScript**:
```typescript
interface HTTPError {
  detail: string;
  status_code: number;
  timestamp: string;
  path?: string;
}
```

**Python**:
```python
class HTTPError(BaseModel):
    detail: str
    status_code: int
    timestamp: datetime
    path: Optional[str] = None
```

---

## Usage Examples

### TypeScript Type Definitions

Save as `src/types/api.ts`:

```typescript
// Copy all TypeScript interfaces from above
export type { 
  Coordinate,
  PriorityClass,
  WatershedBase,
  WatershedDetail,
  PredictionRequest,
  PredictionResponse,
  // ... etc
};
```

### Python Pydantic Models

Save as `backend/app/models/schemas.py`:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Literal, Tuple
from datetime import datetime
from enum import Enum

# Copy all Python classes from above
```

---

## Schema Validation

### Request Validation

All incoming requests are automatically validated against schemas.

**Invalid Request Example**:
```bash
curl -X POST http://localhost:8000/api/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{"longitude": 200, "latitude": 13.4567}'
```

**Error Response** (422):
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

### Response Validation

All responses are validated before sending to ensure consistency.

---

## OpenAPI Schema

Download the complete OpenAPI 3.0 schema:

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

Use with tools like:
- Postman
- Insomnia
- Swagger Editor
- OpenAPI Generator

---

**Last Updated**: November 12, 2025  
**API Version**: 2.0.0
