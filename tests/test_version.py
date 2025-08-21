from fastapi.testclient import TestClient
from app.main import app

def test_version_endpoint():
    client = TestClient(app)
    r = client.get("/version")
    assert r.status_code == 200
    data = r.json()
    assert "version" in data and "uptime_sec" in data
