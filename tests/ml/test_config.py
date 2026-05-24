"""
ML configuration tests
"""
import pytest
from pathlib import Path


@pytest.mark.ml
@pytest.mark.unit
class TestMLConfig:
    """Tests for ML configuration"""

    def test_config_loads(self):
        """Test that ML configuration loads successfully"""
        import sys
        from pathlib import Path

        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from ml.src import config

        assert config.PROJECT_ROOT is not None
        assert config.FEATURE_NAMES is not None
        assert config.TARGET_CRS is not None

    def test_feature_names_complete(self):
        """Test that all required features are defined"""
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from ml.src import config

        feature_names = config.FEATURE_NAMES

        # Should have 17 features
        assert len(feature_names) == 17

        # Check for essential features
        essential_features = [
            "elevation",
            "slope",
            "aspect",
            "flow_accumulation",
            "rainfall",
        ]

        for feature in essential_features:
            assert feature in feature_names

    def test_target_crs_valid(self):
        """Test that target CRS is valid"""
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from ml.src import config

        target_crs = config.TARGET_CRS
        assert target_crs == "EPSG:32644"

    def test_resolution_configured(self):
        """Test that resolution is configured"""
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from ml.src import config

        resolution = config.RESOLUTION
        assert resolution == 30  # 30m for SRTM

    def test_project_paths_exist(self):
        """Test that project root exists"""
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from ml.src import config

        project_root = config.PROJECT_ROOT

        assert isinstance(project_root, Path)
        assert project_root.exists()


@pytest.mark.ml
@pytest.mark.unit
class TestDirectoryStructure:
    """Tests for ML directory structure"""

    def test_ml_src_exists(self, project_root):
        """Test that ml/src directory exists"""
        ml_src = project_root / "ml" / "src"
        assert ml_src.exists()
        assert ml_src.is_dir()

    def test_ml_modules_exist(self, project_root):
        """Test that all ML modules exist"""
        ml_src = project_root / "ml" / "src"

        required_modules = [
            "preprocessing",
            "features",
            "models",
            "watershed",
            "visualization",
            "utils",
        ]

        for module in required_modules:
            module_dir = ml_src / module
            assert module_dir.exists(), f"Module {module} does not exist"
            assert module_dir.is_dir()

            # Check for __init__.py
            init_file = module_dir / "__init__.py"
            assert init_file.exists(), f"Module {module} missing __init__.py"

    def test_config_file_exists(self, project_root):
        """Test that config.py exists"""
        config_file = project_root / "ml" / "src" / "config.py"
        assert config_file.exists()
