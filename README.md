This project aims to study different ML models for sentiment analysis.This repository contains the code and resources for this project.

## Project Structure

The project is organized into the following directories:

*   **`api/`**: Contains the FastAPI application for serving the sentiment analysis model.
*   **`iac/`**: Infrastructure as Code (IaC) using Terraform (OpenTofu) to deploy the application and its dependencies.
*   **`notebooks/`**: Jupyter notebooks for model development, experimentation, and analysis.
*   **`data/`**: (Not versioned) This directory is intended for storing datasets used in the project.
*   **`models/`**:  This directory will store trained machine learning models.

## Data Setup

This project requires certain data files to be placed in the `data/` directory.

### Automated Data Population

A shell script is provided to automate the download and setup of the required dataset. To use it, run the following command from the root of the project:

```bash
bash populate_data.sh
```

This script will:
1. Create the `data` directory.
2. Download the sentiment analysis dataset.
3. Extract the archive and move the relevant CSV file (`training.1600000.processed.noemoticon.csv`) into the `data` directory.
4. Clean up the temporary files.

### Manual Data Setup

If you prefer to set up the data manually, follow these steps:

1.  **Glove Embeddings**:
    *   The file `glove.6B.100d.txt` is required. It should be placed in `data/glove.6B/`.
    *   This file is part of the GloVe embeddings which can be downloaded from the [Stanford NLP website](https://nlp.stanford.edu/projects/glove/). You will need to download `glove.6B.zip` and extract it.

2.  **Sentiment Analysis Dataset**:
    *   The training dataset needs to be downloaded and extracted into the `data/` directory.
    *   Download the dataset from [this link](https://s3-eu-west-1.amazonaws.com/static.oc-static.com/prod/courses/files/AI+Engineer/Project+7%C2%A0-+D%C3%A9tectez+les+Bad+Buzz+gr%C3%A2ce+au+Deep+Learning/sentiment140.zip).

## Technologies and Packages

This project leverages the following key technologies and Python packages:

*   **Python**: The primary programming language.
*   **TensorFlow/Keras**: For building and training deep learning models.
*   **Hugging Face Transformers**: For utilizing pre-trained language models like DistilBERT.
*   **NLTK**: For natural language processing tasks such as tokenization and stop-word removal.
*   **FastAPI**: For building the RESTful API to serve the sentiment analysis model.
*   **MLflow**: For tracking experiments, logging parameters, metrics, and models.
*   **Docker**: For containerizing the application and its environment.
*   **Terraform (OpenTofu)**: For defining and provisioning the infrastructure.
*   **Jupyter Notebook**: For interactive development and experimentation.

A detailed list of Python dependencies can be found in `api/requirements.txt` and `iac/ml-requirements.txt`.

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

# Monitoring Installation

This project uses Prometheus and Grafana for monitoring. These tools are deployed using Docker Compose.

1.  **Ensure Docker is Running**: Make sure Docker Desktop or your Docker daemon is running on your machine.

2.  **Navigate to the Monitoring Directory**:
    ```bash
    cd monitoring/
    ```

3.  **Start Monitoring Services**:
    Run the following command to start Prometheus and Grafana:
    ```bash
    docker-compose up -d
    ```
    The `-d` flag runs the containers in detached mode (in the background).

4.  **Access Grafana**:
    Once the services are up, you can access Grafana by opening your web browser and navigating to `http://localhost:3000`.
    *   **Default Username**: `admin`
    *   **Default Password**: `admin` (you will be prompted to change this on first login)

5.  **Access Prometheus**:
    You can access the Prometheus UI at `http://localhost:9090`.

6.  **Stop Monitoring Services**:
    To stop and remove the monitoring containers, navigate to the `monitoring/` directory and run:
    ```bash
    docker-compose down
    ```

### Grafana Alerting Rules

This project includes a predefined alerting rule for Grafana. To use it, you need to import the rules from the `monitoring/alerting_rules.yaml` file into your Grafana instance.

**To import the rules:**

1.  Navigate to your Grafana instance (usually `http://localhost:3000`).
2.  Go to the "Alerting" section in the left-hand menu.
3.  Find the option to import alert rules and upload the `alerting_rules.yaml` file.

**Defined Rule:**

*   **Alert: High Prediction Error Rate (`Alerte - Taux d'erreur de prédiction élevé`)**
    *   **Description:** This rule monitors the number of incorrect predictions made by the sentiment analysis API.
    *   **Condition:** It triggers an alert if there are more than 2 `bad_prediction` events within a 5-minute window.


## 3. Python Dependencies

Python dependencies are managed in two files:
*   `api/requirements.txt`: for the FastAPI application.
*   `iac/ml-requirements.txt`: for the machine learning environment (Jupyter, Tensorflow, etc.).

If you add a dependency, be sure to add it to the correct file, then rebuild the Docker image.


# Github Action runner
```bash
cd actions-runner/
./run.sh
```

# Key Points and Troubleshooting

This section clarifies some configuration aspects that may be confusing.

## 1. MLflow Configuration

MLflow operates on a client-server model. It is crucial that the client (your notebook) and the server (the web interface and model service) look at the same location for data.

*   **In the notebook (`script_notebook_modelisation.ipynb`)**:
    ```python
    mlflow.set_tracking_uri("file:/mlflow")
    ```
    This line configures the **MLflow client**. It tells it to save all data (metrics, parameters, models) in the `/mlflow` directory **inside the Docker container**.

*   **In the startup script (`iac/start.sh`)**:
    ```bash
    mlflow server --backend-store-uri /mlflow ...
    ```
    This line starts the **MLflow server** and tells it to read data from this same `/mlflow` directory.

*   **The link between the two (`iac/main.tf`)**:
    The magic happens thanks to Docker volume mapping:
    ```terraform
    volumes {
      host_path      = "/home/samuel/mlflow_data"
      container_path = "/mlflow"
    }
    ```
    This block links the container's `/mlflow` directory to the `/home/samuel/mlflow_data` directory on your host machine. Thus, the data written by the notebook is persisted on your machine and read by the MLflow server.

> **Conclusion**: It is normal and correct for the paths to be different. One is seen from inside the container, the other from the outside. The Docker volume synchronizes them.

## 2. Docker and Terraform (OpenTofu) Workflow

The Docker image build is now manual to avoid timeout issues with Terraform.

When you modify a file that is included in your Docker image (such as `iac/start.sh`, `iac/Dockerfile`, `api/requirements.txt`, or `iac/ml-requirements.txt`), you must rebuild the image manually:
```bash
docker build -t mycustom/ml-image:latest -f iac/Dockerfile .
```

`tofu apply` will not automatically detect this change. To force Terraform/Tofu to recreate the container with the new image, we use an environment variable in `iac/main.tf` which is based on the unique identifier (hash) of the image:

```terraform
# iac/main.tf
resource "docker_container" "ml_container" {
  # ...
  env = ["IMAGE_ID=${data.docker_image.ml_image.id}"]
  # ...
}
```

With this change, every `tofu apply` after an image rebuild will update your container.

