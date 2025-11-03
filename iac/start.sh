#!/bin/bash

# Lancer MLflow sur le port 5000 en tâche de fond
# On lui spécifie d'utiliser le répertoire /mlflow (qui est mappé sur le volume de l'hôte)
# comme backend pour stocker les métadonnées et comme racine pour les artefacts (modèles, etc.).
mlflow server --backend-store-uri /mlflow --default-artifact-root /mlflow --host 0.0.0.0 --port 5000 &

# Lancer l'API FastAPI en tâche de fond
cd /root/work/api
uvicorn main:app --host 0.0.0.0 --port 8000 &
cd /

# Lancer Jupyter Notebook sur le port 8888 au premier plan
jupyter notebook --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
