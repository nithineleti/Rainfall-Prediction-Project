"""
Feature engineering tests
"""
import pytest
import numpy as np
import pandas as pd


@pytest.mark.ml
@pytest.mark.feature
@pytest.mark.unit
class TestFeatureValidation:
    """Tests for feature validation"""

    def test_sample_data_has_all_features(self, sample_feature_data, ml_config):
        """Test that sample data contains all required features"""
        feature_names = ml_config["feature_names"]

        for feature in feature_names:
            assert feature in sample_feature_data.columns

    def test_feature_data_types(self, sample_feature_data):
        """Test that features have correct data types"""
        # All features should be numeric
        for column in sample_feature_data.columns:
            assert pd.api.types.is_numeric_dtype(
                sample_feature_data[column]
            ), f"{column} is not numeric"

    def test_no_missing_values_in_sample(self, sample_feature_data):
        """Test that sample data has no missing values"""
        assert sample_feature_data.isnull().sum().sum() == 0

    def test_feature_ranges_valid(self, sample_feature_data):
        """Test that features are within expected ranges"""
        # Elevation should be non-negative
        assert (sample_feature_data["elevation"] >= 0).all()

        # Slope should be 0-90 degrees
        assert (sample_feature_data["slope"] >= 0).all()
        assert (sample_feature_data["slope"] <= 90).all()

        # Aspect should be 0-360 degrees
        assert (sample_feature_data["aspect"] >= 0).all()
        assert (sample_feature_data["aspect"] <= 360).all()

        # NDVI should be -1 to 1
        assert (sample_feature_data["ndvi"] >= -1).all()
        assert (sample_feature_data["ndvi"] <= 1).all()


@pytest.mark.ml
@pytest.mark.feature
@pytest.mark.integration
class TestFeatureStackCreation:
    """Tests for feature stack creation"""

    def test_feature_stack_module_exists(self, project_root):
        """Test that feature stack module exists"""
        feature_stack_path = (
            project_root / "ml" / "src" / "features" / "feature_stack.py"
        )
        assert feature_stack_path.exists()

    @pytest.mark.skip(reason="Requires raster data")
    def test_create_feature_stack(self):
        """Test feature stack creation (integration test)"""
        # This would require actual raster data
        # Skip for now, implement later with test fixtures
        pass
