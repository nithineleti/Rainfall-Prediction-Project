"""
Backend configuration tests
"""
import pytest


@pytest.mark.unit
class TestBackendConfig:
    """Tests for backend configuration"""

    def test_config_loads(self):
        """Test that backend configuration loads successfully"""
        from backend.app.core.config import Settings

        settings = Settings()

        assert settings.APP_NAME == "Watershed-UP API"
        assert settings.VERSION is not None
        assert isinstance(settings.VERSION, str)

    def test_cors_origins_configured(self):
        """Test that CORS origins are properly configured"""
        from backend.app.core.config import Settings

        settings = Settings()

        assert len(settings.CORS_ORIGINS) > 0
        assert "http://localhost:3000" in settings.CORS_ORIGINS

    def test_data_directory_configured(self):
        """Test that data directory paths are configured"""
        from backend.app.core.config import Settings

        settings = Settings()

        assert settings.DATA_DIR is not None
        assert settings.RAW_DATA_DIR is not None
        assert settings.PROCESSED_DATA_DIR is not None

    def test_model_directory_configured(self):
        """Test that model directory is configured"""
        from backend.app.core.config import Settings

        settings = Settings()

        assert settings.MODELS_DIR is not None
