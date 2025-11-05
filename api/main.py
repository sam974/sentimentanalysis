# main.py

# --- 1. Imports ---
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging
import logging_loki

# --- Configuration du logging vers Loki ---
# L'URL pointe vers votre serveur Loki local
handler = logging_loki.LokiHandler(
    url="http://localhost:3100/loki/api/v1/push", 
    tags={"application": "sentiment-api"},
    version="1",
)

# On récupère le logger de base
logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# --- 2. Création de l'application FastAPI ---
app = FastAPI(
    title="API d'Analyse de Sentiment",
    description="Une API simple pour prédire le sentiment (positif/négatif) d'un texte basé sur un modèle DistilBERT.",
    version="1.0"
)

# --- 3. Chargement du modèle et du tokenizer (une seule fois au démarrage) ---
# C'est une optimisation cruciale : le modèle est chargé en mémoire une seule fois
# lorsque l'API démarre, et non à chaque requête.
# Définir le chemin absolu
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

print("Chargement du tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

print("Chargement du modèle...")
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval() # Mettre le modèle en mode évaluation est une bonne pratique

print("Modèle et tokenizer chargés avec succès !")

# --- 4. Définition du format des données d'entrée ---
# On utilise Pydantic pour définir la "carte d'identité" des données que l'API attend.
# Ici, nous attendons un objet JSON avec une clé "text" contenant une chaîne de caractères.
class TweetInput(BaseModel):
    text: str

class FeedbackInput(BaseModel):
    text: str
    prediction: str

# --- 5. Création du point de terminaison (endpoint) de prédiction ---
@app.post("/predict/")
def predict_sentiment(tweet: TweetInput):
    """
    Prédit le sentiment d'un tweet.
    - **text**: Le texte du tweet à analyser.
    - **return**: Un JSON avec le sentiment prédit et le score de confiance.
    """
    # Étape 1 : Préparer le texte avec le tokenizer
    inputs = tokenizer(tweet.text, return_tensors="pt", truncation=True, padding=True)

    # Étape 2 : Faire la prédiction avec le modèle
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Étape 3 : Traiter le résultat
    logits = outputs.logits
    predicted_class_id = torch.argmax(logits, dim=1).item()
    
    # Étape 4 : Mapper l'ID à une étiquette de sentiment claire
    sentiment = "Positif" if predicted_class_id == 1 else "Négatif"

    # Étape 5 : Renvoyer le résultat au format JSON
    return {
        "text": tweet.text,
        "sentiment": sentiment
    }

# --- Endpoint de feedback ---
@app.post("/feedback/")
def log_feedback(feedback: FeedbackInput):
    """
    Enregistre un feedback utilisateur comme un log d'erreur dans Loki.
    """
    logger.error(
        "Mauvaise prédiction signalée par l'utilisateur",
        extra={
            "tags": {"event": "bad_prediction"},
            "labels": { # Ces labels sont indexés et permettent de filtrer dans Grafana
                "tweet_text": feedback.text,
                "model_prediction": feedback.prediction
            }
        }
    )
    return {"message": "Feedback reçu, merci !"}