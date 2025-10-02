#!/bin/bash

# Lancer MLflow sur le port 5000 en tâche de fond
mlflow server --host 0.0.0.0 --port 5000 &

# Lancer Jupyter Notebook sur le port 8888 au premier plan
jupyter notebook --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
