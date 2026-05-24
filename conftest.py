"""
Pytest configuration and fixtures for Watershed-UP tests
"""
import os
import sys
from pathlib import Path

import pytest

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# Session-level fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_dir(project_root):
    """Get test data directory"""
    test_data = project_root / "tests" / "data"
    test_data.mkdir(parents=True, exist_ok=True)
    return test_data


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    """Create temporary directory for test outputs"""
    return tmp_path_factory.mktemp("test_outputs")


# ============================================================================
# Backend fixtures
# ============================================================================

@pytest.fixture(scope="session")
def backend_app():
    """Create FastAPI test app"""
    try:
        from backend.app.main import app
        return app
    except ImportError:
        pytest.skip("Backend dependencies not available")


@pytest.fixture
def backend_client(backend_app):
    """Create FastAPI test client"""
    from fastapi.testclient import TestClient
    return TestClient(backend_app)


# ============================================================================
# ML fixtures
# ============================================================================

@pytest.fixture(scope="session")
def ml_config():
    """Get ML configuration"""
    import sys
    from pathlib import Path

    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    try:
        # Import config module directly
        from ml.src import config
        return {
            "project_root": config.PROJECT_ROOT,
            "feature_names": config.FEATURE_NAMES,
            "target_crs": config.TARGET_CRS,
            "resolution": config.RESOLUTION,
        }
    except Exception as e:
        pytest.skip(f"ML dependencies not available: {e}")


@pytest.fixture
def sample_feature_data():
    """Create sample feature data for testing"""
    import numpy as np
    import pandas as pd

    # Create sample data with 17 features (matching config)
    np.random.seed(42)
    n_samples = 100

    data = {
        "elevation": np.random.uniform(0, 1000, n_samples),
        "slope": np.random.uniform(0, 45, n_samples),
        "aspect": np.random.uniform(0, 360, n_samples),
        "flow_accumulation": np.random.uniform(0, 10000, n_samples),
        "twi": np.random.uniform(0, 20, n_samples),
        "drainage_density": np.random.uniform(0, 5, n_samples),
        "stream_distance": np.random.uniform(0, 5000, n_samples),
        "geology": np.random.randint(1, 10, n_samples),
        "lulc": np.random.randint(1, 15, n_samples),
        "ndvi": np.random.uniform(-1, 1, n_samples),
        "rainfall": np.random.uniform(500, 2000, n_samples),
        "soil_type": np.random.randint(1, 8, n_samples),
        "watershed_area": np.random.uniform(1, 100, n_samples),
        "perimeter": np.random.uniform(5, 50, n_samples),
        "circularity": np.random.uniform(0, 1, n_samples),
        "elongation": np.random.uniform(0, 1, n_samples),
        "compactness": np.random.uniform(0, 1, n_samples),
    }

    return pd.DataFrame(data)


# ============================================================================
# Geospatial fixtures
# ============================================================================

@pytest.fixture
def sample_raster_path(data_dir):
    """Create a sample raster file for testing"""
    try:
        import numpy as np
        import rasterio
        from rasterio.transform import from_bounds

        # Create small test raster
        data = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        raster_path = data_dir / "test_raster.tif"

        # Define transform (small area in UTM 44N)
        transform = from_bounds(
            500000, 3000000, 503000, 3003000,  # 3km x 3km
            100, 100
        )

        # Write raster
        with rasterio.open(
            raster_path,
            "w",
            driver="GTiff",
            height=100,
            width=100,
            count=1,
            dtype=np.uint8,
            crs="EPSG:32644",
            transform=transform,
        ) as dst:
            dst.write(data, 1)

        return raster_path
    except ImportError:
        pytest.skip("Rasterio not available")


@pytest.fixture
def sample_vector_path(data_dir):
    """Create a sample vector file for testing"""
    try:
        import geopandas as gpd
        from shapely.geometry import Point

        # Create sample points
        points = [Point(500000 + i * 1000, 3000000 + i * 1000) for i in range(10)]
        gdf = gpd.GeoDataFrame(
            {"id": range(10), "value": np.random.rand(10)},
            geometry=points,
            crs="EPSG:32644",
        )

        vector_path = data_dir / "test_points.geojson"
        gdf.to_file(vector_path, driver="GeoJSON")

        return vector_path
    except ImportError:
        pytest.skip("Geopandas not available")


# ============================================================================
# Cleanup
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup resources after each test"""
    yield
    # Add any cleanup logic here if needed
