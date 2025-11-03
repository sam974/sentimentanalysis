# app.py

import streamlit as st
import requests

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Air Paradis - Analyse de Sentiment",
    page_icon="✈️",
    layout="centered"
)

# 1. Initialiser le "session state" pour garder les infos en mémoire
if 'sentiment' not in st.session_state:
    st.session_state.sentiment = None
if 'last_analyzed_text' not in st.session_state:
    st.session_state.last_analyzed_text = ""

# --- Contenu de l'Application ---

# Titre principal
st.title("✈️ Analyseur de Sentiment pour Air Paradis")
st.write(
    "Entrez un tweet ou un commentaire pour prédire si le sentiment est positif ou négatif."
)

# Zone de saisie de texte pour l'utilisateur
user_input = st.text_area(
    "Écrivez le tweet à analyser ici :",
    "The flight was delayed for 3 hours, this is unacceptable!", # Exemple par défaut
    height=100
)

# 2. Bouton d'analyse : il enregistre le résultat dans le session_state
if st.button("Analyser le sentiment"):
    if user_input:
        with st.spinner("Analyse en cours..."):
            try:
                api_url = "http://127.0.0.1:8000/predict/"
                payload = {"text": user_input}
                response = requests.post(api_url, json=payload)
                response.raise_for_status() 

                result = response.json()
                
                # 3. On enregistre le résultat DANS LA SESSION
                st.session_state.sentiment = result["sentiment"]
                st.session_state.last_analyzed_text = user_input

            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion à l'API : {e}")
                st.warning("Assurez-vous que le serveur de l'API (FastAPI) est bien lancé.")
    else:
        st.warning("Veuillez entrer un texte à analyser.")

# 4. N'afficher ce bloc QUE SI une analyse a été faite (résultat en mémoire)
if st.session_state.sentiment:
    
    st.subheader("Résultat de l'analyse")
    if st.session_state.sentiment == "Négatif":
        st.error(f"Sentiment prédit : **Négatif** 😡")
    else:
        st.success(f"Sentiment prédit : **Positif** 😊")

    # 5. Le code des boutons de feedback est maintenant à l'extérieur
    # Il sera donc exécuté lors du rechargement de la page
    st.write("Cette prédiction était-elle correcte ?")
    
    col1, col2 = st.columns(2)

    if col1.button("Prédiction Correcte 👍"):
        st.toast("Merci pour votre retour !")
        # On réinitialise l'état pour cacher les boutons
        st.session_state.sentiment = None
        st.session_state.last_analyzed_text = ""

    if col2.button("Prédiction Incorrecte 👎"):
        # Ce code sera maintenant exécuté !
        feedback_api_url = "http://127.0.0.1:8000/feedback/"
        # On utilise le texte et le sentiment stockés dans la session
        feedback_payload = {
            "text": st.session_state.last_analyzed_text, 
            "prediction": st.session_state.sentiment
        }
        
        try:
            requests.post(feedback_api_url, json=feedback_payload)
            st.toast("Merci ! Le modèle sera amélioré grâce à votre retour.")
        except requests.exceptions.RequestException as e:
            st.error(f"Impossible d'envoyer le feedback : {e}")
        
        # On réinitialise l'état pour cacher les boutons
        st.session_state.sentiment = None
        st.session_state.last_analyzed_text = ""