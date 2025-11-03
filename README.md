This project aims to study different ML models for sentiment analysis.

# Installation

1.  **Build the Docker Image**

    From the project root directory, run the following command. This needs to be done only once, or whenever you change the `Dockerfile` or the dependencies.

    ```bash
    docker build -t mycustom/ml-image:latest -f iac/Dockerfile .
    ```

2.  **Deploy with Terraform (OpenTofu)**

    From the `iac` directory, run:

    ```bash
    tofu apply
    ```

For debug:
```bash
docker exec -it ml_training bash
```

# Points d'attention et Dépannage

Cette section clarifie certains aspects de la configuration qui peuvent prêter à confusion.

## 1. Configuration de MLflow

MLflow fonctionne sur un modèle client-serveur. Il est crucial que le client (votre notebook) et le serveur (l'interface web et le service de modèles) regardent le même emplacement pour les données.

*   **Dans le notebook (`projet7_distillbert.ipynb`)** :
    ```python
    mlflow.set_tracking_uri("file:/mlflow")
    ```
    Cette ligne configure le **client MLflow**. Elle lui indique de sauvegarder toutes les données (métriques, paramètres, modèles) dans le répertoire `/mlflow` **à l'intérieur du conteneur Docker**.

*   **Dans le script de démarrage (`iac/start.sh`)** :
    ```bash
    mlflow server --backend-store-uri /mlflow ...
    ```
    Cette ligne démarre le **serveur MLflow** et lui indique de lire les données depuis ce même répertoire `/mlflow`.

*   **Le lien entre les deux (`iac/main.tf`)** :
    La magie s'opère grâce au mappage de volume Docker :
    ```terraform
    volumes {
      host_path      = "/home/samuel/mlflow_data"
      container_path = "/mlflow"
    }
    ```
    Ce bloc relie le répertoire `/mlflow` du conteneur au répertoire `/home/samuel/mlflow_data` sur votre machine hôte. Ainsi, les données écrites par le notebook sont persistées sur votre machine et lues par le serveur MLflow.

> **Conclusion** : Il est normal et correct que les chemins soient différents. L'un est vu de l'intérieur du conteneur, l'autre de l'extérieur. Le volume Docker les synchronise.

## 2. Workflow Docker et Terraform (OpenTofu)

Le build de l'image Docker est maintenant manuel pour éviter des problèmes de timeout avec Terraform.

Lorsque vous modifiez un fichier qui est inclus dans votre image Docker (comme `iac/start.sh`, `iac/Dockerfile`, `api/requirements.txt`, ou `iac/ml-requirements.txt`), vous devez reconstruire l'image manuellement:
```bash
docker build -t mycustom/ml-image:latest -f iac/Dockerfile .
```

`tofu apply` ne détectera pas ce changement automatiquement. Pour forcer Terraform/Tofu à recréer le conteneur avec la nouvelle image, nous utilisons une variable d'environnement dans `iac/main.tf` qui se base sur l'identifiant unique (hash) de l'image :

```terraform
# iac/main.tf
resource "docker_container" "ml_container" {
  # ...
  env = ["IMAGE_ID=${data.docker_image.ml_image.id}"]
  # ...
}
```

Avec ce changement, chaque `tofu apply` après une reconstruction d'image mettra à jour votre conteneur.

## 3. Dépendances Python

Les dépendances Python sont gérées dans deux fichiers :
*   `api/requirements.txt`: pour l'application FastAPI.
*   `iac/ml-requirements.txt`: pour l'environnement de machine learning (Jupyter, Tensorflow, etc.).

Si vous ajoutez une dépendance, assurez-vous de l'ajouter au bon fichier, puis reconstruisez l'image Docker.

## 4. Erreur NLTK `LookupError: Resource punkt not found`

Lors de la première exécution du notebook, vous pourriez rencontrer une erreur liée à la bibliothèque `nltk`.

**Cause** : `nltk` a besoin de télécharger des paquets de données (comme des tokenizers, des listes de stop-words, etc.) pour fonctionner.

**Solution** : Le notebook contient déjà une cellule qui s'occupe de ce téléchargement. Assurez-vous de l'exécuter.

```python
# Cellule de téléchargement des ressources NLTK
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

Cette opération n'est nécessaire qu'une seule fois, car les données sont sauvegardées dans le conteneur.


# Github Action runner
```bash
cd actions-runner/
./run.sh 
```