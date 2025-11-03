# tests/test_api.py
from fastapi.testclient import TestClient
from api.main import app # On importe notre application FastAPI

client = TestClient(app)

def test_prediction_positive():
    """Teste une prédiction pour un sentiment positif."""
    response = client.post("/predict/", json={"text": "I love this airline, the service is amazing!"})
    assert response.status_code == 200
    assert response.json()["sentiment"] == "Positif"

def test_prediction_negative():
    """Teste une prédiction pour un sentiment négatif."""
    response = client.post("/predict/", json={"text": "My flight was delayed and I lost my luggage."})
    assert response.status_code == 200
    assert response.json()["sentiment"] == "Négatif"

def test_invalid_input():
    """Teste le cas où les données sont mal formatées."""
    response = client.post("/predict/", json={"wrong_key": "some text"})
    assert response.status_code == 422 # Erreur de validation FastAPI