"""
SENKRON API Test Suite
/version ve /healthz/details endpoint'lerini test eder
"""

import pytest
from fastapi.testclient import TestClient

from app import __version__
from app.main import app

# Test client oluştur
client = TestClient(app)


class TestVersionEndpoint:
    """Version endpoint testleri"""

    def test_version_endpoint_exists(self):
        """Version endpoint'inin mevcut olduğunu doğrula"""
        response = client.get("/version")
        assert response.status_code == 200

    def test_version_response_structure(self):
        """Version response yapısını doğrula"""
        response = client.get("/version")
        data = response.json()

        # Gerekli alanların varlığını kontrol et
        required_fields = [
            "version",
            "time",
            "uptime_sec",
            "started_at",
            "name",
            "node",
            "python",
        ]

        for field in required_fields:
            assert field in data, f"'{field}' alanı response'da bulunamadı"

    def test_version_value(self):
        """Version değerinin doğru olduğunu kontrol et"""
        response = client.get("/version")
        data = response.json()

        assert data["version"] == __version__
        assert data["name"] == "SENKRONX_PLUS API"

    def test_version_types(self):
        """Version response'daki veri tiplerini kontrol et"""
        response = client.get("/version")
        data = response.json()

        assert isinstance(data["version"], str)
        assert isinstance(data["time"], str)
        assert isinstance(data["uptime_sec"], (int, float))
        assert isinstance(data["started_at"], str)
        assert isinstance(data["name"], str)
        assert isinstance(data["node"], str)
        assert isinstance(data["python"], str)


class TestHealthzEndpoint:
    """Healthz endpoint testleri"""

    def test_healthz_endpoint_exists(self):
        """Healthz endpoint'inin mevcut olduğunu doğrula"""
        response = client.get("/healthz/details")
        assert response.status_code == 200

    def test_healthz_response_structure(self):
        """Healthz response yapısını doğrula"""
        response = client.get("/healthz/details")
        data = response.json()

        # Ana yapı kontrolü
        assert "status" in data
        assert "services" in data
        assert "notes" in data

    def test_healthz_status_ok(self):
        """Healthz status'ünün 'ok' olduğunu kontrol et"""
        response = client.get("/healthz/details")
        data = response.json()

        assert data["status"] == "ok"

    def test_healthz_services_structure(self):
        """Services yapısını kontrol et"""
        response = client.get("/healthz/details")
        data = response.json()

        services = data["services"]
        assert isinstance(services, dict)

        # Beklenen servisler
        expected_services = ["api", "ml_core", "db"]
        for service in expected_services:
            assert service in services
            assert isinstance(services[service], bool)

    def test_healthz_api_service_healthy(self):
        """API servisinin sağlıklı olduğunu kontrol et"""
        response = client.get("/healthz/details")
        data = response.json()

        # API servisi her zaman True olmalı
        assert data["services"]["api"] is True

    def test_healthz_notes_present(self):
        """Notes alanının mevcut olduğunu kontrol et"""
        response = client.get("/healthz/details")
        data = response.json()

        assert isinstance(data["notes"], str)
        assert len(data["notes"]) > 0


class TestAPIIntegration:
    """API entegrasyon testleri"""

    def test_multiple_version_calls(self):
        """Birden fazla version çağrısının tutarlı olduğunu test et"""
        import time

        response1 = client.get("/version")
        # Küçük bir bekleme süresi ekle
        time.sleep(0.01)
        response2 = client.get("/version")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # Version aynı kalmalı
        assert data1["version"] == data2["version"]
        assert data1["name"] == data2["name"]

        # Uptime değerleri pozitif olmalı
        assert data1["uptime_sec"] >= 0
        assert data2["uptime_sec"] >= 0

    def test_api_consistency(self):
        """API'nin tutarlı davrandığını test et"""
        # Her iki endpoint de çalışmalı
        version_response = client.get("/version")
        health_response = client.get("/healthz/details")

        assert version_response.status_code == 200
        assert health_response.status_code == 200

        # JSON formatında olmalı
        assert version_response.headers["content-type"] == "application/json"
        assert health_response.headers["content-type"] == "application/json"


# Pytest işaretleri
pytestmark = pytest.mark.unit
