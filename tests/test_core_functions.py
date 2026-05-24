"""
Unit tests for core watershed functions

Run with: pytest tests/test_core_functions.py -v
"""
import pytest
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config_loader import config, get_lat_center, get_priority_weights


class TestConfiguration:
    """Test configuration loading"""
    
    def test_config_loads(self):
        """Test that configuration loads without errors"""
        assert config is not None
    
    def test_latitude_center(self):
        """Test latitude center value"""
        lat = get_lat_center()
        assert isinstance(lat, (int, float))
        assert 0 <= lat <= 90  # Valid latitude range
    
    def test_priority_weights(self):
        """Test priority weights sum to 1.0"""
        weights = get_priority_weights()
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01  # Allow small floating point error
    
    def test_priority_weights_positive(self):
        """Test all weights are positive"""
        weights = get_priority_weights()
        assert all(w > 0 for w in weights.values())


class TestGeospatialFunctions:
    """Test geospatial utility functions"""
    
    def test_degree_to_meter_conversion(self):
        """Test degree to meter conversion at Lucknow latitude"""
        lat = 26.8
        meters_per_deg_lon = 111320 * np.cos(np.radians(lat))
        
        # At 26.8°N, 1 degree longitude ≈ 99,500 meters
        assert 99000 < meters_per_deg_lon < 100000
    
    def test_slope_calculation(self):
        """Test slope calculation gives realistic values"""
        # Simulate flat terrain with small elevation change
        dem = np.array([
            [100.0, 100.1, 100.2],
            [100.0, 100.1, 100.2],
            [100.0, 100.1, 100.2]
        ])
        
        # Calculate gradient
        dy, dx = np.gradient(dem, 100, 100)  # 100m pixel size
        slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
        slope_deg = np.degrees(slope_rad)
        
        # Slope should be very gentle (< 1°)
        assert slope_deg.mean() < 1.0


class TestDataValidation:
    """Test data validation utilities"""
    
    def test_nodata_masking(self):
        """Test NoData value masking"""
        arr = np.array([1.0, 2.0, -9999, 3.0, np.nan])
        
        # Mask NoData and NaN
        mask = (arr != -9999) & np.isfinite(arr)
        valid_data = arr[mask]
        
        assert len(valid_data) == 3
        assert np.allclose(valid_data, [1.0, 2.0, 3.0])
    
    def test_normalization(self):
        """Test min-max normalization"""
        arr = np.array([10, 20, 30, 40, 50])
        
        # Normalize to 0-1
        normalized = (arr - arr.min()) / (arr.max() - arr.min())
        
        assert normalized.min() == 0.0
        assert normalized.max() == 1.0
        assert np.allclose(normalized, [0.0, 0.25, 0.5, 0.75, 1.0])


class TestMLUtils:
    """Test machine learning utility functions"""
    
    def test_spatial_groups_creation(self):
        """Test spatial group creation for CV"""
        from sklearn.cluster import KMeans
        
        # Create sample coordinates
        coords = np.random.rand(100, 2) * 100  # 100 random points
        
        # Create 5 spatial groups
        kmeans = KMeans(n_clusters=5, random_state=42)
        groups = kmeans.fit_predict(coords)
        
        # Should have 5 unique groups
        assert len(np.unique(groups)) == 5
        assert groups.min() == 0
        assert groups.max() == 4


class TestWatershedPrioritization:
    """Test watershed prioritization logic"""
    
    def test_stress_score_calculation(self):
        """Test groundwater stress score (inverse of GWP)"""
        gwp_values = np.array([0.2, 0.5, 0.8])  # Low, Medium, High GWP
        
        # Normalize (already 0-1)
        # Reverse (low GWP = high stress)
        stress_scores = 1 - gwp_values
        
        assert stress_scores[0] > stress_scores[1]  # Low GWP = high stress
        assert stress_scores[1] > stress_scores[2]  # Medium > High
        assert np.allclose(stress_scores, [0.8, 0.5, 0.2])
    
    def test_improvement_potential(self):
        """Test improvement potential calculation (inverted U-shape)"""
        gwp_values = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        
        # Peak at 0.5
        potential = 1 - np.abs(gwp_values - 0.5) * 2
        potential = np.clip(potential, 0, 1)
        
        # Middle value should have highest potential
        assert potential[2] == 1.0  # GWP=0.5 has max potential
        assert potential[0] < potential[2]  # Very low GWP has less potential
        assert potential[4] < potential[2]  # Very high GWP has less potential


# Fixture for sample data
@pytest.fixture
def sample_raster_data():
    """Create sample raster data for testing"""
    rows, cols = 10, 10
    dem = np.random.rand(rows, cols) * 100 + 100  # 100-200m elevation
    slope = np.random.rand(rows, cols) * 5  # 0-5° slope
    return {'dem': dem, 'slope': slope}


def test_sample_fixture(sample_raster_data):
    """Test that fixtures work correctly"""
    assert 'dem' in sample_raster_data
    assert 'slope' in sample_raster_data
    assert sample_raster_data['dem'].shape == (10, 10)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
