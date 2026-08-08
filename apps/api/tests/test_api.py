from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_project_lifecycle():
    created = client.post('/api/v1/projects', json={'name': 'Test', 'instructions': 'Be concise'})
    assert created.status_code == 201
    assert client.get('/api/v1/projects').status_code == 200


def test_memory_lifecycle():
    created = client.post('/api/v1/memory', json={'user_id': 'test-user', 'content': 'prefers concise answers'})
    assert created.status_code == 201
    assert len(client.get('/api/v1/memory/test-user').json()) == 1
    assert client.delete('/api/v1/memory/test-user').status_code == 204
