from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_gospel_endpoint_returns_specific_date():
    response = client.get("/api/v1/gospel", params={"date": "2026-04-19"})

    assert response.status_code == 200
    assert response.json()["records"][0]["gospels"] == [
        {"citation": "Luke 24:13-35", "sources": ["USCCB"]}
    ]


def test_gospel_endpoint_defaults_to_today_provider():
    app.dependency_overrides.clear()

    from src.api.main import get_today

    app.dependency_overrides[get_today] = lambda: "2026-04-19"
    try:
        response = client.get("/api/v1/gospel")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["date"] == "2026-04-19"


def test_gospel_endpoint_returns_400_for_invalid_date():
    response = client.get("/api/v1/gospel", params={"date": "04/19/2026"})

    assert response.status_code == 400
    assert response.json()["detail"] == "date must be YYYY-MM-DD"


def test_gospel_endpoint_returns_404_for_unknown_date():
    response = client.get("/api/v1/gospel", params={"date": "2099-01-01"})

    assert response.status_code == 404
    assert response.json()["detail"] == "No Gospel metadata found for 2099-01-01"
