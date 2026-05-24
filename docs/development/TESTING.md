# Testing Guide

Comprehensive testing strategy and guidelines for the Watershed Prioritization project.

---

## Testing Philosophy

1. **Test-Driven Development (TDD)**: Write tests before/alongside code
2. **Coverage Goals**: Aim for >80% code coverage
3. **Fast Tests**: Unit tests should run in milliseconds
4. **Isolated Tests**: Each test should be independent
5. **Readable Tests**: Tests are documentation

---

## Backend Testing (Python)

### Test Framework: pytest

**Installation**:
```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

**Directory Structure**:
```
tests/
├── backend/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── test_main.py             # API endpoints
│   ├── test_services/
│   │   ├── test_watershed.py
│   │   └── test_prediction.py
│   ├── test_models/
│   │   └── test_schemas.py
│   └── test_utils/
│       ├── test_spatial.py
│       └── test_validators.py
└── ml/
    ├── test_preprocessing.py
    ├── test_features.py
    └── test_models.py
```

### Running Tests

**Basic usage**:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/backend/test_services/test_watershed.py

# Run specific test
pytest tests/backend/test_services/test_watershed.py::test_get_watersheds

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "watershed"

# Run only failed tests
pytest --lf

# Stop on first failure
pytest -x
```

**With coverage**:
```bash
# Generate coverage report
pytest --cov=backend --cov-report=html

# Coverage for specific module
pytest --cov=backend.app.services --cov-report=term-missing

# Minimum coverage threshold
pytest --cov=backend --cov-fail-under=80
```

### Writing Tests

**Basic test structure**:

```python
import pytest
from backend.app.services.watershed import WatershedService

def test_get_watersheds_returns_list():
    """Test that get_watersheds returns a list."""
    service = WatershedService()
    result = service.get_watersheds(page=1, page_size=10)
    
    assert isinstance(result, list)
    assert len(result) <= 10
    
def test_get_watersheds_pagination():
    """Test pagination works correctly."""
    service = WatershedService()
    
    page1 = service.get_watersheds(page=1, page_size=5)
    page2 = service.get_watersheds(page=2, page_size=5)
    
    assert len(page1) == 5
    assert len(page2) == 5
    assert page1[0]['id'] != page2[0]['id']  # Different data
```

**Test naming conventions**:

```python
# Good - Descriptive names
def test_calculate_drainage_density_returns_float():
def test_calculate_drainage_density_raises_error_for_empty_watershed():
def test_filter_by_priority_filters_correctly():

# Bad - Vague names
def test_drainage():
def test_filter():
def test_1():
```

### Fixtures

**Shared test data** (`conftest.py`):

```python
import pytest
import geopandas as gpd
from pathlib import Path

@pytest.fixture
def sample_watershed():
    """Create sample watershed for testing."""
    from shapely.geometry import Polygon
    
    polygon = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
    gdf = gpd.GeoDataFrame(
        {'id': [1], 'name': ['Test Watershed'], 'area_km2': [100.0]},
        geometry=[polygon],
        crs="EPSG:4326"
    )
    return gdf

@pytest.fixture
def sample_streams():
    """Create sample stream network for testing."""
    from shapely.geometry import LineString
    
    line = LineString([(0, 0), (1, 1)])
    gdf = gpd.GeoDataFrame(
        {'id': [1], 'stream_order': [3]},
        geometry=[line],
        crs="EPSG:4326"
    )
    return gdf

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir
```

**Using fixtures**:

```python
def test_calculate_drainage_density(sample_watershed, sample_streams):
    """Test drainage density calculation."""
    from backend.app.utils.spatial import calculate_drainage_density
    
    density = calculate_drainage_density(sample_watershed, sample_streams)
    
    assert isinstance(density, float)
    assert density > 0
```

### Mocking

**Mock external dependencies**:

```python
from unittest.mock import Mock, patch
import pytest

@patch('backend.app.services.watershed.gpd.read_file')
def test_load_watersheds_handles_file_not_found(mock_read_file):
    """Test handling of missing file."""
    mock_read_file.side_effect = FileNotFoundError("File not found")
    
    service = WatershedService()
    
    with pytest.raises(FileNotFoundError):
        service.load_watersheds()
    
    mock_read_file.assert_called_once()
```

**Mock database calls**:

```python
@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = Mock()
    session.query.return_value.filter.return_value.first.return_value = {
        'id': 1,
        'name': 'Test Watershed'
    }
    return session

def test_get_watershed_by_id(mock_db_session):
    """Test getting watershed by ID."""
    service = WatershedService(db=mock_db_session)
    watershed = service.get_by_id(1)
    
    assert watershed['id'] == 1
    assert watershed['name'] == 'Test Watershed'
```

### API Testing

**Test FastAPI endpoints**:

```python
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_watersheds_endpoint():
    """Test get watersheds endpoint."""
    response = client.get("/api/watersheds", params={"page": 1, "page_size": 10})
    
    assert response.status_code == 200
    data = response.json()
    assert "watersheds" in data
    assert "total" in data
    assert isinstance(data["watersheds"], list)

def test_get_watersheds_pagination():
    """Test pagination parameters."""
    response = client.get("/api/watersheds", params={"page": 1, "page_size": 5})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["watersheds"]) <= 5

def test_prediction_endpoint():
    """Test prediction endpoint."""
    payload = {
        "latitude": 18.5,
        "longitude": 79.5
    }
    response = client.post("/api/predictions/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert data["prediction"] in ["High", "Low"]
```

### Parametrized Tests

**Test multiple inputs**:

```python
import pytest

@pytest.mark.parametrize("priority,expected_count", [
    ("High", 15),
    ("Medium", 25),
    ("Low", 10),
])
def test_filter_by_priority(priority, expected_count):
    """Test filtering by different priority classes."""
    service = WatershedService()
    result = service.filter_by_priority(priority)
    
    assert len(result) == expected_count

@pytest.mark.parametrize("lat,lon,valid", [
    (18.5, 79.5, True),
    (18.0, 78.0, True),
    (91.0, 79.5, False),  # Invalid latitude
    (18.5, 181.0, False), # Invalid longitude
])
def test_validate_coordinates(lat, lon, valid):
    """Test coordinate validation."""
    from backend.app.utils.validators import validate_coordinates
    
    if valid:
        assert validate_coordinates(lat, lon) is True
    else:
        with pytest.raises(ValueError):
            validate_coordinates(lat, lon)
```

### Testing Exceptions

```python
import pytest

def test_watershed_not_found_raises_error():
    """Test error when watershed doesn't exist."""
    service = WatershedService()
    
    with pytest.raises(WatershedNotFoundError) as exc_info:
        service.get_by_id(99999)
    
    assert "not found" in str(exc_info.value).lower()

def test_invalid_coordinates_raises_valueerror():
    """Test error for invalid coordinates."""
    from backend.app.utils.validators import validate_coordinates
    
    with pytest.raises(ValueError) as exc_info:
        validate_coordinates(91.0, 79.5)
    
    assert "latitude" in str(exc_info.value).lower()
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_get_watersheds():
    """Test async watershed retrieval."""
    service = AsyncWatershedService()
    result = await service.get_watersheds(page=1, page_size=10)
    
    assert isinstance(result, list)
    assert len(result) <= 10
```

---

## Frontend Testing (TypeScript)

### Test Framework: Vitest + React Testing Library

**Installation**:
```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

**Configuration** (`vite.config.ts`):
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'src/test/'],
    },
  },
});
```

**Setup file** (`src/test/setup.ts`):
```typescript
import '@testing-library/jest-dom';
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Cleanup after each test
afterEach(() => {
  cleanup();
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Generate coverage
npm run test:coverage

# Run specific test file
npm test WatershedList.test.tsx

# UI mode
npm run test:ui
```

### Component Testing

**Basic component test**:

```typescript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import WatershedCard from '../components/WatershedCard';

describe('WatershedCard', () => {
  it('renders watershed name', () => {
    const watershed = {
      id: 1,
      name: 'Test Watershed',
      area_km2: 100.5,
      priority_class: 'High',
    };
    
    render(<WatershedCard watershed={watershed} />);
    
    expect(screen.getByText('Test Watershed')).toBeInTheDocument();
  });
  
  it('displays area correctly', () => {
    const watershed = {
      id: 1,
      name: 'Test Watershed',
      area_km2: 100.5,
      priority_class: 'High',
    };
    
    render(<WatershedCard watershed={watershed} />);
    
    expect(screen.getByText(/100.5 km²/i)).toBeInTheDocument();
  });
  
  it('applies correct priority color', () => {
    const watershed = {
      id: 1,
      name: 'Test Watershed',
      area_km2: 100.5,
      priority_class: 'High',
    };
    
    const { container } = render(<WatershedCard watershed={watershed} />);
    const priorityBadge = container.querySelector('.priority-badge');
    
    expect(priorityBadge).toHaveClass('priority-high');
  });
});
```

**User interaction testing**:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import PredictionForm from '../components/PredictionForm';

describe('PredictionForm', () => {
  it('calls onSubmit with form data', async () => {
    const handleSubmit = vi.fn();
    const user = userEvent.setup();
    
    render(<PredictionForm onSubmit={handleSubmit} />);
    
    // Enter coordinates
    const latInput = screen.getByLabelText(/latitude/i);
    const lonInput = screen.getByLabelText(/longitude/i);
    
    await user.type(latInput, '18.5');
    await user.type(lonInput, '79.5');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /predict/i });
    await user.click(submitButton);
    
    // Check callback
    expect(handleSubmit).toHaveBeenCalledWith({
      latitude: 18.5,
      longitude: 79.5,
    });
  });
  
  it('shows validation error for invalid coordinates', async () => {
    const user = userEvent.setup();
    render(<PredictionForm onSubmit={vi.fn()} />);
    
    const latInput = screen.getByLabelText(/latitude/i);
    await user.type(latInput, '95'); // Invalid latitude
    
    const submitButton = screen.getByRole('button', { name: /predict/i });
    await user.click(submitButton);
    
    expect(screen.getByText(/invalid latitude/i)).toBeInTheDocument();
  });
});
```

### Hook Testing

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import useWatersheds from '../hooks/useWatersheds';

describe('useWatersheds', () => {
  it('fetches watersheds on mount', async () => {
    const { result } = renderHook(() => useWatersheds(1, 20));
    
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(result.current.data).toBeInstanceOf(Array);
  });
  
  it('refetches on page change', async () => {
    const { result, rerender } = renderHook(
      ({ page, pageSize }) => useWatersheds(page, pageSize),
      { initialProps: { page: 1, pageSize: 20 } }
    );
    
    await waitFor(() => expect(result.current.loading).toBe(false));
    const initialData = result.current.data;
    
    rerender({ page: 2, pageSize: 20 });
    
    await waitFor(() => {
      expect(result.current.data).not.toBe(initialData);
    });
  });
});
```

### Mocking API Calls

```typescript
import { vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';

vi.mock('axios');

describe('WatershedService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('fetches watersheds from API', async () => {
    const mockData = {
      watersheds: [{ id: 1, name: 'Test' }],
      total: 1,
    };
    
    (axios.get as any).mockResolvedValue({ data: mockData });
    
    const service = new WatershedService();
    const result = await service.getWatersheds(1, 20);
    
    expect(result).toEqual(mockData);
    expect(axios.get).toHaveBeenCalledWith(
      '/api/watersheds',
      { params: { page: 1, page_size: 20 } }
    );
  });
  
  it('handles API errors', async () => {
    (axios.get as any).mockRejectedValue(new Error('Network error'));
    
    const service = new WatershedService();
    
    await expect(service.getWatersheds(1, 20)).rejects.toThrow('Network error');
  });
});
```

---

## ML Pipeline Testing

### Data Validation Tests

```python
import pytest
import numpy as np
import rasterio

def test_dem_has_no_nodata():
    """Test that processed DEM has no NoData values."""
    with rasterio.open('data/processed/dem_processed.tif') as src:
        dem = src.read(1)
        
        assert not np.isnan(dem).any()
        assert (dem != src.nodata).all()

def test_feature_stack_shape():
    """Test feature stack dimensions."""
    with rasterio.open('data/processed/feature_stack.tif') as src:
        assert src.count == 17  # 17 feature bands
        assert src.height > 0
        assert src.width > 0

def test_samples_balanced():
    """Test that training samples are reasonably balanced."""
    import pandas as pd
    
    samples = pd.read_csv('data/processed/samples_train.csv')
    
    class_counts = samples['label'].value_counts()
    ratio = class_counts.max() / class_counts.min()
    
    assert ratio < 3.0  # No more than 3:1 imbalance
```

### Model Tests

```python
import pytest
import joblib
import numpy as np

@pytest.fixture
def trained_model():
    """Load trained model."""
    return joblib.load('models/xgboost_model.pkl')

def test_model_prediction_shape(trained_model):
    """Test model output shape."""
    X = np.random.rand(10, 17)  # 10 samples, 17 features
    
    predictions = trained_model.predict(X)
    probabilities = trained_model.predict_proba(X)
    
    assert predictions.shape == (10,)
    assert probabilities.shape == (10, 2)  # 2 classes

def test_model_prediction_range(trained_model):
    """Test predictions are in valid range."""
    X = np.random.rand(100, 17)
    
    predictions = trained_model.predict(X)
    probabilities = trained_model.predict_proba(X)
    
    assert np.all(np.isin(predictions, [0, 1]))
    assert np.all(probabilities >= 0)
    assert np.all(probabilities <= 1)
    assert np.allclose(probabilities.sum(axis=1), 1.0)

def test_model_reproducibility(trained_model):
    """Test model produces same results for same input."""
    X = np.random.rand(10, 17)
    
    pred1 = trained_model.predict(X)
    pred2 = trained_model.predict(X)
    
    assert np.array_equal(pred1, pred2)
```

### Feature Engineering Tests

```python
def test_slope_calculation():
    """Test slope calculation produces valid values."""
    from ml.src.features.terrain import calculate_slope
    
    # Create simple DEM
    dem = np.array([
        [100, 100, 100],
        [100, 110, 100],
        [100, 100, 100]
    ])
    
    slope = calculate_slope(dem, cell_size=30)
    
    assert slope.shape == dem.shape
    assert np.all(slope >= 0)
    assert np.all(slope <= 90)  # Slope in degrees

def test_drainage_density():
    """Test drainage density calculation."""
    import geopandas as gpd
    from shapely.geometry import Polygon, LineString
    
    watershed = gpd.GeoDataFrame(
        geometry=[Polygon([(0, 0), (0, 1000), (1000, 1000), (1000, 0)])],
        crs="EPSG:32644"
    )
    streams = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (1000, 1000)])],
        crs="EPSG:32644"
    )
    
    from ml.src.features.drainage import calculate_drainage_density
    density = calculate_drainage_density(watershed, streams)
    
    assert isinstance(density, float)
    assert density > 0
```

---

## Integration Tests

**Test complete workflow**:

```python
def test_complete_prediction_workflow():
    """Test end-to-end prediction workflow."""
    # 1. Load model
    model = joblib.load('models/xgboost_model.pkl')
    
    # 2. Extract features at point
    lat, lon = 18.5, 79.5
    features = extract_features_at_point(lat, lon)
    
    # 3. Make prediction
    X = np.array([features])
    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0]
    
    # 4. Validate output
    assert prediction in [0, 1]
    assert 0 <= probability[prediction] <= 1
```

---

## CI/CD Testing

**GitHub Actions** (`.github/workflows/test.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test -- --coverage
```

---

## Coverage Goals

- **Unit Tests**: >80% coverage
- **Integration Tests**: Critical paths covered
- **End-to-End Tests**: Major workflows tested

**Check coverage**:
```bash
# Backend
pytest --cov=backend --cov-report=html
open htmlcov/index.html

# Frontend
npm run test:coverage
open coverage/index.html
```

---

**Last Updated**: November 12, 2025
