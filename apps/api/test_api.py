from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_project():
    response = client.post("/api/v1/projects", json={"name": "Test", "instructions": "Be concise"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"

def test_create_run_validation():
    response = client.post("/api/v1/runs", json={"model_id": "m", "dataset_id": "d", "epochs": 0})
    assert response.status_code == 422
