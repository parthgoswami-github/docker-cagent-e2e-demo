from app.app import app


def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["service"] == "orders-api"


def test_health_in_development(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 503
    assert response.get_json()["status"] == "degraded"
