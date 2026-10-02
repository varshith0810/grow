from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_rankings():
    r = client.get("/api/market/rankings?period=day")
    assert r.status_code == 200
    assert len(r.json()["top"]) == 10

def test_stock():
    r = client.get("/api/stocks/RELIANCE")
    assert r.status_code == 200
    assert r.json()["quote"]["symbol"] == "RELIANCE"
