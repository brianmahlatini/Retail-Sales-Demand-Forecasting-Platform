from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_feature_explanation_endpoint():
    client = TestClient(app)
    response = client.get("/model/features")

    assert response.status_code == 200
    payload = response.json()
    assert payload["target"] == "sales_units"
    assert "lag_7" in payload["features"]

