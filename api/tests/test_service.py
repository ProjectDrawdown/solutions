from starlette.testclient import TestClient

from api.service import app

client = TestClient(app)

def test_solutions():
    response = client.get("/solutions/solarpvutil")
    assert response.status_code == 200
    assert 'solarpvutil' in response.json() 
