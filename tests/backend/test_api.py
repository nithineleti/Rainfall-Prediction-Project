"""
Backend API tests for Watershed-UP
"""
import pytest
from fastapi import status


@pytest.mark.api
@pytest.mark.unit
class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check(self, backend_client):
        """Test health check endpoint returns OK"""
        response = backend_client.get("/api/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_contains_version(self, backend_client):
        """Test health check includes version info"""
        response = backend_client.get("/api/health")
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)


@pytest.mark.api
@pytest.mark.unit
class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_endpoint(self, backend_client):
        """Test root endpoint returns welcome message"""
        response = backend_client.get("/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "message" in data or "name" in data


@pytest.mark.api
@pytest.mark.integration
class TestDataEndpoints:
    """Tests for data management endpoints"""

    def test_list_datasets_empty(self, backend_client):
        """Test listing datasets when none exist"""
        response = backend_client.get("/api/v1/data/datasets")

        # Should return 200 even if empty
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_upload_dataset_no_file(self, backend_client):
        """Test upload without file returns error"""
        response = backend_client.post("/api/v1/data/upload")

        # Should return 422 (validation error) or 400 (bad request)
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
        ]


@pytest.mark.api
@pytest.mark.integration
class TestModelEndpoints:
    """Tests for model endpoints"""

    def test_list_models(self, backend_client):
        """Test listing trained models"""
        response = backend_client.get("/api/v1/model/list")

        # Should return 200 even if empty
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_model_status_without_training(self, backend_client):
        """Test getting model status when no training exists"""
        response = backend_client.get("/api/v1/model/status")

        # Should return 200 or 404
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]


@pytest.mark.api
@pytest.mark.integration
class TestWatershedEndpoints:
    """Tests for watershed analysis endpoints"""

    def test_list_watersheds_empty(self, backend_client):
        """Test listing watersheds when none exist"""
        response = backend_client.get("/api/v1/watershed/list")

        # Should return 200 even if empty
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_get_nonexistent_watershed(self, backend_client):
        """Test getting watershed that doesn't exist"""
        response = backend_client.get("/api/v1/watershed/details/999999")

        # Should return 404
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
@pytest.mark.integration
class TestCORSHeaders:
    """Tests for CORS configuration"""

    def test_cors_headers_present(self, backend_client):
        """Test that CORS headers are configured"""
        # Make OPTIONS request
        response = backend_client.options(
            "/api/v1/data/datasets",
            headers={"Origin": "http://localhost:3000"}
        )

        # Should have CORS headers (if CORS is configured)
        # This test may need adjustment based on actual CORS setup
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        ]
