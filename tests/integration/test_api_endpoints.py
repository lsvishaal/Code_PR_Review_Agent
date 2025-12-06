"""Integration tests for API endpoints."""



class TestHealthEndpoints:
    """Tests for health and info endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns correct information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "CodeReview Agent API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "pr-review-agent"

    def test_version_endpoint(self, client):
        """Test version endpoint."""
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "version" in data
        assert "debug" in data

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Metrics should be in Prometheus format
        assert "http_requests_total" in response.text or "# TYPE" in response.text
