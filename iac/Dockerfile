FROM python:3.11-slim

# Installer git pour MLflow et les packages Python nécessaires
RUN apt-get update && apt-get install -y git 

# Installer pip et packages Python en fixant la version tensorflow compatible
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir tensorflow==2.19.0 \
    && pip install --no-cache-dir pandas mlflow jupyter torch transformers nltk tf-keras

# Installer tensorflow-text avec version compatible (ajuster au besoin)
RUN pip install --no-cache-dir tensorflow-text==2.19.0

# Exposer les ports pour Jupyter (8888) et MLflow (5000)
EXPOSE 8888
EXPOSE 5000

# Copier le script de démarrage
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Lancer le script au démarrage
CMD ["/start.sh"]