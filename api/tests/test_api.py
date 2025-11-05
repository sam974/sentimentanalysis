import pytest
from fastapi.testclient import TestClient
from api.main import app # On importe notre application FastAPI

# --- La Correction (La Fixture) ---
#
# On crée un "fixture" pour nos tests.
# Le 'scope="module"' signifie que le code de démarrage (lifespan)
# ne s'exécutera qu'une seule fois pour tous les tests de ce fichier,
# au lieu de s'exécuter pour chaque test. C'est beaucoup plus rapide.
@pytest.fixture(scope="module")
def client():
    """
    Crée un TestClient qui respecte le cycle de vie (lifespan) de l'application.
    C'est la clé pour que app.state.model et app.state.tokenizer existent.
    """
    # L'utilisation de 'with' déclenche les événements 'startup' (lifespan)
    with TestClient(app) as test_client:
        yield test_client
    # Les événements 'shutdown' (lifespan) sont exécutés ici

# --- Vos tests, mis à jour pour utiliser le fixture 'client' ---

def test_prediction_positive(client): # <-- On injecte le fixture 'client'
    """Teste une prédiction pour un sentiment positif."""
    response = client.post("/predict/", json={"text": "I love this airline, the service is amazing!"})
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "Positif"
    assert data["text"] == "I love this airline, the service is amazing!"

def test_prediction_negative(client): # <-- On injecte le fixture 'client'
    """Teste une prédiction pour un sentiment négatif."""
    response = client.post("/predict/", json={"text": "My flight was delayed and I lost my luggage."})
    
    # Vérifications
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "Négatif"
    assert data["text"] == "My flight was delayed and I lost my luggage."

def test_feedback_endpoint(client): # <-- On injecte le fixture 'client'
    """Teste le point de terminaison de feedback."""
    response = client.post("/feedback/", json={"text": "Test tweet", "prediction": "Positif"})
    
    # Vérifications
    assert response.status_code == 200
    assert response.json() == {"message": "Feedback reçu, merci !"}

def test_invalid_input(client): # <-- On injecte le fixture 'client'
    """Teste le cas où les données sont mal formatées."""
    response = client.post("/predict/", json={"wrong_key": "some text"})
    # Erreur de validation Pydantic/FastAPI
    assert response.status_code == 422