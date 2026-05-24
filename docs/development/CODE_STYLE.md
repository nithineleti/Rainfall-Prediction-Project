# Code Style Guide

This document defines coding standards and style guidelines for the Watershed Prioritization project.

---

## General Principles

1. **Readability First**: Code is read more than written
2. **Consistency**: Follow existing patterns
3. **Simplicity**: Prefer simple over clever
4. **Documentation**: Code should be self-documenting
5. **Testing**: Write testable code

---

## Python Style Guide

### PEP 8 Compliance

**All Python code must follow [PEP 8](https://peps.python.org/pep-0008/)**

### Formatting

**Use Black** for automatic formatting:

```bash
# Format all Python files
black .

# Check without modifying
black --check .

# Format specific file
black backend/app/main.py
```

**Black Configuration** (`.black.toml` or `pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
```

### Line Length

**Maximum**: 100 characters (Black default)

**Exceptions**:
- Long URLs in comments
- Import statements (but try to break)

### Naming Conventions

**Files and Modules**:
```python
# Good
watershed_service.py
feature_extraction.py
dem_processing.py

# Bad
WatershedService.py
featureExtraction.py
DEMProcessing.py
```

**Classes**:
```python
# Good
class WatershedService:
class PredictionModel:
class DataLoader:

# Bad
class watershed_service:
class predictionModel:
class data_loader:
```

**Functions and Variables**:
```python
# Good
def calculate_drainage_density(watershed):
    flow_accumulation = get_flow_accumulation()
    total_length = sum_stream_lengths()
    
# Bad
def CalculateDrainageDensity(Watershed):
    FlowAccumulation = GetFlowAccumulation()
    TotalLength = SumStreamLengths()
```

**Constants**:
```python
# Good
MAX_PAGE_SIZE = 100
DEFAULT_CRS = "EPSG:32644"
FEATURE_COUNT = 17

# Bad
max_page_size = 100
defaultCrs = "EPSG:32644"
featureCount = 17
```

**Private Methods**:
```python
class WatershedService:
    def public_method(self):
        """Public method."""
        pass
    
    def _private_method(self):
        """Private method (internal use)."""
        pass
    
    def __internal_method(self):
        """Name-mangled method (very private)."""
        pass
```

### Imports

**Order** (as per PEP 8 and isort):

```python
# 1. Standard library
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict

# 2. Third-party libraries
import numpy as np
import pandas as pd
import geopandas as gpd
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

# 3. Local imports
from app.services import WatershedService
from app.models.schemas import WatershedBase
from app.utils.spatial import calculate_area
```

**Use isort**:
```bash
# Sort imports
isort .

# Check without modifying
isort --check-only .
```

**Avoid wildcard imports**:
```python
# Bad
from module import *

# Good
from module import specific_function, SpecificClass
```

### Type Hints

**Always use type hints** for function signatures:

```python
from typing import List, Optional, Dict, Tuple

def get_watersheds(
    page: int,
    page_size: int,
    priority: Optional[str] = None
) -> Dict[str, any]:
    """Get watersheds with type hints."""
    pass

def calculate_area(
    geometry: gpd.GeoSeries
) -> float:
    """Calculate area in km²."""
    pass

def extract_features(
    raster_path: Path,
    points: gpd.GeoDataFrame
) -> List[Dict[str, float]]:
    """Extract feature values at points."""
    pass
```

**Use type annotations for class attributes**:

```python
from typing import Optional

class WatershedService:
    data_path: Path
    cache: Optional[Dict] = None
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.cache = {}
```

### Docstrings

**Use Google-style docstrings**:

```python
def calculate_drainage_density(
    watershed: gpd.GeoDataFrame,
    streams: gpd.GeoDataFrame
) -> float:
    """Calculate drainage density for a watershed.
    
    Drainage density is the total length of streams divided by watershed area.
    
    Args:
        watershed: GeoDataFrame containing single watershed polygon
        streams: GeoDataFrame containing stream network
        
    Returns:
        Drainage density in km/km²
        
    Raises:
        ValueError: If watershed or streams are empty
        
    Example:
        >>> watershed = gpd.read_file('watershed.gpkg')
        >>> streams = gpd.read_file('streams.gpkg')
        >>> density = calculate_drainage_density(watershed, streams)
        >>> print(f"Drainage density: {density:.2f} km/km²")
    """
    if watershed.empty or streams.empty:
        raise ValueError("Watershed and streams cannot be empty")
    
    area_km2 = watershed.geometry.area[0] / 1e6
    total_length_km = streams.geometry.length.sum() / 1000
    
    return total_length_km / area_km2
```

**Class docstrings**:

```python
class WatershedService:
    """Service for managing watershed data and operations.
    
    This service handles loading, filtering, and analyzing watershed data
    from GeoPackage files. It provides caching for improved performance.
    
    Attributes:
        data_path: Path to watershed GeoPackage file
        cache: In-memory cache for loaded data
        
    Example:
        >>> service = WatershedService(Path('watersheds.gpkg'))
        >>> watersheds = service.get_watersheds(page=1, page_size=20)
        >>> print(f"Found {len(watersheds)} watersheds")
    """
    
    def __init__(self, data_path: Path):
        """Initialize watershed service.
        
        Args:
            data_path: Path to GeoPackage file
        """
        self.data_path = data_path
        self.cache = {}
```

### Error Handling

**Use specific exceptions**:

```python
# Good
try:
    watershed = load_watershed(id)
except FileNotFoundError:
    logger.error(f"Watershed file not found: {id}")
    raise
except ValueError as e:
    logger.error(f"Invalid watershed ID: {id} - {e}")
    raise
    
# Bad
try:
    watershed = load_watershed(id)
except Exception as e:
    pass  # Silent failure
```

**Raise meaningful exceptions**:

```python
# Good
if longitude < -180 or longitude > 180:
    raise ValueError(
        f"Longitude {longitude} out of range. Must be between -180 and 180."
    )

# Bad
if longitude < -180 or longitude > 180:
    raise Exception("Bad longitude")
```

**Use custom exceptions**:

```python
class WatershedNotFoundError(Exception):
    """Raised when watershed cannot be found."""
    pass

class InvalidCoordinateError(ValueError):
    """Raised when coordinates are invalid."""
    pass

# Usage
raise WatershedNotFoundError(f"Watershed {id} not found in database")
```

### Logging

**Use logging, not print**:

```python
import logging

logger = logging.getLogger(__name__)

# Good
logger.info("Processing watershed %d", watershed_id)
logger.error("Failed to load data: %s", error, exc_info=True)

# Bad
print(f"Processing watershed {watershed_id}")
print(f"Error: {error}")
```

**Log levels**:

```python
logger.debug("Detailed debug information")    # Development
logger.info("Processing started")             # General info
logger.warning("Unexpected value encountered") # Warnings
logger.error("Operation failed")              # Errors
logger.critical("System failure")             # Critical failures
```

### Code Organization

**Function length**: Keep functions < 50 lines

```python
# Good - Small, focused function
def calculate_area(geometry: gpd.GeoSeries) -> float:
    """Calculate area in km²."""
    return geometry.area[0] / 1e6

# Bad - Too long, do too much
def process_watershed(watershed):
    # 200 lines of mixed concerns...
```

**Single Responsibility Principle**:

```python
# Good - Each function does one thing
def load_data(path: Path) -> gpd.GeoDataFrame:
    """Load data from file."""
    return gpd.read_file(path)

def filter_by_priority(data: gpd.GeoDataFrame, priority: str) -> gpd.GeoDataFrame:
    """Filter by priority class."""
    return data[data['priority_class'] == priority]

def paginate(data: gpd.GeoDataFrame, page: int, page_size: int) -> gpd.GeoDataFrame:
    """Apply pagination."""
    start = (page - 1) * page_size
    end = start + page_size
    return data.iloc[start:end]

# Bad - One function does everything
def get_watersheds(path, priority, page, page_size):
    # Loads, filters, paginates all in one
```

---

## TypeScript Style Guide

### Airbnb Style

**Follow [Airbnb TypeScript Style Guide](https://github.com/airbnb/javascript)**

### Formatting

**Use Prettier** for automatic formatting:

```bash
# Format all TypeScript files
npm run format

# Check without modifying
npm run format:check
```

**Prettier Configuration** (`.prettierrc`):
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always"
}
```

### Naming Conventions

**Files**:
```typescript
// Components (PascalCase)
WatershedList.tsx
PredictionForm.tsx
AnalyticsDashboard.tsx

// Utilities (camelCase)
formatters.ts
validators.ts
apiClient.ts

// Types (camelCase)
watershed.ts
prediction.ts
```

**Components**:
```typescript
// Good - Functional components with arrow functions
const WatershedList: React.FC = () => {
  return <div>...</div>;
};

// Good - With props interface
interface WatershedListProps {
  onSelect: (id: number) => void;
}

const WatershedList: React.FC<WatershedListProps> = ({ onSelect }) => {
  return <div>...</div>;
};

// Bad - Class components (avoid unless necessary)
class WatershedList extends React.Component {
  render() {
    return <div>...</div>;
  }
}
```

**Variables and Functions**:
```typescript
// Good
const watershedData = fetchWatersheds();
const handleClick = () => {...};
const isLoading = false;

// Bad
const WatershedData = fetchWatersheds();
const HandleClick = () => {...};
const is_loading = false;
```

**Interfaces and Types**:
```typescript
// Good
interface Watershed {
  id: number;
  name: string;
}

type PriorityClass = 'High' | 'Medium' | 'Low';

// Bad
interface watershed {
  id: number;
}

type priority_class = string;
```

**Constants**:
```typescript
// Good
const MAX_PAGE_SIZE = 100;
const API_BASE_URL = 'http://localhost:8000';

// Bad
const maxPageSize = 100;
const apiBaseUrl = 'http://localhost:8000';
```

### Type Annotations

**Always use TypeScript features**:

```typescript
// Good - Explicit types
const fetchWatersheds = async (
  page: number,
  pageSize: number
): Promise<WatershedListResponse> => {
  const response = await apiClient.get('/watersheds', { params: { page, pageSize } });
  return response.data;
};

// Bad - No types (defeats TypeScript purpose)
const fetchWatersheds = async (page, pageSize) => {
  const response = await apiClient.get('/watersheds', { params: { page, pageSize } });
  return response.data;
};
```

**Interface vs Type**:

```typescript
// Use interface for objects
interface Watershed {
  id: number;
  name: string;
  area: number;
}

// Use type for unions, primitives
type PriorityClass = 'High' | 'Medium' | 'Low';
type ID = number | string;
```

### React Best Practices

**Hooks**:

```typescript
// Good - Custom hooks
const useWatersheds = (page: number, pageSize: number) => {
  const [data, setData] = useState<Watershed[]>([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchData();
  }, [page, pageSize]);
  
  return { data, loading };
};

// Use in component
const WatershedList: React.FC = () => {
  const { data, loading } = useWatersheds(1, 20);
  
  if (loading) return <Spinner />;
  return <Table data={data} />;
};
```

**Props destructuring**:

```typescript
// Good
const WatershedCard: React.FC<{ watershed: Watershed }> = ({ watershed }) => {
  return <div>{watershed.name}</div>;
};

// Avoid
const WatershedCard: React.FC<{ watershed: Watershed }> = (props) => {
  return <div>{props.watershed.name}</div>;
};
```

**Event handlers**:

```typescript
// Good
const handleClick = useCallback((id: number) => {
  console.log(`Clicked: ${id}`);
}, []);

// Good - Inline for simple cases
<button onClick={() => console.log('clicked')}>Click</button>

// Bad - Creating function on every render
<button onClick={function() { console.log('clicked'); }}>Click</button>
```

---

## Linting

### Python (Flake8, Pylint)

**Install**:
```bash
pip install flake8 pylint mypy
```

**Run**:
```bash
# Flake8
flake8 backend/app/

# Pylint
pylint backend/app/

# MyPy (type checking)
mypy backend/app/
```

**Configuration** (`.flake8`):
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.venv
```

### TypeScript (ESLint)

**Install**:
```bash
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

**Run**:
```bash
npm run lint
npm run lint:fix
```

**Configuration** (`.eslintrc.json`):
```json
{
  "extends": [
    "airbnb-typescript",
    "plugin:@typescript-eslint/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "project": "./tsconfig.json"
  },
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```

---

## Pre-commit Hooks

**Install Husky**:
```bash
npm install --save-dev husky lint-staged
npx husky install
```

**Add pre-commit hook** (`.husky/pre-commit`):
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Python
black backend/ --check
flake8 backend/

# TypeScript
npm run lint
npm run type-check
```

**Lint-staged** (`package.json`):
```json
{
  "lint-staged": {
    "*.py": ["black", "flake8"],
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"]
  }
}
```

---

## Comments

**When to comment**:

```python
# Good - Explain WHY, not WHAT
# Use Haversine formula for accurate distance on sphere
distance = haversine(lat1, lon1, lat2, lon2)

# Bad - Obvious comment
# Calculate distance
distance = haversine(lat1, lon1, lat2, lon2)
```

**TODO comments**:

```python
# TODO(username): Add support for multi-polygon watersheds
# FIXME: This breaks for negative elevations
# HACK: Temporary workaround for GDAL bug
```

---

**Last Updated**: November 12, 2025
