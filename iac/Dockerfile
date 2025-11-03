FROM python:3.11-slim

# Mettre à jour et installer les paquets système nécessaires
RUN apt-get update && apt-get install -y git

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances et les installer
COPY api/requirements.txt ./api-requirements.txt
COPY iac/ml-requirements.txt ./ml-requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r api-requirements.txt && \
    pip install --no-cache-dir -r ml-requirements.txt

# Exposer les ports nécessaires
EXPOSE 8000 
EXPOSE 8888
EXPOSE 5000

# Copier le script de démarrage et le rendre exécutable
COPY iac/start.sh /start.sh
RUN chmod +x /start.sh

# Commande par défaut pour lancer le conteneur
CMD ["/start.sh"]