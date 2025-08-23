"""Tests for SBZET API endpoints"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and version endpoints"""

    def test_version_endpoint(self):
        """Test /version endpoint"""
        response = client.get("/version")
        assert response.status_code == 200

        data = response.json()
        assert "version" in data
        assert "time" in data
        assert "uptime_sec" in data
        assert "name" in data
        assert data["name"] == "SENKRONX_PLUS API"

    def test_healthz_details(self):
        """Test /healthz/details endpoint"""
        response = client.get("/healthz/details")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "services" in data

        services = data["services"]
        assert services["api"] is True
        assert services["sbzet_quantum"] is True
        assert services["timeline_engine"] is True
        assert services["unified_predictor"] is True
        assert services["ephemeris_engine"] is True


class TestPredictEndpoint:
    """Test POST /predict endpoint"""

    def test_predict_basic(self):
        """Test basic prediction request"""
        payload = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "E": 5.0,
            "delta_g": 0.1,
            "D": 2.0
        }

        response = client.post("/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "astro" in data
        assert "quant" in data
        assert "final" in data
        assert "weights" in data
        assert "metadata" in data
        assert "version" in data
        assert "timestamp" in data
        assert "sbzet_version" in data

        assert 0.0 <= data["astro"] <= 1.0
        assert 0.0 <= data["quant"] <= 1.0
        assert 0.0 <= data["final"] <= 1.0
        assert data["sbzet_version"] == "v2025.9"

    def test_predict_custom_weights(self):
        """Test prediction with custom weights"""
        payload = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "E": 5.0,
            "delta_g": 0.1,
            "D": 2.0,
            "weights": [0.3, 0.7]
        }

        response = client.post("/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["weights"] == [0.3, 0.7]

    def test_predict_invalid_date_format(self):
        """Test prediction with invalid date format"""
        payload = {
            "start_date": "invalid-date",
            "end_date": "2024-01-31",
            "E": 5.0,
            "delta_g": 0.1,
            "D": 2.0
        }

        response = client.post("/predict", json=payload)
        assert response.status_code == 400
        assert "Geçersiz parametre" in response.json()["detail"]

    def test_predict_invalid_date_range(self):
        """Test prediction with invalid date range"""
        payload = {
            "start_date": "2024-01-31",
            "end_date": "2024-01-01",  # End before start
            "E": 5.0,
            "delta_g": 0.1,
            "D": 2.0
        }

        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or data["final"] == 0.0

    def test_predict_missing_fields(self):
        """Test prediction with missing required fields"""
        payload = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }

        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error


class TestPatternsEndpoint:
    """Test GET /patterns endpoint"""

    def test_patterns_basic(self):
        """Test basic pattern discovery request"""
        response = client.get("/patterns?start=2024-01-01&end=2024-12-31")
        assert response.status_code == 200

        data = response.json()
        assert "period" in data
        assert "windows" in data
        assert "patterns" in data
        assert "pattern_count" in data
        assert "version" in data
        assert "timestamp" in data

        assert data["period"]["start"] == "2024-01-01"
        assert data["period"]["end"] == "2024-12-31"
        assert "window_a" in data["windows"]
        assert "window_b" in data["windows"]
        assert isinstance(data["patterns"], list)
        assert isinstance(data["pattern_count"], int)

    def test_patterns_narrow_range(self):
        """Test pattern discovery with narrow date range"""
        response = client.get("/patterns?start=2024-02-01&end=2024-02-28")
        assert response.status_code == 200

        data = response.json()
        assert data["period"]["start"] == "2024-02-01"
        assert data["period"]["end"] == "2024-02-28"

    def test_patterns_invalid_date_format(self):
        """Test patterns with invalid date format"""
        response = client.get("/patterns?start=invalid&end=2024-12-31")
        assert response.status_code == 400
        assert "Geçersiz tarih formatı" in response.json()["detail"]

    def test_patterns_missing_params(self):
        """Test patterns with missing parameters"""
        response = client.get("/patterns")
        assert response.status_code == 422  # Missing required query params

    def test_patterns_future_dates(self):
        """Test patterns with future dates (should work but return fewer events)"""
        response = client.get("/patterns?start=2025-01-01&end=2025-12-31")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["patterns"], list)


class TestEndpointIntegration:
    """Test endpoint integration scenarios"""

    def test_predict_then_patterns(self):
        """Test using predict and patterns endpoints together"""
        predict_payload = {
            "start_date": "2024-06-01",
            "end_date": "2024-06-30",
            "E": 6.0,
            "delta_g": 0.2,
            "D": 1.5
        }

        predict_response = client.post("/predict", json=predict_payload)
        assert predict_response.status_code == 200

        patterns_response = client.get("/patterns?start=2024-06-01&end=2024-06-30")
        assert patterns_response.status_code == 200

        predict_data = predict_response.json()
        patterns_data = patterns_response.json()

        assert "final" in predict_data
        assert "patterns" in patterns_data
