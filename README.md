This project aims to study different ML models for sentiment analysis.This repository contains the code and resources for this project.

## Project Structure

The project is organized into the following directories:

*   **`api/`**: Contains the FastAPI application for serving the sentiment analysis model.
*   **`iac/`**: Infrastructure as Code (IaC) using Terraform (OpenTofu) to deploy the application and its dependencies.
*   **`notebooks/`**: Jupyter notebooks for model development, experimentation, and analysis.
*   **`data/`**: (Not versioned) This directory is intended for storing datasets used in the project.
*   **`models/`**:  This directory will store trained machine learning models.

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

## 3. Python Dependencies

Python dependencies are managed in two files:
*   `api/requirements.txt`: for the FastAPI application.
*   `iac/ml-requirements.txt`: for the machine learning environment (Jupyter, Tensorflow, etc.).

If you add a dependency, be sure to add it to the correct file, then rebuild the Docker image.

## 4. NLTK Error `LookupError: Resource punkt not found`

When running the notebook for the first time, you may encounter an error related to the `nltk` library.

**Cause**: `nltk` needs to download data packages (such as tokenizers, stop-word lists, etc.) to function.

**Solution**: The notebook already contains a cell that handles this download. Make sure to run it.

```python
# NLTK resource download cell
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

This operation is only necessary once, as the data is saved in the container.


# Github Action runner
```bash
cd actions-runner/
./run.sh
```